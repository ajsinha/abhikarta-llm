"""
Flask Application Factory Module.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.
"""

from flask import Flask
import logging
import os

logger = logging.getLogger(__name__)


def create_app(settings):
    """
    Application factory for creating Flask app.
    
    Args:
        settings: Settings object with configuration
        
    Returns:
        Configured Flask application
    """
    # Get the directory where this file is located
    web_dir = os.path.dirname(os.path.abspath(__file__))
    
    app = Flask(
        __name__,
        template_folder=os.path.join(web_dir, 'templates'),
        static_folder=os.path.join(web_dir, 'static')
    )
    
    # Configure app
    app.secret_key = settings.secret_key
    app.config['DEBUG'] = settings.debug
    app.config['APP_NAME'] = settings.app_name
    app.config['APP_VERSION'] = settings.app_version
    
    # Store settings in app config
    app.config['SETTINGS'] = settings
    
    # Initialize facades
    from ..user_management import UserFacade
    from ..database import DatabaseFacade
    
    user_facade = UserFacade(settings.users_file)
    db_facade = DatabaseFacade(settings)
    
    # Connect to database and initialize schema
    db_facade.connect()
    db_facade.init_schema()
    
    # Store facades in app config
    app.config['USER_FACADE'] = user_facade
    app.config['DB_FACADE'] = db_facade
    
    # Register routes
    _register_routes(app, user_facade, db_facade)
    
    # Register template context
    _register_context_processors(app, settings)
    
    # Register error handlers
    _register_error_handlers(app)
    
    logger.info(f"Flask application created: {settings.app_name} v{settings.app_version}")
    
    return app


def _register_routes(app, user_facade, db_facade):
    """Register all route blueprints."""
    from .routes import (
        AuthRoutes,
        AdminRoutes,
        UserRoutes,
        AgentRoutes,
        MCPRoutes,
        APIRoutes,
        AIORGRoutes,
        WorkflowRoutes,
        HITLRoutes
    )
    
    # Create route handlers
    route_handlers = [
        AuthRoutes(app),
        AdminRoutes(app),
        UserRoutes(app),
        AgentRoutes(app),
        MCPRoutes(app),
        APIRoutes(app),
        AIORGRoutes(app),
        WorkflowRoutes(app),
        HITLRoutes(app)
    ]
    
    # Set facades and register routes
    for handler in route_handlers:
        handler.set_user_facade(user_facade)
        handler.set_db_facade(db_facade)
        handler.register_routes()
    
    logger.info("Routes registered")


def _register_context_processors(app, settings):
    """Register template context processors."""
    from datetime import datetime
    
    @app.context_processor
    def inject_globals():
        """Inject global variables into templates."""
        return {
            'app_name': settings.app_name,
            'app_version': settings.app_version
        }
    
    @app.template_filter('format_datetime')
    def format_datetime_filter(value, format='%Y-%m-%d %H:%M'):
        """
        Format a datetime value for display.
        Handles both datetime objects and strings.
        """
        if value is None:
            return '-'
        
        if isinstance(value, datetime):
            return value.strftime(format)
        
        if isinstance(value, str):
            # Return the appropriate slice based on format
            if format == '%Y-%m-%d' or len(format) <= 10:
                return value[:10] if len(value) >= 10 else value
            elif format == '%Y-%m-%d %H:%M':
                return value[:16] if len(value) >= 16 else value
            else:
                return value[:19] if len(value) >= 19 else value
        
        return str(value)
    
    @app.template_filter('dt')
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


def _register_error_handlers(app):
    """Register error handlers."""
    from flask import render_template
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
