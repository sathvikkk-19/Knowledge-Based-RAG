from app.vector.embedder import LocalEmbedder
from app.vector.pgvector_store import PgVectorStore


class VectorRetriever:
    def __init__(self):
        self.embedder = LocalEmbedder()
        self.store = PgVectorStore()
        self.store.initialize()

    def retrieve(
        self,
        question: str,
        limit: int = 5,
    ) -> list[dict]:

        query_embedding = self.embedder.embed_text(
            question
        )

        rows = self.store.search(
            query_embedding=query_embedding,
            limit=limit,
        )

        results = []

        for row in rows:
            (
                chunk_id,
                document_id,
                content,
                section_path,
                document_date,
                similarity,
            ) = row

            results.append(
                {
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "content": content,
                    "section_path": section_path,
                    "document_date": document_date,
                    "similarity": float(similarity),
                }
            )

        return results

    def close(self):
        self.store.close()
