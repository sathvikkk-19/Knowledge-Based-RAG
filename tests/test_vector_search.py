from app.vector.embedder import LocalEmbedder
from app.vector.pgvector_store import PgVectorStore


def main():
    print("=" * 80)
    print("VECTOR SEARCH TEST")
    print("=" * 80)

    question = (
        "What database does the Acme Cloud Platform use?"
    )

    print()
    print(f"Question: {question}")

    embedder = LocalEmbedder()

    print()
    print("Embedding question...")

    query_embedding = embedder.embed_text(
        question
    )

    store = PgVectorStore()

    try:
        store.initialize()

        results = store.search(
            query_embedding=query_embedding,
            limit=5,
        )

        print()
        print(
            f"Retrieved {len(results)} chunks."
        )

        print()
        print("=" * 80)
        print("SEARCH RESULTS")
        print("=" * 80)

        for index, row in enumerate(
            results,
            start=1,
        ):
            (
                chunk_id,
                document_id,
                content,
                section_path,
                document_date,
                similarity,
            ) = row

            print()
            print(
                f"Result #{index}"
            )

            print(
                f"Similarity: "
                f"{similarity:.4f}"
            )

            print(
                f"Document: "
                f"{document_id}"
            )

            print(
                f"Chunk ID: "
                f"{chunk_id}"
            )

            print()
            print(content)

            print()
            print("-" * 80)

    finally:
        store.close()


if __name__ == "__main__":
    main()
