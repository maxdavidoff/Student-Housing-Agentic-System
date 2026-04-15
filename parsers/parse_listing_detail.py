from __future__ import annotations

from extractors.listing_detail_extractor import extract_detail_fields


def parse_listing_detail(html: str) -> dict:
    return extract_detail_fields(html)
