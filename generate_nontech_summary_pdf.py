import os
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas

base_dir = r"C:\Users\ABDUL\.gemini\antigravity\scratch\autocare-us2"
desktop_dir = r"C:\Users\ABDUL\Desktop"
deliverable_dir = r"C:\Users\ABDUL\Desktop\AutoCare_AI_Complete_Deliverable_2026-11-10"
pdf_path = os.path.join(base_dir, "AutoCare_AI_Complete_Project_Guide_NonTech.pdf")

class NonTechCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NonTechCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NonTechCanvas, self).showPage()
        super(NonTechCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "AutoCare AI — Simple Student & Supervisor Project Guide")
            self.drawRightString(letter[0] - 54, letter[1] - 36, "PUCIT • BS Data Science")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawString(54, 34, "AutoCare AI — 5 Team Leads, Completed Work, and What's Next")
        self.drawRightString(letter[0] - 54, 34, page_str)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 46, letter[0] - 54, 46)
        self.restoreState()

def build_pdf():
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54
    )
    styles = getSampleStyleSheet()
    
    style_badge = ParagraphStyle('Badge', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor('#0284C7'), spaceAfter=4)
    style_title = ParagraphStyle('MainTitle', fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#0F172A'), spaceAfter=4)
    style_sub = ParagraphStyle('SubTitle', fontName='Helvetica-Oblique', fontSize=9.5, leading=13, textColor=colors.HexColor('#64748B'), spaceAfter=12)
    style_h1 = ParagraphStyle('SectionH1', fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=colors.HexColor('#0F172A'), spaceBefore=10, spaceAfter=6)
    style_h2 = ParagraphStyle('SectionH2', fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=colors.HexColor('#0284C7'), spaceBefore=8, spaceAfter=4)
    style_body = ParagraphStyle('Body', fontName='Helvetica', fontSize=8.5, leading=12, textColor=colors.HexColor('#334155'), spaceAfter=4)
    style_bullet = ParagraphStyle('Bullet', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#334155'), leftIndent=12, spaceAfter=2)
    style_th = ParagraphStyle('TableHeader', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white)
    style_td = ParagraphStyle('TableCell', fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=colors.HexColor('#1E293B'))
    style_td_bold = ParagraphStyle('TableCellBold', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.HexColor('#0F172A'))

    elements = []

    # Title
    elements.append(Paragraph("PUCIT FINAL YEAR PROJECT • NON-TECHNICAL STUDENT & SUPERVISOR GUIDE", style_badge))
    elements.append(Paragraph("AutoCare AI: Complete Project Guide in Plain English", style_title))
    elements.append(Paragraph("How It Works, What Each of the 5 Team Members Built, and What Comes Next", style_sub))

    # Meta
    meta_data = [
        [Paragraph("<b>Degree & College:</b>", style_td_bold), Paragraph("PUCIT University of the Punjab — BS Data Science", style_td)],
        [Paragraph("<b>The 5 Team Members:</b>", style_td_bold), Paragraph("Abdullah (035), Talha Ali Bhatti (016), Danial Hameed (014), Ahmad Zahid (033), Muhammad Abdullah (032)", style_td)],
        [Paragraph("<b>Project Scope:</b>", style_td_bold), Paragraph("Intelligent Automotive Doctor reading OEM manuals, diagnosing faults in Urdu/English, and predicting fair repair costs", style_td)],
        [Paragraph("<b>Status:</b>", style_td_bold), Paragraph("124 Completed Code Tasks (Done) + 14 Future Big Data Tasks (To Do) | 138 Total Jira Tickets", style_td)],
    ]
    t_meta = Table(meta_data, colWidths=[120, 384])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elements.append(t_meta)
    elements.append(Spacer(1, 10))

    # Section 1
    elements.append(Paragraph("1. What is AutoCare AI in Very Simple Words?", style_h1))
    elements.append(Paragraph(
        "AutoCare AI is a <b>Smart Digital Doctor for your car</b> designed specifically for Pakistani drivers (Toyota Corolla, Honda Civic, Suzuki Swift). "
        "When an engine warning light turns on or your car makes a strange noise, roadside mechanics often give confusing advice and overcharge you for parts you don't need. "
        "Standard ChatGPT also fails because it doesn't know local Pakistani parts availability or market prices in Rupees.<br/><br/>"
        "With AutoCare AI, a car owner can simply type or speak in <b>English, Urdu, or Roman Urdu</b> (e.g. <i>'Gari dhuwan de rahi hai aur engine garam ho raha hai'</i>). "
        "AutoCare AI reads the official car manufacturer service manual, tells you the exact problem, warns you if your brakes or engine are in dangerous condition, "
        "and gives you the fair repair cost in Pakistani Rupees (PKR) so you never get cheated at the workshop.",
        style_body
    ))
    elements.append(Spacer(1, 8))

    # Section 2: Team Leads
    elements.append(Paragraph("2. The 5 Team Members: Who Did What and What Will They Do Next?", style_h1))

    members = [
        (
            "1. ABDULLAH (Roll No: BSDSF23A035) — Group Leader & AI Brain Architect",
            "27 Tickets (116 Story Points)",
            [
                "<b>Custom AI Model from Scratch:</b> Built our own mini-ChatGPT model in PyTorch ($1.32\\text{M}$ parameters) trained specifically on automotive diagnosis, completely independent of commercial APIs.",
                "<b>Subword BPE Tokenizer:</b> Built a custom language converter teaching the AI to understand car words in English, Urdu, and Roman Urdu.",
                "<b>Consistent Hash Ring:</b> Built a smart distributed traffic circle with 160 virtual nodes that routes incoming car data across servers evenly so computers don't crash.",
                "<b>FastAPI Gateway & Git Master:</b> Orchestrated backend microservices and manages the master GitHub repo with 125 commits."
            ],
            [
                "<b>AUT-204:</b> Scale the Consistent Hash Ring across multiple distributed Big Data nodes.",
                "<b>AUT-205:</b> Implement SHA-256 Merkle audit logs so vehicle repair histories can never be secretly modified.",
                "<b>AUT-206:</b> Upgrade user password security to high-memory Argon2id encryption."
            ]
        ),
        (
            "2. TALHA ALI BHATTI (Roll No: BSDSF23A016) — Storage & High-Speed Ingestion Lead",
            "26 Tickets (101 Story Points)",
            [
                "<b>MinIO S3 Object Storage Cluster:</b> Created a secure, private cloud warehouse right on our system to store thousands of vehicle telemetry streams safely.",
                "<b>SHA-256 CAS Deduplication:</b> Built an engine that skips duplicate car manuals and files, saving over 70% hard-drive storage space.",
                "<b>10,000 msg/s Telemetry Streamer:</b> Built a simulator that pushes 10,000 live car sensor signals every second (RPM, speed, engine heat).",
                "<b>Snappy Parquet Columnar Lakehouse:</b> Stores car records in compressed columnar formats organized by car make, model, year, and city."
            ],
            [
                "<b>AUT-201:</b> Deploy Docker Compose Apache Kafka cluster in high-speed KRaft mode.",
                "<b>AUT-202:</b> Connect live 10,000 msg/s telemetry streams directly into Kafka streaming topics.",
                "<b>AUT-203:</b> Build automated Parquet compaction jobs merging micro-batches into fast analytical chunks."
            ]
        ),
        (
            "3. DANIAL HAMEED (Roll No: BSDSF23A014) — Data Engineering & Multilingual Corpus Lead",
            "27 Tickets (112 Story Points)",
            [
                "<b>111-File Automotive Dataset:</b> Gathered, cleaned, and standardized 111 dataset files across 14 categories (PakWheels, Facebook mechanics, YouTube interviews).",
                "<b>45 Official Car Handbooks:</b> Extracted and chunked technical service manuals for Toyota Corolla, Honda Civic, and Suzuki Swift with exact page citations.",
                "<b>Urdu & Roman Urdu Dictionary:</b> Created a bilingual translator mapping informal mechanic slang (like <i>'dhuwan'</i>, <i>'jhatka'</i>, <i>'missing'</i>) to SAE diagnostic codes.",
                "<b>Counting Bloom Filter:</b> Implemented a mathematical filter checking if an error code exists in less than 1 millisecond."
            ],
            [
                "<b>AUT-209:</b> Embed DuckDB OLAP engine for zero-copy analytical queries across Parquet partitions.",
                "<b>AUT-213:</b> Conduct and log all 10 empirical Big Data benchmarks (ingestion speed, compression ratio, query latency)."
            ]
        ),
        (
            "4. AHMAD ZAHID (Roll No: BSDSF23A033) — ML Triage, Safety & Workshop Fraud Lead",
            "28 Tickets (126 Story Points)",
            [
                "<b>Cost-Sensitive Triage Classifier:</b> Trained an emergency triage model with a 10× safety penalty on critical faults (like brake failure or overheating) so dangerous problems are never missed.",
                "<b>Platt Scaling Calibration:</b> Added mathematical confidence calibration that eliminates AI guessing and keeps calibration error below 0.05.",
                "<b>NLI Workshop Invoice Verifier:</b> Built a fraud-detection engine that checks mechanic repair estimates against car manuals to catch unnecessary upsells.",
                "<b>Selective Abstention Gate:</b> If the AI is not 100% sure of an answer, Ahmad's code stops the AI from guessing or making up claims."
            ],
            [
                "<b>AUT-210:</b> Train an Isolation Forest Anomaly Detector to catch hidden sensor faults before a dashboard light trips.",
                "<b>AUT-214:</b> Finalize Level 0, 1, and 2 DFD diagrams and academic presentation slides."
            ]
        ),
        (
            "5. MUHAMMAD ABDULLAH (Roll No: BSDSF23A032) — Web Portal UI, Fleet Analytics & Pricing Lead",
            "30 Tickets (124 Story Points)",
            [
                "<b>Modern React 18 Web Portal:</b> Built a modern automotive engineering website with dark mode, interactive diagnostic terminal, and live sensor tickers.",
                "<b>Pakistani Fair-Price Estimator:</b> Built a verified database of genuine parts and labor costs in Pakistani Rupees (PKR) across Lahore, Karachi, and Islamabad.",
                "<b>DuckDB In-Memory OLAP Engine:</b> Enabled sub-80 millisecond database queries across 500,000 records ($15\\times$ faster than standard SQL).",
                "<b>Climate Multipliers:</b> Formulated algorithms factoring in Pakistani summer heat ($45^\\circ\\text{C}+$ in Lahore/Multan) to calculate realistic component wear."
            ],
            [
                "<b>AUT-207:</b> Implement PySpark distributed batch processing for fleet-wide rolling window aggregations.",
                "<b>AUT-208:</b> Connect Spark Structured Streaming for continuous live telemetry anomaly detection.",
                "<b>AUT-211 & 212:</b> Add a live Big Data Operations Dashboard to the website showing real-time data ingestion meters."
            ]
        )
    ]

    for title, stats, done_items, next_items in members:
        elements.append(Paragraph(title, style_h2))
        elements.append(Paragraph(f"<b>Workload:</b> {stats}", style_body))
        elements.append(Paragraph("<font color='#059669'><b>Completed Work (Done):</b></font>", style_body))
        for it in done_items:
            elements.append(Paragraph(f"• {it}", style_bullet))
        elements.append(Paragraph("<font color='#2563EB'><b>What He Will Build Next:</b></font>", style_body))
        for it in next_items:
            elements.append(Paragraph(f"• {it}", style_bullet))
        elements.append(Spacer(1, 4))

    # Page Break for Summary Table
    elements.append(PageBreak())

    # Section 3
    elements.append(Paragraph("3. How Jira Proves 100% Teamwork to Your Professor", style_h1))
    elements.append(Paragraph(
        "Jira is the industry standard for managing software projects. In our project, every code change is tracked:<br/>"
        "• <b>Total Tickets:</b> 138 Tickets<br/>"
        "• <b>Completed Work:</b> 124 Completed Tickets (marked <b>DONE</b>, backed by 125 Git commits)<br/>"
        "• <b>Upcoming Work:</b> 14 Pre-Structured Big Data Tickets (marked <b>TO DO</b>)<br/>"
        "• <b>Equal Participation:</b> Every member has between 26 and 30 tickets (~115 Story Points each), providing indisputable mathematical proof of teamwork for academic grading.",
        style_body
    ))
    elements.append(Spacer(1, 10))

    # Section 4: Launchers
    elements.append(Paragraph("4. Desktop 1-Click Launchers", style_h1))
    l_data = [
        [Paragraph("<b>Launcher File</b>", style_th), Paragraph("<b>What It Does When Double-Clicked</b>", style_th)],
        [Paragraph("<b>OPEN_JIRA_APP.bat</b>", style_td_bold), Paragraph("Opens your complete, interactive Jira Kanban Board in your browser showing all 138 tickets, Git commits, and member filters.", style_td)],
        [Paragraph("<b>OPEN_AUTOCARE_WEBSITE.bat</b>", style_td_bold), Paragraph("Launches your live AutoCare AI car diagnostic web portal at http://localhost:8000/app/#/dashboard.", style_td)],
        [Paragraph("<b>AutoCare_AI_Complete_Project_Guide_NonTech.docx</b>", style_td_bold), Paragraph("This exact non-technical project guide in editable Microsoft Word format.", style_td)],
        [Paragraph("<b>GitHub Repository</b>", style_td_bold), Paragraph("Live remote repository containing all 125 commits: https://github.com/marketbul/autocare-ai.git", style_td)],
    ]
    t_l = Table(l_data, colWidths=[174, 330])
    t_l.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_l)

    doc.build(elements, canvasmaker=NonTechCanvas)
    print(f"[OK] Generated PDF File: {pdf_path}")
    shutil.copy2(pdf_path, os.path.join(desktop_dir, "AutoCare_AI_Complete_Project_Guide_NonTech.pdf"))
    shutil.copy2(pdf_path, os.path.join(deliverable_dir, "AutoCare_AI_Complete_Project_Guide_NonTech.pdf"))
    print(f"[SYNC] Copied PDF to Desktop!")

if __name__ == "__main__":
    build_pdf()
