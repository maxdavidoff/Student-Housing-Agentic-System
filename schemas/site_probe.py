from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ProbeResult(BaseModel):
    site_name: str
    base_domain: str
    search_url: Optional[str] = None
    listing_url: Optional[str] = None
    probe_status: str = "not_run"
    scrapeable: bool = False
    listing_count_seen: int = 0
    minimum_schema_pass: bool = False
    blocked: bool = False
    error_message: Optional[str] = None
    notes: list[str] = Field(default_factory=list)
    sample_listing: dict = Field(default_factory=dict)
    artifact_paths: list[str] = Field(default_factory=list)
