from __future__ import annotations

from extractors.listing_index_extractor import extract_listing_card_urls


def parse_listing_index(html: str, base_url: str, max_urls: int = 25) -> list[str]:
    return extract_listing_card_urls(html, base_url=base_url, max_urls=max_urls)
