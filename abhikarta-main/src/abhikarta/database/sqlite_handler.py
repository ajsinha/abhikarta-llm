"""
SQLite Handler Module - SQLite database implementation.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.
"""

import sqlite3
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime
import logging
import threading

from .db_facade import DatabaseHandler

logger = logging.getLogger(__name__)


class SQLiteHandler(DatabaseHandler):
    """SQLite implementation of DatabaseHandler."""
    
    def __init__(self, db_path: str):
        """
        Initialize SQLite handler.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._local = threading.local()
        logger.info(f"SQLite handler created for: {db_path}")
    
    @property
    def connection(self):
        """Get thread-local connection."""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self.connect()
        return self._local.connection
    
    def connect(self) -> None:
        """Establish database connection."""
        # Ensure directory exists
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Register custom timestamp converter that handles ISO format (with T separator)
        def convert_timestamp(val):
            """Convert timestamp bytes to datetime, handling ISO format."""
            if val is None:
                return None
            try:
                # Decode bytes to string
                if isinstance(val, bytes):
                    val = val.decode('utf-8')
                # Handle ISO format with T separator
                val = val.replace('T', ' ')
                # Handle microseconds
                if '.' in val:
                    return datetime.strptime(val, '%Y-%m-%d %H:%M:%S.%f')
                else:
                    return datetime.strptime(val, '%Y-%m-%d %H:%M:%S')
            except Exception:
                # Return as string if parsing fails
                return val
        
        # Register the converter
        sqlite3.register_converter("TIMESTAMP", convert_timestamp)
        sqlite3.register_converter("timestamp", convert_timestamp)
        
        self._local.connection = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        logger.debug(f"SQLite connected: {self.db_path}")
    
    def disconnect(self) -> None:
        """Close database connection."""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
            logger.debug("SQLite disconnected")
    
    def execute(self, query: str, params: tuple = None) -> Any:
        """
        Execute a query.
        
        Args:
            query: SQL query string
            params: Query parameters (must be tuple or None)
            
        Returns:
            Last row ID
        """
        cursor = self.connection.cursor()
        try:
            # Ensure params is properly formatted
            if params is not None:
                # Convert to tuple if it's a list
                if isinstance(params, list):
                    params = tuple(params)
                # Ensure single values are wrapped in tuple
                elif not isinstance(params, tuple):
                    params = (params,)
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"SQLite execute error: {e}")
            logger.error(f"Query: {query[:100]}...")
            logger.error(f"Params: {params} (type: {type(params).__name__ if params else 'None'})")
            self.connection.rollback()
            raise
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """
        Fetch single row.
        
        Args:
            query: SQL query string
            params: Query parameters (must be tuple or None)
            
        Returns:
            Row as dictionary or None
        """
        cursor = self.connection.cursor()
        try:
            # Step 1: Prepare params
            if params is not None:
                if isinstance(params, list):
                    params = tuple(params)
                elif not isinstance(params, tuple):
                    params = (params,)
            
            # Step 2: Execute query
            try:
                if params is not None:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
            except Exception as exec_err:
                logger.error(f"fetch_one execute error: {exec_err}")
                raise
            
            # Step 3: Fetch row
            try:
                row = cursor.fetchone()
            except Exception as fetch_err:
                logger.error(f"fetch_one fetchone error: {fetch_err}")
                raise
            
            if row is None:
                return None
            
            # Step 4: Get column names
            try:
                if cursor.description is None:
                    logger.warning("fetch_one: cursor.description is None")
                    return None
                columns = []
                for i, desc in enumerate(cursor.description):
                    col_name = desc[0] if desc else f"col_{i}"
                    columns.append(col_name)
            except Exception as col_err:
                logger.error(f"fetch_one column extraction error: {col_err}")
                raise
            
            # Step 5: Build dict manually (most compatible way)
            try:
                result = {}
                for i, col in enumerate(columns):
                    if i < len(row):
                        result[col] = row[i]
                return result
            except Exception as dict_err:
                logger.error(f"fetch_one dict building error: {dict_err}")
                logger.error(f"row type: {type(row)}, row: {row}")
                logger.error(f"columns: {columns}")
                raise
            
        except Exception as e:
            logger.error(f"SQLite fetch_one error: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params} (type: {type(params).__name__ if params else 'None'})")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict]:
        """
        Fetch all rows.
        
        Args:
            query: SQL query string
            params: Query parameters (must be tuple or None)
            
        Returns:
            List of rows as dictionaries
        """
        cursor = self.connection.cursor()
        try:
            # Step 1: Prepare params
            if params is not None:
                if isinstance(params, list):
                    params = tuple(params)
                elif not isinstance(params, tuple):
                    params = (params,)
            
            # Step 2: Execute query
            try:
                if params is not None:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
            except Exception as exec_err:
                logger.error(f"fetch_all execute error: {exec_err}")
                raise
            
            # Step 3: Fetch rows
            try:
                rows = cursor.fetchall()
            except Exception as fetch_err:
                logger.error(f"fetch_all fetchall error: {fetch_err}")
                raise
            
            if not rows:
                return []
            
            # Step 4: Get column names
            try:
                if cursor.description is None:
                    logger.warning("fetch_all: cursor.description is None")
                    return []
                columns = []
                for i, desc in enumerate(cursor.description):
                    col_name = desc[0] if desc else f"col_{i}"
                    columns.append(col_name)
            except Exception as col_err:
                logger.error(f"fetch_all column extraction error: {col_err}")
                raise
            
            # Step 5: Build dicts manually (most compatible way)
            try:
                results = []
                for row in rows:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        if i < len(row):
                            row_dict[col] = row[i]
                    results.append(row_dict)
                return results
            except Exception as dict_err:
                logger.error(f"fetch_all dict building error: {dict_err}")
                logger.error(f"columns: {columns}")
                raise
            
        except Exception as e:
            logger.error(f"SQLite fetch_all error: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params} (type: {type(params).__name__ if params else 'None'})")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def commit(self) -> None:
        """
        Commit current transaction.
        
        Note: SQLite handler auto-commits in execute(), so this is typically
        a no-op. However, it's provided for API consistency and explicit
        transaction control when needed.
        """
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.commit()
            logger.debug("SQLite commit")
    
    def rollback(self) -> None:
        """
        Rollback current transaction.
        
        Note: SQLite handler auto-commits in execute(), so this is typically
        only needed after an error before auto-commit occurs.
        """
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.rollback()
            logger.debug("SQLite rollback")
    
    def init_schema(self) -> None:
        """Initialize SQLite schema using the schema module."""
        from .schema import SQLiteSchema
        
        schema = SQLiteSchema()
        try:
            schema.initialize_database(self.connection)
            logger.info("SQLite schema initialized via schema module")
        except Exception as e:
            logger.error(f"SQLite schema init error: {e}")
            raise
    
    def init_schema_legacy(self) -> None:
        """Initialize SQLite schema (legacy method)."""
        schema = self._get_schema()
        cursor = self.connection.cursor()
        try:
            cursor.executescript(schema)
            self.connection.commit()
            logger.info("SQLite schema initialized (legacy)")
        except Exception as e:
            logger.error(f"SQLite schema init error: {e}")
            self.connection.rollback()
            raise
    
    def _get_schema(self) -> str:
        """Get SQLite schema SQL."""
        return """
        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            fullname TEXT NOT NULL,
            email TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Roles table
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_name TEXT UNIQUE NOT NULL,
            description TEXT,
            permissions TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- User roles mapping
        CREATE TABLE IF NOT EXISTS user_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            role_name TEXT NOT NULL,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Agents table
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            agent_type TEXT,
            config TEXT,
            status TEXT DEFAULT 'draft',
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Agent versions table
        CREATE TABLE IF NOT EXISTS agent_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            version TEXT NOT NULL,
            config TEXT,
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Executions table
        CREATE TABLE IF NOT EXISTS executions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            execution_id TEXT UNIQUE NOT NULL,
            agent_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            input_data TEXT,
            output_data TEXT,
            error_message TEXT,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- HITL requests table
        CREATE TABLE IF NOT EXISTS hitl_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT UNIQUE NOT NULL,
            execution_id TEXT NOT NULL,
            request_type TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            context TEXT,
            response TEXT,
            reviewer_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP
        );
        
        -- MCP Plugins table
        CREATE TABLE IF NOT EXISTS mcp_plugins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plugin_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            server_type TEXT,
            config TEXT,
            status TEXT DEFAULT 'inactive',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- LLM Configurations table
        CREATE TABLE IF NOT EXISTS llm_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_id TEXT UNIQUE NOT NULL,
            provider TEXT NOT NULL,
            model TEXT NOT NULL,
            settings TEXT,
            is_default INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Audit logs table
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            action TEXT NOT NULL,
            resource_type TEXT,
            resource_id TEXT,
            details TEXT,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);
        CREATE INDEX IF NOT EXISTS idx_agents_agent_id ON agents(agent_id);
        CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
        CREATE INDEX IF NOT EXISTS idx_executions_agent_id ON executions(agent_id);
        CREATE INDEX IF NOT EXISTS idx_executions_user_id ON executions(user_id);
        CREATE INDEX IF NOT EXISTS idx_executions_status ON executions(status);
        CREATE INDEX IF NOT EXISTS idx_hitl_requests_status ON hitl_requests(status);
        CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
        CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
        
        -- Insert default roles
        INSERT OR IGNORE INTO roles (role_name, description, permissions) VALUES
            ('super_admin', 'Full system access', '["*"]'),
            ('domain_admin', 'Domain administration', '["users.*", "agents.*", "mcp.*", "executions.*"]'),
            ('agent_developer', 'Agent development', '["agents.create", "agents.read", "agents.update", "agents.test"]'),
            ('agent_publisher', 'Agent publishing', '["agents.read", "agents.publish", "agents.approve"]'),
            ('hitl_reviewer', 'HITL review', '["hitl.*", "executions.read"]'),
            ('agent_user', 'Agent execution', '["agents.read", "agents.execute", "executions.read"]'),
            ('viewer', 'Read-only access', '["agents.read", "executions.read"]');
        """
