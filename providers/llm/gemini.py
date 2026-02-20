from google import genai
from core.models import ProviderIntentResponse
from core.exceptions import SemanticValidationError
from core.prompts import build_intent_prompt
from providers.llm.base import LLMProvider
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

    def classify(self, transcript: str) -> ProviderIntentResponse:

        @resilient(
            retry_attempts=self.settings.LLM_RETRY,
            timeout_seconds=self.settings.LLM_TIMEOUT,
            circuit_breaker=self.breaker,
            retry_exceptions=(Exception, SemanticValidationError),
            step_name="gemini_llm",
            logger=self.logger,
        )
        def execute():

            prompt = build_intent_prompt(transcript)

            response = self.client.models.generate_content(
                model=self.settings.GEMINI_LLM_MODEL,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ProviderIntentResponse.model_json_schema(),
                },
            )


            return response.text

        return execute()
