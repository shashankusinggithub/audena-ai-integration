from providers.tts.base import TTSProvider
from resilience.resilient import resilient


class StubTTSProvider(TTSProvider):
    def __init__(self, settings, logger=None):
        self.settings = settings
        self.logger = logger


    @property
    def name(self):
        return "stub_tts"


    def synthesize(self, text: str) -> str:
        @resilient(
        retry_attempts=self.settings.TTS_RETRY,
        timeout_seconds=self.settings.TTS_TIMEOUT,
        circuit_breaker=None,
        step_name="stub_tts",
        logger=self.logger,
    )
        def execute():
            return f"[AUDIO_GENERATED]: {text}"

        return execute()
