# Commands

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install
cp .env.example .env
```

## Run the discovery-first pipeline

```bash
python -m pipelines.run_discovery
python -m pipelines.run_search
python -m pipelines.run_eval
```

## Test the browser fetch layer only

```bash
python -m pipelines.run_fetch_debug --url https://example.com --output-dir data/debug/example_fetch
```

## Turn on OpenAI web discovery later

Edit `.env`:

```env
DISCOVERY_BACKEND=openai_web_search
OPENAI_API_KEY=your_real_key_here
OPENAI_MODEL=gpt-5.2
DISCOVERY_MODEL=gpt-5.2
```

Then rerun:

```bash
python -m pipelines.run_discovery
python -m pipelines.run_search
```
