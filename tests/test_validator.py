from app.ingestion.loader import load_documents
from app.ingestion.chunker import chunk_documents
from app.ingestion.cache import load_cached_extraction
from app.ingestion.validator import ExtractionValidator


def main():
    print("=" * 80)
    print("EVIDENCE-BASED EXTRACTION VALIDATOR TEST")
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

    extraction = load_cached_extraction(
        chunk["text"]
    )

    if extraction is None:
        raise RuntimeError(
            "No cached extraction found."
        )

    print()
    print(
        f"Original relationships: "
        f"{len(extraction.relationships)}"
    )

    validator = ExtractionValidator()

    validated = validator.validate(
        extraction=extraction,
        source_text=chunk["text"],
    )

    print()
    print(
        f"Valid relationships: "
        f"{len(validated.relationships)}"
    )

    print()
    print("VALID RELATIONSHIPS")
    print("-" * 80)

    for relationship in validated.relationships:
        print(
            f"{relationship.source_entity}"
            f" --[{relationship.relationship_type}]-->"
            f" {relationship.target_entity}"
        )


if __name__ == "__main__":
    main()
