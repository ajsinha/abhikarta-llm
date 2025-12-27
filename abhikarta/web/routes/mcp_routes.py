"""
MCP Routes Module - Handles MCP plugin management routes and functionality

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

from flask import render_template, request, redirect, url_for, session, flash
import logging
import json
import uuid
from datetime import datetime

from .abstract_routes import AbstractRoutes, admin_required

logger = logging.getLogger(__name__)


class MCPRoutes(AbstractRoutes):
    """
    Handles MCP plugin management routes for the application.
    
    This class manages routes for MCP server and plugin management.
    
    Attributes:
        app: Flask application instance
        db_facade: DatabaseFacade instance for database operations
    """
    
    def __init__(self, app):
        """
        Initialize MCPRoutes.
        
        Args:
            app: Flask application instance
        """
        super().__init__(app)
        logger.info("MCPRoutes initialized")
    
    def register_routes(self):
        """Register all MCP routes."""
        
        @self.app.route('/admin/mcp/plugins')
        @admin_required
        def mcp_plugins():
            """List all MCP plugins."""
            plugins = []
            try:
                plugins = self.db_facade.fetch_all(
                    "SELECT * FROM mcp_plugins ORDER BY name"
                )
            except Exception as e:
                logger.error(f"Error getting MCP plugins: {e}")
            
            return render_template('mcp/plugins.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   plugins=plugins)
        
        @self.app.route('/admin/mcp/plugins/add', methods=['GET', 'POST'])
        @admin_required
        def add_mcp_plugin():
            """Add a new MCP plugin."""
            server_types = ['stdio', 'http', 'websocket']
            
            if request.method == 'POST':
                name = request.form.get('name', '').strip()
                description = request.form.get('description', '').strip()
                server_type = request.form.get('server_type', 'stdio')
                config = request.form.get('config', '{}')
                
                if not name:
                    flash('Plugin name is required', 'error')
                    return render_template('mcp/add_plugin.html',
                                           fullname=session.get('fullname'),
                                           userid=session.get('user_id'),
                                           roles=session.get('roles', []),
                                           server_types=server_types)
                
                # Validate JSON config
                try:
                    config_dict = json.loads(config) if config else {}
                except json.JSONDecodeError:
                    flash('Invalid JSON configuration', 'error')
                    return render_template('mcp/add_plugin.html',
                                           fullname=session.get('fullname'),
                                           userid=session.get('user_id'),
                                           roles=session.get('roles', []),
                                           server_types=server_types)
                
                plugin_id = f"mcp_{uuid.uuid4().hex[:12]}"
                
                try:
                    self.db_facade.execute(
                        """INSERT INTO mcp_plugins 
                           (plugin_id, name, description, server_type, config, status)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (plugin_id, name, description, server_type, 
                         json.dumps(config_dict), 'inactive')
                    )
                    
                    self.log_audit('create_mcp_plugin', 'mcp_plugin', plugin_id)
                    flash(f'MCP plugin "{name}" created successfully', 'success')
                    return redirect(url_for('mcp_plugins'))
                except Exception as e:
                    logger.error(f"Error creating MCP plugin: {e}")
                    flash('Failed to create MCP plugin', 'error')
            
            return render_template('mcp/add_plugin.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   server_types=server_types)
        
        @self.app.route('/admin/mcp/plugins/<plugin_id>')
        @admin_required
        def mcp_plugin_detail(plugin_id):
            """
            Display detailed information about a specific MCP plugin.
            
            Args:
                plugin_id: The unique identifier for the MCP plugin
                
            Returns:
                Rendered template with plugin details
            """
            try:
                plugin = self.db_facade.fetch_one(
                    "SELECT * FROM mcp_plugins WHERE plugin_id = ?",
                    (plugin_id,)
                )
                
                if not plugin:
                    flash(f'MCP Plugin "{plugin_id}" not found', 'error')
                    logger.warning(f"Attempted to access non-existent MCP plugin: {plugin_id}")
                    return redirect(url_for('mcp_plugins'))
                
                # Parse config JSON
                config = {}
                if plugin.get('config'):
                    try:
                        config = json.loads(plugin['config'])
                    except:
                        config = {}
                
                # Convert plugin info to JSON for raw data display
                plugin_info_json = json.dumps(dict(plugin), indent=2, default=str)
                
                logger.info(f"Admin {session.get('user_id')} viewed details for MCP plugin: {plugin_id}")
                
                return render_template('mcp/plugin_detail.html',
                                       fullname=session.get('fullname'),
                                       userid=session.get('user_id'),
                                       roles=session.get('roles', []),
                                       plugin=plugin,
                                       config=config,
                                       plugin_info_json=plugin_info_json)
            
            except Exception as e:
                logger.error(f"Error retrieving MCP plugin details for {plugin_id}: {e}", exc_info=True)
                flash(f'Error retrieving plugin details: {str(e)}', 'error')
                return redirect(url_for('mcp_plugins'))
        
        @self.app.route('/admin/mcp/plugins/<plugin_id>/edit', methods=['GET', 'POST'])
        @admin_required
        def edit_mcp_plugin(plugin_id):
            """Edit an existing MCP plugin."""
            plugin = None
            try:
                plugin = self.db_facade.fetch_one(
                    "SELECT * FROM mcp_plugins WHERE plugin_id = ?",
                    (plugin_id,)
                )
            except Exception as e:
                logger.error(f"Error getting MCP plugin: {e}")
            
            if not plugin:
                flash('MCP plugin not found', 'error')
                return redirect(url_for('mcp_plugins'))
            
            server_types = ['stdio', 'http', 'websocket']
            
            if request.method == 'POST':
                name = request.form.get('name', '').strip()
                description = request.form.get('description', '').strip()
                server_type = request.form.get('server_type', 'stdio')
                config = request.form.get('config', '{}')
                
                if not name:
                    flash('Plugin name is required', 'error')
                    return render_template('mcp/edit_plugin.html',
                                           fullname=session.get('fullname'),
                                           userid=session.get('user_id'),
                                           roles=session.get('roles', []),
                                           plugin=plugin,
                                           server_types=server_types)
                
                # Validate JSON config
                try:
                    config_dict = json.loads(config) if config else {}
                except json.JSONDecodeError:
                    flash('Invalid JSON configuration', 'error')
                    return render_template('mcp/edit_plugin.html',
                                           fullname=session.get('fullname'),
                                           userid=session.get('user_id'),
                                           roles=session.get('roles', []),
                                           plugin=plugin,
                                           server_types=server_types)
                
                try:
                    self.db_facade.execute(
                        """UPDATE mcp_plugins 
                           SET name = ?, description = ?, server_type = ?, config = ?,
                               updated_at = ?
                           WHERE plugin_id = ?""",
                        (name, description, server_type, json.dumps(config_dict),
                         datetime.now().isoformat(), plugin_id)
                    )
                    
                    self.log_audit('update_mcp_plugin', 'mcp_plugin', plugin_id)
                    flash(f'MCP plugin "{name}" updated successfully', 'success')
                    return redirect(url_for('mcp_plugin_detail', plugin_id=plugin_id))
                except Exception as e:
                    logger.error(f"Error updating MCP plugin: {e}")
                    flash('Failed to update MCP plugin', 'error')
            
            return render_template('mcp/edit_plugin.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   plugin=plugin,
                                   server_types=server_types)
        
        @self.app.route('/admin/mcp/plugins/<plugin_id>/activate', methods=['POST'])
        @admin_required
        def activate_mcp_plugin(plugin_id):
            """Activate an MCP plugin."""
            try:
                self.db_facade.execute(
                    "UPDATE mcp_plugins SET status = ?, updated_at = ? WHERE plugin_id = ?",
                    ('active', datetime.now().isoformat(), plugin_id)
                )
                self.log_audit('activate_mcp_plugin', 'mcp_plugin', plugin_id)
                flash('MCP plugin activated successfully', 'success')
            except Exception as e:
                logger.error(f"Error activating MCP plugin: {e}")
                flash('Failed to activate MCP plugin', 'error')
            
            return redirect(url_for('mcp_plugin_detail', plugin_id=plugin_id))
        
        @self.app.route('/admin/mcp/plugins/<plugin_id>/deactivate', methods=['POST'])
        @admin_required
        def deactivate_mcp_plugin(plugin_id):
            """Deactivate an MCP plugin."""
            try:
                self.db_facade.execute(
                    "UPDATE mcp_plugins SET status = ?, updated_at = ? WHERE plugin_id = ?",
                    ('inactive', datetime.now().isoformat(), plugin_id)
                )
                self.log_audit('deactivate_mcp_plugin', 'mcp_plugin', plugin_id)
                flash('MCP plugin deactivated successfully', 'success')
            except Exception as e:
                logger.error(f"Error deactivating MCP plugin: {e}")
                flash('Failed to deactivate MCP plugin', 'error')
            
            return redirect(url_for('mcp_plugin_detail', plugin_id=plugin_id))
        
        @self.app.route('/admin/mcp/plugins/<plugin_id>/delete', methods=['POST'])
        @admin_required
        def delete_mcp_plugin(plugin_id):
            """Delete an MCP plugin."""
            try:
                self.db_facade.execute(
                    "DELETE FROM mcp_plugins WHERE plugin_id = ?",
                    (plugin_id,)
                )
                self.log_audit('delete_mcp_plugin', 'mcp_plugin', plugin_id)
                flash('MCP plugin deleted successfully', 'success')
            except Exception as e:
                logger.error(f"Error deleting MCP plugin: {e}")
                flash('Failed to delete MCP plugin', 'error')
            
            return redirect(url_for('mcp_plugins'))
        
        logger.info("MCP routes registered")
