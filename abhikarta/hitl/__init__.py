"""
HITL Module - Human-in-the-Loop framework.

Provides functionality for:
- Creating HITL tasks during workflow/agent execution
- Assigning tasks to users
- Managing task lifecycle (pending -> in_progress -> approved/rejected)
- Adding comments and responses
- Tracking assignment history

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

from .hitl_manager import (
    HITLManager,
    HITLTask,
    HITLComment,
    HITLStatus,
    HITLTaskType,
    HITLPriority,
    create_hitl_from_execution
)

__all__ = [
    'HITLManager',
    'HITLTask',
    'HITLComment',
    'HITLStatus',
    'HITLTaskType',
    'HITLPriority',
    'create_hitl_from_execution'
]
