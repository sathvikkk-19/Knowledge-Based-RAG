from app.ingestion.loader import load_documents
from app.ingestion.chunker import chunk_documents
from app.vector.embedder import LocalEmbedder


def main():
    print("=" * 80)
    print("LOCAL EMBEDDING TEST")
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

    print()
    print("Loading local embedding model...")

    embedder = LocalEmbedder()

    embedding = embedder.embed_text(
        chunk["text"]
    )

    print()
    print(
        f"Embedding dimensions: "
        f"{len(embedding)}"
    )

    print(
        f"First 5 values: "
        f"{embedding[:5]}"
    )

    print()
    print("Local embedding successful.")


if __name__ == "__main__":
    main()
