from pydantic import BaseModel, Field
from enum import Enum


class STTResult(BaseModel):
    transcript: str
    language: str | None = None



class IntentLiterals(str, Enum): # Inherit from str for string values
    ACCOUNT_SUPPORT = "account_support"
    BILLING_ISSUE = "billing_issue"
    TECHNICAL_SUPPORT = "technical_support"
    GENERAL_QUERY = "general_query"
    UNCERTAIN = "uncertain"

class ProviderIntentResponse(BaseModel):
    intent: IntentLiterals  
    confidence: float = Field(ge=0.0, le=1.0)
    notes: str

class ClarificationResponse(BaseModel):
    clarification_question: str

class PipelineIntentResponse(ProviderIntentResponse):
    provider_used: str | None = None
    fallback_triggered: bool = False
    clarification_question: str | None = None
