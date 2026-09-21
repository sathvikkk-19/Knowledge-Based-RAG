from abc import ABC, abstractmethod

from app.ingestion.extractor import ExtractionResult


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def extract(self, text: str) -> ExtractionResult:
        pass
