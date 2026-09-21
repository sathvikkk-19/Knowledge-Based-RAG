from app.graph.neo4j_client import Neo4jClient
from app.vector.pgvector_client import PostgresClient


def main():
    neo4j = Neo4jClient()
    postgres = PostgresClient()

    try:
        print(neo4j.verify_connection())

        print(postgres.verify_connection())

        postgres.enable_pgvector()
        print("pgvector extension enabled successfully")

    finally:
        neo4j.close()
        postgres.close()


if __name__ == "__main__":
    main()
