"""
Abhikarta LLM Web Application - Main Flask Application

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

from flask import Flask, render_template, redirect, url_for
from flask_session import Session
import logging
import os
from typing import Optional
from web.route_management.abstract_routes import AbstractRoutes
from tool_management.mcp_server_manager import MCPServerManager
from core.config.properties_configurator import PropertiesConfigurator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AbhikartaLLMWeb:
    """
    Main Flask application class for Abhikarta LLM Web Interface.
    
    This class encapsulates the Flask application and manages route registration
    for different modules (authentication, admin, user).
    
    Attributes:
        app: Flask application instance
        user_manager: UserManager instance for user operations
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize the Abhikarta LLM Web Application.
        
        Args:
            secret_key: Secret key for session management (generated if not provided)
        """
        self.app = Flask(__name__, 
                        template_folder='templates',
                        static_folder='static')
        self.prop_conf = PropertiesConfigurator()
        self.flask_session_folder = self.prop_conf.get('flask.session.dir','/tmp/flask_session')
        self.user_manager = None
        self.role_manager = None
        self.resource_manager = None
        self.db_connection_pool_name = None
        self.mcp_server_manager = MCPServerManager()

        # Configure application
        self.app.config['SECRET_KEY'] = secret_key or os.urandom(24).hex()
        self.app.config['SESSION_TYPE'] = 'filesystem'
        self.app.config['SESSION_PERMANENT'] = False
        self.app.config['SESSION_USE_SIGNER'] = True
        self.app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

        # Core session configuration
        self.app.config['SESSION_FILE_DIR'] =  self.flask_session_folder # Where to store session files
        self.app.config['SESSION_FILE_THRESHOLD'] = 5000  # Max number of sessions before cleanup
        self.app.config['SESSION_FILE_MODE'] = 0o600  # File permissions (default)

        # Initialize session
        Session(self.app)
        
        self.cleanup_sessions()
        logger.info("Abhikarta LLM Web Application initialized")

    def cleanup_sessions(self):
        """
        Clean up Flask session files.

        Args:
            session_dir: Directory containing Flask session files
        """
        session_path = os.path.join(os.getcwd(), self.flask_session_folder)

        if not os.path.exists(session_path):
            logger.info(f"Session directory {session_path} does not exist. Nothing to clean.")
            return

        try:
            # Remove all files in the session directory
            file_count = 0
            for filename in os.listdir(session_path):
                file_path = os.path.join(session_path, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    file_count += 1
                    logger.debug(f"Removed session file: {filename}")

            logger.info(f"Successfully cleaned up {file_count} session file(s) from {session_path}")

        except Exception as e:
            logger.error(f"Error cleaning up session files: {e}")
            raise

    def set_db_connection_pool_name(self, db_connection_pool_name):
        self.db_connection_pool_name = db_connection_pool_name

    def set_user_manager(self, user_manager):
        self.user_manager = user_manager
        # Initialize user manager
        if not self.user_manager._initialized:
            if not self.user_manager.initialize():
                raise RuntimeError("Failed to initialize UserManager")
    def set_role_manager(self,role_manager):
        self.role_manager = role_manager

    def set_resource_manager(self, resource_manager):
        self.resource_manager = resource_manager

    def prepare_routes(self):
        # Register routes
        self._register_routes()
        self._register_error_handlers()

    def _prepare_a_route(self, routes_object: AbstractRoutes):
        routes_object.set_role_manager(self.role_manager)
        routes_object.set_user_manager(self.user_manager)
        routes_object.set_resource_manager(self.resource_manager)
        routes_object.register_routes()

    def _register_routes(self):
        """Register all route modules."""
        from web.route_management.auth_routes import AuthRoutes
        from web.route_management.admin_routes import AdminRoutes
        from web.route_management.resource_routes import ResourceRoutes
        from web.route_management.role_routes import RoleRoutes
        from web.route_management.user_routes import UserRoutes
        from web.route_management.model_routes import ModelRoutes

        for rt in [AuthRoutes, AdminRoutes, ResourceRoutes, RoleRoutes, UserRoutes, ModelRoutes]:
            # Register route handler
            logger.info(f'registering route using {rt}')
            r_rt = rt(self.app, self.db_connection_pool_name)
            self._prepare_a_route(r_rt)



        # Register home route
        @self.app.route('/')
        def index():
            """Redirect to login page."""
            return redirect(url_for('login'))
        
        logger.info("All routes registered successfully")
    
    def _register_error_handlers(self):
        """Register error handlers for the application."""
        
        @self.app.errorhandler(404)
        def not_found(error):
            """Handle 404 errors."""
            return render_template('error.html', 
                                 error_code=404,
                                 error_message="Page not found"), 404
        
        @self.app.errorhandler(403)
        def forbidden(error):
            """Handle 403 errors."""
            return render_template('error.html',
                                 error_code=403,
                                 error_message="Access forbidden"), 403
        
        @self.app.errorhandler(500)
        def internal_error(error):
            """Handle 500 errors."""
            logger.error(f"Internal server error: {error}")
            return render_template('error.html',
                                 error_code=500,
                                 error_message="Internal server error"), 500
        
        logger.info("Error handlers registered")
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """
        Run the Flask application.
        
        Args:
            host: Host address to bind to
            port: Port number to listen on
            debug: Enable debug mode
        """
        logger.info(f"Starting Abhikarta LLM Web Application on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)
    
    def get_app(self):
        """
        Get the Flask application instance.
        
        Returns:
            Flask application instance
        """
        return self.app


