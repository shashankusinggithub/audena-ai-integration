import os
from resilience.circuit_breaker import CircuitBreaker
import dotenv

dotenv.load_dotenv()

class Settings:

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    GEMINI_LLM_MODEL = os.getenv("GEMINI_LLM_MODEL", "gemini-2.5-flash-lite")
    GEMINI_STT_MODEL = os.getenv("GEMINI_STT_MODEL", "gemini-2.5-flash-lite")

    OPENAI_LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "gpt-4.1-mini")

    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "turbo")

    STT_TIMEOUT = int(os.getenv("STT_TIMEOUT", 25))

    WHISPER_TIMEOUT = int(os.getenv("WHISPER_TIMEOUT", 120))
    LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", 15))
    TTS_TIMEOUT = int(os.getenv("TTS_TIMEOUT", 15))



    STT_RETRY = int(os.getenv("STT_RETRY", 2))
    LLM_RETRY = int(os.getenv("LLM_RETRY", 2))
    TTS_RETRY = int(os.getenv("TTS_RETRY", 2))

    STT_BREAKER = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=30,
    )

    LLM_BREAKER = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=30,
    )

    LLM_BREAKER_OPENAI = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=30,
    )

    STT_PROVIDER_ORDER = ["whisper", "gemini"]
    LLM_PROVIDER_ORDER = ["gemini", "openai"]
    TTS_PROVIDER_ORDER = ["stub"]

    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.4))
