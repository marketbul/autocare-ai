# FINAL YEAR PROJECT PROPOSAL
# AutoCare AI
**An Evidence-Grounded Diagnostic, Verification and Maintenance-Prediction System for Vehicles**  
*Retrieval-augmented reasoning, calibrated urgency classification, repair-claim verification, and predictive maintenance in English, Urdu and Roman Urdu*

### Project Members
- **Talha Ali Bhatti** (BSDSF23A016) — AI-ML & Knowledge Graph Lead
- **Danial Hameed** (BSDSF23A014) — Data & Retrieval Lead
- **Abdullah** (BSDSF23A035) — Group Leader & System Architect
- **Ahmad Zahid** (BSDSF23A033) — ML Triage & Verification Lead
- **Muhammad Abdullah** (BSDSF23A032) — Frontend & Mobile App Lead

### Supervisor
- **Dr. Khurram Shehzad**  
  Department of Data Science, University of the Punjab, Lahore (2026)

---

## Abstract
Vehicle owners in Pakistan routinely face a bind: dashboard warning lights, unusual noises, and maintenance schedules are explained only in dense, English-language manufacturer manuals, while day-to-day diagnosis is left to workshop mechanics whose recommendations the owner has no independent way to verify. This information asymmetry contributes to unnecessary repairs and inflated costs, and — when genuine warnings are dismissed as exaggeration — to delayed attention on conditions that affect road safety. Generic AI chatbots do not close this gap: without grounding in verified, vehicle-specific documentation, large language models routinely produce confident, plausible-sounding, and sometimes incorrect diagnostic advice.

AutoCare AI is a multi-component decision-support system rather than a question-answering interface. A Retrieval-Augmented Generation (RAG) core answers vehicle maintenance and diagnostic questions from verified manufacturer manuals and public diagnostic-code references with document-level citations. Layered on top of that core are six trained or inferential modules that together constitute the project’s data-science contribution:
1. Supervised fault-category and repair-urgency classifier (M2)
2. Calibrated confidence and selective-abstention layer (M3)
3. Evidence-grounded explanation module (M4)
4. Repair-recommendation verifier (M5)
5. Automotive knowledge graph supporting multi-hop root-cause chain inference (M6)
6. Vehicle health index with a personalised maintenance-prediction model (M7)
7. Similar-case retrieval over a diagnostic case bank (M8)
8. Automated service report generator (M9)
9. Accident and collision damage image-assessment module (M10)

The system supports English, Urdu, and Roman Urdu queries, addressing a language-access gap existing tools leave unaddressed.

---

## 1. System Architecture (5 Layers)
- **L1 Ingestion & Knowledge Construction:** PDF extraction, structure-aware chunking, metadata tagging, embedding, BM25 index, knowledge-graph extraction, case-bank construction, accident-image preprocessing.
- **L2 Evidence Retrieval:** Vehicle-profile metadata filter, hybrid semantic + keyword retrieval, reranking, citation validation.
- **L3 Reasoning & Inference:** Urgency and fault classifier (M2), repair verifier (M5), knowledge-graph root-cause inference (M6), similar-case retrieval (M8), health index and maintenance prediction (M7), accident-image damage classifier (M10).
- **L4 Trust & Calibration:** Confidence estimation and calibration, abstention gate, evidence-attribution and explanation generation (M3, M4).
- **L5 Delivery:** FastAPI service layer, React application, multilingual response rendering, PDF service report (M9).

---

## 2. In-Scope Vehicles
- Toyota Corolla (2014–2025)
- Honda Civic (2015–2025)
- Suzuki Swift (2015–2025)
*(Prototype currently focused on Toyota Corolla as the primary validation vehicle).*
