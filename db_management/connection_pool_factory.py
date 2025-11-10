"""
Concrete Connection Pool Implementations

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

import sqlite3
from typing import Any
import logging
import time

from .abstract_pool import AbstractConnectionPool
from .pool_config import SQLitePoolConfig, PostgreSQLPoolConfig, MySQLPoolConfig


class SQLiteConnectionPool(AbstractConnectionPool):
    """
    Connection pool implementation for SQLite databases.

    Supports both file-based and in-memory SQLite databases with
    thread-safe connection management. Includes automatic WAL mode
    configuration and retry logic for database locked errors.
    """

    def __init__(self, config: SQLitePoolConfig):
        """
        Initialize SQLite connection pool.

        Args:
            config: SQLite pool configuration
        """
        self._logger = logging.getLogger(f"SQLitePool:{config.pool_name}")
        self._config = config  # Store config before super().__init__
        super().__init__(config)

    def _configure_connection(self, conn: sqlite3.Connection) -> None:
        """
        Configure SQLite connection with optimal settings for pooling.

        Args:
            conn: SQLite connection to configure
        """
        cursor = conn.cursor()

        try:
            # Set busy timeout (in milliseconds)
            cursor.execute(f"PRAGMA busy_timeout = {self._config.busy_timeout}")

            # Enable WAL mode for better concurrency (only for file-based databases)
            if self._config.enable_wal_mode and self._config.database_path != ":memory:":
                cursor.execute(f"PRAGMA journal_mode = {self._config.journal_mode}")
                result = cursor.fetchone()
                self._logger.info(f"Journal mode set to: {result[0] if result else 'unknown'}")

            # Set synchronous mode
            cursor.execute(f"PRAGMA synchronous = {self._config.synchronous}")

            # Set cache size (negative value means KB)
            cursor.execute(f"PRAGMA cache_size = {self._config.cache_size}")

            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")

            # Set temp_store to memory for better performance
            cursor.execute("PRAGMA temp_store = MEMORY")

            conn.commit()
            self._logger.debug("SQLite connection configured successfully")

        except Exception as e:
            self._logger.warning(f"Error configuring connection: {e}")
        finally:
            cursor.close()

    def _create_raw_connection(self) -> sqlite3.Connection:
        """
        Create a new SQLite connection with retry logic for locked database.

        Returns:
            SQLite connection object

        Raises:
            Exception: If connection creation fails after retries
        """
        params = self._config.get_connection_params()
        max_retries = 3
        retry_delay = 0.5  # seconds

        for attempt in range(max_retries):
            try:
                conn = sqlite3.connect(**params)
                conn.row_factory = sqlite3.Row  # Enable column access by name

                # Configure the connection
                self._configure_connection(conn)

                self._logger.debug(f"Created SQLite connection to {params['database']}")
                return conn

            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                    self._logger.warning(
                        f"Database locked on connection creation (attempt {attempt + 1}/{max_retries}), "
                        f"retrying in {retry_delay}s..."
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    raise
            except Exception as e:
                self._logger.error(f"Error creating SQLite connection: {e}")
                raise

    def _validate_connection(self, connection: sqlite3.Connection) -> bool:
        """
        Validate SQLite connection by executing a simple query with retry logic.

        Args:
            connection: SQLite connection to validate

        Returns:
            True if connection is valid, False otherwise
        """
        max_retries = 2
        retry_delay = 0.1

        for attempt in range(max_retries):
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                return True

            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                    self._logger.debug(
                        f"Database locked during validation (attempt {attempt + 1}/{max_retries}), retrying..."
                    )
                    time.sleep(retry_delay)
                else:
                    self._logger.warning(f"Connection validation failed: {e}")
                    return False

            except Exception as e:
                self._logger.warning(f"Connection validation failed: {e}")
                return False

        return False

    def _close_raw_connection(self, connection: sqlite3.Connection) -> None:
        """
        Close SQLite connection.

        Args:
            connection: SQLite connection to close
        """
        try:
            # Rollback any pending transactions
            try:
                connection.rollback()
            except Exception:
                pass

            connection.close()
            self._logger.debug("Closed SQLite connection")
        except Exception as e:
            self._logger.warning(f"Error closing connection: {e}")


class PostgreSQLConnectionPool(AbstractConnectionPool):
    """
    Connection pool implementation for PostgreSQL databases.

    Requires psycopg2 or psycopg (psycopg3) to be installed.
    """

    def __init__(self, config: PostgreSQLPoolConfig):
        """
        Initialize PostgreSQL connection pool.

        Args:
            config: PostgreSQL pool configuration
        """
        self._logger = logging.getLogger(f"PostgreSQLPool:{config.pool_name}")

        # Import psycopg2/psycopg
        try:
            import psycopg2
            self._psycopg_module = psycopg2
            self._psycopg_errors = psycopg2.errors
            self._connection_error = psycopg2.OperationalError
            self._logger.info("Using psycopg2 for PostgreSQL connections")
        except ImportError:
            try:
                import psycopg
                self._psycopg_module = psycopg
                self._psycopg_errors = psycopg.errors
                self._connection_error = psycopg.OperationalError
                self._logger.info("Using psycopg3 for PostgreSQL connections")
            except ImportError:
                raise ImportError(
                    "PostgreSQL connection requires either psycopg2 or psycopg (psycopg3) "
                    "to be installed. Install with: pip install psycopg2-binary or pip install psycopg"
                )

        super().__init__(config)

    def _create_raw_connection(self) -> Any:
        """
        Create a new PostgreSQL connection.

        Returns:
            PostgreSQL connection object
        """
        params = self._config.get_connection_params()
        conn = self._psycopg_module.connect(**params)
        self._logger.debug(
            f"Created PostgreSQL connection to {params['host']}:{params['port']}/{params['database']}"
        )
        return conn

    def _validate_connection(self, connection: Any) -> bool:
        """
        Validate PostgreSQL connection.

        Args:
            connection: PostgreSQL connection to validate

        Returns:
            True if connection is valid, False otherwise
        """
        try:
            # Check if connection is closed
            if connection.closed:
                return False

            # Execute simple query
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception as e:
            self._logger.warning(f"Connection validation failed: {e}")
            return False

    def _close_raw_connection(self, connection: Any) -> None:
        """
        Close PostgreSQL connection.

        Args:
            connection: PostgreSQL connection to close
        """
        try:
            if not connection.closed:
                connection.close()
            self._logger.debug("Closed PostgreSQL connection")
        except Exception as e:
            self._logger.warning(f"Error closing connection: {e}")


class MySQLConnectionPool(AbstractConnectionPool):
    """
    Connection pool implementation for MySQL/MariaDB databases.

    Requires mysql-connector-python or PyMySQL to be installed.
    """

    def __init__(self, config: MySQLPoolConfig):
        """
        Initialize MySQL connection pool.

        Args:
            config: MySQL pool configuration
        """
        self._logger = logging.getLogger(f"MySQLPool:{config.pool_name}")

        # Import MySQL connector
        try:
            import mysql.connector
            self._mysql_module = mysql.connector
            self._connection_error = mysql.connector.Error
            self._logger.info("Using mysql-connector-python for MySQL connections")
        except ImportError:
            try:
                import pymysql
                self._mysql_module = pymysql
                self._connection_error = pymysql.Error
                self._logger.info("Using PyMySQL for MySQL connections")
            except ImportError:
                raise ImportError(
                    "MySQL connection requires either mysql-connector-python or PyMySQL "
                    "to be installed. Install with: pip install mysql-connector-python or pip install pymysql"
                )

        super().__init__(config)

    def _create_raw_connection(self) -> Any:
        """
        Create a new MySQL connection.

        Returns:
            MySQL connection object
        """
        params = self._config.get_connection_params()
        conn = self._mysql_module.connect(**params)
        self._logger.debug(
            f"Created MySQL connection to {params['host']}:{params['port']}/{params['database']}"
        )
        return conn

    def _validate_connection(self, connection: Any) -> bool:
        """
        Validate MySQL connection.

        Args:
            connection: MySQL connection to validate

        Returns:
            True if connection is valid, False otherwise
        """
        try:
            # Check if connection is open
            if not connection.is_connected():
                return False

            # Execute simple query
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception as e:
            self._logger.warning(f"Connection validation failed: {e}")
            return False

    def _close_raw_connection(self, connection: Any) -> None:
        """
        Close MySQL connection.

        Args:
            connection: MySQL connection to close
        """
        try:
            if connection.is_connected():
                connection.close()
            self._logger.debug("Closed MySQL connection")
        except Exception as e:
            self._logger.warning(f"Error closing connection: {e}")


# Factory function for creating pools
def create_connection_pool(config: Any) -> AbstractConnectionPool:
    """
    Factory function to create appropriate connection pool based on configuration.

    Args:
        config: Pool configuration object (SQLitePoolConfig, PostgreSQLPoolConfig, etc.)

    Returns:
        Appropriate connection pool instance

    Raises:
        ValueError: If configuration type is not recognized
    """
    if isinstance(config, SQLitePoolConfig):
        return SQLiteConnectionPool(config)
    elif isinstance(config, PostgreSQLPoolConfig):
        return PostgreSQLConnectionPool(config)
    elif isinstance(config, MySQLPoolConfig):
        return MySQLConnectionPool(config)
    else:
        raise ValueError(f"Unknown configuration type: {type(config)}")