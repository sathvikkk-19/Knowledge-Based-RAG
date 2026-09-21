from app.ingestion.chunker import chunk_documents
from app.ingestion.loader import load_documents
from app.llm.router import LLMRouter


def main():
    documents = load_documents("data/documents")
    chunks = chunk_documents(documents)

    if not chunks:
        raise RuntimeError(
            "No chunks were created."
        )

    first_chunk = chunks[0]

    print("Testing extraction on:")
    print(
        f"Document: "
        f"{first_chunk['document_id']}"
    )
    print(
        f"Chunk ID: "
        f"{first_chunk['chunk_id']}"
    )
    print()
    print(first_chunk["text"])
    print()

    router = LLMRouter()

    result, provider = router.extract(
        first_chunk["text"]
    )

    print()
    print("=" * 80)
    print(f"PROVIDER USED: {provider}")

    print()
    print("ENTITIES")

    for entity in result.entities:
        print(
            f"- {entity.entity_type}: "
            f"{entity.canonical_name}"
        )

        if entity.aliases:
            print(
                f"  Aliases: "
                f"{entity.aliases}"
            )

    print()
    print("RELATIONSHIPS")

    for relationship in result.relationships:
        print(
            f"- {relationship.source_entity} "
            f"--[{relationship.relationship_type}]--> "
            f"{relationship.target_entity} "
            f"(confidence="
            f"{relationship.confidence})"
        )


if __name__ == "__main__":
    main()
