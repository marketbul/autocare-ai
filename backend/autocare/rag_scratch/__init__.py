"""AutoCare AI Custom RAG & Generative Token Engine built from scratch.

Components:
- AutomotiveTokenizer: Multi-lingual subword tokenizer for Urdu, Roman Urdu & English.
- AutomotiveEmbedder: Dense vector embedding model with L2 normalization.
- AutomotiveVectorStore: Hybrid vector index combining Dense Cosine Similarity and BM25.
- AutomotiveCausalLM: PyTorch Causal Self-Attention Transformer Decoder.
- AutoCareRAGFromScratch: End-to-end RAG diagnostic pipeline.
"""
from .embedding_engine import AutomotiveEmbedder
from .rag_pipeline import AutoCareRAGFromScratch, DiagnosticResponse
from .tokenizer import AutomotiveTokenizer
from .transformer_decoder import AutomotiveCausalLM, GenerativeTokenPredictor
from .vector_store import AutomotiveVectorStore

__all__ = [
    "AutomotiveTokenizer",
    "AutomotiveEmbedder",
    "AutomotiveVectorStore",
    "AutomotiveCausalLM",
    "GenerativeTokenPredictor",
    "AutoCareRAGFromScratch",
    "DiagnosticResponse",
]
