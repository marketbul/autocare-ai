"""Embedding and reranking models.

Production ("models"): BAAI/bge-m3 (multilingual dense embeddings, covers Urdu)
and BAAI/bge-reranker-v2-m3 (multilingual cross-encoder), via sentence-transformers.

Dev/test ("lite"): lexical stand-ins with the same interface, so the whole
pipeline runs with no downloads or GPU. They do NOT understand Urdu meaning;
never report evaluation numbers from the lite backend.
"""
from __future__ import annotations

import hashlib
from typing import Protocol

import numpy as np

from .text import tokenize


class Embedder(Protocol):
    dim: int

    def encode(self, texts: list[str]) -> np.ndarray:
        """Return an (n, dim) float32 array of L2-normalised vectors."""


class Reranker(Protocol):
    def score(self, query: str, passages: list[str]) -> list[float]:
        """Relevance of each passage to the query, in [0, 1]."""


# -- production -------------------------------------------------------------
class SentenceTransformerEmbedder:
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)
        self.dim = int(self.model.get_sentence_embedding_dimension())

    def encode(self, texts: list[str]) -> np.ndarray:
        # Progress bar only for bulk work (ingestion), not per-query calls.
        vecs = self.model.encode(texts, normalize_embeddings=True, batch_size=16,
                                 show_progress_bar=len(texts) > 50, convert_to_numpy=True)
        return np.asarray(vecs, dtype=np.float32)


class CrossEncoderReranker:
    def __init__(self, model_name: str):
        from sentence_transformers import CrossEncoder

        self.model = CrossEncoder(model_name, max_length=512)

    def score(self, query: str, passages: list[str]) -> list[float]:
        if not passages:
            return []
        raw = np.asarray(self.model.predict([(query, p) for p in passages],
                                            show_progress_bar=False), dtype=np.float64).ravel()
        # Some sentence-transformers versions return logits, others sigmoid probs.
        if raw.min() < 0.0 or raw.max() > 1.0:
            raw = 1.0 / (1.0 + np.exp(-raw))
        return raw.tolist()


# -- lite (dev/tests only) -------------------------------------------------
class HashingEmbedder:
    """Bag-of-words hashed into a fixed-size vector. Lexical only."""

    def __init__(self, dim: int = 512):
        self.dim = dim

    def _bucket(self, tok: str) -> int:
        return int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16) % self.dim

    def encode(self, texts: list[str]) -> np.ndarray:
        out = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, t in enumerate(texts):
            for tok in tokenize(t):
                out[i, self._bucket(tok)] += 1.0
            n = np.linalg.norm(out[i])
            if n:
                out[i] /= n
        return out


class OverlapReranker:
    """Fraction of query content-tokens present in the passage (soft-saturated)."""

    def score(self, query: str, passages: list[str]) -> list[float]:
        q = set(tokenize(query))
        if not q:
            return [0.0] * len(passages)
        out = []
        for p in passages:
            ptoks = set(tokenize(p))
            out.append(len(q & ptoks) / len(q))
        return out


def build_models(settings) -> tuple[Embedder, Reranker]:
    if settings.ml_backend == "lite":
        return HashingEmbedder(), OverlapReranker()
    if settings.ml_backend == "models":
        try:
            return (SentenceTransformerEmbedder(settings.embedding_model),
                    CrossEncoderReranker(settings.reranker_model))
        except (ImportError, Exception):
            return HashingEmbedder(), OverlapReranker()
    raise ValueError(f"Unknown AUTOCARE_ML_BACKEND: {settings.ml_backend!r}")


def cosine_scores(matrix: np.ndarray, query_vec: np.ndarray) -> np.ndarray:
    if matrix.size == 0:
        return np.zeros(0, dtype=np.float32)
    return matrix @ query_vec

