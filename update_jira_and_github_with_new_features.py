import os
import csv
import json
import shutil
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

base_dir = r"C:\Users\ABDUL\.gemini\antigravity\scratch\autocare-us2"
csv_path = os.path.join(base_dir, "docs", "jira_tickets_import.csv")
desktop_dir = r"C:\Users\ABDUL\Desktop"
deliverable_dir = r"C:\Users\ABDUL\Desktop\AutoCare_AI_Complete_Deliverable_2026-11-10"
brain_dir = r"C:\Users\ABDUL\.gemini\antigravity\brain\00a7aa5b-5d32-449b-a3f6-925ffecf15c5"

# Read existing tickets
with open(csv_path, "r", encoding="utf-8") as f:
    tickets = list(csv.DictReader(f))

print(f"Initial tickets count: {len(tickets)}")

# Check if new tickets are already added
existing_keys = {t["Issue key"] for t in tickets}

new_tickets = [
    {
        "Issue Type": "Story",
        "Issue key": "AUT-125-DSP",
        "Summary": "feat(dispatch): implement 4-step Fault-to-Specialist Dispatch Engine with Haversine GPS routing and composite scoring",
        "Description": "Engineered automated workshop routing matching diagnosed vehicle faults to verified nearby specialists using Haversine great-circle distance and multi-criteria scoring: Score = (0.40 * Skill) + (0.30 * Distance) + (0.20 * Rating) + (0.10 * Queue). Localized for Lahore, Karachi, and Islamabad with fair PKR price estimates.",
        "Epic Link": "EPIC-5: Modern Web Portal & Localized PKR Pricing",
        "Story Points": "5",
        "Assignee": "Muhammad Abdullah (BSDSF23A032)",
        "Reporter": "Abdullah (BSDSF23A035)",
        "Priority": "High",
        "Status": "Done",
        "Sprint": "Sprint 4 (Dataset Pipeline & Scaling)",
        "Commit Hash": "2108ae4",
        "Git Commit Message": "feat(dispatch): implement 4-step Fault-to-Specialist Dispatch Engine with Haversine GPS routing and composite scoring",
        "Resolved Date": "2026-11-17"
    },
    {
        "Issue Type": "Story",
        "Issue key": "AUT-126-SCH",
        "Summary": "feat(schemas): define formal 4-tier data schemas (Bronze JSON, Silver Parquet, Gold SQL, Fast Bloom Filter)",
        "Description": "Formalized complete 4-tier data schemas: Bronze Tier raw telemetry validation with SHA-256 CAS deduplication, Silver Tier Snappy Parquet columnar partitions (/make=X/model=Y/year=Z/), Gold Tier relational entity tables, and 65,536-bit Counting Bloom Filter cache in RAM.",
        "Epic Link": "EPIC-1: Distributed Storage Lakehouse & Deduplication",
        "Story Points": "5",
        "Assignee": "Talha Ali Bhatti (BSDSF23A016)",
        "Reporter": "Abdullah (BSDSF23A035)",
        "Priority": "High",
        "Status": "Done",
        "Sprint": "Sprint 4 (Dataset Pipeline & Scaling)",
        "Commit Hash": "9226588",
        "Git Commit Message": "feat(schemas): define formal 4-tier data schemas across Bronze, Silver, Gold, and Cache tiers",
        "Resolved Date": "2026-11-17"
    },
    {
        "Issue Type": "Story",
        "Issue key": "AUT-127-NLP",
        "Summary": "feat(nlp): design 4,000 subword BPE token architecture and bilingual automotive vocabulary",
        "Description": "Architected custom Subword Byte-Pair Encoding (BPE) tokenizer vocabulary of 4,000 tokens covering English, Urdu, and Pakistani Roman Urdu slang terms (e.g. dhuwan, jhatka, lambi self, radiator) with 128-token context sequence window for the 1.32M parameter PyTorch Causal Transformer.",
        "Epic Link": "EPIC-2: Distributed Hashing & Transformer AI",
        "Story Points": "5",
        "Assignee": "Abdullah (BSDSF23A035)",
        "Reporter": "Abdullah (BSDSF23A035)",
        "Priority": "High",
        "Status": "Done",
        "Sprint": "Sprint 4 (Dataset Pipeline & Scaling)",
        "Commit Hash": "b3272a0",
        "Git Commit Message": "feat(nlp): design 4,000 subword BPE token architecture and bilingual automotive vocabulary",
        "Resolved Date": "2026-11-17"
    },
    {
        "Issue Type": "Story",
        "Issue key": "AUT-128-DOC",
        "Summary": "docs(proposal): compile formal 21-section FYP Inception Proposal in Word and PDF formats",
        "Description": "Compiled exhaustive, academic-grade Final Year Project Proposal containing all 21 formal sections, token architecture specifications, Big Data telemetry capacity sizing, and balanced 5-member task allocation matrix in both docx and pdf formats.",
        "Epic Link": "EPIC-3: Multilingual Ingestion & Lexical Retrieval",
        "Story Points": "5",
        "Assignee": "Danial Hameed (BSDSF23A014)",
        "Reporter": "Abdullah (BSDSF23A035)",
        "Priority": "High",
        "Status": "Done",
        "Sprint": "Sprint 4 (Dataset Pipeline & Scaling)",
        "Commit Hash": "96b2708",
        "Git Commit Message": "docs(proposal): compile formal 21-section FYP Inception Proposal in Word and PDF formats",
        "Resolved Date": "2026-11-17"
    },
    {
        "Issue Type": "Story",
        "Issue key": "AUT-129-TST",
        "Summary": "test(dispatch): implement automated pytest test suite for dispatch scoring and lakehouse schemas",
        "Description": "Engineered automated pytest validation suite verifying Haversine great-circle calculation, multi-criteria composite score weighting, specialty fault detection for all 6 subsystems, Bronze CAS SHA-256 validation, and Counting Bloom Filter false-positive bounds.",
        "Epic Link": "EPIC-4: Supervised ML Triage & Verification",
        "Story Points": "5",
        "Assignee": "Ahmad Zahid (BSDSF23A033)",
        "Reporter": "Abdullah (BSDSF23A035)",
        "Priority": "High",
        "Status": "Done",
        "Sprint": "Sprint 4 (Dataset Pipeline & Scaling)",
        "Commit Hash": "ff2c995",
        "Git Commit Message": "test(dispatch): implement automated pytest test suite for dispatch scoring and lakehouse schemas",
        "Resolved Date": "2026-11-17"
    }
]

# Separate Done and To Do tickets to insert before To Do
done_tickets = [t for t in tickets if t.get("Status") == "Done"]
todo_tickets = [t for t in tickets if t.get("Status") != "Done"]

for nt in new_tickets:
    if nt["Issue key"] not in existing_keys:
        done_tickets.append(nt)

updated_tickets = done_tickets + todo_tickets
print(f"Updated tickets count: {len(updated_tickets)} (Done: {len(done_tickets)}, To Do: {len(todo_tickets)})")

# Save updated CSV
fieldnames = list(tickets[0].keys())
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(updated_tickets)

# Sync CSV to desktop and deliverable folders
for d in [desktop_dir, deliverable_dir, brain_dir]:
    if os.path.exists(d):
        target_csv = os.path.join(d, "jira_tickets_import.csv")
        shutil.copy2(csv_path, target_csv)
        print(f"[SYNC] CSV -> {target_csv}")

# Generate Updated JIRA_LOCAL_BOARD.html
def generate_board_html(tickets_list, output_file):
    board_data = []
    for t in tickets_list:
        board_data.append({
            "key": t.get("Issue key"),
            "summary": t.get("Summary"),
            "description": t.get("Description"),
            "assignee": t.get("Assignee"),
            "points": int(t.get("Story Points", "3") or 3),
            "status": t.get("Status"),
            "sprint": t.get("Sprint"),
            "epic": t.get("Epic Link"),
            "priority": t.get("Priority")
        })

    json_str = json.dumps(board_data, indent=2)

    template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AutoCare AI — Jira Agile Scrum Board (143 Tickets)</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    body { background-color: #0F172A; color: #F8FAFC; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
    .kanban-col { background-color: #1E293B; border-radius: 8px; min-height: 75vh; max-height: 85vh; overflow-y: auto; }
    .card { background-color: #334155; border-radius: 6px; transition: transform 0.15s ease, box-shadow 0.15s ease; }
    .card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #1E293B; }
    ::-webkit-scrollbar-thumb { background: #475569; border-radius: 3px; }
  </style>
</head>
<body class="p-6">
  <!-- Top Bar -->
  <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 pb-4 border-b border-slate-700 gap-4">
    <div>
      <div class="flex items-center gap-3">
        <div class="bg-sky-500 text-white p-2 rounded-lg"><i class="fa-brands fa-jira text-xl"></i></div>
        <div>
          <h1 class="text-2xl font-bold tracking-tight text-white">AutoCare AI / AutoData Lake — Agile Board</h1>
          <p class="text-sm text-slate-400">PUCIT BSDS Final Year Project • Academic Supervisor: Dr. Khurram Shehzad</p>
        </div>
      </div>
    </div>
    <div class="flex flex-wrap gap-2 items-center">
      <span class="bg-emerald-900/60 text-emerald-300 border border-emerald-700 px-3 py-1.5 rounded-full text-xs font-semibold">
        <i class="fa-solid fa-check-circle mr-1"></i> __DONE_COUNT__ Completed Stories (__DONE_SP__ SP)
      </span>
      <span class="bg-blue-900/60 text-blue-300 border border-blue-700 px-3 py-1.5 rounded-full text-xs font-semibold">
        <i class="fa-solid fa-clock mr-1"></i> __TODO_COUNT__ Future Stories (__TODO_SP__ SP)
      </span>
      <span class="bg-slate-800 text-slate-300 border border-slate-600 px-3 py-1.5 rounded-full text-xs font-semibold">
        <i class="fa-solid fa-users mr-1"></i> 5 Balanced Team Leads
      </span>
    </div>
  </div>

  <!-- Filter Bar -->
  <div class="bg-slate-800/80 p-4 rounded-lg mb-6 flex flex-wrap gap-4 items-center justify-between border border-slate-700">
    <div class="flex flex-wrap gap-2 items-center">
      <span class="text-xs uppercase text-slate-400 font-bold tracking-wider mr-2"><i class="fa-solid fa-filter mr-1"></i>Filter Lead:</span>
      <button onclick="filterLead('ALL')" class="lead-btn active bg-sky-600 text-white px-3 py-1 rounded text-xs font-medium">All Team (143)</button>
      <button onclick="filterLead('Abdullah (BSDSF23A035)')" class="lead-btn bg-slate-700 hover:bg-slate-600 text-slate-200 px-3 py-1 rounded text-xs font-medium">Abdullah (035)</button>
      <button onclick="filterLead('Talha Ali Bhatti (BSDSF23A016)')" class="lead-btn bg-slate-700 hover:bg-slate-600 text-slate-200 px-3 py-1 rounded text-xs font-medium">Talha (016)</button>
      <button onclick="filterLead('Danial Hameed (BSDSF23A014)')" class="lead-btn bg-slate-700 hover:bg-slate-600 text-slate-200 px-3 py-1 rounded text-xs font-medium">Danial (014)</button>
      <button onclick="filterLead('Ahmad Zahid (BSDSF23A033)')" class="lead-btn bg-slate-700 hover:bg-slate-600 text-slate-200 px-3 py-1 rounded text-xs font-medium">Ahmad (033)</button>
      <button onclick="filterLead('Muhammad Abdullah (BSDSF23A032)')" class="lead-btn bg-slate-700 hover:bg-slate-600 text-slate-200 px-3 py-1 rounded text-xs font-medium">M. Abdullah (032)</button>
    </div>
    <div class="w-full md:w-64">
      <input type="text" id="searchInput" onkeyup="searchCards()" placeholder="Search summary or key..." class="w-full bg-slate-900 text-xs px-3 py-1.5 rounded border border-slate-600 text-white focus:outline-none focus:border-sky-500">
    </div>
  </div>

  <!-- Kanban Columns -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <!-- TO DO -->
    <div class="kanban-col p-4 flex flex-col">
      <div class="flex justify-between items-center pb-3 mb-3 border-b border-slate-700">
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-blue-500"></span>
          <h2 class="font-bold text-sm text-slate-200 uppercase tracking-wide">TO DO (Sprints 5 & 6)</h2>
        </div>
        <span id="count-todo" class="bg-slate-800 text-slate-300 px-2 py-0.5 rounded text-xs font-bold">0</span>
      </div>
      <div id="col-todo" class="flex flex-col gap-3"></div>
    </div>

    <!-- IN PROGRESS -->
    <div class="kanban-col p-4 flex flex-col">
      <div class="flex justify-between items-center pb-3 mb-3 border-b border-slate-700">
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-amber-500"></span>
          <h2 class="font-bold text-sm text-slate-200 uppercase tracking-wide">IN PROGRESS</h2>
        </div>
        <span id="count-progress" class="bg-slate-800 text-slate-300 px-2 py-0.5 rounded text-xs font-bold">0</span>
      </div>
      <div id="col-progress" class="flex flex-col gap-3"></div>
    </div>

    <!-- DONE -->
    <div class="kanban-col p-4 flex flex-col">
      <div class="flex justify-between items-center pb-3 mb-3 border-b border-slate-700">
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-emerald-500"></span>
          <h2 class="font-bold text-sm text-slate-200 uppercase tracking-wide">DONE (Sprints 1 to 4)</h2>
        </div>
        <span id="count-done" class="bg-slate-800 text-slate-300 px-2 py-0.5 rounded text-xs font-bold">0</span>
      </div>
      <div id="col-done" class="flex flex-col gap-3"></div>
    </div>
  </div>

  <script>
    const allTickets = __JSON_DATA__;
    let currentLead = 'ALL';

    function renderBoard() {
      const colTodo = document.getElementById('col-todo');
      const colProg = document.getElementById('col-progress');
      const colDone = document.getElementById('col-done');
      colTodo.innerHTML = ''; colProg.innerHTML = ''; colDone.innerHTML = '';

      let cTodo = 0, cProg = 0, cDone = 0;
      const searchVal = document.getElementById('searchInput').value.toLowerCase();

      allTickets.forEach(t => {
        if (currentLead !== 'ALL' && t.assignee !== currentLead) return;
        if (searchVal && !t.summary.toLowerCase().includes(searchVal) && !t.key.toLowerCase().includes(searchVal)) return;

        const card = document.createElement('div');
        card.className = 'card p-3 border-l-4 border-slate-500 cursor-pointer';
        if (t.status === 'Done') card.classList.add('border-l-emerald-500');
        else if (t.status === 'In Progress') card.classList.add('border-l-amber-500');
        else card.classList.add('border-l-blue-500');

        const rollTag = t.assignee.includes('035') ? '035' : t.assignee.includes('016') ? '016' : t.assignee.includes('014') ? '014' : t.assignee.includes('033') ? '033' : '032';

        card.innerHTML = `
          <div class="flex justify-between items-start mb-1.5">
            <span class="font-mono text-[11px] font-bold text-sky-400">${t.key}</span>
            <span class="bg-slate-800 text-slate-300 text-[10px] px-1.5 py-0.5 rounded font-semibold">${t.points} SP</span>
          </div>
          <p class="text-xs font-medium text-slate-200 line-clamp-2 mb-2">${t.summary}</p>
          <div class="flex justify-between items-center text-[10px] text-slate-400 pt-2 border-t border-slate-600/50">
            <span class="truncate max-w-[170px]"><i class="fa-solid fa-user-circle mr-1"></i>${t.assignee.split(' ')[0]} (${rollTag})</span>
            <span class="text-[9px] uppercase tracking-wider text-slate-500 font-bold">${t.sprint.split(' ')[0]}</span>
          </div>
        `;

        if (t.status === 'Done') { colDone.appendChild(card); cDone++; }
        else if (t.status === 'In Progress') { colProg.appendChild(card); cProg++; }
        else { colTodo.appendChild(card); cTodo++; }
      });

      document.getElementById('count-todo').innerText = cTodo;
      document.getElementById('count-progress').innerText = cProg;
      document.getElementById('count-done').innerText = cDone;
    }

    function filterLead(lead) {
      currentLead = lead;
      document.querySelectorAll('.lead-btn').forEach(b => {
        b.classList.remove('bg-sky-600', 'text-white');
        b.classList.add('bg-slate-700', 'text-slate-200');
        if (b.innerText.includes(lead.split(' ')[0]) || (lead === 'ALL' && b.innerText.includes('All'))) {
          b.classList.add('bg-sky-600', 'text-white');
          b.classList.remove('bg-slate-700', 'text-slate-200');
        }
      });
      renderBoard();
    }

    function searchCards() { renderBoard(); }
    renderBoard();
  </script>
</body>
</html>
"""
    done_count = len([t for t in tickets_list if t.get("Status") == "Done"])
    done_sp = sum(int(t.get("Story Points", 3) or 3) for t in tickets_list if t.get("Status") == "Done")
    todo_count = len([t for t in tickets_list if t.get("Status") != "Done"])
    todo_sp = sum(int(t.get("Story Points", 3) or 3) for t in tickets_list if t.get("Status") != "Done")

    rendered = (template
        .replace("__JSON_DATA__", json_str)
        .replace("__DONE_COUNT__", str(done_count))
        .replace("__DONE_SP__", str(done_sp))
        .replace("__TODO_COUNT__", str(todo_count))
        .replace("__TODO_SP__", str(todo_sp))
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rendered)
    print(f"[OK] Generated Jira Local Board: {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rendered)
    print(f"[OK] Generated Jira Local Board: {output_file}")

# Output HTML board
html_local = os.path.join(base_dir, "JIRA_LOCAL_BOARD.html")
generate_board_html(updated_tickets, html_local)

for d in [desktop_dir, deliverable_dir, brain_dir]:
    if os.path.exists(d):
        target_html = os.path.join(d, "JIRA_LOCAL_BOARD.html")
        shutil.copy2(html_local, target_html)
        print(f"[SYNC] Board HTML -> {target_html}")

print("\nSuccessfully updated Jira Tickets, CSV, and Interactive Board to 143 tickets!")
