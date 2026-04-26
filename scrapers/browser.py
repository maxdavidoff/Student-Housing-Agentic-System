from __future__ import annotations

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from config.settings import SCRAPER_HEADLESS, SCRAPER_TIMEOUT_MS


class BrowserManager:
    def __init__(self, headless: bool | None = None) -> None:
        self._pw: Playwright | None = None
        self.browser: Browser | None = None
        self.headless = SCRAPER_HEADLESS if headless is None else headless

    def __enter__(self) -> "BrowserManager":
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(headless=self.headless)
        return self

    def new_context(self, **kwargs) -> BrowserContext:
        if self.browser is None:
            raise RuntimeError("Browser is not initialized")
        context = self.browser.new_context(**kwargs)
        context.set_default_timeout(SCRAPER_TIMEOUT_MS)
        return context

    def new_page(self) -> tuple[BrowserContext, Page]:
        context = self.new_context()
        page = context.new_page()
        page.set_default_timeout(SCRAPER_TIMEOUT_MS)
        return context, page

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.browser is not None:
            self.browser.close()
        if self._pw is not None:
            self._pw.stop()
