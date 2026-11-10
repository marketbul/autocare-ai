# AI Auto Pakistan — Local Dataset Bundle (Zero-Port File Edition)
**Generated At (UTC):** 2026-11-10T18:34:11.522665+00:00

## Files Inside This Folder
* `dataset_viewer.html` — Double-click to browse, search, and filter all records directly in your browser (no localhost port needed).
* `owner_mechanic_qa_solutions.json` — Single consolidated YouTube Problem & Solution Q&A + Whisper transcript file (1654 YouTube records; 922 with proposed solutions).
* `online_mechanic_qa_solutions.json` — Stack Exchange Mechanics (CC-BY-SA) + NHTSA Complaints/Recalls Problem & Solution JSON (8820 records; 2973 with solutions/remedies).
* `facebook_qa_solutions.json` — Curated Facebook Community Q&A Problem & Solution file (0 Facebook records; add CSV/JSON files into `Facebook_Community_QA/` to populate).
* `ai_agent_knowledge.jsonl` — Structured AI-Agent RAG & Triage dataset (`is_verified_fact` boundary included).
* `master_dataset.json`, `master_dataset.jsonl`, `master_dataset.csv` — Complete cleaned records.
* `ml_splits/` — Leak-free `train.jsonl`, `val.jsonl`, `test.jsonl`, and `dataset_card.json`.
* `media_screenshots/` — Extracted diagnostic screenshots (14 file(s)).
* `audio_wav/` — Extracted 16kHz mono audio clips (5 file(s)).
* `youtube_raw/` — Raw YouTube Data API v3 metadata + comment JSON batches (61 file(s)).

## Current Honest Inventory
* **Total Real Records:** 10760
* **YouTube Videos Harvested:** 1654
* **Stack Exchange + NHTSA Records:** 8820
* **Facebook Curated Q&A Imported:** 0
* **YouTube API Key Configured:** True
* **Whisper Speech-to-Text Installed:** True
* **yt-dlp Installed (for Creative Commons / permitted videos):** True

## How to Run Full Automatic YouTube + Transcription + Damage Screenshots Into This Folder
```powershell
cd "C:\Users\ABDUL\.gemini\antigravity\scratch\autocare-us2\backend"
# Optional: install Whisper & yt-dlp once for CC-BY / permitted video audio-to-text:
# pip install faster-whisper yt-dlp

python -m data_engine.auto_collect_bundle --api-key YOUR_YOUTUBE_API_KEY --all-queries
```
