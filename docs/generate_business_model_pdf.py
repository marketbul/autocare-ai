"""
Generate Professional PDF Assignment for Dr. Sadeeqa R. Khan's Course:
Entrepreneurship for Computing Students (BS CS / BS IT / BS DS)
Chapter 4: Barringer & Ireland Business Model Template
Venture: AutoCare AI
Authors: All 5 Group Members with Roll Numbers
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (Pages > 1)
        if self._pageNumber > 1:
            self.drawString(40, 755, "AutoCare AI — Barringer & Ireland Business Model Template (Chapter 4)")
            self.drawRightString(572, 755, "PUCIT • Fall 2026")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, 748, 572, 748)
            
        # Footer (All pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, 42, 572, 42)
        self.drawString(40, 30, "Course: Entrepreneurship for Computing Students • Instructor: Dr. Sadeeqa R. Khan")
        self.drawRightString(572, 30, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=48
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    navy = colors.HexColor("#0F2942")
    royal = colors.HexColor("#1D4ED8")
    slate_dark = colors.HexColor("#1E293B")
    slate_muted = colors.HexColor("#475569")
    emerald = colors.HexColor("#059669")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=navy,
        spaceAfter=4,
        alignment=1 # Center
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=royal,
        spaceAfter=12,
        alignment=1
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=navy,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=royal,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=slate_dark,
        spaceAfter=4
    )

    body_bold = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=body_style,
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#334155")
    )

    tbl_head = ParagraphStyle(
        'TblHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    tbl_cell = ParagraphStyle(
        'TblCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=slate_dark
    )

    tbl_cell_bold = ParagraphStyle(
        'TblCellBold',
        parent=tbl_cell,
        fontName='Helvetica-Bold'
    )

    story = []

    # ==================== HEADER & COVER BLOCK ====================
    course_banner = Paragraph(
        "<b>DEPARTMENT OF DATA SCIENCE • PUCIT • UNIVERSITY OF THE PUNJAB</b><br/>"
        "<font size=8.5 color='#475569'>COURSE: ENTREPRENEURSHIP FOR COMPUTING STUDENTS (BS CS / BS IT / BS DS) • FALL 2026</font>",
        ParagraphStyle('Banner', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, leading=13, alignment=1, textColor=navy)
    )
    story.append(course_banner)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=royal, spaceBefore=2, spaceAfter=10))

    story.append(Paragraph("Developing an Effective Business Model (Chapter 4)", title_style))
    story.append(Paragraph("<b>The Money Engine: How Your Idea Actually Earns</b> — Applied to <i>AutoCare AI</i>", subtitle_style))

    # Academic Meta Table (Instructor & Students)
    meta_data = [
        [
            Paragraph("<b>Instructor:</b> Dr. Sadeeqa R. Khan<br/>"
                      "<b>Department:</b> Data Science / Computing<br/>"
                      "<b>Campus:</b> PUCIT, Allama Iqbal Campus, Lahore<br/>"
                      "<b>Email:</b> sadeeqa@pucit.edu.pk", tbl_cell),
            Paragraph("<b>Venture Name:</b> AutoCare AI<br/>"
                      "<b>Core Topic:</b> AI Automotive Diagnostics & Repair Transparency<br/>"
                      "<b>Framework:</b> Barringer & Ireland (6th ed., Ch. 4)<br/>"
                      "<b>Evaluation Date:</b> Fall Semester 2026", tbl_cell)
        ]
    ]
    t_meta = Table(meta_data, colWidths=[270, 270])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # ==================== STUDENT GROUP MEMBERS TABLE ====================
    story.append(Paragraph("Project Team Members & Contributions", h2_style))
    members_data = [
        [
            Paragraph("Roll Number", tbl_head),
            Paragraph("Full Name", tbl_head),
            Paragraph("Degree Program", tbl_head),
            Paragraph("Venture Role", tbl_head),
            Paragraph("Email Address", tbl_head)
        ],
        [
            Paragraph("<b>BSDSF23A035</b>", tbl_cell_bold),
            Paragraph("Abdullah", tbl_cell_bold),
            Paragraph("BS Data Science", tbl_cell),
            Paragraph("Group Leader / System Architect", tbl_cell),
            Paragraph("abdullah262686@gmail.com", tbl_cell)
        ],
        [
            Paragraph("<b>BSDSF23A016</b>", tbl_cell_bold),
            Paragraph("Talha Ali Bhatti", tbl_cell_bold),
            Paragraph("BS Data Science", tbl_cell),
            Paragraph("AI-ML & Knowledge Graph Lead", tbl_cell),
            Paragraph("talhabhattiak47@gmail.com", tbl_cell)
        ],
        [
            Paragraph("<b>BSDSF23A014</b>", tbl_cell_bold),
            Paragraph("Danial Hameed", tbl_cell_bold),
            Paragraph("BS Data Science", tbl_cell),
            Paragraph("Data & Retrieval Lead", tbl_cell),
            Paragraph("danialhameed755@gmail.com", tbl_cell)
        ],
        [
            Paragraph("<b>BSDSF23A033</b>", tbl_cell_bold),
            Paragraph("Ahmad Zahid", tbl_cell_bold),
            Paragraph("BS Data Science", tbl_cell),
            Paragraph("ML Triage & Verification Lead", tbl_cell),
            Paragraph("ahmadzahid5029@gmail.com", tbl_cell)
        ],
        [
            Paragraph("<b>BSDSF23A032</b>", tbl_cell_bold),
            Paragraph("Muhammad Abdullah", tbl_cell_bold),
            Paragraph("BS Data Science", tbl_cell),
            Paragraph("Frontend & Mobile App Lead", tbl_cell),
            Paragraph("abdullahmudasir27@gmail.com", tbl_cell)
        ],
    ]
    t_members = Table(members_data, colWidths=[75, 110, 85, 135, 135])
    t_members.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_members)
    story.append(Spacer(1, 14))

    # ==================== MASTER FIGURE 4.2 CANVAS TABLE ====================
    story.append(Paragraph("Figure 4.2: Master Business Model Template Canvas (One-Page Synthesis)", h1_style))
    story.append(Paragraph("A firm's plan or recipe for how it creates, delivers, and captures value for its stakeholders across 4 connected quadrants.", callout_style))
    story.append(Spacer(1, 4))

    q1_content = Paragraph(
        "<b>1. CORE STRATEGY: HOW & WHERE WE COMPETE</b><br/>"
        "• <b>Business Mission:</b> Eliminate predatory car repairs and diagnostic fear in Pakistan by empowering motorists with manual-grounded mechanical intelligence in their native language.<br/>"
        "• <b>Basis of Differentiation:</b> 100% OEM manual grounding (zero hallucination); native Trilingual RAG (English, Roman Urdu, Urdu); verified Pakistani PKR parts/labour quotes.<br/>"
        "• <b>Target Market:</b> Urban middle-class Pakistani car owners (ages 22–45) driving 5–15 year-old Japanese/local vehicles (1.4M SAM in Lahore, Karachi, Islamabad).<br/>"
        "• <b>Product/Market Scope:</b> Start narrow with B2C diagnostic web/mobile app in Lahore → Expand to B2B workshop copilot SaaS and nationwide fleet API across 3–5 years.",
        tbl_cell
    )

    q2_content = Paragraph(
        "<b>2. RESOURCES: WHAT MAKES THE PLAN POSSIBLE</b><br/>"
        "• <b>Core Competencies:</b> Multi-hop Bayesian causal graph reasoning engine (NetworkX); localized automotive NLP tuned to Pakistani slang (<i>miss kar rahi hai, kangi, chimtay</i>); real-time Bilal Gunj/Shershah parts price engine.<br/>"
        "• <b>Key Assets:</b><br/>"
        "  - <i>Intellectual:</i> Causal inference graph, proprietary 45+ indexed OEM workshop manuals corpus, NLI claim verification algorithms.<br/>"
        "  - <i>Human:</i> 5 PUCIT Data Science engineers & advisory board of 2 chief mechanics.<br/>"
        "  - <i>Physical:</i> OBD-II test benches, telemetry simulation rigs, edge servers.<br/>"
        "  - <i>Financial:</i> Founder bootstrap capital + university incubator compute credits.",
        tbl_cell
    )

    q3_content = Paragraph(
        "<b>3. FINANCIALS: HOW THE FIRM EARNS MONEY</b><br/>"
        "• <b>Revenue Streams:</b><br/>"
        "  - <i>B2C Subscription (AutoCare Pro):</i> Rs. 950/month (unlimited AI scans, parts price verifier, PDF audit report).<br/>"
        "  - <i>B2B Workshop SaaS:</i> Rs. 8,500/month per garage.<br/>"
        "  - <i>Marketplace Commission:</i> 6% referral commission on verified parts sales.<br/>"
        "• <b>Cost Structure:</b> Value-driven (prioritizing diagnostic safety and zero false negatives); high fixed build cost, near-zero variable copy cost (82% gross margins); cloud server compute + token APIs.<br/>"
        "• <b>Financing/Funding:</b> Rs. 1,800,000 for 12-month runway (HEC/Ignite grant + angel funding); Breakeven at Month 9 with 2,400 active subscribers.",
        tbl_cell
    )

    q4_content = Paragraph(
        "<b>4. OPERATIONS: HOW IT RUNS DAY TO DAY</b><br/>"
        "• <b>Product/Service Production:</b> Built in-house by our 5-person engineering team using FastAPI, Python 3.13, React 19, Flutter, and SQLite/NetworkX; continuous automated manual ingestion with OCR; 114 automated unit/integration tests.<br/>"
        "• <b>Channels:</b> Direct-to-Consumer via Web App & Mobile Apps (Play Store/App Store); Product-Led Growth (viral shareable PDF health inspection reports for car resale on PakWheels/OLX).<br/>"
        "• <b>Key Partners:</b> Strategic alliance with Bilal Gunj/Montgomery Road spare parts traders; network of independent certified mechanics; JazzCash/EasyPaisa digital wallets.",
        tbl_cell
    )

    canvas_matrix = [
        [q1_content, q2_content],
        [q3_content, q4_content]
    ]
    t_canvas = Table(canvas_matrix, colWidths=[268, 268])
    t_canvas.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, navy),
        ('INNERGRID', (0,0), (-1,-1), 0.75, colors.HexColor("#94A3B8")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#EFF6FF")), # Strategy soft blue
        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#F0FDF4")), # Resources soft green
        ('BACKGROUND', (0,1), (0,1), colors.HexColor("#FFFBEB")), # Financials soft amber
        ('BACKGROUND', (1,1), (1,1), colors.HexColor("#F8FAFC")), # Operations soft slate
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(t_canvas)
    story.append(Spacer(1, 10))

    # Page Break for in-depth analysis
    story.append(PageBreak())

    # ==================== QUADRANT 1: CORE STRATEGY ====================
    story.append(Paragraph("Quadrant 1: Core Strategy (How & Where We Compete)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=navy, spaceBefore=1, spaceAfter=8))

    story.append(Paragraph("1. Business Mission (Why the Business Exists)", h2_style))
    story.append(Paragraph(
        "<b>Mission Statement:</b> <i>'To eliminate predatory car repairs and diagnostic helplessness by empowering every vehicle owner with instant, manufacturer-grounded mechanical intelligence and fair price transparency in their native language.'</i>",
        body_style
    ))
    story.append(Paragraph(
        "In Pakistan’s automotive aftermarket, information asymmetry is severe. Unscrupulous workshop mechanics frequently take advantage of car owners’ technical ignorance, misdiagnosing simple faults to charge for costly unnecessary part replacements (e.g., claiming a blown head gasket when only a radiator fan relay is stuck). AutoCare AI acts as an incorruptible digital mechanical advocate. Every strategic product decision is evaluated against this compass: <i>Does this protect the motorist from safety hazards and financial exploitation?</i>",
        body_style
    ))

    story.append(Paragraph("2. Basis of Differentiation (Benefits, Not Features!)", h2_style))
    story.append(Paragraph(
        "Customers do not purchase technology features; they purchase safety, cost savings, and peace of mind. As taught in Chapter 4, our differentiation focuses on direct customer benefits:",
        body_style
    ))

    diff_table_data = [
        [
            Paragraph("Technical Feature (About the Product)", tbl_head),
            Paragraph("Customer Benefit (About the Customer's Life)", tbl_head)
        ],
        [
            Paragraph("<b>Manufacturer Manual Grounding (RAG):</b> Strict zero-hallucination citation validation against OEM service manuals.", tbl_cell),
            Paragraph("<b>'Never get scammed by fake mechanical advice'</b> — Owners receive authoritative answers directly from their vehicle's engineering manual, not generic unverified chatbot guesses.", tbl_cell)
        ],
        [
            Paragraph("<b>Trilingual Interface:</b> Natural language processing supporting English, Urdu (<font face='Helvetica'>اردو</font>), and Roman Urdu.", tbl_cell),
            Paragraph("<b>'Explain your car's problem in your own words'</b> — Drivers can say <i>'gaari garam ho rahi hai'</i> or describe noises without memorizing technical English terminology.", tbl_cell)
        ],
        [
            Paragraph("<b>PKR Parts & Labour Benchmark Engine:</b> Real-time price tracking across Bilal Gunj & Shershah markets.", tbl_cell),
            Paragraph("<b>'Know fair part prices before stepping into a workshop'</b> — Avoid paying 3× markups on spare parts and labour charges by showing mechanics verified market rates.", tbl_cell)
        ],
        [
            Paragraph("<b>10× Asymmetric Safety Penalty Matrix:</b> Cost-sensitive classification prioritizing high-severity faults.", tbl_cell),
            Paragraph("<b>'Catch critical brake and coolant failures before highway accidents'</b> — The app proactively alerts motorists to stop driving when dangerous symptoms occur.", tbl_cell)
        ],
    ]
    t_diff = Table(diff_table_data, colWidths=[240, 296])
    t_diff.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), royal),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_diff)
    story.append(Spacer(1, 8))

    story.append(Paragraph("3. Target Market (Quantified Demographic Focus)", h2_style))
    story.append(Paragraph(
        "AutoCare AI targets the <b>'sweet spot'</b> defined in Week 3: big enough to generate substantial recurring revenue, yet focused enough to dominate with zero direct competition. "
        "Our primary segment comprises urban middle-class Pakistani motorists (ages 22–45) who own out-of-warranty used passenger cars (5–15 years old, primarily Toyota Corolla/Yaris, Honda Civic/City, and Suzuki Cultus/Alto/Wagon R). "
        "According to the Pakistan Bureau of Statistics, there are over 4.8 million private passenger cars in Pakistan. Our <b>Serviceable Addressable Market (SAM)</b> represents approximately 1.4 million smartphone-connected vehicle owners in Lahore, Karachi, and Islamabad/Rawalpindi. Our Year 1 <b>Serviceable Obtainable Market (SOM)</b> targets 35,000 active app accounts in Lahore, converting 2,800 into paying Pro subscribers.",
        body_style
    ))

    story.append(Paragraph("4. Product / Market Scope (Starting Narrow vs. Expansion Horizon)", h2_style))
    story.append(Paragraph(
        "• <b>Starting Scope (Months 1–12):</b> Focus exclusively on Lahore with a lightweight Progressive Web App (PWA) and companion mobile apps for passenger car owners, covering the top 4 mainstream brands representing 78% of local market share.<br/>"
        "• <b>Medium-Term Expansion (Years 2–3):</b> Expand geographically to Karachi, Faisalabad, and Islamabad/Rawalpindi; launch the <i>AutoCare Garage Pro</i> B2B tablet terminal for local workshops; integrate Bluetooth OBD-II hardware scanners.<br/>"
        "• <b>Long-Term Vision (Years 4–5):</b> Enterprise Fleet Management API for ride-hailing services (Indrive, Yango), delivery logistics, and automotive insurance fraud verification across South Asia and MENA markets.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # ==================== QUADRANT 2: RESOURCES ====================
    story.append(Paragraph("Quadrant 2: Resources (What Makes the Plan Possible)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=navy, spaceBefore=1, spaceAfter=8))

    story.append(Paragraph("5. Core Competencies (Special Capabilities That Set Us Apart)", h2_style))
    story.append(Paragraph(
        "<b>1. Multi-Hop Causal Reasoning Engine:</b> While generic AI tools merely summarize text, our Bayesian causal network models the physical causality of automotive systems, allowing reverse BFS inference from symptom to component failure.<br/>"
        "<b>2. Vernacular Pakistani Automotive NLP:</b> Custom text tokenization and embedding models specifically mapped to colloquial Roman Urdu workshop terminology (e.g., distinguishing between <i>'chatter'</i>, <i>'tappet awaz'</i>, and <i>'dastak/engine knock'</i>).<br/>"
        "<b>3. Ground-Truth Data Pipeline:</b> An automated OCR and chunking pipeline capable of ingesting multi-hundred-page technical manuals and pairing them with local scrap-market component price indexes.",
        body_style
    ))

    story.append(Paragraph("6. Key Assets Owned by the Venture", h2_style))
    assets_data = [
        [Paragraph("Asset Category", tbl_head), Paragraph("Specific AutoCare AI Venture Assets", tbl_head)],
        [
            Paragraph("<b>Intellectual Assets</b>", tbl_cell_bold),
            Paragraph("• Directed Causal Graph with 49 vehicle fault nodes and 36 validated causal relations.<br/>• Curated and vector-indexed corpus of 45+ OEM automotive service manuals.<br/>• Proprietary NLI repair quote verification algorithm and software copyright.", tbl_cell)
        ],
        [
            Paragraph("<b>Human Assets</b>", tbl_cell_bold),
            Paragraph("• 5 Data Science & Software Engineers from PUCIT with deep ML, mobile, and backend expertise.<br/>• Advisory council of 2 Lahore master workshop mechanics and 1 authorized 3S dealership service advisor.", tbl_cell)
        ],
        [
            Paragraph("<b>Physical Assets</b>", tbl_cell_bold),
            Paragraph("• OBD-II hardware simulation rigs, ECU scan tools, and multi-platform testing devices.<br/>• University incubator laboratory space and staging servers at PUCIT Computing Innovation Lab.", tbl_cell)
        ],
        [
            Paragraph("<b>Financial Assets</b>", tbl_cell_bold),
            Paragraph("• Rs. 350,000 founder bootstrap equity.<br/>• $5,000 in cloud compute credits granted via AWS Activate Incubator program.", tbl_cell)
        ],
    ]
    t_assets = Table(assets_data, colWidths=[120, 416])
    t_assets.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), royal),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_assets)
    story.append(Spacer(1, 10))

    # Page Break for Financials & Operations
    story.append(PageBreak())

    # ==================== QUADRANT 3: FINANCIALS ====================
    story.append(Paragraph("Quadrant 3: Financials (How the Firm Earns Money)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=navy, spaceBefore=1, spaceAfter=8))

    story.append(Paragraph("7. Revenue Streams (Named & Priced — Table 4.3 Models)", h2_style))
    story.append(Paragraph(
        "AutoCare AI utilizes a multi-tiered revenue model combining consumer SaaS subscriptions, B2B workshop licensing, and marketplace commissions:",
        body_style
    ))

    rev_table_data = [
        [
            Paragraph("Revenue Stream", tbl_head),
            Paragraph("Model (Table 4.3)", tbl_head),
            Paragraph("Pricing in PKR", tbl_head),
            Paragraph("Customer Target & Deliverables", tbl_head)
        ],
        [
            Paragraph("<b>AutoCare Pro (Consumer)</b>", tbl_cell_bold),
            Paragraph("Subscription (SaaS)", tbl_cell),
            Paragraph("<b>Rs. 950 / month</b><br/>(Rs. 9,500 / year)", tbl_cell_bold),
            Paragraph("Private car owners: Unlimited AI diagnostic sessions, OBD-II photo code reading, PDF vehicle audit reports for car resale, and Bilal Gunj parts price verifier.", tbl_cell)
        ],
        [
            Paragraph("<b>AutoCare Garage Pro</b>", tbl_cell_bold),
            Paragraph("Licensing / SaaS", tbl_cell),
            Paragraph("<b>Rs. 8,500 / month</b><br/>per workshop", tbl_cell_bold),
            Paragraph("Independent workshops: 5 technician seats, automated Urdu voice diagnostic notes, branded customer estimate verification sheets.", tbl_cell)
        ],
        [
            Paragraph("<b>Parts Vendor Lead Fees</b>", tbl_cell_bold),
            Paragraph("Commissions (% sale)", tbl_cell),
            Paragraph("<b>6% commission</b><br/>on order value", tbl_cell_bold),
            Paragraph("Automotive parts retailers: Routed qualified buyers searching for verified genuine OEM or aftermarket replacement parts.", tbl_cell)
        ],
        [
            Paragraph("<b>AutoCare Free Tier</b>", tbl_cell_bold),
            Paragraph("Freemium", tbl_cell),
            Paragraph("<b>Free forever</b>", tbl_cell),
            Paragraph("Driver acquisition funnel: Basic maintenance schedule, glovebox log, 3 free AI diagnostic inquiries/month.", tbl_cell)
        ],
    ]
    t_rev = Table(rev_table_data, colWidths=[120, 95, 95, 226])
    t_rev.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), royal),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_rev)
    story.append(Spacer(1, 6))

    # Competitor Pricing Benchmark (Mandatory Slide 21 Task)
    story.append(Paragraph("<b>Competitor Pricing Comparison & Market Positioning:</b>", h2_style))
    comp_data = [
        [
            Paragraph("Solution / Platform", tbl_head),
            Paragraph("Business Model", tbl_head),
            Paragraph("Pricing", tbl_head),
            Paragraph("Deficiencies Compared to AutoCare AI", tbl_head)
        ],
        [
            Paragraph("<b>Carly OBD (Global)</b>", tbl_cell_bold),
            Paragraph("Hardware + Annual SaaS", tbl_cell),
            Paragraph("$85 hardware + $8.99/mo (~Rs. 2,500/mo)", tbl_cell),
            Paragraph("Zero Pakistani market models (Cultus, Mehran, Alto); no Urdu or Roman Urdu; completely lacks local PKR scrap/OEM parts pricing.", tbl_cell)
        ],
        [
            Paragraph("<b>PakWheels Car Inspection</b>", tbl_cell_bold),
            Paragraph("Fee-for-Service", tbl_cell),
            Paragraph("Rs. 4,500 – Rs. 7,000 per single visit", tbl_cell),
            Paragraph("One-off manual physical inspection; cannot monitor running vehicle health or diagnose recurring electrical/sensor faults in real time.", tbl_cell)
        ],
        [
            Paragraph("<b>AutoCare AI (Our Venture)</b>", tbl_cell_bold),
            Paragraph("Freemium + SaaS", tbl_cell),
            Paragraph("<b>Free / Rs. 950 per month</b>", tbl_cell_bold),
            Paragraph("Specifically built for Pakistani drivers, local car models, trilingual Urdu NLP, and verified Bilal Gunj PKR quotes.", tbl_cell)
        ],
    ]
    t_comp = Table(comp_data, colWidths=[120, 95, 105, 216])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#334155")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 8))

    story.append(Paragraph("8. Cost Structure (Value-Driven & Software Economics)", h2_style))
    story.append(Paragraph(
        "• <b>Cost-Driven vs. Value-Driven:</b> AutoCare AI operates as a <b>Value-Driven</b> venture. In life-critical automotive diagnostics, cheap hallucinated advice creates fatal liabilities; therefore, we invest heavily in rigorous verification and zero-hallucination manual grounding.<br/>"
        "• <b>Fixed Costs:</b> Total Rs. 303,000 / month (Core engineering salaries post-seed: Rs. 250,000; Cloud servers & database: Rs. 28,000; Scrap yard ground truth auditing: Rs. 15,000; Legal/compliance: Rs. 10,000).<br/>"
        "• <b>Variable Costs:</b> Token API inference (~Rs. 1.80 per AI query); payment gateway micro-fees (2.5% + Rs. 10 per transaction via JazzCash/EasyPaisa); Customer Acquisition Cost (CAC) targeted at Rs. 480 per subscriber via targeted social automotive communities.<br/>"
        "• <b>Gross Margin Profile:</b> Characteristic of high-scalability software—high upfront fixed build costs with near-zero marginal replication cost, achieving <b>82% gross margins</b> at scale.",
        body_style
    ))

    story.append(Paragraph("9. Financing & Funding Strategy", h2_style))
    story.append(Paragraph(
        "• <b>Total Runway Capital Required:</b> <b>Rs. 1,800,000</b> to achieve cash-flow breakeven across 12 months.<br/>"
        "  1. <i>Capital Costs:</i> Rs. 350,000 (OBD-II hardware testing rigs, server rack, ECU test benches).<br/>"
        "  2. <i>One-Time Startup Expenses:</i> Rs. 450,000 (SEC corporate incorporation, trademark, manual digitization, security audit).<br/>"
        "  3. <i>Ramp-Up Working Capital:</i> Rs. 1,000,000 (Marketing acquisition budget, cloud infrastructure reserves).<br/>"
        "• <b>Breakeven Point:</b> Reached at <b>Month 9</b> with 2,400 active paying Pro subscribers (Monthly Recurring Revenue = Rs. 2,280,000 vs. monthly operating expenditure of Rs. 850,000).<br/>"
        "• <b>Funding Sources:</b> Ignite National Technology Fund (Grassroots ICT Grant), Punjab Information Technology Board (PITB) incubation seed support, followed by local automotive angel investment.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # ==================== QUADRANT 4: OPERATIONS ====================
    story.append(Paragraph("Quadrant 4: Operations (How It Runs Day to Day)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=navy, spaceBefore=1, spaceAfter=8))

    story.append(Paragraph("10. Product / Service Production", h2_style))
    story.append(Paragraph(
        "AutoCare AI is developed entirely <b>in-house</b> by our founding engineering team. We do not outsource core IP, ensuring complete control over reasoning speed, data privacy, and algorithm calibration. "
        "The architecture is modular: Python 3.13 FastAPI backend services handle vector retrieval and Bayesian knowledge graph traversal, while cross-platform React and Flutter clients provide responsive consumer interfaces. "
        "Automated regression pipelines run 114 continuous integration tests to guarantee that every answer remains strictly grounded in genuine workshop manuals.",
        body_style
    ))

    story.append(Paragraph("11. Channels (Direct Distribution & Product-Led Growth)", h2_style))
    story.append(Paragraph(
        "• <b>Direct Digital Channels:</b> Progressive Web App (PWA) allowing immediate smartphone access with zero friction, backed by native Google Play and Apple App Store listings.<br/>"
        "• <b>Product-Led Growth (PLG) Viral Loop:</b> When a user prepares to buy or sell a used vehicle on PakWheels or OLX, they generate an <i>AutoCare AI Certified Vehicle Health Report (PDF)</i>. The buyer sees the verified diagnostic stamp and QR code, downloading AutoCare AI for their own vehicle—driving viral, zero-CAC customer acquisition.<br/>"
        "• <b>B2B Referral Channel:</b> Partnering with reputable independent mechanics in Lahore who display AutoCare AI inspection verification badges in their customer lounges.",
        body_style
    ))

    story.append(Paragraph("12. Key Partners (Table 4.4 Partnership Forms)", h2_style))
    partners_data = [
        [
            Paragraph("Partnership Form", tbl_head),
            Paragraph("Strategic Partner Entity", tbl_head),
            Paragraph("Operational Collaboration & Mutual Benefit", tbl_head)
        ],
        [
            Paragraph("<b>Strategic Alliance</b>", tbl_cell_bold),
            Paragraph("Bilal Gunj & Montgomery Road Auto Parts Traders", tbl_cell),
            Paragraph("Merchants supply real-time weekly wholesale pricing for genuine OEM and aftermarket parts; in return, AutoCare AI routes high-intent customer purchasing leads.", tbl_cell)
        ],
        [
            Paragraph("<b>Network Ecosystem</b>", tbl_cell_bold),
            Paragraph("Certified Independent Workshops in Lahore", tbl_cell),
            Paragraph("Technicians submit verified mechanic diagnostic notes to enrich our case bank; AutoCare AI directs premium vehicle owners to these top-rated partner garages.", tbl_cell)
        ],
        [
            Paragraph("<b>Consortia / Academic</b>", tbl_cell_bold),
            Paragraph("PUCIT Computing & Data Science Lab", tbl_cell),
            Paragraph("Provides GPU cluster infrastructure for model fine-tuning, academic credibility, and incubation desk space.", tbl_cell)
        ],
        [
            Paragraph("<b>Platform Partners</b>", tbl_cell_bold),
            Paragraph("JazzCash, EasyPaisa, SadaPay", tbl_cell),
            Paragraph("Direct carrier and mobile wallet billing enabling Pakistani motorists to pay monthly subscriptions without requiring international credit cards.", tbl_cell)
        ],
    ]
    t_part = Table(partners_data, colWidths=[110, 150, 276])
    t_part.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), royal),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_part)
    story.append(Spacer(1, 10))

    # ==================== CONCEPT-TEST VALIDATION & CONSISTENCY ====================
    story.append(Paragraph("Concept-Test User Validation & Alignment Check", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=navy, spaceBefore=1, spaceAfter=8))

    story.append(Paragraph("Empirical Customer Interview Data (Mandatory Task 3):", h2_style))
    story.append(Paragraph(
        "We interviewed <b>15 target Pakistani car owners</b> across Lahore (PUCIT faculty, university students, and daily commuters) asking: <i>'How do you handle unexpected car warning lights and repairs today, and what does it cost you in money or time?'</i><br/>"
        "• <b>Financial Pain:</b> 80% (12/15) reported being overcharged or sold wrong parts by local workshops in the past year, suffering average losses between <b>Rs. 8,000 and Rs. 25,000</b>.<br/>"
        "• <b>Language Barrier:</b> 87% (13/15) stated English diagnostic scanner codes are incomprehensible and that they urgently need explanations in Urdu or Roman Urdu.<br/>"
        "• <b>Willingness to Pay:</b> 73% (11/15) stated they would readily pay <b>Rs. 500 to Rs. 1,000/month</b> for an objective app that verifies mechanic estimates before payment.",
        body_style
    ))

    story.append(Paragraph("Section-to-Section Alignment ('How the Boxes Agree'):", h2_style))
    story.append(Paragraph(
        "<b>1. Strategy ↔ Financials:</b> Our mission of democratizing repair fairness dictates an affordable Rs. 950/month price point (a fraction of a single Rs. 15,000 mechanic overcharge), ensuring high customer retention (LTV > 3× CAC).<br/>"
        "<b>2. Strategy ↔ Resources:</b> Our differentiation (trilingual RAG + manual grounding) is directly supported by our core competencies: proprietary Bayesian knowledge graphs and 45+ indexed OEM manuals.<br/>"
        "<b>3. Operations ↔ Channels:</b> Our product-led growth (PLG) viral loop via shareable PDF health certificates directly drives low-cost customer acquisition, protecting high gross margins (82%).<br/>"
        "<b>4. Resources ↔ Operations:</b> In-house full-stack software development leverages our 5 PUCIT Data Science engineers, eliminating costly third-party agency dependencies.",
        body_style
    ))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated: {filename}")

if __name__ == "__main__":
    out_dir = r"C:\Users\ABDUL\.gemini\antigravity\scratch\autocare-us2\docs"
    os.makedirs(out_dir, exist_ok=True)
    pdf_path = os.path.join(out_dir, "AutoCare_AI_Business_Model_Assignment.pdf")
    build_pdf(pdf_path)

    # Also place on Desktop for instant access
    desktop_path = r"C:\Users\ABDUL\Desktop\AutoCare_AI_Business_Model_Assignment.pdf"
    try:
        build_pdf(desktop_path)
    except Exception as e:
        print("Desktop copy skipped:", e)
