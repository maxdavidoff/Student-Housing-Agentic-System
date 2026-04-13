from __future__ import annotations

from typing import Optional

from schemas.repair import RepairDecision, RepairPatch


class NoopRepairClient:
    """Placeholder repair client. Returns no patch."""

    def repair_listing(self, decision: RepairDecision, raw_row: dict) -> Optional[RepairPatch]:
        return None
