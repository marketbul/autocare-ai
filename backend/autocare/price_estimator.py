"""Automotive Exact Price Estimator & Explanation Engine for Pakistan.
Computes itemized exact repair bills in PKR (OEM vs Aftermarket vs Kabli)
with comprehensive engineering and market explanations across major Pakistani cities.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


CITY_FACTORS = {
    "Lahore": {
        "parts_factor": 1.00,
        "labor_factor": 1.00,
        "primary_hubs": "Bilal Gunj, Montgomery Road, Badami Bagh",
        "description": "Baseline auto parts hub with direct access to Bilal Gunj wholesale import warehouses."
    },
    "Karachi": {
        "parts_factor": 0.98,
        "labor_factor": 0.95,
        "primary_hubs": "Plaza Market (M.A Jinnah Rd), Shershah Scrap/Kabli Market, Tariq Road",
        "description": "Port city proximity reduces freight costs by ~2%. High workshop competition keeps labor competitive."
    },
    "Islamabad": {
        "parts_factor": 1.04,
        "labor_factor": 1.10,
        "primary_hubs": "Sector I-9, G-10 Workshop Cluster, Rawalpindi Sultan Ka Khoo",
        "description": "Freight transit from southern ports adds ~4%. Capital territory technician labor rates average +10% higher."
    },
    "Rawalpindi": {
        "parts_factor": 1.02,
        "labor_factor": 1.00,
        "primary_hubs": "Sultan Ka Khoo, Peshawar Road, Saddar Auto Market",
        "description": "Northern transit hub with extensive Kabli and OEM supply lines centered at Sultan Ka Khoo."
    }
}


class PriceEstimator:
    def __init__(self, catalog_path: Optional[Path | str] = None) -> None:
        if catalog_path is None:
            catalog_path = Path(__file__).resolve().parent.parent / "data" / "pakistan_automotive_parts_catalog.json"
        self.catalog_path = Path(catalog_path)
        self.records: List[Dict[str, Any]] = []
        self._load_catalog()

    def _load_catalog(self) -> None:
        if not self.catalog_path.exists():
            # Fall back to building it if not present
            from .parts_dataset_builder import generate_local_parts_dataset
            generate_local_parts_dataset()

        with open(self.catalog_path, "r", encoding="utf-8") as f:
            self.records = json.load(f)

    def get_all_parts(self, model: Optional[str] = None, category: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns filtered parts catalog records."""
        results = list(self.records)

        if model and model.lower() != "all":
            clean_model = model.lower()
            results = [r for r in results if clean_model in r["vehicle_model"].lower()]

        if category and category.lower() != "all":
            clean_cat = category.lower()
            results = [r for r in results if r["subsystem"].lower() == clean_cat]

        if search and search.strip():
            terms = search.lower().split()
            filtered = []
            for r in results:
                haystack = f"{r['part_name']} {r['part_number_oem']} {r['subsystem']} {r['common_symptoms']} {r['vehicle_model']}".lower()
                if any(t in haystack for t in terms):
                    filtered.append(r)
            results = filtered

        return results

    def find_best_matching_part(self, query: str, vehicle_model: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Matches a user symptom or part name against the catalog using relevance scoring."""
        if not query or not query.strip():
            # Default to first relevant vehicle part
            candidates = self.get_all_parts(vehicle_model)
            return candidates[0] if candidates else (self.records[0] if self.records else None)

        clean_query = query.lower().strip()
        tokens = [w for w in clean_query.replace("-", " ").replace(",", " ").split() if len(w) > 2]

        # Vehicle filter preference
        candidates = list(self.records)
        if vehicle_model and vehicle_model.lower() != "all":
            v_key = vehicle_model.lower()
            vehicle_matched = [r for r in candidates if v_key in r["vehicle_model"].lower()]
            if vehicle_matched:
                candidates = vehicle_matched

        best_score = -1
        best_record = None

        for r in candidates:
            score = 0
            # Match directly on part name
            part_name_clean = r["part_name"].lower()
            if clean_query in part_name_clean:
                score += 15
            for t in tokens:
                if t in part_name_clean:
                    score += 5
                if t in r["subsystem"].lower():
                    score += 4
                if t in r["common_symptoms"].lower():
                    score += 3
                if t in r["part_number_oem"].lower():
                    score += 10
                if t in r["counterfeit_warning"].lower():
                    score += 1

            if score > best_score:
                best_score = score
                best_record = r

        return best_record or (candidates[0] if candidates else None)

    def estimate_exact_price(
        self,
        query_or_part: str,
        vehicle_model: str = "Toyota Corolla",
        quality_tier: str = "genuine_oem",  # "genuine_oem" | "aftermarket" | "kabli_refurbished"
        city: str = "Lahore"
    ) -> Dict[str, Any]:
        """Calculates exact line-item quotation in PKR with comprehensive explanation."""
        part = self.find_best_matching_part(query_or_part, vehicle_model)
        if not part:
            return {"error": "No matching part found in catalog"}

        city_data = CITY_FACTORS.get(city, CITY_FACTORS["Lahore"])
        parts_factor = city_data["parts_factor"]
        labor_factor = city_data["labor_factor"]

        # Select base part price based on quality tier
        if quality_tier == "aftermarket":
            tier_name = f"Certified Quality Aftermarket ({part['aftermarket_brand']})"
            base_part_price = part["aftermarket_price_exact_pkr"]
            part_price_min = part["aftermarket_price_min_pkr"]
            part_price_max = part["aftermarket_price_max_pkr"]
            tier_advice = f"Good cost-effective choice. {part['aftermarket_brand']} meets JIS/SAE specifications for everyday commuting in Pakistan."
        elif quality_tier == "kabli_refurbished":
            tier_name = "Tested Japanese Kabli (Bilal Gunj / Shershah Salvage)"
            base_part_price = part["kabli_refurbished_price_pkr"]
            part_price_min = round(part["kabli_refurbished_price_pkr"] * 0.85)
            part_price_max = round(part["kabli_refurbished_price_pkr"] * 1.15)
            tier_advice = "Genuine OEM recycled from Japanese domestic market half-cuts. Always verify bearing spin and test under pressure before payment."
        else:  # genuine_oem
            quality_tier = "genuine_oem"
            tier_name = f"Factory Genuine OEM ({part['oem_brand']})"
            base_part_price = part["oem_price_exact_pkr"]
            part_price_min = part["oem_price_min_pkr"]
            part_price_max = part["oem_price_max_pkr"]
            tier_advice = f"Maximum durability and thermal endurance. Guaranteed fitment for {part['vehicle_model']} without modification."

        # Adjusted Part Cost
        adjusted_part_cost = round(base_part_price * parts_factor)
        adjusted_part_min = round(part_price_min * parts_factor)
        adjusted_part_max = round(part_price_max * parts_factor)

        # Labor Cost
        labor_hours = part["standard_labor_hours"]
        base_labor_rate = part["base_labor_rate_pkr"]
        adjusted_labor_cost = round(base_labor_rate * labor_factor)

        # Consumables / Lathe Tooling
        consumables_cost = round(part["consumables_lathe_pkr"])

        # Exact Total Bill
        exact_total_pkr = adjusted_part_cost + adjusted_labor_cost + consumables_cost
        total_min_pkr = adjusted_part_min + round(adjusted_labor_cost * 0.9) + consumables_cost
        total_max_pkr = adjusted_part_max + round(adjusted_labor_cost * 1.15) + consumables_cost

        # Build Explanation Sections
        explanation = {
            "component_summary": f"{part['part_name']} ({part['part_number_oem']}) for {part['vehicle_model']} {part['vehicle_generation']}.",
            "diagnostic_rationale": f"Identified component is in the {part['subsystem'].upper()} subsystem. Primary symptoms include: {part['common_symptoms']}.",
            "failure_consequence": part["failure_consequence"],
            "tier_assessment": tier_advice,
            "counterfeit_prevention": part["counterfeit_warning"],
            "city_market_context": f"Pricing calibrated for {city}. {city_data['description']} Best sourced from {city_data['primary_hubs']}.",
            "workshop_negotiation_checklist": [
                f"Verify standard replacement labor: This job requires {labor_hours} hours. Do not pay beyond Rs. {adjusted_labor_cost:,}.",
                f"Confirm consumables: Ask if the quote includes Rs. {consumables_cost:,} for required shop supplies/lathe work or if it is billed separately.",
                f"Inspect packaging: Ensure part packaging has tamper seals intact before mechanic installs it on the vehicle."
            ]
        }

        return {
            "matched_part": {
                "part_id": part["part_id"],
                "part_name": part["part_name"],
                "part_number_oem": part["part_number_oem"],
                "vehicle_model": part["vehicle_model"],
                "vehicle_generation": part["vehicle_generation"],
                "engine_code": part["engine_code"],
                "subsystem": part["subsystem"],
                "selected_tier": quality_tier,
                "tier_name": tier_name,
            },
            "location": {
                "city": city,
                "hubs": city_data["primary_hubs"]
            },
            "pricing_breakdown": {
                "part_price_exact_pkr": adjusted_part_cost,
                "part_price_range_pkr": f"Rs. {adjusted_part_min:,} - Rs. {adjusted_part_max:,}",
                "labor_hours": labor_hours,
                "labor_cost_pkr": adjusted_labor_cost,
                "consumables_lathe_pkr": consumables_cost,
                "exact_total_pkr": exact_total_pkr,
                "total_range_pkr": f"Rs. {total_min_pkr:,} - Rs. {total_max_pkr:,}",
                "currency": "PKR"
            },
            "explanation": explanation
        }
