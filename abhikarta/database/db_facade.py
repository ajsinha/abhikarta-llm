"""
Database Facade Module - Unified interface for database operations.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseHandler(ABC):
    """Abstract base class for database handlers."""
    
    @abstractmethod
    def connect(self) -> None:
        """Establish database connection."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection."""
        pass
    
    @abstractmethod
    def execute(self, query: str, params: tuple = None) -> Any:
        """Execute a query and return last row ID."""
        pass
    
    @abstractmethod
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """Fetch single row as dictionary."""
        pass
    
    @abstractmethod
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict]:
        """Fetch all rows as list of dictionaries."""
        pass
    
    @abstractmethod
    def init_schema(self) -> None:
        """Initialize database schema."""
        pass


class DatabaseFacade:
    """
    Facade for database operations.
    Automatically selects SQLite or PostgreSQL based on configuration.
    """
    
    def __init__(self, settings):
        """
        Initialize database facade.
        
        Args:
            settings: Settings object with database configuration
        """
        self.settings = settings
        self._handler: DatabaseHandler = None
        self._init_handler()
    
    def _init_handler(self) -> None:
        """Initialize appropriate database handler based on config."""
        db_type = self.settings.database.type.lower()
        
        if db_type == "sqlite":
            from .sqlite_handler import SQLiteHandler
            self._handler = SQLiteHandler(self.settings.database.sqlite_path)
            logger.info(f"Initialized SQLite handler: {self.settings.database.sqlite_path}")
        
        elif db_type == "postgresql":
            from .postgres_handler import PostgresHandler
            self._handler = PostgresHandler(
                host=self.settings.database.pg_host,
                port=self.settings.database.pg_port,
                database=self.settings.database.pg_database,
                user=self.settings.database.pg_user,
                password=self.settings.database.pg_password
            )
            logger.info(f"Initialized PostgreSQL handler: {self.settings.database.pg_host}")
        
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def connect(self) -> None:
        """Establish database connection."""
        self._handler.connect()
        logger.info("Database connected")
    
    def disconnect(self) -> None:
        """Close database connection."""
        self._handler.disconnect()
        logger.info("Database disconnected")
    
    def execute(self, query: str, params: tuple = None) -> Any:
        """
        Execute a query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Last row ID or None
        """
        return self._handler.execute(query, params)
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """
        Fetch single row.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Row as dictionary or None
        """
        return self._handler.fetch_one(query, params)
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict]:
        """
        Fetch all rows.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of rows as dictionaries
        """
        return self._handler.fetch_all(query, params)
    
    def init_schema(self) -> None:
        """Initialize database schema."""
        self._handler.init_schema()
        logger.info("Database schema initialized")
    
    @property
    def db_type(self) -> str:
        """Get current database type."""
        return self.settings.database.type
