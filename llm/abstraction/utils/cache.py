"""
Advanced Caching Mechanisms

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import time
import hashlib
import json
import threading
from typing import Any, Optional, Callable
from collections import OrderedDict
import functools


class LRUCache:
    """LRU Cache with TTL support"""
    
    def __init__(self, max_size: int = 100, ttl_seconds: Optional[float] = None):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = OrderedDict()
        self.timestamps = {}
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None
            
            if self.ttl_seconds is not None:
                if time.time() - self.timestamps[key] > self.ttl_seconds:
                    del self.cache[key]
                    del self.timestamps[key]
                    self.misses += 1
                    return None
            
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]
    
    def set(self, key: str, value: Any):
        """Set value in cache"""
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            else:
                if len(self.cache) >= self.max_size:
                    oldest_key = next(iter(self.cache))
                    del self.cache[oldest_key]
                    del self.timestamps[oldest_key]
            
            self.cache[key] = value
            self.timestamps[key] = time.time()
    
    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
            self.hits = 0
            self.misses = 0
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'ttl_seconds': self.ttl_seconds
        }


def cache_key_from_args(*args, **kwargs) -> str:
    """Generate cache key from function arguments"""
    key_data = {
        'args': args,
        'kwargs': sorted(kwargs.items())
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_str.encode()).hexdigest()


def cached(
    cache: LRUCache,
    key_func: Optional[Callable] = None
):
    """Decorator to cache function results"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{cache_key_from_args(*args, **kwargs)}"
            
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            
            return result
        
        return wrapper
    return decorator


class ResponseCache:
    """
    Specialized cache for LLM responses.
    
    Wraps LRUCache with a convenient API for caching LLM responses
    based on prompt, model, and parameters.
    """
    
    def __init__(self, max_size: int = 100, ttl: Optional[float] = None):
        """
        Initialize ResponseCache.
        
        Args:
            max_size: Maximum number of cached responses
            ttl: Time-to-live in seconds (None = no expiration)
        """
        self._cache = LRUCache(max_size=max_size, ttl_seconds=ttl)
    
    def _make_key(self, prompt: str, model: str, **kwargs) -> str:
        """Generate cache key from prompt, model, and parameters"""
        params_str = "|".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return f"{prompt}|{model}|{params_str}"
    
    def get(self, prompt: str, model: str, **kwargs) -> Optional[str]:
        """
        Get cached response.
        
        Args:
            prompt: The prompt text
            model: The model name
            **kwargs: Additional parameters (e.g., temperature=0.7)
        
        Returns:
            Cached response or None if not found
        """
        key = self._make_key(prompt, model, **kwargs)
        return self._cache.get(key)
    
    def set(self, prompt: str, model: str, response: str, **kwargs):
        """
        Cache a response.
        
        Args:
            prompt: The prompt text
            model: The model name
            response: The response to cache
            **kwargs: Additional parameters (e.g., temperature=0.7)
        """
        key = self._make_key(prompt, model, **kwargs)
        self._cache.set(key, response)
    
    def clear(self):
        """Clear all cached responses"""
        self._cache.clear()
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        return self._cache.get_stats()
