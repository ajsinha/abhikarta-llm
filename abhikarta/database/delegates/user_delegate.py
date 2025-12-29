"""
User Delegate - Database operations for Users, Roles, Sessions, API Keys.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Version: 1.3.0
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid
import logging

from ..database_delegate import DatabaseDelegate

logger = logging.getLogger(__name__)


class UserDelegate(DatabaseDelegate):
    """
    Delegate for user-related database operations.
    
    Handles tables: users, roles, user_roles, sessions, api_keys
    """
    
    # =========================================================================
    # USERS
    # =========================================================================
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by user_id."""
        return self.fetch_one(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email."""
        return self.fetch_one(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        )
    
    def get_all_users(self, active_only: bool = False) -> List[Dict]:
        """Get all users."""
        query = "SELECT * FROM users"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY created_at DESC"
        return self.fetch_all(query) or []
    
    def get_users_count(self, active_only: bool = False) -> int:
        """Get count of users."""
        where = "is_active = 1" if active_only else None
        return self.get_count("users", where)
    
    def create_user(self, user_id: str, password_hash: str, fullname: str,
                    email: str = None, is_active: int = 1,
                    preferences: str = '{}') -> bool:
        """Create a new user."""
        try:
            self.execute(
                """INSERT INTO users 
                   (user_id, password_hash, fullname, email, is_active, preferences)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, password_hash, fullname, email, is_active, preferences)
            )
            return True
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False
    
    def update_user(self, user_id: str, **kwargs) -> bool:
        """Update user fields."""
        if not kwargs:
            return False
        
        valid_fields = ['password_hash', 'fullname', 'email', 'is_active', 
                        'preferences', 'failed_login_attempts', 'locked_until']
        
        updates = []
        params = []
        for key, value in kwargs.items():
            if key in valid_fields:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if not updates:
            return False
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?"
        
        try:
            self.execute(query, tuple(params))
            return True
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        try:
            self.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            return True
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False
    
    def update_last_login(self, user_id: str) -> bool:
        """Update last login timestamp."""
        try:
            self.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP, failed_login_attempts = 0 WHERE user_id = ?",
                (user_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
            return False
    
    def increment_failed_login(self, user_id: str) -> int:
        """Increment failed login attempts and return new count."""
        try:
            self.execute(
                "UPDATE users SET failed_login_attempts = failed_login_attempts + 1 WHERE user_id = ?",
                (user_id,)
            )
            user = self.get_user_by_id(user_id)
            return user.get('failed_login_attempts', 0) if user else 0
        except Exception as e:
            logger.error(f"Error incrementing failed login: {e}")
            return 0
    
    def lock_user(self, user_id: str, until: datetime) -> bool:
        """Lock user account until specified time."""
        try:
            self.execute(
                "UPDATE users SET locked_until = ? WHERE user_id = ?",
                (until.isoformat(), user_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error locking user: {e}")
            return False
    
    def user_exists(self, user_id: str) -> bool:
        """Check if user exists."""
        return self.exists("users", "user_id = ?", (user_id,))
    
    # =========================================================================
    # ROLES
    # =========================================================================
    
    def get_all_roles(self) -> List[Dict]:
        """Get all roles."""
        return self.fetch_all("SELECT * FROM roles ORDER BY role_name") or []
    
    def get_role(self, role_name: str) -> Optional[Dict]:
        """Get role by name."""
        return self.fetch_one(
            "SELECT * FROM roles WHERE role_name = ?",
            (role_name,)
        )
    
    def create_role(self, role_name: str, display_name: str,
                    description: str = None, permissions: str = '[]',
                    is_system: int = 0) -> bool:
        """Create a new role."""
        try:
            self.execute(
                """INSERT INTO roles 
                   (role_name, display_name, description, permissions, is_system)
                   VALUES (?, ?, ?, ?, ?)""",
                (role_name, display_name, description, permissions, is_system)
            )
            return True
        except Exception as e:
            logger.error(f"Error creating role: {e}")
            return False
    
    def role_exists(self, role_name: str) -> bool:
        """Check if role exists."""
        return self.exists("roles", "role_name = ?", (role_name,))
    
    # =========================================================================
    # USER ROLES
    # =========================================================================
    
    def get_user_roles(self, user_id: str) -> List[Dict]:
        """Get all roles for a user."""
        return self.fetch_all(
            """SELECT r.* FROM roles r
               INNER JOIN user_roles ur ON r.role_name = ur.role_name
               WHERE ur.user_id = ?""",
            (user_id,)
        ) or []
    
    def get_user_role_names(self, user_id: str) -> List[str]:
        """Get role names for a user."""
        roles = self.fetch_all(
            "SELECT role_name FROM user_roles WHERE user_id = ?",
            (user_id,)
        ) or []
        return [r['role_name'] for r in roles]
    
    def assign_role(self, user_id: str, role_name: str, assigned_by: str = None) -> bool:
        """Assign a role to a user."""
        try:
            self.execute(
                """INSERT OR IGNORE INTO user_roles 
                   (user_id, role_name, assigned_by)
                   VALUES (?, ?, ?)""",
                (user_id, role_name, assigned_by)
            )
            return True
        except Exception as e:
            logger.error(f"Error assigning role: {e}")
            return False
    
    def remove_role(self, user_id: str, role_name: str) -> bool:
        """Remove a role from a user."""
        try:
            self.execute(
                "DELETE FROM user_roles WHERE user_id = ? AND role_name = ?",
                (user_id, role_name)
            )
            return True
        except Exception as e:
            logger.error(f"Error removing role: {e}")
            return False
    
    def remove_all_roles(self, user_id: str) -> bool:
        """Remove all roles from a user."""
        try:
            self.execute("DELETE FROM user_roles WHERE user_id = ?", (user_id,))
            return True
        except Exception as e:
            logger.error(f"Error removing all roles: {e}")
            return False
    
    def user_has_role(self, user_id: str, role_name: str) -> bool:
        """Check if user has a specific role."""
        return self.exists(
            "user_roles",
            "user_id = ? AND role_name = ?",
            (user_id, role_name)
        )
    
    def user_is_admin(self, user_id: str) -> bool:
        """Check if user has admin role."""
        return self.user_has_role(user_id, 'super_admin') or \
               self.user_has_role(user_id, 'domain_admin')
    
    # =========================================================================
    # SESSIONS
    # =========================================================================
    
    def create_session(self, user_id: str, session_data: str = '{}',
                       ip_address: str = None, user_agent: str = None,
                       expires_at: str = None) -> Optional[str]:
        """Create a new session and return session_id."""
        session_id = str(uuid.uuid4())
        try:
            self.execute(
                """INSERT INTO sessions 
                   (session_id, user_id, session_data, ip_address, user_agent, expires_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (session_id, user_id, session_data, ip_address, user_agent, expires_at)
            )
            return session_id
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return None
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID."""
        return self.fetch_one(
            "SELECT * FROM sessions WHERE session_id = ? AND is_active = 1",
            (session_id,)
        )
    
    def get_user_sessions(self, user_id: str, active_only: bool = True) -> List[Dict]:
        """Get all sessions for a user."""
        query = "SELECT * FROM sessions WHERE user_id = ?"
        if active_only:
            query += " AND is_active = 1"
        query += " ORDER BY created_at DESC"
        return self.fetch_all(query, (user_id,)) or []
    
    def update_session_activity(self, session_id: str) -> bool:
        """Update session last activity timestamp."""
        try:
            self.execute(
                "UPDATE sessions SET last_activity = CURRENT_TIMESTAMP WHERE session_id = ?",
                (session_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error updating session activity: {e}")
            return False
    
    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a session."""
        try:
            self.execute(
                "UPDATE sessions SET is_active = 0 WHERE session_id = ?",
                (session_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error invalidating session: {e}")
            return False
    
    def invalidate_user_sessions(self, user_id: str) -> bool:
        """Invalidate all sessions for a user."""
        try:
            self.execute(
                "UPDATE sessions SET is_active = 0 WHERE user_id = ?",
                (user_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error invalidating user sessions: {e}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions. Returns count of deleted sessions."""
        try:
            result = self.fetch_one(
                "SELECT COUNT(*) as count FROM sessions WHERE expires_at < CURRENT_TIMESTAMP"
            )
            count = result.get('count', 0) if result else 0
            self.execute(
                "DELETE FROM sessions WHERE expires_at < CURRENT_TIMESTAMP"
            )
            return count
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {e}")
            return 0
    
    # =========================================================================
    # API KEYS
    # =========================================================================
    
    def create_api_key(self, user_id: str, key_hash: str, name: str,
                       description: str = None, permissions: str = '[]',
                       rate_limit: int = 1000, expires_at: str = None) -> Optional[str]:
        """Create a new API key and return key_id."""
        key_id = str(uuid.uuid4())
        try:
            self.execute(
                """INSERT INTO api_keys 
                   (key_id, user_id, key_hash, name, description, permissions, rate_limit, expires_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (key_id, user_id, key_hash, name, description, permissions, rate_limit, expires_at)
            )
            return key_id
        except Exception as e:
            logger.error(f"Error creating API key: {e}")
            return None
    
    def get_api_key(self, key_id: str) -> Optional[Dict]:
        """Get API key by ID."""
        return self.fetch_one(
            "SELECT * FROM api_keys WHERE key_id = ?",
            (key_id,)
        )
    
    def get_api_key_by_hash(self, key_hash: str) -> Optional[Dict]:
        """Get API key by hash."""
        return self.fetch_one(
            "SELECT * FROM api_keys WHERE key_hash = ? AND is_active = 1",
            (key_hash,)
        )
    
    def get_user_api_keys(self, user_id: str) -> List[Dict]:
        """Get all API keys for a user."""
        return self.fetch_all(
            "SELECT * FROM api_keys WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        ) or []
    
    def update_api_key_usage(self, key_id: str) -> bool:
        """Update API key last used timestamp and increment usage count."""
        try:
            self.execute(
                """UPDATE api_keys 
                   SET last_used_at = CURRENT_TIMESTAMP, usage_count = usage_count + 1 
                   WHERE key_id = ?""",
                (key_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error updating API key usage: {e}")
            return False
    
    def deactivate_api_key(self, key_id: str) -> bool:
        """Deactivate an API key."""
        try:
            self.execute(
                "UPDATE api_keys SET is_active = 0 WHERE key_id = ?",
                (key_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error deactivating API key: {e}")
            return False
    
    def delete_api_key(self, key_id: str) -> bool:
        """Delete an API key."""
        try:
            self.execute("DELETE FROM api_keys WHERE key_id = ?", (key_id,))
            return True
        except Exception as e:
            logger.error(f"Error deleting API key: {e}")
            return False
