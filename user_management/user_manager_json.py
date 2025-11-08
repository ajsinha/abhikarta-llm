"""
User Manager JSON Module - JSON file-backed user management implementation.

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

import json
import logging
import os
import threading
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import shutil

from user_manager import UserManager
from user import User, Role, Resource, Permission

logger = logging.getLogger(__name__)


class UserManagerJSON(UserManager):
    """
    JSON file-backed implementation of UserManager.
    
    This implementation stores users, roles, and resources in a JSON file.
    Suitable for smaller deployments or development environments.
    
    Features:
    - Simple file-based storage
    - Thread-safe operations with file locking
    - Automatic backup on write
    - Auto-reload capability to detect external changes
    """
    
    def __init__(self, json_file_path: str = "config/users.json", auto_reload: bool = True):
        """
        Initialize the JSON-backed user manager.
        
        Args:
            json_file_path: Path to the JSON file
            auto_reload: Automatically reload if file changes externally
        """
        super().__init__()
        self._json_file_path = json_file_path
        self._auto_reload = auto_reload
        self._lock = threading.RLock()
        self._file_lock = threading.Lock()
        self._last_modified = None
        
        # In-memory cache
        self._users: Dict[str, User] = {}
        self._roles: Dict[str, Role] = {}
        self._resources: Dict[str, Resource] = {}
        
        logger.info(f"UserManagerJSON initialized with file: {json_file_path}")
    
    def _ensure_directory(self):
        """Ensure the directory for the JSON file exists."""
        directory = os.path.dirname(self._json_file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    def _check_and_reload(self):
        """Check if file has been modified and reload if necessary."""
        if not self._auto_reload or not os.path.exists(self._json_file_path):
            return
        
        try:
            current_modified = os.path.getmtime(self._json_file_path)
            if self._last_modified is None or current_modified > self._last_modified:
                logger.info("External file modification detected, reloading...")
                self._load_from_file()
        except Exception as e:
            logger.error(f"Failed to check file modification: {e}")
    
    def _load_from_file(self) -> bool:
        """Load data from JSON file into memory."""
        with self._file_lock:
            try:
                if not os.path.exists(self._json_file_path):
                    logger.info(f"JSON file not found: {self._json_file_path}")
                    # Initialize with empty data
                    self._users = {}
                    self._roles = {}
                    self._resources = {}
                    return True
                
                with open(self._json_file_path, 'r') as f:
                    data = json.load(f)
                
                # Load users
                self._users = {}
                for user_data in data.get('users', []):
                    user = User.from_dict(user_data)
                    self._users[user.userid] = user
                
                # Load roles
                self._roles = {}
                for role_data in data.get('roles', []):
                    role = Role.from_dict(role_data)
                    self._roles[role.name] = role
                
                # Load resources
                self._resources = {}
                for resource_data in data.get('resources', []):
                    resource = Resource.from_dict(resource_data)
                    self._resources[resource.name] = resource
                
                self._last_modified = os.path.getmtime(self._json_file_path)
                logger.info(f"Loaded {len(self._users)} users, {len(self._roles)} roles, "
                           f"{len(self._resources)} resources from {self._json_file_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to load from JSON file: {e}")
                return False
    
    def _save_to_file(self) -> bool:
        """Save data from memory to JSON file."""
        with self._file_lock:
            try:
                self._ensure_directory()
                
                # Create backup if file exists
                if os.path.exists(self._json_file_path):
                    backup_path = f"{self._json_file_path}.backup"
                    shutil.copy2(self._json_file_path, backup_path)
                    logger.debug(f"Created backup: {backup_path}")
                
                # Prepare data
                data = {
                    'users': [user.to_dict(include_password=True) for user in self._users.values()],
                    'roles': [role.to_dict() for role in self._roles.values()],
                    'resources': [resource.to_dict() for resource in self._resources.values()],
                    'metadata': {
                        'last_updated': datetime.now().isoformat(),
                        'version': '1.0'
                    }
                }
                
                # Write to file
                with open(self._json_file_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                
                self._last_modified = os.path.getmtime(self._json_file_path)
                logger.info(f"Saved data to {self._json_file_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to save to JSON file: {e}")
                return False
    
    def initialize(self) -> bool:
        """Initialize by loading from JSON file."""
        success = self._load_from_file()
        self._initialized = success
        return success
    
    def close(self) -> None:
        """Close and cleanup."""
        logger.info("Closing UserManagerJSON")
        # Optionally save on close
        # self._save_to_file()
    
    # ==================== User Operations ====================
    
    def save_user(self, user: User) -> bool:
        """Save a user to the JSON file."""
        if not self.validate_user(user):
            return False
        
        with self._lock:
            self._check_and_reload()
            self._users[user.userid] = user
            return self._save_to_file()
    
    def load_user(self, userid: str) -> Optional[User]:
        """Load a user from memory."""
        with self._lock:
            self._check_and_reload()
            return self._users.get(userid)
    
    def delete_user(self, userid: str) -> bool:
        """Delete a user from the JSON file."""
        with self._lock:
            self._check_and_reload()
            if userid not in self._users:
                return False
            
            del self._users[userid]
            return self._save_to_file()
    
    def list_users(self) -> List[User]:
        """List all users."""
        with self._lock:
            self._check_and_reload()
            return list(self._users.values())
    
    def user_exists(self, userid: str) -> bool:
        """Check if a user exists."""
        with self._lock:
            self._check_and_reload()
            return userid in self._users
    
    # ==================== Role Operations ====================
    
    def save_role(self, role: Role) -> bool:
        """Save a role to the JSON file."""
        if not self.validate_role(role):
            return False
        
        with self._lock:
            self._check_and_reload()
            self._roles[role.name] = role
            return self._save_to_file()
    
    def load_role(self, role_name: str) -> Optional[Role]:
        """Load a role from memory."""
        with self._lock:
            self._check_and_reload()
            return self._roles.get(role_name)
    
    def delete_role(self, role_name: str) -> bool:
        """Delete a role from the JSON file."""
        with self._lock:
            self._check_and_reload()
            if role_name not in self._roles:
                return False
            
            # Remove role from all users
            for user in self._users.values():
                user.remove_role(role_name)
            
            del self._roles[role_name]
            return self._save_to_file()
    
    def list_roles(self) -> List[Role]:
        """List all roles."""
        with self._lock:
            self._check_and_reload()
            return list(self._roles.values())
    
    def role_exists(self, role_name: str) -> bool:
        """Check if a role exists."""
        with self._lock:
            self._check_and_reload()
            return role_name in self._roles
    
    # ==================== Resource Operations ====================
    
    def save_resource(self, resource: Resource) -> bool:
        """Save a resource to the JSON file."""
        if not self.validate_resource(resource):
            return False
        
        with self._lock:
            self._check_and_reload()
            self._resources[resource.name] = resource
            return self._save_to_file()
    
    def load_resource(self, resource_name: str) -> Optional[Resource]:
        """Load a resource from memory."""
        with self._lock:
            self._check_and_reload()
            return self._resources.get(resource_name)
    
    def delete_resource(self, resource_name: str) -> bool:
        """Delete a resource from the JSON file."""
        with self._lock:
            self._check_and_reload()
            if resource_name not in self._resources:
                return False
            
            # Remove resource from all roles
            for role in self._roles.values():
                role.remove_resource(resource_name)
            
            del self._resources[resource_name]
            return self._save_to_file()
    
    def list_resources(self, resource_type: Optional[str] = None) -> List[Resource]:
        """List all resources."""
        with self._lock:
            self._check_and_reload()
            resources = list(self._resources.values())
            
            if resource_type:
                resources = [r for r in resources if r.resource_type == resource_type]
            
            return resources
    
    def resource_exists(self, resource_name: str) -> bool:
        """Check if a resource exists."""
        with self._lock:
            self._check_and_reload()
            return resource_name in self._resources
    
    # ==================== Bulk Operations ====================
    
    def load_all_data(self) -> Dict[str, Any]:
        """Load all data."""
        with self._lock:
            self._check_and_reload()
            return {
                'users': list(self._users.values()),
                'roles': list(self._roles.values()),
                'resources': list(self._resources.values())
            }
    
    def save_all_data(self, users: List[User], roles: List[Role], 
                     resources: List[Resource]) -> bool:
        """Save all data."""
        with self._lock:
            # Clear existing data
            self._users.clear()
            self._roles.clear()
            self._resources.clear()
            
            # Add new data
            for resource in resources:
                self._resources[resource.name] = resource
            
            for role in roles:
                self._roles[role.name] = role
            
            for user in users:
                self._users[user.userid] = user
            
            return self._save_to_file()
    
    # ==================== Additional Methods ====================
    
    def reload(self) -> bool:
        """Manually reload data from file."""
        with self._lock:
            return self._load_from_file()
    
    def get_file_path(self) -> str:
        """Get the path to the JSON file."""
        return self._json_file_path
    
    def create_backup(self, backup_path: Optional[str] = None) -> bool:
        """
        Create a backup of the JSON file.
        
        Args:
            backup_path: Path for the backup file. If None, uses default naming.
            
        Returns:
            True if backup created successfully
        """
        try:
            if not os.path.exists(self._json_file_path):
                logger.warning("Cannot create backup: JSON file does not exist")
                return False
            
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{self._json_file_path}.{timestamp}.backup"
            
            shutil.copy2(self._json_file_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """
        Restore data from a backup file.
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            True if restore successful
        """
        with self._lock:
            try:
                if not os.path.exists(backup_path):
                    logger.error(f"Backup file not found: {backup_path}")
                    return False
                
                shutil.copy2(backup_path, self._json_file_path)
                logger.info(f"Restored from backup: {backup_path}")
                return self._load_from_file()
            except Exception as e:
                logger.error(f"Failed to restore from backup: {e}")
                return False


# Example usage
if __name__ == "__main__":
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create a UserManagerJSON instance
    manager = UserManagerJSON("config/users.json")
    manager.initialize()
    
    # Create test data
    resource1 = Resource("test_api", "api", "Test API")
    manager.save_resource(resource1)
    
    role1 = Role("test_role", "Test Role")
    role1.add_resource("test_api", Permission.all_permissions())
    manager.save_role(role1)
    
    from user import PasswordEncryption
    user1 = User(
        userid="testuser",
        fullname="Test User",
        emailaddress="test@example.com",
        password_hash=PasswordEncryption.encrypt_password("password123"),
        roles=["test_role"]
    )
    manager.save_user(user1)
    
    # List all data
    print("\nAll users:", [u.userid for u in manager.list_users()])
    print("All roles:", [r.name for r in manager.list_roles()])
    print("All resources:", [r.name for r in manager.list_resources()])
    
    # Statistics
    stats = manager.get_statistics()
    print("\nStatistics:", json.dumps(stats, indent=2))
