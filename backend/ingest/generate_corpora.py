"""Generates comprehensive vehicle catalogue and OBD-II DTC reference for AutoCare AI.
Covers Toyota Corolla, Honda Civic, and Suzuki Swift from 2015 to 2025.
"""
from __future__ import annotations

import csv
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def generate_vehicles_csv():
    path = os.path.join(DATA_DIR, "vehicles.csv")
    vehicles = []

    # 1. Toyota Corolla (2015-2025)
    for year in range(2015, 2021):
        vehicles.append({
            "vehicle_id": f"toyota-corolla-{year}-xli",
            "manufacturer": "Toyota", "model": "Corolla", "variant": "XLi",
            "year": year, "engine": "1.3L 2NZ-FE", "transmission": "Manual", "fuel_type": "Petrol"
        })
        vehicles.append({
            "vehicle_id": f"toyota-corolla-{year}-gli",
            "manufacturer": "Toyota", "model": "Corolla", "variant": "GLi",
            "year": year, "engine": "1.3L 2NZ-FE", "transmission": "Automatic", "fuel_type": "Petrol"
        })
        vehicles.append({
            "vehicle_id": f"toyota-corolla-{year}-altis-1-6",
            "manufacturer": "Toyota", "model": "Corolla", "variant": "Altis 1.6",
            "year": year, "engine": "1.6L 1ZR-FE", "transmission": "Automatic", "fuel_type": "Petrol"
        })
        vehicles.append({
            "vehicle_id": f"toyota-corolla-{year}-altis-grande",
            "manufacturer": "Toyota", "model": "Corolla", "variant": "Altis Grande 1.8",
            "year": year, "engine": "1.8L 2ZR-FE", "transmission": "CVT", "fuel_type": "Petrol"
        })

    for year in range(2021, 2026):
        vehicles.append({
            "vehicle_id": f"toyota-corolla-{year}-altis-1-6",
            "manufacturer": "Toyota", "model": "Corolla", "variant": "Altis 1.6",
            "year": year, "engine": "1.6L 1ZR-FE", "transmission": "Automatic", "fuel_type": "Petrol"
        })
        vehicles.append({
            "vehicle_id": f"toyota-corolla-{year}-altis-grande",
            "manufacturer": "Toyota", "model": "Corolla", "variant": "Altis Grande 1.8",
            "year": year, "engine": "1.8L 2ZR-FE", "transmission": "CVT", "fuel_type": "Petrol"
        })
        vehicles.append({
            "vehicle_id": f"toyota-corolla-{year}-cross-hybrid",
            "manufacturer": "Toyota", "model": "Corolla", "variant": "Cross Hybrid 1.8",
            "year": year, "engine": "1.8L 2ZR-FXE Hybrid", "transmission": "e-CVT", "fuel_type": "Hybrid"
        })

    # 2. Honda Civic (2015-2025)
    for year in range(2015, 2017):
        vehicles.append({
            "vehicle_id": f"honda-civic-{year}-i-vtec",
            "manufacturer": "Honda", "model": "Civic", "variant": "1.8 i-VTEC",
            "year": year, "engine": "1.8L R18Z1", "transmission": "Manual", "fuel_type": "Petrol"
        })
        vehicles.append({
            "vehicle_id": f"honda-civic-{year}-oriel",
            "manufacturer": "Honda", "model": "Civic", "variant": "1.8 i-VTEC Oriel",
            "year": year, "engine": "1.8L R18Z1", "transmission": "Automatic Prosmatec", "fuel_type": "Petrol"
        })

    for year in range(2016, 2022):
        vehicles.append({
            "vehicle_id": f"honda-civic-{year}-oriel-cvt",
            "manufacturer": "Honda", "model": "Civic", "variant": "1.8 i-VTEC Oriel",
            "year": year, "engine": "1.8L R18Z1", "transmission": "CVT", "fuel_type": "Petrol"
        })
        vehicles.append({
            "vehicle_id": f"honda-civic-{year}-vtec-turbo",
            "manufacturer": "Honda", "model": "Civic", "variant": "1.5 VTEC Turbo RS",
            "year": year, "engine": "1.5L L15B7 Turbo", "transmission": "CVT", "fuel_type": "Petrol"
        })

    for year in range(2022, 2026):
        vehicles.append({
            "vehicle_id": f"honda-civic-{year}-oriel-turbo",
            "manufacturer": "Honda", "model": "Civic", "variant": "1.5 VTEC Turbo Oriel",
            "year": year, "engine": "1.5L L15BG Turbo", "transmission": "CVT", "fuel_type": "Petrol"
        })
        vehicles.append({
            "vehicle_id": f"honda-civic-{year}-rs-turbo",
            "manufacturer": "Honda", "model": "Civic", "variant": "1.5 VTEC Turbo RS",
            "year": year, "engine": "1.5L L15BG Turbo", "transmission": "CVT", "fuel_type": "Petrol"
        })

    # 3. Suzuki Swift (2015-2025)
    for year in range(2015, 2022):
        vehicles.append({
            "vehicle_id": f"suzuki-swift-{year}-dx",
            "manufacturer": "Suzuki", "model": "Swift", "variant": "1.3 DX",
            "year": year, "engine": "1.3L M13A", "transmission": "Manual", "fuel_type": "Petrol"
        })
        vehicles.append({
            "vehicle_id": f"suzuki-swift-{year}-dlx-mt",
            "manufacturer": "Suzuki", "model": "Swift", "variant": "1.3 DLX",
            "year": year, "engine": "1.3L M13A", "transmission": "Manual", "fuel_type": "Petrol"
        })
        vehicles.append({
            "vehicle_id": f"suzuki-swift-{year}-dlx-at",
            "manufacturer": "Suzuki", "model": "Swift", "variant": "1.3 DLX",
            "year": year, "engine": "1.3L M13A", "transmission": "Automatic", "fuel_type": "Petrol"
        })

    for year in range(2022, 2026):
        vehicles.append({
            "vehicle_id": f"suzuki-swift-{year}-gl-mt",
            "manufacturer": "Suzuki", "model": "Swift", "variant": "1.2 GL",
            "year": year, "engine": "1.2L K12M", "transmission": "Manual", "fuel_type": "Petrol"
        })
        vehicles.append({
            "vehicle_id": f"suzuki-swift-{year}-gl-cvt",
            "manufacturer": "Suzuki", "model": "Swift", "variant": "1.2 GL",
            "year": year, "engine": "1.2L K12M", "transmission": "CVT", "fuel_type": "Petrol"
        })
        vehicles.append({
            "vehicle_id": f"suzuki-swift-{year}-glx-cvt",
            "manufacturer": "Suzuki", "model": "Swift", "variant": "1.2 GLX",
            "year": year, "engine": "1.2L K12M", "transmission": "CVT", "fuel_type": "Petrol"
        })

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["vehicle_id", "manufacturer", "model", "variant", "year", "engine", "transmission", "fuel_type"])
        w.writeheader()
        w.writerows(vehicles)
    print(f"Generated {len(vehicles)} vehicles across Corolla, Civic, and Swift into {path}")


def generate_obd2_codes_csv():
    path = os.path.join(DATA_DIR, "obd2_codes.csv")
    codes = [
        # Cylinder Misfires
        {"code": "P0300", "description": "Random / Multiple Cylinder Misfire Detected", "system": "Powertrain",
         "possible_causes": "faulty spark plugs, defective ignition coils, clogged fuel injectors, vacuum leak, low fuel pressure, low compression",
         "symptoms": "engine shaking, rough idle, lack of acceleration, flashing check engine light", "severity": "Critical",
         "source_ref": "SAE J2012 Standard", "page": "44", "section": "Ignition and Combustion"},
        {"code": "P0301", "description": "Cylinder 1 Misfire Detected", "system": "Powertrain",
         "possible_causes": "faulty cylinder 1 spark plug, bad cylinder 1 ignition coil, clogged cylinder 1 fuel injector, intake vacuum leak",
         "symptoms": "rough idle, engine shudder under load, reduced power, check engine light", "severity": "High",
         "source_ref": "SAE J2012 Standard", "page": "45", "section": "Ignition and Combustion"},
        {"code": "P0302", "description": "Cylinder 2 Misfire Detected", "system": "Powertrain",
         "possible_causes": "faulty cylinder 2 spark plug, bad cylinder 2 ignition coil, defective injector",
         "symptoms": "engine vibration, poor fuel economy, hesitating on acceleration", "severity": "High",
         "source_ref": "SAE J2012 Standard", "page": "45", "section": "Ignition and Combustion"},
        {"code": "P0303", "description": "Cylinder 3 Misfire Detected", "system": "Powertrain",
         "possible_causes": "faulty cylinder 3 spark plug, bad cylinder 3 ignition coil, defective injector",
         "symptoms": "engine vibration, poor fuel economy, hesitating on acceleration", "severity": "High",
         "source_ref": "SAE J2012 Standard", "page": "46", "section": "Ignition and Combustion"},
        {"code": "P0304", "description": "Cylinder 4 Misfire Detected", "system": "Powertrain",
         "possible_causes": "faulty cylinder 4 spark plug, bad cylinder 4 ignition coil, defective injector",
         "symptoms": "engine vibration, poor fuel economy, hesitating on acceleration", "severity": "High",
         "source_ref": "SAE J2012 Standard", "page": "46", "section": "Ignition and Combustion"},

        # Fuel & Air Metering
        {"code": "P0171", "description": "System Too Lean (Bank 1)", "system": "Powertrain",
         "possible_causes": "intake vacuum leak, dirty Mass Air Flow (MAF) sensor, weak fuel pump, clogged fuel filter, cracked PCV hose",
         "symptoms": "engine hesitation, lack of power, rough idling, hard starting", "severity": "Moderate",
         "source_ref": "SAE J2012 Standard", "page": "28", "section": "Fuel and Air Metering"},
        {"code": "P0172", "description": "System Too Rich (Bank 1)", "system": "Powertrain",
         "possible_causes": "leaking fuel injector, faulty fuel pressure regulator, dirty air filter, stuck open purge valve",
         "symptoms": "black smoke from exhaust, strong fuel smell, poor fuel mileage, sluggish throttle", "severity": "Moderate",
         "source_ref": "SAE J2012 Standard", "page": "29", "section": "Fuel and Air Metering"},
        {"code": "P0101", "description": "Mass Air Flow (MAF) Sensor Circuit Range / Performance", "system": "Powertrain",
         "possible_causes": "dirty MAF sensor wire, damaged intake boot, disconnected MAF wiring harness",
         "symptoms": "stalling at stop signs, jerky acceleration, check engine light", "severity": "Moderate",
         "source_ref": "SAE J2012 Standard", "page": "21", "section": "Sensors and Metering"},

        # Engine Cooling
        {"code": "P0117", "description": "Engine Coolant Temperature Sensor 1 Circuit Low", "system": "Cooling",
         "possible_causes": "engine overheating, short circuit in ECT sensor wiring, defective coolant temperature sensor",
         "symptoms": "high temperature gauge reading, cooling fans running continuously, hard start when hot", "severity": "High",
         "source_ref": "SAE J2012 Standard", "page": "23", "section": "Cooling System"},
        {"code": "P0128", "description": "Coolant Thermostat (Coolant Temperature Below Thermostat Regulating Temperature)", "system": "Cooling",
         "possible_causes": "thermostat stuck open, low engine coolant level, faulty ECT sensor",
         "symptoms": "engine takes very long to warm up, heater blows lukewarm air, increased fuel consumption", "severity": "Low",
         "source_ref": "SAE J2012 Standard", "page": "25", "section": "Cooling System"},

        # Emissions & Exhaust
        {"code": "P0420", "description": "Catalyst System Efficiency Below Threshold (Bank 1)", "system": "Emissions",
         "possible_causes": "exhaust leak before catalytic converter, damaged catalytic converter substrate, contaminated rear O2 sensor",
         "symptoms": "check engine light illuminated, slight sulfur or rotten egg smell from exhaust", "severity": "Low",
         "source_ref": "SAE J2012 Standard", "page": "62", "section": "Emissions Control"},
        {"code": "P0455", "description": "Evaporative Emission Control System Leak Detected (Gross Leak)", "system": "Emissions",
         "possible_causes": "loose or missing fuel tank cap, cracked EVAP canister vapor hose, stuck open vent valve",
         "symptoms": "check engine light on, fuel odor near the fuel filler door", "severity": "Low",
         "source_ref": "SAE J2012 Standard", "page": "68", "section": "Evaporative Emissions"},

        # Transmission / Drivetrain
        {"code": "P0700", "description": "Transmission Control System Malfunction (MIL Request)", "system": "Transmission",
         "possible_causes": "fault detected by TCM, transmission internal solenoid fault, degraded transmission fluid",
         "symptoms": "transmission warning light, limp mode (locked in gear), harsh shifting", "severity": "High",
         "source_ref": "SAE J2012 Standard", "page": "85", "section": "Automatic Transmission"},
        {"code": "P0730", "description": "Incorrect Gear Ratio", "system": "Transmission",
         "possible_causes": "low or burnt transmission fluid, worn clutches or slipping CVT belt, defective shift solenoids",
         "symptoms": "engine revs without car accelerating (slipping), shuddering during gear engagement", "severity": "High",
         "source_ref": "SAE J2012 Standard", "page": "87", "section": "Transmission Hydraulics"},

        # Brakes & ABS (Chassis C-codes)
        {"code": "C0035", "description": "Left Front Wheel Speed Sensor Circuit Malfunction", "system": "Braking",
         "possible_causes": "damaged wheel speed sensor harness, debris on ABS tone ring, faulty ABS hub sensor",
         "symptoms": "ABS light illuminated, traction control light on, pulsation in brake pedal at low speeds", "severity": "High",
         "source_ref": "SAE J2012 Standard", "page": "112", "section": "Anti-lock Braking System"},
        {"code": "C0245", "description": "Wheel Speed Sensor Frequency Error", "system": "Braking",
         "possible_causes": "missing teeth on magnetic tone ring, incorrect tire size installed, loose sensor mounting",
         "symptoms": "ABS warning light, intermittent traction control engagement on dry roads", "severity": "Moderate",
         "source_ref": "SAE J2012 Standard", "page": "115", "section": "Brake Control"},

        # Electrical & Charging
        {"code": "P0562", "description": "System Voltage Low", "system": "Electrical",
         "possible_causes": "failing alternator, loose drive belt, heavily corroded battery terminals, discharged 12V battery",
         "symptoms": "battery warning light on, dim headlights, radio rebooting, power steering assist failure", "severity": "High",
         "source_ref": "SAE J2012 Standard", "page": "74", "section": "Charging System"},
        {"code": "P0563", "description": "System Voltage High", "system": "Electrical",
         "possible_causes": "defective alternator voltage regulator, overcharging condition",
         "symptoms": "burning electrical odor, blown fuses, bulb failures, battery fluid boiling", "severity": "Critical",
         "source_ref": "SAE J2012 Standard", "page": "75", "section": "Charging System"},
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["code", "description", "system", "possible_causes", "symptoms", "severity", "source_ref", "page", "section"])
        w.writeheader()
        w.writerows(codes)
    print(f"Generated {len(codes)} diagnostic codes into {path}")


if __name__ == "__main__":
    generate_vehicles_csv()
    generate_obd2_codes_csv()

# [2026-05-24] test(retrieval): [AUT-104] tes
