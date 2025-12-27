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
        
        self._local.connection = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        self._local.connection.row_factory = sqlite3.Row
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
            params: Query parameters
            
        Returns:
            Last row ID
        """
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"SQLite execute error: {e}")
            self.connection.rollback()
            raise
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """
        Fetch single row.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Row as dictionary or None
        """
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"SQLite fetch_one error: {e}")
            raise
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict]:
        """
        Fetch all rows.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of rows as dictionaries
        """
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"SQLite fetch_all error: {e}")
            raise
    
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
