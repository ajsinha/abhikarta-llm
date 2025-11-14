from abc import ABC, abstractmethod
from functools import wraps
from flask import render_template, request, redirect, url_for, session, flash
import logging
from tool_management.mcp_server_manager import MCPServerManager
logger = logging.getLogger(__name__)

class AbstractRoutes(ABC):

    def __init__(self, app, db_connection_pool_name: str):
        self.app = app
        self.db_connection_pool_name = db_connection_pool_name
        self.user_manager = None
        self.role_manager = None
        self.resource_manager = None
        self.mcp_server_manager = MCPServerManager()

    def set_user_manager(self, user_manager):
        self.user_manager = user_manager

    def set_role_manager(self,role_manager):
        self.role_manager = role_manager

    def set_resource_manager(self, resource_manager):
        self.resource_manager = resource_manager

    @abstractmethod
    def register_routes(self):
        pass


def login_required(f):
    """
    Decorator to require login for a route.

    Args:
        f: Function to wrap

    Returns:
        Wrapped function
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'userid' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    Decorator to require admin role for a route.

    Args:
        f: Function to wrap

    Returns:
        Wrapped function
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'userid' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))

        if not session.get('is_admin', False):
            flash('You do not have permission to access this page', 'error')
            logger.warning(f"User {session.get('userid')} attempted to access admin page without permission")
            return redirect(url_for('user_dashboard'))

        return f(*args, **kwargs)

    return decorated_function
