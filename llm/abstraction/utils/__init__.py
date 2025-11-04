"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.3

Utility Functions
"""

# Import what exists
try:
    from .retry import retry_with_backoff, RetryConfig
except ImportError:
    pass

try:
    from .rate_limiter import RateLimiter, SlidingWindowRateLimiter
except ImportError:
    pass

try:
    from .cache import LRUCache, ResponseCache, cached, cache_key_from_args
except ImportError:
    pass

try:
    from .async_client import AsyncLLMClient
except ImportError:
    pass

# Import streaming utilities we created
try:
    from .streaming import StreamHandler, StreamMetrics, print_stream, collect_stream_with_metrics
except ImportError:
    pass

try:
    from .benchmark import benchmark_provider, BenchmarkResults
except ImportError:
    pass

__all__ = [
    'StreamHandler',
    'StreamMetrics',
    'print_stream',
    'collect_stream_with_metrics',
]

