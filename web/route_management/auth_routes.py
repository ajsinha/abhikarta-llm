"""
Authentication Routes Module - Handles login, logout, and authentication

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
from web.route_management.abstract_routes import admin_required,login_required
import logging
from typing import Optional
from user_management.user_manager import UserManager
from user_management.user import User
from web.route_management.abstract_routes import AbstractRoutes

logger = logging.getLogger(__name__)


class AuthRoutes(AbstractRoutes):
    """
    Handles authentication-related routes for the application.
    
    This class manages login, logout, and session management functionality.
    
    Attributes:
        app: Flask application instance
        user_manager: UserManager instance for user operations
    """
    
    def __init__(self, app):
        """
        Initialize AuthRoutes.
        
        Args:
            app: Flask application instance
            user_manager: UserManager instance for database operations
        """
        super().__init__(app)


        logger.info("AuthRoutes initialized")
    
    def register_routes(self):
        """Register all authentication routes."""
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            """Handle user login."""
            # If already logged in, redirect to appropriate dashboard
            if 'userid' in session:
                if session.get('is_admin', False):
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('user_dashboard'))
            
            if request.method == 'POST':
                userid = request.form.get('userid', '').strip()
                password = request.form.get('password', '')
                
                # Validate input
                if not userid or not password:
                    flash('Please provide both User ID and password', 'error')
                    return render_template('login.html')
                
                # Authenticate user
                user = self._authenticate_user(userid, password)
                
                if user:
                    # Update last login
                    user.update_last_login()
                    self.user_manager.save_user(user)
                    
                    # Set session variables
                    session['userid'] = user.userid
                    session['fullname'] = user.fullname
                    session['email'] = user.emailaddress
                    session['roles'] = user.roles
                    session['is_admin'] = user.has_role('admin')
                    
                    logger.info(f"User {userid} logged in successfully")
                    
                    # Redirect based on role
                    if session['is_admin']:
                        return redirect(url_for('admin_dashboard'))
                    else:
                        return redirect(url_for('user_dashboard'))
                else:
                    flash('Invalid User ID or password', 'error')
                    logger.warning(f"Failed login attempt for user: {userid}")
            
            return render_template('login.html')
        
        @self.app.route('/logout')
        def logout():
            """Handle user logout."""
            userid = session.get('userid', 'unknown')
            session.clear()
            flash('You have been logged out successfully', 'success')
            logger.info(f"User {userid} logged out")
            return redirect(url_for('login'))
        
        @self.app.route('/user/dashboard')
        @login_required
        def user_dashboard():
            """User dashboard for non-admin users."""
            if 'userid' not in session:
                flash('Please login to access the dashboard', 'warning')
                return redirect(url_for('login'))
            
            return render_template('user_dashboard.html',
                                 fullname=session.get('fullname'),
                                 userid=session.get('userid'),
                                 roles=session.get('roles', []))
        
        logger.info("Authentication routes registered")
    
    def _authenticate_user(self, userid: str, password: str) -> Optional[User]:
        """
        Authenticate a user with userid and password.
        
        Args:
            userid: User ID
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        try:
            # Load user from database
            user = self.user_manager.load_user(userid)
            
            if not user:
                logger.warning(f"User {userid} not found")
                return None
            
            # Check if user is enabled
            if not user.enabled:
                logger.warning(f"User {userid} is disabled")
                return None
            
            # Verify password
            if not user.verify_password(password):
                logger.warning(f"Invalid password for user {userid}")
                return None
            
            return user
            
        except Exception as e:
            logger.error(f"Error authenticating user {userid}: {e}")
            return None

