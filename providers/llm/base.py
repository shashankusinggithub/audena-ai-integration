from abc import ABC, abstractmethod
from typing import Type, TypeVar
from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)

class LLMProvider(ABC):

    @abstractmethod
    def generate(self, prompt: str, response_model: Type[ModelT]) -> ModelT:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass
