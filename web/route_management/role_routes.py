"""
Role Routes Module - Handles role management API endpoints

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

from flask import request, jsonify, session
from flask import render_template, session, redirect, url_for, flash
from web.route_management.abstract_routes import admin_required,login_required
from web.route_management.abstract_routes import AbstractRoutes
from user_management.user import Role, Permission
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class RoleRoutes(AbstractRoutes):
    """
    Handles role-related API routes for the application.

    This class manages all role operations including:
    - Listing roles (all users)
    - Viewing role details (all users)
    - Creating roles (admin only)
    - Updating roles (admin only)
    - Deleting roles (admin only)
    - Assigning resources to roles (admin only)
    - Removing resources from roles (admin only)
    - Managing role permissions (admin only)
    - Batch operations (admin only)

    Attributes:
        app: Flask application instance
        role_manager: RoleManager instance for database operations
        user_manager: UserManager instance for user operations
    """

    def __init__(self, app, db_connection_pool_name: str):
        """
        Initialize RoleRoutes.

        Args:
            app: Flask application instance
        """
        super().__init__(app, db_connection_pool_name)
        logger.info("RoleRoutes initialized")

    def register_routes(self):
        """Register all role-related API routes."""

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

            return render_template('rbac/manage_roles.html',
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
        def admin_create_role():
            """Create new role page."""
            # Get all resources for selection
            resources = self.user_manager.list_resources()

            return render_template('rbac/create_role.html',
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

            return render_template('rbac/edit_role.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('userid'),
                                   roles=session.get('roles', []),
                                   role=role,
                                   resources=resources,
                                   users_with_role=users_with_role)

        # ==================== List Roles (All Logged-in Users) ====================

        @self.app.route('/api/roles', methods=['GET'])
        @login_required
        def list_roles():
            """
            List all roles with optional filtering.

            Query Parameters:
                - enabled: Filter by enabled status (true/false)
                - search: Search by name or description
                - page: Page number (default: 1)
                - per_page: Items per page (default: 10)

            Returns:
                JSON response with list of roles
            """
            try:
                # Get query parameters
                enabled_filter = request.args.get('enabled', None)
                search_query = request.args.get('search', '').strip()
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 10, type=int)

                # Get roles from database
                roles = self.role_manager.list_roles()

                # Apply enabled filter
                if enabled_filter is not None:
                    is_enabled = enabled_filter.lower() == 'true'
                    roles = [r for r in roles if r.enabled == is_enabled]

                # Apply search filter
                if search_query:
                    search_lower = search_query.lower()
                    roles = [
                        r for r in roles
                        if search_lower in r.name.lower() or
                           (r.description and search_lower in r.description.lower())
                    ]

                # Pagination
                total_roles = len(roles)
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                paginated_roles = roles[start_idx:end_idx]

                # Convert to dict
                roles_data = [self._role_to_dict(r) for r in paginated_roles]

                return jsonify({
                    'success': True,
                    'roles': roles_data,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total_roles,
                        'total_pages': (total_roles + per_page - 1) // per_page
                    }
                }), 200

            except Exception as e:
                logger.error(f"Error listing roles: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error listing roles: {str(e)}'
                }), 500

        # ==================== Get Role Details (All Logged-in Users) ====================

        @self.app.route('/api/roles/<role_name>', methods=['GET'])
        @login_required
        def get_role(role_name):
            """
            Get detailed information about a specific role.

            Args:
                role_name: Name of the role

            Returns:
                JSON response with role details including resources and users
            """
            try:
                role = self.role_manager.load_role(role_name)

                if not role:
                    return jsonify({
                        'success': False,
                        'message': f'Role "{role_name}" not found'
                    }), 404

                # Get users with this role
                users_with_role = self.role_manager.get_users_with_role(role_name)

                role_data = self._role_to_dict(role, include_resources=True)
                role_data['users'] = users_with_role
                role_data['user_count'] = len(users_with_role)

                return jsonify({
                    'success': True,
                    'role': role_data
                }), 200

            except Exception as e:
                logger.error(f"Error getting role {role_name}: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error getting role: {str(e)}'
                }), 500

        # ==================== Create Role (Admin Only) ====================

        @self.app.route('/api/admin/roles', methods=['POST'])
        @admin_required
        def create_role():
            """
            Create a new role.

            Request Body:
                {
                    "name": "role_name",
                    "description": "Role description",
                    "enabled": true,
                    "resources": {
                        "resource1": {
                            "create": true,
                            "read": true,
                            "update": true,
                            "delete": false,
                            "execute": false
                        }
                    },
                    "metadata": {}
                }

            Returns:
                JSON response with created role
            """
            try:
                data = request.get_json()

                # Validate required fields
                if not data or 'name' not in data:
                    return jsonify({
                        'success': False,
                        'message': 'Role name is required'
                    }), 400

                role_name = data['name'].strip()

                # Validate role name format
                if not role_name or not role_name.replace('_', '').isalnum():
                    return jsonify({
                        'success': False,
                        'message': 'Role name must contain only letters, numbers, and underscores'
                    }), 400

                # Check if role already exists
                if self.role_manager.role_exists(role_name):
                    return jsonify({
                        'success': False,
                        'message': f'Role "{role_name}" already exists'
                    }), 409

                # Parse resources and permissions
                resources = {}
                if 'resources' in data and data['resources']:
                    for resource_name, perms in data['resources'].items():
                        # Verify resource exists
                        if not self.resource_manager.resource_exists(resource_name):
                            return jsonify({
                                'success': False,
                                'message': f'Resource "{resource_name}" does not exist'
                            }), 400

                        resources[resource_name] = Permission(
                            create=perms.get('create', False),
                            read=perms.get('read', False),
                            update=perms.get('update', False),
                            delete=perms.get('delete', False),
                            execute=perms.get('execute', False)
                        )

                # Create role object
                role = Role(
                    name=role_name,
                    description=data.get('description', '').strip(),
                    resources=resources,
                    enabled=data.get('enabled', True),
                    created_at=datetime.now(),
                    metadata=data.get('metadata', {})
                )

                # Save to database
                if self.role_manager.save_role(role):
                    logger.info(f"Admin {session.get('userid')} created role '{role_name}'")
                    return jsonify({
                        'success': True,
                        'message': f'Role "{role_name}" created successfully',
                        'role': self._role_to_dict(role, include_resources=True)
                    }), 201
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to create role'
                    }), 500

            except Exception as e:
                logger.error(f"Error creating role: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error creating role: {str(e)}'
                }), 500

        # ==================== Update Role (Admin Only) ====================

        @self.app.route('/api/admin/roles/<role_name>', methods=['PUT'])
        @admin_required
        def update_role(role_name):
            """
            Update an existing role.

            Args:
                role_name: Name of the role to update

            Request Body:
                {
                    "description": "Updated description",
                    "enabled": true,
                    "resources": {...},
                    "metadata": {}
                }

            Returns:
                JSON response with updated role
            """
            try:
                # Protect admin role
                if role_name.lower() == 'admin':
                    return jsonify({
                        'success': False,
                        'message': 'Cannot modify system admin role'
                    }), 403

                # Load existing role
                role = self.role_manager.load_role(role_name)

                if not role:
                    return jsonify({
                        'success': False,
                        'message': f'Role "{role_name}" not found'
                    }), 404

                data = request.get_json()

                # Update description
                if 'description' in data:
                    role.description = data['description'].strip()

                # Update enabled status
                if 'enabled' in data:
                    role.enabled = bool(data['enabled'])

                # Update resources
                if 'resources' in data:
                    resources = {}
                    for resource_name, perms in data['resources'].items():
                        # Verify resource exists
                        if not self.resource_manager.resource_exists(resource_name):
                            return jsonify({
                                'success': False,
                                'message': f'Resource "{resource_name}" does not exist'
                            }), 400

                        resources[resource_name] = Permission(
                            create=perms.get('create', False),
                            read=perms.get('read', False),
                            update=perms.get('update', False),
                            delete=perms.get('delete', False),
                            execute=perms.get('execute', False)
                        )
                    role.resources = resources

                # Update metadata
                if 'metadata' in data:
                    role.metadata = data['metadata']

                # Save to database
                if self.role_manager.save_role(role):
                    logger.info(f"Admin {session.get('userid')} updated role '{role_name}'")
                    return jsonify({
                        'success': True,
                        'message': f'Role "{role_name}" updated successfully',
                        'role': self._role_to_dict(role, include_resources=True)
                    }), 200
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to update role'
                    }), 500

            except Exception as e:
                logger.error(f"Error updating role {role_name}: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error updating role: {str(e)}'
                }), 500

        # ==================== Delete Role (Admin Only) ====================

        @self.app.route('/api/admin/roles/<role_name>', methods=['DELETE'])
        @admin_required
        def delete_role(role_name):
            """
            Delete a role.

            Args:
                role_name: Name of the role to delete

            Query Parameters:
                - force: Force delete even if users have this role

            Returns:
                JSON response indicating success or failure
            """
            try:
                # Protect admin role
                if role_name.lower() == 'admin':
                    return jsonify({
                        'success': False,
                        'message': 'Cannot delete system admin role'
                    }), 403

                # Check if role exists
                if not self.role_manager.role_exists(role_name):
                    return jsonify({
                        'success': False,
                        'message': f'Role "{role_name}" not found'
                    }), 404

                # Check if role is assigned to users
                users_with_role = self.role_manager.get_users_with_role(role_name)

                if users_with_role and not request.args.get('force', 'false').lower() == 'true':
                    return jsonify({
                        'success': False,
                        'message': f'Role "{role_name}" is assigned to {len(users_with_role)} user(s). Use force=true to delete anyway.',
                        'users': users_with_role
                    }), 409

                # Delete role
                if self.role_manager.delete_role(role_name):
                    logger.info(f"Admin {session.get('userid')} deleted role '{role_name}'")
                    return jsonify({
                        'success': True,
                        'message': f'Role "{role_name}" deleted successfully'
                    }), 200
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to delete role'
                    }), 500

            except Exception as e:
                logger.error(f"Error deleting role {role_name}: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error deleting role: {str(e)}'
                }), 500

        # ==================== Assign Resource to Role (Admin Only) ====================

        @self.app.route('/api/admin/roles/<role_name>/resources/<resource_name>', methods=['POST'])
        @admin_required
        def assign_resource_to_role(role_name, resource_name):
            """
            Assign a resource to a role with specific permissions.

            Args:
                role_name: Name of the role
                resource_name: Name of the resource

            Request Body:
                {
                    "create": true,
                    "read": true,
                    "update": true,
                    "delete": false,
                    "execute": false
                }

            Returns:
                JSON response indicating success or failure
            """
            try:
                # Verify role exists
                role = self.role_manager.load_role(role_name)
                if not role:
                    return jsonify({
                        'success': False,
                        'message': f'Role "{role_name}" not found'
                    }), 404

                # Verify resource exists
                if not self.resource_manager.resource_exists(resource_name):
                    return jsonify({
                        'success': False,
                        'message': f'Resource "{resource_name}" not found'
                    }), 404

                data = request.get_json() or {}

                # Create permission object
                permission = Permission(
                    create=data.get('create', False),
                    read=data.get('read', True),  # Default read to true
                    update=data.get('update', False),
                    delete=data.get('delete', False),
                    execute=data.get('execute', False)
                )

                # Assign resource to role
                if self.role_manager.assign_resource_to_role(role_name, resource_name, permission):
                    logger.info(
                        f"Admin {session.get('userid')} assigned resource '{resource_name}' to role '{role_name}'")
                    return jsonify({
                        'success': True,
                        'message': f'Resource "{resource_name}" assigned to role "{role_name}"',
                        'permission': self._permission_to_dict(permission)
                    }), 200
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to assign resource to role'
                    }), 500

            except Exception as e:
                logger.error(f"Error assigning resource to role: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error assigning resource: {str(e)}'
                }), 500

        # ==================== Remove Resource from Role (Admin Only) ====================

        @self.app.route('/api/admin/roles/<role_name>/resources/<resource_name>', methods=['DELETE'])
        @admin_required
        def remove_resource_from_role(role_name, resource_name):
            """
            Remove a resource from a role.

            Args:
                role_name: Name of the role
                resource_name: Name of the resource

            Returns:
                JSON response indicating success or failure
            """
            try:
                # Verify role exists
                if not self.role_manager.role_exists(role_name):
                    return jsonify({
                        'success': False,
                        'message': f'Role "{role_name}" not found'
                    }), 404

                # Remove resource from role
                if self.role_manager.remove_resource_from_role(role_name, resource_name):
                    logger.info(
                        f"Admin {session.get('userid')} removed resource '{resource_name}' from role '{role_name}'")
                    return jsonify({
                        'success': True,
                        'message': f'Resource "{resource_name}" removed from role "{role_name}"'
                    }), 200
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to remove resource from role'
                    }), 500

            except Exception as e:
                logger.error(f"Error removing resource from role: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error removing resource: {str(e)}'
                }), 500

        # ==================== Get Role Permissions for Resource (All Logged-in Users) ====================

        @self.app.route('/api/roles/<role_name>/resources/<resource_name>/permissions', methods=['GET'])
        @login_required
        def get_role_resource_permissions(role_name, resource_name):
            """
            Get the permissions a role has for a specific resource.

            Args:
                role_name: Name of the role
                resource_name: Name of the resource

            Returns:
                JSON response with permissions
            """
            try:
                permission = self.role_manager.get_permission(role_name, resource_name)

                if not permission:
                    return jsonify({
                        'success': False,
                        'message': f'No permissions found for role "{role_name}" on resource "{resource_name}"'
                    }), 404

                return jsonify({
                    'success': True,
                    'role': role_name,
                    'resource': resource_name,
                    'permissions': self._permission_to_dict(permission)
                }), 200

            except Exception as e:
                logger.error(f"Error getting permissions: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error getting permissions: {str(e)}'
                }), 500

        # ==================== Batch Assign Resources (Admin Only) ====================

        @self.app.route('/api/admin/roles/<role_name>/resources/batch', methods=['POST'])
        @admin_required
        def batch_assign_resources(role_name):
            """
            Assign multiple resources to a role.

            Args:
                role_name: Name of the role

            Request Body:
                {
                    "resources": {
                        "resource1": {
                            "create": true,
                            "read": true,
                            "update": false,
                            "delete": false,
                            "execute": false
                        },
                        "resource2": {...}
                    }
                }

            Returns:
                JSON response with batch operation results
            """
            try:
                # Verify role exists
                if not self.role_manager.role_exists(role_name):
                    return jsonify({
                        'success': False,
                        'message': f'Role "{role_name}" not found'
                    }), 404

                data = request.get_json()

                if not data or 'resources' not in data:
                    return jsonify({
                        'success': False,
                        'message': 'resources is required'
                    }), 400

                results = {}
                success_count = 0

                for resource_name, perms in data['resources'].items():
                    # Verify resource exists
                    if not self.resource_manager.resource_exists(resource_name):
                        results[resource_name] = {'success': False, 'message': 'Resource not found'}
                        continue

                    permission = Permission(
                        create=perms.get('create', False),
                        read=perms.get('read', True),
                        update=perms.get('update', False),
                        delete=perms.get('delete', False),
                        execute=perms.get('execute', False)
                    )

                    if self.role_manager.assign_resource_to_role(role_name, resource_name, permission):
                        results[resource_name] = {'success': True}
                        success_count += 1
                    else:
                        results[resource_name] = {'success': False, 'message': 'Assignment failed'}

                logger.info(
                    f"Admin {session.get('userid')} batch assigned {success_count} resources to role '{role_name}'")

                return jsonify({
                    'success': True,
                    'message': f'{success_count} resource(s) assigned',
                    'results': results
                }), 200

            except Exception as e:
                logger.error(f"Error in batch assign operation: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error in batch operation: {str(e)}'
                }), 500

        # ==================== Get Role Statistics (All Logged-in Users) ====================

        @self.app.route('/api/roles/statistics', methods=['GET'])
        @login_required
        def get_role_statistics():
            """
            Get statistics about roles.

            Returns:
                JSON response with role statistics
            """
            try:
                stats = self.role_manager.get_role_statistics()

                return jsonify({
                    'success': True,
                    'statistics': stats
                }), 200

            except Exception as e:
                logger.error(f"Error getting role statistics: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error getting statistics: {str(e)}'
                }), 500

        logger.info("Role API routes registered")

    # ==================== Helper Methods ====================

    def _role_to_dict(self, role: Role, include_resources: bool = False) -> Dict[str, Any]:
        """
        Convert a Role object to a dictionary.

        Args:
            role: Role object to convert
            include_resources: Whether to include detailed resource permissions

        Returns:
            Dictionary representation of the role
        """
        # Handle created_at - could be datetime object or string from database
        created_at_str = None
        if role.created_at:
            if hasattr(role.created_at, 'isoformat'):
                # It's a datetime object
                created_at_str = role.created_at.isoformat()
            elif isinstance(role.created_at, str):
                # It's already a string
                created_at_str = role.created_at

        result = {
            'name': role.name,
            'description': role.description,
            'enabled': role.enabled,
            'created_at': created_at_str,
            'metadata': role.metadata,
            'resource_count': len(role.resources)
        }

        if include_resources:
            result['resources'] = {
                resource_name: self._permission_to_dict(permission)
                for resource_name, permission in role.resources.items()
            }
        else:
            result['resource_names'] = list(role.resources.keys())

        return result

    def _permission_to_dict(self, permission: Permission) -> Dict[str, bool]:
        """
        Convert a Permission object to a dictionary.

        Args:
            permission: Permission object to convert

        Returns:
            Dictionary representation of the permission
        """
        return {
            'create': permission.create,
            'read': permission.read,
            'update': permission.update,
            'delete': permission.delete,
            'execute': permission.execute
        }