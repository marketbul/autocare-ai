import os
import sys
import csv
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# -------------------------------------------------------------
# Ticket Master Dataset
# -------------------------------------------------------------
TICKETS = [
    # Sprint 1
    {
        "key": "AUT-101",
        "type": "Story",
        "summary": "MinIO S3 Distributed Multi-Bucket Cluster Architecture",
        "epic": "EPIC-1: Distributed Storage & CAS",
        "sp": 5,
        "assignee": "Talha Ali Bhatti (bsdsf23a016)",
        "priority": "Highest",
        "status": "Done",
        "sprint": "Sprint 1 (Storage & Hash Ring)",
        "desc": "Provision distributed MinIO multi-tenant object storage cluster with standard buckets: raw-telemetry, processed-parquet, model-checkpoints, and corpus-manuals. Configure IAM credentials, CORS, and lifecycle policies.",
        "ac": "MinIO S3 API accepts credentials; bucket assertions pass; concurrent PUT/GET multipart verified.",
        "branch": "feature/AUT-101-minio-cluster",
        "commit": "[AUT-101] feat(storage): provision distributed MinIO S3 cluster and bucket policies"
    },
    {
        "key": "AUT-102",
        "type": "Story",
        "summary": "SHA-256 Content-Addressable Storage (CAS) Deduplication Engine",
        "epic": "EPIC-1: Distributed Storage & CAS",
        "sp": 5,
        "assignee": "Talha Ali Bhatti (bsdsf23a016)",
        "priority": "High",
        "status": "Done",
        "sprint": "Sprint 1 (Storage & Hash Ring)",
        "desc": "Implement cryptographic SHA-256 content-addressable storage handler that splits raw manuals and telemetry chunks, computes SHA-256 hex digest, and avoids redundant uploads via content indexing.",
        "ac": "Duplicate uploads produce zero additional disk usage; deduplication log reports > 30% byte savings.",
        "branch": "feature/AUT-102-cas-deduplication",
        "commit": "[AUT-102] feat(storage): implement SHA-256 content-addressable storage deduplication"
    },
    {
        "key": "AUT-103",
        "type": "Story",
        "summary": "S3 Asynchronous Multipart Uploader with Exponential Backoff",
        "epic": "EPIC-1: Distributed Storage & CAS",
        "sp": 3,
        "assignee": "Talha Ali Bhatti (bsdsf23a016)",
        "priority": "Medium",
        "status": "Done",
        "sprint": "Sprint 1 (Storage & Hash Ring)",
        "desc": "Build asynchronous multipart uploader for telemetry files > 5MB with automated exponential backoff jitter (base 0.5s, max 5 retries) against network disconnects.",
        "ac": "Handles simulated MinIO disconnects without losing data; unit tests verify exponential retry backoff.",
        "branch": "feature/AUT-103-s3-resilient-uploader",
        "commit": "[AUT-103] feat(storage): resilient asynchronous multipart uploader with exponential backoff"
    },
    {
        "key": "AUT-104",
        "type": "Story",
        "summary": "Consistent Hash Ring with 160 Virtual Nodes per Physical Node",
        "epic": "EPIC-2: Distributed Hashing & Bloom Filters",
        "sp": 8,
        "assignee": "Abdullah (bsdsf23a035)",
        "priority": "Highest",
        "status": "Done",
        "sprint": "Sprint 1 (Storage & Hash Ring)",
        "desc": "Build distributed Consistent Hash Ring in Python from scratch using MurmurHash3 across 32-bit integer space. Assign 160 virtual nodes (tokens) per physical storage node to ensure uniform partition distribution.",
        "ac": "Key distribution standard deviation across 4 storage nodes < 5%; adding/removing node rebalances exactly K/N keys.",
        "branch": "feature/AUT-104-consistent-hash-ring",
        "commit": "[AUT-104] feat(algorithms): consistent hash ring with 160 virtual nodes and Murmur3"
    },
    {
        "key": "AUT-105",
        "type": "Story",
        "summary": "Consistent Hash Node Dynamic Rebalancing & Binary Ring Lookup",
        "epic": "EPIC-2: Distributed Hashing & Bloom Filters",
        "sp": 5,
        "assignee": "Abdullah (bsdsf23a035)",
        "priority": "High",
        "status": "Done",
        "sprint": "Sprint 1 (Storage & Hash Ring)",
        "desc": "Implement binary search (bisect) ring routing with O(log M) complexity to identify target storage nodes for VIN keys. Include node join/leave dynamic rebalancing generator.",
        "ac": "Lookup latency < 0.05ms for 100K lookups; rebalance generator outputs minimal node migration diffs.",
        "branch": "feature/AUT-105-ring-rebalancing",
        "commit": "[AUT-105] feat(algorithms): bisect ring lookup and dynamic cluster rebalancing logic"
    },
    {
        "key": "AUT-114",
        "type": "Story",
        "summary": "DuckDB High-Performance In-Memory OLAP Query Engine Integration",
        "epic": "EPIC-4: Analytics Engine & Fleet Anomaly",
        "sp": 5,
        "assignee": "Muhammad Abdullah (bsdsf23a032)",
        "priority": "Highest",
        "status": "Done",
        "sprint": "Sprint 1 (Storage & Hash Ring)",
        "desc": "Embed DuckDB columnar engine into backend for zero-copy SQL analytics scanning local and MinIO-hosted Parquet files for fleet aggregations, DTC frequencies, and mileage trends.",
        "ac": "Executes analytical aggregations across 500,000 rows in < 80ms; zero memory duplication between Arrow and DuckDB.",
        "branch": "feature/AUT-114-duckdb-olap",
        "commit": "[AUT-114] feat(analytics): embed DuckDB OLAP engine for zero-copy parquet querying"
    },
    {
        "key": "AUT-115",
        "type": "Story",
        "summary": "Automotive Dataset Ingestion & Entity Schema Standardization",
        "epic": "EPIC-4: Analytics Engine & Fleet Anomaly",
        "sp": 5,
        "assignee": "Muhammad Abdullah (bsdsf23a032)",
        "priority": "High",
        "status": "Done",
        "sprint": "Sprint 1 (Storage & Hash Ring)",
        "desc": "Ingest, clean, deduplicate, and standardize 111 dataset files across 14 categories (PakWheels, Mechanic Videos, Facebook Auto QA, OBD-II manuals, PKR pricing indices) into unified entity schemas.",
        "ac": "Clean dataset catalog saved in dataset/ and Desktop deliverable; missing values imputed; UTF-8 verified.",
        "branch": "feature/AUT-115-dataset-standardization",
        "commit": "[AUT-115] feat(data): clean, preprocess and standardize 111 automotive dataset files"
    },
    {
        "key": "AUT-116",
        "type": "Story",
        "summary": "PySpark Distributed DataFrame Windowed Transformations Pipeline",
        "epic": "EPIC-4: Analytics Engine & Fleet Anomaly",
        "sp": 3,
        "assignee": "Muhammad Abdullah (bsdsf23a032)",
        "priority": "Medium",
        "status": "Done",
        "sprint": "Sprint 1 (Storage & Hash Ring)",
        "desc": "Implement PySpark distributed processing script simulating multi-worker DataFrame transformations: windowed moving averages of coolant temperature, rolling fuel trim standard deviations, and trip segmentation.",
        "ac": "Pipeline executes on local PySpark master; writes partition-aggregated parquet tables without schema drift.",
        "branch": "feature/AUT-116-pyspark-pipeline",
        "commit": "[AUT-116] feat(analytics): PySpark distributed windowed transformations pipeline"
    },

    # Sprint 2
    {
        "key": "AUT-106",
        "type": "Story",
        "summary": "Counting Bloom Filter for O(1) Set Membership & Redundant I/O Gate",
        "epic": "EPIC-2: Distributed Hashing & Bloom Filters",
        "sp": 8,
        "assignee": "Abdullah (bsdsf23a035)",
        "priority": "Highest",
        "status": "Done",
        "sprint": "Sprint 2 (Bloom Filter & Stream Ingest)",
        "desc": "Implement memory-efficient Counting Bloom Filter using k independent hash functions (double-hashing with Murmur3) and bit array sized for 100K DTC items to eliminate redundant disk queries.",
        "ac": "Zero false negatives under all test cases; empirical false positive rate <= 1.0% matching theoretical bound.",
        "branch": "feature/AUT-106-bloom-filter",
        "commit": "[AUT-106] feat(algorithms): counting bloom filter with k-hash double-hashing gate"
    },
    {
        "key": "AUT-107",
        "type": "Story",
        "summary": "Bloom Filter Bit-Array Serialization & Redis State Sync",
        "epic": "EPIC-2: Distributed Hashing & Bloom Filters",
        "sp": 5,
        "assignee": "Abdullah (bsdsf23a035)",
        "priority": "High",
        "status": "Done",
        "sprint": "Sprint 2 (Bloom Filter & Stream Ingest)",
        "desc": "Implement binary serialization of Bloom Filter bit-vectors to disk and asynchronous synchronization to Redis for multi-node state replication across worker pods.",
        "ac": "Filter restores from snapshot in < 10ms; byte representation fits within 120 KB memory footprint for 100K items.",
        "branch": "feature/AUT-107-bloom-serialization",
        "commit": "[AUT-107] feat(algorithms): bloom filter binary serialization and snapshot restore"
    },
    {
        "key": "AUT-108",
        "type": "Story",
        "summary": "OBD-II CAN-Bus High-Velocity Telemetry Stream Generator",
        "epic": "EPIC-3: Stream Ingest & Parquet Lakehouse",
        "sp": 5,
        "assignee": "Talha Ali Bhatti (bsdsf23a016)",
        "priority": "Highest",
        "status": "Done",
        "sprint": "Sprint 2 (Bloom Filter & Stream Ingest)",
        "desc": "Build high-throughput OBD-II CAN-bus telemetry stream simulator generating 10,000 events/second for Pakistani fleet vehicles (Corolla, Civic, Swift, Mehran, Alto) with synthetic fault injections.",
        "ac": "Generator sustains 10,000 messages/sec with configurable error injections (overheating, catalytic faults).",
        "branch": "feature/AUT-108-telemetry-streamer",
        "commit": "[AUT-108] feat(ingest): high-velocity OBD-II CAN-bus synthetic telemetry generator"
    },
    {
        "key": "AUT-109",
        "type": "Story",
        "summary": "In-Memory Sliding-Window Batch Buffer & Ingestion Sink",
        "epic": "EPIC-3: Stream Ingest & Parquet Lakehouse",
        "sp": 5,
        "assignee": "Talha Ali Bhatti (bsdsf23a016)",
        "priority": "High",
        "status": "Done",
        "sprint": "Sprint 2 (Bloom Filter & Stream Ingest)",
        "desc": "Build sliding-window batching sink consuming high-frequency telemetry events, buffering in memory over 1-second or 5,000-record windows, validating schema, and flushing to parquet.",
        "ac": "Zero memory leaks over 1-hour continuous simulation; buffer backpressure drops 0 valid packets.",
        "branch": "feature/AUT-109-batch-buffer",
        "commit": "[AUT-109] feat(ingest): sliding-window telemetry buffer and micro-batch flusher"
    },
    {
        "key": "AUT-110",
        "type": "Story",
        "summary": "Snappy Columnar Parquet Lakehouse Partitioning (Make/Model/Year/Region)",
        "epic": "EPIC-3: Stream Ingest & Parquet Lakehouse",
        "sp": 3,
        "assignee": "Talha Ali Bhatti (bsdsf23a016)",
        "priority": "Medium",
        "status": "Done",
        "sprint": "Sprint 2 (Bloom Filter & Stream Ingest)",
        "desc": "Write PyArrow columnar parquet generator with Snappy compression and hierarchical partitioning scheme: /lakehouse/telemetry/make=Toyota/model=Corolla/year=2021/region=Punjab/data.parquet.",
        "ac": "Parquet files achieve > 70% compression ratio vs raw JSON; DuckDB partition pruning executes in < 50ms.",
        "branch": "feature/AUT-110-parquet-partitioning",
        "commit": "[AUT-110] feat(lakehouse): snappy columnar parquet writer with hierarchical partitioning"
    },
    {
        "key": "AUT-117",
        "type": "Story",
        "summary": "Fleet Diagnostic Trouble Code (DTC) Anomaly Detection Model",
        "epic": "EPIC-4: Analytics Engine & Fleet Anomaly",
        "sp": 8,
        "assignee": "Muhammad Abdullah (bsdsf23a032)",
        "priority": "Highest",
        "status": "Done",
        "sprint": "Sprint 2 (Bloom Filter & Stream Ingest)",
        "desc": "Train unsupervised anomaly detection model (Isolation Forest + Rolling Z-Score) on multivariate OBD-II time-series (RPM, Speed, Throttle, STFT) to detect precursor states before DTC trip.",
        "ac": "Model achieves F1-Score >= 0.88 on identifying cooling system leaks and misfire precursors on test datasets.",
        "branch": "feature/AUT-117-anomaly-detector",
        "commit": "[AUT-117] feat(ml): unsupervised Isolation Forest anomaly detection for OBD-II telemetry"
    },
    {
        "key": "AUT-118",
        "type": "Story",
        "summary": "Regional Component Degradation & Pakistani Climate Risk Multipliers",
        "epic": "EPIC-4: Analytics Engine & Fleet Anomaly",
        "sp": 5,
        "assignee": "Muhammad Abdullah (bsdsf23a032)",
        "priority": "High",
        "status": "Done",
        "sprint": "Sprint 2 (Bloom Filter & Stream Ingest)",
        "desc": "Formulate empirical component degradation algorithms accounting for extreme Pakistani operational environments (45C Lahore/Multan summers, dusty roads, adulterated fuel quality).",
        "ac": "Algorithm shifts maintenance intervals by -25% for severe climate; produces calibrated health scores (0-100%).",
        "branch": "feature/AUT-118-climate-wear-engine",
        "commit": "[AUT-118] feat(analytics): regional climate risk multipliers and component wear equations"
    },

    # Sprint 3
    {
        "key": "AUT-111",
        "type": "Story",
        "summary": "Automated Parquet Compaction Job & Small File Merging Engine",
        "epic": "EPIC-3: Stream Ingest & Parquet Lakehouse",
        "sp": 5,
        "assignee": "Talha Ali Bhatti (bsdsf23a016)",
        "priority": "High",
        "status": "Done",
        "sprint": "Sprint 3 (Transformer LM & DuckDB OLAP)",
        "desc": "Develop scheduled background compaction task merging micro-batch parquet files (< 16MB) into optimal 128MB analytical lakehouse chunks to prevent S3 small-file fragmentation.",
        "ac": "Merges 100 small parquet files into 1 consolidated chunk; row count and checksum match perfectly.",
        "branch": "feature/AUT-111-parquet-compaction",
        "commit": "[AUT-111] feat(lakehouse): parquet small-file compaction and catalog vacuum engine"
    },
    {
        "key": "AUT-112",
        "type": "Story",
        "summary": "Lakehouse Schema Evolution & Corrupt Record Dead-Letter Sink",
        "epic": "EPIC-3: Stream Ingest & Parquet Lakehouse",
        "sp": 3,
        "assignee": "Talha Ali Bhatti (bsdsf23a016)",
        "priority": "Medium",
        "status": "Done",
        "sprint": "Sprint 3 (Transformer LM & DuckDB OLAP)",
        "desc": "Add dynamic schema evolution handling to parquet writer. Detect new sensor fields and route malformed/corrupted OBD-II records to dead-letter quarantine bucket (raw-quarantine/).",
        "ac": "Unrecognized fields backward-compatible without job failure; corrupt records isolated and tagged.",
        "branch": "feature/AUT-112-schema-evolution",
        "commit": "[AUT-112] feat(lakehouse): schema evolution handler and dead-letter quarantine sink"
    },
    {
        "key": "AUT-131",
        "type": "Task",
        "summary": "Distributed Lakehouse Cache Invalidation & Parquet Metadata Indexing",
        "epic": "EPIC-3: Stream Ingest & Parquet Lakehouse",
        "sp": 5,
        "assignee": "Talha Ali Bhatti (bsdsf23a016)",
        "priority": "High",
        "status": "Done",
        "sprint": "Sprint 3 (Transformer LM & DuckDB OLAP)",
        "desc": "Build Parquet footer metadata cache index to accelerate partition pruning and file discovery for distributed DuckDB query nodes.",
        "ac": "Metadata cache reduces directory scan overhead by 80% on 10,000 parquet file partitions.",
        "branch": "feature/AUT-131-metadata-cache",
        "commit": "[AUT-131] feat(lakehouse): parquet footer metadata cache and partition indexer"
    },
    {
        "key": "AUT-119",
        "type": "Task",
        "summary": "DuckDB Analytical Query Benchmark vs Traditional Relational SQL",
        "epic": "EPIC-4: Analytics Engine & Fleet Anomaly",
        "sp": 5,
        "assignee": "Muhammad Abdullah (bsdsf23a032)",
        "priority": "High",
        "status": "Done",
        "sprint": "Sprint 3 (Transformer LM & DuckDB OLAP)",
        "desc": "Conduct comparative benchmark measuring query execution time of DuckDB (Parquet columnar) against SQLite/Postgres for 10 analytical fleet queries (group-bys, filters, window functions).",
        "ac": "DuckDB demonstrates > 15x speedup on multi-column group-bys; benchmarking table and speedup graph generated.",
        "branch": "feature/AUT-119-olap-benchmarks",
        "commit": "[AUT-119] test(benchmark): comparative query latency benchmark of DuckDB vs SQLite"
    },
    {
        "key": "AUT-120",
        "type": "Story",
        "summary": "Pakistani Fair-Price Market Estimator & Workshop Labor Models",
        "epic": "EPIC-4: Analytics Engine & Fleet Anomaly",
        "sp": 5,
        "assignee": "Muhammad Abdullah (bsdsf23a032)",
        "priority": "High",
        "status": "Done",
        "sprint": "Sprint 3 (Transformer LM & DuckDB OLAP)",
        "desc": "Build PKR cost estimation module calculating OEM parts costs, genuine market replacement costs, and reasonable mechanic labor hours across Pakistani workshops (Lahore, Karachi, Islamabad).",
        "ac": "Returns low-median-high price ranges for top 50 common repairs; flagged workshop verifier detects overcharging > 35%.",
        "branch": "feature/AUT-120-pak-pricing-model",
        "commit": "[AUT-120] feat(pricing): localized PKR parts and mechanic labor fair-price estimator"
    },
    {
        "key": "AUT-132",
        "type": "Story",
        "summary": "Workshop Diagnostic Estimate Verifier & Fraud Detection Heuristics",
        "epic": "EPIC-4: Analytics Engine & Fleet Anomaly",
        "sp": 3,
        "assignee": "Muhammad Abdullah (bsdsf23a032)",
        "priority": "Medium",
        "status": "Done",
        "sprint": "Sprint 3 (Transformer LM & DuckDB OLAP)",
        "desc": "Implement rule-based and NLI cross-checking heuristics to verify workshop repair invoices against vehicle symptoms and OEM service schedules, detecting unnecessary upsells.",
        "ac": "Correctly flags 95% of synthetic inflated repair quotes (e.g. replacing throttle body for minor sensor dirt).",
        "branch": "feature/AUT-132-repair-verifier",
        "commit": "[AUT-132] feat(verifier): workshop estimate cross-checker and invoice fraud detector"
    },
    {
        "key": "AUT-121",
        "type": "Story",
        "summary": "Custom Subword Byte-Pair Encoding (BPE) Tokenizer from Scratch",
        "epic": "EPIC-5: Causal Transformer LM & RAG",
        "sp": 5,
        "assignee": "Abdullah (bsdsf23a035)",
        "priority": "Highest",
        "status": "Done",
        "sprint": "Sprint 3 (Transformer LM & DuckDB OLAP)",
        "desc": "Build automotive subword BPE Tokenizer in pure Python from scratch without external libraries. Learn merge pairs from bilingual automotive corpus (English, Urdu, Roman Urdu). Vocab size: 4,000 tokens.",
        "ac": "Tokenizer compresses automotive terms (radiator, catalytic, dhuwan); encode/decode roundtrips with 100% byte fidelity.",
        "branch": "feature/AUT-121-bpe-tokenizer",
        "commit": "[AUT-121] feat(rag-scratch): subword BPE tokenizer with 4000 vocab and special tokens"
    },
    {
        "key": "AUT-122",
        "type": "Story",
        "summary": "Dense L2-Normalized Vector Embedding Neural Network (D=128)",
        "epic": "EPIC-5: Causal Transformer LM & RAG",
        "sp": 3,
        "assignee": "Abdullah (bsdsf23a035)",
        "priority": "High",
        "status": "Done",
        "sprint": "Sprint 3 (Transformer LM & DuckDB OLAP)",
        "desc": "Implement trainable Dense Embedding Neural Network in PyTorch (D=128, unit L2 normalization). Maps tokenized chunks into continuous metric space where automotive symptoms and faults cluster closely.",
        "ac": "Vector dot product matches cosine similarity on unit sphere; forward pass takes < 2ms per sentence batch.",
        "branch": "feature/AUT-122-vector-embedder",
        "commit": "[AUT-122] feat(rag-scratch): dense L2-normalized vector embedding neural network (D=128)"
    },
    {
        "key": "AUT-123",
        "type": "Story",
        "summary": "4-Layer Causal Transformer Decoder with Multi-Head Self-Attention",
        "epic": "EPIC-5: Causal Transformer LM & RAG",
        "sp": 5,
        "assignee": "Abdullah (bsdsf23a035)",
        "priority": "Highest",
        "status": "Done",
        "sprint": "Sprint 3 (Transformer LM & DuckDB OLAP)",
        "desc": "Construct 4-layer Causal Transformer Decoder (1,321,728 parameters) in PyTorch from scratch. Implement multi-head self-attention (n_heads=4, d_model=128, d_ff=512), positional embeddings, and causal triangular masking.",
        "ac": "Causal mask strictly prohibits future token attention; compiles cleanly and outputs logit distributions over 4,000 vocab.",
        "branch": "feature/AUT-123-transformer-decoder",
        "commit": "[AUT-123] feat(rag-scratch): 4-layer causal transformer decoder with multi-head attention"
    },

    # Sprint 4
    {
        "key": "AUT-124",
        "type": "Story",
        "summary": "Autoregressive LM Training Pipeline with AdamW & Perplexity Tracking",
        "epic": "EPIC-5: Causal Transformer LM & RAG",
        "sp": 5,
        "assignee": "Abdullah (bsdsf23a035)",
        "priority": "Highest",
        "status": "Done",
        "sprint": "Sprint 4 (RAG Integration & Web Portal)",
        "desc": "Develop PyTorch training pipeline training Causal Transformer LM over 3 epochs on 10,784 automotive diagnostic pairs with AdamW (lr=1e-3, weight decay 0.01) and Perplexity metric tracking.",
        "ac": "Training loss drops monotonically from 3.11 to 2.24; test perplexity drops from 22.61 to 9.48; weights saved in weights/.",
        "branch": "feature/AUT-124-autoregressive-training",
        "commit": "[AUT-124] feat(rag-scratch): autoregressive LM training pipeline with AdamW and Perplexity tracking"
    },
    {
        "key": "AUT-125",
        "type": "Story",
        "summary": "Hybrid Vector Store (Cosine Similarity + BM25 Lexical Ranking)",
        "epic": "EPIC-5: Causal Transformer LM & RAG",
        "sp": 5,
        "assignee": "Abdullah (bsdsf23a035)",
        "priority": "High",
        "status": "Done",
        "sprint": "Sprint 4 (RAG Integration & Web Portal)",
        "desc": "Build in-memory hybrid search vector store indexing 17,390 chunked passages from OEM manuals, PakWheels discussions, and mechanic interviews. Combine dense cosine similarity (0.65) with BM25 lexical term frequency (0.35).",
        "ac": "Query retrieval latency < 15ms; top-5 recall >= 92% on standard vehicle symptom queries.",
        "branch": "feature/AUT-125-hybrid-vector-store",
        "commit": "[AUT-125] feat(rag-scratch): hybrid dense vector + BM25 lexical retrieval engine"
    },
    {
        "key": "AUT-126",
        "type": "Story",
        "summary": "Multilingual Grounded RAG Generation & Anti-Hallucination Gate",
        "epic": "EPIC-5: Causal Transformer LM & RAG",
        "sp": 3,
        "assignee": "Abdullah (bsdsf23a035)",
        "priority": "Highest",
        "status": "Done",
        "sprint": "Sprint 4 (RAG Integration & Web Portal)",
        "desc": "Wire vector retrieval engine into Causal Transformer LM. Condition answer generation on retrieved chunks (<ctx>...<ans>...). Enforce strict ground-truth attribution checks and selective abstention on low confidence.",
        "ac": "Answers generate verified OEM citations (page, section); outputs fair PKR estimates; abstains safely on unsupported queries.",
        "branch": "feature/AUT-126-grounded-rag-pipeline",
        "commit": "[AUT-126] feat(rag-scratch): end-to-end grounded RAG generation with selective abstention"
    },
    {
        "key": "AUT-113",
        "type": "Task",
        "summary": "Storage IOPS & Ingestion Latency Percentile Benchmark Profiler",
        "epic": "EPIC-3: Stream Ingest & Parquet Lakehouse",
        "sp": 5,
        "assignee": "Talha Ali Bhatti (bsdsf23a016)",
        "priority": "High",
        "status": "Done",
        "sprint": "Sprint 4 (RAG Integration & Web Portal)",
        "desc": "Construct automated benchmarking script profiling MinIO S3 write throughput (MB/s), ingestion latency percentiles (p50, p95, p99), and disk IOPS across raw JSON vs Snappy Parquet.",
        "ac": "Benchmark report logged with markdown output and latency histograms confirming p95 < 120ms.",
        "branch": "feature/AUT-113-storage-benchmarks",
        "commit": "[AUT-113] perf(storage): automated IOPS and ingestion latency benchmarking suite"
    },
    {
        "key": "AUT-129",
        "type": "Task",
        "summary": "End-to-End System Integration Testing & Pytest Verification",
        "epic": "EPIC-1: Distributed Storage & CAS",
        "sp": 8,
        "assignee": "Talha Ali Bhatti (bsdsf23a016)",
        "priority": "Highest",
        "status": "Done",
        "sprint": "Sprint 4 (RAG Integration & Web Portal)",
        "desc": "Write comprehensive unit and integration test suite covering MinIO S3 uploaders, Consistent Hash Ring token assignments, Bloom Filter accuracy, DuckDB Parquet reads, and RAG scratch model inference.",
        "ac": "pytest executes 25+ automated test cases with 100% pass rate; zero critical bugs in execution path.",
        "branch": "feature/AUT-129-integration-tests",
        "commit": "[AUT-129] test(integration): full pytest test suite for distributed storage, hashing, and RAG"
    },
    {
        "key": "AUT-127",
        "type": "Story",
        "summary": "Modern Automotive Diagnostic Web Portal Redesign (React + Tailwind)",
        "epic": "EPIC-6: UI Web Portal & Benchmarks",
        "sp": 5,
        "assignee": "Muhammad Abdullah (bsdsf23a032)",
        "priority": "Highest",
        "status": "Done",
        "sprint": "Sprint 4 (RAG Integration & Web Portal)",
        "desc": "Transform frontend from dense dashboard widgets into a professional automotive web portal. Implement 6 comprehensive architectural sections: Hero with live ticker, Diagnostic Terminal, 4-Stage Architecture, Scenarios, Fair Price Estimator, and Academic Footer.",
        "ac": "Responsive mobile/desktop layout; dark modern palette with emerald/amber accents; zero console runtime errors; Vite build succeeds.",
        "branch": "feature/AUT-127-web-portal-redesign",
        "commit": "[AUT-127] feat(frontend): modern automotive engineering web portal with diagnostic terminal"
    },
    {
        "key": "AUT-128",
        "type": "Story",
        "summary": "FastAPI Asynchronous RAG Inference & Telemetry REST Endpoints",
        "epic": "EPIC-6: UI Web Portal & Benchmarks",
        "sp": 5,
        "assignee": "Muhammad Abdullah (bsdsf23a032)",
        "priority": "High",
        "status": "Done",
        "sprint": "Sprint 4 (RAG Integration & Web Portal)",
        "desc": "Implement high-concurrency FastAPI asynchronous endpoints: /api/rag/ask, /api/telemetry/ingest, /api/analytics/fleet-summary, /api/health. Mount static Vite frontend distribution at /app/ with automatic root / redirect.",
        "ac": "Responds with HTTP 200 OK; handles 20 concurrent requests without thread starvation; OpenAPI swagger verified.",
        "branch": "feature/AUT-128-fastapi-backend",
        "commit": "[AUT-128] feat(api): asynchronous RAG inference endpoints and Vite SPA static mount"
    },
    {
        "key": "AUT-130",
        "type": "Story",
        "summary": "Final Academic Project Initiation Document (PID) & Defense Slides",
        "epic": "EPIC-6: UI Web Portal & Benchmarks",
        "sp": 3,
        "assignee": "Muhammad Abdullah (bsdsf23a032)",
        "priority": "Medium",
        "status": "Done",
        "sprint": "Sprint 4 (RAG Integration & Web Portal)",
        "desc": "Draft and compile comprehensive 4-week Big Data Project Initiation Document (PID) in professional .docx and .pdf formats conforming to PUCIT academic guidelines, complete with system architecture flowcharts, WBS, and performance metrics.",
        "ac": "Professional PDF and DOCX generated in deliverables folder; verified formatting, headers, tables, and academic citations.",
        "branch": "docs/AUT-130-academic-pid",
        "commit": "[AUT-130] docs(academic): generate professional 4-week Big Data PID in PDF and Word"
    }
]

# -------------------------------------------------------------
# 1. Export Jira CSV Import File
# -------------------------------------------------------------
def export_jira_csv(filepath):
    fieldnames = [
        "Issue Type", "Issue key", "Summary", "Description", "Epic Link",
        "Story Points", "Assignee", "Reporter", "Priority", "Status",
        "Sprint", "Acceptance Criteria", "Git Branch", "Commit Tag"
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for t in TICKETS:
            writer.writerow({
                "Issue Type": t["type"],
                "Issue key": t["key"],
                "Summary": t["summary"],
                "Description": t["desc"],
                "Epic Link": t["epic"],
                "Story Points": t["sp"],
                "Assignee": t["assignee"],
                "Reporter": "Abdullah (bsdsf23a035)",
                "Priority": t["priority"],
                "Status": t["status"],
                "Sprint": t["sprint"],
                "Acceptance Criteria": t["ac"],
                "Git Branch": t["branch"],
                "Commit Tag": t["commit"]
            })
    print(f"[OK] Exported Jira CSV: {filepath}")

# -------------------------------------------------------------
# 2. Build DOCX Document
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

def build_jira_docx(filepath):
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
    r_badge = p_badge.add_run("AGILE SCRUM WORKFLOW & WORK BREAKDOWN STRUCTURE (WBS) • PUCIT FYP")
    r_badge.font.name = 'Arial'
    r_badge.font.size = Pt(8.5)
    r_badge.font.bold = True
    r_badge.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    # Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(2)
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run("AutoCare AI: Jira Sprint Backlog & Team Distribution")
    r_title.font.name = 'Arial'
    r_title.font.size = Pt(20)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(14)
    r_sub = p_sub.add_run("End-to-End Task Partitioning, RACI Ownership, 4 Sprints (156 SP), and Git Commit Traceability")
    r_sub.font.size = Pt(11)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    # Meta Table
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Institution & Dept", "Punjab University College of Information Technology (PUCIT) — Data Science"),
        ("Project Key & Repo", "Key: AUT | GitHub: https://github.com/marketbul/autocare-ai.git"),
        ("Scrum Team", "Talha Ali Bhatti (016), Muhammad Abdullah (032), Abdullah (035)"),
        ("Sprint Cycle & Scope", "4 Sprints (4 Weeks) | 156 Total Story Points (52 SP per member, 100% Balanced)")
    ]
    for i, (k, v) in enumerate(meta_data):
        row = meta_table.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.0)
        c1.width = Inches(4.8)
        c0.paragraphs[0].text = k
        c0.paragraphs[0].runs[0].font.bold = True
        c0.paragraphs[0].runs[0].font.size = Pt(9.5)
        c0.paragraphs[0].runs[0].font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        c1.paragraphs[0].text = v
        c1.paragraphs[0].runs[0].font.size = Pt(9.5)
        set_cell_background(c0, "F8FAFC")
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)
    set_table_borders(meta_table)

    # Heading 1
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    h1 = doc.add_paragraph()
    r = h1.add_run("1. Team Work Breakdown & RACI Ownership Matrix")
    r.font.name = 'Arial'; r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    raci_table = doc.add_table(rows=7, cols=5)
    raci_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Epic / Workstream", "Primary Lead", "Talha (016)", "M. Abdullah (032)", "Abdullah (035)"]
    for j, h in enumerate(headers):
        cell = raci_table.rows[0].cells[j]
        cell.paragraphs[0].text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9)
        set_cell_background(cell, "0F172A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_margins(cell, 80, 80, 80, 80)
    
    raci_rows = [
        ("EPIC-1: MinIO Storage & CAS Deduplication", "Talha Ali Bhatti", "Accountable / Lead", "Consulted", "Informed"),
        ("EPIC-2: Consistent Hashing & Bloom Filters", "Abdullah", "Consulted", "Informed", "Accountable / Lead"),
        ("EPIC-3: Stream Ingest & Parquet Lakehouse", "Talha Ali Bhatti", "Accountable / Lead", "Consulted", "Informed"),
        ("EPIC-4: DuckDB Analytics & Fleet Anomaly", "Muhammad Abdullah", "Informed", "Accountable / Lead", "Consulted"),
        ("EPIC-5: Causal Transformer LM & RAG Engine", "Abdullah", "Informed", "Consulted", "Accountable / Lead"),
        ("EPIC-6: UI Web Portal, Benchmarks & Defense", "Muhammad Abdullah", "Consulted", "Accountable / Lead", "Consulted"),
    ]
    for i, rdata in enumerate(raci_rows):
        row = raci_table.rows[i+1]
        for j, text in enumerate(rdata):
            cell = row.cells[j]
            cell.paragraphs[0].text = text
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)
            if j == 0:
                cell.paragraphs[0].runs[0].font.bold = True
            bg = "F8FAFC" if i % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 80, 80)
    set_table_borders(raci_table)

    # Heading 2
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    h2 = doc.add_paragraph()
    r = h2.add_run("2. 4-Week Sprint Schedule & Velocity Allocation")
    r.font.name = 'Arial'; r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    sprint_table = doc.add_table(rows=6, cols=6)
    sprint_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sheaders = ["Sprint", "Timeline", "Talha (SP)", "M. Abdullah (SP)", "Abdullah (SP)", "Sprint Total"]
    for j, h in enumerate(sheaders):
        cell = sprint_table.rows[0].cells[j]
        cell.paragraphs[0].text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9)
        set_cell_background(cell, "1E293B")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_margins(cell, 80, 80, 80, 80)
    
    sprint_data = [
        ("Sprint 1", "Days 1–7 (Storage & Hash Ring)", "13 SP", "13 SP", "13 SP", "39 SP"),
        ("Sprint 2", "Days 8–14 (Bloom Filter & Ingest)", "13 SP", "13 SP", "13 SP", "39 SP"),
        ("Sprint 3", "Days 15–21 (Transformer LM & DuckDB)", "13 SP", "13 SP", "13 SP", "39 SP"),
        ("Sprint 4", "Days 22–28 (RAG Integration & Web Portal)", "13 SP", "13 SP", "13 SP", "39 SP"),
        ("Total", "4 Weeks (Full Platform Delivery)", "52 SP", "52 SP", "52 SP", "156 SP")
    ]
    for i, sdata in enumerate(sprint_data):
        row = sprint_table.rows[i+1]
        for j, text in enumerate(sdata):
            cell = row.cells[j]
            cell.paragraphs[0].text = text
            cell.paragraphs[0].runs[0].font.size = Pt(9)
            if i == 4 or j in [0, 5]:
                cell.paragraphs[0].runs[0].font.bold = True
            bg = "E2E8F0" if i == 4 else ("F8FAFC" if i % 2 == 1 else "FFFFFF")
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 80, 80)
    set_table_borders(sprint_table)

    # Heading 3: Full Backlog
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    h3 = doc.add_paragraph()
    r = h3.add_run("3. Complete Jira Ticket Catalog & Commit Linkages (AUT-101 – AUT-132)")
    r.font.name = 'Arial'; r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    ticket_table = doc.add_table(rows=len(TICKETS)+1, cols=6)
    ticket_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    theaders = ["Key", "Type", "Summary", "SP", "Assignee", "Status"]
    for j, h in enumerate(theaders):
        cell = ticket_table.rows[0].cells[j]
        cell.paragraphs[0].text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9)
        set_cell_background(cell, "0F172A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_margins(cell, 80, 80, 60, 60)

    for i, t in enumerate(TICKETS):
        row = ticket_table.rows[i+1]
        row_vals = [
            t["key"],
            t["type"],
            t["summary"],
            f"{t['sp']} SP",
            t["assignee"].split()[0], # Short name
            t["status"]
        ]
        for j, text in enumerate(row_vals):
            cell = row.cells[j]
            cell.paragraphs[0].text = text
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)
            if j in [0, 3]:
                cell.paragraphs[0].runs[0].font.bold = True
            bg = "F8FAFC" if i % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, 50, 50, 60, 60)
    set_table_borders(ticket_table)

    # Heading 4: How to link Git commits
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    h4 = doc.add_paragraph()
    r = h4.add_run("4. Git Commit & Agile Traceability Standard")
    r.font.name = 'Arial'; r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_git = doc.add_paragraph()
    p_git.add_run(
        "To maintain seamless synchronization between Jira and GitHub, every engineer prefixes their commit messages "
        "with their assigned ticket key. Example: git commit -m \"[AUT-121] feat(rag-scratch): subword BPE tokenizer with 4000 vocab\". "
        "Jira will automatically trace the commit to the sprint burndown chart and mark the issue as verified."
    )

    doc.save(filepath)
    print(f"[OK] Saved DOCX: {filepath}")

# -------------------------------------------------------------
# 3. Build Professional PDF Document
# -------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "AutoCare AI — Agile Jira Scrum Workflow & Team Work Breakdown")
            self.drawRightString(letter[0] - 54, letter[1] - 36, "PUCIT • BS Data Science")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)
            
        # Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawString(54, 34, "AutoCare AI / AutoData Lake — Final Year Project | Sprint Backlog AUT-101 to AUT-132")
        self.drawRightString(letter[0] - 54, 34, page_str)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 46, letter[0] - 54, 46)
        self.restoreState()

def build_jira_pdf(filepath):
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    style_badge = ParagraphStyle(
        'Badge',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#0284C7'),
        spaceAfter=4
    )
    style_title = ParagraphStyle(
        'MainTitle',
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6
    )
    style_sub = ParagraphStyle(
        'SubTitle',
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=14
    )
    style_h1 = ParagraphStyle(
        'SectionH1',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=12,
        spaceAfter=8
    )
    style_body = ParagraphStyle(
        'Body',
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#334155')
    )
    style_th = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )
    style_td = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#1E293B')
    )
    style_td_bold = ParagraphStyle(
        'TableCellBold',
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#0F172A')
    )

    elements = []

    # Title Header
    elements.append(Paragraph("JIRA AGILE SCRUM SPECIFICATION • DEPARTMENT OF DATA SCIENCE (PUCIT)", style_badge))
    elements.append(Paragraph("AutoCare AI: Agile Jira Workflow & Work Breakdown Structure", style_title))
    elements.append(Paragraph("Formal Distribution across 3 Students (Talha, M. Abdullah, Abdullah) | 4 Sprints | 156 Story Points", style_sub))

    # Meta Table
    meta_data = [
        [Paragraph("<b>Academic Scope:</b>", style_td_bold), Paragraph("PUCIT BS Data Science Final Year Project / Big Data Systems", style_td)],
        [Paragraph("<b>Jira Key & Repo:</b>", style_td_bold), Paragraph("Project Key: <b>AUT</b> | Remote: github.com/marketbul/autocare-ai.git", style_td)],
        [Paragraph("<b>Engineering Team:</b>", style_td_bold), Paragraph("Talha Ali Bhatti (016) | M. Abdullah (032) | Abdullah (035)", style_td)],
        [Paragraph("<b>Velocity & Balance:</b>", style_td_bold), Paragraph("156 Story Points Total | Exactly 52 SP per member (100% Balanced)", style_td)]
    ]
    t_meta = Table(meta_data, colWidths=[120, 384])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_meta)
    elements.append(Spacer(1, 10))

    # Section 1: RACI
    elements.append(Paragraph("1. Team Work Breakdown & RACI Responsibility Matrix", style_h1))
    raci_table_data = [
        [
            Paragraph("Epic / Module", style_th),
            Paragraph("Primary Lead", style_th),
            Paragraph("Talha (016)", style_th),
            Paragraph("M. Abdullah (032)", style_th),
            Paragraph("Abdullah (035)", style_th),
        ],
        [Paragraph("EPIC-1: MinIO S3 & CAS Storage", style_td_bold), Paragraph("Talha Ali Bhatti", style_td), Paragraph("<b>Accountable</b>", style_td), Paragraph("Consulted", style_td), Paragraph("Informed", style_td)],
        [Paragraph("EPIC-2: Consistent Hashing & Bloom Filter", style_td_bold), Paragraph("Abdullah", style_td), Paragraph("Consulted", style_td), Paragraph("Informed", style_td), Paragraph("<b>Accountable</b>", style_td)],
        [Paragraph("EPIC-3: Stream Ingest & Parquet Lakehouse", style_td_bold), Paragraph("Talha Ali Bhatti", style_td), Paragraph("<b>Accountable</b>", style_td), Paragraph("Consulted", style_td), Paragraph("Informed", style_td)],
        [Paragraph("EPIC-4: DuckDB Analytics & Fleet Anomaly", style_td_bold), Paragraph("Muhammad Abdullah", style_td), Paragraph("Informed", style_td), Paragraph("<b>Accountable</b>", style_td), Paragraph("Consulted", style_td)],
        [Paragraph("EPIC-5: Causal Transformer LM & RAG Engine", style_td_bold), Paragraph("Abdullah", style_td), Paragraph("Informed", style_td), Paragraph("Consulted", style_td), Paragraph("<b>Accountable</b>", style_td)],
        [Paragraph("EPIC-6: UI Web Portal, Benchmarks & Defense", style_td_bold), Paragraph("Muhammad Abdullah", style_td), Paragraph("Consulted", style_td), Paragraph("<b>Accountable</b>", style_td), Paragraph("Consulted", style_td)],
    ]
    t_raci = Table(raci_table_data, colWidths=[154, 90, 85, 95, 80])
    t_raci.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_raci)
    elements.append(Spacer(1, 10))

    # Section 2: Sprint Velocity
    elements.append(Paragraph("2. 4-Week Sprint Schedule & Velocity Allocation", style_h1))
    sprint_data = [
        [Paragraph("Sprint", style_th), Paragraph("Timeline & Focus", style_th), Paragraph("Talha (SP)", style_th), Paragraph("M. Abd (SP)", style_th), Paragraph("Abdullah (SP)", style_th), Paragraph("Total SP", style_th)],
        [Paragraph("Sprint 1", style_td_bold), Paragraph("Days 1–7 (Storage & Consistent Hash)", style_td), Paragraph("13 SP", style_td), Paragraph("13 SP", style_td), Paragraph("13 SP", style_td), Paragraph("<b>39 SP</b>", style_td)],
        [Paragraph("Sprint 2", style_td_bold), Paragraph("Days 8–14 (Bloom Filter & Stream Ingest)", style_td), Paragraph("13 SP", style_td), Paragraph("13 SP", style_td), Paragraph("13 SP", style_td), Paragraph("<b>39 SP</b>", style_td)],
        [Paragraph("Sprint 3", style_td_bold), Paragraph("Days 15–21 (Transformer LM & DuckDB)", style_td), Paragraph("13 SP", style_td), Paragraph("13 SP", style_td), Paragraph("13 SP", style_td), Paragraph("<b>39 SP</b>", style_td)],
        [Paragraph("Sprint 4", style_td_bold), Paragraph("Days 22–28 (RAG Integration & Web Portal)", style_td), Paragraph("13 SP", style_td), Paragraph("13 SP", style_td), Paragraph("13 SP", style_td), Paragraph("<b>39 SP</b>", style_td)],
        [Paragraph("Total", style_td_bold), Paragraph("4 Weeks (Platform Ready for Defense)", style_td_bold), Paragraph("<b>52 SP</b>", style_td_bold), Paragraph("<b>52 SP</b>", style_td_bold), Paragraph("<b>52 SP</b>", style_td_bold), Paragraph("<b>156 SP</b>", style_td_bold)],
    ]
    t_sprint = Table(sprint_data, colWidths=[65, 179, 65, 65, 65, 65])
    t_sprint.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#E2E8F0')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_sprint)
    elements.append(Spacer(1, 10))

    # Page Break for Tickets Table
    elements.append(PageBreak())

    # Section 3: Tickets Catalog
    elements.append(Paragraph("3. Complete Jira Ticket Catalog & Commit Linkages (AUT-101 – AUT-132)", style_h1))
    
    ticket_table_data = [
        [
            Paragraph("Key", style_th),
            Paragraph("Type", style_th),
            Paragraph("Summary & Commit Tag", style_th),
            Paragraph("SP", style_th),
            Paragraph("Assignee", style_th),
            Paragraph("Status", style_th),
        ]
    ]
    for t in TICKETS:
        ticket_table_data.append([
            Paragraph(f"<b>{t['key']}</b>", style_td_bold),
            Paragraph(t["type"], style_td),
            Paragraph(f"<b>{t['summary']}</b><br/><font color='#64748B'>{t['commit']}</font>", style_td),
            Paragraph(f"<b>{t['sp']}</b>", style_td_bold),
            Paragraph(t["assignee"].split()[0], style_td),
            Paragraph(f"<font color='#059669'><b>{t['status']}</b></font>", style_td),
        ])

    t_tickets = Table(ticket_table_data, colWidths=[48, 42, 254, 30, 70, 60])
    t_tickets.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elements.append(t_tickets)
    elements.append(Spacer(1, 10))

    # Traceability Notes
    elements.append(Paragraph("4. Traceability & Automatic Jira Status Transitions", style_h1))
    elements.append(Paragraph(
        "By enforcing the <code>[AUT-xxx]</code> commit message standard across all Git feature branches, "
        "the GitHub for Jira integration automatically advances stories from <i>In Progress</i> to <i>Code Review</i> "
        "and <i>Done</i>. Each member has completed exactly 52 Story Points, demonstrating balanced collaboration for academic evaluation.",
        style_body
    ))

    doc.build(elements, canvasmaker=NumberedCanvas)
    print(f"[OK] Saved PDF: {filepath}")

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
    export_jira_csv(csv_path)

    docx_path = os.path.join(base_dir, "AutoCare_AI_Jira_Workflow_Backlog.docx")
    build_jira_docx(docx_path)

    pdf_path = os.path.join(base_dir, "AutoCare_AI_Jira_Workflow_Backlog.pdf")
    build_jira_pdf(pdf_path)

    # Sync to Desktop and brain artifacts
    import shutil
    targets = [
        (csv_path, os.path.join(desktop_dir, "jira_tickets_import.csv")),
        (docx_path, os.path.join(desktop_dir, "AutoCare_AI_Jira_Workflow_Backlog.docx")),
        (pdf_path, os.path.join(desktop_dir, "AutoCare_AI_Jira_Workflow_Backlog.pdf")),
        (docx_path, os.path.join(brain_dir, "AutoCare_AI_Jira_Workflow_Backlog.docx")),
        (pdf_path, os.path.join(brain_dir, "AutoCare_AI_Jira_Workflow_Backlog.pdf")),
        (os.path.join(base_dir, "JIRA_AGILE_WORKFLOW.md"), os.path.join(desktop_dir, "JIRA_AGILE_WORKFLOW.md")),
    ]
    for src, dst in targets:
        shutil.copy2(src, dst)
        print(f"[SYNC] {src} -> {dst}")

    print("\nAll Jira Agile workflow documents generated and synchronized successfully!")
