from __future__ import annotations

from adapters.base import ListingAdapter
from utils.failures import write_failure_artifact


def extract_from_sites(
    site_plan: list[dict],
    adapter: ListingAdapter,
    query: dict,
    dead_letter_dir: str,
) -> list[dict]:
    """Fetch raw rows from all queryable sites and log failed fetches."""
    rows: list[dict] = []

    for site in site_plan:
        if not site.get("worth_querying", False):
            continue

        try:
            fetched = adapter.fetch({"site": site, "query": query})
        except Exception as exc:
            write_failure_artifact(
                dead_letter_dir,
                {"stage": "fetch", "site": site, "error": str(exc)},
            )
            continue

        for row in fetched:
            if not row.get("listing_id") or not row.get("listing_url"):
                write_failure_artifact(
                    dead_letter_dir,
                    {
                        "stage": "validate_row",
                        "site": site,
                        "error": "missing_listing_id_or_url",
                        "row": row,
                    },
                )
                continue
            rows.append(row)

    return rows
