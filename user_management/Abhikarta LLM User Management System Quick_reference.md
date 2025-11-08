# Abhikarta LLM User Management System
## Quick Reference Guide

---

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

### Legal Notice

This document and the associated software architecture are proprietary and confidential. Unauthorized copying, distribution, modification, or use of this document or the software system it describes is strictly prohibited without explicit written permission from the copyright holder.

**Patent Pending**: Certain architectural patterns and implementations described in this document may be subject to patent applications.

---

## Quick Start

### Installation

```bash
pip install bcrypt PyJWT psycopg2-binary mysql-connector-python
```

### Basic Setup

```python
from user_registry import get_user_registry
from user import User, Role, Resource, Permission, PasswordEncryption

# Get the singleton registry
registry = get_user_registry()
```

---

## Common Operations

### 1. User Management

#### Create a User

```python
user = User(
    userid="john_doe",
    fullname="John Doe",
    emailaddress="john@example.com",
    password_hash=PasswordEncryption.encrypt_password("SecurePass123!"),
    roles=["developer"]
)
registry.add_user(user)
```

#### Update User

```python
registry.update_user("john_doe", fullname="John Smith", enabled=False)
```

#### Get User

```python
user = registry.get_user("john_doe")
print(f"User: {user.fullname}, Roles: {user.roles}")
```

#### List All Users

```python
users = registry.list_users()
for user in users:
    print(f"{user.userid}: {user.fullname}")
```

#### Delete User

```python
registry.remove_user("john_doe")
```

---

### 2. Role Management

#### Create a Role

```python
role = Role(
    name="data_analyst",
    description="Data analyst with read access"
)
registry.add_role(role)
```

#### Add Resource to Role

```python
registry.add_resource_to_role(
    "data_analyst",
    "analytics_dashboard",
    Permission(read=True)
)
```

#### Remove Resource from Role

```python
registry.remove_resource_from_role("data_analyst", "analytics_dashboard")
```

#### Get Role

```python
role = registry.get_role("data_analyst")
print(f"Role: {role.name}, Resources: {list(role.resources.keys())}")
```

#### List All Roles

```python
roles = registry.list_roles()
for role in roles:
    print(f"{role.name}: {role.description}")
```

#### Delete Role (Cascading)

```python
# This removes the role from all users first, then deletes the role
registry.remove_role("data_analyst")
```

---

### 3. Resource Management

#### Create a Resource

```python
resource = Resource(
    name="customer_data",
    resource_type="data",
    description="Customer database",
    enabled=True
)
registry.add_resource(resource)
```

#### Get Resource

```python
resource = registry.get_resource("customer_data")
print(f"Resource: {resource.name}, Type: {resource.resource_type}")
```

#### List Resources

```python
# List all resources
all_resources = registry.list_resources()

# List by type
api_resources = registry.list_resources(resource_type="api")

# List only enabled
enabled_resources = registry.list_resources(enabled_only=True)
```

#### Enable/Disable Resource

```python
# Disable a resource (affects RBAC but doesn't delete)
registry.disable_resource("legacy_api")

# Re-enable later
registry.enable_resource("legacy_api")
```

#### Delete Resource (Cascading)

```python
# This removes the resource from all roles first, then deletes it
registry.remove_resource("customer_data")
```

---

### 4. Permission Management

#### Define Permissions

```python
# All permissions
perm = Permission.all_permissions()

# Read-only
perm = Permission.read_only()

# Custom permissions
perm = Permission(
    create=True,
    read=True,
    update=True,
    delete=False,
    execute=True
)
```

#### Check Specific Permission

```python
can_read = registry.check_permission(
    userid="john_doe",
    resource_name="customer_data",
    permission_type="read"
)
```

#### Get All User Permissions

```python
permissions = registry.get_user_permissions("john_doe")
for resource_name, perm in permissions.items():
    print(f"{resource_name}: read={perm.read}, write={perm.update}")
```

#### Get Accessible Resources

```python
# All accessible resources
resources = registry.get_accessible_resources("john_doe")

# Filtered by permission type
readable = registry.get_accessible_resources("john_doe", "read")
writable = registry.get_accessible_resources("john_doe", "update")
```

---

### 5. Pattern-Based Permissions

#### Using Wildcards

```python
# Create role with wildcard access
role = Role("superuser", "Full access to everything")
role.add_resource("*", Permission.all_permissions())
registry.add_role(role)
```

#### Using Prefix Patterns

```python
# Create role with prefix pattern
role = Role("google_user", "Access to all Google services")
role.add_resource("google*", Permission.all_permissions())
registry.add_role(role)

# This will match: google_search, google_maps, google_drive, etc.
```

#### Example Pattern Usage

```python
# Resources
registry.add_resource(Resource("yahoo_finance", "external", "Yahoo Finance"))
registry.add_resource(Resource("yahoo_news", "external", "Yahoo News"))
registry.add_resource(Resource("yahoo_sports", "external", "Yahoo Sports"))

# Role with pattern
role = Role("yahoo_user", "Yahoo services user")
role.add_resource("yahoo*", Permission(read=True, execute=True))
registry.add_role(role)

# User gets access to all yahoo_* resources
user = User(
    userid="jane",
    fullname="Jane Smith",
    emailaddress="jane@example.com",
    password_hash=PasswordEncryption.encrypt_password("pass"),
    roles=["yahoo_user"]
)
registry.add_user(user)

# Check access
print(registry.check_permission("jane", "yahoo_finance", "read"))  # True
print(registry.check_permission("jane", "yahoo_news", "read"))     # True
print(registry.check_permission("jane", "yahoo_sports", "read"))   # True
```

---

### 6. Authentication

#### Login (Get JWT Token)

```python
token = registry.authenticate("john_doe", "SecurePass123!")
if token:
    print(f"Login successful. Token: {token}")
else:
    print("Login failed")
```

#### Verify Token

```python
payload = registry.verify_token(token)
if payload:
    print(f"Valid token for user: {payload['userid']}")
    print(f"Roles: {payload['roles']}")
else:
    print("Invalid or expired token")
```

#### Refresh Token

```python
new_token = registry.refresh_token(old_token)
if new_token:
    print("Token refreshed successfully")
```

#### Update Last Login

```python
user = registry.get_user("john_doe")
user.update_last_login()
registry.update_user(user.userid, last_login=user.last_login)
```

---

### 7. Password Management

#### Encrypt Password

```python
encrypted = PasswordEncryption.encrypt_password("MySecurePassword123!")
```

#### Verify Password

```python
is_valid = PasswordEncryption.verify_password(
    "MySecurePassword123!",
    encrypted_hash
)
```

#### Generate Secure Password

```python
secure_pass = PasswordEncryption.generate_secure_password(length=16)
print(f"Generated password: {secure_pass}")
```

#### Change User Password

```python
user = registry.get_user("john_doe")
user.update_password("NewSecurePassword456!")
registry.update_user(user.userid, password_hash=user.password_hash)
```

---

### 8. Using UserManager (Persistence)

#### JSON File Persistence

```python
from user_manager_json import UserManagerJSON

# Initialize
manager = UserManagerJSON("config/users.json")
manager.initialize()

# Save data
manager.save_user(user)
manager.save_role(role)
manager.save_resource(resource)

# Load data
user = manager.load_user("john_doe")
role = manager.load_role("developer")
resource = manager.load_resource("api_endpoint")

# List data
users = manager.list_users()
roles = manager.list_roles()
resources = manager.list_resources()

# Convenience methods
manager.add_role_to_user("john_doe", "analyst")
manager.add_resource_to_role("analyst", "dashboard", Permission.read_only())

# Close
manager.close()
```

#### Database Persistence

```python
from user_manager_db import UserManagerDB
from db.db_connection_pool import DatabaseConnectionPool, PoolConfig

# Setup connection pool
pool = DatabaseConnectionPool(
    db_type='postgresql',
    host='localhost',
    database='abhikarta',
    user='dbuser',
    password='dbpass',
    pool_config=PoolConfig(min_idle=2, max_total=10)
)

# Initialize
manager = UserManagerDB(pool, db_type='postgresql')
manager.initialize()

# Use same interface as JSON manager
manager.save_user(user)
user = manager.load_user("john_doe")

# Close
manager.close()
```

---

### 9. Statistics and Monitoring

#### Get Registry Statistics

```python
stats = registry.get_statistics()
print(f"Total users: {stats['users']['total']}")
print(f"Enabled users: {stats['users']['enabled']}")
print(f"Total roles: {stats['roles']['total']}")
print(f"Total resources: {stats['resources']['total']}")
print(f"Auth success rate: {stats['authentication']['success_rate']:.2f}%")
```

#### Manager Statistics

```python
stats = manager.get_statistics()
print(f"Users in storage: {stats['users']['total']}")
print(f"Roles in storage: {stats['roles']['total']}")
```

---

### 10. Admin Operations

#### Admin Login

```python
# Default admin credentials (CHANGE IMMEDIATELY)
admin_token = registry.authenticate("admin", "admin123")
```

#### Change Admin Password

```python
admin = registry.get_user("admin")
admin.update_password("NewAdminPassword!")
# Save to persistence layer if using one
```

#### Admin Has Full Access

```python
# Admin can access any resource
can_access = registry.check_permission("admin", "any_resource", "delete")
# Always returns True

# Get all accessible resources
resources = registry.get_accessible_resources("admin")
# Returns all resources in the system
```

---

## Configuration

### JWT Configuration

```python
# In user_registry.py, modify these class variables:
UserRegistry.JWT_SECRET_KEY = "your-secret-key-here"
UserRegistry.JWT_ALGORITHM = "HS256"
UserRegistry.JWT_EXPIRATION_HOURS = 24
```

### Password Encryption Configuration

```python
# In user.py, modify this class variable:
PasswordEncryption.BCRYPT_ROUNDS = 12  # Higher = more secure but slower
```

---

## Error Handling

### Common Exceptions

```python
try:
    user = User(
        userid="test",
        fullname="Test User",
        emailaddress="test@example.com",
        password_hash=PasswordEncryption.encrypt_password("pass"),
        roles=["nonexistent_role"]  # Role doesn't exist
    )
    registry.add_user(user)
except ValueError as e:
    print(f"Error: {e}")  # Role 'nonexistent_role' does not exist
```

### Best Practice

```python
# Check before operations
if not registry.get_user("john_doe"):
    print("User not found")

if not registry.check_permission("john_doe", "api", "read"):
    print("Access denied")

# Validate before adding
from user_manager import UserManager
if manager.validate_user(user):
    manager.save_user(user)
```

---

## Database Setup

### PostgreSQL

```bash
# Create database
createdb abhikarta

# Run schema
psql abhikarta < schema.sql
```

### MySQL

```bash
# Create database
mysql -u root -p -e "CREATE DATABASE abhikarta;"

# Run schema (after converting to MySQL syntax)
mysql -u root -p abhikarta < schema.sql
```

### SQLite

```bash
# Create database and run schema
sqlite3 abhikarta.db < schema.sql
```

---

## Complete Example

```python
from user_registry import get_user_registry
from user import User, Role, Resource, Permission, PasswordEncryption

# Get registry
registry = get_user_registry()

# Create a resource
api_resource = Resource(
    name="payment_api",
    resource_type="api",
    description="Payment processing API"
)
registry.add_resource(api_resource)

# Create a role
cashier_role = Role("cashier", "Cashier with payment access")
cashier_role.add_resource("payment_api", Permission(read=True, execute=True))
registry.add_role(cashier_role)

# Create a user
cashier = User(
    userid="cashier001",
    fullname="Alice Cashier",
    emailaddress="alice@store.com",
    password_hash=PasswordEncryption.encrypt_password("CashierPass123!"),
    roles=["cashier"]
)
registry.add_user(cashier)

# Authenticate
token = registry.authenticate("cashier001", "CashierPass123!")
print(f"Login successful: {token is not None}")

# Check permission
can_process = registry.check_permission("cashier001", "payment_api", "execute")
print(f"Can process payments: {can_process}")

# Get all permissions
perms = registry.get_user_permissions("cashier001")
print(f"Accessible resources: {list(perms.keys())}")
```

---

## Troubleshooting

### Issue: User can't access resource

**Check:**
1. User exists and is enabled
2. User has role assigned
3. Role exists and is enabled
4. Role has resource
5. Resource exists and is enabled

```python
user = registry.get_user("userid")
print(f"User enabled: {user.enabled if user else False}")
print(f"User roles: {user.roles if user else []}")

for role_name in user.roles:
    role = registry.get_role(role_name)
    print(f"Role {role_name} enabled: {role.enabled if role else False}")
    print(f"Role resources: {list(role.resources.keys()) if role else []}")

resource = registry.get_resource("resource_name")
print(f"Resource enabled: {resource.enabled if resource else False}")
```

### Issue: Authentication fails

**Check:**
1. Correct userid
2. Correct password
3. User is enabled

```python
user = registry.get_user("userid")
if not user:
    print("User does not exist")
elif not user.enabled:
    print("User is disabled")
else:
    # Test password separately
    if user.verify_password("password"):
        print("Password is correct")
    else:
        print("Password is incorrect")
```

---

## Additional Resources

- **Full Documentation**: See `architecture_documentation.md`
- **Example Code**: See `example_usage.py`
- **Database Schema**: See `schema.sql`
- **Sample Data**: See `config/users.json`

---

**Document Version**: 1.0  
**Last Updated**: November 2025  
**Authors**: Ashutosh Sinha
