import time

from app.ingestion.cache import (
    load_cached_extraction,
    save_extraction,
)
from app.ingestion.extractor import ExtractionResult
from app.llm.gemini_provider import GeminiProvider
from app.llm.groq_provider import GroqProvider


class LLMRouter:
    def __init__(self):
        self.providers = [
            GeminiProvider(),
            GroqProvider(),
        ]

    def extract(
        self,
        text: str,
    ) -> tuple[ExtractionResult, str]:

        # ---------------------------------------------------------
        # 1. Check cache first
        # ---------------------------------------------------------

        cached = load_cached_extraction(text)

        if cached is not None:
            print(
                "Using cached extraction."
            )

            return cached, "cache"

        # ---------------------------------------------------------
        # 2. No cache - call providers
        # ---------------------------------------------------------

        errors = []

        for provider in self.providers:

            if not provider.is_available():
                continue

            try:
                print(
                    f"Trying LLM provider: "
                    f"{provider.name}"
                )

                result = provider.extract(
                    text
                )

                print(
                    f"Successful provider: "
                    f"{provider.name}"
                )

                # -------------------------------------------------
                # 3. Save successful extraction
                # -------------------------------------------------

                save_extraction(
                    text=text,
                    extraction=result,
                    provider=provider.name,
                )

                print(
                    "Extraction saved to cache."
                )

                return result, provider.name

            except Exception as exc:

                error_message = (
                    f"{provider.name}: "
                    f"{type(exc).__name__}: {exc}"
                )

                errors.append(
                    error_message
                )

                print(
                    f"Provider failed: "
                    f"{error_message}"
                )

                time.sleep(0.5)

        if not errors:
            raise RuntimeError(
                "No LLM providers are configured."
            )

        raise RuntimeError(
            "All configured LLM providers failed.\n"
            + "\n".join(errors)
        )
