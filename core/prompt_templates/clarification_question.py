from typing import Final


CLARIFICATION_QUESTION_TEMPLATE: Final[str] = '''
You generate a single clarification question for an intent classification system.

Task:
- The user's latest transcript could not be classified with high confidence.
- Ask exactly one short, specific question that helps disambiguate the intent.
- Keep it polite and actionable.
- Return STRICT JSON only.

Return JSON with this structure:
{{
  "clarification_question": "<single question>"
}}

Rules:
- Ask one question only.
- Do not include markdown, extra keys, or explanations outside JSON.
- Keep the question under 200 characters.

User transcript:
"""{transcript}"""
'''
