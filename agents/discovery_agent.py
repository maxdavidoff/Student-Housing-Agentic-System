from __future__ import annotations

from urllib.parse import quote_plus

from config.settings import DISCOVERY_BACKEND
from llm_clients.openai_discovery_client import OpenAIDiscoveryClient
from schemas.preferences import PreferenceProfile
from schemas.site_candidate import SiteCandidate


def build_discovery_prompt(prefs: PreferenceProfile) -> str:
    city = prefs.university.city or ""
    state = prefs.university.state or ""
    return f"""
Find websites with student housing listings near {prefs.university.name} in {city}, {state}.
Prioritize official university off-campus housing pages, local student housing sites,
and listing pages that appear scrapeable. Exclude generic search engine result pages.
Return JSON with this shape:
{{
  "candidates": [
    {{
      "site_name": str,
      "source_type": str,
      "base_domain": str,
      "base_url": str,
      "candidate_search_url": str,
      "candidate_listing_url": str,
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


def discover_candidate_sites(prefs: PreferenceProfile) -> tuple[str, list[SiteCandidate]]:
    prompt = build_discovery_prompt(prefs)

    if DISCOVERY_BACKEND == "openai_web_search":
        payload = OpenAIDiscoveryClient().discover_sites(prompt)
        candidates = [SiteCandidate(**row) for row in payload.get("candidates", [])]
        return prompt, candidates

    return prompt, _sample_candidates(prefs)
