import os
import json

from dotenv import load_dotenv
from google import genai

from app.llm.router_schema import (
    QueryRoute,
    RetrievalRoute,
    QueryType,
)


load_dotenv()


ROUTER_PROMPT = """
You are a retrieval routing classifier for a hybrid RAG system.

Your job is to decide whether a user question should be answered using:

GRAPH:
Use when the question requires relationships between entities,
multi-hop reasoning, dependencies, comparisons across entities,
or aggregation over relationships.

VECTOR:
Use when the question asks for a definition, explanation,
policy lookup, or a simple fact that can usually be answered
from one relevant passage.

BOTH:
Use when the question is complex or uncertain and combining
graph relationships with document passages would improve the answer.

Classify the query type as one of:

single_fact
definition
relationship
multi_hop
comparison
aggregation
unknown

Also extract the important entities mentioned in the question.

Return ONLY valid JSON with this structure:

{
  "route": "graph" | "vector" | "both",
  "query_type": "single_fact" | "definition" | "relationship" | "multi_hop" | "comparison" | "aggregation" | "unknown",
  "confidence": 0.0,
  "entities": [],
  "reasoning": ""
}

Rules:

1. confidence must be between 0 and 1.
2. Do not invent entities.
3. Keep reasoning short.
4. Prefer GRAPH for questions requiring two or more relationship hops.
5. Prefer VECTOR for simple factual questions.
6. Use BOTH when the answer needs both relationship structure and source text.
"""


class QueryRouter:

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

    def route(self, question: str) -> QueryRoute:

        prompt = (
            ROUTER_PROMPT
            + "\n\nUser question:\n"
            + question
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        text = response.text.strip()

        # Remove Markdown code fences if the model adds them.
        if text.startswith("```"):
            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:

            raise ValueError(
                f"Router returned invalid JSON: {text}"
            ) from exc

        result = QueryRoute.model_validate(data)

        # Low-confidence fallback.
        if result.confidence < 0.70:
            result.route = RetrievalRoute.BOTH

        return result
