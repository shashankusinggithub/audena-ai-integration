from abc import ABC, abstractmethod
from core.models import STTResult


class STTProvider(ABC):

    @abstractmethod
    def transcribe(self, audio_path: str) -> STTResult:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass
