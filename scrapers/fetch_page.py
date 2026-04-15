from __future__ import annotations

import argparse
from pathlib import Path

from scrapers.browser import BrowserManager
from scrapers.snapshot import save_html, save_text


def fetch_url(url: str, output_dir: str) -> dict[str, str]:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    with BrowserManager() as manager:
        context, page = manager.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(1500)
            title = page.title()
            html = page.content()
            current_url = page.url
        finally:
            context.close()

    html_path = str(Path(output_dir) / "page.html")
    meta_path = str(Path(output_dir) / "meta.txt")
    save_html(html_path, html)
    save_text(meta_path, f"title={title}\nurl={current_url}\n")

    return {
        "title": title,
        "url": current_url,
        "html_path": html_path,
        "meta_path": meta_path,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch a page with Playwright and save HTML")
    parser.add_argument("--url", required=True, help="URL to fetch")
    parser.add_argument(
        "--output-dir",
        default="data/debug/fetch",
        help="Directory where artifacts should be written",
    )
    args = parser.parse_args()
    result = fetch_url(args.url, args.output_dir)
    print(result)
