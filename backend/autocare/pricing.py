"""Automotive Spare Parts and Labour Price Reference for Pakistan (Proposal §7.9).
Provides market-verified benchmark pricing (OEM vs Aftermarket parts + Workshop Labour)
for Toyota Corolla, Honda Civic, and Suzuki Swift across major Pakistani urban centres.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class PartPriceQuote:
    part_name: str
    category: str
    oem_price_min_pkr: float
    oem_price_max_pkr: float
    aftermarket_price_min_pkr: float
    aftermarket_price_max_pkr: float
    estimated_labour_pkr: float
    recommended_replacement_hours: float
    quality_notes: str


PAKISTAN_PRICE_DATABASE: dict[str, list[PartPriceQuote]] = {
    "corolla": [
        PartPriceQuote(
            part_name="Front Brake Pads (Set)",
            category="braking",
            oem_price_min_pkr=14500,
            oem_price_max_pkr=18500,
            aftermarket_price_min_pkr=4500,
            aftermarket_price_max_pkr=7500,
            estimated_labour_pkr=2000,
            recommended_replacement_hours=1.0,
            quality_notes="Toyota OEM pads (Advics/Akebono) resist brake fade. Aftermarket brands (MK Kashiyama / Asuki) require bed-in."
        ),
        PartPriceQuote(
            part_name="Engine Water Pump & Gasket",
            category="cooling",
            oem_price_min_pkr=18000,
            oem_price_max_pkr=24000,
            aftermarket_price_min_pkr=6500,
            aftermarket_price_max_pkr=10500,
            estimated_labour_pkr=4500,
            recommended_replacement_hours=2.5,
            quality_notes="Aisin OEM water pump recommended. Unbranded pumps frequently suffer premature bearing failure within 20,000 km."
        ),
        PartPriceQuote(
            part_name="Engine Thermostat Valve (82°C)",
            category="cooling",
            oem_price_min_pkr=4800,
            oem_price_max_pkr=6500,
            aftermarket_price_min_pkr=1800,
            aftermarket_price_max_pkr=2800,
            estimated_labour_pkr=1500,
            recommended_replacement_hours=0.8,
            quality_notes="Always replace rubber O-ring seal. Avoid removing thermostat permanently in Pakistan summers as ECU stays in warm-up loop."
        ),
        PartPriceQuote(
            part_name="Cylinder Head Gasket (Multi-Layer Steel)",
            category="engine",
            oem_price_min_pkr=16500,
            oem_price_max_pkr=22000,
            aftermarket_price_min_pkr=5500,
            aftermarket_price_max_pkr=8500,
            estimated_labour_pkr=25000,
            recommended_replacement_hours=8.0,
            quality_notes="Requires cylinder head resurfacing / skimming (Rs. 6,000 - 9,000 lathe charges) if engine severely overheated."
        ),
        PartPriceQuote(
            part_name="Super CVT-i Transmission Fluid (4L Can FE)",
            category="transmission",
            oem_price_min_pkr=15500,
            oem_price_max_pkr=19500,
            aftermarket_price_min_pkr=9000,
            aftermarket_price_max_pkr=13000,
            estimated_labour_pkr=2500,
            recommended_replacement_hours=1.2,
            quality_notes="Toyota Genuine CVT Fluid FE only. Use of Dexron ATF or CVT-TC fluid will cause shuddering and slip."
        ),
        PartPriceQuote(
            part_name="Ignition Coil (Per Cylinder)",
            category="electrical",
            oem_price_min_pkr=12000,
            oem_price_max_pkr=16000,
            aftermarket_price_min_pkr=3500,
            aftermarket_price_max_pkr=5500,
            estimated_labour_pkr=1000,
            recommended_replacement_hours=0.5,
            quality_notes="Denso OEM diamond coils prevent intermittent secondary misfire codes (P0300/P0301)."
        )
    ],
    "civic": [
        PartPriceQuote(
            part_name="Front Ceramic Brake Pads (Set)",
            category="braking",
            oem_price_min_pkr=19500,
            oem_price_max_pkr=26000,
            aftermarket_price_min_pkr=6000,
            aftermarket_price_max_pkr=9500,
            estimated_labour_pkr=2500,
            recommended_replacement_hours=1.0,
            quality_notes="Nissin OEM pads recommended. Aftermarket metallic pads can cause brake rotor warping on high speed stops."
        ),
        PartPriceQuote(
            part_name="AC Condenser & Receiver Drier Assembly",
            category="cooling",
            oem_price_min_pkr=38000,
            oem_price_max_pkr=48000,
            aftermarket_price_min_pkr=16000,
            aftermarket_price_max_pkr=24000,
            estimated_labour_pkr=6000,
            recommended_replacement_hours=3.0,
            quality_notes="10th Gen Civic (FC) condenser commonly suffers stone chip corrosion. Vacuum and R134a recharge required."
        ),
        PartPriceQuote(
            part_name="1.5L Turbo High-Pressure Fuel Injector (Each)",
            category="engine",
            oem_price_min_pkr=32000,
            oem_price_max_pkr=42000,
            aftermarket_price_min_pkr=12000,
            aftermarket_price_max_pkr=18000,
            estimated_labour_pkr=7000,
            recommended_replacement_hours=3.5,
            quality_notes="Direct injection injectors operate at 20 MPa. Leaking injectors cause cylinder fuel washing and oil dilution."
        ),
        PartPriceQuote(
            part_name="Earth Dreams CVT Fluid HCF-2 (4 Litres)",
            category="transmission",
            oem_price_min_pkr=18000,
            oem_price_max_pkr=23000,
            aftermarket_price_min_pkr=11000,
            aftermarket_price_max_pkr=15000,
            estimated_labour_pkr=3000,
            recommended_replacement_hours=1.2,
            quality_notes="Honda HCF-2 fluid mandatory. Never use Honda ATF DW-1 or generic multi-vehicle CVT fluids."
        ),
        PartPriceQuote(
            part_name="Electric Power Steering (EPS) Motor Assembly",
            category="steering",
            oem_price_min_pkr=65000,
            oem_price_max_pkr=95000,
            aftermarket_price_min_pkr=28000,
            aftermarket_price_max_pkr=42000,
            estimated_labour_pkr=8000,
            recommended_replacement_hours=4.0,
            quality_notes="Sticky steering notch in 11th Gen requires torque sensor calibration via Honda HDS scanner."
        )
    ],
    "swift": [
        PartPriceQuote(
            part_name="Front Brake Pads (Set)",
            category="braking",
            oem_price_min_pkr=9500,
            oem_price_max_pkr=13500,
            aftermarket_price_min_pkr=3200,
            aftermarket_price_max_pkr=5200,
            estimated_labour_pkr=1500,
            recommended_replacement_hours=0.8,
            quality_notes="Pak Suzuki genuine pads guarantee rotor longevity. Clean caliper slide pins with silicone grease."
        ),
        PartPriceQuote(
            part_name="Radiator Cooling Fan Motor Assembly",
            category="cooling",
            oem_price_min_pkr=16000,
            oem_price_max_pkr=22000,
            aftermarket_price_min_pkr=6500,
            aftermarket_price_max_pkr=9500,
            estimated_labour_pkr=2500,
            recommended_replacement_hours=1.5,
            quality_notes="Failing fan motor carbon brushes cause sudden traffic overheating in 40°C+ summer weather."
        ),
        PartPriceQuote(
            part_name="Clutch Plate & Pressure Plate Kit (Manual)",
            category="transmission",
            oem_price_min_pkr=22000,
            oem_price_max_pkr=29000,
            aftermarket_price_min_pkr=12000,
            aftermarket_price_max_pkr=17000,
            estimated_labour_pkr=7000,
            recommended_replacement_hours=4.0,
            quality_notes="Exedy OEM clutch kit recommended. Inspect and machine flywheel surface before installation."
        ),
        PartPriceQuote(
            part_name="CVT Fluid Green-2 (4 Litres)",
            category="transmission",
            oem_price_min_pkr=14000,
            oem_price_max_pkr=18000,
            aftermarket_price_min_pkr=8500,
            aftermarket_price_max_pkr=12000,
            estimated_labour_pkr=2500,
            recommended_replacement_hours=1.0,
            quality_notes="Jatco CVT7 requires Suzuki Green-2 or Shell Spirax S5 CVT X. Replace auxiliary paper filter cartridge."
        ),
        PartPriceQuote(
            part_name="Alternator / Serpentine V-Belt",
            category="engine",
            oem_price_min_pkr=4200,
            oem_price_max_pkr=5800,
            aftermarket_price_min_pkr=1600,
            aftermarket_price_max_pkr=2500,
            estimated_labour_pkr=1200,
            recommended_replacement_hours=0.6,
            quality_notes="Mitsuboshi or Bando 4PK/5PK belt. Check tensioner bearing for squealing noise."
        )
    ]
}


class PricingService:
    def get_quotes_for_model(self, model: str, category: Optional[str] = None) -> list[dict]:
        clean_model = (model or "").lower()
        key = "corolla"
        if "civic" in clean_model:
            key = "civic"
        elif "swift" in clean_model:
            key = "swift"

        quotes = PAKISTAN_PRICE_DATABASE.get(key, PAKISTAN_PRICE_DATABASE["corolla"])
        if category and category.lower() != "all":
            quotes = [q for q in quotes if q.category.lower() == category.lower()]

        return [
            {
                "part_name": q.part_name,
                "category": q.category,
                "oem_price_range_pkr": f"Rs. {q.oem_price_min_pkr:,.0f} - {q.oem_price_max_pkr:,.0f}",
                "aftermarket_price_range_pkr": f"Rs. {q.aftermarket_price_min_pkr:,.0f} - {q.aftermarket_price_max_pkr:,.0f}",
                "estimated_labour_pkr": f"Rs. {q.estimated_labour_pkr:,.0f}",
                "total_estimated_repair_pkr": f"Rs. {q.oem_price_min_pkr + q.estimated_labour_pkr:,.0f} - {q.oem_price_max_pkr + q.estimated_labour_pkr:,.0f}",
                "recommended_replacement_hours": q.recommended_replacement_hours,
                "quality_notes": q.quality_notes,
            }
            for q in quotes
        ]
