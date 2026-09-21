from app.llm.router_schema import (
    QueryRoute,
    RetrievalRoute,
    QueryType,
)


def main():
    print("=" * 80)
    print("QUERY ROUTER SCHEMA TEST")
    print("=" * 80)

    route = QueryRoute(
        route=RetrievalRoute.GRAPH,
        query_type=QueryType.MULTI_HOP,
        confidence=0.94,
        entities=[
            "Acme Cloud Platform",
            "Acme API Gateway",
            "PostgreSQL",
        ],
        reasoning=(
            "The question requires following relationships "
            "across multiple entities."
        ),
    )

    print()
    print("Schema validation successful.")
    print()
    print("ROUTE")
    print("-" * 80)
    print(f"Route: {route.route.value}")
    print(f"Query type: {route.query_type.value}")
    print(f"Confidence: {route.confidence}")
    print(f"Entities: {route.entities}")
    print(f"Reasoning: {route.reasoning}")
    print()

    print("JSON OUTPUT")
    print("-" * 80)
    print(route.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
