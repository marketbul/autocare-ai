"""Automotive Fault Taxonomy for AI Auto Pakistan.

Defines the 18 standardized automotive fault categories, multilingual labels
(English, Urdu, Roman Urdu, Punjabi), affected subcomponents, and diagnostic boundaries.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class DiagnosisStage(str, Enum):
    """Distinguishes anecdotal reports from confirmed technical diagnostics."""
    OWNER_REPORTED_PROBLEM = "owner_reported_problem"
    MECHANIC_SUGGESTED_CAUSE = "mechanic_suggested_cause"
    MECHANIC_CONFIRMED_DIAGNOSIS = "mechanic_confirmed_diagnosis"
    VERIFIED_REPAIR_OUTCOME = "verified_repair_outcome"


@dataclass
class FaultCategory:
    category_id: str
    name: str
    name_ur: str
    name_roman_ur: str
    description: str
    subcomponents: List[str] = field(default_factory=list)
    multilingual_symptom_keywords: List[str] = field(default_factory=list)
    typical_causes: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "category_id": self.category_id,
            "name": self.name,
            "name_ur": self.name_ur,
            "name_roman_ur": self.name_roman_ur,
            "description": self.description,
            "subcomponents": self.subcomponents,
            "multilingual_symptom_keywords": self.multilingual_symptom_keywords,
            "typical_causes": self.typical_causes,
        }


# The 18 mandatory automotive fault categories tailored to Pakistani vehicles
AUTOMOTIVE_FAULT_CATEGORIES: Dict[str, FaultCategory] = {
    "FC-01": FaultCategory(
        category_id="FC-01",
        name="Engine",
        name_ur="انجن",
        name_roman_ur="Injan / Engine",
        description="Internal combustion engine mechanical issues, combustion chamber, pistons, valves, cylinder head, gaskets, knocking, and misfires.",
        subcomponents=["Pistons", "Cylinder Head", "Head Gasket", "Valves", "Timing Belt/Chain", "Camshaft", "Crankshaft", "Connecting Rods", "Engine Mounts"],
        multilingual_symptom_keywords=["engine knocking", "khatkhat", "misfire", "engine awaz", "rough idle", "loss of power", "pataka", "انجن کی آواز", "کھٹ کھٹ", "کمزور پک", "jhatka engine"],
        typical_causes=["Worn rod bearings", "Blown head gasket", "Carbon accumulation", "Timing misalignment", "Broken engine mount"],
    ),
    "FC-02": FaultCategory(
        category_id="FC-02",
        name="Transmission",
        name_ur="ٹرانسمیشن / گیئر بکس",
        name_roman_ur="Transmission / Gearbox",
        description="Manual, automatic (AT), and continuously variable transmission (CVT) gearbox issues, gear shifting delays, slipping, and gear whine.",
        subcomponents=["Torque Converter", "CVT Belt/Pulley", "Gearbox Solenoids", "Synchronizer Rings", "Shift Fork", "Transmission Valve Body", "Gear Oil"],
        multilingual_symptom_keywords=["gear slip", "gear phansna", "gear nahi lag raha", "delay in shifting", "gear awaz", "CVT judder", "گیئر نہیں لگ رہا", "گیئر سلپ", "gear jerking"],
        typical_causes=["Low or degraded transmission fluid", "Worn synchronizers", "Faulty shift solenoid", "CVT belt wear"],
    ),
    "FC-03": FaultCategory(
        category_id="FC-03",
        name="Clutch",
        name_ur="کلچ سسٹم",
        name_roman_ur="Clutch System",
        description="Manual transmission clutch friction disk, pressure plate, release bearing, master/slave cylinders, and cable/hydraulic actuation.",
        subcomponents=["Clutch Plate", "Pressure Plate", "Release Bearing", "Flywheel", "Clutch Master Cylinder", "Clutch Slave Cylinder", "Clutch Cable"],
        multilingual_symptom_keywords=["clutch slip", "clutch hard", "clutch pedal down", "clutch awaz", "heavy clutch", "کلچ سخت ہے", "کلچ سلپ", "clutch chhorne pe awaz"],
        typical_causes=["Worn clutch friction plate", "Damaged release bearing", "Leaking slave cylinder", "Stretched clutch cable"],
    ),
    "FC-04": FaultCategory(
        category_id="FC-04",
        name="Brakes",
        name_ur="بریک سسٹم",
        name_roman_ur="Brakes / Break System",
        description="Hydraulic friction braking, ABS module, master cylinder, brake pads, rotors, drums, calipers, brake booster, and lines.",
        subcomponents=["Brake Pads", "Brake Rotors / Discs", "Brake Calipers", "Brake Master Cylinder", "Brake Booster", "ABS Actuator / Module", "Brake Lines / Fluid"],
        multilingual_symptom_keywords=["brake squeal", "seeti", "chis", "brake lagane pe awaz", "spongy brake", "brake pedal floor", "car pulling on brake", "بریک پیڈل نیچے", "بریک کی آواز", "بریک فیل"],
        typical_causes=["Worn brake pads", "Warped brake rotor", "Air in brake lines", "Master cylinder internal leakage", "ABS sensor failure"],
    ),
    "FC-05": FaultCategory(
        category_id="FC-05",
        name="Suspension",
        name_ur="سسپنشن / جھولے",
        name_roman_ur="Suspension / Chimte / Shocks",
        description="Shock absorbers, struts, coil springs, lower control arms (chimte), ball joints, stabilizer bar links, and suspension bushings.",
        subcomponents=["Shock Absorbers", "Struts", "Coil Springs", "Lower Control Arm (Chimta)", "Ball Joints", "Sway Bar Bushings", "Link Rods", "Strut Mounts"],
        multilingual_symptom_keywords=["khadkhad", "gaddhe pe awaz", "chulbula", "car bouncing", "suspension thud", "chimte ki awaz", "shock leak", "کھڈوں میں آواز", "جھٹکے", "شاک خراب"],
        typical_causes=["Blown shock absorber", "Torn lower control arm bushing", "Worn ball joint", "Broken link rod"],
    ),
    "FC-06": FaultCategory(
        category_id="FC-06",
        name="Steering",
        name_ur="اسٹیئرنگ سسٹم",
        name_roman_ur="Steering / Kangi",
        description="Steering rack and pinion (steering kangi), electric power steering (EPS) motor, hydraulic steering pump, tie rod ends, and steering column.",
        subcomponents=["Steering Rack (Kangi)", "Tie Rod Ends", "EPS Motor", "EPS ECU", "Power Steering Pump", "Steering Column", "Clock Spring"],
        multilingual_symptom_keywords=["steering hard", "steering wandering", "steering awaz", "EPS light on", "steering katne pe awaz", "tak tak steering", "اسٹیئرنگ بھاری", "اسٹیئرنگ کی آواز"],
        typical_causes=["Worn steering rack teeth / bushes", "Tie rod play", "EPS torque sensor failure", "Low power steering fluid"],
    ),
    "FC-07": FaultCategory(
        category_id="FC-07",
        name="Electrical System",
        name_ur="الیکٹریکل سسٹم / وائرنگ",
        name_roman_ur="Electrical / Wiring",
        description="Vehicle wiring harness, fuses, relays, lighting systems, power windows, central locking, ignition switch, and grounding circuits.",
        subcomponents=["Wiring Harness", "Fuse Box", "Relays", "Headlights / Tail lights", "Power Window Motor", "Central Locking Actuator", "Ground Wire"],
        multilingual_symptom_keywords=["fuse blow", "light band", "short circuit", "wiring short", "sheeshey nahi chal rahe", "locking problem", "وائرنگ جل گئی", "فیوز اڑ گیا"],
        typical_causes=["Short circuit from aftermarket accessories", "Corroded chassis ground", "Blown fuse", "Faulty relay"],
    ),
    "FC-08": FaultCategory(
        category_id="FC-08",
        name="Battery and Charging",
        name_ur="بیٹری اور چارجنگ",
        name_roman_ur="Battery aur Generator / Alternator",
        description="12V lead-acid / dry battery, alternator (generator), voltage regulator, battery terminals, charging cables, and parasitic draw.",
        subcomponents=["12V Battery", "Alternator (Generator)", "Voltage Regulator", "Battery Terminals", "Ground Strap", "Drive Belt"],
        multilingual_symptom_keywords=["battery drain", "battery down", "battery light on", "dhakka start", "self nahi utha raha", "alternator awaz", "بیٹری ڈاؤن", "گاڑی سلف نہیں لے رہی"],
        typical_causes=["Sulfated / expired battery cells", "Worn alternator carbon brushes", "Loose alternator belt", "Parasitic current drain"],
    ),
    "FC-09": FaultCategory(
        category_id="FC-09",
        name="Cooling System",
        name_ur="کولنگ سسٹم / ریڈی ایٹر",
        name_roman_ur="Cooling System / Radiator",
        description="Engine cooling, radiator, cooling fan, water pump, thermostat valve, coolant reservoir, radiator cap, and hoses.",
        subcomponents=["Radiator", "Cooling Fan Motor", "Water Pump", "Thermostat Valve", "Coolant Reservoir", "Radiator Cap", "Radiator Hoses"],
        multilingual_symptom_keywords=["car overheat", "radiator pani kam", "coolant leak", "gauge full up", "steam from bonnet", "fan nahi chal raha", "گاڑی گرم ہو رہی ہے", "پانی کم ہو رہا ہے", "ریڈی ایٹر لیک"],
        typical_causes=["Failed radiator fan motor", "Stuck thermostat valve", "Clogged radiator core", "Leaking water pump seal", "Faulty radiator cap"],
    ),
    "FC-10": FaultCategory(
        category_id="FC-10",
        name="Fuel System",
        name_ur="فیول سسٹم / پٹرول فیڈ",
        name_roman_ur="Fuel System / Petrol System",
        description="Fuel delivery, fuel pump, fuel filter, fuel injectors, throttle body, fuel rail, pressure regulator, and fuel tank.",
        subcomponents=["Fuel Pump", "Fuel Filter", "Fuel Injectors", "Throttle Body", "Fuel Pressure Regulator", "Fuel Tank", "Fuel Lines"],
        multilingual_symptom_keywords=["poor fuel average", "fuel smell", "engine bogging", "race nahi le rahi", "injector choke", "petrol ziyaada kha rahi", "پٹرول زیادہ کھا رہی ہے", "فیول پمپ کی آواز"],
        typical_causes=["Clogged fuel injectors", "Weak fuel pump pressure", "Dirty fuel filter", "Faulty fuel pressure regulator"],
    ),
    "FC-11": FaultCategory(
        category_id="FC-11",
        name="Exhaust System",
        name_ur="ایگزاسٹ / سائلنسر",
        name_roman_ur="Exhaust / Silencer",
        description="Exhaust manifold, catalytic converter, muffler (silencer), exhaust pipes, oxygen sensors, and exhaust leaks.",
        subcomponents=["Exhaust Manifold", "Catalytic Converter (Cat)", "Oxygen (O2) Sensor", "Muffler", "Resonator", "Exhaust Flange Gasket"],
        multilingual_symptom_keywords=["loud exhaust", "silencer phata hua", "cat choked", "silencer awaz", "exhaust smoke smell", "سائلنسر کی آواز", "کیٹالسٹ چوک"],
        typical_causes=["Choked catalytic converter", "Cracked exhaust manifold", "Rusted silencer body", "Failed O2 sensor"],
    ),
    "FC-12": FaultCategory(
        category_id="FC-12",
        name="Air Conditioning",
        name_ur="ایئر کنڈیشننگ / اے سی",
        name_roman_ur="Air Conditioning / AC",
        description="Automotive HVAC, AC compressor, condenser, cooling coil (evaporator), expansion valve, blower motor, cabin filter, and refrigerant gas (R134a).",
        subcomponents=["AC Compressor", "AC Condenser", "Evaporator / Cooling Coil", "Expansion Valve", "AC Blower Motor", "Cabin Filter", "AC Gas (R134a)"],
        multilingual_symptom_keywords=["AC cooling nahi kar raha", "AC gas leak", "AC compressor awaz", "blower slow", "AC bad smell", "اے سی ٹھنڈا نہیں کر رہا", "اے سی گیس لیک"],
        typical_causes=["Leaking cooling coil", "Seized AC compressor clutch", "Low refrigerant charge", "Choked cabin air filter"],
    ),
    "FC-13": FaultCategory(
        category_id="FC-13",
        name="Tires and Wheels",
        name_ur="ٹائر اور پہیے",
        name_roman_ur="Tires aur Wheels / Pahiye",
        description="Tires, steel/alloy rims, wheel bearings, wheel alignment, wheel balancing, lug nuts, and tire pressure monitoring.",
        subcomponents=["Tires", "Alloy / Steel Wheels", "Wheel Bearings", "Wheel Hub", "Lug Nuts", "Tire Valves"],
        multilingual_symptom_keywords=["car vibration at 80", "wheel bearing awaz", "gunjti awaz", "tire uneven wear", "steering wobble", "ٹائر گھس رہا ہے", "پہیے کی آواز"],
        typical_causes=["Worn wheel hub bearing", "Unbalanced wheels", "Misaligned toe/camber", "Bent alloy rim"],
    ),
    "FC-14": FaultCategory(
        category_id="FC-14",
        name="Sensors and ECU",
        name_ur="سینسرز اور ای سی یو",
        name_roman_ur="Sensors aur ECU",
        description="Electronic Control Unit (ECU), engine sensors (MAF, MAP, O2, Crank, Cam, Knock, TPS, Coolant Temp), and wiring signals.",
        subcomponents=["Engine ECU", "MAF / MAP Sensor", "Crankshaft Position Sensor", "Camshaft Position Sensor", "Throttle Position Sensor (TPS)", "Knock Sensor"],
        multilingual_symptom_keywords=["check engine light on", "sensor kharab", "crank sensor fail", "misfire code", "ECU error", "چیک انجن لائٹ", "سینسر خراب"],
        typical_causes=["Dirty MAF sensor", "Faulty crank/cam position sensor", "Wiring loom resistance issue", "Corroded sensor connector"],
    ),
    "FC-15": FaultCategory(
        category_id="FC-15",
        name="Body and Exterior",
        name_ur="باڈی اور بیرونی حصہ",
        name_roman_ur="Body aur Exterior",
        description="Vehicle frame, body panels, bumpers, doors, hood, trunk lid, paint finish, rust/corrosion, and structural alignment.",
        subcomponents=["Front Bumper", "Rear Bumper", "Fenders", "Doors", "Hood / Bonnet", "Trunk / Diggi", "Side Mirrors", "Windshield"],
        multilingual_symptom_keywords=["bumper loose", "bonnet rattle", "door alignment", "body rust", "rust in running board", "باڈی میں زنگ", "بمپر ٹوٹ گیا"],
        typical_causes=["Collision impact", "Saltwater/moisture corrosion", "Loose plastic clips", "Worn door hinges"],
    ),
    "FC-16": FaultCategory(
        category_id="FC-16",
        name="Interior and Dashboard",
        name_ur="انٹیریئر اور ڈیش بورڈ",
        name_roman_ur="Interior aur Dashboard",
        description="Dashboard instrument cluster, warning indicators, seats, seat belts, steering clock spring, dashboard rattles, and center console.",
        subcomponents=["Instrument Cluster", "Warning Lights", "Dashboard Trim", "Seats", "Seat Belts", "Center Console", "Airbag Module"],
        multilingual_symptom_keywords=["dashboard rattle", "speedometer not working", "warning light blinking", "interior squeak", "ڈیش بورڈ سے آواز", "میٹر بند"],
        typical_causes=["Loose dashboard clips", "Speedometer cable / VSS sensor failure", "Blown cluster bulbs / LEDs"],
    ),
    "FC-17": FaultCategory(
        category_id="FC-17",
        name="Starting and Ignition",
        name_ur="اسٹارٹنگ اور اگنیشن",
        name_roman_ur="Starting aur Ignition / Self",
        description="Starter motor (self), ignition coils, spark plugs, ignition key switch, immobilizer, and starter solenoid.",
        subcomponents=["Starter Motor (Self)", "Starter Solenoid", "Ignition Coils", "Spark Plugs", "Ignition Switch", "Immobilizer Key / Antenna"],
        multilingual_symptom_keywords=["car not starting", "gaari start nahi ho rahi", "self le rahi hai start nahi ho rahi", "click sound no crank", "khali self", "گاڑی اسٹارٹ نہیں ہو رہی", "سلف آواز کر رہا ہے"],
        typical_causes=["Worn starter motor brushes", "Fouled spark plugs", "Weak ignition coil", "Immobilizer key chip unread"],
    ),
    "FC-18": FaultCategory(
        category_id="FC-18",
        name="Lubrication System",
        name_ur="لیوبریکیشن سسٹم / انجن آئل",
        name_roman_ur="Lubrication System / Engine Oil",
        description="Engine oil pump, oil filter, oil pan (chamber), oil pressure switch, oil passages, oil consumption, and oil leaks.",
        subcomponents=["Oil Pump", "Oil Filter", "Oil Pan / Sump (Chamber)", "Oil Pressure Switch", "Valve Cover Gasket", "Crankshaft Oil Seals"],
        multilingual_symptom_keywords=["oil leak", "oil pressure light", "engine oil kam ho raha", "chamber leak", "oil batti on", "blue smoke oil burn", "انجن آئل کم ہو رہا ہے", "آئل لیک"],
        typical_causes=["Worn valve stem seals", "Damaged oil pan / chamber gasket", "Clogged oil pump pickup strainer", "Leaking main oil seal"],
    ),
}


class TaxonomyManager:
    """Provides validated categorization and multilingual taxonomy lookups."""

    def __init__(self, categories: Optional[Dict[str, FaultCategory]] = None) -> None:
        self._categories = categories or AUTOMOTIVE_FAULT_CATEGORIES

    def get_by_id(self, category_id: str) -> Optional[FaultCategory]:
        return self._categories.get(category_id)

    def get_by_name(self, name: str) -> Optional[FaultCategory]:
        lower_name = name.strip().lower()
        for cat in self._categories.values():
            if cat.name.lower() == lower_name or cat.category_id.lower() == lower_name:
                return cat
        return None

    def list_all(self) -> List[FaultCategory]:
        return list(self._categories.values())

    def match_category_from_text(self, text: str) -> Optional[FaultCategory]:
        """Heuristic rule-based matching using multilingual keywords."""
        if not text:
            return None
        text_lower = text.lower()

        # Score categories by keyword frequency
        scores: Dict[str, int] = {}
        for cat_id, cat in self._categories.items():
            score = 0
            # Check main category names
            if cat.name.lower() in text_lower:
                score += 5
            # Check symptom keywords
            for kw in cat.multilingual_symptom_keywords:
                if kw.lower() in text_lower:
                    score += 3
            # Check subcomponents
            for comp in cat.subcomponents:
                if comp.lower() in text_lower:
                    score += 2
            if score > 0:
                scores[cat_id] = score

        if not scores:
            return None
        best_cat_id = max(scores, key=lambda k: scores[k])
        return self._categories[best_cat_id]


_TAXONOMY_INSTANCE: TaxonomyManager | None = None


def get_taxonomy_manager() -> TaxonomyManager:
    """Singleton getter for TaxonomyManager."""
    global _TAXONOMY_INSTANCE
    if _TAXONOMY_INSTANCE is None:
        _TAXONOMY_INSTANCE = TaxonomyManager()
    return _TAXONOMY_INSTANCE
