"""
Retry Mechanisms with Exponential Backoff

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import time
import functools
from typing import Callable, Type, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


def calculate_backoff(
    attempt: int,
    base_delay: float,
    exponential_base: float,
    max_delay: float,
    jitter: bool = True
) -> float:
    """Calculate backoff delay with exponential backoff and optional jitter"""
    import random
    
    delay = min(base_delay * (exponential_base ** attempt), max_delay)
    
    if jitter:
        delay *= (0.5 + random.random())
    
    return delay


def retry_with_backoff(
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable] = None
):
    """Decorator to retry a function with exponential backoff"""
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                    
                except retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt == config.max_attempts - 1:
                        logger.error(f"Function {func.__name__} failed after {config.max_attempts} attempts: {str(e)}")
                        raise
                    
                    delay = calculate_backoff(attempt, config.base_delay, config.exponential_base, config.max_delay, config.jitter)
                    
                    logger.warning(f"Function {func.__name__} failed (attempt {attempt + 1}/{config.max_attempts}): {str(e)}. Retrying in {delay:.2f}s...")
                    
                    if on_retry:
                        on_retry(attempt, delay, e)
                    
                    time.sleep(delay)
            
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator
