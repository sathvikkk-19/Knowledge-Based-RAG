class Embedder:

    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    DIMENSIONS = 384

    def __init__(self):
        print(f"Loading embedding model: {self.MODEL_NAME}")
        try:
            from fastembed import TextEmbedding
            self.backend = "fastembed"
            self.model = TextEmbedding(model_name=self.MODEL_NAME)
        except Exception as e:
            from sentence_transformers import SentenceTransformer
            self.backend = "sentence_transformers"
            self.model = SentenceTransformer(self.MODEL_NAME)

        print(
            f"Embedding model loaded using {self.backend}. Dimensions: {self.DIMENSIONS}"
        )

    def embed(self, text: str) -> list[float]:
        if self.backend == "fastembed":
            embeddings = list(self.model.embed([text]))
            return embeddings[0].tolist()
        else:
            embedding = self.model.encode(
                text,
                normalize_embeddings=True
            )
            return embedding.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if self.backend == "fastembed":
            embeddings = list(self.model.embed(texts))
            return [e.tolist() for e in embeddings]
        else:
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=True
            )
            return embeddings.tolist()
