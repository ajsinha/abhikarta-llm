"""
Test ResponseCache Import Fix

Verifies that ResponseCache can be imported and used correctly.

© 2025-2030 All rights reserved Ashutosh Sinha
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.abstraction.utils import (
    RetryConfig, retry_with_backoff,
    RateLimiter, SlidingWindowRateLimiter,
    LRUCache, ResponseCache, cached
)


def test_imports():
    """Test that all imports work"""
    print("="*60)
    print("Testing Utils Imports")
    print("="*60)
    print()
    
    print("✓ RetryConfig")
    print("✓ retry_with_backoff")
    print("✓ RateLimiter")
    print("✓ SlidingWindowRateLimiter")
    print("✓ LRUCache")
    print("✓ ResponseCache")
    print("✓ cached")
    print()
    print("✓ All imports successful!")


def test_lru_cache():
    """Test LRUCache functionality"""
    print()
    print("="*60)
    print("Testing LRUCache")
    print("="*60)
    print()
    
    cache = LRUCache(max_size=100, ttl_seconds=3600)
    
    # Test set and get
    cache.set("key1", "value1")
    result = cache.get("key1")
    assert result == "value1", f"Expected 'value1', got {result}"
    print("✓ LRUCache set/get works")
    
    # Test stats
    stats = cache.get_stats()
    assert stats['size'] == 1
    assert stats['hits'] == 1
    assert stats['misses'] == 0
    print(f"✓ LRUCache stats: {stats}")


def test_response_cache():
    """Test ResponseCache functionality"""
    print()
    print("="*60)
    print("Testing ResponseCache")
    print("="*60)
    print()
    
    cache = ResponseCache(max_size=100, ttl=3600)
    
    # Test set and get with prompt/model API
    prompt = "What is AI?"
    model = "gpt-4"
    response = "AI is artificial intelligence..."
    
    cache.set(prompt, model, response, temperature=0.7)
    result = cache.get(prompt, model, temperature=0.7)
    
    assert result == response, f"Expected '{response}', got {result}"
    print("✓ ResponseCache set/get works")
    
    # Test with different temperature (should miss)
    result2 = cache.get(prompt, model, temperature=0.9)
    assert result2 is None
    print("✓ ResponseCache correctly differentiates parameters")
    
    # Test stats
    stats = cache.get_stats()
    assert stats['size'] == 1
    assert stats['hits'] == 1
    assert stats['misses'] == 1
    print(f"✓ ResponseCache stats: {stats}")


def test_response_cache_api():
    """Test ResponseCache API matches test_advanced.py usage"""
    print()
    print("="*60)
    print("Testing ResponseCache API Compatibility")
    print("="*60)
    print()
    
    # Test exactly as used in test_advanced.py
    cache = ResponseCache(max_size=100, ttl=3600)
    
    cache.set("What is AI?", "gpt-4", "AI is...", temperature=0.7)
    result = cache.get("What is AI?", "gpt-4", temperature=0.7)
    
    assert result == "AI is..."
    print("✓ test_response_cache() pattern works")
    
    # Test mock with caching pattern
    cache2 = ResponseCache()
    prompt = "Test prompt"
    response1 = "Mock response"
    cache2.set(prompt, "mock-model", response1, temperature=0.7)
    cached_response = cache2.get(prompt, "mock-model", temperature=0.7)
    assert cached_response == response1
    print("✓ test_mock_with_caching() pattern works")


def main():
    """Run all tests"""
    print("\n╔" + "="*58 + "╗")
    print("║" + "  RESPONSE CACHE IMPORT FIX - VERIFICATION  ".center(58) + "║")
    print("╚" + "="*58 + "╝\n")
    
    try:
        test_imports()
        test_lru_cache()
        test_response_cache()
        test_response_cache_api()
        
        print()
        print("="*60)
        print("✓ ALL TESTS PASSED")
        print("="*60)
        print()
        print("ResponseCache is now available and working!")
        print("test_advanced.py imports should work correctly.")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
