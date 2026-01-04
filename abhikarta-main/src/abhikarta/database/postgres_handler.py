"""
PostgreSQL Handler Module - PostgreSQL database implementation.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.
"""

from typing import Any, Dict, List, Optional
import logging

from .db_facade import DatabaseHandler

logger = logging.getLogger(__name__)


class PostgresHandler(DatabaseHandler):
    """PostgreSQL implementation of DatabaseHandler."""
    
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        """
        Initialize PostgreSQL handler.
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        logger.info(f"PostgreSQL handler created for: {host}:{port}/{database}")
    
    def connect(self) -> None:
        """Establish database connection."""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.connection.autocommit = False
            logger.info(f"PostgreSQL connected: {self.host}:{self.port}/{self.database}")
        except ImportError:
            logger.error("psycopg2 not installed. Install with: pip install psycopg2-binary")
            raise
        except Exception as e:
            logger.error(f"PostgreSQL connection error: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.debug("PostgreSQL disconnected")
    
    def execute(self, query: str, params: tuple = None) -> Any:
        """
        Execute a query.
        
        Args:
            query: SQL query string
            params: Query parameters (must be tuple or None)
            
        Returns:
            Last row ID or None
        """
        try:
            # Ensure params is properly formatted
            if params is not None:
                # Convert to tuple if it's a list
                if isinstance(params, list):
                    params = tuple(params)
                # Ensure single values are wrapped in tuple
                elif not isinstance(params, tuple):
                    params = (params,)
            
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                self.connection.commit()
                
                # Try to get returning id
                if cursor.description:
                    try:
                        result = cursor.fetchone()
                        return result[0] if result else None
                    except:
                        return None
                return None
        except Exception as e:
            logger.error(f"PostgreSQL execute error: {e}")
            logger.error(f"Query: {query[:200]}...")
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
        try:
            import psycopg2.extras
            
            # Ensure params is properly formatted
            if params is not None:
                # Convert to tuple if it's a list
                if isinstance(params, list):
                    params = tuple(params)
                # Ensure single values are wrapped in tuple
                elif not isinstance(params, tuple):
                    params = (params,)
            
            with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query, params)
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"PostgreSQL fetch_one error: {e}")
            logger.error(f"Query: {query[:200]}...")
            logger.error(f"Params: {params} (type: {type(params).__name__ if params else 'None'})")
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
        try:
            import psycopg2.extras
            
            # Ensure params is properly formatted
            if params is not None:
                # Convert to tuple if it's a list
                if isinstance(params, list):
                    params = tuple(params)
                # Ensure single values are wrapped in tuple
                elif not isinstance(params, tuple):
                    params = (params,)
            
            with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"PostgreSQL fetch_all error: {e}")
            logger.error(f"Query: {query[:200]}...")
            logger.error(f"Params: {params} (type: {type(params).__name__ if params else 'None'})")
            raise
    
    def commit(self) -> None:
        """
        Commit current transaction.
        
        PostgreSQL requires explicit commits when autocommit is False.
        """
        if self.connection:
            self.connection.commit()
            logger.debug("PostgreSQL commit")
    
    def rollback(self) -> None:
        """
        Rollback current transaction.
        
        PostgreSQL requires explicit rollback to abort failed transactions.
        """
        if self.connection:
            self.connection.rollback()
            logger.debug("PostgreSQL rollback")
    
    def init_schema(self) -> None:
        """Initialize PostgreSQL schema using the schema module."""
        from .schema import PostgresSchema
        
        schema = PostgresSchema()
        try:
            schema.initialize_database(self.connection)
            logger.info("PostgreSQL schema initialized via schema module")
        except Exception as e:
            logger.error(f"PostgreSQL schema init error: {e}")
            raise
    
    def init_schema_legacy(self) -> None:
        """Initialize PostgreSQL schema (legacy method)."""
        schema = self._get_schema()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(schema)
                self.connection.commit()
            logger.info("PostgreSQL schema initialized (legacy)")
        except Exception as e:
            logger.error(f"PostgreSQL schema init error: {e}")
            self.connection.rollback()
            raise
    
    def _get_schema(self) -> str:
        """Get PostgreSQL schema SQL."""
        return """
        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(100) UNIQUE NOT NULL,
            fullname VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Roles table
        CREATE TABLE IF NOT EXISTS roles (
            id SERIAL PRIMARY KEY,
            role_name VARCHAR(100) UNIQUE NOT NULL,
            description TEXT,
            permissions JSONB,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- User roles mapping
        CREATE TABLE IF NOT EXISTS user_roles (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(100) NOT NULL,
            role_name VARCHAR(100) NOT NULL,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Agents table
        CREATE TABLE IF NOT EXISTS agents (
            id SERIAL PRIMARY KEY,
            agent_id VARCHAR(100) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            agent_type VARCHAR(50),
            config JSONB,
            status VARCHAR(50) DEFAULT 'draft',
            created_by VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Agent versions table
        CREATE TABLE IF NOT EXISTS agent_versions (
            id SERIAL PRIMARY KEY,
            agent_id VARCHAR(100) NOT NULL,
            version VARCHAR(50) NOT NULL,
            config JSONB,
            created_by VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Executions table
        CREATE TABLE IF NOT EXISTS executions (
            id SERIAL PRIMARY KEY,
            execution_id VARCHAR(100) UNIQUE NOT NULL,
            agent_id VARCHAR(100) NOT NULL,
            user_id VARCHAR(100) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            input_data JSONB,
            output_data JSONB,
            error_message TEXT,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- HITL requests table
        CREATE TABLE IF NOT EXISTS hitl_requests (
            id SERIAL PRIMARY KEY,
            request_id VARCHAR(100) UNIQUE NOT NULL,
            execution_id VARCHAR(100) NOT NULL,
            request_type VARCHAR(50) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            context JSONB,
            response JSONB,
            reviewer_id VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP
        );
        
        -- MCP Plugins table
        CREATE TABLE IF NOT EXISTS mcp_plugins (
            id SERIAL PRIMARY KEY,
            plugin_id VARCHAR(100) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            server_type VARCHAR(50),
            config JSONB,
            status VARCHAR(50) DEFAULT 'inactive',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- LLM Configurations table
        CREATE TABLE IF NOT EXISTS llm_configs (
            id SERIAL PRIMARY KEY,
            config_id VARCHAR(100) UNIQUE NOT NULL,
            provider VARCHAR(50) NOT NULL,
            model VARCHAR(100) NOT NULL,
            settings JSONB,
            is_default BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Audit logs table
        CREATE TABLE IF NOT EXISTS audit_logs (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(100),
            action VARCHAR(100) NOT NULL,
            resource_type VARCHAR(100),
            resource_id VARCHAR(100),
            details JSONB,
            ip_address VARCHAR(50),
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
        
        -- Insert default roles (use ON CONFLICT for PostgreSQL)
        INSERT INTO roles (role_name, description, permissions) VALUES
            ('super_admin', 'Full system access', '["*"]'),
            ('domain_admin', 'Domain administration', '["users.*", "agents.*", "mcp.*", "executions.*"]'),
            ('agent_developer', 'Agent development', '["agents.create", "agents.read", "agents.update", "agents.test"]'),
            ('agent_publisher', 'Agent publishing', '["agents.read", "agents.publish", "agents.approve"]'),
            ('hitl_reviewer', 'HITL review', '["hitl.*", "executions.read"]'),
            ('agent_user', 'Agent execution', '["agents.read", "agents.execute", "executions.read"]'),
            ('viewer', 'Read-only access', '["agents.read", "executions.read"]')
        ON CONFLICT (role_name) DO NOTHING;
        """
