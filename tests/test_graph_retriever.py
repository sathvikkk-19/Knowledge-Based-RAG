from app.graph.graph_retriever import GraphRetriever


def main():
    print("=" * 80)
    print("GRAPH RETRIEVER TEST")
    print("=" * 80)

    retriever = GraphRetriever()

    try:
        entity_name = "Acme Cloud Platform"

        print()
        print(
            f"Starting entity: {entity_name}"
        )

        results = retriever.get_neighbors(
            entity_name=entity_name,
            max_hops=2,
        )

        print()
        print(
            f"Retrieved {len(results)} graph paths."
        )

        for index, result in enumerate(
            results,
            start=1,
        ):
            print()
            print(
                f"Path #{index}"
            )

            print()
            print("Nodes:")

            for node in result["nodes"]:
                print(
                    f"  - "
                    f"{node['entity_type']}: "
                    f"{node['name']}"
                )

            print()
            print("Relationships:")

            for relationship in result[
                "relationships"
            ]:
                print(
                    f"  - "
                    f"{relationship['type']} "
                    f"(confidence="
                    f"{relationship['confidence']})"
                )

                print(
                    f"    chunk="
                    f"{relationship['source_chunk_id']}"
                )

    finally:
        retriever.close()


if __name__ == "__main__":
    main()
