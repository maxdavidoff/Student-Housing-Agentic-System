from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.2")

SCRAPER_BACKEND = os.getenv("SCRAPER_BACKEND", "sample").strip().lower()
SCRAPER_HEADLESS = os.getenv("SCRAPER_HEADLESS", "true").lower() == "true"
SCRAPER_TIMEOUT_MS = int(os.getenv("SCRAPER_TIMEOUT_MS", "30000"))
SCRAPER_SAVE_HTML = os.getenv("SCRAPER_SAVE_HTML", "true").lower() == "true"
SCRAPER_MAX_PAGES_PER_SITE = int(os.getenv("SCRAPER_MAX_PAGES_PER_SITE", "5"))
SCRAPER_SITE_CONFIG_PATH = os.getenv(
    "SCRAPER_SITE_CONFIG_PATH",
    "data/site_configs/playwright_sites.json",
)

DISCOVERY_BACKEND = os.getenv("DISCOVERY_BACKEND", "sample").strip().lower()
DISCOVERY_MODEL = os.getenv("DISCOVERY_MODEL", OPENAI_MODEL)
SEED_SITE_CONFIG_PATH = os.getenv(
    "SEED_SITE_CONFIG_PATH",
    "data/site_configs/seed_sites.json",
)

OHANA_BASE_URL = os.getenv("OHANA_BASE_URL", "https://liveohana.ai")
OHANA_LOGIN_URL = os.getenv("OHANA_LOGIN_URL", f"{OHANA_BASE_URL}/login")
OHANA_STORAGE_STATE_PATH = os.getenv(
    "OHANA_STORAGE_STATE_PATH",
    "auth/ohana_state.json",
)
OHANA_RESULTS_URL = os.getenv(
    "OHANA_RESULTS_URL",
    f"{OHANA_BASE_URL}/sublet",
)
OHANA_PROBE_URL = os.getenv(
    "OHANA_PROBE_URL",
    f"{OHANA_BASE_URL}/sublet",
)
OHANA_REQUIRE_AUTH = os.getenv("OHANA_REQUIRE_AUTH", "true").lower() == "true"
OHANA_LISTING_LINK_SELECTOR = os.getenv(
    "OHANA_LISTING_LINK_SELECTOR",
    "a[href*='/sublet/'], a[href*='/listing/'], a[href*='/room/']",
)
OHANA_MAX_LISTINGS = int(os.getenv("OHANA_MAX_LISTINGS", "10"))
