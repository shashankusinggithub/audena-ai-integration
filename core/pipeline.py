from core import tts_router
from core.models import IntentResponse
from core.exceptions import AllProvidersFailedError
from utils.logging import get_logger


class VoicePipeline:

    def __init__(self, stt_router, llm_router, tts_router, logger=None):
        self.stt_router = stt_router
        self.llm_router = llm_router
        self.tts_router = tts_router
        self.logger = logger or get_logger()

    def run(self, audio_path: str) -> dict:

        try:
            stt_result = self.stt_router.transcribe(audio_path)

            # Basic validation
            transcript = stt_result.transcript.strip()
            if not transcript:
                self.logger.warning(
                    {
                        "message": "Empty transcript detected, triggering fallback",
                        "step": "stt_validation",
                    }
                )
                return self._fallback("Empty transcript")

            # Step 2: LLM reasoning
            intent_result: IntentResponse = self.llm_router.classify(transcript)

            response = intent_result.model_dump()
            audio_stub = self.tts_router.synthesize(response["intent"])
            response["audio_stub"] = audio_stub

            self.logger.info(
                    {
                        "message": "Pipeline step completed",
                        "step": "llm_classification",
                        "intent": response.get("intent"),
                        "confidence": response.get("confidence"),
                        "provider_used": response.get("provider_used"),
                        "audio_stub": response.get("audio_stub"),
                    }
                )
            self.logger.info(
                    {
                        "message": "Voice pipeline completed",
                        "audio_path": audio_path,
                        "fallback_triggered": response.get("fallback_triggered"),
                    }
                )

            return response

        except AllProvidersFailedError as e:
            self.logger.error(
                {
                    "message": "Pipeline failed because all providers failed",
                    "audio_path": audio_path,
                    "error": str(e),
                },
                exc_info=True,
            )
            return self._fallback("All providers failed")

        except Exception as e:
            self.logger.error(
                {
                    "message": "Pipeline failed unexpectedly",
                    "audio_path": audio_path,
                    "error_type": type(e).__name__,
                    "error": str(e),
                },
                exc_info=True,
            )
            return self._fallback(str(e))

    def _fallback(self, reason: str) -> dict:
        self.logger.warning(
                {
                    "message": "Returning fallback response",
                    "reason": reason,
                }
            )

        return {
            "intent": "uncertain",
            "confidence": 0.0,
            "notes": reason,
            "provider_used": None,
            "fallback_triggered": True,
        }
