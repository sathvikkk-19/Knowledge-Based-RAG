from app.vector.retriever import VectorRetriever


def main():
    print("=" * 80)
    print("VECTOR RETRIEVER TEST")
    print("=" * 80)

    question = (
        "What database does the Acme Cloud Platform use?"
    )

    retriever = VectorRetriever()

    try:
        results = retriever.retrieve(
            question=question,
            limit=5,
        )

        print()
        print(
            f"Question: {question}"
        )

        print()
        print(
            f"Retrieved {len(results)} results."
        )

        for index, result in enumerate(
            results,
            start=1,
        ):
            print()
            print(
                f"Result #{index}"
            )

            print(
                f"Similarity: "
                f"{result['similarity']:.4f}"
            )

            print(
                f"Document: "
                f"{result['document_id']}"
            )

            print(
                f"Chunk ID: "
                f"{result['chunk_id']}"
            )

            print()
            print(
                result["content"]
            )

            print(
                "-" * 80
            )

    finally:
        retriever.close()


if __name__ == "__main__":
    main()
