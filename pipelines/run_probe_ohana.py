from __future__ import annotations

from adapters.ohana_adapter import OhanaAdapter
from agents.probe_agent import probe_sites
from agents.preference_parser import build_preference_profile
from config.settings import OHANA_BASE_URL, OHANA_PROBE_URL
from schemas.site_candidate import VerifiedSiteCandidate
from utils.io import read_json, write_jsonl


def run_probe(preferences_path: str, output_dir: str) -> None:
    prefs_payload = read_json(preferences_path)
    prefs = build_preference_profile(prefs_payload)

    site = VerifiedSiteCandidate(
        site_name="Ohana",
        source_type="sublet_marketplace",
        base_domain="liveohana.ai",
        base_url=OHANA_BASE_URL,
        candidate_search_url=OHANA_PROBE_URL,
        candidate_listing_url=None,
        relevance_reason="User-curated Ohana source for authenticated sublet browsing.",
        discovery_confidence=0.95,
        scrape_method_hint="ohana",
        browser_required=True,
        worth_querying=True,
        verified=True,
        verified_search_url=OHANA_PROBE_URL,
        normalized_base_domain="liveohana.ai",
        verification_notes=["manual_seed_site"],
        verification_confidence=0.95,
        structural_score=0.75,
        trust_score=0.80,
        overall_site_score=0.86,
    )

    results = probe_sites(
        candidates=[site],
        adapter=OhanaAdapter(),
        query=prefs.model_dump(mode="json"),
        dead_letter_dir=f"{output_dir}/dead_letter_queue",
        artifacts_dir=f"{output_dir}/artifacts",
        max_sites=1,
    )
    write_jsonl(f"{output_dir}/probe_results_ohana.jsonl", [r.model_dump(mode="json") for r in results])


if __name__ == "__main__":
    run_probe(
        preferences_path="data/searches/example/preferences.json",
        output_dir="data/searches/example",
    )
