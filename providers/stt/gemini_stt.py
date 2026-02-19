import mimetypes
from google import genai
from google.genai import types
from core.models import STTResult
from providers.stt.base import STTProvider
from resilience.resilient import resilient


class GeminiSTTProvider(STTProvider):

    def __init__(self, settings, logger=None):
        self.settings = settings
        self.logger = logger
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    @property
    def name(self) -> str:
        return "gemini_stt"

    def transcribe(self, audio_path: str):

        @resilient(
            retry_attempts=self.settings.STT_RETRY,
            timeout_seconds=self.settings.STT_TIMEOUT,
            circuit_breaker=self.settings.STT_BREAKER,
            step_name="gemini_stt",
            logger=self.logger,
        )
        def execute():

            with open(audio_path, "rb") as f:
                audio_bytes = f.read()

            mime_type, _ = mimetypes.guess_type(audio_path)
            audio_part = types.Part.from_bytes(
                data=audio_bytes,
                mime_type=mime_type or "audio/wav",
            )

            response = self.client.models.generate_content(
                model=self.settings.GEMINI_STT_MODEL,
                contents=[
                    "Transcribe this audio and return only the transcript text.",
                    audio_part,
                ],
            )

            transcript = response.text.strip()

            return STTResult(
                transcript=transcript,
                language=None,
            )

        return execute()
