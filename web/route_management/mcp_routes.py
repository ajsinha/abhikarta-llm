"""
MCP Routes Module - Handles admin-specific routes and functionality

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
from web.route_management.abstract_routes import admin_required
import logging
import json
from user_management.user_manager import UserManager
from web.route_management.abstract_routes import AbstractRoutes

logger = logging.getLogger(__name__)


class MCPRoutes(AbstractRoutes):
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


        logger.info("MCPRoutes initialized")

    def register_routes(self):
        """Register all mcp routes."""

        @self.app.route('/admin/mcp/server/<server_key>')
        @admin_required
        def mcp_server_details(server_key):
            """
            Display detailed information about a specific MCP server.

            Args:
                server_key: The unique key identifying the MCP server

            Returns:
                Rendered template with server details
            """
            try:
                # Get all server statuses
                if self.mcp_server_manager is None:
                    flash('MCP Server Manager not initialized', 'error')
                    return redirect(url_for('admin_dashboard'))

                mcp_status = self.mcp_server_manager.status_all()

                # Check if server exists
                if server_key not in mcp_status:
                    flash(f'MCP Server "{server_key}" not found', 'error')
                    logger.warning(f"Attempted to access non-existent MCP server: {server_key}")
                    return redirect(url_for('admin_dashboard'))

                # Get server information
                server_info = mcp_status[server_key]

                # Get tools for this server using the get_tools_for_server_proxy method
                try:
                    tools_dict = self.mcp_server_manager.get_tools_for_server_proxy(server_key)
                    # Convert dict of MCPToolSchema objects to list of dicts for template
                    tools = []
                    if tools_dict:
                        for tool_name, tool_schema in tools_dict.items():
                            tool_dict = {
                                'name': tool_schema.name,
                                'description': tool_schema.description,
                                'inputSchema': tool_schema.input_schema,
                                'outputSchema': tool_schema.output_schema
                            }
                            tools.append(tool_dict)
                    logger.info(f"Retrieved {len(tools)} tools for server: {server_key}")
                except Exception as e:
                    logger.error(f"Error retrieving tools for server {server_key}: {e}", exc_info=True)
                    tools = []

                # Convert server info to JSON for raw data display
                server_info_json = json.dumps(server_info, indent=2, default=str)

                logger.info(f"Admin {session.get('userid')} viewed details for MCP server: {server_key}")

                return render_template('mcp/mcp_server_details.html',
                                       fullname=session.get('fullname'),
                                       userid=session.get('userid'),
                                       roles=session.get('roles', []),
                                       server_key=server_key,
                                       server_info=server_info,
                                       server_info_json=server_info_json,
                                       tools=tools)

            except Exception as e:
                logger.error(f"Error retrieving MCP server details for {server_key}: {e}", exc_info=True)
                flash(f'Error retrieving server details: {str(e)}', 'error')
                return redirect(url_for('admin_dashboard'))

        @self.app.route('/admin/mcp/server/<server_key>/tool/<tool_name>')
        @admin_required
        def mcp_tool_details(server_key, tool_name):
            """
            Display detailed information about a specific tool from an MCP server.

            Args:
                server_key: The unique key identifying the MCP server
                tool_name: The name of the tool

            Returns:
                Rendered template with tool details
            """
            try:
                # Get all server statuses
                if self.mcp_server_manager is None:
                    flash('MCP Server Manager not initialized', 'error')
                    return redirect(url_for('admin_dashboard'))

                mcp_status = self.mcp_server_manager.status_all()

                # Check if server exists
                if server_key not in mcp_status:
                    flash(f'MCP Server "{server_key}" not found', 'error')
                    logger.warning(f"Attempted to access non-existent MCP server: {server_key}")
                    return redirect(url_for('admin_dashboard'))

                # Get server information
                server_info = mcp_status[server_key]

                # Get all tools for this server
                try:
                    tools_dict = self.mcp_server_manager.get_tools_for_server_proxy(server_key)

                    # Find the specific tool
                    tool_info = None
                    if tools_dict and tool_name in tools_dict:
                        tool_schema = tools_dict[tool_name]
                        tool_info = {
                            'name': tool_schema.name,
                            'description': tool_schema.description,
                            'inputSchema': tool_schema.input_schema,
                            'outputSchema': tool_schema.output_schema
                        }

                except Exception as e:
                    logger.error(f"Error retrieving tools for server {server_key}: {e}", exc_info=True)
                    flash(f'Error retrieving tools: {str(e)}', 'error')
                    return redirect(url_for('mcp_server_details', server_key=server_key))

                if tool_info is None:
                    flash(f'Tool "{tool_name}" not found in server "{server_key}"', 'error')
                    logger.warning(f"Attempted to access non-existent tool: {tool_name} in server: {server_key}")
                    return redirect(url_for('mcp_server_details', server_key=server_key))

                # Convert tool info to JSON for raw data display
                tool_info_json = json.dumps(tool_info, indent=2, default=str)

                logger.info(f"Admin {session.get('userid')} viewed details for tool: {tool_name} in server: {server_key}")

                return render_template('mcp/mcp_tool_details.html',
                                       fullname=session.get('fullname'),
                                       userid=session.get('userid'),
                                       roles=session.get('roles', []),
                                       server_key=server_key,
                                       server_name=server_info.get('name', server_key),
                                       tool_name=tool_name,
                                       tool_info=tool_info,
                                       tool_info_json=tool_info_json)

            except Exception as e:
                logger.error(f"Error retrieving tool details for {tool_name} in server {server_key}: {e}", exc_info=True)
                flash(f'Error retrieving tool details: {str(e)}', 'error')
                return redirect(url_for('mcp_server_details', server_key=server_key))