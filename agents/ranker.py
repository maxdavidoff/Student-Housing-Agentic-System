from __future__ import annotations

from schemas.listing import ListingRecord
from schemas.preferences import PreferenceProfile
from scoring.filters import passes_hard_filters
from scoring.score_components import component_scores


def build_explanation(listing: ListingRecord, prefs: PreferenceProfile) -> str:
    parts: list[str] = []

    rent = listing.normalized.pricing.monthly_rent
    if rent is not None:
        parts.append(f"${rent:,.0f}/mo")

    dist = listing.normalized.location.distance_miles_to_campus
    if dist is not None:
        parts.append(f"{dist:.1f} miles from campus")

    matched_prefs = [
        pref for pref in prefs.preferences.preferred
        if listing.normalized.amenities.get(pref, False)
    ]
    if matched_prefs:
        parts.append("matches preferred: " + ", ".join(matched_prefs[:3]))

    if listing.freshness.low_availability_warning:
        parts.append("stale listing warning")

    if listing.quality.missing_fields:
        parts.append("missing info: " + ", ".join(listing.quality.missing_fields[:2]))

    if len(listing.sources) > 1:
        parts.append(f"verified across {len(listing.sources)} sources")

    return " | ".join(parts)


def score_listing(listing: ListingRecord, prefs: PreferenceProfile) -> ListingRecord:
    passed, reasons = passes_hard_filters(listing, prefs)
    scores = component_scores(listing, prefs)
    weights = prefs.ranking_weights.as_dict()

    raw_weighted = sum(scores[k] * weights[k] for k in scores)
    final_score = raw_weighted * listing.quality.confidence_multiplier

    if not passed:
        final_score *= 0.10

    listing.ranking.hard_filter_pass = passed
    listing.ranking.component_scores = scores
    listing.ranking.raw_weighted_score = round(raw_weighted, 4)
    listing.ranking.final_score = round(final_score, 4)
    listing.ranking.explanation = build_explanation(listing, prefs)

    if reasons:
        listing.quality.parse_warnings.extend(reasons)

    return listing


def rank_listings(listings: list[ListingRecord], prefs: PreferenceProfile, top_k: int = 5) -> list[ListingRecord]:
    scored = [score_listing(item, prefs) for item in listings]
    scored.sort(
        key=lambda x: (
            x.ranking.hard_filter_pass,
            x.ranking.final_score,
            len(x.sources),
        ),
        reverse=True,
    )
    return scored[:top_k]
