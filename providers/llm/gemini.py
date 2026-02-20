from typing import Type
from google import genai
from pydantic import ValidationError

from core.exceptions import ProviderExecutionError, SemanticValidationError
from providers.llm.base import LLMProvider, ModelT
from resilience.resilient import resilient
from utils.logging import get_logger


class GeminiLLMProvider(LLMProvider):

    def __init__(self, settings, logger=None):
        self.settings = settings
        self.logger = logger or get_logger()
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.breaker = settings.LLM_BREAKER

    @property
    def name(self) -> str:
        return "gemini"

    def generate(self, prompt: str, response_model: Type[ModelT]) -> ModelT:

        @resilient(
            retry_attempts=self.settings.LLM_RETRY,
            timeout_seconds=self.settings.LLM_TIMEOUT,
            circuit_breaker=self.breaker,
            retry_exceptions=(ProviderExecutionError, SemanticValidationError),
            step_name="gemini_llm",
            logger=self.logger,
        )
        def execute():

            try:
                response = self.client.models.generate_content(
                    model=self.settings.GEMINI_LLM_MODEL,
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": response_model.model_json_schema(),
                    },
                )
            except Exception as e:
                raise ProviderExecutionError(f"Gemini request failed: {e}") from e

            try:
                return response_model.model_validate_json(response.text)
            except ValidationError as e:
                raise SemanticValidationError(
                    f"Gemini returned invalid structured output: {e}"
                ) from e

        return execute()
