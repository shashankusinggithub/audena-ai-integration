from google import genai
from core.models import IntentResponse
from core.exceptions import SemanticValidationError
from core.prompts import build_intent_prompt
from providers.llm.base import LLMProvider
from resilience.resilient import resilient


class GeminiLLMProvider(LLMProvider):

    def __init__(self, settings, logger=None):
        self.settings = settings
        self.logger = logger
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.breaker = settings.LLM_BREAKER

    @property
    def name(self) -> str:
        return "gemini"

    def classify(self, transcript: str) -> IntentResponse:

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
                    "response_schema": IntentResponse.model_json_schema(),
                },
            )

            raw_text = response.text

            try:
                parsed = IntentResponse.model_validate_json(raw_text)
            except Exception as e:
                raise SemanticValidationError(
                    f"Invalid structured output from Gemini: {e}"
                )

            return parsed

        return execute()
