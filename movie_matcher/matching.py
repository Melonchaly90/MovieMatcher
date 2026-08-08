import difflib
import pandas as pd
from typing import Any
from movie_matcher.data_loader import find_by_normalized_title

def find_close_matches(df: pd.DataFrame, query: str, n: int = 3, cutoff: float = 0.6) -> list[str]:
    """
    Finds close matches for a movie title query using fuzzy string matching.
    
    This function normalizes the query and compares it against a deduplicated list 
    of normalized titles from the dataset. Deduplication is necessary because multiple 
    movies might share the same normalized title (e.g., "The Host"), and returning 
    duplicate suggestions for a fuzzy match would be confusing for the user.
    
    Args:
        df: The pandas DataFrame containing movie data with a 'normalized_title' column.
        query: The user's search string.
        n: The maximum number of close matches to return.
        cutoff: The similarity threshold (0.0 to 1.0) for a match to be considered.
        
    Returns:
        A list of original movie Titles that closely match the query.
    """
    normalized_query = query.strip().lower()
    candidates = df['normalized_title'].dropna().unique().tolist()
    
    matches = difflib.get_close_matches(normalized_query, candidates, n=n, cutoff=cutoff)
    
    # Map back to original titles
    # Since we deduplicated normalized_titles, we can use find_by_normalized_title
    # which deterministically returns the lowest-rank match for any collisions.
    original_titles = []
    for match in matches:
        row = find_by_normalized_title(df, match)
        if row is not None:
            original_titles.append(row['Title'])
            
    return original_titles

def resolve_title(df: pd.DataFrame, query: str) -> dict[str, Any]:
    """
    Orchestrates exact and fuzzy title resolution into a single predictable contract.
    
    This function returns a dictionary with a "status" key rather than returning 
    mixed types (like a row, a list, or None). This design allows the CLI layer 
    to branch predictably on the "status" key ("exact", "fuzzy", or "not_found").
    
    Args:
        df: The pandas DataFrame containing movie data.
        query: The user's search string.
        
    Returns:
        A dictionary describing the resolution result.
        - If exact match: {"status": "exact", "title": str}
        - If near miss: {"status": "fuzzy", "suggestions": list[str]}
        - If no match: {"status": "not_found"}
    """
    normalized_query = query.strip().lower()
    exact_match = find_by_normalized_title(df, normalized_query)
    
    if exact_match is not None:
        return {"status": "exact", "title": exact_match['Title']}
        
    suggestions = find_close_matches(df, query)
    
    if suggestions:
        return {"status": "fuzzy", "suggestions": suggestions}
        
    return {"status": "not_found"}
