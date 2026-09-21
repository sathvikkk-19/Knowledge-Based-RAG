from app.graph.entity_resolver import EntityResolver
from app.graph.graph_writer import GraphWriter
from app.ingestion.chunker import chunk_documents
from app.ingestion.loader import load_documents
from app.llm.router import LLMRouter


def main():
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

    print("=" * 80)
    print("GRAPH INGESTION TEST")
    print("=" * 80)

    print(
        f"Document: {chunk['document_id']}"
    )

    print(
        f"Chunk ID: {chunk['chunk_id']}"
    )

    print()

    router = LLMRouter()

    extraction, provider = router.extract(
        chunk["text"]
    )

    print(
        f"LLM provider: {provider}"
    )

    print(
        f"Entities extracted: "
        f"{len(extraction.entities)}"
    )

    print(
        f"Relationships extracted: "
        f"{len(extraction.relationships)}"
    )

    resolver = EntityResolver(
        similarity_threshold=0.90
    )

    mapping = resolver.resolve_all(
        extraction.entities
    )

    print()
    print("ENTITY MAPPING")
    print("-" * 80)

    for original, canonical in mapping.items():
        print(
            f"{original} -> {canonical}"
        )

    writer = GraphWriter()

    try:
        writer.create_constraints()

        writer.write_extraction(
            extraction=extraction,
            entity_mapping=mapping,
            chunk_id=chunk["chunk_id"],
            document_id=chunk["document_id"],
        )

        print()
        print(
            "Graph ingestion successful."
        )

    finally:
        writer.close()


if __name__ == "__main__":
    main()
