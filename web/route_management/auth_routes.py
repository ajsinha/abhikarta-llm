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
from web.route_management.abstract_routes import admin_required, login_required
import logging
from typing import Optional
from user_management.user_manager import UserManager
from user_management.user import User
from web.route_management.abstract_routes import AbstractRoutes

logger = logging.getLogger(__name__)


class AuthRoutes(AbstractRoutes):
    """
    Handles authentication-related routes for the application.

    This class manages login, logout, session management, and password management.

    Attributes:
        app: Flask application instance
        user_manager: UserManager instance for user operations
    """

    def __init__(self, app, db_connection_pool_name: str):
        """
        Initialize AuthRoutes.

        Args:
            app: Flask application instance
        """
        super().__init__(app, db_connection_pool_name)
        logger.info("AuthRoutes initialized")

    def register_routes(self):
        """Register all authentication routes."""

        @self.app.route('/about', methods=['GET'])
        def about():
            """
            Render the About page with platform information, copyright, and legal disclaimers.

            This page is publicly accessible and does not require authentication.
            """
            logger.info("About page accessed")

            # Get user info if logged in, otherwise use default values
            fullname = session.get('fullname', 'Guest')
            userid = session.get('userid', None)
            roles = session.get('roles', [])

            return render_template('about.html',
                                   fullname=fullname,
                                   userid=userid,
                                   roles=roles)

        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            """Handle user login with password validation."""
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

                # Load user first to check password status
                user = self.user_manager.load_user(userid)

                if not user:
                    flash('Invalid User ID or password', 'error')
                    logger.warning(f"Failed login attempt for user: {userid}")
                    return render_template('login.html')

                # Check if user is enabled
                if not user.enabled:
                    flash('Your account has been disabled. Please contact administrator.', 'error')
                    logger.warning(f"Login attempt for disabled user: {userid}")
                    return render_template('login.html')

                # Check password validity (empty, None, or too short)
                if self._needs_password_setup(user):
                    # User needs to set password - create temporary session
                    session['temp_userid'] = userid
                    session['needs_password_setup'] = True
                    flash('You need to set up a password for your account', 'warning')
                    logger.info(f"User {userid} redirected to password setup")
                    return redirect(url_for('set_password'))

                # Authenticate user with password
                if not user.verify_password(password):
                    flash('Invalid User ID or password', 'error')
                    logger.warning(f"Invalid password for user: {userid}")
                    return render_template('login.html')

                # Successful login
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

            return render_template('login.html')

        @self.app.route('/set-password', methods=['GET', 'POST'])
        def set_password():
            """Handle initial password setup for users with no/weak passwords."""
            # Check if user is in temporary session (coming from login)
            if 'temp_userid' not in session or not session.get('needs_password_setup'):
                flash('Invalid access. Please login first.', 'error')
                return redirect(url_for('login'))

            temp_userid = session['temp_userid']

            if request.method == 'POST':
                new_password = request.form.get('new_password', '')
                confirm_password = request.form.get('confirm_password', '')

                # Validate passwords
                if not new_password or not confirm_password:
                    flash('Both password fields are required', 'error')
                    return render_template('rbac/set_password.html', userid=temp_userid)

                if len(new_password) < 8:
                    flash('Password must be at least 8 characters long', 'error')
                    return render_template('rbac/set_password.html', userid=temp_userid)

                if new_password != confirm_password:
                    flash('Passwords do not match', 'error')
                    return render_template('rbac/set_password.html', userid=temp_userid)

                # Load user and set password
                user = self.user_manager.load_user(temp_userid)
                if not user:
                    flash('User not found', 'error')
                    session.pop('temp_userid', None)
                    session.pop('needs_password_setup', None)
                    return redirect(url_for('login'))

                # Set new password
                user.set_password(new_password)
                user.update_last_login()

                # Save user
                if self.user_manager.save_user(user):
                    # Clear temporary session and create real session
                    session.pop('temp_userid', None)
                    session.pop('needs_password_setup', None)

                    # Set full session
                    session['userid'] = user.userid
                    session['fullname'] = user.fullname
                    session['email'] = user.emailaddress
                    session['roles'] = user.roles
                    session['is_admin'] = user.has_role('admin')

                    flash('Password set successfully! Welcome to the platform.', 'success')
                    logger.info(f"User {temp_userid} successfully set up password")

                    # Redirect based on role
                    if session['is_admin']:
                        return redirect(url_for('admin_dashboard'))
                    else:
                        return redirect(url_for('user_dashboard'))
                else:
                    flash('Failed to set password. Please try again.', 'error')
                    return render_template('rbac/set_password.html', userid=temp_userid)

            # GET request - show password setup form
            return render_template('rbac/set_password.html', userid=temp_userid)

        @self.app.route('/reset-password', methods=['GET', 'POST'])
        @login_required
        def reset_password():
            """Handle password reset for logged-in users."""
            userid = session.get('userid')

            if request.method == 'POST':
                current_password = request.form.get('current_password', '')
                new_password = request.form.get('new_password', '')
                confirm_password = request.form.get('confirm_password', '')

                # Validate inputs
                if not current_password or not new_password or not confirm_password:
                    flash('All password fields are required', 'error')
                    return render_template('rbac/reset_password.html')

                if len(new_password) < 8:
                    flash('New password must be at least 8 characters long', 'error')
                    return render_template('rbac/reset_password.html')

                if new_password != confirm_password:
                    flash('New passwords do not match', 'error')
                    return render_template('rbac/reset_password.html')

                # Load user
                user = self.user_manager.load_user(userid)
                if not user:
                    flash('User not found', 'error')
                    return redirect(url_for('logout'))

                # Verify current password
                if not user.verify_password(current_password):
                    flash('Current password is incorrect', 'error')
                    logger.warning(f"Failed password reset attempt for user {userid}: incorrect current password")
                    return render_template('rbac/reset_password.html')

                # Check if new password is same as current
                if user.verify_password(new_password):
                    flash('New password must be different from current password', 'warning')
                    return render_template('rbac/reset_password.html')

                # Set new password
                user.set_password(new_password)

                # Save user
                if self.user_manager.save_user(user):
                    flash('Password reset successfully!', 'success')
                    logger.info(f"User {userid} successfully reset password")

                    # Redirect back to dashboard
                    if session.get('is_admin'):
                        return redirect(url_for('admin_dashboard'))
                    else:
                        return redirect(url_for('user_dashboard'))
                else:
                    flash('Failed to reset password. Please try again.', 'error')
                    return render_template('rbac/reset_password.html')

            # GET request - show password reset form
            return render_template('rbac/reset_password.html')

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

    def _needs_password_setup(self, user: User) -> bool:
        """
        Check if user needs to set up a password.

        A user needs password setup if:
        - Password hash is None
        - Password hash is empty string
        - Password hash is less than 3 characters

        Args:
            user: User object to check

        Returns:
            True if user needs password setup, False otherwise
        """
        if not user.password_hash:
            return True

        if isinstance(user.password_hash, str) and len(user.password_hash) < 3:
            return True

        return False

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