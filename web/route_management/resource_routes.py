"""
Resource Routes Module - Handles resource management API endpoints

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
from user_management.user import Resource
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ResourceRoutes(AbstractRoutes):
    """
    Handles resource-related API routes for the application.

    This class manages all resource operations including:
    - Listing resources (all users)
    - Viewing resource details (all users)
    - Creating resources (admin only)
    - Updating resources (admin only)
    - Deleting resources (admin only)
    - Assigning resources to roles (admin only)
    - Removing resources from roles (admin only)
    - Batch operations (admin only)

    Attributes:
        app: Flask application instance
        resource_manager: ResourceManager instance for database operations
    """

    def __init__(self, app):
        """
        Initialize ResourceRoutes.

        Args:
            app: Flask application instance
        """
        super().__init__(app)
        logger.info("ResourceRoutes initialized")

    def register_routes(self):
        """Register all resource-related API routes."""

        # ==================== List Resources (All Logged-in Users) ====================
        @self.app.route('/admin/resources')
        @admin_required
        def manage_resources():
            """Manage resources page with pagination."""
            from flask import request

            # Get pagination parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', '10')
            resource_type = request.args.get('type', None)

            # Get all resources
            all_resources = self.user_manager.list_resources(resource_type=resource_type)
            total_resources = len(all_resources)

            # Handle pagination
            if per_page == 'all':
                paginated_resources = all_resources
                total_pages = 1
                page = 1
            else:
                per_page = int(per_page)
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                paginated_resources = all_resources[start_idx:end_idx]
                total_pages = (total_resources + per_page - 1) // per_page

            # Get unique resource types for filter
            all_resources_for_types = self.user_manager.list_resources()
            resource_types = list(set([r.resource_type for r in all_resources_for_types]))

            return render_template('manage_resources.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('userid'),
                                   roles=session.get('roles', []),
                                   resource_list=paginated_resources,
                                   total_resources=total_resources,
                                   current_page=page,
                                   total_pages=total_pages,
                                   per_page=str(per_page),
                                   resource_types=resource_types,
                                   selected_type=resource_type)

        @self.app.route('/admin/resources/create')
        @admin_required
        def admin_create_resource():
            """Create new resource page."""
            return render_template('create_resource.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('userid'),
                                   roles=session.get('roles', []))

        @self.app.route('/admin/resources/edit/<resource_name>')
        @admin_required
        def edit_resource(resource_name):
            """Edit existing resource page."""
            # Load the resource
            resource = self.user_manager.load_resource(resource_name)

            if not resource:
                flash(f'Resource "{resource_name}" not found', 'error')
                return redirect(url_for('manage_resources'))

            # Get roles that have this resource
            roles_with_resource = self.user_manager.get_roles_with_resource(resource_name)

            return render_template('edit_resource.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('userid'),
                                   roles=session.get('roles', []),
                                   resource=resource,
                                   roles_with_resource=roles_with_resource)

        @self.app.route('/admin/resources/assign')
        @admin_required
        def admin_assign_resource_to_role():
            """Assign resource to role page."""
            # Get all roles and resources
            all_roles = self.user_manager.list_roles()
            all_resources = self.user_manager.list_resources()

            return render_template('assign_resource.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('userid'),
                                   roles=session.get('roles', []),
                                   all_roles=all_roles,
                                   all_resources=all_resources)

        @self.app.route('/api/resources', methods=['GET'])
        @login_required
        def list_resources():
            """
            List all resources with optional filtering.

            Query Parameters:
                - type: Filter by resource type
                - enabled: Filter by enabled status (true/false)
                - search: Search by name or description
                - page: Page number (default: 1)
                - per_page: Items per page (default: 10)

            Returns:
                JSON response with list of resources
            """
            try:
                # Get query parameters
                resource_type = request.args.get('type', None)
                enabled_filter = request.args.get('enabled', None)
                search_query = request.args.get('search', '').strip()
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 10, type=int)

                # Get resources from database
                if resource_type:
                    resources = self.resource_manager.list_resources(resource_type=resource_type)
                else:
                    resources = self.resource_manager.list_resources()

                # Apply enabled filter
                if enabled_filter is not None:
                    is_enabled = enabled_filter.lower() == 'true'
                    resources = [r for r in resources if r.enabled == is_enabled]

                # Apply search filter
                if search_query:
                    search_lower = search_query.lower()
                    resources = [
                        r for r in resources
                        if search_lower in r.name.lower() or
                           (r.description and search_lower in r.description.lower())
                    ]

                # Pagination
                total_resources = len(resources)
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                paginated_resources = resources[start_idx:end_idx]

                # Convert to dict
                resources_data = [self._resource_to_dict(r) for r in paginated_resources]

                return jsonify({
                    'success': True,
                    'resources': resources_data,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total_resources,
                        'total_pages': (total_resources + per_page - 1) // per_page
                    }
                }), 200

            except Exception as e:
                logger.error(f"Error listing resources: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error listing resources: {str(e)}'
                }), 500

        # ==================== Get Resource Details (All Logged-in Users) ====================

        @self.app.route('/api/resources/<resource_name>', methods=['GET'])
        @login_required
        def get_resource(resource_name):
            """
            Get detailed information about a specific resource.

            Args:
                resource_name: Name of the resource

            Returns:
                JSON response with resource details
            """
            try:
                resource = self.resource_manager.load_resource(resource_name)

                if not resource:
                    return jsonify({
                        'success': False,
                        'message': f'Resource "{resource_name}" not found'
                    }), 404

                # Get roles using this resource
                roles_with_resource = self.resource_manager.get_roles_with_resource(resource_name)

                resource_data = self._resource_to_dict(resource)
                resource_data['roles'] = roles_with_resource

                return jsonify({
                    'success': True,
                    'resource': resource_data
                }), 200

            except Exception as e:
                logger.error(f"Error getting resource {resource_name}: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error getting resource: {str(e)}'
                }), 500

        # ==================== Create Resource (Admin Only) ====================

        @self.app.route('/api/admin/resources', methods=['POST'])
        @admin_required
        def create_resource():
            """
            Create a new resource.

            Request Body:
                {
                    "name": "resource_name",
                    "resource_type": "api",
                    "description": "Resource description",
                    "enabled": true,
                    "metadata": {}
                }

            Returns:
                JSON response with created resource
            """
            try:
                data = request.get_json()

                # Validate required fields
                if not data or 'name' not in data:
                    return jsonify({
                        'success': False,
                        'message': 'Resource name is required'
                    }), 400

                resource_name = data['name'].strip()

                # Validate resource name format
                if not resource_name or not resource_name.replace('_', '').isalnum():
                    return jsonify({
                        'success': False,
                        'message': 'Resource name must contain only letters, numbers, and underscores'
                    }), 400

                # Check if resource already exists
                if self.resource_manager.resource_exists(resource_name):
                    return jsonify({
                        'success': False,
                        'message': f'Resource "{resource_name}" already exists'
                    }), 409

                # Validate resource type
                if 'resource_type' not in data or not data['resource_type'].strip():
                    return jsonify({
                        'success': False,
                        'message': 'Resource type is required'
                    }), 400

                # Create resource object
                resource = Resource(
                    name=resource_name,
                    resource_type=data['resource_type'].strip(),
                    description=data.get('description', '').strip(),
                    enabled=data.get('enabled', True),
                    created_at=datetime.now(),
                    metadata=data.get('metadata', {})
                )

                # Save to database
                if self.resource_manager.save_resource(resource):
                    logger.info(f"Admin {session.get('userid')} created resource '{resource_name}'")
                    return jsonify({
                        'success': True,
                        'message': f'Resource "{resource_name}" created successfully',
                        'resource': self._resource_to_dict(resource)
                    }), 201
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to create resource'
                    }), 500

            except Exception as e:
                logger.error(f"Error creating resource: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error creating resource: {str(e)}'
                }), 500

        # ==================== Update Resource (Admin Only) ====================

        @self.app.route('/api/admin/resources/<resource_name>', methods=['PUT'])
        @admin_required
        def update_resource(resource_name):
            """
            Update an existing resource.

            Args:
                resource_name: Name of the resource to update

            Request Body:
                {
                    "resource_type": "api",
                    "description": "Updated description",
                    "enabled": true,
                    "metadata": {}
                }

            Returns:
                JSON response with updated resource
            """
            try:
                # Load existing resource
                resource = self.resource_manager.load_resource(resource_name)

                if not resource:
                    return jsonify({
                        'success': False,
                        'message': f'Resource "{resource_name}" not found'
                    }), 404

                data = request.get_json()

                # Update fields
                if 'resource_type' in data:
                    resource.resource_type = data['resource_type'].strip()

                if 'description' in data:
                    resource.description = data['description'].strip()

                if 'enabled' in data:
                    resource.enabled = bool(data['enabled'])

                if 'metadata' in data:
                    resource.metadata = data['metadata']

                # Save to database
                if self.resource_manager.save_resource(resource):
                    logger.info(f"Admin {session.get('userid')} updated resource '{resource_name}'")
                    return jsonify({
                        'success': True,
                        'message': f'Resource "{resource_name}" updated successfully',
                        'resource': self._resource_to_dict(resource)
                    }), 200
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to update resource'
                    }), 500

            except Exception as e:
                logger.error(f"Error updating resource {resource_name}: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error updating resource: {str(e)}'
                }), 500

        # ==================== Delete Resource (Admin Only) ====================

        @self.app.route('/api/admin/resources/<resource_name>', methods=['DELETE'])
        @admin_required
        def delete_resource(resource_name):
            """
            Delete a resource.

            Args:
                resource_name: Name of the resource to delete

            Returns:
                JSON response indicating success or failure
            """
            try:
                # Check if resource exists
                if not self.resource_manager.resource_exists(resource_name):
                    return jsonify({
                        'success': False,
                        'message': f'Resource "{resource_name}" not found'
                    }), 404

                # Check if resource is being used by any roles
                roles_using_resource = self.resource_manager.get_roles_with_resource(resource_name)

                if roles_using_resource and not request.args.get('force', 'false').lower() == 'true':
                    return jsonify({
                        'success': False,
                        'message': f'Resource "{resource_name}" is being used by {len(roles_using_resource)} role(s). Use force=true to delete anyway.',
                        'roles': roles_using_resource
                    }), 409

                # Delete resource
                if self.resource_manager.delete_resource(resource_name):
                    logger.info(f"Admin {session.get('userid')} deleted resource '{resource_name}'")
                    return jsonify({
                        'success': True,
                        'message': f'Resource "{resource_name}" deleted successfully'
                    }), 200
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to delete resource'
                    }), 500

            except Exception as e:
                logger.error(f"Error deleting resource {resource_name}: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error deleting resource: {str(e)}'
                }), 500

        # ==================== Get Resource Statistics (All Logged-in Users) ====================

        @self.app.route('/api/resources/statistics', methods=['GET'])
        @login_required
        def get_resource_statistics():
            """
            Get statistics about resources.

            Returns:
                JSON response with resource statistics
            """
            try:
                stats = self.resource_manager.get_resource_statistics()

                return jsonify({
                    'success': True,
                    'statistics': stats
                }), 200

            except Exception as e:
                logger.error(f"Error getting resource statistics: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error getting statistics: {str(e)}'
                }), 500

        # ==================== Get Resource Types (All Logged-in Users) ====================

        @self.app.route('/api/resources/types', methods=['GET'])
        @login_required
        def get_resource_types():
            """
            Get list of all resource types.

            Returns:
                JSON response with resource types
            """
            try:
                types = self.resource_manager.get_resource_types()

                return jsonify({
                    'success': True,
                    'types': types
                }), 200

            except Exception as e:
                logger.error(f"Error getting resource types: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error getting types: {str(e)}'
                }), 500

        # ==================== Batch Operations (Admin Only) ====================

        @self.app.route('/api/admin/resources/batch/enable', methods=['POST'])
        @admin_required
        def batch_enable_resources():
            """
            Enable or disable multiple resources.

            Request Body:
                {
                    "resource_names": ["resource1", "resource2"],
                    "enabled": true
                }

            Returns:
                JSON response with batch operation results
            """
            try:
                data = request.get_json()

                if not data or 'resource_names' not in data:
                    return jsonify({
                        'success': False,
                        'message': 'resource_names is required'
                    }), 400

                resource_names = data['resource_names']
                enabled = data.get('enabled', True)

                updated_count = self.resource_manager.enable_resources_batch(resource_names, enabled)

                action = 'enabled' if enabled else 'disabled'
                logger.info(f"Admin {session.get('userid')} {action} {updated_count} resources")

                return jsonify({
                    'success': True,
                    'message': f'{updated_count} resource(s) {action}',
                    'updated_count': updated_count
                }), 200

            except Exception as e:
                logger.error(f"Error in batch enable operation: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error in batch operation: {str(e)}'
                }), 500

        @self.app.route('/api/admin/resources/batch/delete', methods=['POST'])
        @admin_required
        def batch_delete_resources():
            """
            Delete multiple resources.

            Request Body:
                {
                    "resource_names": ["resource1", "resource2"]
                }

            Returns:
                JSON response with batch operation results
            """
            try:
                data = request.get_json()

                if not data or 'resource_names' not in data:
                    return jsonify({
                        'success': False,
                        'message': 'resource_names is required'
                    }), 400

                resource_names = data['resource_names']
                results = self.resource_manager.delete_resources_batch(resource_names)

                success_count = sum(1 for success in results.values() if success)

                logger.info(f"Admin {session.get('userid')} deleted {success_count} resources in batch")

                return jsonify({
                    'success': True,
                    'message': f'{success_count} resource(s) deleted',
                    'results': results
                }), 200

            except Exception as e:
                logger.error(f"Error in batch delete operation: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error in batch operation: {str(e)}'
                }), 500

        logger.info("Resource API routes registered")

    # ==================== Helper Methods ====================

    def _resource_to_dict(self, resource: Resource) -> Dict[str, Any]:
        """
        Convert a Resource object to a dictionary.

        Args:
            resource: Resource object to convert

        Returns:
            Dictionary representation of the resource
        """
        return {
            'name': resource.name,
            'resource_type': resource.resource_type,
            'description': resource.description,
            'enabled': resource.enabled,
            'created_at': resource.created_at.isoformat() if resource.created_at else None,
            'metadata': resource.metadata
        }