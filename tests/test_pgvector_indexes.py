from app.vector.pgvector_store import PgVectorStore


def main():
    print("=" * 80)
    print("PGVECTOR INDEX TEST")
    print("=" * 80)

    store = PgVectorStore()

    try:
        store.initialize()

        rows = store.connection.execute(
            """
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'document_chunks'
            ORDER BY indexname;
            """
        ).fetchall()

        print()

        for row in rows:
            print(f"- {row[0]}")

        print()
        print("Index check complete.")

    finally:
        store.close()


if __name__ == "__main__":
    main()
