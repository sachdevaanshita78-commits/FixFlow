
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

load_dotenv(override=True)

client = QdrantClient(
    url=os.environ["QDRANT_URL"],
    api_key=os.environ["QDRANT_API_KEY"],
)

COLLECTION = "fixflow"

# Check that the collection exists.
if not client.collection_exists(COLLECTION):
    raise RuntimeError(
        f"Qdrant collection '{COLLECTION}' does not exist."
    )

# Create the index required by the tenant filter.
client.create_payload_index(
    collection_name=COLLECTION,
    field_name="tenant_id",
    field_schema=models.PayloadSchemaType.KEYWORD,
    wait=True,
)

print("Success: tenant_id payload index created.")

# Verify the collection configuration.
info = client.get_collection(COLLECTION)
print("Collection:", COLLECTION)
print("Indexed tenant_id for filtering.")
