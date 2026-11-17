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

def build_docx_architecture(output_path):
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
    r = p_title.add_run("SYSTEM ARCHITECTURE & SCHEMA WORKFLOW SPECIFICATION\nAutoCare AI / AutoData Lake")
    r.font.name = 'Arial'; r.font.size = Pt(18); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(12)
    r = p_sub.add_run("Complete End-to-End Visual Schema, Arrow Workflows, Database Tables & Pipeline Transitions\n[Written in Clear, Student-Friendly English for Technical Presentations & FYP Defense]")
    r.font.size = Pt(10); r.font.italic = True; r.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    # Metadata Table
    t_meta = doc.add_table(rows=5, cols=2)
    t_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_info = [
        ("Institution", "Punjab University College of Information Technology (PUCIT), Lahore"),
        ("Project Supervisor", "Dr. Khurram Shehzad (Associate Professor, Department of Data Science)"),
        ("Project Team (5 Members)", "1. Abdullah (035) — Lead AI & System Architect\n2. Talha Ali Bhatti (016) — Distributed Storage & Ingestion Lead\n3. Danial Hameed (014) — Data Engineering & Multilingual Lead\n4. Ahmad Zahid (033) — ML Triage & Safety Verification Lead\n5. Muhammad Abdullah (032) — Web Portal UI & Market Pricing Lead"),
        ("Workflow Structure", "End-to-End Pipeline with Complete Data Schemas (Bronze -> Silver -> Gold -> Analytics -> AI -> Dispatch)"),
        ("Target Vehicle Fleet", "Toyota Corolla (2014-2025), Honda Civic (2015-2025), Suzuki Swift (2015-2025)")
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

    # SECTION 1: MASTER ARROW WORKFLOW (VISUAL PIPELINE)
    doc.add_paragraph().paragraph_format.space_before = Pt(12)
    h = doc.add_paragraph()
    r = h.add_run("1. MASTER SYSTEM ARROW WORKFLOW (STEP-BY-STEP DATA FLOW)")
    r.font.name = 'Arial'; r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    workflow_boxes = [
        ("STAGE 1: DATA INGESTION & USER INPUT",
         "🚗 [Car CAN-bus Sensors] (10,000 msgs/s)  ──► [Async Telemetry Streamer] (Talha)\n"
         "📖 [45 Official OEM Manuals] (PDFs)       ──► [PDF Text Chunker & Parser] (Danial)\n"
         "👤 [Car Driver Input] (Roman Urdu Query)   ──► [React 18 Web Terminal] (M. Abdullah)"),
        
        ("STAGE 2: STREAMING MESSAGE QUEUE & ROUTING",
         "──► [Apache Kafka Cluster (KRaft)] ──► Partitioned by VIN Hash\n"
         "──► [Consistent Hash Ring] (160 Virtual Nodes) (Abdullah) ──► Distributes load evenly"),

        ("STAGE 3: 4-TIER STORAGE & COMPRESSION LAKEHOUSE",
         "──► [Bronze Tier: MinIO S3] ──► SHA-256 CAS Deduplication deletes duplicate files (>30% disk saved)\n"
         "──► [Silver Tier: Snappy Parquet] ──► Columnar storage sorted by make/model/year (>75% space saved)\n"
         "──► [Gold Tier: Relational DB] ──► SQLite/PostgreSQL (Users, Vehicles, Diagnosis, Dispatch)\n"
         "──► [RAM Cache: Bloom Filter] ──► 65,536-bit Counting Bloom Filter checks fault code in 1 ms"),

        ("STAGE 4: IN-MEMORY ANALYTICS & MACHINE LEARNING TRIAGE",
         "──► [DuckDB In-Memory OLAP] ──► Scans 500k rows in <80ms for fleet moving averages\n"
         "──► [Cost-Sensitive Safety Triage ML] ──► 10x safety penalty matrix for brakes & overheating (Ahmad)\n"
         "──► [Platt Scaling Calibration] ──► Aligns confidence probabilities to real-world accuracy (ECE < 0.05)"),

        ("STAGE 5: GROUNDED AI & RAG CITATION ENGINE",
         "──► [Subword BPE Tokenizer] (4,000 Vocab) ──► Converts English/Urdu/Roman Urdu slang (Abdullah)\n"
         "──► [Hybrid BM25 + Dense RAG] ──► Retrieves exact 3 manual passages from 45 handbooks (Danial)\n"
         "──► [PyTorch Causal Transformer LM] (1.32M Params) ──► Generates answer with exact page citations\n"
         "──► [Selective Abstention Gate] ──► If confidence < 0.35, politely refuses to guess"),

        ("STAGE 6: PRICING, FRAUD CHECK & MECHANIC DISPATCH",
         "──► [NLI Repair Bill Verifier] ──► Cross-checks mechanic estimates against OEM manuals (Ahmad)\n"
         "──► [Pakistani PKR Pricing Engine] ──► Low/Median/High parts cost in Lahore & Karachi (M. Abdullah)\n"
         "──► [Fault-to-Specialist Dispatch Engine] ──► Composite Score = (40% Skill) + (30% Dist) + (20% Rating) + (10% Queue)\n"
         "──► [OpenStreetMap Live Map] ──► Shows closest certified specialist workshop with directions to Driver")
    ]

    for stage_title, stage_content in workflow_boxes:
        p_st = doc.add_paragraph()
        p_st.paragraph_format.space_before = Pt(4); p_st.paragraph_format.space_after = Pt(2)
        r_title = p_st.add_run(f"📌 {stage_title}")
        r_title.font.bold = True; r_title.font.size = Pt(10); r_title.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)
        
        p_box = doc.add_paragraph()
        p_box.paragraph_format.space_after = Pt(6)
        r_code = p_box.add_run(stage_content)
        r_code.font.name = 'Consolas'; r_code.font.size = Pt(8.5); r_code.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    # SECTION 2: COMPLETE DATABASE SCHEMAS (ALL 4 TIERS)
    doc.add_paragraph().paragraph_format.space_before = Pt(12)
    h2 = doc.add_paragraph()
    r = h2.add_run("2. COMPLETE DATA SCHEMAS ACROSS ALL TIERS")
    r.font.name = 'Arial'; r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    # SCHEMA 1: BRONZE TIER (JSON STREAM)
    doc.add_paragraph().paragraph_format.space_before = Pt(4)
    h_s1 = doc.add_paragraph()
    r = h_s1.add_run("Schema A: Bronze Tier — Raw CAN-Bus Telemetry JSON (MinIO S3)")
    r.font.bold = True; r.font.size = Pt(10.5); r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    bronze_fields = [
        ("timestamp", "TIMESTAMP (ISO 8601)", "Exact sensor reading time (e.g. '2026-11-17T08:30:00.125Z')"),
        ("vin", "STRING (17 chars)", "Vehicle Identification Number (e.g. 'NZE140-5021984')"),
        ("make", "STRING", "Manufacturer (e.g. 'Toyota')"),
        ("model", "STRING", "Car model (e.g. 'Corolla Altis')"),
        ("year", "INTEGER", "Model year (e.g. 2021)"),
        ("engine_rpm", "INTEGER", "Engine revolutions per minute (e.g. 2450 RPM)"),
        ("speed_kmh", "FLOAT", "Vehicle road speed (e.g. 68.5 km/h)"),
        ("coolant_temp_c", "FLOAT", "Engine coolant temperature (e.g. 104.2 °C - Overheating!)"),
        ("fuel_trim_pct", "FLOAT", "Short-term fuel trim percentage (e.g. +14.2%)"),
        ("maf_rate_gs", "FLOAT", "Mass Air Flow sensor rate in grams/sec (e.g. 18.4 g/s)"),
        ("active_dtc_codes", "ARRAY<STRING>", "Active Diagnostic Trouble Codes (e.g. ['P0217', 'P0300'])"),
        ("sha256_cas_hash", "STRING (64 hex)", "Cryptographic payload fingerprint for duplicate rejection")
    ]
    t_b = doc.add_table(rows=len(bronze_fields)+1, cols=3)
    t_b.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h_text in enumerate(["Field Name", "Data Type", "Description & Practical Example"]):
        c = t_b.rows[0].cells[j]
        c.paragraphs[0].text = h_text; c.paragraphs[0].runs[0].font.bold = True; c.paragraphs[0].runs[0].font.size = Pt(8.5)
        set_cell_background(c, "0F172A"); c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_margins(c, 30, 30, 40, 40)
    for r_idx, (fn, dt, desc) in enumerate(bronze_fields):
        row = t_b.rows[r_idx+1]
        for col_idx, val in enumerate([fn, dt, desc]):
            c = row.cells[col_idx]
            c.paragraphs[0].text = val; c.paragraphs[0].runs[0].font.size = Pt(8)
            if col_idx == 0:
                c.paragraphs[0].runs[0].font.bold = True
            bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            set_cell_background(c, bg); set_cell_margins(c, 25, 25, 40, 40)
    set_table_borders(t_b)

    # SCHEMA 2: SILVER TIER (PARQUET PARTITIONED LAKEHOUSE)
    doc.add_paragraph().paragraph_format.space_before = Pt(8)
    h_s2 = doc.add_paragraph()
    r = h_s2.add_run("Schema B: Silver Tier — Snappy Parquet Columnar Lakehouse Schema")
    r.font.bold = True; r.font.size = Pt(10.5); r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    parquet_desc = doc.add_paragraph()
    parquet_desc.add_run(
        "Partition Path on Disk: /lakehouse/telemetry/make={make}/model={model}/year={year}/region={region}/\n"
        "Storage Engine: PyArrow with Snappy Compression (75%+ disk savings). Scanned directly by DuckDB in RAM."
    )
    parquet_desc.runs[0].font.size = Pt(8.5); parquet_desc.runs[0].font.italic = True

    # SCHEMA 3: GOLD TIER (RELATIONAL APPLICATION DATABASE)
    doc.add_paragraph().paragraph_format.space_before = Pt(8)
    h_s3 = doc.add_paragraph()
    r = h_s3.add_run("Schema C: Gold Tier — Relational Tables (SQLite / PostgreSQL)")
    r.font.bold = True; r.font.size = Pt(10.5); r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    relational_tables = [
        ("vehicles", "id (PK), vin (Unique), make, model, year, engine_type, odometer_km, owner_id (FK)", "Stores registered car profiles"),
        ("diagnostic_sessions", "id (PK), vehicle_id (FK), user_query, detected_dtc, safety_tier, ai_citation, confidence, created_at", "Stores driver diagnosis records & manual proof"),
        ("manual_chunks", "id (PK), manual_id (FK), vehicle_model, chapter, section, page_number, content_text, embedding_vector", "Stores 326 parsed manual excerpts with page citations"),
        ("mechanic_workshops", "id (PK), workshop_name, specialty_code, city, latitude, longitude, rating_stars, active_queue_slots", "Stores certified workshop profiles and GPS coordinates"),
        ("dispatch_tickets", "id (PK), session_id (FK), workshop_id (FK), fault_subsystem, estimated_pkr_low, estimated_pkr_high, dispatch_status", "Stores live referral tickets with fair PKR pricing")
    ]
    t_g = doc.add_table(rows=len(relational_tables)+1, cols=3)
    t_g.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h_text in enumerate(["Table Name", "Columns & Foreign Keys", "Business Purpose"]):
        c = t_g.rows[0].cells[j]
        c.paragraphs[0].text = h_text; c.paragraphs[0].runs[0].font.bold = True; c.paragraphs[0].runs[0].font.size = Pt(8.5)
        set_cell_background(c, "0F172A"); c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_margins(c, 30, 30, 40, 40)
    for r_idx, (tname, cols, purp) in enumerate(relational_tables):
        row = t_g.rows[r_idx+1]
        for col_idx, val in enumerate([tname, cols, purp]):
            c = row.cells[col_idx]
            c.paragraphs[0].text = val; c.paragraphs[0].runs[0].font.size = Pt(8)
            if col_idx == 0:
                c.paragraphs[0].runs[0].font.bold = True
            bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            set_cell_background(c, bg); set_cell_margins(c, 25, 25, 40, 40)
    set_table_borders(t_g)

    # SECTION 3: FAULT-TO-MECHANIC DISPATCH WORKFLOW WITH ARROWS
    doc.add_paragraph().paragraph_format.space_before = Pt(12)
    h3 = doc.add_paragraph()
    r = h3.add_run("3. FAULT-TO-MECHANIC DISPATCH ARROW WORKFLOW")
    r.font.name = 'Arial'; r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    dispatch_flow = doc.add_paragraph()
    dispatch_flow.add_run(
        "[Driver Reports Overheating Issue: P0217]\n"
        "             │\n"
        "             ▼  (Step 1: Match Specialty)\n"
        "[Target Specialty: 'Engine & Cooling Specialist']\n"
        "             │\n"
        "             ▼  (Step 2: Haversine GPS Distance Calculation)\n"
        "[Compute Road Distance to Nearby Workshops in Lahore / Karachi]\n"
        "             │\n"
        "             ▼  (Step 3: Multi-Criteria Composite Scoring Formula)\n"
        "Score = (40% * Skill Match) + (30% * Proximity) + (20% * Customer Rating) + (10% * Open Queue Slot)\n"
        "             │\n"
        "             ▼  (Step 4: Dispatch Decision)\n"
        "[Winning Workshop Selected] (e.g. 'Bilal Auto Cooling Care', 2.4 km away, Rating 4.8/5)\n"
        "             │\n"
        "             ▼  (Step 5: Deliverable to Driver)\n"
        "• Displays on OpenStreetMap (Leaflet.js) with turn-by-turn driving directions\n"
        "• Attaches Fair Market Price Range in PKR: Rs. 1,200 - 1,800 (Prevents mechanic fraud)\n"
        "• Creates digital dispatch ticket in Gold database"
    )
    dispatch_flow.runs[0].font.name = 'Consolas'; dispatch_flow.runs[0].font.size = Pt(8.5); dispatch_flow.runs[0].font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    doc.save(output_path)
    print(f"[OK] Generated Word Architecture with Complete Schemas: {output_path}")

def build_pdf_architecture(output_path):
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
    style_mono = ParagraphStyle('Mono', fontName='Courier', fontSize=7, leading=9, textColor=colors.HexColor('#0F172A'), spaceAfter=4)
    style_th = ParagraphStyle('TableHeader', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.white)
    style_td = ParagraphStyle('TableCell', fontName='Helvetica', fontSize=7, leading=9, textColor=colors.HexColor('#1E293B'))
    style_td_bold = ParagraphStyle('TableCellBold', fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=colors.HexColor('#0F172A'))

    elements = []

    # Title
    elements.append(Paragraph("PUCIT BS DATA SCIENCE • TECHNICAL ARCHITECTURE & SCHEMAS", style_badge))
    elements.append(Paragraph("AutoCare AI: Visual Architecture & Complete Workflow", style_title))
    elements.append(Paragraph("Arrow Workflow Pipelines, Database Tables, Storage Tiers & Fault Dispatch | Simple English", style_sub))

    # Meta Table
    meta_info = [
        [Paragraph("<b>Supervisor:</b>", style_td_bold), Paragraph("Dr. Khurram Shehzad (Associate Professor, Department of Data Science, PUCIT)", style_td)],
        [Paragraph("<b>Team Leads:</b>", style_td_bold), Paragraph("Abdullah (035), Talha Ali Bhatti (016), Danial Hameed (014), Ahmad Zahid (033), Muhammad Abdullah (032)", style_td)],
        [Paragraph("<b>Core Stack:</b>", style_td_bold), Paragraph("PyTorch 1.32M Transformer, Apache Kafka, MinIO S3, PyArrow Parquet, DuckDB, FastAPI, React 18", style_td)],
        [Paragraph("<b>Data Tiers:</b>", style_td_bold), Paragraph("Bronze (MinIO S3 Raw) -> Silver (Parquet Lakehouse) -> Gold (SQLite/Postgres) -> RAM Bloom Filter", style_td)]
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

    # Master Arrow Workflow
    elements.append(Paragraph("1. Complete System Workflow with Directional Arrows", style_h1))
    flow_text = (
        "<b>[1. Data Sources]</b> Car CAN-bus (10k msgs/s) + 45 Service Manuals + Driver Roman Urdu Query<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>│</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>▼</b><br/>"
        "<b>[2. Streaming & Ingestion]</b> Apache Kafka (KRaft mode) + Consistent Hash Ring (160 vNodes)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>│</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>▼</b><br/>"
        "<b>[3. Storage Tiers]</b> Bronze MinIO S3 (CAS Deduplication) ──► Silver Snappy Parquet (75% savings)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>│</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>▼</b><br/>"
        "<b>[4. Fast Analytics]</b> DuckDB In-Memory OLAP scans 500k rows in computer RAM in &lt; 80 ms<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>│</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>▼</b><br/>"
        "<b>[5. AI & Safety Triage]</b> 10x Safety Penalty Triage + 4k Subword BPE + 1.32M PyTorch Transformer<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>│</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>▼</b><br/>"
        "<b>[6. RAG Grounding]</b> Retrieves exact 3 manual passages with chapter/page citations (Zero Hallucination)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>│</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>▼</b><br/>"
        "<b>[7. Pricing & Dispatch]</b> Fair PKR Pricing + Haversine GPS routing ──► OpenStreetMap Specialist Dispatch"
    )
    elements.append(Paragraph(flow_text, style_body))
    elements.append(Spacer(1, 6))

    # Database Schemas Table
    elements.append(Paragraph("2. Multi-Tier Database Schemas (Data Structure)", style_h1))
    schema_table_data = [
        [Paragraph("Tier & Format", style_th), Paragraph("Key Columns & Data Fields", style_th), Paragraph("Purpose & Compression", style_th)],
        [Paragraph("<b>Bronze Tier</b><br/>(MinIO S3 JSON)", style_td_bold), Paragraph("timestamp, vin, make, model, year, engine_rpm, coolant_temp, speed, active_dtc, sha256_hash", style_td), Paragraph("Raw streaming data; SHA-256 CAS deduplication deletes duplicates (>30% disk saved)", style_td)],
        [Paragraph("<b>Silver Tier</b><br/>(Snappy Parquet)", style_td_bold), Paragraph("/telemetry/make=Toyota/model=Corolla/year=2021/region=Punjab/<br/>Snappy compressed columnar blocks", style_td), Paragraph("Analytics lakehouse; Snappy compression saves >75% storage; scanned by DuckDB in RAM", style_td)],
        [Paragraph("<b>Gold Tier</b><br/>(SQLite/Postgres)", style_td_bold), Paragraph("• vehicles (id, vin, make, model)<br/>• diagnostic_sessions (id, dtc, citation, urgency)<br/>• mechanic_workshops (id, specialty, lat, lon, rating)", style_td), Paragraph("Application database powering user accounts, diagnosis history, and workshop dispatch tickets", style_td)],
        [Paragraph("<b>Fast Cache Tier</b><br/>(RAM Bloom Filter)", style_td_bold), Paragraph("65,536-bit array with k=4 hash functions", style_td), Paragraph("Checks whether a Diagnostic Trouble Code is valid in 1 ms with &lt; 1% false positive rate", style_td)]
    ]
    t_schemas = Table(schema_table_data, colWidths=[95, 230, 197])
    t_schemas.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elements.append(t_schemas)
    elements.append(Spacer(1, 6))

    # Dispatch Formula
    elements.append(Paragraph("3. Fault-to-Specialist Dispatch Logic", style_h1))
    elements.append(Paragraph(
        "When an issue like Engine Overheating is diagnosed, the system computes:<br/>"
        "<b>Dispatch Score = (0.40 × Skill Match) + (0.30 × Haversine Distance) + (0.20 × Rating) + (0.10 × Open Queue)</b><br/>"
        "The winning workshop is sent directly to the driver's phone with turn-by-turn map directions and fair PKR parts prices.",
        style_body
    ))

    doc.build(elements)
    print(f"[OK] Generated PDF Architecture with Schemas: {output_path}")

def sync_architecture_files(docx_path, pdf_path):
    targets = [
        r"C:\Users\ABDUL\Desktop",
        r"C:\Users\ABDUL\Desktop\AutoCare_AI_Complete_Deliverable_2026-11-10",
        r"C:\Users\ABDUL\.gemini\antigravity\brain\00a7aa5b-5d32-449b-a3f6-925ffecf15c5"
    ]
    for target in targets:
        if os.path.exists(target):
            shutil.copy2(docx_path, os.path.join(target, "AutoCare_AI_System_Architecture.docx"))
            shutil.copy2(pdf_path, os.path.join(target, "AutoCare_AI_System_Architecture.pdf"))
            print(f"[SYNC] -> {target}")

if __name__ == "__main__":
    base_dir = r"C:\Users\ABDUL\.gemini\antigravity\scratch\autocare-us2"
    docx_file = os.path.join(base_dir, "AutoCare_AI_System_Architecture.docx")
    pdf_file = os.path.join(base_dir, "AutoCare_AI_System_Architecture.pdf")

    build_docx_architecture(docx_file)
    build_pdf_architecture(pdf_file)
    sync_architecture_files(docx_file, pdf_file)
    print("\nAll System Architecture Schema & Arrow Workflow deliverables successfully generated and synchronized!")
