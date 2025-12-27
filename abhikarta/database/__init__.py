"""
Database Module - Database abstraction layer.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.

Patent Pending: Certain architectural patterns and implementations described in this
software may be subject to patent applications.
"""

from .db_facade import DatabaseFacade, DatabaseHandler
from .schema import SQLiteSchema, PostgresSchema, get_schema

__all__ = [
    'DatabaseFacade', 
    'DatabaseHandler',
    'SQLiteSchema',
    'PostgresSchema',
    'get_schema'
]
