"""
Abstract Connection Pool Base Classes

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This document and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use of this document or the software
system it describes is strictly prohibited without explicit written permission from the
copyright holder. This document is provided "as is" without warranty of any kind, either
expressed or implied. The copyright holder shall not be liable for any damages arising
from the use of this document or the software system it describes.

Patent Pending: Certain architectural patterns and implementations described in this
document may be subject to patent applications.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Set
from threading import RLock, Thread, Event
import time
import logging
from contextlib import contextmanager
from queue import Queue, Empty, Full

from .pool_config import PoolConfiguration


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class PooledConnection:
    """
    Wrapper class for pooled database connections.
    
    Tracks connection state, usage statistics, and provides automatic
    return to pool functionality.
    """
    
    def __init__(self, connection: Any, pool: 'AbstractConnectionPool'):
        """
        Initialize a pooled connection.
        
        Args:
            connection: The underlying database connection object
            pool: Reference to the parent connection pool
        """
        self._connection = connection
        self._pool = pool
        self._in_use = False
        self._created_at = time.time()
        self._last_used = time.time()
        self._use_count = 0

    @property
    def cursor(self):
        return self._connection.cursor()

    @property
    def connection(self) -> Any:
        """Get the underlying connection object."""
        return self._connection
    
    @property
    def in_use(self) -> bool:
        """Check if connection is currently in use."""
        return self._in_use
    
    @property
    def idle_time(self) -> float:
        """Get idle time in seconds."""
        return time.time() - self._last_used
    
    @property
    def age(self) -> float:
        """Get connection age in seconds."""
        return time.time() - self._created_at
    
    def mark_in_use(self) -> None:
        """Mark connection as in use."""
        self._in_use = True
        self._use_count += 1
        self._last_used = time.time()
    
    def mark_idle(self) -> None:
        """Mark connection as idle."""
        self._in_use = False
        self._last_used = time.time()
    
    def close(self) -> None:
        """Close the underlying connection."""
        try:
            if self._connection:
                self._connection.close()
        except Exception as e:
            logging.warning(f"Error closing connection: {e}")
        finally:
            self._connection = None
    
    def __enter__(self):
        """Enter context manager - return the underlying connection."""
        return self._connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager - return connection to pool."""
        if self._pool is not None:
            self._pool.close_connection(self)
        return False  # Don't suppress exceptions


class AbstractConnectionPool(ABC):
    """
    Abstract base class for database connection pools.
    
    Implements the Object Pool pattern with thread-safe operations.
    Subclasses must implement database-specific connection creation and validation.
    """
    
    def __init__(self, config: PoolConfiguration):
        """
        Initialize the connection pool.
        
        Args:
            config: Pool configuration object
        """
        config.validate()
        self._config = config
        self._lock = RLock()  # Reentrant lock for thread safety
        
        # Connection management
        self._available_connections: Queue = Queue(maxsize=config.max_connections)
        self._all_connections: Set[PooledConnection] = set()
        self._active_count = 0
        
        # Background maintenance
        self._cleanup_thread: Optional[Thread] = None
        self._shutdown_event = Event()
        self._logger = logging.getLogger(f"{self.__class__.__name__}:{config.pool_name}")
        
        # Initialize pool
        self._initialize_pool()
        self._start_cleanup_thread()
    
    @abstractmethod
    def _create_raw_connection(self) -> Any:
        """
        Create a new database connection.
        
        Returns:
            A new database connection object
            
        Raises:
            Exception: If connection creation fails
        """
        pass
    
    @abstractmethod
    def _validate_connection(self, connection: Any) -> bool:
        """
        Validate that a connection is still alive and functional.
        
        Args:
            connection: Database connection to validate
            
        Returns:
            True if connection is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def _close_raw_connection(self, connection: Any) -> None:
        """
        Close a database connection.
        
        Args:
            connection: Database connection to close
        """
        pass
    
    def _initialize_pool(self) -> None:
        """Initialize the pool with minimum number of connections."""
        with self._lock:
            for _ in range(self._config.min_connections):
                try:
                    pooled_conn = self._create_pooled_connection()
                    self._available_connections.put_nowait(pooled_conn)
                    self._all_connections.add(pooled_conn)
                except Exception as e:
                    self._logger.error(f"Error initializing connection: {e}")
    
    def _create_pooled_connection(self) -> PooledConnection:
        """
        Create a new pooled connection.
        
        Returns:
            A new PooledConnection instance
        """
        raw_conn = self._create_raw_connection()
        return PooledConnection(raw_conn, self)
    
    def get_connection(self, timeout: Optional[float] = None) -> PooledConnection:
        """
        Get a connection from the pool.
        
        Args:
            timeout: Maximum time to wait for a connection (uses config default if None)
            
        Returns:
            A pooled connection object
            
        Raises:
            TimeoutError: If no connection available within timeout
            RuntimeError: If pool is shut down
        """
        if self._shutdown_event.is_set():
            raise RuntimeError("Connection pool is shut down")
        
        timeout = timeout or self._config.connection_timeout
        deadline = time.time() + timeout
        
        while True:
            remaining_time = deadline - time.time()
            if remaining_time <= 0:
                raise TimeoutError(
                    f"Could not acquire connection within {timeout} seconds"
                )
            
            try:
                # Try to get an available connection
                pooled_conn = self._available_connections.get(
                    timeout=min(remaining_time, 0.1)
                )
                
                # Validate connection
                if self._validate_connection(pooled_conn.connection):
                    with self._lock:
                        pooled_conn.mark_in_use()
                        self._active_count += 1
                    self._logger.debug(f"Connection acquired from pool")
                    return pooled_conn
                else:
                    # Connection is invalid, close and create new one
                    self._logger.warning("Invalid connection detected, creating new one")
                    with self._lock:
                        self._all_connections.discard(pooled_conn)
                        pooled_conn.close()
                    
            except Empty:
                # No available connections, try to create new one
                with self._lock:
                    if len(self._all_connections) < self._config.max_connections:
                        try:
                            pooled_conn = self._create_pooled_connection()
                            self._all_connections.add(pooled_conn)
                            pooled_conn.mark_in_use()
                            self._active_count += 1
                            self._logger.debug("Created new connection")
                            return pooled_conn
                        except Exception as e:
                            self._logger.error(f"Error creating connection: {e}")
                            time.sleep(0.1)  # Brief pause before retry
    
    def close_connection(self, pooled_conn: PooledConnection) -> None:
        """
        Return a connection to the pool.
        
        Args:
            pooled_conn: The pooled connection to return
        """
        if not isinstance(pooled_conn, PooledConnection):
            raise TypeError("Expected PooledConnection instance")
        
        with self._lock:
            if pooled_conn not in self._all_connections:
                self._logger.warning("Attempted to return unknown connection")
                return
            
            if not pooled_conn.in_use:
                self._logger.warning("Attempted to return connection that's not in use")
                return
            
            pooled_conn.mark_idle()
            self._active_count -= 1
            
            try:
                # Validate before returning to pool
                if self._validate_connection(pooled_conn.connection):
                    self._available_connections.put_nowait(pooled_conn)
                    self._logger.debug("Connection returned to pool")
                else:
                    # Connection is invalid, remove from pool
                    self._all_connections.discard(pooled_conn)
                    pooled_conn.close()
                    self._logger.warning("Invalid connection removed from pool")
            except Full:
                # Pool is full, close the connection
                self._all_connections.discard(pooled_conn)
                pooled_conn.close()
                self._logger.debug("Pool full, connection closed")
    
    @contextmanager
    def get_connection_context(self, timeout: Optional[float] = None):
        """
        Context manager for automatic connection return.
        
        Args:
            timeout: Maximum time to wait for a connection
            
        Yields:
            The underlying database connection object
            
        Example:
            with pool.get_connection_context() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM table")
        """
        pooled_conn = self.get_connection(timeout)
        try:
            yield pooled_conn.connection
        finally:
            self.close_connection(pooled_conn)
    
    def _cleanup_idle_connections(self) -> None:
        """Remove excess idle connections based on configuration."""
        with self._lock:
            idle_connections = []
            
            # Collect all available connections temporarily
            while not self._available_connections.empty():
                try:
                    conn = self._available_connections.get_nowait()
                    idle_connections.append(conn)
                except Empty:
                    break
            
            # Sort by idle time (oldest first)
            idle_connections.sort(key=lambda c: c.idle_time, reverse=True)
            
            # Determine how many to close
            excess_count = len(idle_connections) - self._config.max_idle_connections
            
            if excess_count > 0:
                # Keep minimum connections
                total_connections = len(self._all_connections)
                can_close = max(0, total_connections - self._config.min_connections)
                to_close = min(excess_count, can_close)
                
                # Close excess connections
                for i in range(to_close):
                    conn = idle_connections.pop(0)
                    self._all_connections.discard(conn)
                    conn.close()
                    self._logger.info(f"Closed idle connection (age: {conn.age:.2f}s)")
            
            # Return remaining connections to pool
            for conn in idle_connections:
                try:
                    self._available_connections.put_nowait(conn)
                except Full:
                    # Should not happen, but handle gracefully
                    self._all_connections.discard(conn)
                    conn.close()
    
    def _maintenance_loop(self) -> None:
        """Background thread for pool maintenance."""
        self._logger.info("Maintenance thread started")
        
        while not self._shutdown_event.is_set():
            try:
                # Wait with ability to interrupt
                if self._shutdown_event.wait(self._config.validation_interval):
                    break
                
                self._cleanup_idle_connections()
                
            except Exception as e:
                self._logger.error(f"Error in maintenance loop: {e}")
        
        self._logger.info("Maintenance thread stopped")
    
    def _start_cleanup_thread(self) -> None:
        """Start the background cleanup thread."""
        self._cleanup_thread = Thread(
            target=self._maintenance_loop,
            name=f"PoolCleanup-{self._config.pool_name}",
            daemon=True
        )
        self._cleanup_thread.start()
    
    def get_stats(self) -> dict:
        """
        Get current pool statistics.
        
        Returns:
            Dictionary with pool statistics
        """
        with self._lock:
            return {
                'pool_name': self._config.pool_name,
                'total_connections': len(self._all_connections),
                'active_connections': self._active_count,
                'available_connections': self._available_connections.qsize(),
                'max_connections': self._config.max_connections,
                'min_connections': self._config.min_connections,
            }
    
    def shutdown(self) -> None:
        """Shutdown the pool and close all connections."""
        self._logger.info("Shutting down connection pool")
        self._shutdown_event.set()
        
        # Wait for cleanup thread
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5.0)
        
        # Close all connections
        with self._lock:
            for conn in list(self._all_connections):
                conn.close()
            self._all_connections.clear()
            
            # Clear the queue
            while not self._available_connections.empty():
                try:
                    self._available_connections.get_nowait()
                except Empty:
                    break
        
        self._logger.info("Connection pool shut down complete")
