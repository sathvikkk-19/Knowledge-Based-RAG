from app.graph.entity_resolver import EntityResolver
from app.ingestion.extractor import Entity


def main():
    resolver = EntityResolver(
        similarity_threshold=0.90
    )

    entities = [
        Entity(
            entity_type="Company",
            canonical_name="Acme Corporation",
        ),
        Entity(
            entity_type="Company",
            canonical_name="Acme Corp",
        ),
        Entity(
            entity_type="Company",
            canonical_name="ACME Corporation",
        ),
        Entity(
            entity_type="Technology",
            canonical_name="Kubernetes",
        ),
        Entity(
            entity_type="Technology",
            canonical_name="PostgreSQL",
        ),
    ]

    mappings = resolver.resolve_all(
        entities
    )

    print("ENTITY RESOLUTION")
    print("=" * 80)

    for original, canonical in mappings.items():
        print(
            f"{original} -> {canonical}"
        )

    print()
    print("CANONICAL ENTITIES")
    print("=" * 80)

    for entity in resolver.entities.values():
        print(
            f"- {entity.entity_type}: "
            f"{entity.canonical_name}"
        )

        if entity.aliases:
            print(
                f"  Aliases: {entity.aliases}"
            )


if __name__ == "__main__":
    main()
