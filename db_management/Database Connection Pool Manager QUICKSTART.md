# db_management - Database Connection Pool Manager

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha** | Email: ajsinha@gmail.com

High-performance, thread-safe database connection pool manager for Python applications supporting SQLite, PostgreSQL, and MySQL.

---

## Quick Start

### Installation

```bash
# Install from the module directory
cd db_management
pip install .

# Or install with database-specific extras
pip install ".[postgresql]"  # For PostgreSQL
pip install ".[mysql]"       # For MySQL
pip install ".[all]"         # For all databases
```

### Basic Usage

```python
from db_management import get_pool_manager, SQLitePoolConfig

# Get singleton manager
manager = get_pool_manager()

# Create a connection pool
config = SQLitePoolConfig(
    pool_name="my_app",
    database_path="app.db",
    min_connections=2,
    max_connections=10
)
manager.create_pool(config)

# Pattern 1: PooledConnection as context manager (Recommended)
conn = manager.get_connection_from_pool("my_app")
with conn as connection:
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
# Connection automatically returned to pool

# Pattern 2: Pool's context manager (Also Recommended)
with manager.get_connection_context("my_app") as connection:
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
```

---

## Module Structure

```
db_management/
├── __init__.py              # Public API exports
├── pool_config.py          # Configuration classes
├── abstract_pool.py        # Abstract base classes  
├── connection_pools.py     # Concrete implementations
├── pool_manager.py         # Singleton manager
│
├── examples/
│   ├── __init__.py
│   └── examples.py         # 6 comprehensive examples
│
├── tests/
│   ├── __init__.py
│   ├── test_quick.py      # Quick verification tests
│   └── test_context_manager.py  # Context manager tests
│
├── setup.py               # Package installation
├── requirements.txt       # Dependencies
├── INSTALL.md            # Installation guide
├── README.md             # Complete documentation
├── ARCHITECTURE.md       # Technical architecture
├── VISUAL_GUIDE.md      # Quick visual reference
└── PROJECT_SUMMARY.md   # Project overview
```

---

## Key Features

✅ **Thread-Safe Operations** - Deadlock-free with reentrant locks  
✅ **Multiple Database Support** - SQLite, PostgreSQL, MySQL  
✅ **Singleton Pool Manager** - Centralized control  
✅ **Context Manager Protocol** - Automatic resource cleanup  
✅ **Background Maintenance** - Automatic idle connection cleanup  
✅ **Comprehensive Statistics** - Real-time monitoring  
✅ **Production Ready** - Full error handling and logging  

---

## Import Patterns

### Import from main module (Recommended)

```python
from db_management import (
    get_pool_manager,
    SQLitePoolConfig,
    PostgreSQLPoolConfig,
    MySQLPoolConfig
)
```

### Import specific components

```python
from db_management.pool_manager import PoolManager
from db_management.pool_config import SQLitePoolConfig
from db_management.connection_pool_factory import SQLiteConnectionPool
```

### Import everything

```python
import db_management

manager = db_management.get_pool_manager()
config = db_management.SQLitePoolConfig(...)
```

---

## Running Tests

```bash
# Quick verification tests
python -m db_management.tests.test_quick

# Context manager tests  
python -m db_management.tests.test_context_manager

# Or with pytest
cd db_management
pytest tests/ -v
```

---

## Running Examples

```bash
# Run all 6 examples
python -m db_management.examples.examples

# Or directly
cd examples
python examples.py
```

**Examples included:**
1. SQLite file-based database
2. SQLite in-memory with multi-threading
3. PostgreSQL with transactions
4. MySQL with batch operations
5. Multi-pool management
6. Stress test (50 threads, 1000 operations)

---

## Configuration Examples

### SQLite (File-based)

```python
from db_management import SQLitePoolConfig

config = SQLitePoolConfig(
    pool_name="app_db",
    database_path="application.db",
    min_connections=2,
    max_connections=10,
    connection_timeout=30.0
)
```

### PostgreSQL

```python
from db_management import PostgreSQLPoolConfig

config = PostgreSQLPoolConfig(
    pool_name="postgres_db",
    host="localhost",
    port=5432,
    database="mydb",
    user="postgres",
    password="secret",
    min_connections=5,
    max_connections=20
)
```

### MySQL

```python
from db_management import MySQLPoolConfig

config = MySQLPoolConfig(
    pool_name="mysql_db",
    host="localhost",
    port=3306,
    database="mydb",
    user="root",
    password="secret",
    min_connections=5,
    max_connections=20
)
```

---

## API Quick Reference

### Pool Manager Methods

```python
manager = get_pool_manager()

# Pool management
manager.create_pool(config)
manager.pool_exists(pool_name) → bool
manager.get_all_pool_names() → list
manager.remove_pool(pool_name, force=False)
manager.shutdown_all()

# Connection operations
conn = manager.get_connection_from_pool(pool_name, timeout=None)
manager.close_connection(conn, pool_name)

# Context managers
with conn as connection:  # PooledConnection context manager
    # Use connection
    pass

with manager.get_connection_context(pool_name) as connection:
    # Use connection
    pass

# Monitoring
stats = manager.get_pool_stats(pool_name)
all_stats = manager.get_all_stats()
```

---

## Documentation

| Document | Description |
|----------|-------------|
| **README.md** | Complete user guide with API reference (800+ lines) |
| **INSTALL.md** | Installation guide with troubleshooting |
| **ARCHITECTURE.md** | Technical architecture and design patterns |
| **VISUAL_GUIDE.md** | Visual diagrams and quick reference |
| **PROJECT_SUMMARY.md** | Project overview and file descriptions |

---

## Common Use Cases

### Web Application

```python
from db_management import get_pool_manager, PostgreSQLPoolConfig

# Initialize at startup
manager = get_pool_manager()
config = PostgreSQLPoolConfig(
    pool_name="webapp",
    host="localhost",
    database="mydb",
    min_connections=5,
    max_connections=20
)
manager.create_pool(config)

# Use in request handlers
def get_user(user_id):
    manager = get_pool_manager()
    with manager.get_connection_context("webapp") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()
```

### Multi-Database Application

```python
from db_management import get_pool_manager, SQLitePoolConfig, PostgreSQLPoolConfig

manager = get_pool_manager()

# Create multiple pools
manager.create_pool(SQLitePoolConfig(pool_name="cache", ...))
manager.create_pool(PostgreSQLPoolConfig(pool_name="primary", ...))

# Use different databases
with manager.get_connection_context("cache") as conn:
    # Fast cache operations
    pass

with manager.get_connection_context("primary") as conn:
    # Main database operations
    pass
```

---

## Design Patterns

- **Singleton Pattern** - Single pool manager instance
- **Object Pool Pattern** - Connection pooling and reuse
- **Factory Pattern** - Database-specific pool creation
- **Strategy Pattern** - Abstract database implementations
- **Context Manager Protocol** - Automatic cleanup

---

## Thread Safety

✅ Reentrant locks (RLock) for complex operations  
✅ Thread-safe Queue for connection storage  
✅ Atomic operations for critical sections  
✅ Deadlock prevention through lock hierarchy  
✅ Event-based coordination for cleanup thread  

---

## Performance

- **~1000 operations/second** on standard hardware (SQLite, 10 threads)
- **Linear scaling** up to pool saturation
- **O(1) connection acquisition** (average case)
- **Automatic connection validation** before reuse
- **Background cleanup** doesn't block operations

---

## Requirements

- **Python** ≥ 3.7
- **typing-extensions** ≥ 4.0.0 (always required)
- **psycopg2-binary** ≥ 2.9.0 (for PostgreSQL)
- **mysql-connector-python** ≥ 8.0.0 (for MySQL)

---

## License

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha** - ajsinha@gmail.com

This software and documentation are proprietary and confidential. Unauthorized copying, distribution, modification, or use is strictly prohibited without explicit written permission.

**Patent Pending**: Certain architectural patterns may be subject to patent applications.

---

## Support

For questions, issues, or licensing inquiries:
**Ashutosh Sinha** - ajsinha@gmail.com

---

## Version

**Current Version:** 1.0.0  
**Release Date:** November 2025

