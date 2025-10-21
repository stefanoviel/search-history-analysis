import chromadb
from chromadb.utils import embedding_functions
import time
import os

from tqdm import tqdm

# --- Configuration ---
MODEL_NAME = 'all-MiniLM-L6-v2'
TOP_K = 10
FILE_PATH = '/Users/stefano/Downloads/diario/search_queries.txt'
# --- ChromaDB Configuration ---
CHROMA_PERSIST_DIR = 'chroma_db'
CHROMA_COLLECTION_NAME = 'search_queries'



# --- 2. Load Queries from File (re-used from previous script) ---
def load_queries_from_file(filepath):
    """Reads the search queries from the local file."""
    try:
        with open(filepath, 'r') as f:
            queries = [line.strip() for line in f if line.strip()]
        return queries
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return []
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return []

# --- Main Execution ---
if __name__ == "__main__":
    
    # --- A. Setup ChromaDB Client and Embedding Function ---
    print("Initializing ChromaDB...")
    # This embedding function will download and use the specified model automatically.
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    
    # This creates a client that will store data on disk in the 'chroma_db' directory.
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    
    # --- B. Create or Load the Collection ---
    # The get_or_create_collection method handles both cases for us.
    # We pass our embedding function so Chroma knows how to vectorize the text.
    collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME,
        embedding_function=sentence_transformer_ef
    )
    
    # --- C. Populate the Database (only if it's empty) ---
    if collection.count() == 0:
        print("Collection is empty. Populating with new data...")
        
        
        queries = load_queries_from_file(FILE_PATH)
        if not queries:
            print("Could not load queries. Exiting.")
            exit()
            
        print(f"Adding {len(queries)} queries to the collection. This may take a while...")
        start_time = time.time()
        
        # 2. Add data to ChromaDB
        # We need unique IDs for each entry. A simple string version of the index is fine.
        # ChromaDB handles the embedding and indexing automatically.
        # It's also smart about batching, so we can pass the whole list.
        # Split queries into batches of 5000 for efficient insertion
        batch_size = 5000
        for i in tqdm(range(0, len(queries), batch_size)):
            batch = queries[i:i + batch_size]
            collection.add(
                documents=batch,
                ids=[str(j) for j in range(i, i + len(batch))]
            )
        
        print(f"Database population complete in {time.time() - start_time:.2f} seconds.")
        
        # 3. Clean up the source file
        try:
            os.remove(FILE_PATH)
            print(f"Clean up: Removed source file '{FILE_PATH}'")
        except Exception as e:
            print(f"Could not remove source file: {e}")
    else:
        print(f"Loaded existing collection with {collection.count()} items.")

    # --- D. Interactive Search Loop ---
    print("\n--- Interactive Search Ready ---")
    print("Enter your search query below. Type 'exit' to quit.")
    while True:
        try:
            user_query = input("\nQuery > ")
            if user_query.lower() == 'exit':
                print("Exiting...")
                break
            if not user_query.strip():
                continue

            start_time = time.time()
            results = collection.query(
                query_texts=[user_query],
                n_results=TOP_K
            )
            search_time = time.time() - start_time
            print(f"Search completed in {search_time:.4f} seconds.")
            
            print(f"\nTop {TOP_K} most similar queries found:")
            # The results object contains documents, distances, etc.
            docs = results['documents'][0]
            distances = results['distances'][0]
            
            for rank, (doc, dist) in enumerate(zip(docs, distances)):
                # Chroma uses L2 distance, so we can convert it to a similarity score
                similarity = 1 / (1 + dist)
                print(f"  Rank {rank + 1} | Score: {similarity:.4f} | Query: {doc}")
        
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break
