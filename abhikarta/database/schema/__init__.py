"""
Database Schema Module - SQL schema definitions for different database backends.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.

Patent Pending: Certain architectural patterns and implementations described in this
software may be subject to patent applications.
"""

from .sqlite_schema import SQLiteSchema
from .postgres_schema import PostgresSchema

__all__ = ['SQLiteSchema', 'PostgresSchema']


def get_schema(db_type: str):
    """
    Get the appropriate schema class for the database type.
    
    Args:
        db_type: Database type ('sqlite' or 'postgresql')
        
    Returns:
        Schema class instance
    """
    if db_type.lower() == 'sqlite':
        return SQLiteSchema()
    elif db_type.lower() in ('postgresql', 'postgres'):
        return PostgresSchema()
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
