import os
from pathlib import Path

from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

from ingestion import ingest_directory
from chunking import chunk_all

COLLECTION = "fixflow"
MODEL_NAME = "BAAI/bge-m3"
VECTOR_SIZE = 1024
BATCH_SIZE = 16
UPSERT_BATCH = 64
project_root = Path(__file__).resolve().parent.parent

def get_secret(name: str) -> str | None:
    """Read from environment variables, or from Colab Secrets if running in Colab."""
    value = os.getenv(name)
    if value:
        return value
    else:
        return None


QDRANT_URL = get_secret("QDRANT_URL")
QDRANT_API_KEY = get_secret("QDRANT_API_KEY")

if not QDRANT_URL or not QDRANT_API_KEY:
    raise RuntimeError(
        "Set QDRANT_URL and QDRANT_API_KEY (environment variables or Colab Secrets)."
    )

model = SentenceTransformer(MODEL_NAME)
model.max_seq_length = 512
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=60)


def build_index():
    documents, errors = ingest_directory(str(project_root / "aurora_bank_documents"))
    chunks = chunk_all(documents)

    # Rebuild from scratch each run (fine at this size, avoids duplicates)
    if client.collection_exists(COLLECTION):
        client.delete_collection(COLLECTION)

    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=models.VectorParams(
            size=VECTOR_SIZE,
            distance=models.Distance.COSINE,
        ),
    )

    # Payload index so filtering by document is fast on the server
    client.create_payload_index(
        collection_name=COLLECTION,
        field_name="document_id",
        field_schema=models.PayloadSchemaType.KEYWORD,
    )

    vectors = model.encode(
        [c["text"] for c in chunks],
        batch_size=BATCH_SIZE,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    points = [
        models.PointStruct(
            id=chunk["id"],
            vector=vector.tolist(),
            payload={**chunk["metadata"], "text": chunk["text"]},
        )
        for chunk, vector in zip(chunks, vectors)
    ]

    # Upload in batches so each request to the cloud stays small
    for i in range(0, len(points), UPSERT_BATCH):
        client.upsert(
            collection_name=COLLECTION,
            points=points[i:i + UPSERT_BATCH],
        )

    count = client.count(collection_name=COLLECTION, exact=True).count
    print(f"Stored {len(points)} chunks from {len(documents)} documents")
    print(f"Qdrant Cloud reports {count} points in '{COLLECTION}'")


def search(query: str, top_k: int = 5):
    query_vector = model.encode(query, normalize_embeddings=True).tolist()
    result = client.query_points(
        collection_name=COLLECTION,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )
    return result.points


if __name__ == "__main__":
    build_index()

    questions = [
        "What happens if I don't complete re-KYC?",
        "How do I escalate a complaint to the nodal officer?",
        "How do I block my lost debit card?",
        "What is the UPI daily transaction limit?",
        "What is the penalty for premature FD withdrawal?",
    ]

    for q in questions:
        print(f"\nQ: {q}")
        for hit in search(q, top_k=3):
            p = hit.payload
            print(f"  {hit.score:.3f} | {p['doc_code']} | {p['section']}")