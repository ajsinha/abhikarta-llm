"""
User Module - Represents a user entity in the Abhikarta LLM system.

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

import hashlib
import secrets
import bcrypt
from typing import List, Optional, Dict, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json


@dataclass
class User:
    """
    Represents a user in the Abhikarta LLM system.
    
    Attributes:
        userid: Unique identifier for the user
        fullname: Full name of the user
        emailaddress: Email address of the user
        password_hash: Encrypted password (bcrypt hash)
        roles: List of role names assigned to the user
        enabled: Whether the user account is enabled
        created_at: Timestamp when the user was created
        updated_at: Timestamp when the user was last updated
        last_login: Timestamp of the last login
        metadata: Additional user metadata
    """
    userid: str
    fullname: str
    emailaddress: str
    password_hash: str
    roles: List[str] = field(default_factory=list)
    enabled: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        now = datetime.now()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
    
    def add_role(self, role: str) -> None:
        """
        Add a role to the user.
        
        Args:
            role: Name of the role to add
        """
        if role not in self.roles:
            self.roles.append(role)
            self.updated_at = datetime.now()
    
    def remove_role(self, role: str) -> bool:
        """
        Remove a role from the user.
        
        Args:
            role: Name of the role to remove
            
        Returns:
            True if role was removed, False if role was not found
        """
        if role in self.roles:
            self.roles.remove(role)
            self.updated_at = datetime.now()
            return True
        return False
    
    def has_role(self, role: str) -> bool:
        """
        Check if user has a specific role.
        
        Args:
            role: Name of the role to check
            
        Returns:
            True if user has the role, False otherwise
        """
        return role in self.roles
    
    def verify_password(self, password: str) -> bool:
        """
        Verify a password against the stored hash.
        
        Args:
            password: Plain text password to verify
            
        Returns:
            True if password matches, False otherwise
        """
        print(self.password_hash)
        xp=PasswordEncryption.encrypt_password_md5(password)
        print(xp)
        return PasswordEncryption.verify_password(password, self.password_hash)
    
    def update_password(self, new_password: str) -> None:
        """
        Update the user's password.
        
        Args:
            new_password: New plain text password
        """
        self.password_hash = PasswordEncryption.encrypt_password(new_password)
        self.updated_at = datetime.now()
    
    def update_last_login(self) -> None:
        """Update the last login timestamp."""
        self.last_login = datetime.now()
    
    def to_dict(self, include_password: bool = False) -> Dict[str, Any]:
        """
        Convert user to dictionary representation.
        
        Args:
            include_password: Whether to include the password hash
            
        Returns:
            Dictionary representation of the user
        """
        data = {
            'userid': self.userid,
            'fullname': self.fullname,
            'emailaddress': self.emailaddress,
            'roles': self.roles.copy(),
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'metadata': self.metadata.copy()
        }
        
        if include_password:
            data['password_hash'] = self.password_hash
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        Create a User instance from dictionary.
        
        Args:
            data: Dictionary containing user data
            
        Returns:
            User instance
        """
        # Parse datetime fields
        created_at = None
        if 'created_at' in data and data['created_at']:
            created_at = datetime.fromisoformat(data['created_at']) if isinstance(data['created_at'], str) else data['created_at']
        
        updated_at = None
        if 'updated_at' in data and data['updated_at']:
            updated_at = datetime.fromisoformat(data['updated_at']) if isinstance(data['updated_at'], str) else data['updated_at']
        
        last_login = None
        if 'last_login' in data and data['last_login']:
            last_login = datetime.fromisoformat(data['last_login']) if isinstance(data['last_login'], str) else data['last_login']
        
        return cls(
            userid=data['userid'],
            fullname=data['fullname'],
            emailaddress=data['emailaddress'],
            password_hash=data['password_hash'],
            roles=data.get('roles', []),
            enabled=data.get('enabled', True),
            created_at=created_at,
            updated_at=updated_at,
            last_login=last_login,
            metadata=data.get('metadata', {})
        )
    
    def __repr__(self) -> str:
        """String representation of the user."""
        return f"User(userid='{self.userid}', fullname='{self.fullname}', roles={self.roles}, enabled={self.enabled})"


class PasswordEncryption:
    """
    Utility class for password encryption and validation.
    
    Uses bcrypt for secure password hashing with salting.
    """
    
    # Bcrypt work factor (cost factor) - higher is more secure but slower
    BCRYPT_ROUNDS = 12


    @staticmethod
    def encrypt_password_md5(password: str):
        """
        Hashes a password using the MD5 algorithm.
        """
        # Convert the string password to bytes
        password_bytes = password.encode('utf-8')

        # Create the MD5 hash object
        m = hashlib.md5()

        # Update the hash object with the password bytes
        m.update(password_bytes)

        # Get the hexadecimal representation of the hash
        return m.hexdigest()

    @staticmethod
    def encrypt_password_bcrypt(password: str) -> str:
        """
        Encrypt a plain text password using bcrypt.
        
        Args:
            password: Plain text password to encrypt
            
        Returns:
            Bcrypt hash string
            
        Raises:
            ValueError: If password is empty or None
        """
        if not password:
            raise ValueError("Password cannot be empty")
        
        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=PasswordEncryption.BCRYPT_ROUNDS)
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        # Return hash as string
        return password_hash.decode('utf-8')

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify a password against a hash.

        Args:
            password: Plain text password to verify
            password_hash: Bcrypt hash to verify against

        Returns:
            True if password matches, False otherwise
        """
        if not password or not password_hash:
            return False

        md5hash = PasswordEncryption.encrypt_password_md5(password)
        return  md5hash == password_hash

    @staticmethod
    def verify_password_bcrypt(password: str, password_hash: str) -> bool:
        """
        Verify a password against a hash.
        
        Args:
            password: Plain text password to verify
            password_hash: Bcrypt hash to verify against
            
        Returns:
            True if password matches, False otherwise
        """
        if not password or not password_hash:
            return False
        
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception:
            return False
    
    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """
        Generate a cryptographically secure random password.
        
        Args:
            length: Length of the password to generate
            
        Returns:
            Randomly generated password
        """
        if length < 8:
            raise ValueError("Password length must be at least 8 characters")
        
        # Use secrets module for cryptographically strong random generation
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password


@dataclass
class Resource:
    """
    Represents a resource in the system.
    
    Attributes:
        name: Unique name of the resource
        resource_type: Type/category of the resource
        description: Description of the resource
        enabled: Whether the resource is enabled
        created_at: Timestamp when the resource was created
        metadata: Additional resource metadata
    """
    name: str
    resource_type: str
    description: str = ""
    enabled: bool = True
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert resource to dictionary."""
        return {
            'name': self.name,
            'resource_type': self.resource_type,
            'description': self.description,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'metadata': self.metadata.copy()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Resource':
        """Create Resource from dictionary."""
        created_at = None
        if 'created_at' in data and data['created_at']:
            created_at = datetime.fromisoformat(data['created_at']) if isinstance(data['created_at'], str) else data['created_at']
        
        return cls(
            name=data['name'],
            resource_type=data['resource_type'],
            description=data.get('description', ''),
            enabled=data.get('enabled', True),
            created_at=created_at,
            metadata=data.get('metadata', {})
        )


@dataclass
class Permission:
    """
    Represents permissions on a resource.
    
    Attributes:
        create: Permission to create
        read: Permission to read
        update: Permission to update/modify
        delete: Permission to delete
        execute: Permission to execute
    """
    create: bool = False
    read: bool = False
    update: bool = False
    delete: bool = False
    execute: bool = False
    
    def to_dict(self) -> Dict[str, bool]:
        """Convert permission to dictionary."""
        return {
            'create': self.create,
            'read': self.read,
            'update': self.update,
            'delete': self.delete,
            'execute': self.execute
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, bool]) -> 'Permission':
        """Create Permission from dictionary."""
        return cls(
            create=data.get('create', False),
            read=data.get('read', False),
            update=data.get('update', False),
            delete=data.get('delete', False),
            execute=data.get('execute', False)
        )
    
    @classmethod
    def all_permissions(cls) -> 'Permission':
        """Create a Permission object with all permissions enabled."""
        return cls(create=True, read=True, update=True, delete=True, execute=True)
    
    @classmethod
    def read_only(cls) -> 'Permission':
        """Create a Permission object with only read permission."""
        return cls(read=True)
    
    def has_any_permission(self) -> bool:
        """Check if any permission is granted."""
        return any([self.create, self.read, self.update, self.delete, self.execute])


@dataclass
class Role:
    """
    Represents a role in the RBAC system.
    
    Attributes:
        name: Unique name of the role
        description: Description of the role
        resources: Dictionary mapping resource names to their permissions
        enabled: Whether the role is enabled
        created_at: Timestamp when the role was created
        metadata: Additional role metadata
    """
    name: str
    description: str = ""
    resources: Dict[str, Permission] = field(default_factory=dict)
    enabled: bool = True
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def add_resource(self, resource_name: str, permission: Permission) -> None:
        """Add a resource with permissions to the role."""
        self.resources[resource_name] = permission
    
    def remove_resource(self, resource_name: str) -> bool:
        """Remove a resource from the role."""
        if resource_name in self.resources:
            del self.resources[resource_name]
            return True
        return False
    
    def has_resource(self, resource_name: str) -> bool:
        """Check if role has a specific resource."""
        return resource_name in self.resources
    
    def get_permission(self, resource_name: str) -> Optional[Permission]:
        """Get permissions for a specific resource."""
        return self.resources.get(resource_name)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert role to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'resources': {k: v.to_dict() for k, v in self.resources.items()},
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'metadata': self.metadata.copy()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Role':
        """Create Role from dictionary."""
        created_at = None
        if 'created_at' in data and data['created_at']:
            created_at = datetime.fromisoformat(data['created_at']) if isinstance(data['created_at'], str) else data['created_at']
        
        resources = {}
        if 'resources' in data:
            for resource_name, perm_dict in data['resources'].items():
                resources[resource_name] = Permission.from_dict(perm_dict)
        
        return cls(
            name=data['name'],
            description=data.get('description', ''),
            resources=resources,
            enabled=data.get('enabled', True),
            created_at=created_at,
            metadata=data.get('metadata', {})
        )


# Example usage
if __name__ == "__main__":
    # Example 1: Create a user with encrypted password
    password = "SecurePassword123!"
    encrypted_password = PasswordEncryption.encrypt_password(password)
    
    user = User(
        userid="user001",
        fullname="John Doe",
        emailaddress="john.doe@example.com",
        password_hash=encrypted_password,
        roles=["developer", "analyst"]
    )
    
    print(f"Created user: {user}")
    print(f"Password verification: {user.verify_password(password)}")
    
    # Example 2: Create a resource
    resource = Resource(
        name="model_api",
        resource_type="api",
        description="LLM Model API endpoint"
    )
    
    print(f"\nCreated resource: {resource.to_dict()}")
    
    # Example 3: Create a role with permissions
    role = Role(
        name="developer",
        description="Developer role with API access"
    )
    role.add_resource("model_api", Permission(create=True, read=True, execute=True))
    role.add_resource("training_data", Permission(read=True))
    
    print(f"\nCreated role: {role.to_dict()}")
    
    # Example 4: User to/from dict
    user_dict = user.to_dict(include_password=True)
    print(f"\nUser as dict: {json.dumps(user_dict, indent=2, default=str)}")
    
    user_restored = User.from_dict(user_dict)
    print(f"Restored user: {user_restored}")
