from __future__ import annotations

import math

from schemas.eval_case import EvalCase
from utils.io import read_json


def recall_at_k(predicted_ids: list[str], gold_ids: list[str], k: int = 5) -> float:
    topk = predicted_ids[:k]
    if not gold_ids:
        return 1.0
    hits = sum(1 for item in gold_ids if item in topk)
    return hits / len(gold_ids)


def ndcg_at_k(predicted_ids: list[str], gold_ranked_ids: list[str], k: int = 5) -> float:
    gold_relevance = {listing_id: (len(gold_ranked_ids) - idx) for idx, listing_id in enumerate(gold_ranked_ids)}
    dcg = 0.0
    for i, pred in enumerate(predicted_ids[:k], start=1):
        rel = gold_relevance.get(pred, 0)
        dcg += (2 ** rel - 1) / math.log2(i + 1)

    ideal = 0.0
    for i, gold_id in enumerate(gold_ranked_ids[:k], start=1):
        rel = gold_relevance.get(gold_id, 0)
        ideal += (2 ** rel - 1) / math.log2(i + 1)

    if ideal == 0:
        return 1.0
    return dcg / ideal


def constraint_violation_rate(predicted_ids: list[str], must_exclude_ids: list[str], k: int = 5) -> float:
    topk = predicted_ids[:k]
    if not topk:
        return 0.0
    violations = sum(1 for item in topk if item in set(must_exclude_ids))
    return violations / len(topk)


def freshness_at_k(ranked: list[dict], max_age_days: float = 3.0, k: int = 5) -> float:
    topk = ranked[:k]
    if not topk:
        return 1.0
    fresh = 0
    for row in topk:
        age_days = row.get("age_days")
        if age_days is not None and age_days <= max_age_days:
            fresh += 1
    return fresh / len(topk)


def evaluate_case(eval_case_path: str, ranked_results_path: str) -> dict:
    eval_case = EvalCase(**read_json(eval_case_path))
    ranked = read_json(ranked_results_path)
    predicted_ids = [row["listing_id"] for row in ranked]

    fresh_rate = freshness_at_k(ranked, max_age_days=3.0, k=5)
    stale_warning = fresh_rate < 0.5

    return {
        "eval_case_id": eval_case.eval_case_id,
        "recall_at_5": round(recall_at_k(predicted_ids, eval_case.gold.acceptable_ids, 5), 4),
        "ndcg_at_5": round(ndcg_at_k(predicted_ids, eval_case.gold.top_5_ordered_ids, 5), 4),
        "constraint_violation_rate": round(
            constraint_violation_rate(predicted_ids, eval_case.gold.must_exclude_ids, 5), 4
        ),
        "freshness_at_5": round(fresh_rate, 4),
        "stale_results_warning": stale_warning,
    }


if __name__ == "__main__":
    summary = evaluate_case(
        eval_case_path="data/eval/eval_001.json",
        ranked_results_path="data/searches/example/ranked_results.json",
    )
    print(summary)
