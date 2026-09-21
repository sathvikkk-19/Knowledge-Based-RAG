import os

from dotenv import load_dotenv
from google import genai

from app.retrieval.context_fusion import ContextFusion


load_dotenv()


ANSWER_PROMPT = """
You are an enterprise RAG assistant.

Answer the user's question using ONLY the provided retrieved context.

The context contains:
1. Vector evidence from source documents.
2. Graph evidence containing entities and relationships.

Rules:
- Do not invent information.
- If the context does not contain enough information, say so.
- Prefer precise answers.
- Use graph relationships when they directly answer the question.
- Use document text when additional explanation is needed.
- Keep the answer concise but useful.
- Do not mention information that is not supported by the context.

USER QUESTION:
{question}

VECTOR CONTEXT:
{vector_context}

GRAPH CONTEXT:
{graph_context}
"""


class AnswerGenerator:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured in the .env file."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash-lite",
        )

        self.fusion = ContextFusion()

    def generate(
        self,
        question: str,
        vector_results,
        graph_results,
    ):

        context = self.fusion.fuse(
            question=question,
            vector_results=vector_results,
            graph_results=graph_results,
        )

        prompt = ANSWER_PROMPT.format(
            question=question,
            vector_context=context["vector_context"],
            graph_context=context["graph_context"],
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        sources = []

        for item in context["vector_context"]:
            chunk_id = item.get("chunk_id")

            if chunk_id and chunk_id not in sources:
                sources.append(chunk_id)

        graph_evidence = []

        for path in context["graph_context"]["paths"]:

            nodes = path.get("nodes", [])
            relationships = path.get(
                "relationships",
                []
            )

            if not nodes or not relationships:
                continue

            for relationship in relationships:

                graph_evidence.append(
                    {
                        "relationship":
                            relationship.get("type"),
                        "confidence":
                            relationship.get("confidence"),
                        "source_chunk_id":
                            relationship.get(
                                "source_chunk_id"
                            ),
                        "nodes": nodes,
                    }
                )

        return {
            "answer": response.text.strip(),
            "sources": sources,
            "graph_evidence": graph_evidence,
            "context": context,
        }
