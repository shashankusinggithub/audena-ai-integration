from typing import Final


INTENT_CLASSIFICATION_TEMPLATE: Final[str] = '''
You are an intent classification system.

Your task:
- Interpret the user's request.
- Classify it into one of the allowed intents.
- Return STRICT JSON only.
- Do NOT include any explanation outside JSON.

Allowed intents:
{allowed_intents}

Return JSON with the following structure:
{{
  "intent": "<one of allowed intents>",
  "confidence": <float between 0 and 1>,
  "notes": "<short explanation>"
}}

Rules:
- If the request is unclear, ambiguous, or incomplete,
  return intent="unclear_request" and confidence=0.0.
- Confidence must always be between 0 and 1.

User transcript:
"""{transcript}"""
'''
