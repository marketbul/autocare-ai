# AutoCare AI: Master 138-Ticket Jira Agile Scrum Workflow & Commit Traceability

**Institution:** Punjab University College of Information Technology (PUCIT), University of the Punjab  
**Track:** BS Data Science Final Year Project (FYP) / Big Data Distributed Systems  
**Project Key:** `AUT` | **Remote Repository:** `https://github.com/marketbul/autocare-ai.git`  
**Total Tickets:** **138 Tickets** (124 Completed + 14 Future Reserved)  
**Total Velocity:** **579 Story Points** across 6 Sprints  

---

## 📅 1. 6-Sprint Master Roadmap Overview

| Sprint | Timeline / Milestone Scope | Tickets Covered | Status | Story Points |
| :--- | :--- | :---: | :---: | :---: |
| **Sprint 1** | Architecture, Vehicle Taxonomy & Manual Chunking | 30 Tickets | **Done (100%)** | 102 SP |
| **Sprint 2** | Cost-Sensitive Triage ML & Platt Calibration | 25 Tickets | **Done (100%)** | 95 SP |
| **Sprint 3** | Causal Knowledge Graph & Workshop Quote Verifier | 28 Tickets | **Done (100%)** | 106 SP |
| **Sprint 4** | Dataset Scaling, Causal LM from Scratch & Web UI | 41 Tickets | **Done (100%)** | 154 SP |
| **Sprint 5** | **[FUTURE]** Kafka Ingestion, MinIO Lakehouse & Consistent Hashing | 6 Tickets | **To Do (Reserved)** | 34 SP |
| **Sprint 6** | **[FUTURE]** PySpark Streaming, DuckDB OLAP Analytics & Defense | 8 Tickets | **To Do (Reserved)** | 44 SP |
| **Total** | **End-to-End Enterprise Big Data Automotive Platform** | **138 Tickets** | **124 Done / 14 To Do** | **579 SP** |

---

## 👥 2. 5-Member Team Allocation

1. **Abdullah (BSDSF23A035)** — *Group Leader & System Architect / RAG Lead*
2. **Talha Ali Bhatti (BSDSF23A016)** — *Lead Distributed Storage & Ingestion Engineer*
3. **Danial Hameed (BSDSF23A014)** — *Lead Data Engineer & Multilingual Corpus Lead*
4. **Ahmad Zahid (BSDSF23A033)** — *Lead ML Triage & Confidence Calibration*
5. **Muhammad Abdullah (BSDSF23A032)** — *Lead Frontend, Analytics & Regional Economics*

---

## 🎯 3. Master Tickets Catalog (First 124 Commits Mapped + Future Reserved Space)

Every single commit in the Git repository is directly mapped to a Jira ticket below, followed by reserved tickets for future Big Data work:

| Key | Sprint | Summary | SP | Assignee | Git Commit Hash | Status |
| :--- | :--- | :--- | :---: | :--- | :---: | :---: |
| **AUT-095** | Sprint | Initial commit: AutoCare AI prototype with Stories 1-4, 12, RAG core, and React UI | 5 SP | Abdullah | `76b7256` | **Done** |
| **AUT-096** | Sprint | docs: add FYP proposal and user stories specifications | 3 SP | Abdullah | `3b3e2c1` | **Done** |
| **AUT-097** | Sprint | feat: complete FYP-1 implementation for 3 cars (2015-2025), intelligent modules M3-M9, and UI screen | 5 SP | Abdullah | `859693e` | **Done** |
| **AUT-098** | Sprint | fix: make user_vehicle_id optional on verification/case bank APIs and add graceful ml fallback | 3 SP | Abdullah | `b19f061` | **Done** |
| **AUT-099** | Sprint | feat: add 45 comprehensive vehicle manuals and downloader script across Corolla, Civic, and Swift (2 | 3 SP | Talha | `bc39793` | **Done** |
| **AUT-117** | Sprint | ci: add GitHub Actions CI workflow, PR template, Docker compose, and Jira 6-month sprint backlog | 3 SP | Muhammad | `37ede42` | **Done** |
| **AUT-101** | Sprint | test(taxonomy): add vehicle configuration schema unit tests | 3 SP | Talha | `565e202` | **Done** |
| **AUT-101** | Sprint | feat(taxonomy): seed 96 vehicle configurations for Corolla, Civic, Swift (2015-2025) | 3 SP | Talha | `e602e60` | **Done** |
| **AUT-102** | Sprint | feat(dtc): ingest SAE J2012 diagnostic trouble codes and symptoms | 3 SP | Talha | `7dde6bb` | **Done** |
| **AUT-102** | Sprint | test(dtc): add assertions for DTC severity and possible cause mapping | 3 SP | Talha | `b225afc` | **Done** |
| **AUT-77** | Sprint | Merge pull request #1 from marketbul/feature/us1-vehicle-taxonomy | 3 SP | Muhammad | `0c83883` | **Done** |
| **AUT-103** | Sprint | feat(ingest): structure-aware PDF chunker isolating warnings and tables | 3 SP | Danial | `91d5193` | **Done** |
| **AUT-104** | Sprint | feat(retrieval): implement BM25 lexical retriever with tokenization | 3 SP | Abdullah | `977b502` | **Done** |
| **AUT-105** | Sprint | feat(nlp): add Urdu and Roman Urdu automotive glossary translator | 3 SP | Abdullah | `cf7724f` | **Done** |
| **AUT-104** | Sprint | test(retrieval): test hybrid BM25 + dense semantic retrieval on manual passages | 3 SP | Abdullah | `4d4eb42` | **Done** |
| **AUT-82** | Sprint | Merge pull request #2 from marketbul/feature/us2-multilingual-rag | 5 SP | Muhammad | `61b91b9` | **Done** |
| **AUT-106** | Sprint | feat(ocr): camera fault code reader with regex verification | 3 SP | Danial | `d7243f0` | **Done** |
| **AUT-106B** | Sprint | fix(ocr): enhance contrast and binarization for low-light scanner screens | 3 SP | Danial | `de41956` | **Done** |
| **AUT-85** | Sprint | Merge pull request #3 from marketbul/feature/us3-photo-code-scanner | 3 SP | Talha | `efd5dbf` | **Done** |
| **AUT-107** | Sprint | test(triage): add baseline evaluation test on symptom corpora | 5 SP | Ahmad | `dc826eb` | **Done** |
| **AUT-107** | Sprint | feat(ml): train baseline gradient boosting classifier (high Critical error 68.2%) | 3 SP | Ahmad | `4a2eb79` | **Done** |
| **AUT-107B** | Sprint | refactor(ml): implement cost-sensitive loss weighting dropping Critical FNR to 11.4% | 3 SP | Ahmad | `758b744` | **Done** |
| **AUT-89** | Sprint | Merge pull request #4 from marketbul/feature/us4-cost-sensitive-triage | 5 SP | Ahmad | `20afd2b` | **Done** |
| **AUT-108** | Sprint | feat(calibration): implement Platt scaling and temperature calibration (M3) | 5 SP | Ahmad | `e410822` | **Done** |
| **AUT-108** | Sprint | test(calibration): evaluate Expected Calibration Error (ECE) and Brier reliability score | 5 SP | Ahmad | `ec2ff87` | **Done** |
| **AUT-109** | Sprint | feat(gate): add selective abstention gate for high-uncertainty vehicle queries | 3 SP | Ahmad | `bc33b8b` | **Done** |
| **AUT-93** | Sprint | Merge pull request #5 from marketbul/feature/us5-calibrated-confidence | 3 SP | Ahmad | `0ced1cc` | **Done** |
| **AUT-111** | Sprint | feat(trace): assemble transparent multi-hop explanation traces (M4) | 5 SP | Talha | `178ab5b` | **Done** |
| **AUT-111B** | Sprint | test(trace): verify explanation trace completeness across all 3 vehicles | 3 SP | Muhammad | `fb812a3` | **Done** |
| **AUT-96** | Sprint | Merge pull request #6 from marketbul/feature/us6-explanation-trace | 5 SP | Muhammad | `d655210` | **Done** |
| **AUT-112** | Sprint | test(verifier): add failing unit test for workshop repair claim verification | 5 SP | Ahmad | `55d6f79` | **Done** |
| **AUT-112** | Sprint | feat(verifier): implement repair verifier using premise entailment logic (M5) | 5 SP | Ahmad | `1bc023c` | **Done** |
| **AUT-112B** | Sprint | docs(verifier): enforce Proposal Section 17 non-accusatory ethical guidelines | 5 SP | Ahmad | `6b4261d` | **Done** |
| **AUT-100** | Sprint | Merge pull request #7 from marketbul/feature/us7-repair-verifier | 5 SP | Ahmad | `2c9883b` | **Done** |
| **AUT-110** | Sprint | feat(kg): build NetworkX directed causal graph with 49 nodes and 36 causal edges (M6) | 5 SP | Abdullah | `d3fe41e` | **Done** |
| **AUT-110** | Sprint | test(kg): test multi-hop causal inference from overheating symptom to head gasket | 5 SP | Abdullah | `8be24e1` | **Done** |
| **AUT-110** | Sprint | refactor(kg): optimize cycle detection and confidence propagation in causal chains | 5 SP | Ahmad | `09fe894` | **Done** |
| **AUT-104** | Sprint | Merge pull request #8 from marketbul/feature/us8-knowledge-graph | 3 SP | Abdullah | `0a50519` | **Done** |
| **AUT-114** | Sprint | feat(casebank): implement similar-case memory bank with resolution tracking (M8) | 3 SP | Muhammad | `70a0333` | **Done** |
| **AUT-114** | Sprint | feat(casebank): add provenance tracking distinguishing seeded vs real user cases | 3 SP | Muhammad | `9183870` | **Done** |
| **AUT-107** | Sprint | Merge pull request #9 from marketbul/feature/us9-case-bank | 3 SP | Ahmad | `1dbaa7b` | **Done** |
| **AUT-113** | Sprint | feat(health): calculate 6-component subsystem health index and mileage degradation (M7) | 3 SP | Talha | `d81ae36` | **Done** |
| **AUT-113** | Sprint | feat(health): implement scheduled maintenance forecaster with Pakistan severe climate multiplier | 3 SP | Talha | `27d4c25` | **Done** |
| **AUT-113** | Sprint | test(health): verify maintenance interval prediction under severe city driving profile | 3 SP | Talha | `2cd6169` | **Done** |
| **AUT-111** | Sprint | Merge pull request #10 from marketbul/feature/us10-health-predictor | 3 SP | Talha | `b8909fb` | **Done** |
| **AUT-115** | Sprint | feat(report): implement ReportLab PDF service audit report generator (M9) | 3 SP | Danial | `97aa1ae` | **Done** |
| **AUT-115** | Sprint | test(report): test PDF certificate generation with case metadata and checklist | 3 SP | Danial | `214fcef` | **Done** |
| **AUT-114** | Sprint | Merge pull request #11 from marketbul/feature/us11-audit-report-pdf | 3 SP | Muhammad | `9a40892` | **Done** |
| **AUT-116** | Sprint | feat(ui): add responsive React screens for repair verification and health index | 3 SP | Muhammad | `1006455` | **Done** |
| **AUT-116** | Sprint | feat(ui): integrate SimilarCasesScreen and PDF report download in frontend | 3 SP | Muhammad | `cea7a3b` | **Done** |
| **AUT-119** | Sprint | feat(manuals): download and index 45 comprehensive OEM manuals for 3 cars | 3 SP | Danial | `19437e2` | **Done** |
| **AUT-120** | Sprint | test(suite): author comprehensive acceptance test suite with 115 passing tests | 5 SP | Muhammad | `a1275ae` | **Done** |
| **AUT-119** | Sprint | Merge pull request #12 from marketbul/feature/us12-vision-damage-assessor | 3 SP | Muhammad | `b4dd9aa` | **Done** |
| **AUT-120** | Sprint | chore(release): v1.0.0-fyp1 final integrated decision support system | 3 SP | Abdullah | `428ac44` | **Done** |
| **AUT-122** | Sprint | fix(ci): resolve GitHub Actions CI build issues, add missing dependencies, and fix JSX comment synta | 5 SP | Danial | `ad8333f` | **Done** |
| **AUT-122** | Sprint | fix(sql): change comment prefix to standard SQL double-dash in schema.sqlite.sql | 3 SP | Danial | `f49e4a3` | **Done** |
| **AUT-123** | Sprint | fix(rag): add graceful fallback to extractive generator when no cloud LLM key is configured | 5 SP | Abdullah | `17f3d08` | **Done** |
| **AUT-123** | Sprint | docs: update project team members and add collaborator attribution | 3 SP | Abdullah | `24b4e07` | **Done** |
| **AUT-117** | Sprint | feat(corpus): implement interactive 45 manuals corpus explorer and hybrid RAG details | 5 SP | Danial | `4bcfc7f` | **Done** |
| **AUT-118** | Sprint | feat(graph): add automotive causal knowledge graph visual inspector | 5 SP | Ahmad | `1e7b895` | **Done** |
| **AUT-119** | Sprint | feat(analytics): add model reliability dashboard with Platt calibration and triage FNR matrix | 5 SP | Ahmad | `16d93f6` | **Done** |
| **AUT-120** | Sprint | feat(pricing): implement Pakistan spare parts & workshop labour cost estimator in PKR | 3 SP | Muhammad | `178762a` | **Done** |
| **AUT-121** | Sprint | feat(system): integrate all 5-person FYP-1 modules, navigation, and defense architecture specificati | 3 SP | Abdullah | `dce9a7a` | **Done** |
| **AUT-130** | Sprint | docs: finalize FYP-1 defense specification with Friday-to-Monday sprint git audit | 3 SP | Muhammad | `8c740f7` | **Done** |
| **AUT-131** | Sprint | fix(api): clean up service attribute assignment syntax in graph_export | 5 SP | Muhammad | `af1d294` | **Done** |
| **AUT-124** | Sprint | feat(auth): implement Google OAuth token verification and automatic account provisioning | 5 SP | Abdullah | `d3133d5` | **Done** |
| **AUT-124** | Sprint | test(auth): add comprehensive test suite for Google account auto-registration | 5 SP | Abdullah | `3868db6` | **Done** |
| **AUT-124** | Sprint | feat(ui): integrate Google Sign-In button and instant verification modal in AuthScreen | 5 SP | Abdullah | `35c1736` | **Done** |
| **AUT-125** | Sprint | feat(kg): enhance multi-hop causal inference path scoring and diagnostic ranking | 5 SP | Abdullah | `744f8f2` | **Done** |
| **AUT-126** | Sprint | feat(ui): redesign web dashboard into Linear/Raycast dark-zinc Bento Grid layout | 5 SP | Abdullah | `9629858` | **Done** |
| **AUT-127** | Sprint | feat(mobile): build cross-platform mobile apps using Flutter and React Native Expo | 5 SP | Muhammad | `3d4cbc5` | **Done** |
| **AUT-128** | Sprint | docs(design): add Figma token studio tokens and design system specifications | 5 SP | Abdullah | `6468a89` | **Done** |
| **AUT-129** | Sprint | fix(api): robust attribute access for knowledge graph in export endpoint | 3 SP | Muhammad | `18a51f0` | **Done** |
| **AUT-130** | Sprint | style(ui): aesthetic Linear and Raycast dark-zinc redesign with electric violet and emerald accents | 5 SP | Muhammad | `0e89971` | **Done** |
| **AUT-131** | Sprint | feat(ui): clean dual-theme light/dark mode and simple SaaS landing card with role switcher | 5 SP | Muhammad | `4ff82a8` | **Done** |
| **AUT-132** | Sprint | feat(ui): add settings screen, simplify executive dashboard, and declutter navigation | 5 SP | Ahmad | `862cee4` | **Done** |
| **AUT-133** | Sprint | refactor(ui): remove redundant theme toggle from lower left corner account bar | 5 SP | Muhammad | `7b2d407` | **Done** |
| **AUT-134** | Sprint | docs(business): Barringer & Ireland business model template for AutoCare AI (Chapter 4) | 3 SP | Muhammad | `1c676eb` | **Done** |
| **AUT-135** | Sprint | docs(assignment): generate printable PDF assignment with all group members and roll numbers | 3 SP | Muhammad | `fe9ef56` | **Done** |
| **AUT-146** | Sprint | docs: update group member roll numbers and student names in business model assignment | 3 SP | Danial | `d26d061` | **Done** |
| **AUT-147** | Sprint | docs: add AGENTS.md with permanent team roster and attribution guidelines | 5 SP | Abdullah | `ac69679` | **Done** |
| **AUT-148** | Sprint | docs: streamline business model pdf to clean 3-page template matching Chapter 4 rubric | 5 SP | Ahmad | `49f89d9` | **Done** |
| **AUT-136** | Sprint | feat(ui): upgrade to enterprise SaaS UI/UX with sleek topbar, authentic Google OAuth, and Linear des | 5 SP | Danial | `f736ee5` | **Done** |
| **AUT-137** | Sprint | feat(ui): consolidate car owner diagnostic journey into unified 4-stage dashboard with PKR cost tria | 5 SP | Ahmad | `3a15e7c` | **Done** |
| **AUT-151** | Sprint | docs(pid): add 4-week professional term project initiation document in PDF and DOCX formats | 3 SP | Talha | `7d6535a` | **Done** |
| **AUT-140** | Sprint | feat(arch): initialize AI Auto Pakistan data engine architecture, source registry, and audit logger  | 3 SP | Ahmad | `981835b` | **Done** |
| **AUT-141** | Sprint | feat(taxonomy): implement 18-category Pakistani automotive fault taxonomy and fleet specs (Phase 2) | 3 SP | Ahmad | `09d09af` | **Done** |
| **AUT-142** | Sprint | feat(schema): build normalized Pydantic automotive records and unit tests (Phase 2) | 5 SP | Ahmad | `6adc549` | **Done** |
| **AUT-143** | Sprint | feat(sources): add YouTube collector, Facebook import, PakWheels importer, and consent-gated intervi | 5 SP | Ahmad | `d546df0` | **Done** |
| **AUT-144** | Sprint | feat(templates): add CSV templates for Facebook, PakWheels, mechanic interviews, and owner reports ( | 3 SP | Danial | `7e77834` | **Done** |
| **AUT-145** | Sprint | feat(cleaning): implement canonical deduplication, multilingual normalizer, and quality validator (P | 5 SP | Talha | `0a2616b` | **Done** |
| **AUT-146** | Sprint | feat(media): implement media asset vault and transcript claim extraction pipeline (Phase 8) | 5 SP | Danial | `65cf36b` | **Done** |
| **AUT-147** | Sprint | feat(storage): add unified relational DDL schema and multi-source database manager (Phase 9) | 5 SP | Talha | `6066265` | **Done** |
| **AUT-148** | Sprint | feat(ml): build leak-free grouped ML dataset splitter with dataset card generation (Phase 11) | 5 SP | Ahmad | `8c11d5f` | **Done** |
| **AUT-149** | Sprint | feat(reports): add dataset quality report generator, CLI import commands, and Phase 8-11 integration | 3 SP | Talha | `f239a27` | **Done** |
| **AUT-150** | Sprint | chore(git): ignore dynamic runtime data engine outputs and log files | 3 SP | Abdullah | `46f02a6` | **Done** |
| **AUT-151** | Sprint | feat(storage): extend database manager with vehicle fleet seeding, review workflow, and router mount | 3 SP | Talha | `dcc632e` | **Done** |
| **AUT-152** | Sprint | feat(ingest): add LocalDatasetConsolidator unifying OBD-II codes, symptom corpus, manuals, and PKR p | 3 SP | Talha | `cc111a7` | **Done** |
| **AUT-153** | Sprint | test(server): isolate semantic symptom groups in ML splitter and add dashboard API integration tests | 5 SP | Ahmad | `9196192` | **Done** |
| **AUT-154** | Sprint | feat(dashboard): build FastAPI dataset engineering API and interactive localhost dashboard | 5 SP | Danial | `0090282` | **Done** |
| **AUT-155** | Sprint | feat(sources): add AutomotiveBlogImporter and CSV research template for authorized blogs | 3 SP | Danial | `510f5ca` | **Done** |
| **AUT-156** | Sprint | feat(dashboard): add blog CSV import, paste-CSV input, and in-app collection guide to localhost UI | 5 SP | Muhammad | `175f55c` | **Done** |
| **AUT-157** | Sprint | feat(youtube-media): add YouTube comment threads/solution extractor and ffmpeg authorized video/scre | 5 SP | Danial | `54513b4` | **Done** |
| **AUT-158** | Sprint | feat(ml-export): add AI-Agent JSONL exporter with verified-fact boundary and integration tests | 3 SP | Talha | `0f97bf8` | **Done** |
| **AUT-159** | Sprint | feat(pipeline): wire autonomous YouTube comments, authorized video processing, and agent-jsonl expor | 5 SP | Danial | `8ed39f4` | **Done** |
| **AUT-160** | Sprint | feat(media-damage): detect spoken Urdu/English damage cues and capture exact timestamp screenshots | 5 SP | Talha | `3ef1e02` | **Done** |
| **AUT-161** | Sprint | feat(bundle): build zero-port standalone dataset folder exporter and offline file:// HTML viewer | 5 SP | Danial | `201811b` | **Done** |
| **AUT-162** | Sprint | feat(launcher): add root-level one-click run_auto_collector.bat and Consented_Mechanic_Videos drop f | 3 SP | Talha | `b5fa48e` | **Done** |
| **AUT-163** | Sprint | feat(cc-youtube): support Creative Commons videoLicense search and safe yt_dlp audio+video extractio | 5 SP | Danial | `23a19bc` | **Done** |
| **AUT-164** | Sprint | fix(whisper): decode 16kHz WAV via stdlib wave+numpy for faster-whisper and link media_assets FKs | 5 SP | Talha | `f8f8f19` | **Done** |
| **AUT-165** | Sprint | feat(viewer): render screenshot/audio links in offline dataset_viewer.html and update stats test | 3 SP | Danial | `9bd5288` | **Done** |
| **AUT-166** | Sprint | fix(youtube-audit): deduplicate CC-BY YouTube records, filter STT noise, and add fleet word-boundary | 5 SP | Ahmad | `8af0f39` | **Done** |
| **AUT-167** | Sprint | feat(youtube-qa): add Toyota/Suzuki/Honda queries, YouTube pagination, and consolidated Q&A JSON exp | 5 SP | Danial | `6d7ffd3` | **Done** |
| **AUT-168** | Sprint | feat(facebook-local): add local Facebook_Community_QA drop folder, flexible Q&A importer, and facebo | 5 SP | Danial | `0d50c32` | **Done** |
| **AUT-169** | Sprint | feat(open-qa): add Stack Exchange Mechanics (CC-BY-SA) and NHTSA Safety REST collectors for RAG & ML | 5 SP | Danial | `7f630bf` | **Done** |
| **AUT-170** | Sprint | fix(open-qa): expand Stack Exchange/NHTSA queries, unify KIA brand casing, and disambiguate NHTSA co | 3 SP | Danial | `a0cb72f` | **Done** |
| **AUT-171** | Sprint | feat(scale-10k): scale open APIs, YouTube/PakWheels channel queries, and export caps to 10,760 recor | 5 SP | Danial | `32e2460` | **Done** |
| **AUT-184** | Sprint | feat(dataset): consolidate multi-source automotive dataset and automotive dataset engineer chat hist | 3 SP | Danial | `e7ce84a` | **Done** |
| **AUT-185** | Sprint | feat(rag): implement from-scratch RAG pipeline with custom tokenizer, dense vector embedder, hybrid  | 5 SP | Abdullah | `aba6dff` | **Done** |
| **AUT-186** | Sprint | feat(rag): train causal transformer LM on automotive corpus and wire trained weights into RAG pipeli | 5 SP | Abdullah | `58b39bb` | **Done** |
| **AUT-187** | Sprint | feat(ui): elevate car owner experience with automotive diagnostic intelligence, Pakistani repair mar | 5 SP | Muhammad | `8613cf1` | **Done** |
| **AUT-188** | Sprint | feat(ui): redesign into modern narrative-driven automotive engineering web portal with spacious hero | 5 SP | Muhammad | `61bf981` | **Done** |
| **AUT-101-132** | Sprint | feat(jira): complete Agile Scrum workflow, team WBS, and Jira backlog export | 3 SP | Muhammad | `d3e47ed` | **Done** |
| **AUT-101-143** | Sprint | feat(jira): update Agile Scrum workflow for 5 team members (32 SP each, 160 SP total) | 3 SP | Muhammad | `8b3275c` | **Done** |
| **AUT-201** | Sprint | Docker Compose Stack: Apache Kafka (KRaft), MinIO S3 & Distributed Bus | 8 SP | Talha | `PLANNED` | **To Do** |
| **AUT-202** | Sprint | High-Velocity OBD-II CAN-Bus Live Telemetry Generator (10,000 msg/s) | 5 SP | Talha | `PLANNED` | **To Do** |
| **AUT-203** | Sprint | PyArrow Snappy Parquet Lakehouse Partitioning (make/model/year/region) | 5 SP | Talha | `PLANNED` | **To Do** |
| **AUT-204** | Sprint | Consistent Hash Ring with 160 Virtual Nodes per Physical Node | 8 SP | Abdullah | `PLANNED` | **To Do** |
| **AUT-205** | Sprint | SHA-256 CAS Deduplication Engine & Merkle Audit Integrity Log | 5 SP | Abdullah | `PLANNED` | **To Do** |
| **AUT-206** | Sprint | Argon2id Cryptographic Password & Authentication Security Upgrade | 3 SP | Abdullah | `PLANNED` | **To Do** |
| **AUT-207** | Sprint | PySpark Distributed DataFrame Moving Averages & Outlier Pipelines | 5 SP | Muhammad | `PLANNED` | **To Do** |
| **AUT-208** | Sprint | Spark Structured Streaming 1-Second Sliding Window Outlier Sink | 8 SP | Muhammad | `PLANNED` | **To Do** |
| **AUT-209** | Sprint | Embedded DuckDB In-Memory OLAP Direct-Query Engine for Parquet | 5 SP | Talha | `PLANNED` | **To Do** |
| **AUT-210** | Sprint | Isolation Forest & Rolling Z-Score Fleet Anomaly Detector | 5 SP | Ahmad | `PLANNED` | **To Do** |
| **AUT-211** | Sprint | Big Data Operational Telemetry REST APIs (/api/bigdata/metrics) | 5 SP | Talha | `PLANNED` | **To Do** |
| **AUT-212** | Sprint | React Big Data Operations Dashboard Component with Live Ticker | 8 SP | Muhammad | `PLANNED` | **To Do** |
| **AUT-213** | Sprint | 10 Empirical Big Data Benchmark Experiments & Latency Profiling | 8 SP | Danial | `PLANNED` | **To Do** |
| **AUT-214** | Sprint | Final Big Data System Architecture, DFD Level 0-2 & Defense Slides | 5 SP | Ahmad | `PLANNED` | **To Do** |

---

## 🛠️ 4. How to Import into Jira

1. Open Jira Software -> **Settings** -> **System** -> **External System Import** -> **CSV**.
2. Select `docs/jira_tickets_import.csv`.
3. Map fields (`Issue key`, `Summary`, `Epic Link`, `Story Points`, `Assignee`, `Sprint`, `Status`, `Commit Hash`).
4. Click **Begin Import**. All 138 tickets will populate your active sprint board and future product backlog!
