# AutoCare AI: User Stories 1–4 and 12

Story 1 (vehicle profile), Story 2 (ask a diagnostic question in EN / UR / Roman UR), Story 3 (fault code typed or read from a scanner photo), Story 4 (fault category + urgency, module M2) and Story 12 (damage photos → severity + body area, module M10, with an interim assessor).
Scope: Toyota Corolla, model years 2014–2025. Full slice through L2 retrieval, L3 classification, L4 abstention, and L5 FastAPI + React.

```
backend/
  autocare/
    config.py       settings + supported vehicles (Corolla 2014–2025)
    db.py           one SQL dialect for PostgreSQL and SQLite
    repository.py   all SQL; table/column names = ER diagram
    language.py     en / ur / roman_ur detection + cross-lingual query expansion
    text.py         tokeniser, DTC regex (P0301 etc.)
    bm25.py         keyword retrieval
    ml.py           BGE-M3 embedder + BGE reranker (and dev-only "lite" stand-ins)
    retrieval.py    profile filter -> hybrid -> exact-DTC guard -> rerank -> evidence gate
    generation.py   LLM returns JSON claims tied to evidence ids
    validation.py   citation validation (drops uncited / unsupported claims)
    triage.py       Story 4 / M2: category + urgency classifier, Critical-first rule, safety rules
    scan.py         Story 3: read codes from a scanner photo (vision model or Tesseract)
    accounts.py     roles, Story 1 garage, history, mechanic notes, admin
    service.py      orchestration + abstention + DiagnosticCase logging
    schemas.py      API contract (pydantic)
    api.py          POST /api/v1/diagnose/query
  ingest/           seed vehicles, load DTC reference, chunk owner-manual PDFs, train_triage
  data/symptom_labels.starter.csv   starter M2 training set (69 symptoms x 3 languages)
  sql/              schema.postgres.sql (pgvector) / schema.sqlite.sql
  tests/            one test class per acceptance criterion
frontend/src/
  api/diagnose.js
  components/DiagnosticQuery.jsx + .css
```

## Acceptance criteria → code → test

| AC | Requirement | Where | Test class |
|---|---|---|---|
| AC0 | No active profile → prompt to register | `service.py` raises `VehicleProfileRequired` → HTTP 428 | `AC0_ProfileRequired` |
| AC1 | Retrieve from *my* vehicle's manual + DTC ref; answer in my language | `repository.chunks_in_scope`, `language.detect_language`, prompt language rule | `AC1_RetrieveAndAnswerInSameLanguage` (incl. Civic-contamination test) |
| AC2 | Every claim cites document + section + page; none without | `validation.py` + server-rendered citations | `AC2_EveryClaimCited` |
| AC3 | Exact DTC matched, not similar codes | `retrieval.py` exact-DTC guard; one chunk per code | `AC3_ExactCodeMatch` |
| AC4 | Mixed Roman Urdu + English works | `language.py` marker words + glossary expansion | `AC4_MixedRomanUrduEnglish` |
| AC5 | No strong match → say so, don't generate | evidence gate in `retrieval.py`; LLM never called | `AC5_AbstainWithoutEvidence` |

### Story 1: Register vehicle profile (`tests/test_us1_acceptance.py`)

| AC | Requirement | Where |
|---|---|---|
| 1 | Save make/model/variant/year as the profile; it scopes every answer | `accounts.add_vehicle`, `repository.chunks_in_scope` |
| 2 | Out-of-scope vehicles shown as unsupported, can't be set | `accounts.catalog` (also lists Honda Civic / Suzuki Swift from the proposal, greyed out), `add_vehicle` refuses |
| 3 | Update mileage without re-entering the profile | `accounts.update_vehicle` (sets `last_reading_date`; a lower reading needs "save as correction") |
| 4 | Several cars, separate histories | `uservehicle` per car; `my_cases` grouped by car |
| 5 | No profile → prompt to register | `VehicleProfileRequired` → HTTP 428 → "Add or choose your car" |

Also stored: `registration_year` and `usage_profile` (city / highway / mixed) from the ER diagram, for M7 later.

### Story 3: Fault code typed or read from a photo (`tests/test_us3_acceptance.py`)

| AC | Requirement | Where |
|---|---|---|
| 1 | Typed code → matching reference entry with citation | exact-DTC guard (Story 2) |
| 2 | Photo → code extracted → same lookup as typed | `POST /api/v1/diagnose/read-code` → owner confirms → `/diagnose/query` with `code_source: "photo"` |
| 3 | Blurry / low confidence → ask to retype or retake, never guess | `scan.READ_THRESHOLD = 0.80`; an unclear read returns **no** codes |
| 4 | Code not in reference → say so, lower confidence | "code not found" message (Story 2) + triage confidence × 0.7 and marked unsure |

How confidence is measured: the **vision** reader (default) reads the photo twice with two different instructions ("list the codes" and "transcribe the screen") and only trusts codes both reads agree on. The model's own "I'm sure" is not used. The **tesseract** reader uses Tesseract's per-word confidence. If a letter had to be read as a digit (O→0), confidence drops. The photo is never stored.

### Story 4: Fault category and urgency, M2 (`tests/test_us4_acceptance.py`)

| AC | Requirement | Where |
|---|---|---|
| 1 | One category + one of Low/Moderate/High/Critical; saved to `diagnosticcase.predicted_category/predicted_urgency` | `triage.TriageClassifier`, `service._classify` |
| 2 | Critical → "Stop driving immediately — seek assistance; do not continue the journey" first | `URGENCY_ACTION`; React shows it at the top of the answer |
| 3 | Low → "Schedule this at your next convenient service.", no alarming words | `URGENCY_ACTION` |
| 4 | Ambiguous → lower confidence, not false certainty | `uncertain` when top < 0.55 or margin < 0.20; alternatives listed |
| 5 | Same symptom in EN / UR / Roman UR → same labels | multilingual BGE-M3 features + the LLM's English rendering averaged in |

How it decides:
1. **Classifier.** Logistic regression over [character TF-IDF | BGE-M3 embedding]. This is the "lightweight multilingual" option. A fine-tuned transformer (the proposal's primary model) can replace `TriageModel` later behind the same interface. `--baseline` runs TF-IDF + gradient boosting for the comparison table.
2. **Critical-first rule.** Critical wins whenever P(critical) ≥ a threshold tuned on grouped out-of-fold predictions for 95 % Critical recall. If that target can't be met, the threshold is picked by cost, with a missed Critical counting as 5 false alarms. It never goes below 0.15.
3. **Safety rules** (`triage.SAFETY_RULES`) for brake failure, red brake light, smoke/fire, burning wiring, fuel leak, oil pressure, overheating, steering lock, and tyre burst/loose wheel, in all three languages. They can only *raise* urgency. **A mechanic should review this list.**
4. A code's `severity` in `diagnosticcode` is a floor. For a bare code, the category comes from the code's `system` (or its SAE J2012 group), and the urgency is marked unsure if the reference has no severity.
5. If the answer abstains, no label is shown (Story 5 rule). Only a safety-rule warning still appears.

**Training data.** `data/symptom_labels.starter.csv` was **written by the developer** (`synthesised=yes`, `reviewed=no`): 69 symptoms × 3 languages. It's enough to run the system, **not to report results**. The team should label the real set as `data/symptom_labels.csv`, with the same columns and one `group_id` per symptom across its translations. Then run:
```
python -m ingest.train_triage --with-dtc --baseline
```
This prints grouped-CV accuracy, the **Critical false-negative rate** on its own line (§11.3), per-language accuracy and cross-language consistency, and saves `models/triage.pkl` + `triage_report.json`. The API retrains by itself on start if the CSV or the embedding model changed.

`diagnosticcase.confidence` currently holds the **raw** classifier probability. Story 5 replaces it with the calibrated score.

### Story 12: Damage photos → severity and body area, M10 (`tests/test_us12_acceptance.py`)

| AC | Requirement | Where |
|---|---|---|
| 1 | 1–4 photos → Minor / Moderate / Severe + body area | `damage.DamageService`; result = worst trusted photo, all trusted areas; saved in `damageimage` |
| 2 | Workshop repair → verifier uses image evidence | **Not yet**: needs Story 7 (verifier). `damageimage` rows link to the case so the verifier can read them |
| 3 | Always say an inspection can find more | `INSPECTION_NOTE`, shown on every result |
| 4 | Unclear photos → inconclusive, no confident label | each photo assessed twice with differently worded prompts; a label is only used when both agree (≥ 0.70) |
| 5 | Asked about cost / fault → decline | `asks_out_of_scope` (EN / Roman UR / UR) adds the refusal; the result never contains cost or fault |

**The assessor is interim.** It's the vision model on your Groq endpoint, working zero-shot with the severity definitions in `docs/damage_labelling_protocol.md`. The proposal's M10 is a fine-tuned ResNet/EfficientNet trained on a labelled image set (ML lead). It plugs in by implementing `assess(image, mime) -> PhotoAssessment`. Report the vision model only as a baseline. Photos are **not stored** (`file_ref` = NULL) until the consent process for keeping them exists.

## Run the tests (no downloads, no API key)

```bash
cd backend
PYTHONPATH=.:tests python -m unittest discover -s tests -v      # 99 tests (4 need the Tesseract program; skipped without it)
```
Test corpus passages are made-up fixtures, not real Toyota text.

## Quick local run (SQLite + lite models)

```bash
cd backend
pip install -r requirements.txt
export AUTOCARE_DATABASE_URL=sqlite:///autocare.db AUTOCARE_ML_BACKEND=lite AUTOCARE_GENERATION_MODE=extractive

cp data/vehicles_corolla.template.csv data/vehicles_corolla.csv   # then fill variant/engine from spec sheets
python -m ingest.seed_vehicles vehicles --csv data/vehicles_corolla.csv
python -m ingest.dtc_ingest --csv data/obd2_codes.csv \
    --document-name "SAE J2012 OBD-II Generic Codes" --source "<url>" --license-note "<terms>"
python -m ingest.pdf_ingest --pdf manuals/corolla_2018.pdf --manufacturer Toyota --model Corolla \
    --years 2018 --document-name "Corolla 2018 Owner's Manual" --source "<url>" \
    --license-note "Manufacturer owner's manual" --page-offset 0
python -m ingest.create_user --role admin --name "Your Name" --email you@example.com   # asks for a password
python -m uvicorn autocare.api:app --reload
```

## Real setup (what the evaluation should use)

1. PostgreSQL with pgvector: `psql -f sql/schema.postgres.sql`.
2. `AUTOCARE_ML_BACKEND=models` downloads BGE-M3 and bge-reranker-v2-m3 (about 2.5 GB). A GPU helps, but CPU works.
3. `AUTOCARE_GENERATION_MODE=llm` needs an OpenAI-compatible endpoint. Groq's free tier, OpenAI, or a local Ollama all work (see `.env.example`). Urdu and Roman Urdu answers need this mode.
4. Re-run ingestion **with the same embedding model** you serve with. The API refuses mismatched embedding sizes.
5. Start the API with `python -m uvicorn autocare.api:app --env-file .env`. Ingestion scripts read the shell environment: `set -a; source .env; set +a`.

`--page-offset` makes citations match the page numbers **printed** in the manual: printed = physical − offset. Check one page by hand per manual.

## API

`POST /api/v1/diagnose/query` with `{"user_vehicle_id": "...", "query": "brake se awaz aati hai"}`

* `200`: `status: "answered" | "abstained"`, `claims[]` (each has ≥1 citation number), `citations[]` (document_name, section, page_number, excerpt), `abstention`, `retrieved_but_insufficient[]`, `notices[]`, `signals` (inputs for M3), `disclaimer`.
* `428 vehicle_profile_required`, `422 unsupported_vehicle`, `502 generation_failed`. The message is in the query's language.

## React app

**No Node.js needed to run it.** `frontend/dist/` is already built, and the API serves it.
Start the API, then open **http://localhost:8000/app/** (or just http://localhost:8000/).

- Sign in (or create an owner account). What you see depends on your role.
- Each answer shows three status lamps (your car only, lines verified, evidence strength) and a "How this answer was checked" trace (proposal M4). Evidence strength is the raw reranker score, not a calibrated confidence (M3, Story 5).
- Branding (emblem, favicon) comes from `frontend/public/`.
- Urdu answers render right-to-left in Noto Nastaliq Urdu; citations stay left-to-right.

## Roles

| Role | Screens | How you get it |
|---|---|---|
| **Car owner** | Ask AutoCare, My cars (Story 1: add car, mileage), History | Sign up in the app |
| **Mechanic** | Share advice (sent for review, needs consent), My advice | An admin promotes the account |
| **Admin** | Overview (per-language answer rate, §11.1), Mechanic notes (approve/reject), Manuals & sources, Users & roles, plus the owner screens for testing | `python -m ingest.create_user --role admin ...` |

Only modules with a working backend have screens. M2–M10 (OBD-II live data, prediction, maintenance, etc.) get screens when their backend exists.

Security: passwords use PBKDF2-SHA256 (240k iterations); sessions are HMAC-signed tokens valid 7 days. Set `AUTOCARE_SECRET_KEY` in production; otherwise a random key is saved to `backend/.secret_key` (git-ignored). The role is re-read from the database on every request, so a demotion takes effect at once.

Endpoints: `/api/v1/auth/{register,login,me}`, `/catalog/vehicles`, `/me/vehicles` (GET/POST/PATCH), `/me/cases`, `/diagnose/query`, `/mechanic/notes`, `/admin/{stats,documents,notes,users,reindex}`. All except register/login/health need `Authorization: Bearer <token>`.

**Upgrading an existing database:** the new `appuser` table is created automatically on start. Old cars registered to `dev-user` are not linked to any account: sign in and add your car again under **My cars**.

To change the UI, install Node.js 20+ and run:
```
cd frontend
npm install
npm run dev        # http://localhost:5173, forwards /api to the running API
npm run build      # rebuilds dist/ for http://localhost:8000/app/
```

## Decisions made (yours to confirm)

1. **`document.vehicle_id` is nullable.** The ER draws Document→Vehicle as mandatory, but the generic OBD-II reference belongs to no single vehicle. NULL means it applies to all. The alternative is copying the DTC reference once per model year.
2. **Scope filter = manufacturer + model + year**, not exact variant. Owner manuals are per model year, so a manual shared by several years gets one `document` row per year (`--years 2014-2016`).
3. **Year range 2014–2025** as you asked. The proposal (§4.2) says **2015–2025**, so one of them should be corrected. Change it in `config.py`.
4. **Embeddings:** BGE-M3 (multilingual BGE, per proposal §10). **Reranker:** bge-reranker-v2-m3. **Vector search:** in-process exact cosine over pgvector-stored embeddings. This gives the same results as a FAISS flat index, and at the size of three manuals it's fast. Swap in FAISS or Qdrant later behind `ScopedIndex`.
5. **Generation:** any OpenAI-compatible LLM, JSON claims only. The proposal doesn't name a model, so pick one and record it for the System A/C comparison.
6. **Thresholds** `MIN_EVIDENCE_SCORE=0.30` and `MIN_CLAIM_SUPPORT=0.25` are **untuned placeholders**. Set them from the risk–coverage curve on the held-out question set (§7.2) and report them.
7. **Unknown code + no other evidence → abstain.** Unknown code + strong symptom evidence → answer, with a "code not found" notice. A neighbouring code (P0302 for P0301) is never used.
8. **Every query is logged as a `diagnosticcase`.** `predicted_category`/`predicted_urgency` come from M2 (Story 4); `confidence` holds the raw classifier probability until M3 (Story 5). `outcome` stays NULL because it's the real-world resolution.
9. **`appuser` table (not in the ER diagram).** Role-based access needs accounts; `uservehicle.user_id` now refers to `appuser.user_id`. Add it to the ER diagram, or tell me to drop it.
10. **Mechanic notes from the app** are stored as `mechanic_note_pending` and are never searched until an admin approves them.
11. **Moderate = "within two weeks".** The proposal says "within a defined window" without naming one. Two weeks is a placeholder; confirm it with a mechanic.
12. **Fault categories:** engine (incl. fuel, ignition, emissions), transmission, braking, electrical, cooling, suspension & steering, tyres & wheels, plus `general` for how-to questions, which get no urgency.
13. **Vision model for photos:** `qwen/qwen3.8-27b`, the vision model Groq listed in October 2026. Groq changes models often. If photo reading starts returning 404, check console.groq.com/docs/vision and change `AUTOCARE_VISION_MODEL` in `start.bat`.
14. **`damageimage.file_ref` is nullable** and stays empty: photos aren't kept. `label_source` = `model:vision` for predictions.

## Known limitations

* Urdu / Roman-Urdu questions are rewritten into an English search query by the LLM before search and reranking (the reranker scores Roman Urdu poorly: 0.03 vs 0.97 for the same correct passage in testing). The answer is still written in the user's language. The rewritten query is returned in `signals.retrieval_query` so it can be audited.
* Each non-English claim is verified through its English rendering (`text_en`). This assumes `text_en` faithfully matches `text`; spot-check a sample in the evaluation.

* The Roman Urdu / Urdu glossary in `language.py` is small and hand-written. Extend it from the team's labelled symptom set.
* The "lite" backend is lexical and does not understand Urdu. Never report numbers from it.
* `pdf_ingest.py` is a working baseline (font-size headings, WARNING/CAUTION boxes, tables, numbered steps), not the final L1 pipeline. Scanned PDFs need OCR first.

---

## 👥 Project Team & Contributors

| Name | Role | Email |
| :--- | :--- | :--- |
| **Muhammad Abdullah** | Project Lead & Full-Stack Architecture | `abdullah262686@gmail.com` |
| **Danial Hameed** | Backend & API Engineering | `danialhameed755@gmail.com` |
| **Abdullah Mudasir** | Frontend & DevOps Engineering | `abdullahmudasir27@gmail.com` |
| **Talha Bhatti** | Data Pipeline & Knowledge Graph Engineering | `talhabhattiak47@gmail.com` |
| **Ahmad Zahid** | Machine Learning & Triage Model Lead | `ahmadzahid5029@gmail.com` |

