# AutoCare AI: 6-Month Agile Jira Backlog & Sprint Roadmap

This document outlines the professional **Agile Scrum Methodology** for AutoCare AI across a 6-month FYP lifecycle (divided into six 4-week Sprints). It provides ready-to-import Jira Epics, User Stories, Spikes, Bug tickets, Story Points, and Git commit linkages to demonstrate consistent, enterprise-grade engineering.

---

## 📅 6-Month Sprint Roadmap Overview

| Sprint | Timeline | Theme / Objective | Key Epics Covered | Total Story Points |
| :--- | :--- | :--- | :--- | :--- |
| **Sprint 1 (Weeks 1–4)** | Month 1 | Foundation, Architecture & Taxonomy Setup | EPIC-1: Data Ingestion & Vehicle Scope | 28 SP |
| **Sprint 2 (Weeks 5–8)** | Month 2 | Hybrid Retrieval-Augmented Generation (RAG) | EPIC-2: Multilingual Search & Grounding | 34 SP |
| **Sprint 3 (Weeks 9–12)**| Month 3 | Supervised Triage ML & Calibration Layer | EPIC-3: Cost-Sensitive Triage & Abstention | 40 SP |
| **Sprint 4 (Weeks 13–16)**| Month 4 | Multi-Hop Causal Reasoning & Knowledge Graph | EPIC-4: Causal Inference & Explanation | 38 SP |
| **Sprint 5 (Weeks 17–20)**| Month 5 | Repair Verification & Similar-Case Memory | EPIC-5: Workshop Audit & Health Index | 36 SP |
| **Sprint 6 (Weeks 21–24)**| Month 6 | System Hardening, UI Integration & Evaluation | EPIC-6: Delivery, CI/CD & Final Defence | 26 SP |
| **Total** | **24 Weeks** | **End-to-End Decision Support System** | **6 Epics, 32 User Stories** | **202 Story Points** |

---

## 🎯 Epics & Jira Tickets Catalog

### EPIC-1: Automotive Knowledge Ingestion & Scope Definition
- **Ticket ID:** `AUT-101` (Story, 5 SP)
  - **Summary:** Define 3-Vehicle Taxonomy & Specifications (Corolla, Civic, Swift 2015–2025)
  - **Description:** Build database schema and seed tables for 96 engine, transmission, and trim configurations.
  - **Acceptance Criteria:** `vehicle` table seeded; rejects unsupported vehicles with informative guidance.
  - **Git Branch:** `feature/us1-vehicle-taxonomy`
  - **Commit Tag:** `feat(taxonomy): [AUT-101] seed 96 vehicle configurations for Corolla, Civic, Swift`

- **Ticket ID:** `AUT-102` (Story, 8 SP)
  - **Summary:** SAE J2012 OBD-II Trouble Code Parser & Ingestion Pipeline
  - **Description:** Ingest 18 standard diagnostic codes with symptoms, causes, and severities into SQLite/Postgres.
  - **Git Branch:** `feature/us1-vehicle-taxonomy`
  - **Commit Tag:** `feat(dtc): [AUT-102] ingest SAE J2012 standard diagnostic trouble codes`

- **Ticket ID:** `AUT-103` (Story, 8 SP)
  - **Summary:** Structure-Aware PDF Extraction & Manual Chunking Engine
  - **Description:** PDF parser with header detection, warning/caution box isolation, and page mapping.
  - **Git Branch:** `feature/us2-multilingual-rag`
  - **Commit Tag:** `feat(ingest): [AUT-103] structure-aware PDF chunking with warning callouts`

---

### EPIC-2: Multilingual Hybrid Retrieval (RAG)
- **Ticket ID:** `AUT-104` (Story, 8 SP)
  - **Summary:** Implement BM25 Keyword Index & Semantic Embedding Vector Store
  - **Description:** Hybrid retrieval combining BM25 lexical search with BGE-M3 dense embeddings and cosine similarity.
  - **Acceptance Criteria:** Hybrid alpha blending produces top-20 candidate pool; reranker filters evidence.
  - **Git Branch:** `feature/us2-multilingual-rag`
  - **Commit Tag:** `feat(retrieval): [AUT-104] implement hybrid BM25 + dense semantic vector search`

- **Ticket ID:** `AUT-105` (Story, 8 SP)
  - **Summary:** Multilingual Query Translation & Urdu/Roman Urdu Automotive Lexicon
  - **Description:** Domain-specific glossary translation mapping Pakistani mechanical terms (dhuwan, awaz, garam, jhatka) to standard automotive ontology.
  - **Git Branch:** `feature/us2-multilingual-rag`
  - **Commit Tag:** `feat(nlp): [AUT-105] add Urdu and Roman Urdu automotive glossary translator`

- **Ticket ID:** `AUT-106` (Story, 5 SP)
  - **Summary:** OCR Scanner & Vision Model Fallback for Dashboard Fault Codes
  - **Description:** Camera/photo intake pipeline extracting DTC alphanumeric codes from scanner photos with regex validation.
  - **Git Branch:** `feature/us3-photo-code-scanner`
  - **Commit Tag:** `feat(ocr): [AUT-106] camera code extractor with regex verification`

---

### EPIC-3: Cost-Sensitive Machine Learning & Confidence Calibration
- **Ticket ID:** `AUT-107` (Story, 8 SP)
  - **Summary:** Train Supervised Fault Category & Repair Urgency Triage Classifier (M2)
  - **Description:** Multi-label TF-IDF + Calibrated Classifier with Grouped Cross-Validation. Cost-sensitive loss weighting Critical safety false negatives at 10x penalty.
  - **Acceptance Criteria:** Critical False Negative Rate $< 0.15$ on held-out vehicle test fold.
  - **Git Branch:** `feature/us4-cost-sensitive-triage`
  - **Commit Tag:** `feat(ml): [AUT-107] train cost-sensitive triage classifier with grouped CV`

- **Ticket ID:** `AUT-108` (Story, 5 SP)
  - **Summary:** Platt Scaling & Temperature Calibration Engine (M3)
  - **Description:** Calibrate raw model probabilities to true empirical risk; track ECE (Expected Calibration Error).
  - **Git Branch:** `feature/us5-calibrated-confidence`
  - **Commit Tag:** `feat(calibration): [AUT-108] implement Platt scaling and ECE calculation`

- **Ticket ID:** `AUT-109` (Story, 5 SP)
  - **Summary:** Selective Abstention Gate & Uncertainty Thresholds
  - **Description:** Gate answers if reranker top score $< 0.30$ or calibrated confidence $< 0.70$.
  - **Git Branch:** `feature/us5-calibrated-confidence`
  - **Commit Tag:** `feat(gate): [AUT-109] enforce selective abstention when evidence is insufficient`

---

### EPIC-4: Multi-Hop Causal Reasoning & Explanation Tracing
- **Ticket ID:** `AUT-110` (Story, 8 SP)
  - **Summary:** Directed Causal Knowledge Graph Inference Engine (M6)
  - **Description:** NetworkX directed causal graph linking symptoms $\rightarrow$ failure modes $\rightarrow$ root causes with path traversal.
  - **Git Branch:** `feature/us8-knowledge-graph`
  - **Commit Tag:** `feat(kg): [AUT-110] multi-hop causal inference engine with NetworkX`

- **Ticket ID:** `AUT-111` (Story, 5 SP)
  - **Summary:** Structured Explanation Trace Builder (M4)
  - **Description:** Assemble auditable diagnostic traces detailing extracted symptoms, active DTCs, manual citations, and causal graph paths.
  - **Git Branch:** `feature/us6-explanation-trace`
  - **Commit Tag:** `feat(trace): [AUT-111] build transparent multi-hop explanation trace`

---

### EPIC-5: Workshop Repair Verification & Vehicle Health Index
- **Ticket ID:** `AUT-112` (Story, 8 SP)
  - **Summary:** Repair Verifier & Workshop Estimate Cross-Checker (M5)
  - **Description:** Natural Language Inference / entailment checking between workshop claims and manual citations, issuing `supported`, `partially_supported`, or `unsupported` verdicts.
  - **Git Branch:** `feature/us7-repair-verifier`
  - **Commit Tag:** `feat(verifier): [AUT-112] repair estimate verifier with evidence citations`

- **Ticket ID:** `AUT-113` (Story, 8 SP)
  - **Summary:** Vehicle Health Index & Maintenance Interval Forecaster (M7)
  - **Description:** Multi-subsystem degradation scoring (Engine, Transmission, Braking, Cooling, Tyres, Electrical) with severe Pakistani climate multipliers.
  - **Git Branch:** `feature/us10-health-predictor`
  - **Commit Tag:** `feat(health): [AUT-113] multi-component health index and service interval forecaster`

- **Ticket ID:** `AUT-114` (Story, 5 SP)
  - **Summary:** Case-Based Memory Bank with Provenance Tracking (M8)
  - **Description:** Historical case retrieval comparing symptom embeddings and returning verified resolutions with `seeded` vs `real` provenance.
  - **Git Branch:** `feature/us9-case-bank`
  - **Commit Tag:** `feat(casebank): [AUT-114] similar case bank with provenance tracking`

- **Ticket ID:** `AUT-115` (Story, 5 SP)
  - **Summary:** Automated PDF Service Audit Certificate Generation (M9)
  - **Description:** ReportLab PDF report generation with case summary, triage level, evidence citations, and workshop guidance.
  - **Git Branch:** `feature/us11-audit-report-pdf`
  - **Commit Tag:** `feat(report): [AUT-115] generate verifiable PDF service audit reports`

---

### EPIC-6: Frontend Integration, Testing & Cloud CI/CD
- **Ticket ID:** `AUT-116` (Story, 8 SP)
  - **Summary:** React Modern UI Screens (Verify, Health, Similar Cases, Query)
  - **Description:** Production responsive interface with role-based navigation and dark mode aesthetic.
  - **Git Branch:** `feature/us12-vision-damage-assessor`
  - **Commit Tag:** `feat(ui): [AUT-116] responsive React screens for diagnosis, verifier, and health index`

- **Ticket ID:** `AUT-117` (Story, 5 SP)
  - **Summary:** GitHub Actions Automated CI/CD Pipeline & Ruff Linting
  - **Description:** Automated workflow running tests, lint checks, and build validation on every PR.
  - **Git Branch:** `main`
  - **Commit Tag:** `ci: [AUT-117] setup GitHub Actions workflow for backend tests and frontend build`

- **Ticket ID:** `AUT-118` (Story, 5 SP)
  - **Summary:** Docker Microservices & Production Containerization
  - **Description:** Dockerfile and Docker Compose orchestration for FastAPI, PostgreSQL, Redis, and React.
  - **Git Branch:** `main`
  - **Commit Tag:** `ops: [AUT-118] add multi-container Docker compose for production scaling`

---

## 🛠️ How to Connect Jira to GitHub

1. **Create a Free Jira Software Project:**
   - Go to [atlassian.com/software/jira](https://www.atlassian.com/software/jira) $\rightarrow$ Create Project $\rightarrow$ Choose **Scrum**.
   - Set Project Key: `AUT`.
2. **Link Jira to your GitHub Repository:**
   - In Jira: Settings $\rightarrow$ Apps $\rightarrow$ Search for **GitHub for Jira**.
   - Connect account `marketbul` and select repository `marketbul/autocare-ai`.
3. **Automatic Jira Status Tracking via Git Commits:**
   - Whenever you commit with the ticket key, e.g.:
     `git commit -m "[AUT-107] feat: train cost-sensitive triage classifier"`
   - Jira will automatically attach the commit, branch, and PR to the ticket and move it to **In Progress** or **Done**!
