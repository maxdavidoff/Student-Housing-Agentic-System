from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class RepairDecision(BaseModel):
    listing_id: Optional[str] = None
    should_repair: bool = False
    priority: int = Field(default=0, ge=0, le=100)
    target_fields: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    evidence_text: str = ""


class RepairPatch(BaseModel):
    applied: bool = False
    target_fields: list[str] = Field(default_factory=list)
    field_values: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    notes: list[str] = Field(default_factory=list)
    model_name: Optional[str] = None


class RepairAudit(BaseModel):
    listing_id: Optional[str] = None
    cheap_repairs_applied: list[str] = Field(default_factory=list)
    repair_decision: RepairDecision = Field(default_factory=RepairDecision)
    llm_repair_attempted: bool = False
    llm_repair_applied: bool = False
    llm_repair_notes: list[str] = Field(default_factory=list)
