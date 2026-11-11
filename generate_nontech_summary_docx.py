import os
import shutil
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

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

def generate_nontech_summary_docx():
    base_dir = r"C:\Users\ABDUL\.gemini\antigravity\scratch\autocare-us2"
    desktop_dir = r"C:\Users\ABDUL\Desktop"
    deliverable_dir = r"C:\Users\ABDUL\Desktop\AutoCare_AI_Complete_Deliverable_2026-11-10"

    doc = Document()

    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)

    normal = doc.styles['Normal']
    normal.font.name = 'Calibri'
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
    normal.paragraph_format.line_spacing = 1.2
    normal.paragraph_format.space_after = Pt(5)

    # Top Badge
    p_badge = doc.add_paragraph()
    r = p_badge.add_run("PUCIT FINAL YEAR PROJECT • SIMPLE STUDENT & SUPERVISOR GUIDE")
    r.font.name = 'Arial'; r.font.size = Pt(8.5); r.font.bold = True; r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    # Main Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(2)
    p_title.paragraph_format.space_after = Pt(2)
    r = p_title.add_run("AutoCare AI: Complete Project Guide in Plain English")
    r.font.name = 'Arial'; r.font.size = Pt(20); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(12)
    r = p_sub.add_run("A Non-Technical Guide: How AutoCare AI Works, What Each of the 5 Members Did, and What Is Coming Next")
    r.font.size = Pt(11); r.font.italic = True; r.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    # Meta Table
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Degree & College", "Punjab University College of Information Technology (PUCIT) — BS Data Science"),
        ("Project Name", "AutoCare AI / AutoData Lake (Intelligent Automotive Intelligence Platform)"),
        ("The 5 Team Members", "Abdullah (035), Talha Ali Bhatti (016), Danial Hameed (014), Ahmad Zahid (033), Muhammad Abdullah (032)"),
        ("Work Status", "124 Completed Code Tasks (Done) + 14 Upcoming Big Data Tasks (To Do) | Total 138 Jira Tickets")
    ]
    for i, (k, v) in enumerate(meta_data):
        row = meta_table.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.0); c1.width = Inches(4.8)
        c0.paragraphs[0].text = k
        c0.paragraphs[0].runs[0].font.bold = True; c0.paragraphs[0].runs[0].font.size = Pt(9.5)
        c1.paragraphs[0].text = v
        c1.paragraphs[0].runs[0].font.size = Pt(9.5)
        set_cell_background(c0, "F8FAFC"); set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, 60, 60, 80, 80); set_cell_margins(c1, 60, 60, 80, 80)
    set_table_borders(meta_table)

    # SECTION 1
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    h1 = doc.add_paragraph()
    r = h1.add_run("1. What is AutoCare AI in Very Simple Words?")
    r.font.name = 'Arial'; r.font.size = Pt(14); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p = doc.add_paragraph()
    p.add_run(
        "Imagine you own a car in Pakistan (such as a Toyota Corolla, Honda Civic, or Suzuki Swift). "
        "One day while driving on the road, an engine warning light turns on or your car starts making a strange rattling sound. "
        "Normally, car owners face two big problems:\n"
        "1. Local mechanics in roadside workshops often give confusing advice and can easily overcharge you by recommending expensive repairs that your car does not actually need.\n"
        "2. If you try asking a generic AI (like standard ChatGPT), it often gives generic Western advice that does not match Pakistani cars, fuel quality, or local workshop prices.\n\n"
        "AutoCare AI is a Smart Digital Doctor for your car. You can type or speak in English, Urdu, or Roman Urdu (for example: \"Gari dhuwan de rahi hai aur engine garam ho raha hai\"). "
        "AutoCare AI reads the car's official manufacturer handbook, diagnoses the exact mechanical fault, gives you verified repair instructions, warns you if your brakes or engine are in dangerous condition, "
        "and tells you the exact fair repair cost in Pakistani Rupees (PKR) so no workshop can cheat you."
    )

    # SECTION 2
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    h2 = doc.add_paragraph()
    r = h2.add_run("2. The 5 Team Members: Who Did What and What Will They Do Next?")
    r.font.name = 'Arial'; r.font.size = Pt(14); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_lead_intro = doc.add_paragraph()
    p_lead_intro.add_run(
        "The entire project workload is divided equally among our 5 team members. Each member is the specialist lead of their specific department. "
        "Below is the exact non-technical explanation of what each person has built so far, and what they will build next."
    )

    members_detail = [
        (
            "MEMBER 1: ABDULLAH (Roll No: BSDSF23A035)",
            "The Group Leader & AI Brain Architect",
            "27 Tickets (116 Story Points)",
            "What He Built So Far (Completed Work):",
            [
                "Built our own custom AI Brain from scratch using PyTorch (instead of paying OpenAI). This AI model has 1.32 million learning parameters and was specifically trained on automotive fault pairs.",
                "Built the BPE Tokenizer: A custom language converter that teaches our AI model how to read mechanical words in English, Urdu, and Roman Urdu.",
                "Engineered the Consistent Hash Ring (160 Virtual Nodes): A smart distributed traffic circle that balances incoming car records evenly across computers so no single server crashes.",
                "Built the main FastAPI web gateway and manages the master GitHub repository with 125 verified commits."
            ],
            "What He Will Build Next (Future Big Data Phase):",
            [
                "AUT-204: Scale the Consistent Hash Ring across multiple distributed Big Data nodes.",
                "AUT-205: Implement SHA-256 Merkle Audit Logs to ensure vehicle records can never be secretly edited or hacked.",
                "AUT-206: Upgrade user password security to high-memory Argon2id encryption."
            ]
        ),
        (
            "MEMBER 2: TALHA ALI BHATTI (Roll No: BSDSF23A016)",
            "The Digital Warehouse & High-Speed Pipeline Engineer",
            "26 Tickets (101 Story Points)",
            "What He Built So Far (Completed Work):",
            [
                "Built the MinIO S3 Object Storage Cluster: A private, high-speed digital warehouse hosted right on our machine to store car data safely.",
                "Built Content-Addressable Storage (CAS) Deduplication: When multiple people upload the same vehicle manual or repetitive data, his system automatically stores it only once, saving over 70% hard-drive space.",
                "Built the OBD-II CAN-Bus Telemetry Streamer: An ultra-fast simulator that pumps 10,000 car sensor signals every second without crashing.",
                "Built the Snappy Parquet Columnar Lakehouse: Stores car records in compressed columnar formats organized by car make, model, year, and city."
            ],
            "What He Will Build Next (Future Big Data Phase):",
            [
                "AUT-201: Launch the Docker Compose Apache Kafka cluster in high-speed KRaft mode.",
                "AUT-202: Connect the 10,000 events/second live telemetry generator directly into Kafka topics.",
                "AUT-203: Build automated Parquet compaction jobs to merge tiny data files into high-speed analytical blocks."
            ]
        ),
        (
            "MEMBER 3: DANIAL HAMEED (Roll No: BSDSF23A014)",
            "The Data Collector, Librarian & Language Specialist",
            "27 Tickets (112 Story Points)",
            "What He Built So Far (Completed Work):",
            [
                "Collected, cleaned, and standardized 111 dataset files across 14 categories (PakWheels discussions, mechanic interview videos, Facebook questions).",
                "Extracted and chunked 45 official service handbooks for Toyota Corolla, Honda Civic, and Suzuki Swift, tagging every repair procedure with its exact book page number.",
                "Built our Bilingual Automotive Dictionary: Automatically translates informal Pakistani mechanic slang (like 'dhuwan' for smoke, 'jhatka' for engine jerking, 'missing' for misfire) into formal SAE diagnostic codes.",
                "Built the Counting Bloom Filter: A lightning-fast math gate that checks if an error code exists in less than 1 millisecond, preventing wasteful disk searches."
            ],
            "What He Will Build Next (Future Big Data Phase):",
            [
                "AUT-209: Integrate DuckDB in-memory queries directly onto Parquet files for sub-80 millisecond analytical searches.",
                "AUT-213: Run and document the 10 empirical Big Data benchmarks (data ingestion speed, storage compression ratios, and query performance)."
            ]
        ),
        (
            "MEMBER 4: AHMAD ZAHID (Roll No: BSDSF23A033)",
            "The Safety Doctor & Workshop Fraud Inspector",
            "28 Tickets (126 Story Points)",
            "What He Built So Far (Completed Work):",
            [
                "Built the Cost-Sensitive Triage Classifier: A smart medical-style triage model that treats critical safety faults (like brake failure or engine overheating) with a 10x safety penalty so dangerous problems are never missed.",
                "Built Platt Scaling & Confidence Calibration: A mathematical safety layer that stops the AI from guessing. If the AI is not 100% sure of an answer, Ahmad's code forces it to safely abstain rather than lying.",
                "Built the NLI Workshop Invoice Verifier: A fraud-detection engine that reads a mechanic's repair bill and cross-checks it against official car manuals to catch unnecessary upsells.",
                "Enforced Proposal Section 17 Ethical Guidelines: Ensures the system gives neutral, polite, and fact-backed repair advice without making wrongful legal accusations."
            ],
            "What He Will Build Next (Future Big Data Phase):",
            [
                "AUT-210: Build the Isolation Forest Anomaly Detector to catch hidden sensor failures before a warning light even trips.",
                "AUT-214: Compile the finalized DFD Level 0, Level 1, and Level 2 diagrams and academic defense presentation slides."
            ]
        ),
        (
            "MEMBER 5: MUHAMMAD ABDULLAH (Roll No: BSDSF23A032)",
            "The Web Portal Designer, Analytics & Market Pricing Specialist",
            "30 Tickets (124 Story Points)",
            "What He Built So Far (Completed Work):",
            [
                "Built the modern React 18 Web Portal: A sleek, professional automotive engineering website (with dark mode, interactive diagnostic terminal, live tickers, and scenario cards).",
                "Built the Pakistani Fair-Price Market Estimator: A verified pricing database in Pakistani Rupees (PKR) covering genuine vs aftermarket parts and labor rates across Lahore, Karachi, and Islamabad.",
                "Integrated the DuckDB In-Memory OLAP Engine: Enables super-fast database queries that crunch through 500,000 vehicle records in less than a blink of an eye (15x faster than normal databases).",
                "Formulated Vehicle Health Index & Climate Multipliers: Accounts for severe Pakistani summer heat (45°C+ in Lahore/Multan) to calculate realistic component wear on radiators, suspension, and oils."
            ],
            "What He Will Build Next (Future Big Data Phase):",
            [
                "AUT-207: Implement PySpark distributed batch processing for fleet-wide rolling window aggregations.",
                "AUT-208: Connect Spark Structured Streaming to Kafka for continuous real-time telemetry processing.",
                "AUT-211 & AUT-212: Add a live Big Data Operations Dashboard to the website showing real-time data ingestion meters and storage counters."
            ]
        )
    ]

    for title, role, stats, done_hdr, done_list, next_hdr, next_list in members_detail:
        doc.add_paragraph().paragraph_format.space_after = Pt(4)
        h_mem = doc.add_paragraph()
        r = h_mem.add_run(f"📌 {title}")
        r.font.name = 'Arial'; r.font.size = Pt(12); r.font.bold = True; r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)
        
        p_subm = doc.add_paragraph()
        p_subm.paragraph_format.space_after = Pt(4)
        r = p_subm.add_run(f"Department: {role}  |  Assigned Work: {stats}")
        r.font.bold = True; r.font.size = Pt(9.5); r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

        # Done Header
        p_dh = doc.add_paragraph()
        p_dh.paragraph_format.space_before = Pt(2); p_dh.paragraph_format.space_after = Pt(2)
        r = p_dh.add_run(f"✅ {done_hdr}")
        r.font.bold = True; r.font.size = Pt(10); r.font.color.rgb = RGBColor(0x05, 0x96, 0x69)

        for item in done_list:
            bp = doc.add_paragraph(style='List Bullet')
            bp.paragraph_format.space_after = Pt(2)
            r = bp.add_run(item)
            r.font.size = Pt(9.5)

        # Next Header
        p_nh = doc.add_paragraph()
        p_nh.paragraph_format.space_before = Pt(4); p_nh.paragraph_format.space_after = Pt(2)
        r = p_nh.add_run(f"🚀 {next_hdr}")
        r.font.bold = True; r.font.size = Pt(10); r.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)

        for item in next_list:
            bp = doc.add_paragraph(style='List Bullet')
            bp.paragraph_format.space_after = Pt(2)
            r = bp.add_run(item)
            r.font.size = Pt(9.5)

    # SECTION 3
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    h3 = doc.add_paragraph()
    r = h3.add_run("3. The End-to-End System Story: How Data Moves in One Picture")
    r.font.name = 'Arial'; r.font.size = Pt(14); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_flow = doc.add_paragraph()
    p_flow.add_run(
        "Here is what happens inside AutoCare AI whenever a car owner uses the website:\n\n"
        "Step 1: The Car Owner opens the website (built by Muhammad Abdullah) and types: 'Corolla 2021 engine is jerking and smoking'.\n"
        "Step 2: The Language Engine (built by Danial Hameed) translates 'jerking' into misfire and checks the Counting Bloom Filter to see if the manual is available.\n"
        "Step 3: The Data Ingestion Pipe (built by Talha Ali Bhatti) logs the car's record into our high-speed MinIO/Parquet storage warehouse.\n"
        "Step 4: The Safety Doctor (built by Ahmad Zahid) checks the severity: Is it dangerous to drive, or is it a minor issue?\n"
        "Step 5: The AI Brain (built by Abdullah) reads the exact Corolla 2021 manufacturer manual and writes a verified step-by-step fix with exact book citations.\n"
        "Step 6: The Pricing Calculator (built by Muhammad Abdullah) estimates genuine parts and labor costs in PKR.\n\n"
        "Outcome Delivered: In less than 1 second, the car owner sees the exact problem, the verified manual fix, whether it is safe to drive, and the honest market price in PKR!"
    )

    # SECTION 4
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    h4 = doc.add_paragraph()
    r = h4.add_run("4. How Jira Proves Teamwork & Collaboration")
    r.font.name = 'Arial'; r.font.size = Pt(14); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_jira = doc.add_paragraph()
    p_jira.add_run(
        "Jira is the world's most popular tool for managing software projects. "
        "In our project, every single line of code is tracked on Jira under Project Key 'AUT':\n"
        "• Total Tickets: 138 Tickets\n"
        "• Completed Work: 124 Completed Tickets (marked 'Done' and linked directly to our 125 Git commits)\n"
        "• Upcoming Work: 14 Pre-Planned Tickets (marked 'To Do' for our next Big Data tasks)\n"
        "• Equal Workload: Every single member has between 26 and 30 tickets, proving 100% equal participation for academic grading!"
    )

    # SECTION 5: ONE-CLICK SHORTCUTS
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    h5 = doc.add_paragraph()
    r = h5.add_run("5. Quick 1-Click Launchers on Your Desktop")
    r.font.name = 'Arial'; r.font.size = Pt(14); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    table_launch = doc.add_table(rows=4, cols=2)
    table_launch.alignment = WD_TABLE_ALIGNMENT.CENTER
    launch_data = [
        ("OPEN_JIRA_APP.bat", "Double-click this on your Desktop to open your interactive Jira Scrum Board with all 138 tickets and member filters!"),
        ("OPEN_AUTOCARE_WEBSITE.bat", "Double-click this on your Desktop to open your live AutoCare AI car diagnostic web portal (http://localhost:8000/app/#/dashboard)."),
        ("AutoCare_AI_Jira_Workflow_Backlog.pdf", "Print-ready PDF report of all 138 Jira tickets, Git commits, and 6-sprint roadmap."),
        ("GitHub Repository", "All code, models, and Jira files are pushed live at: https://github.com/marketbul/autocare-ai.git")
    ]
    for i, (k, v) in enumerate(launch_data):
        row = table_launch.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2); c1.width = Inches(4.6)
        c0.paragraphs[0].text = k
        c0.paragraphs[0].runs[0].font.bold = True; c0.paragraphs[0].runs[0].font.size = Pt(9)
        c1.paragraphs[0].text = v
        c1.paragraphs[0].runs[0].font.size = Pt(9)
        set_cell_background(c0, "F8FAFC"); set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, 50, 50, 60, 60); set_cell_margins(c1, 50, 50, 60, 60)
    set_table_borders(table_launch)

    out_file = os.path.join(base_dir, "AutoCare_AI_Complete_Project_Guide_NonTech.docx")
    doc.save(out_file)
    print(f"[OK] Generated Word File: {out_file}")

    # Copy to Desktop and Deliverables
    desktop_file = os.path.join(desktop_dir, "AutoCare_AI_Complete_Project_Guide_NonTech.docx")
    deliverable_file = os.path.join(deliverable_dir, "AutoCare_AI_Complete_Project_Guide_NonTech.docx")
    shutil.copy2(out_file, desktop_file)
    shutil.copy2(out_file, deliverable_file)
    print(f"[SYNC] Copied to Desktop: {desktop_file}")

if __name__ == "__main__":
    generate_nontech_summary_docx()
