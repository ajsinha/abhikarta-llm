"""
Example Usage of Fixed SQLite Connection Pool

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

from pool_config import SQLitePoolConfig
from pool_manager import get_pool_manager
import logging

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def example_basic_usage():
    """Basic usage example with fixed configuration."""

    # Create pool configuration with improved settings
    config = SQLitePoolConfig(
        pool_name="my_app_db",
        database_path='/home/ashutosh/PycharmProjects/abhikarta-llm/data/abhikarta-llm.db',

        # Pool settings
        min_connections=1,
        max_connections=5,
        max_idle_connections=2,
        connection_timeout=30.0,
        idle_timeout=300.0,

        # SQLite-specific settings (NEW - fixes the "database is locked" issue)
        timeout=30.0,  # SQLite busy timeout in seconds
        busy_timeout=30000,  # Busy timeout in milliseconds
        enable_wal_mode=True,  # Enable WAL mode for better concurrency
        journal_mode="WAL",  # Write-Ahead Logging
        synchronous="NORMAL",  # Safe with WAL, faster than FULL
        cache_size=-2000,  # 2MB cache
        isolation_level="DEFERRED",  # Better than None for concurrent access
        check_same_thread=False  # Required for pooling
    )

    # Get pool manager and create pool
    manager = get_pool_manager()
    manager.create_pool(config)

    # Use the pool
    try:
        # Method 1: Manual connection management
        conn = manager.get_connection_from_pool("my_app_db")
        try:
            cursor = conn.connection.cursor()
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()
            print(f"SQLite version: {version[0]}")
            cursor.close()
        finally:
            manager.close_connection(conn, "my_app_db")

        # Method 2: Context manager (recommended)
        with manager.get_connection_context("my_app_db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()
            print(f"SQLite version: {version[0]}")
            cursor.close()

        # Check pool stats
        stats = manager.get_pool_stats("my_app_db")
        print(f"Pool stats: {stats}")

    finally:
        # Cleanup
        manager.remove_pool("my_app_db")


def example_concurrent_writes():
    """
    Example showing concurrent write operations that would have
    failed with the old configuration.
    """
    import threading
    import time

    # Create pool with fixed configuration
    config = SQLitePoolConfig(
        pool_name="concurrent_db",
        database_path='/tmp/test_concurrent.db',
        min_connections=1,
        max_connections=10,
        timeout=30.0,
        busy_timeout=30000,
        enable_wal_mode=True,
        isolation_level="DEFERRED"
    )

    manager = get_pool_manager()
    manager.create_pool(config)

    # Create test table
    with manager.get_connection_context("concurrent_db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id INTEGER,
                timestamp REAL
            )
        """)
        conn.commit()
        cursor.close()

    def worker(thread_id, num_operations):
        """Worker function that performs database operations."""
        for i in range(num_operations):
            try:
                with manager.get_connection_context("concurrent_db") as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO test_table (thread_id, timestamp) VALUES (?, ?)",
                        (thread_id, time.time())
                    )
                    conn.commit()
                    cursor.close()
                    print(f"Thread {thread_id}: Inserted record {i + 1}")
                    time.sleep(0.01)  # Small delay
            except Exception as e:
                print(f"Thread {thread_id}: Error - {e}")

    # Create multiple threads
    threads = []
    num_threads = 5
    operations_per_thread = 10

    print(f"\nStarting {num_threads} concurrent threads...")
    for i in range(num_threads):
        thread = threading.Thread(target=worker, args=(i, operations_per_thread))
        threads.append(thread)
        thread.start()

    # Wait for all threads
    for thread in threads:
        thread.join()

    # Verify results
    with manager.get_connection_context("concurrent_db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        print(f"\nTotal records inserted: {count}")
        cursor.close()

    # Cleanup
    manager.remove_pool("concurrent_db")
    print("Test completed successfully!")


def example_transaction_handling():
    """Example showing proper transaction handling."""

    config = SQLitePoolConfig(
        pool_name="transaction_db",
        database_path=':memory:',
        min_connections=1,
        max_connections=5,
        isolation_level="DEFERRED"
    )

    manager = get_pool_manager()
    manager.create_pool(config)

    # Create test table
    with manager.get_connection_context("transaction_db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE accounts (
                id INTEGER PRIMARY KEY,
                balance REAL
            )
        """)
        cursor.execute("INSERT INTO accounts VALUES (1, 1000)")
        cursor.execute("INSERT INTO accounts VALUES (2, 500)")
        conn.commit()
        cursor.close()

    # Transaction example - transfer money
    with manager.get_connection_context("transaction_db") as conn:
        try:
            cursor = conn.cursor()

            # Start transaction (automatic with DEFERRED isolation level)
            cursor.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
            cursor.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")

            # Commit transaction
            conn.commit()
            print("Transaction committed successfully")

            # Verify
            cursor.execute("SELECT * FROM accounts")
            for row in cursor.fetchall():
                print(f"Account {row[0]}: ${row[1]}")

            cursor.close()

        except Exception as e:
            conn.rollback()
            print(f"Transaction rolled back: {e}")

    # Cleanup
    manager.remove_pool("transaction_db")


if __name__ == "__main__":
    print("=" * 60)
    print("Example 1: Basic Usage")
    print("=" * 60)
    example_basic_usage()

    print("\n" + "=" * 60)
    print("Example 2: Concurrent Writes (WAL mode demonstration)")
    print("=" * 60)
    example_concurrent_writes()

    print("\n" + "=" * 60)
    print("Example 3: Transaction Handling")
    print("=" * 60)
    example_transaction_handling()