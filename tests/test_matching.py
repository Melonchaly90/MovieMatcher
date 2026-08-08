import pytest
import pandas as pd
from movie_matcher.matching import find_close_matches, resolve_title
from movie_matcher.data_loader import clean_dataset

def test_resolve_title_exact_match():
    df = pd.DataFrame({
        'Rank': [1, 2],
        'Title': ['The Avengers', 'Iron Man'],
        'Genre': ['Action', 'Action'],
        'Description': ['Desc1', 'Desc2']
    })
    df = clean_dataset(df)
    
    result = resolve_title(df, '  the AVENGERS  ')
    assert result['status'] == 'exact'
    assert result['title'] == 'The Avengers'
    assert 'suggestions' not in result

def test_resolve_title_fuzzy_match():
    df = pd.DataFrame({
        'Rank': [1, 2],
        'Title': ['Avengers', 'Iron Man'],
        'Genre': ['Action', 'Action'],
        'Description': ['Desc1', 'Desc2']
    })
    df = clean_dataset(df)
    
    # Near miss typo
    result = resolve_title(df, 'Avngers')
    assert result['status'] == 'fuzzy'
    assert 'suggestions' in result
    assert result['suggestions'][0] == 'Avengers'

def test_resolve_title_not_found():
    df = pd.DataFrame({
        'Rank': [1, 2],
        'Title': ['Avengers', 'Iron Man'],
        'Genre': ['Action', 'Action'],
        'Description': ['Desc1', 'Desc2']
    })
    df = clean_dataset(df)
    
    result = resolve_title(df, 'Completely Random String 12345')
    assert result['status'] == 'not_found'
    assert 'suggestions' not in result
    assert result == {'status': 'not_found'}

def test_find_close_matches_deduplicates():
    df = pd.DataFrame({
        'Rank': [1, 2, 3],
        'Title': ['The Host', 'The Host', 'Other Movie'],
        'Genre': ['Horror', 'Sci-Fi', 'Action'],
        'Description': ['Desc1', 'Desc2', 'Desc3']
    })
    df = clean_dataset(df)
    
    # Even though there are two rows that map to 'the host', 
    # find_close_matches should only return one suggestion for it.
    suggestions = find_close_matches(df, 'The Hst')
    assert len(suggestions) == 1
    assert suggestions[0] == 'The Host'

def test_find_close_matches_empty_on_no_match():
    df = pd.DataFrame({
        'Rank': [1, 2],
        'Title': ['Avengers', 'Iron Man'],
        'Genre': ['Action', 'Action'],
        'Description': ['Desc1', 'Desc2']
    })
    df = clean_dataset(df)
    
    suggestions = find_close_matches(df, 'xyzqwer', cutoff=0.6)
    assert isinstance(suggestions, list)
    assert len(suggestions) == 0
