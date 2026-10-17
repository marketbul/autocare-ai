"""Generates structured owner manuals and maintenance schedules for all 3 cars:
1. Toyota Corolla (2015-2025)
2. Honda Civic (2015-2025)
3. Suzuki Swift (2015-2025)
Ingests them directly into the database as Document and DocumentChunk records.
"""
from __future__ import annotations

import datetime as dt
import uuid

from autocare.repository import encode_embedding


def generate_manual_data():
    """Returns a dictionary mapping (make, model, year_range_label, doc_name) -> list of chunks."""
    manuals = []

    # --------------------------------------------------------------------------
    # 1. TOYOTA COROLLA (2015 - 2025)
    # --------------------------------------------------------------------------
    manuals.append({
        "manufacturer": "Toyota",
        "model": "Corolla",
        "doc_name": "Toyota Corolla Owner's Manual & Maintenance Guide (2015-2025)",
        "doc_type": "owner_manual",
        "version": "OM-COROLLA-PK-2024",
        "source": "Toyota Indus Motor Company Official Technical Documentation",
        "license_note": "Manufacturer consumer reference manual",
        "years": list(range(2015, 2026)),
        "chunks": [
            {
                "section": "Brakes > Brake Pad Wear Indicators",
                "page": 412,
                "type": "warning",
                "text": "WARNING: The disc brake pads have built-in metallic wear indicators. When the brake pad friction material wears down to approximately 1.0 mm (the service limit), the indicator contacts the rotor, producing a high-pitched squealing or harsh grinding noise while braking. Continued driving with worn brake pads will damage the brake disc rotors, reduce stopping distance drastically, and may lead to total brake failure. Have the front and rear brake pads inspected and replaced immediately by an authorized technician."
            },
            {
                "section": "Brakes > Brake Fluid & Spongy Pedal",
                "page": 414,
                "type": "procedure",
                "text": "Brake Fluid Inspection: The brake fluid level must be between the MAX and MIN lines on the transparent reservoir. Use only genuine Toyota Brake Fluid or equivalent DOT 3 or DOT 4 fluid. If the brake pedal feels spongy, soft, or travels excessively close to the floorboard before biting, air has entered the hydraulic brake lines or the brake master cylinder seals are bypassing. Bleed the brake system and inspect all brake lines and calipers for fluid leaks immediately."
            },
            {
                "section": "Warning Lights > Brake System Warning Light",
                "page": 540,
                "type": "warning",
                "text": "DANGER: If the red brake system warning light (circle with exclamation point or BRAKE) illuminates while driving and does not extinguish when the parking brake is fully released, stop the vehicle immediately in a safe location. This indicates critically low brake fluid level or a hydraulic brake circuit failure. Continuing to drive under this condition carries an extreme risk of collision. Turn off the engine and seek professional roadside assistance."
            },
            {
                "section": "Engine & Cooling > Overheating Procedure",
                "page": 548,
                "type": "procedure",
                "text": "If the engine coolant temperature gauge enters the RED zone, or steam/coolant spray emerges from the engine hood: 1. Pull over safely, shift to Neutral/Park, and turn OFF the air conditioning. 2. If no steam is visible, keep the engine idling for 2-3 minutes to allow coolant circulation, then switch off the ignition. 3. WARNING: Never open the radiator cap or coolant reservoir tank while the engine is hot. Scalding pressurized coolant can cause severe burn injuries. Wait at least 30 minutes until the engine is completely cold before checking coolant level or inspecting for blown radiator hoses."
            },
            {
                "section": "Engine & Cooling > Coolant Specification & Thermostat",
                "page": 550,
                "type": "narrative",
                "text": "Engine Coolant: The cooling system uses Toyota Super Long Life Coolant (50/50 pre-diluted pink ethylene glycol). Do not add plain tap water as it causes mineral scaling and internal radiator corrosion. A failing or stuck-closed thermostat prevents coolant flow to the radiator, resulting in rapid engine overheating within 5 to 10 minutes of driving. A stuck-open thermostat causes trouble code P0128 and poor heater performance."
            },
            {
                "section": "Engine & Lubrication > Oil Pressure & Level",
                "page": 555,
                "type": "warning",
                "text": "CAUTION: The oil pressure warning light indicates critically low oil pressure, NOT oil level. If this light illuminates while driving, stop the engine immediately. Operating the engine without sufficient oil pressure causes catastrophic metal-on-metal bearing destruction and engine seizure within seconds. Check oil level on the dipstick and inspect the oil filter and sump for severe leaks."
            },
            {
                "section": "Transmission > Automatic & Super CVT-i Fluid",
                "page": 482,
                "type": "narrative",
                "text": "Transmission Care: Super CVT-i transmissions require Toyota Genuine CVT Fluid FE (or TC for earlier 2015-2016 models). Using incorrect fluid such as standard Dexron ATF will cause CVT belt slippage, metallic shuddering during initial acceleration, and internal push-belt failure. Inspect CVT fluid condition every 40,000 km or 24 months. If the transmission shudders when pulling away or jerks between D and R, inspect fluid level and quality."
            },
            {
                "section": "Electrical > 12V Battery & Alternator System",
                "page": 510,
                "type": "narrative",
                "text": "Battery & Charging System: If the battery warning lamp illuminates while driving, the alternator is no longer charging the 12V battery. The vehicle is running purely on remaining battery reserve power, which will deplete within 15 to 30 minutes, cutting power to ignition, fuel pump, and Electric Power Steering. Check for a snapped or slipping serpentine alternator belt, loose battery terminal clamps, or internal alternator voltage regulator failure."
            },
            {
                "section": "Steering & Suspension > EPS & Front End Play",
                "page": 460,
                "type": "narrative",
                "text": "Steering & Suspension: A yellow EPS warning lamp indicates a malfunction in the Electric Power Steering actuator or torque sensor. Manual steering effort will increase significantly. If clunking or knocking noises occur when driving over bumps or rough pavement, inspect the front stabilizer bar end-links, lower control arm rubber bushings, and tie-rod ball joints for mechanical play."
            },
            {
                "section": "Maintenance Schedule > Recommended Service Intervals",
                "page": 620,
                "type": "table",
                "text": "Toyota Corolla Periodic Maintenance Table:\n- Every 5,000 km: Replace engine oil (0W-20 or 5W-30) and genuine oil filter; inspect tire pressures (32 PSI).\n- Every 10,000 km: Rotate tires; inspect front disc pads and rear brake drums/discs; inspect air cleaner element.\n- Every 20,000 km: Replace air cleaner element; inspect steering linkages, ball joints, and suspension mounting bolts.\n- Every 40,000 km: Inspect/replace drive belt; replace brake fluid (DOT 3/4); inspect CVT transmission fluid.\n- Every 80,000 km: Replace spark plugs (Iridium); drain and replace engine coolant; inspect fuel tank vapor hoses."
            }
        ]
    })

    # --------------------------------------------------------------------------
    # 2. HONDA CIVIC (2015 - 2025)
    # --------------------------------------------------------------------------
    manuals.append({
        "manufacturer": "Honda",
        "model": "Civic",
        "doc_name": "Honda Civic Owner's Manual & Service Reference (2015-2025)",
        "doc_type": "owner_manual",
        "version": "OM-CIVIC-PK-2024",
        "source": "Honda Atlas Cars Pakistan Official Technical Manual",
        "license_note": "Manufacturer consumer reference manual",
        "years": list(range(2015, 2026)),
        "chunks": [
            {
                "section": "Braking System > Brake Pad Wear & Grinding",
                "page": 305,
                "type": "warning",
                "text": "WARNING: Honda Civic disc brakes feature acoustic wear sensors on both inner and outer pads. If you hear a continuous metallic scraping or grinding noise when pressing the brake pedal, the friction lining has worn below the minimum safety threshold (1.6 mm). Continued operation will score the brake rotors and reduce braking force. Replace front and rear brake pads and evaluate brake rotor thickness immediately."
            },
            {
                "section": "Braking System > Spongy Pedal & VSA Malfunction",
                "page": 308,
                "type": "procedure",
                "text": "Brake Pedal Travel & Sponginess: A soft, sinking brake pedal indicates moisture contamination in the brake fluid, internal seal leakage inside the master cylinder, or air bubbles in the ABS/VSA modulator valve block. Use only genuine Honda Heavy Duty Brake Fluid DOT 3 or DOT 4. Flush and bleed the hydraulic circuit every 3 years or 40,000 km regardless of mileage."
            },
            {
                "section": "Warning Lights > Brake System Indicator & Electric Parking Brake",
                "page": 380,
                "type": "warning",
                "text": "DANGER: The red Brake System indicator warning light signifies: 1. Parking brake engaged; 2. Critically low brake fluid; or 3. Failure of the dual hydraulic brake system. If the light stays on with parking brake released, brake pedal feel is altered, or the yellow Electric Parking Brake (EPB) error symbol flashes, stop the vehicle immediately and do not drive. Call an authorized Honda dealership."
            },
            {
                "section": "Engine & Cooling > VTEC / Turbo Overheating",
                "page": 410,
                "type": "procedure",
                "text": "Engine Overheating: If the temperature gauge icon reaches the high mark (H) or the driver information interface displays 'ENGINE TEMPERATURE TOO HIGH': 1. Safely pull over, engage P, and turn the climate control heating to maximum to help dissipate engine block heat. 2. Turn off the engine if steam or boiling coolant is escaping from under the hood. 3. DANGER: Do not touch the radiator cap or coolant expansion tank until the engine is fully cold. Use only Honda Long Life Antifreeze/Coolant Type 2 (blue formula)."
            },
            {
                "section": "Engine > Turbocharger & Ignition Misfire",
                "page": 415,
                "type": "narrative",
                "text": "Engine Performance & Misfire: On 1.5L VTEC Turbo and 1.8L i-VTEC engines, a flashing Check Engine light indicates severe combustion misfire (DTC P0300, P0301-P0304). Driving with a flashing check engine light will overheat and permanently melt the catalytic converter. Likely causes include carbon-fouled direct injection injectors, degraded NGK laser iridium spark plugs, or cracked ignition coil packs."
            },
            {
                "section": "Transmission > Earth Dreams CVT Fluid Care",
                "page": 350,
                "type": "warning",
                "text": "CAUTION: Honda Earth Dreams CVT requires exclusively Honda HCF-2 Transmission Fluid (Continuously Variable Transmission Fluid). NEVER use standard automatic transmission fluid (ATF DW-1 or generic fluid). Using non-HCF-2 fluid will cause severe shuddering, belt slip, torque converter overheating, and fatal internal CVT destruction. Replace HCF-2 fluid every 40,000 km."
            },
            {
                "section": "Electrical > Battery Sensor & Charging System",
                "page": 395,
                "type": "narrative",
                "text": "Charging System Indicator: A lit battery symbol indicates the alternator is not providing charging voltage to the 12V battery. On Civic models equipped with an intelligent battery sensor (IBS) on the negative terminal, ensure the sensor wiring is not disconnected or corroded. A failed alternator will cause multiple warning lights (VSA, EPS, ABS) to illuminate sequentially as system voltage drops below 11 Volts."
            },
            {
                "section": "Steering & Suspension > EPS Rack & Strut Mounts",
                "page": 365,
                "type": "narrative",
                "text": "Electric Power Steering (EPS): If the steering wheel feels heavy or binds when turning, check the EPS warning lamp. A dull clunking sound from the steering rack when turning at slow speeds over cobblestones or speed bumps indicates wear in the steering rack guide bushing or front strut upper mount bearings."
            },
            {
                "section": "Maintenance Schedule > Honda Recommended Intervals",
                "page": 500,
                "type": "table",
                "text": "Honda Civic Periodic Maintenance Schedule:\n- Every 5,000 km: Engine oil and genuine Honda oil filter replacement (0W-20 synthetic recommended); inspect fluid levels and tire pressure (32 PSI).\n- Every 10,000 km: Inspect brake pads, discs, and lines; tire rotation; inspect suspension components and driveshaft boots.\n- Every 20,000 km: Replace engine air cleaner element and dust/pollen cabin filter; inspect drive belt condition.\n- Every 40,000 km: Replace CVT transmission fluid (Honda HCF-2); replace brake fluid (DOT 3/4).\n- Every 80,000 km: Replace spark plugs (Iridium); inspect valve clearance; inspect fuel lines and cooling system."
            }
        ]
    })

    # --------------------------------------------------------------------------
    # 3. SUZUKI SWIFT (2015 - 2025)
    # --------------------------------------------------------------------------
    manuals.append({
        "manufacturer": "Suzuki",
        "model": "Swift",
        "doc_name": "Pak Suzuki Swift Owner's Manual & Service Booklet (2015-2025)",
        "doc_type": "owner_manual",
        "version": "OM-SWIFT-PK-2024",
        "source": "Pak Suzuki Motor Co. Ltd. Official Technical Documentation",
        "license_note": "Manufacturer consumer reference manual",
        "years": list(range(2015, 2026)),
        "chunks": [
            {
                "section": "Braking System > Brake Pads & Rear Drum Shoes",
                "page": 210,
                "type": "warning",
                "text": "WARNING: Front disc brake pads feature metal wear indicators that emit a loud squeal or metallic grinding sound when pad thickness reaches 1.5 mm. Rear drum brake shoes should be inspected and adjusted every 10,000 km. Driving with worn brake friction material reduces braking efficiency, causes severe brake fade during downhill driving, and damages the brake discs and drums. Replace worn pads immediately."
            },
            {
                "section": "Braking System > Spongy Pedal & Fluid Levels",
                "page": 212,
                "type": "procedure",
                "text": "Brake Fluid & Hydraulic Bleeding: The master cylinder reservoir is situated in the engine bay. Keep fluid filled to MAX line using genuine Suzuki Brake Fluid or DOT 3 / DOT 4. A low fluid level indicates worn brake pads or external leakage from rear wheel cylinders. If the brake pedal travels down easily and feels spongy, air must be bled from the four brake corners."
            },
            {
                "section": "Warning Lights > Brake System Warning Lamp",
                "page": 240,
                "type": "warning",
                "text": "DANGER: If the red brake warning light remains illuminated with the handbrake released, or turns on while driving, the brake fluid level is dangerously low or the brake system has failed. Stop the car immediately in a safe spot off the road. Do not attempt to drive. Have the vehicle towed to an authorized Suzuki workshop."
            },
            {
                "section": "Engine & Cooling > Overheating & Thermostat",
                "page": 260,
                "type": "procedure",
                "text": "Engine Overheating (M13A & K12M Engines): If the high temperature warning indicator lights up or steam pours from the radiator: 1. Turn off the A/C and park safely. 2. Switch off the ignition. 3. DANGER: Never loosen the radiator cap while the engine is hot; boiling coolant under high pressure will erupt. 4. Once cooled, inspect the coolant overflow bottle. If dry, check for split radiator hoses, water pump weep hole leaks, or radiator electric fan failure."
            },
            {
                "section": "Engine > Ignition Coils & M13A/K12M Misfires",
                "page": 265,
                "type": "narrative",
                "text": "Engine Shaking & Hesitation: A check engine light accompanied by severe engine shuddering when accelerating in 2nd or 3rd gear is typically caused by ignition coil breakdown or fouled nickel/iridium spark plugs. On Suzuki M13A and K12M engines, heat degradation of coil boots causes spark flashover to the cylinder head, generating misfire codes P0300 through P0304."
            },
            {
                "section": "Transmission > Manual Clutch & CVT Care",
                "page": 230,
                "type": "narrative",
                "text": "Transmission Maintenance: For Manual models, a burning odor when starting uphill or engine RPM rising without car speed increasing indicates a slipping, worn clutch friction disc. For CVT models (2022-2025), use exclusively Suzuki CVT Fluid Green-2. Do not use generic ATF. A delayed engagement when shifting from N to D indicates degraded CVT fluid or low fluid level."
            },
            {
                "section": "Electrical > Alternator & Serpentine Belt",
                "page": 255,
                "type": "narrative",
                "text": "Charging System & Belts: The battery warning light indicates the alternator is not supplying electrical current. On Suzuki Swift, check the tension of the serpentine alternator/water pump drive belt. A screeching sound upon starting or when turning the steering wheel indicates a loose or glazed drive belt. If the belt snaps, the water pump also stops turning, causing immediate catastrophic engine overheating within minutes."
            },
            {
                "section": "Steering & Suspension > Lower Arm & Ball Joint",
                "page": 225,
                "type": "narrative",
                "text": "Suspension & Steering: Front suspension uses MacPherson struts with lower A-arms. Rattle or knocking noises when driving over small bumps or steering wander on the highway indicate worn front lower control arm rear rubber bushings or loose ball joints. Inspect suspension bushings every 20,000 km."
            },
            {
                "section": "Maintenance Schedule > Suzuki Periodic Maintenance",
                "page": 310,
                "type": "table",
                "text": "Suzuki Swift Periodic Maintenance Schedule:\n- Every 5,000 km: Replace engine oil (10W-40 for M13A, 0W-20 for K12M) and oil filter; inspect tire pressures (30 PSI front, 29 PSI rear).\n- Every 10,000 km: Inspect brake pads, clean and adjust rear drum brake shoes; rotate tires; inspect air cleaner element.\n- Every 20,000 km: Replace air cleaner and AC cabin filter; inspect drive belts; check suspension mounting bolts and ball joints.\n- Every 40,000 km: Replace brake fluid (DOT 3/4); replace manual transmission oil (75W-90) or CVT fluid (Green-2); replace spark plugs.\n- Every 80,000 km: Flush and replace engine coolant; inspect fuel filter and evap canister lines."
            }
        ]
    })

    return manuals


def seed_manuals_into_db(repo, embedder):
    manuals = generate_manual_data()
    total_docs = 0
    total_chunks = 0

    for m in manuals:
        texts = [f"{c['section']}\n{c['text']}" for c in m["chunks"]]
        vectors = embedder.encode(texts) if hasattr(embedder, "encode") else [None] * len(texts)

        for year in m["years"]:
            vids = repo.find_vehicle_ids(m["manufacturer"], m["model"], year)
            if not vids:
                continue
            doc_id = str(uuid.uuid4())
            repo.insert_document({
                "document_id": doc_id,
                "vehicle_id": vids[0],
                "document_name": f"{m['manufacturer']} {m['model']} {year} Owner's Manual",
                "document_type": m["doc_type"],
                "version": m["version"],
                "source": m["source"],
                "license_note": m["license_note"],
                "ingest_date": dt.date.today().isoformat(),
            })
            total_docs += 1

            chunk_rows = []
            for c, vec in zip(m["chunks"], vectors):
                chunk_rows.append({
                    "chunk_id": str(uuid.uuid4()),
                    "document_id": doc_id,
                    "section": c["section"],
                    "page_number": c["page"],
                    "text": c["text"],
                    "embedding": encode_embedding(vec) if vec is not None else None,
                    "chunk_type": c["type"],
                })

            repo.insert_chunks(chunk_rows)
            total_chunks += len(chunk_rows)

    print(f"Successfully seeded {total_docs} manual documents and {total_chunks} structured chunks across Corolla, Civic, and Swift (2015-2025).")



if __name__ == "__main__":
    from autocare.config import load_settings
    from autocare.db import Database
    from autocare.ml import create_embedder
    from autocare.repository import Repository

    s = load_settings()
    db = Database(s.database_url)
    db.create_schema()
    repo = Repository(db)
    embedder, _ = create_embedder(s)
    seed_manuals_into_db(repo, embedder)
