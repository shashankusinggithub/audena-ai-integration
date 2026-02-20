from core.prompt_templates import INTENT_CLASSIFICATION_TEMPLATE, CLARIFICATION_QUESTION_TEMPLATE
from core.models import IntentLiterals




def _format_allowed_intents(intents: tuple[str, ...]) -> str:
    return "\n".join(f'- "{intent}"' for intent in intents)


def build_intent_prompt(transcript: str) -> str:
    """Build and return the intent-classification prompt."""

    return INTENT_CLASSIFICATION_TEMPLATE.format(
        allowed_intents=_format_allowed_intents([e.value for e in IntentLiterals]),
        transcript=transcript,
    ).strip()


def build_clarification_prompt(transcript: str) -> str:
    """Build and return the clarification-question prompt."""

    return CLARIFICATION_QUESTION_TEMPLATE.format(
        transcript=transcript,
    ).strip()