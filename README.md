# Student Housing Agentic System

A discovery-first housing search pipeline for student rentals and sublets.

## Current architecture

1. Parse and validate user housing preferences.
2. Discover candidate listing sites.
3. Verify URLs and rank candidate sites.
4. Probe each site with a one-listing validation pass.
5. Scrape approved sites.
6. Repair, normalize, deduplicate, and rank listings.

## Backends

- `sample`: local development backend for the full pipeline.
- `playwright`: generic browser-backed scraper starter.
- `ohana`: authenticated browser adapter for Ohana.

## Why discovery/probing exists

The system should not blindly scrape a hardcoded URL. It first builds candidate sites, verifies URLs, then probes one listing to confirm that the site can produce the minimum listing schema. If the probe cannot find a listing-detail URL or cannot extract a valid row, the site is not approved for a full scrape.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install
cp .env.example .env
```

## Sample workflow

```bash
python -m pipelines.run_discovery
python -m pipelines.run_search
python -m pipelines.run_eval
```

## Ohana workflow

1. Copy `data/site_configs/seed_sites.example.json` to `data/site_configs/seed_sites.json`.
2. Set these values in `.env`:

```env
SCRAPER_BACKEND=ohana
DISCOVERY_BACKEND=sample
OHANA_REQUIRE_AUTH=true
```

3. Capture a logged-in browser session:

```bash
python -m scripts.login_ohana
```

4. Probe Ohana before running the full pipeline:

```bash
python -m pipelines.run_probe_ohana
```

5. Inspect the probe output:

```bash
cat data/searches/example/probe_results_ohana.jsonl
```

If the probe fails with no listing-detail URLs, inspect the saved HTML under `data/searches/example/artifacts/ohana/` and tune `OHANA_LISTING_LINK_SELECTOR` in `.env`. You can also seed a known detail URL in `data/site_configs/seed_sites.json` as `candidate_listing_url` to test detail-page extraction directly.

6. Run the full pipeline only after the probe succeeds:

```bash
python -m pipelines.run_search
python -m pipelines.run_eval
```

## Notes

- `.env` and `auth/` are ignored by Git.
- The Ohana adapter fails closed to avoid approving the `/sublet` index page as if it were an individual listing.
- Tune selectors after inspecting saved HTML artifacts from your own authenticated session.
