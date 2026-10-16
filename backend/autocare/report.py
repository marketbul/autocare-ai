"""M9: Automated PDF Service Report Generation (Story 13).

Generates a downloadable, professional PDF diagnostic and service audit report
using ReportLab, containing:
- Vehicle profile & odometer reading
- Reported symptoms & OBD-II codes
- Predicted fault category & repair urgency level
- Calibrated confidence & selective prediction decision
- Citable evidence trace with document, section, and page references
- Knowledge graph multi-hop root cause chain
- Repair-recommendation verifier verdict and alternatives (if requested)
- Professional physical inspection disclaimer.
"""
from __future__ import annotations

import io
from dataclasses import dataclass, field
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_service_report_pdf(
    report_id: str,
    vehicle_info: dict,
    query_text: str,
    diagnosis_data: dict,
    citations: list[dict],
    root_cause_chain: str | None = None,
    verification: dict | None = None,
    health_score: float | None = None,
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748b"),
    )
    h2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1e293b"),
        fontName="Helvetica-Bold",
        spaceBefore=10,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
    )
    badge_style = ParagraphStyle(
        "BadgeText",
        parent=styles["Normal"],
        fontSize=10,
        leading=12,
        fontName="Helvetica-Bold",
        textColor=colors.white,
    )

    story = []

    # 1. Header
    story.append(Paragraph("AutoCare AI — Diagnostic & Maintenance Service Report", title_style))
    story.append(Paragraph(f"Report Ref: {report_id}  |  Generated: {diagnosis_data.get('date', 'Today')}", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=12))

    # 2. Vehicle Profile Box
    v_data = [
        [
            Paragraph("<b>Vehicle:</b>", body_style),
            Paragraph(f"{vehicle_info.get('manufacturer', '')} {vehicle_info.get('model', '')} ({vehicle_info.get('year', '')})", body_style),
            Paragraph("<b>Odometer:</b>", body_style),
            Paragraph(f"{vehicle_info.get('current_mileage', 'N/A'):,} km" if isinstance(vehicle_info.get('current_mileage'), (int, float)) else "N/A", body_style),
        ],
        [
            Paragraph("<b>Engine / Variant:</b>", body_style),
            Paragraph(f"{vehicle_info.get('variant', 'Standard')} - {vehicle_info.get('engine', 'Standard')}", body_style),
            Paragraph("<b>Health Index:</b>", body_style),
            Paragraph(f"{health_score}%" if health_score is not None else "N/A", body_style),
        ]
    ]
    v_table = Table(v_data, colWidths=[1.1 * inch, 2.3 * inch, 1.1 * inch, 2.5 * inch])
    v_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(v_table)
    story.append(Spacer(1, 12))

    # 3. Reported Symptoms
    story.append(Paragraph("Reported Symptoms & Diagnostic Query", h2_style))
    story.append(Paragraph(f"<i>\"{query_text}\"</i>", body_style))
    story.append(Spacer(1, 10))

    # 4. Diagnosis & Urgency Triage
    story.append(Paragraph("Diagnostic Triage & Calibrated Reliability", h2_style))
    urgency = (diagnosis_data.get("predicted_urgency") or "Moderate").title()
    category = (diagnosis_data.get("predicted_category") or "General").title()
    confidence = diagnosis_data.get("confidence", 0.85)

    urg_color = "#16a34a"  # Low = Green
    if urgency.lower() == "moderate":
        urg_color = "#eab308"
    elif urgency.lower() == "high":
        urg_color = "#f97316"
    elif urgency.lower() == "critical":
        urg_color = "#dc2626"

    diag_data = [
        [
            Paragraph("<b>Fault Category:</b>", body_style),
            Paragraph(category, body_style),
            Paragraph("<b>Repair Urgency:</b>", body_style),
            Paragraph(f"<font color='{urg_color}'><b>{urgency.upper()}</b></font>", body_style),
        ],
        [
            Paragraph("<b>Calibrated Confidence:</b>", body_style),
            Paragraph(f"{round(confidence * 100, 1)}%", body_style),
            Paragraph("<b>Recommended Action:</b>", body_style),
            Paragraph(diagnosis_data.get("action_text", "Have inspected by a technician."), body_style),
        ]
    ]
    diag_table = Table(diag_data, colWidths=[1.3 * inch, 2.1 * inch, 1.3 * inch, 2.3 * inch])
    diag_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(diag_table)
    story.append(Spacer(1, 12))

    # 5. Root-Cause Chain
    if root_cause_chain:
        story.append(Paragraph("Causal Root-Cause Chain (Knowledge Graph)", h2_style))
        story.append(Paragraph(f"<b>Root Cause Trace:</b> {root_cause_chain}", body_style))
        story.append(Spacer(1, 10))

    # 6. Workshop Claim Verification (if active)
    if verification:
        story.append(Paragraph("Workshop Repair-Claim Verification", h2_style))
        verdict = verification.get("verdict", "unsupported").replace("_", " ").title()
        v_color = "#16a34a" if "supported" in verdict.lower() and "un" not in verdict.lower() else "#dc2626"

        verif_data = [
            [Paragraph("<b>Proposed Repair:</b>", body_style), Paragraph(verification.get("proposed_repair", ""), body_style)],
            [Paragraph("<b>Verdict:</b>", body_style), Paragraph(f"<font color='{v_color}'><b>{verdict.upper()}</b></font>", body_style)],
            [Paragraph("<b>Explanation:</b>", body_style), Paragraph(verification.get("explanation", ""), body_style)],
        ]
        if verification.get("indicated_alternatives"):
            alts = ", ".join(verification["indicated_alternatives"])
            verif_data.append([Paragraph("<b>Indicated Alternatives:</b>", body_style), Paragraph(alts, body_style)])

        verif_table = Table(verif_data, colWidths=[1.5 * inch, 5.5 * inch])
        verif_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#faf5ff")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#d8b4fe")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(verif_table)
        story.append(Spacer(1, 12))

    # 7. Document Citations & Evidence Trace
    if citations:
        story.append(Paragraph("Authoritative Evidence & Manual Citations", h2_style))
        cite_rows = [[Paragraph("<b>Source Document</b>", body_style), Paragraph("<b>Section & Page</b>", body_style), Paragraph("<b>Verified Text Excerpt</b>", body_style)]]
        for c in citations[:4]:
            cite_rows.append([
                Paragraph(c.get("document_name", "Manual"), body_style),
                Paragraph(f"{c.get('section', '')}<br/>Page {c.get('page_number', '?')}", body_style),
                Paragraph(f"\"{c.get('excerpt', c.get('text', ''))[:140]}...\"", body_style),
            ])
        c_table = Table(cite_rows, colWidths=[2.0 * inch, 1.8 * inch, 3.2 * inch])
        c_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(c_table)
        story.append(Spacer(1, 14))

    # 8. Disclaimer
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94a3b8"), spaceAfter=8))
    disclaimer = (
        "<b>Important Notice:</b> AutoCare AI generates evidence-grounded diagnostic guidance "
        "derived from official vehicle manufacturer manuals. This report does not replace an in-person "
        "physical inspection by a qualified professional mechanic. Software cannot detect internal mechanical "
        "fractures or hidden sensor anomalies without physical examination."
    )
    story.append(Paragraph(disclaimer, ParagraphStyle("Disc", parent=styles["Normal"], fontSize=8, leading=11, textColor=colors.HexColor("#64748b"))))

    doc.build(story)
    return buffer.getvalue()
