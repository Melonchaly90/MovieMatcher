import logging
from typing import Optional
import numpy as np
import pandas as pd
import scipy.sparse
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from movie_matcher.data_loader import find_by_normalized_title

logger = logging.getLogger(__name__)

def build_genre_vectors(df: pd.DataFrame) -> tuple[CountVectorizer, scipy.sparse.csr_matrix]:
    """
    Fits a CountVectorizer over the dataframe's Genre column and returns both the 
    fitted vectorizer and the resulting document-term matrix.
    
    The default CountVectorizer tokenizer splits on non-word characters, which is unsafe 
    for genres because it would break hyphenated labels like "Sci-Fi" into separate 
    meaningless tokens ("sci" and "fi"). Therefore, this function uses a custom tokenizer 
    that splits strictly on commas and normalizes each genre by stripping whitespace 
    and lowercasing.
    
    Args:
        df: The pandas DataFrame containing a 'Genre' column.
        
    Returns:
        A tuple containing the fitted CountVectorizer and the sparse document-term matrix.
    """
    vectorizer = CountVectorizer(
        tokenizer=lambda text: [g.strip().lower() for g in text.split(',')],
        token_pattern=None,
        lowercase=False,  # the custom tokenizer already lowercases the tokens
    )
    
    dt_matrix = vectorizer.fit_transform(df['Genre'])
    return vectorizer, dt_matrix

def top_k_similar(similarity_scores: np.ndarray, df: pd.DataFrame, exclude_position: int, k: int = 3) -> list[dict]:
    """
    Ranks movies by similarity scores descending and returns the top k.
    
    This function excludes the query movie itself (at `exclude_position`) from 
    consideration. For any movies with equal similarity scores, ties are broken by 
    sorting them in ascending alphabetical order based on their `normalized_title` 
    column. This tie-breaking rule ensures deterministic and reproducible results 
    without relying on incoming row order or randomness.
    
    Args:
        similarity_scores: A 1D array of similarity scores aligned with `df`'s rows.
        df: The pandas DataFrame containing the movies.
        exclude_position: The row index of the query movie to exclude from results.
        k: The maximum number of recommendations to return.
        
    Returns:
        A list of dictionaries representing the top k recommended movies, each with 
        keys "title", "genre", and "similarity".
    """
    # Create a DataFrame to easily handle sorting and tie-breaking
    results_df = pd.DataFrame({
        'position': range(len(df)),
        'title': df['Title'],
        'genre': df['Genre'],
        'normalized_title': df['normalized_title'],
        'similarity': similarity_scores
    })
    
    # Exclude the query movie itself
    results_df = results_df[results_df['position'] != exclude_position]
    
    # Sort by similarity descending, then normalized_title ascending
    results_df = results_df.sort_values(
        by=['similarity', 'normalized_title'],
        ascending=[False, True]
    )
    
    # Take top k
    top_k_df = results_df.head(k)
    
    # Build output list
    output = []
    for _, row in top_k_df.iterrows():
        output.append({
            "title": row['title'],
            "genre": row['genre'],
            "similarity": round(float(row['similarity']), 4)
        })
        
    return output

def recommend_by_genre(df: pd.DataFrame, title: str, k: int = 3) -> Optional[list[dict]]:
    """
    Orchestrates the genre-based movie recommendation process.
    
    This function looks up a movie by its normalized title, builds genre vectors 
    for the entire dataset, computes cosine similarity between the queried movie 
    and all others, and returns the top k matches.
    
    Args:
        df: The pandas DataFrame containing the movie dataset.
        title: The title of the movie to query.
        k: The maximum number of recommendations to return.
        
    Returns:
        A list of recommended movie dictionaries, or None if the queried title is not found.
    """
    # a. Reset index to ensure contiguous 0..n-1 range for position alignment
    df = df.reset_index(drop=True)
    
    # b. Normalize the input title and look it up
    normalized_query_title = title.lower().strip()
    match = find_by_normalized_title(df, normalized_query_title)
    
    # c. If no match is found, return None
    if match is None:
        return None
        
    # d. Build genre vectors
    vectorizer, matrix = build_genre_vectors(df)
    
    # e. Compute cosine similarity
    # Determine the matched movie's row POSITION in the reset-index df
    # Since match is a Series from the reset-index df, its name is its index position
    exclude_position = match.name
    query_vector = matrix[exclude_position]
    
    # Calculate similarity between the query vector and all rows
    similarity_scores = cosine_similarity(query_vector, matrix).flatten()
    
    # g. Return the result of top_k_similar
    return top_k_similar(similarity_scores, df, exclude_position, k)

def build_description_vectors(df: pd.DataFrame) -> tuple[TfidfVectorizer, scipy.sparse.csr_matrix]:
    """
    Fits a TfidfVectorizer over the dataframe's Description column and returns both the 
    fitted vectorizer and the resulting document-term matrix.
    
    Unlike genres, which require a custom tokenizer to prevent splitting hyphenated labels 
    like "Sci-Fi", movie descriptions are normal English prose. Therefore, this function 
    uses the TfidfVectorizer's default tokenizer and token pattern. It also uses 
    stop_words='english' to filter out common English words (e.g., "the", "a", "of") 
    that would otherwise dominate the vector space without carrying content signal.
    
    Args:
        df: The pandas DataFrame containing a 'Description' column.
        
    Returns:
        A tuple containing the fitted TfidfVectorizer and the sparse document-term matrix.
    """
    vectorizer = TfidfVectorizer(stop_words='english')
    dt_matrix = vectorizer.fit_transform(df['Description'])
    return vectorizer, dt_matrix

def recommend_by_description(df: pd.DataFrame, title: str, k: int = 3) -> Optional[list[dict]]:
    """
    Orchestrates the description-based movie recommendation process.
    
    This function looks up a movie by its normalized title, builds description vectors 
    for the entire dataset, computes cosine similarity between the queried movie 
    and all others, and returns the top k matches.
    
    Args:
        df: The pandas DataFrame containing the movie dataset.
        title: The title of the movie to query.
        k: The maximum number of recommendations to return.
        
    Returns:
        A list of recommended movie dictionaries, or None if the queried title is not found.
    """
    # a. Reset index to ensure contiguous 0..n-1 range for position alignment
    df = df.reset_index(drop=True)
    
    # b. Normalize the input title and look it up
    normalized_query_title = title.lower().strip()
    match = find_by_normalized_title(df, normalized_query_title)
    
    # c. If no match is found, return None
    if match is None:
        return None
        
    # d. Build description vectors
    vectorizer, matrix = build_description_vectors(df)
    
    # e. Compute cosine similarity
    # Determine the matched movie's row POSITION in the reset-index df
    # Since match is a Series from the reset-index df, its name is its index position
    exclude_position = match.name
    query_vector = matrix[exclude_position]
    
    # Calculate similarity between the query vector and all rows
    similarity_scores = cosine_similarity(query_vector, matrix).flatten()
    
    # g. Return the result of top_k_similar
    return top_k_similar(similarity_scores, df, exclude_position, k)
