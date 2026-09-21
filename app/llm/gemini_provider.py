from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY
from app.ingestion.extractor import ExtractionResult
from app.llm.provider import LLMProvider


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self):
        self.client = None

        if GEMINI_API_KEY:
            self.client = genai.Client(
                api_key=GEMINI_API_KEY
            )

    def is_available(self) -> bool:
        return self.client is not None

    def extract(self, text: str) -> ExtractionResult:
        if not self.client:
            raise RuntimeError(
                "Gemini API key is not configured."
            )

        response = self.client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction="""
You are extracting a controlled knowledge graph
from an enterprise document.

Your output must follow the provided schema exactly.

ONTOLOGY
---------

Allowed entity types:

Product
Component
Company
API
Technology
Version
Feature
Document


Allowed relationship types:

DEPENDS_ON
USES
PROVIDED_BY
INTEGRATES_WITH
COMPATIBLE_WITH
REQUIRES
PART_OF
HAS_FEATURE
VERSION_OF
REPLACED_BY


ENTITY RULES
------------

1. Only create entities that are explicitly supported
   by the document.

2. Do not invent entities.

3. Use the most specific entity type possible.

4. A product such as:
   "Acme Cloud Platform"
   must be Product.

5. A company such as:
   "Acme Technologies"
   must be Company.

6. A database, framework, operating system, platform,
   runtime, or infrastructure technology such as:
   PostgreSQL
   Kubernetes
   must be Technology unless it is clearly a Product,
   Component, or API.

7. Version numbers must NEVER be classified as Technology.

8. A standalone version number such as:
   "3.0"
   must be Version only when the document clearly
   associates it with a product or technology.

9. When a version belongs to another entity, create a
   descriptive canonical version name containing its
   parent entity.

   Example:

   Product:
   Acme Cloud Platform

   Version:
   Acme Cloud Platform 3.0

   Do NOT create a generic Version node called:
   3.0

10. Similarly:

   Technology:
   Kubernetes

   Version:
   Kubernetes 1.30

   Do NOT create a generic Version node called:
   1.30

11. Put the original short version expression into aliases.

   Example:

   canonical_name:
   Acme Cloud Platform 3.0

   aliases:
   ["3.0", "version 3.0"]

12. A version should have a VERSION_OF relationship
   pointing to its parent Product or Technology.

13. Features such as:
   improved API management
   automated deployment
   centralized monitoring

   should be Feature entities.

14. Do not create an entity simply because a number,
   adjective, or common word appears in the text.

15. Do not create duplicate entities for the same concept.


RELATIONSHIP RULES
------------------

1. Only create relationships explicitly supported
   by the document.

2. Never invent relationships.

3. source_entity and target_entity MUST exactly match
   an entity's canonical_name.

4. If a Product has a version:

   Acme Cloud Platform 3.0
       VERSION_OF
   Acme Cloud Platform

5. If a Technology has a version:

   Kubernetes 1.30
       VERSION_OF
   Kubernetes

6. If a version introduces features:

   Acme Cloud Platform 3.0
       HAS_FEATURE
   automated deployment

7. If a product depends on a component:

   Acme Cloud Platform
       DEPENDS_ON
   Acme API Gateway

8. If a product uses a technology:

   Acme Cloud Platform
       USES
   PostgreSQL

9. If a product requires a technology:

   Acme Cloud Platform
       REQUIRES
   Kubernetes

10. Do not create a relationship merely because two
    entities occur in the same sentence.

11. Confidence must be between 0.0 and 1.0.

12. Use high confidence only when the relationship is
    directly supported by the text.
""",
                response_mime_type="application/json",
                response_schema=ExtractionResult,
            ),
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return ExtractionResult.model_validate_json(
            response.text
        )
