"""Tiny in-memory corpus for tests.

The passages are TEST FIXTURES written for these tests, not text from a real
Toyota manual; page numbers are arbitrary. A Honda Civic manual is included only
to prove the vehicle filter keeps it out of Corolla answers.
"""
from __future__ import annotations

from dataclasses import replace

from autocare.config import Settings
from autocare.db import Database
from autocare.ml import HashingEmbedder, OverlapReranker
from autocare.repository import Repository, encode_embedding
from autocare.retrieval import Retriever
from autocare.service import DiagnoseService

VEHICLES = [
    dict(vehicle_id="toyota-corolla-2018-xli", manufacturer="Toyota", model="Corolla",
         variant="XLi", year=2018, engine="1.3L", transmission="Manual", fuel_type="Petrol"),
    dict(vehicle_id="toyota-corolla-2012-xli", manufacturer="Toyota", model="Corolla",
         variant="XLi", year=2012, engine="1.3L", transmission="Manual", fuel_type="Petrol"),
    dict(vehicle_id="honda-civic-2018-base", manufacturer="Honda", model="Civic",
         variant=None, year=2018, engine="1.8L", transmission="CVT", fuel_type="Petrol"),
]
USER_VEHICLES = [("uv-corolla", "toyota-corolla-2018-xli", 82000),
                 ("uv-old-corolla", "toyota-corolla-2012-xli", 150000),
                 ("uv-civic", "honda-civic-2018-base", 40000)]

DOCS = [
    ("doc-corolla-2018", "toyota-corolla-2018-xli", "Corolla 2018 Owner's Manual", "owner_manual"),
    ("doc-civic-2018", "honda-civic-2018-base", "Civic 2018 Owner's Manual", "owner_manual"),
    ("doc-dtc", None, "OBD-II Generic Code Reference", "dtc_reference"),
]

CHUNKS = [
    ("c-brake-pads", "doc-corolla-2018", "Brakes > Brake pad wear indicator", 412, "narrative",
     "The disc brake pads have wear indicators that produce a high-pitched squealing or grinding "
     "noise when braking once the pads are worn to the service limit. If you hear this noise "
     "while braking, have the brake pads checked and replaced."),
    ("c-brake-light", "doc-corolla-2018", "Warning lights > Brake system warning light", 540, "warning",
     "WARNING: If the brake system warning light comes on while driving, the brake fluid level may "
     "be low or there may be a malfunction in the brake system. Stop the vehicle in a safe place "
     "and contact your dealer."),
    ("c-overheat", "doc-corolla-2018", "If the engine overheats", 548, "procedure",
     "If the engine coolant temperature gauge enters the red zone or the engine overheats, stop "
     "the vehicle, turn off the air conditioning and check for steam or smoke from the engine "
     "compartment. Check the coolant level once the engine has cooled."),
    ("c-mil", "doc-corolla-2018", "Warning lights > Malfunction indicator lamp", 541, "narrative",
     "The malfunction indicator lamp (check engine light) comes on when the engine control system "
     "detects a fault such as an engine misfire. If it flashes, reduce speed and have the vehicle "
     "inspected."),
    ("c-civic-brakes", "doc-civic-2018", "Brakes", 300, "narrative",
     "Civic: a grinding noise when braking means the brake pads are worn; replace the brake pads "
     "at a Honda dealer."),
    ("c-p0301", "doc-dtc", "P0301", 45, "dtc_entry",
     "P0301: Cylinder 1 Misfire Detected\nSystem: Powertrain\nPossible causes: faulty spark plug, "
     "ignition coil or fuel injector on cylinder 1\nSymptoms: rough idle, engine shaking, check "
     "engine light\nSeverity: High"),
    ("c-p0302", "doc-dtc", "P0302", 45, "dtc_entry",
     "P0302: Cylinder 2 Misfire Detected\nSystem: Powertrain\nPossible causes: faulty spark plug, "
     "ignition coil or fuel injector on cylinder 2\nSymptoms: rough idle, engine shaking, check "
     "engine light\nSeverity: High"),
    ("c-p0171", "doc-dtc", "P0171", 40, "dtc_entry",
     "P0171: System Too Lean (Bank 1)\nSystem: Powertrain\nPossible causes: vacuum leak, dirty "
     "mass air flow sensor, weak fuel pump\nSymptoms: hesitation, rough idle\nSeverity: Moderate"),
]

CODES = [("P0301", "Cylinder 1 Misfire Detected"), ("P0302", "Cylinder 2 Misfire Detected"),
         ("P0171", "System Too Lean (Bank 1)")]


class FakeLLM:
    """Records every call; returns `script(question, language, evidence)` or, by
    default, the first sentence of each passage as a claim citing it."""

    def __init__(self, script=None, language=None):
        self.calls: list[dict] = []
        self.script = script
        if language:
            self.language = language

    def generate(self, question, language, vehicle, evidence):
        self.calls.append({"question": question, "language": language,
                           "vehicle": vehicle, "evidence": list(evidence)})
        if self.script:
            return self.script(question, language, evidence)
        return [{"text": e.chunk.text.split(". ")[0], "evidence_ids": [e.label]} for e in evidence[:2]]


TEST_SETTINGS = Settings(database_url="sqlite:///:memory:", ml_backend="lite",
                         generation_mode="extractive", min_evidence_score=0.15,
                         min_claim_support=0.25, candidate_k=10, final_k=4,
                         supported_vehicles={("toyota", "corolla"): (2014, 2025)})



_TRIAGE_MODEL = None
STARTER_LABELS = __import__("pathlib").Path(__file__).resolve().parents[1] / "data" / "symptom_labels.starter.csv"


def triage_model():
    """Starter-set classifier with the lite embedder, trained once per test run."""
    global _TRIAGE_MODEL
    if _TRIAGE_MODEL is None:
        from autocare.triage import read_labels, train
        _TRIAGE_MODEL, _ = train(read_labels(STARTER_LABELS), HashingEmbedder(), "lite", folds=3)
    return _TRIAGE_MODEL


def build(generator=None, settings: Settings | None = None, triage: bool = False):
    settings = settings or TEST_SETTINGS
    db = Database(settings.database_url)
    db.create_schema()
    repo = Repository(db)
    emb = HashingEmbedder()
    for v in VEHICLES:
        repo.upsert_vehicle(v)
    for uvid, vid, km in USER_VEHICLES:
        repo.insert_user_vehicle(dict(user_vehicle_id=uvid, user_id="u1", vehicle_id=vid,
                                      registration_year=None, current_mileage=km,
                                      last_reading_date=None, usage_profile=None))
    for doc_id, vid, name, dtype in DOCS:
        repo.insert_document(dict(document_id=doc_id, vehicle_id=vid, document_name=name,
                                  document_type=dtype, version="test", source="test fixture",
                                  license_note="test fixture", ingest_date="2026-10-01"))
    vecs = emb.encode([f"{c[2]}\n{c[5]}" for c in CHUNKS])
    repo.insert_chunks([dict(chunk_id=c[0], document_id=c[1], section=c[2], page_number=c[3],
                             chunk_type=c[4], text=c[5], embedding=encode_embedding(v))
                        for c, v in zip(CHUNKS, vecs)])
    for code, desc in CODES:
        repo.upsert_diagnostic_code(dict(code=code, description=desc, system="Powertrain",
                                         possible_causes=None, symptoms=None, severity=None,
                                         source_ref="test fixture"))
    reranker = OverlapReranker()
    retriever = Retriever(repo, emb, reranker, settings)
    gen = generator if generator is not None else FakeLLM()
    tc = None
    if triage:
        from autocare.triage import TriageClassifier
        tc = TriageClassifier(triage_model(), emb)
    return DiagnoseService(repo, retriever, gen, reranker, settings, triage=tc), gen, db


__all__ = ["build", "FakeLLM", "TEST_SETTINGS", "replace", "triage_model"]

# [2026-05-07] test(taxonomy): [AUT-101] add 

# [2026-10-07] test(suite): [AUT-120] author 
