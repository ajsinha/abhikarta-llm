"""
Resource Management Database Module - Database-backed resource management implementation.

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
from user_management.user import Resource

logger = logging.getLogger(__name__)


class ResourceManagementDB:
    """
    Database-backed implementation for Resource Management.

    This implementation provides CRUD operations for resources stored in a
    relational database. Supports multiple database types (PostgreSQL, MySQL,
    SQLite) through a connection pool manager.

    Features:
    - Transaction support for data consistency
    - Connection pooling for performance
    - Thread-safe operations
    - Resource type filtering
    - Search capabilities
    """

    def __init__(self, db_connection_pool_name: str):
        """
        Initialize the database-backed resource manager.

        Args:
            db_connection_pool_name: Database connection pool name
        """
        self._db_connection_pool_name = db_connection_pool_name
        self._connection_pool_manager = get_pool_manager()
        self._lock = threading.RLock()
        logger.info(f"ResourceManagementDB initialized with {db_connection_pool_name} connection pool")

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

    # ==================== Resource CRUD Operations ====================

    def save_resource(self, resource: Resource) -> bool:
        """
        Save a resource to the database (insert or update).

        Args:
            resource: Resource object to save

        Returns:
            True if save successful, False otherwise
        """
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:

                        if self.resource_exists(resource.name):
                            # Update existing resource
                            cursor.execute("""
                                UPDATE resources 
                                SET resource_type = ?, description = ?, enabled = ?, metadata = ?
                                WHERE resource_name = ?
                            """, (
                                resource.resource_type,
                                resource.description,
                                resource.enabled,
                                json.dumps(resource.metadata),
                                resource.name
                            ))
                        else:
                            # Insert new resource
                            cursor.execute("""
                                INSERT INTO resources 
                                (resource_name, resource_type, description, enabled, created_at, metadata)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (
                                resource.name,
                                resource.resource_type,
                                resource.description,
                                resource.enabled,
                                resource.created_at,
                                json.dumps(resource.metadata)
                            ))

                        logger.info(f"Saved resource '{resource.name}'")
                        return True
            except Exception as e:
                logger.error(f"Failed to save resource '{resource.name}': {e}")
                return False

    def load_resource(self, resource_name: str) -> Optional[Resource]:
        """
        Load a resource from the database.

        Args:
            resource_name: Name of the resource to load

        Returns:
            Resource object if found, None otherwise
        """
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:
                        cursor.execute("""
                            SELECT resource_name, resource_type, description, enabled, 
                                   created_at, metadata
                            FROM resources WHERE resource_name = ?
                        """, (resource_name,))

                        row = cursor.fetchone()
                        if not row:
                            return None

                        # Create resource object
                        resource = Resource(
                            name=row[0],
                            resource_type=row[1],
                            description=row[2],
                            enabled=bool(row[3]),
                            created_at=row[4],
                            metadata=json.loads(row[5]) if row[5] else {}
                        )

                        return resource
            except Exception as e:
                logger.error(f"Failed to load resource '{resource_name}': {e}")
                return None

    def delete_resource(self, resource_name: str) -> bool:
        """
        Delete a resource from the database.

        Args:
            resource_name: Name of the resource to delete

        Returns:
            True if delete successful, False otherwise
        """
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:
                        # Delete from role_resources first
                        cursor.execute("DELETE FROM role_resources WHERE resource_name = ?", (resource_name,))

                        # Delete resource
                        cursor.execute("DELETE FROM resources WHERE resource_name = ?", (resource_name,))

                        deleted = cursor.rowcount > 0

                        if deleted:
                            logger.info(f"Deleted resource '{resource_name}'")
                        return deleted
            except Exception as e:
                logger.error(f"Failed to delete resource '{resource_name}': {e}")
                return False

    def resource_exists(self, resource_name: str) -> bool:
        """
        Check if a resource exists in the database.

        Args:
            resource_name: Name of the resource to check

        Returns:
            True if resource exists, False otherwise
        """
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("SELECT 1 FROM resources WHERE resource_name = ?", (resource_name,))
                    exists = cursor.fetchone() is not None
                    return exists
        except Exception as e:
            logger.error(f"Failed to check resource existence '{resource_name}': {e}")
            return False

    def list_resources(self, resource_type: Optional[str] = None, enabled_only: bool = False) -> List[Resource]:
        """
        List all resources from the database.

        Args:
            resource_type: Filter by resource type (optional)
            enabled_only: If True, return only enabled resources

        Returns:
            List of Resource objects
        """
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:

                        # Build query based on filters
                        if resource_type and enabled_only:
                            cursor.execute("""
                                SELECT resource_name FROM resources 
                                WHERE resource_type = ? AND enabled = 1
                                ORDER BY resource_name
                            """, (resource_type,))
                        elif resource_type:
                            cursor.execute("""
                                SELECT resource_name FROM resources 
                                WHERE resource_type = ? 
                                ORDER BY resource_name
                            """, (resource_type,))
                        elif enabled_only:
                            cursor.execute("""
                                SELECT resource_name FROM resources 
                                WHERE enabled = 1
                                ORDER BY resource_name
                            """)
                        else:
                            cursor.execute("""
                                SELECT resource_name FROM resources ORDER BY resource_name
                            """)

                        resource_names = [row[0] for row in cursor.fetchall()]

                        resources = []
                        for resource_name in resource_names:
                            resource = self.load_resource(resource_name)
                            if resource:
                                resources.append(resource)

                        return resources
            except Exception as e:
                logger.error(f"Failed to list resources: {e}")
                return []

    # ==================== Search and Query Operations ====================

    def search_resources(self, query: str) -> List[Resource]:
        """
        Search resources by name, type, or description.

        Args:
            query: Search query string

        Returns:
            List of matching Resource objects
        """
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:

                        search_pattern = f"%{query}%"
                        cursor.execute("""
                            SELECT resource_name FROM resources 
                            WHERE resource_name LIKE ? 
                               OR resource_type LIKE ? 
                               OR description LIKE ?
                            ORDER BY resource_name
                        """, (search_pattern, search_pattern, search_pattern))

                        resource_names = [row[0] for row in cursor.fetchall()]

                        resources = []
                        for resource_name in resource_names:
                            resource = self.load_resource(resource_name)
                            if resource:
                                resources.append(resource)

                        return resources
            except Exception as e:
                logger.error(f"Failed to search resources with query '{query}': {e}")
                return []

    def get_resource_types(self) -> List[str]:
        """
        Get all unique resource types in the database.

        Returns:
            List of resource type strings
        """
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        SELECT DISTINCT resource_type FROM resources 
                        ORDER BY resource_type
                    """)

                    types = [row[0] for row in cursor.fetchall()]
                    return types
        except Exception as e:
            logger.error(f"Failed to get resource types: {e}")
            return []

    def get_resources_by_type(self, resource_type: str) -> List[Resource]:
        """
        Get all resources of a specific type.

        Args:
            resource_type: The resource type to filter by

        Returns:
            List of Resource objects
        """
        return self.list_resources(resource_type=resource_type)

    def count_resources(self, resource_type: Optional[str] = None, enabled_only: bool = False) -> int:
        """
        Count total number of resources.

        Args:
            resource_type: Filter by resource type (optional)
            enabled_only: If True, count only enabled resources

        Returns:
            Number of resources
        """
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:

                    # Build query based on filters
                    if resource_type and enabled_only:
                        cursor.execute("""
                            SELECT COUNT(*) FROM resources 
                            WHERE resource_type = ? AND enabled = 1
                        """, (resource_type,))
                    elif resource_type:
                        cursor.execute("""
                            SELECT COUNT(*) FROM resources 
                            WHERE resource_type = ?
                        """, (resource_type,))
                    elif enabled_only:
                        cursor.execute("SELECT COUNT(*) FROM resources WHERE enabled = 1")
                    else:
                        cursor.execute("SELECT COUNT(*) FROM resources")

                    count = cursor.fetchone()[0]
                    return count
        except Exception as e:
            logger.error(f"Failed to count resources: {e}")
            return 0

    def get_roles_using_resource(self, resource_name: str) -> List[str]:
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
            logger.error(f"Failed to get roles using resource '{resource_name}': {e}")
            return []

    # ==================== Batch Operations ====================

    def save_resources_batch(self, resources: List[Resource]) -> Dict[str, bool]:
        """
        Save multiple resources in a batch operation.

        Args:
            resources: List of Resource objects to save

        Returns:
            Dictionary mapping resource names to save success status
        """
        results = {}
        with self._lock:
            for resource in resources:
                results[resource.name] = self.save_resource(resource)
        return results

    def delete_resources_batch(self, resource_names: List[str]) -> Dict[str, bool]:
        """
        Delete multiple resources in a batch operation.

        Args:
            resource_names: List of resource names to delete

        Returns:
            Dictionary mapping resource names to delete success status
        """
        results = {}
        with self._lock:
            for resource_name in resource_names:
                results[resource_name] = self.delete_resource(resource_name)
        return results

    def enable_resources_batch(self, resource_names: List[str], enabled: bool = True) -> int:
        """
        Enable or disable multiple resources in a batch operation.

        Args:
            resource_names: List of resource names
            enabled: True to enable, False to disable

        Returns:
            Number of resources updated
        """
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:

                        updated_count = 0
                        for resource_name in resource_names:
                            cursor.execute("""
                                UPDATE resources 
                                SET enabled = ? 
                                WHERE resource_name = ?
                            """, (enabled, resource_name))

                            if cursor.rowcount > 0:
                                updated_count += 1

                        logger.info(f"Batch {'enabled' if enabled else 'disabled'} {updated_count} resources")
                        return updated_count
            except Exception as e:
                logger.error(f"Failed to batch update resources: {e}")
                return 0

    # ==================== Statistics ====================

    def get_resource_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about resources in the database.

        Returns:
            Dictionary with resource statistics
        """
        try:
            total = self.count_resources(enabled_only=False)
            enabled = self.count_resources(enabled_only=True)
            disabled = total - enabled

            # Count by type
            types = self.get_resource_types()
            type_counts = {}
            for resource_type in types:
                type_counts[resource_type] = self.count_resources(resource_type=resource_type)

            # Count total role assignments
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("SELECT COUNT(*) FROM role_resources")
                    total_assignments = cursor.fetchone()[0]

            return {
                'total': total,
                'enabled': enabled,
                'disabled': disabled,
                'types': types,
                'type_counts': type_counts,
                'total_role_assignments': total_assignments
            }
        except Exception as e:
            logger.error(f"Failed to get resource statistics: {e}")
            return {
                'total': 0,
                'enabled': 0,
                'disabled': 0,
                'types': [],
                'type_counts': {},
                'total_role_assignments': 0
            }

    def get_unused_resources(self) -> List[Resource]:
        """
        Get all resources that are not assigned to any role.

        Returns:
            List of Resource objects not assigned to any role
        """
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:

                        cursor.execute("""
                            SELECT r.resource_name 
                            FROM resources r
                            LEFT JOIN role_resources rr ON r.resource_name = rr.resource_name
                            WHERE rr.resource_name IS NULL
                            ORDER BY r.resource_name
                        """)

                        resource_names = [row[0] for row in cursor.fetchall()]

                        resources = []
                        for resource_name in resource_names:
                            resource = self.load_resource(resource_name)
                            if resource:
                                resources.append(resource)

                        return resources
            except Exception as e:
                logger.error(f"Failed to get unused resources: {e}")
                return []

    def get_most_used_resources(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most frequently used resources (by number of role assignments).

        Args:
            limit: Maximum number of resources to return

        Returns:
            List of dictionaries with resource info and usage count
        """
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:

                    cursor.execute("""
                        SELECT r.resource_name, r.resource_type, COUNT(rr.role_name) as usage_count
                        FROM resources r
                        LEFT JOIN role_resources rr ON r.resource_name = rr.resource_name
                        GROUP BY r.resource_name, r.resource_type
                        ORDER BY usage_count DESC, r.resource_name
                        LIMIT ?
                    """, (limit,))

                    results = []
                    for row in cursor.fetchall():
                        resource = self.load_resource(row[0])
                        if resource:
                            results.append({
                                'resource': resource,
                                'usage_count': row[2]
                            })

                    return results
        except Exception as e:
            logger.error(f"Failed to get most used resources: {e}")
            return []


# Example usage
if __name__ == "__main__":
    # Initialize resource manager
    resource_mgr = ResourceManagementDB("abhikarta_db")

    # List all resources
    resources = resource_mgr.list_resources()
    print(f"Total resources: {len(resources)}")

    for resource in resources[:5]:  # Show first 5
        print(f"\nResource: {resource.name}")
        print(f"  Type: {resource.resource_type}")
        print(f"  Description: {resource.description}")
        print(f"  Enabled: {resource.enabled}")

    # Get statistics
    stats = resource_mgr.get_resource_statistics()
    print(f"\nResource Statistics:")
    print(f"  Total: {stats['total']}")
    print(f"  Enabled: {stats['enabled']}")
    print(f"  Types: {stats['types']}")

    # Get most used resources
    most_used = resource_mgr.get_most_used_resources(limit=5)
    print(f"\nMost Used Resources:")
    for item in most_used:
        print(f"  {item['resource'].name}: {item['usage_count']} roles")