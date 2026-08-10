# Movie Matcher — Project Plan (Living Document)

**Source of truth:** `KHIZEX_Week6_MovieMatcher_Assignment.pdf`
(Khizex AI Engineering Internship, Week 6)

This document is the project's requirements traceability matrix, binding
architectural decisions, milestone roadmap, and completion log.

All planned implementation milestones and assignment requirements have now
been completed and verified.

---

## Requirements → Architecture Traceability

| PDF requirement (§)                                                     | Module / File                                             | Status   |
| ----------------------------------------------------------------------- | --------------------------------------------------------- | -------- |
| Load/clean, missing-value handling (3.1)                                | `movie_matcher/data_loader.py`                            | **Done** |
| Title normalization + deduplication (3.1)                               | `movie_matcher/data_loader.py`                            | **Done** |
| CountVectorizer genres / TfidfVectorizer descriptions (3.2)             | `movie_matcher/recommender.py`                            | **Done** |
| Cosine similarity, top-3, self-exclusion, deterministic tie-break (3.3) | `movie_matcher/recommender.py`                            | **Done** |
| Fuzzy match + confirmation + not-found handling (3.3)                   | `movie_matcher/matching.py` + `movie_matcher/cli.py`      | **Done** |
| Genre-vs-description comparison + written analysis (3.4)                | `movie_matcher/comparison.py` + `docs/results_writeup.md` | **Done** |
| Modular structure, type hints, no bare `except` (3.5)                   | Whole repository                                          | **Done** |
| Tests covering required behaviors (3.5)                                 | `tests/`                                                  | **Done** |
| README documenting dataset, vectorization, tie-break, fuzzy matching    | `README.md`                                               | **Done** |
| User-facing Streamlit interface                                         | `app.py` + `assets/`                                      | **Done** |
| Streamlit dependency                                                    | `requirements.txt`                                        | **Done** |

---

## Dataset

`data/imdb_movie_data.csv` — 1,000 movies with the following columns:

`Rank, Title, Genre, Description, Director, Actors, Year, Runtime (Minutes), Rating, Votes, Revenue (Millions), Metascore`

Full provenance and pre-validation findings are documented in:

`data/DATA_SOURCE_NOTES.md`

Key findings that shape the design:

* Zero missing `Title`, `Genre`, or `Description` values.
* Zero exact duplicate rows.
* One title collision: `"The Host"` appears at Rank 240 and Rank 633.
* The two `"The Host"` records represent different movies and must not be
  incorrectly treated as duplicate records.

---

## Binding Architectural Decisions

### 1. Independent recommendation pipelines

No blended or combined vector is used.

Genre and description similarity remain two independent pipelines:

* `CountVectorizer` for genres
* `TfidfVectorizer` for descriptions

This preserves the direct comparison required by §3.4 and avoids introducing
an unreviewed weighting or combination rule.

### 2. Deterministic tie-breaking

Recommendations are ordered by:

1. Descending cosine similarity.
2. Alphabetical order of normalized title when similarity scores are equal.
3. Lowest `Rank` when normalized titles are identical.

This makes recommendation results reproducible.

### 3. Deduplication

Exact duplicate rows are removed while preserving the first occurrence by
`Rank`.

The `"The Host"` title collision is not treated as an exact duplicate because
the records represent different movies.

### 4. Missing values

Rows missing `Title`, `Genre`, or `Description` are dropped.

These fields are required by the corresponding recommendation pipelines, so
fabricating replacement values could introduce misleading signals.

### 5. Fuzzy matching

`difflib.get_close_matches` from the Python standard library is used for
approximate title matching.

A fuzzy match requires explicit user confirmation before recommendations are
generated.

### 6. No secrets or external API calls

The project does not require API keys, credentials, or external service
calls.

No secrets are hardcoded into the repository.

### 7. Modular architecture

The project separates:

* Data loading and cleaning
* Recommendation/vectorization logic
* Title matching
* Genre/description comparison
* CLI interaction
* Streamlit presentation

The Streamlit frontend uses the existing recommendation pipeline rather than
duplicating recommendation logic inside `app.py`.

### 8. Testing and verification

Test files are maintained alongside the implementation and cover the required
behaviors.

The completed application was also manually verified through the running
Streamlit interface in a web browser.

Browser verification covered the major user-facing behaviors, including
recommendation generation, fuzzy matching, confirmation, not-found handling,
self-exclusion, top-3 results, comparison behavior, and poster display.

---

## Milestone Roadmap

1. **Data loader** — load, clean, normalize, deduplicate, and deterministic
   title lookup — **COMPLETE**
2. **Genre pipeline** — CountVectorizer + shared `top_k_similar()` ranking core
   — **COMPLETE**
3. **Description pipeline** — TfidfVectorizer using the shared ranking core —
   **COMPLETE**
4. **Fuzzy matching + not-found handling + CLI** — **COMPLETE**
5. **Comparison module** — compare genre and description recommendations for
   three sample queries — **COMPLETE**
6. **Testing, requirements gap-check, and code-quality review** — **COMPLETE**
7. **README, results write-up, Streamlit frontend, final QA, and repository
   preparation** — **COMPLETE**

---

## Repository Structure

```text
movie_matcher/
├── data/
│   ├── imdb_movie_data.csv
│   └── DATA_SOURCE_NOTES.md
├── movie_matcher/
│   ├── __init__.py
│   ├── data_loader.py       # load/clean/normalize/dedup + title lookup
│   ├── recommender.py       # vectorization + cosine similarity
│   ├── matching.py          # fuzzy title matching + not-found handling
│   ├── comparison.py        # §3.4 comparison and analysis
│   └── cli.py               # terminal interface
├── tests/
│   ├── test_data_loader.py
│   ├── test_recommender.py
│   ├── test_matching.py
│   ├── test_comparison.py
│   └── test_integration.py
├── docs/
│   └── results_writeup.md
├── assets/
│   └── ...                  # movie poster assets used by Streamlit
├── app.py                   # Streamlit web interface
├── README.md
├── project plan.md
├── pytest.ini
└── requirements.txt
```

---

# Milestone Log

## Milestone 1 — Data Loader — COMPLETE

Implemented the data loading and cleaning pipeline with:

* CSV ingestion
* Required-column validation
* Missing-value handling
* Empty-field handling
* Title normalization
* Exact duplicate removal
* Deterministic title lookup
* Lowest-`Rank` resolution for identical normalized titles

Files:

* `movie_matcher/data_loader.py`
* `tests/test_data_loader.py`

---

## Milestone 2 — Genre Recommendation Pipeline — COMPLETE

Implemented genre-based movie similarity using:

* `CountVectorizer`
* A comma-splitting tokenizer to preserve compound genre labels such as
  `"Sci-Fi"`
* Cosine similarity
* Shared `top_k_similar()` ranking logic
* Self-exclusion
* Deterministic tie-breaking
* Title lookup integration

Files:

* `movie_matcher/recommender.py`
* `tests/test_recommender.py`

---

## Milestone 3 — Description Recommendation Pipeline — COMPLETE

Implemented description-based similarity using:

* `TfidfVectorizer`
* English stop-word removal
* Default text tokenization
* The shared `top_k_similar()` ranking core

The description pipeline remains independent from the genre pipeline so that
the two approaches can be compared directly.

Files:

* `movie_matcher/recommender.py`
* `tests/test_recommender.py`

---

## Milestone 4 — Matching + CLI — COMPLETE

Implemented:

* Exact title matching
* Fuzzy title matching using `difflib`
* Deduplicated fuzzy-match candidates
* Explicit fuzzy-match confirmation
* Predictable exact/fuzzy/not-found status handling
* CLI interaction

The implementation correctly handles the `"The Host"` title collision.

Files:

* `movie_matcher/matching.py`
* `movie_matcher/cli.py`
* `tests/test_matching.py`

---

## Milestone 5 — Genre vs. Description Comparison — COMPLETE

Implemented a comparison layer that treats both recommendation pipelines as
independent black boxes.

The comparison module supports:

* Running both recommendation methods
* Combining their results for display
* Formatting comparison output
* Gracefully handling not-found sample titles

Files:

* `movie_matcher/comparison.py`
* `tests/test_comparison.py`
* `docs/results_writeup.md`

Three sample comparisons were performed against the full dataset.

### `"The Dark Knight"`

**Genre-based:**

* Bastille Day — 1.00
* Blood Father — 1.00
* Chappie — 1.00

**Description-based:**

* The Dark Knight Rises — 0.21
* Revolutionary Road — 0.12
* Thor: The Dark World — 0.11

### `"Interstellar"`

**Genre-based:**

* The Martian — 1.00
* Cloud Atlas — 0.82
* The Fountain — 0.82

**Description-based:**

* The World's End — 0.24
* Gravity — 0.13
* Silence — 0.13

### `"Doctor Strange"`

**Genre-based:**

* Avatar — 1.00
* Clash of the Titans — 1.00
* Conan the Barbarian — 1.00

**Description-based:**

* No Strings Attached — 0.11
* Sleeping Beauty — 0.11
* Step Up 2: The Streets — 0.10

### Main observation

Genre-based similarity frequently produces exact 1.00 ties because the dataset
contains a relatively small genre vocabulary and many movies share identical
genre combinations.

Therefore, the deterministic alphabetical tie-break is important to the
actual behavior of the system rather than being merely an edge-case safeguard.

Description-based similarity produces a smoother similarity gradient but can
also produce recommendations based on shared textual vocabulary that do not
necessarily correspond to strong human-perceived similarity.

The complete analysis is documented in:

`docs/results_writeup.md`

---

## Milestone 6 — Testing, Requirements Gap-Check, and Code Quality — COMPLETE

The implementation was checked against the assignment requirements and the
project's architectural constraints.

The verification covered:

* Top-3 recommendation count
* Self-exclusion
* Not-found handling
* Fuzzy title matching
* Fuzzy-match confirmation
* Deterministic tie-breaking
* Title normalization
* Duplicate handling
* Missing-value handling
* Genre vectorization
* Description vectorization
* Cosine similarity
* Genre/description comparison
* Modular separation of responsibilities
* Type hints
* No bare `except` blocks
* Required test files
* Integration behavior

The application was also manually exercised through the browser to verify the
actual user-facing workflow.

The browser verification confirmed that the implemented behavior works through
the Streamlit interface rather than only at the module level.

---

## Milestone 7 — Documentation, Streamlit Frontend, and Final QA — COMPLETE

### Streamlit frontend — COMPLETE

A Streamlit-based graphical interface was added through:

```text
app.py
```

The interface provides a user-facing way to interact with Movie Matcher
without requiring direct terminal interaction.

Movie poster assets are stored under:

```text
assets/
```

The Streamlit application was successfully launched locally with:

```powershell
streamlit run app.py
```

The running application was manually verified through a web browser.

### Dependency update — COMPLETE

`requirements.txt` includes the dependencies required to run the application,
including Streamlit.

### README — COMPLETE

`README.md` documents:

* Project purpose
* Dataset
* Data cleaning
* Vectorization choices
* Cosine similarity
* Top-3 behavior
* Self-exclusion
* Deterministic tie-breaking
* Fuzzy matching
* Streamlit interface
* CLI
* Testing and verification
* Project structure
* Design principles

### Results write-up — COMPLETE

`docs/results_writeup.md` documents:

* The three required sample comparisons
* Genre-based recommendations
* Description-based recommendations
* Similarity scores
* Interpretation of the results
* Strengths and weaknesses of both approaches
* Importance of deterministic tie-breaking
* Overall conclusion

### Final QA — COMPLETE

Final verification confirmed:

* Assignment requirements are addressed.
* Documentation reflects the implemented architecture.
* Repository structure reflects the actual project.
* No external API keys or secrets are required.
* `requirements.txt` includes Streamlit.
* The Streamlit application launches successfully.
* User-facing behavior was manually verified in the browser.
* Fuzzy matching and confirmation behavior were checked.
* Not-found behavior was checked.
* Self-exclusion and top-3 recommendation behavior were checked.
* Genre and description recommendation outputs were checked.
* Comparison behavior was checked.
* Movie poster assets display through the frontend.

---

# Project Completion Status

**Movie Matcher implementation: COMPLETE**

The project now contains:

* A cleaned and validated movie dataset pipeline.
* Independent genre and description recommendation engines.
* Cosine-similarity ranking.
* Deterministic tie-breaking.
* Fuzzy title matching with confirmation.
* Not-found handling.
* Genre-vs-description comparison.
* Automated test files covering core functionality.
* A command-line interface.
* A Streamlit web interface.
* Movie poster assets.
* Complete README documentation.
* Results and analysis documentation.
* Final browser-based functional verification.

The implementation is ready for final Git staging, commit, and repository
submission.
