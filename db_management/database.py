"""
Simple Database Persistence Layer
Supports SQLite and PostgreSQL without SQLAlchemy

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

import sqlite3
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from contextlib import contextmanager


class Database:
    """Simple database abstraction layer"""
    
    def __init__(self, db_type: str = 'sqlite', **kwargs):
        self.db_type = db_type
        self.connection = None
        
        if db_type == 'sqlite':
            db_path = kwargs.get('db_path', 'data/abhikarta.db_management')
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            self.db_path = db_path
        elif db_type == 'postgresql':
            import psycopg2
            self.pg_params = {
                'host': kwargs.get('host', 'localhost'),
                'port': kwargs.get('port', 5432),
                'database': kwargs.get('database', 'abhikarta'),
                'user': kwargs.get('user', 'postgres'),
                'password': kwargs.get('password', '')
            }
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            if self.db_type == 'sqlite':
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
            elif self.db_type == 'postgresql':
                import psycopg2
                import psycopg2.extras
                conn = psycopg2.connect(**self.pg_params)
                conn.cursor_factory = psycopg2.extras.RealDictCursor
            
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def execute(self, query: str, params: Tuple = ()) -> None:
        """Execute a query"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
    
    def fetchone(self, query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        """Fetch one row"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def fetchall(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Fetch all rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert a row and return last row id"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' if self.db_type == 'sqlite' else '%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(data.values()))
            return cursor.lastrowid
    
    def update(self, table: str, data: Dict[str, Any], where: str, where_params: Tuple = ()) -> int:
        """Update rows"""
        set_clause = ', '.join([f"{k} = {'?' if self.db_type == 'sqlite' else '%s'}" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(data.values()) + where_params)
            return cursor.rowcount
    
    def delete(self, table: str, where: str, where_params: Tuple = ()) -> int:
        """Delete rows"""
        query = f"DELETE FROM {table} WHERE {where}"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, where_params)
            return cursor.rowcount
    
    def initialize_schema(self) -> None:
        """Initialize database schema"""
        pass


# Global database instance
_db_instance: Optional[Database] = None

def get_db() -> Database:
    """Get global database instance"""
    global _db_instance
    if _db_instance is None:
        # Default to SQLite, can be configured
        _db_instance = Database(db_type='sqlite', db_path='data/abhikarta.db_management')
        _db_instance.initialize_schema()
    return _db_instance


def initialize_db(db_type: str = 'sqlite', **kwargs) -> Database:
    """Initialize database with specific configuration"""
    global _db_instance
    _db_instance = Database(db_type=db_type, **kwargs)
    _db_instance.initialize_schema()
    return _db_instance
