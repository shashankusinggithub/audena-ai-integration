# Voice Agent Pipeline

A minimal voice agent pipeline:

```
Audio → STT → LLM  →  TTS 
```

It supports multiple STT and LLM providers, structured outputs, retry logic, and fallback handling.

---

## How to Run

0. Pre-requisites

* Python 3.11+
* `ffmpeg` installed and available in PATH
* Refer to [Whisper installation guide](https://github.com/openai/whisper) for installation instructions.

1. Install dependencies. Its recommended to use a virtual environment.

```
pip install -r requirements.txt
```
2. Set required environment variables  in .env file:

```
GEMINI_API_KEY=...
OPENAI_API_KEY=...
```

3. Run:

```
python run_pipeline.py <audio_file.wav>
# Or to run evaluation script
python run_eval.py
```

Example:

```
python run_pipeline.py samples/Which-llm-is-better?.m4a
```

The output is a structured JSON object containing intent, confidence, and metadata.

---

## Key Design Decisions

* **Explicit pipeline orchestration**
  Clear `STT → LLM → output` flow. No hidden logic.

* **Adapter pattern for providers**
  STT and LLM providers implement base interfaces. Easy to swap or extend.

* **Router-based fallback**
  If a provider fails or returns low-confidence output, the next provider is tried.

* **Structured output enforced**
  Both Gemini and OpenAI use JSON schema validation. Output is validated with Pydantic.

* **Single composite resilience decorator**
  Retry + timeout + circuit breaker are handled in one place to keep provider code clean.

* **One-step intent + clarification output**

  LLM returns intent, confidence, notes, and (when uncertain) a clarification question in one structured response.
  Reason:
  * Single round-trip to LLM for intent + clarification.
  * Reduces latency and provider load.
  * Improves user experience by eliminating multiple back-and-forths.

  Tradeoff:
  * 2-step process should be considered when LLM output intent is uncertain very rarely.
  * 2-step process is more robust against LLM errors or unexpected outputs.
  * 2-step process can be used when for more complex or domain-specific tasks where a single response is not sufficient.
  * Increased latency for clarification loop.
  * Potential for infinite loops if LLM keeps returning uncertain responses.
  * Requires careful handling of user interruptions.



* **Separation of concerns**

  * `core/` → orchestration & business logic
  * `providers/` → external integrations
  * `resilience/` → reliability logic - (retry, timeout, circuit breaker)


---

## Where Things Might Break

* LLM may still produce unexpected structured output in rare cases.
* Confidence threshold is heuristic and may need tuning.
* Circuit breaker is in-memory and not distributed-safe.
* Timeout implementation uses threads and may not scale for heavy concurrency.
* STT quality depends heavily on audio clarity.

This is intentionally simple and script-oriented.

---

## What I Would Improve With More Time
* There is a lot of latency in the pipeline. I would add a cache layer for STT results.
* Introducing the WebRTC for real-time audio processing with better models that can be interrupted.
* Add exponential backoff with jitter for retries.
* Add small evaluation dataset and automated regression checks.
* Add request IDs and structured tracing.
* Add cost-aware or latency-aware routing.
* Improve prompt retry strategy (tighten prompt on second attempt or add error messages).
* Persist metrics for monitoring provider health.

---

## Evaluation / Regression Testing Approach

I would maintain a small curated set of representative audio samples with expected intents.

After any model, prompt, or provider change, I would:

* Run the pipeline on all samples
* Compare predicted intents against expected ones
* Track fallback frequency
* Flag regressions automatically

This keeps behavior stable despite model updates.



