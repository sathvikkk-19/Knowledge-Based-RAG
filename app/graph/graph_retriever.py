from app.graph.neo4j_client import Neo4jClient


class GraphRetriever:
    def __init__(self):
        self.neo4j = Neo4jClient()

    def find_entity(
        self,
        entity_name: str,
    ) -> list[dict]:

        query = """
        MATCH (e:Entity)
        WHERE toLower(e.name) = toLower($entity_name)
           OR any(
                alias IN coalesce(e.aliases, [])
                WHERE toLower(alias) = toLower($entity_name)
           )
        RETURN
            e.entity_id AS entity_id,
            e.name AS name,
            e.entity_type AS entity_type,
            e.aliases AS aliases
        """

        with self.neo4j.driver.session() as session:
            result = session.run(
                query,
                entity_name=entity_name,
            )

            return [
                record.data()
                for record in result
            ]

    def get_neighbors(
        self,
        entity_name: str,
        max_hops: int = 2,
    ) -> list[dict]:

        max_hops = max(
            1,
            min(max_hops, 3),
        )

        query = f"""
        MATCH path =
            (start:Entity)-[*1..{max_hops}]-(connected:Entity)

        WHERE toLower(start.name) = toLower(
            $entity_name
        )

        WITH path

        RETURN DISTINCT
            [
                node IN nodes(path) |
                {{
                    name: node.name,
                    entity_type: node.entity_type
                }}
            ] AS nodes,

            [
                relationship IN relationships(path) |
                {{
                    type: relationship.relationship_type,
                    confidence: relationship.confidence,
                    source_chunk_id:
                        relationship.source_chunk_id,
                    document_id:
                        relationship.document_id
                }}
            ] AS relationships

        LIMIT 50
        """

        with self.neo4j.driver.session() as session:
            result = session.run(
                query,
                entity_name=entity_name,
            )

            return [
                record.data()
                for record in result
            ]

    def close(self):
        self.neo4j.close()
