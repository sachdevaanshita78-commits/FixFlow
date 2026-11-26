from sentence_transformers import SentenceTransformer

DEFAULT_MODEL = "sentence-transformers/all-mpnet-base-v2"


class EmbeddingService:

    def __init__(self):
        self._models = {}

    def _get(self, model_name=DEFAULT_MODEL):
        if model_name not in self._models:
            self._models[model_name] = SentenceTransformer(model_name)

        return self._models[model_name]

    def generate_embeddings(self, texts, model_name=DEFAULT_MODEL):
        model = self._get(model_name)

        return model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )


embedding_service = EmbeddingService()