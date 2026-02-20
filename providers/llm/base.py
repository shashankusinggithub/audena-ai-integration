from abc import ABC, abstractmethod
from core.models import ProviderIntentResponse


class LLMProvider(ABC):

    @abstractmethod
    def classify(self, transcript: str) -> ProviderIntentResponse:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass
