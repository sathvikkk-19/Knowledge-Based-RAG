from app.retrieval.hybrid_retriever import HybridRetriever
from app.llm.answer_generator import AnswerGenerator


def main():

    retriever = HybridRetriever()
    generator = AnswerGenerator()

    questions = [
        "What database does the Acme Cloud Platform use?",
        "What does the Acme Cloud Platform depend on?",
        "What technologies does the Acme Cloud Platform require, and what versions are supported?",
    ]

    for question in questions:

        print("=" * 80)
        print("QUESTION")
        print("=" * 80)
        print(question)

        result = retriever.retrieve(question)

        answer = generator.generate(
            question=question,
            vector_results=result["vector_results"],
            graph_results=result["graph_results"],
        )

        print("\nROUTE")
        print("-" * 80)
        print(result["route"].route.value)

        print("\nFINAL ANSWER")
        print("-" * 80)
        print(answer["answer"])

        print()

    retriever.close()


if __name__ == "__main__":
    main()
