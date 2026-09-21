import json

from groq import Groq

from app.config import GROQ_API_KEY
from app.ingestion.extractor import ExtractionResult
from app.llm.provider import LLMProvider


class GroqProvider(LLMProvider):
    name = "groq"

    def __init__(self):
        self.client = None

        if GROQ_API_KEY:
            self.client = Groq(
                api_key=GROQ_API_KEY
            )

    def is_available(self) -> bool:
        return self.client is not None

    def extract(self, text: str) -> ExtractionResult:
        if not self.client:
            raise RuntimeError(
                "Groq API key is not configured."
            )

        schema = ExtractionResult.model_json_schema()

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": """
You extract structured knowledge from enterprise documents.

Allowed entity types:
Product, Component, Company, API, Technology,
Version, Feature, Document.

Allowed relationship types:
DEPENDS_ON, USES, PROVIDED_BY, INTEGRATES_WITH,
COMPATIBLE_WITH, REQUIRES, PART_OF, HAS_FEATURE,
VERSION_OF, REPLACED_BY.

Rules:

1. Extract only information explicitly supported by the text.
2. Never invent entities or relationships.
3. Use canonical entity names.
4. Put alternative names in aliases.
5. Relationship source_entity and target_entity must
   exactly match entity canonical_name values.
6. Confidence must be between 0.0 and 1.0.
7. Return empty lists when no valid information exists.
8. Do not create relationships merely because entities
   appear together in a sentence.
""",
                },
                {
                    "role": "user",
                    "content": text,
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "extraction_result",
                    "strict": True,
                    "schema": schema,
                },
            },
            temperature=0,
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError(
                "Groq returned an empty response."
            )

        data = json.loads(content)

        return ExtractionResult.model_validate(data)
