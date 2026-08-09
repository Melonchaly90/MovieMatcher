"""
Integration tests that run against the REAL dataset (data/imdb_movie_data.csv).

This is an intentional, narrow exception to the rule that governs every other
test file in this project ("never read the real CSV in unit tests").  These
tests exist specifically to confirm that the full pipeline — loading,
cleaning, vectorization, and recommendation — works end-to-end on the actual
shipped data, not just on hand-built fixtures.  They complement, rather than
replace, the fast deterministic unit tests elsewhere.
"""

import pandas as pd
from movie_matcher.data_loader import load_dataset, clean_dataset
from movie_matcher.recommender import recommend_by_genre, recommend_by_description


def test_real_dataset_loads_and_cleans_without_error():
    df_raw = load_dataset("data/imdb_movie_data.csv")
    raw_count = len(df_raw)

    df = clean_dataset(df_raw)

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert 'normalized_title' in df.columns
    # The real CSV is pre-validated to have no rows dropped during cleaning.
    assert len(df) == raw_count


def test_real_dataset_genre_recommendation_returns_exactly_three():
    df_raw = load_dataset("data/imdb_movie_data.csv")
    df = clean_dataset(df_raw)

    results = recommend_by_genre(df, "The Dark Knight", k=3)

    assert results is not None
    assert len(results) == 3
    returned_titles = [r['title'] for r in results]
    assert "The Dark Knight" not in returned_titles


def test_real_dataset_description_recommendation_returns_exactly_three():
    df_raw = load_dataset("data/imdb_movie_data.csv")
    df = clean_dataset(df_raw)

    results = recommend_by_description(df, "The Dark Knight", k=3)

    assert results is not None
    assert len(results) == 3
    returned_titles = [r['title'] for r in results]
    assert "The Dark Knight" not in returned_titles
