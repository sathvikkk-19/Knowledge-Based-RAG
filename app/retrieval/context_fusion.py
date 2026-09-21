from typing import Any


class ContextFusion:

    def fuse(
        self,
        question: str,
        vector_results: list[Any],
        graph_results: dict,
    ) -> dict:

        vector_context = []

        for row in vector_results:
            vector_context.append(
                {
                    "chunk_id": row[0],
                    "document_id": row[1],
                    "content": row[2],
                    "section_path": row[3],
                    "document_date": row[4],
                    "similarity": float(row[5]),
                }
            )

        graph_context = {
            "resolved_entities":
                graph_results.get(
                    "resolved_entities", []
                ),
            "paths":
                graph_results.get(
                    "paths", []
                ),
        }

        return {
            "question": question,
            "vector_context": vector_context,
            "graph_context": graph_context,
        }
