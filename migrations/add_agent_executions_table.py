#!/usr/bin/env python3
"""
Migration Script: Add agent_executions table and metadata column
Version: 1.4.7

This script:
1. Adds 'metadata' column to 'executions' table if not exists
2. Creates 'agent_executions' table if not exists

Run from project root: python migrations/add_agent_executions_table.py
"""

import sqlite3
import sys
from datetime import datetime

# Configuration - update this path if needed
DATABASE_PATH = 'abhikarta.db'


def run_migration(db_path: str = DATABASE_PATH):
    """Run the migration."""
    print(f"Running migration on: {db_path}")
    print(f"Migration: Add agent_executions table and metadata column")
    print("-" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Check if executions table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='executions'
        """)
        if not cursor.fetchone():
            print("Warning: executions table does not exist. Schema may need to be created first.")
            return False
        
        # 2. Check if metadata column exists in executions table
        cursor.execute("PRAGMA table_info(executions)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'metadata' not in columns:
            print("Adding 'metadata' column to 'executions' table...")
            cursor.execute("""
                ALTER TABLE executions 
                ADD COLUMN metadata TEXT DEFAULT '{}'
            """)
            print("✓ Added 'metadata' column to 'executions' table")
        else:
            print("✓ 'metadata' column already exists in 'executions' table")
        
        # 3. Create agent_executions table if not exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='agent_executions'
        """)
        
        if not cursor.fetchone():
            print("Creating 'agent_executions' table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_id TEXT UNIQUE NOT NULL,
                    agent_id TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    input_data TEXT,
                    output_data TEXT,
                    error_message TEXT,
                    duration_ms INTEGER,
                    metadata TEXT DEFAULT '{}',
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    created_by TEXT DEFAULT 'system',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
                )
            """)
            print("✓ Created 'agent_executions' table")
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_agent_executions_agent_id 
                ON agent_executions(agent_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_agent_executions_status 
                ON agent_executions(status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_agent_executions_created_at 
                ON agent_executions(created_at)
            """)
            print("✓ Created indexes for 'agent_executions' table")
        else:
            print("✓ 'agent_executions' table already exists")
        
        # 4. Update schema version
        cursor.execute("""
            INSERT INTO schema_version (version, description, applied_at)
            VALUES (?, ?, ?)
        """, (
            '1.4.7.1',
            'Added agent_executions table and metadata column to executions',
            datetime.utcnow().isoformat()
        ))
        print("✓ Updated schema version to 1.4.7.1")
        
        conn.commit()
        print("-" * 60)
        print("✓ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during migration: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        conn.close()


def run_postgres_migration(conn_string: str):
    """Run the migration for PostgreSQL."""
    try:
        import psycopg2
    except ImportError:
        print("psycopg2 not installed. Skipping PostgreSQL migration.")
        return False
    
    print(f"Running PostgreSQL migration...")
    print("-" * 60)
    
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    
    try:
        # 1. Check if metadata column exists in executions table
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'executions' AND column_name = 'metadata'
        """)
        
        if not cursor.fetchone():
            print("Adding 'metadata' column to 'executions' table...")
            cursor.execute("""
                ALTER TABLE executions 
                ADD COLUMN metadata JSONB DEFAULT '{}'
            """)
            print("✓ Added 'metadata' column to 'executions' table")
        else:
            print("✓ 'metadata' column already exists in 'executions' table")
        
        # 2. Create agent_executions table if not exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'agent_executions'
            )
        """)
        
        if not cursor.fetchone()[0]:
            print("Creating 'agent_executions' table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_executions (
                    id SERIAL PRIMARY KEY,
                    execution_id TEXT UNIQUE NOT NULL,
                    agent_id TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    input_data JSONB,
                    output_data JSONB,
                    error_message TEXT,
                    duration_ms INTEGER,
                    metadata JSONB DEFAULT '{}',
                    started_at TIMESTAMP WITH TIME ZONE,
                    completed_at TIMESTAMP WITH TIME ZONE,
                    created_by TEXT DEFAULT 'system',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
                )
            """)
            print("✓ Created 'agent_executions' table")
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_agent_executions_agent_id 
                ON agent_executions(agent_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_agent_executions_status 
                ON agent_executions(status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_agent_executions_created_at 
                ON agent_executions(created_at)
            """)
            print("✓ Created indexes for 'agent_executions' table")
        else:
            print("✓ 'agent_executions' table already exists")
        
        # 3. Update schema version
        cursor.execute("""
            INSERT INTO schema_version (version, description, applied_at)
            VALUES (%s, %s, %s)
        """, (
            '1.4.7.1',
            'Added agent_executions table and metadata column to executions',
            datetime.utcnow().isoformat()
        ))
        print("✓ Updated schema version to 1.4.7.1")
        
        conn.commit()
        print("-" * 60)
        print("✓ PostgreSQL migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during PostgreSQL migration: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    db_path = sys.argv[1] if len(sys.argv) > 1 else DATABASE_PATH
    
    # Check if it's a PostgreSQL connection string
    if db_path.startswith('postgresql://') or db_path.startswith('postgres://'):
        success = run_postgres_migration(db_path)
    else:
        success = run_migration(db_path)
    
    sys.exit(0 if success else 1)
