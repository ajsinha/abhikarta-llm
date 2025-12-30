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
        AIORGRoutes
    )
    
    # Create route handlers
    route_handlers = [
        AuthRoutes(app),
        AdminRoutes(app),
        UserRoutes(app),
        AgentRoutes(app),
        MCPRoutes(app),
        APIRoutes(app),
        AIORGRoutes(app)
    ]
    
    # Set facades and register routes
    for handler in route_handlers:
        handler.set_user_facade(user_facade)
        handler.set_db_facade(db_facade)
        handler.register_routes()
    
    logger.info("Routes registered")


def _register_context_processors(app, settings):
    """Register template context processors."""
    
    @app.context_processor
    def inject_globals():
        """Inject global variables into templates."""
        return {
            'app_name': settings.app_name,
            'app_version': settings.app_version
        }


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
