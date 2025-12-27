# Abhikarta-LLM
## Detailed Design Document

**Version:** 1.1.6  
**Date:** December 2025  
**Classification:** CONFIDENTIAL

---

## Copyright and Legal Notice

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email:** ajsinha@gmail.com

### Legal Notice

This document and the associated software architecture are proprietary and confidential. Unauthorized copying, distribution, modification, or use of this document or the software system it describes is strictly prohibited without explicit written permission from the copyright holder. This document is provided "as is" without warranty of any kind, either expressed or implied. The copyright holder shall not be liable for any damages arising from the use of this document or the software system it describes.

**Patent Pending:** Certain architectural patterns and implementations described in this document may be subject to patent applications.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Architecture](#2-system-architecture)
3. [Module Design](#3-module-design)
4. [Database Design](#4-database-design)
5. [User Management & Authentication](#5-user-management--authentication)
6. [Web Application Design](#6-web-application-design)
7. [LLM Facade Design](#7-llm-facade-design)
8. [LangChain & LangGraph Integration](#8-langchain--langgraph-integration)
9. [Tools System Design](#9-tools-system-design-new-in-v116)
10. [MCP Plugin Framework Design](#10-mcp-plugin-framework-design)
11. [UI/UX Design](#11-uiux-design)
12. [Configuration Management](#12-configuration-management)
13. [Security Design](#13-security-design)
14. [API Specifications](#14-api-specifications)
15. [Deployment Architecture](#15-deployment-architecture)

---

## 1. Introduction

### 1.1 Purpose

This document provides the detailed technical design for Abhikarta-LLM, an AI Agent Design & Orchestration Platform. It covers architecture, module design, database schema, API specifications, and implementation guidelines.

### 1.2 Scope

- Modular Python application structure
- Dual database support (SQLite/PostgreSQL)
- User management via JSON file with facade pattern
- Flask-based web application
- BMO-inspired UI theme
- LLM and MCP abstraction layers

### 1.3 Design Principles

1. **Modularity:** Loosely coupled modules with clear interfaces
2. **Facade Pattern:** Unified interfaces for complex subsystems
3. **Configuration-Driven:** Behavior controlled via config files
4. **Database Agnostic:** Switch between SQLite and PostgreSQL
5. **Security First:** RBAC, audit logging, secure defaults

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Web Browser                              │
│                    (jQuery + Bootstrap 5)                        │
└─────────────────────────────────┬───────────────────────────────┘
                                  │ HTTP/WebSocket
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Flask Application                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Web Module (abhikarta.web)            │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │              Routes Module                       │    │   │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────┐ │    │   │
│  │  │  │  Auth   │ │  Admin  │ │  User   │ │  MCP  │ │    │   │
│  │  │  │ Routes  │ │ Routes  │ │ Routes  │ │Routes │ │    │   │
│  │  │  └─────────┘ └─────────┘ └─────────┘ └───────┘ │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │              Templates (Jinja2)                  │    │   │
│  │  │         base.html + page templates               │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  User Facade    │    │   LLM Facade    │    │   MCP Facade    │
│  (users.json)   │    │  (4 providers)  │    │  (Plugin Mgr)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        │                        │
┌─────────────────┐               │                        │
│  Database       │               │                        │
│  Facade         │               ▼                        ▼
│ (SQLite/PG)     │    ┌─────────────────────────────────────┐
└─────────────────┘    │      External Services              │
                       │  OpenAI | Anthropic | Ollama | AWS  │
                       │         MCP Servers                  │
                       └─────────────────────────────────────┘
```

### 2.2 Module Dependency Graph

```
abhikarta (root)
├── config (no dependencies)
├── utils (depends on: config)
├── database (depends on: config, utils)
├── user_management (depends on: config, utils)
├── rbac (depends on: user_management)
├── llm_provider (depends on: config, utils)
├── mcp (depends on: config, utils)
├── agent (depends on: llm_provider, mcp, database)
├── hitl (depends on: database, user_management)
└── web (depends on: all above)
```

---

## 3. Module Design

### 3.1 Config Module (`abhikarta/config/`)

#### 3.1.1 settings.py

```python
"""
Application settings management.
Loads configuration from config.yaml and environment variables.
"""

class Settings:
    """Central settings manager."""
    
    # Application
    APP_NAME: str = "Abhikarta-LLM"
    APP_VERSION: str = "1.1.6"
    DEBUG: bool = False
    SECRET_KEY: str
    
    # Database
    DB_TYPE: str  # "sqlite" or "postgresql"
    SQLITE_PATH: str
    PG_HOST: str
    PG_PORT: int
    PG_DATABASE: str
    PG_USER: str
    PG_PASSWORD: str
    
    # LLM Providers
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str
    OLLAMA_BASE_URL: str
    AWS_REGION: str
    
    # Paths
    DATA_DIR: str
    USERS_FILE: str
    
    @classmethod
    def load(cls, config_path: str = "config.yaml") -> "Settings":
        """Load settings from file and environment."""
        pass
```

### 3.2 Database Module (`abhikarta/database/`)

#### 3.2.1 db_facade.py - Database Facade

```python
"""
Database Facade - Provides unified interface for SQLite and PostgreSQL.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

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
        """Execute a query."""
        pass
    
    @abstractmethod
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """Fetch single row."""
        pass
    
    @abstractmethod
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict]:
        """Fetch all rows."""
        pass
    
    @abstractmethod
    def init_schema(self) -> None:
        """Initialize database schema."""
        pass


class DatabaseFacade:
    """
    Facade for database operations.
    Automatically selects SQLite or PostgreSQL based on config.
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._handler: DatabaseHandler = None
        self._init_handler()
    
    def _init_handler(self) -> None:
        """Initialize appropriate database handler."""
        if self.settings.DB_TYPE == "sqlite":
            from .sqlite_handler import SQLiteHandler
            self._handler = SQLiteHandler(self.settings.SQLITE_PATH)
        elif self.settings.DB_TYPE == "postgresql":
            from .postgres_handler import PostgresHandler
            self._handler = PostgresHandler(
                host=self.settings.PG_HOST,
                port=self.settings.PG_PORT,
                database=self.settings.PG_DATABASE,
                user=self.settings.PG_USER,
                password=self.settings.PG_PASSWORD
            )
        else:
            raise ValueError(f"Unsupported database type: {self.settings.DB_TYPE}")
    
    def connect(self) -> None:
        self._handler.connect()
    
    def disconnect(self) -> None:
        self._handler.disconnect()
    
    def execute(self, query: str, params: tuple = None) -> Any:
        return self._handler.execute(query, params)
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        return self._handler.fetch_one(query, params)
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict]:
        return self._handler.fetch_all(query, params)
    
    def init_schema(self) -> None:
        self._handler.init_schema()
```

#### 3.2.2 sqlite_handler.py

```python
"""SQLite database handler implementation."""

import sqlite3
from typing import Any, Dict, List, Optional
from .db_facade import DatabaseHandler

class SQLiteHandler(DatabaseHandler):
    """SQLite implementation of DatabaseHandler."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
    
    def connect(self) -> None:
        self.connection = sqlite3.connect(
            self.db_path,
            check_same_thread=False
        )
        self.connection.row_factory = sqlite3.Row
    
    def disconnect(self) -> None:
        if self.connection:
            self.connection.close()
    
    def execute(self, query: str, params: tuple = None) -> Any:
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self.connection.commit()
        return cursor.lastrowid
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict]:
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def init_schema(self) -> None:
        """Initialize SQLite schema."""
        schema = self._get_schema()
        cursor = self.connection.cursor()
        cursor.executescript(schema)
        self.connection.commit()
    
    def _get_schema(self) -> str:
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
        
        -- Executions table
        CREATE TABLE IF NOT EXISTS executions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            execution_id TEXT UNIQUE NOT NULL,
            agent_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            input_data TEXT,
            output_data TEXT,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        CREATE INDEX IF NOT EXISTS idx_executions_agent_id ON executions(agent_id);
        CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
        """
```

#### 3.2.3 postgres_handler.py

```python
"""PostgreSQL database handler implementation."""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Any, Dict, List, Optional
from .db_facade import DatabaseHandler

class PostgresHandler(DatabaseHandler):
    """PostgreSQL implementation of DatabaseHandler."""
    
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
    
    def connect(self) -> None:
        self.connection = psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password
        )
    
    def disconnect(self) -> None:
        if self.connection:
            self.connection.close()
    
    def execute(self, query: str, params: tuple = None) -> Any:
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            self.connection.commit()
            try:
                return cursor.fetchone()[0] if cursor.description else None
            except:
                return None
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def init_schema(self) -> None:
        """Initialize PostgreSQL schema."""
        schema = self._get_schema()
        with self.connection.cursor() as cursor:
            cursor.execute(schema)
            self.connection.commit()
    
    def _get_schema(self) -> str:
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
        
        -- Executions table
        CREATE TABLE IF NOT EXISTS executions (
            id SERIAL PRIMARY KEY,
            execution_id VARCHAR(100) UNIQUE NOT NULL,
            agent_id VARCHAR(100) NOT NULL,
            user_id VARCHAR(100) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            input_data JSONB,
            output_data JSONB,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        CREATE INDEX IF NOT EXISTS idx_executions_agent_id ON executions(agent_id);
        CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
        """
```

### 3.3 User Management Module (`abhikarta/user_management/`)

#### 3.3.1 user_facade.py - User Management Facade

```python
"""
User Management Facade - Handles user operations via users.json file.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class UserFacade:
    """
    Facade for user management operations.
    Manages users through a JSON file (users.json).
    """
    
    def __init__(self, users_file: str):
        self.users_file = Path(users_file)
        self._users: Dict = {}
        self._load_users()
    
    def _load_users(self) -> None:
        """Load users from JSON file."""
        if self.users_file.exists():
            with open(self.users_file, 'r') as f:
                data = json.load(f)
                self._users = {u['user_id']: u for u in data.get('users', [])}
            logger.info(f"Loaded {len(self._users)} users from {self.users_file}")
        else:
            self._users = {}
            logger.warning(f"Users file not found: {self.users_file}")
    
    def _save_users(self) -> None:
        """Save users to JSON file."""
        data = {'users': list(self._users.values())}
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.users_file, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(self._users)} users to {self.users_file}")
    
    def authenticate(self, user_id: str, password: str) -> Optional[Dict]:
        """
        Authenticate user with plain text password comparison.
        
        Args:
            user_id: User identifier
            password: Plain text password
            
        Returns:
            User dict if authenticated, None otherwise
        """
        user = self._users.get(user_id)
        if user and user.get('password') == password and user.get('is_active', True):
            logger.info(f"User authenticated: {user_id}")
            return {k: v for k, v in user.items() if k != 'password'}
        logger.warning(f"Authentication failed for user: {user_id}")
        return None
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID (excluding password)."""
        user = self._users.get(user_id)
        if user:
            return {k: v for k, v in user.items() if k != 'password'}
        return None
    
    def list_users(self) -> List[Dict]:
        """List all users (excluding passwords)."""
        return [
            {k: v for k, v in u.items() if k != 'password'}
            for u in self._users.values()
        ]
    
    def create_user(self, user_data: Dict) -> bool:
        """Create a new user."""
        user_id = user_data.get('user_id')
        if user_id in self._users:
            logger.warning(f"User already exists: {user_id}")
            return False
        self._users[user_id] = user_data
        self._save_users()
        logger.info(f"User created: {user_id}")
        return True
    
    def update_user(self, user_id: str, user_data: Dict) -> bool:
        """Update an existing user."""
        if user_id not in self._users:
            logger.warning(f"User not found: {user_id}")
            return False
        self._users[user_id].update(user_data)
        self._save_users()
        logger.info(f"User updated: {user_id}")
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user (soft delete by setting is_active=False)."""
        if user_id not in self._users:
            return False
        self._users[user_id]['is_active'] = False
        self._save_users()
        logger.info(f"User deactivated: {user_id}")
        return True
    
    def get_user_roles(self, user_id: str) -> List[str]:
        """Get roles for a user."""
        user = self._users.get(user_id)
        return user.get('roles', []) if user else []
    
    def has_role(self, user_id: str, role: str) -> bool:
        """Check if user has a specific role."""
        roles = self.get_user_roles(user_id)
        return role in roles
    
    def is_admin(self, user_id: str) -> bool:
        """Check if user is an admin (super_admin or domain_admin)."""
        roles = self.get_user_roles(user_id)
        return 'super_admin' in roles or 'domain_admin' in roles
    
    def reload(self) -> None:
        """Reload users from file."""
        self._load_users()
```

### 3.4 Web Module (`abhikarta/web/`)

#### 3.4.1 Route Architecture

```
abhikarta/web/routes/
├── __init__.py
├── abstract_routes.py    # Base class and decorators
├── auth_routes.py        # Login, logout, session management
├── admin_routes.py       # Admin dashboard, system management
├── user_routes.py        # User dashboard, agent execution
├── agent_routes.py       # Agent management (CRUD)
├── mcp_routes.py         # MCP plugin management
└── api_routes.py         # REST API endpoints
```

#### 3.4.2 abstract_routes.py - Base Class

```python
"""
Abstract Routes Module - Base class for all route handlers.
"""

from abc import ABC, abstractmethod
from functools import wraps
from flask import session, redirect, url_for, flash
import logging

logger = logging.getLogger(__name__)

class AbstractRoutes(ABC):
    """Base class for route handlers."""
    
    def __init__(self, app):
        self.app = app
        self.user_facade = None
        self.db_facade = None
        self.llm_facade = None
        self.mcp_facade = None
    
    def set_user_facade(self, user_facade):
        self.user_facade = user_facade
    
    def set_db_facade(self, db_facade):
        self.db_facade = db_facade
    
    def set_llm_facade(self, llm_facade):
        self.llm_facade = llm_facade
    
    def set_mcp_facade(self, mcp_facade):
        self.mcp_facade = mcp_facade
    
    @abstractmethod
    def register_routes(self):
        """Register routes with Flask app."""
        pass


def login_required(f):
    """Decorator to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('auth.login'))
        if not session.get('is_admin', False):
            flash('Admin access required', 'error')
            return redirect(url_for('user.dashboard'))
        return f(*args, **kwargs)
    return decorated_function
```

---

## 4. Database Design

### 4.1 Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐
│   users     │       │   roles     │
├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │
│ user_id     │◄──────│ role_name   │
│ fullname    │       │ description │
│ email       │       │ permissions │
│ is_active   │       │ is_active   │
│ created_at  │       │ created_at  │
│ updated_at  │       └─────────────┘
└─────────────┘              │
      │                      │
      │    ┌─────────────────┘
      │    │
      ▼    ▼
┌─────────────┐
│ user_roles  │
├─────────────┤
│ id (PK)     │
│ user_id     │
│ role_name   │
│ assigned_at │
└─────────────┘

┌─────────────┐       ┌─────────────┐
│   agents    │       │ executions  │
├─────────────┤       ├─────────────┤
│ id (PK)     │◄──────│ id (PK)     │
│ agent_id    │       │ execution_id│
│ name        │       │ agent_id    │
│ description │       │ user_id     │
│ agent_type  │       │ status      │
│ config      │       │ input_data  │
│ status      │       │ output_data │
│ created_by  │       │ started_at  │
│ created_at  │       │ completed_at│
│ updated_at  │       │ created_at  │
└─────────────┘       └─────────────┘

┌─────────────┐       ┌─────────────┐
│ mcp_plugins │       │ audit_logs  │
├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │
│ plugin_id   │       │ user_id     │
│ name        │       │ action      │
│ description │       │ resource_typ│
│ server_type │       │ resource_id │
│ config      │       │ details     │
│ status      │       │ ip_address  │
│ created_at  │       │ created_at  │
│ updated_at  │       └─────────────┘
└─────────────┘
```

### 4.2 Table Specifications

#### 4.2.1 users

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER/SERIAL | PRIMARY KEY | Auto-increment ID |
| user_id | VARCHAR(100) | UNIQUE NOT NULL | Login identifier |
| fullname | VARCHAR(255) | NOT NULL | Display name |
| email | VARCHAR(255) | | Email address |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| created_at | TIMESTAMP | DEFAULT NOW | Creation time |
| updated_at | TIMESTAMP | DEFAULT NOW | Last update time |

#### 4.2.2 roles

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER/SERIAL | PRIMARY KEY | Auto-increment ID |
| role_name | VARCHAR(100) | UNIQUE NOT NULL | Role identifier |
| description | TEXT | | Role description |
| permissions | TEXT/JSONB | | Permission list |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| created_at | TIMESTAMP | DEFAULT NOW | Creation time |

#### 4.2.3 agents

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER/SERIAL | PRIMARY KEY | Auto-increment ID |
| agent_id | VARCHAR(100) | UNIQUE NOT NULL | Agent identifier |
| name | VARCHAR(255) | NOT NULL | Agent name |
| description | TEXT | | Agent description |
| agent_type | VARCHAR(50) | | Type (ReAct, RAG, etc.) |
| config | TEXT/JSONB | | Agent configuration |
| status | VARCHAR(50) | DEFAULT 'draft' | Lifecycle status |
| created_by | VARCHAR(100) | | Creator user_id |
| created_at | TIMESTAMP | DEFAULT NOW | Creation time |
| updated_at | TIMESTAMP | DEFAULT NOW | Last update time |

---

## 5. User Management & Authentication

### 5.1 users.json Structure

```json
{
  "users": [
    {
      "user_id": "admin",
      "password": "admin123",
      "fullname": "System Administrator",
      "email": "admin@abhikarta.local",
      "roles": ["super_admin"],
      "is_active": true
    },
    {
      "user_id": "developer",
      "password": "dev123",
      "fullname": "Agent Developer",
      "email": "developer@abhikarta.local",
      "roles": ["agent_developer"],
      "is_active": true
    },
    {
      "user_id": "user",
      "password": "user123",
      "fullname": "Business User",
      "email": "user@abhikarta.local",
      "roles": ["agent_user"],
      "is_active": true
    }
  ]
}
```

### 5.2 Authentication Flow

```
┌────────────┐     ┌────────────┐     ┌────────────┐
│   Browser  │────▶│  Flask     │────▶│ UserFacade │
│            │     │  Route     │     │            │
└────────────┘     └────────────┘     └────────────┘
      │                  │                   │
      │  POST /login     │                   │
      │  user_id, pwd    │                   │
      │─────────────────▶│                   │
      │                  │  authenticate()   │
      │                  │──────────────────▶│
      │                  │                   │
      │                  │◀──────────────────│
      │                  │  user_data/None   │
      │                  │                   │
      │                  │  Set session      │
      │◀─────────────────│                   │
      │  Redirect        │                   │
```

### 5.3 Session Management

```python
# Session data structure
session = {
    'user_id': 'admin',
    'fullname': 'System Administrator',
    'email': 'admin@abhikarta.local',
    'roles': ['super_admin'],
    'is_admin': True,
    'logged_in_at': '2025-12-26T10:00:00'
}
```

---

## 6. Web Application Design

### 6.1 Flask Application Structure

```python
# abhikarta/web/app.py

from flask import Flask
from .routes import (
    AuthRoutes, AdminRoutes, UserRoutes, 
    AgentRoutes, MCPRoutes, APIRoutes
)

def create_app(settings):
    """Application factory."""
    app = Flask(__name__,
        template_folder='templates',
        static_folder='static'
    )
    
    app.secret_key = settings.SECRET_KEY
    app.config['DEBUG'] = settings.DEBUG
    
    # Initialize facades
    user_facade = UserFacade(settings.USERS_FILE)
    db_facade = DatabaseFacade(settings)
    
    # Register routes
    routes = [
        AuthRoutes(app),
        AdminRoutes(app),
        UserRoutes(app),
        AgentRoutes(app),
        MCPRoutes(app),
        APIRoutes(app)
    ]
    
    for route in routes:
        route.set_user_facade(user_facade)
        route.set_db_facade(db_facade)
        route.register_routes()
    
    return app
```

### 6.2 Template Hierarchy

```
templates/
├── base.html              # Base layout with BMO theme
├── components/
│   ├── navbar.html        # Navigation bar
│   ├── sidebar.html       # Admin sidebar
│   ├── footer.html        # Footer
│   └── flash_messages.html
├── auth/
│   ├── login.html
│   └── logout.html
├── admin/
│   ├── dashboard.html
│   ├── users.html
│   ├── settings.html
│   └── monitoring.html
├── user/
│   ├── dashboard.html
│   └── history.html
├── agents/
│   ├── list.html
│   ├── detail.html
│   ├── designer.html
│   └── execute.html
└── mcp/
    ├── plugins.html
    ├── plugin_detail.html
    └── tool_detail.html
```

---

## 7. LLM Facade Design

### 7.1 Class Diagram

```
┌───────────────────────────────────┐
│           LLMFacade               │
├───────────────────────────────────┤
│ - providers: Dict[str, Provider]  │
│ - default_provider: str           │
├───────────────────────────────────┤
│ + chat_completion()               │
│ + embed()                         │
│ + function_call()                 │
│ + get_capabilities()              │
│ + health_check()                  │
└───────────────────────────────────┘
            ▲
            │ uses
            │
┌───────────────────────────────────┐
│     LLMProvider (Abstract)        │
├───────────────────────────────────┤
│ + chat_completion()               │
│ + embed()                         │
│ + function_call()                 │
│ + get_capabilities()              │
│ + health_check()                  │
└───────────────────────────────────┘
     ▲      ▲      ▲      ▲
     │      │      │      │
┌────┴──┐┌──┴───┐┌─┴────┐┌┴──────┐
│OpenAI ││Claude││Ollama││Bedrock│
│Provider│Provider│Provider│Provider│
└───────┘└──────┘└──────┘└───────┘
```

### 7.2 Provider Configuration

```yaml
# config.yaml
llm_providers:
  openai:
    enabled: true
    api_key: "${OPENAI_API_KEY}"
    default_model: "gpt-4o"
    fallback_model: "gpt-3.5-turbo"
  
  anthropic:
    enabled: true
    api_key: "${ANTHROPIC_API_KEY}"
    default_model: "claude-3-5-sonnet-20241022"
  
  ollama:
    enabled: true
    base_url: "http://localhost:11434"
    default_model: "llama3"
  
  bedrock:
    enabled: false
    region: "us-east-1"
    default_model: "anthropic.claude-3-sonnet-20240229-v1:0"

default_provider: "openai"

fallback_chain:
  - "openai"
  - "anthropic"
  - "ollama"
```

### 7.3 LLM Call Logging

All LLM calls are automatically logged to the `llm_calls` database table for audit, debugging, and cost tracking.

```
┌─────────────────────────────────────────────────────────────────┐
│                      LLM CALL LOGGING                           │
├─────────────────────────────────────────────────────────────────┤
│  LLMFacade.complete()                                           │
│      │                                                          │
│      ├──► Call Provider API                                     │
│      │                                                          │
│      ├──► Log to llm_calls table:                              │
│      │    • call_id (UUID)                                      │
│      │    • execution_id (link to execution)                    │
│      │    • agent_id (link to agent)                            │
│      │    • provider, model                                     │
│      │    • system_prompt, user_prompt, messages                │
│      │    • response_content, tool_calls                        │
│      │    • input_tokens, output_tokens, total_tokens          │
│      │    • cost_estimate (auto-calculated)                     │
│      │    • latency_ms                                          │
│      │    • status (success/failed), error_message              │
│      │                                                          │
│      └──► Return LLMResponse                                    │
└─────────────────────────────────────────────────────────────────┘
```

**Cost Calculation:**
```python
COSTS_PER_MILLION = {
    'openai': {'gpt-4o': {'input': 2.50, 'output': 10.00}},
    'anthropic': {'claude-3-5-sonnet': {'input': 3.00, 'output': 15.00}},
    'ollama': {}  # Free for local models
}
```

---

## 7A. Workflow DAG Execution System

### 7A.1 Overview

The Workflow DAG system enables users to define and execute complex multi-step pipelines as Directed Acyclic Graphs with embedded Python modules.

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKFLOW DAG SYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │  JSON DAG   │───►│ DAG Parser  │───►│  DAGWorkflow │        │
│  │ Definition  │    │             │    │    Object    │        │
│  └─────────────┘    └─────────────┘    └──────┬──────┘        │
│                                               │                 │
│                                               ▼                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │  Execution  │◄───│  Workflow   │◄───│ Node Factory │        │
│  │   Results   │    │  Executor   │    │             │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7A.2 Supported Node Types

| Node Type | Description | Key Configuration |
|-----------|-------------|-------------------|
| `input` | Workflow entry point | schema, defaults |
| `output` | Final output formatting | format, schema |
| `python` | Execute Python code | code, imports |
| `llm` | Call language model | provider, model, prompt |
| `http` | Make HTTP request | url, method, headers |
| `condition` | Conditional branching | expression, branches |
| `transform` | Data transformation | operation, mapping |
| `delay` | Add delay | seconds |
| `hitl` | Human approval | task_type, timeout |
| `parallel` | Parallel execution | branches |
| `loop` | Iterate over items | items, max_iterations |
| `tool` | Execute MCP tool | plugin_id, tool_name |

### 7A.3 DAG Parser

```python
@dataclass
class DAGNode:
    node_id: str
    name: str
    node_type: str
    config: Dict
    python_code: Optional[str]
    dependencies: List[str]
    position: Tuple[int, int]

@dataclass
class DAGWorkflow:
    workflow_id: str
    name: str
    nodes: Dict[str, DAGNode]
    edges: List[Tuple[str, str]]
    entry_point: str
    python_modules: Dict[str, str]
    
    def get_execution_order(self) -> List[str]:
        """Topological sort for node execution."""
        
    def validate(self) -> List[str]:
        """Validate DAG structure, detect cycles."""
```

### 7A.4 Workflow Executor

```python
class WorkflowExecutor:
    def execute_workflow(self, workflow: DAGWorkflow, 
                        input_data: Dict) -> WorkflowExecution:
        """
        Execute workflow with:
        1. Load Python modules into namespace
        2. Get execution order (topological sort)
        3. Execute each node in order
        4. Track step results
        5. Log all LLM calls
        6. Save execution to database
        """
```

### 7A.5 Python Module System

Users can define reusable Python modules in the workflow JSON:

```json
{
  "python_modules": {
    "utils": "def clean(text):\n    return text.strip()",
    "validators": "def is_valid(data):\n    return 'name' in data"
  }
}
```

These are loaded into a namespace and can be imported by Python nodes:

```python
# In Python node code:
from utils import clean
from validators import is_valid

result = clean(input_data['text'])
if is_valid(input_data):
    output = {'cleaned': result}
```

### 7A.6 Database Schema

**workflows table:**
- workflow_id, name, description, version
- dag_definition (JSON)
- python_modules (JSON)
- status, created_by, execution_count

**workflow_nodes table:**
- node_id, workflow_id, name, node_type
- config (JSON), python_code
- dependencies (JSON array)

**execution_steps table:**
- execution_id, step_number, node_id, node_type
- status, input_data, output_data
- started_at, completed_at, duration_ms

---

## 8. LangChain & LangGraph Integration

Abhikarta-LLM uses **LangChain** for LLM abstraction and agent execution, and **LangGraph** for workflow orchestration. This provides a robust, industry-standard foundation for AI agent development.

### 8.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Abhikarta-LLM Application                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    LangChain Layer                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │   │
│  │  │ LLM Factory │  │    Tools    │  │   Agent Executor    │   │   │
│  │  │             │  │   Factory   │  │   (ReAct, Tool-     │   │   │
│  │  │ - OpenAI    │  │             │  │    calling, etc)    │   │   │
│  │  │ - Anthropic │  │ - MCP Tools │  │                     │   │   │
│  │  │ - Google    │  │ - Code Frags│  │                     │   │   │
│  │  │ - Ollama    │  │ - Built-ins │  │                     │   │   │
│  │  │ - etc.      │  │             │  │                     │   │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    LangGraph Layer                            │   │
│  │  ┌─────────────────────────────────────────────────────────┐ │   │
│  │  │              Workflow Graph Executor                     │ │   │
│  │  │                                                          │ │   │
│  │  │  ┌─────────┐    ┌─────────┐    ┌─────────┐             │ │   │
│  │  │  │  Node   │───▶│  Node   │───▶│  Node   │             │ │   │
│  │  │  │ (LLM)   │    │ (Tool)  │    │ (Code)  │             │ │   │
│  │  │  └─────────┘    └─────────┘    └─────────┘             │ │   │
│  │  │       │              │                                  │ │   │
│  │  │       ▼              ▼                                  │ │   │
│  │  │  ┌─────────────────────────────────────────────────┐   │ │   │
│  │  │  │              State Management                    │   │ │   │
│  │  │  │  - Input/Output tracking                        │   │ │   │
│  │  │  │  - Node outputs                                 │   │ │   │
│  │  │  │  - Conditional branching                        │   │ │   │
│  │  │  │  - HITL checkpoints                            │   │ │   │
│  │  │  └─────────────────────────────────────────────────┘   │ │   │
│  │  └─────────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 8.2 LangChain LLM Factory

The LLM Factory creates LangChain LLM instances from database configurations:

```python
from abhikarta.langchain import LLMFactory, get_langchain_llm

# Create LLM from database configuration
llm = get_langchain_llm(db_facade, model_id='gpt-4o')

# Or create directly with factory
llm = LLMFactory.create_llm(provider_config, model_config)

# Supported providers:
# - OpenAI (ChatOpenAI)
# - Anthropic (ChatAnthropic)
# - Google (ChatGoogleGenerativeAI)
# - Azure OpenAI (AzureChatOpenAI)
# - AWS Bedrock (ChatBedrock)
# - Ollama (ChatOllama)
# - Mistral (ChatMistralAI)
# - Cohere (ChatCohere)
# - Together AI (ChatTogether)
# - Groq (ChatGroq)
# - HuggingFace (ChatHuggingFace)
```

### 8.3 LangChain Tools Integration

Tools from MCP servers are automatically converted to LangChain tools:

```python
from abhikarta.langchain import ToolFactory, MCPToolAdapter

# Get all tools from active MCP servers
factory = ToolFactory(db_facade)
tools = factory.get_mcp_tools()

# Get tools from specific server
tools = factory.get_mcp_tools(server_id='my-server')

# Get code fragment as tool
tool = factory.get_code_fragment_tool('fragment-id')

# Get built-in tools
tools = factory.get_builtin_tools(['wikipedia', 'web_search'])

# Create custom tool
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(description="Search query")

tool = factory.create_custom_tool(
    name="search",
    description="Search the web",
    func=my_search_function,
    args_schema=SearchInput
)
```

### 8.4 LangChain Agent Execution

Agents are executed using LangChain's agent framework:

```python
from abhikarta.langchain import AgentExecutor, create_react_agent, create_tool_calling_agent

# Create agent with tools
llm = get_langchain_llm(db_facade, model_id='claude-3-5-sonnet')
tools = factory.get_all_tools()

# ReAct agent (reasoning + acting)
agent = create_react_agent(llm, tools, system_prompt="You are a helpful assistant")

# Tool-calling agent (native function calling)
agent = create_tool_calling_agent(llm, tools, system_prompt="You are a helpful assistant")

# Execute agent
result = agent.invoke({"input": "What is the weather in NYC?"})
print(result["output"])

# Or use the high-level executor with database integration
executor = AgentExecutor(db_facade)
result = executor.execute_agent(agent_id='my-agent', input_data="Hello")
print(result.output)
print(result.tool_calls)
print(result.intermediate_steps)
```

**Agent Types:**
| Type | Description | Best For |
|------|-------------|----------|
| `react` | Reasoning + Acting | General purpose, any LLM |
| `tool_calling` | Native function calling | OpenAI, Anthropic, Gemini |
| `structured_chat` | Structured output format | Multi-turn conversations |

### 8.5 LangGraph Workflow Execution

Workflows are executed using LangGraph's StateGraph:

```python
from abhikarta.langchain import WorkflowGraphExecutor, create_workflow_graph

# Execute workflow from database
executor = WorkflowGraphExecutor(db_facade)
result = executor.execute_workflow(
    workflow_id='my-workflow',
    input_data={'query': 'Analyze this data'},
    variables={'user_name': 'John'}
)

print(result.status)        # 'completed', 'failed', 'waiting_for_human'
print(result.output)        # Final output
print(result.node_outputs)  # Output from each node
print(result.executed_nodes) # List of executed node IDs

# Create custom workflow graph
workflow_config = {
    'nodes': [
        {'id': 'start', 'type': 'start'},
        {'id': 'llm1', 'type': 'llm', 'config': {'model_id': 'gpt-4o'}},
        {'id': 'tool1', 'type': 'tool', 'config': {'tool_name': 'search'}},
        {'id': 'end', 'type': 'end'}
    ],
    'edges': [
        {'source': 'start', 'target': 'llm1'},
        {'source': 'llm1', 'target': 'tool1'},
        {'source': 'tool1', 'target': 'end'}
    ]
}

graph = create_workflow_graph(workflow_config, db_facade)
result = graph.invoke({'input': 'Hello'})
```

### 8.6 Workflow State Management

LangGraph workflows use a typed state dictionary:

```python
class WorkflowState(TypedDict, total=False):
    # Input/Output
    input: Any
    output: Any
    
    # Execution tracking
    current_node: str
    executed_nodes: List[str]
    node_outputs: Dict[str, Any]
    
    # Error handling
    error: Optional[str]
    status: str  # running, completed, failed, waiting_for_human
    
    # Context
    context: Dict[str, Any]
    variables: Dict[str, Any]
    
    # Human-in-the-loop
    hitl_pending: bool
    hitl_message: Optional[str]
    hitl_response: Optional[str]
    
    # Metadata
    execution_id: str
    workflow_id: str
    started_at: str
    messages: List[Dict]
```

### 8.7 Node Types

LangGraph workflow nodes support various types:

| Node Type | Description | Configuration |
|-----------|-------------|---------------|
| `start` | Entry point | - |
| `end` | Exit point | - |
| `llm` | LLM call | `model_id`, `system_prompt`, `prompt_template` |
| `agent` | Agent execution | `agent_id` |
| `tool` | Tool execution | `tool_name`, `server_id` |
| `code` | Python code | `code` (Python code string) |
| `condition` | Conditional branch | `condition` (Python expression) |
| `hitl` | Human-in-the-loop | `message` |
| `rag` | RAG retrieval | `collection_id`, `k` |

### 8.8 Conditional Branching

LangGraph supports conditional edges:

```python
workflow_config = {
    'nodes': [
        {'id': 'check', 'type': 'condition', 'config': {'condition': 'len(input) > 100'}},
        {'id': 'short_path', 'type': 'llm', 'config': {...}},
        {'id': 'long_path', 'type': 'llm', 'config': {...}},
    ],
    'edges': [
        {'source': 'check', 'target': 'short_path', 'condition': 'not node_outputs["check"]'},
        {'source': 'check', 'target': 'long_path', 'condition': 'node_outputs["check"]'},
    ]
}
```

### 8.9 Module Structure

```
abhikarta/langchain/
├── __init__.py           # Module exports
├── llm_factory.py        # LangChain LLM creation
├── tools.py              # Tool creation and MCP integration
├── agents.py             # Agent execution
└── workflow_graph.py     # LangGraph workflow execution
```

### 8.10 Dependencies

Required packages for LangChain/LangGraph:

```
# Core
langchain>=0.3.0
langgraph>=0.2.0
langchain-core>=0.3.0
langchain-community>=0.3.0

# Providers (install as needed)
langchain-openai>=0.2.0
langchain-anthropic>=0.2.0
langchain-google-genai>=2.0.0
langchain-ollama>=0.2.0
langchain-mistralai>=0.2.0
langchain-cohere>=0.3.0
langchain-groq>=0.2.0
langchain-aws>=0.2.0
langchain-huggingface>=0.1.0
```

---

## 9. Tools System Design (New in v1.1.6)

### 9.1 Overview

The Tools System provides a unified, centralized approach to tool management in Abhikarta-LLM. All tools extend the abstract `BaseTool` class, enabling consistent interfaces for agents, workflows, and LLM integrations.

### 9.2 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ToolsRegistry                            │
│   (Singleton - Centralized Tool Management)                 │
├─────────────────────────────────────────────────────────────┤
│   register() / unregister() / get() / execute()            │
│   list_tools() / search() / to_openai_functions()          │
├─────────────────────────────────────────────────────────────┤
│                     BaseTool (Abstract)                      │
│   - tool_id, name, description, category                    │
│   - execute() / get_schema() / validate_input()            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ Function │ │   MCP    │ │   HTTP   │ │  Code    │      │
│  │   Tool   │ │   Tool   │ │   Tool   │ │ Fragment │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│  ┌──────────┐ ┌──────────┐                                  │
│  │LangChain │ │  Async   │                                  │
│  │   Tool   │ │   Tool   │                                  │
│  └──────────┘ └──────────┘                                  │
└─────────────────────────────────────────────────────────────┘
```

### 9.3 BaseTool Abstract Class

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum

class ToolType(Enum):
    FUNCTION = "function"
    MCP = "mcp"
    CODE_FRAGMENT = "code_fragment"
    HTTP = "http"
    LANGCHAIN = "langchain"
    PLUGIN = "plugin"
    CUSTOM = "custom"

class ToolCategory(Enum):
    UTILITY = "utility"
    DATA = "data"
    AI = "ai"
    INTEGRATION = "integration"
    FILE = "file"
    COMMUNICATION = "communication"
    SEARCH = "search"
    DATABASE = "database"
    CUSTOM = "custom"

@dataclass
class ToolResult:
    success: bool
    output: Any = None
    error: str = None
    execution_time_ms: float = 0

class BaseTool(ABC):
    """Abstract base class for all tools."""
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with parameters."""
        pass
    
    @abstractmethod
    def get_schema(self) -> ToolSchema:
        """Return parameter schema."""
        pass
    
    def to_openai_function(self) -> Dict[str, Any]:
        """Convert to OpenAI function format."""
        pass
    
    def to_anthropic_tool(self) -> Dict[str, Any]:
        """Convert to Anthropic tool format."""
        pass
    
    def to_langchain_tool(self):
        """Convert to LangChain StructuredTool."""
        pass
```

### 9.4 Tool Implementations

#### 9.4.1 FunctionTool

```python
from abhikarta.tools import FunctionTool, tool

# Method 1: Using from_function
def search(query: str, limit: int = 10) -> str:
    """Search for items."""
    return f"Found {limit} results for {query}"

tool = FunctionTool.from_function(search)

# Method 2: Using decorator
@tool(name="calculator")
def calculate(expression: str) -> float:
    return eval(expression)
```

#### 9.4.2 MCPTool

```python
from abhikarta.tools import MCPTool

# Automatically created when MCP server connects
tool = MCPTool.from_mcp_tool_definition(
    tool_def={"name": "fetch", "description": "..."},
    server_url="http://localhost:8000",
    server_name="my_server"
)
```

#### 9.4.3 HTTPTool

```python
from abhikarta.tools import HTTPTool, HTTPMethod

weather_tool = HTTPTool.create(
    name="get_weather",
    description="Get current weather",
    url="https://api.weather.com/v1/current",
    method=HTTPMethod.GET,
    parameters=[
        {"name": "city", "type": "string", "required": True}
    ]
)
```

#### 9.4.4 CodeFragmentTool

```python
from abhikarta.tools import CodeFragmentTool

tool = CodeFragmentTool.create(
    name="calculate_tax",
    code="result = input_data['amount'] * 0.1",
    parameters=[{"name": "amount", "type": "number"}]
)
```

### 9.5 ToolsRegistry

```python
from abhikarta.tools import get_tools_registry

registry = get_tools_registry()

# Register tools
registry.register(my_tool)
registry.register_function(my_function)

# Discovery
tool = registry.get("tool_name")
tools = registry.list_tools()
matching = registry.search("weather")

# Execution
result = registry.execute("tool_name", param1="value")

# LLM Format Conversion
openai_functions = registry.to_openai_functions()
anthropic_tools = registry.to_anthropic_tools()
langchain_tools = registry.to_langchain_tools()

# MCP Integration
registry.register_from_mcp_server(
    server_url="http://localhost:8000",
    server_name="my_server"
)

# Statistics
stats = registry.get_stats()
```

### 9.6 Module Structure

```
abhikarta/tools/
├── __init__.py           # Exports all components
├── base_tool.py          # BaseTool, ToolMetadata, ToolSchema, ToolResult
├── function_tool.py      # FunctionTool, AsyncFunctionTool, @tool decorator
├── mcp_tool.py           # MCPTool, MCPPluginTool
├── http_tool.py          # HTTPTool, WebhookTool, HTTPMethod
├── code_fragment_tool.py # CodeFragmentTool, PythonExpressionTool
├── langchain_tool.py     # LangChainToolWrapper, wrap_langchain_tools
└── registry.py           # ToolsRegistry singleton
```

---

## 10. MCP Plugin Framework Design

### 10.1 Overview (Enhanced in v1.1.6)

The MCP (Model Context Protocol) module now includes centralized server management with automatic tool registration.

### 10.2 MCPServerManager

```python
from abhikarta.mcp import get_mcp_manager, MCPServerConfig

# Get singleton instance
manager = get_mcp_manager()

# Add a server
config = MCPServerConfig(
    server_id="weather-server",
    name="Weather API",
    url="http://localhost:8080",
    auto_connect=True,
    auth_type=MCPAuthType.BEARER_TOKEN,
    auth_token="secret"
)
manager.add_server(config)

# Connect and load tools
manager.connect_server("weather-server")

# Health monitoring
manager.start_health_monitor(interval_seconds=30)

# Get statistics
stats = manager.get_stats()
```

### 10.3 MCPServerConfig

```python
@dataclass
class MCPServerConfig:
    server_id: str
    name: str
    url: str
    description: str = ""
    transport: MCPTransportType = MCPTransportType.HTTP
    auth_type: MCPAuthType = MCPAuthType.NONE
    auth_token: str = ""
    timeout_seconds: int = 30
    auto_connect: bool = True
    retry_count: int = 3
```

### 10.4 Plugin Registration

```python
# MCP Plugin configuration structure
{
    "plugin_id": "filesystem",
    "name": "Filesystem Plugin",
    "description": "File system operations",
    "server_type": "stdio",
    "config": {
        "command": "npx",
        "args": ["@modelcontextprotocol/server-filesystem", "/data"],
        "env": {}
    },
    "permissions": {
        "allowed_roles": ["agent_developer", "super_admin"]
    },
    "status": "active"
}
```

### 10.5 MCP Module Structure

```
abhikarta/mcp/
├── __init__.py    # Exports all components
├── server.py      # MCPServer, MCPServerConfig, MCPServerState
├── client.py      # HTTPMCPClient, WebSocketMCPClient
└── manager.py     # MCPServerManager singleton
```

### 10.6 Tool Integration

When an MCP server connects, all its tools are:
1. Wrapped as `MCPTool` instances (extending `BaseTool`)
2. Automatically registered with `ToolsRegistry`
3. Available for use by agents, workflows, and API

```python
# Tools are auto-registered when server connects
manager.connect_server("weather-server")

# Access via ToolsRegistry
registry = get_tools_registry()
tool = registry.get("weather-server_get_weather")
result = tool.execute(city="London")
```

---

## 11. UI/UX Design

### 11.1 Color Palette (BMO-Inspired)

```css
:root {
    /* Primary Colors */
    --bmo-blue: #0075BE;
    --bmo-dark-blue: #003865;
    --bmo-light-blue: #E8F4FC;
    
    /* Backgrounds */
    --bg-primary: #E8F4FC;
    --bg-card: #FFFFFF;
    --bg-dark: #003865;
    
    /* Text */
    --text-primary: #333333;
    --text-secondary: #666666;
    --text-light: #FFFFFF;
    
    /* Status Colors */
    --success: #28A745;
    --warning: #FFC107;
    --danger: #DC3545;
    --info: #17A2B8;
    
    /* Borders */
    --border-color: #DEE2E6;
    --border-radius: 8px;
}
```

### 10.2 Base Template Structure

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Abhikarta-LLM{% endblock %}</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
    
    <!-- Custom CSS -->
    <link href="{{ url_for('static', filename='css/theme.css') }}" rel="stylesheet">
    
    {% block extra_css %}{% endblock %}
</head>
<body class="bg-light-blue">
    <!-- Navigation -->
    {% include 'components/navbar.html' %}
    
    <!-- Flash Messages -->
    {% include 'components/flash_messages.html' %}
    
    <!-- Main Content -->
    <main class="container-fluid py-4">
        {% block content %}{% endblock %}
    </main>
    
    <!-- Footer -->
    {% include 'components/footer.html' %}
    
    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Custom JS -->
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### 10.3 Page Layouts

#### Admin Dashboard
```
┌────────────────────────────────────────────────────────┐
│  [Logo] Abhikarta-LLM          [User] ▼  [Logout]     │  <- Dark Blue Nav
├────────────────────────────────────────────────────────┤
│ ┌──────────┐ ┌──────────────────────────────────────┐ │
│ │ Sidebar  │ │                                      │ │
│ │ ───────  │ │     Dashboard Cards                  │ │
│ │ Dashboard│ │  ┌────────┐ ┌────────┐ ┌────────┐   │ │
│ │ Users    │ │  │ Users  │ │ Agents │ │ Plugins│   │ │
│ │ Agents   │ │  │   12   │ │   34   │ │   8    │   │ │
│ │ MCP      │ │  └────────┘ └────────┘ └────────┘   │ │
│ │ Settings │ │                                      │ │
│ │          │ │  Recent Activity                     │ │
│ │          │ │  ┌──────────────────────────────┐   │ │
│ │          │ │  │ Activity Table               │   │ │
│ │          │ │  └──────────────────────────────┘   │ │
│ └──────────┘ └──────────────────────────────────────┘ │
│                    Light Blue Background               │
└────────────────────────────────────────────────────────┘
```

---

## 12. Configuration Management

### 11.1 config.yaml Structure

```yaml
# Abhikarta-LLM Configuration
# Version: 1.1.6

app:
  name: "Abhikarta-LLM"
  version: "1.1.6"
  debug: false
  secret_key: "${SECRET_KEY}"

# Database Configuration
database:
  type: "sqlite"  # Options: sqlite, postgresql
  
  sqlite:
    path: "./data/abhikarta.db"
  
  postgresql:
    host: "${PG_HOST:localhost}"
    port: ${PG_PORT:5432}
    database: "${PG_DATABASE:abhikarta}"
    user: "${PG_USER:abhikarta_user}"
    password: "${PG_PASSWORD}"

# User Management
users:
  file: "./data/users.json"

# LLM Providers
llm:
  default_provider: "openai"
  
  providers:
    openai:
      enabled: true
      api_key: "${OPENAI_API_KEY}"
      default_model: "gpt-4o"
    
    anthropic:
      enabled: true
      api_key: "${ANTHROPIC_API_KEY}"
      default_model: "claude-3-5-sonnet-20241022"
    
    ollama:
      enabled: true
      base_url: "${OLLAMA_BASE_URL:http://localhost:11434}"
      default_model: "llama3"
    
    bedrock:
      enabled: false
      region: "${AWS_REGION:us-east-1}"
      default_model: "anthropic.claude-3-sonnet-20240229-v1:0"

# MCP Configuration
mcp:
  plugins_dir: "./data/mcp_plugins"
  
# Logging
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "./logs/abhikarta.log"

# Server
server:
  host: "0.0.0.0"
  port: 5000
```

---

## 13. Security Design

### 12.1 Authentication Flow

```
1. User submits credentials (user_id, password)
2. UserFacade.authenticate() checks against users.json
3. Plain text password comparison (initial implementation)
4. On success: Create Flask session with user data
5. On failure: Return error, log attempt
```

### 12.2 Authorization (RBAC)

```python
# Role hierarchy
ROLES = {
    'super_admin': {
        'description': 'Full system access',
        'permissions': ['*']
    },
    'domain_admin': {
        'description': 'Domain administration',
        'permissions': ['users.*', 'agents.*', 'mcp.*', 'executions.*']
    },
    'agent_developer': {
        'description': 'Agent development',
        'permissions': ['agents.create', 'agents.read', 'agents.update', 'agents.test']
    },
    'agent_publisher': {
        'description': 'Agent publishing',
        'permissions': ['agents.read', 'agents.publish', 'agents.approve']
    },
    'agent_user': {
        'description': 'Agent execution',
        'permissions': ['agents.read', 'agents.execute', 'executions.read']
    },
    'viewer': {
        'description': 'Read-only access',
        'permissions': ['agents.read', 'executions.read']
    }
}
```

### 12.3 Audit Logging

```python
def log_audit(user_id: str, action: str, resource_type: str, 
              resource_id: str, details: dict, ip_address: str):
    """Log an audit event."""
    audit_entry = {
        'user_id': user_id,
        'action': action,
        'resource_type': resource_type,
        'resource_id': resource_id,
        'details': json.dumps(details),
        'ip_address': ip_address,
        'created_at': datetime.now().isoformat()
    }
    db_facade.execute(
        "INSERT INTO audit_logs (...) VALUES (...)",
        tuple(audit_entry.values())
    )
```

---

## 14. API Specifications

### 13.1 REST API Endpoints

#### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/login | User login |
| POST | /api/auth/logout | User logout |
| GET | /api/auth/session | Get current session |

#### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/users | List users |
| GET | /api/users/{id} | Get user |
| POST | /api/users | Create user |
| PUT | /api/users/{id} | Update user |
| DELETE | /api/users/{id} | Delete user |

#### Agents
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/agents | List agents |
| GET | /api/agents/{id} | Get agent |
| POST | /api/agents | Create agent |
| PUT | /api/agents/{id} | Update agent |
| DELETE | /api/agents/{id} | Delete agent |
| POST | /api/agents/{id}/execute | Execute agent |

#### MCP Plugins
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/mcp/plugins | List plugins |
| GET | /api/mcp/plugins/{id} | Get plugin |
| POST | /api/mcp/plugins | Register plugin |
| DELETE | /api/mcp/plugins/{id} | Unregister plugin |
| GET | /api/mcp/plugins/{id}/tools | List tools |
| POST | /api/mcp/plugins/{id}/tools/{name} | Execute tool |

### 13.2 Response Format

```json
{
    "success": true,
    "data": { ... },
    "message": "Operation successful",
    "timestamp": "2025-12-26T10:00:00Z"
}
```

### 13.3 Error Response

```json
{
    "success": false,
    "error": {
        "code": "AUTH_001",
        "message": "Invalid credentials"
    },
    "timestamp": "2025-12-26T10:00:00Z"
}
```

---

## 15. Deployment Architecture

### 14.1 Directory Structure

```
abhikarta-llm/
├── abhikarta/              # Main package
│   ├── __init__.py
│   ├── config/
│   ├── database/
│   ├── user_management/
│   ├── rbac/
│   ├── llm_provider/
│   ├── mcp/
│   ├── agent/
│   ├── hitl/
│   ├── web/
│   └── utils/
├── data/                   # Data directory
│   ├── users.json
│   ├── abhikarta.db
│   └── mcp_plugins/
├── logs/                   # Log files
├── docs/                   # Documentation
│   ├── REQUIREMENTS.md
│   └── DESIGN.md
├── tests/                  # Test suite
├── config.yaml             # Configuration
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
├── README.md
└── LICENSE
```

### 14.2 Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "run.py"]
```

### 14.3 Docker Compose

```yaml
version: '3.8'

services:
  abhikarta:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    
  # Optional: PostgreSQL
  postgres:
    image: postgres:16
    environment:
      - POSTGRES_DB=abhikarta
      - POSTGRES_USER=abhikarta_user
      - POSTGRES_PASSWORD=${PG_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    profiles:
      - postgres

volumes:
  pgdata:
```

---

## Appendix A: File Inventory

### Core Modules

| File | Purpose |
|------|---------|
| abhikarta/__init__.py | Package initialization (v1.1.6) |
| abhikarta/config/settings.py | Settings management |
| run_server.py | Application entry point |

### Database Module

| File | Purpose |
|------|---------|
| abhikarta/database/__init__.py | Database module exports |
| abhikarta/database/db_facade.py | Database facade pattern |
| abhikarta/database/sqlite_handler.py | SQLite implementation |
| abhikarta/database/postgres_handler.py | PostgreSQL implementation |
| abhikarta/database/schema/__init__.py | Schema module exports |
| abhikarta/database/schema/sqlite_schema.py | SQLite DDL (15 tables, indexes, triggers) |
| abhikarta/database/schema/postgres_schema.py | PostgreSQL DDL (16 tables, JSONB, full-text search) |

### Agent Module

| File | Purpose |
|------|---------|
| abhikarta/agent/__init__.py | Agent module exports |
| abhikarta/agent/agent_manager.py | Agent CRUD and lifecycle management |
| abhikarta/agent/agent_template.py | Template library with 6 built-in templates |

### User Management Module

| File | Purpose |
|------|---------|
| abhikarta/user_management/__init__.py | User management exports |
| abhikarta/user_management/user_facade.py | User CRUD operations |

### Web Module

| File | Purpose |
|------|---------|
| abhikarta/web/__init__.py | Web module exports |
| abhikarta/web/app.py | Flask application factory |
| abhikarta/web/abhikarta_llm_web.py | Main web application class |
| abhikarta/web/routes/abstract_routes.py | Base route class with decorators |
| abhikarta/web/routes/auth_routes.py | Authentication routes |
| abhikarta/web/routes/admin_routes.py | Admin dashboard and user management |
| abhikarta/web/routes/agent_routes.py | Agent designer and template library |
| abhikarta/web/routes/user_routes.py | User-facing agent execution |
| abhikarta/web/routes/api_routes.py | REST API endpoints |
| abhikarta/web/routes/mcp_routes.py | MCP plugin management |

### Templates

| File | Purpose |
|------|---------|
| abhikarta/web/templates/base.html | Base layout template |
| abhikarta/web/templates/auth/login.html | Login page |
| abhikarta/web/templates/admin/dashboard.html | Admin dashboard |
| abhikarta/web/templates/admin/users.html | User management (modal-based) |
| abhikarta/web/templates/agents/list.html | Agent list view |
| abhikarta/web/templates/agents/designer.html | Visual agent designer |
| abhikarta/web/templates/agents/templates.html | Template library |
| abhikarta/web/templates/agents/detail.html | Agent details |
| abhikarta/web/templates/agents/test.html | Agent testing interface |
| abhikarta/web/templates/user/dashboard.html | User dashboard |
| abhikarta/web/templates/user/agents.html | Published agents list |
| abhikarta/web/templates/user/execute_agent.html | Agent execution interface |
| abhikarta/web/templates/help/help.html | Help documentation |
| abhikarta/web/templates/help/about.html | About page |

### Configuration Files

| File | Purpose |
|------|---------|
| config/application.properties | Main application configuration |
| data/users.json | User data storage (JSON backend) |
| requirements.txt | Python dependencies |

---

## Appendix B: Database Schema Summary

### SQLite Schema (sqlite_schema.py)

**Tables:** schema_version, users, roles, user_roles, agents, agent_versions, agent_templates, executions, execution_steps, hitl_tasks, mcp_plugins, audit_logs, sessions, api_keys, system_settings

**Features:**
- 24+ indexes for query optimization
- 3 triggers for automatic timestamp updates
- 7 default roles with permissions

### PostgreSQL Schema (postgres_schema.py)

**Tables:** All SQLite tables plus metrics table

**PostgreSQL-Specific Features:**
- JSONB columns for flexible configuration storage
- Custom ENUM types: agent_status, execution_status, hitl_status, difficulty_level
- Full-text search with tsvector on agents table
- GIN indexes for JSONB and array columns
- UUID extension support
- Partition templates for high-volume tables

---

## Appendix C: Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Dec 2025 | Initial release with core functionality |
| 1.0.1 | Dec 2025 | Code Fragments (db/file/s3 URIs), 19 database tables |
| 1.1.6 | Dec 2025 | Visual Agent Designer with drag-drop canvas, LLM Provider/Model Management, RBAC for models, MCP Tool Servers for dynamic tool loading, **LangChain & LangGraph integration** for agent and workflow execution, 23 database tables |

### v1.1.6 LangChain/LangGraph Features

- **LangChain LLM Factory**: Create LangChain LLM instances from database configurations (OpenAI, Anthropic, Google, Ollama, Mistral, Cohere, Together, Groq, HuggingFace, AWS Bedrock)
- **LangChain Tools**: MCP Tool Server integration, Code Fragment tools, Built-in tools (Wikipedia, Web Search, Python REPL)
- **LangChain Agents**: ReAct, Tool-Calling, and Structured Chat agent types
- **LangGraph Workflows**: StateGraph-based workflow execution with state management, conditional branching, and HITL support
- **Execution Logging**: Full logging of agent and workflow executions with intermediate steps and tool calls

---

*— End of Design Document —*
