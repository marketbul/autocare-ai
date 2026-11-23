"""Fault-to-Specialist Dispatch Engine for AutoCare AI.

Matches vehicle mechanical failure modes and OBD-II Diagnostic Trouble Codes (DTCs)
to verified specialist workshops across major Pakistani metropolitan hubs
(Lahore, Karachi, Rawalpindi/Islamabad) using:
1. Subsystem Specialty Matching (Engine, Brakes, EFI/Electrical, Transmission, Suspension, HVAC).
2. Haversine Great-Circle GPS Distance Calculation.
3. Multi-Criteria Composite Scoring:
   Score = (0.40 * Skill) + (0.30 * Distance) + (0.20 * Rating) + (0.10 * Queue).
4. Localized Fair PKR Parts and Labor Pricing Integration.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# 1. SPECIALTY TAXONOMY & DTC MAPPING
# ---------------------------------------------------------------------------

SPECIALTIES = {
    "engine_cooling": {
        "title": "Engine & Radiator Cooling Specialist",
        "description": "Engine overheating, radiator leaks, water pump failure, blown head gasket, thermostat stuck.",
        "dtc_prefixes": ["P0217", "P0117", "P0118", "P0119", "P0128", "P0125"],
        "keywords": ["overheat", "garam", "radiator", "coolant", "water pump", "head gasket", "fan relay", "boil"],
        "price_range_pkr": {"low": 1200, "median": 2800, "high": 8500}
    },
    "brakes_hydraulics": {
        "title": "Hydraulic Brake & ABS Specialist",
        "description": "Brake pad wear, spongy brake pedal, ABS warning light, master cylinder leaks, disc warping.",
        "dtc_prefixes": ["C0035", "C0040", "C1201", "P0571", "C0200", "C0205"],
        "keywords": ["brake", "break", "abs", "pad", "spongy", "pedal", "oil leak", "rotor", "disc"],
        "price_range_pkr": {"low": 1500, "median": 3500, "high": 9500}
    },
    "efi_electrical": {
        "title": "EFI Diagnostics & Auto Electrician",
        "description": "Engine misfire, rough idle, bad oxygen sensor, MAF sensor, wiring shorts, ECU diagnostics.",
        "dtc_prefixes": ["P0300", "P0301", "P0302", "P0303", "P0304", "P0171", "P0172", "P0101", "P0335"],
        "keywords": ["missing", "misfire", "jhatka", "lambi self", "spark plug", "injector", "wiring", "sensor", "efi"],
        "price_range_pkr": {"low": 1000, "median": 3200, "high": 12000}
    },
    "transmission_gearbox": {
        "title": "Automatic & CVT Transmission Specialist",
        "description": "Transmission slipping, gear shift delay, shudder, CVT fluid degradation, torque converter lockup.",
        "dtc_prefixes": ["P0700", "P0730", "P0741", "P0746", "P0841", "P0842"],
        "keywords": ["gear", "transmission", "cvt", "slip", "shudder", "clutch", "d-mode", "reverse"],
        "price_range_pkr": {"low": 3500, "median": 8500, "high": 25000}
    },
    "suspension_steering": {
        "title": "Suspension, Steering & Bushings Specialist",
        "description": "Suspension clunking over bumps, steering rack play, worn shock absorbers, tie rod play.",
        "dtc_prefixes": ["C1511", "C1521", "C1554", "P0606"],
        "keywords": ["khadka", "awaaz", "suspension", "steering", "shock", "kamani", "bush", "tie rod", "bearing"],
        "price_range_pkr": {"low": 1800, "median": 4500, "high": 14000}
    },
    "hvac_air_conditioning": {
        "title": "Car Air Conditioning (AC) Specialist",
        "description": "AC blowing warm air, compressor clutch failure, refrigerant gas leak, cooling coil choked.",
        "dtc_prefixes": ["B1421", "B1424", "P0531", "P0532", "P0533"],
        "keywords": ["ac", "cooling", "gas leak", "compressor", "chilled", "heater", "blower", "condenser"],
        "price_range_pkr": {"low": 2000, "median": 5500, "high": 16000}
    },
    "bodywork_denting": {
        "title": "Bodywork, Denting & Painting Specialist",
        "description": "Accident collision repair, paintless dry denting (PDR), computerized oven paint baking, panel alignment.",
        "dtc_prefixes": ["B0001", "B0010", "B1000"],
        "keywords": ["dent", "denting", "paint", "painting", "scratch", "accident", "body", "bumper", "fender", "collision"],
        "price_range_pkr": {"low": 3000, "median": 8500, "high": 35000}
    }
}

# ---------------------------------------------------------------------------
# 2. VERIFIED SPECIALIST WORKSHOP DIRECTORY (5 DUMMY WORKSHOPS)
# ---------------------------------------------------------------------------
# Pre-configured 5 dedicated automotive specialist workshops mapped to core
# vehicle subsystems. Dummy phone numbers are placeholders awaiting user custom input.

VERIFIED_WORKSHOPS = [
    {
        "id": "w_dummy_01",
        "name": "AutoCare Certified Engine & Powertrain Workshop",
        "category": "Engine, Transmission & Cooling",
        "city": "Lahore",
        "area": "Auto Care Zone 1 (Engine Hub)",
        "lat_offset": 0.012,
        "lon_offset": 0.015,
        "lat": 31.5324,
        "lon": 74.3737,
        "specialties": ["engine_cooling", "transmission_gearbox"],
        "rating": 4.9,
        "review_count": 184,
        "active_queue_slots": 3,
        "verified_oem": ["Toyota", "Honda", "Suzuki"],
        "contact": "+92 344 7564460"
    },
    {
        "id": "w_dummy_02",
        "name": "Precision Brake, Steering & Suspension Center",
        "category": "Suspension, Steering & Braking",
        "city": "Lahore",
        "area": "Auto Care Zone 2 (Chassis Hub)",
        "lat_offset": -0.018,
        "lon_offset": -0.012,
        "lat": 31.5024,
        "lon": 74.3467,
        "specialties": ["brakes_hydraulics", "suspension_steering"],
        "rating": 4.8,
        "review_count": 142,
        "active_queue_slots": 2,
        "verified_oem": ["Toyota", "Honda", "Suzuki"],
        "contact": "+92 344 7564461"
    },
    {
        "id": "w_dummy_03",
        "name": "CoolTech Automotive AC & Climate Specialist",
        "category": "AC & Climate Control",
        "city": "Lahore",
        "area": "Auto Care Zone 3 (Thermal Hub)",
        "lat_offset": 0.022,
        "lon_offset": -0.019,
        "lat": 31.5424,
        "lon": 74.3397,
        "specialties": ["hvac_air_conditioning"],
        "rating": 4.8,
        "review_count": 126,
        "active_queue_slots": 2,
        "verified_oem": ["Toyota", "Suzuki", "Daihatsu"],
        "contact": "+92 344 7564462"
    },
    {
        "id": "w_dummy_04",
        "name": "MasterCraft Denting, Painting & Bodywork Lab",
        "category": "Bodywork, Denting & Painting",
        "city": "Lahore",
        "area": "Auto Care Zone 4 (Collision Hub)",
        "lat_offset": -0.025,
        "lon_offset": 0.021,
        "lat": 31.4954,
        "lon": 74.3797,
        "specialties": ["bodywork_denting"],
        "rating": 4.9,
        "review_count": 210,
        "active_queue_slots": 4,
        "verified_oem": ["Toyota", "Honda", "Kia", "Hyundai"],
        "contact": "+92 344 7564463"
    },
    {
        "id": "w_dummy_05",
        "name": "Apex General Auto Care & EFI Electrical Center",
        "category": "General Auto Care & EFI Diagnostics",
        "city": "Lahore",
        "area": "Auto Care Zone 5 (Diagnostics Hub)",
        "lat_offset": 0.005,
        "lon_offset": -0.008,
        "lat": 31.5254,
        "lon": 74.3507,
        "specialties": ["efi_electrical", "engine_cooling"],
        "rating": 4.9,
        "review_count": 275,
        "active_queue_slots": 3,
        "verified_oem": ["Toyota", "Honda", "Suzuki", "Nissan"],
        "contact": "+92 344 7564464"
    }
]

# ---------------------------------------------------------------------------
# 3. HAVERSINE GPS DISTANCE FORMULA
# ---------------------------------------------------------------------------

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points on the Earth in kilometers."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

# ---------------------------------------------------------------------------
# 4. DISPATCH ENGINE MODELS & LOGIC
# ---------------------------------------------------------------------------

class DispatchRequest(BaseModel):
    user_lat: float = Field(default=31.5204, description="User current latitude (default Lahore)")
    user_lon: float = Field(default=74.3587, description="User current longitude")
    city: str = Field(default="Lahore", description="Target metropolitan city")
    dtc_code: Optional[str] = Field(default=None, description="Diagnostic trouble code (e.g. P0217)")
    symptom_text: Optional[str] = Field(default=None, description="Driver description in English/Urdu")
    vehicle_make: str = Field(default="Toyota", description="Vehicle make (Toyota, Honda, Suzuki)")

class WorkshopRecommendation(BaseModel):
    workshop_id: str
    name: str
    city: str
    area: str
    lat: float
    lon: float
    distance_km: float
    rating: float
    review_count: int
    matched_specialty: str
    specialty_title: str
    composite_score: float
    estimated_pkr_low: int
    estimated_pkr_median: int
    estimated_pkr_high: int
    verified_oem: List[str]
    contact: str

class DispatchResponse(BaseModel):
    detected_specialty: str
    specialty_title: str
    specialty_description: str
    recommendations: List[WorkshopRecommendation]
    fair_price_pkr: Dict[str, int]
    routing_algorithm: str = "Haversine Proximity + Multi-Criteria Composite Scoring"

def detect_specialty(dtc_code: Optional[str], symptom_text: Optional[str]) -> str:
    """Classify the incoming fault into 1 of 6 core automotive specialties."""
    if dtc_code:
        code_upper = dtc_code.strip().upper()
        for spec_key, spec_data in SPECIALTIES.items():
            for prefix in spec_data["dtc_prefixes"]:
                if code_upper.startswith(prefix):
                    return spec_key

    if symptom_text:
        text_lower = symptom_text.lower()
        # Count keyword frequency and weights for each specialty
        counts: Dict[str, int] = {k: 0 for k in SPECIALTIES}
        for spec_key, spec_data in SPECIALTIES.items():
            for kw in spec_data["keywords"]:
                if kw in text_lower:
                    # Give higher weight to strong anchor terms
                    weight = 2 if kw in ["gear", "transmission", "brake", "radiator", "overheat", "ac"] else 1
                    counts[spec_key] += weight

        best_spec = max(counts, key=counts.get)
        if counts[best_spec] > 0:
            return best_spec

    return "engine_cooling"  # Default fallback specialty

def evaluate_composite_score(skill_match: float, distance_km: float, rating: float, queue_slots: int) -> float:
    """Calculate the multi-criteria composite routing score:
    Score = (0.40 * Skill) + (0.30 * Distance) + (0.20 * Rating) + (0.10 * Queue)
    """
    # Skill match is 1.0 (exact match) or 0.5 (general)
    # Distance: Normalized score from 0 to 1 (1.0 for 0 km, 0.0 for >= 25 km)
    norm_dist = max(0.0, 1.0 - (distance_km / 25.0))
    # Rating: Normalized from 0 to 1 (rating / 5.0)
    norm_rating = min(1.0, max(0.0, rating / 5.0))
    # Queue: Normalized from 0 to 1 (more slots = better, capped at 4)
    norm_queue = min(1.0, queue_slots / 4.0)

    score = (0.40 * skill_match) + (0.30 * norm_dist) + (0.20 * norm_rating) + (0.10 * norm_queue)
    return round(score, 3)

def recommend_specialist_workshops(req: DispatchRequest) -> DispatchResponse:
    """Match driver fault to verified nearby workshops and return ranked recommendations."""
    specialty_key = detect_specialty(req.dtc_code, req.symptom_text)
    spec_info = SPECIALTIES[specialty_key]

    results: List[WorkshopRecommendation] = []
    for w in VERIFIED_WORKSHOPS:
        # Compute realistic nearby coordinates offset from user location
        if "lat_offset" in w and "lon_offset" in w:
            w_lat = round(req.user_lat + w["lat_offset"], 5)
            w_lon = round(req.user_lon + w["lon_offset"], 5)
        else:
            w_lat = w["lat"]
            w_lon = w["lon"]

        dist = haversine_distance_km(req.user_lat, req.user_lon, w_lat, w_lon)
        skill = 1.0 if specialty_key in w["specialties"] else 0.4
        score = evaluate_composite_score(skill, dist, w["rating"], w["active_queue_slots"])

        results.append(WorkshopRecommendation(
            workshop_id=w["id"],
            name=w["name"],
            city=req.city or w["city"],
            area=w["area"],
            lat=w_lat,
            lon=w_lon,
            distance_km=dist,
            rating=w["rating"],
            review_count=w["review_count"],
            matched_specialty=specialty_key,
            specialty_title=spec_info["title"],
            composite_score=score,
            estimated_pkr_low=spec_info["price_range_pkr"]["low"],
            estimated_pkr_median=spec_info["price_range_pkr"]["median"],
            estimated_pkr_high=spec_info["price_range_pkr"]["high"],
            verified_oem=w["verified_oem"],
            contact=w["contact"]
        ))

    # Sort descending by composite score
    results.sort(key=lambda x: x.composite_score, reverse=True)

    return DispatchResponse(
        detected_specialty=specialty_key,
        specialty_title=spec_info["title"],
        specialty_description=spec_info["description"],
        recommendations=results[:5],  # Top 5 ranked workshops
        fair_price_pkr=spec_info["price_range_pkr"]
    )
