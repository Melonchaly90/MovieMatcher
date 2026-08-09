import logging
from pathlib import Path
from typing import Union
import pandas as pd

logger = logging.getLogger(__name__)

def load_dataset(csv_path: Union[str, Path]) -> pd.DataFrame:
    """
    Reads the movie dataset from a CSV file and validates required columns.
    
    Args:
        csv_path: Path to the CSV file.
        
    Returns:
        A pandas DataFrame containing the loaded data.
        
    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If required columns ('Title', 'Genre', 'Description') are missing.
    """
    path_obj = Path(csv_path)
    if not path_obj.is_file():
        raise FileNotFoundError(f"Dataset file not found at: {csv_path}")
        
    try:
        df = pd.read_csv(csv_path)
    except pd.errors.EmptyDataError as e:
        raise pd.errors.EmptyDataError(f"Failed to read CSV at {csv_path}: {e}") from e
    except pd.errors.ParserError as e:
        raise pd.errors.ParserError(f"Failed to read CSV at {csv_path}: {e}") from e
        
    required_columns = {'Title', 'Genre', 'Description'}
    missing_columns = required_columns - set(df.columns)
    
    if missing_columns:
        raise ValueError(f"Missing required columns in dataset: {', '.join(missing_columns)}")
        
    return df

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the movie dataset by handling missing values and duplicates.
    
    This function drops rows with missing Title, Genre, or Description. Dropping is
    chosen over filling because these fields are critical for downstream vectorization;
    fabricating fill values would inject false signals into recommendations.
    
    It also adds a 'normalized_title' column and removes exact duplicate rows
    (keeping the one with the lowest Rank).
    
    Args:
        df: The raw pandas DataFrame.
        
    Returns:
        A cleaned pandas DataFrame.
    """
    cleaned_df = df.copy()
    initial_count = len(cleaned_df)
    
    # Strip whitespace from string columns to handle empty-after-strip correctly
    for col in ['Title', 'Genre', 'Description']:
        if pd.api.types.is_string_dtype(cleaned_df[col]):
            cleaned_df[col] = cleaned_df[col].str.strip()
            
    # Drop rows where required columns are null
    cleaned_df.dropna(subset=['Title', 'Genre', 'Description'], inplace=True)
    
    # Drop rows where required columns are empty strings
    cleaned_df = cleaned_df[
        (cleaned_df['Title'] != '') & 
        (cleaned_df['Genre'] != '') & 
        (cleaned_df['Description'] != '')
    ]
    
    dropped_missing = initial_count - len(cleaned_df)
    if dropped_missing > 0:
        logger.info(f"Dropped {dropped_missing} rows due to missing Title, Genre, or Description.")
        
    # Add normalized title
    cleaned_df['normalized_title'] = cleaned_df['Title'].str.lower().str.strip()
    
    # Exact duplicates share every column including Rank, so no ordering step is needed before dropping them.
    count_before_dedup = len(cleaned_df)
    cleaned_df = cleaned_df.drop_duplicates(keep='first')
    dropped_dups = count_before_dedup - len(cleaned_df)
    
    if dropped_dups > 0:
        logger.info(f"Dropped {dropped_dups} exact duplicate rows.")
        
    return cleaned_df

def find_by_normalized_title(df: pd.DataFrame, normalized_title: str) -> Union[pd.Series, None]:
    """
    Finds a movie exactly matching the given normalized title.
    
    If multiple rows match (e.g., different movies with the same title),
    it deterministically returns the one with the lowest Rank to ensure
    reproducible similarity ranking.
    
    Args:
        df: The cleaned pandas DataFrame.
        normalized_title: The title string to match (assumed to be already normalized).
        
    Returns:
        The matching row as a pandas Series, or None if no match is found.
    """
    matches = df[df['normalized_title'] == normalized_title]
    
    if len(matches) == 0:
        return None
    elif len(matches) == 1:
        return matches.iloc[0]
    else:
        # Multiple matches: tie-break by returning the row with the lowest Rank.
        # This deterministic choice ensures reproducible behavior without randomness.
        if 'Rank' in matches.columns:
            return matches.sort_values('Rank').iloc[0]
        else:
            return matches.iloc[0]
