from __future__ import annotations

from typing import Optional

from schemas.listing import ListingRecord, SourceInfo


def _norm_str(value: Optional[str]) -> str:
    return (value or "").strip().lower()


def _same_address(a: ListingRecord, b: ListingRecord) -> bool:
    aa = a.normalized.address
    bb = b.normalized.address
    return (
        _norm_str(aa.street) == _norm_str(bb.street)
        and _norm_str(aa.city) == _norm_str(bb.city)
        and _norm_str(aa.state) == _norm_str(bb.state)
        and _norm_str(aa.postal_code) == _norm_str(bb.postal_code)
        and bool(aa.street)
    )


def _same_geo(a: ListingRecord, b: ListingRecord, tol: float = 0.0008) -> bool:
    aa = a.normalized.address
    bb = b.normalized.address
    if aa.lat is None or aa.lng is None or bb.lat is None or bb.lng is None:
        return False
    return abs(aa.lat - bb.lat) <= tol and abs(aa.lng - bb.lng) <= tol


def _same_unit_shape(a: ListingRecord, b: ListingRecord) -> bool:
    return (
        a.normalized.unit.bedrooms == b.normalized.unit.bedrooms
        and a.normalized.unit.bathrooms == b.normalized.unit.bathrooms
    )


def _close_price(a: ListingRecord, b: ListingRecord, tol: float = 75.0) -> bool:
    pa = a.normalized.pricing.monthly_rent
    pb = b.normalized.pricing.monthly_rent
    if pa is None or pb is None:
        return False
    return abs(pa - pb) <= tol


def is_probable_duplicate(a: ListingRecord, b: ListingRecord) -> bool:
    if _same_address(a, b) and _close_price(a, b):
        return True
    if _same_geo(a, b) and _same_unit_shape(a, b) and _close_price(a, b):
        return True
    return False


def _merge_sources(a: list[SourceInfo], b: list[SourceInfo]) -> list[SourceInfo]:
    seen = set()
    merged: list[SourceInfo] = []
    for src in a + b:
        key = (src.site_name, src.listing_url)
        if key not in seen:
            seen.add(key)
            merged.append(src)
    return merged


def merge_duplicate_group(group: list[ListingRecord]) -> ListingRecord:
    base = group[0]

    for other in group[1:]:
        base.sources = _merge_sources(base.sources, other.sources)
        for k, v in other.normalized.amenities.items():
            base.normalized.amenities[k] = base.normalized.amenities.get(k, False) or v
        for field, conf in other.quality.field_confidence.items():
            base.quality.field_confidence[field] = max(
                base.quality.field_confidence.get(field, 0.0), conf
            )
        base.quality.repair_notes.extend(other.quality.repair_notes)
        base.quality.dedupe_notes.append(f"merged_duplicate:{other.listing_id}")

    base.canonical_id = base.canonical_id or f"canon_{base.listing_id}"
    return base


def deduplicate_listings(records: list[ListingRecord]) -> list[ListingRecord]:
    """Group likely duplicates and merge them into canonical listings."""
    groups: list[list[ListingRecord]] = []

    for rec in records:
        placed = False
        for group in groups:
            if is_probable_duplicate(rec, group[0]):
                group.append(rec)
                placed = True
                break
        if not placed:
            groups.append([rec])

    return [merge_duplicate_group(group) for group in groups]
