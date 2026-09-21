from typing import Literal

from pydantic import BaseModel, Field


EntityType = Literal[
    "Product",
    "Component",
    "Company",
    "API",
    "Technology",
    "Version",
    "Feature",
    "Document",
]


RelationshipType = Literal[
    "DEPENDS_ON",
    "USES",
    "PROVIDED_BY",
    "INTEGRATES_WITH",
    "COMPATIBLE_WITH",
    "REQUIRES",
    "PART_OF",
    "HAS_FEATURE",
    "VERSION_OF",
    "REPLACED_BY",
]


class Entity(BaseModel):
    entity_type: EntityType
    canonical_name: str = Field(min_length=1)
    aliases: list[str] = Field(default_factory=list)


class Relationship(BaseModel):
    source_entity: str = Field(min_length=1)
    relationship_type: RelationshipType
    target_entity: str = Field(min_length=1)
    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )


class ExtractionResult(BaseModel):
    entities: list[Entity]
    relationships: list[Relationship]
