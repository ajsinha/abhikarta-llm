"""
Migration: Update swarm_executions table schema

This migration updates the swarm_executions table to use consistent column names:
- start_time -> started_at
- end_time -> completed_at  
- duration_seconds -> duration_ms
- Adds created_at if missing (removed in favor of started_at)

Version: 1.5.2
Copyright © 2025-2030, All Rights Reserved
"""

import logging
import sqlite3
from datetime import datetime

logger = logging.getLogger(__name__)


def migrate_sqlite(db_path: str) -> bool:
    """
    Migrate SQLite database schema for swarm_executions.
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        True if migration successful, False otherwise
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='swarm_executions'"
        )
        if not cursor.fetchone():
            logger.info("swarm_executions table does not exist, skipping migration")
            conn.close()
            return True
        
        # Get current columns
        cursor.execute("PRAGMA table_info(swarm_executions)")
        columns = {row[1]: row for row in cursor.fetchall()}
        column_names = set(columns.keys())
        
        logger.info(f"Current swarm_executions columns: {column_names}")
        
        # Check if migration is needed
        needs_migration = (
            'start_time' in column_names or 
            'end_time' in column_names or
            'duration_seconds' in column_names
        )
        
        if not needs_migration and 'started_at' in column_names:
            logger.info("swarm_executions schema already up to date")
            conn.close()
            return True
        
        logger.info("Migrating swarm_executions table schema...")
        
        # SQLite doesn't support RENAME COLUMN in older versions,
        # so we need to recreate the table
        
        # 1. Create new table with correct schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS swarm_executions_new (
                execution_id TEXT PRIMARY KEY,
                swarm_id TEXT NOT NULL,
                correlation_id TEXT,
                trigger_type TEXT,
                trigger_id TEXT,
                trigger_data TEXT,
                status TEXT DEFAULT 'pending',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                duration_ms INTEGER,
                result_json TEXT,
                error_message TEXT,
                events_processed INTEGER DEFAULT 0,
                agents_used INTEGER DEFAULT 0,
                iterations INTEGER DEFAULT 0,
                user_id TEXT,
                FOREIGN KEY (swarm_id) REFERENCES swarms(swarm_id)
            )
        """)
        
        # 2. Copy data from old table, mapping old columns to new
        # Build column mapping
        old_to_new = {
            'execution_id': 'execution_id',
            'swarm_id': 'swarm_id',
            'correlation_id': 'correlation_id',
            'trigger_type': 'trigger_type',
            'trigger_id': 'trigger_id',
            'trigger_data': 'trigger_data',
            'status': 'status',
            'start_time': 'started_at',
            'started_at': 'started_at',
            'end_time': 'completed_at',
            'completed_at': 'completed_at',
            'duration_seconds': 'duration_ms',  # Will need conversion
            'duration_ms': 'duration_ms',
            'result_json': 'result_json',
            'error_message': 'error_message',
            'events_processed': 'events_processed',
            'agents_used': 'agents_used',
            'iterations': 'iterations',
            'user_id': 'user_id',
            'created_at': 'started_at',  # Map old created_at to started_at
        }
        
        # Build SELECT statement for copying data
        select_cols = []
        insert_cols = []
        
        for old_col in column_names:
            new_col = old_to_new.get(old_col)
            if new_col and new_col not in insert_cols:
                if old_col == 'duration_seconds':
                    # Convert seconds to milliseconds
                    select_cols.append(f"CAST({old_col} * 1000 AS INTEGER)")
                else:
                    select_cols.append(old_col)
                insert_cols.append(new_col)
        
        if select_cols:
            insert_sql = f"""
                INSERT INTO swarm_executions_new ({', '.join(insert_cols)})
                SELECT {', '.join(select_cols)} FROM swarm_executions
            """
            cursor.execute(insert_sql)
            logger.info(f"Copied {cursor.rowcount} rows to new table")
        
        # 3. Drop old table
        cursor.execute("DROP TABLE swarm_executions")
        
        # 4. Rename new table
        cursor.execute("ALTER TABLE swarm_executions_new RENAME TO swarm_executions")
        
        # 5. Recreate indexes
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_swarm_executions_swarm ON swarm_executions(swarm_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_swarm_executions_status ON swarm_executions(status)"
        )
        
        conn.commit()
        conn.close()
        
        logger.info("swarm_executions schema migration completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        return False


def migrate_postgres(connection_string: str) -> bool:
    """
    Migrate PostgreSQL database schema for swarm_executions.
    
    PostgreSQL supports ALTER TABLE RENAME COLUMN, so this is simpler.
    
    Args:
        connection_string: PostgreSQL connection string
        
    Returns:
        True if migration successful, False otherwise
    """
    try:
        import psycopg2
        
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'swarm_executions'
            )
        """)
        if not cursor.fetchone()[0]:
            logger.info("swarm_executions table does not exist, skipping migration")
            conn.close()
            return True
        
        # Get current columns
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'swarm_executions'
        """)
        column_names = {row[0] for row in cursor.fetchall()}
        
        logger.info(f"Current swarm_executions columns: {column_names}")
        
        # Rename columns if needed
        if 'start_time' in column_names:
            cursor.execute(
                "ALTER TABLE swarm_executions RENAME COLUMN start_time TO started_at"
            )
            logger.info("Renamed start_time -> started_at")
        
        if 'end_time' in column_names:
            cursor.execute(
                "ALTER TABLE swarm_executions RENAME COLUMN end_time TO completed_at"
            )
            logger.info("Renamed end_time -> completed_at")
        
        if 'duration_seconds' in column_names:
            # Add new column, copy data, drop old column
            cursor.execute(
                "ALTER TABLE swarm_executions ADD COLUMN IF NOT EXISTS duration_ms INTEGER"
            )
            cursor.execute(
                "UPDATE swarm_executions SET duration_ms = CAST(duration_seconds * 1000 AS INTEGER)"
            )
            cursor.execute(
                "ALTER TABLE swarm_executions DROP COLUMN duration_seconds"
            )
            logger.info("Converted duration_seconds -> duration_ms")
        
        # Add missing columns
        if 'started_at' not in column_names and 'start_time' not in column_names:
            cursor.execute("""
                ALTER TABLE swarm_executions 
                ADD COLUMN IF NOT EXISTS started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            """)
        
        if 'completed_at' not in column_names and 'end_time' not in column_names:
            cursor.execute("""
                ALTER TABLE swarm_executions 
                ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP WITH TIME ZONE
            """)
        
        if 'duration_ms' not in column_names and 'duration_seconds' not in column_names:
            cursor.execute("""
                ALTER TABLE swarm_executions 
                ADD COLUMN IF NOT EXISTS duration_ms INTEGER
            """)
        
        conn.commit()
        conn.close()
        
        logger.info("swarm_executions schema migration completed successfully")
        return True
        
    except ImportError:
        logger.warning("psycopg2 not installed, skipping PostgreSQL migration")
        return True
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        return False


def run_migration(db_facade=None, db_path: str = None, connection_string: str = None):
    """
    Run the migration using either a db_facade or direct connection parameters.
    
    Args:
        db_facade: Optional database facade instance
        db_path: Optional SQLite database path
        connection_string: Optional PostgreSQL connection string
    """
    if db_facade:
        # Determine database type from facade
        db_type = getattr(db_facade, 'db_type', 'sqlite')
        
        if db_type == 'sqlite':
            db_path = getattr(db_facade, 'db_path', None)
            if db_path:
                return migrate_sqlite(db_path)
        elif db_type == 'postgres':
            conn_str = getattr(db_facade, 'connection_string', None)
            if conn_str:
                return migrate_postgres(conn_str)
    
    if db_path:
        return migrate_sqlite(db_path)
    
    if connection_string:
        return migrate_postgres(connection_string)
    
    logger.warning("No database connection provided for migration")
    return False


if __name__ == '__main__':
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
        success = migrate_sqlite(db_path)
        sys.exit(0 if success else 1)
    else:
        print("Usage: python update_swarm_executions_schema.py <database_path>")
        sys.exit(1)
