"""
Database Connection Pool Configuration Module

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

from dataclasses import dataclass
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod


@dataclass
class PoolConfiguration(ABC):
    """
    Abstract base class for connection pool configuration.
    
    Attributes:
        pool_name: Unique identifier for the pool
        min_connections: Minimum number of connections to maintain
        max_connections: Maximum number of connections allowed
        max_idle_connections: Maximum number of idle connections before cleanup
        connection_timeout: Timeout in seconds for acquiring a connection
        idle_timeout: Time in seconds before an idle connection is closed
        validation_interval: Interval in seconds to validate connections
    """
    pool_name: str
    min_connections: int = 2
    max_connections: int = 10
    max_idle_connections: int = 5
    connection_timeout: float = 30.0
    idle_timeout: float = 300.0  # 5 minutes
    validation_interval: float = 60.0  # 1 minute
    
    @abstractmethod
    def get_connection_params(self) -> Dict[str, Any]:
        """Return database-specific connection parameters."""
        pass
    
    def validate(self) -> None:
        """Validate configuration parameters."""
        if self.min_connections < 0:
            raise ValueError("min_connections must be non-negative")
        if self.max_connections < self.min_connections:
            raise ValueError("max_connections must be >= min_connections")
        if self.max_idle_connections < 0:
            raise ValueError("max_idle_connections must be non-negative")
        if self.connection_timeout <= 0:
            raise ValueError("connection_timeout must be positive")
        if self.idle_timeout <= 0:
            raise ValueError("idle_timeout must be positive")


@dataclass
class SQLitePoolConfig(PoolConfiguration):
    """Configuration for SQLite connection pools."""
    
    database_path: str = ":memory:"
    check_same_thread: bool = False
    timeout: float = 5.0
    isolation_level: Optional[str] = None
    
    def get_connection_params(self) -> Dict[str, Any]:
        """Return SQLite connection parameters."""
        return {
            'database': self.database_path,
            'check_same_thread': self.check_same_thread,
            'timeout': self.timeout,
            'isolation_level': self.isolation_level
        }


@dataclass
class PostgreSQLPoolConfig(PoolConfiguration):
    """Configuration for PostgreSQL connection pools."""
    
    host: str = "localhost"
    port: int = 5432
    database: str = "postgres"
    user: str = "postgres"
    password: str = ""
    sslmode: str = "prefer"
    connect_timeout: int = 10
    
    def get_connection_params(self) -> Dict[str, Any]:
        """Return PostgreSQL connection parameters."""
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'password': self.password,
            'sslmode': self.sslmode,
            'connect_timeout': self.connect_timeout
        }


@dataclass
class MySQLPoolConfig(PoolConfiguration):
    """Configuration for MySQL connection pools."""
    
    host: str = "localhost"
    port: int = 3306
    database: str = "mysql"
    user: str = "root"
    password: str = ""
    charset: str = "utf8mb4"
    connect_timeout: int = 10
    autocommit: bool = False
    
    def get_connection_params(self) -> Dict[str, Any]:
        """Return MySQL connection parameters."""
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'password': self.password,
            'charset': self.charset,
            'connect_timeout': self.connect_timeout,
            'autocommit': self.autocommit
        }
