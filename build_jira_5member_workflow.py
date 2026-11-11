import os
import sys
import csv
import shutil
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.pdfgen import canvas

# -------------------------------------------------------------
# 5-Member Master Tickets Dataset (40 Tickets, 160 SP Total)
# -------------------------------------------------------------
TICKETS_5 = [
    # ------------------- SPRINT 1 (40 SP Total) -------------------
    # Abdullah (035) - 8 SP
    {
        "key": "AUT-104", "type": "Story", "sp": 8, "sprint": "Sprint 1",
        "assignee": "Abdullah (BSDSF23A035)", "role": "System Architect / RAG Lead",
        "epic": "EPIC-2: Distributed Hashing & Partitioning",
        "summary": "Consistent Hash Ring with 160 Virtual Nodes per Physical Node",
        "desc": "Build distributed Consistent Hash Ring in Python from scratch using MurmurHash3 across 32-bit keyspace [0, 2^32-1]. Assign 160 virtual nodes (tokens) per physical storage node to ensure uniform partition distribution (variance < 5%).",
        "ac": "Standard deviation of key distribution across storage nodes < 5%; node addition/removal re-routes only K/N keys.",
        "branch": "feature/AUT-104-consistent-hash-ring",
        "commit": "[AUT-104] feat(algorithms): consistent hash ring with 160 virtual nodes and Murmur3"
    },
    # Talha Ali Bhatti (016) - 8 SP (5 + 3)
    {
        "key": "AUT-101", "type": "Story", "sp": 5, "sprint": "Sprint 1",
        "assignee": "Talha Ali Bhatti (BSDSF23A016)", "role": "Distributed Storage & Ingestion Lead",
        "epic": "EPIC-1: Distributed Object Storage & CAS",
        "summary": "MinIO S3 Distributed Multi-Bucket Cluster Architecture",
        "desc": "Provision distributed MinIO multi-tenant object storage cluster with standard buckets: raw-telemetry, processed-parquet, model-checkpoints, and corpus-manuals. Configure IAM credentials, CORS, and lifecycle policies.",
        "ac": "MinIO S3 API accepts credentials; bucket assertions pass; concurrent PUT/GET multipart verified.",
        "branch": "feature/AUT-101-minio-cluster",
        "commit": "[AUT-101] feat(storage): provision distributed MinIO S3 cluster and bucket policies"
    },
    {
        "key": "AUT-102", "type": "Story", "sp": 3, "sprint": "Sprint 1",
        "assignee": "Talha Ali Bhatti (BSDSF23A016)", "role": "Distributed Storage & Ingestion Lead",
        "epic": "EPIC-1: Distributed Object Storage & CAS",
        "summary": "SHA-256 Content-Addressable Storage (CAS) Deduplication Engine",
        "desc": "Implement cryptographic SHA-256 content-addressable storage handler that splits raw incoming manuals and telemetry batches, computes SHA-256 hex digest, and avoids redundant uploads via content indexing.",
        "ac": "Duplicate uploads produce zero additional disk footprint; deduplication log reports > 30% byte savings.",
        "branch": "feature/AUT-102-cas-deduplication",
        "commit": "[AUT-102] feat(storage): implement SHA-256 content-addressable storage deduplication"
    },
    # Danial Hameed (014) - 8 SP (5 + 3)
    {
        "key": "AUT-115", "type": "Story", "sp": 5, "sprint": "Sprint 1",
        "assignee": "Danial Hameed (BSDSF23A014)", "role": "Data Engineering & Corpus Lead",
        "epic": "EPIC-2: Multilingual Corpus & Data Engineering",
        "summary": "Automotive Dataset Ingestion & Unified Entity Schema Standardization",
        "desc": "Ingest, clean, deduplicate, and standardize 111 dataset files across 14 categories (PakWheels, Mechanic Videos, Facebook Auto QA, OBD-II manuals, PKR pricing indices) into unified entity schemas.",
        "ac": "Clean dataset catalog saved in dataset/ and Desktop deliverable; missing values imputed; UTF-8 verified.",
        "branch": "feature/AUT-115-dataset-standardization",
        "commit": "[AUT-115] feat(data): clean, preprocess and standardize 111 automotive dataset files"
    },
    {
        "key": "AUT-103", "type": "Story", "sp": 3, "sprint": "Sprint 1",
        "assignee": "Danial Hameed (BSDSF23A014)", "role": "Data Engineering & Corpus Lead",
        "epic": "EPIC-2: Multilingual Corpus & Data Engineering",
        "summary": "Structure-Aware Technical Manual Chunking & Metadata Extraction",
        "desc": "Build PDF chunking pipeline isolating diagnostic trouble code charts, warning callouts, and repair procedures from OEM manuals across Corolla, Civic, and Swift into 512-token segments with metadata headers.",
        "ac": "Extracts 326 clean chunks preserving warning and caution blocks with exact page number citations.",
        "branch": "feature/AUT-103-manual-chunker",
        "commit": "[AUT-103] feat(ingest): structure-aware PDF chunking with OEM metadata headers"
    },
    # Ahmad Zahid (033) - 8 SP (5 + 3)
    {
        "key": "AUT-138", "type": "Story", "sp": 5, "sprint": "Sprint 1",
        "assignee": "Ahmad Zahid (BSDSF23A033)", "role": "ML Triage & Calibration Lead",
        "epic": "EPIC-4: Supervised ML Triage & Calibration",
        "summary": "Supervised Fault Category & Severity Triage Classifier",
        "desc": "Train multi-class TF-IDF + Logistic Regression triage classifier mapping user-reported complaints and active DTCs into 4 severity tiers (Critical, Major, Moderate, Minor).",
        "ac": "Model achieves Macro-F1 >= 0.85 across held-out vehicle test split; inference latency < 15ms.",
        "branch": "feature/AUT-138-triage-classifier",
        "commit": "[AUT-138] feat(ml): train supervised fault category and severity triage classifier"
    },
    {
        "key": "AUT-139", "type": "Story", "sp": 3, "sprint": "Sprint 1",
        "assignee": "Ahmad Zahid (BSDSF23A033)", "role": "ML Triage & Calibration Lead",
        "epic": "EPIC-4: Supervised ML Triage & Calibration",
        "summary": "Cost-Sensitive Loss Matrix (10x Safety Penalty on Critical Errors)",
        "desc": "Formulate and apply asymmetric cost matrix penalizing false negatives on Critical brake and engine overheating failures at 10x higher weight than false alarms.",
        "ac": "Critical False Negative Rate drops below 0.10 on benchmark test evaluation set.",
        "branch": "feature/AUT-139-cost-sensitive-matrix",
        "commit": "[AUT-139] feat(ml): cost-sensitive loss weighting with 10x safety penalty matrix"
    },
    # Muhammad Abdullah (032) - 8 SP (5 + 3)
    {
        "key": "AUT-114", "type": "Story", "sp": 5, "sprint": "Sprint 1",
        "assignee": "Muhammad Abdullah (BSDSF23A032)", "role": "Frontend, Analytics & Economics Lead",
        "epic": "EPIC-6: Analytics & Web Portal UI",
        "summary": "DuckDB In-Memory OLAP Query Engine Integration for Parquet",
        "desc": "Embed DuckDB columnar engine into backend for zero-copy SQL analytics scanning local and MinIO-hosted Parquet files for fleet aggregations, DTC frequencies, and mileage trends.",
        "ac": "Executes analytical aggregations across 500,000 rows in < 80ms; zero memory duplication between Arrow and DuckDB.",
        "branch": "feature/AUT-114-duckdb-olap",
        "commit": "[AUT-114] feat(analytics): embed DuckDB OLAP engine for zero-copy parquet querying"
    },
    {
        "key": "AUT-116", "type": "Story", "sp": 3, "sprint": "Sprint 1",
        "assignee": "Muhammad Abdullah (BSDSF23A032)", "role": "Frontend, Analytics & Economics Lead",
        "epic": "EPIC-6: Analytics & Web Portal UI",
        "summary": "PySpark Distributed DataFrame Windowed Transformations Pipeline",
        "desc": "Implement PySpark distributed processing script simulating multi-worker DataFrame transformations: windowed moving averages of coolant temperature, rolling fuel trim standard deviations, and trip segmentation.",
        "ac": "Pipeline executes on local PySpark master; writes partition-aggregated parquet tables without schema drift.",
        "branch": "feature/AUT-116-pyspark-pipeline",
        "commit": "[AUT-116] feat(analytics): PySpark distributed windowed transformations pipeline"
    },

    # ------------------- SPRINT 2 (40 SP Total) -------------------
    # Abdullah (035) - 8 SP (5 + 3)
    {
        "key": "AUT-105", "type": "Story", "sp": 5, "sprint": "Sprint 2",
        "assignee": "Abdullah (BSDSF23A035)", "role": "System Architect / RAG Lead",
        "epic": "EPIC-2: Distributed Hashing & Partitioning",
        "summary": "Consistent Hash Node Dynamic Rebalancing & Binary Ring Routing",
        "desc": "Implement binary search (bisect) ring routing with O(log M) complexity to identify target storage nodes for VIN keys. Include node join/leave dynamic rebalancing generator.",
        "ac": "Lookup latency < 0.05ms for 100K lookups; rebalance generator outputs minimal node migration diffs.",
        "branch": "feature/AUT-105-ring-rebalancing",
        "commit": "[AUT-105] feat(algorithms): bisect ring lookup and dynamic cluster rebalancing logic"
    },
    {
        "key": "AUT-128", "type": "Story", "sp": 3, "sprint": "Sprint 2",
        "assignee": "Abdullah (BSDSF23A035)", "role": "System Architect / RAG Lead",
        "epic": "EPIC-5: Causal Transformer LM & RAG",
        "summary": "FastAPI Asynchronous Gateway & Microservice Routing Architecture",
        "desc": "Implement asynchronous FastAPI server with structured dependency injection, JWT authentication, and high-concurrency connection pools for RAG and telemetry pipelines.",
        "ac": "Handles 50 concurrent requests without thread starvation; automated OpenAPI documentation verified.",
        "branch": "feature/AUT-128-fastapi-gateway",
        "commit": "[AUT-128] feat(api): asynchronous FastAPI gateway with JWT auth and OpenAPI specs"
    },
    # Talha Ali Bhatti (016) - 8 SP (5 + 3)
    {
        "key": "AUT-108", "type": "Story", "sp": 5, "sprint": "Sprint 2",
        "assignee": "Talha Ali Bhatti (BSDSF23A016)", "role": "Distributed Storage & Ingestion Lead",
        "epic": "EPIC-3: Stream Ingest & Columnar Parquet",
        "summary": "OBD-II CAN-Bus High-Velocity Telemetry Stream Generator",
        "desc": "Build high-throughput OBD-II CAN-bus telemetry stream simulator generating 10,000 events/second for Pakistani fleet vehicles (Corolla, Civic, Swift, Mehran, Alto) with synthetic fault injections.",
        "ac": "Generator sustains 10,000 messages/sec with configurable error injections (overheating, catalytic faults).",
        "branch": "feature/AUT-108-telemetry-streamer",
        "commit": "[AUT-108] feat(ingest): high-velocity OBD-II CAN-bus synthetic telemetry generator"
    },
    {
        "key": "AUT-110", "type": "Story", "sp": 3, "sprint": "Sprint 2",
        "assignee": "Talha Ali Bhatti (BSDSF23A016)", "role": "Distributed Storage & Ingestion Lead",
        "epic": "EPIC-3: Stream Ingest & Columnar Parquet",
        "summary": "Snappy Columnar Parquet Lakehouse Partitioning (Make/Model/Year/Region)",
        "desc": "Write PyArrow columnar parquet generator with Snappy compression and hierarchical partitioning scheme: /lakehouse/telemetry/make=Toyota/model=Corolla/year=2021/region=Punjab/data.parquet.",
        "ac": "Parquet files achieve > 70% compression ratio vs raw JSON; DuckDB partition pruning executes in < 50ms.",
        "branch": "feature/AUT-110-parquet-partitioning",
        "commit": "[AUT-110] feat(lakehouse): snappy columnar parquet writer with hierarchical partitioning"
    },
    # Danial Hameed (014) - 8 SP (5 + 3)
    {
        "key": "AUT-106", "type": "Story", "sp": 5, "sprint": "Sprint 2",
        "assignee": "Danial Hameed (BSDSF23A014)", "role": "Data Engineering & Corpus Lead",
        "epic": "EPIC-2: Multilingual Corpus & Data Engineering",
        "summary": "Counting Bloom Filter for O(1) Set Membership & Redundant I/O Gate",
        "desc": "Implement memory-efficient Counting Bloom Filter using k independent hash functions (double-hashing with Murmur3) and bit array sized for 100K DTC items to eliminate redundant disk queries.",
        "ac": "Zero false negatives under all test cases; empirical false positive rate <= 1.0% matching theoretical bound.",
        "branch": "feature/AUT-106-bloom-filter",
        "commit": "[AUT-106] feat(algorithms): counting bloom filter with k-hash double-hashing gate"
    },
    {
        "key": "AUT-107", "type": "Story", "sp": 3, "sprint": "Sprint 2",
        "assignee": "Danial Hameed (BSDSF23A014)", "role": "Data Engineering & Corpus Lead",
        "epic": "EPIC-2: Multilingual Corpus & Data Engineering",
        "summary": "Bloom Filter Bit-Array Serialization & Redis State Sync",
        "desc": "Implement binary serialization of Bloom Filter bit-vectors to disk and asynchronous synchronization to Redis for multi-node state replication across worker pods.",
        "ac": "Filter restores from snapshot in < 10ms; byte representation fits within 120 KB memory footprint for 100K items.",
        "branch": "feature/AUT-107-bloom-serialization",
        "commit": "[AUT-107] feat(algorithms): bloom filter binary serialization and snapshot restore"
    },
    # Ahmad Zahid (033) - 8 SP (5 + 3)
    {
        "key": "AUT-140", "type": "Story", "sp": 5, "sprint": "Sprint 2",
        "assignee": "Ahmad Zahid (BSDSF23A033)", "role": "ML Triage & Calibration Lead",
        "epic": "EPIC-4: Supervised ML Triage & Calibration",
        "summary": "Platt Scaling & Temperature Confidence Calibration (ECE Optimization)",
        "desc": "Apply Platt scaling (sigmoid regression on log-odds) and temperature scaling to align raw model probabilities with empirical accuracy. Measure Expected Calibration Error (ECE) and Brier Score.",
        "ac": "Expected Calibration Error reduced from 0.18 to < 0.05 on held-out validation cases.",
        "branch": "feature/AUT-140-confidence-calibration",
        "commit": "[AUT-140] feat(calibration): implement Platt scaling and Expected Calibration Error (ECE) minimizer"
    },
    {
        "key": "AUT-141", "type": "Story", "sp": 3, "sprint": "Sprint 2",
        "assignee": "Ahmad Zahid (BSDSF23A033)", "role": "ML Triage & Calibration Lead",
        "epic": "EPIC-4: Supervised ML Triage & Calibration",
        "summary": "Grouped K-Fold Cross-Validation Protocol across Vehicle Models",
        "desc": "Implement Grouped K-Fold cross-validation partitioning folds strictly by vehicle chassis/model to verify out-of-domain generalization without data leakage across vehicle generations.",
        "ac": "Cross-validation runs without vehicle leakage; reports mean and standard deviation of accuracy across 5 folds.",
        "branch": "feature/AUT-141-grouped-kfold",
        "commit": "[AUT-141] test(ml): implement Grouped K-Fold validation across vehicle chassis groups"
    },
    # Muhammad Abdullah (032) - 8 SP (5 + 3)
    {
        "key": "AUT-117", "type": "Story", "sp": 5, "sprint": "Sprint 2",
        "assignee": "Muhammad Abdullah (BSDSF23A032)", "role": "Frontend, Analytics & Economics Lead",
        "epic": "EPIC-6: Analytics & Web Portal UI",
        "summary": "Fleet Diagnostic Trouble Code (DTC) Anomaly Detection Model",
        "desc": "Train unsupervised anomaly detection model (Isolation Forest + Rolling Z-Score) on multivariate OBD-II time-series (RPM, Speed, Throttle, STFT) to detect precursor states before DTC trip.",
        "ac": "Model achieves F1-Score >= 0.88 on identifying cooling system leaks and misfire precursors on test datasets.",
        "branch": "feature/AUT-117-anomaly-detector",
        "commit": "[AUT-117] feat(ml): unsupervised Isolation Forest anomaly detection for OBD-II telemetry"
    },
    {
        "key": "AUT-118", "type": "Story", "sp": 3, "sprint": "Sprint 2",
        "assignee": "Muhammad Abdullah (BSDSF23A032)", "role": "Frontend, Analytics & Economics Lead",
        "epic": "EPIC-6: Analytics & Web Portal UI",
        "summary": "Regional Component Degradation & Pakistani Climate Risk Multipliers",
        "desc": "Formulate empirical component degradation algorithms accounting for extreme Pakistani operational environments (45C Lahore/Multan summers, dusty roads, adulterated fuel quality).",
        "ac": "Algorithm shifts maintenance intervals by -25% for severe climate; produces calibrated health scores (0-100%).",
        "branch": "feature/AUT-118-climate-wear-engine",
        "commit": "[AUT-118] feat(analytics): regional climate risk multipliers and component wear equations"
    },

    # ------------------- SPRINT 3 (40 SP Total) -------------------
    # Abdullah (035) - 8 SP (5 + 3)
    {
        "key": "AUT-121", "type": "Story", "sp": 5, "sprint": "Sprint 3",
        "assignee": "Abdullah (BSDSF23A035)", "role": "System Architect / RAG Lead",
        "epic": "EPIC-5: Causal Transformer LM & RAG",
        "summary": "Custom Subword Byte-Pair Encoding (BPE) Tokenizer from Scratch",
        "desc": "Build automotive subword BPE Tokenizer in pure Python from scratch without external libraries. Learn merge pairs from bilingual automotive corpus (English, Urdu, Roman Urdu). Vocab size: 4,000 tokens.",
        "ac": "Tokenizer compresses automotive terms (radiator, catalytic, dhuwan); encode/decode roundtrips with 100% byte fidelity.",
        "branch": "feature/AUT-121-bpe-tokenizer",
        "commit": "[AUT-121] feat(rag-scratch): subword BPE tokenizer with 4000 vocab and special tokens"
    },
    {
        "key": "AUT-123", "type": "Story", "sp": 3, "sprint": "Sprint 3",
        "assignee": "Abdullah (BSDSF23A035)", "role": "System Architect / RAG Lead",
        "epic": "EPIC-5: Causal Transformer LM & RAG",
        "summary": "4-Layer Causal Transformer Decoder with Multi-Head Self-Attention",
        "desc": "Construct 4-layer Causal Transformer Decoder (1,321,728 parameters) in PyTorch from scratch. Implement multi-head self-attention (n_heads=4, d_model=128, d_ff=512), positional embeddings, and causal triangular masking.",
        "ac": "Causal mask strictly prohibits future token attention; compiles cleanly and outputs logit distributions over 4,000 vocab.",
        "branch": "feature/AUT-123-transformer-decoder",
        "commit": "[AUT-123] feat(rag-scratch): 4-layer causal transformer decoder with multi-head attention"
    },
    # Talha Ali Bhatti (016) - 8 SP (5 + 3)
    {
        "key": "AUT-109", "type": "Story", "sp": 5, "sprint": "Sprint 3",
        "assignee": "Talha Ali Bhatti (BSDSF23A016)", "role": "Distributed Storage & Ingestion Lead",
        "epic": "EPIC-3: Stream Ingest & Columnar Parquet",
        "summary": "In-Memory Sliding-Window Batch Buffer & Ingestion Sink",
        "desc": "Build sliding-window batching sink consuming high-frequency telemetry events, buffering in memory over 1-second or 5,000-record windows, validating schema, and flushing to parquet.",
        "ac": "Zero memory leaks over 1-hour continuous simulation; buffer backpressure drops 0 valid packets.",
        "branch": "feature/AUT-109-batch-buffer",
        "commit": "[AUT-109] feat(ingest): sliding-window telemetry buffer and micro-batch flusher"
    },
    {
        "key": "AUT-111", "type": "Story", "sp": 3, "sprint": "Sprint 3",
        "assignee": "Talha Ali Bhatti (BSDSF23A016)", "role": "Distributed Storage & Ingestion Lead",
        "epic": "EPIC-3: Stream Ingest & Columnar Parquet",
        "summary": "Automated Parquet Compaction Job & Small File Merging Engine",
        "desc": "Develop scheduled background compaction task merging micro-batch parquet files (< 16MB) into optimal 128MB analytical lakehouse chunks to prevent S3 small-file fragmentation.",
        "ac": "Merges 100 small parquet files into 1 consolidated chunk; row count and checksum match perfectly.",
        "branch": "feature/AUT-111-parquet-compaction",
        "commit": "[AUT-111] feat(lakehouse): parquet small-file compaction and catalog vacuum engine"
    },
    # Danial Hameed (014) - 8 SP (5 + 3)
    {
        "key": "AUT-136", "type": "Story", "sp": 5, "sprint": "Sprint 3",
        "assignee": "Danial Hameed (BSDSF23A014)", "role": "Data Engineering & Corpus Lead",
        "epic": "EPIC-2: Multilingual Corpus & Data Engineering",
        "summary": "Multilingual Automotive Lexicon (Urdu & Roman Urdu to Standard DTCs)",
        "desc": "Build comprehensive bilingual automotive glossary mapping Pakistani colloquial mechanic terminology (e.g., dhuwan, awaz, garam, jhatka, missing) into standard SAE J2012 fault taxonomies.",
        "ac": "Successfully maps 150+ informal mechanical terms to formal technical ontology with synonym resolution.",
        "branch": "feature/AUT-136-multilingual-lexicon",
        "commit": "[AUT-136] feat(nlp): bilingual Urdu and Roman Urdu automotive mechanical term translator"
    },
    {
        "key": "AUT-122", "type": "Story", "sp": 3, "sprint": "Sprint 3",
        "assignee": "Danial Hameed (BSDSF23A014)", "role": "Data Engineering & Corpus Lead",
        "epic": "EPIC-2: Multilingual Corpus & Data Engineering",
        "summary": "Dense L2-Normalized Vector Embedding Neural Network (D=128)",
        "desc": "Implement trainable Dense Embedding Neural Network in PyTorch (D=128, unit L2 normalization). Maps tokenized chunks into continuous metric space where automotive symptoms and faults cluster closely.",
        "ac": "Vector dot product matches cosine similarity on unit sphere; forward pass takes < 2ms per sentence batch.",
        "branch": "feature/AUT-122-vector-embedder",
        "commit": "[AUT-122] feat(rag-scratch): dense L2-normalized vector embedding neural network (D=128)"
    },
    # Ahmad Zahid (033) - 8 SP (5 + 3)
    {
        "key": "AUT-132", "type": "Story", "sp": 5, "sprint": "Sprint 3",
        "assignee": "Ahmad Zahid (BSDSF23A033)", "role": "ML Triage & Calibration Lead",
        "epic": "EPIC-4: Supervised ML Triage & Calibration",
        "summary": "Workshop Repair Invoice Verifier & Non-Accusatory NLI Engine",
        "desc": "Implement natural language inference (NLI) cross-checking engine validating workshop estimate line-items against OEM diagnostic procedures, providing neutral, evidence-backed verdicts.",
        "ac": "Returns Supported, Partially Supported, or Unsupported verdicts accompanied by exact manual citations.",
        "branch": "feature/AUT-132-repair-verifier",
        "commit": "[AUT-132] feat(verifier): non-accusatory workshop invoice verifier with NLI evidence cross-check"
    },
    {
        "key": "AUT-142", "type": "Story", "sp": 3, "sprint": "Sprint 3",
        "assignee": "Ahmad Zahid (BSDSF23A033)", "role": "ML Triage & Calibration Lead",
        "epic": "EPIC-4: Supervised ML Triage & Calibration",
        "summary": "Repair Fraud & Unnecessary Parts Replacement Detection Heuristics",
        "desc": "Construct rule-based and anomaly scoring heuristics detecting predatory workshop practices (e.g. charging for throttle body replacement when simple cleaning was mandated by manual).",
        "ac": "Flags 94% of synthetic over-repair scenarios without generating false accusations against honest workshops.",
        "branch": "feature/AUT-142-fraud-heuristics",
        "commit": "[AUT-142] feat(verifier): predatory repair detection heuristics and consumer protection rules"
    },
    # Muhammad Abdullah (032) - 8 SP (5 + 3)
    {
        "key": "AUT-119", "type": "Task", "sp": 5, "sprint": "Sprint 3",
        "assignee": "Muhammad Abdullah (BSDSF23A032)", "role": "Frontend, Analytics & Economics Lead",
        "epic": "EPIC-6: Analytics & Web Portal UI",
        "summary": "DuckDB OLAP Benchmark vs Traditional Relational SQL (15x Speedup)",
        "desc": "Conduct comparative benchmark measuring query execution time of DuckDB (Parquet columnar) against SQLite/Postgres for 10 analytical fleet queries (group-bys, filters, window functions).",
        "ac": "DuckDB demonstrates > 15x speedup on multi-column group-bys; benchmarking table and speedup graph generated.",
        "branch": "feature/AUT-119-olap-benchmarks",
        "commit": "[AUT-119] test(benchmark): comparative query latency benchmark of DuckDB vs SQLite"
    },
    {
        "key": "AUT-120", "type": "Story", "sp": 3, "sprint": "Sprint 3",
        "assignee": "Muhammad Abdullah (BSDSF23A032)", "role": "Frontend, Analytics & Economics Lead",
        "epic": "EPIC-6: Analytics & Web Portal UI",
        "summary": "Pakistani Fair-Price Market Estimator (PKR Parts & Mechanic Labor)",
        "desc": "Build PKR cost estimation module calculating OEM parts costs, genuine market replacement costs, and reasonable mechanic labor hours across Pakistani workshops (Lahore, Karachi, Islamabad).",
        "ac": "Returns low-median-high price ranges for top 50 common repairs; flagged workshop verifier detects overcharging > 35%.",
        "branch": "feature/AUT-120-pak-pricing-model",
        "commit": "[AUT-120] feat(pricing): localized PKR parts and mechanic labor fair-price estimator"
    },

    # ------------------- SPRINT 4 (40 SP Total) -------------------
    # Abdullah (035) - 8 SP (5 + 3)
    {
        "key": "AUT-124", "type": "Story", "sp": 5, "sprint": "Sprint 4",
        "assignee": "Abdullah (BSDSF23A035)", "role": "System Architect / RAG Lead",
        "epic": "EPIC-5: Causal Transformer LM & RAG",
        "summary": "Autoregressive LM Training Pipeline with AdamW & Perplexity Optimization",
        "desc": "Develop PyTorch training pipeline training Causal Transformer LM over 3 epochs on 10,784 automotive diagnostic pairs with AdamW (lr=1e-3, weight decay 0.01) and Perplexity metric tracking.",
        "ac": "Training loss drops monotonically from 3.11 to 2.24; test perplexity drops from 22.61 to 9.48; weights saved in weights/.",
        "branch": "feature/AUT-124-autoregressive-training",
        "commit": "[AUT-124] feat(rag-scratch): autoregressive LM training pipeline with AdamW and Perplexity tracking"
    },
    {
        "key": "AUT-126", "type": "Story", "sp": 3, "sprint": "Sprint 4",
        "assignee": "Abdullah (BSDSF23A035)", "role": "System Architect / RAG Lead",
        "epic": "EPIC-5: Causal Transformer LM & RAG",
        "summary": "Multilingual Grounded RAG Generation & Anti-Hallucination Pipeline",
        "desc": "Wire vector retrieval engine into Causal Transformer LM. Condition answer generation on retrieved chunks (<ctx>...<ans>...). Enforce strict ground-truth attribution checks and citations.",
        "ac": "Answers generate verified OEM citations (page, section); outputs fair PKR estimates; zero uncited claims.",
        "branch": "feature/AUT-126-grounded-rag-pipeline",
        "commit": "[AUT-126] feat(rag-scratch): end-to-end grounded RAG generation with selective abstention"
    },
    # Talha Ali Bhatti (016) - 8 SP (5 + 3)
    {
        "key": "AUT-113", "type": "Task", "sp": 5, "sprint": "Sprint 4",
        "assignee": "Talha Ali Bhatti (BSDSF23A016)", "role": "Distributed Storage & Ingestion Lead",
        "epic": "EPIC-3: Stream Ingest & Columnar Parquet",
        "summary": "Storage IOPS & Ingestion Latency Percentile Benchmark Profiler",
        "desc": "Construct automated benchmarking script profiling MinIO S3 write throughput (MB/s), ingestion latency percentiles (p50, p95, p99), and disk IOPS across raw JSON vs Snappy Parquet.",
        "ac": "Benchmark report logged with markdown output and latency histograms confirming p95 < 120ms.",
        "branch": "feature/AUT-113-storage-benchmarks",
        "commit": "[AUT-113] perf(storage): automated IOPS and ingestion latency benchmarking suite"
    },
    {
        "key": "AUT-112", "type": "Story", "sp": 3, "sprint": "Sprint 4",
        "assignee": "Talha Ali Bhatti (BSDSF23A016)", "role": "Distributed Storage & Ingestion Lead",
        "epic": "EPIC-3: Stream Ingest & Columnar Parquet",
        "summary": "Lakehouse Schema Evolution & Corrupt Record Dead-Letter Sink",
        "desc": "Add dynamic schema evolution handling to parquet writer. Detect new sensor fields and route malformed/corrupted OBD-II records to dead-letter quarantine bucket (raw-quarantine/).",
        "ac": "Unrecognized fields backward-compatible without job failure; corrupt records isolated and tagged.",
        "branch": "feature/AUT-112-schema-evolution",
        "commit": "[AUT-112] feat(lakehouse): schema evolution handler and dead-letter quarantine sink"
    },
    # Danial Hameed (014) - 8 SP (5 + 3)
    {
        "key": "AUT-125", "type": "Story", "sp": 5, "sprint": "Sprint 4",
        "assignee": "Danial Hameed (BSDSF23A014)", "role": "Data Engineering & Corpus Lead",
        "epic": "EPIC-2: Multilingual Corpus & Data Engineering",
        "summary": "Hybrid Vector Store (Dense Cosine Similarity + BM25 Lexical Ranking)",
        "desc": "Build in-memory hybrid search vector store indexing 17,390 chunked passages from OEM manuals, PakWheels discussions, and mechanic interviews. Combine dense cosine similarity (0.65) with BM25 lexical term frequency (0.35).",
        "ac": "Query retrieval latency < 15ms; top-5 recall >= 92% on standard vehicle symptom queries.",
        "branch": "feature/AUT-125-hybrid-vector-store",
        "commit": "[AUT-125] feat(rag-scratch): hybrid dense vector + BM25 lexical retrieval engine"
    },
    {
        "key": "AUT-137", "type": "Story", "sp": 3, "sprint": "Sprint 4",
        "assignee": "Danial Hameed (BSDSF23A014)", "role": "Data Engineering & Corpus Lead",
        "epic": "EPIC-2: Multilingual Corpus & Data Engineering",
        "summary": "Reciprocal Rank Fusion (RRF) & Context Re-Ranking Layer",
        "desc": "Implement Reciprocal Rank Fusion (RRF) with k=60 to fuse BM25 and dense embedding candidate lists into unified ranked context windows for LM prompt ingestion.",
        "ac": "RRF ranking outperforms standalone dense or lexical retrieval by +6.4% on Recall@5 across technical queries.",
        "branch": "feature/AUT-137-reciprocal-rank-fusion",
        "commit": "[AUT-137] feat(retrieval): Reciprocal Rank Fusion (RRF) multi-list reranking layer"
    },
    # Ahmad Zahid (033) - 8 SP (5 + 3)
    {
        "key": "AUT-143", "type": "Story", "sp": 5, "sprint": "Sprint 4",
        "assignee": "Ahmad Zahid (BSDSF23A033)", "role": "ML Triage & Calibration Lead",
        "epic": "EPIC-4: Supervised ML Triage & Calibration",
        "summary": "Selective Abstention Gate & Uncertainty Threshold Governance",
        "desc": "Implement strict selective abstention gate. If top retrieval similarity < 0.35 or calibrated confidence < 0.70, system abstains safely with structured guidance rather than hallucinating dangerous repair advice.",
        "ac": "Zero hallucinated critical repair procedures on out-of-scope queries; abstention log records trigger reason.",
        "branch": "feature/AUT-143-selective-abstention",
        "commit": "[AUT-143] feat(safety): selective abstention gate and confidence threshold governance"
    },
    {
        "key": "AUT-129", "type": "Task", "sp": 3, "sprint": "Sprint 4",
        "assignee": "Ahmad Zahid (BSDSF23A033)", "role": "ML Triage & Calibration Lead",
        "epic": "EPIC-4: Supervised ML Triage & Calibration",
        "summary": "End-to-End System Safety Validation & Pytest Test Suite",
        "desc": "Construct automated end-to-end integration test suite verifying that all safety-critical triage and abstention invariants hold across all supported vehicle models and edge cases.",
        "ac": "pytest executes 30+ test cases with 100% pass rate; all safety boundaries verified.",
        "branch": "feature/AUT-129-safety-tests",
        "commit": "[AUT-129] test(safety): complete pytest test suite for triage safety and abstention gates"
    },
    # Muhammad Abdullah (032) - 8 SP (5 + 3)
    {
        "key": "AUT-127", "type": "Story", "sp": 5, "sprint": "Sprint 4",
        "assignee": "Muhammad Abdullah (BSDSF23A032)", "role": "Frontend, Analytics & Economics Lead",
        "epic": "EPIC-6: Analytics & Web Portal UI",
        "summary": "Modern Automotive Diagnostic Web Portal Redesign (React 18 + Tailwind)",
        "desc": "Transform frontend from dense dashboard widgets into a professional automotive web portal. Implement 6 comprehensive architectural sections: Hero with live ticker, Diagnostic Terminal, 4-Stage Architecture, Scenarios, Fair Price Estimator, and Academic Footer.",
        "ac": "Responsive mobile/desktop layout; dark modern palette with emerald/amber accents; zero console runtime errors; Vite build succeeds.",
        "branch": "feature/AUT-127-web-portal-redesign",
        "commit": "[AUT-127] feat(frontend): modern automotive engineering web portal with diagnostic terminal"
    },
    {
        "key": "AUT-130", "type": "Story", "sp": 3, "sprint": "Sprint 4",
        "assignee": "Muhammad Abdullah (BSDSF23A032)", "role": "Frontend, Analytics & Economics Lead",
        "epic": "EPIC-6: Analytics & Web Portal UI",
        "summary": "Final Academic Project Initiation Document (PID) & Defense Presentation",
        "desc": "Draft and compile comprehensive 4-week Big Data Project Initiation Document (PID) in professional .docx and .pdf formats conforming to PUCIT academic guidelines, complete with system architecture flowcharts, WBS, and performance metrics.",
        "ac": "Professional PDF and DOCX generated in deliverables folder; verified formatting, headers, tables, and academic citations.",
        "branch": "docs/AUT-130-academic-pid",
        "commit": "[AUT-130] docs(academic): generate professional 4-week Big Data PID in PDF and Word"
    }
]

# -------------------------------------------------------------
# 1. Export 5-Member Jira CSV
# -------------------------------------------------------------
def export_5member_csv(filepath):
    fieldnames = [
        "Issue Type", "Issue key", "Summary", "Description", "Epic Link",
        "Story Points", "Assignee", "Reporter", "Priority", "Status",
        "Sprint", "Acceptance Criteria", "Git Branch", "Commit Tag"
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for t in TICKETS_5:
            writer.writerow({
                "Issue Type": t["type"],
                "Issue key": t["key"],
                "Summary": t["summary"],
                "Description": t["desc"],
                "Epic Link": t["epic"],
                "Story Points": t["sp"],
                "Assignee": t["assignee"],
                "Reporter": "Abdullah (BSDSF23A035)",
                "Priority": "Highest" if t["sp"] >= 5 else "High",
                "Status": "Done",
                "Sprint": t["sprint"],
                "Acceptance Criteria": t["ac"],
                "Git Branch": t["branch"],
                "Commit Tag": t["commit"]
            })
    print(f"[OK] Exported 5-Member Jira CSV: {filepath}")

# -------------------------------------------------------------
# 2. Build 5-Member DOCX Document
# -------------------------------------------------------------
def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color_hex="CBD5E1"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="{color_hex}"/>'
        f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="{color_hex}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color_hex}"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def build_5member_docx(filepath):
    doc = Document()
    
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)
        
    normal = doc.styles['Normal']
    normal.font.name = 'Calibri'
    normal.font.size = Pt(10)
    normal.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
    normal.paragraph_format.line_spacing = 1.15
    normal.paragraph_format.space_after = Pt(4)

    # Top tracker
    p_badge = doc.add_paragraph()
    r_badge = p_badge.add_run("5-MEMBER AGILE SCRUM SPECIFICATION • DEPARTMENT OF DATA SCIENCE (PUCIT)")
    r_badge.font.name = 'Arial'
    r_badge.font.size = Pt(8.5)
    r_badge.font.bold = True
    r_badge.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    # Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(2)
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run("AutoCare AI: 5-Member Jira Sprint Backlog & WBS")
    r_title.font.name = 'Arial'
    r_title.font.size = Pt(20)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(14)
    r_sub = p_sub.add_run("Equally Balanced Work Breakdown: 32 SP per Member | 4 Sprints | 160 Total Story Points | Jira & Git Traceability")
    r_sub.font.size = Pt(10.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    # Meta Table
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Institution & Degree", "Punjab University College of Information Technology (PUCIT) — BS Data Science"),
        ("Project Key & Repo", "Key: AUT | GitHub: https://github.com/marketbul/autocare-ai.git"),
        ("5 Team Members", "Abdullah (035), Talha Ali Bhatti (016), Danial Hameed (014), Ahmad Zahid (033), Muhammad Abdullah (032)"),
        ("Total Story Points", "160 SP Total (Exactly 32 SP per member, 8 SP per member per sprint, 100% Balanced)")
    ]
    for i, (k, v) in enumerate(meta_data):
        row = meta_table.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(1.8)
        c1.width = Inches(5.0)
        c0.paragraphs[0].text = k
        c0.paragraphs[0].runs[0].font.bold = True
        c0.paragraphs[0].runs[0].font.size = Pt(9.5)
        c0.paragraphs[0].runs[0].font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        c1.paragraphs[0].text = v
        c1.paragraphs[0].runs[0].font.size = Pt(9.5)
        set_cell_background(c0, "F8FAFC")
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, 60, 60, 80, 80)
        set_cell_margins(c1, 60, 60, 80, 80)
    set_table_borders(meta_table)

    # Heading 1: Member Roster
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    h1 = doc.add_paragraph()
    r = h1.add_run("1. 5-Member Engineering Roles & Core Ownership")
    r.font.name = 'Arial'; r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    roster_table = doc.add_table(rows=6, cols=5)
    roster_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    rheaders = ["Student Name", "Roll No", "Primary Role", "Assigned Epics", "Total SP"]
    for j, h in enumerate(rheaders):
        cell = roster_table.rows[0].cells[j]
        cell.paragraphs[0].text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9)
        set_cell_background(cell, "0F172A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_margins(cell, 80, 80, 70, 70)

    roster_rows = [
        ("Abdullah (Lead)", "BSDSF23A035", "System Architect & RAG Lead", "EPIC-2 (Hashing), EPIC-5 (Transformer LM)", "32 SP"),
        ("Talha Ali Bhatti", "BSDSF23A016", "Distributed Storage & Ingestion", "EPIC-1 (MinIO/CAS), EPIC-3 (Parquet Ingest)", "32 SP"),
        ("Danial Hameed", "BSDSF23A014", "Data Engineering & Corpus Lead", "EPIC-2 (Bloom Gate), EPIC-2 (Dataset & Lexicon)", "32 SP"),
        ("Ahmad Zahid", "BSDSF23A033", "ML Triage & Calibration Lead", "EPIC-4 (Triage ML, Calibration, NLI Verifier)", "32 SP"),
        ("Muhammad Abdullah", "BSDSF23A032", "Frontend, Analytics & Economics", "EPIC-6 (DuckDB OLAP, Web Portal UI, Pricing)", "32 SP"),
    ]
    for i, rdata in enumerate(roster_rows):
        row = roster_table.rows[i+1]
        for j, text in enumerate(rdata):
            cell = row.cells[j]
            cell.paragraphs[0].text = text
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)
            if j in [0, 4]:
                cell.paragraphs[0].runs[0].font.bold = True
            bg = "F8FAFC" if i % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 70, 70)
    set_table_borders(roster_table)

    # Heading 2: Sprint Velocity
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    h2 = doc.add_paragraph()
    r = h2.add_run("2. 4-Week Sprint Schedule & Velocity Allocation (160 SP)")
    r.font.name = 'Arial'; r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    sprint_table = doc.add_table(rows=6, cols=8)
    sprint_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sheaders = ["Sprint", "Timeline", "Abdullah", "Talha", "Danial", "Ahmad", "M. Abd", "Total SP"]
    for j, h in enumerate(sheaders):
        cell = sprint_table.rows[0].cells[j]
        cell.paragraphs[0].text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(8.5)
        set_cell_background(cell, "1E293B")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_margins(cell, 70, 70, 50, 50)
    
    sprint_data = [
        ("Sprint 1", "Days 1–7 (Foundation)", "8 SP", "8 SP", "8 SP", "8 SP", "8 SP", "40 SP"),
        ("Sprint 2", "Days 8–14 (Ingest & Bloom)", "8 SP", "8 SP", "8 SP", "8 SP", "8 SP", "40 SP"),
        ("Sprint 3", "Days 15–21 (Transformer LM)", "8 SP", "8 SP", "8 SP", "8 SP", "8 SP", "40 SP"),
        ("Sprint 4", "Days 22–28 (RAG & Portal UI)", "8 SP", "8 SP", "8 SP", "8 SP", "8 SP", "40 SP"),
        ("Total", "4 Weeks (Defense Ready)", "32 SP", "32 SP", "32 SP", "32 SP", "32 SP", "160 SP")
    ]
    for i, sdata in enumerate(sprint_data):
        row = sprint_table.rows[i+1]
        for j, text in enumerate(sdata):
            cell = row.cells[j]
            cell.paragraphs[0].text = text
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)
            if i == 4 or j in [0, 7]:
                cell.paragraphs[0].runs[0].font.bold = True
            bg = "E2E8F0" if i == 4 else ("F8FAFC" if i % 2 == 1 else "FFFFFF")
            set_cell_background(cell, bg)
            set_cell_margins(cell, 50, 50, 50, 50)
    set_table_borders(sprint_table)

    # Heading 3: Full Backlog
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    h3 = doc.add_paragraph()
    r = h3.add_run("3. Complete 5-Member Jira Ticket Catalog (40 Tickets, AUT-101 to AUT-143)")
    r.font.name = 'Arial'; r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    ticket_table = doc.add_table(rows=len(TICKETS_5)+1, cols=6)
    ticket_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    theaders = ["Key", "Sprint", "Summary", "SP", "Assignee", "Status"]
    for j, h in enumerate(theaders):
        cell = ticket_table.rows[0].cells[j]
        cell.paragraphs[0].text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9)
        set_cell_background(cell, "0F172A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_margins(cell, 70, 70, 50, 50)

    for i, t in enumerate(TICKETS_5):
        row = ticket_table.rows[i+1]
        row_vals = [
            t["key"],
            t["sprint"],
            t["summary"],
            f"{t['sp']} SP",
            t["assignee"].split()[0], # Short name
            "Done"
        ]
        for j, text in enumerate(row_vals):
            cell = row.cells[j]
            cell.paragraphs[0].text = text
            cell.paragraphs[0].runs[0].font.size = Pt(8)
            if j in [0, 3]:
                cell.paragraphs[0].runs[0].font.bold = True
            bg = "F8FAFC" if i % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, 45, 45, 50, 50)
    set_table_borders(ticket_table)

    doc.save(filepath)
    print(f"[OK] Saved 5-Member DOCX: {filepath}")

# -------------------------------------------------------------
# 3. Build 5-Member PDF Document
# -------------------------------------------------------------
class NumberedCanvas5(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas5, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas5, self).showPage()
        super(NumberedCanvas5, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "AutoCare AI — 5-Member Jira Scrum Backlog & Work Breakdown")
            self.drawRightString(letter[0] - 54, letter[1] - 36, "PUCIT • BS Data Science")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)
            
        # Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawString(54, 34, "AutoCare AI — 5 Members (32 SP each) | Key: AUT | 160 Story Points Total")
        self.drawRightString(letter[0] - 54, 34, page_str)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 46, letter[0] - 54, 46)
        self.restoreState()

def build_5member_pdf(filepath):
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    style_badge = ParagraphStyle('Badge', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor('#0284C7'), spaceAfter=4)
    style_title = ParagraphStyle('MainTitle', fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#0F172A'), spaceAfter=4)
    style_sub = ParagraphStyle('SubTitle', fontName='Helvetica-Oblique', fontSize=9.5, leading=13, textColor=colors.HexColor('#64748B'), spaceAfter=12)
    style_h1 = ParagraphStyle('SectionH1', fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=colors.HexColor('#0F172A'), spaceBefore=10, spaceAfter=6)
    style_body = ParagraphStyle('Body', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#334155'))
    style_th = ParagraphStyle('TableHeader', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.white)
    style_td = ParagraphStyle('TableCell', fontName='Helvetica', fontSize=7, leading=9, textColor=colors.HexColor('#1E293B'))
    style_td_bold = ParagraphStyle('TableCellBold', fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=colors.HexColor('#0F172A'))

    elements = []

    # Title Header
    elements.append(Paragraph("5-MEMBER AGILE SCRUM SPECIFICATION • DEPARTMENT OF DATA SCIENCE (PUCIT)", style_badge))
    elements.append(Paragraph("AutoCare AI: 5-Member Jira Sprint Backlog & WBS", style_title))
    elements.append(Paragraph("Formal Distribution across 5 Students (32 SP Each) | 4 Sprints | 160 Story Points Total", style_sub))

    # Meta Table
    meta_data = [
        [Paragraph("<b>Academic Scope:</b>", style_td_bold), Paragraph("PUCIT BS Data Science Final Year Project / Big Data Systems", style_td)],
        [Paragraph("<b>Jira Key & Repo:</b>", style_td_bold), Paragraph("Key: <b>AUT</b> | Remote: github.com/marketbul/autocare-ai.git", style_td)],
        [Paragraph("<b>5 Team Members:</b>", style_td_bold), Paragraph("Abdullah (035), Talha (016), Danial (014), Ahmad (033), M. Abdullah (032)", style_td)],
        [Paragraph("<b>Velocity & Balance:</b>", style_td_bold), Paragraph("160 SP Total | Exactly 32 SP per member (8 SP per sprint) | 100% Balanced", style_td)]
    ]
    t_meta = Table(meta_data, colWidths=[110, 394])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_meta)
    elements.append(Spacer(1, 8))

    # Section 1: Roster
    elements.append(Paragraph("1. 5-Member Engineering Roles & Core Ownership", style_h1))
    roster_data = [
        [Paragraph("Member", style_th), Paragraph("Roll No", style_th), Paragraph("Primary Role", style_th), Paragraph("Assigned Epics", style_th), Paragraph("Total SP", style_th)],
        [Paragraph("Abdullah (Lead)", style_td_bold), Paragraph("BSDSF23A035", style_td), Paragraph("System Architect & RAG", style_td), Paragraph("Consistent Hashing, Causal Transformer LM", style_td), Paragraph("<b>32 SP</b>", style_td)],
        [Paragraph("Talha Ali Bhatti", style_td_bold), Paragraph("BSDSF23A016", style_td), Paragraph("Storage & Ingestion", style_td), Paragraph("MinIO S3, CAS Deduplication, Parquet Lakehouse", style_td), Paragraph("<b>32 SP</b>", style_td)],
        [Paragraph("Danial Hameed", style_td_bold), Paragraph("BSDSF23A014", style_td), Paragraph("Data & Multilingual", style_td), Paragraph("Dataset Ingestion, Bloom Filter, Bilingual Lexicon", style_td), Paragraph("<b>32 SP</b>", style_td)],
        [Paragraph("Ahmad Zahid", style_td_bold), Paragraph("BSDSF23A033", style_td), Paragraph("ML Triage & Calib", style_td), Paragraph("Cost-Sensitive Triage, Platt Scaling, NLI Verifier", style_td), Paragraph("<b>32 SP</b>", style_td)],
        [Paragraph("Muhammad Abdullah", style_td_bold), Paragraph("BSDSF23A032", style_td), Paragraph("Frontend & Analytics", style_td), Paragraph("DuckDB OLAP, Modern Web Portal UI, PKR Pricing", style_td), Paragraph("<b>32 SP</b>", style_td)],
    ]
    t_roster = Table(roster_data, colWidths=[95, 65, 100, 184, 60])
    t_roster.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elements.append(t_roster)
    elements.append(Spacer(1, 8))

    # Section 2: Sprint Velocity
    elements.append(Paragraph("2. 4-Week Sprint Schedule & Velocity Allocation (160 SP)", style_h1))
    sprint_data = [
        [Paragraph("Sprint", style_th), Paragraph("Timeline", style_th), Paragraph("Abdullah", style_th), Paragraph("Talha", style_th), Paragraph("Danial", style_th), Paragraph("Ahmad", style_th), Paragraph("M. Abd", style_th), Paragraph("Sprint SP", style_th)],
        [Paragraph("Sprint 1", style_td_bold), Paragraph("Days 1–7", style_td), Paragraph("8 SP", style_td), Paragraph("8 SP", style_td), Paragraph("8 SP", style_td), Paragraph("8 SP", style_td), Paragraph("8 SP", style_td), Paragraph("<b>40 SP</b>", style_td)],
        [Paragraph("Sprint 2", style_td_bold), Paragraph("Days 8–14", style_td), Paragraph("8 SP", style_td), Paragraph("8 SP", style_td), Paragraph("8 SP", style_td), Paragraph("8 SP", style_td), Paragraph("8 SP", style_td), Paragraph("<b>40 SP</b>", style_td)],
        [Paragraph("Sprint 3", style_td_bold), Paragraph("Days 15–21", style_td), Paragraph("8 SP", style_td), Paragraph("8 SP", style_td), Paragraph("8 SP", style_td), Paragraph("8 SP", style_td), Paragraph("8 SP", style_td), Paragraph("<b>40 SP</b>", style_td)],
        [Paragraph("Sprint 4", style_td_bold), Paragraph("Days 22–28", style_td), Paragraph("8 SP", style_td), Paragraph("8 SP", style_td), Paragraph("8 SP", style_td), Paragraph("8 SP", style_td), Paragraph("8 SP", style_td), Paragraph("<b>40 SP</b>", style_td)],
        [Paragraph("Total", style_td_bold), Paragraph("4 Weeks", style_td_bold), Paragraph("<b>32 SP</b>", style_td_bold), Paragraph("<b>32 SP</b>", style_td_bold), Paragraph("<b>32 SP</b>", style_td_bold), Paragraph("<b>32 SP</b>", style_td_bold), Paragraph("<b>32 SP</b>", style_td_bold), Paragraph("<b>160 SP</b>", style_td_bold)],
    ]
    t_sprint = Table(sprint_data, colWidths=[54, 60, 55, 55, 55, 55, 60, 60])
    t_sprint.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#E2E8F0')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elements.append(t_sprint)
    elements.append(Spacer(1, 8))

    # Page Break for Tickets Table
    elements.append(PageBreak())

    # Section 3: Tickets Catalog
    elements.append(Paragraph("3. Complete 5-Member Jira Ticket Catalog (40 Tickets, AUT-101 – AUT-143)", style_h1))
    
    ticket_table_data = [
        [
            Paragraph("Key", style_th),
            Paragraph("Sprint", style_th),
            Paragraph("Summary & Git Commit Tag", style_th),
            Paragraph("SP", style_th),
            Paragraph("Assignee", style_th),
            Paragraph("Status", style_th),
        ]
    ]
    for t in TICKETS_5:
        ticket_table_data.append([
            Paragraph(f"<b>{t['key']}</b>", style_td_bold),
            Paragraph(t["sprint"], style_td),
            Paragraph(f"<b>{t['summary']}</b><br/><font color='#64748B'>{t['commit']}</font>", style_td),
            Paragraph(f"<b>{t['sp']}</b>", style_td_bold),
            Paragraph(t["assignee"].split()[0], style_td),
            Paragraph(f"<font color='#059669'><b>Done</b></font>", style_td),
        ])

    t_tickets = Table(ticket_table_data, colWidths=[46, 42, 266, 25, 75, 50])
    t_tickets.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    elements.append(t_tickets)

    doc.build(elements, canvasmaker=NumberedCanvas5)
    print(f"[OK] Saved 5-Member PDF: {filepath}")

# -------------------------------------------------------------
# 4. Generate 5-Member Markdown Specification
# -------------------------------------------------------------
def build_5member_md(filepath):
    content = """# AutoCare AI: 5-Member Jira Agile Scrum Workflow & Team Work Breakdown Structure (WBS)

**Academic Institution:** Punjab University College of Information Technology (PUCIT), University of the Punjab  
**Department:** Department of Data Science / Computing  
**Course / Track:** BS Data Science — Final Year Project / Big Data Systems  
**Project Key:** `AUT`  
**Remote Repository:** `https://github.com/marketbul/autocare-ai.git`  
**Cadence:** 4 Sprints (4 Weeks High-Velocity Execution Cycle)  
**Total Velocity:** 160 Story Points (Equally divided: 32 SP per member, 8 SP per member per sprint)  

---

## 👥 1. 5-Member Engineering Roster & RACI Ownership Matrix

| Member Name | University Roll No | Primary Role | Total SP | Focus Areas |
| :--- | :--- | :--- | :---: | :--- |
| **Abdullah** *(Group Leader)* | `BSDSF23A035` | **Lead System Architect & RAG Lead** | **32 SP** | Consistent Hash Ring (160 vNodes), Subword BPE Tokenizer, 4-Layer Causal Transformer LM from scratch, FastAPI Gateway |
| **Talha Ali Bhatti** | `BSDSF23A016` | **Lead Distributed Storage & Ingestion Engineer** | **32 SP** | MinIO S3 Multi-Bucket Cluster, SHA-256 CAS Deduplication, OBD-II Stream Ingestion, Snappy Parquet Lakehouse Compaction |
| **Danial Hameed** | `BSDSF23A014` | **Lead Data Engineer & Multilingual Corpus Lead** | **32 SP** | 111 Dataset Standardization, Counting Bloom Filter Gate, Hybrid BM25 + Dense Vector Index, Urdu/Roman Urdu Automotive Lexicon |
| **Ahmad Zahid** | `BSDSF23A033` | **Lead ML Triage & Confidence Calibration** | **32 SP** | Cost-Sensitive Triage Classifier (10x safety penalty), Platt Scaling & ECE Minimizer, NLI Repair Verifier, Selective Abstention Gate |
| **Muhammad Abdullah** | `BSDSF23A032` | **Lead Frontend, Analytics & Market Economics** | **32 SP** | DuckDB In-Memory OLAP Aggregations, PySpark DataFrame Pipelines, Modern Automotive Web Portal UI (React 18), Pakistani PKR Pricing |

### RACI Governance Framework
- **R (Responsible):** The engineer implementing the algorithm and unit tests.
- **A (Accountable):** The primary owner ensuring the ticket meets acceptance criteria.
- **C (Consulted):** Team members providing schema inputs, interfaces, or mathematical validation.
- **I (Informed):** Team members notified during daily standups and Git pull requests.

| Epic / Module | Abdullah (`035`) | Talha (`016`) | Danial (`014`) | Ahmad (`033`) | M. Abdullah (`032`) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **EPIC-1: Distributed Storage & CAS** | C | **A / R** | C | I | I |
| **EPIC-2: Consistent Hashing & Bloom Filter** | **A / R** | C | **A / R** | I | I |
| **EPIC-3: Stream Ingestion & Parquet** | I | **A / R** | C | I | C |
| **EPIC-4: Supervised ML Triage & Calibration** | C | I | I | **A / R** | I |
| **EPIC-5: Causal Transformer LM & RAG** | **A / R** | I | **A / R** | C | I |
| **EPIC-6: Analytics, Web Portal UI & Defense** | C | C | I | I | **A / R** |

---

## 🗓️ 2. 4-Week Sprint Schedule & Velocity Allocation (160 SP)

| Sprint Milestone | Timeline | Abdullah | Talha | Danial | Ahmad | M. Abdullah | Sprint Total |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Sprint 1 (Architecture & Foundation)** | Days 1–7 | 8 SP | 8 SP | 8 SP | 8 SP | 8 SP | **40 SP** |
| **Sprint 2 (Bloom Filter, Ingestion & Calib)** | Days 8–14 | 8 SP | 8 SP | 8 SP | 8 SP | 8 SP | **40 SP** |
| **Sprint 3 (Transformer LM, Compaction & NLI)**| Days 15–21| 8 SP | 8 SP | 8 SP | 8 SP | 8 SP | **40 SP** |
| **Sprint 4 (RAG Integration, Web UI & Defense)**| Days 22–28| 8 SP | 8 SP | 8 SP | 8 SP | 8 SP | **40 SP** |
| **Final Total** | **4 Weeks** | **32 SP** | **32 SP** | **32 SP** | **32 SP** | **32 SP** | **160 SP** |

---

## 🎯 3. Complete 5-Member Jira Ticket Catalog (40 Tickets, AUT-101 – AUT-143)

### Sprint 1 (Days 1–7): Architecture Foundation & Core Ingestion
- `AUT-104` (Story, 8 SP, **Abdullah**): Consistent Hash Ring with 160 Virtual Nodes per Physical Node
- `AUT-101` (Story, 5 SP, **Talha Ali Bhatti**): MinIO S3 Distributed Multi-Bucket Cluster Architecture
- `AUT-102` (Story, 3 SP, **Talha Ali Bhatti**): SHA-256 Content-Addressable Storage (CAS) Deduplication Engine
- `AUT-115` (Story, 5 SP, **Danial Hameed**): Automotive Dataset Ingestion & Unified Entity Schema Standardization (111 files)
- `AUT-103` (Story, 3 SP, **Danial Hameed**): Structure-Aware Technical Manual Chunking & Metadata Extraction
- `AUT-138` (Story, 5 SP, **Ahmad Zahid**): Supervised Fault Category & Severity Triage Classifier
- `AUT-139` (Story, 3 SP, **Ahmad Zahid**): Cost-Sensitive Loss Matrix (10x Safety Penalty on Critical Errors)
- `AUT-114` (Story, 5 SP, **Muhammad Abdullah**): DuckDB In-Memory OLAP Query Engine Integration for Parquet
- `AUT-116` (Story, 3 SP, **Muhammad Abdullah**): PySpark Distributed DataFrame Windowed Transformations Pipeline

### Sprint 2 (Days 8–14): Distributed Filters, Ingestion Streams & Calibration
- `AUT-105` (Story, 5 SP, **Abdullah**): Consistent Hash Node Dynamic Rebalancing & Binary Ring Routing
- `AUT-128` (Story, 3 SP, **Abdullah**): FastAPI Asynchronous Gateway & Microservice Routing Architecture
- `AUT-108` (Story, 5 SP, **Talha Ali Bhatti**): OBD-II CAN-Bus High-Velocity Telemetry Stream Generator (10,000 msg/s)
- `AUT-110` (Story, 3 SP, **Talha Ali Bhatti**): Snappy Columnar Parquet Lakehouse Partitioning
- `AUT-106` (Story, 5 SP, **Danial Hameed**): Counting Bloom Filter for O(1) Set Membership & Redundant I/O Gate
- `AUT-107` (Story, 3 SP, **Danial Hameed**): Bloom Filter Bit-Array Serialization & Redis State Sync
- `AUT-140` (Story, 5 SP, **Ahmad Zahid**): Platt Scaling & Temperature Confidence Calibration (ECE Optimization)
- `AUT-141` (Story, 3 SP, **Ahmad Zahid**): Grouped K-Fold Cross-Validation Protocol across Vehicle Models
- `AUT-117` (Story, 5 SP, **Muhammad Abdullah**): Fleet Diagnostic Trouble Code (DTC) Anomaly Detection Model
- `AUT-118` (Story, 3 SP, **Muhammad Abdullah**): Regional Component Degradation & Pakistani Climate Risk Multipliers

### Sprint 3 (Days 15–21): Transformer LM from Scratch, Compaction & Workshop Verifier
- `AUT-121` (Story, 5 SP, **Abdullah**): Custom Subword Byte-Pair Encoding (BPE) Tokenizer from Scratch (4,000 Vocab)
- `AUT-123` (Story, 3 SP, **Abdullah**): 4-Layer Causal Transformer Decoder with Multi-Head Self-Attention
- `AUT-109` (Story, 5 SP, **Talha Ali Bhatti**): In-Memory Sliding-Window Batch Buffer & Ingestion Sink
- `AUT-111` (Story, 3 SP, **Talha Ali Bhatti**): Automated Parquet Compaction Job & Small File Merging Engine
- `AUT-136` (Story, 5 SP, **Danial Hameed**): Multilingual Automotive Lexicon (Urdu & Roman Urdu to Standard DTCs)
- `AUT-122` (Story, 3 SP, **Danial Hameed**): Dense L2-Normalized Vector Embedding Neural Network (D=128)
- `AUT-132` (Story, 5 SP, **Ahmad Zahid**): Workshop Repair Invoice Verifier & Non-Accusatory NLI Engine
- `AUT-142` (Story, 3 SP, **Ahmad Zahid**): Repair Fraud & Unnecessary Parts Replacement Detection Heuristics
- `AUT-119` (Task, 5 SP, **Muhammad Abdullah**): DuckDB OLAP Benchmark vs Traditional Relational SQL (15x Speedup)
- `AUT-120` (Story, 3 SP, **Muhammad Abdullah**): Pakistani Fair-Price Market Estimator (PKR Parts & Mechanic Labor)

### Sprint 4 (Days 22–28): Multilingual Grounded RAG, Web Portal UI & Defense
- `AUT-124` (Story, 5 SP, **Abdullah**): Autoregressive LM Training Pipeline with AdamW & Perplexity Optimization
- `AUT-126` (Story, 3 SP, **Abdullah**): Multilingual Grounded RAG Generation & Anti-Hallucination Pipeline
- `AUT-113` (Task, 5 SP, **Talha Ali Bhatti**): Storage IOPS & Ingestion Latency Percentile Benchmark Profiler
- `AUT-112` (Story, 3 SP, **Talha Ali Bhatti**): Lakehouse Schema Evolution & Corrupt Record Dead-Letter Sink
- `AUT-125` (Story, 5 SP, **Danial Hameed**): Hybrid Vector Store (Dense Cosine Similarity + BM25 Lexical Ranking)
- `AUT-137` (Story, 3 SP, **Danial Hameed**): Reciprocal Rank Fusion (RRF) & Context Re-Ranking Layer
- `AUT-143` (Story, 5 SP, **Ahmad Zahid**): Selective Abstention Gate & Uncertainty Threshold Governance
- `AUT-129` (Task, 3 SP, **Ahmad Zahid**): End-to-End System Safety Validation & Pytest Test Suite
- `AUT-127` (Story, 5 SP, **Muhammad Abdullah**): Modern Automotive Diagnostic Web Portal Redesign (React 18 + Tailwind)
- `AUT-130` (Story, 3 SP, **Muhammad Abdullah**): Final Academic Project Initiation Document (PID) & Defense Presentation

---

## 🛠️ 4. Jira & GitHub Integration

1. **Importing into Jira:**
   - In Atlassian Jira, go to **Settings** -> **System** -> **External System Import** -> **CSV**.
   - Select `docs/jira_tickets_import.csv`.
   - Map fields (`Issue key`, `Summary`, `Description`, `Epic Link`, `Story Points`, `Assignee`, `Sprint`, `Status`).
2. **Git Commit Traceability:**
   - Every commit must include the ticket key:
     `git commit -m "[AUT-121] feat(rag-scratch): subword BPE tokenizer with 4000 vocab and special tokens"`
   - Jira's development integration automatically links the commit, branch, and PR to the ticket.
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] Saved 5-Member Markdown: {filepath}")

# -------------------------------------------------------------
# Main Runner
# -------------------------------------------------------------
if __name__ == "__main__":
    base_dir = r"C:\Users\ABDUL\.gemini\antigravity\scratch\autocare-us2"
    docs_dir = os.path.join(base_dir, "docs")
    desktop_dir = r"C:\Users\ABDUL\Desktop\AutoCare_AI_Complete_Deliverable_2026-11-10"
    brain_dir = r"C:\Users\ABDUL\.gemini\antigravity\brain\00a7aa5b-5d32-449b-a3f6-925ffecf15c5"

    os.makedirs(docs_dir, exist_ok=True)
    os.makedirs(desktop_dir, exist_ok=True)

    csv_path = os.path.join(docs_dir, "jira_tickets_import.csv")
    export_5member_csv(csv_path)

    docx_path = os.path.join(base_dir, "AutoCare_AI_Jira_Workflow_Backlog.docx")
    build_5member_docx(docx_path)

    pdf_path = os.path.join(base_dir, "AutoCare_AI_Jira_Workflow_Backlog.pdf")
    build_5member_pdf(pdf_path)

    md_path = os.path.join(docs_dir, "JIRA_AGILE_WORKFLOW.md")
    build_5member_md(md_path)
    shutil.copy2(md_path, os.path.join(base_dir, "JIRA_AGILE_WORKFLOW.md"))

    # Copy to Desktop deliverables
    targets = [
        (csv_path, os.path.join(desktop_dir, "jira_tickets_import.csv")),
        (docx_path, os.path.join(desktop_dir, "AutoCare_AI_Jira_Workflow_Backlog.docx")),
        (pdf_path, os.path.join(desktop_dir, "AutoCare_AI_Jira_Workflow_Backlog.pdf")),
        (docx_path, os.path.join(brain_dir, "AutoCare_AI_Jira_Workflow_Backlog.docx")),
        (pdf_path, os.path.join(brain_dir, "AutoCare_AI_Jira_Workflow_Backlog.pdf")),
        (md_path, os.path.join(desktop_dir, "JIRA_AGILE_WORKFLOW.md")),
    ]
    for src, dst in targets:
        shutil.copy2(src, dst)
        print(f"[SYNC] {src} -> {dst}")

    print("\nAll 5-Member Jira documents successfully generated and synchronized!")
