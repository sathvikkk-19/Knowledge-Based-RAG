import re

from app.ingestion.extractor import ExtractionResult


ALLOWED_RELATIONSHIPS = {
    "PROVIDED_BY": {
        ("Product", "Company"),
        ("Component", "Company"),
        ("Technology", "Company"),
    },
    "DEPENDS_ON": {
        ("Product", "Component"),
        ("Product", "Technology"),
        ("Component", "Component"),
        ("Component", "Technology"),
    },
    "USES": {
        ("Product", "Technology"),
        ("Product", "Component"),
        ("Component", "Technology"),
    },
    "INTEGRATES_WITH": {
        ("Product", "Product"),
        ("Product", "Component"),
        ("Product", "Technology"),
        ("Component", "Product"),
        ("Component", "Component"),
        ("Component", "Technology"),
        ("Technology", "Technology"),
    },
    "COMPATIBLE_WITH": {
        ("Product", "Technology"),
        ("Product", "Version"),
        ("Technology", "Technology"),
        ("Technology", "Version"),
    },
    "REQUIRES": {
        ("Product", "Component"),
        ("Product", "Technology"),
        ("Component", "Component"),
        ("Component", "Technology"),
    },
    "PART_OF": {
        ("Component", "Product"),
        ("Component", "Component"),
    },
    "HAS_FEATURE": {
        ("Product", "Feature"),
        ("Version", "Feature"),
    },
    "VERSION_OF": {
        ("Version", "Product"),
        ("Version", "Technology"),
        ("Version", "Component"),
    },
    "REPLACED_BY": {
        ("Product", "Product"),
        ("Version", "Version"),
        ("Technology", "Technology"),
        ("Component", "Component"),
    },
}


EVIDENCE_PATTERNS = {
    "PROVIDED_BY": [
        r"\bdeveloped by\b",
        r"\bprovided by\b",
        r"\bcreated by\b",
        r"\bmaintained by\b",
    ],
    "DEPENDS_ON": [
        r"\bdepends on\b",
        r"\bdepends upon\b",
        r"\bdependent on\b",
    ],
    "USES": [
        r"\buses\b",
        r"\butilizes\b",
        r"\busing\b",
    ],
    "INTEGRATES_WITH": [
        r"\bintegrates with\b",
        r"\bintegration with\b",
        r"\bworks with\b",
    ],
    "COMPATIBLE_WITH": [
        r"\bcompatible with\b",
        r"\bcompatibility with\b",
    ],
    "REQUIRES": [
        r"\brequires\b",
        r"\brequired\b",
        r"\bneeds\b",
        r"\bmust have\b",
    ],
    "PART_OF": [
        r"\bpart of\b",
        r"\bcomponent of\b",
        r"\bbelongs to\b",
        r"\bcontained in\b",
    ],
    "HAS_FEATURE": [
        r"\bintroduced\b",
        r"\bfeatures\b",
        r"\bincludes\b",
        r"\bprovides\b",
    ],
    "VERSION_OF": [
        r"\bversion of\b",
        r"\bversion\b",
    ],
    "REPLACED_BY": [
        r"\breplaced by\b",
        r"\bsuperseded by\b",
    ],
}


class ExtractionValidator:

    def _normalize(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.lower()).strip()

    def _get_sentences(self, source_text: str) -> list[str]:
        sentences = re.split(
            r"(?<=[.!?])\s+",
            source_text,
        )

        return [
            self._normalize(sentence)
            for sentence in sentences
            if sentence.strip()
        ]

    def _entity_aliases(self, entity) -> list[str]:
        aliases = list(
            getattr(entity, "aliases", []) or []
        )

        aliases.append(entity.canonical_name)

        result = []

        for alias in aliases:
            if alias and alias not in result:
                result.append(alias)

        return result

    def _entity_mentioned(
        self,
        sentence: str,
        entity,
    ) -> bool:

        normalized_sentence = self._normalize(sentence)

        for alias in self._entity_aliases(entity):

            normalized_alias = self._normalize(alias)

            if normalized_alias in normalized_sentence:
                return True

        return False

    def _relationship_has_evidence(
        self,
        relationship,
        source_entity,
        target_entity,
        source_text: str,
    ) -> bool:

        sentences = self._get_sentences(source_text)

        patterns = EVIDENCE_PATTERNS.get(
            relationship.relationship_type,
            [],
        )

        for sentence in sentences:

            source_present = self._entity_mentioned(
                sentence,
                source_entity,
            )

            target_present = self._entity_mentioned(
                sentence,
                target_entity,
            )

            if source_present and target_present:

                if not patterns:
                    return True

                if any(
                    re.search(pattern, sentence)
                    for pattern in patterns
                ):
                    return True

        # Handle references such as:
        # "The platform depends on the Acme API Gateway."
        if relationship.relationship_type == "DEPENDS_ON":

            target_present = any(
                self._entity_mentioned(
                    sentence,
                    target_entity,
                )
                for sentence in sentences
            )

            if target_present:

                source_aliases = {
                    self._normalize(alias)
                    for alias in self._entity_aliases(
                        source_entity
                    )
                }

                if "platform" in source_aliases:

                    for sentence in sentences:

                        if (
                            "the platform" in sentence
                            and any(
                                re.search(
                                    pattern,
                                    sentence,
                                )
                                for pattern in patterns
                            )
                        ):
                            return True

        # Handle "uses PostgreSQL" where the product is
        # referred to through context.
        if relationship.relationship_type == "USES":

            target_present = any(
                self._entity_mentioned(
                    sentence,
                    target_entity,
                )
                for sentence in sentences
            )

            if target_present:

                for sentence in sentences:

                    if re.search(
                        r"\buses\b",
                        sentence,
                    ):
                        return True

        # Handle version relationships.
        if relationship.relationship_type == "VERSION_OF":

            source_name = self._normalize(
                source_entity.canonical_name
            )

            target_name = self._normalize(
                target_entity.canonical_name
            )

            if (
                "version" in source_name
                and target_name in source_name
            ):
                return True

        # Handle compatibility statements where the
        # version entity and base technology may not both
        # appear exactly as canonical names.
        if relationship.relationship_type == "COMPATIBLE_WITH":

            for sentence in sentences:

                if not any(
                    re.search(
                        pattern,
                        sentence,
                    )
                    for pattern in patterns
                ):
                    continue

                source_present = self._entity_mentioned(
                    sentence,
                    source_entity,
                )

                target_present = self._entity_mentioned(
                    sentence,
                    target_entity,
                )

                if source_present or target_present:
                    return True

        # "component of the platform" can establish PART_OF
        # when the component and product are connected through
        # the same sentence/context.
        if relationship.relationship_type == "PART_OF":

            for sentence in sentences:

                if not re.search(
                    r"\bcomponent of\b",
                    sentence,
                ):
                    continue

                source_present = self._entity_mentioned(
                    sentence,
                    source_entity,
                )

                target_present = self._entity_mentioned(
                    sentence,
                    target_entity,
                )

                if source_present or target_present:
                    return True

        return False

    def validate(
        self,
        extraction: ExtractionResult,
        source_text: str,
    ) -> ExtractionResult:

        entity_map = {
            entity.canonical_name: entity
            for entity in extraction.entities
        }

        valid_relationships = []

        for relationship in extraction.relationships:

            source_entity = entity_map.get(
                relationship.source_entity
            )

            target_entity = entity_map.get(
                relationship.target_entity
            )

            if not source_entity or not target_entity:

                print(
                    "Rejected relationship: "
                    "entity could not be resolved."
                )

                print(
                    f"  {relationship.source_entity}"
                    f" --[{relationship.relationship_type}]-->"
                    f" {relationship.target_entity}"
                )

                continue

            pair = (
                source_entity.entity_type,
                target_entity.entity_type,
            )

            allowed_pairs = ALLOWED_RELATIONSHIPS.get(
                relationship.relationship_type,
                set(),
            )

            if pair not in allowed_pairs:

                print(
                    "Rejected relationship: "
                    "invalid entity-type combination."
                )

                print(
                    f"  {relationship.source_entity}"
                    f" --[{relationship.relationship_type}]-->"
                    f" {relationship.target_entity}"
                )

                continue

            if not self._relationship_has_evidence(
                relationship,
                source_entity,
                target_entity,
                source_text,
            ):

                print(
                    "Rejected relationship: "
                    "no sentence-level evidence."
                )

                print(
                    f"  {relationship.source_entity}"
                    f" --[{relationship.relationship_type}]-->"
                    f" {relationship.target_entity}"
                )

                continue

            valid_relationships.append(
                relationship
            )

        extraction.relationships = valid_relationships

        return extraction
