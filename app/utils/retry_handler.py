"""
app/utils/retry_handler.py
===========================

Retry logic with exponential backoff for handling API rate limits and transient failures.

This module provides decorators and utilities for retrying operations that may fail
due to rate limiting (429 errors) or temporary network issues.

Design principles:
- Exponential backoff to respect rate limits
- Configurable retry attempts and delays
- Special handling for 429 (Too Many Requests) errors
- Logging for debugging and monitoring
"""

from __future__ import annotations

import logging
import time
from functools import wraps
from typing import Any, Callable, TypeVar, cast

logger = logging.getLogger(__name__)

T = TypeVar("T")


def retry_with_exponential_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    retry_on_429: bool = True,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator that retries a function with exponential backoff on failure.
    
    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay between retries in seconds (default: 1.0)
        backoff_factor: Multiplier for delay on each retry (default: 2.0)
        max_delay: Maximum delay between retries in seconds (default: 60.0)
        retry_on_429: Whether to retry specifically on 429 errors (default: True)
    
    Returns:
        Decorated function that will retry on failure
    
    Example:
        @retry_with_exponential_backoff(max_retries=3, initial_delay=2.0)
        def call_api():
            return requests.get("https://api.example.com/data")
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exception = exc
                    
                    # Check if this is a 429 error
                    is_429_error = (
                        "429" in str(exc) or
                        "Too Many Requests" in str(exc) or
                        "rate limit" in str(exc).lower()
                    )
                    
                    # If we've exhausted retries, raise
                    if attempt >= max_retries:
                        logger.error(
                            "%s failed after %d attempts: %s",
                            func.__name__,
                            max_retries + 1,
                            exc,
                        )
                        raise
                    
                    # If retry_on_429 is False and this isn't a 429, don't retry
                    if not retry_on_429 and not is_429_error:
                        raise
                    
                    # Calculate sleep time with exponential backoff
                    sleep_time = min(delay, max_delay)
                    
                    logger.warning(
                        "%s failed (attempt %d/%d): %s. Retrying in %.1fs...",
                        func.__name__,
                        attempt + 1,
                        max_retries + 1,
                        exc,
                        sleep_time,
                    )
                    
                    time.sleep(sleep_time)
                    delay *= backoff_factor
            
            # Should never reach here, but just in case
            raise last_exception if last_exception else RuntimeError("Unexpected retry failure")
        
        return cast(Callable[..., T], wrapper)
    return decorator


def retry_on_rate_limit(
    max_retries: int = 5,
    initial_delay: float = 2.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Specialized retry decorator for rate limit errors (429).
    
    This is a convenience wrapper around retry_with_exponential_backoff
    with settings optimized for API rate limiting scenarios.
    
    Args:
        max_retries: Maximum number of retry attempts (default: 5)
        initial_delay: Initial delay between retries in seconds (default: 2.0)
    
    Returns:
        Decorated function that will retry on rate limit errors
    
    Example:
        @retry_on_rate_limit(max_retries=5, initial_delay=3.0)
        def call_llm_api(prompt: str) -> str:
            return llm_client.invoke(prompt)
    """
    return retry_with_exponential_backoff(
        max_retries=max_retries,
        initial_delay=initial_delay,
        backoff_factor=2.0,
        max_delay=60.0,
        retry_on_429=True,
    )
