from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator


def _norm_token(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


class CampusAnchor(BaseModel):
    label: str
    lat: Optional[float] = None
    lng: Optional[float] = None


class UniversityContext(BaseModel):
    name: str
    city: Optional[str] = None
    state: Optional[str] = None
    campus_anchor: CampusAnchor


class Dates(BaseModel):
    move_in: date
    move_out: Optional[date] = None
    lease_term_months: Optional[int] = Field(default=None, ge=1, le=24)
    flexible_days: int = Field(default=0, ge=0, le=60)


class Budget(BaseModel):
    monthly_rent_max: float = Field(gt=0)
    utilities_included_required: bool = False
    one_time_fee_max: Optional[float] = Field(default=None, ge=0)


class Roommates(BaseModel):
    count: int = Field(default=0, ge=0, le=10)
    wants_private_bedroom: bool = False
    shared_bath_ok: bool = True


class LocationPreferences(BaseModel):
    max_distance_miles: Optional[float] = Field(default=None, ge=0)
    max_commute_minutes: Optional[int] = Field(default=None, ge=0)
    transport_modes: list[str] = Field(default_factory=lambda: ["walk"])

    @field_validator("transport_modes")
    @classmethod
    def normalize_modes(cls, value: list[str]) -> list[str]:
        if not value:
            return ["walk"]
        return sorted({_norm_token(v) for v in value})


class PreferenceBuckets(BaseModel):
    required: list[str] = Field(default_factory=list)
    preferred: list[str] = Field(default_factory=list)
    dealbreakers: list[str] = Field(default_factory=list)

    @field_validator("required", "preferred", "dealbreakers")
    @classmethod
    def normalize_lists(cls, value: list[str]) -> list[str]:
        return sorted({_norm_token(v) for v in value})


class RankingWeights(BaseModel):
    budget: float = 0.35
    distance: float = 0.25
    amenities: float = 0.20
    lease_fit: float = 0.15
    recency: float = 0.05

    def as_dict(self) -> dict[str, float]:
        return self.model_dump()


class PreferenceProfile(BaseModel):
    search_id: str
    university: UniversityContext
    dates: Dates
    budget: Budget
    roommates: Roommates
    location: LocationPreferences
    preferences: PreferenceBuckets
    ranking_weights: RankingWeights = Field(default_factory=RankingWeights)
