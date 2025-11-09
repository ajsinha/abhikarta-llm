"""
Connection Pool Manager - Singleton Implementation

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

from typing import Dict, Optional, Any
from threading import RLock
import logging
import atexit

from .abstract_pool import AbstractConnectionPool, PooledConnection
from .pool_config import PoolConfiguration
from .connection_pool_factory import create_connection_pool


class PoolManager:
    """
    Singleton Pool Manager for managing multiple database connection pools.
    
    This class implements the Singleton pattern to ensure only one instance
    manages all connection pools across the application. It provides thread-safe
    operations for pool management and connection handling.
    
    Features:
    - Thread-safe singleton implementation
    - Multiple pool management by name
    - Automatic cleanup on application exit
    - Deadlock-free design with consistent lock ordering
    
    Example:
        manager = PoolManager.get_instance()
        manager.create_pool(sqlite_config)
        conn = manager.get_connection_from_pool("my_pool")
        # Use connection
        manager.close_connection(conn, "my_pool")
    """
    
    _instance: Optional['PoolManager'] = None
    _lock: RLock = RLock()  # Class-level lock for singleton creation
    
    def __new__(cls) -> 'PoolManager':
        """
        Create or return the singleton instance.
        
        Uses double-checked locking pattern for thread-safe singleton creation.
        
        Returns:
            The singleton PoolManager instance
        """
        if cls._instance is None:
            with cls._lock:
                # Double-check after acquiring lock
                if cls._instance is None:
                    instance = super().__new__(cls)
                    cls._instance = instance
        return cls._instance
    
    def __init__(self):
        """
        Initialize the PoolManager (only called once for singleton).
        
        Sets up internal data structures and registers cleanup handler.
        """
        # Only initialize once
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self._pools: Dict[str, AbstractConnectionPool] = {}
        self._instance_lock = RLock()  # Instance-level lock for pool operations
        self._logger = logging.getLogger("PoolManager")
        
        # Register cleanup on exit
        atexit.register(self.shutdown_all)
        
        self._logger.info("PoolManager initialized")
    
    @classmethod
    def get_instance(cls) -> 'PoolManager':
        """
        Get the singleton instance of PoolManager.
        
        Returns:
            The singleton PoolManager instance
            
        Example:
            manager = PoolManager.get_instance()
        """
        return cls()
    
    def create_pool(self, config: PoolConfiguration) -> None:
        """
        Create a new connection pool with the given configuration.
        
        Args:
            config: Pool configuration object
            
        Raises:
            ValueError: If a pool with the same name already exists
            
        Example:
            config = SQLitePoolConfig(pool_name="my_db", database_path="app.db")
            manager.create_pool(config)
        """
        with self._instance_lock:
            pool_name = config.pool_name
            
            if pool_name in self._pools:
                raise ValueError(f"Pool '{pool_name}' already exists")
            
            # Create pool using factory
            pool = create_connection_pool(config)
            self._pools[pool_name] = pool
            
            self._logger.info(f"Created pool '{pool_name}' with {config.__class__.__name__}")
    
    def get_pool(self, pool_name: str) -> AbstractConnectionPool:
        """
        Get a connection pool by name.
        
        Args:
            pool_name: Name of the pool to retrieve
            
        Returns:
            The requested connection pool
            
        Raises:
            KeyError: If pool does not exist
        """
        with self._instance_lock:
            if pool_name not in self._pools:
                raise KeyError(f"Pool '{pool_name}' does not exist")
            return self._pools[pool_name]
    
    def pool_exists(self, pool_name: str) -> bool:
        """
        Check if a pool exists.
        
        Args:
            pool_name: Name of the pool to check
            
        Returns:
            True if pool exists, False otherwise
        """
        with self._instance_lock:
            return pool_name in self._pools
    
    def get_connection_from_pool(
        self, 
        pool_name: str, 
        timeout: Optional[float] = None
    ) -> PooledConnection:
        """
        Get a connection from the specified pool.
        
        Args:
            pool_name: Name of the pool to get connection from
            timeout: Maximum time to wait for a connection (uses pool default if None)
            
        Returns:
            A pooled connection object
            
        Raises:
            KeyError: If pool does not exist
            TimeoutError: If no connection available within timeout
            
        Example:
            conn = manager.get_connection_from_pool("my_pool")
            try:
                # Use connection
                cursor = conn.connection.cursor()
                cursor.execute("SELECT * FROM table")
            finally:
                manager.close_connection(conn, "my_pool")
        """
        pool = self.get_pool(pool_name)
        connection = pool.get_connection(timeout)
        self._logger.debug(f"Connection acquired from pool '{pool_name}'")
        return connection
    
    def close_connection(self, connection: PooledConnection, pool_name: str) -> None:
        """
        Return a connection to the specified pool.
        
        Args:
            connection: The pooled connection to return
            pool_name: Name of the pool to return connection to
            
        Raises:
            KeyError: If pool does not exist
            
        Example:
            manager.close_connection(conn, "my_pool")
        """
        pool = self.get_pool(pool_name)
        pool.close_connection(connection)
        self._logger.debug(f"Connection returned to pool '{pool_name}'")
    
    def get_connection_context(
        self, 
        pool_name: str, 
        timeout: Optional[float] = None
    ):
        """
        Get a context manager for automatic connection handling.
        
        Args:
            pool_name: Name of the pool to get connection from
            timeout: Maximum time to wait for a connection
            
        Yields:
            The underlying database connection object
            
        Example:
            with manager.get_connection_context("my_pool") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM table")
        """
        pool = self.get_pool(pool_name)
        return pool.get_connection_context(timeout)
    
    def remove_pool(self, pool_name: str, force: bool = False) -> None:
        """
        Remove and shutdown a connection pool.
        
        Args:
            pool_name: Name of the pool to remove
            force: If True, force removal even if connections are active
            
        Raises:
            KeyError: If pool does not exist
            RuntimeError: If pool has active connections and force=False
        """
        with self._instance_lock:
            if pool_name not in self._pools:
                raise KeyError(f"Pool '{pool_name}' does not exist")
            
            pool = self._pools[pool_name]
            stats = pool.get_stats()
            
            if not force and stats['active_connections'] > 0:
                raise RuntimeError(
                    f"Pool '{pool_name}' has {stats['active_connections']} active connections. "
                    f"Use force=True to remove anyway."
                )
            
            # Shutdown and remove pool
            pool.shutdown()
            del self._pools[pool_name]
            
            self._logger.info(f"Removed pool '{pool_name}'")
    
    def get_all_pool_names(self) -> list:
        """
        Get names of all registered pools.
        
        Returns:
            List of pool names
        """
        with self._instance_lock:
            return list(self._pools.keys())
    
    def get_pool_stats(self, pool_name: str) -> dict:
        """
        Get statistics for a specific pool.
        
        Args:
            pool_name: Name of the pool
            
        Returns:
            Dictionary with pool statistics
            
        Raises:
            KeyError: If pool does not exist
        """
        pool = self.get_pool(pool_name)
        return pool.get_stats()
    
    def get_all_stats(self) -> Dict[str, dict]:
        """
        Get statistics for all pools.
        
        Returns:
            Dictionary mapping pool names to their statistics
        """
        with self._instance_lock:
            return {
                name: pool.get_stats()
                for name, pool in self._pools.items()
            }
    
    def shutdown_all(self) -> None:
        """
        Shutdown all connection pools.
        
        This method is automatically called on application exit.
        It can also be called manually for graceful shutdown.
        """
        with self._instance_lock:
            self._logger.info("Shutting down all connection pools")
            
            for pool_name, pool in list(self._pools.items()):
                try:
                    pool.shutdown()
                    self._logger.info(f"Shutdown pool '{pool_name}'")
                except Exception as e:
                    self._logger.error(f"Error shutting down pool '{pool_name}': {e}")
            
            self._pools.clear()
            self._logger.info("All pools shut down")
    
    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance (primarily for testing).
        
        Warning: This should only be used in testing scenarios.
        """
        with cls._lock:
            if cls._instance is not None:
                cls._instance.shutdown_all()
                cls._instance = None


# Convenience function to get the singleton instance
def get_pool_manager() -> PoolManager:
    """
    Get the singleton PoolManager instance.
    
    Returns:
        The singleton PoolManager instance
        
    Example:
        manager = get_pool_manager()
    """
    return PoolManager.get_instance()
