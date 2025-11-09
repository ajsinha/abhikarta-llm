"""
SQLite Database Schema Initializer - Reads schema.sql and creates SQLite database.

This script reads the PostgreSQL schema.sql file and adapts it for SQLite,
then creates and initializes a SQLite database with the schema.

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

import sqlite3
import re
import logging
import os
import sys
from typing import List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SQLiteSchemaAdapter:
    """
    Adapter to convert PostgreSQL schema to SQLite-compatible schema.
    
    Handles the following conversions:
    - JSONB → TEXT
    - VARCHAR(n) → TEXT
    - BOOLEAN → INTEGER
    - Removes CASCADE from DROP TABLE
    - Removes COMMENT ON statements
    - Adapts CHECK constraints
    - Handles foreign key syntax
    """
    
    @staticmethod
    def adapt_sql_for_sqlite(sql: str) -> str:
        """
        Adapt PostgreSQL SQL to SQLite-compatible SQL.
        
        Args:
            sql: PostgreSQL SQL statement
            
        Returns:
            SQLite-compatible SQL statement
        """
        # Remove comments (-- style and /* */ style)
        # Keep them for now to preserve documentation
        
        # Replace JSONB with TEXT
        sql = re.sub(r'\bJSONB\b', 'TEXT', sql, flags=re.IGNORECASE)
        
        # Replace VARCHAR(n) with TEXT
        sql = re.sub(r'\bVARCHAR\s*\(\d+\)', 'TEXT', sql, flags=re.IGNORECASE)
        
        # Replace BOOLEAN with INTEGER
        sql = re.sub(r'\bBOOLEAN\b', 'INTEGER', sql, flags=re.IGNORECASE)
        
        # Replace TRUE with 1 and FALSE with 0
        sql = re.sub(r'\bTRUE\b', '1', sql, flags=re.IGNORECASE)
        sql = re.sub(r'\bFALSE\b', '0', sql, flags=re.IGNORECASE)
        
        # Remove CASCADE from DROP TABLE
        sql = re.sub(r'DROP\s+TABLE\s+IF\s+EXISTS\s+(\w+)\s+CASCADE',
                    r'DROP TABLE IF EXISTS \1', sql, flags=re.IGNORECASE)
        
        # Handle DEFAULT CURRENT_TIMESTAMP (already compatible)
        # SQLite uses CURRENT_TIMESTAMP the same way
        
        # Remove PostgreSQL-specific :: casting for JSONB and TEXT
        # This handles both simple strings and complex JSON structures
        # Pattern: '<anything>'::TYPE -> '<anything>'
        sql = re.sub(r"::(?:JSONB|TEXT|JSON)\b", '', sql, flags=re.IGNORECASE)
        
        return sql
    
    @staticmethod
    def extract_statements(sql_content: str) -> List[str]:
        """
        Extract individual SQL statements from the schema file.
        
        Args:
            sql_content: Complete SQL file content
            
        Returns:
            List of individual SQL statements
        """
        statements = []
        current_statement = []
        in_comment_block = False
        
        for line in sql_content.split('\n'):
            stripped = line.strip()
            
            # Handle multi-line comment blocks
            if '/*' in stripped:
                in_comment_block = True
            if '*/' in stripped:
                in_comment_block = False
                continue
            
            # Skip comment lines and empty lines
            if in_comment_block or not stripped or stripped.startswith('--'):
                continue
            
            # Skip COMMENT ON statements (not supported by SQLite)
            if stripped.upper().startswith('COMMENT ON'):
                # Skip until we find a semicolon
                if ';' not in stripped:
                    while True:
                        continue
                continue
            
            current_statement.append(line)
            
            # Check if statement is complete (ends with semicolon)
            if ';' in line:
                statement = '\n'.join(current_statement)
                if statement.strip():
                    statements.append(statement)
                current_statement = []
        
        # Add any remaining statement
        if current_statement:
            statement = '\n'.join(current_statement)
            if statement.strip():
                statements.append(statement)
        
        return statements
    
    @staticmethod
    def filter_sqlite_incompatible(statements: List[str]) -> List[str]:
        """
        Filter out statements that are not compatible with SQLite.
        
        Args:
            statements: List of SQL statements
            
        Returns:
            Filtered list of SQLite-compatible statements
        """
        filtered = []
        skip_next = False
        
        for stmt in statements:
            stmt_upper = stmt.upper().strip()
            
            # Skip COMMENT ON statements
            if stmt_upper.startswith('COMMENT ON'):
                continue
            
            # Skip PostgreSQL-specific commands
            if any(cmd in stmt_upper for cmd in ['ALTER DATABASE', 'CREATE EXTENSION']):
                continue
            
            filtered.append(stmt)
        
        return filtered


class SQLiteSchemaInitializer:
    """
    Initializer for SQLite database schema.
    
    Reads the schema.sql file, adapts it for SQLite, and creates the database.
    """
    
    def __init__(self, schema_file: str = 'schema.sql', db_file: str = 'abhikarta.db_management'):
        """
        Initialize the schema initializer.
        
        Args:
            schema_file: Path to the PostgreSQL schema.sql file
            db_file: Path to the SQLite database file to create
        """
        self.schema_file = schema_file
        self.db_file = db_file
        self.adapter = SQLiteSchemaAdapter()
        self.connection: Optional[sqlite3.Connection] = None
        
        logger.info(f"Initialized SQLiteSchemaInitializer")
        logger.info(f"Schema file: {schema_file}")
        logger.info(f"Database file: {db_file}")
    
    def read_schema_file(self) -> str:
        """
        Read the schema.sql file.
        
        Returns:
            Content of the schema file
            
        Raises:
            FileNotFoundError: If schema file doesn't exist
        """
        if not os.path.exists(self.schema_file):
            raise FileNotFoundError(f"Schema file not found: {self.schema_file}")
        
        with open(self.schema_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"Read schema file: {len(content)} bytes")
        return content
    
    def create_database(self, overwrite: bool = False) -> None:
        """
        Create the SQLite database.
        
        Args:
            overwrite: If True, delete existing database file
            
        Raises:
            FileExistsError: If database exists and overwrite is False
        """
        if os.path.exists(self.db_file):
            if overwrite:
                os.remove(self.db_file)
                logger.info(f"Removed existing database: {self.db_file}")
            else:
                raise FileExistsError(
                    f"Database file already exists: {self.db_file}. "
                    f"Use overwrite=True to replace it."
                )
        
        # Create connection
        self.connection = sqlite3.connect(self.db_file)
        
        # Enable foreign key support (not enabled by default in SQLite)
        self.connection.execute("PRAGMA foreign_keys = ON")
        
        logger.info(f"Created SQLite database: {self.db_file}")
    
    def execute_schema(self, sql_content: str) -> None:
        """
        Execute the schema SQL on the SQLite database.
        
        Args:
            sql_content: SQL schema content
        """
        if not self.connection:
            raise RuntimeError("Database connection not established")
        
        # Extract statements
        statements = self.adapter.extract_statements(sql_content)
        logger.info(f"Extracted {len(statements)} SQL statements")
        
        # Filter incompatible statements
        statements = self.adapter.filter_sqlite_incompatible(statements)
        logger.info(f"Filtered to {len(statements)} SQLite-compatible statements")
        
        # Execute each statement
        cursor = self.connection.cursor()
        executed = 0
        skipped = 0
        
        for i, statement in enumerate(statements, 1):
            try:
                # Adapt the statement for SQLite
                adapted_stmt = self.adapter.adapt_sql_for_sqlite(statement)
                
                # Skip empty statements
                if not adapted_stmt.strip():
                    continue
                
                # Execute the statement
                cursor.execute(adapted_stmt)
                executed += 1
                
                # Log progress for major statements
                stmt_preview = adapted_stmt.strip()[:60]
                if any(keyword in stmt_preview.upper() 
                       for keyword in ['CREATE TABLE', 'INSERT INTO', 'CREATE INDEX']):
                    logger.debug(f"Executed ({i}/{len(statements)}): {stmt_preview}...")
                
            except sqlite3.Error as e:
                # Log error but continue
                logger.warning(f"Error executing statement {i}: {e}")
                logger.debug(f"Statement: {adapted_stmt[:200]}...")
                skipped += 1
                
                # Decide whether to continue or stop
                if "syntax error" in str(e).lower():
                    logger.error("Syntax error encountered, stopping execution")
                    raise
        
        # Commit all changes
        self.connection.commit()
        
        logger.info(f"Schema execution complete: {executed} executed, {skipped} skipped")
    
    def verify_schema(self) -> bool:
        """
        Verify that the schema was created correctly.
        
        Returns:
            True if schema is valid, False otherwise
        """
        if not self.connection:
            return False
        
        cursor = self.connection.cursor()
        
        # Check that main tables exist
        expected_tables = ['users', 'roles', 'resources', 'user_roles', 'role_resources']
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        logger.info(f"Existing tables: {existing_tables}")
        
        # Verify expected tables
        missing_tables = [t for t in expected_tables if t not in existing_tables]
        
        if missing_tables:
            logger.error(f"Missing tables: {missing_tables}")
            return False
        
        # Check admin user exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE userid = 'admin'")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            logger.error("Admin user not found")
            return False
        
        # Check admin role exists
        cursor.execute("SELECT COUNT(*) FROM roles WHERE role_name = 'admin'")
        admin_role_count = cursor.fetchone()[0]
        
        if admin_role_count == 0:
            logger.error("Admin role not found")
            return False
        
        logger.info("Schema verification passed")
        return True
    
    def get_statistics(self) -> dict:
        """
        Get statistics about the created database.
        
        Returns:
            Dictionary with table counts
        """
        if not self.connection:
            return {}
        
        cursor = self.connection.cursor()
        stats = {}
        
        tables = ['users', 'roles', 'resources', 'user_roles', 'role_resources']
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[table] = count
            except sqlite3.Error:
                stats[table] = 0
        
        return stats
    
    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def initialize(self, overwrite: bool = False) -> bool:
        """
        Complete initialization process.
        
        Args:
            overwrite: If True, overwrite existing database
            
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Read schema file
            logger.info("Step 1: Reading schema file...")
            sql_content = self.read_schema_file()
            
            # Create database
            logger.info("Step 2: Creating SQLite database...")
            self.create_database(overwrite=overwrite)
            
            # Execute schema
            logger.info("Step 3: Executing schema...")
            self.execute_schema(sql_content)
            
            # Verify schema
            logger.info("Step 4: Verifying schema...")
            if not self.verify_schema():
                logger.error("Schema verification failed")
                return False
            
            # Get statistics
            logger.info("Step 5: Getting statistics...")
            stats = self.get_statistics()
            logger.info(f"Database statistics: {stats}")
            
            logger.info("=" * 70)
            logger.info("SQLite database initialization completed successfully!")
            logger.info(f"Database file: {os.path.abspath(self.db_file)}")
            logger.info(f"Tables created: {len(stats)}")
            logger.info(f"Users: {stats.get('users', 0)}")
            logger.info(f"Roles: {stats.get('roles', 0)}")
            logger.info(f"Resources: {stats.get('resources', 0)}")
            logger.info("=" * 70)
            
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}", exc_info=True)
            return False


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Initialize SQLite database from schema.sql',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create database using default names
  python create_sqlite_db.py
  
  # Create database with custom names
  python create_sqlite_db.py --schema my_schema.sql --database my_db.db_management
  
  # Overwrite existing database
  python create_sqlite_db.py --overwrite
  
  # Verbose output
  python create_sqlite_db.py --verbose
        """
    )
    
    parser.add_argument(
        '--schema',
        default='schema.sql',
        help='Path to schema.sql file (default: schema.sql)'
    )
    
    parser.add_argument(
        '--database',
        default='abhikarta.db_management',
        help='Path to SQLite database file (default: abhikarta.db_management)'
    )
    
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing database if it exists'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose (DEBUG) logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Print header
    print()
    print("=" * 70)
    print("SQLite Database Schema Initializer")
    print("Abhikarta LLM User Management System")
    print("=" * 70)
    print()
    
    # Initialize
    initializer = SQLiteSchemaInitializer(
        schema_file=args.schema,
        db_file=args.database
    )
    
    try:
        success = initializer.initialize(overwrite=args.overwrite)
        
        if success:
            print()
            print("✅ Database initialization successful!")
            print(f"📁 Database file: {os.path.abspath(args.database)}")
            print()
            print("You can now use this database with UserManagerDB:")
            print()
            print("  from user_manager_db import UserManagerDB")
            print("  import sqlite3")
            print()
            print("  # Create a simple connection wrapper")
            print(f"  conn = sqlite3.connect('{args.database}')")
            print("  manager = UserManagerDB(conn, db_type='sqlite')")
            print("  manager.initialize()")
            print()
            return 0
        else:
            print()
            print("❌ Database initialization failed!")
            print("   Check the logs above for details.")
            print()
            return 1
            
    except FileExistsError as e:
        print()
        print(f"❌ Error: {e}")
        print("   Use --overwrite flag to replace existing database.")
        print()
        return 1
        
    except FileNotFoundError as e:
        print()
        print(f"❌ Error: {e}")
        print(f"   Make sure {args.schema} exists in the current directory.")
        print()
        return 1
        
    except Exception as e:
        print()
        print(f"❌ Unexpected error: {e}")
        print("   See logs for details.")
        print()
        return 1
        
    finally:
        initializer.close()


if __name__ == "__main__":
    sys.exit(main())
