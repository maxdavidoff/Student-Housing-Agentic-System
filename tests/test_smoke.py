from __future__ import annotations

from agents.preference_parser import build_preference_profile
from agents.repair_agent import RepairManager


def test_preference_parser_smoke() -> None:
    payload = {
        "search_id": "smoke_001",
        "university": {
            "name": "University of Pennsylvania",
            "city": "Philadelphia",
            "state": "PA",
            "campus_anchor": {"label": "College Hall", "lat": 39.9522, "lng": -75.1932},
        },
        "dates": {"move_in": "2026-08-15", "lease_term_months": 12, "flexible_days": 14},
        "budget": {"monthly_rent_max": 1400},
        "roommates": {"count": 2, "wants_private_bedroom": True},
        "location": {"max_distance_miles": 1.5, "max_commute_minutes": 20},
        "preferences": {"required": ["laundry"], "preferred": ["wifi"], "dealbreakers": []},
    }
    prefs = build_preference_profile(payload)
    assert prefs.university.name == "University of Pennsylvania"


def test_repair_manager_smoke() -> None:
    payload = {
        "search_id": "smoke_001",
        "university": {
            "name": "University of Pennsylvania",
            "city": "Philadelphia",
            "state": "PA",
            "campus_anchor": {"label": "College Hall", "lat": 39.9522, "lng": -75.1932},
        },
        "dates": {"move_in": "2026-08-15", "lease_term_months": 12, "flexible_days": 14},
        "budget": {"monthly_rent_max": 1400},
        "roommates": {"count": 2, "wants_private_bedroom": True},
        "location": {"max_distance_miles": 1.5, "max_commute_minutes": 20},
        "preferences": {"required": ["laundry"], "preferred": ["wifi"], "dealbreakers": []},
    }
    prefs = build_preference_profile(payload)
    manager = RepairManager()
    row, audit = manager.prepare_row(
        {
            "listing_id": "lst_test",
            "title": "Student house near campus",
            "description": "Starting at $1100. Laundry hookups only.",
            "price_text": "Starting at $1100",
            "address_text": "Near campus",
            "amenities_text": [],
        },
        prefs,
    )
    assert row["price_is_estimated"] is True
    assert audit.repair_decision.should_repair is True
