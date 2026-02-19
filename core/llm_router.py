from typing import List
from core.exceptions import (
    AllProvidersFailedError,
    LowConfidenceError,
)
from core.models import IntentResponse


class LLMRouter:

    def __init__(
        self,
        providers: List,
        confidence_threshold: float = 0.4,
        logger=None,
    ):
        self.providers = providers
        self.confidence_threshold = confidence_threshold
        self.logger = logger

    def classify(self, transcript: str) -> IntentResponse:
        last_error = None
        fallback_triggered = False


        for idx, provider in enumerate(self.providers):
            try:
                result: IntentResponse = provider.classify(transcript)

                if result.confidence < self.confidence_threshold:
                    raise LowConfidenceError(
                        f"Low confidence: {result.confidence}"
                    )

                result.provider_used = provider.name
                result.fallback_triggered = fallback_triggered

                self.logger.info(
                    {
                        "message": "LLM step completed",
                        "provider": provider.name,
                        "intent": result.intent,
                        "confidence": result.confidence,
                        "fallback_triggered": result.fallback_triggered,
                    }
                )

                return result

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
