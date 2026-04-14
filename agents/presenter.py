from __future__ import annotations

from schemas.listing import ListingRecord


def present_top_results(results: list[ListingRecord]) -> list[dict]:
    payload: list[dict] = []
    for idx, row in enumerate(results, start=1):
        payload.append(
            {
                "rank": idx,
                "listing_id": row.listing_id,
                "canonical_id": row.canonical_id,
                "title": row.raw.title,
                "final_score": row.ranking.final_score,
                "raw_weighted_score": row.ranking.raw_weighted_score,
                "hard_filter_pass": row.ranking.hard_filter_pass,
                "explanation": row.ranking.explanation,
                "price": row.normalized.pricing.monthly_rent,
                "distance_miles": row.normalized.location.distance_miles_to_campus,
                "confidence_multiplier": row.quality.confidence_multiplier,
                "age_days": row.freshness.age_days,
                "low_availability_warning": row.freshness.low_availability_warning,
                "source_sites": [src.site_name for src in row.sources],
                "source_urls": [src.listing_url for src in row.sources],
                "amenities": [k for k, v in row.normalized.amenities.items() if v],
            }
        )
    return payload
