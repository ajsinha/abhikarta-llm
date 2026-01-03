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

from flask import render_template, request, redirect, url_for, session, flash, jsonify
import logging
import json
import secrets
import string

from .abstract_routes import AbstractRoutes, admin_required, login_required

logger = logging.getLogger(__name__)


class AdminRoutes(AbstractRoutes):
    """
    Handles admin-specific routes for the application.
    
    This class manages routes that are only accessible to users with admin role.
    
    Attributes:
        app: Flask application instance
        user_facade: UserFacade instance for user operations
        db_facade: DatabaseFacade instance for database operations
    """
    
    def __init__(self, app):
        """
        Initialize AdminRoutes.
        
        Args:
            app: Flask application instance
        """
        super().__init__(app)
        logger.info("AdminRoutes initialized")
    
    def register_routes(self):
        """Register all admin routes."""
        
        @self.app.route('/admin/dashboard')
        @admin_required
        def admin_dashboard():
            """Admin dashboard with management cards."""
            # Get user statistics
            stats = self.user_facade.get_statistics()
            
            # Get agent count using delegate
            agent_count = 0
            try:
                agent_count = self.db_facade.agents.get_agents_count()
            except Exception as e:
                logger.error(f"Error getting agent count: {e}", exc_info=True)
            
            # Get execution count using delegate
            execution_count = 0
            try:
                execution_count = self.db_facade.executions.get_executions_count()
            except Exception as e:
                logger.error(f"Error getting execution count: {e}", exc_info=True)
            
            # Get MCP plugin count using delegate
            mcp_count = 0
            try:
                mcp_count = self.db_facade.mcp.get_plugins_count()
            except Exception as e:
                logger.error(f"Error getting MCP plugin count: {e}", exc_info=True)
            
            # Get recent audit logs using delegate
            audit_logs = []
            try:
                audit_logs = self.db_facade.audit.get_recent_logs(limit=10)
            except Exception as e:
                logger.error(f"Error getting audit logs: {e}", exc_info=True)
            
            return render_template('admin/dashboard.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   stats=stats,
                                   agent_count=agent_count,
                                   execution_count=execution_count,
                                   mcp_count=mcp_count,
                                   audit_logs=audit_logs)
        
        @self.app.route('/admin/users')
        @admin_required
        def manage_users():
            """Manage users page."""
            # Get all users
            users = self.user_facade.list_users()
            
            # Get available roles
            available_roles = [
                'super_admin', 'domain_admin', 'agent_developer',
                'agent_publisher', 'hitl_reviewer', 'agent_user', 'viewer'
            ]
            
            # Calculate user statistics
            total_users = len(users)
            active_users = sum(1 for u in users if u.get('is_active', True))
            admin_count = sum(1 for u in users if 'super_admin' in u.get('roles', []) or 'domain_admin' in u.get('roles', []))
            
            user_stats = {
                'total': total_users,
                'active': active_users,
                'admins': admin_count,
                'roles_count': len(available_roles)
            }
            
            return render_template('admin/users.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   users=users,
                                   available_roles=available_roles,
                                   user_stats=user_stats)
        
        @self.app.route('/admin/users/add', methods=['GET', 'POST'])
        @admin_required
        def add_user():
            """Add new user."""
            available_roles = [
                'super_admin', 'domain_admin', 'agent_developer',
                'agent_publisher', 'hitl_reviewer', 'agent_user', 'viewer'
            ]
            
            if request.method == 'POST':
                user_id = request.form.get('user_id', '').strip()
                password = request.form.get('password', '')
                fullname = request.form.get('fullname', '').strip()
                email = request.form.get('email', '').strip()
                selected_roles = request.form.getlist('roles')
                
                if not user_id or not password or not fullname:
                    flash('User ID, password, and full name are required', 'error')
                    return render_template('admin/add_user.html',
                                           fullname=session.get('fullname'),
                                           userid=session.get('user_id'),
                                           roles=session.get('roles', []),
                                           available_roles=available_roles)
                
                user_data = {
                    'user_id': user_id,
                    'password': password,
                    'fullname': fullname,
                    'email': email,
                    'roles': selected_roles,
                    'is_active': True
                }
                
                if self.user_facade.create_user(user_data):
                    self.log_audit('create_user', 'user', user_id)
                    flash(f'User "{user_id}" created successfully', 'success')
                    return redirect(url_for('manage_users'))
                else:
                    flash(f'User "{user_id}" already exists', 'error')
            
            return render_template('admin/add_user.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   available_roles=available_roles)
        
        @self.app.route('/admin/users/<user_id>/edit', methods=['GET', 'POST'])
        @admin_required
        def edit_user(user_id):
            """Edit existing user."""
            user = self.user_facade.get_user(user_id)
            
            if not user:
                flash(f'User "{user_id}" not found', 'error')
                return redirect(url_for('manage_users'))
            
            available_roles = [
                'super_admin', 'domain_admin', 'agent_developer',
                'agent_publisher', 'hitl_reviewer', 'agent_user', 'viewer'
            ]
            
            if request.method == 'POST':
                fullname = request.form.get('fullname', '').strip()
                email = request.form.get('email', '').strip()
                selected_roles = request.form.getlist('roles')
                is_active = request.form.get('is_active') == 'on'
                
                update_data = {
                    'fullname': fullname,
                    'email': email,
                    'roles': selected_roles,
                    'is_active': is_active
                }
                
                # Check if password is being changed
                new_password = request.form.get('new_password', '')
                if new_password:
                    update_data['password'] = new_password
                
                if self.user_facade.update_user(user_id, update_data):
                    self.log_audit('update_user', 'user', user_id)
                    flash(f'User "{user_id}" updated successfully', 'success')
                    return redirect(url_for('manage_users'))
                else:
                    flash('Failed to update user', 'error')
            
            return render_template('admin/edit_user.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   user=user,
                                   available_roles=available_roles)
        
        @self.app.route('/admin/users/<user_id>/view')
        @admin_required
        def view_user(user_id):
            """View user details."""
            user = self.user_facade.get_user(user_id)
            
            if not user:
                flash(f'User "{user_id}" not found', 'error')
                return redirect(url_for('manage_users'))
            
            # Get recent activity for this user
            recent_activity = []
            try:
                logs = self.db_facade.execute_query(
                    "SELECT * FROM audit_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT 20",
                    (user_id,)
                )
                recent_activity = logs if logs else []
            except Exception as e:
                logger.warning(f"Could not fetch user activity: {e}")
            
            return render_template('admin/view_user.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   user=user,
                                   recent_activity=recent_activity)
        
        @self.app.route('/admin/users/<user_id>/delete', methods=['POST'])
        @admin_required
        def delete_user(user_id):
            """Delete (deactivate) a user."""
            if user_id == session.get('user_id'):
                flash('You cannot delete your own account', 'error')
                return redirect(url_for('manage_users'))
            
            if self.user_facade.delete_user(user_id):
                self.log_audit('delete_user', 'user', user_id)
                flash(f'User "{user_id}" has been deactivated', 'success')
            else:
                flash(f'User "{user_id}" not found', 'error')
            
            return redirect(url_for('manage_users'))
        
        @self.app.route('/admin/settings')
        @admin_required
        def admin_settings():
            """Admin settings page."""
            settings = self.app.config.get('SETTINGS')
            
            return render_template('admin/settings.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   db_type=settings.database.type if settings else 'unknown',
                                   app_version=settings.app_version if settings else 'unknown')
        
        @self.app.route('/admin/audit-logs')
        @admin_required
        def audit_logs():
            """View audit logs."""
            page = request.args.get('page', 1, type=int)
            per_page = 50
            offset = (page - 1) * per_page
            
            # Get total count using delegate
            try:
                total_count = self.db_facade.audit.get_audit_logs_count()
            except:
                total_count = 0
            
            # Get logs using delegate
            logs = []
            try:
                logs = self.db_facade.audit.get_audit_logs(limit=per_page, offset=offset)
            except Exception as e:
                logger.error(f"Error getting audit logs: {e}", exc_info=True)
            
            total_pages = (total_count + per_page - 1) // per_page
            
            return render_template('admin/audit_logs.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   logs=logs,
                                   page=page,
                                   total_pages=total_pages,
                                   total_count=total_count)
        
        # ============================================
        # USER UPDATE FROM MODAL
        # ============================================
        
        @self.app.route('/admin/users/update', methods=['POST'])
        @admin_required
        def update_user():
            """Update user from modal form."""
            user_id = request.form.get('user_id')
            fullname = request.form.get('fullname', '').strip()
            email = request.form.get('email', '').strip()
            selected_roles = request.form.getlist('roles')
            is_active = 'is_active' in request.form
            
            update_data = {
                'fullname': fullname,
                'email': email,
                'roles': selected_roles,
                'is_active': is_active
            }
            
            if self.user_facade.update_user(user_id, update_data):
                self.log_audit('update_user', 'user', user_id)
                flash(f'User "{user_id}" updated successfully', 'success')
            else:
                flash('Failed to update user', 'error')
            
            return redirect(url_for('manage_users'))
        
        # ============================================
        # API ENDPOINTS FOR USER MANAGEMENT
        # ============================================
        
        @self.app.route('/api/users/<user_id>')
        @admin_required
        def api_get_user(user_id):
            """API: Get user details."""
            user = self.user_facade.get_user(user_id)
            if user:
                return jsonify({
                    'user_id': user.get('user_id'),
                    'fullname': user.get('fullname'),
                    'email': user.get('email'),
                    'roles': user.get('roles', []),
                    'is_active': user.get('is_active', True),
                    'created_at': user.get('created_at')
                })
            return jsonify({'error': 'User not found'}), 404
        
        @self.app.route('/api/users/<user_id>/reset-password', methods=['POST'])
        @admin_required
        def api_reset_password(user_id):
            """API: Reset user password."""
            user = self.user_facade.get_user(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Generate new password
            alphabet = string.ascii_letters + string.digits
            new_password = ''.join(secrets.choice(alphabet) for _ in range(12))
            
            if self.user_facade.update_user(user_id, {'password': new_password}):
                self.log_audit('reset_password', 'user', user_id)
                return jsonify({
                    'success': True,
                    'new_password': new_password
                })
            
            return jsonify({'error': 'Failed to reset password'}), 500
        
        @self.app.route('/api/users/<user_id>/toggle-status', methods=['POST'])
        @admin_required
        def api_toggle_user_status(user_id):
            """API: Toggle user active status."""
            if user_id == session.get('user_id'):
                return jsonify({'error': 'Cannot modify your own status'}), 400
            
            user = self.user_facade.get_user(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            new_status = not user.get('is_active', True)
            
            if self.user_facade.update_user(user_id, {'is_active': new_status}):
                self.log_audit('toggle_status', 'user', user_id, {'is_active': new_status})
                return jsonify({
                    'success': True,
                    'is_active': new_status
                })
            
            return jsonify({'error': 'Failed to update status'}), 500
        
        # ============================================
        # API KEY MANAGEMENT
        # ============================================
        
        @self.app.route('/admin/api-keys')
        @admin_required
        def admin_api_keys():
            """Display API keys management page."""
            api_keys = []
            users_dict = {}
            
            try:
                # Get all API keys
                result = self.db_facade.fetch_all(
                    "SELECT * FROM api_keys ORDER BY created_at DESC"
                )
                api_keys = result if result else []
                
                # Get users for display
                users = self.user_facade.get_all_users()
                users_dict = {u['user_id']: u for u in users}
                
            except Exception as e:
                logger.error(f"Error getting API keys: {e}", exc_info=True)
            
            return render_template('admin/api_keys.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   api_keys=api_keys,
                                   users=users_dict)
        
        @self.app.route('/admin/api-keys/create', methods=['GET', 'POST'])
        @admin_required
        def create_api_key():
            """Create a new API key."""
            import secrets
            import hashlib
            import uuid
            
            if request.method == 'POST':
                name = request.form.get('name', '').strip()
                description = request.form.get('description', '').strip()
                user_id = request.form.get('user_id', '').strip()
                expires_days = int(request.form.get('expires_days', 365))
                rate_limit = int(request.form.get('rate_limit', 1000))
                
                if not name or not user_id:
                    flash('Name and User are required', 'error')
                    return redirect(url_for('create_api_key'))
                
                # Generate API key
                raw_key = f"abk_{secrets.token_urlsafe(32)}"
                key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
                key_id = str(uuid.uuid4())
                
                # Calculate expiration
                from datetime import datetime, timedelta
                expires_at = datetime.now() + timedelta(days=expires_days)
                
                try:
                    self.db_facade.execute(
                        """INSERT INTO api_keys 
                           (key_id, user_id, key_hash, name, description, rate_limit, expires_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (key_id, user_id, key_hash, name, description, rate_limit, expires_at)
                    )
                    
                    self.log_audit('create_api_key', 'api_key', key_id, {'user_id': user_id, 'name': name})
                    
                    # Show the key once - it won't be shown again
                    flash(f'API Key created successfully! Save this key - it will not be shown again: {raw_key}', 'success')
                    return redirect(url_for('admin_api_keys'))
                    
                except Exception as e:
                    logger.error(f"Error creating API key: {e}", exc_info=True)
                    flash('Error creating API key', 'error')
            
            # Get users for dropdown
            users = self.user_facade.get_all_users()
            
            return render_template('admin/create_api_key.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   users=users)
        
        @self.app.route('/admin/api-keys/<key_id>/revoke', methods=['POST'])
        @admin_required
        def revoke_api_key(key_id):
            """Revoke an API key."""
            try:
                self.db_facade.execute(
                    "UPDATE api_keys SET is_active = 0 WHERE key_id = ?",
                    (key_id,)
                )
                self.log_audit('revoke_api_key', 'api_key', key_id)
                flash('API key revoked successfully', 'success')
            except Exception as e:
                logger.error(f"Error revoking API key: {e}", exc_info=True)
                flash('Error revoking API key', 'error')
            
            return redirect(url_for('admin_api_keys'))
        
        @self.app.route('/admin/api-keys/<key_id>/delete', methods=['POST'])
        @admin_required
        def delete_api_key(key_id):
            """Delete an API key."""
            try:
                self.db_facade.execute(
                    "DELETE FROM api_keys WHERE key_id = ?",
                    (key_id,)
                )
                self.log_audit('delete_api_key', 'api_key', key_id)
                flash('API key deleted successfully', 'success')
            except Exception as e:
                logger.error(f"Error deleting API key: {e}", exc_info=True)
                flash('Error deleting API key', 'error')
            
            return redirect(url_for('admin_api_keys'))
        
        # ============================================
        # CODE FRAGMENTS MANAGEMENT
        # ============================================
        
        @self.app.route('/admin/code-fragments')
        @admin_required
        def admin_code_fragments():
            """Display code fragments management page."""
            fragments = []
            categories = set()
            
            try:
                fragments = self.db_facade.code_fragments.get_all_fragments()
                
                # Extract unique categories
                for f in fragments:
                    if f.get('category'):
                        categories.add(f['category'])
                        
            except Exception as e:
                logger.error(f"Error getting code fragments: {e}", exc_info=True)
            
            return render_template('admin/code_fragments.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   fragments=fragments,
                                   categories=sorted(categories))
        
        @self.app.route('/admin/code-fragments/add', methods=['GET', 'POST'])
        @admin_required
        def add_code_fragment():
            """Add a new code fragment."""
            import uuid
            import json
            
            if request.method == 'POST':
                fragment_id = request.form.get('fragment_id', '').strip()
                name = request.form.get('name', '').strip()
                description = request.form.get('description', '').strip()
                language = request.form.get('language', 'python')
                code = request.form.get('code', '')
                category = request.form.get('category', 'general').strip()
                tags = request.form.get('tags', '').strip()
                dependencies = request.form.get('dependencies', '').strip()
                
                if not fragment_id or not name or not code:
                    flash('Fragment ID, Name, and Code are required', 'error')
                    return redirect(url_for('add_code_fragment'))
                
                # Parse tags and dependencies
                tags_list = [t.strip() for t in tags.split(',') if t.strip()] if tags else []
                deps_list = [d.strip() for d in dependencies.split(',') if d.strip()] if dependencies else []
                
                try:
                    result = self.db_facade.code_fragments.create_fragment(
                        name=name,
                        code=code,
                        created_by=session.get('user_id'),
                        description=description,
                        language=language,
                        category=category,
                        tags=json.dumps(tags_list),
                        dependencies=json.dumps(deps_list)
                    )
                    
                    if result:
                        self.log_audit('create_code_fragment', 'code_fragment', fragment_id)
                        flash(f'Code fragment "{name}" created successfully', 'success')
                        return redirect(url_for('admin_code_fragments'))
                    else:
                        flash('Error creating code fragment', 'error')
                    
                except Exception as e:
                    logger.error(f"Error creating code fragment: {e}", exc_info=True)
                    flash(f'Error creating code fragment: {str(e)}', 'error')
            
            return render_template('admin/add_code_fragment.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []))
        
        @self.app.route('/admin/code-fragments/<fragment_id>')
        @admin_required
        def view_code_fragment(fragment_id):
            """View a code fragment."""
            import json
            
            try:
                fragment = self.db_facade.code_fragments.get_fragment(fragment_id)
                
                if not fragment:
                    flash('Code fragment not found', 'error')
                    return redirect(url_for('admin_code_fragments'))
                
                # Parse JSON fields
                fragment['tags'] = json.loads(fragment.get('tags', '[]'))
                fragment['dependencies'] = json.loads(fragment.get('dependencies', '[]'))
                
                return render_template('admin/view_code_fragment.html',
                                       fullname=session.get('fullname'),
                                       userid=session.get('user_id'),
                                       roles=session.get('roles', []),
                                       fragment=fragment)
                
            except Exception as e:
                logger.error(f"Error viewing code fragment: {e}", exc_info=True)
                flash('Error loading code fragment', 'error')
                return redirect(url_for('admin_code_fragments'))
        
        @self.app.route('/admin/code-fragments/<fragment_id>/edit', methods=['GET', 'POST'])
        @admin_required
        def edit_code_fragment(fragment_id):
            """Edit a code fragment."""
            import json
            
            try:
                fragment = self.db_facade.code_fragments.get_fragment(fragment_id)
                
                if not fragment:
                    flash('Code fragment not found', 'error')
                    return redirect(url_for('admin_code_fragments'))
                
                if request.method == 'POST':
                    name = request.form.get('name', '').strip()
                    description = request.form.get('description', '').strip()
                    language = request.form.get('language', 'python')
                    code = request.form.get('code', '')
                    category = request.form.get('category', 'general').strip()
                    tags = request.form.get('tags', '').strip()
                    dependencies = request.form.get('dependencies', '').strip()
                    is_active = 1 if 'is_active' in request.form else 0
                    
                    if not name or not code:
                        flash('Name and Code are required', 'error')
                        return redirect(url_for('edit_code_fragment', fragment_id=fragment_id))
                    
                    # Parse tags and dependencies
                    tags_list = [t.strip() for t in tags.split(',') if t.strip()] if tags else []
                    deps_list = [d.strip() for d in dependencies.split(',') if d.strip()] if dependencies else []
                    
                    # Increment version
                    current_version = fragment.get('version', '1.0.0')
                    parts = current_version.split('.')
                    parts[-1] = str(int(parts[-1]) + 1)
                    new_version = '.'.join(parts)
                    
                    self.db_facade.code_fragments.update_fragment(
                        fragment_id,
                        updated_by=session.get('user_id'),
                        name=name,
                        description=description,
                        language=language,
                        code=code,
                        category=category,
                        tags=json.dumps(tags_list),
                        dependencies=json.dumps(deps_list),
                        is_active=is_active,
                        version=new_version
                    )
                    
                    self.log_audit('update_code_fragment', 'code_fragment', fragment_id)
                    flash(f'Code fragment updated to v{new_version}', 'success')
                    return redirect(url_for('admin_code_fragments'))
                
                # Parse JSON fields for display
                fragment['tags'] = ', '.join(json.loads(fragment.get('tags', '[]')))
                fragment['dependencies'] = ', '.join(json.loads(fragment.get('dependencies', '[]')))
                
                return render_template('admin/edit_code_fragment.html',
                                       fullname=session.get('fullname'),
                                       userid=session.get('user_id'),
                                       roles=session.get('roles', []),
                                       fragment=fragment)
                
            except Exception as e:
                logger.error(f"Error editing code fragment: {e}", exc_info=True)
                flash('Error updating code fragment', 'error')
                return redirect(url_for('admin_code_fragments'))
        
        @self.app.route('/admin/code-fragments/<fragment_id>/delete', methods=['POST'])
        @admin_required
        def delete_code_fragment(fragment_id):
            """Delete a code fragment."""
            try:
                # Check if it's a system fragment
                fragment = self.db_facade.code_fragments.get_fragment(fragment_id)
                
                if fragment and fragment.get('is_system'):
                    flash('Cannot delete system code fragments', 'error')
                    return redirect(url_for('admin_code_fragments'))
                
                self.db_facade.code_fragments.delete_fragment(fragment_id)
                
                self.log_audit('delete_code_fragment', 'code_fragment', fragment_id)
                flash('Code fragment deleted successfully', 'success')
                
            except Exception as e:
                logger.error(f"Error deleting code fragment: {e}", exc_info=True)
                flash('Error deleting code fragment', 'error')
            
            return redirect(url_for('admin_code_fragments'))
        
        @self.app.route('/admin/code-fragments/<fragment_id>/toggle', methods=['POST'])
        @admin_required
        def toggle_code_fragment(fragment_id):
            """Toggle code fragment active status."""
            try:
                fragment = self.db_facade.code_fragments.get_fragment(fragment_id)
                
                if not fragment:
                    return jsonify({'error': 'Fragment not found'}), 404
                
                if fragment.get('is_active'):
                    self.db_facade.code_fragments.deactivate_fragment(fragment_id)
                    new_status = 0
                else:
                    self.db_facade.code_fragments.activate_fragment(fragment_id)
                    new_status = 1
                
                self.log_audit('toggle_code_fragment', 'code_fragment', fragment_id, {'is_active': new_status})
                return jsonify({'success': True, 'is_active': new_status})
                
            except Exception as e:
                logger.error(f"Error toggling code fragment: {e}", exc_info=True)
                return jsonify({'error': str(e)}), 500
        
        # ============================================
        # LLM PROVIDERS MANAGEMENT
        # ============================================
        
        @self.app.route('/admin/llm-providers')
        @admin_required
        def admin_llm_providers():
            """Display LLM providers management page."""
            providers = []
            try:
                providers = self.db_facade.llm.get_all_providers()
            except Exception as e:
                logger.error(f"Error getting LLM providers: {e}", exc_info=True)
            
            return render_template('admin/llm_providers.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   providers=providers)
        
        @self.app.route('/admin/llm-providers/add', methods=['GET', 'POST'])
        @admin_required
        def add_llm_provider():
            """Add a new LLM provider."""
            if request.method == 'POST':
                provider_id = request.form.get('provider_id', '').strip().lower()
                name = request.form.get('name', '').strip()
                description = request.form.get('description', '').strip()
                provider_type = request.form.get('provider_type', '').strip()
                api_endpoint = request.form.get('api_endpoint', '').strip()
                api_key_name = request.form.get('api_key_name', '').strip()
                rate_limit_rpm = int(request.form.get('rate_limit_rpm', 60))
                rate_limit_tpm = int(request.form.get('rate_limit_tpm', 100000))
                is_active = 1 if 'is_active' in request.form else 0
                
                if not provider_id or not name or not provider_type:
                    flash('Provider ID, Name, and Type are required', 'error')
                    return redirect(url_for('add_llm_provider'))
                
                try:
                    result = self.db_facade.llm.create_provider(
                        provider_id=provider_id,
                        name=name,
                        provider_type=provider_type,
                        description=description,
                        api_endpoint=api_endpoint,
                        api_key_name=api_key_name,
                        rate_limit_rpm=rate_limit_rpm,
                        rate_limit_tpm=rate_limit_tpm,
                        is_active=is_active,
                        created_by=session.get('user_id')
                    )
                    if result:
                        self.log_audit('create_llm_provider', 'llm_provider', provider_id)
                        flash(f'LLM Provider "{name}" created successfully', 'success')
                        return redirect(url_for('admin_llm_providers'))
                    else:
                        flash('Error creating provider', 'error')
                except Exception as e:
                    logger.error(f"Error creating LLM provider: {e}", exc_info=True)
                    flash(f'Error creating provider: {str(e)}', 'error')
            
            return render_template('admin/add_llm_provider.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []))
        
        @self.app.route('/admin/llm-providers/<provider_id>/edit', methods=['GET', 'POST'])
        @admin_required
        def edit_llm_provider(provider_id):
            """Edit an LLM provider."""
            try:
                provider = self.db_facade.llm.get_provider(provider_id)
                if not provider:
                    flash('Provider not found', 'error')
                    return redirect(url_for('admin_llm_providers'))
                
                if request.method == 'POST':
                    name = request.form.get('name', '').strip()
                    description = request.form.get('description', '').strip()
                    api_endpoint = request.form.get('api_endpoint', '').strip()
                    api_key_name = request.form.get('api_key_name', '').strip()
                    rate_limit_rpm = int(request.form.get('rate_limit_rpm', 60))
                    rate_limit_tpm = int(request.form.get('rate_limit_tpm', 100000))
                    is_active = 1 if 'is_active' in request.form else 0
                    is_default = 1 if 'is_default' in request.form else 0
                    
                    # If setting as default, unset others
                    if is_default:
                        self.db_facade.execute("UPDATE llm_providers SET is_default = 0")
                    
                    self.db_facade.execute(
                        """UPDATE llm_providers SET name=?, description=?, api_endpoint=?,
                           api_key_name=?, rate_limit_rpm=?, rate_limit_tpm=?, is_active=?,
                           is_default=?, updated_at=CURRENT_TIMESTAMP
                           WHERE provider_id=?""",
                        (name, description, api_endpoint, api_key_name, rate_limit_rpm,
                         rate_limit_tpm, is_active, is_default, provider_id)
                    )
                    self.log_audit('update_llm_provider', 'llm_provider', provider_id)
                    flash('Provider updated successfully', 'success')
                    return redirect(url_for('admin_llm_providers'))
                
                return render_template('admin/edit_llm_provider.html',
                                       fullname=session.get('fullname'),
                                       userid=session.get('user_id'),
                                       roles=session.get('roles', []),
                                       provider=provider)
            except Exception as e:
                logger.error(f"Error editing LLM provider: {e}", exc_info=True)
                flash('Error updating provider', 'error')
                return redirect(url_for('admin_llm_providers'))
        
        @self.app.route('/admin/llm-providers/<provider_id>/delete', methods=['POST'])
        @admin_required
        def delete_llm_provider(provider_id):
            """Delete an LLM provider."""
            try:
                # Check if provider has models
                models = self.db_facade.llm.get_provider_models(provider_id)
                if models:
                    flash('Cannot delete provider with existing models. Delete models first.', 'error')
                    return redirect(url_for('admin_llm_providers'))
                
                self.db_facade.llm.delete_provider(provider_id)
                self.log_audit('delete_llm_provider', 'llm_provider', provider_id)
                flash('Provider deleted successfully', 'success')
            except Exception as e:
                logger.error(f"Error deleting LLM provider: {e}", exc_info=True)
                flash('Error deleting provider', 'error')
            
            return redirect(url_for('admin_llm_providers'))
        
        @self.app.route('/admin/llm-providers/<provider_id>/set-default', methods=['POST'])
        @admin_required
        def set_default_provider(provider_id):
            """Set a provider as the default."""
            try:
                # Unset all providers as default
                self.db_facade.execute("UPDATE llm_providers SET is_default = 0")
                # Set this provider as default
                self.db_facade.execute(
                    "UPDATE llm_providers SET is_default = 1 WHERE provider_id = ?",
                    (provider_id,)
                )
                self.log_audit('set_default_provider', 'llm_provider', provider_id)
                flash(f'Provider "{provider_id}" set as default', 'success')
            except Exception as e:
                logger.error(f"Error setting default provider: {e}", exc_info=True)
                flash('Error setting default provider', 'error')
            
            return redirect(url_for('admin_llm_providers'))
        
        @self.app.route('/admin/llm-providers/<provider_id>/toggle-status', methods=['POST'])
        @admin_required
        def toggle_provider_status(provider_id):
            """Toggle a provider's active status."""
            try:
                provider = self.db_facade.llm.get_provider(provider_id)
                if provider:
                    new_status = 0 if provider.get('is_active', 1) else 1
                    self.db_facade.execute(
                        "UPDATE llm_providers SET is_active = ? WHERE provider_id = ?",
                        (new_status, provider_id)
                    )
                    status_text = 'activated' if new_status else 'deactivated'
                    self.log_audit(f'toggle_provider_{status_text}', 'llm_provider', provider_id)
                    flash(f'Provider "{provider_id}" {status_text}', 'success')
            except Exception as e:
                logger.error(f"Error toggling provider status: {e}", exc_info=True)
                flash('Error toggling provider status', 'error')
            
            return redirect(url_for('admin_llm_providers'))
        
        # ============================================
        # LLM PROVIDERS & MODELS API (for Visual Designers)
        # ============================================
        
        @self.app.route('/api/llm/providers')
        @login_required
        def api_llm_providers():
            """Get all active LLM providers for dropdowns."""
            try:
                providers = self.db_facade.llm.get_all_providers(active_only=True)
                return jsonify({
                    'success': True,
                    'providers': [
                        {
                            'provider_id': p.get('provider_id'),
                            'name': p.get('name'),
                            'provider_type': p.get('provider_type'),
                            'description': p.get('description', ''),
                            'is_default': p.get('is_default', 0)
                        }
                        for p in providers
                    ]
                })
            except Exception as e:
                logger.error(f"Error getting LLM providers: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/llm/providers/<provider_id>/models')
        @login_required
        def api_llm_provider_models(provider_id):
            """Get all active models for a specific provider."""
            try:
                models = self.db_facade.llm.get_provider_models(provider_id, active_only=True)
                return jsonify({
                    'success': True,
                    'provider_id': provider_id,
                    'models': [
                        {
                            'model_id': m.get('model_id'),
                            'name': m.get('name'),
                            'display_name': m.get('display_name') or m.get('name'),
                            'model_type': m.get('model_type', 'chat'),
                            'context_window': m.get('context_window', 4096),
                            'supports_vision': m.get('supports_vision', 0),
                            'supports_functions': m.get('supports_functions', 0),
                            'is_default': m.get('is_default', 0)
                        }
                        for m in models
                    ]
                })
            except Exception as e:
                logger.error(f"Error getting models for provider {provider_id}: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/llm/models')
        @login_required
        def api_llm_all_models():
            """Get all active LLM models grouped by provider."""
            try:
                providers = self.db_facade.llm.get_all_providers(active_only=True)
                result = []
                
                for provider in providers:
                    provider_id = provider.get('provider_id')
                    models = self.db_facade.llm.get_provider_models(provider_id, active_only=True)
                    
                    result.append({
                        'provider_id': provider_id,
                        'provider_name': provider.get('name'),
                        'provider_type': provider.get('provider_type'),
                        'is_default': provider.get('is_default', 0),
                        'models': [
                            {
                                'model_id': m.get('model_id'),
                                'name': m.get('name'),
                                'display_name': m.get('display_name') or m.get('name'),
                                'model_type': m.get('model_type', 'chat'),
                                'context_window': m.get('context_window', 4096),
                                'supports_vision': m.get('supports_vision', 0),
                                'supports_functions': m.get('supports_functions', 0),
                                'is_default': m.get('is_default', 0)
                            }
                            for m in models
                        ]
                    })
                
                return jsonify({
                    'success': True,
                    'providers': result
                })
            except Exception as e:
                logger.error(f"Error getting all LLM models: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)})
        
        # ============================================
        # LLM MODELS MANAGEMENT
        # ============================================
        
        @self.app.route('/admin/llm-models')
        @admin_required
        def admin_llm_models():
            """Display LLM models management page."""
            models = []
            providers = []
            selected_provider = request.args.get('provider', '')
            
            try:
                # Filter by provider if specified
                if selected_provider:
                    models = self.db_facade.llm.get_all_models(provider_id=selected_provider)
                else:
                    models = self.db_facade.llm.get_all_models()
                
                # Get ALL providers for filter (not just active ones)
                providers = self.db_facade.llm.get_all_providers()
            except Exception as e:
                logger.error(f"Error getting LLM models: {e}", exc_info=True)
            
            return render_template('admin/llm_models.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   models=models,
                                   providers=providers,
                                   selected_provider=selected_provider)
        
        @self.app.route('/admin/llm-models/add', methods=['GET', 'POST'])
        @admin_required
        def add_llm_model():
            """Add a new LLM model."""
            providers = self.db_facade.fetch_all(
                "SELECT provider_id, name FROM llm_providers WHERE is_active = 1 ORDER BY name"
            ) or []
            
            if request.method == 'POST':
                model_id = request.form.get('model_id', '').strip()
                provider_id = request.form.get('provider_id', '').strip()
                name = request.form.get('name', '').strip()
                display_name = request.form.get('display_name', '').strip()
                description = request.form.get('description', '').strip()
                model_type = request.form.get('model_type', 'chat')
                context_window = int(request.form.get('context_window', 4096))
                max_output_tokens = int(request.form.get('max_output_tokens', 4096))
                input_cost = float(request.form.get('input_cost_per_1k', 0))
                output_cost = float(request.form.get('output_cost_per_1k', 0))
                supports_vision = 1 if 'supports_vision' in request.form else 0
                supports_functions = 1 if 'supports_functions' in request.form else 0
                supports_streaming = 1 if 'supports_streaming' in request.form else 0
                is_active = 1 if 'is_active' in request.form else 0
                
                if not model_id or not provider_id or not name:
                    flash('Model ID, Provider, and Name are required', 'error')
                    return redirect(url_for('add_llm_model'))
                
                try:
                    self.db_facade.execute(
                        """INSERT INTO llm_models 
                           (model_id, provider_id, name, display_name, description, model_type,
                            context_window, max_output_tokens, input_cost_per_1k, output_cost_per_1k,
                            supports_vision, supports_functions, supports_streaming, is_active)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (model_id, provider_id, name, display_name or name, description, model_type,
                         context_window, max_output_tokens, input_cost, output_cost,
                         supports_vision, supports_functions, supports_streaming, is_active)
                    )
                    self.log_audit('create_llm_model', 'llm_model', model_id)
                    flash(f'LLM Model "{display_name or name}" created successfully', 'success')
                    return redirect(url_for('admin_llm_models'))
                except Exception as e:
                    logger.error(f"Error creating LLM model: {e}", exc_info=True)
                    flash(f'Error creating model: {str(e)}', 'error')
            
            return render_template('admin/add_llm_model.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   providers=providers)
        
        @self.app.route('/admin/llm-models/<model_id>/edit', methods=['GET', 'POST'])
        @admin_required
        def edit_llm_model(model_id):
            """Edit an LLM model."""
            try:
                model = self.db_facade.fetch_one(
                    "SELECT * FROM llm_models WHERE model_id = ?",
                    (model_id,)
                )
                if not model:
                    flash('Model not found', 'error')
                    return redirect(url_for('admin_llm_models'))
                
                providers = self.db_facade.fetch_all(
                    "SELECT provider_id, name FROM llm_providers ORDER BY name"
                ) or []
                
                if request.method == 'POST':
                    display_name = request.form.get('display_name', '').strip()
                    description = request.form.get('description', '').strip()
                    context_window = int(request.form.get('context_window', 4096))
                    max_output_tokens = int(request.form.get('max_output_tokens', 4096))
                    input_cost = float(request.form.get('input_cost_per_1k', 0))
                    output_cost = float(request.form.get('output_cost_per_1k', 0))
                    supports_vision = 1 if 'supports_vision' in request.form else 0
                    supports_functions = 1 if 'supports_functions' in request.form else 0
                    supports_streaming = 1 if 'supports_streaming' in request.form else 0
                    is_active = 1 if 'is_active' in request.form else 0
                    is_default = 1 if 'is_default' in request.form else 0
                    
                    if is_default:
                        self.db_facade.execute("UPDATE llm_models SET is_default = 0")
                    
                    self.db_facade.execute(
                        """UPDATE llm_models SET display_name=?, description=?, context_window=?,
                           max_output_tokens=?, input_cost_per_1k=?, output_cost_per_1k=?,
                           supports_vision=?, supports_functions=?, supports_streaming=?,
                           is_active=?, is_default=?, updated_at=CURRENT_TIMESTAMP
                           WHERE model_id=?""",
                        (display_name, description, context_window, max_output_tokens,
                         input_cost, output_cost, supports_vision, supports_functions,
                         supports_streaming, is_active, is_default, model_id)
                    )
                    self.log_audit('update_llm_model', 'llm_model', model_id)
                    flash('Model updated successfully', 'success')
                    return redirect(url_for('admin_llm_models'))
                
                return render_template('admin/edit_llm_model.html',
                                       fullname=session.get('fullname'),
                                       userid=session.get('user_id'),
                                       roles=session.get('roles', []),
                                       model=model,
                                       providers=providers)
            except Exception as e:
                logger.error(f"Error editing LLM model: {e}", exc_info=True)
                flash('Error updating model', 'error')
                return redirect(url_for('admin_llm_models'))
        
        @self.app.route('/admin/llm-models/<model_id>/delete', methods=['POST'])
        @admin_required
        def delete_llm_model(model_id):
            """Delete an LLM model."""
            try:
                # Delete permissions first
                self.db_facade.execute(
                    "DELETE FROM model_permissions WHERE model_id = ?",
                    (model_id,)
                )
                self.db_facade.execute(
                    "DELETE FROM llm_models WHERE model_id = ?",
                    (model_id,)
                )
                self.log_audit('delete_llm_model', 'llm_model', model_id)
                flash('Model deleted successfully', 'success')
            except Exception as e:
                logger.error(f"Error deleting LLM model: {e}", exc_info=True)
                flash('Error deleting model', 'error')
            
            return redirect(url_for('admin_llm_models'))
        
        @self.app.route('/admin/llm-models/<model_id>/set-default', methods=['POST'])
        @admin_required
        def set_default_model(model_id):
            """Set a model as the default."""
            try:
                # Unset all models as default
                self.db_facade.execute("UPDATE llm_models SET is_default = 0")
                # Set this model as default
                self.db_facade.execute(
                    "UPDATE llm_models SET is_default = 1 WHERE model_id = ?",
                    (model_id,)
                )
                self.log_audit('set_default_model', 'llm_model', model_id)
                flash(f'Model "{model_id}" set as default', 'success')
            except Exception as e:
                logger.error(f"Error setting default model: {e}", exc_info=True)
                flash('Error setting default model', 'error')
            
            return redirect(url_for('admin_llm_models'))
        
        @self.app.route('/admin/llm-models/<model_id>/toggle-status', methods=['POST'])
        @admin_required
        def toggle_model_status(model_id):
            """Toggle a model's active status."""
            try:
                model = self.db_facade.fetch_one(
                    "SELECT * FROM llm_models WHERE model_id = ?",
                    (model_id,)
                )
                if model:
                    new_status = 0 if model.get('is_active', 1) else 1
                    self.db_facade.execute(
                        "UPDATE llm_models SET is_active = ? WHERE model_id = ?",
                        (new_status, model_id)
                    )
                    status_text = 'activated' if new_status else 'deactivated'
                    self.log_audit(f'toggle_model_{status_text}', 'llm_model', model_id)
                    flash(f'Model "{model_id}" {status_text}', 'success')
            except Exception as e:
                logger.error(f"Error toggling model status: {e}", exc_info=True)
                flash('Error toggling model status', 'error')
            
            return redirect(url_for('admin_llm_models'))
        
        @self.app.route('/admin/llm-models/<model_id>/permissions', methods=['GET', 'POST'])
        @admin_required
        def model_permissions(model_id):
            """Manage model permissions by role."""
            try:
                model = self.db_facade.fetch_one(
                    "SELECT * FROM llm_models WHERE model_id = ?",
                    (model_id,)
                )
                if not model:
                    flash('Model not found', 'error')
                    return redirect(url_for('admin_llm_models'))
                
                roles = self.db_facade.fetch_all("SELECT * FROM roles ORDER BY role_name") or []
                permissions = self.db_facade.fetch_all(
                    "SELECT * FROM model_permissions WHERE model_id = ?",
                    (model_id,)
                ) or []
                
                # Create a dict for easy lookup
                perm_dict = {p['role_name']: p for p in permissions}
                
                if request.method == 'POST':
                    # Clear existing permissions for this model
                    self.db_facade.execute(
                        "DELETE FROM model_permissions WHERE model_id = ?",
                        (model_id,)
                    )
                    
                    # Add new permissions
                    for role in roles:
                        role_name = role['role_name']
                        can_use = 1 if f'can_use_{role_name}' in request.form else 0
                        daily_limit = int(request.form.get(f'daily_limit_{role_name}', -1))
                        monthly_limit = int(request.form.get(f'monthly_limit_{role_name}', -1))
                        
                        if can_use:
                            self.db_facade.execute(
                                """INSERT INTO model_permissions 
                                   (model_id, role_name, can_use, daily_limit, monthly_limit, created_by)
                                   VALUES (?, ?, ?, ?, ?, ?)""",
                                (model_id, role_name, can_use, daily_limit, monthly_limit,
                                 session.get('user_id'))
                            )
                    
                    self.log_audit('update_model_permissions', 'llm_model', model_id)
                    flash('Model permissions updated successfully', 'success')
                    return redirect(url_for('admin_llm_models'))
                
                return render_template('admin/model_permissions.html',
                                       fullname=session.get('fullname'),
                                       userid=session.get('user_id'),
                                       roles_list=session.get('roles', []),
                                       model=model,
                                       roles=roles,
                                       perm_dict=perm_dict)
            except Exception as e:
                logger.error(f"Error managing model permissions: {e}", exc_info=True)
                flash('Error managing permissions', 'error')
                return redirect(url_for('admin_llm_models'))
        
        # ============================================
        # MCP TOOL SERVERS MANAGEMENT ROUTES
        # ============================================
        
        @self.app.route('/admin/mcp-tool-servers')
        @admin_required
        def admin_mcp_tool_servers():
            """Display MCP Tool Servers management page."""
            servers = []
            try:
                servers = self.db_facade.mcp.get_all_servers()
            except Exception as e:
                logger.error(f"Error getting MCP tool servers: {e}", exc_info=True)
            
            return render_template('admin/mcp_tool_servers.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   servers=servers)
        
        @self.app.route('/admin/mcp-tool-servers/add', methods=['GET', 'POST'])
        @admin_required
        def add_mcp_tool_server():
            """Add a new MCP Tool Server."""
            if request.method == 'POST':
                import uuid
                server_id = str(uuid.uuid4())[:8]
                name = request.form.get('name', '').strip()
                description = request.form.get('description', '').strip()
                base_url = request.form.get('base_url', '').strip().rstrip('/')
                tools_endpoint = request.form.get('tools_endpoint', '/api/tools/list').strip()
                auth_type = request.form.get('auth_type', 'none')
                auth_config = request.form.get('auth_config', '{}').strip()
                auth_endpoint = request.form.get('auth_endpoint', '').strip()
                timeout_seconds = int(request.form.get('timeout_seconds', 30))
                auto_refresh = 1 if 'auto_refresh' in request.form else 0
                refresh_interval = int(request.form.get('refresh_interval_minutes', 60))
                is_active = 1 if 'is_active' in request.form else 0
                
                if not name or not base_url:
                    flash('Name and Base URL are required', 'error')
                    return redirect(url_for('add_mcp_tool_server'))
                
                try:
                    # Validate auth_config is valid JSON
                    json.loads(auth_config)
                except:
                    auth_config = '{}'
                
                try:
                    result = self.db_facade.mcp.create_server(
                        name=name,
                        base_url=base_url,
                        created_by=session.get('user_id'),
                        description=description,
                        tools_endpoint=tools_endpoint,
                        auth_type=auth_type,
                        auth_config=auth_config,
                        auth_endpoint=auth_endpoint,
                        is_active=is_active,
                        auto_refresh=auto_refresh,
                        refresh_interval_minutes=refresh_interval,
                        timeout_seconds=timeout_seconds
                    )
                    
                    if result:
                        server_id = result
                        self.log_audit('create', 'mcp_tool_server', server_id)
                    
                    # Connect to MCP manager and load tools if active
                    if is_active:
                        try:
                            from abhikarta.mcp import get_mcp_manager, MCPServerConfig
                            from abhikarta.tools import get_tools_registry
                            
                            manager = get_mcp_manager()
                            registry = get_tools_registry()
                            
                            # Ensure manager has registry set
                            if not manager._tools_registry:
                                manager.set_tools_registry(registry)
                            if not manager._db_facade:
                                manager.set_db_facade(self.db_facade)
                            
                            # Parse auth config
                            auth_data = json.loads(auth_config) if auth_config else {}
                            auth_token = auth_data.get('token') or auth_data.get('api_key')
                            
                            # Create server config
                            config = MCPServerConfig(
                                server_id=server_id,
                                name=name,
                                description=description,
                                url=base_url,
                                tools_endpoint=tools_endpoint,
                                auth_token=auth_token,
                                timeout_seconds=timeout_seconds,
                                auto_connect=True
                            )
                            
                            # Add and connect
                            manager.add_server(config, connect=True)
                            
                            # Get tool count
                            server = manager.get_server(server_id)
                            tool_count = server.state.tool_count if server else 0
                            
                            flash(f'MCP Tool Server "{name}" added and connected successfully. Loaded {tool_count} tools.', 'success')
                        except Exception as e:
                            logger.error(f"Error connecting to MCP server: {e}", exc_info=True)
                            flash(f'Server added but connection failed: {str(e)}', 'warning')
                    else:
                        flash(f'MCP Tool Server "{name}" added successfully (not active)', 'success')
                    
                    return redirect(url_for('admin_mcp_tool_servers'))
                except Exception as e:
                    logger.error(f"Error adding MCP tool server: {e}", exc_info=True)
                    flash(f'Error adding server: {str(e)}', 'error')
            
            return render_template('admin/add_mcp_tool_server.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []))
        
        @self.app.route('/admin/mcp-tool-servers/<server_id>/edit', methods=['GET', 'POST'])
        @admin_required
        def edit_mcp_tool_server(server_id):
            """Edit an existing MCP Tool Server."""
            server = self.db_facade.fetch_one(
                "SELECT * FROM mcp_tool_servers WHERE server_id = ?",
                (server_id,)
            )
            
            if not server:
                flash('Server not found', 'error')
                return redirect(url_for('admin_mcp_tool_servers'))
            
            if request.method == 'POST':
                name = request.form.get('name', '').strip()
                description = request.form.get('description', '').strip()
                base_url = request.form.get('base_url', '').strip().rstrip('/')
                tools_endpoint = request.form.get('tools_endpoint', '/api/tools/list').strip()
                auth_type = request.form.get('auth_type', 'none')
                auth_config = request.form.get('auth_config', '{}').strip()
                auth_endpoint = request.form.get('auth_endpoint', '').strip()
                timeout_seconds = int(request.form.get('timeout_seconds', 30))
                auto_refresh = 1 if 'auto_refresh' in request.form else 0
                refresh_interval = int(request.form.get('refresh_interval_minutes', 60))
                is_active = 1 if 'is_active' in request.form else 0
                
                if not name or not base_url:
                    flash('Name and Base URL are required', 'error')
                    return redirect(url_for('edit_mcp_tool_server', server_id=server_id))
                
                try:
                    json.loads(auth_config)
                except:
                    auth_config = '{}'
                
                try:
                    self.db_facade.execute(
                        """UPDATE mcp_tool_servers SET
                           name = ?, description = ?, base_url = ?, tools_endpoint = ?,
                           auth_type = ?, auth_config = ?, auth_endpoint = ?, is_active = ?, auto_refresh = ?,
                           refresh_interval_minutes = ?, timeout_seconds = ?
                           WHERE server_id = ?""",
                        (name, description, base_url, tools_endpoint,
                         auth_type, auth_config, auth_endpoint, is_active, auto_refresh,
                         refresh_interval, timeout_seconds, server_id)
                    )
                    self.log_audit('update', 'mcp_tool_server', server_id)
                    flash('Server updated successfully', 'success')
                    return redirect(url_for('admin_mcp_tool_servers'))
                except Exception as e:
                    logger.error(f"Error updating MCP tool server: {e}", exc_info=True)
                    flash(f'Error updating server: {str(e)}', 'error')
            
            return render_template('admin/edit_mcp_tool_server.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   server=server)
        
        @self.app.route('/admin/mcp-tool-servers/<server_id>/delete', methods=['POST'])
        @admin_required
        def delete_mcp_tool_server(server_id):
            """Delete an MCP Tool Server."""
            try:
                self.db_facade.execute(
                    "DELETE FROM mcp_tool_servers WHERE server_id = ?",
                    (server_id,)
                )
                self.log_audit('delete', 'mcp_tool_server', server_id)
                flash('Server deleted successfully', 'success')
            except Exception as e:
                logger.error(f"Error deleting MCP tool server: {e}", exc_info=True)
                flash(f'Error deleting server: {str(e)}', 'error')
            return redirect(url_for('admin_mcp_tool_servers'))
        
        @self.app.route('/admin/mcp-tool-servers/<server_id>/test-page')
        @admin_required
        def mcp_server_test_page(server_id):
            """Display test page for an MCP Tool Server."""
            server = self.db_facade.fetch_one(
                "SELECT * FROM mcp_tool_servers WHERE server_id = ?",
                (server_id,)
            )
            
            if not server:
                flash('Server not found', 'error')
                return redirect(url_for('admin_mcp_tool_servers'))
            
            return render_template('admin/mcp_server_test.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   server=server)
        
        @self.app.route('/admin/mcp-tool-servers/<server_id>/test', methods=['POST'])
        @admin_required
        def test_mcp_tool_server(server_id):
            """Test connection to an MCP Tool Server and show debug info."""
            import urllib.request
            import urllib.error
            
            server = self.db_facade.fetch_one(
                "SELECT * FROM mcp_tool_servers WHERE server_id = ?",
                (server_id,)
            )
            
            if not server:
                return jsonify({'success': False, 'error': 'Server not found'})
            
            result = {
                'success': False,
                'server_name': server['name'],
                'url': '',
                'status_code': None,
                'content_type': None,
                'response_size': 0,
                'response_preview': '',
                'tools_found': 0,
                'error': None
            }
            
            try:
                # Build the full URL
                base_url = server['base_url'].rstrip('/')
                endpoint = server['tools_endpoint']
                if not endpoint.startswith('/'):
                    endpoint = '/' + endpoint
                full_url = f"{base_url}{endpoint}"
                result['url'] = full_url
                
                timeout = server.get('timeout_seconds', 30) or 30
                
                # Create request
                req = urllib.request.Request(full_url)
                req.add_header('Accept', 'application/json')
                req.add_header('Content-Type', 'application/json')
                req.add_header('User-Agent', 'Abhikarta-LLM/1.4.8')
                
                # Add auth if configured
                auth_type = server.get('auth_type', 'none')
                if auth_type and auth_type != 'none':
                    try:
                        auth_config = json.loads(server.get('auth_config', '{}'))
                        if auth_type == 'bearer' and 'token' in auth_config:
                            req.add_header('Authorization', f"Bearer {auth_config['token']}")
                        elif auth_type == 'api_key' and 'key' in auth_config and 'header' in auth_config:
                            req.add_header(auth_config['header'], auth_config['key'])
                        elif auth_type == 'basic' and 'username' in auth_config and 'password' in auth_config:
                            import base64
                            credentials = f"{auth_config['username']}:{auth_config['password']}"
                            encoded = base64.b64encode(credentials.encode()).decode()
                            req.add_header('Authorization', f"Basic {encoded}")
                    except:
                        pass
                
                # Make request
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    result['status_code'] = response.getcode()
                    result['content_type'] = response.headers.get('Content-Type', 'unknown')
                    raw_data = response.read()
                    result['response_size'] = len(raw_data)
                    
                    if raw_data:
                        try:
                            response_text = raw_data.decode('utf-8')
                        except:
                            response_text = raw_data.decode('latin-1')
                        
                        result['response_preview'] = response_text[:1000]
                        
                        # Try to parse JSON
                        try:
                            data = json.loads(response_text)
                            
                            # Count tools
                            tools = []
                            if isinstance(data, dict):
                                for key in ['tools', 'data', 'items', 'results']:
                                    if key in data and isinstance(data[key], list):
                                        tools = data[key]
                                        break
                            elif isinstance(data, list):
                                tools = data
                            
                            result['tools_found'] = len(tools)
                            result['success'] = True
                            
                        except json.JSONDecodeError as je:
                            result['error'] = f"Invalid JSON: {str(je)}"
                    else:
                        result['error'] = "Empty response from server"
                        
            except urllib.error.HTTPError as e:
                result['status_code'] = e.code
                result['error'] = f"HTTP {e.code}: {e.reason}"
                try:
                    result['response_preview'] = e.read().decode('utf-8')[:500]
                except:
                    pass
            except urllib.error.URLError as e:
                result['error'] = f"Connection failed: {str(e.reason)}"
            except Exception as e:
                result['error'] = f"{type(e).__name__}: {str(e)}"
            
            return jsonify(result)
        
        @self.app.route('/admin/mcp-tool-servers/<server_id>/refresh', methods=['POST'])
        @admin_required
        def refresh_mcp_tool_server(server_id):
            """Refresh tools from an MCP Tool Server."""
            import urllib.request
            import urllib.error
            
            server = self.db_facade.fetch_one(
                "SELECT * FROM mcp_tool_servers WHERE server_id = ?",
                (server_id,)
            )
            
            if not server:
                flash('Server not found', 'error')
                return redirect(url_for('admin_mcp_tool_servers'))
            
            try:
                # Build the full URL
                base_url = server['base_url'].rstrip('/')
                endpoint = server['tools_endpoint']
                if not endpoint.startswith('/'):
                    endpoint = '/' + endpoint
                full_url = f"{base_url}{endpoint}"
                timeout = server.get('timeout_seconds', 30) or 30
                
                logger.info(f"Refreshing MCP tools from: {full_url}")
                
                # Create request with headers
                req = urllib.request.Request(full_url)
                req.add_header('Accept', 'application/json')
                req.add_header('Content-Type', 'application/json')
                req.add_header('User-Agent', 'Abhikarta-LLM/1.4.8')
                
                # Add auth headers if configured
                auth_type = server.get('auth_type', 'none')
                if auth_type and auth_type != 'none':
                    try:
                        auth_config = json.loads(server.get('auth_config', '{}'))
                        if auth_type == 'bearer' and 'token' in auth_config:
                            req.add_header('Authorization', f"Bearer {auth_config['token']}")
                        elif auth_type == 'api_key' and 'key' in auth_config and 'header' in auth_config:
                            req.add_header(auth_config['header'], auth_config['key'])
                        elif auth_type == 'basic' and 'username' in auth_config and 'password' in auth_config:
                            import base64
                            credentials = f"{auth_config['username']}:{auth_config['password']}"
                            encoded = base64.b64encode(credentials.encode()).decode()
                            req.add_header('Authorization', f"Basic {encoded}")
                    except Exception as auth_err:
                        logger.warning(f"Auth config error: {auth_err}")
                
                # Fetch tools
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    status_code = response.getcode()
                    content_type = response.headers.get('Content-Type', '')
                    raw_data = response.read()
                    
                    logger.info(f"Response status: {status_code}, Content-Type: {content_type}, Size: {len(raw_data)} bytes")
                    
                    if not raw_data:
                        raise ValueError("Server returned empty response")
                    
                    # Decode response
                    try:
                        response_text = raw_data.decode('utf-8')
                    except UnicodeDecodeError:
                        response_text = raw_data.decode('latin-1')
                    
                    # Log first 500 chars for debugging
                    logger.debug(f"Response preview: {response_text[:500]}")
                    
                    # Parse JSON
                    try:
                        data = json.loads(response_text)
                    except json.JSONDecodeError as je:
                        logger.error(f"JSON parse error. Response starts with: {response_text[:200]}", exc_info=True)
                        raise ValueError(f"Invalid JSON response: {str(je)[:100]}")
                
                # Extract tools list - handle different response formats
                tools = []
                if isinstance(data, dict):
                    # Try common keys: tools, data, items, results
                    for key in ['tools', 'data', 'items', 'results']:
                        if key in data and isinstance(data[key], list):
                            tools = data[key]
                            break
                    # If no list found, check if dict itself contains tool-like entries
                    if not tools and 'name' in data and 'inputSchema' in data:
                        tools = [data]  # Single tool response
                elif isinstance(data, list):
                    tools = data
                else:
                    raise ValueError(f"Unexpected response format: {type(data).__name__}")
                
                tool_count = len(tools)
                logger.info(f"Parsed {tool_count} tools from {server['name']}")
                
                # Update database with cached tools
                self.db_facade.execute(
                    """UPDATE mcp_tool_servers SET
                       cached_tools = ?, tool_count = ?,
                       last_refresh = CURRENT_TIMESTAMP,
                       last_refresh_status = 'success'
                       WHERE server_id = ?""",
                    (json.dumps(tools), tool_count, server_id)
                )
                
                self.log_audit('refresh', 'mcp_tool_server', server_id)
                flash(f'Successfully loaded {tool_count} tools from {server["name"]}', 'success')
                
            except urllib.error.HTTPError as e:
                error_msg = f"HTTP {e.code}: {e.reason}"
                try:
                    error_body = e.read().decode('utf-8')[:200]
                    error_msg += f" - {error_body}"
                except:
                    pass
                logger.error(f"HTTP error refreshing MCP server: {error_msg}", exc_info=True)
                self.db_facade.execute(
                    """UPDATE mcp_tool_servers SET
                       last_refresh = CURRENT_TIMESTAMP,
                       last_refresh_status = ?
                       WHERE server_id = ?""",
                    (error_msg[:500], server_id)
                )
                flash(f'HTTP Error: {error_msg}', 'error')
                
            except urllib.error.URLError as e:
                error_msg = f"Connection error: {str(e.reason)}"
                logger.error(f"URL error refreshing MCP server: {error_msg}", exc_info=True)
                self.db_facade.execute(
                    """UPDATE mcp_tool_servers SET
                       last_refresh = CURRENT_TIMESTAMP,
                       last_refresh_status = ?
                       WHERE server_id = ?""",
                    (error_msg[:500], server_id)
                )
                flash(f'Connection Error: {error_msg}', 'error')
                
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                logger.error(f"Error refreshing MCP tool server: {error_msg}", exc_info=True)
                self.db_facade.execute(
                    """UPDATE mcp_tool_servers SET
                       last_refresh = CURRENT_TIMESTAMP,
                       last_refresh_status = ?
                       WHERE server_id = ?""",
                    (error_msg[:500], server_id)
                )
                flash(f'Error: {error_msg}', 'error')
            
            return redirect(url_for('admin_mcp_tool_servers'))
        
        @self.app.route('/admin/mcp-tool-servers/<server_id>/tools')
        @admin_required
        def view_mcp_server_tools(server_id):
            """View tools from an MCP Tool Server."""
            server = self.db_facade.fetch_one(
                "SELECT * FROM mcp_tool_servers WHERE server_id = ?",
                (server_id,)
            )
            
            if not server:
                flash('Server not found', 'error')
                return redirect(url_for('admin_mcp_tool_servers'))
            
            tools = []
            try:
                tools = json.loads(server.get('cached_tools', '[]'))
            except:
                pass
            
            return render_template('admin/mcp_server_tools.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   server=server,
                                   tools=tools)
        
        @self.app.route('/admin/mcp-tool-servers/api/all-tools')
        @login_required
        def api_all_mcp_tools():
            """Internal API: Get all tools (built-in + MCP) for Visual Designer."""
            try:
                all_tools = []
                
                # 1. Get built-in tools from ToolsRegistry
                try:
                    from abhikarta.tools.registry import ToolsRegistry
                    registry = ToolsRegistry.get_instance()
                    builtin_tools = registry.list_tools(enabled_only=True)
                    
                    logger.info(f"Found {len(builtin_tools)} enabled tools in registry")
                    
                    for tool in builtin_tools:
                        try:
                            # Skip MCP tools as we'll get them from servers below
                            tool_type_val = getattr(tool.metadata, 'tool_type', None)
                            if tool_type_val and hasattr(tool_type_val, 'value'):
                                if tool_type_val.value in ['mcp', 'mcp_plugin']:
                                    continue
                            
                            # Build tool entry with builtin namespace
                            # Safely get schema using get_schema() method
                            schema_dict = {}
                            try:
                                tool_schema = tool.get_schema()
                                if tool_schema:
                                    schema_dict = tool_schema.to_dict()
                            except:
                                schema_dict = {}
                            
                            # Safely get category
                            category_val = 'general'
                            if tool.metadata and tool.metadata.category:
                                try:
                                    category_val = tool.metadata.category.value
                                except:
                                    category_val = str(tool.metadata.category)
                            
                            # Safely get tool type
                            tool_type_str = 'function'
                            if tool.metadata and tool.metadata.tool_type:
                                try:
                                    tool_type_str = tool.metadata.tool_type.value
                                except:
                                    tool_type_str = str(tool.metadata.tool_type)
                            
                            tool_entry = {
                                'name': tool.name,
                                'display_name': f"builtin:{tool.name}",
                                'description': tool.description or '',
                                'inputSchema': schema_dict,
                                '_source': 'builtin',
                                '_source_type': 'builtin',
                                '_server_id': 'builtin',
                                '_server_name': 'Built-in Tools',
                                '_category': category_val,
                                '_tool_type': tool_type_str
                            }
                            all_tools.append(tool_entry)
                        except Exception as te:
                            logger.warning(f"Error processing tool {getattr(tool, 'name', 'unknown')}: {te}")
                            continue
                            
                    logger.info(f"Added {len([t for t in all_tools if t.get('_source') == 'builtin'])} builtin tools")
                except Exception as e:
                    logger.error(f"Could not load built-in tools: {e}", exc_info=True)
                
                # 2. Get MCP tools from active servers
                servers = self.db_facade.fetch_all(
                    "SELECT server_id, name, tool_count FROM mcp_tool_servers WHERE is_active = 1"
                ) or []
                
                for server in self.db_facade.fetch_all(
                    "SELECT * FROM mcp_tool_servers WHERE is_active = 1"
                ) or []:
                    try:
                        cached_tools = json.loads(server.get('cached_tools', '[]'))
                        server_name = server['name']
                        for tool in cached_tools:
                            tool_name = tool.get('name', 'unknown')
                            tool['display_name'] = f"mcp:{server_name}:{tool_name}"
                            tool['_source'] = 'mcp'
                            tool['_source_type'] = 'mcp'
                            tool['_server_id'] = server['server_id']
                            tool['_server_name'] = server_name
                            all_tools.append(tool)
                    except:
                        pass
                
                return jsonify({
                    'success': True,
                    'tools': all_tools,
                    'servers': [dict(s) for s in servers],
                    'tool_count': len(all_tools),
                    'builtin_count': len([t for t in all_tools if t.get('_source') == 'builtin']),
                    'mcp_count': len([t for t in all_tools if t.get('_source') == 'mcp'])
                })
            except Exception as e:
                logger.error(f"Error getting all tools: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/admin/mcp-tool-servers/all-tools')
        @admin_required
        def view_all_mcp_tools():
            """View all tools from all active MCP Tool Servers."""
            servers = []
            all_tools = []
            tool_by_server = {}
            
            try:
                servers = self.db_facade.fetch_all(
                    "SELECT * FROM mcp_tool_servers WHERE is_active = 1 ORDER BY name"
                ) or []
                
                for server in servers:
                    try:
                        cached_tools = json.loads(server.get('cached_tools', '[]'))
                        tool_by_server[server['server_id']] = {
                            'server': server,
                            'tools': cached_tools
                        }
                        for tool in cached_tools:
                            tool['_server_id'] = server['server_id']
                            tool['_server_name'] = server['name']
                            tool['_server_url'] = server['base_url']
                            all_tools.append(tool)
                    except:
                        tool_by_server[server['server_id']] = {
                            'server': server,
                            'tools': []
                        }
            except Exception as e:
                logger.error(f"Error getting all MCP tools: {e}", exc_info=True)
                flash(f'Error loading tools: {str(e)}', 'error')
            
            return render_template('admin/all_mcp_tools.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   servers=servers,
                                   all_tools=all_tools,
                                   tool_by_server=tool_by_server)
        
        # =====================================================================
        # HITL Administration Routes
        # =====================================================================
        
        @self.app.route('/admin/hitl')
        @admin_required
        def admin_hitl_tasks():
            """Admin view of all HITL tasks."""
            from abhikarta.hitl import HITLManager
            
            status_filter = request.args.get('status', '')
            manager = HITLManager(self.db_facade)
            
            if status_filter:
                tasks = manager.get_all_tasks(status=status_filter, limit=200)
            else:
                tasks = manager.get_all_tasks(limit=200)
            
            stats = manager.get_stats()
            
            # Get users for assignment dropdown
            users = self.db_facade.fetch_all(
                "SELECT user_id, fullname FROM users WHERE is_active = 1 ORDER BY fullname"
            ) or []
            
            return render_template('admin/hitl_tasks.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   tasks=tasks,
                                   stats=stats,
                                   users=users,
                                   status_filter=status_filter)
        
        @self.app.route('/admin/hitl/create', methods=['GET', 'POST'])
        @admin_required
        def admin_hitl_create():
            """Create a new HITL task."""
            from abhikarta.hitl import HITLManager
            from datetime import datetime, timedelta
            
            if request.method == 'POST':
                title = request.form.get('title', '').strip()
                task_type = request.form.get('task_type', 'approval')
                description = request.form.get('description', '').strip()
                priority = int(request.form.get('priority', 5))
                assigned_to = request.form.get('assigned_to') or None
                timeout_minutes = int(request.form.get('timeout_minutes', 1440))
                tags = request.form.get('tags', '').strip()
                
                if not title:
                    flash('Title is required', 'error')
                else:
                    manager = HITLManager(self.db_facade)
                    
                    task = manager.create_task(
                        title=title,
                        task_type=task_type,
                        description=description,
                        priority=priority,
                        assigned_to=assigned_to,
                        timeout_minutes=timeout_minutes,
                        created_by=session.get('user_id'),
                        tags=[t.strip() for t in tags.split(',') if t.strip()]
                    )
                    
                    self.log_audit('create_hitl', 'hitl_task', task.task_id)
                    flash(f'HITL task created: {task.task_id}', 'success')
                    return redirect(url_for('admin_hitl_tasks'))
            
            # Get users for assignment
            users = self.db_facade.fetch_all(
                "SELECT user_id, fullname FROM users WHERE is_active = 1 ORDER BY fullname"
            ) or []
            
            return render_template('admin/hitl_create.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   users=users)
        
        @self.app.route('/admin/hitl/<task_id>')
        @admin_required
        def admin_hitl_detail(task_id):
            """Admin view of HITL task detail."""
            from abhikarta.hitl import HITLManager
            
            manager = HITLManager(self.db_facade)
            task = manager.get_task(task_id)
            
            if not task:
                flash('Task not found', 'error')
                return redirect(url_for('admin_hitl_tasks'))
            
            comments = manager.get_comments(task_id, include_internal=True)
            
            # Get assignment history
            assignments = self.db_facade.fetch_all(
                """SELECT * FROM hitl_assignments 
                   WHERE task_id = ? 
                   ORDER BY assigned_at DESC""",
                (task_id,)
            ) or []
            
            # Get users for reassignment
            users = self.db_facade.fetch_all(
                "SELECT user_id, fullname FROM users WHERE is_active = 1 ORDER BY fullname"
            ) or []
            
            return render_template('admin/hitl_detail.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   task=task,
                                   comments=comments,
                                   assignments=assignments,
                                   users=users)
        
        @self.app.route('/admin/hitl/<task_id>/cancel', methods=['POST'])
        @admin_required
        def admin_hitl_cancel(task_id):
            """Cancel a HITL task."""
            from abhikarta.hitl import HITLManager
            
            reason = request.form.get('reason', '')
            
            manager = HITLManager(self.db_facade)
            manager.cancel_task(task_id, session.get('user_id'), reason)
            
            self.log_audit('cancel_hitl', 'hitl_task', task_id, {'reason': reason})
            flash('Task cancelled', 'warning')
            
            return redirect(url_for('admin_hitl_tasks'))
        
        @self.app.route('/admin/hitl/<task_id>/assign', methods=['POST'])
        @admin_required
        def admin_hitl_assign(task_id):
            """Assign a HITL task."""
            from abhikarta.hitl import HITLManager
            
            assign_to = request.form.get('assign_to')
            reason = request.form.get('reason', '')
            
            if not assign_to:
                flash('Please select a user', 'error')
                return redirect(url_for('admin_hitl_detail', task_id=task_id))
            
            manager = HITLManager(self.db_facade)
            manager.assign_task(task_id, assign_to, session.get('user_id'), reason)
            
            self.log_audit('assign_hitl', 'hitl_task', task_id, 
                          {'assigned_to': assign_to, 'reason': reason})
            flash(f'Task assigned to {assign_to}', 'success')
            
            return redirect(url_for('admin_hitl_detail', task_id=task_id))
        
        @self.app.route('/admin/hitl/<task_id>/resolve', methods=['POST'])
        @admin_required
        def admin_hitl_resolve(task_id):
            """Admin resolve a HITL task."""
            from abhikarta.hitl import HITLManager
            import json
            
            resolution = request.form.get('resolution')
            comment = request.form.get('comment', '')
            response_data_str = request.form.get('response_data', '{}')
            
            try:
                response_data = json.loads(response_data_str) if response_data_str else {}
            except:
                response_data = {'raw_input': response_data_str}
            
            manager = HITLManager(self.db_facade)
            user_id = session.get('user_id')
            
            if resolution == 'approve':
                manager.approve_task(task_id, user_id, response_data, comment)
                flash('Task approved', 'success')
            elif resolution == 'reject':
                manager.reject_task(task_id, user_id, response_data, comment)
                flash('Task rejected', 'warning')
            
            self.log_audit(f'{resolution}_hitl', 'hitl_task', task_id)
            
            return redirect(url_for('admin_hitl_tasks'))
        
        logger.info("Admin routes registered")
