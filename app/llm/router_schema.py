from enum import Enum

from pydantic import BaseModel, Field


class RetrievalRoute(str, Enum):
    GRAPH = "graph"
    VECTOR = "vector"
    BOTH = "both"


class QueryType(str, Enum):
    SINGLE_FACT = "single_fact"
    DEFINITION = "definition"
    RELATIONSHIP = "relationship"
    MULTI_HOP = "multi_hop"
    COMPARISON = "comparison"
    AGGREGATION = "aggregation"
    UNKNOWN = "unknown"


class QueryRoute(BaseModel):
    route: RetrievalRoute = Field(
        description="The retrieval system that should answer the question."
    )

    query_type: QueryType = Field(
        description="The type of question being asked."
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the routing decision."
    )

    entities: list[str] = Field(
        default_factory=list,
        description="Important entities mentioned in the question."
    )

    reasoning: str = Field(
        description="Short explanation for why this route was selected."
    )
