import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_professional_pdf(output_path):
    # Standard 0.75-inch margins for an authoritative academic/technical look
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=45,
        bottomMargin=45
    )
    
    styles = getSampleStyleSheet()
    
    # Minimalist Academic Color Palette
    c_primary = colors.HexColor("#0F172A")    # Deep Slate / Near Black
    c_secondary = colors.HexColor("#334155")  # Muted Charcoal
    c_dark = colors.HexColor("#1E293B")       # Dark Slate 800
    c_body = colors.HexColor("#334155")       # Readable Slate 700
    c_border = colors.HexColor("#CBD5E1")     # Neutral Border Gray
    c_bg_head = colors.HexColor("#1E293B")    # Slate 800 Header
    c_bg_alt = colors.HexColor("#F8FAFC")     # Soft White/Gray
    c_bg_subtle = colors.HexColor("#F1F5F9")  # Neutral Slate 100
    
    # Typographic Hierarchy
    top_tracker = ParagraphStyle(
        'TopTracker',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=c_secondary,
        alignment=0,
        spaceAfter=3
    )

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=c_primary,
        spaceAfter=3
    )
    
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=14,
        textColor=c_secondary,
        spaceAfter=8
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=c_primary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=c_secondary,
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_body,
        spaceAfter=4
    )

    body_bold = ParagraphStyle(
        'BodyBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=c_primary,
        spaceAfter=4
    )

    tbl_hdr = ParagraphStyle(
        'TblHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=0
    )

    tbl_hdr_center = ParagraphStyle(
        'TblHdrCenter',
        parent=tbl_hdr,
        alignment=1
    )

    tbl_cell = ParagraphStyle(
        'TblCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=c_dark
    )

    tbl_cell_center = ParagraphStyle(
        'TblCellCenter',
        parent=tbl_cell,
        alignment=1
    )

    tbl_cell_bold = ParagraphStyle(
        'TblCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.8,
        leading=10.5,
        textColor=c_primary
    )

    callout_p = ParagraphStyle(
        'CalloutP',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=c_dark
    )

    story = []

    # Document Header
    story.append(Paragraph("PROJECT INITIATION DOCUMENT (PID) &bull; BIG DATA &amp; DISTRIBUTED SYSTEMS", top_tracker))
    story.append(Paragraph("AutoData Lake: Distributed Object Storage, Consistent Hashing &amp; Telemetry Lakehouse", title_style))
    story.append(Paragraph("A 4-Week Rapid Engineering Term Project for Connected Vehicle Fleets &bull; Fall 2026", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=0, spaceAfter=8))

    # Executive Summary Callout Box
    synopsis = (
        "<b>EXECUTIVE FORMULATION:</b> Connected vehicle fleets generate massive streams of high-velocity sensor data "
        "alongside heavy unstructured binary assets (service manuals, diagnostic trouble codes, and cluster scans). This 4-week "
        "term project implements foundational Big Data and distributed systems architectures from first principles—bypassing "
        "monolithic relational databases and superficial API wrappers. The architecture integrates <b>Distributed Object Storage (MinIO S3)</b>, "
        "<b>Content-Addressable Storage (CAS via SHA-256)</b> for multi-gigabyte deduplication, a custom <b>Consistent Hashing Ring with Virtual Nodes</b> "
        "for fault-tolerant partition sharding, an in-memory <b>Bloom Filter</b> for sub-millisecond DTC pre-indexing, and an <b>Apache Parquet Lakehouse</b> "
        "analyzed via <b>DuckDB/PySpark</b>. The delivery is scheduled across four intensive, milestone-driven weekly sprints."
    )
    t_syn = Table([[Paragraph(synopsis, callout_p)]], colWidths=[522])
    t_syn.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_alt),
        ('BOX', (0,0), (-1,-1), 0.75, c_border),
        ('LINELEFT', (0,0), (0,-1), 3, c_secondary),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_syn)
    story.append(Spacer(1, 6))

    # Metadata & Team Table
    meta_team_data = [
        [Paragraph("Course &amp; Degree:", tbl_cell_bold), Paragraph("Big Data Systems (CS/DS) — Bachelor of Science in Data Science (BSDS)", tbl_cell),
         Paragraph("Execution Window:", tbl_cell_bold), Paragraph("4 Weeks (Intensive Term Sprint)", tbl_cell_bold)],
        [Paragraph("Department:", tbl_cell_bold), Paragraph("Department of Data Science / Computing", tbl_cell),
         Paragraph("Submission Category:", tbl_cell_bold), Paragraph("Term Project Initiation Document (PID)", tbl_cell)]
    ]
    t_meta = Table(meta_team_data, colWidths=[80, 200, 95, 147])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), c_bg_subtle),
        ('BACKGROUND', (2,0), (2,-1), c_bg_subtle),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 6))

    # Team Members Table
    story.append(Paragraph("1. Project Team Roster &amp; Core Technical Roles", h1_style))
    team_data = [
        [Paragraph("Sr.", tbl_hdr_center), Paragraph("Member Name", tbl_hdr), Paragraph("Roll No.", tbl_hdr), Paragraph("Assigned Technical Role (4-Week Scope)", tbl_hdr)],
        [Paragraph("1", tbl_cell_center), Paragraph("Talha Ali Bhatti", tbl_cell_bold), Paragraph("bsdsf23a016", tbl_cell_bold), Paragraph("Distributed Storage &amp; Streaming Lead: MinIO S3 cluster setup, bucket lifecycle policies, OBD-II stream generator, and Apache Parquet partitioning.", tbl_cell)],
        [Paragraph("2", tbl_cell_center), Paragraph("Muhammad Abdullah", tbl_cell_bold), Paragraph("bsdsf23a032", tbl_cell_bold), Paragraph("Data Engineering &amp; Analytics Lead: Batch ETL pipelines (DuckDB/PySpark), fleet anomaly models, and query latency benchmarking.", tbl_cell)],
        [Paragraph("3", tbl_cell_center), Paragraph("Abdullah", tbl_cell_bold), Paragraph("bsdsf23a035", tbl_cell_bold), Paragraph("Distributed Algorithms Lead: Consistent Hashing Ring (Virtual Nodes), Content-Addressable Storage (CAS SHA-256), and Bloom Filter engine.", tbl_cell)],
    ]
    t_team = Table(team_data, colWidths=[20, 110, 75, 317])
    t_team.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_bg_head),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_alt]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_team)
    story.append(Spacer(1, 6))

    # 2. The 5 V's Table
    story.append(Paragraph("2. Big Data Characteristics (The 5 V's of Automotive Telematics)", h1_style))
    v_data = [
        [Paragraph("Dimension", tbl_hdr), Paragraph("Workload Manifestation in Connected Vehicles", tbl_hdr), Paragraph("Architectural Solution in AutoData Lake", tbl_hdr)],
        [Paragraph("Volume", tbl_cell_bold), Paragraph("10,000+ vehicles generating ~50MB daily telemetry + 20GB unstructured OEM service manual PDFs &amp; damage photos.", tbl_cell), Paragraph("Distributed Object Storage (MinIO S3) decoupled from compute; storage compression via Apache Parquet.", tbl_cell)],
        [Paragraph("Velocity", tbl_cell_bold), Paragraph("Continuous CAN-bus &amp; OBD-II sensor streams arriving at 10 Hz to 50 Hz per vehicle requiring sub-second triage.", tbl_cell), Paragraph("Asynchronous Dual-Speed Ingestion (Speed Buffer) utilizing sliding-window micro-batching.", tbl_cell)],
        [Paragraph("Variety", tbl_cell_bold), Paragraph("Structured telemetry (Parquet), Unstructured binary media (PDF manuals, cluster photos), and Semi-structured logs (DTCs).", tbl_cell), Paragraph("Unified Multi-Modal Lakehouse storing structured time-series and binary blobs with unified catalogs.", tbl_cell)],
        [Paragraph("Veracity", tbl_cell_bold), Paragraph("Sensor dropouts, noise, corrupt frames, and redundant manual uploads across owners.", tbl_cell), Paragraph("SHA-256 cryptographic verification for Content-Addressable Storage (CAS) and schema enforcement.", tbl_cell)],
        [Paragraph("Value", tbl_cell_bold), Paragraph("Driver safety triage, fleet predictive failure warning, and localized Pakistani PKR repair cost benchmarks.", tbl_cell), Paragraph("Distributed OLAP analytics (DuckDB/PySpark) driving component longevity models &amp; price protection.", tbl_cell)],
    ]
    t_v = Table(v_data, colWidths=[65, 230, 227])
    t_v.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_bg_head),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_alt]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_v)
    story.append(Spacer(1, 6))

    # 3. Foundational Big Data Concepts Implemented
    story.append(Paragraph("3. Core Distributed Systems Concepts Implemented", h1_style))
    story.append(Paragraph("<b>3.1 Distributed Object Storage (MinIO S3 API):</b> Eliminates POSIX inode bottlenecks by persisting unstructured assets as immutable objects under partitioned URI keys: <i>s3://autodata-lake/telemetry/year=2026/make=toyota/model=corolla/vin={VIN}/</i>.", body_style))
    story.append(Paragraph("<b>3.2 Content-Addressable Storage (CAS SHA-256):</b> Ingested manuals and cluster photos are indexed by their cryptographic hash <i>H(F) = SHA-256(F)</i>. Duplicates share a single physical block with atomic reference counters, saving 40%–60% storage.", body_style))
    story.append(Paragraph("<b>3.3 Consistent Hashing Ring (Ketama with Virtual Nodes):</b> Vehicle VINs are mapped onto a 32-bit keyspace [0, 2^32 - 1] with <i>V = 150</i> virtual replicas per node. Adding or removing a node migrates only <i>K/N</i> keys on average, avoiding full-cluster invalidation.", body_style))
    story.append(Paragraph("<b>3.4 Scalable In-Memory Bloom Filter:</b> Pre-indexes 10,000+ SAE diagnostic trouble codes (DTCs) using <i>k = (m/n) ln(2)</i> hash functions, guaranteeing zero false negatives and intercepting non-existent queries prior to disk I/O.", body_style))
    story.append(Paragraph("<b>3.5 Columnar Lakehouse Storage (Apache Parquet + Snappy):</b> High-velocity telemetry is converted into columnar format with dictionary encoding and run-length compression, achieving &gt;70% size reduction and fast column projection pushdown.", body_style))
    story.append(Spacer(1, 6))

    # 4. 4-Week Sprint Roadmap
    story.append(Paragraph("4. 4-Week Rapid Execution Roadmap &amp; Sprint Milestones", h1_style))
    story.append(Paragraph("The project is structured into four intensive 1-week sprints to achieve full end-to-end implementation:", body_style))
    
    four_week_data = [
        [Paragraph("Sprint", tbl_hdr_center), Paragraph("Timeline", tbl_hdr), Paragraph("Sprint Scope &amp; Key Technical Deliverables", tbl_hdr), Paragraph("Owner / Lead", tbl_hdr)],
        [
            Paragraph("W1", tbl_cell_center),
            Paragraph("Week 1<br/>Days 1–7", tbl_cell_bold),
            Paragraph("<b>Infrastructure &amp; CAS Deduplication Engine:</b><br/>"
                      "• Containerized MinIO Distributed Object Storage setup with S3 bucket hierarchy.<br/>"
                      "• Implement Content-Addressable Storage (CAS SHA-256) deduplication module.<br/>"
                      "• Ingest OEM PDF service manuals and benchmark storage deduplication ratio.", tbl_cell),
            Paragraph("Talha Ali (016)<br/>Abdullah (035)", tbl_cell_bold)
        ],
        [
            Paragraph("W2", tbl_cell_center),
            Paragraph("Week 2<br/>Days 8–14", tbl_cell_bold),
            Paragraph("<b>Consistent Hashing &amp; Bloom Filter Layer:</b><br/>"
                      "• Implement <i>ConsistentHashRing</i> with virtual node replication (V=150) and bisect routing.<br/>"
                      "• Implement in-memory <i>BloomFilter</i> for 10,000+ SAE OBD-II diagnostic fault codes.<br/>"
                      "• Run statistical Chi-Square test on hash ring to verify uniform key distribution.", tbl_cell),
            Paragraph("Abdullah (035)", tbl_cell_bold)
        ],
        [
            Paragraph("W3", tbl_cell_center),
            Paragraph("Week 3<br/>Days 15–21", tbl_cell_bold),
            Paragraph("<b>Stream Ingestion &amp; Columnar Lakehouse Analytics:</b><br/>"
                      "• Build simulated high-frequency CAN-bus / OBD-II stream generator (10 Hz – 50 Hz).<br/>"
                      "• Implement streaming buffer and compaction into partitioned Apache Parquet files.<br/>"
                      "• Configure DuckDB / PySpark analytical queries for fleet-wide anomaly detection.", tbl_cell),
            Paragraph("Talha Ali (016)<br/>M. Abdullah (032)", tbl_cell_bold)
        ],
        [
            Paragraph("W4", tbl_cell_center),
            Paragraph("Week 4<br/>Days 22–28", tbl_cell_bold),
            Paragraph("<b>Integration, Empirical Benchmarking &amp; Project Defense:</b><br/>"
                      "• Connect data engine with FastAPI endpoints and cluster telemetry dashboard.<br/>"
                      "• Execute 5 quantitative benchmarks (Chi-Square uniformity, K/N churn, query latency).<br/>"
                      "• Finalize technical term project report, code profiling, and presentation slide deck.", tbl_cell),
            Paragraph("All Members<br/>(Joint Defense)", tbl_cell_bold)
        ],
    ]
    t_4w = Table(four_week_data, colWidths=[24, 60, 318, 120])
    t_4w.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_bg_head),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_alt]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_4w)
    story.append(Spacer(1, 6))

    # 5. RACI Matrix
    story.append(Paragraph("5. 4-Week RACI Responsibility Assignment Matrix", h1_style))
    raci_data = [
        [Paragraph("Technical Work Package", tbl_hdr), Paragraph("Talha Ali (016)", tbl_hdr_center), Paragraph("M. Abdullah (032)", tbl_hdr_center), Paragraph("Abdullah (035)", tbl_hdr_center)],
        [Paragraph("Week 1: MinIO Object Store Setup &amp; S3 Buckets", tbl_cell), Paragraph("Accountable (A)", tbl_cell_bold), Paragraph("Informed (I)", tbl_cell), Paragraph("Consulted (C)", tbl_cell)],
        [Paragraph("Week 1: CAS Deduplication Engine (SHA-256)", tbl_cell), Paragraph("Informed (I)", tbl_cell), Paragraph("Consulted (C)", tbl_cell), Paragraph("Accountable (A)", tbl_cell_bold)],
        [Paragraph("Week 2: Consistent Hashing Ring with Virtual Nodes", tbl_cell), Paragraph("Consulted (C)", tbl_cell), Paragraph("Informed (I)", tbl_cell), Paragraph("Accountable (A)", tbl_cell_bold)],
        [Paragraph("Week 2: Scalable In-Memory Bloom Filter Lookup", tbl_cell), Paragraph("Informed (I)", tbl_cell), Paragraph("Consulted (C)", tbl_cell), Paragraph("Accountable (A)", tbl_cell_bold)],
        [Paragraph("Week 3: OBD-II High-Frequency Stream Ingestion", tbl_cell), Paragraph("Accountable (A)", tbl_cell_bold), Paragraph("Consulted (C)", tbl_cell), Paragraph("Informed (I)", tbl_cell)],
        [Paragraph("Week 3: Apache Parquet Columnar Lakehouse Storage", tbl_cell), Paragraph("Accountable (A)", tbl_cell_bold), Paragraph("Consulted (C)", tbl_cell), Paragraph("Consulted (C)", tbl_cell)],
        [Paragraph("Week 3: Distributed Fleet Analytics (DuckDB/PySpark)", tbl_cell), Paragraph("Consulted (C)", tbl_cell), Paragraph("Accountable (A)", tbl_cell_bold), Paragraph("Informed (I)", tbl_cell)],
        [Paragraph("Week 4: Empirical Benchmarks &amp; Chi-Square Testing", tbl_cell), Paragraph("Consulted (C)", tbl_cell), Paragraph("Accountable (A)", tbl_cell_bold), Paragraph("Consulted (C)", tbl_cell)],
        [Paragraph("Week 4: Final Documentation, Term Report &amp; Defense", tbl_cell), Paragraph("Responsible (R)", tbl_cell), Paragraph("Responsible (R)", tbl_cell), Paragraph("Responsible (R)", tbl_cell)],
    ]
    t_raci = Table(raci_data, colWidths=[240, 94, 94, 94])
    t_raci.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_bg_head),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_alt]),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 2.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.8),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_raci)
    story.append(Spacer(1, 8))

    # 6. Evaluation & Defensibility
    story.append(Paragraph("6. Academic Significance &amp; Evaluation Defensibility", h1_style))
    story.append(Paragraph(
        "By delivering AutoData Lake within this disciplined 4-week timeline, the group presents a concrete systems-level "
        "engineering project that directly answers academic evaluation criteria: (1) Core distributed algorithms are implemented "
        "from first principles rather than relying on black-box AI code; (2) Performance is validated through formal statistical tests "
        "(Chi-Square uniformity, K/N re-sharding overhead, and query latency); and (3) The architecture mirrors state-of-the-art "
        "telematics pipelines deployed in the automotive industry.",
        body_style
    ))
    story.append(Spacer(1, 4))

    # Footer Sign-off
    story.append(HRFlowable(width="100%", thickness=0.75, color=c_border, spaceBefore=4, spaceAfter=4))
    story.append(Paragraph(
        "Submitted on behalf of Group BSDS-23-AutoData: Talha Ali Bhatti (bsdsf23a016) &bull; Muhammad Abdullah (bsdsf23a032) &bull; Abdullah (bsdsf23a035)",
        ParagraphStyle('Foot', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=7.5, textColor=c_secondary, alignment=1)
    ))

    doc.build(story)
    print(f"Professional 4-week PDF successfully generated at: {output_path}")

if __name__ == "__main__":
    pdf_out1 = r"C:\Users\ABDUL\.gemini\antigravity\scratch\autocare-us2\Big_Data_PID_AutoData_Lake_4Weeks.pdf"
    pdf_out2 = r"C:\Users\ABDUL\.gemini\antigravity\brain\00a7aa5b-5d32-449b-a3f6-925ffecf15c5\Big_Data_PID_AutoData_Lake_4Weeks.pdf"
    generate_professional_pdf(pdf_out1)
    generate_professional_pdf(pdf_out2)
