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

def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_callout_border(cell, color_hex="1E3A8A", sz="36"):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color_hex}"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

def set_table_borders(table, color_hex="E2E8F0"):
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

def build_pid_document(output_path):
    doc = Document()
    
    # Page setup (Letter, 1-inch margins)
    for section in doc.sections:
        section.top_margin = Inches(0.9)
        section.bottom_margin = Inches(0.9)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)
        
    # Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(10.5)
    normal_style.font.color.rgb = RGBColor(0x33, 0x41, 0x55) # Slate 700
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(5)

    # Top Category Tracker
    p_badge = doc.add_paragraph()
    p_badge.paragraph_format.space_after = Pt(2)
    r_badge = p_badge.add_run("ACADEMIC TERM PROJECT • BIG DATA SYSTEMS & DISTRIBUTED COMPUTING")
    r_badge.font.name = 'Arial'
    r_badge.font.size = Pt(8.5)
    r_badge.font.bold = True
    r_badge.font.color.rgb = RGBColor(0x25, 0x63, 0xEB) # Royal Blue

    # Main Project Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(2)
    p_title.paragraph_format.space_after = Pt(2)
    r_title = p_title.add_run("Project Initiation Document (PID)")
    r_title.font.name = 'Arial'
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A) # Slate 900

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(12)
    r_sub = p_sub.add_run("AutoData Lake: A Distributed Object Storage, Consistent Hashing & Telemetry Lakehouse Architecture for Connected Vehicle Fleets")
    r_sub.font.name = 'Calibri'
    r_sub.font.size = Pt(13)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(0x47, 0x55, 0x69) # Slate 600

    # Callout Box - Executive Synopsis
    callout_table = doc.add_table(rows=1, cols=1)
    callout_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    callout_cell = callout_table.rows[0].cells[0]
    callout_cell.width = Inches(6.7)
    set_cell_background(callout_cell, "F8FAFC")
    set_callout_border(callout_cell, color_hex="2563EB", sz="36")
    set_cell_margins(callout_cell, top=100, bottom=100, left=180, right=140)
    
    cp = callout_cell.paragraphs[0]
    cp.paragraph_format.space_after = Pt(2)
    cr_title = cp.add_run("EXECUTIVE SUMMARY & SYSTEM SCOPE\n")
    cr_title.font.name = 'Arial'
    cr_title.font.size = Pt(9.5)
    cr_title.font.bold = True
    cr_title.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
    
    cr_body = cp.add_run(
        "This project establishes a resilient, distributed Big Data Lakehouse engineered to handle the high velocity, "
        "massive volume, and multimodal variety of connected vehicle telematics. Instead of relying on monolithic relational "
        "databases or superficial API integrations, this architecture implements foundational distributed systems algorithms "
        "from first principles—including Consistent Hashing with Virtual Nodes for dynamic partition re-sharding, Content-Addressable "
        "Storage (CAS) via cryptographic SHA-256 digests for multi-gigabyte deduplication, Scalable In-Memory Bloom Filters for "
        "zero-I/O fault verification, and Columnar Storage (Apache Parquet) for high-performance distributed analytics."
    )
    cr_body.font.size = Pt(9.5)
    cr_body.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Document Metadata Table
    meta_table = doc.add_table(rows=5, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False
    set_table_borders(meta_table, "CBD5E1")

    metadata = [
        ("Course & Degree:", "Big Data Systems (CS/DS) — Bachelor of Science in Data Science (BSDS)"),
        ("Academic Institution:", "Department of Data Science / Computing"),
        ("Engineering Domain:", "Distributed Systems, Object Storage, Stream Ingestion & Lakehouse Analytics"),
        ("Document Classification:", "Formal Term Project Initiation Document (PID)"),
        ("Submission Date:", "November 2026")
    ]

    for idx, (label, val) in enumerate(metadata):
        row = meta_table.rows[idx]
        
        c0 = row.cells[0]
        c0.width = Inches(2.1)
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(2)
        r0 = p0.add_run(label)
        r0.font.name = 'Arial'
        r0.font.size = Pt(9.5)
        r0.font.bold = True
        r0.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
        set_cell_background(c0, "F1F5F9")
        set_cell_margins(c0, top=70, bottom=70, left=120, right=120)

        c1 = row.cells[1]
        c1.width = Inches(4.6)
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(val)
        r1.font.size = Pt(9.5)
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c1, top=70, bottom=70, left=120, right=120)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Team Roster Table
    p_roster = doc.add_paragraph()
    p_roster.paragraph_format.space_before = Pt(8)
    p_roster.paragraph_format.space_after = Pt(4)
    r_rh = p_roster.add_run("Project Team & Assigned Engineering Responsibilities")
    r_rh.font.name = 'Arial'
    r_rh.font.size = Pt(12)
    r_rh.font.bold = True
    r_rh.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    team_table = doc.add_table(rows=4, cols=4)
    team_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    team_table.autofit = False
    set_table_borders(team_table, "CBD5E1")

    t_hdrs = ["Sr.", "Member Name", "Roll Number", "Primary Assigned Technical Responsibilities"]
    t_widths = [Inches(0.5), Inches(1.8), Inches(1.3), Inches(3.1)]

    hdr_row = team_table.rows[0]
    for idx, name in enumerate(t_hdrs):
        cell = hdr_row.cells[idx]
        cell.width = t_widths[idx]
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(name)
        r.font.name = 'Arial'
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        if idx == 0:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(cell, "0F2942")
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)

    team_data = [
        ("1", "Talha Ali Bhatti", "bsdsf23a016", "Distributed Storage Lead: MinIO S3 Object Store cluster configuration, bucket lifecycle policies, Kafka/Stream ingestion buffer, and Parquet partitioning schemes."),
        ("2", "Muhammad Abdullah", "bsdsf23a032", "Data Engineering & Analytics Lead: Distributed batch pipelines (PySpark/DuckDB), fleet-wide predictive anomaly models, and OLAP aggregation benchmarks."),
        ("3", "Abdullah", "bsdsf23a035", "Distributed Algorithms Lead: Consistent Hashing Ring engine (Virtual Nodes/Ketama), Content-Addressable Storage (CAS SHA-256) deduplication, and Bloom Filter index.")
    ]

    for r_idx, (sr, name, roll, role) in enumerate(team_data):
        row = team_table.rows[r_idx + 1]
        for c_idx, val in enumerate([sr, name, roll, role]):
            cell = row.cells[c_idx]
            cell.width = t_widths[c_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(val)
            r.font.size = Pt(9)
            if c_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if c_idx == 2:
                r.bold = True
                r.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
            bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # Section Headers Helper
    def add_h1(num, text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(f"{num}. {text}")
        r.font.name = 'Arial'
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x0F, 0x29, 0x42) # Deep Slate/Navy
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(text)
        r.font.name = 'Arial'
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x25, 0x63, 0xEB) # Accent Blue
        return p

    # 1. Background & Problem Statement
    add_h1("1", "Background & Engineering Problem Formulation")
    doc.add_paragraph(
        "Contemporary connected automotive fleets generate immense quantities of distributed telematics. Modern passenger "
        "vehicles contain over 70 Electronic Control Units (ECUs) streaming real-time sensor measurements (engine speed, thermal "
        "indices, fuel air ratios, mass airflow, and transmission statuses) alongside sporadic multimodal diagnostic events "
        "(Diagnostic Trouble Codes - DTCs, high-resolution cluster imagery, and driver symptom descriptions)."
    )
    doc.add_paragraph(
        "Traditional centralized architectures fail under this workload due to three foundational bottlenecks:\n"
        "1. Write Bottlenecks & Schema Rigidity: Relational database management systems (RDBMS) degrade severely when ingesting "
        "continuous 10 Hz - 50 Hz sensor streams across thousands of concurrent vehicles.\n"
        "2. Storage Bloat & Duplication: Maintenance portals repeatedly ingest identical multi-megabyte Original Equipment Manufacturer "
        "(OEM) service manual PDFs, wiring schematics, and common dashboard alert photographs without cryptographic deduplication.\n"
        "3. Distributed Query Inefficiencies: Row-oriented stores force full-table scans for analytical queries, creating unacceptable "
        "latencies for fleet-wide predictive maintenance and component wear analysis."
    )
    doc.add_paragraph(
        "AutoData Lake resolves these challenges by introducing a distributed, decoupled big data storage and processing pipeline "
        "specifically tailored to connected telematics."
    )

    # 2. 5 V's Analysis
    add_h1("2", "The 5 V's of Big Data in Connected Telematics")
    doc.add_paragraph(
        "The project directly addresses the five defining attributes of Big Data as established in distributed systems theory:"
    )

    table_v = doc.add_table(rows=6, cols=3)
    table_v.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_v.autofit = False
    set_table_borders(table_v, "CBD5E1")

    v_hdrs = ["Dimension", "Workload Manifestation in Connected Vehicles", "Architectural Solution in AutoData Lake"]
    v_widths = [Inches(1.2), Inches(2.7), Inches(2.8)]

    hdr_v_row = table_v.rows[0]
    for idx, name in enumerate(v_hdrs):
        cell = hdr_v_row.cells[idx]
        cell.width = v_widths[idx]
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(name)
        r.font.name = 'Arial'
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_background(cell, "0F2942")
        set_cell_margins(cell, top=70, bottom=70, left=90, right=90)

    v_rows = [
        ("Volume", "10,000+ simulated vehicles emitting ~50 MB of raw telemetry daily, accompanied by 20+ GB of unstructured OEM service manuals and diagnostic damage photographs.", "Distributed Object Storage (MinIO) decoupled from compute; storage compression via columnar Apache Parquet format."),
        ("Velocity", "Continuous CAN-bus & OBD-II sensor streams arriving at 10 Hz to 50 Hz per connected vehicle requiring sub-second safety triage.", "Asynchronous Dual-Speed Ingestion (Speed Buffer) utilizing sliding-window micro-batching before disk commit."),
        ("Variety", "Structured telemetry (Parquet), Unstructured binary media (PDF manuals, high-res damage PNG/JPEG), and Semi-structured logs (DTC codes, Urdu/Roman Urdu driver notes).", "Unified Multi-Modal Lakehouse storing structured time-series and unstructured binary blobs with unified metadata catalogs."),
        ("Veracity", "Packet dropouts, sensor noise, corrupted telemetry frames, and redundant manual uploads across owners.", "SHA-256 cryptographic verification for Content-Addressable Storage (CAS) and schema enforcement pipelines."),
        ("Value", "Transforming raw sensor streams into real-time driver safety triage, fleet predictive failure warning, and localized Pakistani market repair cost benchmarks.", "Distributed OLAP analytics (DuckDB/PySpark) driving component longevity models and workshop price protection.")
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
                r.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
            bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=90, right=90)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 3. Core Big Data Theoretical Concepts
    add_h1("3", "Core Big Data & Distributed Systems Foundations")
    doc.add_paragraph(
        "To ensure uncompromising academic rigor, the architecture implements foundational distributed systems algorithms "
        "and data engineering schemes rather than superficial high-level wrappers:"
    )

    add_h2("3.1 Distributed Object Storage Architecture (MinIO / S3 API)")
    doc.add_paragraph(
        "POSIX file systems degrade when scaled to millions of files due to metadata locking and hierarchical inode constraints. "
        "AutoData Lake implements a distributed, cloud-native Object Storage layer via MinIO. All unstructured assets "
        "(manuals, cluster scan photos, and raw telemetry bundles) are treated as immutable binary objects referenced by URI keys. "
        "The lakehouse establishes Hive-style partitioning schemes:\n"
        "s3://autodata-lake/telemetry/year=2026/make=toyota/model=corolla/vin={VIN}/partition_{ID}.parquet\n"
        "This facilitates lifecycle tiering, automated bucket encryption, and distributed parallel reads across cluster nodes."
    )

    add_h2("3.2 Content-Addressable Storage (CAS) & Cryptographic Deduplication")
    doc.add_paragraph(
        "In enterprise automotive operations, identical documents (such as official 60MB Toyota Corolla Electrical Wiring manuals "
        "or recurring instrument cluster DTC photos) are uploaded thousands of times across independent repair workflows. "
        "AutoData Lake implements a Content-Addressable Storage (CAS) engine. Every incoming payload F is digested using SHA-256: "
        "Digest = SHA256(F). The file is stored indexed strictly by its cryptographic hash. If a duplicate hash is detected, physical "
        "allocation is bypassed, and an atomic reference pointer is incremented. This mathematically guarantees zero redundant storage "
        "for duplicate files, reducing unstructured disk overhead by an estimated 40%–60%."
    )

    add_h2("3.3 Distributed Partitioning via Consistent Hashing (Ketama Algorithm)")
    doc.add_paragraph(
        "Naive modulo hashing (Target_Node = Hash(Key) mod N) suffers from catastrophic data invalidation: whenever a node is added "
        "or fails (N -> N +/- 1), virtually all existing keys are re-mapped, crippling network bandwidth. AutoData Lake implements a "
        "custom Consistent Hash Ring with Virtual Nodes (vnodes):"
    )
    doc.add_paragraph(
        "• Ring Topology: The keyspace spans the 32-bit unsigned integer ring [0, 2^32 - 1].\n"
        "• Virtual Node Balancing: Each physical storage node S_i is assigned V virtual replicas (e.g., V = 150) on the ring "
        "using salted hashes Hash(S_i || v), guaranteeing strict statistical uniformity and eliminating hot spots.\n"
        "• Deterministic Routing: Incoming vehicle VIN keys are hashed and mapped to the first clockwise node via binary search (bisect_right).\n"
        "• Fault-Tolerant Re-Sharding: When scaling cluster capacity, only K/N keys are transferred on average, maintaining cluster availability."
    )

    add_h2("3.4 Probabilistic Indexing via Scalable Bloom Filters")
    doc.add_paragraph(
        "To avoid costly disk reads and remote object store lookups for non-existent diagnostic trouble codes or manual citations, "
        "the ingestion layer incorporates an in-memory Bloom Filter. Using m bits and k independent hash functions (MurmurHash3), "
        "the filter checks key existence in O(k) time. Parameterized for n = 10,000 diagnostic trouble codes with a target false positive "
        "probability p < 0.01, the system achieves zero false negatives, intercepting non-existent queries before they consume storage bandwidth."
    )

    add_h2("3.5 Columnar Lakehouse Storage (Apache Parquet & Snappy Compression)")
    doc.add_paragraph(
        "High-velocity telemetry streams are transformed from row-oriented JSON into columnar Apache Parquet. "
        "Columnar organization allows analytical queries (e.g., average engine temperature over 1,000,000 records) to read only "
        "the relevant column chunks from disk, skipping irrelevant attributes. Combined with Run-Length Encoding (RLE), dictionary "
        "encoding, and Snappy compression, this yields a 70%+ reduction in storage footprint compared to uncompressed JSON."
    )

    add_h2("3.6 Dual-Speed Ingestion: Lambda / Kappa Architecture")
    doc.add_paragraph(
        "The architecture bifurcates data flows into two coordinated pipelines:\n"
        "• Speed Layer: Immediate real-time safety evaluation (Driveable vs. Immediate Tow Required) calculated over in-memory sliding windows.\n"
        "• Batch Layer: Periodic consolidation of streaming micro-batches into partitioned Parquet files for distributed OLAP analytics."
    )

    # 4. System Pipeline Architecture
    add_h1("4", "End-to-End System & Data Pipeline Architecture")
    doc.add_paragraph(
        "The system architecture is structured into five cohesive, decoupled tiers:"
    )
    doc.add_paragraph(
        "1. Ingestion Tier: Receives high-velocity OBD-II streams (10-50 Hz), OEM PDF manuals, and camera cluster imagery.\n"
        "2. Algorithmic Processing Tier: Executes SHA-256 CAS deduplication, Bloom Filter pre-indexing, and Consistent Hash Ring node routing.\n"
        "3. Distributed Storage Tier (MinIO S3): Stores partitioned Parquet telemetry datasets, CAS immutable objects, and image lakes.\n"
        "4. Distributed Analytics Tier (DuckDB / PySpark): Performs distributed OLAP queries, fleet-wide component wear modeling, and anomaly detection.\n"
        "5. Telemetry & Presentation Tier: Renders the Vehicle Diagnostic Cockpit alongside a real-time Evaluator Admin Dashboard displaying "
        "node ring distribution, hash collision metrics, and deduplication savings."
    )

    # 5. Technology Stack Table
    add_h1("5", "Technology Stack & Technical Justification")
    table_stack = doc.add_table(rows=6, cols=3)
    table_stack.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_stack.autofit = False
    set_table_borders(table_stack, "CBD5E1")

    s_hdrs = ["System Component", "Selected Technology", "Academic & Engineering Justification"]
    s_widths = [Inches(1.8), Inches(1.8), Inches(3.1)]

    s_hdr_row = table_stack.rows[0]
    for idx, name in enumerate(s_hdrs):
        cell = s_hdr_row.cells[idx]
        cell.width = s_widths[idx]
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(name)
        r.font.name = 'Arial'
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_background(cell, "0F2942")
        set_cell_margins(cell, top=70, bottom=70, left=90, right=90)

    stack_rows = [
        ("Distributed Object Store", "MinIO (S3-compatible API)", "Open-source, cloud-native distributed object store supporting S3 API parity, bucket lifecycle policies, and distributed node clustering."),
        ("Distributed Hashing Engine", "Python (Custom Implementation)", "First-principles implementation of ConsistentHashRing with virtual nodes, MurmurHash3, and BloomFilter to prove foundational distributed systems mastery."),
        ("Columnar Lakehouse", "Apache Parquet + Snappy", "Open-source columnar format delivering superior compression, dictionary encoding, and vector projection pushdown for analytical workloads."),
        ("Distributed Analytics", "DuckDB / PySpark, Polars", "State-of-the-art columnar analytical engines capable of running parallelized SQL and predictive anomaly models across partitioned datasets."),
        ("Ingestion API & Dashboard", "FastAPI + React 19 / Tailwind", "Asynchronous, high-throughput REST ingestion endpoints paired with an Evaluator Dashboard showing live node balance and storage telemetry.")
    ]

    for r_idx, (c0, c1, c2) in enumerate(stack_rows):
        row = table_stack.rows[r_idx + 1]
        for idx, val in enumerate([c0, c1, c2]):
            cell = row.cells[idx]
            cell.width = s_widths[idx]
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if idx == 0:
                r.bold = True
                r.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
            bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=90, right=90)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 6. Empirical Benchmarking Plan
    add_h1("6", "Empirical Evaluation & Benchmarking Methodology")
    doc.add_paragraph(
        "To provide empirical validation and eliminate reliance on subjective code assessment, the group will execute "
        "and publish five formal scientific benchmarks:"
    )
    doc.add_paragraph(
        "1. Hash Distribution Uniformity (Chi-Square Goodness-of-Fit):\n"
        "   We will evaluate key distribution across N storage nodes with virtual node counts V in {10, 50, 100, 200, 300}. "
        "   We will statistically prove that key variance across nodes approaches zero as V scales, passing the Chi-Square test for uniform distribution.\n\n"
        "2. Node Churn & Re-Sharding Overhead (K/N Theoretical Verification):\n"
        "   We will simulate dynamic node additions and evictions across 100,000 keys, measuring the exact percentage of data migrated. "
        "   We will empirically prove that our Consistent Hash Ring migrates only K/N keys compared to >90% key movement under modulo hashing.\n\n"
        "3. Storage Deduplication Efficiency Ratio:\n"
        "   We will benchmark total physical bytes consumed with vs. without Content-Addressable Storage (CAS SHA-256) across a corpus of "
        "   redundant vehicle service manuals and diagnostic photos.\n\n"
        "4. Analytical Query Performance: Row vs. Columnar Lakehouse:\n"
        "   We will execute standardized analytical aggregations (e.g., fleet-wide average engine RPM and coolant temperature) across "
        "   1,000,000 records, comparing query latency and disk I/O between SQLite/PostgreSQL and Apache Parquet.\n\n"
        "5. Bloom Filter False-Positive Verification:\n"
        "   We will experimentally measure false-positive rates across 25,000 lookups and compare the observed curve against theoretical bounds."
    )

    # 7. Timeline & Milestones Table
    add_h1("7", "Project Timeline & 12-Week Sprint Roadmap")
    table_ms = doc.add_table(rows=7, cols=4)
    table_ms.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_ms.autofit = False
    set_table_borders(table_ms, "CBD5E1")

    ms_hdrs = ["Sprint", "Timeline", "Core Scope & Deliverables", "Technical Owner"]
    ms_widths = [Inches(0.9), Inches(1.1), Inches(3.2), Inches(1.5)]

    ms_hdr_row = table_ms.rows[0]
    for idx, name in enumerate(ms_hdrs):
        cell = ms_hdr_row.cells[idx]
        cell.width = ms_widths[idx]
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(name)
        r.font.name = 'Arial'
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        if idx == 0:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(cell, "0F2942")
        set_cell_margins(cell, top=70, bottom=70, left=90, right=90)

    ms_rows = [
        ("M1", "Weeks 1-2", "Project Initiation Document (PID) formalization, architecture blueprint, and containerized MinIO distributed object storage setup.", "All Members"),
        ("M2", "Weeks 3-4", "Core distributed algorithm implementation: ConsistentHashRing with virtual nodes, SHA-256 CAS deduplicator, and Bloom Filter engine.", "Abdullah (035)"),
        ("M3", "Weeks 5-6", "High-frequency OBD-II stream generator (10-50 Hz), Apache Parquet lakehouse schema, and MinIO bucket lifecycle policies.", "Talha Ali Bhatti (016)"),
        ("M4", "Weeks 7-8", "Distributed analytics pipeline (PySpark/DuckDB), fleet-wide predictive anomaly models, and OLAP aggregations.", "Muhammad Abdullah (032)"),
        ("M5", "Weeks 9-10", "System integration with vehicle diagnostic API, Evaluator Admin Dashboard (node ring monitor), and initial benchmark data runs.", "All Members"),
        ("M6", "Weeks 11-12", "Benchmarking experiments execution, final scientific report writing, code profiling, and term project presentation defense.", "All Members")
    ]

    for r_idx, (m0, m1, m2, m3) in enumerate(ms_rows):
        row = table_ms.rows[r_idx + 1]
        for c_idx, val in enumerate([m0, m1, m2, m3]):
            cell = row.cells[c_idx]
            cell.width = ms_widths[c_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if c_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r.bold = True
            bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=90, right=90)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 8. RACI Matrix Table
    add_h1("8", "RACI Responsibility Assignment Matrix")
    doc.add_paragraph(
        "To guarantee transparent individual accountability, technical tasks are governed by the following RACI matrix "
        "(A = Accountable / Technical Lead, R = Responsible / Contributor, C = Consulted, I = Informed):"
    )

    table_raci = doc.add_table(rows=11, cols=4)
    table_raci.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_raci.autofit = False
    set_table_borders(table_raci, "CBD5E1")

    raci_hdrs = ["Technical Task / Deliverable", "Talha Ali Bhatti (016)", "Muhammad Abdullah (032)", "Abdullah (035)"]
    raci_widths = [Inches(3.4), Inches(1.1), Inches(1.1), Inches(1.1)]

    raci_hdr_row = table_raci.rows[0]
    for idx, name in enumerate(raci_hdrs):
        cell = raci_hdr_row.cells[idx]
        cell.width = raci_widths[idx]
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(name)
        r.font.name = 'Arial'
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        if idx > 0:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(cell, "0F2942")
        set_cell_margins(cell, top=70, bottom=70, left=90, right=90)

    raci_rows = [
        ("Distributed Object Store Configuration (MinIO S3)", "Accountable (A)", "Informed (I)", "Consulted (C)"),
        ("Consistent Hashing Ring & Virtual Nodes Engine", "Consulted (C)", "Informed (I)", "Accountable (A)"),
        ("Content-Addressable Storage (CAS SHA-256) Engine", "Informed (I)", "Consulted (C)", "Accountable (A)"),
        ("Scalable In-Memory Bloom Filter Lookup Engine", "Informed (I)", "Consulted (C)", "Accountable (A)"),
        ("High-Frequency Stream Ingestion Buffer & Telemetry Generator", "Accountable (A)", "Consulted (C)", "Informed (I)"),
        ("Apache Parquet Columnar Lakehouse & Partitioning", "Accountable (A)", "Consulted (C)", "Consulted (C)"),
        ("Distributed Fleet Analytics Pipeline (PySpark/DuckDB)", "Consulted (C)", "Accountable (A)", "Informed (I)"),
        ("Fleet Anomaly Detection & Predictive Maintenance Models", "Informed (I)", "Accountable (A)", "Consulted (C)"),
        ("Empirical Benchmarking Execution & Chi-Square Analysis", "Consulted (C)", "Accountable (A)", "Consulted (C)"),
        ("Final Documentation, Scientific Report & Presentation Deck", "Responsible (R)", "Responsible (R)", "Responsible (R)")
    ]

    for r_idx, row_vals in enumerate(raci_rows):
        row = table_raci.rows[r_idx + 1]
        for c_idx, val in enumerate(row_vals):
            cell = row.cells[c_idx]
            cell.width = raci_widths[c_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(val)
            r.font.size = Pt(8)
            if c_idx > 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if "Accountable" in val:
                    r.bold = True
                    r.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
            bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=50, bottom=50, left=90, right=90)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 9. Academic Significance
    add_h1("9", "Academic Significance & Evaluation Defensibility")
    doc.add_paragraph(
        "By delivering AutoData Lake, the group establishes a rigorous, production-grade distributed Big Data project that "
        "directly satisfies academic evaluation criteria:\n"
        "1. Foundational Systems Engineering: Rather than consuming generic external AI wrappers, the group implements core "
        "distributed data structures (Consistent Hashing Ring, In-Memory Bloom Filters, CAS Deduplication) from first principles.\n"
        "2. Scientific Benchmarking: The final submission provides verifiable, reproducible empirical data proving theoretical "
        "bounds on key distribution uniformity, node churn re-sharding overhead, and storage reduction.\n"
        "3. High Domain Relevance: The architecture reflects contemporary telematics infrastructures used by industrial leaders "
        "(e.g., Tesla Fleet Learning, Rivian Cloud, GM OnStar), ensuring tangible professional and academic significance."
    )

    # Sign-off Block
    p_sign = doc.add_paragraph()
    p_sign.paragraph_format.space_before = Pt(16)
    r_s = p_sign.add_run("Submitted on behalf of Group BSDS-23-AutoData:\nTalha Ali Bhatti (bsdsf23a016) • Muhammad Abdullah (bsdsf23a032) • Abdullah (bsdsf23a035)")
    r_s.font.size = Pt(9.5)
    r_s.font.italic = True
    r_s.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    doc.save(output_path)
    print(f"Refined document successfully generated at: {output_path}")

if __name__ == "__main__":
    out1 = r"C:\Users\ABDUL\.gemini\antigravity\scratch\autocare-us2\Big_Data_Project_Initiation_Document_AutoCare.docx"
    out2 = r"C:\Users\ABDUL\.gemini\antigravity\brain\00a7aa5b-5d32-449b-a3f6-925ffecf15c5\Big_Data_Project_Initiation_Document_AutoCare.docx"
    build_pid_document(out1)
    build_pid_document(out2)
