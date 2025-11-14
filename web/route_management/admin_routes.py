"""
Admin Routes Module - Handles admin-specific routes and functionality

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This document and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use of this document or the software
system it describes is strictly prohibited without explicit written permission from the
copyright holder. This document is provided "as is" without warranty of any kind, either
expressed or implied. The copyright holder shall not be liable for any damages arising
from the use of this document or the software system it describes.

Patent Pending: Certain architectural patterns and implementations described in this
document may be subject to patent applications.
"""

from flask import render_template, session, redirect, url_for, flash

from tool_management.mcp_server_manager import MCPServerManager
from web.route_management.abstract_routes import admin_required
import logging
from user_management.user_manager import UserManager
from web.route_management.abstract_routes import AbstractRoutes

logger = logging.getLogger(__name__)


class AdminRoutes(AbstractRoutes):
    """
    Handles admin-specific routes for the application.
    
    This class manages routes that are only accessible to users with admin role.
    
    Attributes:
        app: Flask application instance
        user_manager: UserManager instance for user operations
    """
    
    def __init__(self, app, db_connection_pool_name: str):
        """
        Initialize AdminRoutes.
        
        Args:
            app: Flask application instance
            user_manager: UserManager instance for database operations
        """
        super().__init__(app, db_connection_pool_name)
        self.app = app


        logger.info("AdminRoutes initialized")

    def register_routes(self):
        """Register all admin routes."""

        @self.app.route('/admin/dashboard')
        @admin_required
        def admin_dashboard():
            """Admin dashboard with management cards."""
            # Get statistics
            stats = self.user_manager.get_statistics()

            # Get MCP server status
            mcp_status = {}
            mcp_count = 0
            if self.mcp_server_manager is not None:
                mcp_status = self.mcp_server_manager.status_all()
                mcp_count = len(mcp_status)

            return render_template('admin_dashboard.html',
                                 fullname=session.get('fullname'),
                                 userid=session.get('userid'),
                                 roles=session.get('roles', []),
                                 stats=stats,
                                 mcp_servers=mcp_status,
                                 mcp_count=mcp_count)
        
        @self.app.route('/admin/users')
        @admin_required
        def manage_users():
            """Manage users page."""
            # Get all users
            users = self.user_manager.list_users()
            roles = self.user_manager.list_roles()
            
            return render_template('manage_users.html',
                                 fullname=session.get('fullname'),
                                 userid=session.get('userid'),
                                 roles=session.get('roles', []),
                                 users=users,
                                 available_roles=roles)
        
        @self.app.route('/admin/models')
        @admin_required
        def manage_models():
            """Manage models page."""
            return render_template('manage_models.html',
                                 fullname=session.get('fullname'),
                                 userid=session.get('userid'),
                                 roles=session.get('roles', []))
        
        @self.app.route('/admin/activities')
        @admin_required
        def manage_activities():
            """Manage activities page."""
            return render_template('manage_activities.html',
                                 fullname=session.get('fullname'),
                                 userid=session.get('userid'),
                                 roles=session.get('roles', []))
        
        @self.app.route('/admin/monitor')
        @admin_required
        def monitor_system():
            """Monitor system page."""
            # Get system statistics
            stats = self.user_manager.get_statistics()
            
            return render_template('monitor_system.html',
                                 fullname=session.get('fullname'),
                                 userid=session.get('userid'),
                                 roles=session.get('roles', []),
                                 stats=stats)
        



        logger.info("Admin routes registered")