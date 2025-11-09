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
from web.route_management.auth_routes import admin_required
import logging
from user_management.user_manager import UserManager

logger = logging.getLogger(__name__)


class AdminRoutes:
    """
    Handles admin-specific routes for the application.
    
    This class manages routes that are only accessible to users with admin role.
    
    Attributes:
        app: Flask application instance
        user_manager: UserManager instance for user operations
    """
    
    def __init__(self, app, user_manager: UserManager):
        """
        Initialize AdminRoutes.
        
        Args:
            app: Flask application instance
            user_manager: UserManager instance for database operations
        """
        self.app = app
        self.user_manager = user_manager
        logger.info("AdminRoutes initialized")
    
    def register_routes(self):
        """Register all admin routes."""
        
        @self.app.route('/admin/dashboard')
        @admin_required
        def admin_dashboard():
            """Admin dashboard with management cards."""
            # Get statistics
            stats = self.user_manager.get_statistics()
            
            return render_template('admin_dashboard.html',
                                 fullname=session.get('fullname'),
                                 userid=session.get('userid'),
                                 roles=session.get('roles', []),
                                 stats=stats)
        
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
        
        @self.app.route('/admin/roles')
        @admin_required
        def manage_roles():
            """Manage roles page with pagination."""
            from flask import request
            
            # Get pagination parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', '10')
            
            # Get all roles
            all_roles = self.user_manager.list_roles()
            total_roles = len(all_roles)
            
            # Handle pagination
            if per_page == 'all':
                paginated_roles = all_roles
                total_pages = 1
                page = 1
            else:
                per_page = int(per_page)
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                paginated_roles = all_roles[start_idx:end_idx]
                total_pages = (total_roles + per_page - 1) // per_page
            
            return render_template('manage_roles.html',
                                 fullname=session.get('fullname'),
                                 userid=session.get('userid'),
                                 roles=session.get('roles', []),
                                 role_list=paginated_roles,
                                 total_roles=total_roles,
                                 current_page=page,
                                 total_pages=total_pages,
                                 per_page=str(per_page))
        
        @self.app.route('/admin/roles/create')
        @admin_required
        def create_role():
            """Create new role page."""
            # Get all resources for selection
            resources = self.user_manager.list_resources()
            
            return render_template('create_role.html',
                                 fullname=session.get('fullname'),
                                 userid=session.get('userid'),
                                 roles=session.get('roles', []),
                                 resources=resources)
        
        @self.app.route('/admin/roles/edit/<role_name>')
        @admin_required
        def edit_role(role_name):
            """Edit existing role page."""
            # Load the role
            role = self.user_manager.load_role(role_name)
            
            if not role:
                flash(f'Role "{role_name}" not found', 'error')
                return redirect(url_for('manage_roles'))
            
            # Get all resources
            resources = self.user_manager.list_resources()
            
            # Get users with this role
            users_with_role = self.user_manager.get_users_with_role(role_name)
            
            return render_template('edit_role.html',
                                 fullname=session.get('fullname'),
                                 userid=session.get('userid'),
                                 roles=session.get('roles', []),
                                 role=role,
                                 resources=resources,
                                 users_with_role=users_with_role)
        
        logger.info("Admin routes registered")
