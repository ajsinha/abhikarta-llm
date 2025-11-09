"""
User Registry Module - Singleton registry for RBAC management in Abhikarta LLM.

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

import logging
import threading
import re
import jwt
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime, timedelta
from user import User, Role, Resource, Permission, PasswordEncryption
from user_manager import UserManager

logger = logging.getLogger(__name__)


class UserRegistry:
    """
    Singleton registry for managing users, roles, and resources in the RBAC system.
    
    Features:
    - Singleton pattern ensures only one registry instance
    - Thread-safe operations
    - Pattern-based permission matching (* and prefix matching)
    - JWT-based authentication
    - Comprehensive RBAC operations
    - Admin user with full system access
    - Resource enable/disable support
    - Cascading deletions for data consistency
    """
    
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    
    # JWT Configuration
    JWT_SECRET_KEY = "abhikarta-llm-secret-key-change-in-production"  # Should be loaded from config
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24
    
    # Admin user constants
    ADMIN_USERID = "admin"
    ADMIN_ROLE = "admin"
    
    def __new__(cls):
        """Implement singleton pattern with double-checked locking."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the user registry."""
        # Only initialize once
        if UserRegistry._initialized:
            return
        
        with UserRegistry._lock:
            if UserRegistry._initialized:
                return
            
            logger.info("Initializing UserRegistry")
            
            # Storage
            self.user_manager = None
            self._users: Dict[str, User] = {}
            self._roles: Dict[str, Role] = {}
            self._resources: Dict[str, Resource] = {}
            
            # Thread safety
            self._registry_lock = threading.RLock()
            
            # Statistics
            self._login_attempts = 0
            self._successful_logins = 0
            self._failed_logins = 0
            
            # Initialize admin role and user
            self._initialize_admin()
            
            UserRegistry._initialized = True
            logger.info("UserRegistry initialized successfully")

    def set_user_manager(self, user_manager: UserManager):
        self.user_manager = user_manager

    def _initialize_admin(self):
        """Initialize the admin role and admin user."""
        # Create admin role with full permissions
        admin_role = Role(
            name=self.ADMIN_ROLE,
            description="Administrator role with full system access",
            enabled=True
        )
        
        # Admin role has access to all resources (pattern *)
        admin_role.add_resource("*", Permission.all_permissions())
        self._roles[self.ADMIN_ROLE] = admin_role
        
        # Create admin user with default password (should be changed on first login)
        default_admin_password = "admin123"  # Should be changed immediately
        admin_user = User(
            userid=self.ADMIN_USERID,
            fullname="System Administrator",
            emailaddress="admin@abhikarta.local",
            password_hash=PasswordEncryption.encrypt_password(default_admin_password),
            roles=[self.ADMIN_ROLE],
            enabled=True
        )
        self._users[self.ADMIN_USERID] = admin_user
        
        logger.info(f"Admin user '{self.ADMIN_USERID}' initialized with role '{self.ADMIN_ROLE}'")
    
    # ==================== User Management ====================
    
    def add_user(self, user: User) -> bool:
        """
        Add a new user to the registry.
        
        Args:
            user: User object to add
            
        Returns:
            True if user was added, False if user already exists
        """
        with self._registry_lock:
            if user.userid in self._users:
                logger.warning(f"User '{user.userid}' already exists")
                return False
            
            # Validate roles exist
            for role in user.roles:
                if role not in self._roles:
                    logger.error(f"Role '{role}' does not exist")
                    raise ValueError(f"Role '{role}' does not exist")
            
            self._users[user.userid] = user
            logger.info(f"Added user '{user.userid}' with roles {user.roles}")
            return True
    
    def remove_user(self, userid: str) -> bool:
        """
        Remove a user from the registry.
        
        Args:
            userid: ID of the user to remove
            
        Returns:
            True if user was removed, False if user not found
        """
        with self._registry_lock:
            # Cannot remove admin user
            if userid == self.ADMIN_USERID:
                logger.error("Cannot remove admin user")
                raise ValueError("Cannot remove admin user")
            
            if userid not in self._users:
                logger.warning(f"User '{userid}' not found")
                return False
            
            del self._users[userid]
            logger.info(f"Removed user '{userid}'")
            return True
    
    def get_user(self, userid: str) -> Optional[User]:
        """Get a user by userid."""
        with self._registry_lock:
            return self._users.get(userid)
    
    def list_users(self) -> List[User]:
        """List all users in the registry."""
        with self._registry_lock:
            return list(self._users.values())
    
    def update_user(self, userid: str, **kwargs) -> bool:
        """
        Update user attributes.
        
        Args:
            userid: ID of the user to update
            **kwargs: Attributes to update
            
        Returns:
            True if user was updated, False if user not found
        """
        with self._registry_lock:
            user = self._users.get(userid)
            if not user:
                logger.warning(f"User '{userid}' not found")
                return False
            
            # Update allowed attributes
            for key, value in kwargs.items():
                if hasattr(user, key) and key not in ['userid', 'password_hash']:
                    setattr(user, key, value)
            
            user.updated_at = datetime.now()
            logger.info(f"Updated user '{userid}'")
            return True
    
    # ==================== Role Management ====================
    
    def add_role(self, role: Role) -> bool:
        """
        Add a new role to the registry.
        
        Args:
            role: Role object to add
            
        Returns:
            True if role was added, False if role already exists
        """
        with self._registry_lock:
            if role.name in self._roles:
                logger.warning(f"Role '{role.name}' already exists")
                return False
            
            # Validate resources exist
            for resource_name in role.resources.keys():
                # Skip wildcard patterns
                if not self._is_pattern(resource_name):
                    if resource_name not in self._resources:
                        logger.error(f"Resource '{resource_name}' does not exist")
                        raise ValueError(f"Resource '{resource_name}' does not exist")
            
            self._roles[role.name] = role
            logger.info(f"Added role '{role.name}' with {len(role.resources)} resources")
            return True
    
    def remove_role(self, role_name: str) -> bool:
        """
        Remove a role from the registry.
        
        This operation:
        1. Removes the role from all users
        2. Deletes the role
        
        Args:
            role_name: Name of the role to remove
            
        Returns:
            True if role was removed, False if role not found
        """
        with self._registry_lock:
            # Cannot remove admin role
            if role_name == self.ADMIN_ROLE:
                logger.error("Cannot remove admin role")
                raise ValueError("Cannot remove admin role")
            
            if role_name not in self._roles:
                logger.warning(f"Role '{role_name}' not found")
                return False
            
            # Step 1: Remove role from all users
            users_affected = 0
            for user in self._users.values():
                if user.remove_role(role_name):
                    users_affected += 1
            
            # Step 2: Delete the role
            del self._roles[role_name]
            
            logger.info(f"Removed role '{role_name}' from {users_affected} users")
            return True
    
    def get_role(self, role_name: str) -> Optional[Role]:
        """Get a role by name."""
        with self._registry_lock:
            return self._roles.get(role_name)
    
    def list_roles(self) -> List[Role]:
        """List all roles in the registry."""
        with self._registry_lock:
            return list(self._roles.values())
    
    def add_resource_to_role(self, role_name: str, resource_name: str, 
                            permission: Permission) -> bool:
        """
        Add a resource with permissions to a role.
        
        Args:
            role_name: Name of the role
            resource_name: Name of the resource to add
            permission: Permission object
            
        Returns:
            True if resource was added, False if role not found
        """
        with self._registry_lock:
            role = self._roles.get(role_name)
            if not role:
                logger.warning(f"Role '{role_name}' not found")
                return False
            
            # Validate resource exists (unless it's a pattern)
            if not self._is_pattern(resource_name):
                if resource_name not in self._resources:
                    logger.error(f"Resource '{resource_name}' does not exist")
                    raise ValueError(f"Resource '{resource_name}' does not exist")
            
            role.add_resource(resource_name, permission)
            logger.info(f"Added resource '{resource_name}' to role '{role_name}'")
            return True
    
    def remove_resource_from_role(self, role_name: str, resource_name: str) -> bool:
        """
        Remove a resource from a role.
        
        Args:
            role_name: Name of the role
            resource_name: Name of the resource to remove
            
        Returns:
            True if resource was removed, False if role or resource not found
        """
        with self._registry_lock:
            role = self._roles.get(role_name)
            if not role:
                logger.warning(f"Role '{role_name}' not found")
                return False
            
            success = role.remove_resource(resource_name)
            if success:
                logger.info(f"Removed resource '{resource_name}' from role '{role_name}'")
            return success
    
    # ==================== Resource Management ====================
    
    def add_resource(self, resource: Resource) -> bool:
        """
        Add a new resource to the registry.
        
        Args:
            resource: Resource object to add
            
        Returns:
            True if resource was added, False if resource already exists
        """
        with self._registry_lock:
            if resource.name in self._resources:
                logger.warning(f"Resource '{resource.name}' already exists")
                return False
            
            self._resources[resource.name] = resource
            logger.info(f"Added resource '{resource.name}' of type '{resource.resource_type}'")
            return True
    
    def remove_resource(self, resource_name: str) -> bool:
        """
        Remove a resource from the registry.
        
        This operation:
        1. Removes the resource from all roles
        2. Deletes the resource
        
        Args:
            resource_name: Name of the resource to remove
            
        Returns:
            True if resource was removed, False if resource not found
        """
        with self._registry_lock:
            if resource_name not in self._resources:
                logger.warning(f"Resource '{resource_name}' not found")
                return False
            
            # Step 1: Remove resource from all roles
            roles_affected = 0
            for role in self._roles.values():
                if role.remove_resource(resource_name):
                    roles_affected += 1
            
            # Step 2: Delete the resource
            del self._resources[resource_name]
            
            logger.info(f"Removed resource '{resource_name}' from {roles_affected} roles")
            return True
    
    def get_resource(self, resource_name: str) -> Optional[Resource]:
        """Get a resource by name."""
        with self._registry_lock:
            return self._resources.get(resource_name)
    
    def list_resources(self, resource_type: Optional[str] = None, 
                      enabled_only: bool = False) -> List[Resource]:
        """
        List all resources, optionally filtered by type and enabled status.
        
        Args:
            resource_type: Filter by resource type
            enabled_only: Only return enabled resources
            
        Returns:
            List of resources
        """
        with self._registry_lock:
            resources = list(self._resources.values())
            
            if resource_type:
                resources = [r for r in resources if r.resource_type == resource_type]
            
            if enabled_only:
                resources = [r for r in resources if r.enabled]
            
            return resources
    
    def enable_resource(self, resource_name: str) -> bool:
        """Enable a resource."""
        with self._registry_lock:
            resource = self._resources.get(resource_name)
            if not resource:
                return False
            resource.enabled = True
            logger.info(f"Enabled resource '{resource_name}'")
            return True
    
    def disable_resource(self, resource_name: str) -> bool:
        """Disable a resource."""
        with self._registry_lock:
            resource = self._resources.get(resource_name)
            if not resource:
                return False
            resource.enabled = False
            logger.info(f"Disabled resource '{resource_name}'")
            return True
    
    # ==================== RBAC Authorization ====================
    
    def _is_pattern(self, resource_name: str) -> bool:
        """Check if a resource name is a pattern (contains * or ends with *)."""
        return '*' in resource_name
    
    def _matches_pattern(self, resource_name: str, pattern: str) -> bool:
        """
        Check if a resource name matches a pattern.
        
        Patterns:
        - "*" matches everything
        - "prefix*" matches anything starting with prefix
        
        Args:
            resource_name: Resource name to check
            pattern: Pattern to match against
            
        Returns:
            True if resource matches pattern
        """
        if pattern == "*":
            return True
        
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            return resource_name.startswith(prefix)
        
        return resource_name == pattern
    
    def get_user_permissions(self, userid: str) -> Dict[str, Permission]:
        """
        Get all permissions for a user across all their roles.
        
        This resolves:
        - Pattern-based permissions
        - Disabled resources
        - Permission aggregation from multiple roles
        
        Args:
            userid: User ID
            
        Returns:
            Dictionary mapping resource names to aggregated permissions
        """
        with self._registry_lock:
            user = self._users.get(userid)
            if not user or not user.enabled:
                return {}
            
            # Special handling for admin user
            if userid == self.ADMIN_USERID:
                # Admin has all permissions on all resources
                all_perms = {}
                for resource_name in self._resources.keys():
                    all_perms[resource_name] = Permission.all_permissions()
                return all_perms
            
            # Aggregate permissions from all roles
            aggregated_permissions: Dict[str, Permission] = {}
            
            for role_name in user.roles:
                role = self._roles.get(role_name)
                if not role or not role.enabled:
                    continue
                
                for resource_pattern, permission in role.resources.items():
                    # Check if it's a pattern
                    if self._is_pattern(resource_pattern):
                        # Apply pattern to all matching resources
                        for resource_name, resource in self._resources.items():
                            if not resource.enabled:
                                continue
                            
                            if self._matches_pattern(resource_name, resource_pattern):
                                # Aggregate permissions (OR operation)
                                if resource_name not in aggregated_permissions:
                                    aggregated_permissions[resource_name] = Permission()
                                
                                existing = aggregated_permissions[resource_name]
                                existing.create = existing.create or permission.create
                                existing.read = existing.read or permission.read
                                existing.update = existing.update or permission.update
                                existing.delete = existing.delete or permission.delete
                                existing.execute = existing.execute or permission.execute
                    else:
                        # Direct resource reference
                        resource = self._resources.get(resource_pattern)
                        if not resource or not resource.enabled:
                            continue
                        
                        if resource_pattern not in aggregated_permissions:
                            aggregated_permissions[resource_pattern] = Permission()
                        
                        existing = aggregated_permissions[resource_pattern]
                        existing.create = existing.create or permission.create
                        existing.read = existing.read or permission.read
                        existing.update = existing.update or permission.update
                        existing.delete = existing.delete or permission.delete
                        existing.execute = existing.execute or permission.execute
            
            return aggregated_permissions
    
    def check_permission(self, userid: str, resource_name: str, 
                        permission_type: str) -> bool:
        """
        Check if a user has a specific permission on a resource.
        
        Args:
            userid: User ID
            resource_name: Resource name
            permission_type: One of 'create', 'read', 'update', 'delete', 'execute'
            
        Returns:
            True if user has the permission, False otherwise
        """
        permissions = self.get_user_permissions(userid)
        
        if resource_name not in permissions:
            return False
        
        permission = permissions[resource_name]
        return getattr(permission, permission_type, False)
    
    def get_accessible_resources(self, userid: str, 
                                permission_type: Optional[str] = None) -> List[str]:
        """
        Get list of resources accessible to a user.
        
        Args:
            userid: User ID
            permission_type: Optional filter by permission type
            
        Returns:
            List of accessible resource names
        """
        permissions = self.get_user_permissions(userid)
        
        if permission_type is None:
            return list(permissions.keys())
        
        accessible = []
        for resource_name, permission in permissions.items():
            if getattr(permission, permission_type, False):
                accessible.append(resource_name)
        
        return accessible
    
    # ==================== Authentication ====================
    
    def authenticate(self, userid: str, password: str) -> Optional[str]:
        """
        Authenticate a user and return JWT token.
        
        Args:
            userid: User ID
            password: Plain text password
            
        Returns:
            JWT token if authentication successful, None otherwise
        """
        with self._registry_lock:
            self._login_attempts += 1
            
            user = self._users.get(userid)
            if not user or not user.enabled:
                self._failed_logins += 1
                logger.warning(f"Authentication failed for user '{userid}': user not found or disabled")
                return None
            
            if not user.verify_password(password):
                self._failed_logins += 1
                logger.warning(f"Authentication failed for user '{userid}': invalid password")
                return None
            
            # Update last login
            user.update_last_login()
            self._successful_logins += 1
            
            # Generate JWT token
            token = self._generate_jwt_token(user)
            
            logger.info(f"User '{userid}' authenticated successfully")
            return token
    
    def _generate_jwt_token(self, user: User) -> str:
        """Generate JWT token for a user."""
        payload = {
            'userid': user.userid,
            'fullname': user.fullname,
            'emailaddress': user.emailaddress,
            'roles': user.roles,
            'exp': datetime.utcnow() + timedelta(hours=self.JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.JWT_SECRET_KEY, algorithm=self.JWT_ALGORITHM)
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a JWT token and return payload.
        
        Args:
            token: JWT token string
            
        Returns:
            Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.JWT_SECRET_KEY, algorithms=[self.JWT_ALGORITHM])
            
            # Verify user still exists and is enabled
            userid = payload.get('userid')
            user = self._users.get(userid)
            if not user or not user.enabled:
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
    
    def refresh_token(self, token: str) -> Optional[str]:
        """
        Refresh a JWT token.
        
        Args:
            token: Current JWT token
            
        Returns:
            New JWT token if valid, None otherwise
        """
        payload = self.verify_token(token)
        if not payload:
            return None
        
        user = self._users.get(payload['userid'])
        if not user:
            return None
        
        return self._generate_jwt_token(user)
    
    # ==================== Statistics and Monitoring ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        with self._registry_lock:
            return {
                'users': {
                    'total': len(self._users),
                    'enabled': sum(1 for u in self._users.values() if u.enabled),
                    'disabled': sum(1 for u in self._users.values() if not u.enabled)
                },
                'roles': {
                    'total': len(self._roles),
                    'enabled': sum(1 for r in self._roles.values() if r.enabled),
                    'disabled': sum(1 for r in self._roles.values() if not r.enabled)
                },
                'resources': {
                    'total': len(self._resources),
                    'enabled': sum(1 for r in self._resources.values() if r.enabled),
                    'disabled': sum(1 for r in self._resources.values() if not r.enabled)
                },
                'authentication': {
                    'total_attempts': self._login_attempts,
                    'successful': self._successful_logins,
                    'failed': self._failed_logins,
                    'success_rate': (self._successful_logins / self._login_attempts * 100) 
                                   if self._login_attempts > 0 else 0
                }
            }
    
    def reset(self):
        """Reset the registry (mainly for testing)."""
        with self._registry_lock:
            self._users.clear()
            self._roles.clear()
            self._resources.clear()
            self._login_attempts = 0
            self._successful_logins = 0
            self._failed_logins = 0
            self._initialize_admin()
            logger.info("UserRegistry reset complete")
    
    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance (mainly for testing)."""
        with cls._lock:
            if cls._instance:
                cls._instance.reset()
            cls._instance = None
            cls._initialized = False


# Convenience function to get the singleton instance
def get_user_registry() -> UserRegistry:
    """Get the singleton UserRegistry instance."""
    return UserRegistry()


# Example usage
if __name__ == "__main__":
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get the singleton registry
    registry = get_user_registry()
    
    # Example 1: Add resources
    resources = [
        Resource("model_api", "api", "LLM Model API"),
        Resource("training_data", "data", "Training datasets"),
        Resource("user_management", "admin", "User management system"),
        Resource("yahoo_finance", "external", "Yahoo Finance API"),
        Resource("yahoo_news", "external", "Yahoo News API")
    ]
    
    for resource in resources:
        registry.add_resource(resource)
    
    # Example 2: Create roles
    developer_role = Role("developer", "Developer with API access")
    developer_role.add_resource("model_api", Permission(read=True, execute=True))
    developer_role.add_resource("training_data", Permission(read=True))
    registry.add_role(developer_role)
    
    # Role with pattern matching
    yahoo_role = Role("yahoo_user", "Access to Yahoo resources")
    yahoo_role.add_resource("yahoo*", Permission.all_permissions())
    registry.add_role(yahoo_role)
    
    # Example 3: Create users
    user1 = User(
        userid="john",
        fullname="John Developer",
        emailaddress="john@example.com",
        password_hash=PasswordEncryption.encrypt_password("password123"),
        roles=["developer"]
    )
    registry.add_user(user1)
    
    user2 = User(
        userid="jane",
        fullname="Jane Analyst",
        emailaddress="jane@example.com",
        password_hash=PasswordEncryption.encrypt_password("password456"),
        roles=["yahoo_user"]
    )
    registry.add_user(user2)
    
    # Example 4: Authentication
    token = registry.authenticate("john", "password123")
    if token:
        print(f"Authentication successful. Token: {token[:50]}...")
        
        # Verify token
        payload = registry.verify_token(token)
        print(f"Token payload: {payload}")
    
    # Example 5: Check permissions
    print(f"\nJohn's accessible resources: {registry.get_accessible_resources('john')}")
    print(f"Jane's accessible resources: {registry.get_accessible_resources('jane')}")
    
    print(f"\nJohn can read model_api: {registry.check_permission('john', 'model_api', 'read')}")
    print(f"John can delete model_api: {registry.check_permission('john', 'model_api', 'delete')}")
    
    print(f"\nJane can read yahoo_finance: {registry.check_permission('jane', 'yahoo_finance', 'read')}")
    print(f"Jane can delete yahoo_news: {registry.check_permission('jane', 'yahoo_news', 'delete')}")
    
    # Example 6: Admin user
    admin_token = registry.authenticate("admin", "admin123")
    if admin_token:
        print(f"\nAdmin authenticated. Accessible resources: {len(registry.get_accessible_resources('admin'))}")
    
    # Example 7: Statistics
    stats = registry.get_statistics()
    print(f"\nRegistry Statistics:")
    print(f"Total users: {stats['users']['total']}")
    print(f"Total roles: {stats['roles']['total']}")
    print(f"Total resources: {stats['resources']['total']}")
    print(f"Authentication success rate: {stats['authentication']['success_rate']:.2f}%")
