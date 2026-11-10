"""Custom Dense Vector Embedding Engine built from scratch.

Generates dense L2-normalized vector embeddings for text chunks and queries
using token representation pooling, positional semantics, and projection layers.
"""
from __future__ import annotations

import math
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from .tokenizer import AutomotiveTokenizer


class SemanticEmbeddingModel(nn.Module):
    """PyTorch Embedding Model mapping token IDs to a dense latent vector space."""

    def __init__(self, vocab_size: int, embedding_dim: int = 128, hidden_dim: int = 256):
        super().__init__()
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        
        # Token Embedding Table
        self.token_embeddings = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        
        # Positional Encoding Table (up to 512 tokens)
        self.pos_embeddings = nn.Embedding(512, embedding_dim)
        
        # Contextual Transformation Layers
        self.encoder = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, embedding_dim),
            nn.LayerNorm(embedding_dim),
        )
        
        # Token Importance Self-Attention Gate
        self.attention_gate = nn.Linear(embedding_dim, 1)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        """
        input_ids: (batch_size, seq_len)
        attention_mask: (batch_size, seq_len) with 1 for tokens and 0 for padding
        Returns: (batch_size, embedding_dim) L2-normalized dense vector
        """
        batch_size, seq_len = input_ids.shape
        positions = torch.arange(seq_len, device=input_ids.device).unsqueeze(0).expand(batch_size, seq_len)
        
        # Sum token + positional embeddings
        x = self.token_embeddings(input_ids) + self.pos_embeddings(positions)
        
        # Pass through contextual feed-forward projection
        x = self.encoder(x)  # (batch_size, seq_len, embedding_dim)
        
        # Compute self-attention pooling weights
        scores = self.attention_gate(x).squeeze(-1)  # (batch_size, seq_len)
        scores = scores.masked_fill(attention_mask == 0, -1e9)
        weights = F.softmax(scores, dim=-1).unsqueeze(-1)  # (batch_size, seq_len, 1)
        
        # Weighted sum pooling
        pooled = torch.sum(x * weights, dim=1)  # (batch_size, embedding_dim)
        
        # L2 Normalization: ||v||_2 = 1.0 (enables fast dot-product cosine similarity)
        normalized = F.normalize(pooled, p=2, dim=-1)
        return normalized


class AutomotiveEmbedder:
    """High-level interface to encode text strings into dense NumPy vector matrices."""

    def __init__(self, tokenizer: AutomotiveTokenizer, embedding_dim: int = 128, device: str = "cpu"):
        self.tokenizer = tokenizer
        self.device = torch.device(device)
        self.embedding_dim = embedding_dim
        
        self.model = SemanticEmbeddingModel(
            vocab_size=max(tokenizer.vocab_size, 100),
            embedding_dim=embedding_dim
        ).to(self.device)
        self.model.eval()

    def encode(self, texts: list[str] | str, max_length: int = 128) -> np.ndarray:
        """Encodes one or more texts into an (N, embedding_dim) float32 numpy array."""
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return np.empty((0, self.embedding_dim), dtype=np.float32)

        encoded_seqs = [self.tokenizer.encode(t, max_length=max_length) for t in texts]
        input_ids = torch.tensor(encoded_seqs, dtype=torch.long, device=self.device)
        attention_mask = (input_ids != self.tokenizer.pad_id).long()

        with torch.no_grad():
            vectors = self.model(input_ids, attention_mask)
            
        return vectors.cpu().numpy().astype(np.float32)

    @staticmethod
    def cosine_similarity(query_vec: np.ndarray, doc_vecs: np.ndarray) -> np.ndarray:
        """
        Computes cosine similarity between a single query vector (1, D)
        and an array of document vectors (N, D).
        Since vectors are L2-normalized, CosineSim is simply the dot product!
        """
        if doc_vecs.shape[0] == 0:
            return np.array([], dtype=np.float32)
        if query_vec.ndim == 1:
            query_vec = query_vec.reshape(1, -1)
            
        return np.dot(doc_vecs, query_vec.T).squeeze(-1)

    def save(self, filepath: str | Path) -> None:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), path)

    def load(self, filepath: str | Path) -> None:
        state = torch.load(filepath, map_location=self.device)
        self.model.load_state_dict(state)
        self.model.eval()
