from neo4j import GraphDatabase

from app.config import (
    NEO4J_PASSWORD,
    NEO4J_URI,
    NEO4J_USERNAME,
)


class Neo4jClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
        )

    def verify_connection(self):
        with self.driver.session() as session:
            result = session.run(
                "RETURN 'Neo4j connection successful' AS message"
            )
            return result.single()["message"]

    def close(self):
        self.driver.close()
