"""
Database Delegates Package - Domain-specific database operation handlers.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.

Version: 1.4.8

This package provides specialized delegates for different database domains:
- UserDelegate: Users, Roles, UserRoles, Sessions, API Keys
- LLMDelegate: LLM Providers, Models, Model Permissions, LLM Calls
- AgentDelegate: Agents, Agent Versions, Agent Templates
- WorkflowDelegate: Workflows, Workflow Nodes
- ExecutionDelegate: Executions, Execution Steps
- HITLDelegate: HITL Tasks, Comments, Assignments
- MCPDelegate: MCP Plugins, MCP Tool Servers
- AuditDelegate: Audit Logs, System Settings
- CodeFragmentDelegate: Code Fragments
- SwarmDelegate: Swarms, Agent Pools, Triggers, Executions
- NotificationDelegate: Notification Channels, Logs, Webhooks (v1.4.0)
- ScriptsDelegate: Python Scripts, Script Executions (v1.4.8)
"""

from .user_delegate import UserDelegate
from .llm_delegate import LLMDelegate
from .agent_delegate import AgentDelegate
from .workflow_delegate import WorkflowDelegate
from .execution_delegate import ExecutionDelegate
from .hitl_delegate import HITLDelegate
from .mcp_delegate import MCPDelegate
from .audit_delegate import AuditDelegate
from .code_fragment_delegate import CodeFragmentDelegate
from .swarm_delegate import SwarmDelegate
from .notification_delegate import NotificationDelegate
from .scripts_delegate import ScriptsDelegate

__all__ = [
    'UserDelegate',
    'LLMDelegate',
    'AgentDelegate',
    'WorkflowDelegate',
    'ExecutionDelegate',
    'HITLDelegate',
    'MCPDelegate',
    'AuditDelegate',
    'CodeFragmentDelegate',
    'SwarmDelegate',
    'NotificationDelegate',
    'ScriptsDelegate',
]

__version__ = '1.4.8'
