import json
import time

from config import Settings
from core.stt_router import STTRouter
from core.llm_router import LLMRouter

from providers.llm.gemini import GeminiLLMProvider
from providers.llm.openai import OpenAILLMProvider
from utils.logging import get_logger



class EvalPipeline:
    def __init__(self, router: LLMRouter):
        self.router = router


def build_eval_pipeline(logger):
    settings = Settings()

    llm_providers = [
        GeminiLLMProvider(settings, logger=logger),
        OpenAILLMProvider(settings, logger=logger),
    ]

    llm_router = LLMRouter(
        llm_providers,
        confidence_threshold=settings.CONFIDENCE_THRESHOLD,
        logger=logger,
    )   

    # For evaluation, bypass STT
    pipeline = EvalPipeline(
        router=llm_router
    )

    return pipeline


def run_evaluation():
    logger = get_logger("eval_pipeline")
    pipeline = build_eval_pipeline(logger)
    evaluator = EvalPipeline(pipeline.router)

    with open("tests/test_cases.json") as f:
        test_cases = json.load(f)

    total = len(test_cases)
    correct = 0
    total_confidence = 0
    total_latency = 0
    fallback_count = 0

    for case in test_cases:
        transcript = case["transcript"]
        expected = case["expected_intent"]

        start = time.time()
        result = evaluator.router.classify(transcript)
        latency = time.time() - start

        total_latency += latency
        total_confidence += result.confidence

        if result.intent == expected:
            correct += 1

        if result.fallback_triggered:
            fallback_count += 1
        time.sleep(5)

    logger.info("----- Evaluation Results -----")
    logger.info(f"Accuracy: {correct / total:.2f}")
    logger.info(f"Average confidence: {total_confidence / total:.2f}")
    logger.info(f"Average latency (s): {total_latency / total:.2f}")
    logger.info(f"Fallback rate: {fallback_count / total:.2f}")


if __name__ == "__main__":
    run_evaluation()