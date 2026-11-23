
import os
from functools import lru_cache

from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

load_dotenv()

COLLECTION = "fixflow"
MODEL_NAME = "BAAI/bge-m3"
VECTOR_SIZE = 1024
UPSERT_BATCH = 64


def required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")

    return value


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    model = SentenceTransformer(MODEL_NAME)
    model.max_seq_length = 512
    return model


@lru_cache(maxsize=1)
def get_client() -> QdrantClient:
    client = QdrantClient(
        url=required_env("QDRANT_URL"),
        api_key=required_env("QDRANT_API_KEY"),
        timeout=60,
    )

    if not client.collection_exists(COLLECTION):
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE,
            ),
        )

    # Index tenant ownership for efficient filtered retrieval.
    for field_name in ("tenant_id", "document_id"):
        client.create_payload_index(
            collection_name=COLLECTION,
            field_name=field_name,
            field_schema=models.PayloadSchemaType.KEYWORD,
        )

    return client


def index_document(chunks: list[dict]) -> int:
    """Replace the vectors for one document, not the entire collection."""
    if not chunks:
        return 0

    tenant_id = str(chunks[0]["metadata"]["tenant_id"])
    document_id = str(chunks[0]["metadata"]["document_id"])

    if any(
        str(chunk["metadata"]["tenant_id"]) != tenant_id
        or str(chunk["metadata"]["document_id"]) != document_id
        for chunk in chunks
    ):
        raise ValueError("All chunks must belong to the same document and tenant.")

    client = get_client()
    model = get_model()

    # Remove stale vectors for this document before reindexing.
    delete_document_vectors(tenant_id, document_id)

    vectors = model.encode(
        [chunk["text"] for chunk in chunks],
        batch_size=16,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    points = []

    for chunk, vector in zip(chunks, vectors):
        payload = {
            **chunk["metadata"],
            "text": chunk["text"],
        }

        points.append(
            models.PointStruct(
                id=chunk["id"],
                vector=vector.tolist(),
                payload=payload,
            )
        )

    for start in range(0, len(points), UPSERT_BATCH):
        client.upsert(
            collection_name=COLLECTION,
            points=points[start:start + UPSERT_BATCH],
            wait=True,
        )

    return len(points)


def delete_document_vectors(tenant_id: str, document_id: str) -> None:
    client = get_client()

    client.delete(
        collection_name=COLLECTION,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="tenant_id",
                        match=models.MatchValue(value=str(tenant_id)),
                    ),
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(value=str(document_id)),
                    ),
                ]
            )
        ),
        wait=True,
    )


def search(
    query: str,
    tenant_id: str,
    top_k: int = 5,
) -> list:
    """Retrieve chunks only from the specified tenant."""
    if not query.strip():
        return []

    if not tenant_id:
        raise ValueError("tenant_id is required for tenant-isolated search.")

    client = get_client()
    model = get_model()

    query_vector = model.encode(
        query,
        normalize_embeddings=True,
    ).tolist()

    result = client.query_points(
        collection_name=COLLECTION,
        query=query_vector,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="tenant_id",
                    match=models.MatchValue(value=str(tenant_id)),
                )
            ]
        ),
        limit=top_k,
        with_payload=True,
    )

    return result.points
