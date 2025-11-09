# Abhikarta LLM User Management System

**Version**: 1.0  
**Date**: November 2025  
**Author**: Ashutosh Sinha (ajsinha@gmail.com)

---

## Copyright and Legal Notice

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email**: ajsinha@gmail.com

### Legal Notice

This document and the associated software architecture are proprietary and confidential. Unauthorized copying, distribution, modification, or use of this document or the software system it describes is strictly prohibited without explicit written permission from the copyright holder. This document is provided "as is" without warranty of any kind, either expressed or implied. The copyright holder shall not be liable for any damages arising from the use of this document or the software system it describes.

**Patent Pending**: Certain architectural patterns and implementations described in this document may be subject to patent applications.

---

## Overview

The Abhikarta LLM User Management System is a comprehensive, enterprise-grade Role-Based Access Control (RBAC) solution designed specifically for large language model applications. It provides robust user authentication, flexible authorization, and multiple persistence options.

### Key Features

✅ **Complete RBAC Implementation**: Users, roles, and resources with fine-grained permissions  
✅ **Pattern-Based Permissions**: Support for wildcards (*) and prefix matching (yahoo*)  
✅ **JWT Authentication**: Secure token-based authentication with configurable expiration  
✅ **Multiple Persistence Options**: Database (PostgreSQL/MySQL/SQLite) and JSON file storage  
✅ **Thread-Safe Operations**: All operations are thread-safe for concurrent access  
✅ **Cascading Deletions**: Automatic data consistency maintenance  
✅ **Resource Control**: Enable/disable resources without deletion  
✅ **Admin System**: Built-in admin user with full system access  
✅ **Bcrypt Password Encryption**: Industry-standard secure password hashing  
✅ **Comprehensive Documentation**: Detailed architecture and quick reference guides

---

## Project Structure

```
abhikarta_user_management/
├── README.md                          # This file
├── PROJECT_SUMMARY.md                 # Executive summary
├── architecture_documentation.md      # Detailed architecture documentation
├── quick_reference.md                 # Quick reference guide
├── user.py                           # User, Role, Resource, Permission classes
├── user_registry.py                  # UserRegistry singleton (RBAC core)
├── user_manager.py                   # Abstract UserManager base class
├── user_manager_db.py                # Database-backed implementation
├── user_manager_json.py              # JSON file-backed implementation
├── create_sqlite_db.py               # SQLite database creation utility
├── example_usage.py                  # Comprehensive usage examples
├── schema.sql                        # Database schema (PostgreSQL)
└── config/
    └── users.json                    # Sample JSON configuration file
```

---

## Quick Start

### Installation

```bash
# Install required dependencies
pip install bcrypt PyJWT psycopg2-binary mysql-connector-python
```

### Basic Usage

```python
from user_registry import get_user_registry
from user import User, Role, Resource, Permission, PasswordEncryption

# Get the singleton registry
registry = get_user_registry()

# Create a resource
resource = Resource("api_endpoint", "api", "Main API endpoint")
registry.add_resource(resource)

# Create a role with permissions
role = Role("api_user", "API user with read access")
role.add_resource("api_endpoint", Permission(read=True, execute=True))
registry.add_role(role)

# Create a user
user = User(
    userid="john_doe",
    fullname="John Doe",
    emailaddress="john@example.com",
    password_hash=PasswordEncryption.encrypt_password("SecurePass123!"),
    roles=["api_user"]
)
registry.add_user(user)

# Authenticate
token = registry.authenticate("john_doe", "SecurePass123!")
if token:
    print("Authentication successful!")

# Check permission
can_read = registry.check_permission("john_doe", "api_endpoint", "read")
print(f"Can read: {can_read}")
```

---

## Core Components

### 1. UserRegistry (Singleton)
Central RBAC management system that handles:
- User management (CRUD operations)
- Role management with pattern matching
- Resource management with enable/disable
- Authentication (JWT tokens)
- Authorization (permission checking)
- Statistics and monitoring

### 2. User Class
Represents a user with:
- Unique userid, fullname, email
- Encrypted password (bcrypt)
- Multiple roles
- Enable/disable status
- Metadata support

### 3. Role Class
Represents a role with:
- Resource-to-permission mappings
- Pattern support (*, prefix*)
- Enable/disable status
- Metadata support

### 4. Resource Class
Represents a system resource with:
- Name and type
- Enable/disable status
- Description and metadata

### 5. Permission Class
Fine-grained permissions:
- create, read, update, delete, execute

### 6. UserManager (Abstract)
Persistence layer interface with two implementations:
- **UserManagerDB**: Database-backed (PostgreSQL/MySQL/SQLite)
- **UserManagerJSON**: JSON file-backed

---

## Pattern-Based Permissions

The system supports flexible permission patterns:

### Wildcard (`*`)
Grants access to all resources:
```python
role.add_resource("*", Permission.all_permissions())
# Matches: ALL resources in the system
```

### Prefix Pattern (`prefix*`)
Grants access to resources matching the prefix:
```python
role.add_resource("google*", Permission.all_permissions())
# Matches: google_search, google_maps, google_drive, etc.
```

---

## Database Setup

### SQLite (Easiest - Recommended for Development)

Use the included utility script to automatically create a SQLite database:

```bash
# Create database with default name (abhikarta.db_management)
python create_sqlite_db.py

# Create database with custom name
python create_sqlite_db.py --database my_database.db_management

# Overwrite existing database
python create_sqlite_db.py --overwrite

# Verbose output
python create_sqlite_db.py --verbose
```

The script automatically:
- Reads and adapts the PostgreSQL schema for SQLite
- Creates all tables with proper constraints
- Inserts the admin user and sample data
- Verifies the schema was created correctly

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

# Note: Convert schema.sql for MySQL syntax first
# Then run: mysql -u root -p abhikarta < schema_mysql.sql
```

---

## Admin User

The system includes a built-in admin user with full system access:

- **Username**: `admin`
- **Default Password**: `admin123` (⚠️ **CHANGE IMMEDIATELY**)
- **Permissions**: Full access to all resources
- **Protection**: Cannot be deleted

### Change Admin Password

```python
from user_registry import get_user_registry
from user import PasswordEncryption

registry = get_user_registry()
admin = registry.get_user("admin")
admin.update_password("NewSecureAdminPassword!")
```

---

## Security Features

### Password Security
- **Bcrypt Hashing**: Industry-standard with configurable work factor
- **Automatic Salting**: Unique salt per password
- **No Plain Text**: Passwords never stored or logged in plain text

### JWT Security
- **HMAC-SHA256**: Secure signing algorithm
- **Expiration**: Configurable token lifetime (default: 24 hours)
- **Validation**: Verifies user existence and enabled status
- **Refresh**: Token refresh capability

### Thread Safety
- **Singleton Lock**: Double-checked locking for initialization
- **Registry Lock**: RLock for all registry operations
- **File Lock**: Separate lock for JSON file operations

### Data Consistency
- **Cascading Deletions**: Automatic cleanup of dependencies
- **Validation**: All entities validated before persistence
- **Transactions**: Database operations wrapped in transactions

---

## Usage Examples

### Example 1: Basic Operations

```python
# See example_usage.py for complete examples
from user_registry import get_user_registry
from user import User, Role, Resource, Permission, PasswordEncryption

registry = get_user_registry()

# Create resource
resource = Resource("payment_api", "api", "Payment processing")
registry.add_resource(resource)

# Create role
role = Role("cashier", "Cashier role")
role.add_resource("payment_api", Permission(read=True, execute=True))
registry.add_role(role)

# Create user
user = User(
    userid="cashier001",
    fullname="Alice Cashier",
    emailaddress="alice@store.com",
    password_hash=PasswordEncryption.encrypt_password("SecurePass!"),
    roles=["cashier"]
)
registry.add_user(user)

# Authenticate
token = registry.authenticate("cashier001", "SecurePass!")

# Check permission
can_process = registry.check_permission("cashier001", "payment_api", "execute")
```

### Example 2: JSON Persistence

```python
from user_manager_json import UserManagerJSON

manager = UserManagerJSON("config/users.json")
manager.initialize()

# Save data
manager.save_user(user)
manager.save_role(role)
manager.save_resource(resource)

# Load data
loaded_user = manager.load_user("cashier001")
```

### Example 3: Database Persistence

```python
from user_manager_db import UserManagerDB
from db_management.db_connection_pool import DatabaseConnectionPool

pool = DatabaseConnectionPool(
    db_type='postgresql',
    host='localhost',
    database='abhikarta'
)

manager = UserManagerDB(pool)
manager.initialize()

# Use same interface as JSON manager
manager.save_user(user)
```

---

## Documentation

### Detailed Documentation
- **architecture_documentation.md**: Complete architecture, design patterns, and technical details
- **quick_reference.md**: Quick reference for common operations

### Code Examples
- **example_usage.py**: Comprehensive examples demonstrating all features

---

## File Descriptions

| File | Purpose |
|------|---------|
| `user.py` | Core data models (User, Role, Resource, Permission) and password encryption |
| `user_registry.py` | Singleton RBAC management system |
| `user_manager.py` | Abstract base class for persistence layer |
| `user_manager_db.py` | Database-backed persistence implementation |
| `user_manager_json.py` | JSON file-backed persistence implementation |
| `create_sqlite_db.py` | Utility to create SQLite database from schema.sql |
| `example_usage.py` | Comprehensive usage examples |
| `schema.sql` | PostgreSQL database schema |
| `config/users.json` | Sample JSON configuration with example data |

---

## Testing

Run the comprehensive examples:

```bash
python example_usage.py
```

This will execute 9 different examples demonstrating:
1. Basic operations
2. Pattern-based permissions
3. Disabled resources
4. Cascading deletions
5. JSON persistence
6. Statistics and monitoring
7. Admin operations
8. Multiple roles per user
9. Token refresh

---

## Configuration

### JWT Configuration

Edit `user_registry.py`:

```python
class UserRegistry:
    JWT_SECRET_KEY = "your-secret-key-here"  # Change in production!
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24
```

### Password Encryption

Edit `user.py`:

```python
class PasswordEncryption:
    BCRYPT_ROUNDS = 12  # Higher = more secure but slower
```

---

## Best Practices

### Security
1. ✅ Change admin password immediately
2. ✅ Use strong JWT secret key in production
3. ✅ Use HTTPS for token transmission
4. ✅ Implement rate limiting on authentication
5. ✅ Regular security audits

### Operations
1. ✅ Disable resources instead of deleting when possible
2. ✅ Grant minimum necessary permissions (least privilege)
3. ✅ Regular backups of user data
4. ✅ Monitor authentication statistics
5. ✅ Document custom metadata usage

### Performance
1. ✅ Use database connection pooling
2. ✅ Consider caching user permissions
3. ✅ Limit use of wildcard patterns
4. ✅ Use bulk operations when possible
5. ✅ Ensure proper database indexes

---

## Troubleshooting

### Issue: Authentication fails
**Check:**
- User exists and is enabled
- Password is correct
- Check authentication statistics

### Issue: User can't access resource
**Check:**
- User has role assigned
- Role is enabled
- Role has resource
- Resource is enabled

See `quick_reference.md` for detailed troubleshooting steps.

---

## Support

For questions, issues, or feature requests, please contact:

**Ashutosh Sinha**  
Email: ajsinha@gmail.com

---

## License

Copyright © 2025-2030, All Rights Reserved. See Legal Notice above for full terms.

---

## Changelog

### Version 1.0 (November 2025)
- Initial release
- Complete RBAC implementation
- JWT authentication
- Database and JSON persistence
- Pattern-based permissions
- Comprehensive documentation

---

**Thank you for using the Abhikarta LLM User Management System!**
