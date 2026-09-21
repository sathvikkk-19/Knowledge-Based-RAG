from app.graph.graph_retriever import GraphRetriever


class QuestionGraphRetriever:

    def __init__(self):
        self.retriever = GraphRetriever()

    def retrieve(
        self,
        entities: list[str],
        max_depth: int = 2,
    ) -> dict:

        resolved_entities = []
        all_paths = []
        seen_paths = set()

        for entity_name in entities:

            matches = self.retriever.find_entity(entity_name)

            if not matches:
                print(
                    f"Entity not found in graph: {entity_name}"
                )
                continue

            entity = matches[0]

            resolved_entities.append(
                {
                    "entity_id": entity["entity_id"],
                    "canonical_name": entity["name"],
                    "entity_type": entity["entity_type"],
                    "aliases": entity.get("aliases") or [],
                }
            )

            paths = self.retriever.get_neighbors(
                entity["name"],
                max_hops=max_depth,
            )

            for path in paths:

                nodes = path.get("nodes", [])
                relationships = path.get("relationships", [])

                if not nodes or not relationships:
                    continue

                # Remove cycles where the path returns to the
                # starting entity.
                node_names = [
                    node.get("name")
                    for node in nodes
                ]

                if len(node_names) != len(set(node_names)):
                    continue

                # Create a stable key for deduplication.
                path_key = (
                    tuple(node_names),
                    tuple(
                        relationship.get("type")
                        for relationship in relationships
                    ),
                )

                if path_key in seen_paths:
                    continue

                seen_paths.add(path_key)
                all_paths.append(path)

        return {
            "resolved_entities": resolved_entities,
            "paths": all_paths,
        }

    def close(self):
        self.retriever.close()
