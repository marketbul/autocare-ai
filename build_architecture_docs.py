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
    r = p_title.add_run("COMPLETE SYSTEM ARCHITECTURE DOCUMENT\nAutoCare AI / AutoData Lake")
    r.font.name = 'Arial'; r.font.size = Pt(18); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(12)
    r = p_sub.add_run("9-Layer Distributed Big Data Lakehouse, Causal Transformer AI & Fault-to-Mechanic Dispatch System\n[Written in Simple, Clear English for Student Presentations and Technical Defense]")
    r.font.size = Pt(10); r.font.italic = True; r.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    # Metadata Table
    t_meta = doc.add_table(rows=5, cols=2)
    t_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_info = [
        ("Institution", "Punjab University College of Information Technology (PUCIT), Lahore"),
        ("Project Supervisor", "Dr. Khurram Shehzad (Associate Professor, Department of Data Science)"),
        ("Project Team (5 Members)", "1. Abdullah (035) — Lead AI & System Architect\n2. Talha Ali Bhatti (016) — Distributed Storage & Ingestion Lead\n3. Danial Hameed (014) — Data Engineering & Multilingual Lead\n4. Ahmad Zahid (033) — ML Triage & Safety Verification Lead\n5. Muhammad Abdullah (032) — Web Portal UI & Market Pricing Lead"),
        ("Architecture Pattern", "Decentralized 9-Layer Big Data Streaming Lakehouse + Hybrid RAG + Causal Transformer LM"),
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

    # SECTION 1: ARCHITECTURE OVERVIEW (SIMPLE ENGLISH)
    doc.add_paragraph().paragraph_format.space_before = Pt(12)
    h = doc.add_paragraph()
    r = h.add_run("1. HIGH-LEVEL ARCHITECTURE OVERVIEW (PLAIN ENGLISH)")
    r.font.name = 'Arial'; r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    p_intro = doc.add_paragraph()
    p_intro.add_run(
        "AutoCare AI is built as a modular 9-layer software system. Each layer has one specific job, and they all work together "
        "like a team of specialists. When a driver has a car problem, they write it in simple words (English, Urdu, or Roman Urdu). "
        "The system checks 45 official car handbooks to find the exact verified solution, calculates fair repair costs in PKR, and shows "
        "the best certified local mechanic on a map. At the same time, it can receive 10,000 live car sensor signals per second without freezing."
    )

    # 9 LAYERS EXPLAINED
    layers_data = [
        ("Layer 1: Multi-Modal Data Sources", "Inputs to the System", "Live OBD-II car sensors (RPM, speed, temperature), 45 official service handbooks (Corolla, Civic, Swift), mechanic videos, and PakWheels discussion posts.", "Danial Hameed & Talha Ali Bhatti"),
        ("Layer 2: Data Ingestion & Parsers", "Getting Data In", "High-speed Python scripts that parse PDF manuals into clean text chunks and read live sensor streams without packet loss.", "Talha Ali Bhatti & Danial Hameed"),
        ("Layer 3: Message Queue (Apache Kafka)", "The Digital Highway", "A fast messaging system running in KRaft mode that streams 10,000 sensor messages per second and spreads them across topics.", "Talha Ali Bhatti"),
        ("Layer 4: Distributed Storage (MinIO & Parquet)", "Safe & Compressed Storage", "MinIO S3 stores raw files. PyArrow compresses sensor streams into Snappy Parquet files, saving over 75% hard drive space.", "Talha Ali Bhatti"),
        ("Layer 5: In-Memory Analytics (DuckDB)", "Super-Fast Search", "DuckDB runs directly in computer memory (RAM) to search through 500,000 car sensor records in under 80 milliseconds.", "Muhammad Abdullah & Talha"),
        ("Layer 6: Safety Triage & Anomaly Detection", "Catching Dangers", "Cost-sensitive classifier penalizes missed brake or overheating faults at 10x penalty. Spots strange sensor behavior before a breakdown.", "Ahmad Zahid"),
        ("Layer 7: AI & Reasoning (Causal Transformer)", "The Smart AI Brain", "Our custom 1.32M parameter PyTorch Transformer AI and RAG engine that reads manuals and provides answers with exact page numbers.", "Abdullah (Leader)"),
        ("Layer 8: Backend Server (FastAPI)", "The Traffic Controller", "Asynchronous Python server with JWT security that coordinates requests between the website, the database, and the AI.", "Abdullah (Leader)"),
        ("Layer 9: User Interface & Map Dispatch", "What the User Sees", "A responsive React 18 single-page website with an interactive diagnostic terminal, fair PKR price estimator, and live Leaflet mechanic map.", "Muhammad Abdullah")
    ]

    t_layers = doc.add_table(rows=len(layers_data)+1, cols=4)
    t_layers.alignment = WD_TABLE_ALIGNMENT.CENTER
    l_headers = ["Layer Name", "What It Does (Simple)", "Key Technologies & Components", "Responsible Lead"]
    for j, h_text in enumerate(l_headers):
        c = t_layers.rows[0].cells[j]
        c.paragraphs[0].text = h_text; c.paragraphs[0].runs[0].font.bold = True; c.paragraphs[0].runs[0].font.size = Pt(8.5)
        set_cell_background(c, "0F172A"); c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_margins(c, 40, 40, 50, 50)

    for r_idx, (p_name, p_role, p_tech, p_lead) in enumerate(layers_data):
        row = t_layers.rows[r_idx+1]
        for col_idx, val in enumerate([p_name, p_role, p_tech, p_lead]):
            c = row.cells[col_idx]
            c.paragraphs[0].text = val; c.paragraphs[0].runs[0].font.size = Pt(8)
            if col_idx == 0:
                c.paragraphs[0].runs[0].font.bold = True
            bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            set_cell_background(c, bg)
            set_cell_margins(c, 35, 35, 50, 50)
    set_table_borders(t_layers)

    # SECTION 2: END-TO-END DATA FLOW
    doc.add_paragraph().paragraph_format.space_before = Pt(12)
    h2 = doc.add_paragraph()
    r = h2.add_run("2. HOW DATA MOVES THROUGH THE SYSTEM (STEP-BY-STEP)")
    r.font.name = 'Arial'; r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    flow_steps = [
        ("Step 1: Driver Asks a Question", "The driver visits the website and writes their issue: 'Mera radiator pani boil kar raha hai aur car garam ho rahi hai' (My radiator is boiling water and the car is overheating)."),
        ("Step 2: Language & Word Tokenization", "Our custom Subword BPE Tokenizer breaks down the words into tokens from our 4,000-word dictionary covering English and Roman Urdu slang terms."),
        ("Step 3: Safety Triage Check", "Ahmad's triage classifier checks the urgency. Overheating is flagged as 'CRITICAL DANGER' with a 10x safety priority penalty, warning the driver to turn off the engine immediately."),
        ("Step 4: Manual Search (RAG Engine)", "Danial's search engine scans 45 official service manuals and retrieves the exact 3 passages explaining radiator boiling and cooling system pressure caps."),
        ("Step 5: Verified AI Generation", "Abdullah's 1.32M parameter PyTorch Transformer writes a clear explanation in simple words, citing: 'Corolla Manual, Section 14-2, Page 384'."),
        ("Step 6: Price & Fraud Verification", "Muhammad Abdullah's pricing engine shows the driver the fair market price in PKR: radiator cap (Rs. 1,200 - 1,800), coolant replacement (Rs. 2,500 - 3,500). If a mechanic asks for Rs. 50,000 for an engine overhaul, it flags it as suspicious."),
        ("Step 7: Smart Mechanic Dispatch", "The system calculates the Haversine distance and routes the car to the closest certified 'Engine & Cooling Specialist' workshop on a live map.")
    ]

    for title, desc in flow_steps:
        p_st = doc.add_paragraph()
        r_st = p_st.add_run(f"👉 {title}: ")
        r_st.font.bold = True; r_st.font.size = Pt(9.5); r_st.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        p_st.add_run(desc).font.size = Pt(9)
        p_st.paragraph_format.space_after = Pt(3)

    # SECTION 3: STORAGE TIERS & BIG DATA ARCHITECTURE
    doc.add_paragraph().paragraph_format.space_before = Pt(12)
    h3 = doc.add_paragraph()
    r = h3.add_run("3. DATABASE & STORAGE ARCHITECTURE (4-TIER DESIGN)")
    r.font.name = 'Arial'; r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    storage_tiers = [
        ("Bronze Tier (Raw Landing)", "MinIO S3 Buckets", "Stores raw incoming JSON telemetry logs and raw PDF files exactly as they arrive. Uses SHA-256 Content-Addressable Storage (CAS) to delete duplicate files automatically (saves 30%+ storage)."),
        ("Silver Tier (Clean Lakehouse)", "Snappy Parquet Files", "Stores clean, structured telemetry files organized into neat folders: /telemetry/make=Toyota/model=Corolla/year=2020/. Uses Snappy columnar compression to save over 75% hard drive space."),
        ("Gold Tier (Relational DB)", "SQLite / PostgreSQL", "Stores business entities: registered users, car profiles, diagnostic session history, verified workshops list, and dispatch tickets."),
        ("Fast Cache Tier", "In-Memory Bloom Filter & Redis", "Uses a 65,536-bit Counting Bloom Filter with 4 hash functions to verify whether an OBD-II diagnostic code is valid in 1 millisecond.")
    ]

    t_store = doc.add_table(rows=len(storage_tiers)+1, cols=3)
    t_store.alignment = WD_TABLE_ALIGNMENT.CENTER
    s_headers = ["Storage Tier", "Technology Used", "How It Works & Benefit"]
    for j, h_text in enumerate(s_headers):
        c = t_store.rows[0].cells[j]
        c.paragraphs[0].text = h_text; c.paragraphs[0].runs[0].font.bold = True; c.paragraphs[0].runs[0].font.size = Pt(8.5)
        set_cell_background(c, "0F172A"); c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_margins(c, 40, 40, 50, 50)

    for r_idx, (t_name, t_tech, t_desc) in enumerate(storage_tiers):
        row = t_store.rows[r_idx+1]
        for col_idx, val in enumerate([t_name, t_tech, t_desc]):
            c = row.cells[col_idx]
            c.paragraphs[0].text = val; c.paragraphs[0].runs[0].font.size = Pt(8)
            if col_idx == 0:
                c.paragraphs[0].runs[0].font.bold = True
            bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            set_cell_background(c, bg)
            set_cell_margins(c, 35, 35, 50, 50)
    set_table_borders(t_store)

    # SECTION 4: FAULT-TO-MECHANIC DISPATCH ARCHITECTURE
    doc.add_paragraph().paragraph_format.space_before = Pt(12)
    h4 = doc.add_paragraph()
    r = h4.add_run("4. FAULT-TO-MECHANIC DISPATCH ARCHITECTURE")
    r.font.name = 'Arial'; r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    p_disp = doc.add_paragraph()
    p_disp.add_run(
        "A key innovation in AutoCare AI is the Fault-to-Specialist Dispatch Engine. Instead of showing random general mechanics, "
        "the engine matches the diagnosed problem to verified specialist workshops using a 4-part mathematical formula:\n\n"
        "• Specialty Match (40% Weight): Does this workshop specialize in this exact subsystem? (e.g., Radiator & Cooling vs Brake Hydraulics).\n"
        "• Proximity Distance (30% Weight): How close is the workshop? Calculated using the Haversine GPS formula based on vehicle location.\n"
        "• Customer Rating (20% Weight): Verified past repair rating from 1 to 5 stars.\n"
        "• Queue Availability (10% Weight): Does the workshop have an open bay right now to take the car immediately?\n\n"
        "The winning workshop is displayed on an interactive Leaflet OpenStreetMap view with turn-by-turn directions and estimated fair repair costs in PKR."
    )

    # SECTION 5: SECURITY, BACKEND & DOCKER DEPLOYMENT
    doc.add_paragraph().paragraph_format.space_before = Pt(12)
    h5 = doc.add_paragraph()
    r = h5.add_run("5. SECURITY, BACKEND & DEPLOYMENT ARCHITECTURE")
    r.font.name = 'Arial'; r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    p_sec = doc.add_paragraph()
    p_sec.add_run(
        "• Password Security: Passwords are encrypted using Argon2id, the most secure hashing algorithm that protects against brute-force attacks.\n"
        "• API Protection: Every API call is guarded by JSON Web Tokens (JWT) with user session expiration.\n"
        "• Consistent Hash Ring: The backend uses a 160-virtual-node Consistent Hash Ring (MurmurHash3) so that adding or removing storage nodes does not reshuffle all data.\n"
        "• 100% Free Local Execution (Docker): The entire system runs locally via Docker Compose on standard university laptops (16 GB RAM) without requiring expensive AWS or OpenAI cloud subscriptions."
    )

    doc.save(output_path)
    print(f"[OK] Generated Word Architecture: {output_path}")

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
    style_th = ParagraphStyle('TableHeader', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.white)
    style_td = ParagraphStyle('TableCell', fontName='Helvetica', fontSize=7, leading=9, textColor=colors.HexColor('#1E293B'))
    style_td_bold = ParagraphStyle('TableCellBold', fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=colors.HexColor('#0F172A'))

    elements = []

    # Title
    elements.append(Paragraph("PUCIT BS DATA SCIENCE • TECHNICAL ARCHITECTURE DOCUMENT", style_badge))
    elements.append(Paragraph("AutoCare AI: Complete System Architecture Specification", style_title))
    elements.append(Paragraph("9-Layer Big Data Streaming Lakehouse, Causal Transformer AI & Fault-to-Mechanic Dispatch | Simple English", style_sub))

    # Meta Table
    meta_info = [
        [Paragraph("<b>Supervisor:</b>", style_td_bold), Paragraph("Dr. Khurram Shehzad (Associate Professor, Department of Data Science, PUCIT)", style_td)],
        [Paragraph("<b>Team Leads:</b>", style_td_bold), Paragraph("Abdullah (035), Talha Ali Bhatti (016), Danial Hameed (014), Ahmad Zahid (033), Muhammad Abdullah (032)", style_td)],
        [Paragraph("<b>Core Stack:</b>", style_td_bold), Paragraph("PyTorch 1.32M Transformer, Apache Kafka, MinIO S3, PyArrow Parquet, DuckDB, FastAPI, React 18", style_td)],
        [Paragraph("<b>Architecture Pattern:</b>", style_td_bold), Paragraph("9-Layer Distributed Big Data Streaming Lakehouse + Consistent Hash Ring + Leaflet Dispatch Map", style_td)]
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

    # 9 Layers Table
    elements.append(Paragraph("1. The 9-Layer Distributed System Architecture", style_h1))
    layers_table_data = [
        [Paragraph("Layer", style_th), Paragraph("Role & Plain English Meaning", style_th), Paragraph("Key Tools Used", style_th), Paragraph("Lead", style_th)],
        [Paragraph("<b>L1: Data Sources</b>", style_td_bold), Paragraph("Raw car sensors (10k msgs/s), 45 official service manuals, PakWheels discussions", style_td), Paragraph("CAN-bus, PDF manuals, Q&A", style_td), Paragraph("Danial / Talha", style_td)],
        [Paragraph("<b>L2: Ingestion</b>", style_td_bold), Paragraph("Reads PDFs into clean text passages; streaming generator emits telemetry without drops", style_td), Paragraph("PDF chunker, async streaming", style_td), Paragraph("Danial / Talha", style_td)],
        [Paragraph("<b>L3: Kafka Queue</b>", style_td_bold), Paragraph("Digital highway moving 10,000 sensor messages per second with zero loss", style_td), Paragraph("Apache Kafka (KRaft mode)", style_td), Paragraph("Talha Ali Bhatti", style_td)],
        [Paragraph("<b>L4: Lakehouse</b>", style_td_bold), Paragraph("MinIO S3 raw buckets + Snappy Parquet files saving >75% hard drive space", style_td), Paragraph("MinIO S3, PyArrow Parquet", style_td), Paragraph("Talha Ali Bhatti", style_td)],
        [Paragraph("<b>L5: DuckDB OLAP</b>", style_td_bold), Paragraph("Searches 500,000 car records in computer RAM in less than 80 milliseconds", style_td), Paragraph("DuckDB in-memory engine", style_td), Paragraph("M. Abdullah", style_td)],
        [Paragraph("<b>L6: Safety Triage</b>", style_td_bold), Paragraph("Classifies faults into Danger, Major, Minor; applies 10x penalty on danger errors", style_td), Paragraph("Cost-sensitive ML, Platt ECE", style_td), Paragraph("Ahmad Zahid", style_td)],
        [Paragraph("<b>L7: Transformer AI</b>", style_td_bold), Paragraph("1.32M PyTorch Transformer answering questions with exact manual page numbers", style_td), Paragraph("Custom PyTorch LM, BPE 4k", style_td), Paragraph("Abdullah (Lead)", style_td)],
        [Paragraph("<b>L8: Backend Server</b>", style_td_bold), Paragraph("FastAPI asynchronous server with JWT security and Consistent Hash routing", style_td), Paragraph("FastAPI, JWT, MurmurHash3", style_td), Paragraph("Abdullah (Lead)", style_td)],
        [Paragraph("<b>L9: Web Portal</b>", style_td_bold), Paragraph("React 18 website, PKR price estimator, and Leaflet OpenStreetMap live mechanic dispatch", style_td), Paragraph("React 18, Leaflet, ReportLab", style_td), Paragraph("M. Abdullah", style_td)],
    ]
    t_layers_pdf = Table(layers_table_data, colWidths=[80, 195, 160, 87])
    t_layers_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elements.append(t_layers_pdf)
    elements.append(Spacer(1, 8))

    # Data Flow & Dispatch
    elements.append(Paragraph("2. End-to-End Data Flow & Fault-to-Mechanic Dispatch", style_h1))
    elements.append(Paragraph(
        "<b>1. Driver Query:</b> The car owner types their issue in Roman Urdu (e.g. 'car missing kar rahi hai aur radiator boil ho raha hai').<br/>"
        "<b>2. Tokenization & Safety Triage:</b> Custom BPE tokenizer (4,000 vocab) splits words. The 10x safety triage flags overheating as Danger.<br/>"
        "<b>3. RAG Retrieval & AI Generation:</b> Searches 45 official service manuals. The 1.32M PyTorch Transformer writes a clear explanation citing exact page coordinates.<br/>"
        "<b>4. Pricing & Dispatch:</b> Shows fair PKR price range. The Fault-to-Specialist Engine calculates: "
        "<i>Score = (40% * Skill) + (30% * Proximity) + (20% * Rating) + (10% * Open Queue)</i> and displays the best certified workshop on a live map.",
        style_body
    ))

    doc.build(elements)
    print(f"[OK] Generated PDF Architecture: {output_path}")

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
    print("\nAll System Architecture deliverables successfully generated and synchronized!")
