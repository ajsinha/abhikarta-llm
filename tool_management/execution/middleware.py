"""
Abhikarta LLM - Tool Management Framework
Middleware System

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

This module provides middleware infrastructure and common middleware implementations.
"""

import time
import logging
from typing import Dict, Any, Callable
from functools import wraps
from collections import defaultdict
from datetime import datetime, timedelta

from ..core import ToolResult, ResultStatus


logger = logging.getLogger(__name__)


# ============================================================================
# MIDDLEWARE DECORATORS
# ============================================================================

def middleware(func: Callable) -> Callable:
    """
    Decorator to mark a function as middleware.
    
    Middleware functions receive a context dict and return a (potentially modified) context.
    """
    @wraps(func)
    async def wrapper(context: Dict[str, Any]) -> Dict[str, Any]:
        return await func(context)
    return wrapper


# ============================================================================
# BUILT-IN MIDDLEWARE
# ============================================================================

@middleware
async def logging_middleware(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Logging middleware that logs tool execution details.
    
    Args:
        context: Execution context
        
    Returns:
        Unmodified context
    """
    tool = context.get("tool")
    params = context.get("params", {})
    
    logger.info(
        f"Executing tool: {tool.name} "
        f"(type: {tool.tool_type.value}, "
        f"params: {list(params.keys())})"
    )
    
    return context


@middleware
async def timing_middleware(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Timing middleware that tracks execution time.
    
    Args:
        context: Execution context
        
    Returns:
        Context with timing information
    """
    context["_middleware_start_time"] = time.time()
    return context


@middleware
async def validation_middleware(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validation middleware that performs additional parameter validation.
    
    Args:
        context: Execution context
        
    Returns:
        Context or skip result if validation fails
    """
    tool = context.get("tool")
    params = context.get("params", {})
    
    # Custom validation logic can be added here
    # For now, just log
    logger.debug(f"Validating parameters for tool: {tool.name}")
    
    return context


class RateLimiter:
    """
    Rate limiting middleware for tool execution.
    
    Implements token bucket algorithm for rate limiting.
    """
    
    def __init__(
        self,
        max_calls: int = 100,
        time_window: int = 60,
        per_tool: bool = True
    ):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum calls allowed in time window
            time_window: Time window in seconds
            per_tool: If True, rate limit per tool; if False, global limit
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.per_tool = per_tool
        
        # Track calls: tool_name -> list of timestamps
        self._call_history: Dict[str, list[datetime]] = defaultdict(list)
    
    def _clean_old_calls(self, tool_name: str):
        """Remove calls older than the time window"""
        cutoff = datetime.utcnow() - timedelta(seconds=self.time_window)
        self._call_history[tool_name] = [
            ts for ts in self._call_history[tool_name]
            if ts > cutoff
        ]
    
    def _is_allowed(self, tool_name: str) -> bool:
        """Check if a call is allowed"""
        key = tool_name if self.per_tool else "_global"
        self._clean_old_calls(key)
        return len(self._call_history[key]) < self.max_calls
    
    def _record_call(self, tool_name: str):
        """Record a call"""
        key = tool_name if self.per_tool else "_global"
        self._call_history[key].append(datetime.utcnow())
    
    async def __call__(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Middleware function to enforce rate limiting.
        
        Args:
            context: Execution context
            
        Returns:
            Context or skip result if rate limited
        """
        tool = context.get("tool")
        
        if not self._is_allowed(tool.name):
            logger.warning(f"Rate limit exceeded for tool: {tool.name}")
            
            # Calculate retry_after
            key = tool.name if self.per_tool else "_global"
            if self._call_history[key]:
                oldest_call = min(self._call_history[key])
                retry_after = self.time_window - (
                    datetime.utcnow() - oldest_call
                ).seconds
            else:
                retry_after = self.time_window
            
            context["skip"] = True
            context["result"] = ToolResult.rate_limited_result(
                retry_after=retry_after,
                tool_name=tool.name
            )
            return context
        
        self._record_call(tool.name)
        return context


class CachingMiddleware:
    """
    Caching middleware for tool results.
    
    Caches results based on tool name and parameters.
    """
    
    def __init__(self, ttl: int = 300):
        """
        Initialize caching middleware.
        
        Args:
            ttl: Time-to-live for cache entries in seconds
        """
        self.ttl = ttl
        self._cache: Dict[str, tuple[ToolResult, datetime]] = {}
    
    def _make_cache_key(self, tool_name: str, params: Dict[str, Any]) -> str:
        """Generate cache key from tool name and parameters"""
        import json
        params_str = json.dumps(params, sort_keys=True)
        return f"{tool_name}:{params_str}"
    
    def _is_valid(self, cached_at: datetime) -> bool:
        """Check if cache entry is still valid"""
        age = (datetime.utcnow() - cached_at).total_seconds()
        return age < self.ttl
    
    async def __call__(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Middleware function to check cache and return cached results.
        
        Args:
            context: Execution context
            
        Returns:
            Context with cached result or normal execution
        """
        tool = context.get("tool")
        params = context.get("params", {})
        
        cache_key = self._make_cache_key(tool.name, params)
        
        # Check cache
        if cache_key in self._cache:
            result, cached_at = self._cache[cache_key]
            
            if self._is_valid(cached_at):
                logger.debug(f"Cache hit for tool: {tool.name}")
                result.metadata["cached"] = True
                result.metadata["cached_at"] = cached_at.isoformat()
                
                context["skip"] = True
                context["result"] = result
                return context
            else:
                # Remove expired entry
                del self._cache[cache_key]
        
        logger.debug(f"Cache miss for tool: {tool.name}")
        return context
    
    def cache_result(self, tool_name: str, params: Dict[str, Any], result: ToolResult):
        """
        Manually cache a result.
        
        Args:
            tool_name: Tool name
            params: Parameters
            result: Result to cache
        """
        cache_key = self._make_cache_key(tool_name, params)
        self._cache[cache_key] = (result, datetime.utcnow())
    
    def clear_cache(self, tool_name: Optional[str] = None):
        """
        Clear cache entries.
        
        Args:
            tool_name: If provided, only clear entries for this tool
        """
        if tool_name:
            keys_to_remove = [
                k for k in self._cache.keys()
                if k.startswith(f"{tool_name}:")
            ]
            for key in keys_to_remove:
                del self._cache[key]
        else:
            self._cache.clear()


class AuthenticationMiddleware:
    """
    Authentication middleware for tool execution.
    
    Verifies authentication before allowing tool execution.
    """
    
    def __init__(self, auth_checker: Callable[[str], bool]):
        """
        Initialize authentication middleware.
        
        Args:
            auth_checker: Function that takes a token and returns bool
        """
        self.auth_checker = auth_checker
    
    async def __call__(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Middleware function to check authentication.
        
        Args:
            context: Execution context
            
        Returns:
            Context or skip result if not authenticated
        """
        tool = context.get("tool")
        auth_token = context.get("auth_token")
        
        if not auth_token or not self.auth_checker(auth_token):
            logger.warning(f"Authentication failed for tool: {tool.name}")
            
            context["skip"] = True
            context["result"] = ToolResult.failure_result(
                error="Authentication required",
                error_type="AuthenticationError",
                tool_name=tool.name
            )
            return context
        
        return context


class ErrorHandlingMiddleware:
    """
    Error handling middleware with retry logic.
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize error handling middleware.
        
        Args:
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    async def __call__(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Middleware function with retry logic.
        
        Note: This is a marker middleware. Actual retry logic would be
        implemented in the execution engine.
        """
        context["max_retries"] = self.max_retries
        context["retry_delay"] = self.retry_delay
        return context
