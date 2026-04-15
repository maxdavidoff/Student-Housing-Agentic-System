from __future__ import annotations

import argparse

from scrapers.fetch_page import fetch_url


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch a URL and save HTML artifacts")
    parser.add_argument("--url", required=True, help="URL to fetch")
    parser.add_argument(
        "--output-dir",
        default="data/debug/fetch",
        help="Directory to store the HTML snapshot",
    )
    args = parser.parse_args()
    print(fetch_url(args.url, args.output_dir))
