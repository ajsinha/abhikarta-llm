"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.3
"""

"""Advanced Feature Tests"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.abstraction import LLMClientFactory
from llm.abstraction.utils import (
    RetryConfig, retry_with_backoff,
    RateLimiter, SlidingWindowRateLimiter,
    LRUCache, ResponseCache, cached
)
import time

def test_retry_mechanism():
    """Test retry with exponential backoff"""
    attempts = []
    
    @retry_with_backoff(max_attempts=3, initial_delay=0.1, backoff_factor=2)
    def failing_function():
        attempts.append(1)
        if len(attempts) < 3:
            raise Exception("Test failure")
        return "success"
    
    result = failing_function()
    assert result == "success"
    assert len(attempts) == 3
    print("✓ Retry mechanism test passed")

def test_rate_limiter():
    """Test rate limiting"""
    limiter = RateLimiter(tokens_per_second=10, max_tokens=5)
    
    start = time.time()
    for _ in range(5):
        limiter.acquire()
    elapsed = time.time() - start
    
    assert elapsed < 1.0  # Should burst through first 5
    print("✓ Rate limiter test passed")

def test_sliding_window_limiter():
    """Test sliding window rate limiting"""
    limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=1.0)
    
    # First 5 should succeed immediately
    for _ in range(5):
        assert limiter.acquire(blocking=False)
    
    # 6th should fail without blocking
    assert not limiter.acquire(blocking=False)
    print("✓ Sliding window limiter test passed")

def test_lru_cache():
    """Test LRU cache"""
    cache = LRUCache(max_size=3)
    
    cache.set('a', 1)
    cache.set('b', 2)
    cache.set('c', 3)
    
    assert cache.get('a') == 1
    assert cache.get('b') == 2
    
    cache.set('d', 4)  # Should evict 'c'
    assert cache.get('c') is None
    assert cache.get('d') == 4
    
    stats = cache.get_stats()
    assert stats['size'] == 3
    print("✓ LRU cache test passed")

def test_cached_decorator():
    """Test caching decorator"""
    call_count = [0]
    
    @cached(ttl=1.0)
    def expensive_function(x):
        call_count[0] += 1
        return x * 2
    
    result1 = expensive_function(5)
    result2 = expensive_function(5)
    
    assert result1 == 10
    assert result2 == 10
    assert call_count[0] == 1  # Should only call once
    print("✓ Cached decorator test passed")

def test_response_cache():
    """Test response caching"""
    cache = ResponseCache(max_size=100, ttl=3600)
    
    cache.set("What is AI?", "gpt-4", "AI is...", temperature=0.7)
    result = cache.get("What is AI?", "gpt-4", temperature=0.7)
    
    assert result == "AI is..."
    print("✓ Response cache test passed")

def test_provider_loading():
    """Test loading all providers"""
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    
    providers = factory._provider_factory.list_available_providers()
    
    expected = ['mock', 'anthropic', 'openai', 'google', 'meta', 'huggingface', 'awsbedrock']
    for provider in expected:
        assert provider in providers, f"{provider} not found"
    
    print(f"✓ All {len(providers)} providers loaded")

def test_mock_with_caching():
    """Test mock provider with caching"""
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    
    client = factory.create_mock_client()
    cache = ResponseCache()
    
    # First call - not cached
    prompt = "Test prompt"
    response1 = client.complete(prompt)
    cache.set(prompt, "mock-model", response1, temperature=0.7)
    
    # Second call - from cache
    cached_response = cache.get(prompt, "mock-model", temperature=0.7)
    assert cached_response == response1
    
    stats = cache.get_stats()
    assert stats['hits'] == 1
    print("✓ Mock with caching test passed")

def run_all_tests():
    print("=" * 60)
    print("Running Advanced Feature Tests")
    print("=" * 60)
    print()
    
    tests = [
        ("Retry Mechanism", test_retry_mechanism),
        ("Rate Limiter", test_rate_limiter),
        ("Sliding Window Limiter", test_sliding_window_limiter),
        ("LRU Cache", test_lru_cache),
        ("Cached Decorator", test_cached_decorator),
        ("Response Cache", test_response_cache),
        ("Provider Loading", test_provider_loading),
        ("Mock with Caching", test_mock_with_caching),
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
