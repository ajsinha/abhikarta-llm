"""
Abstract Routes Module - Base class for all route handlers.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.
"""

from abc import ABC, abstractmethod
from functools import wraps
from flask import session, redirect, url_for, flash, request
import logging

logger = logging.getLogger(__name__)


class AbstractRoutes(ABC):
    """
    Abstract base class for route handlers.
    
    Provides common functionality for all route classes including
    facade management and utility methods.
    """
    
    def __init__(self, app):
        """
        Initialize route handler.
        
        Args:
            app: Flask application instance
        """
        self.app = app
        self.user_facade = None
        self.db_facade = None
        self.llm_facade = None
        self.mcp_facade = None
    
    def set_user_facade(self, user_facade):
        """Set user management facade."""
        self.user_facade = user_facade
    
    def set_db_facade(self, db_facade):
        """Set database facade."""
        self.db_facade = db_facade
    
    def set_llm_facade(self, llm_facade):
        """Set LLM facade."""
        self.llm_facade = llm_facade
    
    def set_mcp_facade(self, mcp_facade):
        """Set MCP facade."""
        self.mcp_facade = mcp_facade
    
    @abstractmethod
    def register_routes(self):
        """Register routes with Flask app. Must be implemented by subclasses."""
        pass
    
    def get_current_user(self):
        """Get current logged-in user from session."""
        user_id = session.get('user_id')
        if user_id and self.user_facade:
            return self.user_facade.get_user(user_id)
        return None
    
    def get_session_data(self):
        """Get common session data for templates."""
        return {
            'user_id': session.get('user_id'),
            'fullname': session.get('fullname'),
            'email': session.get('email'),
            'roles': session.get('roles', []),
            'is_admin': session.get('is_admin', False)
        }
    
    def log_audit(self, action: str, resource_type: str = None, 
                  resource_id: str = None, details: dict = None):
        """
        Log an audit event.
        
        Args:
            action: Action performed
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            details: Additional details
        """
        if self.db_facade:
            import json
            try:
                self.db_facade.audit.log_action(
                    action=action,
                    entity_type=resource_type,
                    entity_id=resource_id,
                    user_id=session.get('user_id'),
                    user_ip=request.remote_addr,
                    metadata=json.dumps(details) if details else '{}'
                )
            except Exception as e:
                logger.error(f"Error logging audit: {e}", exc_info=True)


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
        if 'user_id' not in session:
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
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        
        if not session.get('is_admin', False):
            flash('You do not have permission to access this page', 'error')
            logger.warning(
                f"User {session.get('user_id')} attempted to access admin page without permission"
            )
            return redirect(url_for('user_dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """
    Decorator to require specific roles for a route.
    
    Args:
        roles: Required role names
        
    Returns:
        Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login to access this page', 'warning')
                return redirect(url_for('login'))
            
            user_roles = session.get('roles', [])
            
            # Check if user has any of the required roles
            if not any(role in user_roles for role in roles):
                flash('You do not have permission to access this page', 'error')
                logger.warning(
                    f"User {session.get('user_id')} lacks required roles: {roles}"
                )
                return redirect(url_for('user_dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
