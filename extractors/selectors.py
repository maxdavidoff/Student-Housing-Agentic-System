from __future__ import annotations

DEFAULT_INDEX_SELECTORS = {
    "listing_card": [
        "article",
        "[data-testid='property-card']",
        ".listing-card",
        ".property-card",
    ],
    "detail_link": [
        "a[href]",
    ],
}

DEFAULT_DETAIL_SELECTORS = {
    "title": ["h1", "[data-testid='property-title']"],
    "price": ["[data-testid='price']", ".price", "[class*='price']"],
    "address": ["[data-testid='address']", ".address", "address"],
    "description": ["[data-testid='description']", ".description", "section p"],
    "amenity_items": ["[data-testid='amenities'] li", ".amenities li", "ul li"],
}
