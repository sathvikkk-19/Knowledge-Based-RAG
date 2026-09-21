from app.graph.neo4j_client import Neo4jClient
from app.ingestion.extractor import ExtractionResult


class GraphWriter:
    def __init__(self):
        self.neo4j = Neo4jClient()

    def create_constraints(self):
        query = """
        CREATE CONSTRAINT entity_id_unique IF NOT EXISTS
        FOR (e:Entity)
        REQUIRE e.entity_id IS UNIQUE
        """

        with self.neo4j.driver.session() as session:
            session.run(query).consume()

    def write_extraction(
        self,
        extraction: ExtractionResult,
        entity_mapping: dict[str, str],
        chunk_id: str,
        document_id: str,
    ):
        with self.neo4j.driver.session() as session:

            # ---------------------------------------------------------
            # 1. Write entities
            # ---------------------------------------------------------

            for entity in extraction.entities:

                canonical_name = entity_mapping[
                    entity.canonical_name
                ]

                entity_id = self._create_entity_id(
                    entity.entity_type,
                    canonical_name,
                )

                query = """
                MERGE (e:Entity {entity_id: $entity_id})
                SET
                    e.name = $name,
                    e.entity_type = $entity_type,
                    e.aliases = $aliases
                """

                session.run(
                    query,
                    entity_id=entity_id,
                    name=canonical_name,
                    entity_type=entity.entity_type,
                    aliases=entity.aliases,
                ).consume()

            # ---------------------------------------------------------
            # 2. Write relationships
            # ---------------------------------------------------------

            for relationship in extraction.relationships:

                source_name = entity_mapping.get(
                    relationship.source_entity
                )

                target_name = entity_mapping.get(
                    relationship.target_entity
                )

                if not source_name or not target_name:
                    continue

                source_type = self._get_entity_type(
                    extraction,
                    relationship.source_entity,
                )

                target_type = self._get_entity_type(
                    extraction,
                    relationship.target_entity,
                )

                source_id = self._create_entity_id(
                    source_type,
                    source_name,
                )

                target_id = self._create_entity_id(
                    target_type,
                    target_name,
                )

                relationship_key = (
                    self._create_relationship_key(
                        source_id,
                        relationship.relationship_type,
                        target_id,
                        chunk_id,
                    )
                )

                query = """
                MATCH (source:Entity {entity_id: $source_id})
                MATCH (target:Entity {entity_id: $target_id})
                MERGE (source)-[r:RELATIONSHIP {relationship_key: $relationship_key}]->(target)
                SET
                    r.relationship_type = $relationship_type,
                    r.confidence = $confidence,
                    r.source_chunk_id = $chunk_id,
                    r.document_id = $document_id
                """

                session.run(
                    query,
                    source_id=source_id,
                    target_id=target_id,
                    relationship_key=relationship_key,
                    relationship_type=(
                        relationship.relationship_type
                    ),
                    confidence=relationship.confidence,
                    chunk_id=chunk_id,
                    document_id=document_id,
                ).consume()

    @staticmethod
    def _create_entity_id(
        entity_type: str,
        canonical_name: str,
    ) -> str:
        normalized = (
            canonical_name
            .lower()
            .strip()
        )

        return (
            f"{entity_type}:"
            f"{normalized}"
        )

    @staticmethod
    def _create_relationship_key(
        source_id: str,
        relationship_type: str,
        target_id: str,
        chunk_id: str,
    ) -> str:
        return (
            f"{source_id}|"
            f"{relationship_type}|"
            f"{target_id}|"
            f"{chunk_id}"
        )

    @staticmethod
    def _get_entity_type(
        extraction: ExtractionResult,
        entity_name: str,
    ) -> str:

        for entity in extraction.entities:

            if entity.canonical_name == entity_name:
                return entity.entity_type

        raise ValueError(
            f"Entity type not found for: "
            f"{entity_name}"
        )

    def close(self):
        self.neo4j.close()
