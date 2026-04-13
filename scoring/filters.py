from __future__ import annotations

from schemas.listing import ListingRecord
from schemas.preferences import PreferenceProfile


def passes_hard_filters(listing: ListingRecord, prefs: PreferenceProfile) -> tuple[bool, list[str]]:
    reasons: list[str] = []

    rent = listing.normalized.pricing.monthly_rent
    if rent is None:
        reasons.append("missing_rent")
    elif rent > prefs.budget.monthly_rent_max:
        reasons.append("over_budget")

    if prefs.budget.utilities_included_required:
        if listing.normalized.pricing.utilities_included is not True:
            reasons.append("utilities_not_included")

    if prefs.budget.one_time_fee_max is not None:
        fees = listing.normalized.pricing.fees_estimated_total
        if fees is not None and fees > prefs.budget.one_time_fee_max:
            reasons.append("fees_too_high")

    max_dist = prefs.location.max_distance_miles
    dist = listing.normalized.location.distance_miles_to_campus
    if max_dist is not None and dist is not None and dist > max_dist:
        reasons.append("too_far")

    max_commute = prefs.location.max_commute_minutes
    walk = listing.normalized.location.walk_minutes_to_campus
    transit = listing.normalized.location.transit_minutes_to_campus
    observed_commute = walk if walk is not None else transit
    if max_commute is not None and observed_commute is not None and observed_commute > max_commute:
        reasons.append("commute_too_long")

    if prefs.roommates.wants_private_bedroom:
        bedrooms = listing.normalized.unit.bedrooms
        roommate_count = prefs.roommates.count + 1
        if bedrooms is not None and bedrooms < roommate_count:
            reasons.append("not_enough_bedrooms")

    for req in prefs.preferences.required:
        if not listing.normalized.amenities.get(req, False):
            reasons.append(f"missing_required_{req}")

    for dealbreaker in prefs.preferences.dealbreakers:
        if listing.normalized.amenities.get(dealbreaker, False):
            reasons.append(f"dealbreaker_{dealbreaker}")

    return (len(reasons) == 0, reasons)
