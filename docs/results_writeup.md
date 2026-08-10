# Results and Analysis

## Overview

The Movie Matcher system compares two independent approaches to movie recommendation:

* **Genre-based similarity**, using `CountVectorizer`
* **Description-based similarity**, using `TfidfVectorizer`

Both approaches use cosine similarity and the same ranking logic. The queried movie is excluded from its own recommendations, and equal similarity scores are resolved using a deterministic alphabetical tie-break on normalized titles, with the lowest `Rank` used when normalized titles are identical.

The comparison was performed against the project's real 1,000-movie dataset using three sample queries:

* **The Dark Knight**
* **Interstellar**
* **Doctor Strange**

The results demonstrate the different strengths and limitations of categorical genre information compared with free-form textual descriptions.

## 1. The Dark Knight

### Genre-based recommendations

| Movie        | Similarity |
| ------------ | ---------: |
| Bastille Day |       1.00 |
| Blood Father |       1.00 |
| Chappie      |       1.00 |

All three recommendations have a similarity score of 1.00.

This illustrates an important limitation of the genre representation. Genre vectors only capture which genre labels a movie has, not the details of its story, tone, characters, or themes. When several movies share exactly the same genre combination, their vectors can be identical and therefore produce a perfect cosine similarity score.

The alphabetical tie-break is therefore important here. Without a deterministic tie-break, the ordering of equally similar movies would not be clearly defined.

### Description-based recommendations

| Movie                 | Similarity |
| --------------------- | ---------: |
| The Dark Knight Rises |       0.21 |
| Revolutionary Road    |       0.12 |
| Thor: The Dark World  |       0.11 |

The description-based results provide a much smoother similarity gradient.

**The Dark Knight Rises** is a particularly intuitive result because its description shares substantial narrative and thematic vocabulary with the queried movie. The other recommendations demonstrate that description similarity can identify textual relationships that are not visible from genre labels alone.

### Interpretation

For this query, the description-based approach provides a more differentiated ranking because the genre representation produces several exact ties.

The genre approach still provides useful broad-category similarity, but it lacks enough detail to distinguish movies that share the same genre combination.

---

## 2. Interstellar

### Genre-based recommendations

| Movie        | Similarity |
| ------------ | ---------: |
| The Martian  |       1.00 |
| Cloud Atlas  |       0.82 |
| The Fountain |       0.82 |

**The Martian** receives a perfect genre similarity score, indicating that its genre representation matches the representation of *Interstellar* exactly.

**Cloud Atlas** and **The Fountain** have lower but equal similarity scores. Again, the alphabetical tie-break determines their order.

### Description-based recommendations

| Movie           | Similarity |
| --------------- | ---------: |
| The World's End |       0.24 |
| Gravity         |       0.13 |
| Silence         |       0.13 |

The description representation produces a wider range of similarity values.

The results show that textual similarity does not necessarily mean that two movies belong to the same broad genre category. A movie can share vocabulary or thematic concepts with another movie even when their genres differ.

### Interpretation

The genre-based result is arguably more intuitive at the broad-category level: **The Martian** and **Interstellar** share a strong science-fiction orientation.

The description-based approach provides more nuanced similarity scores, but its results demonstrate the risk of relying on textual vocabulary alone. Shared words and themes can connect movies that are not obvious substitutes for one another.

For this query, genre similarity is useful for identifying broad genre neighbors, while description similarity provides a more granular textual comparison.

---

## 3. Doctor Strange

### Genre-based recommendations

| Movie               | Similarity |
| ------------------- | ---------: |
| Avatar              |       1.00 |
| Clash of the Titans |       1.00 |
| Conan the Barbarian |       1.00 |

All three recommendations receive a perfect similarity score.

This is another example of the limited resolution of the genre representation. Several movies can share the same genre labels even though their stories and settings are substantially different.

The alphabetical tie-break is once again responsible for producing a deterministic ordering among equally scored results.

### Description-based recommendations

| Movie                  | Similarity |
| ---------------------- | ---------: |
| No Strings Attached    |       0.11 |
| Sleeping Beauty        |       0.11 |
| Step Up 2: The Streets |       0.10 |

These results demonstrate both the strength and weakness of the TF-IDF approach.

The description representation can identify movies that share vocabulary, narrative structures, or thematic language. However, this does not guarantee that the resulting movies are semantically similar in the way a viewer would normally understand "similar movie."

For example, **Sleeping Beauty** appearing among the recommendations illustrates how shared descriptive language can produce a match even when the movies are very different in conventional genre terms.

### Interpretation

For this query, the genre approach gives broad-category matches, while the description approach exposes the limitations of lexical similarity.

The description results are not necessarily incorrect—the algorithm is correctly finding shared textual signals—but those signals do not always correspond to what a human would consider a useful recommendation.

---

## Genre vs. Description

The comparison reveals a clear trade-off between the two representations.

### Genre-based similarity

**Strengths:**

* Simple and easy to interpret.
* Good at identifying movies with similar broad genre profiles.
* Produces intuitive categorical relationships.
* Deterministic tie-breaking makes repeated results predictable.

**Weaknesses:**

* Uses a relatively small vocabulary.
* Many movies share identical genre combinations.
* Exact ties are common.
* Does not capture plot, characters, tone, or narrative details.

### Description-based similarity

**Strengths:**

* Uses much richer textual information.
* Produces a smoother range of similarity scores.
* Can capture shared themes and narrative vocabulary.
* Can distinguish movies that have the same genres but different descriptions.

**Weaknesses:**

* Lexical similarity does not always equal meaningful movie similarity.
* Shared words can create surprising recommendations.
* Results can be less intuitive than genre-based recommendations.
* TF-IDF does not understand meaning in the same way a human reader does.

---

## Importance of the Tie-Break Rule

The comparison demonstrates that deterministic tie-breaking is not merely an edge-case safeguard.

Genre-based similarity frequently produces exact 1.00 ties because many movies have identical genre vectors. Without a deterministic secondary ordering, the returned top-three list could be ambiguous.

The project therefore uses normalized titles as the primary alphabetical tie-break. This makes recommendation output reproducible and predictable.

A secondary lowest-`Rank` rule is used when two different movies have the same normalized title, such as the two movies titled **The Host**.

---

## User-Facing Verification

In addition to the implementation-level test coverage, the completed application was manually verified through the running Streamlit interface in a web browser.

The verification confirmed the expected end-to-end behavior of the application, including:

* Movie title input and selection
* Genre-based recommendation generation
* Description-based recommendation generation
* Exactly three recommendations
* Self-exclusion of the queried movie
* Fuzzy title matching
* Explicit confirmation of fuzzy matches
* Not-found handling
* Deterministic recommendation behavior
* Movie poster display
* Comparison functionality

This browser-level verification confirmed that the individual modules work together correctly through the actual user-facing application.

---

## Overall Conclusion

Neither representation is universally better.

The **genre-based approach** is stronger when the goal is to find movies with similar broad categorical profiles. It is simple, interpretable, and often produces recommendations that make sense at the genre level. Its main weakness is limited resolution, which leads to frequent exact ties.

The **description-based approach** provides more detailed and differentiated similarity scores because it uses the actual language of movie descriptions. It can capture relationships that genre labels cannot. However, its reliance on word-level similarity can also produce recommendations that are textually related without being genuinely similar from a viewer's perspective.

For this project, keeping the two pipelines independent is therefore useful. The comparison makes the strengths and limitations of each representation visible rather than hiding them behind a combined score.

The final system combines these independent recommendation pipelines with deterministic title matching, fuzzy-match confirmation, a command-line interface, and a Streamlit web interface. This provides both a technically modular implementation and a practical user-facing demonstration of content-based movie recommendation.
