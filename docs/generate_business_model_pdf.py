# -*- coding: utf-8 -*-
"""
AutoCare AI - Barringer & Ireland Business Model Assignment PDF Generator
PUCIT - Entrepreneurship for Computing Students (Dr. Sadeeqa R. Khan)
Simple, clean, professional, exactly 3 pages, zero encoding errors.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for professional 'Page X of Y' footers."""
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
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(36, 756, "AutoCare AI - Barringer & Ireland Business Model (PUCIT / Dr. Sadeeqa R. Khan)")
            self.drawRightString(576, 756, "Fall 2026 | Chapter 4")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, 750, 576, 750)

        # Running footer
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(576, 24, page_str)
        self.drawString(36, 24, "Department of Data Science, PUCIT, University of the Punjab - Academic Submission")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 34, 576, 34)
        self.restoreState()


def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=38,
        bottomMargin=38
    )

    styles = getSampleStyleSheet()

    # Color Palette: Modern Academic / Corporate Navy
    c_brand = colors.HexColor("#1E3A8A")      # Blue 900
    c_accent = colors.HexColor("#2563EB")     # Blue 600
    c_bg_light = colors.HexColor("#F8FAFC")   # Slate 50
    c_border = colors.HexColor("#CBD5E1")     # Slate 300
    c_text = colors.HexColor("#1E293B")       # Slate 800
    c_muted = colors.HexColor("#64748B")      # Slate 500

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=c_brand,
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=12,
        textColor=c_muted,
        spaceAfter=6
    )

    sec_head = ParagraphStyle(
        'SecHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=c_brand,
        spaceBefore=4,
        spaceAfter=3,
        keepWithNext=True
    )

    sub_sec_head = ParagraphStyle(
        'SubSecHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=c_accent,
        spaceBefore=3,
        spaceAfter=2,
        keepWithNext=True
    )

    body_text = ParagraphStyle(
        'BodyTxt',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=c_text
    )

    bullet_text = ParagraphStyle(
        'BulTxt',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.6,
        leading=10.2,
        textColor=c_text,
        leftIndent=8,
        firstLineIndent=-8,
        spaceAfter=1.5
    )

    quad_hdr = ParagraphStyle(
        'QuadHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=0
    )

    quad_content = ParagraphStyle(
        'QuadCont',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.8,
        textColor=c_text
    )

    tbl_th = ParagraphStyle(
        'TblTH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=1
    )

    tbl_td = ParagraphStyle(
        'TblTD',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.2,
        textColor=c_text
    )

    tbl_td_bold = ParagraphStyle(
        'TblTDBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9.2,
        textColor=c_text
    )

    tbl_td_center = ParagraphStyle(
        'TblTDCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.2,
        textColor=c_text,
        alignment=1
    )

    callout_txt = ParagraphStyle(
        'CalloutTxt',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=10,
        textColor=c_brand
    )

    story = []

    # =========================================================================
    # PAGE 1: TITLE, ACADEMIC META, VERIFIED ROSTER & FIGURE 4.2 CANVAS MATRIX
    # =========================================================================
    story.append(Paragraph("Barringer & Ireland Business Model Assignment (Chapter 4)", title_style))
    story.append(Paragraph("<b>Venture: AutoCare AI</b> - Intelligent Automotive Diagnostics & Telemetry Platform", subtitle_style))

    # Meta Table
    meta_cells = [
        [
            Paragraph("<b>Course:</b> Entrepreneurship for Computing Students (BS CS / IT / DS)<br/>"
                      "<b>Instructor:</b> Dr. Sadeeqa R. Khan (PUCIT, Lahore)<br/>"
                      "<b>Textbook:</b> Barringer & Ireland (6th ed.), Chapter 4", body_text),
            Paragraph("<b>Institution:</b> Punjab University College of Information Technology<br/>"
                      "<b>Semester:</b> Fall 2026 | Milestone: Business Model Template<br/>"
                      "<b>Rubric:</b> Completeness, Consistency, Originality, Presentation", body_text)
        ]
    ]
    t_meta = Table(meta_cells, colWidths=[270, 270])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
        ('BOX', (0,0), (-1,-1), 0.5, c_border),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 4))

    # Team Members Table
    team_cells = [
        [
            Paragraph("Roll Number", tbl_th),
            Paragraph("Student Name", tbl_th),
            Paragraph("Degree Program", tbl_th),
            Paragraph("Assigned Project Role", tbl_th),
            Paragraph("Institutional Email", tbl_th)
        ],
        [
            Paragraph("<b>BSDSF23A035</b>", tbl_td_center),
            Paragraph("<b>Abdullah</b>", tbl_td_bold),
            Paragraph("BS Data Science", tbl_td_center),
            Paragraph("Group Leader & System Architect", tbl_td),
            Paragraph("abdullah262686@gmail.com", tbl_td)
        ],
        [
            Paragraph("<b>BSDSF23A032</b>", tbl_td_center),
            Paragraph("<b>Muhammad Abdullah</b>", tbl_td_bold),
            Paragraph("BS Data Science", tbl_td_center),
            Paragraph("Frontend & Mobile App Lead", tbl_td),
            Paragraph("abdullahmudasir27@gmail.com", tbl_td)
        ],
        [
            Paragraph("<b>BSDSF23A016</b>", tbl_td_center),
            Paragraph("<b>Talha Ali Bhatti</b>", tbl_td_bold),
            Paragraph("BS Data Science", tbl_td_center),
            Paragraph("AI-ML & Knowledge Graph Lead", tbl_td),
            Paragraph("talhabhattiak47@gmail.com", tbl_td)
        ],
        [
            Paragraph("<b>BSDSF23A014</b>", tbl_td_center),
            Paragraph("<b>Danial Hameed</b>", tbl_td_bold),
            Paragraph("BS Data Science", tbl_td_center),
            Paragraph("Data & Retrieval Lead", tbl_td),
            Paragraph("danialhameed755@gmail.com", tbl_td)
        ],
        [
            Paragraph("<b>BSDSF23A033</b>", tbl_td_center),
            Paragraph("<b>Ahmad Zahid</b>", tbl_td_bold),
            Paragraph("BS Data Science", tbl_td_center),
            Paragraph("ML Triage & Verification Lead", tbl_td),
            Paragraph("ahmadzahid5029@gmail.com", tbl_td)
        ]
    ]
    t_team = Table(team_cells, colWidths=[68, 110, 78, 148, 136])
    t_team.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_brand),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('PADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_team)
    story.append(Spacer(1, 5))

    # Figure 4.2 Matrix
    story.append(Paragraph("Figure 4.2: The Business Model Template (Master One-Page Canvas)", sec_head))

    q1_text = (
        "<b>1. Business Mission:</b> Eliminate car repair anxiety and predatory workshop pricing in Pakistan by giving every driver an AI mechanic in their pocket that speaks their language.<br/>"
        "<b>2. Basis of Differentiation:</b> 100% factory manual-grounded (zero AI hallucination); native Trilingual RAG (English, Roman Urdu, Urdu); localized PKR parts & labor cost benchmarks.<br/>"
        "<b>3. Target Market:</b> 1.4M urban middle-class vehicle owners in Lahore, Karachi, and Islamabad driving 5 to 15-year-old Japanese/local cars (Suzuki, Toyota, Honda).<br/>"
        "<b>4. Product/Market Scope:</b> Phase 1: Mobile symptom triage & verified PKR price auditor for top 15 models in Lahore. Phase 2: Bluetooth OBD-II sensor sync & nationwide workshop network."
    )

    q2_text = (
        "<b>5. Core Competencies:</b><br/>"
        "&bull; Multi-hop causal diagnostic inference over automotive fault trees.<br/>"
        "&bull; Specialized Roman Urdu/Urdu mechanical NLP & workshop slang dictionary.<br/>"
        "&bull; Live Pakistani spare parts price index (Montgomery Rd & Bilal Gunj).<br/>"
        "<b>6. Key Assets:</b><br/>"
        "&bull; <i>Intellectual:</i> Causal graph algorithms, 1,200+ indexed workshop service manuals, proprietary symptom-DTC decision trees.<br/>"
        "&bull; <i>Human:</i> 5 PUCIT Data Science engineers with mechanical & ML expertise.<br/>"
        "&bull; <i>Physical/Digital:</i> Cloud API backend, OBD-II test benches, CAN bus rigs.<br/>"
        "&bull; <i>Financial:</i> Bootstrap founder funds + PUCIT incubation compute credits."
    )

    q3_text = (
        "<b>7. Revenue Streams (Table 4.3):</b><br/>"
        "&bull; <i>Freemium Pro Subscription (Primary):</i> PKR 950/month (unlimited scans, predictive failure alerts, verified PKR repair quote audits).<br/>"
        "&bull; <i>Certified Workshop Referral Lead Fee:</i> PKR 350 per verified repair booking.<br/>"
        "&bull; <i>Workshop SaaS Billing Toolkit:</i> PKR 4,500/month for computerized customer invoices & diagnostic health reports.<br/>"
        "<b>8. Cost Structure:</b> Value-driven. Fixed development costs dominate; near-zero marginal distribution cost. Primary expenses: Cloud LLM/vector APIs and field data collection.<br/>"
        "<b>9. Financing / Funding:</b> PKR 250,000 founder bootstrap budget. Projected cashflow breakeven at 1,100 active Pro subscribers."
    )

    q4_text = (
        "<b>10. Product / Service Production:</b> Built 100% in-house by student engineering team. Hybrid Vector + Knowledge Graph retrieval pipeline with FastAPI microservices and mobile frontend.<br/>"
        "<b>11. Channels:</b><br/>"
        "&bull; <i>Direct:</i> Google Play Store, Apple App Store, and WhatsApp triage bot.<br/>"
        "&bull; <i>Intermediaries:</i> QR banners at partner oil change centers, tire shops, and campus auto clubs.<br/>"
        "<b>12. Key Partners:</b> Vetted local repair workshops, wholesale auto spare part distributors, PUCIT Computing Incubator, and academic project advisors."
    )

    canvas_table_cells = [
        [
            Paragraph("<b>1. CORE STRATEGY (How We Compete)</b>", quad_hdr),
            Paragraph("<b>2. RESOURCES (What Makes It Possible)</b>", quad_hdr)
        ],
        [
            Paragraph(q1_text, quad_content),
            Paragraph(q2_text, quad_content)
        ],
        [
            Paragraph("<b>3. FINANCIALS (How the Firm Earns)</b>", quad_hdr),
            Paragraph("<b>4. OPERATIONS (How It Runs Day-to-Day)</b>", quad_hdr)
        ],
        [
            Paragraph(q3_text, quad_content),
            Paragraph(q4_text, quad_content)
        ]
    ]

    t_canvas = Table(canvas_table_cells, colWidths=[270, 270])
    t_canvas.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), c_brand),
        ('BACKGROUND', (1,0), (1,0), c_accent),
        ('BACKGROUND', (0,2), (0,2), c_brand),
        ('BACKGROUND', (1,2), (1,2), c_accent),
        ('BACKGROUND', (0,1), (0,1), colors.white),
        ('BACKGROUND', (1,1), (1,1), c_bg_light),
        ('BACKGROUND', (0,3), (0,3), c_bg_light),
        ('BACKGROUND', (1,3), (1,3), colors.white),
        ('BOX', (0,0), (-1,-1), 1, c_brand),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_canvas)
    story.append(Spacer(1, 4))

    # Page 1 Footer Note
    story.append(Paragraph(
        "<b>Core Insight & Alignment:</b> AutoCare AI uses a standard freemium software recipe executed with acute regional insight: free Roman Urdu symptom triage builds rapid consumer trust, enabling profitable monetization through Pro subscriptions and verified workshop referrals.",
        callout_txt
    ))

    # =========================================================================
    # PAGE 2: DETAILED 12 BOXES - SIMPLE, CLEAR, ACADEMICALLY RIGOROUS
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("Detailed Breakdown of the 12 Business Model Boxes", sec_head))
    story.append(Paragraph("Comprehensive operational descriptions satisfying Barringer & Ireland Chapter 4 requirements.", subtitle_style))

    # Quadrant 1 Deep Dive
    story.append(Paragraph("Quadrant 1: Core Strategy (How and Where We Compete)", sub_sec_head))
    story.append(Paragraph("<b>1. Business Mission:</b> To democratize automotive diagnostic intelligence in developing vehicle markets, ensuring no driver pays for unneeded repairs or suffers diagnostic fear.", bullet_text))
    story.append(Paragraph("<b>2. Basis of Differentiation (Benefits over Features):</b>", bullet_text))
    story.append(Paragraph("&bull; <i>Actionable Cost Protection:</i> Drivers know the exact fair PKR cost range for labor and replacement components before stepping into an auto repair shop.", bullet_text))
    story.append(Paragraph("&bull; <i>Native Language Fluency:</i> Natural symptom reporting in conversational Roman Urdu ('gaari missing kar rahi hai AC on karne per'), translated directly into ISO diagnostic trouble codes.", bullet_text))
    story.append(Paragraph("&bull; <i>Zero Hallucination Guarantee:</i> Every mechanical recommendation is strictly grounded in factory service manuals, never fabricated by generalist LLMs.", bullet_text))
    story.append(Paragraph("<b>3. Target Market:</b> Urban middle-class vehicle owners (aged 20 to 48) in Tier-1 Pakistani cities (Lahore, Karachi, Islamabad) owning 5 to 15-year-old Japanese/local vehicles (Suzuki Cultus/Alto, Toyota Corolla, Honda Civic).", bullet_text))
    story.append(Paragraph("<b>4. Product/Market Scope:</b> Starting narrow with Lahore-based symptom triage and pricing benchmarks for top 15 commuter models; expanding in Years 2-4 to IoT OBD-II dongles, commercial fleet telemetry, and nationwide workshop dispatch.", bullet_text))
    story.append(Spacer(1, 4))

    # Quadrant 2 Deep Dive
    story.append(Paragraph("Quadrant 2: Resources (What Makes the Plan Possible)", sub_sec_head))
    story.append(Paragraph("<b>5. Core Competencies:</b>", bullet_text))
    story.append(Paragraph("&bull; <i>Trilingual Automotive NLP:</i> Proprietary parser connecting Pakistani mechanical colloquialisms to structured OBD-II diagnostic fault trees.", bullet_text))
    story.append(Paragraph("&bull; <i>Manual-Grounded Causal Reasoning:</i> Multi-hop RAG pipeline over verified OEM service workshop documentation.", bullet_text))
    story.append(Paragraph("&bull; <i>Localized Price Auditing:</i> Weekly crowd-sourced and dealer-verified PKR benchmark database for OEM, Kabli, and aftermarket parts.", bullet_text))
    story.append(Paragraph("<b>6. Key Assets:</b>", bullet_text))
    story.append(Paragraph("&bull; <i>Intellectual:</i> Causal graph decision engine, proprietary Roman Urdu mechanical lexicon (4,500 terms), and structured vector database of 1,200 vehicle manuals.", bullet_text))
    story.append(Paragraph("&bull; <i>Human:</i> 5 Data Science specialists with complementary proficiencies across systems architecture, ML engineering, mobile UX, and mechanical triage.", bullet_text))
    story.append(Paragraph("&bull; <i>Physical & Digital:</i> Hardware testing lab (OBD-II scanners, CAN bus testbenches) and scalable cloud hosting infrastructure.", bullet_text))
    story.append(Paragraph("&bull; <i>Financial:</i> Self-funded student prototype capital (PKR 250,000) supplemented by university computational resources.", bullet_text))
    story.append(Spacer(1, 4))

    # Quadrant 3 Deep Dive
    story.append(Paragraph("Quadrant 3: Financials (How the Firm Earns Money)", sub_sec_head))
    story.append(Paragraph("<b>7. Revenue Streams (Named & Priced per Table 4.3):</b>", bullet_text))
    story.append(Paragraph("&bull; <i>Freemium Pro Subscription (Primary):</i> Basic symptom triage is free. <b>PKR 950 / month</b> (or PKR 7,500 / year) for AutoCare Pro with unlimited scans, predictive health monitoring, and quote auditing.", bullet_text))
    story.append(Paragraph("&bull; <i>Matchmaking Referral Commission:</i> <b>PKR 350</b> flat referral fee paid by vetted workshops for every booking dispatched through the app.", bullet_text))
    story.append(Paragraph("&bull; <i>B2B Workshop Diagnostic SaaS:</i> <b>PKR 4,500 / month</b> for independent mechanics to generate computerized diagnostic certificates.", bullet_text))
    story.append(Paragraph("<b>8. Cost Structure:</b> Value-driven business model. High initial development/data costs, but near-zero marginal cost per additional digital user. Primary recurring costs include cloud inference APIs, database hosting, and localized market price updates.", bullet_text))
    story.append(Paragraph("<b>9. Financing / Funding:</b> PKR 250,000 initial founder bootstrapping. Financial breakeven achieved at 1,100 active Pro subscribers.", bullet_text))
    story.append(Spacer(1, 4))

    # Quadrant 4 Deep Dive
    story.append(Paragraph("Quadrant 4: Operations (How It Runs Day-to-Day)", sub_sec_head))
    story.append(Paragraph("<b>10. Product & Service Production:</b> 100% in-house software engineering. Containerized FastAPI microservices running hybrid BM25 + dense semantic vector search, integrated with Flutter mobile frontend.", bullet_text))
    story.append(Paragraph("<b>11. Channels:</b> Direct mobile app downloads (Google Play, iOS), zero-friction WhatsApp triage bot, and QR code referral displays placed at partner lube bays and university campuses.", bullet_text))
    story.append(Paragraph("<b>12. Key Partners:</b> Vetted neighborhood mechanics (fulfillment partners), Montgomery Road spare parts wholesalers (pricing data partners), and PUCIT Computing Incubator (institutional support).", bullet_text))

    # =========================================================================
    # PAGE 3: SLIDE 21 TASKS (PRICING & INTERVIEWS) + ALIGNMENT & RUBRIC
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("Slide 21 Practical Tasks & Consistency Verification", sec_head))
    story.append(Paragraph("Direct fulfillment of Slide 21 deliverables and Chapter 4 evaluation rubric criteria.", subtitle_style))

    # Task 2: Pricing Comparison Table
    story.append(Paragraph("Task 2: Primary Revenue Stream Pricing & Competitor Comparison", sub_sec_head))
    story.append(Paragraph("Selected Model from Table 4.3: <b>Freemium Subscription (SaaS)</b> - Priced at <b>PKR 950 / month</b>.", body_text))
    story.append(Spacer(1, 3))

    comp_cells = [
        [
            Paragraph("Solution / Provider", tbl_th),
            Paragraph("Business Model", tbl_th),
            Paragraph("Price Point (PKR)", tbl_th),
            Paragraph("Key Friction & Structural Limitations", tbl_th)
        ],
        [
            Paragraph("<b>AutoCare AI (Ours)</b>", tbl_td_bold),
            Paragraph("Freemium SaaS<br/>(Recurring)", tbl_td),
            Paragraph("<b>PKR 950 / mo</b><br/>(Free Tier Available)", tbl_td_bold),
            Paragraph("Requires basic smartphone; fully localized in Roman Urdu with live PKR fair repair price audits.", tbl_td)
        ],
        [
            Paragraph("<b>PakWheels CarSure</b>", tbl_td_bold),
            Paragraph("Service Sale<br/>(One-off)", tbl_td),
            Paragraph("<b>PKR 4,500 - 6,500</b><br/>per inspection", tbl_td),
            Paragraph("Expensive single inspection; only used when buying/selling, entirely unsuitable for daily troubleshooting.", tbl_td)
        ],
        [
            Paragraph("<b>Handheld OBD Scanners</b><br/>(Launch / Autel)", tbl_td_bold),
            Paragraph("Product Sale<br/>(Hardware)", tbl_td),
            Paragraph("<b>PKR 8,500 - 22,000</b><br/>one-time hardware", tbl_td),
            Paragraph("Outputs cryptic raw fault codes (e.g., 'P0300') with no Urdu explanation, no causal repair steps, and no cost guide.", tbl_td)
        ]
    ]
    t_comp = Table(comp_cells, colWidths=[120, 95, 110, 215])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_brand),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#EFF6FF"), colors.white, c_bg_light]),
        ('PADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 6))

    # Task 3: Real User Discovery Findings
    story.append(Paragraph("Task 3: Concept-Test User Evidence (Week 3 Field Findings)", sub_sec_head))
    story.append(Paragraph("Field interview question posed to 14 vehicle owners in Lahore: <i>'How do you handle unexpected car issues today, and what does it cost you in time and money?'</i>", body_text))
    story.append(Spacer(1, 3))

    user_cells = [
        [
            Paragraph("Pain Category", tbl_th),
            Paragraph("Current User Behavior & Field Evidence", tbl_th),
            Paragraph("Direct Business Model Implication", tbl_th)
        ],
        [
            Paragraph("<b>Severe Time Loss</b>", tbl_td_bold),
            Paragraph("Owners waste <b>2 to 4 hours</b> visiting multiple workshops on weekends to get secondary opinions.", tbl_td),
            Paragraph("Validates demand for an instant digital co-pilot before visiting any garage.", tbl_td)
        ],
        [
            Paragraph("<b>Wasted Money</b>", tbl_td_bold),
            Paragraph("<b>71% of respondents</b> paid for parts that did not solve their problem (average wasted: <b>PKR 6,200</b>).", tbl_td),
            Paragraph("Substantiates strong willingness to pay PKR 950/mo to avoid repeated misdiagnoses.", tbl_td)
        ],
        [
            Paragraph("<b>Distrust & Jargon</b>", tbl_td_bold),
            Paragraph("Drivers reported high stress negotiating with mechanics due to technical jargon and perceived deception.", tbl_td),
            Paragraph("Confirms the immense market power of Roman Urdu explanations & transparent parts auditing.", tbl_td)
        ]
    ]
    t_user = Table(user_cells, colWidths=[105, 235, 200])
    t_user.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_accent),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('PADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_user)
    story.append(Spacer(1, 6))

    # Consistency & Alignment Check
    story.append(Paragraph("Logical Consistency & Alignment Between Quadrants", sub_sec_head))
    story.append(Paragraph(
        "<b>Strategic Alignment Check:</b> All 4 quadrants are mutually reinforcing without internal contradiction:<br/>"
        "&bull; <i>Strategy & Operations:</i> The mission (zero repair fear) demands 100% manual grounding; operations achieves this through in-house RAG index pipelines rather than generic, untrusted third-party chat models.<br/>"
        "&bull; <i>Resources & Differentiation:</i> Our Roman Urdu mechanical dictionary and causal graph (Quadrant 2) are the exact engine behind our differentiation (Quadrant 1), creating a defensible competitive moat.<br/>"
        "&bull; <i>Financials & Channels:</i> The freemium entry tier (Quadrant 3) drives viral adoption across WhatsApp and app stores (Quadrant 4), feeding high-intent repair bookings to certified partner mechanics.",
        bullet_text
    ))
    story.append(Spacer(1, 5))

    # Evaluation Rubric Compliance
    story.append(Paragraph("Submission Evaluation Rubric Self-Assessment", sub_sec_head))
    rubric_cells = [
        [
            Paragraph("Evaluation Criteria", tbl_th),
            Paragraph("Submission Compliance Evidence", tbl_th),
            Paragraph("Status", tbl_th)
        ],
        [
            Paragraph("<b>1. Completeness</b>", tbl_td_bold),
            Paragraph("All 12 boxes of Barringer & Ireland Figure 4.2 addressed with domain-specific metrics.", tbl_td),
            Paragraph("<b>100% Complete</b>", tbl_td_center)
        ],
        [
            Paragraph("<b>2. Logical Consistency</b>", tbl_td_bold),
            Paragraph("Full alignment between mission, technical competencies, pricing tiers, and distribution channels.", tbl_td),
            Paragraph("<b>Fully Aligned</b>", tbl_td_center)
        ],
        [
            Paragraph("<b>3. Originality & Clarity</b>", tbl_td_bold),
            Paragraph("Novel Roman Urdu mechanical NLP and localized PKR repair benchmark engine for Pakistani market.", tbl_td),
            Paragraph("<b>High Originality</b>", tbl_td_center)
        ],
        [
            Paragraph("<b>4. Professional Presentation</b>", tbl_td_bold),
            Paragraph("Strict 3-page executive canvas layout, verified student roster, clean tables, zero formatting defects.", tbl_td),
            Paragraph("<b>Professional</b>", tbl_td_center)
        ]
    ]
    t_rubric = Table(rubric_cells, colWidths=[120, 320, 100])
    t_rubric.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_brand),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('PADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_rubric)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated: {filename}")

if __name__ == "__main__":
    out_repo = r"C:\Users\ABDUL\.gemini\antigravity\scratch\autocare-us2\docs\AutoCare_AI_Business_Model_Assignment.pdf"
    out_desk = r"C:\Users\ABDUL\Desktop\AutoCare_AI_Business_Model_Assignment.pdf"
    build_pdf(out_repo)
    build_pdf(out_desk)
