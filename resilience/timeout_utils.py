import concurrent.futures
from typing import Callable


def _with_timeout(fn: Callable, timeout_seconds: int):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fn)
        return future.result(timeout=timeout_seconds)
