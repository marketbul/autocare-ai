"""Acceptance tests for Stories 10 & 11: Vehicle Health Index & Maintenance Prediction (M7)."""
from __future__ import annotations

import unittest

from autocare.health_maintenance import HealthAndMaintenanceService


class Story10And11(unittest.TestCase):
    def setUp(self):
        self.svc = HealthAndMaintenanceService()

    def test_story10_health_index_breakdown_and_composite(self):
        summary = self.svc.calculate_health_index(
            user_vehicle_id="uv-1",
            current_mileage=45000,
            service_history=[
                {"service_type": "engine", "service_date": "2026-08-01", "mileage": 42000},
                {"service_type": "braking", "service_date": "2026-05-01", "mileage": 40000},
            ],
            active_faults=[]
        )
        self.assertTrue(0.0 <= summary.composite_score <= 100.0)
        self.assertIn("engine", summary.groups)
        self.assertIn("braking", summary.groups)
        self.assertIn("cooling", summary.groups)
        self.assertIn("transmission", summary.groups)
        self.assertIn("not a certified physical sensor", summary.disclaimer)

    def test_story10_open_fault_reduces_group_health(self):
        healthy = self.svc.calculate_health_index("uv-1", 45000, [], active_faults=[])
        faulted = self.svc.calculate_health_index(
            "uv-1", 45000, [],
            active_faults=[{"predicted_category": "braking", "predicted_urgency": "critical"}]
        )
        self.assertLess(faulted.groups["braking"].score, healthy.groups["braking"].score)

    def test_story11_predict_next_service_window(self):
        pred = self.svc.predict_next_service(
            user_vehicle_id="uv-1",
            current_mileage=82000,
            usage_profile="city",
            service_history=[{"service_type": "engine", "mileage": 80000}]
        )
        self.assertIsNotNone(pred.next_item)
        self.assertTrue(pred.target_mileage >= 82000)
        self.assertTrue(pred.days_remaining > 0)
        self.assertIn("-", pred.estimated_due_date)

# [2026-10-07] test(suite): [AUT-120] author 

# [2026-10-05] test(suite): [AUT-120] author compr by Abdullah Mudasir
