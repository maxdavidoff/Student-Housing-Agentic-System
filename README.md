# housing-agent

The project scaffolding for the student housing search agent. 

Diagram: 

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

## Architecture

The intended pipeline is:

1. **Preference intake**  
   Parse user housing preferences into a validated `PreferenceProfile`.

2. **Site discovery**  
   Identify listing sources worth querying for a given university/city.

3. **Listing extraction**  
   Fetch raw listing rows from one or more adapters.

4. **Repair / normalization**  
   Apply cheap deterministic repairs, optionally run a narrow repair step, and normalize rows into canonical listing records.

5. **Deduplication**  
   Merge duplicate listings across multiple sources into one canonical record.

6. **Ranking and presentation**  
   Hard-filter, score, rank, and present top results.

7. **Evaluation**  
   Measure ranking quality, constraint violations, and freshness.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pipelines.run_search
python -m pipelines.run_eval
```

## Suggested Git workflow

```bash
git init
git add .
git commit -m "Initial project scaffold for housing agent"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

Create feature branches for each subsystem, for example:
- `feature/site-discovery`
- `feature/browser-adapter`
- `feature/repair-agent`
- `feature/deduplication`
- `feature/evals`

## Recommended order of implementation

1. Replace `SampleAdapter` with one real source adapter.
2. Save raw HTML / JSON artifacts into `data/` or a `failures/` directory.
3. Implement deterministic parsing for price, beds, baths, and address.
4. Add repair-agent routing for ambiguous fields only.
5. Add cross-source deduplication.
6. Expand ranking and eval coverage.

## Repo layout

```text
housing-agent/
  adapters/
  agents/
  data/
  llm_clients/
  pipelines/
  schemas/
  scoring/
  tests/
  utils/
```
