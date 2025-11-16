"""
Abhikarta LLM Platform - Database Manager
Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)
"""

import sqlite3
import logging
from pathlib import Path
from contextlib import contextmanager
from threading import RLock

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations"""
    
    _instance = None
    _lock = RLock()
    
    def __new__(cls, db_path: str = "llm_execution.db"):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    cls._instance = instance
        return cls._instance
    
    def __init__(self, db_path: str = "llm_execution.db"):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        self.db_path = db_path
        self._connections = {}
        
    @contextmanager
    def get_connection(self):
        """Get database connection"""
        import threading
        thread_id = threading.get_ident()
        
        if thread_id not in self._connections:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            self._connections[thread_id] = conn
        
        try:
            yield self._connections[thread_id]
        except Exception as e:
            self._connections[thread_id].rollback()
            raise
    
    def initialize_schema(self, schema_path: str = None):
        """Initialize database schema"""
        if schema_path is None:
            schema_path = Path(__file__).parent / "schema.sql"
        
        with open(schema_path, "r") as f:
            schema_sql = f.read()
        
        with self.get_connection() as conn:
            conn.executescript(schema_sql)
            conn.commit()
        
        logger.info(f"Database initialized: {self.db_path}")
