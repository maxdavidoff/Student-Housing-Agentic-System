from __future__ import annotations

from typing import Protocol


class ListingAdapter(Protocol):
    def fetch(self, query: dict) -> list[dict]:
        """
        Return raw listing dictionaries in a source-agnostic shape.
        The query payload can include:
        - site metadata
        - normalized preference query
        - artifacts_dir for snapshots
        """
        ...
