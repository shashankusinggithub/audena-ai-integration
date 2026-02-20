from typing import List
from core.exceptions import (
    AllProvidersFailedError,
    LowConfidenceError,
)
from core.models import PipelineIntentResponse
from utils.logging import get_logger
from providers.llm.base import LLMProvider
class LLMRouter:

    def __init__(
        self,
        providers: List[LLMProvider],
        confidence_threshold: float = 0.4,
        logger=None,
    ):
        self.providers = providers
        self.confidence_threshold = confidence_threshold
        self.logger = logger or get_logger()

    def classify(self, transcript: str) -> PipelineIntentResponse:
        last_error = None
        fallback_triggered = False


        for idx, provider in enumerate[LLMProvider](self.providers):
            try:
                result = provider.classify(transcript)
                
                parsed_result = PipelineIntentResponse.model_validate_json(result)
                parsed_result.provider_used = provider.name
                parsed_result.fallback_triggered = fallback_triggered

                if parsed_result.confidence < self.confidence_threshold:
                    raise LowConfidenceError(
                        f"Low confidence: {parsed_result.confidence} for provider {provider.name}"   
                    )


                self.logger.info(
                    {
                        "message": "LLM step completed",
                        "Note": parsed_result.notes,
                        "provider": provider.name,
                        "intent": parsed_result.intent,
                        "confidence": parsed_result.confidence,
                        "fallback_triggered": parsed_result.fallback_triggered,
                    }
                )

                return parsed_result

            except Exception as e:
                last_error = e
                fallback_triggered = True

                self.logger.error(
                    {
                        "message": "LLM provider failed",
                        "provider": provider.name,
                        "provider_index": idx,
                        "error_type": type(e).__name__,
                        "error": str(e),
                        "fallback_to_next": idx < len(self.providers) - 1,
                    },
                    exc_info=True,
                )
                continue

        self.logger.error(
            {
                "message": "All LLM providers failed",
                "last_error_type": type(last_error).__name__ if last_error else None,
                "last_error": str(last_error) if last_error else None,
            }
        )

        raise AllProvidersFailedError("All LLM providers failed") from last_error
