from __future__ import annotations

import hashlib
from pathlib import Path
from urllib.parse import quote_plus

from config.settings import SCRAPER_MAX_PAGES_PER_SITE, SCRAPER_SAVE_HTML
from parsers.parse_listing_detail import parse_listing_detail
from parsers.parse_listing_index import parse_listing_index
from scrapers.browser import BrowserManager
from scrapers.snapshot import save_html


class PlaywrightSiteAdapter:
    """
    Browser-backed starter adapter.

    This adapter is intentionally conservative:
    - it fetches one index page per site
    - extracts candidate detail URLs
    - visits a bounded number of detail pages
    - returns raw rows in the existing source-agnostic shape

    Next step: replace the placeholder search URL generation and selectors
    with site-specific logic for your target housing sites.
    """

    def fetch(self, query: dict) -> list[dict]:
        site = query["site"]
        prefs = query["query"]
        artifacts_dir = query.get("artifacts_dir", "data/debug/scraper_artifacts")

        base_url = site["base_url"]
        search_url = self._build_search_url(site, prefs)
        rows: list[dict] = []

        with BrowserManager() as manager:
            context = manager.new_context()
            index_page = context.new_page()
            index_page.goto(search_url, wait_until="domcontentloaded")
            index_page.wait_for_timeout(1500)
            index_html = index_page.content()

            if SCRAPER_SAVE_HTML:
                self._save_page_html(
                    artifacts_dir,
                    site_name=site["site_name"],
                    page_kind="index",
                    page_key="search",
                    html=index_html,
                )

            detail_urls = parse_listing_index(
                index_html,
                base_url=base_url,
                max_urls=min(site.get("max_pages", SCRAPER_MAX_PAGES_PER_SITE), SCRAPER_MAX_PAGES_PER_SITE),
            )

            for detail_url in detail_urls:
                detail_page = context.new_page()
                detail_page.goto(detail_url, wait_until="domcontentloaded")
                detail_page.wait_for_timeout(1500)
                detail_html = detail_page.content()
                parsed = parse_listing_detail(detail_html)

                listing_id = self._listing_id_from_url(detail_url)
                artifact_path = None
                if SCRAPER_SAVE_HTML:
                    artifact_path = self._save_page_html(
                        artifacts_dir,
                        site_name=site["site_name"],
                        page_kind="detail",
                        page_key=listing_id,
                        html=detail_html,
                    )

                rows.append(
                    {
                        "listing_id": listing_id,
                        "site_name": site["site_name"],
                        "source_type": site["source_type"],
                        "listing_url": detail_url,
                        "title": parsed.get("title"),
                        "description": parsed.get("description"),
                        "price_text": parsed.get("price_text"),
                        "address_text": parsed.get("address_text"),
                        "amenities_text": parsed.get("amenities_text", []),
                        "raw_artifact_path": artifact_path,
                        "parser_strategy": "playwright+bs4",
                    }
                )
                detail_page.close()

            context.close()

        return rows

    def _build_search_url(self, site: dict, prefs: dict) -> str:
        query_str = prefs["university"]["name"]
        template = site.get("search_url_template")
        if template:
            return template.format(query=quote_plus(query_str))
        return site["base_url"]

    def _listing_id_from_url(self, url: str) -> str:
        return hashlib.md5(url.encode("utf-8")).hexdigest()[:12]

    def _save_page_html(self, artifacts_dir: str, site_name: str, page_kind: str, page_key: str, html: str) -> str:
        file_path = Path(artifacts_dir) / site_name.lower().replace(" ", "_") / page_kind / f"{page_key}.html"
        save_html(str(file_path), html)
        return str(file_path)
