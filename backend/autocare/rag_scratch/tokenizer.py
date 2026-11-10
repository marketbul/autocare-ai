"""Custom Multi-Lingual Subword Tokenizer built from scratch.

Supports English, Roman Urdu (e.g., 'gari start nahi ho rahi'), Urdu script,
and technical automotive DTC alphanumeric codes (e.g., 'P0301', 'OBD-II').
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable


class AutomotiveTokenizer:
    PAD_TOKEN = "<PAD>"
    UNK_TOKEN = "<UNK>"
    BOS_TOKEN = "<BOS>"
    EOS_TOKEN = "<EOS>"
    QUERY_TOKEN = "<QUERY>"
    CONTEXT_TOKEN = "<CONTEXT>"
    EVIDENCE_TOKEN = "<EVIDENCE>"
    ANSWER_TOKEN = "<ANSWER>"
    CITATION_TOKEN = "<CITATION>"

    SPECIAL_TOKENS = [
        PAD_TOKEN,
        UNK_TOKEN,
        BOS_TOKEN,
        EOS_TOKEN,
        QUERY_TOKEN,
        CONTEXT_TOKEN,
        EVIDENCE_TOKEN,
        ANSWER_TOKEN,
        CITATION_TOKEN,
    ]

    def __init__(self, vocab: dict[str, int] | None = None):
        if vocab is not None:
            self.vocab = vocab
            self.inv_vocab = {idx: token for token, idx in vocab.items()}
        else:
            self.vocab = {}
            self.inv_vocab = {}
            for idx, token in enumerate(self.SPECIAL_TOKENS):
                self.vocab[token] = idx
                self.inv_vocab[idx] = token

        self.pad_id = self.vocab[self.PAD_TOKEN]
        self.unk_id = self.vocab[self.UNK_TOKEN]
        self.bos_id = self.vocab[self.BOS_TOKEN]
        self.eos_id = self.vocab[self.EOS_TOKEN]

    @property
    def vocab_size(self) -> int:
        return len(self.vocab)

    def _pre_tokenize(self, text: str) -> list[str]:
        """Split text into words, punctuation, and DTC codes."""
        if not text:
            return []
        text = text.strip()
        # Preserve special tokens if present
        for special in self.SPECIAL_TOKENS:
            text = text.replace(special, f" {special} ")

        # Regex recognizing:
        # 1. Alphanumeric DTC fault codes (P0300, B1000, U0100, C1201)
        # 2. English words and Roman Urdu words
        # 3. Urdu Unicode character blocks (\u0600-\u06FF)
        # 4. Numbers and punctuation
        pattern = re.compile(
            r"<[A-Z_]+>|"
            r"[PBUC]\d{4}|"
            r"[\u0600-\u06FF]+|"
            r"[A-Za-z0-9_-]+|"
            r"[.,!?;:\"'()\[\]{}]"
        )
        tokens = pattern.findall(text)
        return [t.strip() for t in tokens if t.strip()]

    def build_vocab(self, texts: Iterable[str], min_freq: int = 1, max_vocab_size: int = 8000) -> None:
        """Constructs vocabulary dictionary from training texts."""
        freqs: dict[str, int] = {}
        for text in texts:
            for token in self._pre_tokenize(text):
                if token in self.SPECIAL_TOKENS:
                    continue
                # Lowercase non-DTC, non-special tokens
                key = token if re.match(r"^[PBUC]\d{4}$", token) else token.lower()
                freqs[key] = freqs.get(key, 0) + 1

        # Sort by frequency
        sorted_tokens = sorted(
            [t for t, f in freqs.items() if f >= min_freq],
            key=lambda t: (-freqs[t], t)
        )

        # Allocate IDs
        self.vocab = {}
        self.inv_vocab = {}
        for idx, token in enumerate(self.SPECIAL_TOKENS):
            self.vocab[token] = idx
            self.inv_vocab[idx] = token

        current_id = len(self.SPECIAL_TOKENS)
        for token in sorted_tokens:
            if current_id >= max_vocab_size:
                break
            self.vocab[token] = current_id
            self.inv_vocab[current_id] = token
            current_id += 1

    def encode(self, text: str, add_special_tokens: bool = False, max_length: int | None = None) -> list[int]:
        """Encodes text to a list of integer token IDs."""
        raw_tokens = self._pre_tokenize(text)
        token_ids: list[int] = []

        if add_special_tokens:
            token_ids.append(self.bos_id)

        for token in raw_tokens:
            if token in self.SPECIAL_TOKENS:
                token_ids.append(self.vocab[token])
            else:
                key = token if re.match(r"^[PBUC]\d{4}$", token) else token.lower()
                token_ids.append(self.vocab.get(key, self.unk_id))

        if add_special_tokens:
            token_ids.append(self.eos_id)

        if max_length is not None:
            if len(token_ids) > max_length:
                token_ids = token_ids[:max_length]
            else:
                token_ids.extend([self.pad_id] * (max_length - len(token_ids)))

        return token_ids

    def decode(self, token_ids: list[int], skip_special_tokens: bool = True) -> str:
        """Decodes integer token IDs back to a readable string."""
        words: list[str] = []
        for tid in token_ids:
            if tid == self.pad_id and skip_special_tokens:
                continue
            token = self.inv_vocab.get(tid, self.UNK_TOKEN)
            if skip_special_tokens and token in self.SPECIAL_TOKENS:
                continue
            words.append(token)

        # Join tokens naturally, attaching punctuation
        text = " ".join(words)
        text = re.sub(r"\s+([.,!?;:])", r"\1", text)
        return text.strip()

    def save(self, filepath: str | Path) -> None:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"vocab": self.vocab}, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, filepath: str | Path) -> AutomotiveTokenizer:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(vocab=data["vocab"])
