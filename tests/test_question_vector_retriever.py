from app.vector.question_vector_retriever import QuestionVectorRetriever


def main():

    print("=" * 80)
    print("QUESTION ? VECTOR RETRIEVAL TEST")
    print("=" * 80)

    question = (
        "What database does the Acme Cloud Platform use?"
    )

    print()
    print(f"Question: {question}")

    retriever = QuestionVectorRetriever()

    results = retriever.retrieve(
        question,
        limit=5,
    )

    print()
    print("=" * 80)
    print("VECTOR SEARCH RESULTS")
    print("=" * 80)

    print()
    print(f"Retrieved {len(results)} chunks.")

    for index, result in enumerate(
        results,
        start=1,
    ):

        print()
        print("-" * 80)
        print(f"Result #{index}")
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
        print(result["content"])

    retriever.close()


if __name__ == "__main__":
    main()
