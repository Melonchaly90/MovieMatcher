import pytest
import pandas as pd
from movie_matcher.data_loader import clean_dataset
from movie_matcher.comparison import (
    compare_recommendations,
    format_comparison,
    run_sample_comparisons,
)


def _make_df():
    """Build a small in-memory DataFrame suitable for clean_dataset."""
    return clean_dataset(pd.DataFrame({
        'Rank': [1, 2, 3, 4, 5],
        'Title': ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon'],
        'Genre': [
            'Action,Sci-Fi',
            'Action',
            'Comedy',
            'Sci-Fi,Adventure',
            'Action,Sci-Fi',
        ],
        'Description': [
            'A hero saves the galaxy from aliens',
            'A hero fights crime in a city',
            'Friends go on a funny road trip',
            'Explorers discover a new alien world',
            'A hero saves the galaxy from invaders',
        ],
    }))


# --- compare_recommendations ---

def test_compare_recommendations_not_found():
    df = _make_df()
    result = compare_recommendations(df, 'Nonexistent Movie')
    assert result is None


def test_compare_recommendations_returns_both_keys():
    df = _make_df()
    result = compare_recommendations(df, 'Alpha', k=2)
    assert result is not None
    assert 'genre_recommendations' in result
    assert 'description_recommendations' in result
    assert isinstance(result['genre_recommendations'], list)
    assert isinstance(result['description_recommendations'], list)


def test_compare_recommendations_matched_title_canonical():
    df = _make_df()
    # Query with different case and extra whitespace
    result = compare_recommendations(df, '  aLpHa  ', k=2)
    assert result is not None
    assert result['matched_title'] == 'Alpha'


def test_compare_recommendations_respects_k():
    df = _make_df()
    result = compare_recommendations(df, 'Alpha', k=2)
    assert result is not None
    assert len(result['genre_recommendations']) == 2
    assert len(result['description_recommendations']) == 2


# --- format_comparison ---

def test_format_comparison_returns_string_with_titles():
    df = _make_df()
    comp = compare_recommendations(df, 'Alpha', k=2)
    assert comp is not None

    output = format_comparison(comp)
    assert isinstance(output, str)

    # The query title and matched title must appear
    assert 'Alpha' in output

    # Every recommended title from both lists must appear
    for rec in comp['genre_recommendations']:
        assert rec['title'] in output
    for rec in comp['description_recommendations']:
        assert rec['title'] in output


# --- run_sample_comparisons ---

def test_run_sample_comparisons_skips_not_found():
    df = _make_df()
    results = run_sample_comparisons(df, ['Alpha', 'NoSuchMovie'], k=2)
    assert len(results) == 1
    assert results[0]['matched_title'] == 'Alpha'


def test_run_sample_comparisons_preserves_order():
    df = _make_df()
    results = run_sample_comparisons(df, ['Gamma', 'Alpha', 'Beta'], k=2)
    assert len(results) == 3
    assert results[0]['matched_title'] == 'Gamma'
    assert results[1]['matched_title'] == 'Alpha'
    assert results[2]['matched_title'] == 'Beta'
