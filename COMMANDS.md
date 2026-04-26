# Commands

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install
cp .env.example .env
```

## Sample pipeline

```bash
python -m pipelines.run_discovery
python -m pipelines.run_search
python -m pipelines.run_eval
```

## Ohana login and probe

```bash
cp data/site_configs/seed_sites.example.json data/site_configs/seed_sites.json
python -m scripts.login_ohana
python -m pipelines.run_probe_ohana
```

If the probe fails, inspect:

```bash
find data/searches/example/artifacts/ohana -type f
cat data/searches/example/probe_results_ohana.jsonl
```

Then tune `OHANA_LISTING_LINK_SELECTOR` in `.env`, or temporarily add a known Ohana detail URL as `candidate_listing_url` in `data/site_configs/seed_sites.json`.

## Ohana full run

Edit `.env`:

```env
SCRAPER_BACKEND=ohana
DISCOVERY_BACKEND=sample
OHANA_REQUIRE_AUTH=true
```

Then run:

```bash
python -m pipelines.run_search
python -m pipelines.run_eval
```
