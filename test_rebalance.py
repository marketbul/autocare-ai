import os
import csv
import json
import shutil
import re

base_dir = r"C:\Users\ABDUL\.gemini\antigravity\scratch\autocare-us2"
csv_path = os.path.join(base_dir, "docs", "jira_tickets_import.csv")

with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    tickets = list(reader)

print(f"Total tickets read: {len(tickets)}")

# Domain-based mapping rules
def assign_ticket_lead(t):
    key = t.get("Issue key", "")
    summary = t.get("Summary", "").lower()
    desc = t.get("Description", "").lower()
    msg = t.get("Git Commit Message", "").lower()
    full_text = f"{summary} {desc} {msg}"

    # 1. ABDULLAH (BSDSF23A035) - AI Brain, Transformer LM, BPE, RAG Scratch, Consistent Hashing, FastApi Gateway
    if any(k in full_text for k in [
        "transformer", "bpe", "tokenizer", "rag-scratch", "causal", "autoregressive",
        "consistent hash", "hash ring", "murmur", "fastapi gateway", "microservice routing",
        "initial commit", "agents.md", "master repository", "argont", "argon2"
    ]) or key in ["AUT-104", "AUT-105", "AUT-121", "AUT-123", "AUT-124", "AUT-126", "AUT-128", "AUT-204", "AUT-205", "AUT-206"]:
        return "Abdullah (BSDSF23A035)", "EPIC-2: Distributed Hashing & Transformer AI"

    # 2. TALHA ALI BHATTI (BSDSF23A016) - Storage, Ingestion, MinIO, Parquet, Compaction, OBD-II Streamer
    if any(k in full_text for k in [
        "minio", "s3", "cas deduplication", "deduplication", "obd-ii", "can-bus", "telemetry stream",
        "parquet", "lakehouse", "compaction", "batch buffer", "multipart", "iops", "quarantine",
        "dtc", "sae j2012", "schema evolution"
    ]) or key in ["AUT-101", "AUT-102", "AUT-108", "AUT-109", "AUT-110", "AUT-111", "AUT-112", "AUT-113", "AUT-201", "AUT-202", "AUT-203"]:
        return "Talha Ali Bhatti (BSDSF23A016)", "EPIC-1: Distributed Object Storage & Ingestion"

    # 3. DANIAL HAMEED (BSDSF23A014) - Data Engineering, Manuals Chunking, Bloom Filter, Multilingual Lexicon, Collectors
    if any(k in full_text for k in [
        "bloom filter", "lexicon", "urdu", "roman urdu", "chunk", "dataset", "corpus", "manual",
        "youtube", "facebook", "whisper", "audio", "nhtsa", "stack exchange", "collector",
        "importer", "bm25", "rrf", "reciprocal rank", "media asset", "consolidat"
    ]) or key in ["AUT-103", "AUT-106", "AUT-107", "AUT-115", "AUT-122", "AUT-125", "AUT-136", "AUT-137", "AUT-209", "AUT-213"]:
        return "Danial Hameed (BSDSF23A014)", "EPIC-3: Multilingual Data Lake & Ingestion"

    # 4. AHMAD ZAHID (BSDSF23A033) - ML Triage, Safety, Platt Calibration, NLI Verifier, Fraud Detection
    if any(k in full_text for k in [
        "triage", "cost-sensitive", "calibration", "platt", "ece", "abstention", "verifier",
        "nli", "fraud", "unnecessary", "brier", "k-fold", "safety", "proposal section 17",
        "ethical", "confidence", "isolation forest", "hazard"
    ]) or key in ["AUT-107", "AUT-108", "AUT-109", "AUT-112", "AUT-132", "AUT-138", "AUT-139", "AUT-140", "AUT-141", "AUT-142", "AUT-143", "AUT-210", "AUT-214"]:
        return "Ahmad Zahid (BSDSF23A033)", "EPIC-4: Supervised ML Triage & Verification"

    # 5. MUHAMMAD ABDULLAH (BSDSF23A032) - Web Portal UI, DuckDB OLAP, PySpark, Regional PKR Pricing, Defense
    if any(k in full_text for k in [
        "portal", "ui", "screen", "frontend", "react", "dashboard", "duckdb", "olap",
        "pyspark", "spark", "pricing", "pkr", "market", "labor", "labour", "health",
        "degradation", "climate", "bento", "viewer", "pid", "slides", "presentation"
    ]) or key in ["AUT-114", "AUT-116", "AUT-117", "AUT-118", "AUT-119", "AUT-120", "AUT-127", "AUT-130", "AUT-207", "AUT-208", "AUT-211", "AUT-212"]:
        return "Muhammad Abdullah (BSDSF23A032)", "EPIC-5: Modern Web Portal & Fleet Analytics"

    # Fallback to current assignee
    curr = t.get("Assignee", "")
    return curr, t.get("Epic Link", "EPIC-1: Core System Engineering")

# Process all tickets
rebalanced = []
for t in tickets:
    new_assignee, new_epic = assign_ticket_lead(t)
    t["Assignee"] = new_assignee
    t["Epic Link"] = new_epic
    rebalanced.append(t)

# Stats after rebalancing
counts = {}
sp_counts = {}
for t in rebalanced:
    name = t["Assignee"].split()[0]
    counts[name] = counts.get(name, 0) + 1
    sp = int(t.get("Story Points", 3) or 3)
    sp_counts[name] = sp_counts.get(name, 0) + sp

print("\n--- REBALANCED TICKETS PER PERSON ---")
for name in sorted(counts.keys()):
    print(f"{name:15}: {counts[name]:2} tickets | {sp_counts[name]:3} Story Points")

print(f"Total Tickets: {sum(counts.values())} | Total SP: {sum(sp_counts.values())}")
