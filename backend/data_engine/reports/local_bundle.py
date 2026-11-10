"""Self-Contained Local Folder Bundle Exporter for AI Auto Pakistan (Zero Port Required).

Assembles all collected records, AI-Agent JSONL, ML splits, extracted screenshots,
audio WAV files, and an offline `dataset_viewer.html` (embedded JSON data so it works
directly via `file:///...` with no HTTP server or port needed) into one master folder:
    <repo_root>/AI_Auto_Pakistan_Dataset/
"""
from __future__ import annotations

import csv
import datetime as dt
import importlib.util
import json
import os
import shutil
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import get_config
from ..ml import AIAgentDatasetExporter
from ..storage import StorageManager


class LocalFolderBundleExporter:
    """Exports the complete dataset and offline viewer into one standalone folder."""

    def __init__(self, bundle_dir: Optional[Path] = None) -> None:
        self.config = get_config()
        self.repo_root = self.config.backend_root.parent
        self.bundle_dir = bundle_dir or (self.repo_root / "AI_Auto_Pakistan_Dataset")
        self.storage = StorageManager()

    def export_bundle(self) -> Dict[str, Any]:
        """Builds the entire standalone folder + offline dataset_viewer.html."""
        self.bundle_dir.mkdir(parents=True, exist_ok=True)
        splits_dir = self.bundle_dir / "ml_splits"
        shots_dir = self.bundle_dir / "media_screenshots"
        audio_dir = self.bundle_dir / "audio_wav"
        yt_raw_dir = self.bundle_dir / "youtube_raw"

        for d in [splits_dir, shots_dir, audio_dir, yt_raw_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # 1. Fetch real records & honest stats from DB
        records, total_real = self.storage.query_records(include_examples=False, limit=100000)
        stats = self.storage.get_dataset_statistics()

        # 2. Save Master JSON, JSONL, CSV
        master_json = self.bundle_dir / "master_dataset.json"
        master_json.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")

        master_jsonl = self.bundle_dir / "master_dataset.jsonl"
        master_jsonl.write_text(
            "\n".join(json.dumps(r, ensure_ascii=False) for r in records),
            encoding="utf-8",
        )

        master_csv = self.bundle_dir / "master_dataset.csv"
        if records:
            cols = [
                "record_id", "make", "model", "variant", "manufacturing_year",
                "fault_category_id", "category_name", "problem_title", "problem_description",
                "symptoms", "severity", "diagnosis_stage", "recommended_solution",
                "estimated_cost_pkr", "parts_cost_pkr", "labor_cost_pkr", "city",
                "source_id", "source_url", "language", "rights_basis", "human_review_status",
                "confidence_score", "collection_date",
            ]
            with open(master_csv, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
                writer.writeheader()
                for it in records:
                    row = dict(it)
                    row["symptoms"] = "; ".join(it.get("symptoms") or [])
                    writer.writerow(row)

        # 3. Export AI-Agent Ready JSONL directly into bundle
        agent_records = AIAgentDatasetExporter(storage=self.storage).build_agent_records(include_pending=True)
        agent_jsonl = self.bundle_dir / "ai_agent_knowledge.jsonl"
        agent_jsonl.write_text(
            "\n".join(json.dumps(r, ensure_ascii=False) for r in agent_records),
            encoding="utf-8",
        )

        # 4. Copy ML Splits
        if self.config.ml_ready_dir.exists():
            for f in self.config.ml_ready_dir.glob("*"):
                if f.is_file():
                    shutil.copy2(f, splits_dir / f.name)

        # 5. Copy Media Screenshots, Audio WAVs, and Raw YouTube JSONs
        img_src = self.config.media_vault_dir / "images"
        copied_images: List[str] = []
        if img_src.exists():
            for f in img_src.glob("*"):
                if f.is_file():
                    shutil.copy2(f, shots_dir / f.name)
                    copied_images.append(f.name)

        aud_src = self.config.media_vault_dir / "audio"
        copied_audio: List[str] = []
        if aud_src.exists():
            for f in aud_src.glob("*"):
                if f.is_file():
                    shutil.copy2(f, audio_dir / f.name)
                    copied_audio.append(f.name)

        yt_src = self.config.raw_dir / "youtube"
        copied_yt = 0
        raw_by_vid: Dict[str, Dict[str, Any]] = {}
        if yt_src.exists():
            for f in yt_src.glob("*.json"):
                if f.is_file():
                    shutil.copy2(f, yt_raw_dir / f.name)
                    copied_yt += 1
                    try:
                        payload = json.loads(f.read_text(encoding="utf-8"))
                        for item in payload.get("items", []):
                            vid = item.get("video_id")
                            if not vid:
                                continue
                            prev = raw_by_vid.get(vid)
                            if prev is None or len(item.get("comments") or []) > len(prev.get("comments") or []):
                                raw_by_vid[vid] = item
                    except Exception:
                        continue

        # 5b. Export consolidated YouTube, Facebook, and Open-API Q&A Problem & Solution JSON files
        qa_path, qa_summary = self._export_consolidated_qa_file(records, raw_by_vid)
        fb_qa_path, fb_qa_summary = self._export_facebook_qa_file(records)
        open_qa_path, open_qa_summary = self._export_online_qa_file(records)

        # 6. Check prerequisite tool / API key availability honestly
        env_status = {
            "youtube_api_key_set": bool(self.config.youtube_api_key or os.getenv("YOUTUBE_API_KEY", "").strip()),
            "yt_dlp_installed": importlib.util.find_spec("yt_dlp") is not None or shutil.which("yt-dlp") is not None,
            "whisper_installed": self._has_whisper(),
        }

        # 7. Write README_LOCAL_BUNDLE.md
        readme_path = self.bundle_dir / "README_LOCAL_BUNDLE.md"
        readme_path.write_text(
            self._build_readme(stats, env_status, len(copied_images), len(copied_audio), copied_yt, qa_summary, fb_qa_summary, open_qa_summary),
            encoding="utf-8",
        )

        # 8. Build zero-server offline HTML viewer (data embedded cleanly in HTML)
        viewer_path = self.bundle_dir / "dataset_viewer.html"
        viewer_path.write_text(
            self._build_offline_html(records, stats, env_status, copied_images, copied_audio),
            encoding="utf-8",
        )

        return {
            "bundle_dir": str(self.bundle_dir),
            "viewer_html": str(viewer_path),
            "viewer_file_url": viewer_path.as_uri(),
            "master_json": str(master_json),
            "master_jsonl": str(master_jsonl),
            "master_csv": str(master_csv),
            "ai_agent_knowledge": str(agent_jsonl),
            "qa_solutions_file": str(qa_path),
            "qa_solutions_summary": qa_summary,
            "facebook_qa_file": str(fb_qa_path),
            "facebook_qa_summary": fb_qa_summary,
            "online_qa_file": str(open_qa_path),
            "online_qa_summary": open_qa_summary,
            "total_records": total_real,
            "screenshots_copied": len(copied_images),
            "audio_files_copied": len(copied_audio),
            "youtube_raw_files_copied": copied_yt,
            "env_status": env_status,
        }

    def _export_consolidated_qa_file(
        self,
        records: List[Dict[str, Any]],
        raw_by_vid: Dict[str, Dict[str, Any]],
    ) -> tuple[Path, Dict[str, Any]]:
        """Writes one consolidated JSON file containing YouTube problem/solution Q&A and transcripts."""
        yt_records = [r for r in records if r.get("source_id") == "youtube_official_api"]
        consolidated: List[Dict[str, Any]] = []
        makes_counter: Counter[str] = Counter()
        models_counter: Counter[str] = Counter()

        for rec in yt_records:
            rid = rec.get("record_id", "")
            vid = rid[3:] if rid.startswith("yt_") else rid
            raw = raw_by_vid.get(vid, {})

            desc = rec.get("problem_description") or ""
            whisper_text: Optional[str] = None
            if "[Whisper Transcript]:" in desc:
                whisper_text = desc.split("[Whisper Transcript]:", 1)[1].split("\n\n", 1)[0].strip()

            qa_threads: List[Dict[str, Any]] = []
            owner_questions: List[str] = list(raw.get("extracted_problem_comments") or [])
            solutions: List[str] = []
            if rec.get("recommended_solution"):
                solutions.append(rec["recommended_solution"])

            for c in raw.get("comments") or []:
                c_text = (c.get("text") or "").strip()
                c_intent = c.get("intent") or "discussion"
                replies = [
                    {"text": (rp.get("text") or "").strip(), "intent": rp.get("intent") or "discussion"}
                    for rp in (c.get("replies") or [])
                    if (rp.get("text") or "").strip()
                ]
                if c_intent == "problem_occurrence" and c_text and c_text not in owner_questions:
                    owner_questions.append(c_text)
                if c_intent in {"suggested_solution", "solution_with_cost"} and c_text and c_text not in solutions:
                    solutions.append(c_text)
                for rp in replies:
                    if rp["intent"] in {"suggested_solution", "solution_with_cost"} and rp["text"] not in solutions:
                        solutions.append(rp["text"])
                if c_text and (c_intent != "discussion" or replies):
                    qa_threads.append({
                        "comment": c_text,
                        "intent": c_intent,
                        "replies": replies,
                    })

            make = rec.get("make") or "Generic"
            model = rec.get("model") or "Multi-Model"
            makes_counter[make] += 1
            models_counter[f"{make} {model}".strip()] += 1

            img_ref = rec.get("image_reference")
            aud_ref = rec.get("audio_reference")
            local_shot = (
                f"media_screenshots/{Path(img_ref).name}"
                if img_ref and not str(img_ref).startswith("http")
                else None
            )
            consolidated.append({
                "record_id": rid,
                "video_id": vid,
                "make": make,
                "model": model,
                "fault_category_id": rec.get("fault_category_id"),
                "category_name": rec.get("category_name"),
                "problem_title": rec.get("problem_title"),
                "problem_description": desc,
                "whisper_transcript": whisper_text,
                "owner_problem_questions": owner_questions,
                "mechanic_and_community_solutions": solutions,
                "qa_threads": qa_threads,
                "estimated_cost_pkr": rec.get("estimated_cost_pkr"),
                "language": rec.get("language"),
                "license": raw.get("license") or rec.get("rights_basis"),
                "verification_status": rec.get("verification_status") or "unverified",
                "human_review_status": rec.get("human_review_status"),
                "audio_file": f"audio_wav/{Path(aud_ref).name}" if aud_ref else None,
                "screenshot_file": local_shot,
                "source_url": rec.get("source_url"),
            })

        consolidated.sort(
            key=lambda x: (
                1 if x["whisper_transcript"] else 0,
                1 if x["mechanic_and_community_solutions"] else 0,
                len(x["qa_threads"]),
            ),
            reverse=True,
        )

        summary = {
            "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "total_youtube_records": len(consolidated),
            "with_owner_problem_questions": sum(1 for x in consolidated if x["owner_problem_questions"]),
            "with_solutions": sum(1 for x in consolidated if x["mechanic_and_community_solutions"]),
            "with_qa_threads": sum(1 for x in consolidated if x["qa_threads"]),
            "with_whisper_transcript": sum(1 for x in consolidated if x["whisper_transcript"]),
            "with_audio_wav": sum(1 for x in consolidated if x["audio_file"]),
            "with_screenshot": sum(1 for x in consolidated if x["screenshot_file"]),
            "makes_breakdown": dict(makes_counter.most_common()),
            "top_models_breakdown": dict(models_counter.most_common(25)),
            "verification_note": "Public YouTube comments and transcripts represent unverified claims until validated by an automotive technician.",
        }

        out_path = self.bundle_dir / "owner_mechanic_qa_solutions.json"
        out_path.write_text(
            json.dumps({"summary": summary, "records": consolidated}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return out_path, summary

    def _export_facebook_qa_file(
        self,
        records: List[Dict[str, Any]],
    ) -> tuple[Path, Dict[str, Any]]:
        """Writes a consolidated JSON file for curated Facebook community Q&A records."""
        fb_records = [r for r in records if r.get("source_id") == "facebook_research_import"]
        makes_counter: Counter[str] = Counter()
        models_counter: Counter[str] = Counter()
        items: List[Dict[str, Any]] = []

        for rec in fb_records:
            make = rec.get("make") or "Generic"
            model = rec.get("model") or "Multi-Model"
            makes_counter[make] += 1
            models_counter[f"{make} {model}".strip()] += 1
            items.append({
                "record_id": rec.get("record_id"),
                "make": make,
                "model": model,
                "variant": rec.get("variant"),
                "manufacturing_year": rec.get("manufacturing_year"),
                "fault_category_id": rec.get("fault_category_id"),
                "category_name": rec.get("category_name"),
                "problem_title": rec.get("problem_title"),
                "problem_description": rec.get("problem_description"),
                "symptoms": rec.get("symptoms") or [],
                "proposed_solution": rec.get("recommended_solution"),
                "estimated_cost_pkr": rec.get("estimated_cost_pkr"),
                "city": rec.get("city"),
                "language": rec.get("language"),
                "verification_status": rec.get("verification_status") or "unverified",
                "human_review_status": rec.get("human_review_status"),
                "source_url": rec.get("source_url"),
            })

        summary = {
            "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "total_facebook_records": len(items),
            "with_solutions": sum(1 for x in items if x["proposed_solution"]),
            "makes_breakdown": dict(makes_counter.most_common()),
            "top_models_breakdown": dict(models_counter.most_common(25)),
            "input_folder": str(self.repo_root / "Facebook_Community_QA"),
            "verification_note": "Community Facebook Q&A records imported from curated public discussions; rows remain unverified unless human-approved.",
        }

        out_path = self.bundle_dir / "facebook_qa_solutions.json"
        out_path.write_text(
            json.dumps({"summary": summary, "records": items}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return out_path, summary

    def _export_online_qa_file(
        self,
        records: List[Dict[str, Any]],
    ) -> tuple[Path, Dict[str, Any]]:
        """Writes a consolidated JSON file for Stack Exchange Mechanics Q&A & NHTSA records."""
        open_sources = {"stackexchange_mechanics", "nhtsa_official_api"}
        open_records = [r for r in records if r.get("source_id") in open_sources]
        makes_counter: Counter[str] = Counter()
        source_counter: Counter[str] = Counter()
        items: List[Dict[str, Any]] = []

        for rec in open_records:
            make = rec.get("make") or "Generic"
            model = rec.get("model") or "Multi-Model"
            src = rec.get("source_id") or "open_api"
            makes_counter[make] += 1
            source_counter[src] += 1
            items.append({
                "record_id": rec.get("record_id"),
                "source_id": src,
                "make": make,
                "model": model,
                "manufacturing_year": rec.get("manufacturing_year"),
                "fault_category_id": rec.get("fault_category_id"),
                "category_name": rec.get("category_name"),
                "problem_title": rec.get("problem_title"),
                "problem_description": rec.get("problem_description"),
                "symptoms": rec.get("symptoms") or [],
                "recommended_solution": rec.get("recommended_solution"),
                "repair_steps": rec.get("repair_steps") or [],
                "verification_status": rec.get("verification_status") or "unverified",
                "rights_basis": rec.get("rights_basis"),
                "source_url": rec.get("source_url"),
            })

        items.sort(key=lambda x: (1 if x["recommended_solution"] else 0, x["source_id"]), reverse=True)
        summary = {
            "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "total_records": len(items),
            "by_source": dict(source_counter),
            "with_solutions": sum(1 for x in items if x["recommended_solution"]),
            "makes_breakdown": dict(makes_counter.most_common()),
        }

        out_path = self.bundle_dir / "online_mechanic_qa_solutions.json"
        out_path.write_text(
            json.dumps({"summary": summary, "records": items}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return out_path, summary

    @staticmethod
    def _has_whisper() -> bool:
        for mod in ("faster_whisper", "whisper"):
            try:
                __import__(mod)
                return True
            except ImportError:
                continue
        return False

    def _build_readme(
        self,
        stats: Dict[str, Any],
        env_status: Dict[str, bool],
        img_count: int,
        aud_count: int,
        yt_files: int,
        qa_summary: Dict[str, Any],
        fb_qa_summary: Dict[str, Any],
        open_qa_summary: Dict[str, Any],
    ) -> str:
        return f"""# AI Auto Pakistan — Local Dataset Bundle (Zero-Port File Edition)
**Generated At (UTC):** {dt.datetime.now(dt.timezone.utc).isoformat()}

## Files Inside This Folder
* `dataset_viewer.html` — Double-click to browse, search, and filter all records directly in your browser (no localhost port needed).
* `owner_mechanic_qa_solutions.json` — Single consolidated YouTube Problem & Solution Q&A + Whisper transcript file ({qa_summary['total_youtube_records']} YouTube records; {qa_summary['with_solutions']} with proposed solutions).
* `online_mechanic_qa_solutions.json` — Stack Exchange Mechanics (CC-BY-SA) + NHTSA Complaints/Recalls Problem & Solution JSON ({open_qa_summary['total_records']} records; {open_qa_summary['with_solutions']} with solutions/remedies).
* `facebook_qa_solutions.json` — Curated Facebook Community Q&A Problem & Solution file ({fb_qa_summary['total_facebook_records']} Facebook records; add CSV/JSON files into `Facebook_Community_QA/` to populate).
* `ai_agent_knowledge.jsonl` — Structured AI-Agent RAG & Triage dataset (`is_verified_fact` boundary included).
* `master_dataset.json`, `master_dataset.jsonl`, `master_dataset.csv` — Complete cleaned records.
* `ml_splits/` — Leak-free `train.jsonl`, `val.jsonl`, `test.jsonl`, and `dataset_card.json`.
* `media_screenshots/` — Extracted diagnostic screenshots ({img_count} file(s)).
* `audio_wav/` — Extracted 16kHz mono audio clips ({aud_count} file(s)).
* `youtube_raw/` — Raw YouTube Data API v3 metadata + comment JSON batches ({yt_files} file(s)).

## Current Honest Inventory
* **Total Real Records:** {stats['real_records_count']}
* **YouTube Videos Harvested:** {stats['real_by_source'].get('youtube_official_api', 0)}
* **Stack Exchange + NHTSA Records:** {open_qa_summary['total_records']}
* **Facebook Curated Q&A Imported:** {fb_qa_summary['total_facebook_records']}
* **YouTube API Key Configured:** {env_status['youtube_api_key_set']}
* **Whisper Speech-to-Text Installed:** {env_status['whisper_installed']}
* **yt-dlp Installed (for Creative Commons / permitted videos):** {env_status['yt_dlp_installed']}

## How to Run Full Automatic YouTube + Transcription + Damage Screenshots Into This Folder
```powershell
cd "C:\\Users\\ABDUL\\.gemini\\antigravity\\scratch\\autocare-us2\\backend"
# Optional: install Whisper & yt-dlp once for CC-BY / permitted video audio-to-text:
# pip install faster-whisper yt-dlp

python -m data_engine.auto_collect_bundle --api-key YOUR_YOUTUBE_API_KEY --all-queries
```
"""

    def _build_offline_html(
        self,
        records: List[Dict[str, Any]],
        stats: Dict[str, Any],
        env_status: Dict[str, bool],
        images: List[str],
        audios: List[str],
    ) -> str:
        embedded_payload = json.dumps(
            {
                "stats": stats,
                "env_status": env_status,
                "images": images,
                "audios": audios,
                "records": records,
            },
            ensure_ascii=False,
        ).replace("</", "<\\/")

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AI Auto Pakistan — Offline Local Dataset Viewer</title>
  <style>
    :root {{ --bg:#f4f6f9; --surface:#fff; --border:#e2e8f0; --text:#0f172a; --muted:#475569; --primary:#0f766e; }}
    * {{ box-sizing:border-box; margin:0; padding:0; }}
    body {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif; background:var(--bg); color:var(--text); line-height:1.5; }}
    header {{ background:#0f172a; color:#fff; padding:18px 26px; }}
    header h1 {{ font-size:1.3rem; }}
    header p {{ font-size:0.84rem; color:#cbd5e1; margin-top:4px; }}
    main {{ max-width:1360px; margin:20px auto; padding:0 20px 50px; }}
    .banner {{ background:#fffbeb; border:1px solid #fde68a; color:#92400e; padding:12px 16px; border-radius:8px; margin-bottom:16px; font-size:0.86rem; }}
    .kpis {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(185px,1fr)); gap:12px; margin-bottom:18px; }}
    .kpi {{ background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:12px 14px; }}
    .kpi .lbl {{ font-size:0.75rem; color:var(--muted); text-transform:uppercase; font-weight:700; }}
    .kpi .val {{ font-size:1.55rem; font-weight:700; margin-top:2px; }}
    .card {{ background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:16px; margin-bottom:18px; }}
    .filters {{ display:flex; flex-wrap:wrap; gap:10px; margin-bottom:14px; }}
    input, select {{ border:1px solid #cbd5e1; border-radius:6px; padding:7px 10px; font-size:0.84rem; }}
    table {{ width:100%; border-collapse:collapse; font-size:0.83rem; }}
    th, td {{ padding:9px 10px; border-bottom:1px solid var(--border); text-align:left; vertical-align:top; }}
    th {{ background:#f8fafc; color:var(--muted); font-size:0.75rem; text-transform:uppercase; }}
    .badge {{ display:inline-block; padding:2px 7px; border-radius:999px; font-size:0.72rem; font-weight:700; background:#e2e8f0; color:#334155; }}
    .badge.ok {{ background:#dcfce7; color:#15803d; }}
    .gallery {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:12px; }}
    .shot {{ border:1px solid var(--border); border-radius:8px; overflow:hidden; background:#fff; }}
    .shot img {{ width:100%; height:140px; object-fit:cover; display:block; }}
    .shot div {{ padding:8px; font-size:0.78rem; word-break:break-all; }}
  </style>
</head>
<body>
  <header>
    <h1>AI Auto Pakistan — Offline Local Dataset Folder Viewer (No Port Required)</h1>
    <p>Loaded directly from local disk files • Master JSONL, <a href="owner_mechanic_qa_solutions.json" target="_blank" style="color:#5eead4;">YouTube Q&amp;A JSON</a>, <a href="online_mechanic_qa_solutions.json" target="_blank" style="color:#5eead4;">StackExchange/NHTSA Q&amp;A JSON</a>, <a href="facebook_qa_solutions.json" target="_blank" style="color:#5eead4;">Facebook Q&amp;A JSON</a>, AI-Agent RAG JSONL &amp; Media</p>
  </header>
  <main>
    <div class="banner" id="blocker-banner"></div>
    <div class="kpis" id="kpis"></div>

    <div class="card">
      <h2 style="font-size:1.02rem; margin-bottom:10px;">Extracted Damage Screenshots (<span id="shot-cnt">0</span>)</h2>
      <div class="gallery" id="shot-gallery"></div>
    </div>

    <div class="card">
      <h2 style="font-size:1.02rem; margin-bottom:10px;">Dataset Records Explorer (<span id="row-cnt">0</span>)</h2>
      <div class="filters">
        <input id="q" placeholder="Search symptoms, problem, Urdu/Roman Urdu..." style="min-width:250px;" oninput="renderTable()" />
        <select id="f-src" onchange="renderTable()"><option value="">All Sources</option></select>
        <select id="f-lang" onchange="renderTable()">
          <option value="">All Languages</option>
          <option value="en">English</option>
          <option value="ur">Urdu</option>
          <option value="roman_ur">Roman Urdu</option>
          <option value="punjabi">Punjabi</option>
        </select>
        <select id="f-cat" onchange="renderTable()"><option value="">All Fault Categories</option></select>
      </div>
      <div style="overflow-x:auto;">
        <table>
          <thead>
            <tr>
              <th>Vehicle</th>
              <th>Problem &amp; Symptoms</th>
              <th>Category</th>
              <th>Lang</th>
              <th>Solution / Repair</th>
              <th>Cost (PKR)</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody id="tbody"></tbody>
        </table>
      </div>
    </div>
  </main>

  <script>
    const DATA = {embedded_payload};
    const s = DATA.stats;
    const e = DATA.env_status;

    const gaps = [];
    if (!e.youtube_api_key_set) gaps.push("YOUTUBE_API_KEY not set");
    if (!e.whisper_installed) gaps.push("faster-whisper/whisper not installed (for audio-to-text)");
    if (!e.yt_dlp_installed) gaps.push("yt-dlp not installed (for Creative Commons permitted clips)");

    document.getElementById("blocker-banner").innerHTML = gaps.length
      ? "<strong>External YouTube/Video Prerequisites Missing:</strong> " + gaps.join(" • ") +
        "<br>Current YouTube/screenshot counts accurately show <strong>0</strong>. Local verified project datasets (<strong>" +
        s.real_records_count + " records</strong>) are loaded below."
      : "<strong>All Pipeline Tools Ready:</strong> YouTube API Key, Whisper STT, and media tools detected.";

    const kpis = [
      ["Real Records", s.real_records_count],
      ["YouTube Videos", s.real_by_source.youtube_official_api || 0],
      ["StackExchange Q&A", s.real_by_source.stackexchange_mechanics || 0],
      ["NHTSA Safety", s.real_by_source.nhtsa_official_api || 0],
      ["Facebook Q&As", s.real_by_source.facebook_research_import || 0],
      ["Manuals & OBD-II", s.real_by_source.manuals_and_bulletins || 0],
      ["Symptom Corpus", s.real_by_source.starter_symptom_corpus || 0],
      ["PKR Price Refs", s.real_by_source.pakistan_price_reference || 0],
      ["Screenshots", DATA.images.length],
      ["Audio WAVs", DATA.audios.length],
      ["Fleet Models", s.distinct_vehicle_models_covered],
    ];
    document.getElementById("kpis").innerHTML = kpis.map(([l, v]) =>
      `<div class="kpi"><div class="lbl">${{l}}</div><div class="val">${{v}}</div></div>`
    ).join("");

    document.getElementById("shot-cnt").textContent = DATA.images.length;
    document.getElementById("shot-gallery").innerHTML = DATA.images.length
      ? DATA.images.map(name => `<div class="shot"><img src="media_screenshots/${{name}}" alt="${{name}}" /><div>${{name}}</div></div>`).join("")
      : `<p style="color:var(--muted); font-size:0.84rem;">0 screenshots extracted yet (requires permitted/Creative Commons video + Whisper/transcript timestamps).</p>`;

    const srcs = [...new Set(DATA.records.map(r => r.source_id).filter(Boolean))].sort();
    const cats = [...new Set(DATA.records.map(r => r.fault_category_id).filter(Boolean))].sort();
    document.getElementById("f-src").innerHTML += srcs.map(x => `<option value="${{x}}">${{x}}</option>`).join("");
    document.getElementById("f-cat").innerHTML += cats.map(x => `<option value="${{x}}">${{x}}</option>`).join("");

    function renderTable() {{
      const q = document.getElementById("q").value.trim().toLowerCase();
      const src = document.getElementById("f-src").value;
      const lang = document.getElementById("f-lang").value;
      const cat = document.getElementById("f-cat").value;

      const filtered = DATA.records.filter(r => {{
        if (src && r.source_id !== src) return false;
        if (lang && r.language !== lang) return false;
        if (cat && r.fault_category_id !== cat) return false;
        if (q) {{
          const hay = (r.problem_title + " " + r.problem_description + " " + (r.make||"") + " " + (r.model||"")).toLowerCase();
          if (!hay.includes(q)) return false;
        }}
        return true;
      }});

      document.getElementById("row-cnt").textContent = filtered.length + " / " + DATA.records.length + (filtered.length > 1000 ? " (showing top 1000)" : "");
      document.getElementById("tbody").innerHTML = filtered.slice(0, 1000).map(r => {{
        const imgLink = r.image_reference ? (r.image_reference.startsWith("http") ? `<br><a href="${{r.image_reference}}" target="_blank" style="color:#475569;font-size:0.75rem;">[Thumbnail]</a>` : `<br><a href="media_screenshots/${{r.image_reference.split('/').pop()}}" target="_blank" style="color:#0f766e;font-size:0.75rem;">[View Screenshot]</a>`) : "";
        const audLink = r.audio_reference ? ` <a href="audio_wav/${{r.audio_reference.split('/').pop()}}" target="_blank" style="color:#1d4ed8;font-size:0.75rem;">[Audio WAV]</a>` : "";
        const urlLink = r.source_url && r.source_url.startsWith("http") ? `<br><a href="${{r.source_url}}" target="_blank" style="color:#1d4ed8;font-size:0.74rem;">${{r.source_url.slice(0,36)}}...</a>` : "";
        return `
        <tr>
          <td><strong>${{r.make || ""}} ${{r.model || ""}}</strong><br><span style="color:var(--muted)">${{r.manufacturing_year || ""}}</span></td>
          <td><strong>${{r.problem_title}}</strong><br><span style="color:var(--muted)">${{(r.problem_description || "").slice(0, 180)}}</span>${{imgLink}}${{audLink}}</td>
          <td><span class="badge">${{r.fault_category_id || "—"}}</span></td>
          <td><span class="badge">${{r.language}}</span></td>
          <td style="font-size:0.78rem;">${{r.recommended_solution ? r.recommended_solution.slice(0, 160) : "—"}}</td>
          <td>${{r.estimated_cost_pkr != null ? "Rs. " + Number(r.estimated_cost_pkr).toLocaleString() : "—"}}</td>
          <td style="font-size:0.78rem;">${{r.source_id}}${{urlLink}}</td>
        </tr>`;
      }}).join("");
    }}
    renderTable();
  </script>
</body>
</html>
"""
