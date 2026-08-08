# Dataset Provenance & Pre-Validation Notes

**File:** `data/imdb_movie_data.csv`
**Rows:** 1000 movies (999 data rows + header)
**Columns:** `Rank, Title, Genre, Description, Director, Actors, Year, Runtime (Minutes), Rating, Votes, Revenue (Millions), Metascore`

## Source
This is the widely-circulated "IMDB-Movie-Data.csv" tutorial dataset (scraped IMDb
metadata for ~1000 films), mirrored across many public data-science tutorial repos.
Retrieved from a public GitHub mirror:
`https://github.com/LearnDataSci/articles` (Python Pandas Tutorial folder).

**Licensing caveat (be upfront about this in the README):** this dataset circulates
widely in tutorials without a single canonical upstream license page. Treat it as
"for coursework/demo use" and say so explicitly in the README rather than asserting
a specific license. If the internship requires a strictly-licensed dataset (e.g. an
official Kaggle CC0 download or the official MovieLens `ml-latest-small`), swap the
file at `data/imdb_movie_data.csv` for one of those — the loader module should not
care which source CSV it reads as long as the column names match, or a config maps
column names.

## Pre-validation performed (so the loader design is grounded, not guessed)
Ran `pandas.read_csv` + `isnull().sum()` + duplicate checks before writing the spec:

- **Missing values:** `Title`, `Genre`, `Description` — **zero nulls**. `Revenue
  (Millions)` has 128 nulls, `Metascore` has 64 nulls (neither column is used by
  the recommender, so this doesn't block anything, but the loader must still be
  written defensively — see below).
- **Exact duplicate rows (all columns identical):** 0.
- **Duplicate titles after case-insensitive + whitespace-trimmed normalization:** 1
  pair — **"The Host"** appears twice: Rank 240 (2013, rating 5.9) and Rank 633
  (2006, rating 7.0, the Bong Joon-ho film). These are **two different movies that
  happen to share a title**, not a data-entry duplicate. The loader must NOT merge
  or drop either row — this is a title-matching ambiguity, not a dedup case.

## Why this matters for the design (binding decisions, not suggestions)
1. **Missing-value handling must still be implemented generically** (drop/fill/flag
   any row with a null `Title`, `Genre`, or `Description`) even though this specific
   CSV happens to have none in those columns today — the grading/testing may swap in
   a messier CSV, and the assignment explicitly requires this to not crash.
2. **Exact-duplicate-row dedup logic must still be implemented** even though this
   CSV has zero exact duplicates — same reasoning as above. Rule: keep the
   **first occurrence by `Rank` (source-file order)**, drop subsequent exact
   duplicates, log how many were dropped.
3. **The "Host" collision is the concrete test case for title-collision handling**:
   when a normalized title matches more than one row, resolve deterministically by
   **lowest `Rank`** (documented tie-break, same rule family as the recommendation
   tie-break) rather than raising an error or picking randomly.
