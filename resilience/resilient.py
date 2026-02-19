import time
import logging
from functools import wraps
from typing import Tuple, Type

from resilience.retry_utils import _retry
from resilience.timeout_utils import _with_timeout


def resilient(
    retry_attempts: int = 2,
    timeout_seconds: int = 10,
    circuit_breaker=None,
    retry_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    step_name: str = "unknown",
    logger=None,
):
    """
    Composite resilience decorator.

    Execution order:
        CircuitBreaker
            ↳ Retry
                ↳ Timeout
                    ↳ Actual function
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()

            def base_call():
                return func(*args, **kwargs)

            def with_timeout():
                return _with_timeout(base_call, timeout_seconds)

            def with_retry():
                return _retry(
                    with_timeout,
                    attempts=retry_attempts,
                    retry_exceptions=retry_exceptions,
                    logger=logger,
                    step_name=step_name,
                )

            try:
                if circuit_breaker:
                    result = circuit_breaker.execute(with_retry)
                else:
                    result = with_retry()

                return result

            finally:
                duration_ms = (time.time() - start) * 1000

                logger.info(
                    {
                        "step": step_name,
                        "latency_ms": round(duration_ms, 2),
                    }
                )

        return wrapper

    return decorator
