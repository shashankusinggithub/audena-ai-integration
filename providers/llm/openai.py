from typing import Type
from openai import OpenAI

from core.exceptions import ProviderExecutionError, SemanticValidationError
from providers.llm.base import LLMProvider, ModelT
from resilience.resilient import resilient
from utils.logging import get_logger


class OpenAILLMProvider(LLMProvider):

    def __init__(self, settings, logger=None):
        self.settings = settings
        self.logger = logger or get_logger()
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.breaker = settings.LLM_BREAKER_OPENAI

    @property
    def name(self) -> str:
        return "openai"

    def generate(self, prompt: str, response_model: Type[ModelT]) -> ModelT:

        @resilient(
            retry_attempts=self.settings.LLM_RETRY,
            timeout_seconds=self.settings.LLM_TIMEOUT,
            circuit_breaker=self.breaker,
            retry_exceptions=(ProviderExecutionError, SemanticValidationError),
            step_name="openai_llm",
            logger=self.logger,
        )
        def execute():

            # https://developers.openai.com/cookbook/examples/structured_outputs_intro
            try:
                completion = self.client.beta.chat.completions.parse(
                    model=self.settings.OPENAI_LLM_MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    response_format=response_model,
                )
            except Exception as e:
                raise ProviderExecutionError(f"OpenAI request failed: {e}") from e

            message = completion.choices[0].message

            if getattr(message, "refusal", None):
                raise SemanticValidationError(f"OpenAI refused request: {message.refusal}")

            parsed = message.parsed

            if parsed is None:
                raise SemanticValidationError("OpenAI returned invalid structured output")

            return parsed

        return execute()
