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
