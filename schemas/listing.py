from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, field_validator


def _norm_token(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


class SourceInfo(BaseModel):
    site_name: str
    source_type: str
    listing_url: str
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    posted_at: Optional[datetime] = None
    parser_strategy: str = "rule_based"
    raw_artifact_path: Optional[str] = None


class RawListing(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    raw_price_text: Optional[str] = None
    raw_address_text: Optional[str] = None
    raw_amenities_text: list[str] = Field(default_factory=list)
    raw_images: list[str] = Field(default_factory=list)


class Address(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class Pricing(BaseModel):
    monthly_rent: Optional[float] = Field(default=None, ge=0)
    rent_frequency: str = "monthly"
    per_person: bool = False
    utilities_included: Optional[bool] = None
    fees_estimated_total: Optional[float] = Field(default=None, ge=0)
    deposit_estimated: Optional[float] = Field(default=None, ge=0)
    price_is_estimated: bool = False


class UnitInfo(BaseModel):
    bedrooms: Optional[float] = Field(default=None, ge=0)
    bathrooms: Optional[float] = Field(default=None, ge=0)
    furnished: Optional[bool] = None
    lease_term_months: Optional[int] = Field(default=None, ge=1, le=24)
    available_from: Optional[str] = None


class LocationStats(BaseModel):
    distance_miles_to_campus: Optional[float] = Field(default=None, ge=0)
    walk_minutes_to_campus: Optional[int] = Field(default=None, ge=0)
    transit_minutes_to_campus: Optional[int] = Field(default=None, ge=0)


class StudentFit(BaseModel):
    near_student_area: Optional[bool] = None
    private_bedroom_possible: Optional[bool] = None
    roommate_friendly: Optional[bool] = None


class FreshnessInfo(BaseModel):
    latest_scraped_at: Optional[datetime] = None
    latest_posted_at: Optional[datetime] = None
    age_days: Optional[float] = None
    low_availability_warning: bool = False


class NormalizedListing(BaseModel):
    address: Address = Field(default_factory=Address)
    pricing: Pricing = Field(default_factory=Pricing)
    unit: UnitInfo = Field(default_factory=UnitInfo)
    location: LocationStats = Field(default_factory=LocationStats)
    amenities: dict[str, bool] = Field(default_factory=dict)
    student_fit: StudentFit = Field(default_factory=StudentFit)

    @field_validator("amenities")
    @classmethod
    def normalize_amenity_keys(cls, value: dict[str, bool]) -> dict[str, bool]:
        return {_norm_token(k): bool(v) for k, v in value.items()}


class QualityInfo(BaseModel):
    field_confidence: dict[str, float] = Field(default_factory=dict)
    missing_fields: list[str] = Field(default_factory=list)
    parse_warnings: list[str] = Field(default_factory=list)
    repair_notes: list[str] = Field(default_factory=list)
    dedupe_notes: list[str] = Field(default_factory=list)
    confidence_multiplier: float = 1.0


class RankingInfo(BaseModel):
    hard_filter_pass: bool = False
    component_scores: dict[str, float] = Field(default_factory=dict)
    raw_weighted_score: float = 0.0
    final_score: float = 0.0
    explanation: Optional[str] = None


class ListingRecord(BaseModel):
    listing_id: str
    canonical_id: Optional[str] = None
    search_id: str
    sources: list[SourceInfo] = Field(default_factory=list)
    raw: RawListing
    normalized: NormalizedListing = Field(default_factory=NormalizedListing)
    freshness: FreshnessInfo = Field(default_factory=FreshnessInfo)
    quality: QualityInfo = Field(default_factory=QualityInfo)
    ranking: RankingInfo = Field(default_factory=RankingInfo)
