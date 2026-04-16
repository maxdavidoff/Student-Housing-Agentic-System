# Student Housing Agentic System — Discovery-First Starter

This project now uses a **discovery → verify → probe → scrape** flow before attempting a full scrape.

## System Flow

```mermaid
flowchart LR
    A[User Preferences] --> B[Preference Parser]
    B --> C[Site Discovery]
    C --> D[Listing Extraction]
    D --> E[Repair Agent]
    E --> F[Normalization]
    F --> G[Deduplication]
    G --> H[Ranking]
    H --> I[Presentation Top 5]

    D --> DLQ[Dead Letter Queue]
    E --> RA[Repair Audit Logs]

    F --> N1[Normalized Listings]
    G --> N2[Canonical Listings]
    H --> N3[Ranked Results]

    subgraph Inputs
        A
    end

    subgraph Core_Agent_System
        B
        C
        D
        E
        F
        G
        H
        I
    end

    subgraph Persistence
        DLQ
        RA
        N1
        N2
        N3
    end

    subgraph Evaluation
        EV1[Extraction Accuracy]
        EV2[Ranking Quality]
        EV3[Freshness Metrics]
        EV4[Human Feedback]
    end

    N1 --> EV1
    N2 --> EV2
    N3 --> EV2
    N3 --> EV3
    I --> EV4
```

## New discovery-first structure

```mermaid
flowchart LR
    A[User Preferences] --> B[LLM Web Discovery]
    B --> C[URL Verification]
    C --> D[Site Ranking]
    D --> E[Probe One Listing]
    E --> F[Approved Sites]
    F --> G[Full Extraction]
    G --> H[Repair]
    H --> I[Normalization]
    I --> J[Deduplication]
    J --> K[Ranking Top 5]
```

## Rationale

It prevents the scraper from jumping straight into blocked or malformed sites.
Each site now has to:

1. be discovered
2. have a valid URL
3. pass a probe
4. return one minimally valid listing row

Only after that does the system use the site for full extraction.

## Main commands

```bash
python -m pipelines.run_discovery
python -m pipelines.run_search
python -m pipelines.run_eval
```

## Main outputs

- `site_candidates.json`
- `verified_sites.json`
- `probe_results.jsonl`
- `approved_sites.json`
- `raw_listings.jsonl`
- `normalized_listings.jsonl`
- `canonical_listings.jsonl`
- `ranked_results.json`

## Notes

- Default discovery backend is `sample` so the project runs without an API key.
- OpenAI web search is wired as a placeholder in `llm_clients/openai_discovery_client.py`.
- Full scraping should only target sites from `approved_sites.json`.
