class SemanticValidationError(Exception):
    """Raised when LLM output fails schema validation."""
    pass


class ProviderExecutionError(Exception):
    """Raised when a provider call fails due to runtime/provider issues."""
    pass


class LowConfidenceError(Exception):
    """Raised when LLM confidence is below acceptable threshold."""
    pass


class AllProvidersFailedError(Exception):
    """Raised when all providers in a router fail."""
    pass
