from app.ingestion.loader import load_documents
from app.ingestion.chunker import chunk_documents
from app.vector.embedder import LocalEmbedder
from app.vector.pgvector_store import PgVectorStore


def main():
    print("=" * 80)
    print("VECTOR INGESTION TEST")
    print("=" * 80)

    documents = load_documents(
        "data/documents"
    )

    chunks = chunk_documents(
        documents
    )

    if not chunks:
        raise RuntimeError(
            "No chunks were created."
        )

    chunk = chunks[0]

    print()
    print(
        f"Document: {chunk['document_id']}"
    )

    print(
        f"Chunk ID: {chunk['chunk_id']}"
    )

    embedder = LocalEmbedder()

    print()
    print("Generating embedding...")

    embedding = embedder.embed_text(
        chunk["text"]
    )

    print(
        f"Embedding dimensions: "
        f"{len(embedding)}"
    )

    store = PgVectorStore()

    try:
        store.initialize()

        store.upsert_chunk(
            chunk_id=chunk["chunk_id"],
            document_id=chunk["document_id"],
            content=chunk["text"],
            embedding=embedding,
            section_path=chunk.get(
                "section_path"
            ),
            document_date=chunk.get(
                "document_date"
            ),
        )

        print()
        print(
            "Chunk successfully stored "
            "in pgvector."
        )

        print(
            f"Total chunks in database: "
            f"{store.count_chunks()}"
        )

    finally:
        store.close()


if __name__ == "__main__":
    main()
