"""Okapi BM25 (keyword half of hybrid retrieval, proposal §6.4).

Implemented here (~30 lines) rather than via rank_bm25 so that tokenisation is
shared with the rest of the pipeline and DTC tokens are guaranteed intact.
"""
from __future__ import annotations

import math
from collections import Counter

import numpy as np


class BM25:
    def __init__(self, corpus_tokens: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.doc_tf = [Counter(toks) for toks in corpus_tokens]
        self.doc_len = np.array([len(t) for t in corpus_tokens], dtype=np.float32)
        self.avgdl = float(self.doc_len.mean()) if len(corpus_tokens) else 0.0
        df: Counter = Counter()
        for tf in self.doc_tf:
            df.update(tf.keys())
        n = len(corpus_tokens)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def scores(self, query_tokens: list[str]) -> np.ndarray:
        out = np.zeros(len(self.doc_tf), dtype=np.float32)
        if not self.doc_tf or self.avgdl == 0:
            return out
        q = set(query_tokens)
        for i, tf in enumerate(self.doc_tf):
            norm = self.k1 * (1 - self.b + self.b * self.doc_len[i] / self.avgdl)
            s = 0.0
            for t in q:
                f = tf.get(t)
                if f:
                    s += self.idf[t] * f * (self.k1 + 1) / (f + norm)
            out[i] = s
        return out
