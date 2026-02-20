from typing import List
from core.exceptions import AllProvidersFailedError
from core.models import STTResult
from utils.logging import get_logger


class STTRouter:

    def __init__(self, providers: List, logger=None):
        self.providers = providers
        self.logger = logger or get_logger()

    def transcribe(self, audio_path: str) -> STTResult:
        last_error = None

        for provider in self.providers:
            try:

                result = provider.transcribe(audio_path)

                if not result.transcript.strip():
                    raise ValueError("Empty transcript")

                self.logger.info(
                    {
                        "message": "STT step completed",
                        "provider": provider.name,
                        "transcript": result.transcript,
                        "language": result.language,
                    }
                )

                return result

            except Exception as e:
                last_error = e

                self.logger.error(
                    {
                        "message": "STT provider failed",
                        "provider": provider.name,
                        "error_type": type(e).__name__,
                        "error": str(e),
                    },
                    exc_info=True,
                )
                continue

        self.logger.error(
            {
                "message": "All STT providers failed",
                "audio_path": audio_path,
                "last_error_type": type(last_error).__name__ if last_error else None,
                "last_error": str(last_error) if last_error else None,
            }
        )

        raise AllProvidersFailedError("All STT providers failed") from last_error
