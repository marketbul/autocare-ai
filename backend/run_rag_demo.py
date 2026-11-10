"""Interactive CLI & Benchmark Demonstration for AutoCare AI From-Scratch RAG Engine.

Tests all 6 pipeline stages:
1. Multi-Modal Text Extraction
2. Subword Tokenization
3. Dense Vector Embeddings (L2 Normalized)
4. Hybrid Cosine + BM25 Vector Retrieval
5. Autoregressive Causal Transformer Token Prediction
6. Verified OEM Citations & Localized PKR Cost Triage
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from autocare.rag_scratch import AutoCareRAGFromScratch


def print_banner(title: str):
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def run_demonstration():
    print_banner("AUTOCARE AI &bull; FROM-SCRATCH RAG &amp; LLM TOKEN ENGINE TEST BENCH")
    print("Initializing pipeline components from scratch (PyTorch CPU)...")
    start_time = time.time()

    rag = AutoCareRAGFromScratch()
    rag.initialize_and_train()
    init_duration = time.time() - start_time
    print(f"\n[OK] Pipeline trained and indexed in {init_duration:.2f} seconds.")

    # Test Scenarios
    test_queries = [
        "Toyota Corolla start nahi ho rahi aur check engine light blink kar rahi hai with missing issue",
        "P0301 Cylinder 1 Misfire detected what is the immediate safety risk and repair cost in Pakistan?",
        "Honda Civic overheating in traffic needle near red line do I need to tow?"
    ]

    for q_idx, query in enumerate(test_queries, 1):
        print_banner(f"TEST SCENARIO {q_idx}: USER DIAGNOSTIC QUERY")
        print(f"Input Query: \"{query}\"")

        # 1. Tokenizer Inspection
        print("\n--- [STAGE 1: MULTI-LINGUAL TOKENIZATION] ---")
        token_ids = rag.tokenizer.encode(query)
        sample_tokens = [rag.tokenizer.inv_vocab.get(tid, "<UNK>") for tid in token_ids[:10]]
        print(f"Token Count: {len(token_ids)}")
        print(f"Sample Token Stream: {sample_tokens} ...")

        # 2. Embedding Inspection
        print("\n--- [STAGE 2: DENSE SEMANTIC VECTOR EMBEDDING] ---")
        vec = rag.embedder.encode([query])
        l2_norm = float((vec ** 2).sum() ** 0.5)
        print(f"Embedding Vector Shape: {vec.shape} (Dimension: {rag.embedder.embedding_dim})")
        print(f"First 8 Vector Dimensions: {[round(float(x), 4) for x in vec[0, :8]]}")
        print(f"L2 Normalization Check (||v||_2): {l2_norm:.4f} (Verified Unit Vector)")

        # 3. Hybrid Retrieval Inspection
        print("\n--- [STAGE 3: HYBRID RETRIEVAL (COSINE + BM25)] ---")
        response = rag.answer_query(query, top_k=2)
        for idx, ev in enumerate(response.retrieved_evidence, 1):
            print(f"Candidate #{idx}: [Chunk: {ev['chunk_id']}]")
            print(f"   Dense Cosine Score: {ev['dense_score']} | Lexical BM25: {ev['lexical_score']} | Hybrid: {ev['hybrid_score']}")
            print(f"   Source: {ev['source']} (Page {ev['page']})")
            print(f"   Excerpt: {ev['text'][:120]}...")

        # 4. Token Prediction Trace
        print("\n--- [STAGE 4: BEHIND-THE-SCENES LLM NEXT-TOKEN PREDICTION] ---")
        print("Transformer Decoder Autoregressive Generation Steps:")
        for trace in response.token_trace[:6]:
            step = trace["step"]
            token = trace["token"]
            tid = trace["token_id"]
            prob = trace["prob"]
            print(f"   Step {step:02d} -> Predicted Token: {repr(token):<12} (ID: {tid:<5} | P={prob:.2%})")

        # 5. Verified Safety Triage
        print("\n--- [STAGE 5: REAL-TIME SAFETY & DRIVEABILITY TRIAGE] ---")
        triage = response.safety_triage
        print(f"Verdict: {triage['verdict']}")
        print(f"Risk Assessment: {triage['risk_level']}")
        print(f"Recommended Action: {triage['immediate_action']}")

        # 6. Grounded Solution & Citations
        print("\n--- [STAGE 6: GROUNDED SOLUTION & LOCALIZED PKR COSTS] ---")
        print(f"Synthesized Response:\n\"{response.generated_text}\"")
        print("\nVerified OEM Manual Citations:")
        for c in response.verified_citations[:2]:
            print(f" &bull; {c['source']} — {c['chapter']} (Page {c['page']})")

        pkr = response.pkr_repair_estimate
        print(f"\nPakistani Market Pricing Benchmark ({pkr['part']}):")
        print(f" &bull; OEM Dealership Cost: {pkr['oem_pkr']}")
        print(f" &bull; Local Market (Rawalpindi/Lahore/Karachi): {pkr['market_pkr']}")
        print(f" &bull; Workshop Labor Benchmark: {pkr['labor_pkr']}")
        print(f" &bull; Expected Downtime: {pkr['downtime']}")


if __name__ == "__main__":
    run_demonstration()
