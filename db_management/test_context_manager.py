#!/usr/bin/env python3
"""
Test PooledConnection Context Manager Support

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

import logging
from pool_manager import get_pool_manager
from pool_config import SQLitePoolConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ContextManagerTest")

def test_pooled_connection_context_manager():
    """Test that PooledConnection works as a context manager."""
    logger.info("Testing PooledConnection as context manager...")
    
    manager = get_pool_manager()
    
    # Create pool
    config = SQLitePoolConfig(
        pool_name="test_cm",
        database_path="test_cm.db",
        min_connections=2,
        max_connections=5
    )
    manager.create_pool(config)
    
    # Create test table
    conn = manager.get_connection_from_pool("test_cm")
    with conn as connection:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test (
                id INTEGER PRIMARY KEY,
                value TEXT
            )
        """)
        connection.commit()
    # Connection automatically returned here!
    
    logger.info("✓ Created table using PooledConnection context manager")
    
    # Insert data
    conn = manager.get_connection_from_pool("test_cm")
    with conn as connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO test (value) VALUES (?)", ("test_value",))
        connection.commit()
    
    logger.info("✓ Inserted data using PooledConnection context manager")
    
    # Query data
    conn = manager.get_connection_from_pool("test_cm")
    with conn as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM test")
        result = cursor.fetchone()
        assert result[1] == "test_value", "Data mismatch!"
    
    logger.info("✓ Queried data using PooledConnection context manager")
    
    # Check stats
    stats = manager.get_pool_stats("test_cm")
    logger.info(f"✓ Pool stats: {stats}")
    assert stats['active_connections'] == 0, "Connections not returned to pool!"
    
    # Cleanup
    manager.remove_pool("test_cm", force=True)
    
    import os
    if os.path.exists("test_cm.db"):
        os.remove("test_cm.db")
    
    logger.info("✓ All context manager tests PASSED!\n")


def test_pool_context_manager():
    """Test the pool's get_connection_context method."""
    logger.info("Testing pool.get_connection_context()...")
    
    manager = get_pool_manager()
    
    config = SQLitePoolConfig(
        pool_name="test_pool_cm",
        database_path="test_pool_cm.db",
        min_connections=2,
        max_connections=5
    )
    manager.create_pool(config)
    
    # Use pool's context manager
    with manager.get_connection_context("test_pool_cm") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()[0]
        assert result == 1
    
    logger.info("✓ Pool context manager works")
    
    stats = manager.get_pool_stats("test_pool_cm")
    assert stats['active_connections'] == 0, "Connection not returned!"
    
    # Cleanup
    manager.remove_pool("test_pool_cm", force=True)
    
    import os
    if os.path.exists("test_pool_cm.db"):
        os.remove("test_pool_cm.db")
    
    logger.info("✓ Pool context manager test PASSED!\n")


def test_both_patterns():
    """Test both context manager patterns work correctly."""
    logger.info("Testing both patterns together...")
    
    manager = get_pool_manager()
    
    config = SQLitePoolConfig(
        pool_name="test_both",
        database_path="test_both.db",
        min_connections=2,
        max_connections=10
    )
    manager.create_pool(config)
    
    # Pattern 1: PooledConnection as context manager
    conn = manager.get_connection_from_pool("test_both")
    with conn as connection:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER, val TEXT)")
        connection.commit()
    
    # Pattern 2: Pool's context manager
    with manager.get_connection_context("test_both") as connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO test VALUES (1, 'hello')")
        connection.commit()
    
    # Pattern 1 again: Verify data
    conn = manager.get_connection_from_pool("test_both")
    with conn as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM test")
        result = cursor.fetchone()
        # Verify data - SQLite Row object supports indexing
        assert result[0] == 1 and result[1] == 'hello', f"Expected (1, 'hello'), got {result}"
    
    logger.info("✓ Both patterns work correctly together")
    
    stats = manager.get_pool_stats("test_both")
    logger.info(f"Final stats: {stats}")
    assert stats['active_connections'] == 0
    
    # Cleanup
    manager.remove_pool("test_both", force=True)
    import os
    if os.path.exists("test_both.db"):
        os.remove("test_both.db")
    
    logger.info("✓ Both patterns test PASSED!\n")


if __name__ == "__main__":
    try:
        logger.info("="*60)
        logger.info("CONTEXT MANAGER SUPPORT TESTS")
        logger.info("="*60 + "\n")
        
        test_pooled_connection_context_manager()
        test_pool_context_manager()
        test_both_patterns()
        
        logger.info("="*60)
        logger.info("ALL CONTEXT MANAGER TESTS PASSED!")
        logger.info("="*60)
        logger.info("\nThe PooledConnection context manager fix is working correctly!")
        
    finally:
        manager = get_pool_manager()
        manager.shutdown_all()
