import sys
from config import Settings
from utils.logging import get_logger

from core.pipeline import VoicePipeline
from core.stt_router import STTRouter
from core.llm_router import LLMRouter
from core.tts_router import TTSRouter



from providers.stt.whisper import WhisperSTTProvider
from providers.stt.gemini_stt import GeminiSTTProvider
from providers.llm.gemini import GeminiLLMProvider
from providers.llm.openai import OpenAILLMProvider
from providers.tts.stub import StubTTSProvider



STT_MAP = {
    "whisper": WhisperSTTProvider,
    "gemini": GeminiSTTProvider,
}
LLM_MAP = {
    "gemini": GeminiLLMProvider,
    "openai": OpenAILLMProvider,
}

TTS_MAP = {
    "stub": StubTTSProvider,
}



def build_stt_providers(settings, logger):
    providers = []

    for name in settings.STT_PROVIDER_ORDER:
        if name in STT_MAP:
            providers.append(STT_MAP[name](settings, logger))

    return providers


def build_llm_providers(settings, logger):
    providers = []

    for name in settings.LLM_PROVIDER_ORDER:
        if name in LLM_MAP:
            providers.append(LLM_MAP[name](settings, logger))

    return providers

def build_tts_provider(settings, logger):
    providers = []

    for name in settings.TTS_PROVIDER_ORDER:
        if name in TTS_MAP:
            providers.append(TTS_MAP[name](settings, logger))

    return providers

def main(audio_path: str):
    settings = Settings()
    logger = get_logger()


    stt_providers = build_stt_providers(settings, logger)
    tts_providers = build_tts_provider(settings, logger)  
    llm_providers = build_llm_providers(settings, logger)


    stt_router = STTRouter(stt_providers, logger=logger)
    llm_router = LLMRouter(
        llm_providers,
        confidence_threshold=settings.CONFIDENCE_THRESHOLD,
        logger=logger,
    )
    tts_router = TTSRouter(tts_providers, logger=logger)



    pipeline = VoicePipeline(stt_router, llm_router, tts_router, logger=logger)

    result = pipeline.run(audio_path)


    print(result)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_pipeline.py <audio_file>")
        sys.exit(1)

    main(sys.argv[1])
