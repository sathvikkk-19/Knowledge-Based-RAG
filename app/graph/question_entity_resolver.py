from app.graph.neo4j_client import Neo4jClient


class QuestionEntityResolver:

    def __init__(self):
        self.graph = Neo4jClient()

    def resolve(self, entity_name: str):

        entity_name = entity_name.strip()

        if not entity_name:
            return None

        query = """
        MATCH (e:Entity)
        WHERE toLower(coalesce(e.name, '')) = toLower($name)
           OR $name IN coalesce(e.aliases, [])
           OR any(
                alias IN coalesce(e.aliases, [])
                WHERE toLower(alias) = toLower($name)
           )
        RETURN
            e.entity_id AS entity_id,
            e.name AS name,
            e.entity_type AS entity_type,
            e.aliases AS aliases
        LIMIT 1
        """

        with self.graph.driver.session() as session:

            result = session.run(
                query,
                name=entity_name,
            ).single()

        if result is None:
            return None

        return {
            "entity_id": result["entity_id"],
            "canonical_name": result["name"],
            "entity_type": result["entity_type"],
            "aliases": result["aliases"] or [],
        }

    def resolve_many(self, entity_names: list[str]):

        resolved = []

        for name in entity_names:

            entity = self.resolve(name)

            if entity is not None:
                resolved.append(entity)

        return resolved

    def close(self):
        self.graph.close()
