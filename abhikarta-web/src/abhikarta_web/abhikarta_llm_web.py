"""
Abhikarta LLM Web Application - Main Flask Application Class

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

from flask import Flask, render_template
import logging
import os
from typing import Optional
from datetime import datetime

from abhikarta.core.config import PropertiesConfigurator

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
    for different modules (authentication, admin, user, agents, etc.).

    Attributes:
        app: Flask application instance
        user_facade: UserFacade instance for user operations
        db_facade: DatabaseFacade instance for database operations
        prop_conf: PropertiesConfigurator instance for configuration
    """

    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize the Abhikarta LLM Web Application.

        Args:
            secret_key: Secret key for session management (generated if not provided)
        """
        # Get web module directory for template and static paths
        web_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.app = Flask(
            __name__,
            template_folder=os.path.join(web_dir, 'templates'),
            static_folder=os.path.join(web_dir, 'static')
        )
        
        # Get properties configurator (singleton)
        self.prop_conf = PropertiesConfigurator()
        
        # Initialize managers
        self.user_facade = None
        self.db_facade = None
        self.llm_facade = None
        self.mcp_facade = None
        
        # Configure application
        self.app.config['SECRET_KEY'] = secret_key or self.prop_conf.get(
            'app.secret.key', 
            os.urandom(24).hex()
        )
        self.app.config['SESSION_TYPE'] = 'filesystem'
        self.app.config['SESSION_PERMANENT'] = False
        self.app.config['PERMANENT_SESSION_LIFETIME'] = self.prop_conf.get_int(
            'session.lifetime.seconds', 3600
        )
        
        # Application metadata
        self.app.config['APP_NAME'] = self.prop_conf.get('app.name', 'Abhikarta-LLM')
        self.app.config['APP_VERSION'] = self.prop_conf.get('app.version', '1.0.0')
        
        # Session directory
        session_dir = self.prop_conf.get('flask.session.dir', './data/flask_session')
        os.makedirs(session_dir, exist_ok=True)
        self.app.config['SESSION_FILE_DIR'] = session_dir
        
        # Register template context processors
        self._register_context_processors()
        
        # Register template filters
        self._register_template_filters()
        
        logger.info("Abhikarta LLM Web Application initialized")

    def set_user_facade(self, user_facade):
        """Set the user management facade."""
        self.user_facade = user_facade
        logger.info("User facade set")

    def set_db_facade(self, db_facade):
        """Set the database facade."""
        self.db_facade = db_facade
        logger.info("Database facade set")

    def set_llm_facade(self, llm_facade):
        """Set the LLM facade."""
        self.llm_facade = llm_facade
        logger.info("LLM facade set")

    def set_mcp_facade(self, mcp_facade):
        """Set the MCP facade."""
        self.mcp_facade = mcp_facade
        logger.info("MCP facade set")

    def prepare_routes(self):
        """Prepare and register all routes."""
        self._register_routes()
        self._register_error_handlers()
        logger.info("Routes prepared successfully")

    def _register_context_processors(self):
        """Register template context processors for global variables."""
        
        @self.app.context_processor
        def inject_globals():
            """Inject global variables into all templates."""
            return {
                'app_name': self.app.config.get('APP_NAME', 'Abhikarta-LLM'),
                'app_version': self.app.config.get('APP_VERSION', '1.0.0'),
                'current_year': datetime.now().year,
                'prop_conf': self.prop_conf
            }

    def _register_template_filters(self):
        """Register custom Jinja2 template filters."""
        
        @self.app.template_filter('datetime')
        def format_datetime(value, format_str='%Y-%m-%d %H:%M:%S'):
            """Format datetime object."""
            if value is None:
                return ''
            if isinstance(value, str):
                try:
                    value = datetime.fromisoformat(value)
                except:
                    return value
            return value.strftime(format_str)
        
        @self.app.template_filter('dt')
        def dt_filter(value, length=16):
            """
            Short filter to format datetime - handles strings and datetime objects.
            Usage: {{ task.created_at|dt }} or {{ task.created_at|dt(10) }}
            """
            if value is None:
                return '-'
            
            if isinstance(value, datetime):
                if length <= 10:
                    return value.strftime('%Y-%m-%d')
                elif length <= 16:
                    return value.strftime('%Y-%m-%d %H:%M')
                else:
                    return value.strftime('%Y-%m-%d %H:%M:%S')
            
            if isinstance(value, str):
                return value[:length] if len(value) >= length else value
            
            return str(value)
        
        @self.app.template_filter('truncate_text')
        def truncate_text(text, length=100, suffix='...'):
            """Truncate text to specified length."""
            if not text:
                return ''
            if len(text) <= length:
                return text
            return text[:length - len(suffix)] + suffix
        
        @self.app.template_filter('json_pretty')
        def json_pretty(value):
            """Pretty print JSON."""
            import json
            try:
                if isinstance(value, str):
                    value = json.loads(value)
                return json.dumps(value, indent=2, default=str)
            except:
                return str(value)

    def _register_routes(self):
        """Register all route modules."""
        from .routes import (
            AuthRoutes,
            AdminRoutes,
            UserRoutes,
            AgentRoutes,
            MCPRoutes,
            APIRoutes,
            WorkflowRoutes,
            AIORGRoutes,  # v1.4.7
            ScriptRoutes  # v1.4.8
        )
        from .routes.swarm_routes import SwarmRoutes
        from .routes.notification_routes import NotificationRoutes  # v1.4.0
        from .routes.metrics_routes import init_metrics_routes  # v1.4.8 Prometheus
        from .routes.conversation_routes import ConversationRoutes  # v1.5.3 Chat Memory
        
        # Initialize Prometheus metrics routes first (uses different pattern)
        init_metrics_routes(self.app, self.prop_conf)
        logger.info("Prometheus metrics routes registered")
        
        # Route classes to register
        route_classes = [
            AuthRoutes,
            AdminRoutes,
            UserRoutes,
            AgentRoutes,
            MCPRoutes,
            APIRoutes,
            WorkflowRoutes,
            SwarmRoutes,  # v1.3.0
            NotificationRoutes,  # v1.4.0
            AIORGRoutes,  # v1.4.7
            ScriptRoutes  # v1.4.8
        ]
        
        for route_class in route_classes:
            logger.info(f'Registering routes: {route_class.__name__}')
            route_handler = route_class(self.app)
            
            # Set facades
            if self.user_facade:
                route_handler.set_user_facade(self.user_facade)
            if self.db_facade:
                route_handler.set_db_facade(self.db_facade)
            if self.llm_facade:
                route_handler.set_llm_facade(self.llm_facade)
            if self.mcp_facade:
                route_handler.set_mcp_facade(self.mcp_facade)
            
            # Register routes
            route_handler.register_routes()
        
        # Register conversation routes (v1.5.3 - different initialization pattern)
        if self.db_facade:
            ConversationRoutes(self.app, self.db_facade)
            logger.info("Registered conversation routes for chat memory")
        
        # Note: The index '/' route is registered in AuthRoutes
        
        logger.info("All routes registered successfully")

    def _register_error_handlers(self):
        """Register error handlers for the application."""
        
        @self.app.errorhandler(404)
        def not_found(error):
            """Handle 404 errors."""
            return render_template('errors/404.html',
                                   error_code=404,
                                   error_message="Page not found"), 404

        @self.app.errorhandler(403)
        def forbidden(error):
            """Handle 403 errors."""
            return render_template('errors/403.html',
                                   error_code=403,
                                   error_message="Access forbidden"), 403

        @self.app.errorhandler(500)
        def internal_error(error):
            """Handle 500 errors."""
            logger.error(f"Internal server error: {error}")
            return render_template('errors/500.html',
                                   error_code=500,
                                   error_message="Internal server error"), 500

        logger.info("Error handlers registered")

    def run(self, host: str = None, port: int = None, debug: bool = None):
        """
        Run the Flask application.

        Args:
            host: Host address to bind to (defaults to config or 0.0.0.0)
            port: Port number to listen on (defaults to config or 5000)
            debug: Enable debug mode (defaults to config or False)
        """
        # Get values from config if not provided
        if host is None:
            host = self.prop_conf.get('server.host', '0.0.0.0')
        if port is None:
            port = self.prop_conf.get_int('server.port', 5000)
        if debug is None:
            debug = self.prop_conf.get_bool('app.debug', False)
        
        logger.info(f"Starting Abhikarta LLM Web Application on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

    def get_app(self):
        """
        Get the Flask application instance.

        Returns:
            Flask application instance
        """
        return self.app
