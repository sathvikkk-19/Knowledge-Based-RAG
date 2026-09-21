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

    def get_graph_data(
        self,
        limit: int = 150,
        document_id: str | None = None,
    ) -> dict:
        if document_id:
            query = """
            MATCH (source:Entity)-[r:RELATIONSHIP]->(target:Entity)
            WHERE r.document_id = $document_id
            RETURN
                source.entity_id AS source_id,
                source.name AS source_name,
                source.entity_type AS source_type,
                r.relationship_type AS relationship,
                r.confidence AS confidence,
                r.document_id AS document_id,
                target.entity_id AS target_id,
                target.name AS target_name,
                target.entity_type AS target_type
            LIMIT $limit
            """
            params = {"document_id": document_id, "limit": limit}
        else:
            query = """
            MATCH (source:Entity)-[r:RELATIONSHIP]->(target:Entity)
            RETURN
                source.entity_id AS source_id,
                source.name AS source_name,
                source.entity_type AS source_type,
                r.relationship_type AS relationship,
                r.confidence AS confidence,
                r.document_id AS document_id,
                target.entity_id AS target_id,
                target.name AS target_name,
                target.entity_type AS target_type
            LIMIT $limit
            """
            params = {"limit": limit}

        nodes_map = {}
        links = []

        with self.neo4j.driver.session() as session:
            result = session.run(query, **params)
            for row in result:
                s_id = row["source_id"] or row["source_name"]
                t_id = row["target_id"] or row["target_name"]

                if s_id not in nodes_map:
                    nodes_map[s_id] = {
                        "id": s_id,
                        "name": row["source_name"],
                        "entity_type": row["source_type"] or "Entity",
                    }

                if t_id not in nodes_map:
                    nodes_map[t_id] = {
                        "id": t_id,
                        "name": row["target_name"],
                        "entity_type": row["target_type"] or "Entity",
                    }

                links.append({
                    "source": s_id,
                    "target": t_id,
                    "relationship": row["relationship"],
                    "confidence": row["confidence"] or 1.0,
                    "document_id": row["document_id"],
                })

        return {
            "nodes": list(nodes_map.values()),
            "links": links,
        }

    def close(self):
        self.neo4j.close()
