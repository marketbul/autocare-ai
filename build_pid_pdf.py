import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_navy = colors.HexColor("#0F2942")
    c_blue = colors.HexColor("#2563EB")
    c_dark = colors.HexColor("#1E293B")
    c_muted = colors.HexColor("#64748B")
    c_bg_light = colors.HexColor("#F8FAFC")
    c_bg_subtle = colors.HexColor("#F1F5F9")
    c_border = colors.HexColor("#CBD5E1")
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_navy,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=11,
        leading=15,
        textColor=c_blue,
        spaceAfter=12
    )

    badge_style = ParagraphStyle(
        'Badge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=c_blue,
        spaceAfter=2
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_navy,
        spaceBefore=12,
        spaceAfter=4
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=c_blue,
        spaceBefore=8,
        spaceAfter=2
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_dark,
        spaceAfter=5
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_dark
    )

    tbl_hdr_style = ParagraphStyle(
        'TblHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    tbl_cell_style = ParagraphStyle(
        'TblCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_dark
    )

    tbl_cell_bold = ParagraphStyle(
        'TblCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=c_navy
    )

    story = []
    
    # Header Badge
    story.append(Paragraph("ACADEMIC TERM PROJECT • BIG DATA SYSTEMS & DISTRIBUTED COMPUTING", badge_style))
    story.append(Paragraph("Project Initiation Document (PID)", title_style))
    story.append(Paragraph("AutoData Lake: Distributed Object Storage, Consistent Hashing & Telemetry Lakehouse Architecture", subtitle_style))
    
    # Executive Callout Box
    callout_text = (
        "<b>EXECUTIVE SCOPE:</b> This project establishes a resilient, distributed Big Data Lakehouse engineered to handle "
        "the high velocity, massive volume, and multimodal variety of connected vehicle telematics. Instead of relying on monolithic "
        "relational databases or superficial API wrappers, this architecture implements foundational distributed algorithms from first "
        "principles—including <b>Consistent Hashing with Virtual Nodes</b> for dynamic partition re-sharding, <b>Content-Addressable "
        "Storage (CAS via SHA-256)</b> for multi-gigabyte deduplication, <b>Scalable In-Memory Bloom Filters</b> for zero-I/O fault verification, "
        "and <b>Columnar Storage (Apache Parquet)</b> for high-performance distributed analytics."
    )
    t_callout = Table([[Paragraph(callout_text, callout_style)]], colWidths=[504])
    t_callout.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('LINELEFT', (0,0), (0,-1), 3.5, c_blue),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_callout)
    story.append(Spacer(1, 8))

    # Metadata & Control Table
    meta_rows = [
        [Paragraph("Course & Degree:", tbl_cell_bold), Paragraph("Big Data Systems (CS/DS) — Bachelor of Science in Data Science (BSDS)", tbl_cell_style)],
        [Paragraph("Department / Faculty:", tbl_cell_bold), Paragraph("Department of Data Science / Computing", tbl_cell_style)],
        [Paragraph("Project Domain:", tbl_cell_bold), Paragraph("Distributed Systems, Object Storage, Stream Ingestion & Lakehouse Analytics", tbl_cell_style)],
        [Paragraph("Document Classification:", tbl_cell_bold), Paragraph("Formal Term Project Initiation Document (PID) • Fall 2026", tbl_cell_style)]
    ]
    t_meta = Table(meta_rows, colWidths=[140, 364])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), c_bg_subtle),
        ('BACKGROUND', (1,0), (1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 8))

    # Team Roster Table
    story.append(Paragraph("Project Team & Assigned Engineering Responsibilities", h1_style))
    team_rows = [
        [Paragraph("Sr.", tbl_hdr_style), Paragraph("Member Name", tbl_hdr_style), Paragraph("Roll No.", tbl_hdr_style), Paragraph("Primary Assigned Technical Responsibilities", tbl_hdr_style)],
        [Paragraph("1", tbl_cell_bold), Paragraph("Talha Ali Bhatti", tbl_cell_style), Paragraph("bsdsf23a016", tbl_cell_bold), Paragraph("Distributed Storage & Streaming Lead: MinIO S3 Object Store cluster configuration, bucket lifecycle policies, Kafka/Stream ingestion buffer, and Parquet partitioning.", tbl_cell_style)],
        [Paragraph("2", tbl_cell_bold), Paragraph("Muhammad Abdullah", tbl_cell_style), Paragraph("bsdsf23a032", tbl_cell_bold), Paragraph("Data Engineering & Analytics Lead: Distributed batch ETL pipelines (PySpark/DuckDB), fleet-wide predictive anomaly models, and OLAP query benchmarking.", tbl_cell_style)],
        [Paragraph("3", tbl_cell_bold), Paragraph("Abdullah", tbl_cell_style), Paragraph("bsdsf23a035", tbl_cell_bold), Paragraph("Distributed Algorithms Lead: Consistent Hashing Ring engine (Virtual Nodes/Ketama), Content-Addressable Storage (CAS SHA-256) deduplication, and Bloom Filter index.", tbl_cell_style)],
    ]
    t_team = Table(team_rows, colWidths=[24, 110, 80, 290])
    t_team.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_team)
    story.append(Spacer(1, 10))

    # 1. 5 V's of Big Data
    story.append(Paragraph("1. The 5 V's of Big Data in Connected Telematics", h1_style))
    v_rows = [
        [Paragraph("Dimension", tbl_hdr_style), Paragraph("Workload Manifestation in Connected Vehicles", tbl_hdr_style), Paragraph("Architectural Solution in AutoData Lake", tbl_hdr_style)],
        [Paragraph("Volume", tbl_cell_bold), Paragraph("10,000+ vehicles generating ~50MB daily telemetry + 20GB unstructured OEM service manual PDFs & damage photos.", tbl_cell_style), Paragraph("Distributed Object Storage (MinIO S3) decoupled from compute; storage compression via Apache Parquet.", tbl_cell_style)],
        [Paragraph("Velocity", tbl_cell_bold), Paragraph("Continuous CAN-bus & OBD-II sensor streams arriving at 10 Hz to 50 Hz per vehicle requiring sub-second safety triage.", tbl_cell_style), Paragraph("Asynchronous Dual-Speed Ingestion (Speed Buffer) utilizing sliding-window micro-batching.", tbl_cell_style)],
        [Paragraph("Variety", tbl_cell_bold), Paragraph("Structured telemetry (Parquet), Unstructured binary media (PDF manuals, cluster photos), and Semi-structured logs (DTCs).", tbl_cell_style), Paragraph("Unified Multi-Modal Lakehouse storing structured time-series and binary blobs with unified catalogs.", tbl_cell_style)],
        [Paragraph("Veracity", tbl_cell_bold), Paragraph("Sensor dropouts, noise, corrupt frames, and redundant manual uploads across owners.", tbl_cell_style), Paragraph("SHA-256 cryptographic verification for Content-Addressable Storage (CAS) and schema enforcement.", tbl_cell_style)],
        [Paragraph("Value", tbl_cell_bold), Paragraph("Driver safety triage, fleet predictive failure warning, and localized Pakistani PKR repair cost benchmarks.", tbl_cell_style), Paragraph("Distributed OLAP analytics (DuckDB/PySpark) driving component longevity models & workshop price protection.", tbl_cell_style)],
    ]
    t_v = Table(v_rows, colWidths=[70, 217, 217])
    t_v.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_v)
    story.append(Spacer(1, 10))

    # 2. Core Concepts
    story.append(Paragraph("2. Foundational Distributed Systems Concepts Implemented", h1_style))
    story.append(Paragraph("<b>2.1 Distributed Object Storage (MinIO S3 API):</b> Replaces POSIX file systems with cloud-native S3 object store for manuals, images, and partitioned telemetry.", body_style))
    story.append(Paragraph("<b>2.2 Content-Addressable Storage (CAS SHA-256):</b> Files stored by SHA-256 hash. Duplicate manual uploads share single physical block, reducing unstructured disk overhead by 40%–60%.", body_style))
    story.append(Paragraph("<b>2.3 Consistent Hashing Ring (Ketama with Virtual Nodes):</b> Vehicle VINs mapped across [0, 2^32 - 1] ring with V=150 virtual nodes per instance. Migrates only K/N keys upon node addition/eviction.", body_style))
    story.append(Paragraph("<b>2.4 Scalable In-Memory Bloom Filter:</b> Pre-indexes 10,000+ SAE diagnostic trouble codes (DTCs) with zero false negatives and p < 0.01, intercepting non-existent queries before storage I/O.", body_style))
    story.append(Paragraph("<b>2.5 Columnar Lakehouse Storage (Apache Parquet + Snappy):</b> Encodes telemetry with dictionary compression and run-length encoding, delivering >70% storage reduction and fast column projection.", body_style))
    story.append(Spacer(1, 6))

    # 3. RACI Matrix
    story.append(Paragraph("3. RACI Responsibility Assignment Matrix", h1_style))
    raci_rows = [
        [Paragraph("Technical Task / Deliverable", tbl_hdr_style), Paragraph("Talha Ali Bhatti (016)", tbl_hdr_style), Paragraph("M. Abdullah (032)", tbl_hdr_style), Paragraph("Abdullah (035)", tbl_hdr_style)],
        [Paragraph("Distributed Object Store Configuration (MinIO S3)", tbl_cell_style), Paragraph("Accountable (A)", tbl_cell_bold), Paragraph("Informed (I)", tbl_cell_style), Paragraph("Consulted (C)", tbl_cell_style)],
        [Paragraph("Consistent Hashing Ring & Virtual Nodes Engine", tbl_cell_style), Paragraph("Consulted (C)", tbl_cell_style), Paragraph("Informed (I)", tbl_cell_style), Paragraph("Accountable (A)", tbl_cell_bold)],
        [Paragraph("Content-Addressable Storage (CAS SHA-256) Engine", tbl_cell_style), Paragraph("Informed (I)", tbl_cell_style), Paragraph("Consulted (C)", tbl_cell_style), Paragraph("Accountable (A)", tbl_cell_bold)],
        [Paragraph("Scalable In-Memory Bloom Filter Lookup Engine", tbl_cell_style), Paragraph("Informed (I)", tbl_cell_style), Paragraph("Consulted (C)", tbl_cell_style), Paragraph("Accountable (A)", tbl_cell_bold)],
        [Paragraph("High-Frequency Stream Ingestion Buffer & Telemetry", tbl_cell_style), Paragraph("Accountable (A)", tbl_cell_bold), Paragraph("Consulted (C)", tbl_cell_style), Paragraph("Informed (I)", tbl_cell_style)],
        [Paragraph("Apache Parquet Columnar Lakehouse & Partitioning", tbl_cell_style), Paragraph("Accountable (A)", tbl_cell_bold), Paragraph("Consulted (C)", tbl_cell_style), Paragraph("Consulted (C)", tbl_cell_style)],
        [Paragraph("Distributed Fleet Analytics Pipeline (PySpark/DuckDB)", tbl_cell_style), Paragraph("Consulted (C)", tbl_cell_style), Paragraph("Accountable (A)", tbl_cell_bold), Paragraph("Informed (I)", tbl_cell_style)],
        [Paragraph("Empirical Benchmarking & Chi-Square Analysis", tbl_cell_style), Paragraph("Consulted (C)", tbl_cell_style), Paragraph("Accountable (A)", tbl_cell_bold), Paragraph("Consulted (C)", tbl_cell_style)],
        [Paragraph("Final Documentation, Scientific Report & Slides", tbl_cell_style), Paragraph("Responsible (R)", tbl_cell_style), Paragraph("Responsible (R)", tbl_cell_style), Paragraph("Responsible (R)", tbl_cell_style)],
    ]
    t_raci = Table(raci_rows, colWidths=[240, 88, 88, 88])
    t_raci.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_raci)
    story.append(Spacer(1, 10))

    # Sign-off
    story.append(Paragraph(
        "<i>Submitted on behalf of Group BSDS-23-AutoData: Talha Ali Bhatti (bsdsf23a016) • Muhammad Abdullah (bsdsf23a032) • Abdullah (bsdsf23a035)</i>",
        ParagraphStyle('Foot', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, textColor=c_muted)
    ))

    doc.build(story)
    print(f"PDF successfully generated at: {output_path}")

if __name__ == "__main__":
    pdf1 = r"C:\Users\ABDUL\.gemini\antigravity\scratch\autocare-us2\Big_Data_Project_Initiation_Document_AutoCare.pdf"
    pdf2 = r"C:\Users\ABDUL\.gemini\antigravity\brain\00a7aa5b-5d32-449b-a3f6-925ffecf15c5\Big_Data_Project_Initiation_Document_AutoCare.pdf"
    generate_pdf(pdf1)
    generate_pdf(pdf2)
