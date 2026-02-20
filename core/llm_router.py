from dataclasses import dataclass
from typing import Generic, Sequence, Type, TypeVar

from pydantic import BaseModel

from core.exceptions import (
    AllProvidersFailedError,
    ProviderExecutionError,
    SemanticValidationError,
)
from core.models import (
    ClarificationResponse,
    IntentLiterals,
    PipelineIntentResponse,
    ProviderIntentResponse,
)
from core.prompts import build_clarification_prompt, build_intent_prompt
from utils.logging import get_logger
from providers.llm.base import LLMProvider


ModelT = TypeVar("ModelT", bound=BaseModel)
DEFAULT_CLARIFICATION_QUESTION = "Could you clarify what you need help with?"


@dataclass(frozen=True)
class FailoverResult(Generic[ModelT]):
    payload: ModelT
    provider_name: str
    provider_index: int
    fallback_triggered: bool


class LLMRouter:

    def __init__(
        self,
        providers: Sequence[LLMProvider],
        confidence_threshold: float = 0.4,
        logger=None,
    ):
        self.providers = list(providers)
        self.confidence_threshold = confidence_threshold
        self.logger = logger or get_logger()

    def classify(self, transcript: str) -> PipelineIntentResponse:
        intent_prompt = build_intent_prompt(transcript)

        intent_outcome = self._run_with_failover(
            prompt=intent_prompt,
            response_model=ProviderIntentResponse,
            preferred_provider_index=0,
            step_label="intent",
        )

        if intent_outcome.payload.confidence >= self.confidence_threshold:
            self.logger.info(
                {
                    "message": "LLM intent classified",
                    "provider": intent_outcome.provider_name,
                    "intent": intent_outcome.payload.intent,
                    "confidence": intent_outcome.payload.confidence,
                    "fallback_triggered": intent_outcome.fallback_triggered,
                }
            )

            return PipelineIntentResponse(
                **intent_outcome.payload.model_dump(),
                provider_used=intent_outcome.provider_name,
                fallback_triggered=intent_outcome.fallback_triggered,
            )

        self.logger.info(
            {
                "message": "Low confidence detected, generating clarification question",
                "provider": intent_outcome.provider_name,
                "confidence": intent_outcome.payload.confidence,
                "threshold": self.confidence_threshold,
                "intent": intent_outcome.payload.intent,
            }
        )

        overall_fallback = intent_outcome.fallback_triggered
        clarification_question = DEFAULT_CLARIFICATION_QUESTION
        clarification_provider = "fallback"

        try:
            clarification_prompt = build_clarification_prompt(transcript)
            clarification_outcome = self._run_with_failover(
                prompt=clarification_prompt,
                response_model=ClarificationResponse,
                preferred_provider_index=intent_outcome.provider_index,
                step_label="clarification",
            )
            clarification_question = clarification_outcome.payload.clarification_question
            clarification_provider = clarification_outcome.provider_name
            overall_fallback = overall_fallback or clarification_outcome.fallback_triggered
        except AllProvidersFailedError:
            overall_fallback = True

        self.logger.info(
            {
                "message": "LLM clarification generated",
                "provider": intent_outcome.provider_name,
                "clarification_provider": clarification_provider,
                "fallback_triggered": overall_fallback,
                "clarification_question": clarification_question,
            }
        )

        return PipelineIntentResponse(
            intent=IntentLiterals.UNCERTAIN,
            confidence=intent_outcome.payload.confidence,
            notes=intent_outcome.payload.notes,
            provider_used=intent_outcome.provider_name,
            fallback_triggered=overall_fallback,
            clarification_question=clarification_question,
        )

    def _run_with_failover(
        self,
        prompt: str,
        response_model: Type[ModelT],
        preferred_provider_index: int,
        step_label: str,
    ) -> FailoverResult[ModelT]:
        last_error: Exception | None = None
        fallback_triggered = False

        ordered_providers = (
            self.providers[preferred_provider_index:]
            + self.providers[:preferred_provider_index]
        )

        for offset, provider in enumerate(ordered_providers):
            provider_index = (preferred_provider_index + offset) % len(self.providers)

            try:
                result = provider.generate(prompt, response_model)
                return FailoverResult(
                    payload=result,
                    provider_name=provider.name,
                    provider_index=provider_index,
                    fallback_triggered=fallback_triggered,
                )

            except (ProviderExecutionError, SemanticValidationError) as e:
                last_error = e
                fallback_triggered = True

                self.logger.warning(
                    {
                        "message": f"LLM {step_label} provider failed",
                        "provider": provider.name,
                        "provider_index": provider_index,
                        "error_type": type(e).__name__,
                        "error": str(e),
                        "fallback_to_next": offset < len(ordered_providers) - 1,
                    }
                )

        self.logger.error(
            {
                "message": f"All providers failed for {step_label}",
                "last_error_type": type(last_error).__name__ if last_error else None,
                "last_error": str(last_error) if last_error else None,
            }
        )

        raise AllProvidersFailedError(
            f"All LLM providers failed during {step_label}"
        ) from last_error

