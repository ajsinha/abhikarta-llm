"""
AI Org Module - AI-Powered Organizational Structures.

This module enables creation and execution of AI-powered organizational
hierarchies where each node represents an AI agent that mirrors a human role.

Key Features:
- Visual org chart designer
- Hierarchical task delegation
- Response aggregation and summarization
- Human-in-the-Loop (HITL) interventions
- Multi-channel notifications
- Complete audit trail

Version: 1.4.5
Copyright © 2025-2030, All Rights Reserved
"""

from .models import (
    AIOrg,
    AINode,
    AITask,
    AIResponse,
    AIHITLAction,
    AIEventLog,
    HITLQueueItem,
    OrgStatus,
    NodeType,
    TaskStatus,
    TaskPriority,
    ResponseType,
    HITLActionType,
    DelegationStrategy,
    HumanMirror,
    HITLConfig
)

from .db_ops import AIORGDBOps, AIORG_SQLITE_SCHEMA, AIORG_POSTGRES_SCHEMA
from .org_manager import OrgManager
from .task_engine import TaskEngine
from .hitl_manager import HITLManager
from .prompts import AIORGPrompts

__all__ = [
    # Models
    'AIOrg',
    'AINode',
    'AITask',
    'AIResponse',
    'AIHITLAction',
    'AIEventLog',
    'HITLQueueItem',
    
    # Enums
    'OrgStatus',
    'NodeType',
    'TaskStatus',
    'TaskPriority',
    'ResponseType',
    'HITLActionType',
    'DelegationStrategy',
    
    # Config classes
    'HumanMirror',
    'HITLConfig',
    
    # DB Operations
    'AIORGDBOps',
    'AIORG_SQLITE_SCHEMA',
    'AIORG_POSTGRES_SCHEMA',
    
    # Managers
    'OrgManager',
    'TaskEngine',
    'HITLManager',
    
    # Prompts
    'AIORGPrompts'
]

__version__ = '1.4.5'


# Singleton instance for db operations
_aiorg_db_ops = None


def get_aiorg_db_ops(db_facade=None):
    """
    Get or create the AI Org database operations instance.
    
    Args:
        db_facade: Database facade instance (required on first call)
        
    Returns:
        AIORGDBOps instance
    """
    global _aiorg_db_ops
    
    if _aiorg_db_ops is None:
        if db_facade is None:
            raise ValueError("db_facade required for first initialization")
        _aiorg_db_ops = AIORGDBOps(db_facade)
    
    return _aiorg_db_ops


def init_aiorg_schema(db_facade, db_type='sqlite'):
    """
    Initialize AI Org database tables.
    
    Args:
        db_facade: Database facade instance
        db_type: 'sqlite' or 'postgres'
    """
    schema = AIORG_SQLITE_SCHEMA if db_type == 'sqlite' else AIORG_POSTGRES_SCHEMA
    
    # Execute each statement
    for statement in schema.split(';'):
        statement = statement.strip()
        if statement:
            try:
                db_facade.execute(statement)
            except Exception as e:
                # Table might already exist
                pass
    
    db_facade.commit()
