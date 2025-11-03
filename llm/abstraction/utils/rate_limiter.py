"""
Rate Limiting Utilities

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import time
import threading
from typing import Optional
from collections import deque


class RateLimiter:
    """Token bucket rate limiter for API calls"""
    
    def __init__(self, requests_per_minute: int = 60, burst_size: Optional[int] = None):
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size or requests_per_minute
        self.tokens = float(self.burst_size)
        self.last_update = time.time()
        self.lock = threading.Lock()
        self.refill_rate = requests_per_minute / 60.0
    
    def acquire(self, tokens: int = 1, block: bool = True, timeout: Optional[float] = None) -> bool:
        """Acquire tokens for making requests"""
        start_time = time.time()
        
        while True:
            with self.lock:
                self._refill()
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return True
            
            if not block:
                return False
            
            if timeout is not None and (time.time() - start_time) >= timeout:
                return False
            
            time.sleep(0.1)
    
    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(self.burst_size, self.tokens + elapsed * self.refill_rate)
        self.last_update = now
    
    def get_available_tokens(self) -> float:
        """Get current number of available tokens"""
        with self.lock:
            self._refill()
            return self.tokens


class SlidingWindowRateLimiter:
    """Sliding window rate limiter"""
    
    def __init__(self, max_requests: int, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()
        self.lock = threading.Lock()
    
    def acquire(self, block: bool = True, timeout: Optional[float] = None) -> bool:
        """Acquire permission to make a request"""
        start_time = time.time()
        
        while True:
            with self.lock:
                now = time.time()
                cutoff = now - self.window_seconds
                
                while self.requests and self.requests[0] < cutoff:
                    self.requests.popleft()
                
                if len(self.requests) < self.max_requests:
                    self.requests.append(now)
                    return True
            
            if not block:
                return False
            
            if timeout is not None and (time.time() - start_time) >= timeout:
                return False
            
            time.sleep(0.1)
    
    def get_request_count(self) -> int:
        """Get current request count in window"""
        with self.lock:
            now = time.time()
            cutoff = now - self.window_seconds
            
            while self.requests and self.requests[0] < cutoff:
                self.requests.popleft()
            
            return len(self.requests)
