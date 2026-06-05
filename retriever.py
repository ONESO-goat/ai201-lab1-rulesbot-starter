import chromadb
import traceback
from chromadb.utils import embedding_functions
from config import CHROMA_COLLECTION, CHROMA_PATH, EMBEDDING_MODEL, N_RESULTS

# Embedding function and ChromaDB client are initialized once at module load.
# sentence-transformers downloads the model on first use — this may take
# 30–60 seconds the very first time. Subsequent runs use a local cache.
_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)
_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_or_create_collection(
    name=CHROMA_COLLECTION,
    embedding_function=_ef,
    metadata={"hnsw:space": "cosine"},
)


def get_collection():
    """Return the ChromaDB collection. Used by app.py during ingestion."""
    return _collection


def embed_and_store(chunks):
    """
    Embed a list of chunks and store them in the vector database.

    This function is already implemented — read through it before moving on.

    _collection.add() takes three parallel lists built from the chunks
    returned by chunk_document():
      - documents : raw text strings — ChromaDB's embedding function converts
                    these to vectors automatically using sentence-transformers
      - metadatas : one dict per chunk, stored alongside the vector so that
                    retrieve() can surface which game a result came from
      - ids       : the unique chunk_id strings used to identify each entry

    You don't generate embeddings manually here — you hand over the text
    and ChromaDB handles the vector math.
    """
    _collection.add(
        documents=[c["text"] for c in chunks],
        metadatas=[{"game": c["game"]} for c in chunks],
        ids=[c["chunk_id"] for c in chunks],
    )
    print(f"Stored {_collection.count()} total chunks in the vector database.")


def readable(results):
    ids = results['ids'][0]
    docs = results['documents'][0]
    metadatas = results['metadatas'][0]
    distances = results['distances'][0]

    # Print out a cleanly formatted view
    for idx, (doc_id, doc_text, meta, dist) in enumerate(zip(ids, docs, metadatas, distances), 1):
        print(f"--- MATCH #{idx} ---")
        print(f"ID: {doc_id}")
        print(f"Game: {meta.get('game', 'Unknown')}")
        print(f"Distance Score: {dist:.4f}")
        print(f"Text:\n{doc_text.strip()}\n")
        
def retrieve(query, n_results=N_RESULTS):
    """
    Find the most relevant rule chunks for a user's question.

    TODO — Milestone 2:

    Use _collection.query() to run a semantic search. It takes:
      - query_texts : a list containing your query string
      - n_results   : how many results to return
      - include     : what to return — use ["documents", "metadatas", "distances"]

    Return a list of dicts, each with:
      - "text"     : the chunk text
      - "game"     : the game name (pull this from metadatas)
      - "distance" : the similarity score (lower = more similar for cosine)

    Note: _collection.query() returns nested lists (one per query). You only
    have one query, so you'll want index [0] to get the actual results.
    """
    if _collection.count() == 0:
        return []

    # Your implementation here.
    try:
        test = _collection.query(query_texts=[query], n_results=n_results)
        print(f"INFORMATION: {readable(test)} - {type(test)}")
        print(f"{test['ids']}")
        #assert test.get("game", None) is not None
        l = []
        for i in range(n_results):
            format = {
                "id": '',
                "text": '',
                "game": '',
                'distance': 0.0
            }
            for key, value in test.items():
                print(f"KEY:\n\t\u2022 {key} - \nVALUE:\n\t\u2022 {value}")
                if not value:
                    continue
                if key == 'ids':
                    format['id'] = value[0][i]
                    
                if key == 'document':
                    format['text'] = value[i]
                if key == 'metadatas':
                     
                    format['game'] = value[0][i]['game']
                    
                if key == 'distances':
                    format['distance'] = value[0][i]
                l.append(format)
                
        print(f"\nFORMAT: \n\t\u2022{l}")
        
        return l
    except Exception as ex:
        print(f"\nError during retriving process: \n\t\u2022{ex}")
        traceback.print_exc()
    return []

if __name__ in "__main__":
    retrieve(query="I like to program, why is that?")