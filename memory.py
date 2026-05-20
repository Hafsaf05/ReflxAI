import chromadb
from sentence_transformers import SentenceTransformer
import uuid

# Load embedding model
model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# Create ChromaDB client
client = chromadb.Client()

# Create collection
collection = client.get_or_create_collection(
    name="failure_memory"
)

def store_memory(task, error):

    embedding = model.encode(error).tolist()

    collection.add(

        documents=[
            f"Task: {task}\nError: {error}"
        ],

        embeddings=[embedding],

        ids=[str(uuid.uuid4())]
    )

def retrieve_memory(query, k=2):

    embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[embedding],
        n_results=k
    )

    return results["documents"]