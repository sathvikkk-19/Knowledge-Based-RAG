from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.context_fusion import ContextFusion


def main():

    retriever = HybridRetriever()
    fusion = ContextFusion()

    question = (
        "What technologies does the Acme Cloud Platform "
        "require, and what versions are supported?"
    )

    result = retriever.retrieve(question)

    context = fusion.fuse(
        question=question,
        vector_results=result["vector_results"],
        graph_results=result["graph_results"],
    )

    print("=" * 80)
    print("CONTEXT FUSION TEST")
    print("=" * 80)

    print("\nQUESTION")
    print(question)

    print("\nVECTOR CONTEXT")
    print("-" * 80)

    for item in context["vector_context"]:
        print(
            f"Chunk: {item['chunk_id']}"
        )
        print(
            f"Similarity: {item['similarity']}"
        )
        print(item["content"])
        print()

    print("\nGRAPH CONTEXT")
    print("-" * 80)

    print(
        "Resolved entities:",
        context["graph_context"]["resolved_entities"]
    )

    print(
        "Paths:",
        len(context["graph_context"]["paths"])
    )

    retriever.close()


if __name__ == "__main__":
    main()
