from app.graph.question_entity_resolver import QuestionEntityResolver


def main():

    print("=" * 80)
    print("QUESTION ENTITY RESOLUTION TEST")
    print("=" * 80)

    resolver = QuestionEntityResolver()

    test_entities = [
        "Acme Cloud Platform",
        "acme cloud platform",
        "platform",
        "Acme API Gateway",
        "PostgreSQL",
        "Something That Does Not Exist",
    ]

    for name in test_entities:

        print()
        print("-" * 80)
        print(f"INPUT: {name}")

        result = resolver.resolve(name)

        if result:

            print("RESOLVED:")
            print(f"  Entity ID:      {result['entity_id']}")
            print(f"  Canonical name: {result['canonical_name']}")
            print(f"  Entity type:    {result['entity_type']}")
            print(f"  Aliases:        {result['aliases']}")

        else:

            print("NOT FOUND")

    resolver.close()


if __name__ == "__main__":
    main()
