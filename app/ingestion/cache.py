import hashlib
import json
from pathlib import Path

from app.ingestion.extractor import ExtractionResult


CACHE_DIR = Path("data/cache")


def get_text_hash(text: str) -> str:
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def get_cache_path(text: str) -> Path:
    text_hash = get_text_hash(text)

    return CACHE_DIR / f"{text_hash}.json"


def load_cached_extraction(
    text: str,
) -> ExtractionResult | None:

    cache_path = get_cache_path(text)

    if not cache_path.exists():
        return None

    try:
        data = json.loads(
            cache_path.read_text(
                encoding="utf-8"
            )
        )

        extraction_data = data.get(
            "extraction"
        )

        if not extraction_data:
            return None

        return ExtractionResult.model_validate(
            extraction_data
        )

    except Exception:
        return None


def save_extraction(
    text: str,
    extraction: ExtractionResult,
    provider: str,
) -> None:

    CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    cache_path = get_cache_path(text)

    data = {
        "text_hash": get_text_hash(text),
        "provider": provider,
        "extraction": extraction.model_dump(),
    }

    cache_path.write_text(
        json.dumps(
            data,
            indent=2,
        ),
        encoding="utf-8",
    )
