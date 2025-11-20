"""
Session Cleanup Task - Background task for cleaning up expired sessions and facades

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha | Email: ajsinha@gmail.com

This module provides:
- Periodic cleanup of expired sessions
- Facade cache maintenance
- Session timeout handling
- Background thread management
"""

import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Callable, Optional

logger = logging.getLogger(__name__)


class SessionCleanupTask:
    """
    Background task for cleaning up expired sessions and facades.

    Features:
    - Runs in separate thread
    - Configurable cleanup interval
    - Session timeout detection
    - Automatic facade eviction
    - Graceful shutdown
    """

    def __init__(self,
                 facade_cache_manager,
                 active_sessions: Dict[str, Dict[str, Any]],
                 cleanup_interval_seconds: int = 300,
                 session_timeout_minutes: int = 30):
        """
        Initialize the cleanup task.

        Args:
            facade_cache_manager: FacadeCacheManager instance
            active_sessions: Dictionary of active chat sessions
            cleanup_interval_seconds: How often to run cleanup (default: 5 minutes)
            session_timeout_minutes: Session inactivity timeout (default: 30 minutes)
        """
        self.facade_cache = facade_cache_manager
        self.active_sessions = active_sessions
        self.cleanup_interval = cleanup_interval_seconds
        self.session_timeout = timedelta(minutes=session_timeout_minutes)

        self._running = False
        self._thread = None
        self._stop_event = threading.Event()

        logger.info(
            f"SessionCleanupTask initialized: "
            f"interval={cleanup_interval_seconds}s, "
            f"timeout={session_timeout_minutes}min"
        )

    def start(self):
        """Start the cleanup task in background thread."""
        if self._running:
            logger.warning("Cleanup task already running")
            return

        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_cleanup_loop, daemon=True)
        self._thread.start()

        logger.info("Session cleanup task started")

    def stop(self, timeout: float = 5.0):
        """
        Stop the cleanup task.

        Args:
            timeout: Maximum time to wait for thread to stop
        """
        if not self._running:
            return

        logger.info("Stopping session cleanup task...")
        self._running = False
        self._stop_event.set()

        if self._thread:
            self._thread.join(timeout=timeout)
            if self._thread.is_alive():
                logger.warning("Cleanup task did not stop within timeout")
            else:
                logger.info("Session cleanup task stopped")

    def is_running(self) -> bool:
        """Check if cleanup task is running."""
        return self._running

    def _run_cleanup_loop(self):
        """Main cleanup loop (runs in background thread)."""
        logger.info("Cleanup loop started")

        while self._running:
            try:
                # Run cleanup
                self._perform_cleanup()

                # Wait for next interval or stop signal
                self._stop_event.wait(timeout=self.cleanup_interval)

            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}", exc_info=True)
                # Continue running even if cleanup fails

        logger.info("Cleanup loop stopped")

    def _perform_cleanup(self):
        """Perform cleanup of expired sessions and facades."""
        try:
            start_time = time.time()

            # Clean up expired cache entries
            expired_count = self.facade_cache.cleanup_expired()

            # Find and clean up inactive sessions
            inactive_sessions = self._find_inactive_sessions()

            for session_id in inactive_sessions:
                try:
                    # Evict facades for this session
                    evicted = self.facade_cache.evict_session(session_id)

                    # Remove from active sessions
                    if session_id in self.active_sessions:
                        del self.active_sessions[session_id]

                    logger.info(
                        f"Cleaned up inactive session {session_id}: "
                        f"Evicted {evicted} facade(s)"
                    )

                except Exception as e:
                    logger.error(
                        f"Error cleaning up session {session_id}: {e}",
                        exc_info=True
                    )

            elapsed_time = time.time() - start_time

            if expired_count > 0 or len(inactive_sessions) > 0:
                logger.info(
                    f"Cleanup completed in {elapsed_time:.2f}s: "
                    f"Expired={expired_count}, "
                    f"Inactive sessions={len(inactive_sessions)}"
                )

            # Log statistics
            stats = self.facade_cache.get_stats()
            logger.debug(
                f"Cache stats: "
                f"facades={stats['total_cached_facades']}, "
                f"sessions={stats['active_sessions']}"
            )

        except Exception as e:
            logger.error(f"Error in cleanup: {e}", exc_info=True)

    def _find_inactive_sessions(self) -> list:
        """
        Find sessions that have been inactive beyond timeout.

        Returns:
            List of inactive session IDs
        """
        now = datetime.now()
        inactive = []

        for session_id, session_info in list(self.active_sessions.items()):
            last_activity = session_info.get('last_activity')

            if last_activity and (now - last_activity) > self.session_timeout:
                inactive.append(session_id)

        return inactive

    def force_cleanup(self):
        """Force immediate cleanup (for testing or manual trigger)."""
        logger.info("Forcing immediate cleanup...")
        self._perform_cleanup()


class SessionCleanupManager:
    """
    Manager for session cleanup with Flask integration.

    This class provides easy integration with Flask applications
    and automatic lifecycle management.
    """

    def __init__(self,
                 facade_cache_manager,
                 active_sessions: Dict[str, Dict[str, Any]],
                 auto_start: bool = True,
                 **kwargs):
        """
        Initialize the cleanup manager.

        Args:
            facade_cache_manager: FacadeCacheManager instance
            active_sessions: Dictionary of active chat sessions
            auto_start: Whether to start cleanup task immediately
            **kwargs: Additional arguments passed to SessionCleanupTask
        """
        self.cleanup_task = SessionCleanupTask(
            facade_cache_manager=facade_cache_manager,
            active_sessions=active_sessions,
            **kwargs
        )

        if auto_start:
            self.cleanup_task.start()

    def __enter__(self):
        """Context manager entry."""
        if not self.cleanup_task.is_running():
            self.cleanup_task.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup_task.stop()

    def start(self):
        """Start the cleanup task."""
        self.cleanup_task.start()

    def stop(self, timeout: float = 5.0):
        """Stop the cleanup task."""
        self.cleanup_task.stop(timeout=timeout)

    def is_running(self) -> bool:
        """Check if cleanup is running."""
        return self.cleanup_task.is_running()

    def force_cleanup(self):
        """Force immediate cleanup."""
        self.cleanup_task.force_cleanup()

    def get_stats(self) -> Dict[str, Any]:
        """Get cleanup statistics."""
        return {
            'running': self.cleanup_task.is_running(),
            'cleanup_interval': self.cleanup_task.cleanup_interval,
            'session_timeout_minutes': self.cleanup_task.session_timeout.total_seconds() / 60,
            'cache_stats': self.cleanup_task.facade_cache.get_stats()
        }


def create_cleanup_manager(facade_cache_manager,
                           active_sessions: Dict[str, Dict[str, Any]],
                           app_config: Optional[Dict[str, Any]] = None) -> SessionCleanupManager:
    """
    Factory function to create SessionCleanupManager with configuration.

    Args:
        facade_cache_manager: FacadeCacheManager instance
        active_sessions: Dictionary of active sessions
        app_config: Optional configuration dictionary

    Returns:
        Configured SessionCleanupManager instance
    """
    # Default configuration
    config = {
        'cleanup_interval_seconds': 300,  # 5 minutes
        'session_timeout_minutes': 30,  # 30 minutes
        'auto_start': True
    }

    # Override with app config if provided
    if app_config:
        config.update(app_config)

    manager = SessionCleanupManager(
        facade_cache_manager=facade_cache_manager,
        active_sessions=active_sessions,
        **config
    )

    logger.info(
        f"Created cleanup manager with config: "
        f"interval={config['cleanup_interval_seconds']}s, "
        f"timeout={config['session_timeout_minutes']}min"
    )

    return manager


__all__ = [
    'SessionCleanupTask',
    'SessionCleanupManager',
    'create_cleanup_manager'
]