# Movie Matcher — Project Plan (living document)

Source of truth: `KHIZEX_Week6_MovieMatcher_Assignment.pdf` (Khizex AI Engineering
Internship, Week 6). This file is the requirements traceability matrix + binding
architectural decisions + milestone roadmap. Update the status column as each
milestone lands.

## Requirements → Architecture traceability

| PDF requirement (§) | Module | Status |
|---|---|---|
| Load/clean, missing-value handling (3.1) | `data_loader.py` | Done |
| Title normalization + dedup (3.1) | `data_loader.py` | Done |
| CountVectorizer genres / TfidfVectorizer descriptions (3.2) | `recommender.py` | Done |
| Cosine similarity, top-3, self-exclusion, tie-break (3.3) | `recommender.py` | Done (genre + description) |
| Fuzzy match + confirmation + not-found (3.3) | `matching.py` | Not started |
| Genre-vs-description comparison + written analysis (3.4) | `comparison.py` + `docs/results_writeup.md` | Not started |
| Modular structure, type hints, no bare `except` (3.5) | whole repo | Not started |
| Tests: top-3 count, self-exclusion, not-found, tie-break (3.5) | `tests/` | Not started |
| README (dataset, vectorization, tie-break, fuzzy match) | `README.md` | Not started |

## Dataset

`data/imdb_movie_data.csv` — 1000 movies, columns:
`Rank, Title, Genre, Description, Director, Actors, Year, Runtime (Minutes), Rating, Votes, Revenue (Millions), Metascore`.
Full provenance and pre-validation findings in `data/DATA_SOURCE_NOTES.md`. Key
findings that shape the design: zero missing Title/Genre/Description; zero exact
duplicate rows; one title collision ("The Host", Rank 240 vs Rank 633 — two
different movies, not a duplicate).

## Binding architectural decisions

1. **No blended/combined vector.** Keep genre (CountVectorizer) and description
   (TfidfVectorizer) as two independent, comparable pipelines — matches §3.4
   exactly and avoids an unreviewed combination rule.
2. **Tie-break, two-tier:** primary = alphabetical by normalized title; secondary
   (identical normalized titles, e.g. "The Host") = lowest `Rank`.
3. **Dedup:** keep first occurrence by `Rank` on exact duplicate rows, log count.
4. **Missing values:** drop rows missing `Title`/`Genre`/`Description` (documented
   choice — these fields can't be vectorized if absent).
5. **Fuzzy matching:** `difflib.get_close_matches` (stdlib), confirm match to user
   before returning recommendations.
6. **No `.env`/secrets** — no API keys or external calls in this project.
7. **Tests co-located per milestone**, not deferred to a single later pass.

## Milestone roadmap

1. Data loader — load, clean, normalize, dedup, exact-title + collision lookup
2. Genre pipeline — CountVectorizer + shared `top_k_similar()` core
3. Description pipeline — TfidfVectorizer, reuse the same core
4. Fuzzy matching + not-found handling + CLI stub
5. Comparison module — 3 sample queries, genre vs. description, side by side
6. Full test sweep + gap-check against §3.5 / self-check checklist
7. README, results write-up, final QA pass

## Repo structure (target)

```
movie_matcher/
├── data/
│   ├── imdb_movie_data.csv
│   └── DATA_SOURCE_NOTES.md
├── movie_matcher/
│   ├── __init__.py
│   ├── data_loader.py     # load/clean/normalize/dedup, pandas at the edges only
│   ├── recommender.py     # vectorization + cosine similarity, pure functions, no I/O
│   ├── matching.py        # fuzzy title matching, not-found handling
│   ├── comparison.py      # §3.4 side-by-side comparison + analysis
│   └── cli.py             # terminal loop / argparse entry point
├── tests/
│   ├── test_data_loader.py
│   ├── test_recommender.py
│   └── test_matching.py
├── docs/
│   └── results_writeup.md
├── README.md
└── requirements.txt
```

## Milestone log

- **Milestone 1 (data_loader.py) — COMPLETE.** Data loading and cleaning
  pipeline: CSV ingestion with required-column validation, missing-value
  handling (drop with documented rationale), title normalization,
  exact-duplicate removal, and exact-title lookup with deterministic
  lowest-Rank collision resolution. 8 unit tests, all logic reviewed.
  Files: `movie_matcher/data_loader.py`, `tests/test_data_loader.py`.
- **Milestone 2 (recommender.py — genre pipeline) — COMPLETE.** Genre-based
  similarity: CountVectorizer with a comma-splitting tokenizer (preserves
  compound genre labels like "Sci-Fi"), an algorithm-agnostic top_k_similar
  ranking core (self-exclusion, descending similarity, alphabetical
  tie-break) designed for reuse by the description pipeline, and
  recommend_by_genre orchestration reusing Milestone 1's title lookup.
  7 unit tests including an end-to-end case with hand-verified cosine
  similarity values. Files: `movie_matcher/recommender.py`,
  `tests/test_recommender.py`.
- **Milestone 3 (recommender.py — description pipeline) — COMPLETE.**
  TF-IDF-based similarity: TfidfVectorizer with stop_words='english' and
  the default tokenizer (deliberate contrast with genre's custom
  comma-splitting tokenizer, documented inline), recommend_by_description
  reusing top_k_similar unchanged. 5 new unit tests including a
  hand-verified near-duplicate-description ranking case and an
  all-stop-words edge case. Files: `movie_matcher/recommender.py`
  (additive only), `tests/test_recommender.py` (additive only).
- **Milestone 4 (matching.py — fuzzy matching + CLI stub):** not started.
