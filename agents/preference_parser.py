from __future__ import annotations

from schemas.preferences import (
    Budget,
    CampusAnchor,
    Dates,
    LocationPreferences,
    PreferenceBuckets,
    PreferenceProfile,
    Roommates,
    UniversityContext,
)


def build_preference_profile(payload: dict) -> PreferenceProfile:
    """Convert a partially structured input payload into a validated preference object."""
    university = UniversityContext(
        name=payload["university"]["name"],
        city=payload["university"].get("city"),
        state=payload["university"].get("state"),
        campus_anchor=CampusAnchor(**payload["university"]["campus_anchor"]),
    )

    return PreferenceProfile(
        search_id=payload["search_id"],
        university=university,
        dates=Dates(**payload["dates"]),
        budget=Budget(**payload["budget"]),
        roommates=Roommates(**payload.get("roommates", {})),
        location=LocationPreferences(**payload.get("location", {})),
        preferences=PreferenceBuckets(**payload.get("preferences", {})),
        ranking_weights=payload.get("ranking_weights", {}),
    )
