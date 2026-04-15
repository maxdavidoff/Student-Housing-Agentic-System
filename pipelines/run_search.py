from __future__ import annotations

from adapters.sample_adapter import SampleAdapter
from agents.deduplicator import deduplicate_listings
from agents.listing_extractor import extract_from_sites
from agents.normalizer import normalize_listing
from agents.preference_parser import build_preference_profile
from agents.presenter import present_top_results
from agents.ranker import rank_listings
from agents.repair_agent import RepairManager
from agents.site_discovery import discover_sites
from utils.io import read_json, write_json, write_jsonl


def run_search(preferences_path: str, output_dir: str) -> None:
    prefs_payload = read_json(preferences_path)
    prefs = build_preference_profile(prefs_payload)

    site_plan = discover_sites(prefs.university.name, prefs.university.city)
    adapter = SampleAdapter()

    raw_rows = extract_from_sites(
        site_plan=site_plan,
        adapter=adapter,
        query=prefs.model_dump(mode="json"),
        dead_letter_dir=f"{output_dir}/dead_letter_queue",
    )

    repair_manager = RepairManager(
        repair_client=None,
        max_llm_repairs=20,
        min_confidence=0.72,
    )

    repaired_rows = []
    repair_audits = []
    for row in raw_rows:
        prepared_row, audit = repair_manager.prepare_row(row, prefs)
        repaired_rows.append(prepared_row)
        repair_audits.append(audit.model_dump(mode="json"))

    normalized = [normalize_listing(row, prefs) for row in repaired_rows]
    deduped = deduplicate_listings(normalized)
    top_results = rank_listings(deduped, prefs, top_k=5)

    write_json(f"{output_dir}/preferences.json", prefs.model_dump(mode="json"))
    write_json(f"{output_dir}/site_plan.json", site_plan)
    write_jsonl(f"{output_dir}/raw_listings.jsonl", raw_rows)
    write_jsonl(f"{output_dir}/repaired_rows.jsonl", repaired_rows)
    write_jsonl(f"{output_dir}/repair_audit.jsonl", repair_audits)
    write_jsonl(
        f"{output_dir}/normalized_listings.jsonl",
        [row.model_dump(mode="json") for row in normalized],
    )
    write_jsonl(
        f"{output_dir}/canonical_listings.jsonl",
        [row.model_dump(mode="json") for row in deduped],
    )
    write_json(
        f"{output_dir}/ranked_results.json",
        present_top_results(top_results),
    )
    write_json(
        f"{output_dir}/run_metadata.json",
        {
            "raw_count": len(raw_rows),
            "repair_rows_attempted": sum(1 for a in repair_audits if a["repair_decision"]["should_repair"]),
            "repair_rows_llm_applied": sum(1 for a in repair_audits if a["llm_repair_applied"]),
            "normalized_count": len(normalized),
            "canonical_count": len(deduped),
            "duplicates_removed": len(normalized) - len(deduped),
        },
    )


if __name__ == "__main__":
    run_search(
        preferences_path="data/searches/example/preferences.json",
        output_dir="data/searches/example",
    )
