import os
import csv
import json
import shutil

base_dir = r"C:\Users\ABDUL\.gemini\antigravity\scratch\autocare-us2"
csv_path = os.path.join(base_dir, "docs", "jira_tickets_import.csv")
desktop_dir = r"C:\Users\ABDUL\Desktop"
deliverable_dir = r"C:\Users\ABDUL\Desktop\AutoCare_AI_Complete_Deliverable_2026-11-10"
brain_dir = r"C:\Users\ABDUL\.gemini\antigravity\brain\00a7aa5b-5d32-449b-a3f6-925ffecf15c5"

with open(csv_path, "r", encoding="utf-8") as f:
    tickets = list(csv.DictReader(f))

# Define clean attribution according to the 5 leads
def classify_lead(t):
    key = t.get("Issue key", "")
    summary = t.get("Summary", "").lower()
    desc = t.get("Description", "").lower()
    msg = t.get("Git Commit Message", "").lower()
    text = f"{summary} {desc} {msg}"

    # 1. Ahmad Zahid (ML Triage, Safety Calibration, Repair Verifier, Fraud Detection, Abstention Gate)
    if any(k in text for k in [
        "triage", "cost-sensitive", "calibration", "platt", "ece", "abstention",
        "verifier", "nli", "fraud", "unnecessary", "brier", "k-fold", "section 17",
        "ethical", "confidence", "isolation forest", "hazard model"
    ]) or key in ["AUT-107", "AUT-107B", "AUT-108", "AUT-109", "AUT-112", "AUT-112B", "AUT-118", "AUT-132", "AUT-138", "AUT-139", "AUT-140", "AUT-141", "AUT-142", "AUT-143", "AUT-148", "AUT-153", "AUT-166", "AUT-210", "AUT-214"]:
        return "Ahmad Zahid (BSDSF23A033)", "EPIC-4: Supervised ML Triage & Verification"

    # 2. Abdullah (System Architect, Transformer LM, BPE, Consistent Hash, FastApi, Master Releases)
    if any(k in text for k in [
        "transformer", "bpe", "tokenizer", "rag-scratch", "causal", "autoregressive",
        "consistent hash", "hash ring", "murmur", "fastapi gateway", "routing architecture",
        "initial commit", "agents.md", "master repository", "argon2", "release", "rag base"
    ]) or key in ["AUT-095", "AUT-096", "AUT-097", "AUT-098", "AUT-104", "AUT-105", "AUT-121", "AUT-123", "AUT-124", "AUT-126", "AUT-128", "AUT-150", "AUT-172", "AUT-173", "AUT-174", "AUT-175", "AUT-204", "AUT-205", "AUT-206"]:
        return "Abdullah (BSDSF23A035)", "EPIC-2: Distributed Hashing & Transformer AI"

    # 3. Talha Ali Bhatti (Storage, MinIO, Parquet, Compaction, Ingestion, OBD-II Streamer, CAS)
    if any(k in text for k in [
        "minio", "s3", "cas deduplication", "deduplication", "obd-ii", "can-bus", "telemetry stream",
        "parquet", "lakehouse", "compaction", "batch buffer", "multipart", "iops", "quarantine",
        "dtc", "sae j2012", "schema evolution", "relational ddl", "storage", "media vault"
    ]) or key in ["AUT-099", "AUT-100", "AUT-101", "AUT-102", "AUT-108", "AUT-109", "AUT-110", "AUT-111", "AUT-112", "AUT-113", "AUT-147", "AUT-149", "AUT-151", "AUT-158", "AUT-160", "AUT-162", "AUT-164", "AUT-201", "AUT-202", "AUT-203"]:
        return "Talha Ali Bhatti (BSDSF23A016)", "EPIC-1: Distributed Object Storage & Ingestion"

    # 4. Danial Hameed (Data Engineering, Manuals Chunking, Bloom Filter, Bilingual Lexicon, Collectors)
    if any(k in text for k in [
        "bloom filter", "lexicon", "urdu", "roman urdu", "chunk", "dataset", "corpus",
        "manual", "youtube", "facebook", "whisper", "audio", "nhtsa", "stack exchange",
        "collector", "importer", "bm25", "rrf", "reciprocal rank", "media asset", "cleaning", "canonical"
    ]) or key in ["AUT-103", "AUT-106", "AUT-106B", "AUT-107", "AUT-115", "AUT-122", "AUT-125", "AUT-136", "AUT-137", "AUT-145", "AUT-146", "AUT-152", "AUT-154", "AUT-155", "AUT-157", "AUT-163", "AUT-167", "AUT-168", "AUT-169", "AUT-170", "AUT-171", "AUT-209", "AUT-213"]:
        return "Danial Hameed (BSDSF23A014)", "EPIC-3: Multilingual Data Lake & Ingestion"

    # 5. Muhammad Abdullah (Web Portal UI, DuckDB OLAP, PySpark, Regional PKR Pricing, Defense)
    return "Muhammad Abdullah (BSDSF23A032)", "EPIC-5: Modern Web Portal & Fleet Analytics"

# Rebalance tickets and harmonize keys
balanced_tickets = []
for t in tickets:
    assignee, epic = classify_lead(t)
    t["Assignee"] = assignee
    t["Epic Link"] = epic
    
    t["key"] = t.get("Issue key", "")
    t["summary"] = t.get("Summary", "")
    t["desc"] = t.get("Description", "")
    t["epic"] = t.get("Epic Link", "")
    t["sp"] = int(t.get("Story Points", 3) or 3)
    t["assignee"] = t.get("Assignee", "")
    t["status"] = t.get("Status", "Done")
    t["sprint"] = t.get("Sprint", "")
    t["commit_hash"] = t.get("Commit Hash", "")
    t["commit_msg"] = t.get("Git Commit Message", "")
    t["date"] = t.get("Resolved Date", "")
    
    balanced_tickets.append(t)

# Save updated CSV
fieldnames = [
    "Issue Type", "Issue key", "Summary", "Description", "Epic Link",
    "Story Points", "Assignee", "Reporter", "Priority", "Status",
    "Sprint", "Commit Hash", "Git Commit Message", "Resolved Date"
]
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for t in balanced_tickets:
        writer.writerow({
            "Issue Type": t.get("Issue Type", "Story"),
            "Issue key": t["key"],
            "Summary": t["summary"],
            "Description": t["desc"],
            "Epic Link": t["epic"],
            "Story Points": t["sp"],
            "Assignee": t["assignee"],
            "Reporter": t.get("Reporter", "Abdullah (BSDSF23A035)"),
            "Priority": t.get("Priority", "High"),
            "Status": t["status"],
            "Sprint": t["sprint"],
            "Commit Hash": t["commit_hash"],
            "Git Commit Message": t["commit_msg"],
            "Resolved Date": t["date"]
        })

print("[OK] Rebalanced CSV saved!")

counts = {}
sp_counts = {}
for t in balanced_tickets:
    n = t["assignee"].split()[0]
    counts[n] = counts.get(n, 0) + 1
    sp_counts[n] = sp_counts.get(n, 0) + t["sp"]

print("\n--- PERFECT 5-LEAD BALANCE RESULT ---")
for n in sorted(counts.keys()):
    print(f"  {n:15}: {counts[n]:2} tickets | {sp_counts[n]:3} Story Points")

# -------------------------------------------------------------
# Rebuild Interactive Jira App (JIRA_LOCAL_BOARD.html)
# -------------------------------------------------------------
from generate_jira_board_app import generate_jira_board_html
generate_jira_board_html()

# -------------------------------------------------------------
# Rebuild Word & PDF Backlog Reports
# -------------------------------------------------------------
from build_complete_100plus_jira import build_full_jira_docx, build_full_jira_pdf, build_full_jira_md

docx_path = os.path.join(base_dir, "AutoCare_AI_Jira_Workflow_Backlog.docx")
pdf_path = os.path.join(base_dir, "AutoCare_AI_Jira_Workflow_Backlog.pdf")
md_path = os.path.join(base_dir, "docs", "JIRA_AGILE_WORKFLOW.md")

build_full_jira_docx(balanced_tickets, docx_path)
build_full_jira_pdf(balanced_tickets, pdf_path)
build_full_jira_md(balanced_tickets, md_path)
shutil.copy2(md_path, os.path.join(base_dir, "JIRA_AGILE_WORKFLOW.md"))

# Sync to Desktop deliverables
targets = [
    (csv_path, os.path.join(desktop_dir, "jira_tickets_import.csv")),
    (csv_path, os.path.join(deliverable_dir, "jira_tickets_import.csv")),
    (docx_path, os.path.join(deliverable_dir, "AutoCare_AI_Jira_Workflow_Backlog.docx")),
    (pdf_path, os.path.join(deliverable_dir, "AutoCare_AI_Jira_Workflow_Backlog.pdf")),
    (docx_path, os.path.join(brain_dir, "AutoCare_AI_Jira_Workflow_Backlog.docx")),
    (pdf_path, os.path.join(brain_dir, "AutoCare_AI_Jira_Workflow_Backlog.pdf")),
    (md_path, os.path.join(deliverable_dir, "JIRA_AGILE_WORKFLOW.md")),
]
for src, dst in targets:
    shutil.copy2(src, dst)
    print(f"[SYNC] {src} -> {dst}")

print("\nAll Jira deliverables successfully rebalanced and regenerated!")
