"""Master seed script for AutoCare AI.

Seeds all 3 vehicle models (Toyota Corolla, Honda Civic, Suzuki Swift, 2015-2025):
1. Vehicles into `vehicle` table.
2. SAE J2012 OBD-II codes into `diagnosticcode` table.
3. Structured owner manuals & periodic maintenance chunks into `document` and `documentchunk`.
4. Automotive Knowledge Graph nodes and causal edges into `graphnode` and `graphedge`.
5. Seed prior diagnostic cases with verified resolutions into `diagnosticcase` for case-bank retrieval.

Usage:
  python -m ingest.seed_all_three_cars
"""
from __future__ import annotations

import csv
import json
import os
import uuid

from autocare.config import load_settings
from autocare.db import Database
from autocare.ml import build_models
from autocare.repository import Repository, encode_embedding
from ingest.dtc_ingest import load as load_dtc
from ingest.generate_corpora import generate_obd2_codes_csv, generate_vehicles_csv
from ingest.generate_manuals import seed_manuals_into_db

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def seed_vehicles(repo: Repository):
    vehicles_path = os.path.join(DATA_DIR, "vehicles.csv")
    if not os.path.exists(vehicles_path):
        generate_vehicles_csv()

    with open(vehicles_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        repo.upsert_vehicle({
            "vehicle_id": r["vehicle_id"],
            "manufacturer": r["manufacturer"].strip(),
            "model": r["model"].strip(),
            "variant": r.get("variant"),
            "year": int(r["year"]),
            "engine": r.get("engine"),
            "transmission": r.get("transmission"),
            "fuel_type": r.get("fuel_type"),
        })
    print(f"Seeded {len(rows)} vehicle configurations into database.")


def seed_obd2_codes(repo: Repository, embedder):
    dtc_path = os.path.join(DATA_DIR, "obd2_codes.csv")
    if not os.path.exists(dtc_path):
        generate_obd2_codes_csv()

    load_dtc(
        repo=repo,
        embedder=embedder,
        csv_path=dtc_path,
        document_name="SAE J2012 OBD-II Diagnostic Trouble Codes Reference",
        source="SAE International J2012 Standards Reference",
        license_note="Public diagnostic code standard reference",
    )
    print("Seeded OBD-II diagnostic trouble codes and chunks into database.")


def seed_knowledge_graph(repo: Repository):
    # 1. Nodes
    nodes = [
        # Components
        ("brake_pads", "component", "Brake Pads", ["front pads", "rear pads", "brake lining"]),
        ("brake_rotors", "component", "Brake Disc Rotors", ["discs", "rotors"]),
        ("brake_caliper", "component", "Brake Caliper", ["caliper pin", "brake piston"]),
        ("brake_master_cylinder", "component", "Brake Master Cylinder", ["master cylinder", "brake pump"]),
        ("brake_fluid", "fluid", "Brake Fluid", ["DOT 3", "DOT 4"]),
        ("battery_12v", "component", "12V Battery", ["car battery", "lead acid battery"]),
        ("alternator", "component", "Alternator", ["charging generator", "dynamo"]),
        ("drive_belt", "component", "Serpentine Drive Belt", ["alternator belt", "fan belt"]),
        ("starter_motor", "component", "Starter Motor", ["starter", "self motor"]),
        ("spark_plug", "component", "Spark Plugs", ["iridium plug", "ignition plug"]),
        ("ignition_coil", "component", "Ignition Coil", ["coil pack", "plug coil"]),
        ("fuel_injector", "component", "Fuel Injector", ["injector nozzle"]),
        ("fuel_pump", "component", "Fuel Pump", ["gas pump"]),
        ("thermostat", "component", "Thermostat", ["coolant thermostat"]),
        ("radiator", "component", "Radiator", ["cooling radiator"]),
        ("water_pump", "component", "Water Pump", ["coolant pump"]),
        ("coolant", "fluid", "Engine Coolant", ["antifreeze", "radiator fluid"]),
        ("cvt_belt", "component", "CVT Steel Belt", ["push belt"]),
        ("cvt_fluid", "fluid", "CVT Transmission Fluid", ["HCF-2", "CVT Fluid FE", "Green-2"]),
        ("clutch_disc", "component", "Clutch Friction Disc", ["clutch plate"]),
        ("tie_rod_end", "component", "Tie Rod Ends", ["steering tie rod"]),
        ("control_arm_bushing", "component", "Lower Control Arm Bushing", ["suspension bush", "A-arm bush"]),
        ("stabilizer_link", "component", "Stabilizer Bar Link", ["sway bar link", "end link"]),
        ("eps_motor", "component", "Electric Power Steering Motor", ["EPS motor", "steering rack motor"]),

        # Symptoms
        ("grinding_on_braking", "symptom", "Grinding Noise When Braking", ["ghisne ki awaz", "scraping noise"]),
        ("squealing_on_braking", "symptom", "Squealing Noise When Braking", ["cheekhne ki awaz", "brake squeak"]),
        ("spongy_brake_pedal", "symptom", "Spongy / Soft Brake Pedal", ["naram brake pedal", "sinking pedal"]),
        ("brake_warning_light", "symptom", "Red Brake Warning Light On", ["lal brake light", "parking light on"]),
        ("engine_overheating", "symptom", "Engine Overheating", ["gaari garam hona", "temperature high", "heat up"]),
        ("steam_from_hood", "symptom", "Steam from Engine Compartment", ["dhuwan nikalna", "boiling coolant"]),
        ("rough_idle", "symptom", "Rough Idle & Engine Shaking", ["engine kaanpna", "vibrating idle"]),
        ("engine_misfire", "symptom", "Engine Combustion Misfire", ["misfire", "jharke lena"]),
        ("battery_warning_light", "symptom", "Battery Warning Lamp Illuminated", ["battery light on", "charging fault"]),
        ("no_crank_no_start", "symptom", "Engine Will Not Crank Or Start", ["gaari start nahi ho rahi", "dead battery"]),
        ("cvt_shudder", "symptom", "Transmission Shudder on Acceleration", ["CVT shudder", "transmission jerk"]),
        ("clutch_slipping", "symptom", "Clutch Slipping Uphill", ["clutch slip", "engine revs high without speed"]),
        ("knocking_over_bumps", "symptom", "Knocking Noise Over Bumps", ["khadkhat ki awaz", "suspension rattle"]),
        ("heavy_steering", "symptom", "Heavy Or Stiff Steering", ["steering sakht", "EPS light on"]),

        # Actions
        ("replace_brake_pads", "action", "Replace Brake Pads", ["install new pads"]),
        ("resurface_brake_rotors", "action", "Resurface or Replace Brake Rotors", ["facing rotors"]),
        ("bleed_brake_system", "action", "Bleed Hydraulic Brake System", ["flush brake fluid"]),
        ("replace_master_cylinder", "action", "Replace Brake Master Cylinder", ["new brake master pump"]),
        ("replace_battery", "action", "Replace 12V Battery", ["new battery"]),
        ("replace_alternator", "action", "Replace Alternator", ["new alternator"]),
        ("tension_drive_belt", "action", "Tension or Replace Drive Belt", ["belt replacement"]),
        ("replace_spark_plugs", "action", "Replace Spark Plugs", ["new spark plugs"]),
        ("replace_ignition_coil", "action", "Replace Ignition Coil", ["new coil pack"]),
        ("replace_thermostat", "action", "Replace Thermostat", ["new thermostat"]),
        ("drain_refill_cvt_fluid", "action", "Drain and Refill CVT Fluid", ["CVT oil change"]),
    ]

    for nid, ntype, name, aliases in nodes:
        repo.db.execute(
            """
            INSERT INTO graphnode (node_id, node_type, canonical_name, aliases, vehicle_scope)
            VALUES (:node_id, :node_type, :canonical_name, :aliases, NULL)
            ON CONFLICT (node_id) DO UPDATE SET
                node_type = excluded.node_type, canonical_name = excluded.canonical_name,
                aliases = excluded.aliases
            """,
            {"node_id": nid, "node_type": ntype, "canonical_name": name, "aliases": json.dumps(aliases)}
        )

    # 2. Edges
    edges = [
        # Worn brake pads -> grinding / squealing -> replace pads / rotors
        ("brake_pads", "grinding_on_braking", "causes", 0.95),
        ("brake_pads", "squealing_on_braking", "causes", 0.90),
        ("brake_pads", "brake_rotors", "causes", 0.85),
        ("brake_rotors", "grinding_on_braking", "causes", 0.90),
        ("brake_pads", "replace_brake_pads", "addressed_by", 0.95),
        ("brake_rotors", "resurface_brake_rotors", "addressed_by", 0.90),

        # Hydraulic / Master cylinder -> spongy pedal / warning light
        ("brake_fluid", "spongy_brake_pedal", "causes", 0.85),
        ("brake_fluid", "brake_warning_light", "causes", 0.90),
        ("brake_master_cylinder", "spongy_brake_pedal", "causes", 0.80),
        ("brake_master_cylinder", "replace_master_cylinder", "addressed_by", 0.85),
        ("spongy_brake_pedal", "bleed_brake_system", "addressed_by", 0.90),

        # Alternator / belt / battery chain
        ("drive_belt", "alternator", "causes", 0.85),
        ("alternator", "battery_12v", "causes", 0.92),
        ("alternator", "battery_warning_light", "causes", 0.95),
        ("battery_12v", "no_crank_no_start", "causes", 0.95),
        ("drive_belt", "tension_drive_belt", "addressed_by", 0.90),
        ("alternator", "replace_alternator", "addressed_by", 0.90),
        ("battery_12v", "replace_battery", "addressed_by", 0.95),

        # Drive belt / water pump / thermostat -> engine overheating -> steam
        ("drive_belt", "water_pump", "causes", 0.80),
        ("water_pump", "engine_overheating", "causes", 0.90),
        ("thermostat", "engine_overheating", "causes", 0.92),
        ("coolant", "engine_overheating", "causes", 0.90),
        ("engine_overheating", "steam_from_hood", "causes", 0.88),
        ("thermostat", "replace_thermostat", "addressed_by", 0.92),

        # Ignition / Spark plug / Coil -> Misfire -> Rough idle
        ("spark_plug", "engine_misfire", "causes", 0.92),
        ("ignition_coil", "engine_misfire", "causes", 0.90),
        ("fuel_injector", "engine_misfire", "causes", 0.85),
        ("engine_misfire", "rough_idle", "causes", 0.95),
        ("spark_plug", "replace_spark_plugs", "addressed_by", 0.95),
        ("ignition_coil", "replace_ignition_coil", "addressed_by", 0.90),

        # Transmission / CVT
        ("cvt_fluid", "cvt_shudder", "causes", 0.90),
        ("cvt_fluid", "drain_refill_cvt_fluid", "addressed_by", 0.92),
        ("clutch_disc", "clutch_slipping", "causes", 0.95),

        # Suspension & Steering
        ("stabilizer_link", "knocking_over_bumps", "causes", 0.90),
        ("control_arm_bushing", "knocking_over_bumps", "causes", 0.88),
        ("eps_motor", "heavy_steering", "causes", 0.92),
    ]

    for src, tgt, rel, conf in edges:
        eid = f"e-{src}-{tgt}-{rel}"
        repo.db.execute(
            """
            INSERT INTO graphedge (edge_id, source_node, target_node, relation_type, confidence, review_status)
            VALUES (:eid, :src, :tgt, :rel, :conf, 'reviewed')
            ON CONFLICT (edge_id) DO UPDATE SET
                confidence = excluded.confidence, review_status = 'reviewed'
            """,
            {"eid": eid, "src": src, "tgt": tgt, "rel": rel, "conf": conf}
        )
    print(f"Seeded {len(nodes)} knowledge graph nodes and {len(edges)} causal edges.")


def seed_prior_cases(repo: Repository):
    cases = [
        {
            "case_id": "seed-case-001",
            "symptom_text": "Loud grinding noise when pressing the brakes, metallic friction sound",
            "code": None,
            "category": "braking",
            "urgency": "high",
            "outcome": "Replaced worn front brake pads and resurfaced brake disc rotors. Stopping power fully restored and noise resolved.",
            "provenance": "seeded",
        },
        {
            "case_id": "seed-case-002",
            "symptom_text": "Brake pedal sinking all the way down to floor, pedal feels very spongy",
            "code": None,
            "category": "braking",
            "urgency": "critical",
            "outcome": "Diagnosed leaking master cylinder primary seal and air in rear brake line. Replaced master cylinder assembly and bled brake fluid with DOT 4.",
            "provenance": "seeded",
        },
        {
            "case_id": "seed-case-003",
            "symptom_text": "Engine shaking at idle with check engine light blinking, code P0301",
            "code": "P0301",
            "category": "engine",
            "urgency": "high",
            "outcome": "Replaced cylinder 1 faulty ignition coil pack and installed 4 new Iridium spark plugs. Cleared P0301; smooth idle restored.",
            "provenance": "seeded",
        },
        {
            "case_id": "seed-case-004",
            "symptom_text": "Temperature gauge needle rising to H mark, steam escaping from radiator cap",
            "code": "P0117",
            "category": "cooling",
            "urgency": "critical",
            "outcome": "Thermostat was jammed closed. Replaced thermostat and gasket, performed cooling system pressure test and refilled with Super Long Life Coolant.",
            "provenance": "seeded",
        },
        {
            "case_id": "seed-case-005",
            "symptom_text": "Battery light illuminated on dashboard, dim headlights, radio rebooting",
            "code": "P0562",
            "category": "electrical",
            "urgency": "high",
            "outcome": "Alternator internal voltage regulator failed and charging output was 11.2V. Replaced alternator unit. Charging restored to 14.2V.",
            "provenance": "seeded",
        },
        {
            "case_id": "seed-case-006",
            "symptom_text": "Car shudders and vibrates when accelerating from standstill, CVT slipping",
            "code": "P0730",
            "category": "transmission",
            "urgency": "high",
            "outcome": "CVT fluid was severely degraded and dark. Performed complete drain and refill using genuine OEM CVT Fluid. Judder completely eliminated.",
            "provenance": "seeded",
        },
    ]

    for c in cases:
        repo.db.execute(
            """
            INSERT INTO diagnosticcase (case_id, user_vehicle_id, symptom_text, language, code,
                                        predicted_category, predicted_urgency, confidence,
                                        outcome, provenance)
            VALUES (:cid, NULL, :stext, 'en', :code, :cat, :urg, 0.95, :outcome, :prov)
            ON CONFLICT (case_id) DO UPDATE SET
                outcome = excluded.outcome, provenance = excluded.provenance
            """,
            {
                "cid": c["case_id"], "stext": c["symptom_text"], "code": c["code"],
                "cat": c["category"], "urg": c["urgency"], "outcome": c["outcome"],
                "prov": c["provenance"],
            }
        )
    print(f"Seeded {len(cases)} prior diagnostic cases for case-bank similarity retrieval.")


def main():
    settings = load_settings()
    db = Database(settings.database_url)
    db.create_schema()
    repo = Repository(db)
    embedder, _ = build_models(settings)

    print("=== SEEDING AUTOCARE AI (ALL 3 VEHICLES: 2015-2025) ===")
    seed_vehicles(repo)
    seed_obd2_codes(repo, embedder)
    seed_manuals_into_db(repo, embedder)
    seed_knowledge_graph(repo)
    seed_prior_cases(repo)
    print("=== ALL 3 VEHICLES & INTELLIGENT MODULE CORPORA SUCCESSFULLY INITIALIZED ===")


if __name__ == "__main__":
    main()
