"""
Routes Module - Flask route handlers.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

from .abstract_routes import AbstractRoutes, login_required, admin_required
from .auth_routes import AuthRoutes
from .admin_routes import AdminRoutes
from .user_routes import UserRoutes
from .agent_routes import AgentRoutes
from .mcp_routes import MCPRoutes
from .api_routes import APIRoutes
from .workflow_routes import WorkflowRoutes

__all__ = [
    'AbstractRoutes',
    'login_required',
    'admin_required',
    'AuthRoutes',
    'AdminRoutes',
    'UserRoutes',
    'AgentRoutes',
    'MCPRoutes',
    'APIRoutes',
    'WorkflowRoutes'
]
