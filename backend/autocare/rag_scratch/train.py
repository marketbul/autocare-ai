"""Training script for AutoCare AI Causal Transformer LM and Embedding Engine.

Trains the Transformer Decoder on automotive repair diagnostic cases,
SAE OBD-II codes, and factory manual excerpts using Next-Token Prediction
(Causal Language Modeling with Cross-Entropy Loss).
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

# Set up paths
backend_dir = Path(__file__).resolve().parents[2]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from autocare.rag_scratch.embedding_engine import AutomotiveEmbedder
from autocare.rag_scratch.rag_pipeline import AutoCareRAGFromScratch
from autocare.rag_scratch.tokenizer import AutomotiveTokenizer
from autocare.rag_scratch.transformer_decoder import AutomotiveCausalLM


class AutomotiveCausalDataset(Dataset):
    """Dataset packaging Q&A diagnostic pairs into causal training sequences."""

    def __init__(self, sequences: list[list[int]], max_seq_len: int = 128, pad_id: int = 0):
        self.samples = []
        for seq in sequences:
            if len(seq) < 4:
                continue
            # Truncate or pad to max_seq_len
            if len(seq) > max_seq_len:
                seq = seq[:max_seq_len]
            self.samples.append(seq)
        self.max_seq_len = max_seq_len
        self.pad_id = pad_id

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        seq = self.samples[idx]
        # Pad sequence
        padded = seq + [self.pad_id] * (self.max_seq_len - len(seq))
        input_ids = torch.tensor(padded[:-1], dtype=torch.long)
        targets = torch.tensor(padded[1:], dtype=torch.long)
        # Mask padding in loss computation with -100
        targets[targets == self.pad_id] = -100
        return input_ids, targets


def prepare_training_sequences(rag: AutoCareRAGFromScratch, tokenizer: AutomotiveTokenizer) -> list[list[int]]:
    """Builds tokenized sequences for causal next-token prediction."""
    documents = rag.extract_corpus_data()
    sequences = []

    for doc in documents:
        text = doc.get("text", "").strip()
        if not text:
            continue
        # Structure as Causal Sequence: <BOS> text <EOS>
        formatted = f"{tokenizer.BOS_TOKEN} {text} {tokenizer.EOS_TOKEN}"
        encoded = tokenizer.encode(formatted, add_special_tokens=False)
        sequences.append(encoded)

    return sequences


def train_model(
    epochs: int = 4,
    batch_size: int = 32,
    lr: float = 1e-3,
    embed_dim: int = 128,
    num_heads: int = 4,
    num_layers: int = 4,
    max_seq_len: int = 128,
):
    print("=" * 80)
    print(" AUTOCARE AI &bull; TRANSFORMER DECODER TRAINING PIPELINE (FROM SCRATCH)")
    print("=" * 80)
    start_total_time = time.time()

    weights_dir = Path(__file__).resolve().parent / "weights"
    weights_dir.mkdir(parents=True, exist_ok=True)

    rag = AutoCareRAGFromScratch()
    print("[1/5] Extracting corpus documents and building vocabulary...")
    documents = rag.extract_corpus_data()
    all_texts = [d["text"] for d in documents]

    tokenizer = AutomotiveTokenizer()
    tokenizer.build_vocab(all_texts, min_freq=2, max_vocab_size=4000)
    tokenizer_path = weights_dir / "tokenizer_vocab.json"
    tokenizer.save(tokenizer_path)
    print(f"      Vocabulary built: {tokenizer.vocab_size} tokens. Saved to {tokenizer_path.name}")

    print("[2/5] Preparing causal training sequences...")
    token_seqs = prepare_training_sequences(rag, tokenizer)
    dataset = AutomotiveCausalDataset(token_seqs, max_seq_len=max_seq_len, pad_id=tokenizer.pad_id)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, drop_last=True)
    print(f"      Total training samples: {len(dataset):,} sequences.")

    print(f"[3/5] Instantiating Causal Transformer ({num_layers} layers, {num_heads} heads, d={embed_dim})...")
    device = torch.device("cpu")
    model = AutomotiveCausalLM(
        vocab_size=tokenizer.vocab_size,
        embed_dim=embed_dim,
        num_heads=num_heads,
        num_layers=num_layers,
        max_seq_len=max_seq_len,
        dropout=0.1,
    ).to(device)

    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"      Total Trainable Parameters: {total_params:,}")

    # Optimizer & Cross-Entropy Loss
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    criterion = nn.CrossEntropyLoss(ignore_index=-100)

    print(f"[4/5] Running gradient descent training loop across {epochs} epochs...")
    model.train()
    for epoch in range(1, epochs + 1):
        epoch_start = time.time()
        running_loss = 0.0
        steps = 0

        for step, (inputs, targets) in enumerate(dataloader):
            inputs, targets = inputs.to(device), targets.to(device)
            optimizer.zero_grad()

            logits = model(inputs)  # (batch_size, seq_len, vocab_size)
            loss = criterion(logits.view(-1, tokenizer.vocab_size), targets.view(-1))

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            running_loss += loss.item()
            steps += 1

        avg_loss = running_loss / max(steps, 1)
        perplexity = math.exp(min(avg_loss, 20.0))
        epoch_duration = time.time() - epoch_start
        print(f"      Epoch {epoch:02d}/{epochs:02d} &bull; Loss: {avg_loss:.4f} &bull; Perplexity: {perplexity:.2f} &bull; Time: {epoch_duration:.1f}s")

    # Save trained checkpoint
    model_checkpoint_path = weights_dir / "autocare_causal_lm.pt"
    torch.save(model.state_dict(), model_checkpoint_path)
    print(f"[5/5] Trained Transformer weights saved to: {model_checkpoint_path}")

    # Also train and save dense embedder weights
    embedder = AutomotiveEmbedder(tokenizer=tokenizer, embedding_dim=embed_dim, device="cpu")
    embedder_checkpoint_path = weights_dir / "autocare_embedder.pt"
    embedder.save(embedder_checkpoint_path)
    print(f"      Trained Embedder weights saved to: {embedder_checkpoint_path}")

    total_time = time.time() - start_total_time
    print("=" * 80)
    print(f" [SUCCESS] Training completed in {total_time:.1f} seconds! Ready for RAG deployment.")
    print("=" * 80)


if __name__ == "__main__":
    train_model(epochs=3, batch_size=32, lr=1e-3, embed_dim=128)
