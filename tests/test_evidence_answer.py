from app.retrieval.hybrid_retriever import HybridRetriever
from app.llm.answer_generator import AnswerGenerator


def main():

    retriever = HybridRetriever()
    generator = AnswerGenerator()

    question = (
        "What technologies does the Acme Cloud Platform "
        "require, and what versions are supported?"
    )

    print("=" * 80)
    print("EVIDENCE-BACKED ANSWER TEST")
    print("=" * 80)

    print("\nQUESTION")
    print(question)

    result = retriever.retrieve(question)

    generated = generator.generate(
        question=question,
        vector_results=result["vector_results"],
        graph_results=result["graph_results"],
    )

    print("\nROUTE")
    print("-" * 80)
    print(result["route"].route.value)

    print("\nFINAL ANSWER")
    print("-" * 80)
    print(generated["answer"])

    print("\nSOURCE CHUNKS")
    print("-" * 80)

    for source in generated["sources"]:
        print(f"- {source}")

    print("\nGRAPH EVIDENCE")
    print("-" * 80)

    for evidence in generated["graph_evidence"]:

        nodes = evidence["nodes"]

        names = [
            node.get("name", "")
            for node in nodes
        ]

        print(
            f"{' -> '.join(names)} "
            f"[{evidence['relationship']}] "
            f"(confidence={evidence['confidence']})"
        )

    retriever.close()


if __name__ == "__main__":
    main()
