from __future__ import annotations

from adapters.base import ListingAdapter
from schemas.site_candidate import VerifiedSiteCandidate
from schemas.site_probe import ProbeResult
from utils.failures import write_failure_artifact


REQUIRED_MINIMAL_FIELDS = ["listing_url", "site_name"]
OPTIONAL_SIGNAL_FIELDS = ["title", "price_text", "address_text", "description"]


def _minimal_schema_pass(row: dict, search_url: str | None = None) -> tuple[bool, list[str]]:
    notes: list[str] = []

    if not all(row.get(field) for field in REQUIRED_MINIMAL_FIELDS):
        notes.append("missing_listing_url_or_site_name")
        return False, notes

    if search_url and row.get("listing_url") == search_url:
        notes.append("listing_url_matches_search_url")
        return False, notes

    if not any(row.get(field) for field in OPTIONAL_SIGNAL_FIELDS):
        notes.append("missing_all_listing_signal_fields")
        return False, notes

    return True, ["sample_listing_validated"]


def probe_sites(
    candidates: list[VerifiedSiteCandidate],
    adapter: ListingAdapter,
    query: dict,
    dead_letter_dir: str,
    artifacts_dir: str,
    max_sites: int = 5,
) -> list[ProbeResult]:
    results: list[ProbeResult] = []

    for site in candidates[:max_sites]:
        if not site.verified or not site.worth_querying:
            results.append(
                ProbeResult(
                    site_name=site.site_name,
                    base_domain=site.base_domain,
                    search_url=site.verified_search_url,
                    probe_status="skipped",
                    notes=["site_not_verified_or_not_queryable"],
                )
            )
            continue

        try:
            rows = adapter.fetch(
                {
                    "site": {
                        **site.model_dump(),
                        "site_name": site.site_name,
                        "source_type": site.source_type,
                        "base_url": site.base_url,
                        "search_url_template": site.verified_search_url,
                        "candidate_listing_url": site.candidate_listing_url,
                        "max_pages": 1,
                    },
                    "query": query,
                    "artifacts_dir": artifacts_dir,
                    "probe_mode": True,
                }
            )
        except Exception as exc:
            artifact_path = write_failure_artifact(
                dead_letter_dir,
                {
                    "stage": "probe",
                    "site": site.model_dump(mode="json"),
                    "error": str(exc),
                },
            )
            results.append(
                ProbeResult(
                    site_name=site.site_name,
                    base_domain=site.base_domain,
                    search_url=site.verified_search_url,
                    probe_status="error",
                    blocked=True,
                    error_message=str(exc),
                    notes=["probe_exception"],
                    artifact_paths=[artifact_path],
                )
            )
            continue

        if not rows:
            results.append(
                ProbeResult(
                    site_name=site.site_name,
                    base_domain=site.base_domain,
                    search_url=site.verified_search_url,
                    probe_status="no_rows",
                    notes=["no_listing_rows_returned"],
                )
            )
            continue

        sample = rows[0]
        schema_pass, notes = _minimal_schema_pass(sample, search_url=site.verified_search_url)
        results.append(
            ProbeResult(
                site_name=site.site_name,
                base_domain=site.base_domain,
                search_url=site.verified_search_url,
                listing_url=sample.get("listing_url"),
                probe_status="ok" if schema_pass else "schema_failed",
                scrapeable=schema_pass,
                listing_count_seen=len(rows),
                minimum_schema_pass=schema_pass,
                notes=notes,
                sample_listing=sample,
                artifact_paths=[sample.get("raw_artifact_path")] if sample.get("raw_artifact_path") else [],
            )
        )

    return results
