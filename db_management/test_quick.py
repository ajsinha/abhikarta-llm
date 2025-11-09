#!/usr/bin/env python3
"""
Quick Test Script for Database Connection Pool Manager

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
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("QuickTest")


def test_basic_functionality():
    """Test basic pool manager functionality."""
    from pool_manager import get_pool_manager
    from pool_config import SQLitePoolConfig
    
    logger.info("="*60)
    logger.info("TEST 1: Basic Functionality")
    logger.info("="*60)
    
    manager = get_pool_manager()
    
    # Create pool (using file-based for better connection pool compatibility)
    config = SQLitePoolConfig(
        pool_name="test_pool",
        database_path="test_pool.db",
        min_connections=2,
        max_connections=5
    )
    manager.create_pool(config)
    logger.info("✓ Pool created successfully")
    
    # Create table
    with manager.get_connection_context("test_pool") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                value TEXT
            )
        """)
        conn.commit()
    logger.info("✓ Table created successfully")
    
    # Insert data
    with manager.get_connection_context("test_pool") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO test_table (value) VALUES (?)", ("test_value",))
        conn.commit()
    logger.info("✓ Data inserted successfully")
    
    # Query data
    with manager.get_connection_context("test_pool") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM test_table")
        result = cursor.fetchone()
        assert result[1] == "test_value", "Data mismatch!"
    logger.info("✓ Data queried successfully")
    
    # Check stats
    stats = manager.get_pool_stats("test_pool")
    logger.info(f"✓ Pool stats: {stats}")
    
    logger.info("✓ TEST 1 PASSED\n")


def test_multi_threading():
    """Test thread safety with concurrent operations."""
    from pool_manager import get_pool_manager
    from pool_config import SQLitePoolConfig
    
    logger.info("="*60)
    logger.info("TEST 2: Multi-Threading")
    logger.info("="*60)
    
    manager = get_pool_manager()
    
    # Create pool (using file-based for thread safety)
    config = SQLitePoolConfig(
        pool_name="thread_test_pool",
        database_path="thread_test.db",
        min_connections=3,
        max_connections=10
    )
    manager.create_pool(config)
    
    # Create table
    with manager.get_connection_context("thread_test_pool") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE thread_test (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id INTEGER,
                value TEXT
            )
        """)
        conn.commit()
    logger.info("✓ Test table created")
    
    # Concurrent insert function
    def insert_data(thread_id, count):
        for i in range(count):
            with manager.get_connection_context("thread_test_pool") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO thread_test (thread_id, value) VALUES (?, ?)",
                    (thread_id, f"value-{i}")
                )
                conn.commit()
        return f"Thread {thread_id} completed"
    
    # Run concurrent operations
    num_threads = 10
    operations_per_thread = 10
    logger.info(f"Running {num_threads} threads with {operations_per_thread} operations each")
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(insert_data, tid, operations_per_thread)
            for tid in range(num_threads)
        ]
        
        for future in as_completed(futures):
            logger.debug(future.result())
    
    # Verify results
    with manager.get_connection_context("thread_test_pool") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM thread_test")
        count = cursor.fetchone()[0]
        expected = num_threads * operations_per_thread
        assert count == expected, f"Expected {expected} rows, got {count}"
    
    logger.info(f"✓ All {count} operations completed successfully")
    
    stats = manager.get_pool_stats("thread_test_pool")
    logger.info(f"✓ Final pool stats: {stats}")
    
    logger.info("✓ TEST 2 PASSED\n")


def test_multiple_pools():
    """Test managing multiple pools simultaneously."""
    from pool_manager import get_pool_manager
    from pool_config import SQLitePoolConfig
    
    logger.info("="*60)
    logger.info("TEST 3: Multiple Pools")
    logger.info("="*60)
    
    manager = get_pool_manager()
    
    # Create multiple pools with unique database files
    pool_names = ["pool_1", "pool_2", "pool_3"]
    for i, pool_name in enumerate(pool_names):
        config = SQLitePoolConfig(
            pool_name=pool_name,
            database_path=f"test_{pool_name}.db",
            min_connections=1,
            max_connections=5
        )
        manager.create_pool(config)
        logger.info(f"✓ Created {pool_name}")
    
    # Use each pool
    for pool_name in pool_names:
        with manager.get_connection_context(pool_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()[0]
            assert result == 1
    
    logger.info("✓ All pools accessible")
    
    # Check all stats
    all_stats = manager.get_all_stats()
    logger.info(f"✓ Managing {len(all_stats)} pools")
    
    # Remove pools
    for pool_name in pool_names:
        manager.remove_pool(pool_name, force=True)
        logger.info(f"✓ Removed {pool_name}")
    
    logger.info("✓ TEST 3 PASSED\n")


def main():
    """Run all tests."""
    try:
        logger.info("Starting Database Connection Pool Manager Tests\n")
        
        # Run tests
        test_basic_functionality()
        test_multi_threading()
        test_multiple_pools()
        
        # Summary
        logger.info("="*60)
        logger.info("ALL TESTS PASSED!")
        logger.info("="*60)
        logger.info("\nThe Database Connection Pool Manager is working correctly.")
        logger.info("You can now run the full examples with: python examples.py")
        
        return 0
        
    except Exception as e:
        logger.error(f"\n{'='*60}")
        logger.error(f"TEST FAILED: {e}")
        logger.error(f"{'='*60}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        # Cleanup
        from pool_manager import get_pool_manager
        import os
        
        manager = get_pool_manager()
        manager.shutdown_all()
        
        # Remove test database files
        test_files = ["test_pool.db", "thread_test.db", 
                     "test_pool_1.db", "test_pool_2.db", "test_pool_3.db"]
        for file in test_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    logger.debug(f"Removed {file}")
                except Exception as e:
                    logger.warning(f"Could not remove {file}: {e}")
        
        logger.info("\nCleanup complete!")


if __name__ == "__main__":
    sys.exit(main())
