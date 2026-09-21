from app.ingestion.chunker import chunk_documents
from app.ingestion.loader import load_documents


def main():
    documents = load_documents("data/documents")

    print(f"Documents loaded: {len(documents)}")

    for document in documents:
        print(
            f"- {document['document_id']}: "
            f"{len(document['text'])} characters"
        )

    chunks = chunk_documents(documents)

    print(f"\nChunks created: {len(chunks)}")

    for chunk in chunks:
        print("\n" + "=" * 80)
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"Document: {chunk['document_id']}")
        print(f"Chunk index: {chunk['chunk_index']}")
        print(f"Text: {chunk['text']}")


if __name__ == "__main__":
    main()
