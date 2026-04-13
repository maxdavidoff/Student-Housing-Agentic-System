from __future__ import annotations

from schemas.listing import ListingRecord
from schemas.preferences import PreferenceProfile


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def budget_score(listing: ListingRecord, prefs: PreferenceProfile) -> float:
    rent = listing.normalized.pricing.monthly_rent
    max_rent = prefs.budget.monthly_rent_max
    if rent is None:
        return 0.35
    if rent > max_rent:
        return 0.0
    return clamp01(1.0 - (rent / max_rent) * 0.7)


def distance_score(listing: ListingRecord, prefs: PreferenceProfile) -> float:
    dist = listing.normalized.location.distance_miles_to_campus
    max_dist = prefs.location.max_distance_miles
    if dist is None:
        return 0.5
    if max_dist is None:
        return clamp01(1.0 / (1.0 + dist))
    if dist > max_dist:
        return 0.0
    return clamp01(1.0 - dist / max_dist)


def amenities_score(listing: ListingRecord, prefs: PreferenceProfile) -> float:
    preferred = prefs.preferences.preferred
    if not preferred:
        return 1.0
    hits = sum(1 for item in preferred if listing.normalized.amenities.get(item, False))
    return hits / len(preferred)


def lease_fit_score(listing: ListingRecord, prefs: PreferenceProfile) -> float:
    desired = prefs.dates.lease_term_months
    actual = listing.normalized.unit.lease_term_months
    if desired is None and actual is None:
        return 0.8
    if desired is None or actual is None:
        return 0.6
    gap = abs(desired - actual)
    return clamp01(1.0 - (gap / max(desired, 1)))


def recency_score(listing: ListingRecord) -> float:
    age_days = listing.freshness.age_days
    if age_days is None:
        return 0.5
    if age_days <= 1:
        return 1.0
    if age_days <= 3:
        return 0.85
    if age_days <= 7:
        return 0.60
    return 0.25


def component_scores(listing: ListingRecord, prefs: PreferenceProfile) -> dict[str, float]:
    return {
        "budget": budget_score(listing, prefs),
        "distance": distance_score(listing, prefs),
        "amenities": amenities_score(listing, prefs),
        "lease_fit": lease_fit_score(listing, prefs),
        "recency": recency_score(listing),
    }
