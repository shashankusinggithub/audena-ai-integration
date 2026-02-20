import whisper
from core.models import STTResult
from providers.stt.base import STTProvider
from resilience.resilient import resilient
from utils.logging import get_logger


class WhisperSTTProvider(STTProvider):

    def __init__(self, settings, logger=None):
        self.settings = settings
        self.logger = logger or get_logger()
        self.model = whisper.load_model(settings.WHISPER_MODEL)

    @property
    def name(self) -> str:
        return "whisper"

    def transcribe(self, audio_path: str) -> STTResult:

        @resilient(
            retry_attempts=self.settings.STT_RETRY,

            timeout_seconds=getattr(
                self.settings,
                "WHISPER_TIMEOUT",
                self.settings.STT_TIMEOUT,
            ),
            circuit_breaker=None,
            step_name="whisper_stt",
            logger=self.logger,
        )
        def execute():
            result = self.model.transcribe(audio_path)

            return STTResult(
                transcript=result.get("text", "").strip(),
                language=result.get("language"),
            )

        return execute()
