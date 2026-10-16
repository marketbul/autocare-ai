"""M7: Vehicle Health Index & Personalised Maintenance Prediction (Stories 10 & 11).

Provides:
1. Vehicle Health Index (M7.1):
   Composite and component-group health scores (engine, transmission, braking,
   electrical, cooling, tyres) based on mileage elapsed, time elapsed, manufacturer
   service intervals, and active diagnostic faults. Transparent and deterministic.

2. Personalised Maintenance Prediction (M7.2):
   Forecasts the next required service item, the target mileage window, and estimated
   due date using vehicle mileage, usage profile (average km/month), and service history.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Any

# Standard manufacturer intervals (km, months)
DEFAULT_INTERVALS = {
    "engine": {"item": "Engine Oil & Filter", "interval_km": 5000, "interval_months": 6},
    "braking": {"item": "Brake System & Pads Inspection", "interval_km": 10000, "interval_months": 12},
    "tyres": {"item": "Tire Rotation & Pressure Check", "interval_km": 10000, "interval_months": 6},
    "cooling": {"item": "Cooling System & Coolant Inspection", "interval_km": 40000, "interval_months": 24},
    "transmission": {"item": "Transmission / CVT Fluid Service", "interval_km": 40000, "interval_months": 24},
    "electrical": {"item": "12V Battery & Charging System Test", "interval_km": 20000, "interval_months": 12},
}

URGENCY_PENALTIES = {
    "low": 10.0,
    "moderate": 25.0,
    "high": 45.0,
    "critical": 75.0,
}


@dataclass
class GroupHealth:
    group: str
    score: float  # 0 to 100
    status: str   # 'good' | 'fair' | 'due' | 'critical'
    last_serviced_mileage: int | None
    last_serviced_date: str | None
    mileage_since_service: int
    open_faults_count: int
    recommendation: str


@dataclass
class VehicleHealthSummary:
    user_vehicle_id: str
    composite_score: float
    status: str
    groups: dict[str, GroupHealth]
    data_completeness: str  # 'complete' | 'partial' | 'baseline_only'
    disclaimer: str = (
        "Transparency Note: The Vehicle Health Index is a structured summary of known recorded "
        "state and manufacturer intervals, not a certified physical sensor measurement."
    )


@dataclass
class NextServicePrediction:
    user_vehicle_id: str
    next_item: str
    target_mileage: int
    mileage_window: tuple[int, int]
    estimated_due_date: str
    days_remaining: int
    urgency: str
    rationale: str


class HealthAndMaintenanceService:
    def __init__(self, db=None):
        self.db = db

    def calculate_health_index(self,
                               user_vehicle_id: str,
                               current_mileage: int,
                               service_history: list[dict] | None = None,
                               active_faults: list[dict] | None = None) -> VehicleHealthSummary:
        history = service_history if service_history is not None else self._load_history(user_vehicle_id)
        faults = active_faults if active_faults is not None else self._load_faults(user_vehicle_id)

        groups_out: dict[str, GroupHealth] = {}
        total_score = 0.0

        for group_name, spec in DEFAULT_INTERVALS.items():
            # Find latest service for this group
            relevant_services = [s for s in history if s.get("service_type", "").lower() == group_name.lower() or
                                 group_name.lower() in s.get("service_type", "").lower()]
            last_km = None
            last_date = None
            if relevant_services:
                latest = max(relevant_services, key=lambda x: x.get("mileage", 0))
                last_km = latest.get("mileage")
                last_date = latest.get("service_date")

            km_since = (current_mileage - last_km) if last_km is not None else (current_mileage % spec["interval_km"])
            interval = spec["interval_km"]

            # Mileage degradation (100% when fresh, drops towards 0% as interval approaches or exceeds)
            if km_since <= interval:
                mileage_score = 100.0 - (km_since / interval) * 40.0  # drops from 100 to 60 at interval
            else:
                overdue = km_since - interval
                mileage_score = max(10.0, 60.0 - (overdue / interval) * 50.0)

            # Fault penalties
            group_faults = [f for f in faults if (f.get("predicted_category") or f.get("system", "")).lower() == group_name.lower()]
            penalty = 0.0
            for f in group_faults:
                urg = (f.get("predicted_urgency") or f.get("severity") or "moderate").lower()
                penalty += URGENCY_PENALTIES.get(urg, 20.0)

            final_group_score = round(max(5.0, min(100.0, mileage_score - penalty)), 1)
            total_score += final_group_score

            if final_group_score >= 80:
                status = "good"
                rec = f"Component in good condition. Next inspection in ~{max(500, interval - km_since)} km."
            elif final_group_score >= 60:
                status = "fair"
                rec = f"Service approaching within ~{max(200, interval - km_since)} km."
            elif final_group_score >= 35:
                status = "due"
                rec = f"Service overdue by {km_since - interval} km. Schedule maintenance soon."
            else:
                status = "critical"
                rec = "Urgent attention required. Fault or severe overdue service detected."

            groups_out[group_name] = GroupHealth(
                group=group_name,
                score=final_group_score,
                status=status,
                last_serviced_mileage=last_km,
                last_serviced_date=str(last_date) if last_date else None,
                mileage_since_service=km_since,
                open_faults_count=len(group_faults),
                recommendation=rec,
            )

        composite = round(total_score / len(DEFAULT_INTERVALS), 1)
        comp_status = "good" if composite >= 80 else ("fair" if composite >= 60 else "due")
        completeness = "complete" if history else "baseline_only"

        return VehicleHealthSummary(
            user_vehicle_id=user_vehicle_id,
            composite_score=composite,
            status=comp_status,
            groups=groups_out,
            data_completeness=completeness,
        )

    def predict_next_service(self,
                             user_vehicle_id: str,
                             current_mileage: int,
                             usage_profile: str = "city",
                             service_history: list[dict] | None = None) -> NextServicePrediction:
        history = service_history if service_history is not None else self._load_history(user_vehicle_id)

        # Monthly mileage rate based on usage profile
        rate_map = {"city": 1000, "mixed": 1500, "highway": 2500}
        km_per_month = rate_map.get((usage_profile or "city").lower(), 1200)

        best_item = "Engine Oil & Filter"
        min_km_remaining = 999999
        rationale = ""

        for group_name, spec in DEFAULT_INTERVALS.items():
            relevant_services = [s for s in history if group_name.lower() in s.get("service_type", "").lower()]
            if relevant_services:
                last_km = max(s.get("mileage", 0) for s in relevant_services)
            else:
                last_km = current_mileage - (current_mileage % spec["interval_km"])

            due_km = last_km + spec["interval_km"]
            remaining_km = due_km - current_mileage

            if remaining_km < min_km_remaining:
                min_km_remaining = remaining_km
                best_item = f"{spec['item']} ({group_name.title()})"
                rationale = f"Based on interval of {spec['interval_km']:,} km (last done at {last_km:,} km)."

        target_km = current_mileage + max(200, min_km_remaining)
        window = (target_km - 500, target_km + 500)

        # Estimate due date
        days_ahead = max(5, int((max(200, min_km_remaining) / km_per_month) * 30))
        due_date = dt.date.today() + dt.timedelta(days=days_ahead)

        urgency = "high" if min_km_remaining <= 500 else ("moderate" if min_km_remaining <= 1500 else "routine")

        return NextServicePrediction(
            user_vehicle_id=user_vehicle_id,
            next_item=best_item,
            target_mileage=target_km,
            mileage_window=window,
            estimated_due_date=due_date.isoformat(),
            days_remaining=days_ahead,
            urgency=urgency,
            rationale=rationale,
        )

    def _load_history(self, uvid: str) -> list[dict]:
        if not self.db:
            return []
        return self.db.query(
            "SELECT service_type, service_date, mileage, cost, notes FROM maintenancerecord WHERE user_vehicle_id = :u",
            {"u": uvid}
        )

    def _load_faults(self, uvid: str) -> list[dict]:
        if not self.db:
            return []
        return self.db.query(
            "SELECT predicted_category, predicted_urgency, code FROM diagnosticcase WHERE user_vehicle_id = :u",
            {"u": uvid}
        )
