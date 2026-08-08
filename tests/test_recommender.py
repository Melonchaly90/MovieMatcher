import pytest
import numpy as np
import pandas as pd
from movie_matcher.recommender import build_genre_vectors, top_k_similar, recommend_by_genre
from movie_matcher.data_loader import clean_dataset

def test_build_genre_vectors_tokenizes_sci_fi_correctly():
    df = pd.DataFrame({
        'Genre': ['Action,Sci-Fi', 'Comedy,Romance', 'Sci-Fi']
    })
    vectorizer, matrix = build_genre_vectors(df)
    features = vectorizer.get_feature_names_out()
    assert 'sci-fi' in features
    assert 'sci' not in features
    assert 'fi' not in features
    assert 'action' in features
    assert 'comedy' in features
    assert 'romance' in features

def test_top_k_similar_excludes_self():
    df = pd.DataFrame({
        'Title': ['A', 'B', 'C'],
        'Genre': ['Action', 'Action', 'Action'],
        'normalized_title': ['a', 'b', 'c']
    })
    # Similarity scores where B has highest (1.0)
    scores = np.array([0.5, 1.0, 0.8])
    # Exclude B (position 1)
    results = top_k_similar(scores, df, exclude_position=1, k=2)
    assert len(results) == 2
    assert results[0]['title'] == 'C' # Highest score among remaining
    assert results[1]['title'] == 'A'
    assert all(r['title'] != 'B' for r in results)

def test_top_k_similar_descending_order():
    df = pd.DataFrame({
        'Title': ['A', 'B', 'C', 'D'],
        'Genre': ['G1', 'G2', 'G3', 'G4'],
        'normalized_title': ['a', 'b', 'c', 'd']
    })
    scores = np.array([0.1, 0.9, 0.5, 0.7])
    results = top_k_similar(scores, df, exclude_position=0, k=3)
    assert [r['title'] for r in results] == ['B', 'D', 'C']
    assert [r['similarity'] for r in results] == [0.9, 0.7, 0.5]

def test_top_k_similar_tie_break():
    df = pd.DataFrame({
        'Title': ['Z Movie', 'A Movie', 'M Movie'],
        'Genre': ['Action', 'Action', 'Action'],
        'normalized_title': ['z movie', 'a movie', 'm movie']
    })
    # All have identical similarity
    scores = np.array([0.8, 0.8, 0.8])
    results = top_k_similar(scores, df, exclude_position=2, k=2)
    # A Movie should come before Z Movie due to alphabetical tie break
    assert results[0]['title'] == 'A Movie'
    assert results[1]['title'] == 'Z Movie'

def test_top_k_similar_fewer_than_k():
    df = pd.DataFrame({
        'Title': ['A', 'B', 'C'],
        'Genre': ['G1', 'G2', 'G3'],
        'normalized_title': ['a', 'b', 'c']
    })
    scores = np.array([1.0, 0.5, 0.4])
    # Ask for 5 items, but only 2 remain after exclusion
    results = top_k_similar(scores, df, exclude_position=0, k=5)
    assert len(results) == 2

def test_recommend_by_genre_not_found():
    df = pd.DataFrame({
        'Title': ['A', 'B'],
        'Genre': ['Action', 'Comedy'],
        'normalized_title': ['a', 'b']
    })
    assert recommend_by_genre(df, 'Nonexistent Movie') is None

def test_recommend_by_genre_end_to_end():
    df = pd.DataFrame({
        'Rank': [1, 2, 3, 4, 5],
        'Title': ['Hero', 'Super', 'Funny', 'Galactic', 'Hero 2'],
        'Genre': ['Action,Sci-Fi', 'Action', 'Comedy', 'Sci-Fi,Adventure', 'Action,Sci-Fi'],
        'Description': ['D1', 'D2', 'D3', 'D4', 'D5']
    })
    # Apply cleaning step since recommend_by_genre expects normalized titles
    df = clean_dataset(df)
    
    results = recommend_by_genre(df, 'Hero', k=2)
    
    assert results is not None
    assert len(results) == 2
    titles = [r['title'] for r in results]
    assert 'Hero' not in titles  # self-exclusion
    # Hero 2 has identical genres to Hero, so it should be #1
    assert titles[0] == 'Hero 2'
    # Galactic has Sci-Fi, Super has Action, either could be #2 depending on count vectors
    # but the point is we got 2 results and Hero is excluded.
