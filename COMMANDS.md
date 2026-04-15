# Commands to run

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install
cp .env.example .env
```

## Run the current sample pipeline

```bash
python -m pipelines.run_search
python -m pipelines.run_eval
```

## Test the new browser fetch layer

```bash
python -m pipelines.run_fetch_debug --url https://example.com --output-dir data/debug/example_fetch
```

## Turn on browser-backed scraping

```bash
cp data/site_configs/playwright_sites.example.json data/site_configs/playwright_sites.json
# edit .env and set: SCRAPER_BACKEND=playwright
# edit the site config file with a real target site
python -m pipelines.run_search
```

## Git branch workflow

```bash
git checkout -b feature/web-scraper-starter
git add .
git commit -m "Add browser-backed scraper starter"
git push -u origin feature/web-scraper-starter
```
