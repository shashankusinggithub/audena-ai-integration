import logging
from typing import Callable, Tuple, Type


def _retry(
    fn: Callable,
    attempts: int,
    retry_exceptions: Tuple[Type[Exception], ...],
    logger=None,
    step_name: str = "unknown",
):
    last_exception = None

    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except retry_exceptions as e:
            last_exception = e

            logger.warning(
                {
                    "message": "Retryable error encountered",
                    "step": step_name,
                    "attempt": attempt,
                    "max_attempts": attempts,
                    "will_retry": attempt < attempts,
                    "error_type": type(e).__name__,
                    "error": str(e),
                }
            )

            if attempt == attempts:

                logger.error(
                    {
                        "message": "Retry attempts exhausted",
                        "step": step_name,
                        "attempt": attempt,
                        "max_attempts": attempts,
                        "error_type": type(e).__name__,
                        "error": str(e),
                    }
                )
                raise

    raise last_exception
