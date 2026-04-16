from __future__ import annotations

from agents.preference_parser import build_preference_profile
from services.discovery_service import run_discovery_pipeline
from utils.io import read_json


def run_discovery(preferences_path: str, output_dir: str) -> None:
    prefs_payload = read_json(preferences_path)
    prefs = build_preference_profile(prefs_payload)
    run_discovery_pipeline(prefs, output_dir)


if __name__ == "__main__":
    run_discovery(
        preferences_path="data/searches/example/preferences.json",
        output_dir="data/searches/example",
    )
