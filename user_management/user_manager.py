"""
User Manager Module - Abstract base class for user management persistence.

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

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from user_management.user import User, Role, Resource, Permission
import logging

logger = logging.getLogger(__name__)


class UserManager(ABC):
    """
    Abstract base class for user management persistence.
    
    This class defines the interface for persisting and retrieving
    users, roles, and resources. Concrete implementations provide
    different storage backends (database, JSON file, etc.).
    
    Strategy Pattern: Different persistence strategies can be
    implemented by subclassing this abstract class.
    """
    
    def __init__(self):
        """Initialize the user manager."""
        self._initialized = False
        logger.info(f"Initializing {self.__class__.__name__}")
    
    # ==================== Initialization ====================
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the persistence layer.
        
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close and cleanup the persistence layer."""
        pass
    
    # ==================== User Operations ====================
    
    @abstractmethod
    def save_user(self, user: User) -> bool:
        """
        Save a user to the persistence layer.
        
        Args:
            user: User object to save
            
        Returns:
            True if save successful, False otherwise
        """
        pass
    
    @abstractmethod
    def load_user(self, userid: str) -> Optional[User]:
        """
        Load a user from the persistence layer.
        
        Args:
            userid: ID of the user to load
            
        Returns:
            User object if found, None otherwise
        """
        pass
    
    @abstractmethod
    def delete_user(self, userid: str) -> bool:
        """
        Delete a user from the persistence layer.
        
        Args:
            userid: ID of the user to delete
            
        Returns:
            True if delete successful, False otherwise
        """
        pass
    
    @abstractmethod
    def list_users(self) -> List[User]:
        """
        List all users in the persistence layer.
        
        Returns:
            List of all users
        """
        pass
    
    @abstractmethod
    def user_exists(self, userid: str) -> bool:
        """
        Check if a user exists.
        
        Args:
            userid: ID of the user to check
            
        Returns:
            True if user exists, False otherwise
        """
        pass
    
    # ==================== Role Operations ====================
    
    @abstractmethod
    def save_role(self, role: Role) -> bool:
        """
        Save a role to the persistence layer.
        
        Args:
            role: Role object to save
            
        Returns:
            True if save successful, False otherwise
        """
        pass
    
    @abstractmethod
    def load_role(self, role_name: str) -> Optional[Role]:
        """
        Load a role from the persistence layer.
        
        Args:
            role_name: Name of the role to load
            
        Returns:
            Role object if found, None otherwise
        """
        pass
    
    @abstractmethod
    def delete_role(self, role_name: str) -> bool:
        """
        Delete a role from the persistence layer.
        
        Args:
            role_name: Name of the role to delete
            
        Returns:
            True if delete successful, False otherwise
        """
        pass
    
    @abstractmethod
    def list_roles(self) -> List[Role]:
        """
        List all roles in the persistence layer.
        
        Returns:
            List of all roles
        """
        pass
    
    @abstractmethod
    def role_exists(self, role_name: str) -> bool:
        """
        Check if a role exists.
        
        Args:
            role_name: Name of the role to check
            
        Returns:
            True if role exists, False otherwise
        """
        pass
    
    # ==================== Resource Operations ====================
    
    @abstractmethod
    def save_resource(self, resource: Resource) -> bool:
        """
        Save a resource to the persistence layer.
        
        Args:
            resource: Resource object to save
            
        Returns:
            True if save successful, False otherwise
        """
        pass
    
    @abstractmethod
    def load_resource(self, resource_name: str) -> Optional[Resource]:
        """
        Load a resource from the persistence layer.
        
        Args:
            resource_name: Name of the resource to load
            
        Returns:
            Resource object if found, None otherwise
        """
        pass
    
    @abstractmethod
    def delete_resource(self, resource_name: str) -> bool:
        """
        Delete a resource from the persistence layer.
        
        Args:
            resource_name: Name of the resource to delete
            
        Returns:
            True if delete successful, False otherwise
        """
        pass
    
    @abstractmethod
    def list_resources(self, resource_type: Optional[str] = None) -> List[Resource]:
        """
        List all resources in the persistence layer.
        
        Args:
            resource_type: Optional filter by resource type
            
        Returns:
            List of resources
        """
        pass
    
    @abstractmethod
    def resource_exists(self, resource_name: str) -> bool:
        """
        Check if a resource exists.
        
        Args:
            resource_name: Name of the resource to check
            
        Returns:
            True if resource exists, False otherwise
        """
        pass
    
    # ==================== Bulk Operations ====================
    
    @abstractmethod
    def load_all_data(self) -> Dict[str, Any]:
        """
        Load all data from the persistence layer.
        
        Returns:
            Dictionary with keys 'users', 'roles', 'resources'
        """
        pass
    
    @abstractmethod
    def save_all_data(self, users: List[User], roles: List[Role], 
                     resources: List[Resource]) -> bool:
        """
        Save all data to the persistence layer.
        
        Args:
            users: List of users to save
            roles: List of roles to save
            resources: List of resources to save
            
        Returns:
            True if save successful, False otherwise
        """
        pass
    
    # ==================== Convenience Methods ====================
    
    def add_resource_to_role(self, role_name: str, resource_name: str, 
                            permission: Permission) -> bool:
        """
        Convenience method to add a resource to a role.
        
        Args:
            role_name: Name of the role
            resource_name: Name of the resource
            permission: Permission object
            
        Returns:
            True if successful, False otherwise
        """
        role = self.load_role(role_name)
        if not role:
            logger.error(f"Role '{role_name}' not found")
            return False
        
        role.add_resource(resource_name, permission)
        return self.save_role(role)
    
    def remove_resource_from_role(self, role_name: str, resource_name: str) -> bool:
        """
        Convenience method to remove a resource from a role.
        
        Args:
            role_name: Name of the role
            resource_name: Name of the resource
            
        Returns:
            True if successful, False otherwise
        """
        role = self.load_role(role_name)
        if not role:
            logger.error(f"Role '{role_name}' not found")
            return False
        
        if role.remove_resource(resource_name):
            return self.save_role(role)
        return False
    
    def add_role_to_user(self, userid: str, role_name: str) -> bool:
        """
        Convenience method to add a role to a user.
        
        Args:
            userid: User ID
            role_name: Name of the role to add
            
        Returns:
            True if successful, False otherwise
        """
        user = self.load_user(userid)
        if not user:
            logger.error(f"User '{userid}' not found")
            return False
        
        if not self.role_exists(role_name):
            logger.error(f"Role '{role_name}' does not exist")
            return False
        
        user.add_role(role_name)
        return self.save_user(user)
    
    def remove_role_from_user(self, userid: str, role_name: str) -> bool:
        """
        Convenience method to remove a role from a user.
        
        Args:
            userid: User ID
            role_name: Name of the role to remove
            
        Returns:
            True if successful, False otherwise
        """
        user = self.load_user(userid)
        if not user:
            logger.error(f"User '{userid}' not found")
            return False
        
        if user.remove_role(role_name):
            return self.save_user(user)
        return False
    
    def get_user_roles(self, userid: str) -> List[str]:
        """
        Get all roles for a user.
        
        Args:
            userid: User ID
            
        Returns:
            List of role names
        """
        user = self.load_user(userid)
        if not user:
            return []
        return user.roles.copy()
    
    def get_role_resources(self, role_name: str) -> Dict[str, Permission]:
        """
        Get all resources for a role.
        
        Args:
            role_name: Name of the role
            
        Returns:
            Dictionary mapping resource names to permissions
        """
        role = self.load_role(role_name)
        if not role:
            return {}
        return role.resources.copy()
    
    def get_users_with_role(self, role_name: str) -> List[str]:
        """
        Get all users that have a specific role.
        
        Args:
            role_name: Name of the role
            
        Returns:
            List of user IDs
        """
        users = self.list_users()
        return [user.userid for user in users if role_name in user.roles]
    
    def get_roles_with_resource(self, resource_name: str) -> List[str]:
        """
        Get all roles that have access to a specific resource.
        
        Args:
            resource_name: Name of the resource
            
        Returns:
            List of role names
        """
        roles = self.list_roles()
        return [role.name for role in roles if resource_name in role.resources]
    
    # ==================== Validation ====================
    
    def validate_user(self, user: User) -> bool:
        """
        Validate a user object.
        
        Args:
            user: User to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not user.userid or not user.fullname or not user.emailaddress:
            logger.error("User validation failed: missing required fields")
            return False
        
        if not user.password_hash:
            logger.error("User validation failed: password hash is required")
            return False
        
        # Validate roles exist
        for role_name in user.roles:
            if not self.role_exists(role_name):
                logger.error(f"User validation failed: role '{role_name}' does not exist")
                return False
        
        return True
    
    def validate_role(self, role: Role) -> bool:
        """
        Validate a role object.
        
        Args:
            role: Role to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not role.name:
            logger.error("Role validation failed: name is required")
            return False
        
        # Validate resources exist (except patterns)
        for resource_name in role.resources.keys():
            if '*' not in resource_name:  # Skip patterns
                if not self.resource_exists(resource_name):
                    logger.error(f"Role validation failed: resource '{resource_name}' does not exist")
                    return False
        
        return True
    
    def validate_resource(self, resource: Resource) -> bool:
        """
        Validate a resource object.
        
        Args:
            resource: Resource to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not resource.name or not resource.resource_type:
            logger.error("Resource validation failed: name and type are required")
            return False
        
        return True
    
    # ==================== Statistics ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the persistence layer.
        
        Returns:
            Dictionary with statistics
        """
        users = self.list_users()
        roles = self.list_roles()
        resources = self.list_resources()
        
        return {
            'users': {
                'total': len(users),
                'enabled': sum(1 for u in users if u.enabled),
                'disabled': sum(1 for u in users if not u.enabled)
            },
            'roles': {
                'total': len(roles),
                'enabled': sum(1 for r in roles if r.enabled),
                'disabled': sum(1 for r in roles if not r.enabled)
            },
            'resources': {
                'total': len(resources),
                'enabled': sum(1 for r in resources if r.enabled),
                'disabled': sum(1 for r in resources if not r.enabled)
            }
        }
