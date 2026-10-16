"""Seed VEHICLE rows from a CSV, and (dev only) create a USERVEHICLE to test with.

Vehicle CSV columns: manufacturer, model, variant, year, engine, transmission, fuel_type
(vehicle_id optional; generated as toyota-corolla-2018-<variant> if blank).
Fill variants/engines from the official spec sheets — do not guess them.

Usage:
  python -m ingest.seed_vehicles vehicles --csv data/vehicles_corolla.csv
  python -m ingest.seed_vehicles dev-user-vehicle --vehicle-id toyota-corolla-2018-xli \
      --user-id dev-user --mileage 82000
"""
from __future__ import annotations

import argparse
import csv
import re
import uuid


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-") or "base"


def _none(v):
    v = (v or "").strip()
    return v or None


def main() -> None:
    from autocare.config import load_settings
    from autocare.db import Database
    from autocare.repository import Repository

    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("vehicles")
    v.add_argument("--csv", required=True)
    u = sub.add_parser("dev-user-vehicle")
    u.add_argument("--vehicle-id", required=True)
    u.add_argument("--user-id", default="dev-user")
    u.add_argument("--mileage", type=int, default=None)
    a = ap.parse_args()

    db = Database(load_settings().database_url)
    db.create_schema()
    repo = Repository(db)

    if a.cmd == "vehicles":
        with open(a.csv, newline="", encoding="utf-8") as f:
            n = 0
            for r in csv.DictReader(f):
                year = int(r["year"])
                vid = _none(r.get("vehicle_id")) or f"{slug(r['manufacturer'])}-{slug(r['model'])}-{year}-{slug(r.get('variant'))}"
                repo.upsert_vehicle({
                    "vehicle_id": vid, "manufacturer": r["manufacturer"].strip(),
                    "model": r["model"].strip(), "variant": _none(r.get("variant")), "year": year,
                    "engine": _none(r.get("engine")), "transmission": _none(r.get("transmission")),
                    "fuel_type": _none(r.get("fuel_type")),
                })
                n += 1
        print(f"Upserted {n} vehicles")
    else:
        uvid = str(uuid.uuid4())
        repo.insert_user_vehicle({
            "user_vehicle_id": uvid, "user_id": a.user_id, "vehicle_id": a.vehicle_id,
            "registration_year": None, "current_mileage": a.mileage,
            "last_reading_date": None, "usage_profile": None,
        })
        print(f"user_vehicle_id = {uvid}")


if __name__ == "__main__":
    main()
