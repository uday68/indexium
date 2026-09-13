# Indexium Backend — Search & Page Indexing Engine

Production-grade replication of Google page indexing and information retrieval subsystems.

## Architecture

```
                                    +------------------+
                                    |   Web Crawler    |
                                    | (httpx + robots) |
                                    +--------+---------+
                                             |
                                             v
                                    +------------------+
                                    |   HTML Parser    |
                                    |  & Normalizer    |
                                    +--------+---------+
                                             |
                                             v
+------------------+                +------------------+
|   Query Parser   |                |  Inverted Index  |
| (Boolean/Phrase) |                | (Postings/Trie)  |
+--------+---------+                +--------+---------+
         |                                   |
         +-----------------+-----------------+
                           |
                           v
                  +------------------+
                  | Ranking Engine   |
                  | - BM25 (default) |
                  | - TF-IDF         |
                  | - PageRank (Key) |
                  +--------+---------+
                           |
                           v
                  +------------------+
                  |  FastAPI Engine  |
                  | & Redis/LRU Cache|
                  +------------------+
```

## Key Modules

- **Crawler (`app/core/crawler/`)**: Asynchronous crawler with polite rate-limiting, robots.txt compliance, URL & content deduplication (SimHash), and link graph generation.
- **Parser & Tokenizer (`app/core/parser/`)**: HTML title/header/body extraction, Unicode normalization, stopword filtering, and query term snippet generator with `<b>` highlighting.
- **Inverted Index (`app/core/index/`)**: Term dictionary with positional posting lists (`doc_id`, `tf`, `positions`), document lengths, serialization, and distributed shard manager.
- **Ranking Engine (`app/core/ranking/`)**:
  - `bm25.py`: Okapi BM25 probabilistic ranking.
  - `tfidf.py`: Vector space TF-IDF baseline.
  - `explain.py`: Transparent ranking score decomposition.
  - **`pagerank.py`**: **THE KEY PART FOR USER IMPLEMENTATION** — contains the link graph and stubbed `compute()` method with clear instructions to implement power iteration or random walk.
- **Query Processing (`app/core/query/`)**: Boolean parser (`+term`, `-term`, `NOT`), exact phrase matcher (`"..."`), Levenshtein typo suggestion, and Trie-based autocomplete.
- **API (`app/api/v1/`)**: REST endpoints for `/search`, `/explain`, `/stats`, and `/admin`.

## Quick Start

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run tests
pytest tests/unit tests/integration -v

# Run benchmark
python scripts/benchmark.py

# Start API server
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

- `GET /api/v1/search?q=search+engine&ranker=bm25&limit=10&explain=true`
- `GET /api/v1/search/autocomplete?prefix=page`
- `GET /api/v1/explain?q=pagerank&doc_id=1`
- `GET /api/v1/stats`
- `GET /api/v1/stats/prometheus`
- `POST /api/v1/admin/index`
- `POST /api/v1/admin/crawl`
