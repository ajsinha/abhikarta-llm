"""
Role Management Database Module - Database-backed role management implementation.

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

import json
import logging
import threading
from contextlib import contextmanager
from typing import List, Optional, Dict, Any

from db_management.pool_manager import get_pool_manager
from user_management.user import Role, Permission

logger = logging.getLogger(__name__)


class RoleManagementDB:
    """
    Database-backed implementation for Role Management.

    This implementation provides CRUD operations for roles and role-resource
    mappings stored in a relational database. Supports multiple database types
    (PostgreSQL, MySQL, SQLite) through a connection pool manager.

    Features:
    - Transaction support for data consistency
    - Connection pooling for performance
    - Thread-safe operations
    - Cascading deletions for role-resource mappings
    - Permission management (CRUD + Execute)
    """

    def __init__(self, db_connection_pool_name: str):
        """
        Initialize the database-backed role manager.

        Args:
            db_connection_pool_name: Database connection pool name
        """
        self._db_connection_pool_name = db_connection_pool_name
        self._connection_pool_manager = get_pool_manager()
        self._lock = threading.RLock()
        logger.info(f"RoleManagementDB initialized with {db_connection_pool_name} connection pool")

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections with auto-commit."""
        with self._connection_pool_manager.get_connection_context(self._db_connection_pool_name) as conn:
            try:
                yield conn  # Yields the actual connection
                conn.commit()  # Auto-commit on success
            except Exception as e:
                conn.rollback()  # Auto-rollback on error
                logger.error(f"Database error: {e}")
                raise

    @contextmanager
    def _get_cursor(self, conn):
        """Context manager for database cursors."""
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    # ==================== Role CRUD Operations ====================

    def save_role(self, role: Role) -> bool:
        """
        Save a role to the database (insert or update).

        Args:
            role: Role object to save

        Returns:
            True if save successful, False otherwise
        """
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:

                        if self.role_exists(role.name):
                            # Update existing role
                            cursor.execute("""
                                UPDATE roles 
                                SET description = ?, enabled = ?, metadata = ?
                                WHERE role_name = ?
                            """, (
                                role.description,
                                role.enabled,
                                json.dumps(role.metadata),
                                role.name
                            ))

                            # Update role_resources - delete old and insert new
                            cursor.execute("DELETE FROM role_resources WHERE role_name = ?", (role.name,))

                            for resource_name, permission in role.resources.items():
                                cursor.execute("""
                                    INSERT INTO role_resources 
                                    (role_name, resource_name, can_create, can_read, 
                                     can_update, can_delete, can_execute)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    role.name, resource_name,
                                    permission.create, permission.read,
                                    permission.update, permission.delete,
                                    permission.execute
                                ))
                        else:
                            # Insert new role
                            cursor.execute("""
                                INSERT INTO roles 
                                (role_name, description, enabled, created_at, metadata)
                                VALUES (?, ?, ?, ?, ?)
                            """, (
                                role.name,
                                role.description,
                                role.enabled,
                                role.created_at,
                                json.dumps(role.metadata)
                            ))

                            # Insert role_resources
                            for resource_name, permission in role.resources.items():
                                cursor.execute("""
                                    INSERT INTO role_resources 
                                    (role_name, resource_name, can_create, can_read, 
                                     can_update, can_delete, can_execute)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    role.name, resource_name,
                                    permission.create, permission.read,
                                    permission.update, permission.delete,
                                    permission.execute
                                ))

                        logger.info(f"Saved role '{role.name}'")
                        return True
            except Exception as e:
                logger.error(f"Failed to save role '{role.name}': {e}")
                return False

    def load_role(self, role_name: str) -> Optional[Role]:
        """
        Load a role from the database.

        Args:
            role_name: Name of the role to load

        Returns:
            Role object if found, None otherwise
        """
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:

                        # Load role
                        cursor.execute("""
                            SELECT role_name, description, enabled, created_at, metadata
                            FROM roles WHERE role_name = ?
                        """, (role_name,))

                        row = cursor.fetchone()
                        if not row:
                            return None

                        # Load role_resources
                        cursor.execute("""
                            SELECT resource_name, can_create, can_read, can_update, 
                                   can_delete, can_execute
                            FROM role_resources WHERE role_name = ?
                        """, (role_name,))

                        resources = {}
                        for res_row in cursor.fetchall():
                            permission = Permission(
                                create=bool(res_row[1]),
                                read=bool(res_row[2]),
                                update=bool(res_row[3]),
                                delete=bool(res_row[4]),
                                execute=bool(res_row[5])
                            )
                            resources[res_row[0]] = permission

                        # Create role object
                        role = Role(
                            name=row[0],
                            description=row[1],
                            resources=resources,
                            enabled=bool(row[2]),
                            created_at=row[3],
                            metadata=json.loads(row[4]) if row[4] else {}
                        )

                        return role
            except Exception as e:
                logger.error(f"Failed to load role '{role_name}': {e}")
                return None

    def delete_role(self, role_name: str) -> bool:
        """
        Delete a role from the database.

        Args:
            role_name: Name of the role to delete

        Returns:
            True if delete successful, False otherwise
        """
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:

                        # Check if this is the admin role
                        if role_name.lower() == 'admin':
                            logger.warning("Cannot delete system admin role")
                            return False

                        # Delete role_resources first (cascading)
                        cursor.execute("DELETE FROM role_resources WHERE role_name = ?", (role_name,))

                        # Delete user_roles associations
                        cursor.execute("DELETE FROM user_roles WHERE role_name = ?", (role_name,))

                        # Delete role
                        cursor.execute("DELETE FROM roles WHERE role_name = ?", (role_name,))

                        deleted = cursor.rowcount > 0

                        if deleted:
                            logger.info(f"Deleted role '{role_name}'")
                        return deleted
            except Exception as e:
                logger.error(f"Failed to delete role '{role_name}': {e}")
                return False

    def role_exists(self, role_name: str) -> bool:
        """
        Check if a role exists in the database.

        Args:
            role_name: Name of the role to check

        Returns:
            True if role exists, False otherwise
        """
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("SELECT 1 FROM roles WHERE role_name = ?", (role_name,))
                    exists = cursor.fetchone() is not None
                    return exists
        except Exception as e:
            logger.error(f"Failed to check role existence '{role_name}': {e}")
            return False

    def list_roles(self, enabled_only: bool = False) -> List[Role]:
        """
        List all roles from the database.

        Args:
            enabled_only: If True, return only enabled roles

        Returns:
            List of Role objects
        """
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:

                        if enabled_only:
                            cursor.execute("""
                                SELECT role_name FROM roles 
                                WHERE enabled = 1 ORDER BY role_name
                            """)
                        else:
                            cursor.execute("""
                                SELECT role_name FROM roles ORDER BY role_name
                            """)

                        role_names = [row[0] for row in cursor.fetchall()]

                        roles = []
                        for role_name in role_names:
                            role = self.load_role(role_name)
                            if role:
                                roles.append(role)

                        return roles
            except Exception as e:
                logger.error(f"Failed to list roles: {e}")
                return []

    # ==================== Resource Permission Operations ====================

    def add_resource_to_role(self, role_name: str, resource_name: str,
                             permission: Permission) -> bool:
        """
        Add a resource with permissions to a role.

        Args:
            role_name: Name of the role
            resource_name: Name of the resource
            permission: Permission object

        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:

                        # Check if role exists
                        if not self.role_exists(role_name):
                            logger.error(f"Role '{role_name}' does not exist")
                            return False

                        # Check if resource permission already exists
                        cursor.execute("""
                            SELECT 1 FROM role_resources 
                            WHERE role_name = ? AND resource_name = ?
                        """, (role_name, resource_name))

                        if cursor.fetchone():
                            # Update existing permission
                            cursor.execute("""
                                UPDATE role_resources 
                                SET can_create = ?, can_read = ?, can_update = ?,
                                    can_delete = ?, can_execute = ?
                                WHERE role_name = ? AND resource_name = ?
                            """, (
                                permission.create, permission.read, permission.update,
                                permission.delete, permission.execute,
                                role_name, resource_name
                            ))
                        else:
                            # Insert new permission
                            cursor.execute("""
                                INSERT INTO role_resources 
                                (role_name, resource_name, can_create, can_read,
                                 can_update, can_delete, can_execute)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (
                                role_name, resource_name,
                                permission.create, permission.read, permission.update,
                                permission.delete, permission.execute
                            ))

                        logger.info(f"Added resource '{resource_name}' to role '{role_name}'")
                        return True
            except Exception as e:
                logger.error(f"Failed to add resource '{resource_name}' to role '{role_name}': {e}")
                return False

    def remove_resource_from_role(self, role_name: str, resource_name: str) -> bool:
        """
        Remove a resource from a role.

        Args:
            role_name: Name of the role
            resource_name: Name of the resource

        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:
                        cursor.execute("""
                            DELETE FROM role_resources 
                            WHERE role_name = ? AND resource_name = ?
                        """, (role_name, resource_name))

                        removed = cursor.rowcount > 0

                        if removed:
                            logger.info(f"Removed resource '{resource_name}' from role '{role_name}'")
                        return removed
            except Exception as e:
                logger.error(f"Failed to remove resource '{resource_name}' from role '{role_name}': {e}")
                return False

    def get_role_resources(self, role_name: str) -> Dict[str, Permission]:
        """
        Get all resources and permissions for a role.

        Args:
            role_name: Name of the role

        Returns:
            Dictionary mapping resource names to permissions
        """
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        SELECT resource_name, can_create, can_read, can_update,
                               can_delete, can_execute
                        FROM role_resources WHERE role_name = ?
                    """, (role_name,))

                    resources = {}
                    for row in cursor.fetchall():
                        permission = Permission(
                            create=bool(row[1]),
                            read=bool(row[2]),
                            update=bool(row[3]),
                            delete=bool(row[4]),
                            execute=bool(row[5])
                        )
                        resources[row[0]] = permission

                    return resources
        except Exception as e:
            logger.error(f"Failed to get resources for role '{role_name}': {e}")
            return {}

    # ==================== Search and Query Operations ====================

    def search_roles(self, query: str) -> List[Role]:
        """
        Search roles by name or description.

        Args:
            query: Search query string

        Returns:
            List of matching Role objects
        """
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:

                        search_pattern = f"%{query}%"
                        cursor.execute("""
                            SELECT role_name FROM roles 
                            WHERE role_name LIKE ? OR description LIKE ?
                            ORDER BY role_name
                        """, (search_pattern, search_pattern))

                        role_names = [row[0] for row in cursor.fetchall()]

                        roles = []
                        for role_name in role_names:
                            role = self.load_role(role_name)
                            if role:
                                roles.append(role)

                        return roles
            except Exception as e:
                logger.error(f"Failed to search roles with query '{query}': {e}")
                return []

    def get_roles_with_resource(self, resource_name: str) -> List[str]:
        """
        Get all roles that have access to a specific resource.

        Args:
            resource_name: Name of the resource

        Returns:
            List of role names
        """
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        SELECT DISTINCT role_name FROM role_resources 
                        WHERE resource_name = ?
                        ORDER BY role_name
                    """, (resource_name,))

                    role_names = [row[0] for row in cursor.fetchall()]
                    return role_names
        except Exception as e:
            logger.error(f"Failed to get roles with resource '{resource_name}': {e}")
            return []

    def count_roles(self, enabled_only: bool = False) -> int:
        """
        Count total number of roles.

        Args:
            enabled_only: If True, count only enabled roles

        Returns:
            Number of roles
        """
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:

                    if enabled_only:
                        cursor.execute("SELECT COUNT(*) FROM roles WHERE enabled = 1")
                    else:
                        cursor.execute("SELECT COUNT(*) FROM roles")

                    count = cursor.fetchone()[0]
                    return count
        except Exception as e:
            logger.error(f"Failed to count roles: {e}")
            return 0

    # ==================== Statistics ====================

    def get_role_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about roles in the database.

        Returns:
            Dictionary with role statistics
        """
        try:
            total = self.count_roles(enabled_only=False)
            enabled = self.count_roles(enabled_only=True)
            disabled = total - enabled

            # Count total resource assignments
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("SELECT COUNT(*) FROM role_resources")
                    total_assignments = cursor.fetchone()[0]

            return {
                'total': total,
                'enabled': enabled,
                'disabled': disabled,
                'total_resource_assignments': total_assignments
            }
        except Exception as e:
            logger.error(f"Failed to get role statistics: {e}")
            return {
                'total': 0,
                'enabled': 0,
                'disabled': 0,
                'total_resource_assignments': 0
            }


# Example usage
if __name__ == "__main__":
    # Initialize role manager
    role_mgr = RoleManagementDB("abhikarta_db")

    # List all roles
    roles = role_mgr.list_roles()
    print(f"Total roles: {len(roles)}")

    for role in roles:
        print(f"\nRole: {role.name}")
        print(f"  Description: {role.description}")
        print(f"  Enabled: {role.enabled}")
        print(f"  Resources: {len(role.resources)}")

    # Get statistics
    stats = role_mgr.get_role_statistics()
    print(f"\nRole Statistics: {stats}")