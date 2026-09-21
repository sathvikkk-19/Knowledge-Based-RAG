from cerebras.cloud.sdk import Cerebras

from app.config import CEREBRAS_API_KEY
from app.ingestion.extractor import ExtractionResult
from app.llm.provider import LLMProvider


class CerebrasProvider(LLMProvider):
    name = "cerebras"

    def __init__(self):
        self.client = None

        if CEREBRAS_API_KEY:
            self.client = Cerebras(
                api_key=CEREBRAS_API_KEY
            )

    def is_available(self) -> bool:
        return self.client is not None

    def extract(self, text: str) -> ExtractionResult:
        if not self.client:
            raise RuntimeError(
                "Cerebras API key is not configured."
            )

        schema = ExtractionResult.model_json_schema()

        response = self.client.chat.completions.create(
            model="gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": """
Extract structured knowledge from the enterprise document.

Only use the entity and relationship types defined by the
provided JSON schema.

Extract only explicitly supported information.
Never invent facts.
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
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError(
                "Cerebras returned an empty response."
            )

        return ExtractionResult.model_validate_json(
            content
        )
