# Vietnamese Legal Temporal RAG

A temporal-aware Retrieval-Augmented Generation framework for Vietnamese
labor-law question answering. Bachelor Thesis & Internship project (VGU,
CSE 2023), supervised by Dr. Tran Huu Tam.

The core idea: existing Vietnamese legal AI treats every retrieved law as
equally valid, so it often cites superseded laws. This project filters
retrieved laws by their **effective dates** so the model only ever sees laws
that were actually in force at the time the question is about.

---

## Project structure (what every folder is for)

```
vn-legal-rag/
├── src/
│   ├── scraper/        # collect labor-law documents from public gov sites
│   │   ├── base_scraper.py      # shared polite-fetch contract
│   │   ├── vbpl_scraper.py      # concrete scraper for vbpl.vn
│   │   └── document_parser.py   # clean text, extract dates + citations
│   │
│   ├── database/       # the ONLY place that touches PostgreSQL
│   │   ├── models.py            # data shapes (MOST IMPORTANT FILE)
│   │   ├── schema.sql           # PostgreSQL tables + pgvector
│   │   └── db.py                # insert + the core temporal query
│   │
│   ├── retrieval/      # Phase 1 baseline search (no time awareness)
│   │   ├── embedder.py          # PhoBERT text -> vectors
│   │   └── hybrid_retriever.py  # dense + BM25 + rank fusion
│   │
│   ├── temporal/       # Phase 2 -- the NOVEL contribution
│   │   ├── query_parser.py      # which date is the question about?
│   │   ├── temporal_filter.py   # keep only laws valid on that date  <- core
│   │   ├── citation_graph.py    # follow Circular -> Decree -> Law links
│   │   └── temporal_rag.py      # orchestrates the whole pipeline
│   │
│   ├── llm/            # uniform interface to every model tested
│   │   └── llm_client.py        # PhoGPT / GPT-4 / Claude / Gemini + prompt
│   │
│   ├── evaluation/     # measure everything for the thesis
│   │   ├── metrics.py           # standard + novel temporal metrics
│   │   └── runner.py            # run models x modes x questions grid
│   │
│   └── api/            # thin web API for demos
│       └── main.py              # POST /ask -> grounded answer
│
├── data/
│   ├── raw/            # scraped documents (gitignored)
│   ├── processed/      # cleaned + embedded data (gitignored)
│   └── questions/      # the evaluation benchmark questions
│
├── configs/
│   └── settings.py     # paths, model names, API keys (from env)
│
├── scripts/
│   └── run_pipeline.py # CLI: scrape / embed / evaluate
│
├── tests/              # unit tests (start with temporal_filter!)
├── notebooks/          # exploratory analysis
├── requirements.txt
└── .gitignore
```

---

## How the pieces connect (the data flow)

```
SCRAPER  ->  DATABASE  ->  RETRIEVAL  ->  TEMPORAL  ->  LLM  ->  answer
(collect)    (store +     (find         (filter by    (write)
             temporal      candidates)   date +
             metadata)                   citations)
```

For the thesis we run three MODES through the same pipeline and compare them:
1. `no_rag`        - model answers alone (worst, lots of hallucination)
2. `standard_rag`  - retrieval but no time filter (still cites old laws)
3. `temporal_rag`  - our system (only valid laws -> fewer hallucinations)

The whole contribution is showing mode 3 beats modes 1 and 2 on the
temporal metrics (Hallucination Rate, Temporal Consistency).

---

## Build order (suggested)

1. `database/models.py` + `database/schema.sql`  (define the shapes first)
2. `scraper/` (get real data into the DB)
3. `retrieval/` (Phase 1 baseline + report -> internship deliverable)
4. `temporal/` (Phase 2 novel work)
5. `llm/` + `evaluation/` (run experiments, get thesis numbers)
6. `api/` (demo for the defense)

---

## Setup (later, when implementing)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# create the database, then:
psql -d vn_legal -f src/database/schema.sql
```
