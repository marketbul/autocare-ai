import os
import shutil
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from data_defense import MEMBERS_DATA

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

def generate_defense_guide_docx():
    base_dir = r"C:\Users\ABDUL\.gemini\antigravity\scratch\autocare-us2"
    desktop_dir = r"C:\Users\ABDUL\Desktop"
    deliverable_dir = r"C:\Users\ABDUL\Desktop\AutoCare_AI_Complete_Deliverable_2026-11-10"

    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.7)
        s.bottom_margin = Inches(0.7)
        s.left_margin = Inches(0.7)
        s.right_margin = Inches(0.7)

    normal = doc.styles['Normal']
    normal.font.name = 'Calibri'
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
    normal.paragraph_format.line_spacing = 1.15
    normal.paragraph_format.space_after = Pt(4)

    # Top Badge
    p_badge = doc.add_paragraph()
    r = p_badge.add_run("PUCIT BS DATA SCIENCE • FYP DEFENSE & TOUGH PROFESSOR SCENARIOS GUIDE")
    r.font.name = 'Arial'; r.font.size = Pt(8.5); r.font.bold = True; r.font.color.rgb = RGBColor(0xDC, 0x26, 0x26)

    # Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(2); p_title.paragraph_format.space_after = Pt(2)
    r = p_title.add_run("AutoCare AI: 5-Member Defense Script & Tough Professor Q&A")
    r.font.name = 'Arial'; r.font.size = Pt(18); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(12)
    r = p_sub.add_run("Complete Non-Technical Explanations, Detailed Individual Work, and 15 Trap Questions Solved with Exact Scripted Answers")
    r.font.size = Pt(10.5); r.font.italic = True; r.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    # Executive Box
    t_meta = doc.add_table(rows=3, cols=2)
    t_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_rows = [
        ("Presentation Date", "Tomorrow's FYP / Big Data Defense"),
        ("Audience / Panel", "Strict University Professors asking tricky scenario-based questions"),
        ("Preparation Strategy", "5 Members speaking in plain English with simple real-life car analogies and exact technical names")
    ]
    for i, (k, v) in enumerate(meta_rows):
        row = t_meta.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(1.8); c1.width = Inches(5.2)
        c0.paragraphs[0].text = k; c0.paragraphs[0].runs[0].font.bold = True; c0.paragraphs[0].runs[0].font.size = Pt(9)
        c1.paragraphs[0].text = v; c1.paragraphs[0].runs[0].font.size = Pt(9)
        set_cell_background(c0, "FEE2E2"); set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, 40, 40, 60, 60); set_cell_margins(c1, 40, 40, 60, 60)
    set_table_borders(t_meta, "EF4444")

    # Section 1
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    h1 = doc.add_paragraph()
    r = h1.add_run("1. The Master Rule for Tomorrow: How Non-Tech Students Win Against Tough Professors")
    r.font.name = 'Arial'; r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_rule = doc.add_paragraph()
    p_rule.add_run(
        "Tough professors always test you using the same trap: They give you a real-life mechanical scenario "
        "(for example: 'What if a car is driving in 48°C heat in Multan?' or 'What if 10,000 cars send signals at once?' or 'What if a mechanic lies?') "
        "and wait to see if you get nervous and say 'We use ChatGPT' or 'We just save it in SQLite'.\n\n"
        "To get an A grade, remember this 3-Step Defense Formula:\n"
        "1. Acknowledge the problem with confidence: 'Sir, that is a critical real-world failure mode.'\n"
        "2. Give the exact technical component your team built: 'That is exactly why Member X built Component Y.'\n"
        "3. Explain it with a simple car analogy: 'Just like an emergency triage doctor / traffic roundabout / filter gate...'"
    )

    # Section 2
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    h2 = doc.add_paragraph()
    r = h2.add_run("2. Detailed Member Breakdown & Tough Professor Scenarios")
    r.font.name = 'Arial'; r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    for m in MEMBERS_DATA:
        doc.add_paragraph().paragraph_format.space_after = Pt(4)
        h_mem = doc.add_paragraph()
        r = h_mem.add_run(f"🎓 {m['name']}")
        r.font.name = 'Arial'; r.font.size = Pt(12); r.font.bold = True; r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

        p_r = doc.add_paragraph()
        p_r.paragraph_format.space_after = Pt(2)
        r = p_r.add_run(f"Role: {m['role']}  |  Workload: {m['stat']}")
        r.font.bold = True; r.font.size = Pt(9.5); r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

        p_pitch = doc.add_paragraph()
        p_pitch.paragraph_format.space_after = Pt(4)
        r = p_pitch.add_run("🎙️ 30-Second Introduction Pitch for Tomorrow:\n")
        r.font.bold = True; r.font.size = Pt(9.5); r.font.color.rgb = RGBColor(0x05, 0x96, 0x69)
        r_text = p_pitch.add_run(f"\"{m['simple_summary']}\"")
        r_text.font.italic = True; r_text.font.size = Pt(9.5)

        p_b = doc.add_paragraph()
        p_b.paragraph_format.space_before = Pt(2); p_b.paragraph_format.space_after = Pt(2)
        r = p_b.add_run("Key Technical Deliverables:")
        r.font.bold = True; r.font.size = Pt(9.5); r.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        for it in m['what_built_detail']:
            bp = doc.add_paragraph(style='List Bullet')
            bp.paragraph_format.space_after = Pt(2)
            bp.add_run(it).font.size = Pt(9)

        doc.add_paragraph().paragraph_format.space_before = Pt(4); doc.add_paragraph().paragraph_format.space_after = Pt(2)
        p_st = doc.add_paragraph()
        r = p_st.add_run("⚔️ Tough Professor Trap Questions & Exact Answers to Defend:")
        r.font.bold = True; r.font.size = Pt(9.5); r.font.color.rgb = RGBColor(0xDC, 0x26, 0x26)

        t_sc = doc.add_table(rows=len(m['scenarios'])+1, cols=2)
        t_sc.alignment = WD_TABLE_ALIGNMENT.CENTER
        c0, c1 = t_sc.rows[0].cells[0], t_sc.rows[0].cells[1]
        c0.width = Inches(2.2); c1.width = Inches(4.8)
        c0.paragraphs[0].text = "Professor's Tough Scenario Question"
        c0.paragraphs[0].runs[0].font.bold = True; c0.paragraphs[0].runs[0].font.size = Pt(8.5)
        c0.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_background(c0, "0F172A")
        c1.paragraphs[0].text = "Your Exact Winning Answer to Speak"
        c1.paragraphs[0].runs[0].font.bold = True; c1.paragraphs[0].runs[0].font.size = Pt(8.5)
        c1.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_background(c1, "0F172A")
        set_cell_margins(c0, 40, 40, 50, 50); set_cell_margins(c1, 40, 40, 50, 50)

        for s_idx, (q, a) in enumerate(m['scenarios']):
            row = t_sc.rows[s_idx+1]
            cell_q, cell_a = row.cells[0], row.cells[1]
            cell_q.paragraphs[0].text = q
            cell_q.paragraphs[0].runs[0].font.bold = True; cell_q.paragraphs[0].runs[0].font.size = Pt(8)
            cell_q.paragraphs[0].runs[0].font.color.rgb = RGBColor(0x99, 0x1B, 0x1B)
            cell_a.paragraphs[0].text = a
            cell_a.paragraphs[0].runs[0].font.size = Pt(8)
            bg = "FEF2F2" if s_idx % 2 == 0 else "FFFFFF"
            set_cell_background(cell_q, bg); set_cell_background(cell_a, bg)
            set_cell_margins(cell_q, 35, 35, 50, 50); set_cell_margins(cell_a, 35, 35, 50, 50)
        set_table_borders(t_sc)

    # Section 3
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    h_chk = doc.add_paragraph()
    r = h_chk.add_run("3. 10-Second Quick Defense Checklist on Your Desktop")
    r.font.name = 'Arial'; r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_c = doc.add_paragraph()
    p_c.add_run(
        "Before entering the presentation room, make sure these are ready on your laptop:\n"
        "1. Website running: Double-click OPEN_AUTOCARE_WEBSITE.bat -> http://localhost:8000/app/#/dashboard.\n"
        "2. Jira Board ready: Double-click OPEN_JIRA_APP.bat -> Filter by member name to show all 138 tickets.\n"
        "3. Print or bring this document: AutoCare_AI_Defense_and_Tough_Questions_Guide.docx.\n"
        "4. GitHub repository link ready: https://github.com/marketbul/autocare-ai.git (showing 126+ commits)."
    )

    out_docx = os.path.join(base_dir, "AutoCare_AI_Defense_and_Tough_Questions_Guide.docx")
    doc.save(out_docx)
    print(f"[OK] Generated Defense DOCX: {out_docx}")

    desktop_docx = os.path.join(desktop_dir, "AutoCare_AI_Defense_and_Tough_Questions_Guide.docx")
    deliverable_docx = os.path.join(deliverable_dir, "AutoCare_AI_Defense_and_Tough_Questions_Guide.docx")
    shutil.copy2(out_docx, desktop_docx)
    shutil.copy2(out_docx, deliverable_docx)
    print(f"[SYNC] Copied Defense DOCX to Desktop: {desktop_docx}")

if __name__ == "__main__":
    generate_defense_guide_docx()
