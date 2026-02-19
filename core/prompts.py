from core.prompt_templates import INTENT_CLASSIFICATION_TEMPLATE


INTENT_ALLOWED_INTENTS: tuple[str, ...] = (
    "account_support",
    "billing_issue",
    "technical_support",
    "general_query",
    "unclear_request",
)


def _format_allowed_intents(intents: tuple[str, ...]) -> str:
    return "\n".join(f'- "{intent}"' for intent in intents)


def build_intent_prompt(transcript: str) -> str:
    """Build and return the intent-classification prompt."""

    return INTENT_CLASSIFICATION_TEMPLATE.format(
        allowed_intents=_format_allowed_intents(INTENT_ALLOWED_INTENTS),
        transcript=transcript,
    ).strip()
