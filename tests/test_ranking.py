from __future__ import annotations

from agents.normalizer import normalize_listing
from agents.ranker import rank_listings
from schemas.preferences import (
    Budget,
    CampusAnchor,
    Dates,
    LocationPreferences,
    PreferenceBuckets,
    PreferenceProfile,
    Roommates,
    UniversityContext,
)


def build_prefs() -> PreferenceProfile:
    return PreferenceProfile(
        search_id="test_search",
        university=UniversityContext(
            name="University of Pennsylvania",
            city="Philadelphia",
            state="PA",
            campus_anchor=CampusAnchor(
                label="College Hall",
                lat=39.9522,
                lng=-75.1932,
            ),
        ),
        dates=Dates(move_in="2026-08-15", lease_term_months=12),
        budget=Budget(monthly_rent_max=1400),
        roommates=Roommates(count=2, wants_private_bedroom=True),
        location=LocationPreferences(max_distance_miles=1.5, max_commute_minutes=20),
        preferences=PreferenceBuckets(required=["laundry"], preferred=["furnished", "wifi"]),
    )


def test_top_result_respects_constraints() -> None:
    prefs = build_prefs()

    rows = [
        {
            "listing_id": "good_1",
            "site_name": "A",
            "source_type": "aggregator",
            "listing_url": "https://example.com/good_1",
            "title": "3BR furnished apartment",
            "description": "Laundry in building and WiFi included",
            "price_text": "$1,200/mo per person",
            "address_text": "4100 Walnut St, Philadelphia, PA 19104",
            "amenities_text": ["Laundry", "WiFi", "Furnished"],
            "bedrooms": 3,
            "bathrooms": 1,
            "lease_term_months": 12,
            "available_from": "2026-08-01",
            "lat": 39.9529,
            "lng": -75.2054,
            "utilities_included": True,
            "furnished": True,
        },
        {
            "listing_id": "bad_1",
            "site_name": "A",
            "source_type": "aggregator",
            "listing_url": "https://example.com/bad_1",
            "title": "2BR cheap unit",
            "description": "No laundry",
            "price_text": "$900/mo",
            "address_text": "4500 Pine St, Philadelphia, PA 19143",
            "amenities_text": [],
            "bedrooms": 2,
            "bathrooms": 1,
            "lease_term_months": 12,
            "available_from": "2026-08-15",
            "lat": 39.9545,
            "lng": -75.2200,
            "utilities_included": False,
            "furnished": False,
        },
    ]

    normalized = [normalize_listing(r, prefs) for r in rows]
    ranked = rank_listings(normalized, prefs, top_k=2)

    assert ranked[0].listing_id == "good_1"
    assert ranked[0].ranking.hard_filter_pass is True
