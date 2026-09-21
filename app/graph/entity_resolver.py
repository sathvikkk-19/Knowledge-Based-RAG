import re
from difflib import SequenceMatcher

from app.ingestion.extractor import Entity


def normalize_name(name: str) -> str:
    normalized = name.lower().strip()

    normalized = re.sub(
        r"[^a-z0-9]+",
        " ",
        normalized,
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    )

    return normalized.strip()


def similarity_score(
    first: str,
    second: str,
) -> float:
    return SequenceMatcher(
        None,
        normalize_name(first),
        normalize_name(second),
    ).ratio()


class EntityResolver:
    def __init__(
        self,
        similarity_threshold: float = 0.90,
    ):
        self.similarity_threshold = (
            similarity_threshold
        )

        self.entities: dict[str, Entity] = {}

    def resolve(
        self,
        entity: Entity,
    ) -> str:

        normalized = normalize_name(
            entity.canonical_name
        )

        if normalized in self.entities:
            existing = self.entities[normalized]

            for alias in entity.aliases:
                if alias not in existing.aliases:
                    existing.aliases.append(alias)

            return existing.canonical_name

        best_match = None
        best_score = 0.0

        for existing_normalized, existing in (
            self.entities.items()
        ):
            if existing.entity_type != entity.entity_type:
                continue

            score = similarity_score(
                entity.canonical_name,
                existing.canonical_name,
            )

            if score > best_score:
                best_score = score
                best_match = existing

        if (
            best_match is not None
            and best_score >= self.similarity_threshold
        ):
            if (
                entity.canonical_name
                not in best_match.aliases
                and entity.canonical_name
                != best_match.canonical_name
            ):
                best_match.aliases.append(
                    entity.canonical_name
                )

            for alias in entity.aliases:
                if alias not in best_match.aliases:
                    best_match.aliases.append(alias)

            return best_match.canonical_name

        self.entities[normalized] = entity

        return entity.canonical_name

    def resolve_all(
        self,
        entities: list[Entity],
    ) -> dict[str, str]:

        mappings = {}

        for entity in entities:
            canonical = self.resolve(entity)

            mappings[
                entity.canonical_name
            ] = canonical

        return mappings
