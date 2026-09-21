from app.llm.query_router import QueryRouter
from app.graph.question_graph_retriever import QuestionGraphRetriever
from app.vector.pgvector_store import PgVectorStore
from app.ingestion.embedder import Embedder


class HybridRetriever:

    def __init__(self):

        self.router = QueryRouter()
        self.graph_retriever = QuestionGraphRetriever()
        self.vector_store = PgVectorStore()
        self.embedder = Embedder()

    def retrieve(
        self,
        question: str,
        vector_limit: int = 5,
        graph_max_hops: int = 2,
        document_id: str | None = None,
    ):

        route = self.router.route(question)

        vector_results = []
        graph_results = {
            "resolved_entities": [],
            "paths": [],
        }

        # --------------------------------------------------
        # VECTOR RETRIEVAL
        # --------------------------------------------------

        if route.route.value in ("vector", "both"):

            query_embedding = self.embedder.embed(
                question
            )

            vector_results = self.vector_store.search(
                query_embedding=query_embedding,
                limit=vector_limit,
                document_id=document_id,
            )

        # --------------------------------------------------
        # GRAPH RETRIEVAL
        # --------------------------------------------------

        if route.route.value in ("graph", "both"):

            graph_results = self.graph_retriever.retrieve(
                entities=route.entities,
                max_depth=graph_max_hops,
            )

        return {
            "question": question,
            "route": route,
            "vector_results": vector_results,
            "graph_results": graph_results,
        }

    def close(self):

        self.graph_retriever.close()
        self.vector_store.close()
