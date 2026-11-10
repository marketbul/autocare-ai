"""Custom In-Memory Vector Store & Hybrid Retrieval Engine built from scratch.

Combines Dense Semantic Vector Search with Lexical BM25 Keyword Search
for exact DTC matching and zero-hallucination evidence grounding.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from .embedding_engine import AutomotiveEmbedder
from .tokenizer import AutomotiveTokenizer


@dataclass
class DocumentChunk:
    chunk_id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: np.ndarray | None = None


@dataclass
class RetrievedEvidence:
    chunk: DocumentChunk
    dense_score: float
    lexical_score: float
    hybrid_score: float
    rank: int


class BM25LexicalScorer:
    """Standard Okapi BM25 implementation from scratch."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = 0
        self.avg_doc_len = 0.0
        self.doc_lengths: list[int] = []
        self.doc_freqs: dict[str, int] = {}
        self.tokenized_corpus: list[list[str]] = []

    def fit(self, corpus_tokens: list[list[str]]) -> None:
        self.tokenized_corpus = corpus_tokens
        self.corpus_size = len(corpus_tokens)
        if self.corpus_size == 0:
            return

        self.doc_lengths = [len(doc) for doc in corpus_tokens]
        self.avg_doc_len = sum(self.doc_lengths) / self.corpus_size

        self.doc_freqs = {}
        for doc in corpus_tokens:
            unique_tokens = set(doc)
            for token in unique_tokens:
                self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1

    def score(self, query_tokens: list[str]) -> np.ndarray:
        scores = np.zeros(self.corpus_size, dtype=np.float32)
        if self.corpus_size == 0 or not query_tokens:
            return scores

        for token in query_tokens:
            if token not in self.doc_freqs:
                continue

            # Inverse Document Frequency (IDF)
            df = self.doc_freqs[token]
            idf = math.log(1.0 + (self.corpus_size - df + 0.5) / (df + 0.5))

            for idx, doc in enumerate(self.tokenized_corpus):
                term_count = doc.count(token)
                if term_count == 0:
                    continue

                doc_len = self.doc_lengths[idx]
                numerator = term_count * (self.k1 + 1.0)
                denominator = term_count + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_len))
                scores[idx] += idf * (numerator / denominator)

        # Normalize lexical scores to [0, 1] range
        max_score = np.max(scores)
        if max_score > 0:
            scores = scores / max_score

        return scores


class AutomotiveVectorStore:
    """In-memory hybrid vector store indexing technical manuals & repair cases."""

    def __init__(self, tokenizer: AutomotiveTokenizer, embedder: AutomotiveEmbedder):
        self.tokenizer = tokenizer
        self.embedder = embedder
        self.chunks: list[DocumentChunk] = []
        self.embeddings: np.ndarray = np.empty((0, embedder.embedding_dim), dtype=np.float32)
        self.bm25 = BM25LexicalScorer()
        self.tokenized_texts: list[list[str]] = []

    def chunk_text(self, text: str, chunk_size: int = 80, overlap: int = 15) -> list[str]:
        """Splits arbitrary long text into overlapping sliding-window chunks."""
        words = text.split()
        if len(words) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_str = " ".join(words[start:end])
            chunks.append(chunk_str)
            if end == len(words):
                break
            start += chunk_size - overlap
        return chunks

    def add_documents(self, documents: list[dict[str, Any]]) -> int:
        """
        documents format:
        [{"id": "doc1", "text": "...", "metadata": {"make": "Toyota", "code": "P0301", "page": 42}}]
        """
        new_chunks: list[DocumentChunk] = []
        raw_texts: list[str] = []

        for doc in documents:
            text = doc.get("text", "").strip()
            if not text:
                continue

            doc_id = doc.get("id", f"doc_{len(self.chunks) + len(new_chunks)}")
            meta = doc.get("metadata", {})

            # Split into semantic windows
            split_passages = self.chunk_text(text)
            for idx, passage in enumerate(split_passages):
                chunk_id = f"{doc_id}_c{idx}"
                chunk_meta = dict(meta)
                chunk_meta["chunk_index"] = idx
                chunk_meta["total_chunks"] = len(split_passages)

                chunk = DocumentChunk(chunk_id=chunk_id, text=passage, metadata=chunk_meta)
                new_chunks.append(chunk)
                raw_texts.append(passage)

        if not new_chunks:
            return 0

        # Compute dense embeddings in batch
        new_vecs = self.embedder.encode(raw_texts)
        for i, chunk in enumerate(new_chunks):
            chunk.embedding = new_vecs[i]

        self.chunks.extend(new_chunks)
        if self.embeddings.shape[0] == 0:
            self.embeddings = new_vecs
        else:
            self.embeddings = np.vstack([self.embeddings, new_vecs])

        # Update BM25 corpus
        self.tokenized_texts = [
            self.tokenizer._pre_tokenize(c.text.lower()) for c in self.chunks
        ]
        self.bm25.fit(self.tokenized_texts)

        return len(new_chunks)

    def search(
        self,
        query: str,
        top_k: int = 4,
        alpha: float = 0.65,
        min_score: float = 0.25,
        filter_metadata: dict[str, Any] | None = None,
    ) -> list[RetrievedEvidence]:
        """
        Performs Hybrid Search:
        Score = alpha * DenseCosineScore + (1 - alpha) * BM25Score
        """
        if len(self.chunks) == 0:
            return []

        # 1. Dense Semantic Similarity
        query_vec = self.embedder.encode([query])
        dense_scores = self.embedder.cosine_similarity(query_vec, self.embeddings)

        # 2. Lexical BM25 Similarity
        query_tokens = self.tokenizer._pre_tokenize(query.lower())
        lexical_scores = self.bm25.score(query_tokens)

        # 3. Hybrid Combination & Filtering
        results: list[RetrievedEvidence] = []
        for idx in range(len(self.chunks)):
            chunk = self.chunks[idx]

            # Metadata filtering
            if filter_metadata:
                match = True
                for k, v in filter_metadata.items():
                    if chunk.metadata.get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            d_score = float(dense_scores[idx]) if idx < len(dense_scores) else 0.0
            l_score = float(lexical_scores[idx]) if idx < len(lexical_scores) else 0.0

            # Boost exact DTC code matches
            query_dtcs = re.findall(r"[PBUC]\d{4}", query.upper())
            chunk_dtcs = re.findall(r"[PBUC]\d{4}", chunk.text.upper())
            has_dtc_match = any(code in chunk_dtcs for code in query_dtcs)
            if has_dtc_match:
                d_score = min(1.0, d_score + 0.3)
                l_score = min(1.0, l_score + 0.4)

            hybrid = alpha * d_score + (1.0 - alpha) * l_score
            if hybrid >= min_score or has_dtc_match:
                results.append(
                    RetrievedEvidence(
                        chunk=chunk,
                        dense_score=round(d_score, 4),
                        lexical_score=round(l_score, 4),
                        hybrid_score=round(hybrid, 4),
                        rank=0,
                    )
                )

        # Sort by hybrid score descending
        results.sort(key=lambda r: r.hybrid_score, reverse=True)
        for r_idx, res in enumerate(results):
            res.rank = r_idx + 1

        return results[:top_k]
