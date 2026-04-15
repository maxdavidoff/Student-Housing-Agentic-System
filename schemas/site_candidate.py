from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class SiteCandidate(BaseModel):
    site_name: str
    source_type: str
    base_domain: str
    base_url: str
    candidate_search_url: Optional[str] = None
    candidate_listing_url: Optional[str] = None
    relevance_reason: str = ""
    discovery_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    scrape_method_hint: str = "playwright"
    browser_required: bool = True
    worth_querying: bool = True


class VerifiedSiteCandidate(SiteCandidate):
    verified: bool = False
    verified_search_url: Optional[str] = None
    normalized_base_domain: Optional[str] = None
    verification_notes: list[str] = Field(default_factory=list)
    verification_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    structural_score: float = Field(default=0.0, ge=0.0, le=1.0)
    trust_score: float = Field(default=0.0, ge=0.0, le=1.0)
    overall_site_score: float = Field(default=0.0, ge=0.0, le=1.0)
