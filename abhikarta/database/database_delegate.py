"""
Database Delegate Module - Abstract base class for database delegates.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.

Version: 1.2.1
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DatabaseDelegate(ABC):
    """
    Abstract base class for database delegates.
    
    Each delegate handles database operations for a specific domain
    (users, agents, workflows, etc.), encapsulating all SQL queries
    and providing a clean interface for the application layer.
    """
    
    def __init__(self, db_facade):
        """
        Initialize database delegate.
        
        Args:
            db_facade: DatabaseFacade instance for database access
        """
        self._db = db_facade
    
    @property
    def db(self):
        """Get database facade instance."""
        return self._db
    
    def execute(self, query: str, params: tuple = None) -> Any:
        """
        Execute a query (INSERT, UPDATE, DELETE).
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Last row ID or None
        """
        return self._db.execute(query, params)
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """
        Fetch single row as dictionary.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Row as dictionary or None
        """
        return self._db.fetch_one(query, params)
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict]:
        """
        Fetch all rows as list of dictionaries.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of rows as dictionaries
        """
        return self._db.fetch_all(query, params)
    
    def get_count(self, table: str, where: str = None, params: tuple = None) -> int:
        """
        Get count of rows in a table.
        
        Args:
            table: Table name
            where: Optional WHERE clause (without 'WHERE' keyword)
            params: Query parameters
            
        Returns:
            Row count
        """
        query = f"SELECT COUNT(*) as count FROM {table}"
        if where:
            query += f" WHERE {where}"
        result = self.fetch_one(query, params)
        return result.get('count', 0) if result else 0
    
    def exists(self, table: str, where: str, params: tuple) -> bool:
        """
        Check if a row exists.
        
        Args:
            table: Table name
            where: WHERE clause (without 'WHERE' keyword)
            params: Query parameters
            
        Returns:
            True if row exists
        """
        return self.get_count(table, where, params) > 0
