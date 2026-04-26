from __future__ import annotations

from pathlib import Path
from urllib.parse import quote_plus

from config.settings import DISCOVERY_BACKEND, SEED_SITE_CONFIG_PATH
from schemas.preferences import PreferenceProfile
from schemas.site_candidate import SiteCandidate
from utils.io import read_json


def build_discovery_prompt(prefs: PreferenceProfile) -> str:
    city = prefs.university.city or ""
    state = prefs.university.state or ""
    return f"""
Find websites with student housing listings near {prefs.university.name} in {city}, {state}.
Prioritize official university off-campus housing pages, local student housing sites,
student sublet marketplaces, and listing pages that appear scrapeable.
Exclude generic search engine result pages and ad redirect URLs.
Return JSON with this shape:
{{
  "candidates": [
    {{
      "site_name": str,
      "source_type": str,
      "base_domain": str,
      "base_url": str,
      "candidate_search_url": str,
      "candidate_listing_url": str | null,
      "relevance_reason": str,
      "discovery_confidence": float,
      "scrape_method_hint": str,
      "browser_required": bool,
      "worth_querying": bool
    }}
  ]
}}
Use current web results only.
""".strip()


def _sample_candidates(prefs: PreferenceProfile) -> list[SiteCandidate]:
    city = prefs.university.city or "unknown"
    q = quote_plus(f"student housing {prefs.university.name} {city}")
    return [
        SiteCandidate(
            site_name="Sample Apartments",
            source_type="aggregator",
            base_domain="example.com",
            base_url="https://example.com",
            candidate_search_url=f"https://example.com/search?q={q}",
            candidate_listing_url="https://example.com/lst_001",
            relevance_reason="Sample source used for local development and pipeline validation.",
            discovery_confidence=0.95,
            scrape_method_hint="sample",
            browser_required=False,
            worth_querying=True,
        ),
        SiteCandidate(
            site_name="Campus Rentals",
            source_type="local_site",
            base_domain="campus.example.com",
            base_url="https://campus.example.com",
            candidate_search_url=f"https://campus.example.com/search?q={q}",
            candidate_listing_url="https://campus.example.com/4100-walnut",
            relevance_reason="Local-style student housing source used for probe and dedupe testing.",
            discovery_confidence=0.88,
            scrape_method_hint="sample",
            browser_required=False,
            worth_querying=True,
        ),
    ]


def _seed_candidates() -> list[SiteCandidate]:
    path = Path(SEED_SITE_CONFIG_PATH)
    if not path.exists():
        return []
    payload = read_json(path)
    rows = payload.get("candidates", payload)
    return [SiteCandidate(**row) for row in rows]


def _merge_candidates(*candidate_lists: list[SiteCandidate]) -> list[SiteCandidate]:
    merged: list[SiteCandidate] = []
    seen = set()
    for items in candidate_lists:
        for candidate in items:
            key = (candidate.site_name.lower(), candidate.base_url.lower())
            if key in seen:
                continue
            seen.add(key)
            merged.append(candidate)
    return merged


def discover_candidate_sites(prefs: PreferenceProfile) -> tuple[str, list[SiteCandidate]]:
    prompt = build_discovery_prompt(prefs)
    seeded = _seed_candidates()

    if DISCOVERY_BACKEND == "openai_web_search":
        # Lazy import so the sample/local backend does not require OpenAI at import time.
        from llm_clients.openai_discovery_client import OpenAIDiscoveryClient

        payload = OpenAIDiscoveryClient().discover_sites(prompt)
        llm_candidates = [SiteCandidate(**row) for row in payload.get("candidates", [])]
        return prompt, _merge_candidates(seeded, llm_candidates)

    return prompt, _merge_candidates(seeded, _sample_candidates(prefs))
