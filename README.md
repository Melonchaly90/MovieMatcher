# Movie Matcher

A content-based movie recommendation system.

Movie Matcher compares movies using two independent representations:

1. **Genre-based similarity** using `CountVectorizer`
2. **Description-based similarity** using `TfidfVectorizer`

For a requested movie, the system returns the three most similar movies while excluding the queried movie itself.

## Project Structure

```text
movie_matcher/
├── data/
│   ├── imdb_movie_data.csv
│   └── DATA_SOURCE_NOTES.md
├── movie_matcher/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── recommender.py
│   ├── matching.py
│   ├── comparison.py
│   └── cli.py
├── tests/
│   ├── test_data_loader.py
│   ├── test_recommender.py
│   ├── test_matching.py
│   ├── test_comparison.py
│   └── test_integration.py
├── docs/
│   └── results_writeup.md
├── README.md
├── pytest.ini
└── requirements.txt
```

## Dataset

The project uses a 1,000-movie dataset containing movie titles, genres, descriptions, and supporting metadata.

The recommendation system relies primarily on:

- `Title`
- `Genre`
- `Description`

The dataset was pre-validated for the fields used by the recommendation pipeline. It contains no missing `Title`, `Genre`, or `Description` values and no exact duplicate rows.

There is one legitimate title collision: two different movies are both titled **"The Host"**. The title-matching logic handles this deterministically rather than treating the two movies as duplicates.

Dataset provenance and validation details are documented in:

`data/DATA_SOURCE_NOTES.md`

## Data Loading and Cleaning

`movie_matcher/data_loader.py` is responsible for loading and cleaning the dataset.

The cleaning process:

1. Loads the CSV with pandas.
2. Validates that `Title`, `Genre`, and `Description` are present.
3. Removes rows with missing required fields.
4. Removes empty required fields after whitespace normalization.
5. Creates a `normalized_title` value using lowercase and trimmed whitespace.
6. Removes exact duplicate rows.

Missing required fields are dropped rather than filled because these fields are necessary for meaningful vectorization. Fabricating replacement values could introduce misleading signals into the recommendation system.

When multiple movies share the same normalized title, exact lookup uses the movie with the lowest `Rank` as a deterministic tie-break.

## Recommendation Approach

Movie Matcher deliberately keeps the genre and description pipelines separate. This makes it possible to compare the behavior of the two representations directly.

### Genre similarity

Genres are represented using `CountVectorizer`.

The dataset stores genres as comma-separated labels, so the genre pipeline uses a custom comma-based tokenizer. This preserves compound labels such as `Sci-Fi` as a single genre rather than splitting the label into unrelated tokens.

Cosine similarity is then calculated between the resulting genre vectors.

### Description similarity

Movie descriptions are represented using `TfidfVectorizer`.

TF-IDF is better suited to free-form prose because it gives less importance to words that occur frequently across many descriptions and more importance to terms that are comparatively distinctive.

The description pipeline also removes English stop words.

Unlike the genre pipeline, it uses the vectorizer's normal text tokenization because descriptions are natural-language prose rather than structured comma-separated labels.

## Similarity Ranking

Both recommendation pipelines use the same `top_k_similar()` ranking logic.

For a queried movie:

1. Calculate cosine similarity against the other movie vectors.
2. Exclude the queried movie itself.
3. Sort by similarity score in descending order.
4. Apply a deterministic alphabetical tie-break using the normalized title.
5. Return the requested number of recommendations.

The CLI and assignment workflow use `k=3`, producing exactly three recommendations when enough movies are available.

This deterministic tie-breaking is particularly important for the genre representation because many movies share identical genre combinations and therefore receive exactly the same similarity score.

## Fuzzy Title Matching

Movie titles are first normalized for case and surrounding whitespace.

If an exact normalized-title match cannot be found, `difflib.get_close_matches` is used to find a reasonable near-match.

The CLI does **not** silently assume that a fuzzy match is correct. Instead, it presents the matched title to the user and requires explicit confirmation before generating recommendations.

If no reasonable match is found, the system reports that the movie was not found instead of producing arbitrary recommendations.

## Genre vs. Description Comparison

The project includes a comparison module that runs the same movie through both recommendation pipelines.

Three sample movies are used for the comparison:

- The Dark Knight
- Interstellar
- Doctor Strange

The observed behavior illustrates the trade-off between the two representations.

Genre-based similarity frequently produces exact ties because the dataset contains a relatively small genre vocabulary and many movies share identical genre combinations. The deterministic alphabetical tie-break therefore has a practical effect on the returned results.

Description-based similarity produces a smoother range of similarity scores because it considers the actual vocabulary used in movie descriptions. However, shared narrative or thematic language can sometimes cause recommendations that are textually similar without being especially similar in genre or plot.

The detailed comparison and analysis are documented in:

`docs/results_writeup.md`

## Testing

The project uses pytest for automated testing.

The test suite covers:

- Dataset loading and validation
- Missing-value handling
- Exact duplicate handling
- Title normalization and title collisions
- Genre vectorization
- Description vectorization
- Cosine-similarity ranking
- Self-exclusion
- Deterministic tie-breaking
- Fuzzy title matching
- Not-found handling
- Comparison-module behavior
- Exact top-3 recommendation counts
- End-to-end behavior against the real dataset

Run the complete test suite with:

```powershell
python -m pytest -v
```

The current full suite contains **37 tests**, all passing.

## Requirements

Install the project dependencies with:

```powershell
python -m pip install -r requirements.txt
```

The main dependencies are:

- pandas
- NumPy
- scikit-learn
- pytest for testing

## Running the Application

The recommendation logic is separated from terminal input so it can be tested independently.

The CLI entry point is:

```text
movie_matcher/cli.py
```

The CLI accepts a movie title, resolves exact or fuzzy matches, confirms fuzzy matches with the user, and then produces recommendations.

## Design Principles

The project follows several deliberate design decisions:

- Genre and description representations remain independent.
- Recommendation logic is separated from CLI input/output.
- Similarity ranking is shared between both recommendation pipelines.
- Missing critical fields are dropped rather than fabricated.
- Title matching is case-insensitive and whitespace-normalized.
- Fuzzy matches require explicit user confirmation.
- Similarity ties are resolved deterministically.
- The queried movie is always excluded from its own recommendations.
- No external API calls or secrets are required.
