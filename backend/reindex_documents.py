
import logging

from database import SessionLocal
from models import Document
from supabase_client import supabase, SUPABASE_BUCKET
from rag_service import index_document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fixflow.reindex")


def main():
    db = SessionLocal()

    try:
        documents = db.query(Document).order_by(Document.created_at).all()
        print(f"Found {len(documents)} documents.")

        successful = 0
        failed = 0

        for document in documents:
            try:
                print(f"\nDownloading: {document.filename}")

                content = supabase.storage.from_(SUPABASE_BUCKET).download(
                    document.storage_path
                )

                chunks = index_document(
                    tenant_id=document.tenant_id,
                    document_id=document.id,
                    filename=document.filename,
                    content=content,
                )

                print(
                    f"SUCCESS: {document.filename} — "
                    f"{chunks} chunks indexed"
                )
                successful += 1

            except Exception:
                logger.exception(
                    "Failed to re-index document %s (%s)",
                    document.filename,
                    document.id,
                )
                failed += 1

        print("\n========== RE-INDEX SUMMARY ==========")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Total: {len(documents)}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
