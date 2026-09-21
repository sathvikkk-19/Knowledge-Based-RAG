from sentence_transformers import SentenceTransformer

from app.vector.pgvector_store import PgVectorStore


class QuestionVectorRetriever:

    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self):
        print(
            f"Loading embedding model: {self.MODEL_NAME}"
        )

        self.model = SentenceTransformer(
            self.MODEL_NAME
        )

        print(
            f"Embedding model loaded. "
            f"Dimensions: {self.model.get_sentence_embedding_dimension()}"
        )

        self.store = PgVectorStore()

    def retrieve(
        self,
        question: str,
        limit: int = 5,
    ) -> list[dict]:

        if not question or not question.strip():
            return []

        print()
        print("Embedding question...")

        embedding = self.model.encode(
            question,
            normalize_embeddings=True,
        ).tolist()

        rows = self.store.search(
            embedding,
            limit=limit,
        )

        results = []

        for row in rows:

            results.append(
                {
                    "chunk_id": row[0],
                    "document_id": row[1],
                    "content": row[2],
                    "section_path": row[3],
                    "document_date": row[4],
                    "similarity": float(row[5]),
                }
            )

        return results

    def close(self):
        self.store.close()
