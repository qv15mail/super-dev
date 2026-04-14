"""Retry with exponential backoff for transient failures."""

import functools
import logging
import time
from collections.abc import Callable
from typing import TypeVar

_logger = logging.getLogger("super_dev.retry")
_T = TypeVar("_T")

RETRYABLE_ERRORS = (ConnectionError, TimeoutError, OSError)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    retryable: tuple = RETRYABLE_ERRORS,
):
    """Decorator: retry on transient errors with exponential backoff."""

    def decorator(func: Callable[..., _T]) -> Callable[..., _T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable as exc:
                    last_error = exc
                    if attempt < max_retries:
                        delay = min(base_delay * (2**attempt), max_delay)
                        _logger.warning(
                            "Retry %d/%d for %s after %.1fs: %s",
                            attempt + 1,
                            max_retries,
                            func.__name__,
                            delay,
                            exc,
                        )
                        time.sleep(delay)
            raise last_error  # type: ignore[misc]

        return wrapper

    return decorator
