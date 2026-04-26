from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from config.settings import (
    OHANA_BASE_URL,
    OHANA_LISTING_LINK_SELECTOR,
    OHANA_MAX_LISTINGS,
    OHANA_REQUIRE_AUTH,
    OHANA_STORAGE_STATE_PATH,
    SCRAPER_MAX_PAGES_PER_SITE,
    SCRAPER_SAVE_HTML,
)
from scrapers.browser import BrowserManager
from scrapers.snapshot import save_html


class OhanaAdapter:
    """
    Authenticated browser adapter for Ohana.

    Intended workflow:
    1. Run `python -m scripts.login_ohana` once in headed mode and sign in manually.
    2. Reuse the saved Playwright storage state here.
    3. Probe one page first before enabling full search.

    This adapter intentionally fails closed: if it cannot find listing-detail links
    on a search/index page, it raises an error rather than pretending the index page
    is a valid listing. That prevents false-positive approvals during probing.
    """

    def fetch(self, query: dict) -> list[dict]:
        site = query["site"]
        artifacts_dir = query.get("artifacts_dir", "data/debug/ohana_artifacts")
        probe_mode = bool(query.get("probe_mode", False))
        target_url = self._target_url(site)
        max_pages = 1 if probe_mode else min(
            int(site.get("max_pages", OHANA_MAX_LISTINGS)),
            SCRAPER_MAX_PAGES_PER_SITE,
            OHANA_MAX_LISTINGS,
        )

        with BrowserManager() as manager:
            context = self._new_context(manager)
            page = context.new_page()
            page.goto(target_url, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

            html = page.content()
            title = page.title()
            if SCRAPER_SAVE_HTML:
                self._save_page_html(
                    artifacts_dir,
                    page_kind="index_or_direct",
                    page_key="ohana_probe" if probe_mode else "ohana_entry",
                    html=html,
                )

            if self._looks_blocked(title, html):
                raise RuntimeError(
                    "Ohana page appears blocked or unauthenticated; re-run login script and verify storage state."
                )

            rows: list[dict]
            if self._looks_like_listing_url(target_url):
                rows = [self._fetch_listing(context, target_url, artifacts_dir)]
            else:
                detail_urls = self._extract_listing_urls(page, html)
                if not detail_urls:
                    raise RuntimeError(
                        "Ohana index/search page loaded, but no listing-detail URLs were found. "
                        "Tune OHANA_LISTING_LINK_SELECTOR after inspecting the saved HTML artifact."
                    )
                rows = [self._fetch_listing(context, detail_url, artifacts_dir) for detail_url in detail_urls[:max_pages]]

            page.close()
            context.close()
            return rows

    def _target_url(self, site: dict) -> str:
        return (
            site.get("candidate_listing_url")
            or site.get("search_url_template")
            or site.get("candidate_search_url")
            or site.get("base_url")
            or OHANA_BASE_URL
        )

    def _new_context(self, manager: BrowserManager):
        storage_path = Path(OHANA_STORAGE_STATE_PATH)
        if storage_path.exists():
            return manager.browser.new_context(storage_state=str(storage_path))
        if OHANA_REQUIRE_AUTH:
            raise FileNotFoundError(
                f"Missing Ohana auth state at {OHANA_STORAGE_STATE_PATH}. Run `python -m scripts.login_ohana` first."
            )
        return manager.new_context()

    def _extract_listing_urls(self, page, html: str) -> list[str]:
        hrefs: list[str] = []

        try:
            page.wait_for_selector(OHANA_LISTING_LINK_SELECTOR, timeout=5000)
            for element in page.locator(OHANA_LISTING_LINK_SELECTOR).all()[: OHANA_MAX_LISTINGS * 3]:
                href = element.get_attribute("href")
                if href:
                    hrefs.append(urljoin(OHANA_BASE_URL, href))
        except PlaywrightTimeoutError:
            pass

        if not hrefs:
            soup = BeautifulSoup(html, "lxml")
            for anchor in soup.select(OHANA_LISTING_LINK_SELECTOR):
                href = anchor.get("href")
                if href:
                    hrefs.append(urljoin(OHANA_BASE_URL, href))

        return [url for url in self._dedupe_urls(hrefs) if self._looks_like_listing_url(url)]

    def _fetch_listing(self, context, detail_url: str, artifacts_dir: str) -> dict:
        page = context.new_page()
        page.goto(detail_url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        html = page.content()
        title = page.title() or self._first_text(html, ["h1", "title"])

        if self._looks_blocked(title or "", html):
            page.close()
            raise RuntimeError(f"Ohana listing page appears blocked or unauthenticated: {detail_url}")

        artifact_path = None
        if SCRAPER_SAVE_HTML:
            artifact_path = self._save_page_html(
                artifacts_dir,
                page_kind="detail",
                page_key=self._listing_id_from_url(detail_url),
                html=html,
            )

        description = self._joined_text(html, [
            "[data-testid='listing-description']",
            ".listing-description",
            ".description",
            "main",
        ])
        price_text = self._first_text(html, [
            "[data-testid='price']",
            ".price",
            "*[class*='price']",
        ])
        address_text = self._first_text(html, [
            "[data-testid='address']",
            ".address",
            "*[class*='address']",
            "*[class*='location']",
        ])
        amenities_text = self._list_text(html, [
            "[data-testid='amenities'] li",
            ".amenities li",
            "*[class*='amenit'] li",
        ])
        image_urls = self._image_urls(html)

        page.close()
        return {
            "listing_id": self._listing_id_from_url(detail_url),
            "site_name": "Ohana",
            "source_type": "sublet_marketplace",
            "listing_url": detail_url,
            "title": title,
            "description": description,
            "price_text": price_text,
            "address_text": address_text,
            "amenities_text": amenities_text,
            "raw_images": image_urls,
            "raw_artifact_path": artifact_path,
            "parser_strategy": "ohana_playwright_authenticated",
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }

    def _first_text(self, html: str, selectors: Iterable[str]) -> str | None:
        soup = BeautifulSoup(html, "lxml")
        for selector in selectors:
            node = soup.select_one(selector)
            if node:
                text = " ".join(node.get_text(" ", strip=True).split())
                if text:
                    return text
        return None

    def _joined_text(self, html: str, selectors: Iterable[str]) -> str | None:
        soup = BeautifulSoup(html, "lxml")
        for selector in selectors:
            nodes = soup.select(selector)
            if nodes:
                text = " ".join(" ".join(node.get_text(" ", strip=True).split()) for node in nodes)
                text = " ".join(text.split())
                if text:
                    return text
        return None

    def _list_text(self, html: str, selectors: Iterable[str]) -> list[str]:
        soup = BeautifulSoup(html, "lxml")
        for selector in selectors:
            nodes = soup.select(selector)
            if nodes:
                values = []
                for node in nodes:
                    text = " ".join(node.get_text(" ", strip=True).split())
                    if text:
                        values.append(text)
                if values:
                    return values
        return []

    def _image_urls(self, html: str) -> list[str]:
        soup = BeautifulSoup(html, "lxml")
        urls: list[str] = []
        for img in soup.select("img[src]")[:20]:
            src = img.get("src")
            if src and src.startswith("http"):
                urls.append(src)
        return urls

    def _dedupe_urls(self, hrefs: Iterable[str]) -> list[str]:
        seen = set()
        out = []
        for href in hrefs:
            if href.startswith("/"):
                href = urljoin(OHANA_BASE_URL, href)
            if not href.startswith("http"):
                continue
            if href in seen:
                continue
            seen.add(href)
            out.append(href)
        return out

    def _looks_like_listing_url(self, url: str) -> bool:
        path = urlparse(url).path.rstrip("/").lower()
        # Reject broad index/search pages.
        if path in {"", "/", "/sublet", "/sublets", "/search"}:
            return False
        return any(token in path for token in ["/sublet/", "/listing/", "/room/"])

    def _listing_id_from_url(self, url: str) -> str:
        return hashlib.md5(url.encode("utf-8")).hexdigest()[:12]

    def _save_page_html(self, artifacts_dir: str, page_kind: str, page_key: str, html: str) -> str:
        safe_key = page_key.replace("/", "_")
        file_path = Path(artifacts_dir) / "ohana" / page_kind / f"{safe_key}.html"
        save_html(str(file_path), html)
        return str(file_path)

    def _looks_blocked(self, title: str, html: str) -> bool:
        lowered = f"{title}\n{html[:4000]}".lower()
        hard_block_tokens = [
            "attention required",
            "cloudflare",
            "verify you are human",
            "checking your browser",
            "cf-browser-verification",
            "turnstile",
        ]
        auth_tokens = ["log in to continue", "sign in to continue", "please log in", "please sign in"]
        return any(token in lowered for token in hard_block_tokens + auth_tokens)
