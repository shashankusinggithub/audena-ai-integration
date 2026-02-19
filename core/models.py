from pydantic import BaseModel, Field
from typing import Literal


class STTResult(BaseModel):
    transcript: str
    language: str | None = None


class IntentResponse(BaseModel):
    intent: Literal[
        "account_support",
        "billing_issue",
        "technical_support",
        "general_query",
        "unclear_request"
    ]
    confidence: float = Field(ge=0.0, le=1.0)
    notes: str
    provider_used: str | None = None
    fallback_triggered: bool = False
