# AutoCare AI: User Stories & Acceptance Criteria

**Department of Data Science, University of the Punjab, Lahore**  
**Primary Actor:** Vehicle Owner  

---

## 1. Register Vehicle Profile (Priority: High)
* **Goal:** Register make, model, variant, and year before diagnostic questions so retrieval is strictly filtered to the vehicle.
* **Acceptance Criteria:**
  - Selected vehicle from supported list becomes active profile and filters all retrieval.
  - Unsupported vehicles cannot be set as active.
  - Current mileage can be updated anytime without re-entering the rest of the profile.
  - Multiple vehicles supported with separate query history.
  - Submitting a query without an active profile prompts for registration (HTTP 428).

## 2. Ask a Diagnostic Question in English, Urdu, or Roman Urdu (Priority: Highest)
* **Goal:** Hybrid retrieval (semantic + BM25 keyword) over owner manuals and DTC codes, with section/page citations and native response language.
* **Acceptance Criteria:**
  - Grounded answer generated in the user's language (English, Urdu, Roman Urdu).
  - Factual claims traceable to document, section, and page.
  - Exact DTC matches prioritized via keyword retrieval.
  - Mixed Roman Urdu + English supported via language expansion.
  - Abstains when evidence is insufficient.

## 3. Enter a Diagnostic Trouble Code from a Scanner Photo (Priority: High)
* **Goal:** Enter code directly or upload photo of OBD-II scanner screen.
* **Acceptance Criteria:**
  - Typed code matches diagnostic-code reference entry.
  - Scanner photo extracts code via OCR / vision model.
  - Blurry images trigger retype/retake prompt rather than guessing.
  - Unrecognized code is flagged and lowers confidence.

## 4. Receive a Fault Category and Repair-Urgency Level (Priority: Highest)
* **Goal:** Automatically classify symptoms into category and urgency (Low, Moderate, High, Critical).
* **Acceptance Criteria:**
  - Returns fault category and urgency level.
  - Critical shows "Stop driving immediately — seek assistance".
  - Low shows calm routine service recommendation.
  - Ambiguous cases lower confidence and list alternatives.
  - Consistent labels across English, Urdu, and Roman Urdu.

## 5. See a Reliability Score and Know When the System Declines to Answer (Priority: Highest - M3)
* **Goal:** Calibrated confidence score and selective abstention gate.
* **Acceptance Criteria:**
  - Calibrated reliability score attached to each output.
  - Score below abstention threshold triggers explicit abstention.
  - Conservative threshold on Critical path.
  - Reliability reflects empirical correctness.

## 6. View the Evidence Trace Behind a Decision (Priority: High - M4)
* **Goal:** Deterministic breakdown of symptoms, codes, manual sections, citations, and graph relations used.
* **Acceptance Criteria:**
  - Lists extracted symptoms, codes, manual citations, and graph relations.
  - Displayed in plain, understandable language.

## 7. Verify a Workshop's Recommended Repair (Priority: Highest - M5)
* **Goal:** Verify workshop claim as Supported, Partially Supported, or Unsupported.
* **Acceptance Criteria:**
  - Returns 3-way verdict with supporting evidence.
  - Unsupported claims suggest direct alternative repairs.
  - Non-accusatory framing; notes that physical inspection can reveal hidden faults.
  - Incorporates collision damage photos into verification premise.

## 8. See the Root Cause, Not Just the Symptom (Priority: High - M6)
* **Goal:** Multi-hop causal chain inference from automotive knowledge graph.
* **Acceptance Criteria:**
  - Returns full causal chain (e.g. battery discharged <- alternator/belt fault).
  - Bounded traversal prevents meaningless paths.
  - Causally related components expand retrieval.

## 9. See Similar Prior Cases and How They Were Resolved (Priority: Medium - M8)
* **Goal:** Search case bank for matching vehicle, symptoms, and DTC code.
* **Acceptance Criteria:**
  - Surfaces closest prior cases and resolutions.
  - Seeded cases visually flagged from real user cases.
  - Allows user to record real post-repair outcome.

## 10. Check My Vehicle's Overall Health Index (Priority: Medium - M7.1)
* **Goal:** Component group score (engine, transmission, brakes, electrical, cooling, tyres).
* **Acceptance Criteria:**
  - Transparent function of mileage, interval, elapsed time, and open faults.
  - Explicitly presented as summary of known state, not physical inspection.

## 11. Get a Personalised Prediction of My Next Service (Priority: High - M7.2)
* **Goal:** Predict next service item and mileage/time window.
* **Acceptance Criteria:**
  - Predicts item and window based on mileage, age, usage rate, and service history.
  - Evaluated on synthetic model and validated against real records.

## 12. Submit Accident or Collision Photos for Damage Assessment (Priority: High - M10)
* **Goal:** Classify exterior collision damage severity (Minor, Moderate, Severe) and affected body area.
* **Acceptance Criteria:**
  - Predicts severity and body region.
  - Feeds into repair verifier and confidence score.
  - Declines out-of-scope requests (fault liability, cost estimation).

## 13. Download a Portable PDF Service Report (Priority: Medium - M9)
* **Goal:** Export complete diagnostic session, evidence trace, urgency, and verifier verdict to PDF.
* **Acceptance Criteria:**
  - Clean PDF report containing vehicle profile, symptoms, diagnosis, citations, and verifier verdict.
  - Abstention and notices faithfully preserved in PDF.
