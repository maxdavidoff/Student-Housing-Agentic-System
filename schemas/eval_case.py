from __future__ import annotations

from pydantic import BaseModel, Field

from schemas.preferences import PreferenceProfile


class EvalGold(BaseModel):
    acceptable_ids: list[str] = Field(default_factory=list)
    top_5_ordered_ids: list[str] = Field(default_factory=list)
    must_exclude_ids: list[str] = Field(default_factory=list)
    rationales: dict[str, str] = Field(default_factory=dict)


class EvalCase(BaseModel):
    eval_case_id: str
    user_preferences: PreferenceProfile
    candidate_listing_ids: list[str]
    gold: EvalGold
