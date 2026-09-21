from app.vector.pgvector_store import PgVectorStore


def main():

    print("=" * 80)
    print("PGVECTOR CONNECTION TEST")
    print("=" * 80)

    store = PgVectorStore()

    try:
        store.initialize()

        print()
        print(
            "PostgreSQL connection successful."
        )

        print(
            "pgvector extension and table "
            "initialized successfully."
        )

        print(
            f"Current chunks: "
            f"{store.count_chunks()}"
        )

    finally:
        store.close()


if __name__ == "__main__":
    main()
