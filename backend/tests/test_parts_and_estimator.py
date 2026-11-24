"""Test suite for Pakistani Automotive Parts Dataset Builder & Exact Price Estimator."""
from autocare.parts_dataset_builder import generate_local_parts_dataset, RAW_ONLINE_PARTS_DATA
from autocare.price_estimator import PriceEstimator


def test_parts_dataset_builder():
    """Verify that dataset generation creates valid dataset structures."""
    assert len(RAW_ONLINE_PARTS_DATA) >= 20
    info = generate_local_parts_dataset()
    assert info["count"] >= 20
    assert info["json_path"].endswith(".json")
    assert info["csv_path"].endswith(".csv")


def test_price_estimator_matching():
    """Test matching queries for parts and vehicles."""
    estimator = PriceEstimator()
    # Test Brake Pads match
    res = estimator.estimate_exact_price("brake pads", "Toyota Corolla", "genuine_oem", "Lahore")
    assert res["matched_part"]["part_name"] == "Front Ceramic Brake Pads (Set of 4)"
    assert res["pricing_breakdown"]["exact_total_pkr"] > 0
    assert "Advics" in res["matched_part"]["tier_name"]

    # Test City Adjustment (Karachi vs Lahore)
    res_khi = estimator.estimate_exact_price("brake pads", "Toyota Corolla", "genuine_oem", "Karachi")
    assert res_khi["location"]["city"] == "Karachi"
    assert res_khi["pricing_breakdown"]["exact_total_pkr"] <= res["pricing_breakdown"]["exact_total_pkr"]


def test_price_estimator_tiers():
    """Test that OEM > Aftermarket > Kabli in pricing."""
    estimator = PriceEstimator()
    oem = estimator.estimate_exact_price("water pump", "Toyota Corolla", "genuine_oem", "Lahore")
    aftermarket = estimator.estimate_exact_price("water pump", "Toyota Corolla", "aftermarket", "Lahore")
    kabli = estimator.estimate_exact_price("water pump", "Toyota Corolla", "kabli_refurbished", "Lahore")

    assert oem["pricing_breakdown"]["exact_total_pkr"] > aftermarket["pricing_breakdown"]["exact_total_pkr"]
    assert aftermarket["pricing_breakdown"]["exact_total_pkr"] > kabli["pricing_breakdown"]["exact_total_pkr"]
    assert len(oem["explanation"]["workshop_negotiation_checklist"]) >= 3
