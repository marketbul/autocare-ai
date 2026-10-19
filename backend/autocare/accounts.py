"""Everything role-specific: accounts, owner garage + history, mechanic submissions,
admin review and stats. Pure Python on top of Database, so it is unit-testable;
api.py only maps HTTP to these calls.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import uuid

from .auth import ROLES, hash_password, verify_password
from .config import PLANNED_MODELS, Settings, is_supported
from .db import Database
from .repository import Repository, encode_embedding
from .service import id_timestamp_ms, time_ordered_id

PENDING = "mechanic_note_pending"
USAGE_PROFILES = ("city", "highway", "mixed")   # feeds M7 maintenance prediction later
APPROVED = "mechanic_note"
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Invalid(ValueError): ...
class Forbidden(PermissionError): ...
class NotFound(LookupError): ...


def _years(spec: str) -> list[int]:
    spec = (spec or "").strip()
    if not spec:
        return []
    try:
        if "-" in spec:
            a, b = (int(x) for x in spec.split("-", 1))
            if b < a or b - a > 20:
                raise ValueError
            return list(range(a, b + 1))
        return [int(y) for y in spec.split(",") if y.strip()]
    except ValueError:
        raise Invalid("Years must look like 2018, 2014-2017 or 2015,2016.")


def _public(u: dict) -> dict:
    return {k: u[k] for k in ("user_id", "full_name", "email", "role", "created_at")}


class Accounts:
    def __init__(self, db: Database, settings: Settings):
        self.db, self.s, self.repo = db, settings, Repository(db)

    # ---------------------------------------------------------------- users
    def create_user(self, full_name: str, email: str, password: str, role: str = "owner") -> dict:
        full_name, email = (full_name or "").strip(), (email or "").strip().lower()
        if not full_name:
            raise Invalid("Enter your name.")
        if not _EMAIL.match(email):
            raise Invalid("Enter a valid email address.")
        if len(password or "") < 8:
            raise Invalid("Use a password of at least 8 characters.")
        if role not in ROLES:
            raise Invalid(f"Role must be one of {', '.join(ROLES)}.")
        if self.db.query("SELECT 1 FROM appuser WHERE email = :e", {"e": email}):
            raise Invalid("An account with this email already exists. Sign in instead.")
        row = {"user_id": str(uuid.uuid4()), "full_name": full_name, "email": email,
               "password_hash": hash_password(password), "role": role,
               "created_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
        self.db.execute("""INSERT INTO appuser (user_id, full_name, email, password_hash, role, created_at)
                           VALUES (:user_id, :full_name, :email, :password_hash, :role, :created_at)""", row)
        return _public(row)

    def register_owner(self, full_name: str, email: str, password: str) -> dict:
        # Self sign-up always creates an owner; only an admin can grant other roles.
        return self.create_user(full_name, email, password, "owner")

    def authenticate_or_register_google(self, email: str, full_name: str = "", google_id: str | None = None) -> dict:
        email = (email or "").strip().lower()
        if not email or not _EMAIL.match(email):
            raise Invalid("A valid Google email address is required.")
        rows = self.db.query("SELECT * FROM appuser WHERE email = :e", {"e": email})
        if rows:
            return _public(rows[0])
        name = full_name.strip() if full_name else email.split("@")[0].replace(".", " ").title()
        oauth_pwd = f"oauth_google_{uuid.uuid4().hex}"
        row = {
            "user_id": str(uuid.uuid4()),
            "full_name": name,
            "email": email,
            "password_hash": hash_password(oauth_pwd),
            "role": "owner",
            "created_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        }
        self.db.execute(
            """INSERT INTO appuser (user_id, full_name, email, password_hash, role, created_at)
               VALUES (:user_id, :full_name, :email, :password_hash, :role, :created_at)""",
            row
        )
        return _public(row)

    def authenticate(self, email: str, password: str) -> dict | None:
        rows = self.db.query("SELECT * FROM appuser WHERE email = :e", {"e": (email or "").strip().lower()})
        if rows and verify_password(password or "", rows[0]["password_hash"]):
            return _public(rows[0])
        return None

    def get_user(self, user_id: str) -> dict | None:
        rows = self.db.query("SELECT * FROM appuser WHERE user_id = :u", {"u": user_id})
        return _public(rows[0]) if rows else None

    def list_users(self) -> list[dict]:
        return [_public(r) for r in self.db.query("SELECT * FROM appuser ORDER BY created_at DESC")]

    def set_role(self, acting_admin_id: str, user_id: str, role: str) -> dict:
        if role not in ROLES:
            raise Invalid(f"Role must be one of {', '.join(ROLES)}.")
        if user_id == acting_admin_id and role != "admin":
            raise Invalid("You can't remove your own admin role. Ask another admin.")
        if not self.get_user(user_id):
            raise NotFound("User not found.")
        self.db.execute("UPDATE appuser SET role = :r WHERE user_id = :u", {"r": role, "u": user_id})
        return self.get_user(user_id)

    # ------------------------------------------------------- owner: garage
    def catalog(self) -> list[dict]:
        """Story 1 selector: every vehicle row, flagged supported / unsupported."""
        rows = self.db.query("""SELECT vehicle_id, manufacturer, model, variant, year, engine, transmission,
                                       fuel_type FROM vehicle ORDER BY manufacturer, model, year DESC, variant""")
        for r in rows:
            r["supported"] = is_supported(self.s, r["manufacturer"], r["model"], r["year"])
        # The proposal's other in-scope models appear too, greyed out, so an owner who
        # searches for them sees "not supported in this release" (AC2) instead of nothing.
        have = {(r["manufacturer"].lower(), r["model"].lower()) for r in rows}
        for make, model, first, last in PLANNED_MODELS:
            if (make.lower(), model.lower()) in have:
                continue
            rows += [{"vehicle_id": None, "manufacturer": make, "model": model, "variant": None, "year": y,
                      "engine": None, "transmission": None, "fuel_type": None,
                      "supported": is_supported(self.s, make, model, y)} for y in range(last, first - 1, -1)]
        return rows

    def _manual_years(self) -> set[tuple]:
        rows = self.db.query("""SELECT DISTINCT lower(v.manufacturer) AS m, lower(v.model) AS mo, v.year AS y
                                FROM document d JOIN vehicle v ON v.vehicle_id = d.vehicle_id
                                WHERE d.document_type = 'owner_manual'""")
        return {(r["m"], r["mo"], int(r["y"])) for r in rows}

    def my_vehicles(self, user_id: str) -> list[dict]:
        rows = self.db.query("""SELECT user_vehicle_id, registration_year, usage_profile, last_reading_date
                                FROM uservehicle WHERE user_id = :u ORDER BY user_vehicle_id""", {"u": user_id})
        manuals = self._manual_years()
        out = []
        for r in rows:
            p = self.repo.get_vehicle_profile(r["user_vehicle_id"])
            if p:
                out.append({"user_vehicle_id": p.user_vehicle_id, "vehicle_id": p.vehicle_id, "label": p.label,
                            "manufacturer": p.manufacturer, "model": p.model, "variant": p.variant,
                            "year": p.year, "current_mileage": p.current_mileage,
                            "registration_year": r["registration_year"], "usage_profile": r["usage_profile"],
                            "last_reading_date": str(r["last_reading_date"]) if r["last_reading_date"] else None,
                            "has_manual": (p.manufacturer.lower(), p.model.lower(), p.year) in manuals})
        return out

    def add_vehicle(self, user_id: str, vehicle_id: str, current_mileage: int | None,
                    registration_year: int | None = None, usage_profile: str | None = None) -> dict:
        v = next((c for c in self.catalog() if vehicle_id and c["vehicle_id"] == vehicle_id), None)
        if not v:
            raise Invalid("Choose a vehicle from the list.")
        if not v["supported"]:
            raise Invalid("This vehicle is not supported in this release.")   # Story 1 AC2
        if current_mileage is not None and not (0 <= int(current_mileage) <= 2_000_000):
            raise Invalid("Mileage must be between 0 and 2,000,000 km.")
        this_year = dt.date.today().year
        if registration_year is not None and not (int(v["year"]) - 1 <= int(registration_year) <= this_year):
            raise Invalid(f"Registration year must be between {int(v['year']) - 1} and {this_year}.")
        if usage_profile not in (None, "") and usage_profile not in USAGE_PROFILES:
            raise Invalid("Usage must be city, highway or mixed.")
        uvid = str(uuid.uuid4())
        self.repo.insert_user_vehicle({
            "user_vehicle_id": uvid, "user_id": user_id, "vehicle_id": vehicle_id,
            "registration_year": int(registration_year) if registration_year is not None else None,
            "current_mileage": current_mileage,
            "last_reading_date": dt.date.today().isoformat() if current_mileage is not None else None,
            "usage_profile": usage_profile or None,
        })
        return next(x for x in self.my_vehicles(user_id) if x["user_vehicle_id"] == uvid)

    def owns_vehicle(self, user_id: str, user_vehicle_id: str) -> bool:
        return bool(self.db.query("SELECT 1 FROM uservehicle WHERE user_vehicle_id = :v AND user_id = :u",
                                  {"v": user_vehicle_id, "u": user_id}))

    def update_vehicle(self, user_id: str, user_vehicle_id: str, *, mileage: int | None = None,
                       correction: bool = False, usage_profile: str | None = None) -> dict:
        """Story 1 AC3: mileage (and usage) change without touching the rest of the profile."""
        if not self.owns_vehicle(user_id, user_vehicle_id):
            raise NotFound("Vehicle not found in your garage.")
        if mileage is not None:
            if not (0 <= int(mileage) <= 2_000_000):
                raise Invalid("Mileage must be between 0 and 2,000,000 km.")
            cur = self.db.query("SELECT current_mileage FROM uservehicle WHERE user_vehicle_id = :v",
                                {"v": user_vehicle_id})[0]["current_mileage"]
            if cur is not None and int(mileage) < int(cur) and not correction:
                # Odometers don't go backwards; a lower number is only accepted as a typo fix.
                raise Invalid(f"That is lower than the last reading ({int(cur):,} km). "
                              "If the last reading was a typo, save it as a correction.")
            self.db.execute("""UPDATE uservehicle SET current_mileage = :m, last_reading_date = :d
                               WHERE user_vehicle_id = :v""",
                            {"m": int(mileage), "d": dt.date.today().isoformat(), "v": user_vehicle_id})
        if usage_profile is not None:
            if usage_profile not in USAGE_PROFILES:
                raise Invalid("Usage must be city, highway or mixed.")
            self.db.execute("UPDATE uservehicle SET usage_profile = :p WHERE user_vehicle_id = :v",
                            {"p": usage_profile, "v": user_vehicle_id})
        return next(x for x in self.my_vehicles(user_id) if x["user_vehicle_id"] == user_vehicle_id)

    def update_mileage(self, user_id: str, user_vehicle_id: str, mileage: int, correction: bool = False) -> dict:
        return self.update_vehicle(user_id, user_vehicle_id, mileage=mileage, correction=correction)

    # ------------------------------------------------------ owner: history
    def my_cases(self, user_id: str, limit: int = 100) -> list[dict]:
        rows = self.db.query("""SELECT c.case_id, c.user_vehicle_id, c.symptom_text, c.language, c.code,
                                       c.evidence_refs, c.predicted_category, c.predicted_urgency
                                FROM diagnosticcase c JOIN uservehicle uv ON uv.user_vehicle_id = c.user_vehicle_id
                                WHERE uv.user_id = :u""", {"u": user_id})
        labels = {v["user_vehicle_id"]: v["label"] for v in self.my_vehicles(user_id)}
        damage: dict[str, list[dict]] = {}
        for d in self.db.query("""SELECT d.case_id, d.predicted_severity FROM damageimage d
                                   JOIN diagnosticcase c ON c.case_id = d.case_id
                                   JOIN uservehicle uv ON uv.user_vehicle_id = c.user_vehicle_id
                                   WHERE uv.user_id = :u""", {"u": user_id}):
            damage.setdefault(d["case_id"], []).append(d)
        out = []
        for r in rows:
            refs = json.loads(r["evidence_refs"] or "[]")
            if r["case_id"] in damage:      # Story 12 photo check
                sev = [d["predicted_severity"] for d in damage[r["case_id"]] if d["predicted_severity"]]
                out.append({"case_id": r["case_id"], "user_vehicle_id": r["user_vehicle_id"],
                            "vehicle": labels.get(r["user_vehicle_id"], ""), "question": r["symptom_text"],
                            "language": r["language"], "code": None, "kind": "damage",
                            "photos": len(damage[r["case_id"]]), "sources": 0,
                            "status": "assessed" if sev else "inconclusive",
                            "severity": max(sev, key=("minor", "moderate", "severe").index) if sev else None,
                            "category": None, "urgency": None, "asked_at_ms": id_timestamp_ms(r["case_id"])})
                continue
            out.append({"case_id": r["case_id"], "user_vehicle_id": r["user_vehicle_id"],
                        "vehicle": labels.get(r["user_vehicle_id"], ""), "question": r["symptom_text"],
                        "language": r["language"], "code": r["code"], "kind": "question", "sources": len(refs),
                        "status": "answered" if refs else "abstained",
                        # An abstained case keeps its prediction in the database (for evaluation)
                        # but the owner never sees it as a reliable label (Story 5).
                        "category": r["predicted_category"] if refs else None,
                        "urgency": r["predicted_urgency"] if refs else None,
                        "asked_at_ms": id_timestamp_ms(r["case_id"])})
        out.sort(key=lambda x: x["case_id"], reverse=True)   # time-ordered ids
        return out[:limit]

    # ------------------------------------------------------ mechanic notes
    def submit_note(self, user: dict, *, topic: str, advice: str, manufacturer: str, model: str, years: str,
                    experience_years: str = "", workshop: str = "", city: str = "", consent: bool = False) -> dict:
        topic, advice = (topic or "").strip(), (advice or "").strip()
        if not consent:
            raise Invalid("Tick the consent box: your name and advice will be shown to car owners.")
        if len(topic) < 3 or len(advice) < 20:
            raise Invalid("Add a short topic and at least one full sentence of advice.")
        if len(advice) > 1500:
            raise Invalid("Keep a note under 1,500 characters; split longer advice into several notes.")
        yrs = _years(years)
        if bool(model.strip()) != bool(yrs):
            raise Invalid("Fill in both the model and the years, or leave both empty for advice about any car.")
        targets: list[str | None] = []
        for y in yrs:
            vids = self.repo.find_vehicle_ids(manufacturer, model, y)
            if not vids:
                raise Invalid(f"No {manufacturer} {model} {y} in the vehicle list.")
            targets.append(vids[0])
        if not yrs:
            targets = [None]
        group = time_ordered_id()
        details = ", ".join(x for x in [f"{experience_years.strip()} yrs" if str(experience_years).strip() else "",
                                        workshop.strip(), city.strip()] if x)
        name = (f"Mechanic note: {user['full_name']}" + (f" ({details})" if details else "")
                + f", {dt.date.today().isoformat()}")
        for vid in targets:
            doc_id = str(uuid.uuid4())
            self.repo.insert_document({
                "document_id": doc_id, "vehicle_id": vid, "document_name": name, "document_type": PENDING,
                "version": group, "source": f"app:{user['user_id']}",
                "license_note": "Submitted by the mechanic in the app with consent to publish (proposal §9.2)",
                "ingest_date": dt.date.today().isoformat(),
            })
            self.repo.insert_chunks([{
                "chunk_id": str(uuid.uuid4()), "document_id": doc_id, "section": topic, "page_number": None,
                "text": f"{topic}: {advice}", "embedding": None, "chunk_type": APPROVED,
            }])
        return self._note_groups(where="d.version = :g", params={"g": group})[0]

    def _note_groups(self, where: str, params: dict) -> list[dict]:
        rows = self.db.query(f"""
            SELECT d.version AS group_id, d.document_type, d.document_name, d.source, c.section, c.text,
                   v.manufacturer, v.model, v.year
            FROM document d JOIN documentchunk c ON c.document_id = d.document_id
            LEFT JOIN vehicle v ON v.vehicle_id = d.vehicle_id
            WHERE d.document_type IN ('{PENDING}', '{APPROVED}') AND d.source LIKE :app_prefix AND {where}""",
            {**params, "app_prefix": "app:%"})
        groups: dict[str, dict] = {}
        for r in rows:
            g = groups.setdefault(r["group_id"], {
                "group_id": r["group_id"], "status": "approved" if r["document_type"] == APPROVED else "pending",
                "author": r["document_name"].split(",")[0].replace("Mechanic note: ", ""),
                "author_user_id": r["source"][4:], "source_label": r["document_name"],
                "topic": r["section"], "advice": r["text"].split(": ", 1)[-1],
                "vehicle": None, "years": [], "submitted_at_ms": id_timestamp_ms(r["group_id"]),
            })
            if r["model"]:
                g["vehicle"] = f"{r['manufacturer']} {r['model']}"
                g["years"].append(int(r["year"]))
        for g in groups.values():
            g["years"].sort()
        return sorted(groups.values(), key=lambda g: g["group_id"], reverse=True)

    def my_notes(self, user_id: str) -> list[dict]:
        return self._note_groups("d.source = :s", {"s": f"app:{user_id}"})

    # ------------------------------------------------------------ admin
    def notes_for_review(self, status: str | None = None) -> list[dict]:
        groups = self._note_groups("1 = 1", {})
        return [g for g in groups if status is None or g["status"] == status]

    def approve_note(self, group_id: str, embedder) -> dict:
        chunks = self.db.query("""SELECT c.chunk_id, c.text FROM documentchunk c
                                  JOIN document d ON d.document_id = c.document_id
                                  WHERE d.version = :g AND d.document_type = :p""", {"g": group_id, "p": PENDING})
        if not chunks:
            raise NotFound("No pending note with that id.")
        vecs = embedder.encode([c["text"] for c in chunks])
        emb = self.db.vector_param("e")
        for c, v in zip(chunks, vecs):
            self.db.execute(f"UPDATE documentchunk SET embedding = {emb} WHERE chunk_id = :c",
                            {"e": encode_embedding(v), "c": c["chunk_id"]})
        self.db.execute("UPDATE document SET document_type = :a WHERE version = :g AND document_type = :p",
                        {"a": APPROVED, "g": group_id, "p": PENDING})
        return self._note_groups("d.version = :g", {"g": group_id})[0]

    def reject_note(self, group_id: str) -> None:
        if not self.db.query("SELECT 1 FROM document WHERE version = :g AND document_type = :p",
                             {"g": group_id, "p": PENDING}):
            raise NotFound("No pending note with that id.")
        self.db.execute("""DELETE FROM documentchunk WHERE document_id IN
                           (SELECT document_id FROM document WHERE version = :g AND document_type = :p)""",
                        {"g": group_id, "p": PENDING})
        self.db.execute("DELETE FROM document WHERE version = :g AND document_type = :p", {"g": group_id, "p": PENDING})

    def documents(self) -> list[dict]:
        rows = self.db.query("""
            SELECT d.document_id, d.document_name, d.document_type, d.source, d.license_note, d.ingest_date,
                   v.manufacturer, v.model, v.year, COUNT(c.chunk_id) AS chunks
            FROM document d LEFT JOIN vehicle v ON v.vehicle_id = d.vehicle_id
            LEFT JOIN documentchunk c ON c.document_id = d.document_id
            WHERE d.document_type <> :p
            GROUP BY d.document_id, d.document_name, d.document_type, d.source, d.license_note, d.ingest_date,
                     v.manufacturer, v.model, v.year
            ORDER BY d.document_type, d.document_name""", {"p": PENDING})
        for r in rows:
            r["scope"] = f"{r['manufacturer']} {r['model']} {r['year']}" if r["model"] else "All vehicles"
        return rows

    def stats(self) -> dict:
        cases = self.db.query("""SELECT language, evidence_refs, predicted_urgency FROM diagnosticcase
                                 WHERE case_id NOT IN (SELECT case_id FROM damageimage WHERE case_id IS NOT NULL)""")
        sev_rows = self.db.query("""SELECT predicted_severity AS s, COUNT(*) AS n FROM damageimage
                                    GROUP BY predicted_severity""")
        by_lang: dict[str, dict] = {}
        by_urgency: dict[str, int] = {}
        for c in cases:
            if c["predicted_urgency"]:
                by_urgency[c["predicted_urgency"]] = by_urgency.get(c["predicted_urgency"], 0) + 1
            d = by_lang.setdefault(c["language"] or "unknown", {"questions": 0, "answered": 0, "abstained": 0})
            d["questions"] += 1
            d["answered" if json.loads(c["evidence_refs"] or "[]") else "abstained"] += 1
        roles = {r["role"]: r["n"] for r in self.db.query("SELECT role, COUNT(*) AS n FROM appuser GROUP BY role")}
        docs = self.db.query("""SELECT document_type, COUNT(*) AS n FROM document GROUP BY document_type""")
        chunks = self.db.query("""SELECT COUNT(*) AS n FROM documentchunk c JOIN document d
                                  ON d.document_id = c.document_id WHERE d.document_type <> :p""", {"p": PENDING})
        return {
            "questions": len(cases), "by_language": by_lang, "users_by_role": roles,
            "by_urgency": by_urgency,
            "damage_photos": {(r["s"] or "inconclusive"): r["n"] for r in sev_rows},
            "documents_by_type": {d["document_type"]: d["n"] for d in docs if d["document_type"] != PENDING},
            "searchable_passages": chunks[0]["n"],
            "pending_notes": len(self.notes_for_review("pending")),
            "vehicles_registered": self.db.query("SELECT COUNT(*) AS n FROM uservehicle")[0]["n"],
        }
