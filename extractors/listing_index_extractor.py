from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from extractors.selectors import DEFAULT_INDEX_SELECTORS


def extract_listing_card_urls(html: str, base_url: str, max_urls: int = 25) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    urls: list[str] = []

    cards = []
    for selector in DEFAULT_INDEX_SELECTORS["listing_card"]:
        cards = soup.select(selector)
        if cards:
            break

    if not cards:
        cards = soup.find_all("a", href=True)

    for card in cards:
        anchors = card.select("a[href]") if hasattr(card, "select") else []
        if not anchors and getattr(card, "name", None) == "a" and card.get("href"):
            anchors = [card]
        for anchor in anchors:
            href = anchor.get("href")
            if not href:
                continue
            absolute = urljoin(base_url, href)
            if absolute not in urls:
                urls.append(absolute)
            if len(urls) >= max_urls:
                return urls

    return urls
