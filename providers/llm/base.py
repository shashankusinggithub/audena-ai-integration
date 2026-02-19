from abc import ABC, abstractmethod
from core.models import IntentResponse


class LLMProvider(ABC):

    @abstractmethod
    def classify(self, transcript: str) -> IntentResponse:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass
