from __future__ import annotations


def discover_sites(university_name: str, city: str | None = None) -> list[dict]:
    return [
        {
            "site_name": "Sample Apartments",
            "source_type": "aggregator",
            "coverage_area": city or "unknown",
            "worth_querying": True,
            "scrape_method": "adapter",
            "confidence": 0.90,
            "browser_required": False,
        },
        {
            "site_name": "Campus Rentals",
            "source_type": "local_site",
            "coverage_area": city or "unknown",
            "worth_querying": True,
            "scrape_method": "adapter",
            "confidence": 0.82,
            "browser_required": True,
        },
    ]
