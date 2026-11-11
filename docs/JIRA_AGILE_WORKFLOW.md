# AutoCare AI: 5-Member Jira Agile Scrum Workflow & Team Work Breakdown Structure (WBS)

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
