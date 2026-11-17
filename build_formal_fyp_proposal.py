import os
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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether

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

def build_docx_proposal(output_path):
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.75)
        s.bottom_margin = Inches(0.75)
        s.left_margin = Inches(0.75)
        s.right_margin = Inches(0.75)

    normal = doc.styles['Normal']
    normal.font.name = 'Calibri'
    normal.font.size = Pt(10)
    normal.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
    normal.paragraph_format.line_spacing = 1.15
    normal.paragraph_format.space_after = Pt(4)

    # Header / College Title
    p_badge = doc.add_paragraph()
    r = p_badge.add_run("PUNJAB UNIVERSITY COLLEGE OF INFORMATION TECHNOLOGY (PUCIT)\nDEPARTMENT OF DATA SCIENCE • BS DATA SCIENCE FINAL YEAR PROJECT (FYP)")
    r.font.name = 'Arial'; r.font.size = Pt(8.5); r.font.bold = True; r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    # Document Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(4); p_title.paragraph_format.space_after = Pt(2)
    r = p_title.add_run("FINAL YEAR PROJECT PROPOSAL\nAutoCare AI / AutoData Lake")
    r.font.name = 'Arial'; r.font.size = Pt(20); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(12)
    r = p_sub.add_run("An Evidence-Grounded Diagnostic, Distributed Big Data Streaming & Fault-to-Mechanic Dispatch System for Pakistani Passenger Vehicles\n[Formal Inception Proposal: Objectives, Token Architecture, Methodology, and Team Division]")
    r.font.size = Pt(10.5); r.font.italic = True; r.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    # Executive Metadata Table
    t_meta = doc.add_table(rows=5, cols=2)
    t_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_info = [
        ("Academic Institution", "Punjab University College of Information Technology (PUCIT), University of the Punjab, Lahore"),
        ("Project Supervisor", "Dr. Khurram Shehzad (Associate Professor, Department of Data Science)"),
        ("Degree & Track", "Bachelor of Science in Data Science (BSDS) — Session 2023–2027"),
        ("Project Team (5 Members)", "1. Abdullah (BSDSF23A035) — Group Leader & System Architect / AI Lead\n2. Talha Ali Bhatti (BSDSF23A016) — Distributed Storage & Ingestion Lead\n3. Danial Hameed (BSDSF23A014) — Data Engineering & Multilingual Corpus Lead\n4. Ahmad Zahid (BSDSF23A033) — ML Triage, Safety Calibration & Verification Lead\n5. Muhammad Abdullah (BSDSF23A032) — Web Portal UI, Fleet Analytics & Market Pricing Lead"),
        ("Target Vehicle Fleet", "Toyota Corolla (2014–2025), Honda Civic (2015–2025), Suzuki Swift (2015–2025) across Pakistani Operating Conditions")
    ]
    for i, (k, v) in enumerate(meta_info):
        row = t_meta.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2); c1.width = Inches(4.8)
        c0.paragraphs[0].text = k; c0.paragraphs[0].runs[0].font.bold = True; c0.paragraphs[0].runs[0].font.size = Pt(9)
        c1.paragraphs[0].text = v; c1.paragraphs[0].runs[0].font.size = Pt(9)
        set_cell_background(c0, "F8FAFC"); set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, 40, 40, 60, 60); set_cell_margins(c1, 40, 40, 60, 60)
    set_table_borders(t_meta)

    # SECTION 1: PROPOSAL DOCUMENT (21 STANDARD SECTIONS)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    h = doc.add_paragraph()
    r = h.add_run("PART 1: FORMAL FYP PROJECT SPECIFICATION")
    r.font.name = 'Arial'; r.font.size = Pt(14); r.font.bold = True; r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    sections_text = [
        ("1. Project Title", 
         "AutoCare AI: An Evidence-Grounded Diagnostic, Distributed Big Data Streaming, and Intelligent Fault-to-Mechanic Dispatch System for Pakistani Passenger Vehicles."),
        
        ("2. Abstract", 
         "Vehicle owners in developing automotive markets like Pakistan face severe informational asymmetry: manufacturer handbooks and service manuals are written exclusively in dense, technical English; roadside workshops often diagnose problems heuristically without standard diagnostic scanners; and repair pricing is unstandardized, leaving consumers vulnerable to predatory parts replacement and inflated labor charges. Conversely, while generic Large Language Models (LLMs) can answer queries conversationally, they suffer from fatal hallucinations—inventing non-existent torque specs or incorrect Diagnostic Trouble Code (DTC) procedures without citation grounding. Furthermore, modern connected vehicles generate massive streams of OBD-II telemetry that single-node relational databases cannot ingest at scale.\n\n"
         "This project proposes AutoCare AI, a decentralized Big Data and AI decision-support platform designed to eliminate these failure modes. The proposed platform will integrate: (1) a custom PyTorch 4-layer Causal Transformer Decoder with a domain-trained subword Byte-Pair Encoding (BPE) tokenizer (4,000 vocab) trained over a 1.5M token corpus; (2) a hybrid semantic vector + BM25 lexical Retrieval-Augmented Generation (RAG) engine grounded in 45 verified OEM service manuals with strict page-level citation boundaries; (3) an Apache Kafka and Snappy-compressed Parquet Lakehouse architecture sustaining 10,000 CAN-bus telemetry events/second with SHA-256 Content-Addressable Storage (CAS) deduplication; (4) a cost-sensitive triage classifier with Platt confidence calibration and selective abstention to eliminate safety-critical false negatives; (5) a Natural Language Inference (NLI) workshop repair claim verifier; and (6) a dynamic Fault-to-Specialist Dispatch Engine that scores and routes vehicle owners to certified local workshops based on technical fault specialization, Haversine GPS proximity, and fair PKR pricing benchmarks."),

        ("3. Introduction", 
         "The automotive aftermarket in Pakistan comprises over 4.5 million registered passenger cars dominated by Japanese and local assemblers (Toyota Indus Motor Company, Honda Atlas, and Pak Suzuki). Unlike Western markets with established OBD-II inspection networks and digital consumer protection databases, Pakistani motorists rely on informal market ecosystems (e.g., Bilal Gunj and Montgomery Road in Lahore; Shershah and Plaza in Karachi; Sultan ka Khoo in Rawalpindi). Drivers communicate automotive failure modes using colloquial Urdu and Roman Urdu terminology (e.g., 'dhuwan' for exhaust smoke, 'lambi self' for delayed crank, 'jhatka' for transmission slip, 'missing' for spark misfire), creating a significant barrier for standard software and documentation.\n\n"
         "AutoCare AI will bridge the gap between car owners, manufacturer technical documentation, and specialized independent workshops. By uniting Big Data distributed stream processing (Kafka, Parquet, MinIO, DuckDB) with grounded NLP intelligence (BPE Tokenizer, Causal Transformer LM, Cost-Sensitive ML, and Haversine Specialist Routing), AutoCare AI aims to democratize verified automotive care, reduce vehicle operating expenses, and elevate road safety across Pakistan."),

        ("4. Problem Statement", 
         "The proposed project systematically tackles four major industry challenges:\n"
         "1. Linguistic & Technical Inaccessibility: Manufacturer service manuals exceed 1,000 pages of dense technical English, rendering them inaccessible to ordinary drivers and grassroots technicians who communicate in Urdu and Roman Urdu.\n"
         "2. LLM Hallucination & Lack of Verifiable Grounding: Commercial generative AI models frequently fabricate automotive advice, which in safety-critical subsystems (brakes, steering, fuel lines) can cause catastrophic mechanical failure or road accidents.\n"
         "3. Economic Exploitation & Information Asymmetry: Due to lack of transparent repair standards, workshops routinely upsell unnecessary component replacements (e.g., advising complete engine overhauls when a Rs. 1,500 spark plug cleaning suffices), exploiting car owners' technical unfamiliarity.\n"
         "4. Big Data Telemetry Ingestion Bottlenecks: Modern telemetry logs and high-frequency OBD-II sensor feeds (RPM, fuel trim, MAF, coolant temp at 100 Hz) crash traditional monolithic databases (SQLite/MySQL) due to lock contention, lack of partitioning, and uncompressed storage overhead."),

        ("5. Proposed Solution", 
         "The proposed AutoCare AI platform will deliver a modular nine-layer architecture:\n"
         "• Multilingual Diagnostic Terminal: Accepts motorists' symptom descriptions via text, audio transcripts, or OBD-II DTC codes in English, Urdu, and Roman Urdu.\n"
         "• Domain-Trained Causal Transformer LM: A 1,321,728-parameter PyTorch neural language model trained from scratch with an automotive BPE tokenizer, enforcing deterministic citation coordinates (e.g., 'Corolla Manual Sec. 14-2, p. 384').\n"
         "• High-Throughput Big Data Lakehouse: An Apache Kafka distributed event bus streaming 10,000 msgs/s into a MinIO S3 object lakehouse, partitioned hierarchically (make/model/year/region) with Snappy Parquet compression achieving > 75% byte reduction.\n"
         "• Cost-Sensitive Safety Triage & Platt Calibration: Prioritizes dangerous safety conditions with a 10x loss penalty matrix, while an abstention gate safely refuses ungrounded queries (similarity < 0.35) instead of hallucinating.\n"
         "• Workshop Quote Verifier & Fair PKR Estimator: Cross-checks mechanic estimates against official maintenance schedules using Natural Language Inference (NLI) and provides verified low-median-high replacement costs in PKR.\n"
         "• Fault-to-Specialist Dispatch Engine: Computes a multi-criteria composite score to route vehicles with specific faults (e.g., overheating, ABS lockup) to verified nearby specialist workshops via OpenStreetMap Overpass GPS queries."),

        ("6. Project Objectives", 
         "1. Curate, clean, and structure a domain data lake comprising 111 dataset files and 45 official service manuals across Toyota Corolla, Honda Civic, and Suzuki Swift (2014–2025).\n"
         "2. Train a domain-specific PyTorch Causal Transformer Decoder with a 4,000 subword BPE tokenizer on a 1.5M token budget, targeting training loss < 2.25 and perplexity < 9.5.\n"
         "3. Build a high-velocity streaming ingestion pipeline using Apache Kafka and PyArrow Parquet sustaining >= 10,000 OBD-II events/second with p95 ingestion latency < 120 ms.\n"
         "4. Implement a SHA-256 Content-Addressable Storage (CAS) deduplication engine yielding > 30% storage savings on redundant manuals and telemetry.\n"
         "5. Engineer a Consistent Hash Ring with 160 virtual nodes ensuring key distribution variance < 5% across distributed storage nodes.\n"
         "6. Train a cost-sensitive triage classifier reducing critical safety false negative rate from 68.2% down to < 12.0%.\n"
         "7. Implement an NLI repair verifier and localized PKR pricing engine covering top 50 common vehicle faults across Lahore, Karachi, and Islamabad.\n"
         "8. Deploy an automated Fault-to-Specialist Dispatch Engine matching diagnosed subsystems to certified workshops via Haversine proximity and rating criteria."),

        ("7. Project Scope", 
         "• Target Vehicle Fleet: Toyota Corolla (11th & 12th Gen, 2014–2025), Honda Civic (10th & 11th Gen, 2015–2025), Suzuki Swift (2nd & 3rd Gen, 2015–2025) covering 1.3L, 1.6L, 1.8L, and 1.2L petrol/hybrid variants.\n"
         "• In-Scope Subsystems: Internal Combustion Engine (ICE), Cooling & Radiators, Fuel & EFI, Automatic & CVT Transmission, Hydraulic Braking & ABS, Steering & Suspension, HVAC Air Conditioning, and Electrical Diagnostics.\n"
         "• Geographic Market Scope: Major Pakistani urban driving cycles (Lahore, Karachi, Rawalpindi/Islamabad) with climate wear multipliers accounting for 45°C+ summer ambient temperatures.\n"
         "• Project Limitations: Does not cover heavy commercial trucks, electric vehicle (EV) high-voltage inverters, or non-Pakistani domestic market (JDM) grey-import luxury models lacking official documentation."),

        ("8. Existing Systems vs. AutoCare AI", 
         "• Generic Web Search & Forum Threads (PakWheels, Facebook): Unstructured, anecdotal, contradictory advice; lacks vehicle chassis verification.\n"
         "• Commercial Generative AI (ChatGPT, Claude, Gemini): Prone to catastrophic hallucinations, lacks document-level bounding citations, costs heavy API fees, violates telemetry data privacy, and lacks localized PKR pricing.\n"
         "• OEM Dealership Diagnostic Scanners (Toyota Techstream, Honda HDS): Proprietary hardware costing thousands of dollars, restricted strictly to authorized 3S workshops, entirely inaccessible to individual car owners.\n"
         "• AutoCare AI Advantage: Evidence-grounded, zero hallucination, local language accessibility (English/Urdu/Roman Urdu), Big Data lakehouse streaming, automated fraud detection, and localized workshop dispatch."),

        ("9. Proposed System Architecture (9 Distributed Layers)", 
         "L1: Multi-Modal Data Sources (CAN-bus, 45 OEM manuals, mechanic videos, PakWheels, Facebook QA)\n"
         "L2: Data Ingestion Layer (Async streaming producers, PDF structure chunkers, circuit breakers)\n"
         "L3: Message Queue Layer (Apache Kafka cluster in KRaft mode, topic partitions)\n"
         "L4: Distributed Storage Layer (MinIO S3 Object Storage, Snappy Parquet Lakehouse, Redis bloom cache)\n"
         "L5: Distributed Processing Layer (PySpark batch transformations, Spark Structured Streaming, DuckDB OLAP)\n"
         "L6: Predictive Analytics Layer (Isolation Forest anomaly detector, Weibull component degradation)\n"
         "L7: AI & Reasoning Layer (From-scratch PyTorch Causal Transformer LM, hybrid BM25+Dense RAG, NLI verifier)\n"
         "L8: Security & API Gateway Layer (FastAPI asynchronous microservices, Argon2id auth, Consistent Hash router)\n"
         "L9: Presentation & Dispatch Layer (React 18 web portal, Leaflet OpenStreetMap live dispatch, ReportLab PDF reports)"),

        ("10. Functional Requirements", 
         "FR-1: System shall accept user fault queries in English, Urdu (Nastaliq), and Roman Urdu, mapping colloquial terms to SAE J2012 trouble codes.\n"
         "FR-2: System shall ingest CAN-bus OBD-II telemetry streams at >= 10,000 events/second and partition into Parquet files by make/model/year/region.\n"
         "FR-3: System shall compute SHA-256 digests for all incoming manuals and telemetry, rejecting duplicate payloads.\n"
         "FR-4: System shall answer diagnostic queries by retrieving top-k chunks and conditioning generation with verified OEM page citations.\n"
         "FR-5: System shall enforce selective abstention if retrieval confidence < 0.35, declining to answer unsupported queries.\n"
         "FR-6: System shall classify diagnosed faults into Critical, Major, Moderate, and Minor safety tiers using cost-sensitive weighting.\n"
         "FR-7: System shall cross-check workshop repair quotes against OEM manuals and generate an entailment verdict (Supported/Unsupported).\n"
         "FR-8: System shall provide fair market price estimates in PKR (low, median, high) for replacement parts and labor.\n"
         "FR-9: System shall automatically match diagnosed faults to certified nearby specialist mechanics using a composite multi-criteria scoring algorithm."),

        ("11. Non-Functional Requirements", 
         "NFR-1 (Latency): Diagnostic inference response time shall not exceed 1.5 seconds; DuckDB analytical queries shall execute in < 80 ms.\n"
         "NFR-2 (Throughput & Scalability): Ingestion message bus shall sustain 10,000 events/second without packet loss under nominal CPU load.\n"
         "NFR-3 (Reliability & Zero Hallucination): Critical safety false negative rate shall remain < 12.0%; zero uncited mechanical claims permitted.\n"
         "NFR-4 (Security): User credentials shall be salted and hashed using Argon2id; all REST API endpoints protected with JWT bearers.\n"
         "NFR-5 (Resource Efficiency): The entire distributed platform will run locally on standard hardware (16 GB RAM, 8 logical cores) utilizing Docker containers without mandatory cloud subscriptions."),

        ("12. Technology Stack", 
         "• Core Languages: Python 3.13, JavaScript (ES6+), SQL, HTML5/CSS3\n"
         "• AI & Machine Learning: PyTorch, Scikit-Learn, NetworkX, NumPy, SciPy\n"
         "• Big Data & Streaming: Apache Kafka (KRaft mode via Docker), PyArrow, Snappy Parquet, DuckDB In-Memory OLAP, PySpark\n"
         "• Distributed Storage & Caching: MinIO S3 Object Storage, Redis, PostgreSQL / SQLite\n"
         "• Backend Framework: FastAPI (Asynchronous ASGI), Uvicorn, Pydantic, Boto3\n"
         "• Frontend Framework: React 18, Vite, Tailwind CSS, Leaflet.js (OpenStreetMap), Lucide Icons\n"
         "• Cryptography & Algorithms: SHA-256 CAS, Argon2id, MurmurHash3 Consistent Hash Ring, Counting Bloom Filter\n"
         "• Reporting & CI/CD: ReportLab PDF Engine, Python-Docx, Docker Compose, GitHub Actions, Jira Software"),

        ("13. Development Methodology", 
         "The project will follow the Agile Scrum Framework structured into 6 focused Sprints:\n"
         "• Sprint 1: Architecture, Vehicle Taxonomy & Manual Chunking (102 SP)\n"
         "• Sprint 2: Cost-Sensitive Triage ML & Platt Confidence Calibration (95 SP)\n"
         "• Sprint 3: Causal Knowledge Graph & Workshop Quote Verifier (106 SP)\n"
         "• Sprint 4: Dataset Scaling, Causal LM from Scratch & Web UI (154 SP)\n"
         "• Sprint 5: Kafka Streaming Ingestion, MinIO Lakehouse & Consistent Hashing (34 SP)\n"
         "• Sprint 6: PySpark Streaming, DuckDB OLAP Analytics & Empirical Defense (44 SP)\n"
         "Total Velocity: 535 Story Points tracked across 138 Jira tickets mapped to 125+ GitHub commits."),

        ("14. Database & Storage Architecture", 
         "The platform will implement a hybrid multi-tier storage design:\n"
         "1. Bronze Tier (Raw Landing Zone): MinIO S3 bucket 'raw-telemetry/' receiving raw JSON CAN-bus messages and 'corpus-manuals/' storing original OEM PDFs with SHA-256 CAS indexing.\n"
         "2. Silver Tier (Partitioned Parquet Lakehouse): PyArrow columnar store partitioned as '/lakehouse/telemetry/make=X/model=Y/year=Z/region=R/' compressed with Snappy, enabling DuckDB partition pruning.\n"
         "3. Gold Tier (Relational & Analytical Store): PostgreSQL / SQLite storing entity tables (vehicle, diagnostic_records, mechanic_specialists, dispatch_tickets, audit_logs).\n"
         "4. In-Memory Cache: Redis bit-array storing Counting Bloom Filter states for O(1) set-membership verification."),

        ("15. AI & Machine Learning Pipeline (Token & Model Architecture)", 
         "• Subword BPE Tokenizer: Learns 4,000 subword merges across bilingual English/Roman Urdu automotive corpora, eliminating out-of-vocabulary errors on technical terms (e.g., 'dhuwan', 'jhatka', 'P0300').\n"
         "• Token Budget & Context Window: Maximum sequence length T_max = 128 tokens; training corpus size estimated at 1,500,000 to 2,000,000 tokens extracted from 45 OEM manuals, NHTSA reports, and PakWheels Q&A.\n"
         "• Dense Vector Embedder (D=128): PyTorch feed-forward network projecting token sequences into unit L2 metric space.\n"
         "• 4-Layer Causal Transformer Decoder: 1,321,728 parameters, 4 attention heads (d_model=128, d_ff=512), causal upper-triangular mask enforcing autoregressive token prediction.\n"
         "• Cost-Sensitive Triage Classifier: Multi-class classifier penalizing critical brake/overheating omissions at 10x penalty.\n"
         "• Platt Scaling: Sigmoid calibration minimizing Expected Calibration Error (ECE < 0.05) and Brier reliability score.\n"
         "• NLI Repair Entailment: Cross-encoder verifying semantic premise entailment between workshop repair claims and manual excerpts."),

        ("16. Big Data Lakehouse Pipeline & Capacity Sizing", 
         "• Ingestion Velocity: Multi-threaded async CAN-bus simulator emitting 10,000 msgs/s with realistic sensor jitter and fault injections.\n"
         "• Ingestion Sizing: 10,000 msgs/s * 250 bytes/msg = 2.5 MB/sec = ~9.0 GB/hour uncompressed telemetry stream.\n"
         "• Compression & Compaction: Snappy Parquet compression reduces disk footprint to ~2.2 GB/hour (> 75% byte reduction). Background compaction consolidates micro-batches (< 16 MB) into 128 MB analytical blocks.\n"
         "• Message Queue: Apache Kafka in KRaft mode partitioned by VIN hash tokens across distributed broker topics.\n"
         "• Counting Bloom Filter: Sized at m = 65,536 bits with k = 4 hash functions ensuring false positive probability P_fp <= 1.0%.\n"
         "• OLAP Analytics: Vectorized DuckDB SIMD queries scanning Parquet metadata footers in zero-copy RAM (< 80 ms latency)."),

        ("17. Fault-to-Specialist Dispatch Engine", 
         "When a mechanical failure is diagnosed (e.g. Engine Overheating P0217), the system activates automated dispatch:\n"
         "1. Maps active DTC and symptoms to 1 of 6 core technical specialties (Cooling/Engine, Brakes/Hydraulics, EFI/Electrical, Transmission, Suspension, HVAC).\n"
         "2. Computes Haversine great-circle distance from vehicle GPS coordinates to all registered workshops.\n"
         "3. Evaluates Composite Dispatch Score: S = (0.40 * Skill) + (0.30 * Distance) + (0.20 * Rating) + (0.10 * Queue).\n"
         "4. Queries OpenStreetMap Overpass API for real-time workshop metadata and dispatches digital repair ticket with fair PKR cost range."),

        ("18. Expected Outcomes & Deliverables", 
         "1. Fully functioning web application featuring an interactive diagnostic terminal, telemetry dashboard, and live workshop dispatch map.\n"
         "2. Offline-runnable 1.32M parameter PyTorch Causal Transformer LM generating verified manual citations.\n"
         "3. End-to-end Big Data streaming lakehouse capable of ingesting 10,000 events/second with Snappy Parquet compression.\n"
         "4. Comprehensive 138-ticket Jira Agile Scrum workflow demonstrating 100% team accountability across all 5 students.\n"
         "5. Automated PDF service report generator providing verifiable pre-purchase and service audit certificates."),

        ("19. Future Enhancements", 
         "• Direct OBD-II Bluetooth Low Energy (BLE) hardware adapter pairing for live real-time vehicle ECU telemetry streaming.\n"
         "• Computer Vision mobile damage scanner using fine-tuned YOLOv8 for automated vehicle exterior dent and scratch assessment.\n"
         "• Voice-first conversational audio interface supporting continuous bidirectional Urdu dialogue for hands-free roadside assistance.\n"
         "• Automated smart contract repair escrow releasing payments to workshops only after OBD-II DTC clear verification."),

        ("20. Risk Management & Mitigation", 
         "• Risk 1 (Model Hallucination): Mitigated by strict selective abstention gate refusing to answer when retrieval similarity < 0.35.\n"
         "• Risk 2 (Storage Exhaustion): Mitigated by Snappy Parquet compression (>75% reduction) and SHA-256 CAS deduplication.\n"
         "• Risk 3 (Network Latency): Mitigated by local offline deployment of transformer weights and embedded DuckDB OLAP engine.\n"
         "• Risk 4 (Legal / Slander Risk): Mitigated by non-accusatory phrasing ('Manufacturer documentation recommends inspecting X before replacing Y')."),

        ("21. References", 
         "[1] Vaswani, A., et al. 'Attention Is All You Need.' NeurIPS 2017.\n"
         "[2] Lewis, P., et al. 'Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.' NeurIPS 2020.\n"
         "[3] Platt, J. 'Probabilistic Outputs for Support Vector Machines.' 1999.\n"
         "[4] Karkkainen, J., et al. 'Fast BPE Tokenization with Compact Vocabularies.' IEEE 2021.\n"
         "[5] Armbrust, M., et al. 'Lakehouse: A New Generation of Open Data Platforms.' CIDR 2021.\n"
         "[6] Raasveldt, M., & Muehleisen, H. 'DuckDB: an Embeddable Analytical Database.' ACM SIGMOD 2019.\n"
         "[7] Society of Automotive Engineers. 'SAE J2012: Diagnostic Trouble Code Definitions.' SAE International 2016.\n"
         "[8] Indus Motor Company Ltd. 'Toyota Corolla Owner's Service Manual (2014–2025).'\n"
         "[9] Honda Atlas Cars Pakistan Ltd. 'Honda Civic Workshop Diagnostic Handbook (2015–2025).'\n"
         "[10] Pak Suzuki Motor Co. Ltd. 'Suzuki Swift Technical Training Manual (2015–2025).'")
    ]

    for title, content in sections_text:
        doc.add_paragraph().paragraph_format.space_after = Pt(2)
        h_sec = doc.add_paragraph()
        r = h_sec.add_run(title)
        r.font.name = 'Arial'; r.font.size = Pt(11.5); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        
        p_c = doc.add_paragraph()
        p_c.add_run(content)
        p_c.paragraph_format.space_after = Pt(8)

    # PART 2: PROPOSED DIVISION OF TASKS ACROSS ALL 5 MEMBERS
    doc.add_paragraph().paragraph_format.space_before = Pt(12)
    h_part2 = doc.add_paragraph()
    r = h_part2.add_run("PART 2: PROPOSED DIVISION OF TASKS ACROSS ALL 5 MEMBERS")
    r.font.name = 'Arial'; r.font.size = Pt(14); r.font.bold = True; r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    members_spec = [
        {
            "name": "1. ABDULLAH (Roll No: BSDSF23A035)",
            "role": "Group Leader & Lead System Architect / AI Lead",
            "sp": "27 Tickets | 116 Story Points | ~20% Workload",
            "modules": "Module M1 (Architecture Gateway), Module M4 (From-Scratch Causal Transformer LM), Module M4B (Subword BPE Tokenizer), Consistent Hash Ring Engine",
            "technical": "• Architect distributed system topology, FastAPI async orchestration server, and JWT auth.\n• Build automotive Subword BPE Tokenizer (4,000 vocab) and PyTorch L2-normalized dense embedder (D=128).\n• Develop 4-layer Causal Transformer Decoder (1.32M parameters) with triangular autoregressive self-attention mask.\n• Engineer Consistent Hash Ring with 160 virtual nodes per physical storage node using MurmurHash3.\n• Wire RAG retrieval into generation with document citation boundary enforcement.",
            "docs": "• Project Initiation Document (PID) System Architecture specifications.\n• System Architecture 5-Person Engineering Specification.\n• GitHub Master Repository administration and release tags.",
            "research": "• Research on causal autoregressive language modeling vs encoder-only models in domain diagnostic NLP.\n• Mathematical proofs of uniform distribution and K/N partition rebalancing in consistent hash topologies.",
            "deliverables": "• Trained PyTorch model weights (autocare_causal_lm.pt, autocare_embedder.pt, tokenizer_vocab.json).\n• Functional Consistent Hash Ring routing module (consistent_hash.py).\n• Asynchronous FastAPI gateway endpoints (/api/diagnose, /api/rag/ask, /api/health).",
            "dependencies": "Depends on Danial's cleaned manuals corpus and BM25 index for RAG context ingestion.",
            "time": "4 Weeks active development + 2 Weeks Big Data scaling.",
            "evaluation": "Evaluated on Transformer training convergence (Loss < 2.25, Perplexity < 9.5), token encode/decode fidelity (100%), and Consistent Hash token variance (< 5%)."
        },
        {
            "name": "2. TALHA ALI BHATTI (Roll No: BSDSF23A016)",
            "role": "Lead Distributed Storage & Ingestion Engineer",
            "sp": "28 Tickets | 111 Story Points | ~20% Workload",
            "modules": "Module L3 (Apache Kafka Streaming Bus), Module L4 (MinIO S3 Lakehouse), Module L4B (SHA-256 CAS Deduplication), Module L4C (Parquet Compaction)",
            "technical": "• Provision MinIO multi-tenant S3 distributed object storage cluster with isolated bucket retention.\n• Build SHA-256 Content-Addressable Storage (CAS) deduplication engine saving 70%+ disk footprint.\n• Develop 10,000 msg/s OBD-II CAN-bus telemetry streaming simulator with error injections.\n• Implement PyArrow Snappy Parquet Lakehouse with hierarchical partitioning (make/model/year/region).\n• Develop scheduled Parquet compaction job merging micro-batches into 128 MB analytical chunks.",
            "docs": "• Big Data Storage Architecture & S3 Bucket Lifecycle Policy documentation.\n• Telemetry ingestion throughput and compression ratio benchmarking reports.\n• Docker Compose multi-container deployment manuals.",
            "research": "• Comparative analysis of columnar storage formats (Parquet vs ORC vs JSON) on multi-dimensional telemetry.\n• Cryptographic hashing performance for content-addressable storage deduplication.",
            "deliverables": "• Containerized Kafka and MinIO cluster configuration files (docker-compose.yml).\n• Telemetry streaming generator (telemetry_streamer.py) and Parquet compaction daemon.\n• Storage IOPS and latency profiling suite (storage_benchmark.py).",
            "dependencies": "Depends on Muhammad Abdullah's schema definitions for CAN-bus entity records.",
            "time": "4 Weeks active development + 2 Weeks Big Data scaling.",
            "evaluation": "Evaluated on ingestion throughput (>= 10,000 msgs/s), p95 latency (< 120 ms), Parquet compression ratio (> 75%), and CAS byte savings (> 30%)."
        },
        {
            "name": "3. DANIAL HAMEED (Roll No: BSDSF23A014)",
            "role": "Lead Data Engineer & Multilingual Corpus Lead",
            "sp": "27 Tickets | 112 Story Points | ~20% Workload",
            "modules": "Module M1 (Corpus Ingestion & PDF Parser), Module M2B (Urdu/Roman Urdu Lexicon), Module M4 (Hybrid BM25 Retrieval), Module L4D (Counting Bloom Filter Gate)",
            "technical": "• Curate, deduplicate, and standardize 111 dataset files across 14 categories into unified schemas.\n• Extract and chunk 45 official service manuals (Corolla, Civic, Swift) with page-level coordinate metadata.\n• Build Urdu & Roman Urdu automotive terminology dictionary mapping 150+ colloquial terms to SAE DTCs.\n• Implement Counting Bloom Filter with k=4 hash functions for O(1) error code membership verification.\n• Develop multi-source data collectors (YouTube CC-BY transcripts, Facebook QA, NHTSA, StackExchange).",
            "docs": "• Comprehensive Dataset Card & Data Dictionary documentation.\n• Multilingual Roman Urdu translation protocol and glossary specifications.\n• Data Cleaning & Canonical Standardization protocol.",
            "research": "• Lexical vs dense semantic retrieval fusion (BM25 + Reciprocal Rank Fusion) on mixed-language automotive text.\n• Optimal bit-array sizing and false-positive bounds for counting Bloom filters.",
            "deliverables": "• 111 clean dataset files cataloged in dataset/ and deliverable folder.\n• Multilingual glossary translator module (lexicon_translator.py).\n• Memory-efficient Counting Bloom Filter with binary serialization (bloom_filter.py).",
            "dependencies": "Provides chunked text and lexical search indexes to Abdullah's RAG pipeline and Ahmad's triage model.",
            "time": "4 Weeks active development + 2 Weeks Big Data scaling.",
            "evaluation": "Evaluated on data corpus completeness (111 files, 45 manuals, 326 chunks), Bloom filter false positive rate (<= 1.0%), and retrieval Recall@5 (>= 92%)."
        },
        {
            "name": "4. AHMAD ZAHID (Roll No: BSDSF23A033)",
            "role": "Lead ML Triage, Safety Calibration & Verification Lead",
            "sp": "28 Tickets | 126 Story Points | ~20% Workload",
            "modules": "Module M2 (Cost-Sensitive Triage Classifier), Module M3 (Platt Scaling Calibrator), Module M5 (NLI Repair Quote Verifier), Module M3B (Selective Abstention Gate)",
            "technical": "• Train multi-class Cost-Sensitive Fault Classifier applying a 10x penalty on critical brake/cooling errors.\n• Implement Platt Scaling and Temperature Calibration to align neural log-odds with empirical accuracy.\n• Build NLI Repair Invoice Verifier cross-checking mechanic line-items against OEM manual citations.\n• Enforce Proposal Section 17 non-accusatory ethical guidelines preventing slander against workshops.\n• Build automated end-to-end safety pytest suite validating that zero ungrounded critical faults are emitted.",
            "docs": "• Machine Learning Model Cards (M2 Triage & M3 Calibration).\n• Section 17 Ethical Compliance & Non-Accusatory Diagnostic Verification Protocol.\n• Pytest automated test coverage and reliability evaluation reports.",
            "research": "• Asymmetric cost matrix optimization for safety-critical medical and automotive triage classification.\n• Expected Calibration Error (ECE) and Brier score minimization under class-imbalanced datasets.",
            "deliverables": "• Trained cost-sensitive triage model checkpoints and calibration artifacts (triage_model.joblib).\n• NLI Repair Verifier engine (repair_verifier.py) and selective abstention filter.\n• Comprehensive automated test suite (tests/test_safety_invariants.py).",
            "dependencies": "Depends on Danial's manuals corpus for NLI premise cross-checking and Abdullah's model logits for Platt scaling.",
            "time": "4 Weeks active development + 2 Weeks Big Data scaling.",
            "evaluation": "Evaluated on Critical False Negative Rate (< 12.0%), Expected Calibration Error (ECE < 0.05), and repair quote fraud detection rate (> 90%)."
        },
        {
            "name": "5. MUHAMMAD ABDULLAH (Roll No: BSDSF23A032)",
            "role": "Lead Frontend UI, Fleet Analytics & Regional Pricing Lead",
            "sp": "28 Tickets | 114 Story Points | ~20% Workload",
            "modules": "Module L9 (React 18 Web Portal), Module L5B (DuckDB In-Memory OLAP), Module M9 (Pakistani Fair Pricing Engine), Module L9B (Fault-to-Mechanic Dispatch UI)",
            "technical": "• Build modern React 18 single-page application with Tailwind CSS, diagnostic console, and live tickers.\n• Integrate DuckDB in-memory OLAP query engine scanning local/MinIO Parquet lakehouse files in < 80 ms.\n• Engineer Pakistani fair-price market estimator indexed in PKR (OEM, aftermarket, Kabli) across Lahore/Karachi.\n• Formulate Pakistani Climate Wear Multipliers accounting for 45°C+ summer heat on component lifespans.\n• Develop Leaflet OpenStreetMap live specialist workshop dispatch map with Haversine GPS routing.",
            "docs": "• UI/UX Design System Specification & Component Architecture manual.\n• Pakistani Spare Parts & Workshop Labor Economic Survey (PKR Benchmarks).\n• Project Initiation Document (PID) business and financial sustainability sections.",
            "research": "• Vectorized SIMD in-memory OLAP vs traditional row-oriented DBMS on multi-million row vehicle telemetry.\n• Empirical component failure acceleration modeling under extreme sub-continental climate profiles.",
            "deliverables": "• Production React frontend distribution (frontend/dist/ mounted at /app/).\n• DuckDB analytical query benchmark suite (duckdb_analytics.py).\n• Localized Pakistani PKR pricing database and automated ReportLab PDF audit generator (report_generator.py).",
            "dependencies": "Depends on backend APIs from Abdullah, storage tables from Talha, and triage status from Ahmad.",
            "time": "4 Weeks active development + 2 Weeks Big Data scaling.",
            "evaluation": "Evaluated on web portal responsiveness (zero runtime console errors), DuckDB query speedup (> 15x over SQLite), and pricing estimation accuracy."
        }
    ]

    for m in members_spec:
        doc.add_paragraph().paragraph_format.space_before = Pt(4); doc.add_paragraph().paragraph_format.space_after = Pt(2)
        h_m = doc.add_paragraph()
        r = h_m.add_run(f"📌 {m['name']}")
        r.font.name = 'Arial'; r.font.size = Pt(12); r.font.bold = True; r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

        p_info = doc.add_paragraph()
        p_info.paragraph_format.space_after = Pt(4)
        r = p_info.add_run(f"Proposed Role: {m['role']}  |  Workload Share: {m['sp']}")
        r.font.bold = True; r.font.size = Pt(9.5); r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

        t_det = doc.add_table(rows=7, cols=2)
        t_det.alignment = WD_TABLE_ALIGNMENT.CENTER
        items = [
            ("Assigned Modules", m["modules"]),
            ("Proposed Engineering Tasks", m["technical"]),
            ("Documentation Responsibilities", m["docs"]),
            ("Research Responsibilities", m["research"]),
            ("Target Deliverables", m["deliverables"]),
            ("Dependencies & Timeline", f"Dependencies: {m['dependencies']}\nEstimated Timeline: {m['time']}"),
            ("Academic Evaluation Criteria", m["evaluation"])
        ]
        for row_idx, (k, v) in enumerate(items):
            row = t_det.rows[row_idx]
            c0, c1 = row.cells[0], row.cells[1]
            c0.width = Inches(2.0); c1.width = Inches(5.0)
            c0.paragraphs[0].text = k; c0.paragraphs[0].runs[0].font.bold = True; c0.paragraphs[0].runs[0].font.size = Pt(8.5)
            c1.paragraphs[0].text = v; c1.paragraphs[0].runs[0].font.size = Pt(8.5)
            bg = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
            set_cell_background(c0, "F1F5F9"); set_cell_background(c1, bg)
            set_cell_margins(c0, 35, 35, 50, 50); set_cell_margins(c1, 35, 35, 50, 50)
        set_table_borders(t_det)

    # PART 3: DEVELOPMENT ROADMAP TABLE
    doc.add_paragraph().paragraph_format.space_before = Pt(12)
    h_part3 = doc.add_paragraph()
    r = h_part3.add_run("PART 3: 8-PHASE PROJECT DEVELOPMENT ROADMAP")
    r.font.name = 'Arial'; r.font.size = Pt(14); r.font.bold = True; r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    roadmap_data = [
        ("Phase 1: Domain Research & Scope Definition", "Survey Bilal Gunj/Shershah markets; collect 45 OEM manuals for Corolla/Civic/Swift; extract SAE J2012 trouble codes.", "Danial Hameed & Ahmad Zahid", "111-file dataset catalog, bilingual lexicon dictionary, and vehicle taxonomy database."),
        ("Phase 2: Distributed System Architecture Design", "Formulate 9-layer architecture; design Consistent Hash Ring (160 vNodes); establish Kafka streaming & MinIO lakehouse schema.", "Abdullah & Talha Ali Bhatti", "System Architecture 5-Person Engineering Spec, Docker Compose cluster, and DFD Level 0-2 diagrams."),
        ("Phase 3: Database & Lakehouse Infrastructure", "Provision MinIO S3 cluster; implement SHA-256 CAS deduplication; write PyArrow Snappy Parquet generator with partitioning.", "Talha Ali Bhatti", "MinIO S3 cluster, CAS deduplication engine, and partitioned Parquet lakehouse storage."),
        ("Phase 4: Frontend Web Portal & Visualization", "Build responsive React 18 single page application; implement diagnostic console, live tickers, dark mode, and PKR pricing cards.", "Muhammad Abdullah", "React 18 production bundle, diagnostic terminal interface, and responsive Tailwind styling."),
        ("Phase 5: AI / ML & RAG Implementation", "Train PyTorch 4-layer Causal Transformer LM (1.32M params) from scratch; build subword BPE tokenizer; train cost-sensitive triage classifier.", "Abdullah & Ahmad Zahid", "Trained transformer weights, BPE tokenizer, cost-sensitive triage model, and Platt calibration engine."),
        ("Phase 6: Big Data Streaming & Dispatch Integration", "Integrate 10,000 msg/s telemetry simulator to Kafka; connect DuckDB OLAP engine; deploy Fault-to-Specialist Dispatch Engine via OSM API.", "Talha, Danial, M. Abdullah", "End-to-end Kafka streaming pipeline, zero-copy DuckDB analytics, and OpenStreetMap mechanic dispatch map."),
        ("Phase 7: Testing, Safety Auditing & Benchmarking", "Run automated safety pytest suite; verify zero hallucination; conduct 10 empirical Big Data benchmarks (IOPS, latency, compression).", "Ahmad Zahid & Team", "Pytest verification reports (zero critical false negatives) and empirical benchmarking performance tables."),
        ("Phase 8: Academic Documentation & Final Defense", "Compile final Project Initiation Document (PID), Word & PDF defense guides, Jira sprint backlogs, and academic presentation slides.", "All 5 Members", "Complete academic documentation, print-ready PDF/Word guides, 138-ticket Jira backlog, and presentation slides.")
    ]

    t_road = doc.add_table(rows=len(roadmap_data)+1, cols=4)
    t_road.alignment = WD_TABLE_ALIGNMENT.CENTER
    r_headers = ["Phase & Focus", "Key Engineering Tasks", "Responsible Leads", "Deliverables"]
    for j, h_text in enumerate(r_headers):
        c = t_road.rows[0].cells[j]
        c.paragraphs[0].text = h_text; c.paragraphs[0].runs[0].font.bold = True; c.paragraphs[0].runs[0].font.size = Pt(8.5)
        set_cell_background(c, "0F172A"); c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_margins(c, 40, 40, 50, 50)

    for r_idx, (p_focus, p_tasks, p_leads, p_deliv) in enumerate(roadmap_data):
        row = t_road.rows[r_idx+1]
        for col_idx, val in enumerate([p_focus, p_tasks, p_leads, p_deliv]):
            c = row.cells[col_idx]
            c.paragraphs[0].text = val; c.paragraphs[0].runs[0].font.size = Pt(8)
            if col_idx == 0:
                c.paragraphs[0].runs[0].font.bold = True
            bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            set_cell_background(c, bg)
            set_cell_margins(c, 35, 35, 50, 50)
    set_table_borders(t_road)

    # PART 4: PROPOSED MILESTONE CHECKLISTS
    doc.add_paragraph().paragraph_format.space_before = Pt(12)
    h_part4 = doc.add_paragraph()
    r = h_part4.add_run("PART 4: PROPOSED TEAM MILESTONE CHECKLISTS")
    r.font.name = 'Arial'; r.font.size = Pt(14); r.font.bold = True; r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    checklists = [
        ("Abdullah (BSDSF23A035) — Lead Architect & AI Lead", [
            ("[PLANNED]", "Build custom Subword BPE Tokenizer with 4,000 automotive vocabulary covering English and Roman Urdu."),
            ("[PLANNED]", "Implement and train 4-layer PyTorch Causal Transformer Decoder (1.32M parameters) with AdamW optimizer."),
            ("[PLANNED]", "Design MurmurHash3 Consistent Hash Ring with 160 virtual nodes per storage node for balanced routing."),
            ("[PLANNED]", "Develop asynchronous FastAPI gateway with JWT token authentication and CORS middleware."),
            ("[PLANNED]", "Scale Consistent Hash Ring across multi-node cluster and implement SHA-256 Merkle audit trees.")
        ]),
        ("Talha Ali Bhatti (BSDSF23A016) — Storage & Ingestion Lead", [
            ("[PLANNED]", "Deploy MinIO S3 distributed object storage cluster with isolated bronze/silver/gold buckets."),
            ("[PLANNED]", "Implement SHA-256 Content-Addressable Storage (CAS) deduplication engine saving > 70% disk space."),
            ("[PLANNED]", "Build high-throughput OBD-II CAN-bus telemetry streaming generator producing 10,000 msgs/s."),
            ("[PLANNED]", "Implement Snappy Parquet Lakehouse writer partitioned by make/model/year/region."),
            ("[PLANNED]", "Deploy Apache Kafka cluster in KRaft mode and develop automated Parquet compaction daemon.")
        ]),
        ("Danial Hameed (BSDSF23A014) — Data Engineering & Corpus Lead", [
            ("[PLANNED]", "Curate and standardize 111 automotive dataset files across 14 categories into unified schemas."),
            ("[PLANNED]", "Extract and chunk 45 official service manuals (Corolla, Civic, Swift) with page-level bounding coordinates."),
            ("[PLANNED]", "Build Urdu and Roman Urdu automotive terminology dictionary mapping 150+ colloquial terms to SAE DTCs."),
            ("[PLANNED]", "Implement memory-efficient Counting Bloom Filter with k=4 hash functions for O(1) membership check."),
            ("[PLANNED]", "Integrate DuckDB in-memory OLAP direct-query engine and benchmark empirical query execution.")
        ]),
        ("Ahmad Zahid (BSDSF23A033) — ML Triage, Safety & Verification Lead", [
            ("[PLANNED]", "Train multi-class Cost-Sensitive Fault Classifier applying a 10x penalty on critical brake/cooling errors."),
            ("[PLANNED]", "Implement Platt Scaling and Temperature Calibration to align neural log-odds with empirical accuracy (ECE < 0.05)."),
            ("[PLANNED]", "Build NLI Repair Invoice Verifier cross-checking mechanic line-items against OEM manual citations."),
            ("[PLANNED]", "Enforce Proposal Section 17 non-accusatory ethical guidelines and selective abstention gate."),
            ("[PLANNED]", "Train multivariate Isolation Forest anomaly detector and assemble academic presentation materials.")
        ]),
        ("Muhammad Abdullah (BSDSF23A032) — Web Portal UI, Analytics & Pricing Lead", [
            ("[PLANNED]", "Develop modern React 18 single-page application with Tailwind CSS, dark mode, and diagnostic terminal."),
            ("[PLANNED]", "Build Pakistani fair-price market estimator database in PKR across Lahore and Karachi spare-parts hubs."),
            ("[PLANNED]", "Formulate Pakistani regional climate wear multipliers accounting for 45°C+ summer driving conditions."),
            ("[PLANNED]", "Deploy Leaflet OpenStreetMap live specialist workshop dispatch map with Haversine GPS routing."),
            ("[PLANNED]", "Implement PySpark distributed batch processing for fleet moving averages and automated PDF reports.")
        ])
    ]

    for c_title, c_items in checklists:
        doc.add_paragraph().paragraph_format.space_before = Pt(4); doc.add_paragraph().paragraph_format.space_after = Pt(2)
        h_ct = doc.add_paragraph()
        r = h_ct.add_run(f"📋 {c_title}")
        r.font.name = 'Arial'; r.font.size = Pt(11); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

        for tag, text in c_items:
            bp = doc.add_paragraph(style='List Bullet')
            bp.paragraph_format.space_after = Pt(2)
            r_tag = bp.add_run(f"{tag} ")
            r_tag.bold = True
            r_tag.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)
            bp.add_run(text).font.size = Pt(9)

    doc.save(output_path)
    print(f"[OK] Generated Word Proposal: {output_path}")

def build_pdf_proposal(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=45, rightMargin=45, topMargin=45, bottomMargin=45
    )
    styles = getSampleStyleSheet()

    style_badge = ParagraphStyle('Badge', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor('#0284C7'), spaceAfter=3)
    style_title = ParagraphStyle('MainTitle', fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#0F172A'), spaceAfter=4)
    style_sub = ParagraphStyle('SubTitle', fontName='Helvetica-Oblique', fontSize=9, leading=12, textColor=colors.HexColor('#64748B'), spaceAfter=10)
    style_h1 = ParagraphStyle('SectionH1', fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=colors.HexColor('#0284C7'), spaceBefore=8, spaceAfter=4)
    style_body = ParagraphStyle('Body', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#334155'), spaceAfter=4)
    style_th = ParagraphStyle('TableHeader', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.white)
    style_td = ParagraphStyle('TableCell', fontName='Helvetica', fontSize=7, leading=9, textColor=colors.HexColor('#1E293B'))
    style_td_bold = ParagraphStyle('TableCellBold', fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=colors.HexColor('#0F172A'))

    elements = []

    # Title
    elements.append(Paragraph("PUCIT BS DATA SCIENCE • FORMAL FINAL YEAR PROJECT PROPOSAL", style_badge))
    elements.append(Paragraph("AutoCare AI / AutoData Lake: Inception Proposal", style_title))
    elements.append(Paragraph("Evidence-Grounded Diagnostics, Big Data Streaming & Fault-to-Mechanic Dispatch System | 5-Member Task Breakdown", style_sub))

    # Meta Table
    meta_info = [
        [Paragraph("<b>Supervisor:</b>", style_td_bold), Paragraph("Dr. Khurram Shehzad (Associate Professor, Department of Data Science, PUCIT)", style_td)],
        [Paragraph("<b>Team Leads:</b>", style_td_bold), Paragraph("Abdullah (035), Talha Ali Bhatti (016), Danial Hameed (014), Ahmad Zahid (033), Muhammad Abdullah (032)", style_td)],
        [Paragraph("<b>Target Fleet:</b>", style_td_bold), Paragraph("Toyota Corolla, Honda Civic, Suzuki Swift (2014-2025) across Pakistani Operating Conditions", style_td)],
        [Paragraph("<b>Architecture:</b>", style_td_bold), Paragraph("9-Layer Big Data Streaming Lakehouse (Kafka/MinIO/Parquet) + Causal Transformer LM (4k BPE Vocab, 1.32M Params)", style_td)]
    ]
    t_meta = Table(meta_info, colWidths=[110, 412])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elements.append(t_meta)
    elements.append(Spacer(1, 8))

    # Abstract
    elements.append(Paragraph("1. Project Abstract & Objectives", style_h1))
    elements.append(Paragraph(
        "AutoCare AI is an evidence-grounded automotive intelligence and distributed Big Data streaming platform designed to eliminate information asymmetry in Pakistan's automotive aftermarket. "
        "Vehicle owners in Pakistan face dense English manuals, ungrounded workshop advice, and predatory repair overcharging. "
        "Conversely, commercial generative AI models hallucinate dangerous diagnostic advice without citation grounding.<br/><br/>"
        "This project proposes to develop a custom PyTorch Causal Transformer Decoder with an automotive BPE tokenizer (4,000 vocab, 1.32M params) trained over a 1.5M token budget, "
        "a hybrid semantic+lexical RAG engine grounded in 45 official service handbooks, an Apache Kafka and Snappy Parquet streaming lakehouse sustaining 10,000 CAN-bus msgs/s with SHA-256 CAS deduplication, "
        "a cost-sensitive triage classifier with Platt confidence calibration, and a dynamic Fault-to-Specialist Dispatch Engine routing drivers to certified workshops via Haversine GPS proximity and verified PKR pricing benchmarks.",
        style_body
    ))
    elements.append(Spacer(1, 6))

    # 5 Members Allocation Table
    elements.append(Paragraph("2. Proposed 5-Member Engineering Task Allocation Matrix", style_h1))
    mem_table = [
        [Paragraph("Member", style_th), Paragraph("Role", style_th), Paragraph("Assigned Modules", style_th), Paragraph("Target Technical Deliverables", style_th), Paragraph("Workload", style_th)],
        [Paragraph("<b>Abdullah</b><br/>(BSDSF23A035)", style_td_bold), Paragraph("Group Leader & AI Lead", style_td), Paragraph("Causal Transformer LM, BPE Tokenizer, Consistent Hash Ring", style_td), Paragraph("PyTorch 1.32M LM, 4k BPE Vocab, Murmur3 Hash Ring (160 vNodes), FastAPI Gateway", style_td), Paragraph("27 Tickets<br/>(116 SP)", style_td_bold)],
        [Paragraph("<b>Talha Ali Bhatti</b><br/>(BSDSF23A016)", style_td_bold), Paragraph("Storage & Ingestion Lead", style_td), Paragraph("Kafka Bus, MinIO S3 Lakehouse, CAS Deduplication", style_td), Paragraph("MinIO cluster, 10k msg/s telemetry streamer, Snappy Parquet writer, Compaction daemon", style_td), Paragraph("28 Tickets<br/>(111 SP)", style_td_bold)],
        [Paragraph("<b>Danial Hameed</b><br/>(BSDSF23A014)", style_td_bold), Paragraph("Data & Multilingual Lead", style_td), Paragraph("111 Dataset Ingestion, Manual Chunking, Bloom Filter", style_td), Paragraph("45 manuals corpus (326 chunks), Urdu/Roman Urdu lexicon, Counting Bloom Filter (k=4)", style_td), Paragraph("27 Tickets<br/>(112 SP)", style_td_bold)],
        [Paragraph("<b>Ahmad Zahid</b><br/>(BSDSF23A033)", style_td_bold), Paragraph("ML Triage & Safety Lead", style_td), Paragraph("Cost-Sensitive Triage, Platt Scaling, NLI Verifier", style_td), Paragraph("10x safety penalty triage classifier, Platt ECE calibrator, NLI quote fraud detector", style_td), Paragraph("28 Tickets<br/>(126 SP)", style_td_bold)],
        [Paragraph("<b>Muhammad Abdullah</b><br/>(BSDSF23A032)", style_td_bold), Paragraph("Frontend & Analytics Lead", style_td), Paragraph("React 18 Web Portal, DuckDB OLAP, PKR Pricing", style_td), Paragraph("React SPA UI, DuckDB in-memory OLAP (<80ms), PKR fair-price estimator, Leaflet dispatch map", style_td), Paragraph("28 Tickets<br/>(114 SP)", style_td_bold)],
    ]
    t_mem = Table(mem_table, colWidths=[85, 95, 115, 175, 52])
    t_mem.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elements.append(t_mem)
    elements.append(Spacer(1, 8))

    # Token & Big Data Specs
    elements.append(Paragraph("3. Token Architecture & Big Data Telemetry Specifications", style_h1))
    specs_data = [
        [Paragraph("<b>Subword BPE Vocab:</b>", style_td_bold), Paragraph("V = 4,000 subword tokens (trained on domain English, Urdu, and Roman Urdu automotive text)", style_td)],
        [Paragraph("<b>Context Window:</b>", style_td_bold), Paragraph("T_max = 128 tokens; autoregressive upper-triangular attention mask", style_td)],
        [Paragraph("<b>Training Token Budget:</b>", style_td_bold), Paragraph("1,500,000 to 2,000,000 tokens extracted from 45 OEM handbooks and community Q&A", style_td)],
        [Paragraph("<b>Neural Architecture:</b>", style_td_bold), Paragraph("4 Layers, 4 Heads, d_model = 128, d_ff = 512, Total Trainable Parameters = 1,321,728 (~1.32M)", style_td)],
        [Paragraph("<b>Telemetry Throughput:</b>", style_td_bold), Paragraph("10,000 CAN-bus messages/sec = 2.5 MB/sec = ~9.0 GB/hour uncompressed -> ~2.2 GB/hour with Snappy Parquet (>75% savings)", style_td)],
        [Paragraph("<b>Counting Bloom Filter:</b>", style_td_bold), Paragraph("m = 65,536 bits, k = 4 hash functions for O(1) membership check with false positive rate P_fp <= 1.0%", style_td)]
    ]
    t_specs = Table(specs_data, colWidths=[120, 402])
    t_specs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elements.append(t_specs)

    doc.build(elements)
    print(f"[OK] Generated PDF Proposal: {output_path}")

def sync_proposal_files(docx_path, pdf_path):
    targets = [
        r"C:\Users\ABDUL\Desktop",
        r"C:\Users\ABDUL\Desktop\AutoCare_AI_Complete_Deliverable_2026-11-10",
        r"C:\Users\ABDUL\.gemini\antigravity\brain\00a7aa5b-5d32-449b-a3f6-925ffecf15c5"
    ]
    for target in targets:
        if os.path.exists(target):
            shutil.copy2(docx_path, os.path.join(target, "AutoCare_AI_Complete_FYP_Proposal.docx"))
            shutil.copy2(pdf_path, os.path.join(target, "AutoCare_AI_Complete_FYP_Proposal.pdf"))
            print(f"[SYNC] -> {target}")

if __name__ == "__main__":
    base_dir = r"C:\Users\ABDUL\.gemini\antigravity\scratch\autocare-us2"
    docx_file = os.path.join(base_dir, "AutoCare_AI_Complete_FYP_Proposal.docx")
    pdf_file = os.path.join(base_dir, "AutoCare_AI_Complete_FYP_Proposal.pdf")

    build_docx_proposal(docx_file)
    build_pdf_proposal(pdf_file)
    sync_proposal_files(docx_file, pdf_file)
    print("\nAll FYP Inception Proposal deliverables successfully updated and synchronized!")
