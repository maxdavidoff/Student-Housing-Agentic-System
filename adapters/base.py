from __future__ import annotations

from typing import Protocol


class ListingAdapter(Protocol):
    def fetch(self, query: dict) -> list[dict]:
        """Fetch raw listing rows from a source."""
        ...
