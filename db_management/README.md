# Database Connection Pool Manager

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

## Legal Notice

This document and the associated software architecture are proprietary and confidential. Unauthorized copying, distribution, modification, or use of this document or the software system it describes is strictly prohibited without explicit written permission from the copyright holder. This document is provided "as is" without warranty of any kind, either expressed or implied. The copyright holder shall not be liable for any damages arising from the use of this document or the software system it describes.

**Patent Pending:** Certain architectural patterns and implementations described in this document may be subject to patent applications.

---

## Overview

A high-performance, thread-safe database connection pool manager supporting multiple database types with enterprise-grade features including automatic connection recycling, configurable pool sizing, and deadlock-free operations.

### Key Features

- **Singleton Pool Manager**: Centralized management of multiple connection pools
- **Thread-Safe Operations**: Reentrant locks with deadlock prevention
- **Multiple Database Support**: SQLite (file & in-memory), PostgreSQL, MySQL
- **Automatic Connection Management**: Connections automatically return to pool
- **Background Maintenance**: Thread monitors and cleans up idle connections
- **Context Manager Support**: Pythonic `with` statement for automatic cleanup
- **Configurable Pooling**: Min/max connections, idle timeouts, validation intervals
- **Production Ready**: Comprehensive logging, error handling, and statistics

### Design Patterns Used

1. **Singleton Pattern**: Ensures single PoolManager instance across application
2. **Object Pool Pattern**: Efficient connection reuse and lifecycle management
3. **Factory Pattern**: Database-specific pool creation
4. **Strategy Pattern**: Abstract base classes for different database implementations
5. **Context Manager Protocol**: Automatic resource management

## Architecture

### Component Hierarchy

```
PoolManager (Singleton)
├── Multiple ConnectionPools (by name)
│   ├── SQLiteConnectionPool
│   ├── PostgreSQLConnectionPool
│   └── MySQLConnectionPool
│       ├── Connection Queue (thread-safe)
│       ├── Active Connections Tracking
│       └── Cleanup Thread
```

### Thread Safety Mechanisms

1. **Reentrant Locks (RLock)**: Allow same thread to acquire lock multiple times
2. **Queue-based Connection Storage**: Thread-safe FIFO queue for available connections
3. **Consistent Lock Ordering**: Prevents deadlocks through predictable lock acquisition
4. **Atomic Operations**: Critical sections protected by locks
5. **Event-driven Cleanup**: Background thread uses threading.Event for clean shutdown

## Installation

### Required Dependencies

```bash
# Core (always required)
pip install --break-system-packages typing-extensions

# For SQLite (built-in with Python)
# No additional dependencies needed

# For PostgreSQL
pip install --break-system-packages psycopg2-binary
# OR
pip install --break-system-packages psycopg  # psycopg3

# For MySQL
pip install --break-system-packages mysql-connector-python
# OR
pip install --break-system-packages pymysql
```

### Project Structure

```
project/
├── pool_config.py          # Configuration classes
├── abstract_pool.py        # Abstract base classes
├── connection_pools.py     # Concrete implementations
├── pool_manager.py         # Singleton manager
├── examples.py             # Usage examples
└── README.md              # This file
```

## Quick Start

### Basic Usage

```python
from pool_manager import get_pool_manager
from pool_config import SQLitePoolConfig

# Get singleton instance
manager = get_pool_manager()

# Create a pool
config = SQLitePoolConfig(
    pool_name="my_database",
    database_path="app.db",
    min_connections=2,
    max_connections=10
)
manager.create_pool(config)

# Method 1: Use PooledConnection as context manager (recommended)
conn = manager.get_connection_from_pool("my_database")
with conn as connection:
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
# Connection automatically returned to pool

# Method 2: Use pool's context manager (also recommended)
with manager.get_connection_context("my_database") as connection:
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
# Connection automatically returned to pool

# Method 3: Manual connection handling (not recommended)
conn = manager.get_connection_from_pool("my_database")
try:
    # Use connection
    cursor = conn.connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
finally:
    manager.close_connection(conn, "my_database")
```

## Configuration

### Pool Configuration Parameters

All pool configurations support these base parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pool_name` | str | required | Unique identifier for the pool |
| `min_connections` | int | 2 | Minimum connections to maintain |
| `max_connections` | int | 10 | Maximum connections allowed |
| `max_idle_connections` | int | 5 | Max idle before cleanup |
| `connection_timeout` | float | 30.0 | Timeout for acquiring connection (seconds) |
| `idle_timeout` | float | 300.0 | Time before idle connection closes (seconds) |
| `validation_interval` | float | 60.0 | Interval for connection validation (seconds) |

### Database-Specific Configurations

#### SQLite Configuration

```python
from pool_config import SQLitePoolConfig

config = SQLitePoolConfig(
    pool_name="sqlite_pool",
    database_path="app.db",  # Use ":memory:" for in-memory
    check_same_thread=False,  # Allow multi-thread access
    timeout=5.0,
    isolation_level=None,  # Autocommit mode
    min_connections=2,
    max_connections=10
)
```

#### PostgreSQL Configuration

```python
from pool_config import PostgreSQLPoolConfig

config = PostgreSQLPoolConfig(
    pool_name="postgres_pool",
    host="localhost",
    port=5432,
    database="mydb",
    user="postgres",
    password="secret",
    sslmode="prefer",
    connect_timeout=10,
    min_connections=3,
    max_connections=15
)
```

#### MySQL Configuration

```python
from pool_config import MySQLPoolConfig

config = MySQLPoolConfig(
    pool_name="mysql_pool",
    host="localhost",
    port=3306,
    database="mydb",
    user="root",
    password="secret",
    charset="utf8mb4",
    connect_timeout=10,
    autocommit=False,
    min_connections=3,
    max_connections=15
)
```

## API Reference

### PoolManager

#### Class Methods

##### `get_instance() -> PoolManager`
Get the singleton instance of PoolManager.

```python
manager = PoolManager.get_instance()
# Or use the convenience function
manager = get_pool_manager()
```

#### Instance Methods

##### `create_pool(config: PoolConfiguration) -> None`
Create a new connection pool.

```python
manager.create_pool(config)
```

**Raises:**
- `ValueError`: If pool with same name already exists

##### `get_connection_from_pool(pool_name: str, timeout: float = None) -> PooledConnection`
Get a connection from the specified pool.

```python
conn = manager.get_connection_from_pool("my_pool", timeout=30.0)

# The returned PooledConnection supports context manager protocol:
with conn as connection:
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM table")
# Connection automatically returned to pool on exit
```

**Parameters:**
- `pool_name`: Name of the pool
- `timeout`: Max wait time (uses pool default if None)

**Returns:** PooledConnection object (supports context manager protocol)

**Raises:**
- `KeyError`: If pool doesn't exist
- `TimeoutError`: If no connection available within timeout

**Note:** The returned `PooledConnection` object implements `__enter__` and `__exit__` methods,
so it can be used directly with the `with` statement. This automatically returns the connection
to the pool when the context exits.

##### `close_connection(connection: PooledConnection, pool_name: str) -> None`
Return a connection to the pool.

```python
manager.close_connection(conn, "my_pool")
```

**Parameters:**
- `connection`: The pooled connection to return
- `pool_name`: Name of the pool

##### `get_connection_context(pool_name: str, timeout: float = None)`
Get a context manager for automatic connection handling.

```python
with manager.get_connection_context("my_pool") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM table")
```

##### `get_pool_stats(pool_name: str) -> dict`
Get statistics for a specific pool.

```python
stats = manager.get_pool_stats("my_pool")
# Returns: {
#     'pool_name': 'my_pool',
#     'total_connections': 5,
#     'active_connections': 2,
#     'available_connections': 3,
#     'max_connections': 10,
#     'min_connections': 2
# }
```

##### `get_all_stats() -> Dict[str, dict]`
Get statistics for all pools.

```python
all_stats = manager.get_all_stats()
```

##### `remove_pool(pool_name: str, force: bool = False) -> None`
Remove and shutdown a connection pool.

```python
manager.remove_pool("my_pool", force=True)
```

**Parameters:**
- `pool_name`: Name of the pool to remove
- `force`: If True, force removal even with active connections

##### `shutdown_all() -> None`
Shutdown all connection pools (automatically called on exit).

```python
manager.shutdown_all()
```

### AbstractConnectionPool

#### Methods

##### `get_connection(timeout: float = None) -> PooledConnection`
Get a connection from the pool.

##### `close_connection(pooled_conn: PooledConnection) -> None`
Return a connection to the pool.

##### `get_connection_context(timeout: float = None)`
Context manager for automatic connection handling.

##### `get_stats() -> dict`
Get pool statistics.

##### `shutdown() -> None`
Shutdown the pool.

## Usage Examples

### Example 1: SQLite File-Based Database

```python
from pool_manager import get_pool_manager
from pool_config import SQLitePoolConfig

manager = get_pool_manager()

# Create pool
config = SQLitePoolConfig(
    pool_name="app_db",
    database_path="application.db",
    min_connections=2,
    max_connections=10
)
manager.create_pool(config)

# Create table
with manager.get_connection_context("app_db") as conn:
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE
        )
    """)
    conn.commit()

# Insert data
with manager.get_connection_context("app_db") as conn:
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        ("John Doe", "john@example.com")
    )
    conn.commit()

# Query data
with manager.get_connection_context("app_db") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    for row in cursor.fetchall():
        print(dict(row))
```

### Example 2: In-Memory SQLite with Multi-Threading

```python
from concurrent.futures import ThreadPoolExecutor
from pool_manager import get_pool_manager
from pool_config import SQLitePoolConfig

manager = get_pool_manager()

# Create in-memory pool
config = SQLitePoolConfig(
    pool_name="cache",
    database_path=":memory:",
    min_connections=5,
    max_connections=20
)
manager.create_pool(config)

# Initialize schema
with manager.get_connection_context("cache") as conn:
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE cache_data (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()

# Concurrent operations
def insert_data(thread_id, count):
    for i in range(count):
        with manager.get_connection_context("cache") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO cache_data VALUES (?, ?)",
                (f"key-{thread_id}-{i}", f"value-{i}")
            )
            conn.commit()

# Run 10 threads, 100 operations each
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [
        executor.submit(insert_data, thread_id, 100)
        for thread_id in range(10)
    ]
    for future in futures:
        future.result()

# Check results
with manager.get_connection_context("cache") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM cache_data")
    count = cursor.fetchone()[0]
    print(f"Total cached items: {count}")
```

### Example 3: PostgreSQL with Transactions

```python
from pool_manager import get_pool_manager
from pool_config import PostgreSQLPoolConfig

manager = get_pool_manager()

config = PostgreSQLPoolConfig(
    pool_name="orders_db",
    host="localhost",
    database="ecommerce",
    user="app_user",
    password="secret",
    min_connections=3,
    max_connections=15
)
manager.create_pool(config)

# Transaction example
with manager.get_connection_context("orders_db") as conn:
    cursor = conn.cursor()
    try:
        # Begin transaction
        cursor.execute("""
            INSERT INTO orders (customer_id, total) 
            VALUES (%s, %s) RETURNING id
        """, (123, 99.99))
        order_id = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO order_items (order_id, product_id, quantity)
            VALUES (%s, %s, %s)
        """, (order_id, 456, 2))
        
        # Commit transaction
        conn.commit()
        print(f"Order {order_id} created successfully")
        
    except Exception as e:
        # Rollback on error
        conn.rollback()
        print(f"Transaction failed: {e}")
```

### Example 4: MySQL with Connection Pool

```python
from pool_manager import get_pool_manager
from pool_config import MySQLPoolConfig

manager = get_pool_manager()

config = MySQLPoolConfig(
    pool_name="analytics_db",
    host="localhost",
    database="analytics",
    user="analyst",
    password="secret",
    min_connections=2,
    max_connections=10
)
manager.create_pool(config)

# Batch insert
employees = [
    ("John", "Doe", "Engineering", 95000),
    ("Jane", "Smith", "Marketing", 85000),
    ("Mike", "Johnson", "Sales", 75000)
]

with manager.get_connection_context("analytics_db") as conn:
    cursor = conn.cursor()
    cursor.executemany(
        """INSERT INTO employees 
           (first_name, last_name, department, salary) 
           VALUES (%s, %s, %s, %s)""",
        employees
    )
    conn.commit()
    print(f"Inserted {cursor.rowcount} employees")
```

### Example 5: Multi-Pool Management

```python
from pool_manager import get_pool_manager
from pool_config import SQLitePoolConfig

manager = get_pool_manager()

# Create multiple pools
pools = {
    "cache": SQLitePoolConfig(
        pool_name="cache",
        database_path=":memory:",
        max_connections=10
    ),
    "user_db": SQLitePoolConfig(
        pool_name="user_db",
        database_path="users.db",
        max_connections=20
    ),
    "logs_db": SQLitePoolConfig(
        pool_name="logs_db",
        database_path="logs.db",
        max_connections=5
    )
}

for config in pools.values():
    manager.create_pool(config)

# Use different pools
with manager.get_connection_context("cache") as conn:
    # Cache operations
    pass

with manager.get_connection_context("user_db") as conn:
    # User database operations
    pass

# Get statistics for all pools
all_stats = manager.get_all_stats()
for pool_name, stats in all_stats.items():
    print(f"{pool_name}: {stats['active_connections']}/{stats['max_connections']} active")
```

## Performance Considerations

### Connection Pool Sizing

**Min Connections:**
- Start with 2-5 for low-traffic applications
- Increase for applications with baseline load
- Consider database resource constraints

**Max Connections:**
- Calculate based on: `max_connections = (available_DB_connections * 0.8) / num_app_instances`
- Leave headroom for administrative connections
- Monitor and adjust based on actual usage

### Idle Connection Management

The background cleanup thread:
- Runs every `validation_interval` seconds (default: 60s)
- Closes connections exceeding `max_idle_connections`
- Maintains at least `min_connections`
- Validates connection health

### Thread Safety

All operations are thread-safe through:
1. Reentrant locks (RLock) for synchronized access
2. Thread-safe Queue for connection storage
3. Atomic operations for state changes
4. No shared mutable state without protection

### Best Practices

1. **Use Context Managers**: Always prefer `get_connection_context()` over manual handling
2. **Configure Timeouts**: Set appropriate `connection_timeout` for your use case
3. **Monitor Statistics**: Regularly check pool stats to optimize configuration
4. **Handle Exceptions**: Wrap database operations in try-except blocks
5. **Close Connections**: Always return connections to pool (automatic with context managers)
6. **Tune Pool Size**: Start conservative, scale based on monitoring
7. **Test Under Load**: Verify pool behavior under expected peak load

## Monitoring and Debugging

### Enable Debug Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Monitor Pool Health

```python
import time
from pool_manager import get_pool_manager

manager = get_pool_manager()

while True:
    stats = manager.get_all_stats()
    for pool_name, pool_stats in stats.items():
        utilization = (pool_stats['active_connections'] / 
                      pool_stats['max_connections'] * 100)
        print(f"{pool_name}: {utilization:.1f}% utilized")
    time.sleep(60)
```

### Common Issues and Solutions

**Issue: TimeoutError when acquiring connection**
- Solution: Increase `max_connections` or decrease `connection_timeout`
- Check for connection leaks (not returning connections)

**Issue: Too many idle connections**
- Solution: Decrease `max_idle_connections` or increase `validation_interval`

**Issue: Connection validation failures**
- Solution: Check database server health
- Verify network connectivity
- Review `idle_timeout` setting

## Testing

### Unit Test Example

```python
import unittest
from pool_manager import PoolManager
from pool_config import SQLitePoolConfig

class TestConnectionPool(unittest.TestCase):
    def setUp(self):
        self.manager = PoolManager.get_instance()
        config = SQLitePoolConfig(
            pool_name="test_pool",
            database_path=":memory:",
            min_connections=1,
            max_connections=5
        )
        self.manager.create_pool(config)
    
    def tearDown(self):
        self.manager.remove_pool("test_pool", force=True)
    
    def test_get_connection(self):
        conn = self.manager.get_connection_from_pool("test_pool")
        self.assertIsNotNone(conn)
        self.manager.close_connection(conn, "test_pool")
    
    def test_context_manager(self):
        with self.manager.get_connection_context("test_pool") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()[0]
            self.assertEqual(result, 1)

if __name__ == '__main__':
    unittest.main()
```

## License and Copyright

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

This software and documentation are proprietary and confidential. See the Legal Notice section at the top of this document for full terms.

**Patent Pending:** Certain architectural patterns and implementations may be subject to patent applications.

## Support and Contact

For questions, issues, or licensing inquiries, please contact:

**Ashutosh Sinha**  
Email: ajsinha@gmail.com

---

**End of Documentation**
