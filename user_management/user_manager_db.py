"""
User Manager Database Module - Database-backed user management implementation.

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
from user import User, Role, Resource, Permission
from user_manager import UserManager

logger = logging.getLogger(__name__)


class UserManagerDB(UserManager):
    """
    Database-backed implementation of UserManager.
    
    This implementation stores users, roles, and resources in a relational database.
    Supports multiple database types (PostgreSQL, MySQL, SQLite) through a connection
    pool manager.
    
    Features:
    - Transaction support for data consistency
    - Connection pooling for performance
    - Thread-safe operations
    - Cascading deletions
    """
    
    def __init__(self, db_connection_pool_name: str):
        """
        Initialize the database-backed user manager.
        
        Args:
            db_connection_pool_name: Database connection pool name
        """
        super().__init__()
        self._db_connection_pool_name = db_connection_pool_name
        self._connection_pool_manager =  get_pool_manager()
        self._lock = threading.RLock()
        logger.info(f"UserManagerDB initialized with {db_connection_pool_name} connection pool")
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = self._connection_pool_manager.get_connection_context(self._db_connection_pool_name)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    @contextmanager
    def _get_cursor(self, conn):
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()


    def close(self) -> None:
        """Close database connections."""
        logger.info("Closing database connections")
        # Connection pool handles cleanup
    
    # ==================== User Operations ====================
    
    def save_user(self, user: User) -> bool:
        """Save a user to the database."""
        if not self.validate_user(user):
            return False
        
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:
                    
                        # Check if user exists
                        if self.user_exists(user.userid):
                            # Update existing user
                            cursor.execute("""
                                UPDATE users 
                                SET fullname = %s, emailaddress = %s, password_hash = %s,
                                    enabled = %s, updated_at = %s, last_login = %s, metadata = %s
                                WHERE userid = %s
                            """, (
                                user.fullname, user.emailaddress, user.password_hash,
                                user.enabled, user.updated_at, user.last_login,
                                json.dumps(user.metadata), user.userid
                            ))

                            # Update roles - delete old and insert new
                            cursor.execute("DELETE FROM user_roles WHERE userid = %s", (user.userid,))
                            for role in user.roles:
                                cursor.execute("""
                                    INSERT INTO user_roles (userid, role_name)
                                    VALUES (%s, %s)
                                """, (user.userid, role))
                        else:
                            # Insert new user
                            cursor.execute("""
                                INSERT INTO users 
                                (userid, fullname, emailaddress, password_hash, enabled, 
                                 created_at, updated_at, last_login, metadata)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                user.userid, user.fullname, user.emailaddress, user.password_hash,
                                user.enabled, user.created_at, user.updated_at, user.last_login,
                                json.dumps(user.metadata)
                            ))

                            # Insert roles
                            for role in user.roles:
                                cursor.execute("""
                                    INSERT INTO user_roles (userid, role_name)
                                    VALUES (%s, %s)
                                """, (user.userid, role))

                        logger.info(f"Saved user '{user.userid}'")
                        return True
            except Exception as e:
                logger.error(f"Failed to save user '{user.userid}': {e}")
                return False
    
    def load_user(self, userid: str) -> Optional[User]:
        """Load a user from the database."""
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:
                    
                        # Load user
                        cursor.execute("""
                            SELECT userid, fullname, emailaddress, password_hash, enabled,
                                   created_at, updated_at, last_login, metadata
                            FROM users WHERE userid = %s
                        """, (userid,))

                        row = cursor.fetchone()
                        if not row:
                            cursor.close()
                            return None

                        # Load roles
                        cursor.execute("""
                            SELECT role_name FROM user_roles WHERE userid = %s
                        """, (userid,))

                        roles = [r[0] for r in cursor.fetchall()]

                        # Create user object
                        user = User(
                            userid=row[0],
                            fullname=row[1],
                            emailaddress=row[2],
                            password_hash=row[3],
                            roles=roles,
                            enabled=row[4],
                            created_at=row[5],
                            updated_at=row[6],
                            last_login=row[7],
                            metadata=json.loads(row[8]) if row[8] else {}
                        )

                        return user
            except Exception as e:
                logger.error(f"Failed to load user '{userid}': {e}")
                return None
    
    def delete_user(self, userid: str) -> bool:
        """Delete a user from the database."""
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:
                    
                        # Delete user roles first (foreign key constraint)
                        cursor.execute("DELETE FROM user_roles WHERE userid = %s", (userid,))

                        # Delete user
                        cursor.execute("DELETE FROM users WHERE userid = %s", (userid,))

                        deleted = cursor.rowcount > 0

                        if deleted:
                            logger.info(f"Deleted user '{userid}'")
                        return deleted
            except Exception as e:
                logger.error(f"Failed to delete user '{userid}': {e}")
                return False
    
    def list_users(self) -> List[User]:
        """List all users from the database."""
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:
                    
                        cursor.execute("""
                            SELECT userid FROM users ORDER BY userid
                        """)

                        userids = [row[0] for row in cursor.fetchall()]

                        users = []
                        for userid in userids:
                            user = self.load_user(userid)
                            if user:
                                users.append(user)

                        return users
            except Exception as e:
                logger.error(f"Failed to list users: {e}")
                return []
    
    def user_exists(self, userid: str) -> bool:
        """Check if a user exists in the database."""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("SELECT 1 FROM users WHERE userid = %s", (userid,))
                    exists = cursor.fetchone() is not None
                    return exists
        except Exception as e:
            logger.error(f"Failed to check user existence '{userid}': {e}")
            return False
    
    # ==================== Role Operations ====================
    
    def save_role(self, role: Role) -> bool:
        """Save a role to the database."""
        if not self.validate_role(role):
            return False
        
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:
                    
                        if self.role_exists(role.name):
                            # Update existing role
                            cursor.execute("""
                                UPDATE roles 
                                SET description = %s, enabled = %s, metadata = %s
                                WHERE role_name = %s
                            """, (
                                role.description, role.enabled,
                                json.dumps(role.metadata), role.name
                            ))

                            # Update resources
                            cursor.execute("DELETE FROM role_resources WHERE role_name = %s", (role.name,))
                            for resource_name, permission in role.resources.items():
                                cursor.execute("""
                                    INSERT INTO role_resources 
                                    (role_name, resource_name, can_create, can_read, 
                                     can_update, can_delete, can_execute)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                                """, (
                                    role.name, resource_name, permission.create, permission.read,
                                    permission.update, permission.delete, permission.execute
                                ))
                        else:
                            # Insert new role
                            cursor.execute("""
                                INSERT INTO roles (role_name, description, enabled, created_at, metadata)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (
                                role.name, role.description, role.enabled,
                                role.created_at, json.dumps(role.metadata)
                            ))

                            # Insert resources
                            for resource_name, permission in role.resources.items():
                                cursor.execute("""
                                    INSERT INTO role_resources 
                                    (role_name, resource_name, can_create, can_read, 
                                     can_update, can_delete, can_execute)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                                """, (
                                    role.name, resource_name, permission.create, permission.read,
                                    permission.update, permission.delete, permission.execute
                                ))

                        logger.info(f"Saved role '{role.name}'")
                        return True
            except Exception as e:
                logger.error(f"Failed to save role '{role.name}': {e}")
                return False
    
    def load_role(self, role_name: str) -> Optional[Role]:
        """Load a role from the database."""
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:
                    
                        # Load role
                        cursor.execute("""
                            SELECT role_name, description, enabled, created_at, metadata
                            FROM roles WHERE role_name = %s
                        """, (role_name,))

                        row = cursor.fetchone()
                        if not row:
                            cursor.close()
                            return None

                        # Load resources
                        cursor.execute("""
                            SELECT resource_name, can_create, can_read, can_update, 
                                   can_delete, can_execute
                            FROM role_resources WHERE role_name = %s
                        """, (role_name,))

                        resources = {}
                        for r in cursor.fetchall():
                            resources[r[0]] = Permission(
                                create=r[1], read=r[2], update=r[3],
                                delete=r[4], execute=r[5]
                            )

                        # Create role object
                        role = Role(
                            name=row[0],
                            description=row[1],
                            resources=resources,
                            enabled=row[2],
                            created_at=row[3],
                            metadata=json.loads(row[4]) if row[4] else {}
                        )

                        return role
            except Exception as e:
                logger.error(f"Failed to load role '{role_name}': {e}")
                return None
    
    def delete_role(self, role_name: str) -> bool:
        """Delete a role from the database."""
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:
                    
                        # Delete role resources first
                        cursor.execute("DELETE FROM role_resources WHERE role_name = %s", (role_name,))

                        # Delete user roles
                        cursor.execute("DELETE FROM user_roles WHERE role_name = %s", (role_name,))

                        # Delete role
                        cursor.execute("DELETE FROM roles WHERE role_name = %s", (role_name,))

                        deleted = cursor.rowcount > 0

                        if deleted:
                            logger.info(f"Deleted role '{role_name}'")
                        return deleted
            except Exception as e:
                logger.error(f"Failed to delete role '{role_name}': {e}")
                return False
    
    def list_roles(self) -> List[Role]:
        """List all roles from the database."""
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:
                    
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
    
    def role_exists(self, role_name: str) -> bool:
        """Check if a role exists in the database."""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("SELECT 1 FROM roles WHERE role_name = %s", (role_name,))
                    exists = cursor.fetchone() is not None
                    return exists
        except Exception as e:
            logger.error(f"Failed to check role existence '{role_name}': {e}")
            return False
    
    # ==================== Resource Operations ====================
    
    def save_resource(self, resource: Resource) -> bool:
        """Save a resource to the database."""
        if not self.validate_resource(resource):
            return False
        
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:
                    
                        if self.resource_exists(resource.name):
                            # Update existing resource
                            cursor.execute("""
                                UPDATE resources 
                                SET resource_type = %s, description = %s, enabled = %s, metadata = %s
                                WHERE resource_name = %s
                            """, (
                                resource.resource_type, resource.description,
                                resource.enabled, json.dumps(resource.metadata), resource.name
                            ))
                        else:
                            # Insert new resource
                            cursor.execute("""
                                INSERT INTO resources 
                                (resource_name, resource_type, description, enabled, created_at, metadata)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (
                                resource.name, resource.resource_type, resource.description,
                                resource.enabled, resource.created_at, json.dumps(resource.metadata)
                            ))

                        logger.info(f"Saved resource '{resource.name}'")
                        return True
            except Exception as e:
                logger.error(f"Failed to save resource '{resource.name}': {e}")
                return False
    
    def load_resource(self, resource_name: str) -> Optional[Resource]:
        """Load a resource from the database."""
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:
                    
                        cursor.execute("""
                            SELECT resource_name, resource_type, description, enabled, 
                                   created_at, metadata
                            FROM resources WHERE resource_name = %s
                        """, (resource_name,))

                        row = cursor.fetchone()

                        if not row:
                            return None

                        resource = Resource(
                            name=row[0],
                            resource_type=row[1],
                            description=row[2],
                            enabled=row[3],
                            created_at=row[4],
                            metadata=json.loads(row[5]) if row[5] else {}
                        )

                        return resource
            except Exception as e:
                logger.error(f"Failed to load resource '{resource_name}': {e}")
                return None
    
    def delete_resource(self, resource_name: str) -> bool:
        """Delete a resource from the database."""
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:
                    
                        # Delete from role_resources first
                        cursor.execute("DELETE FROM role_resources WHERE resource_name = %s", (resource_name,))

                        # Delete resource
                        cursor.execute("DELETE FROM resources WHERE resource_name = %s", (resource_name,))

                        deleted = cursor.rowcount > 0

                        if deleted:
                            logger.info(f"Deleted resource '{resource_name}'")
                        return deleted
            except Exception as e:
                logger.error(f"Failed to delete resource '{resource_name}': {e}")
                return False
    
    def list_resources(self, resource_type: Optional[str] = None) -> List[Resource]:
        """List all resources from the database."""
        with self._lock:
            try:
                with self._get_connection() as conn:
                    with self._get_cursor(conn) as cursor:
                    
                        if resource_type:
                            cursor.execute("""
                                SELECT resource_name FROM resources 
                                WHERE resource_type = %s ORDER BY resource_name
                            """, (resource_type,))
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
    
    def resource_exists(self, resource_name: str) -> bool:
        """Check if a resource exists in the database."""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("SELECT 1 FROM resources WHERE resource_name = %s", (resource_name,))
                    exists = cursor.fetchone() is not None
                    return exists
        except Exception as e:
            logger.error(f"Failed to check resource existence '{resource_name}': {e}")
            return False
    
    # ==================== Bulk Operations ====================
    
    def load_all_data(self) -> Dict[str, Any]:
        """Load all data from the database."""
        return {
            'users': self.list_users(),
            'roles': self.list_roles(),
            'resources': self.list_resources()
        }
    
    def save_all_data(self, users: List[User], roles: List[Role], 
                     resources: List[Resource]) -> bool:
        """Save all data to the database."""
        try:
            # Save in order to maintain referential integrity
            for resource in resources:
                self.save_resource(resource)
            
            for role in roles:
                self.save_role(role)
            
            for user in users:
                self.save_user(user)
            
            logger.info("Saved all data to database")
            return True
        except Exception as e:
            logger.error(f"Failed to save all data: {e}")
            return False


# Example usage
if __name__ == "__main__":
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # This example requires a database connection pool
    # See the example_usage.py file for complete examples
    print("UserManagerDB implementation ready")
    print("Please see example_usage.py for complete examples")
