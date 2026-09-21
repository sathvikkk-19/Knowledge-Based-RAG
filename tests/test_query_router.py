from app.llm.query_router import QueryRouter


QUESTIONS = [
    "What database does the Acme Cloud Platform use?",
    "What is the Acme API Gateway?",
    "What does the Acme Cloud Platform depend on?",
    "What technologies does the Acme Cloud Platform require, and what versions are supported?",
    "What features were introduced in Acme Cloud Platform version 3.0?",
]


def main():

    print("=" * 80)
    print("LLM QUERY ROUTER TEST")
    print("=" * 80)

    router = QueryRouter()

    for question in QUESTIONS:

        print()
        print("-" * 80)
        print(f"QUESTION: {question}")

        result = router.route(question)

        print()
        print(f"Route:      {result.route.value}")
        print(f"Query type: {result.query_type.value}")
        print(f"Confidence: {result.confidence}")
        print(f"Entities:   {result.entities}")
        print(f"Reasoning:  {result.reasoning}")


if __name__ == "__main__":
    main()
