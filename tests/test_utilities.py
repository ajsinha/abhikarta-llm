"""
Tests for Utility Functions

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.abstraction.utils import (
    RetryConfig, retry_with_backoff,
    RateLimiter, SlidingWindowRateLimiter,
    LRUCache, cached
)


def test_retry_mechanism():
    """Test retry with backoff"""
    attempt_count = [0]
    
    @retry_with_backoff(
        retryable_exceptions=(ValueError,),
        config=RetryConfig(max_attempts=3, base_delay=0.1)
    )
    def flaky_function():
        attempt_count[0] += 1
        if attempt_count[0] < 3:
            raise ValueError("Temporary failure")
        return "Success"
    
    result = flaky_function()
    assert result == "Success"
    assert attempt_count[0] == 3
    print(f"✓ Retry mechanism: succeeded after {attempt_count[0]} attempts")


def test_rate_limiter():
    """Test rate limiter"""
    limiter = RateLimiter(requests_per_minute=10)
    
    start = time.time()
    for i in range(3):
        assert limiter.acquire()
    
    elapsed = time.time() - start
    print(f"✓ Rate limiter: processed 3 requests in {elapsed:.2f}s")


def test_sliding_window_limiter():
    """Test sliding window rate limiter"""
    limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=1)
    
    # Should allow 5 requests
    for i in range(5):
        assert limiter.acquire(block=False)
    
    # 6th request should fail without blocking
    assert not limiter.acquire(block=False)
    print("✓ Sliding window limiter: correctly enforced limits")


def test_lru_cache():
    """Test LRU cache"""
    cache = LRUCache(max_size=3)
    
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")
    
    assert cache.get("key1") == "value1"
    
    # Add 4th item, should evict oldest (key2)
    cache.set("key4", "value4")
    assert cache.get("key2") is None
    
    stats = cache.get_stats()
    print(f"✓ LRU cache: size={stats['size']}, hits={stats['hits']}, misses={stats['misses']}")


def test_cached_decorator():
    """Test cached decorator"""
    call_count = [0]
    cache = LRUCache(max_size=10)
    
    @cached(cache)
    def expensive_function(x):
        call_count[0] += 1
        return x * 2
    
    # First call
    result1 = expensive_function(5)
    assert result1 == 10
    assert call_count[0] == 1
    
    # Second call with same arg (should use cache)
    result2 = expensive_function(5)
    assert result2 == 10
    assert call_count[0] == 1  # Should still be 1
    
    print("✓ Cached decorator: cache working correctly")


def run_all_tests():
    """Run all utility tests"""
    print("=" * 60)
    print("Running Utility Tests")
    print("=" * 60)
    print()
    
    tests = [
        ("Retry Mechanism", test_retry_mechanism),
        ("Rate Limiter", test_rate_limiter),
        ("Sliding Window Limiter", test_sliding_window_limiter),
        ("LRU Cache", test_lru_cache),
        ("Cached Decorator", test_cached_decorator),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"Testing {name}...", end=" ")
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ FAILED: {str(e)}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
