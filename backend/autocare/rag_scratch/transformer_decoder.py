"""From-Scratch PyTorch Causal Language Model (Transformer Decoder) with Autoregressive Token Prediction.

Implements the fundamental mechanics of a generative LLM:
- Multi-Head Causal Self-Attention with triangular lower-triangular masking
- Positional encodings and Pre-LayerNorm residual blocks
- Next-token probability distribution projection (LM Head)
- Greedy decoding and temperature-based autoregressive generation
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Generator, Iterator

import torch
import torch.nn as nn
import torch.nn.functional as F

from .tokenizer import AutomotiveTokenizer


class CausalSelfAttention(nn.Module):
    """Multi-Head Self-Attention with causal future-token masking."""

    def __init__(self, embed_dim: int, num_heads: int, max_seq_len: int = 512, dropout: float = 0.1):
        super().__init__()
        assert embed_dim % num_heads == 0, "embed_dim must be divisible by num_heads"
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads

        self.q_proj = nn.Linear(embed_dim, embed_dim)
        self.k_proj = nn.Linear(embed_dim, embed_dim)
        self.v_proj = nn.Linear(embed_dim, embed_dim)
        self.out_proj = nn.Linear(embed_dim, embed_dim)
        self.dropout = nn.Dropout(dropout)

        # Causal mask: upper triangle is -inf so tokens cannot peek into the future
        mask = torch.tril(torch.ones(max_seq_len, max_seq_len)).view(1, 1, max_seq_len, max_seq_len)
        self.register_buffer("causal_mask", mask)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, seq_len, _ = x.shape

        # Linear projections & split into multi-heads
        q = self.q_proj(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)

        # Scaled Dot-Product Attention: (Q * K^T) / sqrt(d_k)
        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)

        # Apply causal mask (tokens can only attend to previous and current tokens)
        mask = self.causal_mask[:, :, :seq_len, :seq_len]
        scores = scores.masked_fill(mask == 0, float("-inf"))

        # Softmax over key dimension
        attn_probs = F.softmax(scores, dim=-1)
        attn_probs = self.dropout(attn_probs)

        # Compute weighted sum over values
        context = torch.matmul(attn_probs, v)  # (batch_size, num_heads, seq_len, head_dim)
        context = context.transpose(1, 2).contiguous().view(batch_size, seq_len, self.embed_dim)

        return self.out_proj(context)


class TransformerBlock(nn.Module):
    """Transformer Decoder Block with Pre-LayerNorm and Residual Connections."""

    def __init__(self, embed_dim: int, num_heads: int, mlp_ratio: int = 4, dropout: float = 0.1):
        super().__init__()
        self.ln1 = nn.LayerNorm(embed_dim)
        self.attn = CausalSelfAttention(embed_dim, num_heads, dropout=dropout)
        
        self.ln2 = nn.LayerNorm(embed_dim)
        self.mlp = nn.Sequential(
            nn.Linear(embed_dim, embed_dim * mlp_ratio),
            nn.GELU(),
            nn.Linear(embed_dim * mlp_ratio, embed_dim),
            nn.Dropout(dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Pre-LN Residual Attention
        x = x + self.attn(self.ln1(x))
        # Pre-LN Residual Feed-Forward
        x = x + self.mlp(self.ln2(x))
        return x


class AutomotiveCausalLM(nn.Module):
    """Generative Transformer Decoder Language Model built from scratch."""

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 128,
        num_heads: int = 4,
        num_layers: int = 4,
        max_seq_len: int = 512,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.max_seq_len = max_seq_len

        # Token & Positional Embeddings
        self.token_embeddings = nn.Embedding(vocab_size, embed_dim)
        self.pos_embeddings = nn.Embedding(max_seq_len, embed_dim)
        self.drop = nn.Dropout(dropout)

        # Stack of Causal Transformer Decoder Blocks
        self.blocks = nn.ModuleList([
            TransformerBlock(embed_dim, num_heads, dropout=dropout) for _ in range(num_layers)
        ])

        # Final LayerNorm & Language Modeling Head
        self.ln_f = nn.LayerNorm(embed_dim)
        self.lm_head = nn.Linear(embed_dim, vocab_size, bias=False)

        # Weight tying (Token embeddings shared with LM Head for efficiency)
        self.lm_head.weight = self.token_embeddings.weight

        self._init_weights()

    def _init_weights(self) -> None:
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.normal_(p, mean=0.0, std=0.02)

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        """
        input_ids: (batch_size, seq_len)
        Returns logits: (batch_size, seq_len, vocab_size)
        """
        batch_size, seq_len = input_ids.shape
        assert seq_len <= self.max_seq_len, f"Sequence length {seq_len} exceeds max {self.max_seq_len}"

        positions = torch.arange(seq_len, device=input_ids.device).unsqueeze(0).expand(batch_size, seq_len)
        x = self.token_embeddings(input_ids) + self.pos_embeddings(positions)
        x = self.drop(x)

        for block in self.blocks:
            x = block(x)

        x = self.ln_f(x)
        logits = self.lm_head(x)  # (batch_size, seq_len, vocab_size)
        return logits


class GenerativeTokenPredictor:
    """High-level runner performing autoregressive step-by-step token prediction."""

    def __init__(self, tokenizer: AutomotiveTokenizer, model: AutomotiveCausalLM, device: str = "cpu"):
        self.tokenizer = tokenizer
        self.model = model
        self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()

    def predict_next_token(self, token_ids: list[int], temperature: float = 0.7, top_k: int = 40) -> tuple[int, str, float]:
        """
        Predicts the single next token from preceding context tokens.
        Returns: (predicted_token_id, predicted_token_str, probability)
        """
        seq = token_ids[-self.model.max_seq_len:]
        input_tensor = torch.tensor([seq], dtype=torch.long, device=self.device)

        with torch.no_grad():
            logits = self.model(input_tensor)
            next_token_logits = logits[0, -1, :]  # Last position logits

            if temperature <= 0.01:
                # Greedy selection
                prob = F.softmax(next_token_logits, dim=-1)
                best_id = int(torch.argmax(next_token_logits).item())
                best_prob = float(prob[best_id].item())
                return best_id, self.tokenizer.inv_vocab.get(best_id, self.tokenizer.UNK_TOKEN), best_prob

            # Temperature scaling
            scaled_logits = next_token_logits / temperature

            # Top-K truncation
            if top_k > 0:
                values, _ = torch.topk(scaled_logits, min(top_k, scaled_logits.size(-1)))
                min_value = values[-1]
                scaled_logits = torch.where(scaled_logits < min_value, torch.tensor(-1e9, device=self.device), scaled_logits)

            probs = F.softmax(scaled_logits, dim=-1)
            sampled_id = int(torch.multinomial(probs, num_samples=1).item())
            sampled_prob = float(probs[sampled_id].item())

            token_str = self.tokenizer.inv_vocab.get(sampled_id, self.tokenizer.UNK_TOKEN)
            return sampled_id, token_str, sampled_prob

    def stream_generate(
        self,
        prompt: str,
        max_new_tokens: int = 100,
        temperature: float = 0.7,
        top_k: int = 40,
    ) -> Iterator[dict[str, Any]]:
        """
        Autoregressively generates tokens one by one and streams them.
        Yields: {"token": str, "token_id": int, "prob": float, "cumulative_text": str}
        """
        tokens = self.tokenizer.encode(prompt, add_special_tokens=False)
        generated_tokens: list[int] = []

        for step in range(max_new_tokens):
            current_context = tokens + generated_tokens
            next_id, token_str, prob = self.predict_next_token(current_context, temperature=temperature, top_k=top_k)

            # Check stop condition
            if next_id == self.tokenizer.eos_id:
                break

            generated_tokens.append(next_id)
            cum_text = self.tokenizer.decode(generated_tokens)

            yield {
                "step": step + 1,
                "token": token_str,
                "token_id": next_id,
                "prob": round(prob, 4),
                "cumulative_text": cum_text,
            }

    def save(self, filepath: str | Path) -> None:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), path)

    def load(self, filepath: str | Path) -> None:
        state = torch.load(filepath, map_location=self.device)
        self.model.load_state_dict(state)
        self.model.eval()
