from app.graph.question_graph_retriever import QuestionGraphRetriever


def main():

    print("=" * 80)
    print("QUESTION ? GRAPH RETRIEVAL TEST")
    print("=" * 80)

    retriever = QuestionGraphRetriever()

    entities = [
        "Acme Cloud Platform"
    ]

    print()
    print(f"Input entities: {entities}")

    result = retriever.retrieve(
        entities,
        max_depth=2,
    )

    print()
    print("RESOLVED ENTITIES")
    print("-" * 80)

    for entity in result["resolved_entities"]:

        print(
            f"{entity['canonical_name']} "
            f"({entity['entity_type']})"
        )

    print()
    print(f"Retrieved paths: {len(result['paths'])}")

    print()
    print("GRAPH PATHS")
    print("-" * 80)

    for index, path in enumerate(result["paths"], start=1):

        print()
        print(f"Path #{index}")

        print("Nodes:")

        for node in path["nodes"]:

            print(
                f"  - {node['entity_type']}: "
                f"{node['name']}"
            )

        print("Relationships:")

        for relationship in path["relationships"]:

            print(
                f"  - {relationship['type']} "
                f"(confidence={relationship['confidence']})"
            )

            if relationship.get("source_chunk_id"):
                print(
                    f"    chunk={relationship['source_chunk_id']}"
                )

    retriever.close()


if __name__ == "__main__":
    main()
