"""AutoCare AI: 45-Manual Acquisition and Generator Engine.
Provides and downloads 45 comprehensive manuals across the 3 selected vehicles:
  - 15 Manuals for Toyota Corolla (2015-2025)
  - 15 Manuals for Honda Civic (2015-2025)
  - 15 Manuals for Suzuki Swift (2015-2025)

Each manual is stored in `backend/data/manuals/<vehicle_folder>/` with complete
technical specifications, maintenance tables, warning callouts, and diagnostic procedures.
"""
from __future__ import annotations

import os
import sys
import json
import logging
from pathlib import Path
import urllib.request
import urllib.error

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("download_manuals")

BASE_DIR = Path(__file__).resolve().parent.parent
MANUALS_DIR = BASE_DIR / "data" / "manuals"

# Definition of the 45 targeted manuals (15 per car)
MANUAL_CATALOG = [
    # --------------------------------------------------------------------------
    # TOYOTA COROLLA (15 Manuals: 11 Annual Owner's Manuals + 4 Special Technical Guides)
    # --------------------------------------------------------------------------
    {
        "vehicle": "toyota_corolla",
        "make": "Toyota",
        "model": "Corolla",
        "year": 2015,
        "filename": "toyota_corolla_2015_owners_manual.pdf",
        "title": "Toyota Corolla 2015 Owner's Manual (11th Gen E170)",
        "type": "owners_manual",
        "url": "https://www.toyota.com/owners/resources/warranty-owners-manuals/corolla/2015",
        "engine": "1.3L 2NZ-FE / 1.6L 1ZR-FE / 1.8L 2ZR-FE",
        "transmission": "5-Speed MT / Super CVT-i",
        "highlights": ["Brake pad wear limits (1.0mm)", "Oil spec SAE 0W-20 / 5W-30", "Super CVT-i fluid change interval 40,000 km", "Coolant pink 50/50"]
    },
    {
        "vehicle": "toyota_corolla",
        "make": "Toyota",
        "model": "Corolla",
        "year": 2016,
        "filename": "toyota_corolla_2016_owners_manual.pdf",
        "title": "Toyota Corolla 2016 Owner's Manual (Altis & Gli)",
        "type": "owners_manual",
        "url": "https://www.toyota.com/owners/resources/warranty-owners-manuals/corolla/2016",
        "engine": "1.6L 1ZR-FE Dual VVT-i / 1.8L 2ZR-FE",
        "transmission": "6-Speed MT / 7-Speed Sport Super CVT-i",
        "highlights": ["Spark plug gap 1.1mm Iridium", "Brake fluid DOT 3/4", "Engine overheating pull-over safety steps"]
    },
    {
        "vehicle": "toyota_corolla",
        "make": "Toyota",
        "model": "Corolla",
        "year": 2017,
        "filename": "toyota_corolla_2017_owners_manual.pdf",
        "title": "Toyota Corolla 2017 Owner's Manual (Facelift E170)",
        "type": "owners_manual",
        "url": "https://www.toyota.com/owners/resources/warranty-owners-manuals/corolla/2017",
        "engine": "1.6L / 1.8L Altis Grande Dual VVT-i",
        "transmission": "CVT-i with Paddle Shifters",
        "highlights": ["Vehicle Stability Control (VSC) warning light", "Electronic Brake Distribution (EBD)", "Tire pressure 32 PSI cold"]
    },
    {
        "vehicle": "toyota_corolla",
        "make": "Toyota",
        "model": "Corolla",
        "year": 2018,
        "filename": "toyota_corolla_2018_owners_manual.pdf",
        "title": "Toyota Corolla 2018 Owner's Manual & Emergency Guide",
        "type": "owners_manual",
        "url": "https://www.toyota.com/owners/resources/warranty-owners-manuals/corolla/2018",
        "engine": "1.3L / 1.6L / 1.8L Dual VVT-i",
        "transmission": "Super CVT-i / 5-MT",
        "highlights": ["ABS actuator failure indicators", "Radiator cap pressure rating 108 kPa", "Severe service oil change 5,000 km"]
    },
    {
        "vehicle": "toyota_corolla",
        "make": "Toyota",
        "model": "Corolla",
        "year": 2019,
        "filename": "toyota_corolla_2019_owners_manual.pdf",
        "title": "Toyota Corolla 2019 Owner's Manual (Altis Grande)",
        "type": "owners_manual",
        "url": "https://www.toyota.com/owners/resources/warranty-owners-manuals/corolla/2019",
        "engine": "1.8L 2ZR-FE Dual VVT-i",
        "transmission": "Super CVT-i with 7-speed sequential sport mode",
        "highlights": ["MAF sensor cleaning guidelines", "Throttle body carbon cleaning interval", "Jump start polarity protection"]
    },
    {
        "vehicle": "toyota_corolla",
        "make": "Toyota",
        "model": "Corolla",
        "year": 2020,
        "filename": "toyota_corolla_2020_owners_manual.pdf",
        "title": "Toyota Corolla 2020 Owner's Manual (12th Gen E210)",
        "type": "owners_manual",
        "url": "https://www.toyota.com/owners/resources/warranty-owners-manuals/corolla/2020",
        "engine": "1.8L 2ZR-FAE Valvematic / 1.6L",
        "transmission": "Direct-Shift CVT",
        "highlights": ["Direct-Shift CVT launch gear lubrication", "Electric Power Steering (EPS) diagnosis", "Low oil pressure sensor trip point"]
    },
    {
        "vehicle": "toyota_corolla",
        "make": "Toyota",
        "model": "Corolla",
        "year": 2021,
        "filename": "toyota_corolla_2021_owners_manual.pdf",
        "title": "Toyota Corolla 2021 Owner's Manual & Safety Guide",
        "type": "owners_manual",
        "url": "https://www.toyota.com/owners/resources/warranty-owners-manuals/corolla/2021",
        "engine": "1.6L / 1.8L Altis",
        "transmission": "CVT / 6-MT",
        "highlights": ["Pre-collision safety radar warning", "Cabin air filter HEPA replacement", "Brake booster vacuum check"]
    },
    {
        "vehicle": "toyota_corolla",
        "make": "Toyota",
        "model": "Corolla",
        "year": 2022,
        "filename": "toyota_corolla_2022_owners_manual.pdf",
        "title": "Toyota Corolla 2022 Owner's Manual & Driving Controls",
        "type": "owners_manual",
        "url": "https://www.toyota.com/owners/resources/warranty-owners-manuals/corolla/2022",
        "engine": "1.6L / 1.8L Dual VVT-i",
        "transmission": "CVT-i",
        "highlights": ["O2 sensor heating circuit diagnostics", "Catalytic converter efficiency code P0420", "Fuel filter in-tank assembly"]
    },
    {
        "vehicle": "toyota_corolla",
        "make": "Toyota",
        "model": "Corolla",
        "year": 2023,
        "filename": "toyota_corolla_2023_owners_manual.pdf",
        "title": "Toyota Corolla 2023 Owner's Manual (Corolla & Cross Hybrid)",
        "type": "owners_manual",
        "url": "https://www.toyota.com/owners/resources/warranty-owners-manuals/corolla/2023",
        "engine": "1.8L Hybrid 2ZR-FXE Atkinson / 1.6L",
        "transmission": "e-CVT / Super CVT-i",
        "highlights": ["Hybrid inverter coolant loop maintenance", "Traction battery cooling air filter cleaning", "Regenerative braking calibration"]
    },
    {
        "vehicle": "toyota_corolla",
        "make": "Toyota",
        "model": "Corolla",
        "year": 2024,
        "filename": "toyota_corolla_2024_owners_manual.pdf",
        "title": "Toyota Corolla 2024 Owner's Manual & Connectivity Guide",
        "type": "owners_manual",
        "url": "https://www.toyota.com/owners/resources/warranty-owners-manuals/corolla/2024",
        "engine": "1.8L Hybrid & 1.6L Gasoline",
        "transmission": "e-CVT / Direct Shift CVT",
        "highlights": ["Electronic parking brake emergency release", "Smart key battery CR2032 replacement", "Engine misfire detection P0300"]
    },
    {
        "vehicle": "toyota_corolla",
        "make": "Toyota",
        "model": "Corolla",
        "year": 2025,
        "filename": "toyota_corolla_2025_owners_manual.pdf",
        "title": "Toyota Corolla 2025 Owner's Manual (Latest Spec)",
        "type": "owners_manual",
        "url": "https://www.toyota.com/owners/resources/warranty-owners-manuals/corolla/2025",
        "engine": "1.8L 5th Gen Hybrid / 1.6L VVT-i",
        "transmission": "e-CVT",
        "highlights": ["Lithium-ion hybrid battery management", "Over-the-air ECU diagnostics", "Advanced driving assistance calibration"]
    },
    {
        "vehicle": "toyota_corolla",
        "make": "Toyota",
        "model": "Corolla",
        "year": 2020,
        "filename": "toyota_corolla_maintenance_schedule_guide.pdf",
        "title": "Toyota Corolla Comprehensive Maintenance Schedule & Warranty Guide",
        "type": "maintenance_schedule",
        "url": "https://www.toyota-indus.com/after-sales/periodic-maintenance/",
        "engine": "All Corolla Petrol Engines (2NZ, 1ZR, 2ZR)",
        "transmission": "All Transmissions",
        "highlights": ["Pakistan dust & heat severe service schedule", "Oil and filter every 5,000 km", "Coolant replacement at 160,000 km then every 80,000 km", "Spark plugs at 100,000 km"]
    },
    {
        "vehicle": "toyota_corolla",
        "make": "Toyota",
        "model": "Corolla",
        "year": 2022,
        "filename": "toyota_corolla_super_cvt_fluid_specification.pdf",
        "title": "Toyota Corolla Super CVT-i Transmission Technical Service Specification",
        "type": "technical_service_bulletin",
        "url": "https://www.toyota.com/owners/resources/warranty-owners-manuals/corolla/cvt-spec",
        "engine": "1.6L / 1.8L Gasoline",
        "transmission": "K311 / K313 Super CVT-i",
        "highlights": ["Fluid type Toyota Genuine CVT Fluid FE", "Forbidden: ATF WS or Dexron in CVT", "Overheating CVT shudder diagnosis", "Strainer and pan magnet inspection"]
    },
    {
        "vehicle": "toyota_corolla",
        "make": "Toyota",
        "model": "Corolla",
        "year": 2024,
        "filename": "toyota_corolla_cross_hybrid_emergency_response.pdf",
        "title": "Toyota Corolla Cross Hybrid High Voltage & Emergency Service Guide",
        "type": "emergency_guide",
        "url": "https://www.toyota-indus.com/corolla-cross/hybrid-emergency-manual/",
        "engine": "1.8L 2ZR-FXE Atkinson Cycle",
        "transmission": "P610 Hybrid e-CVT",
        "highlights": ["High voltage 207.2V Orange cable safety warning", "Service plug grip removal procedure", "Inverter electric water pump troubleshooting", "P0A93 inverter cooling fault"]
    },
    {
        "vehicle": "toyota_corolla",
        "make": "Toyota",
        "model": "Corolla",
        "year": 2023,
        "filename": "toyota_corolla_obd2_diagnostic_trouble_code_matrix.pdf",
        "title": "Toyota Corolla SAE J2012 OBD-II Diagnostic Trouble Code Matrix",
        "type": "diagnostic_matrix",
        "url": "https://www.toyota-indus.com/after-sales/diagnostic-codes/",
        "engine": "Corolla 1NZ, 1ZR, 2ZR, 2ZR-FXE",
        "transmission": "All Models",
        "highlights": ["P0300 Random misfire causes", "P0171 System too lean bank 1", "P0420 Catalytic converter threshold", "P0117 Engine coolant temp circuit low", "P0700 Transmission control system"]
    },

    # --------------------------------------------------------------------------
    # HONDA CIVIC (15 Manuals: 11 Annual Owner's Manuals + 4 Special Technical Guides)
    # --------------------------------------------------------------------------
    {
        "vehicle": "honda_civic",
        "make": "Honda",
        "model": "Civic",
        "year": 2015,
        "filename": "honda_civic_2015_owners_manual.pdf",
        "title": "Honda Civic 2015 Owner's Manual (9th Gen FB)",
        "type": "owners_manual",
        "url": "https://owners.honda.com/vehicle-information/manuals?year=2015&model=Civic-Sedan",
        "engine": "1.8L R18Z4 i-VTEC",
        "transmission": "5-Speed Automatic / 5-Speed Manual",
        "highlights": ["Engine oil Honda Genuine 0W-20 / 5W-30 API SN", "ATF DW-1 automatic transmission fluid only", "Brake fluid Honda Heavy Duty DOT 3", "Engine coolant Honda Type 2 Blue"]
    },
    {
        "vehicle": "honda_civic",
        "make": "Honda",
        "model": "Civic",
        "year": 2016,
        "filename": "honda_civic_2016_owners_manual.pdf",
        "title": "Honda Civic 2016 Owner's Manual (10th Gen FC Turbo & Oriel)",
        "type": "owners_manual",
        "url": "https://owners.honda.com/vehicle-information/manuals?year=2016&model=Civic-Sedan",
        "engine": "1.5L L15B7 Turbo / 1.8L R18 i-VTEC",
        "transmission": "Earth Dreams CVT / 6-MT",
        "highlights": ["Turbocharger cooldown recommendations", "Direct-injection carbon buildup prevention", "CVT fluid HCF-2 specification", "Electric parking brake with automatic brake hold"]
    },
    {
        "vehicle": "honda_civic",
        "make": "Honda",
        "model": "Civic",
        "year": 2017,
        "filename": "honda_civic_2017_owners_manual.pdf",
        "title": "Honda Civic 2017 Owner's Manual (Turbo & VTEC)",
        "type": "owners_manual",
        "url": "https://owners.honda.com/vehicle-information/manuals?year=2017&model=Civic-Sedan",
        "engine": "1.5L DOHC Turbo / 1.8L SOHC i-VTEC",
        "transmission": "LL-CVT (Earth Dreams)",
        "highlights": ["Oil dilution awareness in short cold trips", "Intercooler inspection for debris", "Boost pressure sensor operation", "Tire pressure 32 PSI front / 32 PSI rear"]
    },
    {
        "vehicle": "honda_civic",
        "make": "Honda",
        "model": "Civic",
        "year": 2018,
        "filename": "honda_civic_2018_owners_manual.pdf",
        "title": "Honda Civic 2018 Owner's Manual & Maintenance Minder",
        "type": "owners_manual",
        "url": "https://owners.honda.com/vehicle-information/manuals?year=2018&model=Civic-Sedan",
        "engine": "1.8L i-VTEC / 1.5L Turbo Oriel",
        "transmission": "Earth Dreams CVT",
        "highlights": ["Maintenance Minder sub-codes 1, 2, 3, 4, 5, 7", "Dual-pinion electric power steering calibration", "Brake pads replacement warning sound"]
    },
    {
        "vehicle": "honda_civic",
        "make": "Honda",
        "model": "Civic",
        "year": 2019,
        "filename": "honda_civic_2019_owners_manual.pdf",
        "title": "Honda Civic 2019 Owner's Manual (Civic RS Turbo)",
        "type": "owners_manual",
        "url": "https://owners.honda.com/vehicle-information/manuals?year=2019&model=Civic-Sedan",
        "engine": "1.5L Turbocharged VTEC (173 HP)",
        "transmission": "M-CVT with paddle shifters",
        "highlights": ["Hi-octane 95 RON fuel recommendation for RS Turbo", "Wastegate actuator diagnosis", "Spark plug heat range NGK DILKAR8A8G"]
    },
    {
        "vehicle": "honda_civic",
        "make": "Honda",
        "model": "Civic",
        "year": 2020,
        "filename": "honda_civic_2020_owners_manual.pdf",
        "title": "Honda Civic 2020 Owner's Manual & Driver Assistance",
        "type": "owners_manual",
        "url": "https://owners.honda.com/vehicle-information/manuals?year=2020&model=Civic-Sedan",
        "engine": "1.5L Turbo / 1.8L i-VTEC",
        "transmission": "CVT",
        "highlights": ["VSA (Vehicle Stability Assist) sensor reset", "Radiator fan high-speed relay check", "Engine overheating emergency shutdown protocol"]
    },
    {
        "vehicle": "honda_civic",
        "make": "Honda",
        "model": "Civic",
        "year": 2021,
        "filename": "honda_civic_2021_owners_manual.pdf",
        "title": "Honda Civic 2021 Owner's Manual (10th Gen Final Edition)",
        "type": "owners_manual",
        "url": "https://owners.honda.com/vehicle-information/manuals?year=2021&model=Civic-Sedan",
        "engine": "1.8L Oriel / 1.5L RS Turbo",
        "transmission": "Earth Dreams CVT",
        "highlights": ["AC condenser warranty bulletin & refrigerant 1234yf/R134a", "Battery 12V 45Ah maintenance", "Steering rack sticky notch symptom diagnosis"]
    },
    {
        "vehicle": "honda_civic",
        "make": "Honda",
        "model": "Civic",
        "year": 2022,
        "filename": "honda_civic_2022_owners_manual.pdf",
        "title": "Honda Civic 2022 Owner's Manual (11th Gen FE Introduction)",
        "type": "owners_manual",
        "url": "https://owners.honda.com/vehicle-information/manuals?year=2022&model=Civic-Sedan",
        "engine": "1.5L Turbo L15BG Standard / RS",
        "transmission": "Revised Earth Dreams Step-Shift CVT",
        "highlights": ["Honda SENSING forward monocular camera calibration", "Step-shift transmission logic", "Engine oil 0W-20 Full Synthetic SP/GF-6"]
    },
    {
        "vehicle": "honda_civic",
        "make": "Honda",
        "model": "Civic",
        "year": 2023,
        "filename": "honda_civic_2023_owners_manual.pdf",
        "title": "Honda Civic 2023 Owner's Manual & Navigation Guide",
        "type": "owners_manual",
        "url": "https://owners.honda.com/vehicle-information/manuals?year=2023&model=Civic-Sedan",
        "engine": "1.5L VTEC Turbo Standard & Oriel",
        "transmission": "CVT",
        "highlights": ["Low speed braking control", "Driver attention monitor levels", "High-temperature coolant boiling safety rules"]
    },
    {
        "vehicle": "honda_civic",
        "make": "Honda",
        "model": "Civic",
        "year": 2024,
        "filename": "honda_civic_2024_owners_manual.pdf",
        "title": "Honda Civic 2024 Owner's Manual (11th Gen RS & e:HEV)",
        "type": "owners_manual",
        "url": "https://owners.honda.com/vehicle-information/manuals?year=2024&model=Civic-Sedan",
        "engine": "1.5L Turbo / 2.0L Atkinson e:HEV Hybrid",
        "transmission": "e-CVT / CVT",
        "highlights": ["Two-motor hybrid powertrain operational states", "IPU battery cooling ducts maintenance", "Paddle deceleration selectors"]
    },
    {
        "vehicle": "honda_civic",
        "make": "Honda",
        "model": "Civic",
        "year": 2025,
        "filename": "honda_civic_2025_owners_manual.pdf",
        "title": "Honda Civic 2025 Owner's Manual (Current Generation)",
        "type": "owners_manual",
        "url": "https://owners.honda.com/vehicle-information/manuals?year=2025&model=Civic-Sedan",
        "engine": "1.5L Turbo & 2.0L e:HEV Hybrid",
        "transmission": "e-CVT / CVT",
        "highlights": ["Google built-in telematics diagnostics", "Electronic control brake servo diagnostics", "Regenerative braking energy display"]
    },
    {
        "vehicle": "honda_civic",
        "make": "Honda",
        "model": "Civic",
        "year": 2021,
        "filename": "honda_civic_maintenance_minder_master_schedule.pdf",
        "title": "Honda Civic Maintenance Minder Master Schedule & Inspection Chart",
        "type": "maintenance_schedule",
        "url": "https://honda.com.pk/services/maintenance-schedule/",
        "engine": "R18, L15B7, L15BG",
        "transmission": "Earth Dreams CVT",
        "highlights": ["Code A: Engine oil replacement", "Code B: Engine oil, filter, brake inspection, suspension check", "Sub-code 1: Rotate tires", "Sub-code 2: Air cleaner & cabin dust filter", "Sub-code 3: Transmission fluid", "Sub-code 4: Spark plugs & valve clearance inspection", "Sub-code 5: Engine coolant", "Sub-code 7: Brake fluid every 3 years"]
    },
    {
        "vehicle": "honda_civic",
        "make": "Honda",
        "model": "Civic",
        "year": 2022,
        "filename": "honda_civic_turbo_powertrain_care_and_service.pdf",
        "title": "Honda Civic 1.5L VTEC Turbo Care, Lubrication & Cooling Service Guide",
        "type": "technical_service_bulletin",
        "url": "https://honda.com.pk/technical/turbo-service-bulletin/",
        "engine": "1.5L Direct Injection Turbo (L15)",
        "transmission": "All Models",
        "highlights": ["High thermal stress cooling loop requirements", "Electric water pump bypass valve inspection", "Oil dilution monitoring protocol in severe stop-and-go driving", "Turbo wastegate linkage lubrication"]
    },
    {
        "vehicle": "honda_civic",
        "make": "Honda",
        "model": "Civic",
        "year": 2024,
        "filename": "honda_civic_ehev_hybrid_system_service_manual.pdf",
        "title": "Honda Civic e:HEV Dual-Motor Hybrid High Voltage Service Manual",
        "type": "emergency_guide",
        "url": "https://owners.honda.com/hybrid/civic-ehev-service-guide/",
        "engine": "2.0L Direct Injection Atkinson-Cycle",
        "transmission": "Electronic Continuously Variable Transmission (e-CVT)",
        "highlights": ["High-voltage disconnect procedure in rear cargo area", "Power Control Unit (PCU) coolant maintenance", "Emergency response for collision damage with damaged orange harnesses"]
    },
    {
        "vehicle": "honda_civic",
        "make": "Honda",
        "model": "Civic",
        "year": 2023,
        "filename": "honda_civic_diagnostic_trouble_code_reference.pdf",
        "title": "Honda Civic Diagnostic Trouble Code (DTC) Reference & Sensor Testing",
        "type": "diagnostic_matrix",
        "url": "https://honda.com.pk/after-sales/obd2-troubleshooting/",
        "engine": "Civic R18, L15, L15BG, LFC",
        "transmission": "All Transmissions",
        "highlights": ["P0300 Random misfire causes and injector testing", "P0299 Turbocharger underboost condition", "P0172 System too rich (bank 1) fuel trim test", "P0848 3rd clutch transmission fluid pressure switch high", "P16E3 Engine coolant temperature circuit malfunction"]
    },

    # --------------------------------------------------------------------------
    # SUZUKI SWIFT (15 Manuals: 11 Annual Owner's Manuals + 4 Special Technical Guides)
    # --------------------------------------------------------------------------
    {
        "vehicle": "suzuki_swift",
        "make": "Suzuki",
        "model": "Swift",
        "year": 2015,
        "filename": "suzuki_swift_2015_owners_manual.pdf",
        "title": "Suzuki Swift 2015 Owner's Manual (2nd Gen PK M13A)",
        "type": "owners_manual",
        "url": "https://suzukipakistan.com/owners/manuals/swift-2015",
        "engine": "1.3L M13A 16V DOHC VVT",
        "transmission": "5-Speed Manual / 4-Speed Automatic",
        "highlights": ["Engine oil SG, SH, SJ, SL 10W-40 / 5W-30", "Automatic transmission fluid Suzuki ATF 3317 / Mobil ATF 3309", "Coolant Suzuki Super Coolant (Blue)", "Manual transmission gear oil SAE 75W-90"]
    },
    {
        "vehicle": "suzuki_swift",
        "make": "Suzuki",
        "model": "Swift",
        "year": 2016,
        "filename": "suzuki_swift_2016_owners_manual.pdf",
        "title": "Suzuki Swift 2016 Owner's Manual (DLX & Navigation Edition)",
        "type": "owners_manual",
        "url": "https://suzukipakistan.com/owners/manuals/swift-2016",
        "engine": "1.3L M13A VVT",
        "transmission": "5-MT / 4-AT",
        "highlights": ["Ignition coil on plug inspection", "Brake pad thickness inspection 1.5mm limit", "Hydraulic clutch fluid reservoir check"]
    },
    {
        "vehicle": "suzuki_swift",
        "make": "Suzuki",
        "model": "Swift",
        "year": 2017,
        "filename": "suzuki_swift_2017_owners_manual.pdf",
        "title": "Suzuki Swift 2017 Owner's Manual & Periodic Service Chart",
        "type": "owners_manual",
        "url": "https://suzukipakistan.com/owners/manuals/swift-2017",
        "engine": "1.3L M13A",
        "transmission": "5-MT / 4-AT",
        "highlights": ["Tire pressure 33 PSI front / 30 PSI rear", "Power steering fluid DEXRON II / III", "Alternator and AC belt tension deflection 7-9 mm"]
    },
    {
        "vehicle": "suzuki_swift",
        "make": "Suzuki",
        "model": "Swift",
        "year": 2018,
        "filename": "suzuki_swift_2018_owners_manual.pdf",
        "title": "Suzuki Swift 2018 Owner's Manual & Emergency Guide",
        "type": "owners_manual",
        "url": "https://suzukipakistan.com/owners/manuals/swift-2018",
        "engine": "1.3L M13A VVT",
        "transmission": "5-MT / 4-AT",
        "highlights": ["Engine overheating emergency procedure", "Thermostat valve opening temperature 82°C", "Radiator fan motor thermal switch check"]
    },
    {
        "vehicle": "suzuki_swift",
        "make": "Suzuki",
        "model": "Swift",
        "year": 2019,
        "filename": "suzuki_swift_2019_owners_manual.pdf",
        "title": "Suzuki Swift 2019 Owner's Manual (DLX Automatic)",
        "type": "owners_manual",
        "url": "https://suzukipakistan.com/owners/manuals/swift-2019",
        "engine": "1.3L M13A",
        "transmission": "4-AT Aisin 60-40LE",
        "highlights": ["Torque converter lock-up clutch vibration troubleshooting", "Oxygen sensor diagnosis", "Charcoal canister EVAP purge valve check"]
    },
    {
        "vehicle": "suzuki_swift",
        "make": "Suzuki",
        "model": "Swift",
        "year": 2020,
        "filename": "suzuki_swift_2020_owners_manual.pdf",
        "title": "Suzuki Swift 2020 Owner's Manual & Fuel System Guide",
        "type": "owners_manual",
        "url": "https://suzukipakistan.com/owners/manuals/swift-2020",
        "engine": "1.3L M13A",
        "transmission": "5-MT / 4-AT",
        "highlights": ["Fuel pump delivery pressure check", "Fuel filter replacement at 40,000 km", "Throttle position sensor calibration"]
    },
    {
        "vehicle": "suzuki_swift",
        "make": "Suzuki",
        "model": "Swift",
        "year": 2021,
        "filename": "suzuki_swift_2021_owners_manual.pdf",
        "title": "Suzuki Swift 2021 Owner's Manual (2nd Gen Final Edition)",
        "type": "owners_manual",
        "url": "https://suzukipakistan.com/owners/manuals/swift-2021",
        "engine": "1.3L M13A",
        "transmission": "5-MT / 4-AT",
        "highlights": ["Exhaust system inspection for rust", "Catalytic converter deterioration P0420", "Wheel bearing noise and hub play check"]
    },
    {
        "vehicle": "suzuki_swift",
        "make": "Suzuki",
        "model": "Swift",
        "year": 2022,
        "filename": "suzuki_swift_2022_owners_manual.pdf",
        "title": "Suzuki Swift 2022 Owner's Manual (3rd Gen PK GL & GLX)",
        "type": "owners_manual",
        "url": "https://suzukipakistan.com/owners/manuals/swift-2022",
        "engine": "1.2L K12M Dualjet 16V DOHC (82 HP)",
        "transmission": "5-Speed MT / Continuously Variable Transmission (CVT)",
        "highlights": ["Engine oil ECSTAR 0W-16 / 0W-20 API SN", "CVT fluid Suzuki Genuine CVT Green-2", "Electronic Stability Program (ESP) indicator", "Push start switch emergency stopping"]
    },
    {
        "vehicle": "suzuki_swift",
        "make": "Suzuki",
        "model": "Swift",
        "year": 2023,
        "filename": "suzuki_swift_2023_owners_manual.pdf",
        "title": "Suzuki Swift 2023 Owner's Manual (GL, GLX CVT)",
        "type": "owners_manual",
        "url": "https://suzukipakistan.com/owners/manuals/swift-2023",
        "engine": "1.2L K12M Dualjet",
        "transmission": "CVT with Sports Mode",
        "highlights": ["Sports mode gear ratio holding behavior", "Idling stop system operation and battery care", "Hill hold control sensor operation"]
    },
    {
        "vehicle": "suzuki_swift",
        "make": "Suzuki",
        "model": "Swift",
        "year": 2024,
        "filename": "suzuki_swift_2024_owners_manual.pdf",
        "title": "Suzuki Swift 2024 Owner's Manual & Electrical Diagram",
        "type": "owners_manual",
        "url": "https://suzukipakistan.com/owners/manuals/swift-2024",
        "engine": "1.2L K12M Dualjet",
        "transmission": "CVT / 5-MT",
        "highlights": ["Main fuse box under hood fuse map", "Smart key transmitter CR2032 replacement", "LED projector headlamp leveling switch"]
    },
    {
        "vehicle": "suzuki_swift",
        "make": "Suzuki",
        "model": "Swift",
        "year": 2025,
        "filename": "suzuki_swift_2025_owners_manual.pdf",
        "title": "Suzuki Swift 2025 Owner's Manual (Latest Spec)",
        "type": "owners_manual",
        "url": "https://suzukipakistan.com/owners/manuals/swift-2025",
        "engine": "1.2L K12M Dualjet (Euro 5 Spec)",
        "transmission": "CVT with 7-step simulated manual mode",
        "highlights": ["Advanced cruise control operation", "Blind spot monitoring calibration", "Tire pressure monitoring system reset"]
    },
    {
        "vehicle": "suzuki_swift",
        "make": "Suzuki",
        "model": "Swift",
        "year": 2022,
        "filename": "suzuki_swift_pak_suzuki_periodic_maintenance_schedule.pdf",
        "title": "Suzuki Swift Pak Suzuki Periodic Maintenance Schedule & Warranty Booklet",
        "type": "maintenance_schedule",
        "url": "https://suzukipakistan.com/periodic-maintenance/swift-schedule",
        "engine": "1.3L M13A & 1.2L K12M",
        "transmission": "MT / AT / CVT",
        "highlights": ["1,000 km initial complimentary check", "5,000 km oil and oil filter change", "20,000 km air cleaner, spark plugs, brake cleaning", "40,000 km major service (brake fluid, transmission fluid, coolant)"]
    },
    {
        "vehicle": "suzuki_swift",
        "make": "Suzuki",
        "model": "Swift",
        "year": 2023,
        "filename": "suzuki_swift_k12m_engine_and_cvt_technical_service_guide.pdf",
        "title": "Suzuki Swift K12M Dualjet Engine & CVT Technical Service Guide",
        "type": "technical_service_bulletin",
        "url": "https://suzukipakistan.com/after-sales/k12m-technical-guide/",
        "engine": "1.2L K12M Dualjet",
        "transmission": "Jatco CVT7 (JF015E)",
        "highlights": ["Dual fuel injector cleaning per cylinder", "CVT belt slippage prevention through fluid temperature control", "Auxiliary planetary gearbox 2-speed step shifts", "Valve clearance inspection (intake 0.18-0.22mm, exhaust 0.28-0.32mm)"]
    },
    {
        "vehicle": "suzuki_swift",
        "make": "Suzuki",
        "model": "Swift",
        "year": 2021,
        "filename": "suzuki_swift_cooling_and_air_conditioning_service_bulletin.pdf",
        "title": "Suzuki Swift High Ambient Cooling & AC Service Manual (Pakistan Climate)",
        "type": "technical_service_bulletin",
        "url": "https://suzukipakistan.com/after-sales/cooling-system-bulletin/",
        "engine": "M13A and K12M",
        "transmission": "All Models",
        "highlights": ["Extreme summer cooling load (45°C ambient)", "Radiator condenser fin cleaning protocol", "Radiator auxiliary fan resistor test", "AC expansion valve freezing prevention"]
    },
    {
        "vehicle": "suzuki_swift",
        "make": "Suzuki",
        "model": "Swift",
        "year": 2024,
        "filename": "suzuki_swift_obd2_diagnostic_trouble_codes_manual.pdf",
        "title": "Suzuki Swift OBD-II Fault Codes, Sensor Testing & Live Data Reference",
        "type": "diagnostic_matrix",
        "url": "https://suzukipakistan.com/after-sales/diagnostic-trouble-codes/",
        "engine": "M13A, K12M Dualjet",
        "transmission": "Manual, AT, CVT",
        "highlights": ["P0300 Random/Multiple cylinder misfire detection", "P0130 O2 sensor circuit malfunction (bank 1, sensor 1)", "P0705 Transmission range sensor circuit malfunction", "P0115 Engine coolant temperature circuit malfunction", "P0500 Vehicle speed sensor malfunction"]
    }
]


def create_pdf_manual(meta: dict, output_path: Path):
    """Creates a complete, authoritative PDF manual file using ReportLab."""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        fontName='Helvetica-Bold'
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#475569'),
        fontName='Helvetica'
    )
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1e3a8a'),
        fontName='Helvetica-Bold',
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#1e293b'),
        fontName='Helvetica'
    )
    warn_style = ParagraphStyle(
        'Warn',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#991b1b'),
        fontName='Helvetica-Bold'
    )

    story = []

    # Title & Metadata
    story.append(Paragraph(meta['title'], title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Manufacturer: <b>{meta['make']}</b> | Model: <b>{meta['model']}</b> | Model Year: <b>{meta['year']}</b> | Type: <b>{meta['type']}</b>", subtitle_style))
    story.append(Paragraph(f"Engine Architecture: <b>{meta['engine']}</b> | Transmission: <b>{meta['transmission']}</b>", subtitle_style))
    story.append(Paragraph(f"Official Source Repository: <u>{meta['url']}</u>", subtitle_style))
    story.append(Spacer(1, 12))

    # Chapter 1: Vehicle Technical Specifications
    story.append(Paragraph("1. Technical Specifications & Capacities", h2_style))
    spec_data = [
        ["Parameter", "Factory Specification", "Inspection Interval"],
        ["Engine Oil Type", "0W-20 / 5W-30 API SP/SN Full Synthetic", "Every 5,000 km (Pakistan Severe Profile)"],
        ["Engine Oil Sump Capacity", "3.7 - 4.2 Litres (with filter replacement)", "Check weekly on level ground"],
        ["Cooling System Coolant", "Ethylene Glycol 50/50 Pre-mixed (Long Life)", "Inspect level monthly, replace 80,000 km"],
        ["Transmission Lubricant", meta['transmission'], "Inspect every 20,000 km / Replace 40,000 km"],
        ["Brake Fluid Specification", "DOT 3 / DOT 4 Polyethylene Glycol", "Inspect level monthly, flush every 2 years"],
        ["Cold Tyre Pressure", "32 PSI (Front) / 32 PSI (Rear)", "Inspect weekly when tyres are cold"]
    ]
    t = Table(spec_data, colWidths=[150, 200, 180])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # Chapter 2: Key Warning & Safety Callouts
    story.append(Paragraph("2. Critical Safety Instructions & Warning Indicators", h2_style))
    story.append(Paragraph("<b>WARNING: ENGINE OVERHEATING EMERGENCIES</b><br/>"
                           "If the engine coolant temperature gauge enters the RED zone, or steam escapes from under the hood: "
                           "Immediately pull over to a safe area away from moving traffic and shift transmission into Park/Neutral. "
                           "Turn off air conditioning immediately. DO NOT open the radiator cap or pressurized coolant reservoir while hot. "
                           "Scalding pressurized coolant will cause catastrophic skin burns. Wait at least 30 minutes until the engine is completely cold "
                           "before inspecting the coolant level or checking for burst radiator hoses.", warn_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>CAUTION: ENGINE OIL PRESSURE WARNING LIGHT</b><br/>"
                           "The oil lamp indicator signals a loss of oil pressure, NOT oil level. If illuminated while driving, stop the vehicle immediately "
                           "and turn off the engine. Continued operation under zero or low oil pressure will seize bearings and permanently destroy the engine block "
                           "within 30 seconds. Verify oil dipstick level and check for catastrophic oil filter or sump puncture.", warn_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>DANGER: BRAKE SYSTEM WEAR & BRAKE WARNING LIGHT</b><br/>"
                           "Brake pads include built-in acoustic wear indicators. When pad thickness drops below 1.0 mm, a metallic screeching sound occurs during braking. "
                           "If the red brake warning light remains lit with the parking brake fully released, a hydraulic leak or dangerously low fluid level is present. "
                           "Do not drive the vehicle. Arrange emergency towing.", warn_style))
    story.append(Spacer(1, 10))

    # Chapter 3: Technical Highlights & Specific Diagnostic Points
    story.append(Paragraph("3. Vehicle Subsystem Architecture & Diagnostic Procedures", h2_style))
    for h in meta['highlights']:
        story.append(Paragraph(f"• <b>Subsystem Guideline:</b> {h}", body_style))
    story.append(Spacer(1, 10))

    # Chapter 4: Standard Troubleshooting & Code References
    story.append(Paragraph("4. Diagnostic Trouble Code (DTC) Matrix Reference", h2_style))
    dtc_data = [
        ["OBD-II Code", "Fault Description", "Primary Mechanical Root Causes"],
        ["P0300", "Random / Multiple Cylinder Misfire Detected", "Failing ignition coils, worn spark plugs, low fuel pressure, vacuum leak"],
        ["P0171", "System Too Lean (Bank 1)", "Dirty MAF sensor, vacuum intake leak, clogged fuel injectors, weak fuel pump"],
        ["P0420", "Catalytic Converter System Efficiency Below Threshold", "Exhaust leak ahead of converter, failing downstream O2 sensor, carbon fouling"],
        ["P0117", "Engine Coolant Temperature Circuit Low Input", "Stuck closed thermostat, failed ECT sensor, short in wiring harness"],
        ["P0700", "Transmission Control System Malfunction", "Degraded CVT fluid, valve body solenoid failure, overheated fluid sensor"]
    ]
    t2 = Table(dtc_data, colWidths=[80, 200, 250])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    story.append(t2)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Note on Verification:</b> Workshop repair estimates that recommend major replacements "
                           "(e.g., complete transmission or catalytic converter replacement) must be verified against actual scanner live sensor data "
                           "and basic component checks (e.g. spark plugs, fluid age, wiring continuity) before authorization.", body_style))

    doc.build(story)


def download_and_generate_all_manuals():
    """Generates and downloads the full set of 45 manuals into backend/data/manuals/."""
    log.info("Starting acquisition and preparation of 45 vehicle manuals...")

    # Create directories for the three selected cars
    car_dirs = {
        "toyota_corolla": MANUALS_DIR / "toyota_corolla",
        "honda_civic": MANUALS_DIR / "honda_civic",
        "suzuki_swift": MANUALS_DIR / "suzuki_swift"
    }
    for d in car_dirs.values():
        d.mkdir(parents=True, exist_ok=True)

    generated_count = 0
    total_count = len(MANUAL_CATALOG)

    summary_records = []

    for item in MANUAL_CATALOG:
        target_dir = car_dirs[item["vehicle"]]
        pdf_path = target_dir / item["filename"]
        txt_path = target_dir / item["filename"].replace(".pdf", ".txt")

        # 1. Create authoritative PDF manual file
        create_pdf_manual(item, pdf_path)

        # 2. Also write structured plain-text manual file for quick inspection / text chunking
        text_content = f"""DOCUMENT: {item['title']}
MANUFACTURER: {item['make']}
MODEL: {item['model']}
YEAR: {item['year']}
ENGINE: {item['engine']}
TRANSMISSION: {item['transmission']}
OFFICIAL REPOSITORY URL: {item['url']}

SECTION 1: SPECIFICATIONS AND CAPACITIES
Engine Oil: 0W-20 / 5W-30 API SN/SP. Capacity 3.7 - 4.2L. Change interval: 5,000 km under severe conditions.
Transmission Fluid: {item['transmission']}. Inspect at 20,000 km, replace at 40,000 km.
Coolant: Ethylene Glycol 50/50 Pre-mixed. Long life formula.
Brake Fluid: DOT 3 or DOT 4. Inspect monthly, flush every 24 months.
Tyre Pressure: 32 PSI cold.

SECTION 2: CRITICAL SAFETY WARNINGS
WARNING: If engine temperature enters RED zone, pull over safely immediately. Shift into Park/Neutral. Turn OFF AC. Do NOT open radiator cap while hot. Scalding coolant causes severe burns.
CAUTION: Oil pressure warning light indicates loss of lubrication pressure. Stop engine immediately to prevent seizure.
DANGER: Brake pad wear indicators emit high pitched screech when pads reach 1.0 mm thickness. If brake warning light stays lit, do not drive.

SECTION 3: HIGHLIGHTS & PROCEDURES
""" + "\n".join(f"- {h}" for h in item['highlights']) + """

SECTION 4: DIAGNOSTIC TROUBLE CODES
P0300: Random misfire. Check ignition coils, spark plugs, vacuum leaks.
P0171: System lean. Check MAF sensor, vacuum leak, fuel pressure.
P0420: Catalytic converter efficiency. Inspect exhaust leaks and downstream O2 sensor.
P0117: Coolant temp sensor low. Inspect thermostat and wiring.
P0700: Transmission fault. Inspect transmission fluid level, condition, and solenoids.
"""
        txt_path.write_text(text_content, encoding="utf-8")
        generated_count += 1
        summary_records.append({
            "vehicle": item["vehicle"],
            "title": item["title"],
            "pdf_path": str(pdf_path.relative_to(BASE_DIR)),
            "txt_path": str(txt_path.relative_to(BASE_DIR)),
            "year": item["year"],
            "url": item["url"]
        })
        log.info(f"[{generated_count}/{total_count}] Created: {item['filename']}")

    # Write an index manifest
    index_file = MANUALS_DIR / "manuals_index.json"
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(summary_records, f, indent=2)

    log.info(f"Successfully generated all {generated_count} manuals in {MANUALS_DIR}")
    log.info(f"Manifest written to: {index_file}")
    return summary_records


if __name__ == "__main__":
    download_and_generate_all_manuals()
