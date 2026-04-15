from __future__ import annotations

from pathlib import Path

from config.settings import SCRAPER_BACKEND, SCRAPER_SITE_CONFIG_PATH
from utils.io import read_json


def discover_sites(university_name: str, city: str | None = None) -> list[dict]:
    if SCRAPER_BACKEND == "playwright":
        config_path = Path(SCRAPER_SITE_CONFIG_PATH)
        if config_path.exists():
            return read_json(config_path)
        return []

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
