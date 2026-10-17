"""Train and evaluate the Story 4 / M2 fault-category + urgency classifier.

  python -m ingest.train_triage                       # uses AUTOCARE_ML_BACKEND's embedder
  python -m ingest.train_triage --with-dtc --baseline

Prints grouped cross-validation results (the three language versions of one
symptom are always in the same fold), the Critical false-negative rate on its own
line (proposal §11.3), per-language accuracy and cross-language consistency, then
saves the model where the API loads it from.

--with-dtc  also trains on DiagnosticCode rows whose `severity` is one of
            low/moderate/high/critical (description -> system category, severity).
--baseline  also runs the classical baseline from the proposal (TF-IDF + gradient
            boosting) under the same folds, for the comparison table.

Numbers from the STARTER set are a smoke test, not results: it is small and
written by the developer (synthesised = yes). Report numbers only from the
team-labelled set (data/symptom_labels.csv), and state the synthesised share.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def dtc_rows(db) -> list[dict]:
    from autocare.triage import URGENCIES, sae_category, system_category
    out = []
    for r in db.query("SELECT code, description, system, severity FROM diagnosticcode"):
        sev = (r.get("severity") or "").strip().lower()
        cat = system_category(r.get("system")) or sae_category(r["code"])
        if sev in URGENCIES and cat and r.get("description"):
            out.append({"example_id": f"dtc-{r['code']}", "group_id": f"dtc-{r['code']}", "language": "en",
                        "text": r["description"], "category": cat, "urgency": sev,
                        "source": "dtc_reference", "synthesised": "no", "reviewed": "yes"})
    return out


def baseline(rows: list[dict], folds: int = 5) -> dict:
    import numpy as np
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.model_selection import GroupKFold
    from sklearn.pipeline import make_pipeline

    texts = [r["text"].lower() for r in rows]
    groups = [r["group_id"] for r in rows]
    out = {}
    for target in ("category", "urgency"):
        y = np.array([r[target] for r in rows])
        pred = np.empty(len(rows), dtype=object)
        for tr, te in GroupKFold(n_splits=min(folds, len(set(groups)))).split(texts, y, groups):
            clf = make_pipeline(TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), sublinear_tf=True),
                                GradientBoostingClassifier(random_state=0))
            clf.fit([texts[i] for i in tr], y[tr])
            pred[te] = clf.predict([texts[i] for i in te])
        out[f"{target}_accuracy"] = round(float((pred == y).mean()), 3)
        if target == "urgency":
            crit = y == "critical"
            out["critical_false_negative_rate"] = round(float((pred[crit] != "critical").mean()), 3) if crit.any() else None
    return out


def main() -> None:
    from autocare.config import load_settings, triage_data_path
    from autocare.db import Database
    from autocare.ml import build_models
    from autocare.triage import data_fingerprint, read_labels, train

    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--with-dtc", action="store_true")
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--critical-recall", type=float, default=0.95)
    a = ap.parse_args()

    s = load_settings()
    data = a.data or triage_data_path(s)
    rows = read_labels(data)
    file_fp = data_fingerprint(rows)
    if a.with_dtc:
        db = Database(s.database_url)
        extra = dtc_rows(db)
        print(f"+ {len(extra)} rows from the diagnostic-code reference")
        rows += extra
    print(f"Training on {len(rows)} examples from {data} with embedder {s.embedding_model if s.ml_backend == 'models' else 'lite'}")
    embedder, _ = build_models(s)
    model, rep = train(rows, embedder, s.embedding_model if s.ml_backend == "models" else "lite",
                       critical_recall_target=a.critical_recall)

    print("\nGrouped cross-validation (out-of-fold):")
    print(f"  category accuracy  {rep['category_accuracy']:.3f}")
    print(f"  urgency accuracy   {rep['urgency_accuracy']:.3f}")
    print(f"  CRITICAL false-negative rate  {rep['critical_false_negative_rate']}   "
          f"(critical predicted as low: {rep['critical_predicted_low']})")
    print(f"  critical threshold {rep['critical_threshold']}")
    print(f"  cross-language consistency  {rep['cross_language_consistency']}")
    for lang, v in rep["by_language"].items():
        print(f"  {lang:9s} n={v['n']:4d}  category {v['category_accuracy']:.3f}  urgency {v['urgency_accuracy']:.3f}")
    print("  urgency per class:")
    for k, v in rep["urgency"].items():
        print(f"    {k:9s} P {v['precision']:.2f}  R {v['recall']:.2f}  F1 {v['f1']:.2f}  n={v['support']}")
    if a.baseline:
        b = baseline(rows)
        rep["baseline_tfidf_gbt"] = b
        print(f"\nBaseline TF-IDF + gradient boosting: {b}")

    model.meta["file_fingerprint"] = file_fp   # the API keeps this model while the CSV is unchanged
    model.meta["with_dtc"] = a.with_dtc
    out = Path(a.out or s.triage_model_path)
    model.save(out)
    out.with_name(out.stem + "_report.json").write_text(json.dumps(model.meta, indent=2), encoding="utf-8")
    print(f"\nSaved {out} and {out.with_name(out.stem + '_report.json')}")
    print(f"Synthesised share of training data: {model.meta['synthesised_share']:.0%}")


if __name__ == "__main__":
    main()

# [2026-06-13] feat(ml): [AUT-107] train base

# [2026-06-15] refactor(ml): [AUT-107B] imple

# [2026-06-15] feat(ml): [AUT-107] train baseline  by Ahmad Zahid
