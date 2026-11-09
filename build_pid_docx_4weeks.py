import os
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

def build_pid_4weeks_docx(output_path):
    doc = Document()
    
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(10)
    normal_style.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(4)

    # Top tracker
    p_badge = doc.add_paragraph()
    r_badge = p_badge.add_run("PROJECT INITIATION DOCUMENT (PID) • BIG DATA & DISTRIBUTED SYSTEMS")
    r_badge.font.name = 'Arial'
    r_badge.font.size = Pt(8.5)
    r_badge.font.bold = True
    r_badge.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    # Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(2)
    p_title.paragraph_format.space_after = Pt(2)
    r_title = p_title.add_run("AutoData Lake")
    r_title.font.name = 'Arial'
    r_title.font.size = Pt(20)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(8)
    r_sub = p_sub.add_run("A 4-Week Rapid Engineering Term Project for Connected Vehicle Fleets (Fall 2026)")
    r_sub.font.size = Pt(11.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    # Synopsis Callout
    callout_table = doc.add_table(rows=1, cols=1)
    callout_cell = callout_table.rows[0].cells[0]
    callout_cell.width = Inches(6.9)
    set_cell_background(callout_cell, "F8FAFC")
    set_cell_margins(callout_cell, top=80, bottom=80, left=140, right=120)
    
    cp = callout_cell.paragraphs[0]
    cp.paragraph_format.space_after = Pt(2)
    cr_title = cp.add_run("EXECUTIVE FORMULATION:\n")
    cr_title.font.name = 'Arial'
    cr_title.font.size = Pt(9)
    cr_title.font.bold = True
    cr_title.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    
    cr_body = cp.add_run(
        "Connected vehicle fleets generate massive streams of high-velocity sensor data alongside heavy unstructured binary assets "
        "(service manuals, diagnostic trouble codes, and cluster scans). This 4-week term project implements foundational Big Data "
        "and distributed systems architectures from first principles—bypassing monolithic relational databases and superficial API wrappers. "
        "The architecture integrates Distributed Object Storage (MinIO S3), Content-Addressable Storage (CAS via SHA-256) for multi-gigabyte deduplication, "
        "a custom Consistent Hashing Ring with Virtual Nodes for fault-tolerant partition sharding, an in-memory Bloom Filter for sub-millisecond DTC pre-indexing, "
        "and an Apache Parquet Lakehouse analyzed via DuckDB/PySpark. The delivery is scheduled across four intensive, milestone-driven weekly sprints."
    )
    cr_body.font.size = Pt(9)
    cr_body.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Meta Table
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False
    set_table_borders(meta_table, "CBD5E1")

    metadata = [
        ("Course & Degree:", "Big Data Systems (CS/DS) — Bachelor of Science in Data Science (BSDS)"),
        ("Execution Window:", "4 Weeks (Rapid Term Project Sprint)"),
        ("Department:", "Department of Data Science / Computing"),
        ("Submission Category:", "Term Project Initiation Document (PID) • Fall 2026")
    ]

    for idx, (label, val) in enumerate(metadata):
        row = meta_table.rows[idx]
        c0 = row.cells[0]
        c0.width = Inches(1.8)
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(1)
        r0 = p0.add_run(label)
        r0.font.name = 'Arial'
        r0.font.size = Pt(9)
        r0.font.bold = True
        r0.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        set_cell_background(c0, "F1F5F9")
        set_cell_margins(c0, top=50, bottom=50, left=100, right=100)

        c1 = row.cells[1]
        c1.width = Inches(5.1)
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(1)
        r1 = p1.add_run(val)
        r1.font.size = Pt(9)
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c1, top=50, bottom=50, left=100, right=100)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Section 1: Team
    p_h1 = doc.add_paragraph()
    p_h1.paragraph_format.space_before = Pt(8)
    p_h1.paragraph_format.space_after = Pt(3)
    r_h1 = p_h1.add_run("1. Project Team Roster & Core Technical Roles")
    r_h1.font.name = 'Arial'
    r_h1.font.size = Pt(11)
    r_h1.font.bold = True
    r_h1.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    team_table = doc.add_table(rows=4, cols=4)
    team_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    team_table.autofit = False
    set_table_borders(team_table, "CBD5E1")

    t_hdrs = ["Sr.", "Member Name", "Roll Number", "Assigned Technical Role (4-Week Scope)"]
    t_widths = [Inches(0.4), Inches(1.6), Inches(1.2), Inches(3.7)]

    hdr_row = team_table.rows[0]
    for idx, name in enumerate(t_hdrs):
        cell = hdr_row.cells[idx]
        cell.width = t_widths[idx]
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(name)
        r.font.name = 'Arial'
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        if idx == 0:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(cell, "1E293B")
        set_cell_margins(cell, top=60, bottom=60, left=80, right=80)

    team_data = [
        ("1", "Talha Ali Bhatti", "bsdsf23a016", "Distributed Storage & Streaming Lead: MinIO S3 cluster setup, bucket lifecycle policies, OBD-II stream generator, and Apache Parquet partitioning."),
        ("2", "Muhammad Abdullah", "bsdsf23a032", "Data Engineering & Analytics Lead: Batch ETL pipelines (DuckDB/PySpark), fleet anomaly models, and query latency benchmarking."),
        ("3", "Abdullah", "bsdsf23a035", "Distributed Algorithms Lead: Consistent Hashing Ring (Virtual Nodes), Content-Addressable Storage (CAS SHA-256), and Bloom Filter engine.")
    ]

    for r_idx, (sr, name, roll, role) in enumerate(team_data):
        row = team_table.rows[r_idx + 1]
        for c_idx, val in enumerate([sr, name, roll, role]):
            cell = row.cells[c_idx]
            cell.width = t_widths[c_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if c_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if c_idx == 2:
                r.bold = True
                r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
            bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=50, bottom=50, left=80, right=80)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Section 2: 5 V's
    p_h2 = doc.add_paragraph()
    p_h2.paragraph_format.space_before = Pt(8)
    p_h2.paragraph_format.space_after = Pt(3)
    r_h2 = p_h2.add_run("2. The 5 V's of Big Data in Connected Telematics")
    r_h2.font.name = 'Arial'
    r_h2.font.size = Pt(11)
    r_h2.font.bold = True
    r_h2.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    table_v = doc.add_table(rows=6, cols=3)
    table_v.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_v.autofit = False
    set_table_borders(table_v, "CBD5E1")

    v_hdrs = ["Dimension", "Workload Manifestation in Connected Vehicles", "Architectural Solution in AutoData Lake"]
    v_widths = [Inches(1.1), Inches(2.8), Inches(3.0)]

    hdr_v_row = table_v.rows[0]
    for idx, name in enumerate(v_hdrs):
        cell = hdr_v_row.cells[idx]
        cell.width = v_widths[idx]
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(name)
        r.font.name = 'Arial'
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_background(cell, "1E293B")
        set_cell_margins(cell, top=60, bottom=60, left=80, right=80)

    v_rows = [
        ("Volume", "10,000+ vehicles generating ~50MB daily telemetry + 20GB unstructured OEM service manual PDFs & damage photos.", "Distributed Object Storage (MinIO S3) decoupled from compute; storage compression via Apache Parquet."),
        ("Velocity", "Continuous CAN-bus & OBD-II sensor streams arriving at 10 Hz to 50 Hz per vehicle requiring sub-second triage.", "Asynchronous Dual-Speed Ingestion (Speed Buffer) utilizing sliding-window micro-batching."),
        ("Variety", "Structured telemetry (Parquet), Unstructured binary media (PDF manuals, cluster photos), and Semi-structured logs (DTCs).", "Unified Multi-Modal Lakehouse storing structured time-series and binary blobs with unified catalogs."),
        ("Veracity", "Sensor dropouts, noise, corrupt frames, and redundant manual uploads across owners.", "SHA-256 cryptographic verification for Content-Addressable Storage (CAS) and schema enforcement."),
        ("Value", "Driver safety triage, fleet predictive failure warning, and localized Pakistani PKR repair cost benchmarks.", "Distributed OLAP analytics (DuckDB/PySpark) driving component longevity models & price protection.")
    ]

    for r_idx, (d0, d1, d2) in enumerate(v_rows):
        row = table_v.rows[r_idx + 1]
        for c_idx, val in enumerate([d0, d1, d2]):
            cell = row.cells[c_idx]
            cell.width = v_widths[c_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if c_idx == 0:
                r.bold = True
                r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
            bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=50, bottom=50, left=80, right=80)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Section 3: Core Concepts
    p_h3 = doc.add_paragraph()
    p_h3.paragraph_format.space_before = Pt(8)
    p_h3.paragraph_format.space_after = Pt(3)
    r_h3 = p_h3.add_run("3. Core Distributed Systems Concepts Implemented")
    r_h3.font.name = 'Arial'
    r_h3.font.size = Pt(11)
    r_h3.font.bold = True
    r_h3.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    doc.add_paragraph(
        "• Distributed Object Storage (MinIO S3 API): Eliminates POSIX inode bottlenecks by persisting unstructured assets as immutable objects under partitioned URI keys: s3://autodata-lake/telemetry/year=2026/make=toyota/model=corolla/vin={VIN}/.\n"
        "• Content-Addressable Storage (CAS SHA-256): Ingested manuals and cluster photos are indexed by their cryptographic hash H(F) = SHA-256(F). Duplicates share a single physical block with atomic reference counters, saving 40%–60% storage.\n"
        "• Consistent Hashing Ring (Ketama with Virtual Nodes): Vehicle VINs are mapped onto a 32-bit keyspace [0, 2^32 - 1] with V = 150 virtual replicas per node. Adding or removing a node migrates only K/N keys on average, avoiding full-cluster invalidation.\n"
        "• Scalable In-Memory Bloom Filter: Pre-indexes 10,000+ SAE diagnostic trouble codes (DTCs) using k = (m/n) ln(2) hash functions, guaranteeing zero false negatives and intercepting non-existent queries prior to disk I/O.\n"
        "• Columnar Lakehouse Storage (Apache Parquet + Snappy): High-velocity telemetry is converted into columnar format with dictionary encoding and run-length compression, achieving >70% size reduction and fast column projection pushdown."
    )

    # Section 4: 4-Week Sprint Roadmap
    p_h4 = doc.add_paragraph()
    p_h4.paragraph_format.space_before = Pt(8)
    p_h4.paragraph_format.space_after = Pt(3)
    r_h4 = p_h4.add_run("4. 4-Week Rapid Execution Roadmap & Sprint Milestones")
    r_h4.font.name = 'Arial'
    r_h4.font.size = Pt(11)
    r_h4.font.bold = True
    r_h4.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    table_4w = doc.add_table(rows=5, cols=4)
    table_4w.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_4w.autofit = False
    set_table_borders(table_4w, "CBD5E1")

    w_hdrs = ["Sprint", "Timeline", "Sprint Scope & Key Technical Deliverables", "Technical Owner"]
    w_widths = [Inches(0.6), Inches(1.1), Inches(3.7), Inches(1.5)]

    hdr_4w_row = table_4w.rows[0]
    for idx, name in enumerate(w_hdrs):
        cell = hdr_4w_row.cells[idx]
        cell.width = w_widths[idx]
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(name)
        r.font.name = 'Arial'
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        if idx == 0:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(cell, "1E293B")
        set_cell_margins(cell, top=60, bottom=60, left=80, right=80)

    four_week_rows = [
        ("W1", "Week 1\n(Days 1–7)", "Infrastructure & CAS Deduplication Engine:\n• Containerized MinIO Distributed Object Storage setup with S3 bucket hierarchy.\n• Implement Content-Addressable Storage (CAS SHA-256) deduplication module.\n• Ingest OEM PDF service manuals and benchmark storage deduplication ratio.", "Talha Ali (016)\nAbdullah (035)"),
        ("W2", "Week 2\n(Days 8–14)", "Consistent Hashing & Bloom Filter Layer:\n• Implement ConsistentHashRing with virtual node replication (V=150) and bisect routing.\n• Implement in-memory BloomFilter for 10,000+ SAE OBD-II diagnostic fault codes.\n• Run statistical Chi-Square test on hash ring to verify uniform key distribution.", "Abdullah (035)"),
        ("W3", "Week 3\n(Days 15–21)", "Stream Ingestion & Columnar Lakehouse Analytics:\n• Build simulated high-frequency CAN-bus / OBD-II stream generator (10 Hz – 50 Hz).\n• Implement streaming buffer and compaction into partitioned Apache Parquet files.\n• Configure DuckDB / PySpark analytical queries for fleet-wide anomaly detection.", "Talha Ali (016)\nM. Abdullah (032)"),
        ("W4", "Week 4\n(Days 22–28)", "Integration, Empirical Benchmarking & Project Defense:\n• Connect data engine with FastAPI endpoints and cluster telemetry dashboard.\n• Execute 5 quantitative benchmarks (Chi-Square uniformity, K/N churn, query latency).\n• Finalize technical term project report, code profiling, and presentation slide deck.", "All Members\n(Joint Defense)")
    ]

    for r_idx, (m0, m1, m2, m3) in enumerate(four_week_rows):
        row = table_4w.rows[r_idx + 1]
        for c_idx, val in enumerate([m0, m1, m2, m3]):
            cell = row.cells[c_idx]
            cell.width = w_widths[c_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if c_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r.bold = True
            if c_idx in [1, 3]:
                r.bold = True
            bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=50, bottom=50, left=80, right=80)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Section 5: RACI
    p_h5 = doc.add_paragraph()
    p_h5.paragraph_format.space_before = Pt(8)
    p_h5.paragraph_format.space_after = Pt(3)
    r_h5 = p_h5.add_run("5. 4-Week RACI Responsibility Assignment Matrix")
    r_h5.font.name = 'Arial'
    r_h5.font.size = Pt(11)
    r_h5.font.bold = True
    r_h5.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    table_raci = doc.add_table(rows=11, cols=4)
    table_raci.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_raci.autofit = False
    set_table_borders(table_raci, "CBD5E1")

    r_hdrs = ["Technical Work Package", "Talha Ali (016)", "M. Abdullah (032)", "Abdullah (035)"]
    r_widths = [Inches(3.3), Inches(1.2), Inches(1.2), Inches(1.2)]

    hdr_r_row = table_raci.rows[0]
    for idx, name in enumerate(r_hdrs):
        cell = hdr_r_row.cells[idx]
        cell.width = r_widths[idx]
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(name)
        r.font.name = 'Arial'
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        if idx > 0:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(cell, "1E293B")
        set_cell_margins(cell, top=60, bottom=60, left=80, right=80)

    raci_rows = [
        ("Week 1: MinIO Object Store Setup & S3 Buckets", "Accountable (A)", "Informed (I)", "Consulted (C)"),
        ("Week 1: CAS Deduplication Engine (SHA-256)", "Informed (I)", "Consulted (C)", "Accountable (A)"),
        ("Week 2: Consistent Hashing Ring with Virtual Nodes", "Consulted (C)", "Informed (I)", "Accountable (A)"),
        ("Week 2: Scalable In-Memory Bloom Filter Lookup", "Informed (I)", "Consulted (C)", "Accountable (A)"),
        ("Week 3: OBD-II High-Frequency Stream Ingestion", "Accountable (A)", "Consulted (C)", "Informed (I)"),
        ("Week 3: Apache Parquet Columnar Lakehouse Storage", "Accountable (A)", "Consulted (C)", "Consulted (C)"),
        ("Week 3: Distributed Fleet Analytics (DuckDB/PySpark)", "Consulted (C)", "Accountable (A)", "Informed (I)"),
        ("Week 4: Empirical Benchmarks & Chi-Square Testing", "Consulted (C)", "Accountable (A)", "Consulted (C)"),
        ("Week 4: Final Documentation, Term Report & Defense", "Responsible (R)", "Responsible (R)", "Responsible (R)")
    ]

    for r_idx, row_vals in enumerate(raci_rows):
        row = table_raci.rows[r_idx + 1]
        for c_idx, val in enumerate(row_vals):
            cell = row.cells[c_idx]
            cell.width = r_widths[c_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(val)
            r.font.size = Pt(8)
            if c_idx > 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if "Accountable" in val:
                    r.bold = True
                    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
            bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=40, bottom=40, left=80, right=80)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Footer
    p_sign = doc.add_paragraph()
    r_s = p_sign.add_run("Submitted on behalf of Group BSDS-23-AutoData: Talha Ali Bhatti (bsdsf23a016) • Muhammad Abdullah (bsdsf23a032) • Abdullah (bsdsf23a035)")
    r_s.font.size = Pt(8.5)
    r_s.font.italic = True
    r_s.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    doc.save(output_path)
    print(f"4-week Word docx successfully generated at: {output_path}")

if __name__ == "__main__":
    docx_out1 = r"C:\Users\ABDUL\.gemini\antigravity\scratch\autocare-us2\Big_Data_PID_AutoData_Lake_4Weeks.docx"
    docx_out2 = r"C:\Users\ABDUL\.gemini\antigravity\brain\00a7aa5b-5d32-449b-a3f6-925ffecf15c5\Big_Data_PID_AutoData_Lake_4Weeks.docx"
    build_pid_4weeks_docx(docx_out1)
    build_pid_4weeks_docx(docx_out2)
