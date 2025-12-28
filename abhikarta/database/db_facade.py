"""
Database Facade Module - Unified interface for database operations.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.

Version: 1.2.1
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
    
    Provides access to domain-specific delegates for modular database operations:
    - users: UserDelegate for users, roles, sessions, api_keys
    - llm: LLMDelegate for providers, models, permissions, calls
    - agents: AgentDelegate for agents, versions, templates
    - workflows: WorkflowDelegate for workflows, nodes
    - executions: ExecutionDelegate for executions, steps
    - hitl: HITLDelegate for tasks, comments, assignments
    - mcp: MCPDelegate for plugins, tool_servers
    - audit: AuditDelegate for audit_logs, settings
    - code_fragments: CodeFragmentDelegate for code_fragments
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
        self._init_delegates()
    
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
    
    def _init_delegates(self) -> None:
        """Initialize domain-specific delegates."""
        from .delegates import (
            UserDelegate, LLMDelegate, AgentDelegate, WorkflowDelegate,
            ExecutionDelegate, HITLDelegate, MCPDelegate, AuditDelegate,
            CodeFragmentDelegate
        )
        
        self._users = UserDelegate(self)
        self._llm = LLMDelegate(self)
        self._agents = AgentDelegate(self)
        self._workflows = WorkflowDelegate(self)
        self._executions = ExecutionDelegate(self)
        self._hitl = HITLDelegate(self)
        self._mcp = MCPDelegate(self)
        self._audit = AuditDelegate(self)
        self._code_fragments = CodeFragmentDelegate(self)
        
        logger.info("Database delegates initialized")
    
    # =========================================================================
    # DELEGATE ACCESSORS
    # =========================================================================
    
    @property
    def users(self):
        """Get UserDelegate for user-related operations."""
        return self._users
    
    @property
    def llm(self):
        """Get LLMDelegate for LLM-related operations."""
        return self._llm
    
    @property
    def agents(self):
        """Get AgentDelegate for agent-related operations."""
        return self._agents
    
    @property
    def workflows(self):
        """Get WorkflowDelegate for workflow-related operations."""
        return self._workflows
    
    @property
    def executions(self):
        """Get ExecutionDelegate for execution-related operations."""
        return self._executions
    
    @property
    def hitl(self):
        """Get HITLDelegate for HITL-related operations."""
        return self._hitl
    
    @property
    def mcp(self):
        """Get MCPDelegate for MCP-related operations."""
        return self._mcp
    
    @property
    def audit(self):
        """Get AuditDelegate for audit and settings operations."""
        return self._audit
    
    @property
    def code_fragments(self):
        """Get CodeFragmentDelegate for code fragment operations."""
        return self._code_fragments
    
    # =========================================================================
    # CORE DATABASE OPERATIONS
    # =========================================================================
    
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
