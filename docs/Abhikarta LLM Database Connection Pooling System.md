# Abhikarta LLM Database Connection Pooling System
## Comprehensive Technical Documentation

---

**Version:** 1.0  
**Date:** November 7, 2025  
**Status:** Confidential - Internal Use Only

---

## Copyright and Legal Notice

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email:** ajsinha@gmail.com  
**GitHub:** https://www.github.com/ajsinha/abhikarta

### Legal Notice

This document and the associated software architecture are proprietary and confidential. Unauthorized copying, distribution, modification, or use of this document or the software system it describes is strictly prohibited without explicit written permission from the copyright holder.

This document is provided "as is" without warranty of any kind, either expressed or implied. The copyright holder shall not be liable for any damages arising from the use of this document or the software system it describes.

**Patent Pending:** Certain architectural patterns and implementations described in this document may be subject to patent applications.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Core Components](#core-components)
   - 3.1 [Simple Database Layer](#simple-database-layer)
   - 3.2 [Database Connection Pool](#database-connection-pool)
   - 3.3 [Connection Pool Manager](#connection-pool-manager)
4. [Technical Architecture](#technical-architecture)
5. [Configuration](#configuration)
6. [Usage Examples](#usage-examples)
7. [Advanced Features](#advanced-features)
8. [Monitoring and Statistics](#monitoring-and-statistics)
9. [Performance Optimization](#performance-optimization)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)
12. [Appendix](#appendix)

---

## 1. Executive Summary

The **Abhikarta Database Connection Pooling System** is an enterprise-grade database management solution designed specifically for LLM applications that require high-performance, scalable, and reliable database connectivity across multiple database systems.

### Key Features

- **Multi-Database Support**: PostgreSQL, MySQL, SQLite, SQL Server, and Oracle
- **Enterprise-Grade Pooling**: Apache DBCP-inspired connection pool with advanced features
- **Automatic Pool Management**: Singleton manager with automatic pool creation and cleanup
- **Connection Lifecycle Management**: Comprehensive validation, eviction, and health checking
- **Thread-Safe Operations**: Full concurrent access support with proper locking
- **Abandoned Connection Detection**: Automatic reclamation of leaked connections
- **Comprehensive Monitoring**: Detailed statistics and health checks
- **Zero-Downtime Operations**: Graceful connection rotation and pool maintenance

### Design Philosophy

The system follows three core principles:

1. **Simplicity**: Easy-to-use API with sensible defaults
2. **Reliability**: Robust error handling and automatic recovery
3. **Performance**: Optimized for high-throughput, low-latency operations

---

## 2. Architecture Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ABHIKARTA LLM APPLICATION                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ Database Operations
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              DATABASE CONNECTION POOL MANAGER                    │
│                    (Singleton Instance)                          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Pool Registry                                         │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │    │
│  │  │ Pool A   │  │ Pool B   │  │ Pool C   │   ...      │    │
│  │  │ (PG)     │  │ (MySQL)  │  │ (SQLite) │            │    │
│  │  └──────────┘  └──────────┘  └──────────┘            │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Management Features                                   │    │
│  │  • Pool Creation & Reuse                              │    │
│  │  • Automatic Cleanup                                  │    │
│  │  • Health Monitoring                                  │    │
│  │  • Statistics Collection                              │    │
│  └────────────────────────────────────────────────────────┘    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ Manages
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              DATABASE CONNECTION POOL                            │
│                (Per Database Configuration)                      │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  Connection Queue Management                         │      │
│  │  ┌─────────────────────────────────────────────┐     │      │
│  │  │  IDLE CONNECTIONS (Queue)                   │     │      │
│  │  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐   │     │      │
│  │  │  │ C1   │  │ C2   │  │ C3   │  │ C4   │ … │     │      │
│  │  │  └──────┘  └──────┘  └──────┘  └──────┘   │     │      │
│  │  └─────────────────────────────────────────────┘     │      │
│  │                                                       │      │
│  │  ┌─────────────────────────────────────────────┐     │      │
│  │  │  ACTIVE CONNECTIONS (Map)                   │     │      │
│  │  │  Thread1 → C5                               │     │      │
│  │  │  Thread2 → C6                               │     │      │
│  │  │  Thread3 → C7                               │     │      │
│  │  └─────────────────────────────────────────────┘     │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  Pool Features                                       │      │
│  │  • Connection Validation (test-on-borrow)           │      │
│  │  • Automatic Eviction (idle/expired)                │      │
│  │  • Abandoned Detection                              │      │
│  │  • Min/Max Pool Sizing                              │      │
│  │  • Wait Timeout & Blocking                          │      │
│  └──────────────────────────────────────────────────────┘      │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ Database Connections
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DATABASE SYSTEMS                               │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │PostgreSQL│  │  MySQL   │  │  SQLite  │  │SQL Server│  ...  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Interaction Flow

```
┌──────────────┐
│ Application  │
└──────┬───────┘
       │
       │ 1. Request Connection
       │
       ▼
┌─────────────────────────────┐
│  Pool Manager               │
│  • Check for existing pool  │
│  • Create if needed         │
│  • Return pool reference    │
└──────┬──────────────────────┘
       │
       │ 2. Get Pool
       │
       ▼
┌─────────────────────────────┐
│  Connection Pool            │
│  • Check idle queue         │
│  • Validate connection      │
│  • Create new if needed     │
│  • Mark as active           │
└──────┬──────────────────────┘
       │
       │ 3. Borrow Connection
       │
       ▼
┌─────────────────────────────┐
│  Application                │
│  • Execute queries          │
│  • Process results          │
└──────┬──────────────────────┘
       │
       │ 4. Return Connection
       │
       ▼
┌─────────────────────────────┐
│  Connection Pool            │
│  • Test if needed           │
│  • Return to idle queue     │
│  • Or destroy if invalid    │
└──────┬──────────────────────┘
       │
       │ 5. Background Maintenance
       │
       ▼
┌─────────────────────────────┐
│  Eviction Thread            │
│  • Test idle connections    │
│  • Remove expired           │
│  • Reclaim abandoned        │
│  • Maintain min idle        │
└─────────────────────────────┘
```

---

## 3. Core Components

### 3.1 Simple Database Layer

The simple database layer provides a lightweight abstraction for basic database operations without dependencies on ORMs like SQLAlchemy.

#### Purpose

- **Simplicity**: No heavy ORM dependencies
- **Portability**: Easy SQLite and PostgreSQL support
- **Performance**: Direct connection management
- **Testing**: Simple in-memory database for tests

#### Basic Database Class

```python
class Database:
    """Simple database abstraction layer"""
    
    def __init__(self, db_type: str = 'sqlite', **kwargs):
        """
        Initialize database connection.
        
        Args:
            db_type: 'sqlite' or 'postgresql'
            **kwargs: Database-specific connection parameters
        """
        
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        
    def execute(self, query: str, params: Tuple = ()) -> None:
        """Execute a query"""
        
    def fetchone(self, query: str, params: Tuple = ()) -> Optional[Dict]:
        """Fetch one row"""
        
    def fetchall(self, query: str, params: Tuple = ()) -> List[Dict]:
        """Fetch all rows"""
        
    def insert(self, table: str, data: Dict) -> int:
        """Insert a row and return last row id"""
        
    def update(self, table: str, data: Dict, where: str, where_params: Tuple) -> int:
        """Update rows"""
        
    def delete(self, table: str, where: str, where_params: Tuple) -> int:
        """Delete rows"""
```

#### Usage Example

```python
# SQLite
db = Database(db_type='sqlite', db_path='data/app.db')

# PostgreSQL
db = Database(
    db_type='postgresql',
    host='localhost',
    port=5432,
    database='mydb',
    user='postgres',
    password='secret'
)

# Use with context manager
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE active = ?", (True,))
    users = cursor.fetchall()

# Or use convenience methods
db.insert('users', {
    'name': 'John Doe',
    'email': 'john@example.com',
    'active': True
})

users = db.fetchall("SELECT * FROM users WHERE active = ?", (True,))
```

---

### 3.2 Database Connection Pool

The connection pool manages a pool of database connections for a specific database configuration, providing enterprise-grade features similar to Apache DBCP.

#### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              DATABASE CONNECTION POOL                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  CONNECTION STORAGE                                              │
│                                                                  │
│  Idle Connections Queue (max_total capacity)                    │
│  ┌─────────────────────────────────────────────────────┐        │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐         │        │
│  │  │ Wrapper1 │→ │ Wrapper2 │→ │ Wrapper3 │  ...    │        │
│  │  │ (IDLE)   │  │ (IDLE)   │  │ (IDLE)   │         │        │
│  │  └──────────┘  └──────────┘  └──────────┘         │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                  │
│  Active Connections Map (thread_id → wrapper)                   │
│  ┌─────────────────────────────────────────────────────┐        │
│  │  Thread-123 → Wrapper4 (IN_USE)                     │        │
│  │  Thread-456 → Wrapper5 (IN_USE)                     │        │
│  │  Thread-789 → Wrapper6 (IN_USE)                     │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                  │
│  All Connections Registry (connection_id → wrapper)             │
│  ┌─────────────────────────────────────────────────────┐        │
│  │  All wrappers indexed by ID for tracking            │        │
│  └─────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  CONNECTION WRAPPER                                              │
│                                                                  │
│  ┌─────────────────────────────────────────────────────┐        │
│  │  • Raw database connection                          │        │
│  │  • Metadata (ID, state, timestamps)                 │        │
│  │  • Usage statistics (use_count, error_count)        │        │
│  │  • Transaction state                                │        │
│  │  • Borrowing thread reference                       │        │
│  └─────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  BACKGROUND THREADS                                              │
│                                                                  │
│  Eviction Thread                                                │
│  ┌─────────────────────────────────────────────────────┐        │
│  │  Runs every N seconds:                              │        │
│  │  1. Test idle connections                           │        │
│  │  2. Remove expired connections                      │        │
│  │  3. Remove connections idle too long                │        │
│  │  4. Detect abandoned connections                    │        │
│  │  5. Ensure minimum idle count                       │        │
│  └─────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  SYNCHRONIZATION                                                 │
│                                                                  │
│  • RLock for pool state                                         │
│  • Semaphore for connection count                               │
│  • Queue for FIFO/LIFO ordering                                 │
│  • WeakValueDictionary for tracking                             │
└─────────────────────────────────────────────────────────────────┘
```

#### Key Classes

##### ConnectionWrapper

```python
@dataclass
class ConnectionWrapper:
    """Wrapper for database connections with metadata."""
    connection: Any                          # Raw DB connection
    connection_id: str                       # Unique identifier
    state: ConnectionState                   # Current state
    created_time: datetime                   # Creation timestamp
    last_used_time: datetime                 # Last usage timestamp
    last_tested_time: datetime               # Last validation
    use_count: int = 0                      # Times borrowed
    error_count: int = 0                    # Error occurrences
    in_transaction: bool = False            # Transaction state
    test_query: str = "SELECT 1"           # Validation query
    borrowed_by: Optional[threading.Thread] # Owner thread
```

##### PoolConfig

```python
@dataclass
class PoolConfig:
    """Configuration for the connection pool."""
    
    # Basic settings
    min_idle: int = 2                 # Minimum idle connections
    max_idle: int = 8                 # Maximum idle connections
    max_total: int = 20               # Maximum total connections
    
    # Connection validation
    test_on_borrow: bool = True       # Test before borrowing
    test_on_return: bool = False      # Test on return
    test_while_idle: bool = True      # Test idle connections
    validation_query: Optional[str]   # Custom validation query
    validation_timeout: int = 5       # Validation timeout
    
    # Eviction settings
    time_between_eviction_runs: int = 30      # Eviction interval
    min_evictable_idle_time: int = 300        # Min idle before eviction
    max_connection_lifetime: int = 3600       # Max connection age
    num_tests_per_eviction_run: int = 3       # Connections to test
    
    # Behavior settings
    block_when_exhausted: bool = True         # Block or fail
    max_wait_time: int = 30                   # Max wait time
    lifo: bool = True                         # LIFO vs FIFO
    
    # Monitoring
    abandoned_remove: bool = True             # Remove abandoned
    abandoned_timeout: int = 300              # Abandonment timeout
    log_abandoned: bool = True                # Log abandoned
```

##### DatabaseConnectionPool

```python
class DatabaseConnectionPool:
    """Enterprise-grade database connection pool."""
    
    def __init__(self, db_type: DatabaseType, config: PoolConfig, **connection_kwargs):
        """
        Initialize the connection pool.
        
        Args:
            db_type: Type of database (PostgreSQL, MySQL, etc.)
            config: Pool configuration
            **connection_kwargs: Database-specific connection parameters
        """
        
    @contextmanager
    def get_connection(self, timeout: Optional[float] = None):
        """
        Get a connection from the pool (context manager).
        
        Args:
            timeout: Maximum wait time for connection
            
        Yields:
            Database connection object
        """
        
    def borrow_connection(self, timeout: Optional[float] = None) -> ConnectionWrapper:
        """Borrow a connection from the pool."""
        
    def return_connection(self, wrapper: ConnectionWrapper):
        """Return a connection to the pool."""
        
    def get_pool_status(self) -> Dict[str, Any]:
        """Get current pool status and statistics."""
        
    def close(self):
        """Close the pool and all connections."""
```

#### Connection Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                   CONNECTION LIFECYCLE                           │
└─────────────────────────────────────────────────────────────────┘

                  ┌──────────────┐
                  │   CREATED    │
                  └──────┬───────┘
                         │
                         │ Initialize
                         │
                         ▼
                  ┌──────────────┐
           ┌─────►│     IDLE     │◄─────┐
           │      └──────┬───────┘      │
           │             │              │
           │             │ Borrow       │ Return
           │             │              │
           │             ▼              │
           │      ┌──────────────┐     │
           │      │   IN_USE     │─────┘
           │      └──────┬───────┘
           │             │
           │             │ Validate
           │             │
           │             ▼
           │      ┌──────────────┐
           │      │   TESTING    │
           │      └──────┬───────┘
           │             │
           │             ├─────► IDLE (if valid)
           │             │
           │             ├─────► INVALID (if test fails)
           │             │
           │             ▼
      Evict│      ┌──────────────┐
           │      │   INVALID    │
           │      └──────┬───────┘
           │             │
           │             │ Destroy
           │             │
           │             ▼
           └──────┌──────────────┐
                  │    CLOSED    │
                  └──────────────┘
                         │
                         │ Removed from pool
                         │
                         ▼
                  ┌──────────────┐
                  │   DESTROYED  │
                  └──────────────┘
```

#### Eviction Strategies

```
┌─────────────────────────────────────────────────────────────────┐
│                   EVICTION POLICIES                              │
└─────────────────────────────────────────────────────────────────┘

1. IDLE_TIME Policy
   ┌────────────────────────────────────────────────┐
   │  Evict connections idle longer than threshold  │
   │  • Check: (now - last_used) > min_evictable   │
   │  • Only if: idle_count > min_idle             │
   │  • Purpose: Free unused resources             │
   └────────────────────────────────────────────────┘

2. LIFETIME Policy
   ┌────────────────────────────────────────────────┐
   │  Evict connections older than max lifetime     │
   │  • Check: (now - created) > max_lifetime      │
   │  • Always evict: regardless of activity       │
   │  • Purpose: Prevent stale connections         │
   └────────────────────────────────────────────────┘

3. ERROR_COUNT Policy
   ┌────────────────────────────────────────────────┐
   │  Evict connections with too many errors        │
   │  • Check: error_count > threshold             │
   │  • Purpose: Remove problematic connections    │
   └────────────────────────────────────────────────┘

4. VALIDATION_FAILURE Policy
   ┌────────────────────────────────────────────────┐
   │  Evict connections that fail validation        │
   │  • Test: Execute validation query             │
   │  • Purpose: Remove broken connections         │
   └────────────────────────────────────────────────┘
```

---

### 3.3 Connection Pool Manager

The Connection Pool Manager is a singleton that manages multiple connection pools, automatically creating and reusing pools based on connection configurations.

#### Features

```
┌─────────────────────────────────────────────────────────────────┐
│              POOL MANAGER CAPABILITIES                           │
└─────────────────────────────────────────────────────────────────┘

1. Pool Creation & Reuse
   ┌────────────────────────────────────────────────┐
   │  • Hash-based pool identification              │
   │  • Automatic pool creation on first use        │
   │  • Reuse existing pools for same config       │
   │  • Named pools for specific use cases         │
   └────────────────────────────────────────────────┘

2. Lifecycle Management
   ┌────────────────────────────────────────────────┐
   │  • Automatic initialization                    │
   │  • Lazy pool creation                          │
   │  • Idle pool cleanup                           │
   │  • Graceful shutdown                           │
   └────────────────────────────────────────────────┘

3. Multi-Database Support
   ┌────────────────────────────────────────────────┐
   │  • PostgreSQL                                  │
   │  • MySQL                                       │
   │  • SQLite                                      │
   │  • SQL Server                                  │
   │  • Oracle                                      │
   └────────────────────────────────────────────────┘

4. Monitoring & Statistics
   ┌────────────────────────────────────────────────┐
   │  • Per-pool statistics                         │
   │  • Aggregate metrics                           │
   │  • Health checks                               │
   │  • Performance tracking                        │
   └────────────────────────────────────────────────┘
```

#### Class Structure

```python
class DBConnectionPoolManager:
    """Singleton manager for database connection pools."""
    
    # Singleton instance
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    
    def get_pool(self, connection_config: ConnectionConfig, 
                 pool_config: PoolConfig = None) -> DatabaseConnectionPool:
        """
        Get or create a connection pool.
        
        Args:
            connection_config: Database connection configuration
            pool_config: Optional pool configuration
            
        Returns:
            DatabaseConnectionPool instance
        """
        
    def get_pool_by_name(self, name: str, connection_config: ConnectionConfig) \
            -> DatabaseConnectionPool:
        """Get or create a named pool."""
        
    @contextmanager
    def get_connection(self, connection_config: ConnectionConfig, 
                       timeout: float = None):
        """Get a database connection (convenience method)."""
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get manager and aggregate pool statistics."""
        
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all pools."""
        
    def shutdown(self):
        """Shutdown the manager and close all pools."""
```

#### Pool Registry

```
┌─────────────────────────────────────────────────────────────────┐
│                      POOL REGISTRY                               │
└─────────────────────────────────────────────────────────────────┘

Pool Key (SHA-256 hash of config) → PoolInfo
┌─────────────────────────────────────────────────────────┐
│ e4d909c290... → PoolInfo                                │
│   ├─ pool: DatabaseConnectionPool                       │
│   ├─ config: ConnectionConfig (PostgreSQL:localhost)    │
│   ├─ created_time: 2025-11-07 10:00:00                 │
│   ├─ last_accessed_time: 2025-11-07 10:05:32           │
│   ├─ access_count: 1,247                               │
│   └─ reference_count: 3                                 │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 7e6cc5c8e1... → PoolInfo                                │
│   ├─ pool: DatabaseConnectionPool                       │
│   ├─ config: ConnectionConfig (MySQL:db.server.com)     │
│   ├─ created_time: 2025-11-07 09:30:15                 │
│   ├─ last_accessed_time: 2025-11-07 10:05:28           │
│   ├─ access_count: 892                                 │
│   └─ reference_count: 2                                 │
└─────────────────────────────────────────────────────────┘

Named Pools (custom names)
┌─────────────────────────────────────────────────────────┐
│ "analytics_db" → PoolInfo                               │
│   ├─ pool: DatabaseConnectionPool                       │
│   ├─ config: ConnectionConfig (PostgreSQL:analytics)    │
│   ├─ created_time: 2025-11-07 08:00:00                 │
│   └─ access_count: 5,421                               │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Technical Architecture

### 4.1 Thread Safety

The system implements multiple layers of thread safety:

```python
# Pool Manager Level
class DBConnectionPoolManager:
    _lock = threading.Lock()          # Class-level singleton lock
    _pool_lock = threading.RLock()    # Pool registry lock

# Connection Pool Level
class DatabaseConnectionPool:
    _lock = threading.RLock()         # Pool state lock
    _semaphore = threading.Semaphore()# Connection count semaphore
    _idle_connections = Queue()       # Thread-safe queue
```

#### Locking Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                    LOCKING HIERARCHY                             │
└─────────────────────────────────────────────────────────────────┘

Level 1: Singleton Creation
┌────────────────────────────────────────────────┐
│  DBConnectionPoolManager._lock                 │
│  • Protects singleton instance creation        │
│  • Held only during initialization             │
│  • Very short duration                         │
└────────────────────────────────────────────────┘
        │
        ▼
Level 2: Pool Registry
┌────────────────────────────────────────────────┐
│  DBConnectionPoolManager._pool_lock (RLock)    │
│  • Protects pool registry operations           │
│  • Allows reentrant calls                      │
│  • Held during pool lookup/creation            │
└────────────────────────────────────────────────┘
        │
        ▼
Level 3: Pool State
┌────────────────────────────────────────────────┐
│  DatabaseConnectionPool._lock (RLock)          │
│  • Protects pool state modifications           │
│  • Connection creation/destruction             │
│  • Statistics updates                          │
└────────────────────────────────────────────────┘
        │
        ▼
Level 4: Connection Queue
┌────────────────────────────────────────────────┐
│  Queue (thread-safe by design)                 │
│  • No explicit locking needed                  │
│  • Atomic operations                           │
└────────────────────────────────────────────────┘
```

### 4.2 Connection States

```python
class ConnectionState(Enum):
    IDLE = "idle"           # Available in pool
    IN_USE = "in_use"       # Borrowed by thread
    TESTING = "testing"     # Being validated
    INVALID = "invalid"     # Failed validation
    CLOSED = "closed"       # Destroyed
```

#### State Transitions

```
┌─────────────────────────────────────────────────────────────────┐
│              CONNECTION STATE MACHINE                            │
└─────────────────────────────────────────────────────────────────┘

   [Creation]
       │
       ▼
    (IDLE)───┐
       │     │
       │     │ test_on_borrow=True
       │     │
       │     ▼
       │  (TESTING)──┐
       │     │       │
       │     │       │ validation fails
       │     │       │
       │  [valid]    ▼
       │     │    (INVALID)──► [Destroyed]
       │     │
       │     ▼
       │  (IDLE)
       │
       │ borrow
       │
       ▼
   (IN_USE)
       │
       │ return
       │
       ▼
    (IDLE)
       │
       │ eviction / expiration
       │
       ▼
   (CLOSED)
       │
       ▼
  [Destroyed]
```

### 4.3 Memory Management

```
┌─────────────────────────────────────────────────────────────────┐
│                   MEMORY MANAGEMENT                              │
└─────────────────────────────────────────────────────────────────┘

1. Strong References (Prevent GC)
   ┌────────────────────────────────────────────────┐
   │  Manager._pools: Dict[str, PoolInfo]           │
   │  • Keeps pools alive                           │
   │  • Manually removed during cleanup             │
   └────────────────────────────────────────────────┘

2. Weak References (Allow GC)
   ┌────────────────────────────────────────────────┐
   │  Manager._pool_references: WeakValueDict       │
   │  • Tracks pool usage                           │
   │  • Automatic cleanup when pool destroyed       │
   └────────────────────────────────────────────────┘

3. Thread References
   ┌────────────────────────────────────────────────┐
   │  ConnectionWrapper.borrowed_by: Thread         │
   │  • Reference to borrowing thread               │
   │  • Used for abandoned detection                │
   │  • Cleared on return                           │
   └────────────────────────────────────────────────┘

4. Connection Cleanup
   ┌────────────────────────────────────────────────┐
   │  • Explicit close() on connections             │
   │  • Remove from all tracking dictionaries       │
   │  • Decrement total connection count            │
   │  • Update statistics                           │
   └────────────────────────────────────────────────┘
```

---

## 5. Configuration

### 5.1 Pool Configuration Options

```python
@dataclass
class PoolConfig:
    """Complete pool configuration reference."""
    
    # === POOL SIZING ===
    min_idle: int = 2
    # Minimum number of idle connections to maintain
    # Lower values: Less resource usage
    # Higher values: Better response time
    
    max_idle: int = 8
    # Maximum number of idle connections
    # Controls memory usage
    # Should be >= min_idle
    
    max_total: int = 20
    # Maximum total connections (idle + active)
    # Hard limit on concurrent connections
    # Should be >= max_idle
    
    # === VALIDATION ===
    test_on_borrow: bool = True
    # Test connection before giving to application
    # Ensures connection is valid
    # Adds latency but improves reliability
    
    test_on_return: bool = False
    # Test connection when returned
    # Usually not needed
    # Useful for debugging
    
    test_while_idle: bool = True
    # Test idle connections periodically
    # Prevents stale connections
    # Recommended for production
    
    validation_query: Optional[str] = None
    # Custom query for validation
    # Default: "SELECT 1" (PostgreSQL/MySQL)
    # Oracle: "SELECT 1 FROM DUAL"
    
    validation_timeout: int = 5
    # Timeout for validation query (seconds)
    # Should be short
    
    # === EVICTION ===
    time_between_eviction_runs: int = 30
    # Seconds between eviction thread runs
    # Lower: More responsive, more overhead
    # Higher: Less overhead, slower cleanup
    
    min_evictable_idle_time: int = 300
    # Minimum idle time before eviction (seconds)
    # Connections idle longer than this are candidates
    # 300 seconds = 5 minutes
    
    max_connection_lifetime: int = 3600
    # Maximum connection age (seconds)
    # Forces rotation of connections
    # 3600 seconds = 1 hour
    
    num_tests_per_eviction_run: int = 3
    # Number of connections to test per run
    # Spreads validation load over time
    # Higher: Faster detection, more overhead
    
    # === BLOCKING BEHAVIOR ===
    block_when_exhausted: bool = True
    # Wait for connection if pool exhausted
    # True: Block until available or timeout
    # False: Fail immediately
    
    max_wait_time: int = 30
    # Maximum wait time for connection (seconds)
    # Only used if block_when_exhausted=True
    
    lifo: bool = True
    # Last-In-First-Out connection order
    # True: Use most recently returned connection
    # False: Use oldest available (FIFO)
    # LIFO is usually better for cache locality
    
    # === ABANDONED CONNECTIONS ===
    abandoned_remove: bool = True
    # Detect and reclaim abandoned connections
    # Protects against connection leaks
    
    abandoned_timeout: int = 300
    # Timeout for abandoned connections (seconds)
    # Connection borrowed longer than this is abandoned
    # 300 seconds = 5 minutes
    
    log_abandoned: bool = True
    # Log abandoned connection details
    # Helps identify connection leaks
```

### 5.2 Connection Configuration

```python
@dataclass
class ConnectionConfig:
    """Database connection configuration."""
    
    db_type: DatabaseType
    # Required: Type of database
    # Options: POSTGRESQL, MYSQL, SQLITE, SQLSERVER, ORACLE
    
    # Connection parameters (database-specific)
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    
    # SSL/TLS
    ssl: bool = False
    ssl_ca: Optional[str] = None
    ssl_cert: Optional[str] = None
    ssl_key: Optional[str] = None
    
    # Additional parameters
    charset: Optional[str] = None
    autocommit: bool = False
    connection_timeout: int = 10
    socket_timeout: int = 0
    application_name: Optional[str] = None
```

### 5.3 Configuration Examples

#### Development Configuration

```python
# Development: Small pool, aggressive testing
dev_config = PoolConfig(
    min_idle=1,
    max_idle=3,
    max_total=5,
    test_on_borrow=True,
    test_while_idle=True,
    time_between_eviction_runs=10,
    min_evictable_idle_time=60,
    max_connection_lifetime=300,
    abandoned_remove=True,
    abandoned_timeout=60,
    log_abandoned=True
)
```

#### Production Configuration

```python
# Production: Balanced pool, moderate testing
prod_config = PoolConfig(
    min_idle=5,
    max_idle=20,
    max_total=50,
    test_on_borrow=True,
    test_while_idle=True,
    time_between_eviction_runs=60,
    min_evictable_idle_time=300,
    max_connection_lifetime=3600,
    abandoned_remove=True,
    abandoned_timeout=300,
    log_abandoned=True,
    max_wait_time=30
)
```

#### High-Traffic Configuration

```python
# High traffic: Large pool, minimal testing
high_traffic_config = PoolConfig(
    min_idle=10,
    max_idle=50,
    max_total=100,
    test_on_borrow=False,  # Skip for performance
    test_while_idle=True,
    time_between_eviction_runs=120,
    min_evictable_idle_time=600,
    max_connection_lifetime=7200,
    abandoned_remove=True,
    abandoned_timeout=600,
    max_wait_time=60
)
```

---

## 6. Usage Examples

### 6.1 Basic Usage

#### Simple Database Operations

```python
from abhikarta.database import Database

# Initialize database
db = Database(db_type='sqlite', db_path='data/app.db')

# Insert data
user_id = db.insert('users', {
    'name': 'Alice Smith',
    'email': 'alice@example.com',
    'created_at': datetime.now()
})

# Query data
users = db.fetchall(
    "SELECT * FROM users WHERE created_at > ?",
    (datetime.now() - timedelta(days=7),)
)

# Update data
db.update(
    'users',
    {'last_login': datetime.now()},
    'user_id = ?',
    (user_id,)
)

# Delete data
db.delete('users', 'user_id = ?', (user_id,))
```

#### Connection Pool Usage

```python
from abhikarta.db.db_connection_pool import DatabaseConnectionPool, DatabaseType, PoolConfig

# Create pool
config = PoolConfig(min_idle=5, max_idle=10, max_total=20)

pool = DatabaseConnectionPool(
    db_type=DatabaseType.POSTGRESQL,
    config=config,
    host='localhost',
    port=5432,
    database='myapp',
    user='postgres',
    password='secret'
)

# Use with context manager (recommended)
with pool.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE active = TRUE")
    users = cursor.fetchall()
    cursor.close()

# Manual borrow/return
wrapper = pool.borrow_connection()
try:
    cursor = wrapper.connection.cursor()
    cursor.execute("INSERT INTO logs (message) VALUES (%s)", ('test',))
    wrapper.connection.commit()
    cursor.close()
finally:
    pool.return_connection(wrapper)

# Check pool status
status = pool.get_pool_status()
print(f"Idle: {status['idle_connections']}, Active: {status['active_connections']}")

# Cleanup
pool.close()
```

### 6.2 Pool Manager Usage

#### Getting Pools

```python
from abhikarta.db.db_connection_pool_manager import (
    get_pool_manager,
    ConnectionConfig,
    DatabaseType
)

# Get singleton manager
manager = get_pool_manager()

# Method 1: Using ConnectionConfig
pg_config = ConnectionConfig(
    db_type=DatabaseType.POSTGRESQL,
    host='localhost',
    port=5432,
    database='mydb',
    user='postgres',
    password='secret'
)

pool1 = manager.get_pool(pg_config)

# Method 2: Using kwargs (convenience)
pool2 = manager.get_pool(
    db_type='postgresql',
    host='localhost',
    port=5432,
    database='mydb',
    user='postgres',
    password='secret'
)

# Both return the same pool instance
assert pool1 is pool2  # True!

# Method 3: Named pools
analytics_pool = manager.get_pool_by_name(
    'analytics',
    ConnectionConfig(
        db_type=DatabaseType.POSTGRESQL,
        host='analytics.company.com',
        database='analytics_prod',
        user='analyst',
        password='analyst_pass'
    )
)
```

#### Direct Connection Usage

```python
# Get connection directly (creates pool if needed)
with manager.get_connection(
    db_type='mysql',
    host='mysql.server.com',
    database='app_db',
    user='app_user',
    password='app_pass'
) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending'")
    count = cursor.fetchone()[0]
    cursor.close()
    print(f"Pending orders: {count}")
```

### 6.3 Multi-Database Application

```python
from abhikarta.db.db_connection_pool_manager import get_pool_manager, ConnectionConfig, DatabaseType

class MultiDatabaseApp:
    def __init__(self):
        self.manager = get_pool_manager()
        
        # Define database configurations
        self.dbs = {
            'users': ConnectionConfig(
                db_type=DatabaseType.POSTGRESQL,
                host='users-db.company.com',
                database='users',
                user='app',
                password='secret'
            ),
            'products': ConnectionConfig(
                db_type=DatabaseType.MYSQL,
                host='products-db.company.com',
                database='products',
                user='app',
                password='secret'
            ),
            'analytics': ConnectionConfig(
                db_type=DatabaseType.POSTGRESQL,
                host='analytics-db.company.com',
                database='analytics',
                user='analyst',
                password='secret'
            ),
            'cache': ConnectionConfig(
                db_type=DatabaseType.SQLITE,
                database='cache/local.db'
            )
        }
    
    def get_user(self, user_id: int):
        """Get user from users database."""
        with self.manager.get_connection(self.dbs['users']) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE user_id = %s",
                (user_id,)
            )
            user = cursor.fetchone()
            cursor.close()
            return user
    
    def get_products(self, category: str):
        """Get products from products database."""
        with self.manager.get_connection(self.dbs['products']) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM products WHERE category = %s AND active = TRUE",
                (category,)
            )
            products = cursor.fetchall()
            cursor.close()
            return products
    
    def log_analytics(self, event: str, data: dict):
        """Log analytics event."""
        with self.manager.get_connection(self.dbs['analytics']) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO events (event_name, data, timestamp) VALUES (%s, %s, %s)",
                (event, json.dumps(data), datetime.now())
            )
            conn.commit()
            cursor.close()
    
    def cache_get(self, key: str):
        """Get value from cache."""
        with self.manager.get_connection(self.dbs['cache']) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT value FROM cache WHERE key = ? AND expires_at > ?",
                (key, datetime.now())
            )
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
    
    def get_statistics(self):
        """Get statistics from all databases."""
        return self.manager.get_statistics()

# Usage
app = MultiDatabaseApp()

# Query different databases
user = app.get_user(123)
products = app.get_products('electronics')
app.log_analytics('page_view', {'page': '/home', 'user_id': 123})
cached_value = app.cache_get('popular_products')

# Get statistics
stats = app.get_statistics()
print(f"Total pools: {stats['manager_stats']['total_pools']}")
print(f"Total connections: {stats['aggregate_pool_stats']['total_connections']}")
```

### 6.4 Concurrent Access

```python
import concurrent.futures
from abhikarta.db.db_connection_pool_manager import get_pool_manager, ConnectionConfig, DatabaseType

def worker(worker_id: int, manager, config: ConnectionConfig, queries: int = 10):
    """Worker function to simulate concurrent database access."""
    results = []
    
    for i in range(queries):
        try:
            with manager.get_connection(config) as conn:
                cursor = conn.cursor()
                
                # Simulate work
                cursor.execute("SELECT pg_sleep(0.01)")  # 10ms delay
                cursor.execute("SELECT %s, %s", (worker_id, i))
                result = cursor.fetchone()
                
                cursor.close()
                results.append(result)
                
        except Exception as e:
            print(f"Worker {worker_id} error: {e}")
    
    return results

# Setup
manager = get_pool_manager()
config = ConnectionConfig(
    db_type=DatabaseType.POSTGRESQL,
    host='localhost',
    database='testdb',
    user='postgres',
    password='secret'
)

# Create pool with appropriate size
from abhikarta.db.db_connection_pool import PoolConfig
custom_config = PoolConfig(
    min_idle=5,
    max_idle=20,
    max_total=50,
    max_wait_time=30
)

pool = manager.get_pool(config, custom_config)

# Run concurrent workers
num_workers = 20
queries_per_worker = 50

with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
    futures = []
    for i in range(num_workers):
        future = executor.submit(worker, i, manager, config, queries_per_worker)
        futures.append(future)
    
    # Wait for all to complete
    results = concurrent.futures.wait(futures)
    
    # Check results
    for future in results.done:
        try:
            worker_results = future.result()
            print(f"Worker completed {len(worker_results)} queries")
        except Exception as e:
            print(f"Worker failed: {e}")

# Check final statistics
stats = pool.get_pool_status()
print(f"\nFinal pool statistics:")
print(f"  Idle connections: {stats['idle_connections']}")
print(f"  Active connections: {stats['active_connections']}")
print(f"  Total connections: {stats['total_connections']}")
print(f"  Statistics: {stats['statistics']}")
```

---

## 7. Advanced Features

### 7.1 Connection Validation

#### Custom Validation Queries

```python
# PostgreSQL with specific validation
pg_config = PoolConfig(
    validation_query="SELECT 1 AS test",
    validation_timeout=3,
    test_on_borrow=True,
    test_while_idle=True
)

# Oracle with dual table
oracle_config = PoolConfig(
    validation_query="SELECT 1 FROM DUAL",
    validation_timeout=3,
    test_on_borrow=True
)

# MySQL with ping
mysql_config = PoolConfig(
    validation_query="/* ping */ SELECT 1",
    validation_timeout=2,
    test_on_borrow=True
)
```

#### Validation Strategies

```python
# Strategy 1: Aggressive (safest, slower)
aggressive = PoolConfig(
    test_on_borrow=True,
    test_on_return=True,
    test_while_idle=True,
    validation_timeout=5
)

# Strategy 2: Balanced (recommended)
balanced = PoolConfig(
    test_on_borrow=True,
    test_on_return=False,
    test_while_idle=True,
    validation_timeout=3
)

# Strategy 3: Minimal (fastest, riskier)
minimal = PoolConfig(
    test_on_borrow=False,
    test_on_return=False,
    test_while_idle=True,
    time_between_eviction_runs=120,
    validation_timeout=2
)
```

### 7.2 Abandoned Connection Detection

```python
class AbandonedConnectionMonitor:
    """Monitor and report abandoned connections."""
    
    def __init__(self, pool: DatabaseConnectionPool):
        self.pool = pool
        self.abandoned_log = []
    
    def check_abandoned(self):
        """Check for abandoned connections."""
        status = self.pool.get_pool_status()
        stats = status['statistics']
        
        # Look for signs of abandoned connections
        if stats['connections_borrowed'] > stats['connections_returned'] * 1.1:
            warning = {
                'timestamp': datetime.now(),
                'borrowed': stats['connections_borrowed'],
                'returned': stats['connections_returned'],
                'difference': stats['connections_borrowed'] - stats['connections_returned']
            }
            self.abandoned_log.append(warning)
            return warning
        
        return None
    
    def get_report(self):
        """Get abandoned connection report."""
        return {
            'total_warnings': len(self.abandoned_log),
            'warnings': self.abandoned_log[-10:]  # Last 10
        }

# Usage
monitor = AbandonedConnectionMonitor(pool)

# Periodic check
import schedule
schedule.every(5).minutes.do(monitor.check_abandoned)
```

### 7.3 Connection Warmup

```python
def warmup_pool(pool: DatabaseConnectionPool, target_connections: int = None):
    """
    Warm up pool by creating connections in advance.
    
    Args:
        pool: Pool to warm up
        target_connections: Target number of connections (default: min_idle)
    """
    if target_connections is None:
        target_connections = pool.config.min_idle
    
    status = pool.get_pool_status()
    current = status['total_connections']
    needed = target_connections - current
    
    if needed <= 0:
        print(f"Pool already has {current} connections")
        return
    
    print(f"Warming up pool: creating {needed} connections...")
    
    connections = []
    try:
        # Borrow connections to force creation
        for i in range(needed):
            wrapper = pool.borrow_connection()
            connections.append(wrapper)
            print(f"Created connection {i+1}/{needed}")
        
        print("Warmup complete!")
        
    finally:
        # Return all connections
        for wrapper in connections:
            pool.return_connection(wrapper)

# Usage
warmup_pool(pool, target_connections=10)
```

### 7.4 Connection Rotation

```python
def rotate_connections(pool: DatabaseConnectionPool, percentage: float = 0.5):
    """
    Rotate a percentage of connections in the pool.
    
    Args:
        pool: Pool to rotate
        percentage: Percentage of connections to rotate (0.0 to 1.0)
    """
    status = pool.get_pool_status()
    idle_count = status['idle_connections']
    
    to_rotate = int(idle_count * percentage)
    
    print(f"Rotating {to_rotate} out of {idle_count} idle connections...")
    
    rotated = []
    try:
        # Borrow connections
        for i in range(to_rotate):
            try:
                wrapper = pool.borrow_connection(timeout=1)
                rotated.append(wrapper)
            except TimeoutError:
                break
        
        # Mark as invalid to force recreation
        for wrapper in rotated:
            pool.invalidate_connection(wrapper)
        
        print(f"Rotated {len(rotated)} connections")
        
    except Exception as e:
        print(f"Error during rotation: {e}")

# Usage: Rotate 50% of connections
rotate_connections(pool, percentage=0.5)
```

---

## 8. Monitoring and Statistics

### 8.1 Pool Statistics

```python
# Get pool status
status = pool.get_pool_status()

print(f"Pool State: {status['pool_state']}")
print(f"Idle Connections: {status['idle_connections']}")
print(f"Active Connections: {status['active_connections']}")
print(f"Total Connections: {status['total_connections']}")
print(f"Max Total: {status['max_total']}")

# Get detailed statistics
stats = status['statistics']
print(f"\nStatistics:")
print(f"  Created: {stats['connections_created']}")
print(f"  Destroyed: {stats['connections_destroyed']}")
print(f"  Borrowed: {stats['connections_borrowed']}")
print(f"  Returned: {stats['connections_returned']}")
print(f"  Validated: {stats['connections_validated']}")
print(f"  Invalidated: {stats['connections_invalidated']}")
print(f"  Avg Wait Time: {stats['average_wait_time']:.3f}s")
print(f"  Max Wait Time: {stats['max_wait_time']:.3f}s")
```

### 8.2 Manager Statistics

```python
# Get manager statistics
manager_stats = manager.get_statistics()

print("Manager Statistics:")
print(f"  Total Pools: {manager_stats['manager_stats']['total_pools']}")
print(f"  Pools Created: {manager_stats['manager_stats']['total_pools_created']}")
print(f"  Pools Destroyed: {manager_stats['manager_stats']['total_pools_destroyed']}")
print(f"  Connections Served: {manager_stats['manager_stats']['total_connections_served']}")

print("\nAggregate Pool Stats:")
print(f"  Total Idle: {manager_stats['aggregate_pool_stats']['total_idle_connections']}")
print(f"  Total Active: {manager_stats['aggregate_pool_stats']['total_active_connections']}")
print(f"  Total Connections: {manager_stats['aggregate_pool_stats']['total_connections']}")

print("\nIndividual Pools:")
for pool_info in manager_stats['pools']:
    print(f"  {pool_info['db_type']}:{pool_info['database']}")
    print(f"    Access Count: {pool_info['access_count']}")
    print(f"    Idle: {pool_info['idle']}, Active: {pool_info['active']}")
```

### 8.3 Health Monitoring

```python
def monitor_health(manager):
    """Comprehensive health monitoring."""
    
    # Perform health check
    health = manager.health_check()
    
    print(f"Health Status: {health['status']}")
    print(f"Healthy Pools: {health['healthy_pools']}")
    print(f"Total Pools: {health['total_pools']}")
    
    if health['unhealthy_pools']:
        print("\nUnhealthy Pools:")
        for pool in health['unhealthy_pools']:
            print(f"  {pool['pool_key']}: {pool['error']}")
    
    # Check pool utilization
    stats = manager.get_statistics()
    for pool_info in stats['pools']:
        utilization = pool_info['active'] / (pool_info['idle'] + pool_info['active'])
        
        if utilization > 0.8:
            print(f"WARNING: High utilization for {pool_info['database']}: {utilization:.0%}")
    
    return health['status'] == 'healthy'

# Periodic monitoring
import schedule

schedule.every(1).minutes.do(lambda: monitor_health(manager))

# Run monitoring
while True:
    schedule.run_pending()
    time.sleep(10)
```

### 8.4 Metrics Export

```python
class MetricsExporter:
    """Export pool metrics in various formats."""
    
    def __init__(self, manager):
        self.manager = manager
    
    def to_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        stats = self.manager.get_statistics()
        
        metrics = []
        
        # Manager metrics
        metrics.append(f"# HELP db_pools_total Total number of connection pools")
        metrics.append(f"# TYPE db_pools_total gauge")
        metrics.append(f"db_pools_total {stats['manager_stats']['total_pools']}")
        
        metrics.append(f"# HELP db_connections_total Total database connections")
        metrics.append(f"# TYPE db_connections_total gauge")
        metrics.append(f"db_connections_total {{state='idle'}} "
                      f"{stats['aggregate_pool_stats']['total_idle_connections']}")
        metrics.append(f"db_connections_total {{state='active'}} "
                      f"{stats['aggregate_pool_stats']['total_active_connections']}")
        
        # Per-pool metrics
        for pool in stats['pools']:
            labels = f"database='{pool['database']}',type='{pool['db_type']}'"
            
            metrics.append(f"db_pool_connections {{state='idle',{labels}}} {pool['idle']}")
            metrics.append(f"db_pool_connections {{state='active',{labels}}} {pool['active']}")
            metrics.append(f"db_pool_access_count {{{labels}}} {pool['access_count']}")
        
        return '\n'.join(metrics)
    
    def to_json(self) -> str:
        """Export metrics as JSON."""
        stats = self.manager.get_statistics()
        return json.dumps(stats, indent=2)
    
    def to_csv(self) -> str:
        """Export metrics as CSV."""
        stats = self.manager.get_statistics()
        
        lines = ['database,db_type,idle,active,access_count']
        for pool in stats['pools']:
            lines.append(
                f"{pool['database']},"
                f"{pool['db_type']},"
                f"{pool['idle']},"
                f"{pool['active']},"
                f"{pool['access_count']}"
            )
        
        return '\n'.join(lines)

# Usage
exporter = MetricsExporter(manager)

# Prometheus endpoint
@app.route('/metrics')
def metrics():
    return Response(exporter.to_prometheus(), mimetype='text/plain')

# JSON API
@app.route('/api/metrics')
def metrics_json():
    return jsonify(json.loads(exporter.to_json()))
```

---

## 9. Performance Optimization

### 9.1 Pool Sizing Guidelines

```python
def calculate_pool_size(
    avg_concurrent_requests: int,
    avg_query_duration_ms: float,
    target_wait_time_ms: float = 100
) -> dict:
    """
    Calculate optimal pool size based on workload.
    
    Args:
        avg_concurrent_requests: Average concurrent requests
        avg_query_duration_ms: Average query duration in milliseconds
        target_wait_time_ms: Target maximum wait time
        
    Returns:
        Dictionary with sizing recommendations
    """
    
    # Calculate connections needed
    conn_per_second = 1000 / avg_query_duration_ms
    conn_needed = avg_concurrent_requests / conn_per_second
    
    # Add buffer
    min_idle = max(2, int(conn_needed * 0.5))
    max_idle = max(min_idle, int(conn_needed * 1.2))
    max_total = max(max_idle, int(conn_needed * 2))
    
    return {
        'min_idle': min_idle,
        'max_idle': max_idle,
        'max_total': max_total,
        'reasoning': {
            'connections_per_second': conn_per_second,
            'connections_needed': conn_needed,
            'buffer_percentage': 20
        }
    }

# Example calculation
sizing = calculate_pool_size(
    avg_concurrent_requests=100,
    avg_query_duration_ms=50,  # 50ms average query
    target_wait_time_ms=100
)

print(f"Recommended pool sizing:")
print(f"  min_idle: {sizing['min_idle']}")
print(f"  max_idle: {sizing['max_idle']}")
print(f"  max_total: {sizing['max_total']}")
```

### 9.2 Performance Tuning

```python
# Low-latency configuration
low_latency_config = PoolConfig(
    min_idle=20,              # Keep connections ready
    max_idle=40,
    max_total=80,
    test_on_borrow=False,     # Skip validation for speed
    test_while_idle=True,     # But validate in background
    time_between_eviction_runs=300,
    lifo=True,                # Use hot connections
    block_when_exhausted=False,  # Fail fast
    max_wait_time=5
)

# High-throughput configuration
high_throughput_config = PoolConfig(
    min_idle=50,              # Large pool
    max_idle=100,
    max_total=200,
    test_on_borrow=False,     # Minimal validation overhead
    test_while_idle=True,
    time_between_eviction_runs=600,
    min_evictable_idle_time=1800,
    max_connection_lifetime=7200,
    lifo=True
)

# Memory-constrained configuration
memory_constrained_config = PoolConfig(
    min_idle=1,               # Minimal idle
    max_idle=3,
    max_total=10,
    test_on_borrow=True,
    test_while_idle=True,
    time_between_eviction_runs=30,
    min_evictable_idle_time=60,
    max_connection_lifetime=600,
    lifo=True
)
```

### 9.3 Connection Reuse Optimization

```python
class OptimizedDatabaseAccess:
    """Optimized database access patterns."""
    
    def __init__(self, manager):
        self.manager = manager
        self.config = ConnectionConfig(
            db_type=DatabaseType.POSTGRESQL,
            host='localhost',
            database='mydb',
            user='app',
            password='secret'
        )
    
    def batch_insert(self, table: str, records: List[dict]):
        """
        Optimized batch insert using single connection.
        
        Args:
            table: Table name
            records: List of records to insert
        """
        with self.manager.get_connection(self.config) as conn:
            cursor = conn.cursor()
            
            # Use executemany for efficiency
            if records:
                columns = list(records[0].keys())
                placeholders = ','.join(['%s'] * len(columns))
                query = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
                
                values = [tuple(r[col] for col in columns) for r in records]
                cursor.executemany(query, values)
                
                conn.commit()
                cursor.close()
    
    def batch_select(self, table: str, ids: List[int], batch_size: int = 1000):
        """
        Optimized batch select using single connection.
        
        Args:
            table: Table name
            ids: List of IDs to fetch
            batch_size: Size of each batch
            
        Returns:
            All fetched records
        """
        results = []
        
        with self.manager.get_connection(self.config) as conn:
            cursor = conn.cursor()
            
            # Process in batches
            for i in range(0, len(ids), batch_size):
                batch = ids[i:i+batch_size]
                placeholders = ','.join(['%s'] * len(batch))
                
                cursor.execute(
                    f"SELECT * FROM {table} WHERE id IN ({placeholders})",
                    batch
                )
                
                results.extend(cursor.fetchall())
            
            cursor.close()
        
        return results
    
    def transaction_batch(self, operations: List[callable]):
        """
        Execute multiple operations in a single transaction.
        
        Args:
            operations: List of callable operations
        """
        with self.manager.get_connection(self.config) as conn:
            try:
                cursor = conn.cursor()
                
                # Execute all operations
                for operation in operations:
                    operation(cursor)
                
                conn.commit()
                cursor.close()
                
            except Exception as e:
                conn.rollback()
                raise

# Usage
optimizer = OptimizedDatabaseAccess(manager)

# Batch insert 10,000 records efficiently
records = [{'name': f'User{i}', 'email': f'user{i}@example.com'} for i in range(10000)]
optimizer.batch_insert('users', records)

# Batch select
ids = list(range(1, 10001))
users = optimizer.batch_select('users', ids, batch_size=1000)
```

---

## 10. Best Practices

### 10.1 Connection Management

```python
# ✅ GOOD: Always use context manager
with pool.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    cursor.close()
# Connection automatically returned

# ❌ BAD: Manual borrow without proper return
wrapper = pool.borrow_connection()
cursor = wrapper.connection.cursor()
cursor.execute("SELECT * FROM users")
# Missing return_connection() - connection leak!

# ✅ GOOD: Manual borrow with try/finally
wrapper = pool.borrow_connection()
try:
    cursor = wrapper.connection.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    cursor.close()
finally:
    pool.return_connection(wrapper)
```

### 10.2 Transaction Handling

```python
# ✅ GOOD: Explicit transaction management
with pool.get_connection() as conn:
    try:
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO orders (user_id, total) VALUES (%s, %s)", (1, 100))
        cursor.execute("UPDATE inventory SET quantity = quantity - 1 WHERE product_id = %s", (1,))
        
        conn.commit()
        cursor.close()
        
    except Exception as e:
        conn.rollback()
        raise

# ❌ BAD: No transaction management
with pool.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (user_id, total) VALUES (%s, %s)", (1, 100))
    cursor.execute("UPDATE inventory SET quantity = quantity - 1 WHERE product_id = %s", (1,))
    # Missing commit - changes may not be saved!
```

### 10.3 Error Handling

```python
class RobustDatabaseAccess:
    """Database access with proper error handling."""
    
    def __init__(self, manager, config):
        self.manager = manager
        self.config = config
        self.max_retries = 3
        self.retry_delay = 1
    
    def execute_with_retry(self, query: str, params: tuple = ()):
        """Execute query with retry logic."""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                with self.manager.get_connection(self.config) as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    
                    if query.strip().upper().startswith('SELECT'):
                        results = cursor.fetchall()
                    else:
                        conn.commit()
                        results = cursor.rowcount
                    
                    cursor.close()
                    return results
                    
            except TimeoutError as e:
                last_error = e
                logger.warning(f"Connection timeout on attempt {attempt + 1}")
                time.sleep(self.retry_delay * (attempt + 1))
                
            except Exception as e:
                last_error = e
                logger.error(f"Database error on attempt {attempt + 1}: {e}")
                
                # Don't retry certain errors
                if "syntax error" in str(e).lower():
                    raise
                
                time.sleep(self.retry_delay)
        
        raise Exception(f"Failed after {self.max_retries} attempts: {last_error}")

# Usage
db = RobustDatabaseAccess(manager, config)
results = db.execute_with_retry(
    "SELECT * FROM users WHERE created_at > %s",
    (datetime.now() - timedelta(days=7),)
)
```

### 10.4 Testing Best Practices

```python
import pytest
from abhikarta.db.db_connection_pool_manager import get_pool_manager, ConnectionConfig, DatabaseType

@pytest.fixture
def test_pool():
    """Fixture for test database pool."""
    config = ConnectionConfig(
        db_type=DatabaseType.SQLITE,
        database=':memory:'  # In-memory database
    )
    
    manager = get_pool_manager()
    pool = manager.get_pool(config)
    
    # Setup test schema
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        ''')
        conn.commit()
        cursor.close()
    
    yield pool
    
    # Cleanup
    pool.close()

def test_insert_user(test_pool):
    """Test user insertion."""
    with test_pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            ('Test User', 'test@example.com')
        )
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        cursor.close()
        
    assert count == 1

def test_concurrent_access(test_pool):
    """Test concurrent database access."""
    import concurrent.futures
    
    def insert_user(user_id):
        with test_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
                (user_id, f'User{user_id}', f'user{user_id}@example.com')
            )
            conn.commit()
            cursor.close()
    
    # Insert 100 users concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(insert_user, i) for i in range(100)]
        concurrent.futures.wait(futures)
    
    # Verify
    with test_pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        cursor.close()
    
    assert count == 100
```

---

## 11. Troubleshooting

### 11.1 Common Issues

#### Issue: Connection Timeout

```python
# Problem: Frequent timeout errors

# Diagnosis
status = pool.get_pool_status()
print(f"Active: {status['active_connections']}")
print(f"Max Total: {status['max_total']}")

if status['active_connections'] >= status['max_total']:
    print("Pool exhausted! Consider increasing max_total")

# Solution 1: Increase pool size
config = PoolConfig(
    min_idle=10,
    max_idle=30,
    max_total=50,  # Increased from 20
    max_wait_time=60  # Longer timeout
)

# Solution 2: Check for connection leaks
stats = pool.get_pool_status()['statistics']
if stats['connections_borrowed'] > stats['connections_returned'] * 1.1:
    print("Possible connection leak! Check for missing return_connection() calls")
```

#### Issue: Slow Query Performance

```python
# Problem: Queries are slow

# Diagnosis
stats = pool.get_pool_status()['statistics']
print(f"Average wait time: {stats['average_wait_time']:.3f}s")
print(f"Max wait time: {stats['max_wait_time']:.3f}s")

# Solution 1: Disable test-on-borrow for performance
config = PoolConfig(
    test_on_borrow=False,  # Skip validation
    test_while_idle=True   # But validate in background
)

# Solution 2: Use LIFO for better cache locality
config = PoolConfig(
    lifo=True  # Use most recently returned connection
)

# Solution 3: Increase min_idle to reduce wait
config = PoolConfig(
    min_idle=20,  # More connections ready
    max_idle=40
)
```

#### Issue: Memory Usage

```python
# Problem: High memory usage

# Diagnosis
status = pool.get_pool_status()
print(f"Total connections: {status['total_connections']}")
print(f"Idle connections: {status['idle_connections']}")

# Solution 1: Reduce max_idle
config = PoolConfig(
    min_idle=2,
    max_idle=5,  # Reduced from 10
    max_total=10
)

# Solution 2: Aggressive eviction
config = PoolConfig(
    time_between_eviction_runs=30,  # More frequent
    min_evictable_idle_time=120,    # Shorter idle time
    max_connection_lifetime=600     # Shorter lifetime
)

# Solution 3: Clear idle connections manually
pool.clear_idle_connections()
```

### 11.2 Debugging Tools

```python
class PoolDebugger:
    """Debugging utilities for connection pools."""
    
    def __init__(self, pool: DatabaseConnectionPool):
        self.pool = pool
    
    def diagnose(self):
        """Comprehensive pool diagnosis."""
        status = self.pool.get_pool_status()
        stats = status['statistics']
        
        print("=== Pool Diagnosis ===\n")
        
        # Basic status
        print(f"Pool State: {status['pool_state']}")
        print(f"Idle: {status['idle_connections']}")
        print(f"Active: {status['active_connections']}")
        print(f"Total: {status['total_connections']}")
        print(f"Max: {status['max_total']}\n")
        
        # Utilization
        if status['total_connections'] > 0:
            utilization = status['active_connections'] / status['total_connections']
            print(f"Utilization: {utilization:.1%}")
            
            if utilization > 0.9:
                print("⚠️  HIGH UTILIZATION - Consider increasing pool size")
            elif utilization < 0.1:
                print("ℹ️  LOW UTILIZATION - Pool might be oversized")
        
        # Connection lifecycle
        print(f"\nLifecycle:")
        print(f"  Created: {stats['connections_created']}")
        print(f"  Destroyed: {stats['connections_destroyed']}")
        print(f"  Net: {stats['connections_created'] - stats['connections_destroyed']}")
        
        # Borrowing patterns
        print(f"\nBorrowing:")
        print(f"  Borrowed: {stats['connections_borrowed']}")
        print(f"  Returned: {stats['connections_returned']}")
        
        leak_ratio = stats['connections_borrowed'] / max(stats['connections_returned'], 1)
        if leak_ratio > 1.05:
            print(f"⚠️  POSSIBLE LEAK - Borrow/Return ratio: {leak_ratio:.2f}")
        
        # Wait times
        print(f"\nWait Times:")
        print(f"  Average: {stats['average_wait_time']:.3f}s")
        print(f"  Maximum: {stats['max_wait_time']:.3f}s")
        print(f"  Total Waits: {stats['total_wait_count']}")
        
        if stats['average_wait_time'] > 1.0:
            print("⚠️  HIGH WAIT TIMES - Pool may be undersized")
        
        # Validation
        print(f"\nValidation:")
        print(f"  Validated: {stats['connections_validated']}")
        print(f"  Invalidated: {stats['connections_invalidated']}")
        
        if stats['connections_invalidated'] > stats['connections_validated'] * 0.1:
            print("⚠️  HIGH INVALIDATION RATE - Check database connectivity")
        
        print("\n=== End Diagnosis ===")
    
    def trace_connections(self, duration_seconds: int = 10):
        """Trace connection activity for specified duration."""
        print(f"Tracing connections for {duration_seconds} seconds...\n")
        
        start_status = self.pool.get_pool_status()
        start_stats = start_status['statistics']
        
        time.sleep(duration_seconds)
        
        end_status = self.pool.get_pool_status()
        end_stats = end_status['statistics']
        
        # Calculate deltas
        borrows = end_stats['connections_borrowed'] - start_stats['connections_borrowed']
        returns = end_stats['connections_returned'] - start_stats['connections_returned']
        creates = end_stats['connections_created'] - start_stats['connections_created']
        destroys = end_stats['connections_destroyed'] - start_stats['connections_destroyed']
        
        print(f"Activity over {duration_seconds}s:")
        print(f"  Borrows: {borrows}")
        print(f"  Returns: {returns}")
        print(f"  Creates: {creates}")
        print(f"  Destroys: {destroys}")
        print(f"  Rate: {borrows/duration_seconds:.1f} borrows/sec")

# Usage
debugger = PoolDebugger(pool)
debugger.diagnose()
debugger.trace_connections(60)  # Trace for 1 minute
```

---

## 12. Appendix

### 12.1 Database-Specific Configurations

#### PostgreSQL

```python
pg_config = ConnectionConfig(
    db_type=DatabaseType.POSTGRESQL,
    host='localhost',
    port=5432,
    database='mydb',
    user='postgres',
    password='secret',
    application_name='abhikarta-app',
    ssl=True,
    ssl_ca='/path/to/ca.crt',
    connection_timeout=10
)

pg_pool_config = PoolConfig(
    min_idle=5,
    max_idle=15,
    max_total=30,
    test_on_borrow=True,
    validation_query="SELECT 1",
    max_connection_lifetime=3600
)
```

#### MySQL

```python
mysql_config = ConnectionConfig(
    db_type=DatabaseType.MYSQL,
    host='localhost',
    port=3306,
    database='mydb',
    user='root',
    password='secret',
    charset='utf8mb4',
    autocommit=False,
    ssl=True
)

mysql_pool_config = PoolConfig(
    min_idle=5,
    max_idle=15,
    max_total=30,
    test_on_borrow=True,
    validation_query="SELECT 1",
    max_connection_lifetime=3600
)
```

#### SQLite

```python
sqlite_config = ConnectionConfig(
    db_type=DatabaseType.SQLITE,
    database='data/app.db',
    connection_timeout=10
)

sqlite_pool_config = PoolConfig(
    min_idle=1,
    max_idle=3,
    max_total=5,
    test_on_borrow=False,  # SQLite doesn't need validation
    test_while_idle=False
)
```

### 12.2 Performance Benchmarks

```python
def benchmark_pool(pool: DatabaseConnectionPool, num_operations: int = 1000):
    """Benchmark pool performance."""
    import time
    
    print(f"Benchmarking pool with {num_operations} operations...\n")
    
    # Warmup
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
    
    # Benchmark sequential
    start = time.time()
    for i in range(num_operations):
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
    sequential_time = time.time() - start
    
    # Benchmark concurrent
    import concurrent.futures
    
    def worker():
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
    
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker) for _ in range(num_operations)]
        concurrent.futures.wait(futures)
    concurrent_time = time.time() - start
    
    # Results
    print(f"Results:")
    print(f"  Sequential:")
    print(f"    Total time: {sequential_time:.2f}s")
    print(f"    Operations/sec: {num_operations/sequential_time:.0f}")
    print(f"    Avg latency: {sequential_time/num_operations*1000:.2f}ms")
    
    print(f"\n  Concurrent (10 workers):")
    print(f"    Total time: {concurrent_time:.2f}s")
    print(f"    Operations/sec: {num_operations/concurrent_time:.0f}")
    print(f"    Avg latency: {concurrent_time/num_operations*1000:.2f}ms")
    
    print(f"\n  Speedup: {sequential_time/concurrent_time:.2f}x")
    
    # Pool statistics
    stats = pool.get_pool_status()['statistics']
    print(f"\n  Pool Stats:")
    print(f"    Avg wait: {stats['average_wait_time']*1000:.2f}ms")
    print(f"    Max wait: {stats['max_wait_time']*1000:.2f}ms")

# Run benchmark
benchmark_pool(pool, num_operations=10000)
```

### 12.3 Migration Guide

#### From Direct Connections

```python
# Before: Direct connections
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    database='mydb',
    user='postgres',
    password='secret'
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()
cursor.close()
conn.close()

# After: Using pool manager
from abhikarta.db.db_connection_pool_manager import get_pool_manager, ConnectionConfig, DatabaseType

manager = get_pool_manager()

with manager.get_connection(
    db_type='postgresql',
    host='localhost',
    database='mydb',
    user='postgres',
    password='secret'
) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
```

#### From psycopg2.pool

```python
# Before: psycopg2.pool.ThreadedConnectionPool
from psycopg2.pool import ThreadedConnectionPool

pool = ThreadedConnectionPool(
    minconn=2,
    maxconn=10,
    host='localhost',
    database='mydb',
    user='postgres',
    password='secret'
)

conn = pool.getconn()
try:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
finally:
    pool.putconn(conn)

# After: Abhikarta connection pool
from abhikarta.db.db_connection_pool import DatabaseConnectionPool, DatabaseType, PoolConfig

config = PoolConfig(min_idle=2, max_idle=10, max_total=10)

pool = DatabaseConnectionPool(
    db_type=DatabaseType.POSTGRESQL,
    config=config,
    host='localhost',
    database='mydb',
    user='postgres',
    password='secret'
)

with pool.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
```

### 12.4 Configuration Templates

#### Small Application

```python
# Small app: 10-100 concurrent users
SMALL_APP_CONFIG = PoolConfig(
    min_idle=2,
    max_idle=5,
    max_total=10,
    test_on_borrow=True,
    test_while_idle=True,
    time_between_eviction_runs=60,
    max_connection_lifetime=1800,
    abandoned_timeout=300
)
```

#### Medium Application

```python
# Medium app: 100-1000 concurrent users
MEDIUM_APP_CONFIG = PoolConfig(
    min_idle=10,
    max_idle=30,
    max_total=50,
    test_on_borrow=True,
    test_while_idle=True,
    time_between_eviction_runs=60,
    max_connection_lifetime=3600,
    abandoned_timeout=300,
    max_wait_time=30
)
```

#### Large Application

```python
# Large app: 1000+ concurrent users
LARGE_APP_CONFIG = PoolConfig(
    min_idle=20,
    max_idle=80,
    max_total=150,
    test_on_borrow=False,  # Performance optimization
    test_while_idle=True,
    time_between_eviction_runs=120,
    max_connection_lifetime=7200,
    abandoned_timeout=600,
    max_wait_time=60
)
```

---

## Document End

**Abhikarta Database Connection Pooling System - Complete Technical Documentation**

For the latest updates and support, visit:
- **GitHub**: https://github.com/ajsinha/abhikarta
- **Email**: ajsinha@gmail.com

---

**Copyright © 2025-2030, All Rights Reserved - Ashutosh Sinha**

**Patent Pending**