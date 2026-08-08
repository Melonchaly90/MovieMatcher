import pytest
import pandas as pd
from pathlib import Path
from movie_matcher.data_loader import load_dataset, clean_dataset, find_by_normalized_title

def test_clean_dataset_drops_missing():
    df = pd.DataFrame({
        'Rank': [1, 2, 3, 4],
        'Title': ['A', 'B', '', 'D'],
        'Genre': ['Action', None, 'Comedy', 'Drama'],
        'Description': ['Desc1', 'Desc2', 'Desc3', '   ']
    })
    
    cleaned = clean_dataset(df)
    assert len(cleaned) == 1
    assert cleaned.iloc[0]['Title'] == 'A'

def test_clean_dataset_drops_exact_duplicates():
    df = pd.DataFrame({
        'Rank': [1, 1, 2],
        'Title': ['A', 'A', 'B'],
        'Genre': ['Action', 'Action', 'Action'],
        'Description': ['Desc', 'Desc', 'Desc2'],
        'Year': [2010, 2010, 2011]
    })
    cleaned = clean_dataset(df)
    assert len(cleaned) == 2
    assert sorted(cleaned['Rank'].tolist()) == [1, 2]

def test_clean_dataset_does_not_merge_different_movies():
    df = pd.DataFrame({
        'Rank': [240, 633],
        'Title': ['The Host', 'The Host'],
        'Genre': ['Sci-Fi', 'Horror'],
        'Description': ['Korean movie', 'Alien movie'],
        'Year': [2006, 2013]
    })
    cleaned = clean_dataset(df)
    assert len(cleaned) == 2

def test_find_by_normalized_title_no_match():
    df = pd.DataFrame({
        'Rank': [1],
        'Title': ['A'],
        'normalized_title': ['a']
    })
    assert find_by_normalized_title(df, 'b') is None

def test_find_by_normalized_title_single_match():
    df = pd.DataFrame({
        'Rank': [1],
        'Title': ['A'],
        'normalized_title': ['a']
    })
    match = find_by_normalized_title(df, 'a')
    assert match is not None
    assert match['Title'] == 'A'

def test_find_by_normalized_title_tie_break():
    df = pd.DataFrame({
        'Rank': [633, 240],
        'Title': ['The Host', 'The Host'],
        'normalized_title': ['the host', 'the host']
    })
    match = find_by_normalized_title(df, 'the host')
    assert match is not None
    assert match['Rank'] == 240

def test_load_dataset_missing_file():
    with pytest.raises(FileNotFoundError):
        load_dataset("nonexistent_file.csv")

def test_load_dataset_missing_columns(tmp_path):
    csv_file = tmp_path / "bad_data.csv"
    csv_file.write_text("Title,Genre\nMovie A,Action\n") # Missing Description
    
    with pytest.raises(ValueError, match="Missing required columns"):
        load_dataset(csv_file)
