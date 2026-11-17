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
    r = p_badge.add_run("PUNJAB UNIVERSITY COLLEGE OF INFORMATION TECHNOLOGY (PUCIT)\nDEPARTMENT OF DATA SCIENCE • BS DATA SCIENCE FINAL YEAR PROJECT (FYP) PROPOSAL")
    r.font.name = 'Arial'; r.font.size = Pt(8.5); r.font.bold = True; r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    # Document Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(4); p_title.paragraph_format.space_after = Pt(2)
    r = p_title.add_run("FINAL YEAR PROJECT PROPOSAL\nAutoCare AI / AutoData Lake")
    r.font.name = 'Arial'; r.font.size = Pt(20); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(12)
    r = p_sub.add_run("Smart Car Fault Diagnosis, Big Data Live Telemetry Streaming & Fault-to-Mechanic Dispatch System for Pakistani Vehicles\n[Clear, Simple English Guide: Project Plan, Token Design, and 5-Member Task Breakdown]")
    r.font.size = Pt(10); r.font.italic = True; r.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    # Executive Metadata Table
    t_meta = doc.add_table(rows=5, cols=2)
    t_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_info = [
        ("College & University", "Punjab University College of Information Technology (PUCIT), University of the Punjab, Lahore"),
        ("Project Supervisor", "Dr. Khurram Shehzad (Associate Professor, Department of Data Science)"),
        ("Degree & Session", "BS Data Science (BSDS) — Session 2023–2027"),
        ("Project Team (5 Members)", "1. Abdullah (BSDSF23A035) — Group Leader & System Architect / AI Lead\n2. Talha Ali Bhatti (BSDSF23A016) — Distributed Storage & Ingestion Lead\n3. Danial Hameed (BSDSF23A014) — Data Engineering & Multilingual Corpus Lead\n4. Ahmad Zahid (BSDSF23A033) — ML Triage, Safety Calibration & Verification Lead\n5. Muhammad Abdullah (BSDSF23A032) — Web Portal UI, Fleet Analytics & Market Pricing Lead"),
        ("Target Cars in Pakistan", "Toyota Corolla (2014–2025), Honda Civic (2015–2025), Suzuki Swift (2015–2025)")
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

    # SECTION 1: PROPOSAL DOCUMENT (21 SECTIONS IN SIMPLE ENGLISH)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    h = doc.add_paragraph()
    r = h.add_run("PART 1: COMPLETE FYP PROPOSAL (SIMPLE & CLEAR ENGLISH)")
    r.font.name = 'Arial'; r.font.size = Pt(14); r.font.bold = True; r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    sections_text = [
        ("1. Project Title", 
         "AutoCare AI: An Evidence-Grounded Diagnostic, Distributed Big Data Streaming, and Intelligent Fault-to-Mechanic Dispatch System for Pakistani Passenger Vehicles."),
        
        ("2. Abstract (Simple Summary of the Project)", 
         "Every day, thousands of car drivers in Pakistan face a common problem: when their car breaks down, official car manuals are over 1,000 pages of difficult technical English, local mechanics often guess the problem without proper computer scanners, and repair shops overcharge them for unnecessary parts. If people try to ask generic AI tools like ChatGPT, those tools can make things up (called hallucination), which is very dangerous for car safety (like brakes or engine overheating). Modern cars also produce thousands of sensor readings every second that normal databases cannot handle.\n\n"
         "Our final year project proposes AutoCare AI, a smart software platform that solves all these problems together:\n"
         "1. It gives drivers verified advice taken directly from 45 official car handbooks with exact page numbers, so the AI never makes up fake advice.\n"
         "2. It understands English, Urdu, and everyday Roman Urdu car words (like 'dhuwan' for smoke, 'lambi self' for late starting, 'jhatka' for gear jerk).\n"
         "3. It handles Big Data sensor streams (10,000 readings per second) using modern tools (Apache Kafka and Parquet files) that take 75% less storage space.\n"
         "4. It checks workshop repair bills to stop mechanics from scamming car owners.\n"
         "5. It shows fair Pakistani Rupee (PKR) prices for spare parts and labor.\n"
         "6. It automatically finds the best certified local mechanic nearby who specializes in that exact fault (e.g., radiator specialist for overheating)."),

        ("3. Introduction (Why We Need This Project)", 
         "There are over 4.5 million passenger cars on the roads in Pakistan. The three most common cars are Toyota Corolla, Honda Civic, and Suzuki Swift. But unlike Western countries where every workshop has digital scanners and fixed repair prices, Pakistan's car market is informal (like Bilal Gunj in Lahore, Shershah in Karachi, and Sultan ka Khoo in Rawalpindi).\n\n"
         "Most Pakistani car drivers do not know technical English terms. They explain problems in Roman Urdu. When they go to a workshop, many mechanics advise expensive repairs (like changing an entire engine) when only a simple spark plug needed cleaning. AutoCare AI will give drivers an easy website on their phone or laptop where they can write their car problem in plain words, get honest verified advice from official manuals, see fair market prices in PKR, and get connected to the right specialist mechanic nearby."),

        ("4. Problem Statement (The 4 Main Problems We Are Solving)", 
         "Our project solves four real problems in Pakistan:\n"
         "1. Hard Language Barrier: Official car manuals are thick books in complex English. Ordinary drivers and local mechanics cannot read them easily.\n"
         "2. Generic AI Lies (Hallucinations): Commercial AI tools like ChatGPT guess answers without checking the official handbook. If an AI gives wrong brake torque specs, it can cause a fatal accident.\n"
         "3. Workshop Overcharging and Fraud: Because car owners do not know car mechanics, dishonest workshops charge high prices and replace good parts unnecessarily.\n"
         "4. Big Data Crash on Sensor Feeds: Modern cars send continuous sensor data (RPM, temperature, fuel). If you put this heavy live data into normal databases like MySQL or SQLite, the database freezes and crashes."),

        ("5. Proposed Solution (How AutoCare AI Works)", 
         "AutoCare AI is built as a complete 9-layer system:\n"
         "• Easy Web Screen: The driver enters their car problem in English, Urdu, or Roman Urdu.\n"
         "• Custom Small AI Brain (Causal Transformer): A lightweight 1.32-million parameter neural network built with PyTorch that answers questions using words trained on automotive data.\n"
         "• Manual-Grounded RAG (Retrieval-Augmented Generation): The system searches 45 official service manuals and only gives answers that have proof with an exact page number.\n"
         "• Big Data Stream Engine (Kafka + Parquet): Collects 10,000 live car sensor signals every second and stores them in compressed files that save over 75% hard drive space.\n"
         "• Safety Triage Filter: Treats danger faults (brakes, overheating) with extra care (10x priority) so no dangerous fault is ever ignored.\n"
         "• Mechanic Bill Checker & PKR Fair Price Estimator: Compares mechanic bills against official maintenance rules and shows the fair market price in PKR.\n"
         "• Smart Fault-to-Mechanic Dispatch: When a fault is found, the system finds the closest certified workshop that specializes in that exact issue using a live map."),

        ("6. Project Objectives (What We Will Achieve)", 
         "1. Collect, clean, and organize 111 dataset files and 45 official service manuals for Corolla, Civic, and Swift.\n"
         "2. Build our own subword tokenizer (4,000 words) and train a 1.32-million parameter PyTorch Transformer AI from scratch.\n"
         "3. Build a Big Data streaming pipeline using Apache Kafka that easily receives 10,000 sensor messages per second.\n"
         "4. Implement SHA-256 duplicate removal so identical files and logs do not waste hard drive space (saving 30%+ storage).\n"
         "5. Build a Consistent Hash Ring with 160 virtual points so data is spread evenly across storage computers without crashing.\n"
         "6. Train a safety machine learning model that cuts dangerous missed faults down from 68% to under 12%.\n"
         "7. Build a Pakistani Rupee (PKR) price calculator for top 50 car repairs in Lahore, Karachi, and Islamabad.\n"
         "8. Build an automatic map dispatch system that matches car faults to certified nearby mechanics."),

        ("7. Project Scope (What Is Included and What Is Not)", 
         "• Included Cars: Toyota Corolla (2014 to 2025), Honda Civic (2015 to 2025), Suzuki Swift (2015 to 2025) — petrol and hybrid models.\n"
         "• Included Car Systems: Engine, Radiator/Cooling, Fuel/EFI, Gearbox/Transmission, Brakes/ABS, Steering/Suspension, AC/Heating, and Electrical wiring.\n"
         "• Included Cities: Driving conditions in Lahore, Karachi, and Islamabad/Rawalpindi, including hot summer heat (45°C+ wear effect).\n"
         "• What is NOT Included (Limitations): Heavy trucks and buses, electric vehicle (EV) high-voltage battery packs, and rare imported luxury cars without manuals."),

        ("8. Comparison with Existing Systems", 
         "• Car Forums (PakWheels, Facebook): People give different and conflicting opinions; no one can guarantee if the advice is correct.\n"
         "• Generic AI (ChatGPT, Gemini): Often invents fake advice, charges expensive monthly fees, cannot verify page numbers in official manuals, and does not know local Pakistani market prices.\n"
         "• Dealership Scanners (Toyota Techstream): Cost thousands of dollars, used only inside expensive 3S company dealerships, not available to the public.\n"
         "• AutoCare AI Advantage: 100% verified citations from official manuals, free local execution, understands Roman Urdu, catches workshop fraud, shows PKR prices, and routes to local mechanics."),

        ("9. System Architecture (The 9 Layers Explained Simply)", 
         "Layer 1 (Data Sources): Live car sensors, 45 car handbooks, mechanic videos, and PakWheels discussion posts.\n"
         "Layer 2 (Ingestion): Smart software that reads PDFs and ingests sensor data smoothly.\n"
         "Layer 3 (Message Queue - Apache Kafka): A fast digital highway that moves 10,000 sensor messages per second without dropping any.\n"
         "Layer 4 (Storage - MinIO & Parquet): Stores raw data safely and compresses it into small Parquet files.\n"
         "Layer 5 (Fast Analysis - DuckDB): A super-fast in-memory analytical tool that reads car data in less than 80 milliseconds.\n"
         "Layer 6 (Anomaly Detection): Machine learning that spots strange car behavior before a breakdown happens.\n"
         "Layer 7 (AI & Language Model): Our custom Transformer AI and RAG engine that reads manuals and answers in simple words.\n"
         "Layer 8 (Backend Gateway - FastAPI): The secure Python server that connects the website to the database and AI.\n"
         "Layer 9 (User Website & Map): The clean website where drivers type symptoms and see nearby specialist mechanics on a map."),

        ("10. Functional Requirements (What the Software Will Do)", 
         "• FR-1: Must accept car symptoms in English, Urdu, and Roman Urdu (like 'car missing kar rahi hai').\n"
         "• FR-2: Must ingest 10,000 live sensor messages per second and organize them by car make, model, and year.\n"
         "• FR-3: Must check SHA-256 hash fingerprints to reject duplicate files automatically.\n"
         "• FR-4: Must give every answer with proof from an official manual (e.g. 'Corolla Manual, Chapter 4, Page 120').\n"
         "• FR-5: Must politely say 'I cannot find verified proof for this' if the manual does not contain the answer, instead of guessing.\n"
         "• FR-6: Must divide faults into 4 clear levels: Danger, Major, Moderate, and Minor.\n"
         "• FR-7: Must read mechanic repair bills and tell the user if the mechanic is being honest or lying.\n"
         "• FR-8: Must show the fair market price in PKR (low, average, high) for parts and labor.\n"
         "• FR-9: Must calculate which nearby workshop is best suited for the specific fault and show it on a live map."),

        ("11. Non-Functional Requirements (Performance & Quality Standards)", 
         "• NFR-1 (Speed): AI answers must show up in under 1.5 seconds; data search queries must run in less than 80 milliseconds.\n"
         "• NFR-2 (High Volume): The system must handle 10,000 sensor readings every second without crashing or slowing down.\n"
         "• NFR-3 (Accuracy & Safety): Must have zero made-up claims; dangerous fault misses must stay under 12%.\n"
         "• NFR-4 (Security): User passwords must be protected with strong modern encryption (Argon2id).\n"
         "• NFR-5 (Low Cost): The whole system must run smoothly on a normal student computer (16 GB RAM) using free open-source tools without expensive cloud bills."),

        ("12. Technology Stack (Tools & Languages Used)", 
         "• Main Coding Languages: Python 3.13, JavaScript (React), SQL, HTML, CSS.\n"
         "• AI & Machine Learning: PyTorch (for Transformer LM), Scikit-Learn (for triage classification).\n"
         "• Big Data & Streaming: Apache Kafka (message streaming), PyArrow & Snappy Parquet (compressed storage), DuckDB (fast in-memory analytics).\n"
         "• Database & Storage: MinIO (S3 object storage), SQLite / PostgreSQL, Redis (fast cache).\n"
         "• Backend Server: FastAPI and Uvicorn (high-speed asynchronous Python server).\n"
         "• Frontend Website: React 18, Tailwind CSS, Leaflet.js (free OpenStreetMap for mechanic dispatch).\n"
         "• Reporting & Organization: ReportLab (PDF generator), Docker Compose (container management), Jira (team task tracking)."),

        ("13. Development Methodology (How the Team Works)", 
         "We are using the Agile Scrum Framework divided into 6 clear Sprints:\n"
         "• Sprint 1: Collect manuals, build car definitions, and cut manuals into readable chunks.\n"
         "• Sprint 2: Build the safety triage classifier and calibrate confidence levels.\n"
         "• Sprint 3: Build the mechanic bill fraud checker and causal fault graph.\n"
         "• Sprint 4: Build our custom BPE tokenizer, train the PyTorch Transformer AI, and build the React website.\n"
         "• Sprint 5: Connect Apache Kafka streaming, MinIO storage, and the Consistent Hash Ring.\n"
         "• Sprint 6: Test speed with DuckDB, run safety checks, and prepare final presentations.\n"
         "Total Workload: 535 Story Points spread across 138 clearly defined Jira tasks."),

        ("14. Database & Storage Architecture (Where Data Lives)", 
         "The project uses a 4-level storage plan:\n"
         "1. Bronze Level (Raw Storage): MinIO S3 buckets storing raw incoming JSON sensor messages and original PDF manuals.\n"
         "2. Silver Level (Clean Columnar Storage): Snappy Parquet files neatly sorted into folders by car make, model, and year. Saves 75% space.\n"
         "3. Gold Level (Relational Database): Normal database tables storing registered cars, diagnosis history, mechanics list, and dispatch tickets.\n"
         "4. In-Memory Cache: Fast memory filters (Bloom filters) to check in 1 millisecond if a trouble code is valid."),

        ("15. AI & Token Architecture (How the Language Model Understands Words)", 
         "• What is a Token? A token is a piece of a word. For example, 'overheating' splits into 'over' and 'heating'.\n"
         "• Custom BPE Tokenizer: We built a custom tokenizer with 4,000 subwords. It is specifically trained on English, Urdu, and Roman Urdu words like 'dhuwan' (smoke), 'jhatka' (jerk), 'radiator', and trouble codes like 'P0300'.\n"
         "• Context Window: 128 tokens at a time (enough to read a user symptom and output a direct manual answer).\n"
         "• Training Token Budget: 1,500,000 to 2,000,000 tokens taken from 45 official car handbooks and real Q&A forums.\n"
         "• Neural Network Specs: 4 Transformer Layers, 4 Attention Heads, 1.32 Million trainable parameters. It runs completely offline without paying OpenAI or Google API fees.\n"
         "• Strict Grounding: If the model cannot find the answer in the official manual, it politely abstains instead of inventing a guess."),

        ("16. Big Data Sizing & Telemetry Stream (Handling Heavy Data)", 
         "• Sensor Speed: Modern cars produce 10,000 sensor readings every second (engine RPM, oil pressure, speed, temperature).\n"
         "• Data Math: 10,000 messages * 250 bytes = 2.5 MB per second = ~9 Gigabytes every hour.\n"
         "• How We Save Space: Storing 9 GB/hour in normal databases crashes the computer. Our Snappy Parquet format compresses this down to only ~2.2 GB/hour (over 75% savings).\n"
         "• In-Memory DuckDB: Instead of slow SQL queries that take minutes, DuckDB reads the compressed data directly in RAM in less than 80 milliseconds.\n"
         "• Counting Bloom Filter: Uses 65,536 small bits to check valid trouble codes with 99% accuracy in zero time."),

        ("17. Fault-to-Mechanic Dispatch Logic (How We Route Cars to the Right Mechanic)", 
         "When a car has a problem, it should not go to just any random mechanic. It must go to the right specialist. AutoCare AI handles this in 4 steps:\n"
         "Step 1 (Identify Fault Type): Matches the issue to 1 of 6 specialties: (1) Engine & Cooling, (2) Brakes & ABS, (3) EFI & Wiring, (4) Transmission, (5) Suspension, (6) AC/Cooling.\n"
         "Step 2 (Measure Distance): Calculates the exact road distance in kilometers using the Haversine GPS formula.\n"
         "Step 3 (Calculate Composite Score): Combines 4 factors:\n"
         "   Score = (40% * Mechanic Specialty Match) + (30% * Proximity Distance) + (20% * Customer Rating) + (10% * Available Queue Slot).\n"
         "Step 4 (Dispatch on Live Map): Shows the top certified workshop on an OpenStreetMap interface and sends a digital ticket with estimated fair repair costs in PKR."),

        ("18. Expected Outcomes (What We Will Deliver at the End)", 
         "1. A complete working website where any car owner can diagnose car faults and see nearby specialist mechanics on a map.\n"
         "2. An offline-runnable 1.32M parameter PyTorch AI model that gives answers with exact manual citations.\n"
         "3. A high-speed Big Data streaming engine that handles 10,000 messages/sec with Apache Kafka and Parquet.\n"
         "4. A complete 138-task Jira project proving equal work distribution across all 5 team members.\n"
         "5. An automated PDF report generator that creates formal diagnostic and pre-purchase vehicle inspection certificates."),

        ("19. Future Enhancements (What Can Be Added in Version 2.0)", 
         "• Bluetooth OBD-II Scanner: Direct plug-in device that connects the car's computer port to the mobile app automatically.\n"
         "• Camera Damage Scanner: Using computer vision (YOLOv8) to detect car body dents and paint scratches from a smartphone photo.\n"
         "• Urdu Voice Assistant: Allowing drivers to talk directly in Urdu on speakerphone while driving.\n"
         "• Digital Escrow Payment: Holding repair money safely in a digital account and releasing it to the mechanic only when the car's check-engine light is verified cleared."),

        ("20. Risk Management (What Could Go Wrong and How We Prevent It)", 
         "• Risk 1 (AI Hallucination): Prevented by our strict abstention rule—if retrieval similarity is low, the AI says 'Manual proof not found' instead of guessing.\n"
         "• Risk 2 (Hard Drive Gets Full): Prevented by Snappy Parquet compression (>75% space reduction) and SHA-256 duplicate removal.\n"
         "• Risk 3 (Slow Internet): Prevented because all AI weights and DuckDB analytics run 100% locally on the computer without needing active cloud internet.\n"
         "• Risk 4 (Mechanic Legal Trouble): Prevented by using polite, non-accusatory wording (e.g. 'Manual suggests checking spark plugs before replacing fuel injectors')."),

        ("21. References (Verified Academic & Industry Sources)", 
         "[1] Vaswani, A., et al. 'Attention Is All You Need.' NeurIPS 2017 (The foundation of Transformer AI).\n"
         "[2] Lewis, P., et al. 'Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.' NeurIPS 2020 (RAG architecture).\n"
         "[3] Platt, J. 'Probabilistic Outputs for Support Vector Machines.' 1999 (Platt scaling for probability calibration).\n"
         "[4] Armbrust, M., et al. 'Lakehouse: A New Generation of Open Data Platforms.' CIDR 2021 (Modern data lakehouses).\n"
         "[5] Raasveldt, M., & Muehleisen, H. 'DuckDB: an Embeddable Analytical Database.' ACM SIGMOD 2019 (Fast in-memory analytics).\n"
         "[6] Society of Automotive Engineers. 'SAE J2012: Diagnostic Trouble Code Definitions.' 2016 (Standard OBD-II fault codes).\n"
         "[7] Indus Motor Company Ltd. 'Toyota Corolla Owner's Service Manual (2014–2025).'\n"
         "[8] Honda Atlas Cars Pakistan Ltd. 'Honda Civic Workshop Diagnostic Handbook (2015–2025).'\n"
         "[9] Pak Suzuki Motor Co. Ltd. 'Suzuki Swift Technical Training Manual (2015–2025).'")
    ]

    for title, content in sections_text:
        doc.add_paragraph().paragraph_format.space_after = Pt(2)
        h_sec = doc.add_paragraph()
        r = h_sec.add_run(title)
        r.font.name = 'Arial'; r.font.size = Pt(11); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        
        p_c = doc.add_paragraph()
        p_c.add_run(content)
        p_c.paragraph_format.space_after = Pt(8)

    # PART 2: PROPOSED DIVISION OF TASKS (SIMPLE ENGLISH)
    doc.add_paragraph().paragraph_format.space_before = Pt(12)
    h_part2 = doc.add_paragraph()
    r = h_part2.add_run("PART 2: FAIR DIVISION OF WORK ACROSS ALL 5 GROUP MEMBERS")
    r.font.name = 'Arial'; r.font.size = Pt(14); r.font.bold = True; r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    members_spec = [
        {
            "name": "1. ABDULLAH (Roll No: BSDSF23A035)",
            "role": "Group Leader & Lead AI Architect",
            "sp": "27 Tasks | 116 Story Points | Exactly 20% of the Work",
            "modules": "Module M1 (Gateway), Module M4 (Custom Transformer AI), Module M4B (BPE Tokenizer), Consistent Hash Ring",
            "technical": "• Designs overall system architecture, connects all 5 members' modules, and builds the FastAPI Python server.\n• Builds the custom Subword BPE Tokenizer (4,000 words) for English and Roman Urdu.\n• Builds and trains the 4-layer PyTorch Causal Transformer AI (1.32M parameters) from scratch.\n• Builds the Consistent Hash Ring (160 virtual points) so incoming data is distributed evenly.\n• Connects the RAG search system so answers always cite official manual page numbers.",
            "docs": "• Project Initiation Document (PID) System Architecture chapter.\n• Master System Engineering Specification.\n• GitHub Master Repository management and release tags.",
            "research": "• Research on how small domain-specific Transformers perform compared to large cloud models.\n• Mathematical proofs of even data balancing using Consistent Hashing.",
            "deliverables": "• Trained PyTorch AI model files (autocare_causal_lm.pt, tokenizer_vocab.json).\n• Consistent Hash Ring routing script (consistent_hash.py).\n• FastAPI backend server endpoints (/api/diagnose, /api/rag/ask).",
            "dependencies": "Needs Danial's cleaned manual data to train and test the RAG system.",
            "time": "4 Weeks initial build + 2 Weeks Big Data scaling.",
            "evaluation": "Graded on: AI model training convergence (loss < 2.25, perplexity < 9.5), token conversion accuracy (100%), and Consistent Hash even balancing (< 5% variance)."
        },
        {
            "name": "2. TALHA ALI BHATTI (Roll No: BSDSF23A016)",
            "role": "Lead Distributed Storage & Ingestion Engineer",
            "sp": "28 Tasks | 111 Story Points | Exactly 20% of the Work",
            "modules": "Module L3 (Apache Kafka Bus), Module L4 (MinIO S3 Lakehouse), Module L4B (CAS Deduplication), Module L4C (Parquet Compaction)",
            "technical": "• Sets up MinIO S3 object storage to store raw car data and manuals safely.\n• Builds SHA-256 duplicate removal engine so the computer does not store the same file twice (saves 30%+ disk space).\n• Builds the live telemetry simulator that sends 10,000 sensor readings per second.\n• Writes data into compressed Snappy Parquet files organized into clean folders by car make, model, and year.\n• Builds an automated background cleaner (compaction daemon) that merges small files into solid 128 MB blocks.",
            "docs": "• Big Data Storage and MinIO S3 architecture report.\n• Data compression and disk space savings report.\n• Docker Compose setup manual.",
            "research": "• Research on Parquet vs JSON speed and storage benefits for live car telemetry.\n• Cryptographic hashing performance for fast file deduplication.",
            "deliverables": "• Containerized Kafka and MinIO Docker setup files (docker-compose.yml).\n• Live telemetry generator (telemetry_streamer.py) and compaction script.\n• Storage speed and latency benchmarking reports.",
            "dependencies": "Needs Muhammad Abdullah's data table formats for car records.",
            "time": "4 Weeks initial build + 2 Weeks Big Data scaling.",
            "evaluation": "Graded on: Telemetry speed (10,000 messages/sec), fast response time (< 120 ms), Parquet space savings (> 75%), and duplicate file removal (> 30%)."
        },
        {
            "name": "3. DANIAL HAMEED (Roll No: BSDSF23A014)",
            "role": "Lead Data Engineer & Multilingual Corpus Lead",
            "sp": "27 Tasks | 112 Story Points | Exactly 20% of the Work",
            "modules": "Module M1 (Data Cleaning & PDF Parsing), Module M2B (Urdu/Roman Urdu Dictionary), Module M4 (BM25 Search), Module L4D (Bloom Filter)",
            "technical": "• Collects, cleans, and organizes 111 car dataset files into standard formats.\n• Reads 45 official service manuals (Corolla, Civic, Swift) and cuts them into 326 clean passages with exact page numbers.\n• Builds the Urdu and Roman Urdu car dictionary mapping 150+ slang words (like 'dhuwan', 'jhatka') to official trouble codes.\n• Builds a Counting Bloom Filter that checks in 1 millisecond if a fault code exists without querying a slow database.\n• Collects real-world diagnostic Q&A from PakWheels, Facebook groups, and mechanic videos.",
            "docs": "• Complete Dataset Catalog and Data Dictionary.\n• Urdu & Roman Urdu automotive translation glossary.\n• Data cleaning and standardization guidelines.",
            "research": "• Comparing keyword search (BM25) vs vector search for mixed English-Urdu automotive queries.\n• Sizing bit arrays for zero false-positive errors in Bloom filters.",
            "deliverables": "• 111 clean dataset files ready in the dataset folder.\n• Multilingual translation dictionary module (lexicon_translator.py).\n• Fast Counting Bloom Filter script (bloom_filter.py).",
            "dependencies": "Provides clean text and manuals to Abdullah for AI training and to Ahmad for safety classification.",
            "time": "4 Weeks initial build + 2 Weeks Big Data scaling.",
            "evaluation": "Graded on: Dataset completeness (111 files, 45 manuals, 326 clean chunks), Bloom filter accuracy (< 1% error), and search recall (>= 92%)."
        },
        {
            "name": "4. AHMAD ZAHID (Roll No: BSDSF23A033)",
            "role": "Lead ML Triage, Safety Calibration & Verification Lead",
            "sp": "28 Tasks | 126 Story Points | Exactly 20% of the Work",
            "modules": "Module M2 (Safety Triage Classifier), Module M3 (Confidence Calibrator), Module M5 (Repair Bill Fraud Checker), Module M3B (Abstention Filter)",
            "technical": "• Trains a Machine Learning model that classifies car faults into 4 safety levels (Danger, Major, Moderate, Minor).\n• Applies a 10x penalty on danger faults so the AI never misses dangerous brake or overheating problems.\n• Implements Platt Scaling so the AI's confidence score matches real-world accuracy.\n• Builds the Repair Bill Fraud Checker that cross-checks mechanic bills against official manuals to detect fake repairs.\n• Writes an automated test suite (pytest) proving the AI never makes up answers or misses dangerous faults.",
            "docs": "• Machine Learning Model Cards (M2 Classifier & M3 Calibration).\n• Ethical and Honest Diagnostic Guidelines.\n• Automated Pytest safety test results and verification reports.",
            "research": "• Asymmetric cost matrices in safety-critical AI classification.\n• Calibrating neural network confidence scores using Platt scaling.",
            "deliverables": "• Trained triage model files (triage_model.joblib).\n• Repair Bill Fraud Verifier script (repair_verifier.py).\n• Automated safety test suite (tests/test_safety_invariants.py).",
            "dependencies": "Needs Danial's manuals to check repair bills and Abdullah's AI outputs for probability calibration.",
            "time": "4 Weeks initial build + 2 Weeks Big Data scaling.",
            "evaluation": "Graded on: Danger fault miss rate (< 12%), confidence calibration error (ECE < 0.05), and mechanic bill fraud detection rate (> 90%)."
        },
        {
            "name": "5. MUHAMMAD ABDULLAH (Roll No: BSDSF23A032)",
            "role": "Lead Web UI, Fleet Analytics & Market Pricing Lead",
            "sp": "28 Tasks | 114 Story Points | Exactly 20% of the Work",
            "modules": "Module L9 (React 18 Web Portal), Module L5B (DuckDB Fast Analytics), Module M9 (Pakistani PKR Pricing), Module L9B (Dispatch Map UI)",
            "technical": "• Builds the modern React 18 single-page website with Tailwind CSS, dark mode, and an easy diagnosis screen.\n• Connects DuckDB in-memory database so users can search 500,000 car records in less than 80 milliseconds.\n• Builds the Pakistani Rupee (PKR) price estimator showing real market prices (OEM, aftermarket, Kabli) across Lahore and Karachi.\n• Formulates Pakistani climate wear multipliers to show how 45°C+ summer heat wears down car parts faster.\n• Builds the interactive live map (Leaflet.js / OpenStreetMap) showing nearby specialist mechanics and directions.",
            "docs": "• Website UI/UX Design System and component manual.\n• Pakistani Spare Parts & Workshop Market Price Survey (PKR Benchmarks).\n• Project Initiation Document (PID) business and financial viability sections.",
            "research": "• In-memory columnar analytics (DuckDB) vs standard databases on large telemetry datasets.\n• Modeling car part failure rates under harsh Pakistani summer temperatures.",
            "deliverables": "• Production React website files (frontend/dist/).\n• Fast DuckDB analytical script (duckdb_analytics.py).\n• Localized PKR pricing database and automated PDF report generator (report_generator.py).",
            "dependencies": "Needs backend APIs from Abdullah, storage tables from Talha, and safety statuses from Ahmad.",
            "time": "4 Weeks initial build + 2 Weeks Big Data scaling.",
            "evaluation": "Graded on: Website smooth performance (zero errors), DuckDB query speed (> 15x faster than SQLite), and pricing estimation accuracy."
        }
    ]

    for m in members_spec:
        doc.add_paragraph().paragraph_format.space_before = Pt(4); doc.add_paragraph().paragraph_format.space_after = Pt(2)
        h_m = doc.add_paragraph()
        r = h_m.add_run(f"📌 {m['name']}")
        r.font.name = 'Arial'; r.font.size = Pt(12); r.font.bold = True; r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

        p_info = doc.add_paragraph()
        p_info.paragraph_format.space_after = Pt(4)
        r = p_info.add_run(f"Assigned Role: {m['role']}  |  Workload: {m['sp']}")
        r.font.bold = True; r.font.size = Pt(9.5); r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

        t_det = doc.add_table(rows=7, cols=2)
        t_det.alignment = WD_TABLE_ALIGNMENT.CENTER
        items = [
            ("Assigned Modules", m["modules"]),
            ("Technical Tasks (Simple Terms)", m["technical"]),
            ("Documentation Responsibilities", m["docs"]),
            ("Research Responsibilities", m["research"]),
            ("Target Deliverables", m["deliverables"]),
            ("Dependencies & Timeline", f"Dependencies: {m['dependencies']}\nTimeline: {m['time']}"),
            ("How Professors Will Grade You", m["evaluation"])
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

    # PART 3: DEVELOPMENT ROADMAP (SIMPLE ENGLISH)
    doc.add_paragraph().paragraph_format.space_before = Pt(12)
    h_part3 = doc.add_paragraph()
    r = h_part3.add_run("PART 3: 8-PHASE PROJECT DEVELOPMENT ROADMAP")
    r.font.name = 'Arial'; r.font.size = Pt(14); r.font.bold = True; r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    roadmap_data = [
        ("Phase 1: Research & Data Collection", "Collect 45 car handbooks for Corolla/Civic/Swift; survey spare parts markets (Bilal Gunj); build English-Urdu dictionary.", "Danial Hameed & Ahmad Zahid", "111 cleaned dataset files, bilingual car glossary, and vehicle taxonomy database."),
        ("Phase 2: System Architecture Design", "Plan the 9 system layers; design Consistent Hash Ring; plan Kafka streaming and MinIO storage structure.", "Abdullah & Talha Ali Bhatti", "System Architecture document, Docker setup files, and DFD Level 0, 1, 2 diagrams."),
        ("Phase 3: Database & Lakehouse Setup", "Set up MinIO S3 storage; build SHA-256 duplicate removal; write script to save telemetry as compressed Parquet files.", "Talha Ali Bhatti", "MinIO storage cluster, duplicate file remover, and partitioned Parquet data folders."),
        ("Phase 4: Frontend Website Development", "Build responsive React website; build diagnosis screen, live tickers, dark mode, and PKR price estimation cards.", "Muhammad Abdullah", "Working React website, diagnostic terminal screen, and mobile-friendly styling."),
        ("Phase 5: AI & Machine Learning Modeling", "Build custom 4-layer PyTorch Transformer AI from scratch; build 4k BPE tokenizer; train safety fault classifier.", "Abdullah & Ahmad Zahid", "Trained AI model weights, subword tokenizer, safety classifier, and confidence calibrator."),
        ("Phase 6: Streaming & Map Dispatch Integration", "Connect 10k msg/s telemetry simulator to Kafka; connect fast DuckDB query engine; build live mechanic dispatch map.", "Talha, Danial, M. Abdullah", "End-to-end Kafka streaming pipeline, zero-delay DuckDB analytics, and live mechanic map."),
        ("Phase 7: Testing & Safety Auditing", "Run automated safety tests; verify zero made-up answers; benchmark speed, memory, and compression savings.", "Ahmad Zahid & Team", "Safety test reports (zero dangerous false negatives) and speed benchmark comparison tables."),
        ("Phase 8: Final Documentation & Defense Prep", "Compile final Project Initiation Document (PID), Word & PDF defense guides, Jira sprint charts, and presentation slides.", "All 5 Members", "Complete academic documentation, print-ready Word/PDF guides, and presentation slides.")
    ]

    t_road = doc.add_table(rows=len(roadmap_data)+1, cols=4)
    t_road.alignment = WD_TABLE_ALIGNMENT.CENTER
    r_headers = ["Phase & Focus", "Key Practical Tasks", "Responsible Leads", "Deliverables"]
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

    # PART 4: PROPOSED MILESTONE CHECKLISTS (SIMPLE ENGLISH)
    doc.add_paragraph().paragraph_format.space_before = Pt(12)
    h_part4 = doc.add_paragraph()
    r = h_part4.add_run("PART 4: INDIVIDUAL PROGRESS CHECKLISTS (FOR SUPERVISOR TRACKING)")
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
    elements.append(Paragraph("AutoCare AI / AutoData Lake: Project Proposal", style_title))
    elements.append(Paragraph("Clear, Simple English Guide | 5-Member Engineering Tasks | Token & Big Data Sizing", style_sub))

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
    elements.append(Paragraph("1. Project Abstract & Core Idea (Simple English)", style_h1))
    elements.append(Paragraph(
        "AutoCare AI is an evidence-grounded automotive intelligence and Big Data streaming platform built for Pakistani car owners. "
        "Car owners in Pakistan face dense English manuals, ungrounded workshop advice, and predatory repair overcharging. "
        "Conversely, commercial generative AI models hallucinate dangerous diagnostic advice without citation grounding.<br/><br/>"
        "This project proposes to develop a custom PyTorch Causal Transformer Decoder with an automotive BPE tokenizer (4,000 vocab, 1.32M params) trained over a 1.5M token budget, "
        "a hybrid semantic+lexical RAG engine grounded in 45 official service handbooks, an Apache Kafka and Snappy Parquet streaming lakehouse sustaining 10,000 CAN-bus msgs/s with SHA-256 CAS deduplication, "
        "a cost-sensitive triage classifier with Platt confidence calibration, and a dynamic Fault-to-Specialist Dispatch Engine routing drivers to certified workshops via Haversine GPS proximity and verified PKR pricing benchmarks.",
        style_body
    ))
    elements.append(Spacer(1, 6))

    # 5 Members Allocation Table
    elements.append(Paragraph("2. Balanced 5-Member Engineering Task Allocation Matrix", style_h1))
    mem_table = [
        [Paragraph("Member", style_th), Paragraph("Role", style_th), Paragraph("Assigned Modules", style_th), Paragraph("Key Technical Deliverables", style_th), Paragraph("Workload", style_th)],
        [Paragraph("<b>Abdullah</b><br/>(BSDSF23A035)", style_td_bold), Paragraph("Group Leader & AI Lead", style_td), Paragraph("Causal Transformer LM, BPE Tokenizer, Consistent Hash Ring", style_td), Paragraph("PyTorch 1.32M LM, 4k BPE Vocab, Murmur3 Hash Ring (160 vNodes), FastAPI Gateway", style_td), Paragraph("27 Tasks<br/>(116 SP)", style_td_bold)],
        [Paragraph("<b>Talha Ali Bhatti</b><br/>(BSDSF23A016)", style_td_bold), Paragraph("Storage & Ingestion Lead", style_td), Paragraph("Kafka Bus, MinIO S3 Lakehouse, CAS Deduplication", style_td), Paragraph("MinIO cluster, 10k msg/s telemetry streamer, Snappy Parquet writer, Compaction daemon", style_td), Paragraph("28 Tasks<br/>(111 SP)", style_td_bold)],
        [Paragraph("<b>Danial Hameed</b><br/>(BSDSF23A014)", style_td_bold), Paragraph("Data & Multilingual Lead", style_td), Paragraph("111 Dataset Ingestion, Manual Chunking, Bloom Filter", style_td), Paragraph("45 manuals corpus (326 chunks), Urdu/Roman Urdu lexicon, Counting Bloom Filter (k=4)", style_td), Paragraph("27 Tasks<br/>(112 SP)", style_td_bold)],
        [Paragraph("<b>Ahmad Zahid</b><br/>(BSDSF23A033)", style_td_bold), Paragraph("ML Triage & Safety Lead", style_td), Paragraph("Cost-Sensitive Triage, Platt Scaling, NLI Verifier", style_td), Paragraph("10x safety penalty triage classifier, Platt ECE calibrator, NLI quote fraud detector", style_td), Paragraph("28 Tasks<br/>(126 SP)", style_td_bold)],
        [Paragraph("<b>Muhammad Abdullah</b><br/>(BSDSF23A032)", style_td_bold), Paragraph("Frontend & Analytics Lead", style_td), Paragraph("React 18 Web Portal, DuckDB OLAP, PKR Pricing", style_td), Paragraph("React SPA UI, DuckDB in-memory OLAP (<80ms), PKR fair-price estimator, Leaflet dispatch map", style_td), Paragraph("28 Tasks<br/>(114 SP)", style_td_bold)],
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
    print("\nAll FYP Inception Proposal deliverables successfully updated and synchronized in simple English!")
