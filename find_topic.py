import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from typing import List, Tuple

# --- Configuration ---
# 1. SET YOUR FILE NAME HERE
YOUR_FILE_NAME = "/Users/stefano/Downloads/diario/unique_searches.txt"  # e.g., "google_queries.txt"
OUTPUT_FILE_NAME = "google_search_topics.csv"

# 2. (Optional) CHOOSE A MODEL
# For search queries, 'all-MiniLM-L6-v2' is fast and effective.
# If your queries are in multiple languages, use 'paraphrase-multilingual-MiniLM-L12-v2'
embedding_model_name = "all-MiniLM-L6-v2"

# 3. (Optional) TUNE MODEL PARAMETERS
# min_topic_size: The minimum number of queries to form a topic.
# With 60k queries, a higher number (e.g., 50-100) prevents thousands of tiny topics.
MIN_TOPIC_SIZE = 150

# --- End of Configuration ---


def load_queries(file_path) -> Tuple[List[str], List[str]]:
    """
    Loads queries and their timestamps from a text file, where each line is:
    'YYYY-MM-DD HH:MM:SS.microseconds: Query Text'

    Returns:
        A tuple of (dates, queries), or (None, None) on error.
    """
    print(f"Loading queries and dates from {file_path}...")
    dates = []
    queries = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Split the line at the first ': ' to separate the timestamp from the query
                parts = line.split(': ', 1)
                
                if len(parts) == 2:
                    # The date part includes the time and microseconds, e.g., '2025-10-19 15:35:45.306154'
                    # The format of the date part is assumed to be 'YYYY-MM-DD HH:MM:SS.microseconds'
                    # We take the first part of the split, then strip the colon and any whitespace
                    date_string = parts[0].strip()
                    query_text = parts[1].strip()
                    
                    if date_string and query_text:
                        dates.append(date_string)
                        queries.append(query_text)
                # Lines that don't match the format will be skipped (e.g., just the date, or missing query)
                
        if not queries:
            print(f"ERROR: No valid 'date: query' lines found in {file_path}.")
            return None, None
            
        print(f"Successfully loaded {len(queries)} queries and dates.")
        return dates, queries
    except FileNotFoundError:
        print(f"ERROR: File not found at {file_path}")
        print("Please make sure the file is in the same directory as the script,")
        print("or provide the full path to the file.")
        return None, None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None, None

def main():
    # Step 1: Load the data
    dates, queries = load_queries(YOUR_FILE_NAME)
    if queries is None:
        return

    # Step 2: Initialize BERTopic
    # We use a specific sentence-transformer model for better embeddings
    embedding_model = SentenceTransformer(embedding_model_name)
    
    # Initialize BERTopic
    # verbose=True shows progress
    # min_topic_size is crucial for tuning
    topic_model = BERTopic(
        embedding_model=embedding_model,
        min_topic_size=MIN_TOPIC_SIZE,
        verbose=True,
        calculate_probabilities=True  # Good for seeing topic confidence
    )

    print("\nStarting BERTopic model training...")
    # These print statements are illustrative and won't match BERTopic's internal verbose output exactly
    print("This may take several minutes for 60,000 queries...")
    print("(Step 1/3) Embedding queries...")
    print("(Step 2/3) Reducing dimensionality...")
    print("(Step 3/3) Clustering queries...")

    # Step 3: Fit the model and transform queries to topics
    # This is the main step. It returns a list of topic IDs for each query.
    topics, probs = topic_model.fit_transform(queries)

    print("\nModel training complete!")

    # Step 4: Review the topics
    print("\n--- Top 20 Topics Found ---")
    topic_info_df = topic_model.get_topic_info()
    print(topic_info_df.head(20))

    # --- IMPORTANT: About Topic -1 ---
    # BERTopic uses HDBSCAN for clustering, which identifies outliers.
    # Any query assigned 'Topic -1' is considered an outlier and does not
    # belong to any specific topic. This is normal and very common with
    # diverse data like search queries (e.g., typos, unique questions).
    outlier_count = topic_info_df[topic_info_df.Topic == -1]['Count'].values[0]
    print(f"\nNote: {outlier_count} queries were classified as outliers (Topic -1).")

    # Step 5: Save results to CSV
    print(f"\nSaving results to {OUTPUT_FILE_NAME}...")

    # Get the human-readable topic names (e.g., "-1_some_word_other_word")
    # We create a map of Topic ID -> Topic Name
    topic_names_map = {row.Topic: row.Name for index, row in topic_info_df.iterrows()}

    probabilities = []
    for topic, prob_array in zip(topics, probs):
        if topic == -1:
            probabilities.append(0.0) # Topic -1 has no probability in BERTopic
        else:
            # probs is a list of arrays (one array per document), 
            # where each element is the probability for a topic (0, 1, 2...)
            # We get the probability corresponding to the assigned topic ID
            probabilities.append(prob_array[topic]) 

    # Now create the DataFrame using the flattened list of probabilities
    # --- MODIFICATION: Added 'Date' column ---
    results_df = pd.DataFrame({
        "Date": dates,  # <-- NEW: Include the date list
        "Query": queries,
        "Topic_ID": topics,
        "Topic_Name": [topic_names_map[t] for t in topics],
        "Probability": probabilities
    })

    # Save to CSV
    results_df.to_csv(OUTPUT_FILE_NAME, index=False, encoding='utf-8')
    print(f"Successfully saved all {len(results_df)} queries with their topics.")

    # Step 6: (Optional) Visualize
    # This will create and open an interactive HTML file in your browser
    try:
        print("\nGenerating interactive topic visualization...")
        # This visualization is great for exploring topics
        fig = topic_model.visualize_topics()
        fig.write_html("topic_visualization.html")
        print("Saved 'topic_visualization.html'. Open this file in your browser to explore.")
    except Exception as e:
        print(f"Could not create visualization: {e}")
        print("You may need to run 'pip install bertopic[visualization]'")


if __name__ == "__main__":
    main()