from sentence_transformers import SentenceTransformer

class EmbeddingService:

    def __init__(self):
        self.model = SentenceTransformer(
            "sentence-transformers/all-mpnet-base-v2"
        )

    def generate_embeddings(self, texts):
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embeddings


embedding_service = EmbeddingService()