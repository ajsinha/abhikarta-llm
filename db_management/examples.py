"""
Comprehensive Examples for Database Connection Pool Manager

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

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from pool_manager import get_pool_manager
from pool_config import SQLitePoolConfig, PostgreSQLPoolConfig, MySQLPoolConfig


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("Examples")


def example_sqlite_file_based():
    """
    Example 1: SQLite file-based database connection pool.
    
    Demonstrates:
    - Creating a SQLite pool for a file-based database
    - Getting and using connections
    - Using context manager for automatic connection return
    - Pool statistics
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: SQLite File-Based Database Pool")
    print("="*80)
    
    # Get pool manager singleton
    manager = get_pool_manager()
    
    # Create SQLite pool configuration
    config = SQLitePoolConfig(
        pool_name="sqlite_file_pool",
        database_path="example.db",
        min_connections=2,
        max_connections=10,
        max_idle_connections=5,
        connection_timeout=30.0,
        idle_timeout=300.0
    )
    
    # Create pool
    manager.create_pool(config)
    logger.info(f"Created pool: {config.pool_name}")
    
    # Create a test table
    with manager.get_connection_context("sqlite_file_pool") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        logger.info("Created users table")
    
    # Insert some data
    with manager.get_connection_context("sqlite_file_pool") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            ("John Doe", "john@example.com")
        )
        cursor.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            ("Jane Smith", "jane@example.com")
        )
        conn.commit()
        logger.info("Inserted test data")
    
    # Query data
    with manager.get_connection_context("sqlite_file_pool") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        logger.info(f"Retrieved {len(rows)} users:")
        for row in rows:
            print(f"  - {dict(row)}")
    
    # Show pool statistics
    stats = manager.get_pool_stats("sqlite_file_pool")
    print(f"\nPool Statistics: {stats}")
    
    # Manual connection handling (non-context manager)
    conn = manager.get_connection_from_pool("sqlite_file_pool")
    try:
        cursor = conn.connection.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users")
        count = cursor.fetchone()[0]
        logger.info(f"Total users: {count}")
    finally:
        manager.close_connection(conn, "sqlite_file_pool")


def example_sqlite_in_memory():
    """
    Example 2: SQLite in-memory database connection pool.
    
    Demonstrates:
    - Creating an in-memory SQLite pool
    - Thread-safe operations with multiple threads
    - Concurrent database access
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: SQLite In-Memory Database Pool with Multi-Threading")
    print("="*80)
    
    manager = get_pool_manager()
    
    # Create in-memory SQLite pool
    config = SQLitePoolConfig(
        pool_name="sqlite_memory_pool",
        database_path=":memory:",
        min_connections=3,
        max_connections=15,
        max_idle_connections=6
    )
    
    manager.create_pool(config)
    logger.info(f"Created in-memory pool: {config.pool_name}")
    
    # Initialize schema
    with manager.get_connection_context("sqlite_memory_pool") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        logger.info("Created products table")
    
    # Function to insert products from multiple threads
    def insert_product(thread_id: int, product_num: int):
        try:
            with manager.get_connection_context("sqlite_memory_pool") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
                    (f"Product-{thread_id}-{product_num}", 
                     10.0 + product_num, 
                     100 + product_num)
                )
                conn.commit()
            return f"Thread {thread_id}: Inserted product {product_num}"
        except Exception as e:
            return f"Thread {thread_id}: Error - {e}"
    
    # Concurrent insertions
    logger.info("Starting concurrent insertions...")
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for thread_id in range(5):
            for product_num in range(10):
                future = executor.submit(insert_product, thread_id, product_num)
                futures.append(future)
        
        for future in as_completed(futures):
            result = future.result()
            logger.debug(result)
    
    # Verify results
    with manager.get_connection_context("sqlite_memory_pool") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM products")
        count = cursor.fetchone()[0]
        logger.info(f"Total products inserted: {count}")
    
    # Show statistics
    stats = manager.get_pool_stats("sqlite_memory_pool")
    print(f"\nPool Statistics: {stats}")


def example_postgresql():
    """
    Example 3: PostgreSQL database connection pool.
    
    Demonstrates:
    - Creating a PostgreSQL pool
    - Transaction management
    - Error handling
    
    Note: Requires PostgreSQL server running and psycopg2/psycopg installed.
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: PostgreSQL Database Pool")
    print("="*80)
    
    manager = get_pool_manager()
    
    # Create PostgreSQL pool configuration
    config = PostgreSQLPoolConfig(
        pool_name="postgres_pool",
        host="localhost",
        port=5432,
        database="testdb",
        user="postgres",
        password="postgres",
        min_connections=2,
        max_connections=10,
        max_idle_connections=4
    )
    
    try:
        manager.create_pool(config)
        logger.info(f"Created PostgreSQL pool: {config.pool_name}")
        
        # Create test table
        with manager.get_connection_context("postgres_pool") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    customer_name VARCHAR(100) NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            logger.info("Created orders table")
        
        # Insert with transaction
        with manager.get_connection_context("postgres_pool") as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO orders (customer_name, amount, status) VALUES (%s, %s, %s)",
                    ("Alice Johnson", 150.00, "pending")
                )
                cursor.execute(
                    "INSERT INTO orders (customer_name, amount, status) VALUES (%s, %s, %s)",
                    ("Bob Williams", 275.50, "completed")
                )
                conn.commit()
                logger.info("Inserted orders successfully")
            except Exception as e:
                conn.rollback()
                logger.error(f"Transaction failed: {e}")
        
        # Query data
        with manager.get_connection_context("postgres_pool") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders ORDER BY id")
            rows = cursor.fetchall()
            logger.info(f"Retrieved {len(rows)} orders:")
            for row in rows:
                print(f"  - Order {row[0]}: {row[1]} - ${row[2]}")
        
        # Show statistics
        stats = manager.get_pool_stats("postgres_pool")
        print(f"\nPool Statistics: {stats}")
        
    except ImportError as e:
        logger.warning(f"Skipping PostgreSQL example: {e}")
    except Exception as e:
        logger.error(f"PostgreSQL example failed: {e}")


def example_mysql():
    """
    Example 4: MySQL database connection pool.
    
    Demonstrates:
    - Creating a MySQL pool
    - Batch operations
    - Connection pooling benefits
    
    Note: Requires MySQL server running and mysql-connector-python/pymysql installed.
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: MySQL Database Pool")
    print("="*80)
    
    manager = get_pool_manager()
    
    # Create MySQL pool configuration
    config = MySQLPoolConfig(
        pool_name="mysql_pool",
        host="localhost",
        port=3306,
        database="testdb",
        user="root",
        password="password",
        min_connections=2,
        max_connections=10,
        max_idle_connections=4,
        autocommit=False
    )
    
    try:
        manager.create_pool(config)
        logger.info(f"Created MySQL pool: {config.pool_name}")
        
        # Create test table
        with manager.get_connection_context("mysql_pool") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    department VARCHAR(50),
                    salary DECIMAL(10, 2),
                    hire_date DATE
                )
            """)
            conn.commit()
            logger.info("Created employees table")
        
        # Batch insert
        employees = [
            ("John", "Doe", "Engineering", 95000.00, "2023-01-15"),
            ("Jane", "Smith", "Marketing", 85000.00, "2023-02-20"),
            ("Mike", "Johnson", "Sales", 78000.00, "2023-03-10"),
            ("Sarah", "Williams", "Engineering", 105000.00, "2023-04-05")
        ]
        
        with manager.get_connection_context("mysql_pool") as conn:
            cursor = conn.cursor()
            cursor.executemany(
                """INSERT INTO employees 
                   (first_name, last_name, department, salary, hire_date) 
                   VALUES (%s, %s, %s, %s, %s)""",
                employees
            )
            conn.commit()
            logger.info(f"Inserted {cursor.rowcount} employees")
        
        # Query with aggregation
        with manager.get_connection_context("mysql_pool") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT department, COUNT(*) as count, AVG(salary) as avg_salary
                FROM employees
                GROUP BY department
            """)
            rows = cursor.fetchall()
            logger.info("Department statistics:")
            for row in rows:
                print(f"  - {row[0]}: {row[1]} employees, Avg Salary: ${row[2]:.2f}")
        
        # Show statistics
        stats = manager.get_pool_stats("mysql_pool")
        print(f"\nPool Statistics: {stats}")
        
    except ImportError as e:
        logger.warning(f"Skipping MySQL example: {e}")
    except Exception as e:
        logger.error(f"MySQL example failed: {e}")


def example_multi_pool_management():
    """
    Example 5: Managing multiple pools simultaneously.
    
    Demonstrates:
    - Creating multiple pools
    - Switching between different databases
    - Overall pool management
    """
    print("\n" + "="*80)
    print("EXAMPLE 5: Multi-Pool Management")
    print("="*80)
    
    manager = get_pool_manager()
    
    # Create multiple pools
    pools_config = [
        SQLitePoolConfig(
            pool_name="cache_pool",
            database_path=":memory:",
            min_connections=1,
            max_connections=5
        ),
        SQLitePoolConfig(
            pool_name="analytics_pool",
            database_path="analytics.db",
            min_connections=2,
            max_connections=8
        )
    ]
    
    for config in pools_config:
        manager.create_pool(config)
        logger.info(f"Created pool: {config.pool_name}")
    
    # Initialize cache pool
    with manager.get_connection_context("cache_pool") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE cache (
                key TEXT PRIMARY KEY,
                value TEXT,
                expires_at TIMESTAMP
            )
        """)
        cursor.execute(
            "INSERT INTO cache VALUES (?, ?, datetime('now', '+1 hour'))",
            ("user:1", "John Doe")
        )
        conn.commit()
    
    # Initialize analytics pool
    with manager.get_connection_context("analytics_pool") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE page_views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page TEXT NOT NULL,
                views INTEGER DEFAULT 0
            )
        """)
        cursor.execute(
            "INSERT INTO page_views (page, views) VALUES (?, ?)",
            ("/home", 1500)
        )
        conn.commit()
    
    # Show all pools
    all_pools = manager.get_all_pool_names()
    logger.info(f"Active pools: {all_pools}")
    
    # Show all statistics
    all_stats = manager.get_all_stats()
    print("\nAll Pool Statistics:")
    for pool_name, stats in all_stats.items():
        print(f"  {pool_name}: {stats}")


def example_stress_test():
    """
    Example 6: Stress testing the connection pool.
    
    Demonstrates:
    - High concurrency handling
    - Pool performance under load
    - Connection reuse efficiency
    """
    print("\n" + "="*80)
    print("EXAMPLE 6: Stress Test - High Concurrency")
    print("="*80)
    
    manager = get_pool_manager()
    
    config = SQLitePoolConfig(
        pool_name="stress_test_pool",
        database_path=":memory:",
        min_connections=5,
        max_connections=20,
        max_idle_connections=10,
        connection_timeout=10.0
    )
    
    manager.create_pool(config)
    
    # Create test table
    with manager.get_connection_context("stress_test_pool") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE test_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id INTEGER,
                value TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    
    # Stress test function
    def perform_operations(thread_id: int, num_operations: int) -> dict:
        start_time = time.time()
        successful = 0
        failed = 0
        
        for i in range(num_operations):
            try:
                with manager.get_connection_context("stress_test_pool") as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO test_data (thread_id, value) VALUES (?, ?)",
                        (thread_id, f"Data-{i}")
                    )
                    conn.commit()
                    successful += 1
            except Exception as e:
                failed += 1
                logger.debug(f"Thread {thread_id} operation {i} failed: {e}")
        
        elapsed = time.time() - start_time
        return {
            'thread_id': thread_id,
            'successful': successful,
            'failed': failed,
            'elapsed': elapsed
        }
    
    # Run stress test
    num_threads = 50
    operations_per_thread = 20
    
    logger.info(f"Starting stress test: {num_threads} threads, "
                f"{operations_per_thread} operations each")
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(perform_operations, thread_id, operations_per_thread)
            for thread_id in range(num_threads)
        ]
        
        results = [future.result() for future in as_completed(futures)]
    
    total_time = time.time() - start_time
    
    # Analyze results
    total_successful = sum(r['successful'] for r in results)
    total_failed = sum(r['failed'] for r in results)
    
    logger.info(f"\nStress Test Results:")
    print(f"  Total operations: {num_threads * operations_per_thread}")
    print(f"  Successful: {total_successful}")
    print(f"  Failed: {total_failed}")
    print(f"  Total time: {total_time:.2f} seconds")
    print(f"  Operations/second: {total_successful/total_time:.2f}")
    
    # Final statistics
    stats = manager.get_pool_stats("stress_test_pool")
    print(f"\nFinal Pool Statistics: {stats}")


def main():
    """Run all examples."""
    try:
        # Example 1: SQLite file-based
        example_sqlite_file_based()
        
        # Example 2: SQLite in-memory with threading
        example_sqlite_in_memory()
        
        # Example 3: PostgreSQL (may be skipped if not available)
        example_postgresql()
        
        # Example 4: MySQL (may be skipped if not available)
        example_mysql()
        
        # Example 5: Multi-pool management
        example_multi_pool_management()
        
        # Example 6: Stress test
        example_stress_test()
        
        # Final summary
        print("\n" + "="*80)
        print("ALL EXAMPLES COMPLETED")
        print("="*80)
        
        manager = get_pool_manager()
        all_stats = manager.get_all_stats()
        print(f"\nFinal Status - {len(all_stats)} active pools:")
        for pool_name in sorted(all_stats.keys()):
            print(f"  - {pool_name}")
        
    finally:
        # Cleanup
        logger.info("\nCleaning up all pools...")
        manager = get_pool_manager()
        manager.shutdown_all()
        logger.info("Cleanup complete!")


if __name__ == "__main__":
    main()
