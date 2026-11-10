"""Pakistani Vehicle Fleet Registry for AI Auto Pakistan.

Covers prevalent domestic and imported Japanese (JDM) models in Pakistan,
including engine specs, fuel types, transmission options, and popular generations.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class FleetVehicle:
    make: str
    model: str
    common_variants: List[str]
    engine_cc_range: List[int]
    transmissions: List[str]
    fuel_types: List[str]
    years_range: tuple[int, int]
    market_segment: str  # Economy Hatchback, Compact Sedan, Midsize Sedan, Compact SUV, etc.


PAKISTANI_FLEET: Dict[str, FleetVehicle] = {
    "suzuki-alto": FleetVehicle(
        make="Suzuki",
        model="Alto",
        common_variants=["VX", "VXR", "VXL", "VXL AGS", "Lapin", "Turbo RS"],
        engine_cc_range=[660, 1000],
        transmissions=["Manual", "Automatic", "AGS"],
        fuel_types=["Petrol", "CNG"],
        years_range=(2000, 2026),
        market_segment="Economy Hatchback",
    ),
    "suzuki-cultus": FleetVehicle(
        make="Suzuki",
        model="Cultus",
        common_variants=["VX", "VXR", "VXL", "Auto Gear Shift (AGS)", "Euro II"],
        engine_cc_range=[1000],
        transmissions=["Manual", "AGS"],
        fuel_types=["Petrol", "CNG"],
        years_range=(2000, 2026),
        market_segment="Compact Hatchback",
    ),
    "suzuki-mehran": FleetVehicle(
        make="Suzuki",
        model="Mehran",
        common_variants=["VX", "VXR", "Euro II"],
        engine_cc_range=[800],
        transmissions=["Manual"],
        fuel_types=["Petrol", "CNG"],
        years_range=(1989, 2019),
        market_segment="Entry Hatchback",
    ),
    "suzuki-wagon-r": FleetVehicle(
        make="Suzuki",
        model="Wagon R",
        common_variants=["VXR", "VXL", "AGS", "FX", "FZ Hybrid"],
        engine_cc_range=[660, 1000],
        transmissions=["Manual", "AGS", "CVT"],
        fuel_types=["Petrol", "Hybrid"],
        years_range=(2014, 2026),
        market_segment="Tall Boy Hatchback",
    ),
    "suzuki-swift": FleetVehicle(
        make="Suzuki",
        model="Swift",
        common_variants=["1.3 DX", "1.3 DLX", "1.3 DLX AT", "1.2 GL Manual", "1.2 GL CVT", "1.2 GLX CVT"],
        engine_cc_range=[1200, 1300],
        transmissions=["Manual", "Automatic", "CVT"],
        fuel_types=["Petrol"],
        years_range=(2010, 2026),
        market_segment="Subcompact Hatchback",
    ),
    "toyota-corolla": FleetVehicle(
        make="Toyota",
        model="Corolla",
        common_variants=["XLi", "GLi", "Altis 1.6", "Altis Grande 1.8", "Altis 1.8 CVT-i", "2.0D"],
        engine_cc_range=[1300, 1600, 1800, 2000],
        transmissions=["Manual", "Automatic", "CVT"],
        fuel_types=["Petrol", "Diesel"],
        years_range=(1998, 2026),
        market_segment="Compact Sedan",
    ),
    "toyota-yaris": FleetVehicle(
        make="Toyota",
        model="Yaris",
        common_variants=["1.3 GLi MT", "1.3 GLi CVT", "1.3 ATIV MT", "1.3 ATIV CVT", "1.5 ATIV X MT", "1.5 ATIV X CVT"],
        engine_cc_range=[1300, 1500],
        transmissions=["Manual", "CVT"],
        fuel_types=["Petrol"],
        years_range=(2020, 2026),
        market_segment="Subcompact Sedan",
    ),
    "toyota-vitz": FleetVehicle(
        make="Toyota",
        model="Vitz",
        common_variants=["F 1.0", "Jewela 1.0", "U 1.3", "Hybrid 1.5", "RS"],
        engine_cc_range=[1000, 1300, 1500],
        transmissions=["CVT", "Automatic"],
        fuel_types=["Petrol", "Hybrid"],
        years_range=(2005, 2022),
        market_segment="Imported JDM Hatchback",
    ),
    "toyota-passo": FleetVehicle(
        make="Toyota",
        model="Passo",
        common_variants=["X 1.0", "G 1.0", "Moda", "Plus Hana"],
        engine_cc_range=[1000, 1300],
        transmissions=["CVT"],
        fuel_types=["Petrol"],
        years_range=(2006, 2023),
        market_segment="Imported JDM Hatchback",
    ),
    "honda-civic": FleetVehicle(
        make="Honda",
        model="Civic",
        common_variants=["EXi", "VTi", "VTi Oriel (Reborn)", "VTi Oriel (Rebirth)", "1.8 i-VTEC", "1.5 RS Turbo", "Oriel 1.5 Turbo"],
        engine_cc_range=[1500, 1600, 1800],
        transmissions=["Manual", "Automatic", "CVT"],
        fuel_types=["Petrol"],
        years_range=(2001, 2026),
        market_segment="Compact Sedan",
    ),
    "honda-city": FleetVehicle(
        make="Honda",
        model="City",
        common_variants=["i-DSI", "i-DSI Vario", "1.3 i-VTEC", "1.5 i-VTEC Aspire", "1.2 LS MT", "1.2 LS CVT", "1.5 Aspire CVT"],
        engine_cc_range=[1200, 1300, 1500],
        transmissions=["Manual", "Automatic", "CVT"],
        fuel_types=["Petrol"],
        years_range=(2003, 2026),
        market_segment="Subcompact Sedan",
    ),
    "hyundai-elantra": FleetVehicle(
        make="Hyundai",
        model="Elantra",
        common_variants=["GLS 2.0", "GL 1.6"],
        engine_cc_range=[1600, 2000],
        transmissions=["Automatic"],
        fuel_types=["Petrol"],
        years_range=(2021, 2026),
        market_segment="Compact Sedan",
    ),
    "kia-sportage": FleetVehicle(
        make="KIA",
        model="Sportage",
        common_variants=["Alpha", "FWD", "AWD", "Black Edition"],
        engine_cc_range=[2000],
        transmissions=["Automatic"],
        fuel_types=["Petrol"],
        years_range=(2019, 2026),
        market_segment="Compact Crossover SUV",
    ),
    "changan-alsvin": FleetVehicle(
        make="Changan",
        model="Alsvin",
        common_variants=["1.37L Comfort MT", "1.5L Comfort DCT", "1.5L Lumiere DCT"],
        engine_cc_range=[1370, 1500],
        transmissions=["Manual", "DCT"],
        fuel_types=["Petrol"],
        years_range=(2021, 2026),
        market_segment="Subcompact Sedan",
    ),
    "daihatsu-mira": FleetVehicle(
        make="Daihatsu",
        model="Mira",
        common_variants=["L", "X", "X Limited", "Mira e:S", "Cocoa"],
        engine_cc_range=[660],
        transmissions=["CVT", "Automatic"],
        fuel_types=["Petrol"],
        years_range=(2006, 2024),
        market_segment="Imported Kei Car",
    ),
}


def normalize_make_model(make_str: Optional[str], model_str: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    """Normalizes colloquial and misspelled Pakistani vehicle names."""
    import re
    if not make_str and not model_str:
        return None, None

    m = (make_str or "").strip().lower()
    mo = (model_str or "").strip().lower()
    combined = f"{m} {mo}".strip()

    patterns = [
        (r"\bmehran\b", ("Suzuki", "Mehran")),
        (r"\balto\b", ("Suzuki", "Alto")),
        (r"\bcultus\b", ("Suzuki", "Cultus")),
        (r"\bwagon\s?r\b", ("Suzuki", "Wagon R")),
        (r"\bswift\b", ("Suzuki", "Swift")),
        (r"\b(?:corolla|gli|xli|altis|grande)\b", ("Toyota", "Corolla")),
        (r"\byaris\b", ("Toyota", "Yaris")),
        (r"\bvitz\b", ("Toyota", "Vitz")),
        (r"\bpasso\b", ("Toyota", "Passo")),
        (r"\b(?:hilux|revo)\b", ("Toyota", "Hilux")),
        (r"\bfortuner\b", ("Toyota", "Fortuner")),
        (r"\b(?:civic|reborn|rebirth)\b", ("Honda", "Civic")),
        (r"\bcity\b", ("Honda", "City")),
        (r"\belantra\b", ("Hyundai", "Elantra")),
        (r"\btucson\b", ("Hyundai", "Tucson")),
        (r"\bsportage\b", ("KIA", "Sportage")),
        (r"\bpicanto\b", ("KIA", "Picanto")),
        (r"\balsvin\b", ("Changan", "Alsvin")),
        (r"\bmira\b", ("Daihatsu", "Mira")),
    ]
    for pat, res in patterns:
        if re.search(pat, combined):
            return res

    # Fallback title-casing (canonicalize uppercase brand acronyms like KIA / MG)
    clean_make = make_str.strip().title() if make_str else None
    if clean_make and clean_make.lower() in {"kia", "mg", "dfsk"}:
        clean_make = clean_make.upper()
    clean_model = model_str.strip().title() if model_str else None
    return clean_make, clean_model
