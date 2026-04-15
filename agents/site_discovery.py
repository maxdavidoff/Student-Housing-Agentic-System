from __future__ import annotations

from pathlib import Path

from config.settings import SCRAPER_BACKEND
from services.discovery_service import run_discovery_pipeline
from utils.io import read_json


def discover_sites(university_name: str, city: str | None = None, approved_sites_path: str | None = None) -> list[dict]:
    if approved_sites_path and Path(approved_sites_path).exists():
        return read_json(approved_sites_path)
    return []
