from __future__ import annotations


class SampleAdapter:
    """Temporary adapter used while the real adapters are being built."""

    def fetch(self, query: dict) -> list[dict]:
        site = query["site"]

        if site["site_name"] == "Sample Apartments":
            return [
                {
                    "listing_id": "lst_001",
                    "site_name": "Sample Apartments",
                    "source_type": "aggregator",
                    "listing_url": "https://example.com/lst_001",
                    "title": "3BR furnished apartment near campus",
                    "description": "Laundry in building, WiFi included, AC.",
                    "price_text": "$1,250/mo per person",
                    "address_text": "4100 Walnut St, Philadelphia, PA 19104",
                    "amenities_text": ["Laundry", "WiFi", "Furnished", "Air Conditioning"],
                    "bedrooms": 3,
                    "bathrooms": 1,
                    "lease_term_months": 12,
                    "available_from": "2026-08-01",
                    "lat": 39.9529,
                    "lng": -75.2054,
                    "utilities_included": True,
                    "furnished": True,
                    "scraped_at": "2026-04-13T10:00:00Z",
                    "posted_at": "2026-04-12T09:00:00Z",
                }
            ]

        return []
