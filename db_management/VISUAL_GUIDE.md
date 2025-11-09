# Database Connection Pool Manager - Quick Visual Reference

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

---

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         YOUR APPLICATION                         │
│                                                                  │
│  from pool_manager import get_pool_manager                      │
│  manager = get_pool_manager()  # Get singleton                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    POOL MANAGER (Singleton)                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Pools Dictionary:                                         │  │
│  │  "user_db"    → SQLiteConnectionPool                     │  │
│  │  "orders_db"  → PostgreSQLConnectionPool                 │  │
│  │  "cache_db"   → SQLiteConnectionPool                     │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────┬───────────────┬──────────────────┬─────────────────┘
             │               │                  │
             ▼               ▼                  ▼
   ┌─────────────┐  ┌─────────────┐   ┌─────────────┐
   │ SQLite Pool │  │PostgreSQL   │   │ MySQL Pool  │
   │             │  │    Pool     │   │             │
   └──────┬──────┘  └──────┬──────┘   └──────┬──────┘
          │                │                 │
          ▼                ▼                 ▼
   ┌─────────────────────────────────────────────┐
   │     POOL INTERNAL STRUCTURE                 │
   │  ┌───────────────────────────────────────┐  │
   │  │ Available Queue (Thread-Safe FIFO)   │  │
   │  │  ┌───┐  ┌───┐  ┌───┐  ┌───┐         │  │
   │  │  │ C │  │ C │  │ C │  │ C │  ...    │  │
   │  │  └───┘  └───┘  └───┘  └───┘         │  │
   │  └───────────────────────────────────────┘  │
   │  ┌───────────────────────────────────────┐  │
   │  │ All Connections Set                  │  │
   │  │  {C1, C2, C3, C4, C5, C6, ...}      │  │
   │  └───────────────────────────────────────┘  │
   │  ┌───────────────────────────────────────┐  │
   │  │ Background Cleanup Thread            │  │
   │  │  - Runs every N seconds              │  │
   │  │  - Closes excess idle connections    │  │
   │  └───────────────────────────────────────┘  │
   └─────────────────────────────────────────────┘
                      │
                      ▼
            ┌──────────────────┐
            │ DATABASE SERVER  │
            │  (SQLite/PG/MySQL)│
            └──────────────────┘
```

---

## Connection Lifecycle

```
╔═══════════════════════════════════════════════════════════════╗
║                    CONNECTION LIFECYCLE                        ║
╚═══════════════════════════════════════════════════════════════╝

1. INITIALIZATION (Pool Creation)
   ─────────────────────────────────
   create_pool(config)
          │
          ▼
   Create min_connections
          │
          ├─→ Connection 1 ──┐
          ├─→ Connection 2 ──┤
          └─→ Connection N ──┴─→ Add to Available Queue
                                 Add to All Connections Set
                                 Start Cleanup Thread

2. ACQUISITION (Get Connection)
   ────────────────────────────────
   get_connection_from_pool(pool_name)
          │
          ├─→ Available in Queue? ──YES─→ Validate ──VALID─→ Return
          │                                   │
          │                                INVALID
          │                                   │
          │                              Close & Retry
          │
          └─→ Under max? ──YES─→ Create New ──→ Return
                  │
                  NO
                  │
              Wait/Timeout

3. USAGE (Application Uses Connection)
   ───────────────────────────────────────
   with get_connection_context(pool_name) as conn:
       cursor = conn.cursor()
       cursor.execute("SELECT ...")
       result = cursor.fetchall()
   ────────────────────────────────────────
   # Automatic return to pool on exit

4. RETURN (Close Connection)
   ─────────────────────────────
   close_connection(conn, pool_name)
          │
          ├─→ Validate Connection
          │       │
          │    VALID ──→ Mark Idle ──→ Put in Queue
          │       │
          │   INVALID ──→ Close & Discard
          │
          └─→ Connection Available for Reuse

5. MAINTENANCE (Background Thread)
   ──────────────────────────────────
   Every validation_interval seconds:
          │
          ├─→ Collect Idle Connections
          │
          ├─→ Sort by Idle Time
          │
          ├─→ Calculate Excess (above max_idle_connections)
          │
          ├─→ Close Excess (keeping min_connections)
          │
          └─→ Return Remaining to Queue

6. SHUTDOWN (Pool Cleanup)
   ────────────────────────────
   shutdown_all()
          │
          ├─→ Signal Shutdown Event
          │
          ├─→ Wait for Cleanup Thread
          │
          ├─→ Close All Connections
          │
          └─→ Clear Data Structures
```

---

## Thread Safety Model

```
╔═══════════════════════════════════════════════════════════════╗
║                   THREAD SAFETY ARCHITECTURE                   ║
╚═══════════════════════════════════════════════════════════════╝

LOCK HIERARCHY (Acquire Top → Bottom, Never Reverse)
─────────────────────────────────────────────────────
Level 1: PoolManager._lock       (Highest)
         Used for: Pool registration/removal
         
Level 2: ConnectionPool._lock    (Medium)
         Used for: Connection checkout/checkin
         
Level 3: Queue internal locks    (Lowest)
         Used for: Queue operations

CRITICAL SECTIONS (Protected by Locks)
──────────────────────────────────────
┌─────────────────────────────────────────────┐
│ with pool._lock:                            │
│     ┌─────────────────────────────────────┐ │
│     │ Connection Creation                 │ │
│     │ Connection Validation               │ │
│     │ Statistics Update                   │ │
│     │ Pool State Changes                  │ │
│     └─────────────────────────────────────┘ │
│ # Atomic Operation Complete                 │
└─────────────────────────────────────────────┘

THREAD-SAFE COMPONENTS
──────────────────────
[Queue] → Thread-safe by design (Python's queue.Queue)
[RLock] → Reentrant Lock (same thread can acquire multiple times)
[Event] → Thread-safe signaling for shutdown
[Set]   → Protected by locks in all access paths
```

---

## API Quick Reference

```
╔═══════════════════════════════════════════════════════════════╗
║                    API QUICK REFERENCE                         ║
╚═══════════════════════════════════════════════════════════════╝

INITIALIZATION
──────────────
from pool_manager import get_pool_manager
from pool_config import SQLitePoolConfig, PostgreSQLPoolConfig, MySQLPoolConfig

manager = get_pool_manager()  # Get singleton


POOL MANAGEMENT
───────────────
# Create Pool
manager.create_pool(config)

# Check if exists
manager.pool_exists(pool_name) → bool

# Get pool names
manager.get_all_pool_names() → list

# Remove pool
manager.remove_pool(pool_name, force=False)

# Shutdown all
manager.shutdown_all()


CONNECTION OPERATIONS
─────────────────────
# Method 1: Context Manager (Recommended)
with manager.get_connection_context(pool_name) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT ...")

# Method 2: Manual
conn = manager.get_connection_from_pool(pool_name)
try:
    # Use conn.connection
    cursor = conn.connection.cursor()
finally:
    manager.close_connection(conn, pool_name)


MONITORING & STATISTICS
────────────────────────
# Single pool stats
stats = manager.get_pool_stats(pool_name)
# Returns: {
#     'pool_name': str,
#     'total_connections': int,
#     'active_connections': int,
#     'available_connections': int,
#     'max_connections': int,
#     'min_connections': int
# }

# All pools stats
all_stats = manager.get_all_stats()
# Returns: Dict[pool_name, stats]
```

---

## Configuration Templates

```
╔═══════════════════════════════════════════════════════════════╗
║                  CONFIGURATION TEMPLATES                       ║
╚═══════════════════════════════════════════════════════════════╝

SQLITE FILE-BASED
─────────────────
config = SQLitePoolConfig(
    pool_name="app_db",
    database_path="/path/to/database.db",
    min_connections=2,
    max_connections=10,
    max_idle_connections=5,
    connection_timeout=30.0,
    idle_timeout=300.0
)

SQLITE IN-MEMORY
────────────────
config = SQLitePoolConfig(
    pool_name="cache",
    database_path=":memory:",    # Special in-memory database
    min_connections=3,
    max_connections=15
)

POSTGRESQL
──────────
config = PostgreSQLPoolConfig(
    pool_name="postgres_pool",
    host="localhost",
    port=5432,
    database="mydb",
    user="postgres",
    password="secret",
    sslmode="prefer",
    min_connections=5,
    max_connections=20
)

MYSQL
─────
config = MySQLPoolConfig(
    pool_name="mysql_pool",
    host="localhost",
    port=3306,
    database="mydb",
    user="root",
    password="secret",
    charset="utf8mb4",
    autocommit=False,
    min_connections=5,
    max_connections=20
)
```

---

## Common Patterns

```
╔═══════════════════════════════════════════════════════════════╗
║                     COMMON USAGE PATTERNS                      ║
╚═══════════════════════════════════════════════════════════════╝

PATTERN 1: WEB APPLICATION
──────────────────────────
# At startup
def init_database():
    manager = get_pool_manager()
    config = PostgreSQLPoolConfig(
        pool_name="webapp",
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        # ... other config
    )
    manager.create_pool(config)

# In request handler
def handle_request(user_id):
    manager = get_pool_manager()
    with manager.get_connection_context("webapp") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()


PATTERN 2: MULTI-DATABASE APPLICATION
──────────────────────────────────────
# Create multiple pools
manager = get_pool_manager()
manager.create_pool(sqlite_config)    # "cache"
manager.create_pool(postgres_config)  # "primary"
manager.create_pool(mysql_config)     # "analytics"

# Use different databases
with manager.get_connection_context("cache") as conn:
    # Fast cache operations
    pass

with manager.get_connection_context("primary") as conn:
    # Main database operations
    pass

with manager.get_connection_context("analytics") as conn:
    # Analytics queries
    pass


PATTERN 3: TRANSACTION MANAGEMENT
──────────────────────────────────
with manager.get_connection_context("orders") as conn:
    cursor = conn.cursor()
    try:
        # Begin transaction (implicit)
        cursor.execute("INSERT INTO orders (...) VALUES (...)")
        cursor.execute("UPDATE inventory SET stock = ...")
        conn.commit()  # Success
    except Exception as e:
        conn.rollback()  # Rollback on error
        raise


PATTERN 4: BATCH OPERATIONS
────────────────────────────
with manager.get_connection_context("bulk_db") as conn:
    cursor = conn.cursor()
    
    # executemany for batch insert
    data = [(1, "item1"), (2, "item2"), ...]
    cursor.executemany(
        "INSERT INTO items (id, name) VALUES (?, ?)",
        data
    )
    conn.commit()


PATTERN 5: MONITORING
─────────────────────
import time

def monitor_pools():
    manager = get_pool_manager()
    while True:
        stats = manager.get_all_stats()
        for name, stat in stats.items():
            utilization = stat['active_connections'] / stat['max_connections']
            if utilization > 0.8:
                print(f"WARNING: {name} at {utilization*100:.0f}% capacity")
        time.sleep(60)
```

---

## Performance Tips

```
╔═══════════════════════════════════════════════════════════════╗
║                      PERFORMANCE TIPS                          ║
╚═══════════════════════════════════════════════════════════════╝

1. POOL SIZING
   ───────────
   Formula: max = (DB_max_connections * 0.8) / num_instances
   
   Low Traffic:  min=2,  max=5
   Medium:       min=5,  max=20
   High:         min=10, max=50

2. CONNECTION TIMEOUTS
   ───────────────────
   Fast Operations:  connection_timeout=5.0
   Normal:           connection_timeout=30.0
   Batch/Long:       connection_timeout=60.0

3. IDLE MANAGEMENT
   ───────────────
   Short Sessions:   idle_timeout=300  (5 min)
   Long Sessions:    idle_timeout=1800 (30 min)
   24/7 Service:     idle_timeout=3600 (1 hour)

4. DATABASE CHOICE
   ───────────────
   Low Concurrency (<10):    SQLite file-based
   Medium (10-100):          PostgreSQL
   High (>100):              PostgreSQL/MySQL with proper tuning

5. BEST PRACTICES
   ──────────────
   ✓ Always use context managers
   ✓ Set appropriate timeouts
   ✓ Monitor pool statistics
   ✓ Handle exceptions properly
   ✓ Use parameterized queries
   ✗ Don't hold connections longer than needed
   ✗ Don't create pools repeatedly
   ✗ Don't ignore timeout errors
```

---

## Troubleshooting Guide

```
╔═══════════════════════════════════════════════════════════════╗
║                   TROUBLESHOOTING GUIDE                        ║
╚═══════════════════════════════════════════════════════════════╝

PROBLEM: TimeoutError acquiring connection
CAUSE:    All connections busy
SOLUTION: 
  1. Increase max_connections
  2. Check for connection leaks
  3. Review application logic
  Code:
    stats = manager.get_pool_stats(pool_name)
    if stats['active_connections'] == stats['max_connections']:
        print("Pool saturated! Increase max_connections")

───────────────────────────────────────────────────────────────

PROBLEM: "Pool does not exist" KeyError
CAUSE:    Pool not created before use
SOLUTION:
  Check pool exists before using
  Code:
    if not manager.pool_exists("my_pool"):
        manager.create_pool(config)

───────────────────────────────────────────────────────────────

PROBLEM: SQLite "database is locked"
CAUSE:    SQLite doesn't handle high concurrency
SOLUTION:
  1. Reduce max_connections for SQLite
  2. Increase timeout in SQLitePoolConfig
  3. Use PostgreSQL/MySQL for high concurrency

───────────────────────────────────────────────────────────────

PROBLEM: ImportError: No module named 'psycopg2'
CAUSE:    Database driver not installed
SOLUTION:
  pip install --break-system-packages psycopg2-binary
  # Or for MySQL:
  pip install --break-system-packages mysql-connector-python

───────────────────────────────────────────────────────────────

PROBLEM: Connections not returning to pool
CAUSE:    Not using context manager or forgetting close
SOLUTION:
  Always use context managers:
  with manager.get_connection_context(name) as conn:
      # Use connection
      pass
  # Automatic return!
```

---

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha** | ajsinha@gmail.com

**Patent Pending**: Architectural patterns may be subject to patent applications.
