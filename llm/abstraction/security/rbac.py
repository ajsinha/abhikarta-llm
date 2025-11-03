"""
Role-Based Access Control (RBAC) System

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import json
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Permission(Enum):
    """Available permissions in the system"""
    # Provider permissions
    USE_MOCK = "use_mock_provider"
    USE_ANTHROPIC = "use_anthropic"
    USE_OPENAI = "use_openai"
    USE_GOOGLE = "use_google"
    USE_META = "use_meta"
    USE_HUGGINGFACE = "use_huggingface"
    USE_AWS = "use_aws"
    USE_ALL_PROVIDERS = "use_all_providers"
    
    # Model permissions
    USE_CHEAP_MODELS = "use_cheap_models"  # Models < $0.01/1K tokens
    USE_EXPENSIVE_MODELS = "use_expensive_models"  # Models > $0.01/1K tokens
    USE_ALL_MODELS = "use_all_models"
    
    # Operation permissions
    COMPLETE = "complete"
    CHAT = "chat"
    STREAM = "stream"
    BATCH = "batch"
    EMBEDDINGS = "embeddings"
    
    # Feature permissions
    USE_CACHE = "use_cache"
    USE_HISTORY = "use_history"
    EXPORT_HISTORY = "export_history"
    USE_BENCHMARKING = "use_benchmarking"
    
    # Cost permissions
    UNLIMITED_COST = "unlimited_cost"
    LIMITED_COST = "limited_cost"
    
    # Admin permissions
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_API_KEYS = "manage_api_keys"
    VIEW_ALL_USAGE = "view_all_usage"
    
    # Wildcard
    ALL = "*"


@dataclass
class ResourceLimit:
    """Limits on resource usage"""
    max_tokens_per_request: Optional[int] = None
    max_requests_per_minute: Optional[int] = None
    max_requests_per_day: Optional[int] = None
    max_cost_per_day: Optional[float] = None
    max_cost_per_month: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ResourceLimit':
        return cls(**data)


@dataclass
class Role:
    """Represents a role with permissions and limits"""
    name: str
    description: str
    permissions: Set[str] = field(default_factory=set)
    resource_limits: ResourceLimit = field(default_factory=ResourceLimit)
    created_at: datetime = field(default_factory=datetime.now)
    
    def has_permission(self, permission: str) -> bool:
        """Check if role has a specific permission"""
        # Check for wildcard
        if "*" in self.permissions or Permission.ALL.value in self.permissions:
            return True
        
        # Check for specific permission
        return permission in self.permissions
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['permissions'] = list(self.permissions)
        data['created_at'] = self.created_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Role':
        data['permissions'] = set(data.get('permissions', []))
        data['resource_limits'] = ResourceLimit.from_dict(data.get('resource_limits', {}))
        if 'created_at' in data:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


@dataclass
class User:
    """Represents a user with assigned roles"""
    user_id: str
    email: str
    roles: Set[str] = field(default_factory=set)
    custom_permissions: Set[str] = field(default_factory=set)
    custom_limits: Optional[ResourceLimit] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['roles'] = list(self.roles)
        data['custom_permissions'] = list(self.custom_permissions)
        data['created_at'] = self.created_at.isoformat()
        if self.last_login:
            data['last_login'] = self.last_login.isoformat()
        if self.custom_limits:
            data['custom_limits'] = self.custom_limits.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        data['roles'] = set(data.get('roles', []))
        data['custom_permissions'] = set(data.get('custom_permissions', []))
        if data.get('custom_limits'):
            data['custom_limits'] = ResourceLimit.from_dict(data['custom_limits'])
        if 'created_at' in data:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('last_login'):
            data['last_login'] = datetime.fromisoformat(data['last_login'])
        return cls(**data)


class RBACManager:
    """
    Manages role-based access control for the LLM system.
    
    Features:
    - Define roles with permissions
    - Assign roles to users
    - Check permissions
    - Enforce resource limits
    - Audit trail
    """
    
    def __init__(self, storage_path: str = ".rbac"):
        """
        Initialize RBAC manager.
        
        Args:
            storage_path: Path to store RBAC data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True, parents=True)
        
        self.roles: Dict[str, Role] = {}
        self.users: Dict[str, User] = {}
        
        self.load_data()
        self._initialize_default_roles()
    
    def _initialize_default_roles(self):
        """Initialize default roles if they don't exist"""
        default_roles = {
            'admin': Role(
                name='admin',
                description='Full system access',
                permissions={Permission.ALL.value}
            ),
            'developer': Role(
                name='developer',
                description='Developer access with limits',
                permissions={
                    Permission.USE_MOCK.value,
                    Permission.USE_ANTHROPIC.value,
                    Permission.USE_OPENAI.value,
                    Permission.USE_CHEAP_MODELS.value,
                    Permission.COMPLETE.value,
                    Permission.CHAT.value,
                    Permission.STREAM.value,
                    Permission.USE_CACHE.value,
                    Permission.USE_HISTORY.value,
                    Permission.EXPORT_HISTORY.value,
                },
                resource_limits=ResourceLimit(
                    max_tokens_per_request=4000,
                    max_requests_per_day=1000,
                    max_cost_per_day=10.0
                )
            ),
            'analyst': Role(
                name='analyst',
                description='Read-only analyst access',
                permissions={
                    Permission.USE_MOCK.value,
                    Permission.COMPLETE.value,
                    Permission.CHAT.value,
                    Permission.USE_CACHE.value,
                    Permission.VIEW_ALL_USAGE.value,
                },
                resource_limits=ResourceLimit(
                    max_tokens_per_request=2000,
                    max_requests_per_day=100,
                    max_cost_per_day=1.0
                )
            ),
            'readonly': Role(
                name='readonly',
                description='View-only access',
                permissions={
                    Permission.USE_MOCK.value,
                    Permission.VIEW_ALL_USAGE.value,
                },
                resource_limits=ResourceLimit(
                    max_tokens_per_request=500,
                    max_requests_per_day=50,
                    max_cost_per_day=0.0
                )
            ),
        }
        
        for role_name, role in default_roles.items():
            if role_name not in self.roles:
                self.roles[role_name] = role
        
        self.save_data()
    
    def create_role(
        self,
        name: str,
        description: str,
        permissions: List[str],
        resource_limits: Optional[ResourceLimit] = None
    ) -> Role:
        """
        Create a new role.
        
        Args:
            name: Role name
            description: Role description
            permissions: List of permission strings
            resource_limits: Optional resource limits
            
        Returns:
            Created Role object
        """
        role = Role(
            name=name,
            description=description,
            permissions=set(permissions),
            resource_limits=resource_limits or ResourceLimit()
        )
        
        self.roles[name] = role
        self.save_data()
        
        logger.info(f"Created role: {name}")
        return role
    
    def delete_role(self, name: str) -> bool:
        """Delete a role"""
        if name in ['admin', 'developer', 'analyst', 'readonly']:
            logger.error(f"Cannot delete default role: {name}")
            return False
        
        if name in self.roles:
            del self.roles[name]
            
            # Remove role from all users
            for user in self.users.values():
                user.roles.discard(name)
            
            self.save_data()
            logger.info(f"Deleted role: {name}")
            return True
        
        return False
    
    def create_user(
        self,
        user_id: str,
        email: str,
        roles: Optional[List[str]] = None
    ) -> User:
        """
        Create a new user.
        
        Args:
            user_id: Unique user identifier
            email: User email
            roles: List of role names to assign
            
        Returns:
            Created User object
        """
        user = User(
            user_id=user_id,
            email=email,
            roles=set(roles) if roles else set()
        )
        
        self.users[user_id] = user
        self.save_data()
        
        logger.info(f"Created user: {user_id}")
        return user
    
    def assign_role(self, user_id: str, role_name: str) -> bool:
        """Assign a role to a user"""
        if user_id not in self.users:
            logger.error(f"User not found: {user_id}")
            return False
        
        if role_name not in self.roles:
            logger.error(f"Role not found: {role_name}")
            return False
        
        self.users[user_id].roles.add(role_name)
        self.save_data()
        
        logger.info(f"Assigned role {role_name} to user {user_id}")
        return True
    
    def revoke_role(self, user_id: str, role_name: str) -> bool:
        """Revoke a role from a user"""
        if user_id not in self.users:
            return False
        
        self.users[user_id].roles.discard(role_name)
        self.save_data()
        
        logger.info(f"Revoked role {role_name} from user {user_id}")
        return True
    
    def check_permission(
        self,
        user_id: str,
        permission: str
    ) -> bool:
        """
        Check if a user has a specific permission.
        
        Args:
            user_id: User identifier
            permission: Permission to check
            
        Returns:
            True if user has permission
        """
        if user_id not in self.users:
            logger.warning(f"User not found: {user_id}")
            return False
        
        user = self.users[user_id]
        
        if not user.is_active:
            logger.warning(f"User is inactive: {user_id}")
            return False
        
        # Check custom permissions first
        if permission in user.custom_permissions:
            return True
        
        # Check role permissions
        for role_name in user.roles:
            if role_name in self.roles:
                role = self.roles[role_name]
                if role.has_permission(permission):
                    return True
        
        return False
    
    def get_resource_limits(self, user_id: str) -> ResourceLimit:
        """
        Get effective resource limits for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            ResourceLimit object with combined limits
        """
        if user_id not in self.users:
            return ResourceLimit()
        
        user = self.users[user_id]
        
        # Start with custom limits if specified
        if user.custom_limits:
            return user.custom_limits
        
        # Otherwise, get most permissive limits from roles
        limits = ResourceLimit()
        
        for role_name in user.roles:
            if role_name in self.roles:
                role_limits = self.roles[role_name].resource_limits
                
                # Take maximum of each limit
                if role_limits.max_tokens_per_request:
                    if limits.max_tokens_per_request is None:
                        limits.max_tokens_per_request = role_limits.max_tokens_per_request
                    else:
                        limits.max_tokens_per_request = max(
                            limits.max_tokens_per_request,
                            role_limits.max_tokens_per_request
                        )
                
                # Similar for other limits...
                if role_limits.max_requests_per_day:
                    if limits.max_requests_per_day is None:
                        limits.max_requests_per_day = role_limits.max_requests_per_day
                    else:
                        limits.max_requests_per_day = max(
                            limits.max_requests_per_day,
                            role_limits.max_requests_per_day
                        )
                
                if role_limits.max_cost_per_day:
                    if limits.max_cost_per_day is None:
                        limits.max_cost_per_day = role_limits.max_cost_per_day
                    else:
                        limits.max_cost_per_day = max(
                            limits.max_cost_per_day,
                            role_limits.max_cost_per_day
                        )
        
        return limits
    
    def get_allowed_providers(self, user_id: str) -> List[str]:
        """Get list of providers user can access"""
        provider_permissions = [
            Permission.USE_MOCK,
            Permission.USE_ANTHROPIC,
            Permission.USE_OPENAI,
            Permission.USE_GOOGLE,
            Permission.USE_META,
            Permission.USE_HUGGINGFACE,
            Permission.USE_AWS,
        ]
        
        allowed = []
        for perm in provider_permissions:
            if self.check_permission(user_id, perm.value):
                # Extract provider name from permission
                provider = perm.value.replace('use_', '').replace('_provider', '')
                allowed.append(provider)
        
        return allowed
    
    def deactivate_user(self, user_id: str):
        """Deactivate a user"""
        if user_id in self.users:
            self.users[user_id].is_active = False
            self.save_data()
            logger.info(f"Deactivated user: {user_id}")
    
    def activate_user(self, user_id: str):
        """Activate a user"""
        if user_id in self.users:
            self.users[user_id].is_active = True
            self.save_data()
            logger.info(f"Activated user: {user_id}")
    
    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """Get detailed user information"""
        if user_id not in self.users:
            return None
        
        user = self.users[user_id]
        
        # Collect all permissions
        all_permissions = set(user.custom_permissions)
        for role_name in user.roles:
            if role_name in self.roles:
                all_permissions.update(self.roles[role_name].permissions)
        
        return {
            'user_id': user.user_id,
            'email': user.email,
            'roles': list(user.roles),
            'permissions': list(all_permissions),
            'resource_limits': self.get_resource_limits(user_id).to_dict(),
            'allowed_providers': self.get_allowed_providers(user_id),
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
    
    def list_users(self) -> List[Dict]:
        """List all users"""
        return [self.get_user_info(uid) for uid in self.users.keys()]
    
    def list_roles(self) -> List[Dict]:
        """List all roles"""
        return [role.to_dict() for role in self.roles.values()]
    
    def save_data(self):
        """Save RBAC data to storage"""
        # Save roles
        roles_data = {name: role.to_dict() for name, role in self.roles.items()}
        with open(self.storage_path / "roles.json", 'w') as f:
            json.dump(roles_data, f, indent=2)
        
        # Save users
        users_data = {uid: user.to_dict() for uid, user in self.users.items()}
        with open(self.storage_path / "users.json", 'w') as f:
            json.dump(users_data, f, indent=2)
    
    def load_data(self):
        """Load RBAC data from storage"""
        # Load roles
        roles_file = self.storage_path / "roles.json"
        if roles_file.exists():
            with open(roles_file, 'r') as f:
                roles_data = json.load(f)
                self.roles = {name: Role.from_dict(data) for name, data in roles_data.items()}
        
        # Load users
        users_file = self.storage_path / "users.json"
        if users_file.exists():
            with open(users_file, 'r') as f:
                users_data = json.load(f)
                self.users = {uid: User.from_dict(data) for uid, data in users_data.items()}


class RBACException(Exception):
    """Exception raised for RBAC violations"""
    pass


class PermissionDeniedError(RBACException):
    """Raised when user doesn't have required permission"""
    pass


class ResourceLimitExceededError(RBACException):
    """Raised when resource limit is exceeded"""
    pass
