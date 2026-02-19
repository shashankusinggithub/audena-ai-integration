from abc import ABC, abstractmethod

class TTSProvider(ABC):

    @abstractmethod
    def synthesize(self, text: str) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass