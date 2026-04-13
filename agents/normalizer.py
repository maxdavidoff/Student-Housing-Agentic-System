from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from typing import Optional

from schemas.listing import (
    Address,
    FreshnessInfo,
    ListingRecord,
    NormalizedListing,
    Pricing,
    QualityInfo,
    RawListing,
    SourceInfo,
    StudentFit,
    UnitInfo,
    LocationStats,
)
from schemas.preferences import PreferenceProfile

PRICE_RE = re.compile(r"(\d[\d,]*(?:\.\d{1,2})?)")
BED_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:br|bed|bedroom)", re.IGNORECASE)
BATH_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:ba|bath)", re.IGNORECASE)

AMENITY_PATTERNS = {
    "laundry": ["laundry", "washer", "dryer"],
    "wifi": ["wifi", "wi-fi", "internet included"],
    "furnished": ["furnished"],
    "gym": ["gym", "fitness center"],
    "air_conditioning": ["air conditioning", "a/c", "ac"],
    "dishwasher": ["dishwasher"],
    "parking": ["parking", "garage"],
    "basement_unit": ["basement"],
    "no_kitchen": ["no kitchen", "kitchenette only"],
}


def _haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_miles = 3958.8
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius_miles * c


def _first_price(text: str | None) -> Optional[float]:
    if not text:
        return None
    match = PRICE_RE.search(text.replace("$", ""))
    if not match:
        return None
    return float(match.group(1).replace(",", ""))


def _extract_count(pattern: re.Pattern[str], text: str | None) -> Optional[float]:
    if not text:
        return None
    match = pattern.search(text)
    if not match:
        return None
    return float(match.group(1))


def _infer_amenities(text_blob: str, explicit: list[str]) -> dict[str, bool]:
    text = (text_blob or "").lower()
    explicit_norm = {item.strip().lower() for item in explicit}
    results: dict[str, bool] = {}
    for amenity, phrases in AMENITY_PATTERNS.items():
        phrase_hit = any(p in text for p in phrases)
        explicit_hit = any(p in explicit_norm for p in phrases)
        results[amenity] = phrase_hit or explicit_hit
    return results


def _parse_address(address_text: str | None) -> Address:
    if not address_text:
        return Address()

    parts = [p.strip() for p in address_text.split(",")]
    street = parts[0] if len(parts) > 0 else None
    city = parts[1] if len(parts) > 1 else None
    state = None
    postal_code = None

    if len(parts) > 2:
        state_zip = parts[2].split()
        if state_zip:
            state = state_zip[0]
        if len(state_zip) > 1:
            postal_code = state_zip[1]

    return Address(street=street, city=city, state=state, postal_code=postal_code)


def _parse_dt(value: str | None) -> Optional[datetime]:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _compute_freshness(scraped_at: Optional[datetime], posted_at: Optional[datetime]) -> FreshnessInfo:
    now = datetime.now(timezone.utc)
    anchor = posted_at or scraped_at
    age_days = None
    if anchor is not None:
        age_days = (now - anchor).total_seconds() / 86400
    return FreshnessInfo(
        latest_scraped_at=scraped_at,
        latest_posted_at=posted_at,
        age_days=age_days,
        low_availability_warning=(age_days is not None and age_days > 3),
    )


def _compute_confidence_multiplier(
    field_conf: dict[str, float],
    missing_fields: list[str],
    price_is_estimated: bool,
    address_is_fuzzy: bool,
) -> float:
    avg_conf = sum(field_conf.values()) / len(field_conf) if field_conf else 0.75
    multiplier = avg_conf
    if price_is_estimated:
        multiplier *= 0.85
    if address_is_fuzzy:
        multiplier *= 0.85
    if any(field in missing_fields for field in ["monthly_rent", "bedrooms", "distance_miles_to_campus"]):
        multiplier *= 0.80
    return max(0.50, min(1.0, round(multiplier, 4)))


def normalize_listing(raw_row: dict, prefs: PreferenceProfile) -> ListingRecord:
    """Normalize a raw row into a canonical listing record.

    TODO:
    - replace address parsing with geocoding
    - expand amenities extraction
    - enrich commute time by mode
    """
    row = dict(raw_row)
    repair_notes = list(row.get("repair_notes", []))

    text_blob = " ".join(
        [
            row.get("title", "") or "",
            row.get("description", "") or "",
            row.get("price_text", "") or "",
            row.get("address_text", "") or "",
            " ".join(row.get("amenities_text", []) or []),
        ]
    )

    price = _first_price(row.get("price_text"))
    bedrooms = row.get("bedrooms")
    bathrooms = row.get("bathrooms")
    if bedrooms is None:
        bedrooms = _extract_count(BED_RE, text_blob)
    if bathrooms is None:
        bathrooms = _extract_count(BATH_RE, text_blob)

    address = _parse_address(row.get("address_text"))
    address.lat = row.get("lat")
    address.lng = row.get("lng")

    campus = prefs.university.campus_anchor
    distance = None
    walk_minutes = None
    if (
        campus.lat is not None
        and campus.lng is not None
        and address.lat is not None
        and address.lng is not None
    ):
        distance = _haversine_miles(campus.lat, campus.lng, address.lat, address.lng)
        walk_minutes = int(round(distance * 20))

    amenities = _infer_amenities(text_blob, row.get("amenities_text", []) or [])
    for k, v in row.get("amenity_overrides", {}).items():
        amenities[k] = v

    if row.get("furnished") is True:
        amenities["furnished"] = True

    pricing = Pricing(
        monthly_rent=price,
        per_person="per person" in (row.get("price_text", "") or "").lower(),
        utilities_included=row.get("utilities_included"),
        fees_estimated_total=row.get("fees_estimated_total"),
        deposit_estimated=row.get("deposit_estimated"),
        price_is_estimated=bool(row.get("price_is_estimated", False)),
    )

    normalized = NormalizedListing(
        address=address,
        pricing=pricing,
        unit=UnitInfo(
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            furnished=row.get("furnished"),
            lease_term_months=row.get("lease_term_months"),
            available_from=row.get("available_from"),
        ),
        location=LocationStats(
            distance_miles_to_campus=distance,
            walk_minutes_to_campus=walk_minutes,
            transit_minutes_to_campus=row.get("transit_minutes_to_campus"),
        ),
        amenities=amenities,
        student_fit=StudentFit(
            near_student_area=(distance is not None and distance <= 1.5),
            private_bedroom_possible=(bedrooms is not None and bedrooms >= (prefs.roommates.count + 1)),
            roommate_friendly=(bedrooms is not None and bedrooms >= 2),
        ),
    )

    missing_fields = []
    if price is None:
        missing_fields.append("monthly_rent")
    if distance is None:
        missing_fields.append("distance_miles_to_campus")
    if bedrooms is None:
        missing_fields.append("bedrooms")

    field_conf = {
        "monthly_rent": 0.98 if price is not None else 0.20,
        "distance_miles_to_campus": 0.95 if distance is not None else 0.30,
        "bedrooms": 0.90 if bedrooms is not None else 0.25,
        "bathrooms": 0.85 if bathrooms is not None else 0.25,
        "amenities": 0.80,
    }

    scraped_at = _parse_dt(row.get("scraped_at"))
    posted_at = _parse_dt(row.get("posted_at"))
    freshness = _compute_freshness(scraped_at, posted_at)

    confidence_multiplier = _compute_confidence_multiplier(
        field_conf=field_conf,
        missing_fields=missing_fields,
        price_is_estimated=pricing.price_is_estimated,
        address_is_fuzzy=bool(row.get("address_is_fuzzy", False)),
    )

    return ListingRecord(
        listing_id=row["listing_id"],
        search_id=prefs.search_id,
        sources=[
            SourceInfo(
                site_name=row["site_name"],
                source_type=row["source_type"],
                listing_url=row["listing_url"],
                scraped_at=scraped_at or datetime.now(timezone.utc),
                posted_at=posted_at,
                parser_strategy=row.get("parser_strategy", "rule_based"),
                raw_artifact_path=row.get("raw_artifact_path"),
            )
        ],
        raw=RawListing(
            title=row.get("title"),
            description=row.get("description"),
            raw_price_text=row.get("price_text"),
            raw_address_text=row.get("address_text"),
            raw_amenities_text=row.get("amenities_text", []) or [],
        ),
        normalized=normalized,
        freshness=freshness,
        quality=QualityInfo(
            field_confidence=field_conf,
            missing_fields=missing_fields,
            parse_warnings=[],
            repair_notes=repair_notes,
            confidence_multiplier=confidence_multiplier,
        ),
    )
