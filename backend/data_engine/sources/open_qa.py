"""Open Official Automotive Q&A & Safety API Collectors (No Scraping).

Collects structured problem/solution records via open public REST APIs:
1. Stack Exchange Motor Vehicle Maintenance & Repair API v2.3 (CC BY-SA 4.0)
2. U.S. DOT / NHTSA Vehicle Safety Recalls & Owner Complaints API (Public Domain)
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
import httpx

from ..config import get_config
from ..logger import AuditAction, get_audit_logger
from ..schema import (
    AutomotiveRecord,
    ProblemInfo,
    RepairInfo,
    SourceQualityInfo,
    VehicleInfo,
)
from ..taxonomy import DiagnosisStage, get_taxonomy_manager, normalize_make_model
from .submissions import scrub_pii

SE_API_BASE = "https://api.stackexchange.com/2.3"
NHTSA_RECALLS_URL = "https://api.nhtsa.gov/recalls/recallsByVehicle"
NHTSA_COMPLAINTS_URL = "https://api.nhtsa.gov/complaints/complaintsByVehicle"

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")

DEFAULT_SE_QUERIES: Tuple[Dict[str, str], ...] = (
    {"id": "se_toyota", "param": "q", "value": "toyota corolla yaris prius", "label": "Toyota"},
    {"id": "se_honda", "param": "q", "value": "honda civic city accord", "label": "Honda"},
    {"id": "se_suzuki", "param": "q", "value": "suzuki swift alto cultus", "label": "Suzuki"},
    {"id": "se_hyundai_kia", "param": "q", "value": "hyundai elantra tucson kia sportage", "label": "Hyundai/KIA"},
    {"id": "se_brakes", "param": "tagged", "value": "brakes", "label": "Brakes"},
    {"id": "se_overheating", "param": "tagged", "value": "overheating", "label": "Cooling"},
    {"id": "se_starting", "param": "tagged", "value": "starting", "label": "Starting"},
    {"id": "se_engine", "param": "tagged", "value": "engine", "label": "Engine"},
    {"id": "se_transmission", "param": "tagged", "value": "transmission", "label": "Transmission"},
    {"id": "se_electrical", "param": "tagged", "value": "electrical", "label": "Electrical"},
    {"id": "se_suspension", "param": "tagged", "value": "suspension", "label": "Suspension"},
    {"id": "se_clutch", "param": "tagged", "value": "clutch", "label": "Clutch"},
    {"id": "se_alternator", "param": "tagged", "value": "alternator", "label": "Alternator"},
    {"id": "se_battery", "param": "tagged", "value": "battery", "label": "Battery"},
    {"id": "se_ac", "param": "tagged", "value": "air-conditioning", "label": "AC"},
    {"id": "se_fuel", "param": "tagged", "value": "fuel-system", "label": "Fuel"},
    {"id": "se_ignition", "param": "tagged", "value": "ignition", "label": "Ignition"},
    {"id": "se_steering", "param": "tagged", "value": "steering", "label": "Steering"},
    {"id": "se_oil", "param": "tagged", "value": "oil", "label": "Oil"},
    {"id": "se_cel", "param": "tagged", "value": "check-engine-light", "label": "CEL"},
    {"id": "se_misfire", "param": "tagged", "value": "misfire", "label": "Misfire"},
    {"id": "se_toyota_tag", "param": "tagged", "value": "toyota", "label": "Toyota Tag"},
    {"id": "se_honda_tag", "param": "tagged", "value": "honda", "label": "Honda Tag"},
    {"id": "se_coolant", "param": "tagged", "value": "coolant", "label": "Coolant"},
    {"id": "se_sensors", "param": "tagged", "value": "sensors", "label": "Sensors"},
    {"id": "se_spark", "param": "tagged", "value": "spark-plugs", "label": "Spark Plugs"},
    {"id": "se_abs", "param": "tagged", "value": "abs", "label": "ABS"},
    {"id": "se_fuel_pump", "param": "tagged", "value": "fuel-pump", "label": "Fuel Pump"},
    {"id": "se_exhaust", "param": "tagged", "value": "exhaust", "label": "Exhaust"},
    {"id": "se_dtc", "param": "tagged", "value": "diagnostic-trouble-code", "label": "OBD/DTC"},
)

DEFAULT_NHTSA_VEHICLES: Tuple[Tuple[str, str], ...] = (
    ("toyota", "corolla"),
    ("toyota", "yaris"),
    ("toyota", "prius"),
    ("toyota", "camry"),
    ("toyota", "rav4"),
    ("honda", "civic"),
    ("honda", "accord"),
    ("honda", "cr-v"),
    ("honda", "fit"),
    ("hyundai", "elantra"),
    ("hyundai", "tucson"),
    ("hyundai", "sonata"),
    ("kia", "sportage"),
    ("kia", "rio"),
    ("suzuki", "swift"),
    ("suzuki", "grand vitara"),
)
DEFAULT_NHTSA_YEARS: Tuple[int, ...] = (
    2008, 2010, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025
)


def clean_html_text(raw: str) -> str:
    """Unescapes HTML entities, strips markup tags, collapses whitespace, and scrubs PII."""
    if not raw:
        return ""
    text = html.unescape(raw)
    text = _HTML_TAG_RE.sub(" ", text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return scrub_pii(text)


def _norm_vehicle(make_hint: Optional[str], model_hint: Optional[str], blob: str) -> Tuple[str, str]:
    make, model = normalize_make_model(make_hint, f"{model_hint or ''} {blob}".strip())
    if not make:
        make = make_hint.strip().title() if make_hint else "Generic"
    if not model:
        model = model_hint.strip().title() if model_hint else "Multi-Model"
    return make, model


class StackExchangeMechanicsCollector:
    """Fetches answered owner-vs-mechanic Q&A threads from Stack Exchange Mechanics API."""

    def __init__(self) -> None:
        self.config = get_config()
        self.logger = get_audit_logger()
        self.taxonomy = get_taxonomy_manager()

    def _get_json(self, client: httpx.Client, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        time.sleep(0.15)
        resp = client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        if data.get("backoff"):
            time.sleep(min(int(data["backoff"]) + 0.5, 10.0))
        return data

    def fetch_answered_qa(
        self,
        topics: Optional[Iterable[Dict[str, str]]] = None,
        top_vote_pages: int = 25,
        start_page: int = 1,
        pagesize: int = 100,
        skip_question_ids: Optional[set[int]] = None,
    ) -> List[Dict[str, Any]]:
        """Collects answered Stack Exchange questions paired with sorted mechanic answers."""
        seen_questions: Dict[int, Dict[str, Any]] = {}
        skip_qids = skip_question_ids or set()
        headers = {"User-Agent": "AIAutoPakistan-DataEngine/1.0"}

        with httpx.Client(timeout=self.config.request_timeout_seconds, headers=headers) as client:
            for topic in (topics if topics is not None else DEFAULT_SE_QUERIES):
                try:
                    params = {
                        "site": "mechanics",
                        "answers": 1,
                        "sort": "votes",
                        "order": "desc",
                        "pagesize": min(pagesize, 100),
                        "filter": "withbody",
                        topic["param"]: topic["value"],
                    }
                    data = self._get_json(client, f"{SE_API_BASE}/search/advanced", params)
                    for q in data.get("items", []):
                        qid = q.get("question_id")
                        if qid and qid not in seen_questions and qid not in skip_qids:
                            seen_questions[qid] = q
                except Exception:
                    continue

            for page in range(start_page, top_vote_pages + 1):
                try:
                    data = self._get_json(
                        client,
                        f"{SE_API_BASE}/search/advanced",
                        {
                            "site": "mechanics",
                            "answers": 1,
                            "sort": "votes",
                            "order": "desc",
                            "page": page,
                            "pagesize": min(pagesize, 100),
                            "filter": "withbody",
                        },
                    )
                    for q in data.get("items", []):
                        qid = q.get("question_id")
                        if qid and qid not in seen_questions and qid not in skip_qids:
                            seen_questions[qid] = q
                    if not data.get("has_more"):
                        break
                except Exception:
                    break

            qids = list(seen_questions.keys())
            answers_by_qid: Dict[int, List[Dict[str, Any]]] = {}
            for i in range(0, len(qids), 100):
                batch_ids = ";".join(str(x) for x in qids[i : i + 100])
                try:
                    ans_data = self._get_json(
                        client,
                        f"{SE_API_BASE}/questions/{batch_ids}/answers",
                        {
                            "site": "mechanics",
                            "sort": "votes",
                            "order": "desc",
                            "pagesize": 100,
                            "filter": "withbody",
                        },
                    )
                    for ans in ans_data.get("items", []):
                        aqid = ans.get("question_id")
                        if aqid:
                            answers_by_qid.setdefault(aqid, []).append(ans)
                except Exception:
                    continue

        items: List[Dict[str, Any]] = []
        now_iso = dt.datetime.now(dt.timezone.utc).isoformat()
        for qid, q in seen_questions.items():
            ans_list = answers_by_qid.get(qid, [])
            if not ans_list:
                continue
            ans_list.sort(
                key=lambda a: (1 if a.get("is_accepted") else 0, int(a.get("score", 0))),
                reverse=True,
            )
            title = clean_html_text(q.get("title") or "")
            body = clean_html_text(q.get("body") or "")
            cleaned_answers = [
                {
                    "answer_id": a.get("answer_id"),
                    "is_accepted": bool(a.get("is_accepted")),
                    "score": int(a.get("score", 0)),
                    "text": clean_html_text(a.get("body") or ""),
                }
                for a in ans_list
                if clean_html_text(a.get("body") or "")
            ]
            if not title or not cleaned_answers:
                continue
            items.append({
                "question_id": qid,
                "title": title,
                "body": body,
                "tags": q.get("tags") or [],
                "score": int(q.get("score", 0)),
                "view_count": int(q.get("view_count", 0)),
                "is_accepted": any(a["is_accepted"] for a in cleaned_answers),
                "link": q.get("link") or f"https://mechanics.stackexchange.com/questions/{qid}",
                "content_license": q.get("content_license") or "CC BY-SA 4.0",
                "creation_date": q.get("creation_date"),
                "answers": cleaned_answers[:5],
                "collection_date": now_iso,
            })

        self.logger.log(
            AuditAction.COLLECTION_COMPLETED,
            source_id="stackexchange_mechanics",
            status="SUCCESS",
            details={"questions_with_answers": len(items)},
        )
        return items

    def save_raw_batch(self, items: List[Dict[str, Any]]) -> Path:
        dest = self.config.raw_dir / "stackexchange" / f"se_mechanics_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps({"source": "stackexchange_mechanics", "count": len(items), "items": items}, indent=2, ensure_ascii=False), encoding="utf-8")
        return dest

    def to_automotive_records(self, items: List[Dict[str, Any]]) -> List[AutomotiveRecord]:
        out: List[AutomotiveRecord] = []
        for it in items:
            qid = it["question_id"]
            title = it["title"]
            body = it.get("body") or title
            tags = [str(t) for t in (it.get("tags") or [])]
            top_ans = it["answers"][0]["text"]
            extra_steps = [a["text"][:600] for a in it["answers"][1:3]]

            blob = f"{title} {body} {' '.join(tags)}"
            make, model = _norm_vehicle(None, None, blob)
            cat = self.taxonomy.match_category_from_text(f"{blob} {top_ans}")

            pub_iso = None
            if it.get("creation_date"):
                try:
                    pub_iso = dt.datetime.fromtimestamp(int(it["creation_date"]), tz=dt.timezone.utc).isoformat()
                except Exception:
                    pass

            out.append(
                AutomotiveRecord(
                    record_id=f"se_{qid}",
                    vehicle=VehicleInfo(make=make, model=model),
                    problem=ProblemInfo(
                        problem_title=title[:300],
                        problem_description=body[:2500],
                        symptoms=tags[:8] or [title[:120]],
                        fault_category=cat.category_id if cat else None,
                        diagnosis_stage=DiagnosisStage.OWNER_REPORTED_PROBLEM.value,
                    ),
                    repair=RepairInfo(
                        recommended_solution=top_ans[:2500],
                        repair_steps=extra_steps,
                        verification_status="unverified",
                    ),
                    source=SourceQualityInfo(
                        source_platform="stackexchange_mechanics",
                        source_url=it["link"],
                        source_id=f"se_{qid}",
                        publication_date=pub_iso,
                        collection_date=it.get("collection_date") or dt.datetime.now(dt.timezone.utc).isoformat(),
                        language="en",
                        rights_basis="open_academic_license",
                        permission_status=it.get("content_license") or "CC BY-SA 4.0",
                        human_review_status="ml_ready",
                        confidence_score=0.80 if it.get("is_accepted") else 0.70,
                        evidence_reference=f"accepted={it.get('is_accepted')}; q_score={it.get('score')}; answers={len(it.get('answers', []))}",
                    ),
                )
            )
        return out


class NHTSAComplaintsCollector:
    """Collects official U.S. DOT NHTSA safety recalls (with remedies) & owner complaints."""

    def __init__(self) -> None:
        self.config = get_config()
        self.logger = get_audit_logger()
        self.taxonomy = get_taxonomy_manager()

    def fetch_vehicle_data(
        self,
        vehicles: Optional[Iterable[Tuple[str, str]]] = None,
        years: Optional[Iterable[int]] = None,
        max_complaints_per_model_year: int = 30,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Fetches deduplicated NHTSA recalls and sampled owner complaints across shared models."""
        seen_recalls: Dict[str, Dict[str, Any]] = {}
        seen_complaints: Dict[str, Dict[str, Any]] = {}
        headers = {"User-Agent": "AIAutoPakistan-DataEngine/1.0"}

        with httpx.Client(timeout=self.config.request_timeout_seconds, headers=headers) as client:
            for make, model in (vehicles if vehicles is not None else DEFAULT_NHTSA_VEHICLES):
                for yr in (years if years is not None else DEFAULT_NHTSA_YEARS):
                    params = {"make": make, "model": model, "modelYear": yr}
                    try:
                        rec_resp = client.get(NHTSA_RECALLS_URL, params=params)
                        if rec_resp.status_code == 200:
                            for r in rec_resp.json().get("results", []):
                                camp = str(r.get("NHTSACampaignNumber") or "").strip()
                                if camp and camp not in seen_recalls:
                                    r["_make_q"], r["_model_q"], r["_year_q"] = make, model, yr
                                    seen_recalls[camp] = r
                    except Exception:
                        pass

                    try:
                        cmp_resp = client.get(NHTSA_COMPLAINTS_URL, params=params)
                        if cmp_resp.status_code == 200:
                            added = 0
                            for c in cmp_resp.json().get("results", []):
                                odi = str(c.get("odiNumber") or "").strip()
                                if odi and odi not in seen_complaints and (c.get("summary") or "").strip():
                                    c["_make_q"], c["_model_q"], c["_year_q"] = make, model, yr
                                    seen_complaints[odi] = c
                                    added += 1
                                    if added >= max_complaints_per_model_year:
                                        break
                    except Exception:
                        pass

        self.logger.log(
            AuditAction.COLLECTION_COMPLETED,
            source_id="nhtsa_official_api",
            status="SUCCESS",
            details={"recalls": len(seen_recalls), "complaints": len(seen_complaints)},
        )
        return {
            "recalls": list(seen_recalls.values()),
            "complaints": list(seen_complaints.values()),
        }

    def save_raw_batch(self, payload: Dict[str, List[Dict[str, Any]]]) -> Path:
        dest = self.config.raw_dir / "nhtsa" / f"nhtsa_safety_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps({"source": "nhtsa_official_api", **payload}, indent=2, ensure_ascii=False), encoding="utf-8")
        return dest

    def to_automotive_records(self, payload: Dict[str, List[Dict[str, Any]]]) -> List[AutomotiveRecord]:
        out: List[AutomotiveRecord] = []
        now_iso = dt.datetime.now(dt.timezone.utc).isoformat()

        for r in payload.get("recalls", []):
            camp = str(r["NHTSACampaignNumber"]).strip()
            comp = (r.get("Component") or "Safety Component").strip()
            summary = scrub_pii((r.get("Summary") or "").strip())
            conseq = scrub_pii((r.get("Consequence") or "").strip())
            remedy = scrub_pii((r.get("Remedy") or "").strip())
            if not summary:
                continue

            make, model = _norm_vehicle(r.get("_make_q"), r.get("_model_q"), f"{comp} {summary}")
            year_val = int(r["_year_q"]) if r.get("_year_q") else None
            cat = self.taxonomy.match_category_from_text(f"{comp} {summary} {remedy}")
            full_desc = f"{summary}\nConsequence: {conseq}".strip() if conseq else summary

            out.append(
                AutomotiveRecord(
                    record_id=f"nhtsa_rec_{camp}",
                    vehicle=VehicleInfo(make=make, model=model, manufacturing_year=year_val, market_country="Global/Shared"),
                    problem=ProblemInfo(
                        problem_title=f"[{make} {model} Recall {camp}] {comp[:160]}",
                        problem_description=full_desc[:2500],
                        symptoms=[comp],
                        affected_component=comp[:120],
                        fault_category=cat.category_id if cat else None,
                        severity="high",
                        diagnosis_stage=DiagnosisStage.MECHANIC_CONFIRMED_DIAGNOSIS.value,
                    ),
                    repair=RepairInfo(
                        recommended_solution=remedy[:2500] or None,
                        verification_status="verified_by_oem",
                    ) if remedy else None,
                    source=SourceQualityInfo(
                        source_platform="nhtsa_official_api",
                        source_url=f"https://www.nhtsa.gov/recalls?nhtsaId={camp}",
                        source_id=f"nhtsa_rec_{camp}",
                        collection_date=now_iso,
                        language="en",
                        rights_basis="public_technical_documentation",
                        permission_status="us_dot_public_domain",
                        human_review_status="ml_ready",
                        confidence_score=0.95,
                        evidence_reference=f"NHTSA Campaign {camp}",
                    ),
                )
            )

        for c in payload.get("complaints", []):
            odi = str(c["odiNumber"]).strip()
            comp = (c.get("components") or "Vehicle Component").strip()
            summary = scrub_pii((c.get("summary") or "").strip())
            if not summary:
                continue

            make, model = _norm_vehicle(c.get("_make_q"), c.get("_model_q"), f"{comp} {summary}")
            year_val = int(c["_year_q"]) if c.get("_year_q") else None
            cat = self.taxonomy.match_category_from_text(f"{comp} {summary}")
            sev = "critical" if (c.get("fire") or c.get("crash")) else "moderate"

            out.append(
                AutomotiveRecord(
                    record_id=f"nhtsa_cmp_{odi}",
                    vehicle=VehicleInfo(make=make, model=model, manufacturing_year=year_val, market_country="Global/Shared"),
                    problem=ProblemInfo(
                        problem_title=f"[{make} {model} Owner Report] {comp[:140]}",
                        problem_description=summary[:2500],
                        symptoms=[s.strip() for s in comp.split(",") if s.strip()][:6],
                        affected_component=comp[:120],
                        fault_category=cat.category_id if cat else None,
                        severity=sev,
                        diagnosis_stage=DiagnosisStage.OWNER_REPORTED_PROBLEM.value,
                    ),
                    source=SourceQualityInfo(
                        source_platform="nhtsa_official_api",
                        source_url=f"https://www.nhtsa.gov/vehicle/{year_val}/{make.upper()}/{model.upper()}#complaints-{odi}",
                        source_id=f"nhtsa_cmp_{odi}",
                        collection_date=now_iso,
                        language="en",
                        rights_basis="public_technical_documentation",
                        permission_status="us_dot_public_domain",
                        human_review_status="ml_ready",
                        confidence_score=0.70,
                        evidence_reference=f"NHTSA ODI {odi}",
                    ),
                )
            )

        return out
