"""
User Facade Module - User management via JSON file.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class UserFacade:
    """
    Facade for user management operations.
    Manages users through a JSON file (users.json).
    """
    
    def __init__(self, users_file: str):
        """
        Initialize user facade.
        
        Args:
            users_file: Path to users JSON file
        """
        self.users_file = Path(users_file)
        self._users: Dict[str, Dict] = {}
        self._load_users()
    
    def _load_users(self) -> None:
        """Load users from JSON file."""
        if self.users_file.exists():
            try:
                with open(self.users_file, 'r') as f:
                    data = json.load(f)
                    self._users = {u['user_id']: u for u in data.get('users', [])}
                logger.info(f"Loaded {len(self._users)} users from {self.users_file}")
            except Exception as e:
                logger.error(f"Error loading users file: {e}")
                self._users = {}
        else:
            logger.warning(f"Users file not found: {self.users_file}")
            self._create_default_users()
    
    def _create_default_users(self) -> None:
        """Create default users file with admin user."""
        default_users = {
            "users": [
                {
                    "user_id": "admin",
                    "password": "admin123",
                    "fullname": "System Administrator",
                    "email": "admin@abhikarta.local",
                    "roles": ["super_admin"],
                    "is_active": True,
                    "created_at": datetime.now().isoformat()
                },
                {
                    "user_id": "developer",
                    "password": "dev123",
                    "fullname": "Agent Developer",
                    "email": "developer@abhikarta.local",
                    "roles": ["agent_developer"],
                    "is_active": True,
                    "created_at": datetime.now().isoformat()
                },
                {
                    "user_id": "user",
                    "password": "user123",
                    "fullname": "Business User",
                    "email": "user@abhikarta.local",
                    "roles": ["agent_user"],
                    "is_active": True,
                    "created_at": datetime.now().isoformat()
                }
            ]
        }
        
        # Create directory if needed
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save default users
        with open(self.users_file, 'w') as f:
            json.dump(default_users, f, indent=2)
        
        self._users = {u['user_id']: u for u in default_users['users']}
        logger.info(f"Created default users file: {self.users_file}")
    
    def _save_users(self) -> None:
        """Save users to JSON file."""
        data = {'users': list(self._users.values())}
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.users_file, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(self._users)} users to {self.users_file}")
    
    def authenticate(self, user_id: str, password: str) -> Optional[Dict]:
        """
        Authenticate user with plain text password comparison.
        
        Args:
            user_id: User identifier
            password: Plain text password
            
        Returns:
            User dict (without password) if authenticated, None otherwise
        """
        user = self._users.get(user_id)
        
        if not user:
            logger.warning(f"Authentication failed - user not found: {user_id}")
            return None
        
        if not user.get('is_active', True):
            logger.warning(f"Authentication failed - user inactive: {user_id}")
            return None
        
        if user.get('password') != password:
            logger.warning(f"Authentication failed - invalid password: {user_id}")
            return None
        
        logger.info(f"User authenticated successfully: {user_id}")
        return self._user_without_password(user)
    
    def _user_without_password(self, user: Dict) -> Dict:
        """Return user dict without password field."""
        return {k: v for k, v in user.items() if k != 'password'}
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """
        Get user by ID.
        
        Args:
            user_id: User identifier
            
        Returns:
            User dict (without password) or None
        """
        user = self._users.get(user_id)
        return self._user_without_password(user) if user else None
    
    def list_users(self) -> List[Dict]:
        """
        List all users.
        
        Returns:
            List of user dicts (without passwords)
        """
        return [self._user_without_password(u) for u in self._users.values()]
    
    def create_user(self, user_data: Dict) -> bool:
        """
        Create a new user.
        
        Args:
            user_data: User data dictionary
            
        Returns:
            True if created, False if user exists
        """
        user_id = user_data.get('user_id')
        
        if not user_id:
            logger.error("Cannot create user without user_id")
            return False
        
        if user_id in self._users:
            logger.warning(f"User already exists: {user_id}")
            return False
        
        # Add timestamps
        user_data['created_at'] = datetime.now().isoformat()
        user_data['is_active'] = user_data.get('is_active', True)
        
        self._users[user_id] = user_data
        self._save_users()
        logger.info(f"User created: {user_id}")
        return True
    
    def update_user(self, user_id: str, user_data: Dict) -> bool:
        """
        Update an existing user.
        
        Args:
            user_id: User identifier
            user_data: Updated user data
            
        Returns:
            True if updated, False if user not found
        """
        if user_id not in self._users:
            logger.warning(f"User not found for update: {user_id}")
            return False
        
        # Update fields
        self._users[user_id].update(user_data)
        self._users[user_id]['updated_at'] = datetime.now().isoformat()
        
        self._save_users()
        logger.info(f"User updated: {user_id}")
        return True
    
    def delete_user(self, user_id: str, hard_delete: bool = False) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: User identifier
            hard_delete: If True, remove from file; else soft delete
            
        Returns:
            True if deleted, False if user not found
        """
        if user_id not in self._users:
            logger.warning(f"User not found for delete: {user_id}")
            return False
        
        if hard_delete:
            del self._users[user_id]
        else:
            self._users[user_id]['is_active'] = False
            self._users[user_id]['deleted_at'] = datetime.now().isoformat()
        
        self._save_users()
        logger.info(f"User {'deleted' if hard_delete else 'deactivated'}: {user_id}")
        return True
    
    def get_user_roles(self, user_id: str) -> List[str]:
        """
        Get roles for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of role names
        """
        user = self._users.get(user_id)
        return user.get('roles', []) if user else []
    
    def has_role(self, user_id: str, role: str) -> bool:
        """
        Check if user has a specific role.
        
        Args:
            user_id: User identifier
            role: Role name
            
        Returns:
            True if user has role
        """
        roles = self.get_user_roles(user_id)
        return role in roles
    
    def is_admin(self, user_id: str) -> bool:
        """
        Check if user is an admin (super_admin or domain_admin).
        
        Args:
            user_id: User identifier
            
        Returns:
            True if user is admin
        """
        roles = self.get_user_roles(user_id)
        return 'super_admin' in roles or 'domain_admin' in roles
    
    def add_role(self, user_id: str, role: str) -> bool:
        """
        Add a role to user.
        
        Args:
            user_id: User identifier
            role: Role name
            
        Returns:
            True if added
        """
        if user_id not in self._users:
            return False
        
        roles = self._users[user_id].get('roles', [])
        if role not in roles:
            roles.append(role)
            self._users[user_id]['roles'] = roles
            self._save_users()
            logger.info(f"Role '{role}' added to user: {user_id}")
        return True
    
    def remove_role(self, user_id: str, role: str) -> bool:
        """
        Remove a role from user.
        
        Args:
            user_id: User identifier
            role: Role name
            
        Returns:
            True if removed
        """
        if user_id not in self._users:
            return False
        
        roles = self._users[user_id].get('roles', [])
        if role in roles:
            roles.remove(role)
            self._users[user_id]['roles'] = roles
            self._save_users()
            logger.info(f"Role '{role}' removed from user: {user_id}")
        return True
    
    def change_password(self, user_id: str, new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            user_id: User identifier
            new_password: New password
            
        Returns:
            True if changed
        """
        if user_id not in self._users:
            return False
        
        self._users[user_id]['password'] = new_password
        self._users[user_id]['password_changed_at'] = datetime.now().isoformat()
        self._save_users()
        logger.info(f"Password changed for user: {user_id}")
        return True
    
    def reload(self) -> None:
        """Reload users from file."""
        self._load_users()
        logger.info("Users reloaded from file")
    
    def get_statistics(self) -> Dict:
        """
        Get user statistics.
        
        Returns:
            Statistics dictionary
        """
        active_users = sum(1 for u in self._users.values() if u.get('is_active', True))
        admins = sum(1 for u in self._users.values() 
                     if 'super_admin' in u.get('roles', []) or 'domain_admin' in u.get('roles', []))
        
        return {
            'total_users': len(self._users),
            'active_users': active_users,
            'inactive_users': len(self._users) - active_users,
            'admin_users': admins
        }
