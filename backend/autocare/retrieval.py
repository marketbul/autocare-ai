"""L2 Evidence Retrieval for User Story 2.

Order of operations follows the architecture diagram:
  1. Vehicle-profile metadata filter  -> ScopedIndex holds ONLY in-scope chunks
  2. Hybrid retrieval                 -> weighted sum of semantic + BM25 (§6.4)
  3. Exact-DTC guard (AC3)            -> exact code chunks forced in, other-code chunks removed
  4. Reranking                        -> top candidate_k -> top final_k (§6.6)
  5. Evidence-strength gate (AC5)     -> passages below min_evidence_score are not evidence
Citation validation happens after generation (validation.py).
"""
from __future__ import annotations

import threading
from dataclasses import dataclass, field

import numpy as np

from .bm25 import BM25
from .ml import Embedder, Reranker, cosine_scores
from .repository import ChunkRecord, Repository, VehicleProfile
from .text import extract_dtcs, tokenize


@dataclass(eq=False)
class Evidence:
    chunk: ChunkRecord
    hybrid_score: float
    rerank_score: float
    exact_code_match: bool
    label: str = ""          # "E1".."En", assigned once the final set is fixed


@dataclass
class RetrievalResult:
    evidence: list[Evidence]
    weak_candidates: list[Evidence]           # retrieved but below the evidence threshold
    codes_in_corpus: dict[str, bool]           # queried DTC -> found in an in-scope chunk?
    signals: dict = field(default_factory=dict)


class ScopedIndex:
    """BM25 + dense matrix over the chunks of ONE vehicle scope."""

    def __init__(self, chunks: list[ChunkRecord], dim: int):
        self.chunks = chunks
        self.bm25 = BM25([tokenize(f"{c.section or ''} {c.text}") for c in chunks])
        self.codes = [set(extract_dtcs(f"{c.section or ''} {c.text}")) for c in chunks]
        mat = np.zeros((len(chunks), dim), dtype=np.float32)
        for i, c in enumerate(chunks):
            if c.embedding is not None:
                if c.embedding.shape[0] != dim:
                    raise RuntimeError(
                        f"Chunk {c.chunk_id} has a {c.embedding.shape[0]}-d embedding but the "
                        f"configured model produces {dim}-d vectors. Re-run ingestion with the "
                        f"current embedding model."
                    )
                mat[i] = c.embedding
        self.matrix = mat


class Retriever:
    def __init__(self, repo: Repository, embedder: Embedder, reranker: Reranker, settings):
        self.repo, self.embedder, self.reranker, self.s = repo, embedder, reranker, settings
        self._cache: dict[tuple, ScopedIndex] = {}
        self._lock = threading.Lock()

    def invalidate(self) -> None:
        with self._lock:
            self._cache.clear()

    def index_for(self, v: VehicleProfile) -> ScopedIndex:
        key = (v.manufacturer.lower(), v.model.lower(), int(v.year))
        with self._lock:
            if key not in self._cache:
                chunks = self.repo.chunks_in_scope(v.manufacturer, v.model, v.year)
                self._cache[key] = ScopedIndex(chunks, self.embedder.dim)
            return self._cache[key]

    def retrieve(self, vehicle: VehicleProfile, query: str, dtcs: list[str]) -> RetrievalResult:
        idx = self.index_for(vehicle)
        n = len(idx.chunks)
        codes_in_corpus = {c: any(c in cs for cs in idx.codes) for c in dtcs}
        if n == 0:
            return RetrievalResult([], [], codes_in_corpus, {"n_in_scope": 0, "n_candidates": 0})

        # -- hybrid scores ----------------------------------------------------
        qvec = self.embedder.encode([query])[0]
        sem = np.clip(cosine_scores(idx.matrix, qvec), 0.0, None)
        kw = idx.bm25.scores(tokenize(query))
        sem_n = sem / sem.max() if sem.max() > 0 else sem
        kw_n = kw / kw.max() if kw.max() > 0 else kw
        a = self.s.hybrid_alpha
        hybrid = a * sem_n + (1 - a) * kw_n

        # -- exact-DTC guard (AC3) ------------------------------------------------
        qcodes = set(dtcs)
        exact = np.zeros(n, dtype=bool)
        if qcodes:
            for i, cs in enumerate(idx.codes):
                if cs & qcodes:
                    exact[i] = True
                elif cs:
                    # Chunk is about a DIFFERENT code (e.g. P0302 for a P0301 query):
                    # semantically close, factually wrong. Never let it in.
                    hybrid[i] = -np.inf

        order = [int(i) for i in np.argsort(-hybrid) if hybrid[i] > 0]
        exact_ids = [i for i in order if exact[i]]
        cand = exact_ids + [i for i in order if not exact[i]]
        cand = cand[: max(self.s.candidate_k, len(exact_ids))]
        if not cand:
            return RetrievalResult([], [], codes_in_corpus,
                                   {"n_in_scope": n, "n_candidates": 0})

        # -- rerank ----------------------------------------------------------------
        passages = [f"{idx.chunks[i].section or ''}\n{idx.chunks[i].text}" for i in cand]
        rr = self.reranker.score(query, passages)
        scored = [
            Evidence(idx.chunks[i], float(hybrid[i]), float(r), bool(exact[i]))
            for i, r in zip(cand, rr)
        ]
        scored.sort(key=lambda e: (e.exact_code_match, e.rerank_score), reverse=True)

        # -- evidence gate (AC5) ---------------------------------------------------
        # An exact code match is strong evidence by itself, whatever the reranker says.
        strong = [e for e in scored if e.exact_code_match or e.rerank_score >= self.s.min_evidence_score]
        weak = [e for e in scored if e not in strong]
        evidence = strong[: self.s.final_k]
        for k, e in enumerate(evidence, 1):
            e.label = f"E{k}"

        by_score = sorted((e.rerank_score for e in scored), reverse=True)
        signals = {
            "n_in_scope": n,
            "n_candidates": len(cand),
            "n_evidence": len(evidence),
            "top_rerank_score": round(by_score[0], 4),
            "rerank_margin": round(by_score[0] - by_score[1], 4) if len(by_score) > 1 else None,
            "exact_code_match": bool(any(e.exact_code_match for e in evidence)),
        }
        weak.sort(key=lambda e: e.rerank_score, reverse=True)
        return RetrievalResult(evidence, weak[:3], codes_in_corpus, signals)
