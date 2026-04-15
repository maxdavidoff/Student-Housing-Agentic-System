from __future__ import annotations

from bs4 import BeautifulSoup

from extractors.selectors import DEFAULT_DETAIL_SELECTORS


def _first_text(soup: BeautifulSoup, selectors: list[str]) -> str | None:
    for selector in selectors:
        el = soup.select_one(selector)
        if el:
            text = el.get_text(" ", strip=True)
            if text:
                return text
    return None


def _many_text(soup: BeautifulSoup, selectors: list[str]) -> list[str]:
    for selector in selectors:
        els = soup.select(selector)
        values = [el.get_text(" ", strip=True) for el in els if el.get_text(" ", strip=True)]
        if values:
            return values
    return []


def extract_detail_fields(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    return {
        "title": _first_text(soup, DEFAULT_DETAIL_SELECTORS["title"]),
        "price_text": _first_text(soup, DEFAULT_DETAIL_SELECTORS["price"]),
        "address_text": _first_text(soup, DEFAULT_DETAIL_SELECTORS["address"]),
        "description": _first_text(soup, DEFAULT_DETAIL_SELECTORS["description"]),
        "amenities_text": _many_text(soup, DEFAULT_DETAIL_SELECTORS["amenity_items"]),
    }
