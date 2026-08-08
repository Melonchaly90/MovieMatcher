import logging
import pandas as pd
from movie_matcher.data_loader import (
    load_dataset,
    clean_dataset,
    find_by_normalized_title,
)
from movie_matcher.recommender import recommend_by_genre, recommend_by_description

logger = logging.getLogger(__name__)


def compare_recommendations(
    df: pd.DataFrame, title: str, k: int = 3
) -> dict | None:
    """
    Run the same query through both genre-based and description-based
    recommendation pipelines and return both result sets in a single dict.

    The function resolves the canonical Title for display purposes by
    normalizing the input and looking it up via ``find_by_normalized_title``
    on a reset-index copy of *df* (the same pattern ``recommend_by_genre``
    already uses internally).  If no match is found, ``None`` is returned
    immediately.

    **Intentional repeated-lookup trade-off:** the title is looked up three
    times in total — once here (to resolve the canonical display title) and
    once more inside each of the two ``recommend_*`` functions.  Both
    ``recommend_by_genre`` and ``recommend_by_description`` are complete,
    independent pipelines that each perform their own title resolution,
    vectorization, and similarity computation internally.  This function
    deliberately calls them as black boxes rather than refactoring their
    internals to share a lookup result.  At the dataset's scale (~1 000
    rows) the redundant lookups are negligible in cost, and keeping the
    pipelines independent avoids coupling this comparison layer to the
    internal contracts of the recommender module.

    Args:
        df: The cleaned pandas DataFrame.
        title: The movie title to query.
        k: The maximum number of recommendations per method.

    Returns:
        A dict with keys ``query``, ``matched_title``,
        ``genre_recommendations``, and ``description_recommendations``,
        or ``None`` if the title is not found in the dataset.
    """
    # Resolve canonical title on a reset-index copy (same pattern as
    # recommend_by_genre).
    df_reset = df.reset_index(drop=True)
    normalized = title.strip().lower()
    match = find_by_normalized_title(df_reset, normalized)
    if match is None:
        return None

    canonical_title: str = match["Title"]

    genre_recs = recommend_by_genre(df, title, k)
    desc_recs = recommend_by_description(df, title, k)

    return {
        "query": title,
        "matched_title": canonical_title,
        "genre_recommendations": genre_recs,
        "description_recommendations": desc_recs,
    }


def format_comparison(comparison: dict) -> str:
    """
    Format a single comparison result as a human-readable multi-line string.

    This is a pure function: it does **not** call ``print()``.  Returning a
    string instead of printing directly keeps the function easily testable
    (no need to capture stdout) and gives the caller full control over
    where the output goes (terminal, file, log, etc.).

    Args:
        comparison: A dict as returned by ``compare_recommendations``
                    (assumed not to be ``None``).

    Returns:
        A formatted multi-line string showing the query, matched title,
        and both recommendation lists with numbered entries.
    """
    lines: list[str] = []
    lines.append(f"Query: {comparison['query']}")
    lines.append(f"Matched Title: {comparison['matched_title']}")

    lines.append("")
    lines.append("Genre-based recommendations:")
    for i, rec in enumerate(comparison["genre_recommendations"], 1):
        lines.append(f"  {i}. {rec['title']} (Similarity: {rec['similarity']})")

    lines.append("")
    lines.append("Description-based recommendations:")
    for i, rec in enumerate(comparison["description_recommendations"], 1):
        lines.append(f"  {i}. {rec['title']} (Similarity: {rec['similarity']})")

    return "\n".join(lines)


def run_sample_comparisons(
    df: pd.DataFrame, titles: list[str], k: int = 3
) -> list[dict]:
    """
    Run ``compare_recommendations`` for each title and collect results.

    Titles that are not found in the dataset are gracefully skipped rather
    than raising an exception.  A log message (via the ``logging`` module,
    not ``print``) is emitted for every skipped title so that callers get
    visibility into typos or missing entries without the entire run
    failing.

    Args:
        df: The cleaned pandas DataFrame.
        titles: A list of movie title strings to compare.
        k: The maximum number of recommendations per method.

    Returns:
        A list of successful (non-``None``) comparison dicts, preserving
        the input order of the titles that were found.
    """
    results: list[dict] = []
    for title in titles:
        comparison = compare_recommendations(df, title, k)
        if comparison is None:
            logger.warning(
                "Skipping '%s': title not found in the dataset.", title
            )
            continue
        results.append(comparison)
    return results


if __name__ == "__main__":
    print("Loading movie dataset...")
    df_raw = load_dataset("data/imdb_movie_data.csv")
    df = clean_dataset(df_raw)

    sample_titles = ["The Dark Knight", "Interstellar", "Doctor Strange"]
    comparisons = run_sample_comparisons(df, sample_titles, k=3)

    for i, comp in enumerate(comparisons):
        if i > 0:
            print("\n" + "=" * 60 + "\n")
        print(format_comparison(comp))
