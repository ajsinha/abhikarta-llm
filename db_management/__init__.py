"""
Database Management Module - Connection Pool Manager

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

# Version information
__version__ = "1.0.0"
__author__ = "Ashutosh Sinha"
__email__ = "ajsinha@gmail.com"
__copyright__ = "Copyright © 2025-2030, All Rights Reserved"

# Import configuration classes
from .pool_config import (
    PoolConfiguration,
    SQLitePoolConfig,
    PostgreSQLPoolConfig,
    MySQLPoolConfig
)

# Import pool classes
from .abstract_pool import (
    AbstractConnectionPool,
    PooledConnection
)

from .connection_pool_factory import (
    SQLiteConnectionPool,
    PostgreSQLConnectionPool,
    MySQLConnectionPool,
    create_connection_pool
)

# Import pool manager (main API)
from .pool_manager import (
    PoolManager,
    get_pool_manager
)

# Define public API
__all__ = [
    # Configuration
    'PoolConfiguration',
    'SQLitePoolConfig',
    'PostgreSQLPoolConfig',
    'MySQLPoolConfig',
    
    # Pool classes
    'AbstractConnectionPool',
    'PooledConnection',
    'SQLiteConnectionPool',
    'PostgreSQLConnectionPool',
    'MySQLConnectionPool',
    'create_connection_pool',
    
    # Pool Manager (main API)
    'PoolManager',
    'get_pool_manager',
    
    # Version info
    '__version__',
    '__author__',
    '__email__',
]


def get_version():
    """Return the version string."""
    return __version__


def get_copyright():
    """Return the copyright notice."""
    return __copyright__


# Quick start example in docstring
__doc__ = """
Database Connection Pool Manager - High-Performance Connection Pooling

Quick Start:
-----------
from db_management import get_pool_manager, SQLitePoolConfig

# Get singleton pool manager
manager = get_pool_manager()

# Create a connection pool
config = SQLitePoolConfig(
    pool_name="my_app",
    database_path="app.db",
    min_connections=2,
    max_connections=10
)
manager.create_pool(config)

# Use connections with context manager (Pattern 1 - Recommended)
conn = manager.get_connection_from_pool("my_app")
with conn as connection:
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()

# Or use pool's context manager (Pattern 2 - Also Recommended)
with manager.get_connection_context("my_app") as connection:
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()

Features:
--------
- Thread-safe singleton pool manager
- Multiple database support (SQLite, PostgreSQL, MySQL)
- Automatic connection recycling and cleanup
- Background maintenance thread
- Comprehensive statistics and monitoring
- Production-ready with full error handling

For more information, see the documentation files:
- README.md: Complete user guide
- Database Connection Pool Manager ARCHITECTURE.md: Technical architecture
- VISUAL_GUIDE.md: Quick reference with diagrams

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)
"""
