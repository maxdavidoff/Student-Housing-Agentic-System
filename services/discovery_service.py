from __future__ import annotations

from agents.discovery_agent import discover_candidate_sites
from agents.probe_agent import probe_sites
from agents.site_ranker import rank_verified_sites
from agents.url_verifier import verify_site_candidates
from config.settings import SCRAPER_BACKEND
from schemas.preferences import PreferenceProfile
from utils.io import write_json, write_jsonl


def _build_adapter():
    """Lazy-load adapters so optional browser dependencies do not break sample runs."""
    if SCRAPER_BACKEND == "ohana":
        from adapters.ohana_adapter import OhanaAdapter

        return OhanaAdapter()
    if SCRAPER_BACKEND == "playwright":
        from adapters.playwright_site_adapter import PlaywrightSiteAdapter

        return PlaywrightSiteAdapter()

    from adapters.sample_adapter import SampleAdapter

    return SampleAdapter()


def _approved_site_payload(site, probe, prefs: PreferenceProfile) -> dict:
    return {
        "site_name": site.site_name,
        "source_type": site.source_type,
        "coverage_area": prefs.university.city or "unknown",
        "worth_querying": True,
        "scrape_method": site.scrape_method_hint,
        "browser_required": site.browser_required,
        "base_url": site.base_url,
        "search_url_template": site.verified_search_url or site.candidate_search_url or site.base_url,
        "candidate_listing_url": probe.listing_url or site.candidate_listing_url,
        "confidence": site.overall_site_score,
        "base_domain": site.base_domain,
    }


def run_discovery_pipeline(prefs: PreferenceProfile, output_dir: str) -> dict:
    prompt, candidates = discover_candidate_sites(prefs)
    verified = verify_site_candidates(candidates)
    ranked = rank_verified_sites(verified)

    adapter = _build_adapter()
    probe_results = probe_sites(
        candidates=ranked,
        adapter=adapter,
        query=prefs.model_dump(mode="json"),
        dead_letter_dir=f"{output_dir}/dead_letter_queue",
        artifacts_dir=f"{output_dir}/artifacts",
        max_sites=5,
    )

    approved_sites = []
    for site, probe in zip(ranked, probe_results):
        if probe.scrapeable and probe.minimum_schema_pass:
            approved_sites.append(_approved_site_payload(site, probe, prefs))

    write_json(f"{output_dir}/discovery_prompt.json", {"prompt": prompt})
    write_json(
        f"{output_dir}/site_candidates.json",
        [row.model_dump(mode="json") for row in candidates],
    )
    write_json(
        f"{output_dir}/verified_sites.json",
        [row.model_dump(mode="json") for row in ranked],
    )
    write_jsonl(
        f"{output_dir}/probe_results.jsonl",
        [row.model_dump(mode="json") for row in probe_results],
    )
    write_json(f"{output_dir}/approved_sites.json", approved_sites)

    return {
        "prompt": prompt,
        "site_candidates": candidates,
        "verified_sites": ranked,
        "probe_results": probe_results,
        "approved_sites": approved_sites,
    }
