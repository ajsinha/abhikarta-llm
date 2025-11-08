# Abhikarta LLM User Management System
## Detailed Architecture Documentation

---

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

### Legal Notice

This document and the associated software architecture are proprietary and confidential. Unauthorized copying, distribution, modification, or use of this document or the software system it describes is strictly prohibited without explicit written permission from the copyright holder. This document is provided "as is" without warranty of any kind, either expressed or implied. The copyright holder shall not be liable for any damages arising from the use of this document or the software system it describes.

**Patent Pending**: Certain architectural patterns and implementations described in this document may be subject to patent applications.

---

## Table of Contents

1. [Introduction](#introduction)
2. [System Overview](#system-overview)
3. [Core Components](#core-components)
4. [Architecture Patterns](#architecture-patterns)
5. [Data Model](#data-model)
6. [RBAC Implementation](#rbac-implementation)
7. [Authentication & Authorization](#authentication--authorization)
8. [Persistence Layer](#persistence-layer)
9. [Security Considerations](#security-considerations)
10. [Usage Guidelines](#usage-guidelines)
11. [API Reference](#api-reference)
12. [Best Practices](#best-practices)

---

## Introduction

The Abhikarta LLM User Management System is a comprehensive Role-Based Access Control (RBAC) solution designed for managing users, roles, and resources in large language model applications. The system provides enterprise-grade security, flexible permission management, and multiple persistence options.

### Key Features

- **Robust RBAC**: Complete role-based access control with fine-grained permissions
- **Pattern Matching**: Support for wildcard and prefix-based resource patterns
- **JWT Authentication**: Secure token-based authentication mechanism
- **Multiple Persistence**: Support for both database and JSON file storage
- **Thread-Safe**: All operations are thread-safe for concurrent access
- **Cascading Operations**: Automatic data consistency through cascading deletions
- **Admin User**: Captive admin user with full system access
- **Resource Control**: Enable/disable resources without deletion
- **Extensible**: Abstract base classes allow easy extension

---

## System Overview

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                   UserRegistry (Singleton)                   │
│  - User Management     - Authentication                      │
│  - Role Management     - Authorization                       │
│  - Resource Management - Pattern Matching                    │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│              UserManager (Abstract Base Class)               │
└──────────────────┬──────────────────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
┌────────▼─────────┐  ┌──────▼───────────┐
│  UserManagerDB   │  │ UserManagerJSON  │
│  (Database)      │  │ (JSON File)      │
└──────────────────┘  └──────────────────┘
```

### Component Relationships

1. **UserRegistry**: Central singleton managing all RBAC operations
2. **UserManager**: Abstract interface for persistence operations
3. **UserManagerDB**: Database-backed persistence implementation
4. **UserManagerJSON**: JSON file-backed persistence implementation
5. **User, Role, Resource**: Core data model entities
6. **Permission**: Fine-grained permission specification

---

## Core Components

### 1. User Class (`user.py`)

Represents a user entity in the system.

**Attributes:**
- `userid`: Unique identifier
- `fullname`: User's full name
- `emailaddress`: Email address
- `password_hash`: Encrypted password (bcrypt)
- `roles`: List of assigned role names
- `enabled`: Account status
- `created_at`, `updated_at`, `last_login`: Timestamps
- `metadata`: Additional user data

**Key Methods:**
- `add_role(role)`: Add a role to the user
- `remove_role(role)`: Remove a role from the user
- `verify_password(password)`: Verify password
- `update_password(new_password)`: Update password
- `to_dict() / from_dict()`: Serialization

### 2. Role Class (`user.py`)

Represents a role with associated resources and permissions.

**Attributes:**
- `name`: Unique role identifier
- `description`: Role description
- `resources`: Dictionary mapping resource names to Permission objects
- `enabled`: Role status
- `created_at`: Creation timestamp
- `metadata`: Additional role data

**Key Methods:**
- `add_resource(resource_name, permission)`: Add resource with permissions
- `remove_resource(resource_name)`: Remove resource
- `has_resource(resource_name)`: Check resource existence
- `get_permission(resource_name)`: Get permissions for resource

### 3. Resource Class (`user.py`)

Represents a system resource that can be accessed.

**Attributes:**
- `name`: Unique resource identifier
- `resource_type`: Type/category of resource
- `description`: Resource description
- `enabled`: Resource status (active/inactive)
- `created_at`: Creation timestamp
- `metadata`: Additional resource data

### 4. Permission Class (`user.py`)

Represents fine-grained permissions on a resource.

**Attributes:**
- `create`: Permission to create
- `read`: Permission to read
- `update`: Permission to modify
- `delete`: Permission to delete
- `execute`: Permission to execute operations

**Factory Methods:**
- `all_permissions()`: All permissions enabled
- `read_only()`: Only read permission enabled

### 5. PasswordEncryption Class (`user.py`)

Utility class for secure password handling.

**Methods:**
- `encrypt_password(password)`: Encrypt using bcrypt
- `verify_password(password, hash)`: Verify password
- `generate_secure_password(length)`: Generate random password

### 6. UserRegistry Class (`user_registry.py`)

Singleton class managing all RBAC operations.

**Key Features:**
- Thread-safe operations
- Pattern-based permission matching
- JWT token generation and verification
- Cascading deletions
- Statistics and monitoring

**Core Methods:**

*User Management:*
- `add_user(user)`: Add new user
- `remove_user(userid)`: Remove user
- `get_user(userid)`: Retrieve user
- `list_users()`: List all users
- `update_user(userid, **kwargs)`: Update user

*Role Management:*
- `add_role(role)`: Add new role
- `remove_role(role_name)`: Remove role (with cascading)
- `get_role(role_name)`: Retrieve role
- `list_roles()`: List all roles
- `add_resource_to_role(...)`: Add resource to role
- `remove_resource_from_role(...)`: Remove resource from role

*Resource Management:*
- `add_resource(resource)`: Add new resource
- `remove_resource(resource_name)`: Remove resource (with cascading)
- `get_resource(resource_name)`: Retrieve resource
- `list_resources()`: List all resources
- `enable_resource(resource_name)`: Enable resource
- `disable_resource(resource_name)`: Disable resource

*Authorization:*
- `get_user_permissions(userid)`: Get all user permissions
- `check_permission(userid, resource, type)`: Check specific permission
- `get_accessible_resources(userid)`: Get accessible resources

*Authentication:*
- `authenticate(userid, password)`: Authenticate and get JWT token
- `verify_token(token)`: Verify JWT token
- `refresh_token(token)`: Refresh JWT token

### 7. UserManager Abstract Class (`user_manager.py`)

Abstract base class defining the persistence interface.

**Abstract Methods:**
- `initialize()`: Initialize persistence layer
- `close()`: Cleanup resources
- `save_user(user)`: Persist user
- `load_user(userid)`: Load user
- `delete_user(userid)`: Delete user
- `list_users()`: List all users
- (Similar methods for roles and resources)

**Convenience Methods:**
- `add_resource_to_role(...)`: Add resource to role
- `remove_resource_from_role(...)`: Remove resource from role
- `add_role_to_user(...)`: Add role to user
- `remove_role_from_user(...)`: Remove role from user
- `get_user_roles(userid)`: Get user's roles
- `get_role_resources(role_name)`: Get role's resources

### 8. UserManagerDB Class (`user_manager_db.py`)

Database-backed implementation of UserManager.

**Features:**
- Supports PostgreSQL, MySQL, SQLite
- Transaction support
- Connection pooling
- Thread-safe operations
- Proper referential integrity

**Database Schema:**
- `users`: User accounts
- `roles`: Role definitions
- `resources`: System resources
- `user_roles`: User-to-role mappings
- `role_resources`: Role-to-resource mappings with permissions

### 9. UserManagerJSON Class (`user_manager_json.py`)

JSON file-backed implementation of UserManager.

**Features:**
- Simple file-based storage
- Automatic backup on write
- Auto-reload capability
- Thread-safe file operations
- Suitable for smaller deployments

---

## Architecture Patterns

### 1. Singleton Pattern

**UserRegistry** implements the singleton pattern to ensure only one registry instance exists.

```python
class UserRegistry:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
```

**Benefits:**
- Single source of truth
- Consistent state across application
- Thread-safe initialization

### 2. Strategy Pattern

**UserManager** uses the strategy pattern to allow different persistence implementations.

```python
# Abstract Strategy
class UserManager(ABC):
    @abstractmethod
    def save_user(self, user): pass

# Concrete Strategies
class UserManagerDB(UserManager):
    def save_user(self, user): 
        # Database implementation
        
class UserManagerJSON(UserManager):
    def save_user(self, user):
        # JSON file implementation
```

**Benefits:**
- Easy to switch persistence backends
- Testability
- Extensibility

### 3. Factory Pattern

**Permission** class provides factory methods for common permission sets.

```python
# Factory methods
Permission.all_permissions()
Permission.read_only()
```

### 4. Repository Pattern

**UserManager** acts as a repository abstracting data access.

---

## Data Model

### Entity Relationships

```
┌──────────┐     ┌────────────┐     ┌──────────┐
│  User    │────▶│ User_Roles │◀────│   Role   │
└──────────┘     └────────────┘     └──────────┘
                                           │
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │Role_Resources│
                                    └──────────────┘
                                           │
                                           │
                                           ▼
                                    ┌──────────┐
                                    │ Resource │
                                    └──────────┘
```

### Relationships

1. **User → Roles**: Many-to-Many
   - A user can have multiple roles
   - A role can be assigned to multiple users

2. **Role → Resources**: Many-to-Many with Permissions
   - A role can access multiple resources
   - A resource can be accessed by multiple roles
   - Each relationship includes specific permissions

3. **Resource**: Independent entity
   - Can be enabled/disabled
   - When disabled, not accessible even if role grants access

---

## RBAC Implementation

### Permission Resolution Algorithm

When checking user permissions, the system follows this algorithm:

1. **Load User**: Retrieve user and verify enabled status
2. **Check Admin**: If user is admin, grant all permissions
3. **Iterate Roles**: For each role assigned to user:
   - Verify role is enabled
   - For each resource in role:
     - If pattern (contains `*`):
       - Match against all enabled resources
       - Aggregate permissions (OR operation)
     - If direct reference:
       - Check resource is enabled
       - Aggregate permissions (OR operation)
4. **Return**: Aggregated permissions

### Pattern Matching

The system supports two pattern types:

1. **Wildcard (`*`)**: Matches everything
   ```python
   "*" → Matches all resources
   ```

2. **Prefix (`prefix*`)**: Matches resources starting with prefix
   ```python
   "yahoo*" → Matches: yahoo_finance, yahoo_news, yahoo_weather
   "google*" → Matches: google_search, google_maps
   ```

### Example

```python
# User has two roles
roles = ["developer", "yahoo_user"]

# developer role has:
#   - model_api: read, execute
#   - training_data: read

# yahoo_user role has:
#   - yahoo*: all permissions

# Final permissions:
# - model_api: read, execute
# - training_data: read
# - yahoo_finance: create, read, update, delete, execute
# - yahoo_news: create, read, update, delete, execute
# - yahoo_weather: create, read, update, delete, execute
```

---

## Authentication & Authorization

### Authentication Flow

```
┌─────────┐                 ┌──────────────┐
│ Client  │                 │ UserRegistry │
└────┬────┘                 └──────┬───────┘
     │                             │
     │ authenticate(user, pass)    │
     ├─────────────────────────────▶
     │                             │
     │                    [Verify Credentials]
     │                             │
     │                    [Generate JWT Token]
     │                             │
     │          JWT Token          │
     │◀─────────────────────────────┤
     │                             │
```

### JWT Token Structure

```json
{
  "userid": "user123",
  "fullname": "John Doe",
  "emailaddress": "john@example.com",
  "roles": ["developer", "analyst"],
  "exp": 1735689600,  // Expiration time
  "iat": 1735603200   // Issued at time
}
```

### Authorization Flow

```
┌─────────┐                 ┌──────────────┐
│ Client  │                 │ UserRegistry │
└────┬────┘                 └──────┬───────┘
     │                             │
     │ check_permission(user,      │
     │   resource, type)           │
     ├─────────────────────────────▶
     │                             │
     │                    [Get User Permissions]
     │                             │
     │                    [Check Specific Permission]
     │                             │
     │          True/False         │
     │◀─────────────────────────────┤
     │                             │
```

---

## Persistence Layer

### Database Schema (PostgreSQL)

**Tables:**

1. **users**
   - Primary Key: `userid`
   - Columns: fullname, emailaddress, password_hash, enabled, created_at, updated_at, last_login, metadata

2. **roles**
   - Primary Key: `role_name`
   - Columns: description, enabled, created_at, metadata

3. **resources**
   - Primary Key: `resource_name`
   - Columns: resource_type, description, enabled, created_at, metadata

4. **user_roles**
   - Primary Key: (userid, role_name)
   - Foreign Keys: userid → users, role_name → roles
   - CASCADE DELETE on both foreign keys

5. **role_resources**
   - Primary Key: (role_name, resource_name)
   - Foreign Key: role_name → roles
   - Columns: can_create, can_read, can_update, can_delete, can_execute
   - CASCADE DELETE on role_name

### JSON File Structure

```json
{
  "users": [
    {
      "userid": "...",
      "fullname": "...",
      "emailaddress": "...",
      "password_hash": "...",
      "roles": ["role1", "role2"],
      "enabled": true,
      "created_at": "...",
      "updated_at": "...",
      "last_login": null,
      "metadata": {}
    }
  ],
  "roles": [
    {
      "name": "...",
      "description": "...",
      "resources": {
        "resource1": {
          "create": true,
          "read": true,
          "update": false,
          "delete": false,
          "execute": true
        }
      },
      "enabled": true,
      "created_at": "...",
      "metadata": {}
    }
  ],
  "resources": [
    {
      "name": "...",
      "resource_type": "...",
      "description": "...",
      "enabled": true,
      "created_at": "...",
      "metadata": {}
    }
  ],
  "metadata": {
    "last_updated": "...",
    "version": "1.0"
  }
}
```

---

## Security Considerations

### Password Security

- **Bcrypt**: Uses bcrypt with work factor of 12
- **Salting**: Automatic per-password salting
- **No Plain Text**: Passwords never stored or logged in plain text

### JWT Security

- **Secret Key**: Should be changed in production
- **Expiration**: Configurable expiration time (default 24 hours)
- **Signing**: HMAC-SHA256 algorithm
- **Validation**: Verify user still exists and is enabled

### Thread Safety

- **Singleton Lock**: Double-checked locking for initialization
- **Registry Lock**: RLock for all registry operations
- **File Lock**: Separate lock for JSON file operations
- **Database**: Connection pool handles concurrency

### Data Consistency

- **Cascading Deletions**: Automatic cleanup of dependencies
- **Validation**: All entities validated before persistence
- **Transactions**: Database operations wrapped in transactions
- **Referential Integrity**: Foreign key constraints in database

### Admin Protection

- **Cannot Delete**: Admin user cannot be deleted
- **Cannot Remove**: Admin role cannot be removed
- **Full Access**: Admin always has all permissions
- **System User**: Marked as system user in metadata

---

## Usage Guidelines

### Best Practices

1. **Change Default Password**: Immediately change admin default password
2. **Use Patterns Wisely**: Avoid overly broad patterns
3. **Disable, Don't Delete**: Disable resources/roles instead of deleting when possible
4. **Regular Audits**: Review user permissions regularly
5. **Least Privilege**: Grant minimum necessary permissions
6. **Monitor Failed Logins**: Track authentication failures
7. **Rotate JWT Secret**: Change JWT secret key periodically
8. **Backup Data**: Regular backups of JSON file or database

### Performance Considerations

1. **Connection Pooling**: Use database connection pooling
2. **Caching**: Consider caching user permissions
3. **Batch Operations**: Use bulk operations when possible
4. **Index Usage**: Ensure proper database indexes
5. **Pattern Efficiency**: Limit use of wildcard patterns

---

## API Reference

See `quick_reference.md` for concise API reference.

---

## Best Practices

### For Developers

1. Always use the singleton `get_user_registry()` function
2. Handle exceptions appropriately
3. Log important operations
4. Use context managers for database connections
5. Validate input before passing to methods

### For Administrators

1. Review and approve all role definitions
2. Regularly audit user access
3. Monitor authentication statistics
4. Keep backups of user data
5. Document custom metadata usage

### For Security

1. Never log passwords or tokens
2. Use HTTPS for token transmission
3. Implement rate limiting on authentication
4. Monitor for unusual access patterns
5. Regular security audits

---

## Conclusion

The Abhikarta LLM User Management System provides a robust, flexible, and secure RBAC implementation suitable for enterprise applications. Its modular architecture allows easy extension and customization while maintaining security and data consistency.

For quick reference and examples, see `quick_reference.md`.

For implementation details, refer to the source code comments and docstrings.

---

**Document Version**: 1.0  
**Last Updated**: November 2025  
**Authors**: Ashutosh Sinha
