from app.retrieval.hybrid_retriever import HybridRetriever


def main():

    retriever = HybridRetriever()

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

        route = result["route"]

        print("\nROUTING")
        print("-" * 80)
        print(f"Route: {route.route.value}")
        print(f"Query type: {route.query_type.value}")
        print(f"Confidence: {route.confidence}")
        print(f"Entities: {route.entities}")

        # --------------------------------------------------
        # VECTOR RESULTS
        # --------------------------------------------------

        print("\nVECTOR RESULTS")
        print("-" * 80)

        for row in result["vector_results"]:
            print(row)

        # --------------------------------------------------
        # GRAPH RESULTS
        # --------------------------------------------------

        graph_results = result["graph_results"]

        print("\nRESOLVED ENTITIES")
        print("-" * 80)

        for entity in graph_results["resolved_entities"]:
            print(
                f"{entity['canonical_name']} "
                f"({entity['entity_type']})"
            )

        print("\nGRAPH PATHS")
        print("-" * 80)

        for index, path in enumerate(
            graph_results["paths"],
            start=1,
        ):

            print(f"\nPath #{index}")

            print("Nodes:")

            for node in path["nodes"]:
                print(
                    f"  - {node['name']} "
                    f"({node['entity_type']})"
                )

            print("Relationships:")

            for relationship in path["relationships"]:
                print(
                    f"  - {relationship['type']} "
                    f"(confidence="
                    f"{relationship['confidence']})"
                )

        print()

    retriever.close()


if __name__ == "__main__":
    main()
