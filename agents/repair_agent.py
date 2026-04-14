from __future__ import annotations

from typing import Optional, Protocol

from schemas.preferences import PreferenceProfile
from schemas.repair import RepairAudit, RepairDecision, RepairPatch


class StructuredRepairClient(Protocol):
    def repair_listing(self, decision: RepairDecision, raw_row: dict) -> Optional[RepairPatch]:
        """
        Return a structured patch for only the fields in decision.target_fields.
        Return None if no safe patch can be produced.
        """
        ...


def _text_blob(row: dict) -> str:
    return " ".join(
        [
            row.get("title", "") or "",
            row.get("description", "") or "",
            row.get("price_text", "") or "",
            row.get("address_text", "") or "",
            " ".join(row.get("amenities_text", []) or []),
        ]
    ).lower()


def apply_cheap_repairs(raw_row: dict) -> tuple[dict, list[str]]:
    row = dict(raw_row)
    notes: list[str] = []
    blob = _text_blob(row)

    amenity_overrides = dict(row.get("amenity_overrides", {}))

    if "hookups only" in blob:
        amenity_overrides["laundry"] = False
        amenity_overrides["laundry_hookups_only"] = True
        notes.append("cheap:laundry_hookups_only")

    if "basement" in blob:
        amenity_overrides["basement_unit"] = True
        notes.append("cheap:basement_unit_true")

    if "no kitchen" in blob or "kitchenette only" in blob:
        amenity_overrides["no_kitchen"] = True
        notes.append("cheap:no_kitchen_true")

    title = (row.get("title") or "").lower()
    if "studio" in title and row.get("bedrooms") is None:
        row["bedrooms"] = 0
        notes.append("cheap:studio_bedrooms_0")

    price_text = (row.get("price_text") or "").lower()
    if "starting at" in price_text or "from $" in price_text or "prices start" in price_text:
        row["price_is_estimated"] = True
        notes.append("cheap:price_estimated")

    address_text = (row.get("address_text") or "").strip().lower()
    if not address_text or address_text in {"near campus", "campus area", "close to campus"}:
        row["address_is_fuzzy"] = True
        notes.append("cheap:fuzzy_address")

    row["amenity_overrides"] = amenity_overrides
    return row, notes


def _build_evidence_text(row: dict, max_chars: int = 1200) -> str:
    pieces = [
        f"TITLE: {row.get('title', '')}",
        f"PRICE: {row.get('price_text', '')}",
        f"ADDRESS: {row.get('address_text', '')}",
        f"AMENITIES: {', '.join(row.get('amenities_text', []) or [])}",
        f"DESCRIPTION: {row.get('description', '')}",
    ]
    text = "\n".join(pieces).strip()
    return text[:max_chars]


def build_repair_decision(row: dict, prefs: PreferenceProfile) -> RepairDecision:
    reasons: list[str] = []
    target_fields: list[str] = []

    if row.get("price_is_estimated") and row.get("price_text"):
        reasons.append("estimated_price")
        target_fields.append("price_text")

    if row.get("address_is_fuzzy"):
        reasons.append("fuzzy_address")
        target_fields.append("address_text")

    if row.get("bedrooms") is None:
        reasons.append("missing_bedrooms")
        target_fields.append("bedrooms")

    if row.get("bathrooms") is None:
        reasons.append("missing_bathrooms")
        target_fields.append("bathrooms")

    if prefs.preferences.required:
        blob = _text_blob(row)
        if "laundry" in prefs.preferences.required and (
            "hookups only" in blob or "shared laundry next door" in blob
        ):
            reasons.append("ambiguous_laundry")
            target_fields.append("amenity_overrides")

    deduped_targets: list[str] = []
    for field in target_fields:
        if field not in deduped_targets:
            deduped_targets.append(field)

    deduped_targets = deduped_targets[:3]

    priority = 0
    if "fuzzy_address" in reasons:
        priority += 40
    if "estimated_price" in reasons:
        priority += 30
    if "missing_bedrooms" in reasons:
        priority += 20
    if "missing_bathrooms" in reasons:
        priority += 10

    return RepairDecision(
        listing_id=row.get("listing_id"),
        should_repair=bool(deduped_targets),
        priority=min(priority, 100),
        target_fields=deduped_targets,
        reasons=reasons,
        evidence_text=_build_evidence_text(row),
    )


def apply_repair_patch(row: dict, patch: Optional[RepairPatch], min_confidence: float = 0.72) -> tuple[dict, list[str], bool]:
    if patch is None or not patch.applied or patch.confidence < min_confidence:
        return row, [], False

    updated = dict(row)
    notes: list[str] = []

    for field, value in patch.field_values.items():
        if field in {"price_text", "address_text", "bedrooms", "bathrooms"}:
            updated[field] = value
            notes.append(f"llm:{field}")
        elif field == "amenity_overrides" and isinstance(value, dict):
            merged = dict(updated.get("amenity_overrides", {}))
            merged.update(value)
            updated["amenity_overrides"] = merged
            notes.append("llm:amenity_overrides")

    return updated, notes + list(patch.notes), True


class RepairManager:
    def __init__(
        self,
        repair_client: Optional[StructuredRepairClient] = None,
        max_llm_repairs: int = 25,
        min_confidence: float = 0.72,
    ) -> None:
        self.repair_client = repair_client
        self.max_llm_repairs = max_llm_repairs
        self.min_confidence = min_confidence
        self.repairs_used = 0

    def prepare_row(self, raw_row: dict, prefs: PreferenceProfile) -> tuple[dict, RepairAudit]:
        row, cheap_notes = apply_cheap_repairs(raw_row)
        decision = build_repair_decision(row, prefs)

        audit = RepairAudit(
            listing_id=row.get("listing_id"),
            cheap_repairs_applied=cheap_notes,
            repair_decision=decision,
        )

        llm_notes: list[str] = []
        llm_applied = False

        if (
            self.repair_client is not None
            and decision.should_repair
            and self.repairs_used < self.max_llm_repairs
        ):
            audit.llm_repair_attempted = True
            patch = self.repair_client.repair_listing(decision, row)
            row, llm_notes, llm_applied = apply_repair_patch(
                row,
                patch,
                min_confidence=self.min_confidence,
            )
            if llm_applied:
                self.repairs_used += 1

        combined_notes = cheap_notes + llm_notes
        row["repair_notes"] = combined_notes

        audit.llm_repair_applied = llm_applied
        audit.llm_repair_notes = llm_notes
        return row, audit
