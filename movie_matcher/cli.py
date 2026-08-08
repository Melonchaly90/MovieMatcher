import sys
import pandas as pd
from movie_matcher.data_loader import load_dataset, clean_dataset
from movie_matcher.matching import resolve_title
from movie_matcher.recommender import recommend_by_genre

def main() -> None:
    print("Loading movie dataset...")
    try:
        df_raw = load_dataset("data/imdb_movie_data.csv")
        df = clean_dataset(df_raw)
    except (FileNotFoundError, ValueError, pd.errors.EmptyDataError, pd.errors.ParserError) as e:
        print(f"Error loading dataset: {e}")
        return

    print("Welcome to Movie Matcher! (Type 'quit' or 'exit' to stop)")
    
    while True:
        try:
            query = input("\nEnter a movie title: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
            
        if query.lower() in ('quit', 'exit'):
            print("Goodbye!")
            break
            
        if not query:
            continue
            
        resolution = resolve_title(df, query)
        status = resolution.get("status")
        
        if status == "exact":
            title = resolution["title"]
            print(f"Found exact match for '{title}'. Finding recommendations...")
            results = recommend_by_genre(df, title, k=3)
            
            if results:
                print("\nTop Recommendations:")
                for i, r in enumerate(results, 1):
                    print(f"{i}. {r['title']} (Similarity: {r['similarity']})")
            else:
                print("No recommendations could be generated.")
                
        elif status == "fuzzy":
            suggestions = resolution["suggestions"]
            top_suggestion = suggestions[0]
            print(f"Did you mean '{top_suggestion}'? (y/n)")
            
            try:
                confirm = input().strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break
                
            if confirm == 'y':
                print(f"Finding recommendations for '{top_suggestion}'...")
                results = recommend_by_genre(df, top_suggestion, k=3)
                
                if results:
                    print("\nTop Recommendations:")
                    for i, r in enumerate(results, 1):
                        print(f"{i}. {r['title']} (Similarity: {r['similarity']})")
                else:
                    print("No recommendations could be generated.")
            else:
                print("No recommendation given.")
                
        elif status == "not_found":
            print(f"No matching movie was found for '{query}'.")

if __name__ == "__main__":
    main()
