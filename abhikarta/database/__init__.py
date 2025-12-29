"""
Database Module - Database abstraction layer with modular delegates.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.

Version: 1.3.0

The database module provides:
- DatabaseFacade: Unified interface for database operations
- DatabaseDelegate: Abstract base class for domain-specific delegates
- Domain Delegates: Modular handlers for each entity domain
  - UserDelegate: Users, Roles, Sessions, API Keys
  - LLMDelegate: Providers, Models, Permissions, Calls
  - AgentDelegate: Agents, Versions, Templates
  - WorkflowDelegate: Workflows, Nodes
  - ExecutionDelegate: Executions, Steps
  - HITLDelegate: Tasks, Comments, Assignments
  - MCPDelegate: Plugins, Tool Servers
  - AuditDelegate: Audit Logs, Settings
  - CodeFragmentDelegate: Code Fragments
"""

from .db_facade import DatabaseFacade, DatabaseHandler
from .database_delegate import DatabaseDelegate
from .schema import SQLiteSchema, PostgresSchema, get_schema
from .delegates import (
    UserDelegate,
    LLMDelegate,
    AgentDelegate,
    WorkflowDelegate,
    ExecutionDelegate,
    HITLDelegate,
    MCPDelegate,
    AuditDelegate,
    CodeFragmentDelegate,
)

__all__ = [
    # Core
    'DatabaseFacade', 
    'DatabaseHandler',
    'DatabaseDelegate',
    # Schema
    'SQLiteSchema',
    'PostgresSchema',
    'get_schema',
    # Delegates
    'UserDelegate',
    'LLMDelegate',
    'AgentDelegate',
    'WorkflowDelegate',
    'ExecutionDelegate',
    'HITLDelegate',
    'MCPDelegate',
    'AuditDelegate',
    'CodeFragmentDelegate',
]

__version__ = '1.3.0'
