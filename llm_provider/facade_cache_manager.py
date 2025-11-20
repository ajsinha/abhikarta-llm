"""
Facade Cache Manager - Manages LLM facade instances with session-based lifecycle

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha | Email: ajsinha@gmail.com

This module implements:
- Session-based facade caching
- Automatic cache eviction on session end
- Thread-safe operations
- Memory-efficient instance management
"""

import threading
import logging
import time
from typing import Dict, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class FacadeCacheManager:
    """
    Manages caching of LLM facade instances with session-based lifecycle.

    Features:
    - Cache key: {chat_session_id}:{provider_name}:{model_name}
    - Thread-safe operations
    - Automatic cleanup on session end
    - TTL-based eviction for orphaned entries
    - Memory usage tracking
    """

    def __init__(self, default_ttl_minutes: int = 60):
        """
        Initialize the cache manager.

        Args:
            default_ttl_minutes: Default TTL for cache entries (for orphaned sessions)
        """
        self._cache: Dict[str, Tuple[object, datetime]] = {}
        self._session_facades: Dict[str, Set[str]] = defaultdict(set)
        self._lock = threading.RLock()
        self._default_ttl = timedelta(minutes=default_ttl_minutes)

        logger.info(f"FacadeCacheManager initialized with {default_ttl_minutes}min TTL")

    def _make_cache_key(self, chat_session_id: str, provider_name: str,
                        model_name: str) -> str:
        """
        Create cache key from components.

        Args:
            chat_session_id: Unique chat session identifier
            provider_name: LLM provider name
            model_name: Model name

        Returns:
            Cache key string
        """
        return f"{chat_session_id}:{provider_name}:{model_name}"

    def get_or_create(self, chat_session_id: str, provider_name: str,
                      model_name: str, factory_func) -> object:
        """
        Get cached facade or create new one if not exists.

        Args:
            chat_session_id: Unique chat session identifier
            provider_name: LLM provider name
            model_name: Model name
            factory_func: Callable to create new facade if needed

        Returns:
            LLM facade instance
        """
        cache_key = self._make_cache_key(chat_session_id, provider_name, model_name)

        with self._lock:
            # Check if cached
            if cache_key in self._cache:
                facade, timestamp = self._cache[cache_key]

                # Check if still valid (not expired)
                if datetime.now() - timestamp < self._default_ttl:
                    logger.debug(f"Cache HIT: {cache_key}")
                    return facade
                else:
                    logger.info(f"Cache entry expired: {cache_key}")
                    self._remove_entry(cache_key, chat_session_id)

            # Create new facade
            logger.info(f"Cache MISS: Creating new facade for {cache_key}")
            facade = factory_func()

            # Cache it
            self._cache[cache_key] = (facade, datetime.now())
            self._session_facades[chat_session_id].add(cache_key)

            logger.info(
                f"Cached facade: {cache_key} "
                f"(Session total: {len(self._session_facades[chat_session_id])})"
            )

            return facade

    def get_cached(self, chat_session_id: str, provider_name: str,
                   model_name: str) -> Optional[object]:
        """
        Get cached facade without creating new one.

        Args:
            chat_session_id: Unique chat session identifier
            provider_name: LLM provider name
            model_name: Model name

        Returns:
            LLM facade instance or None if not cached
        """
        cache_key = self._make_cache_key(chat_session_id, provider_name, model_name)

        with self._lock:
            if cache_key in self._cache:
                facade, timestamp = self._cache[cache_key]

                if datetime.now() - timestamp < self._default_ttl:
                    return facade
                else:
                    self._remove_entry(cache_key, chat_session_id)

            return None

    def evict_session(self, chat_session_id: str) -> int:
        """
        Evict all facades for a chat session.

        Args:
            chat_session_id: Chat session identifier to evict

        Returns:
            Number of facades evicted
        """
        with self._lock:
            if chat_session_id not in self._session_facades:
                logger.debug(f"No facades to evict for session: {chat_session_id}")
                return 0

            cache_keys = self._session_facades[chat_session_id].copy()
            evicted_count = 0

            for cache_key in cache_keys:
                if cache_key in self._cache:
                    facade, _ = self._cache[cache_key]

                    # Call cleanup if facade has it
                    if hasattr(facade, 'cleanup'):
                        try:
                            facade.cleanup()
                        except Exception as e:
                            logger.warning(f"Error calling cleanup on {cache_key}: {e}")

                    del self._cache[cache_key]
                    evicted_count += 1

            # Clear session tracking
            del self._session_facades[chat_session_id]

            logger.info(
                f"Evicted {evicted_count} facades for session: {chat_session_id}"
            )

            return evicted_count

    def evict_provider_model(self, chat_session_id: str, provider_name: str,
                             model_name: str) -> bool:
        """
        Evict specific provider/model facade from session.

        Args:
            chat_session_id: Chat session identifier
            provider_name: Provider name
            model_name: Model name

        Returns:
            True if facade was evicted, False if not found
        """
        cache_key = self._make_cache_key(chat_session_id, provider_name, model_name)

        with self._lock:
            return self._remove_entry(cache_key, chat_session_id)

    def _remove_entry(self, cache_key: str, chat_session_id: str) -> bool:
        """
        Remove a cache entry (internal method, assumes lock is held).

        Args:
            cache_key: Cache key to remove
            chat_session_id: Associated session ID

        Returns:
            True if removed, False if not found
        """
        if cache_key in self._cache:
            facade, _ = self._cache[cache_key]

            # Call cleanup if available
            if hasattr(facade, 'cleanup'):
                try:
                    facade.cleanup()
                except Exception as e:
                    logger.warning(f"Error during cleanup of {cache_key}: {e}")

            del self._cache[cache_key]

            # Update session tracking
            if chat_session_id in self._session_facades:
                self._session_facades[chat_session_id].discard(cache_key)

                # Clean up session tracking if empty
                if not self._session_facades[chat_session_id]:
                    del self._session_facades[chat_session_id]

            logger.debug(f"Removed cache entry: {cache_key}")
            return True

        return False

    def cleanup_expired(self) -> int:
        """
        Clean up expired cache entries.

        Returns:
            Number of entries cleaned up
        """
        with self._lock:
            now = datetime.now()
            expired_keys = []

            for cache_key, (facade, timestamp) in self._cache.items():
                if now - timestamp >= self._default_ttl:
                    expired_keys.append(cache_key)

            cleaned = 0
            for cache_key in expired_keys:
                # Extract session ID from cache key
                session_id = cache_key.split(':')[0]
                if self._remove_entry(cache_key, session_id):
                    cleaned += 1

            if cleaned > 0:
                logger.info(f"Cleaned up {cleaned} expired cache entries")

            return cleaned

    def get_stats(self) -> Dict[str, any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            return {
                'total_cached_facades': len(self._cache),
                'active_sessions': len(self._session_facades),
                'facades_by_session': {
                    session_id: len(keys)
                    for session_id, keys in self._session_facades.items()
                },
                'cache_keys': list(self._cache.keys())
            }

    def clear_all(self) -> int:
        """
        Clear all cached facades (for testing or reset).

        Returns:
            Number of facades cleared
        """
        with self._lock:
            count = len(self._cache)

            # Cleanup all facades
            for cache_key, (facade, _) in self._cache.items():
                if hasattr(facade, 'cleanup'):
                    try:
                        facade.cleanup()
                    except Exception as e:
                        logger.warning(f"Error during cleanup of {cache_key}: {e}")

            self._cache.clear()
            self._session_facades.clear()

            logger.info(f"Cleared all {count} cached facades")
            return count


__all__ = ['FacadeCacheManager']