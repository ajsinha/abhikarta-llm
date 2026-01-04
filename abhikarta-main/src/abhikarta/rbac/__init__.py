"""
RBAC Module - Role-Based Access Control.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

# Role definitions
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
    'hitl_reviewer': {
        'description': 'HITL review',
        'permissions': ['hitl.*', 'executions.read']
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

__all__ = ['ROLES']
