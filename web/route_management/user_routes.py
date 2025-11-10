"""
User Routes Module - Handles user management API endpoints

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

from flask import request, jsonify, session, render_template, redirect, url_for, flash
from web.route_management.abstract_routes import admin_required, login_required
from web.route_management.abstract_routes import AbstractRoutes
from user_management.user import User
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class UserRoutes(AbstractRoutes):
    """
    Handles user-related API routes for the application.

    This class manages all user operations including:
    - Creating users (admin only)
    - Updating users (admin only)
    - Deleting users (admin only)
    - Viewing user details (admin only)
    - Enabling/disabling users (admin only)

    Attributes:
        app: Flask application instance
        user_manager: UserManager instance for database operations
    """

    def __init__(self, app, db_connection_pool_name: str):
        """
        Initialize UserRoutes.

        Args:
            app: Flask application instance
        """
        super().__init__(app, db_connection_pool_name)
        logger.info("UserRoutes initialized")

    def register_routes(self):
        """Register all user-related routes."""

        # ==================== View User Details ====================
        @self.app.route('/admin/users/view/<userid>')
        @admin_required
        def view_user(userid):
            """View user details page."""
            # Load the user
            user = self.user_manager.load_user(userid)

            if not user:
                flash(f'User "{userid}" not found', 'error')
                return redirect(url_for('manage_users'))

            # Get available roles
            all_roles = self.user_manager.list_roles()

            return render_template('view_user.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('userid'),
                                   roles=session.get('roles', []),
                                   user=user,
                                   all_roles=all_roles)

        # ==================== Create User ====================
        @self.app.route('/admin/users/create')
        @admin_required
        def admin_create_user():
            """Create new user page."""
            # Get all roles for selection
            roles = self.user_manager.list_roles()

            return render_template('create_user.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('userid'),
                                   roles=session.get('roles', []),
                                   available_roles=roles)

        @self.app.route('/api/admin/users', methods=['POST'])
        @admin_required
        def create_user():
            from user_management.user import PasswordEncryption

            """
            Create a new user.

            Request Body:
                {
                    "userid": "john_doe",
                    "fullname": "John Doe",
                    "emailaddress": "john@example.com",
                    "password": "securepassword",
                    "roles": ["user", "developer"],
                    "enabled": true
                }

            Returns:
                JSON response with success status
            """
            try:
                data = request.get_json()

                # Validate required fields
                required_fields = ['userid', 'fullname', 'emailaddress', 'password']
                for field in required_fields:
                    if field not in data or not data[field]:
                        return jsonify({
                            'success': False,
                            'message': f'{field} is required'
                        }), 400

                userid = data['userid'].strip()
                fullname = data['fullname'].strip()
                emailaddress = data['emailaddress'].strip()
                password = data['password']
                roles = data.get('roles', [])
                enabled = data.get('enabled', True)

                # Check if user already exists
                existing_user = self.user_manager.load_user(userid)
                if existing_user:
                    return jsonify({
                        'success': False,
                        'message': f'User "{userid}" already exists'
                    }), 409

                # Create new user with hashed password
                user = User(
                    userid=userid,
                    fullname=fullname,
                    emailaddress=emailaddress,
                    password_hash=PasswordEncryption.encrypt_password(password),  # Temporary, will be set below
                    roles=roles,
                    enabled=enabled
                )
                # Set the actual password (this hashes it)
                #user.set_password(password)

                # Save user
                if self.user_manager.save_user(user):
                    logger.info(f"Admin {session.get('userid')} created user '{userid}'")
                    return jsonify({
                        'success': True,
                        'message': f'User "{userid}" created successfully',
                        'user': self._user_to_dict(user)
                    }), 201
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to create user'
                    }), 500

            except Exception as e:
                logger.error(f"Error creating user: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error creating user: {str(e)}'
                }), 500

        # ==================== Edit User ====================
        @self.app.route('/admin/users/edit/<userid>')
        @admin_required
        def edit_user(userid):
            """Edit existing user page."""
            # Prevent editing admin user
            if userid.lower() == 'admin':
                flash('Admin user cannot be edited', 'error')
                return redirect(url_for('manage_users'))

            # Load the user
            user = self.user_manager.load_user(userid)

            if not user:
                flash(f'User "{userid}" not found', 'error')
                return redirect(url_for('manage_users'))

            # Get all roles
            all_roles = self.user_manager.list_roles()

            return render_template('edit_user.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('userid'),
                                   roles=session.get('roles', []),
                                   user=user,
                                   available_roles=all_roles)

        @self.app.route('/api/admin/users/<userid>', methods=['PUT'])
        @admin_required
        def update_user(userid):
            """
            Update an existing user.

            Request Body:
                {
                    "fullname": "John Doe Updated",
                    "emailaddress": "john.updated@example.com",
                    "roles": ["user", "admin"],
                    "enabled": true,
                    "password": "newpassword"  // optional
                }

            Returns:
                JSON response with success status
            """
            try:
                # Prevent editing admin user
                if userid.lower() == 'admin':
                    return jsonify({
                        'success': False,
                        'message': 'Admin user cannot be modified'
                    }), 403

                # Load existing user
                user = self.user_manager.load_user(userid)
                if not user:
                    return jsonify({
                        'success': False,
                        'message': f'User "{userid}" not found'
                    }), 404

                data = request.get_json()

                # Update user fields
                if 'fullname' in data:
                    user.fullname = data['fullname'].strip()
                if 'emailaddress' in data:
                    user.emailaddress = data['emailaddress'].strip()
                if 'roles' in data:
                    user.roles = data['roles']
                if 'enabled' in data:
                    user.enabled = data['enabled']

                # Update password if provided
                if 'password' in data and data['password']:
                    user.set_password(data['password'])

                # Save updated user
                if self.user_manager.save_user(user):
                    logger.info(f"Admin {session.get('userid')} updated user '{userid}'")
                    return jsonify({
                        'success': True,
                        'message': f'User "{userid}" updated successfully',
                        'user': self._user_to_dict(user)
                    }), 200
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to update user'
                    }), 500

            except Exception as e:
                logger.error(f"Error updating user {userid}: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error updating user: {str(e)}'
                }), 500

        # ==================== Delete User ====================
        @self.app.route('/api/admin/users/<userid>', methods=['DELETE'])
        @admin_required
        def delete_user(userid):
            """
            Delete a user.

            Returns:
                JSON response with success status
            """
            try:
                # Prevent deleting admin user
                if userid.lower() == 'admin':
                    return jsonify({
                        'success': False,
                        'message': 'Admin user cannot be deleted'
                    }), 403

                # Prevent deleting self
                if userid == session.get('userid'):
                    return jsonify({
                        'success': False,
                        'message': 'You cannot delete your own account'
                    }), 403

                # Check if user exists
                user = self.user_manager.load_user(userid)
                if not user:
                    return jsonify({
                        'success': False,
                        'message': f'User "{userid}" not found'
                    }), 404

                # Delete user
                if self.user_manager.delete_user(userid):
                    logger.info(f"Admin {session.get('userid')} deleted user '{userid}'")
                    return jsonify({
                        'success': True,
                        'message': f'User "{userid}" deleted successfully'
                    }), 200
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to delete user'
                    }), 500

            except Exception as e:
                logger.error(f"Error deleting user {userid}: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error deleting user: {str(e)}'
                }), 500

        # ==================== Enable/Disable User ====================
        @self.app.route('/api/admin/users/<userid>/toggle', methods=['POST'])
        @admin_required
        def toggle_user_status(userid):
            """
            Enable or disable a user.

            Returns:
                JSON response with success status
            """
            try:
                # Prevent disabling admin user
                if userid.lower() == 'admin':
                    return jsonify({
                        'success': False,
                        'message': 'Admin user status cannot be changed'
                    }), 403

                # Prevent disabling self
                if userid == session.get('userid'):
                    return jsonify({
                        'success': False,
                        'message': 'You cannot disable your own account'
                    }), 403

                # Load user
                user = self.user_manager.load_user(userid)
                if not user:
                    return jsonify({
                        'success': False,
                        'message': f'User "{userid}" not found'
                    }), 404

                # Toggle enabled status
                user.enabled = not user.enabled

                # Save user
                if self.user_manager.save_user(user):
                    status = 'enabled' if user.enabled else 'disabled'
                    logger.info(f"Admin {session.get('userid')} {status} user '{userid}'")
                    return jsonify({
                        'success': True,
                        'message': f'User "{userid}" {status} successfully',
                        'enabled': user.enabled
                    }), 200
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to update user status'
                    }), 500

            except Exception as e:
                logger.error(f"Error toggling user status {userid}: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error toggling user status: {str(e)}'
                }), 500

        logger.info("User routes registered")

    # ==================== Helper Methods ====================

    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """
        Convert a User object to a dictionary.

        Args:
            user: User object to convert

        Returns:
            Dictionary representation of the user
        """
        # Handle last_login - could be datetime object or string from database
        last_login_str = None
        if user.last_login:
            if hasattr(user.last_login, 'isoformat'):
                # It's a datetime object
                last_login_str = user.last_login.isoformat()
            elif isinstance(user.last_login, str):
                # It's already a string
                last_login_str = user.last_login

        # Handle created_at
        created_at_str = None
        if user.created_at:
            if hasattr(user.created_at, 'isoformat'):
                created_at_str = user.created_at.isoformat()
            elif isinstance(user.created_at, str):
                created_at_str = user.created_at

        return {
            'userid': user.userid,
            'fullname': user.fullname,
            'emailaddress': user.emailaddress,
            'roles': user.roles,
            'enabled': user.enabled,
            'last_login': last_login_str,
            'created_at': created_at_str
        }