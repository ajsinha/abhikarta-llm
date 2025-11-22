from contextlib import contextmanager
from db_management.pool_manager import get_pool_manager
import logging

logger = logging.getLogger(__name__)

class DBAware:
    def __init__(self, db_connection_pool_name: str):
        """
        Initialize the database-backed role manager.

        Args:
            db_connection_pool_name: Database connection pool name
        """
        self._db_connection_pool_name = db_connection_pool_name
        self._connection_pool_manager = get_pool_manager()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections with auto-commit."""
        with self._connection_pool_manager.get_connection_context(self._db_connection_pool_name) as conn:
            try:
                yield conn  # Yields the actual connection
                conn.commit()  # Auto-commit on success
            except Exception as e:
                conn.rollback()  # Auto-rollback on error
                logger.error(f"Database error: {e}")
                raise

    @contextmanager
    def _get_cursor(self, conn):
        """Context manager for database cursors."""
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()