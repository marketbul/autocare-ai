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
pdf_path = os.path.join(base_dir, "AutoCare_AI_Defense_and_Tough_Questions_Guide.pdf")

class DefenseNumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(DefenseNumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(DefenseNumberedCanvas, self).showPage()
        super(DefenseNumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        if self._pageNumber > 1:
            self.drawString(45, letter[1] - 30, "AutoCare AI — Tough Professor Defense & Scenario Answers")
            self.drawRightString(letter[0] - 45, letter[1] - 30, "PUCIT • BS Data Science")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(45, letter[1] - 34, letter[0] - 45, letter[1] - 34)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawString(45, 25, "AutoCare AI — 5 Team Leads Defense Script & Tough Scenario Questions")
        self.drawRightString(letter[0] - 45, 25, page_str)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(45, 35, letter[0] - 45, 35)
        self.restoreState()

def build_defense_pdf():
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=45, rightMargin=45, topMargin=45, bottomMargin=45
    )
    styles = getSampleStyleSheet()

    style_badge = ParagraphStyle('Badge', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor('#DC2626'), spaceAfter=3)
    style_title = ParagraphStyle('MainTitle', fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#0F172A'), spaceAfter=4)
    style_sub = ParagraphStyle('SubTitle', fontName='Helvetica-Oblique', fontSize=9, leading=12, textColor=colors.HexColor('#64748B'), spaceAfter=10)
    style_h1 = ParagraphStyle('SectionH1', fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=colors.HexColor('#0F172A'), spaceBefore=8, spaceAfter=4)
    style_h2 = ParagraphStyle('SectionH2', fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=colors.HexColor('#0284C7'), spaceBefore=6, spaceAfter=3)
    style_body = ParagraphStyle('Body', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#334155'), spaceAfter=3)
    style_pitch = ParagraphStyle('Pitch', fontName='Helvetica-Oblique', fontSize=8, leading=11, textColor=colors.HexColor('#059669'), spaceAfter=4)
    style_th = ParagraphStyle('TableHeader', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.white)
    style_q = ParagraphStyle('Question', fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=colors.HexColor('#991B1B'))
    style_a = ParagraphStyle('Answer', fontName='Helvetica', fontSize=7, leading=9, textColor=colors.HexColor('#1E293B'))

    elements = []

    # Title
    elements.append(Paragraph("PUCIT BS DATA SCIENCE • FYP DEFENSE & TOUGH PROFESSOR SCENARIOS", style_badge))
    elements.append(Paragraph("AutoCare AI: 5-Member Defense Script & Tough Professor Q&A", style_title))
    elements.append(Paragraph("Complete Non-Technical Explanations, Detailed Individual Work, and 15 Trap Questions Solved with Exact Scripted Answers", style_sub))

    # Meta
    meta_data = [
        [Paragraph("<b>Presentation Scope:</b>", style_q), Paragraph("Tomorrow's FYP Presentation / Big Data Defense Panel", style_a)],
        [Paragraph("<b>Panel Profile:</b>", style_q), Paragraph("Strict University Professors asking tough scenario-based questions", style_a)],
        [Paragraph("<b>Student Strategy:</b>", style_q), Paragraph("Plain English + Simple Car Analogies + Exact Technical Architecture Names", style_a)],
    ]
    t_meta = Table(meta_data, colWidths=[120, 402])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FEF2F2')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#EF4444')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#FCA5A5')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elements.append(t_meta)
    elements.append(Spacer(1, 6))

    # Master Rule
    elements.append(Paragraph("1. The 3-Step Formula to Answer Any Tough Question Tomorrow", style_h1))
    elements.append(Paragraph(
        "<b>Step 1:</b> Acknowledge with confidence: <i>'Sir, that is a critical real-world failure mode.'</i><br/>"
        "<b>Step 2:</b> State the exact technical component built: <i>'That is exactly why Member X built Component Y.'</i><br/>"
        "<b>Step 3:</b> Give the simple car analogy: <i>'Just like an emergency triage doctor / traffic roundabout / filter gate...'</i>",
        style_body
    ))
    elements.append(Spacer(1, 4))

    # 5 Members with scenarios
    from generate_defense_guide_docx import generate_defense_guide_docx
    # Import same members data
    import sys
    sys.path.append(base_dir)
    from generate_defense_guide_docx import MEMBERS_DATA

    for idx, m in enumerate(MEMBERS_DATA):
        elements.append(Paragraph(f"🎓 {m['name']}", style_h2))
        elements.append(Paragraph(f"<b>Role:</b> {m['role']}  |  <b>Workload:</b> {m['stat']}", style_body))
        elements.append(Paragraph(f"<b>🎙️ 30-Second Introduction Pitch:</b> \"{m['simple_summary']}\"", style_pitch))

        # Scenarios Table
        sc_table_data = [
            [Paragraph("Professor's Tough Scenario Question", style_th), Paragraph("Your Exact Winning Answer to Speak", style_th)]
        ]
        for q, a in m['scenarios']:
            sc_table_data.append([
                Paragraph(q, style_q),
                Paragraph(a, style_a)
            ])
        t_sc = Table(sc_table_data, colWidths=[160, 362])
        t_sc.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FEF2F2'), colors.white]),
            ('TOPPADDING', (0,0), (-1,-1), 2.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ]))
        elements.append(t_sc)
        elements.append(Spacer(1, 4))
        if idx in [1, 3]:
            elements.append(PageBreak())

    doc.build(elements, canvasmaker=DefenseNumberedCanvas)
    print(f"[OK] Generated Defense PDF: {pdf_path}")
    shutil.copy2(pdf_path, os.path.join(desktop_dir, "AutoCare_AI_Defense_and_Tough_Questions_Guide.pdf"))
    shutil.copy2(pdf_path, os.path.join(deliverable_dir, "AutoCare_AI_Defense_and_Tough_Questions_Guide.pdf"))
    print(f"[SYNC] Copied Defense PDF to Desktop!")

if __name__ == "__main__":
    build_defense_pdf()
