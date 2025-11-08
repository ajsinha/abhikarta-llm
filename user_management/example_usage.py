"""
Example Usage - Demonstrates the Abhikarta LLM User Management System.

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
import json
from datetime import datetime

from user import User, Role, Resource, Permission, PasswordEncryption
from user_registry import UserRegistry, get_user_registry
from user_manager import UserManager
from user_manager_json import UserManagerJSON

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_1_basic_operations():
    """Example 1: Basic user, role, and resource operations."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Operations")
    print("="*80)
    
    # Get the singleton registry
    registry = get_user_registry()
    
    # Create resources
    print("\n--- Creating Resources ---")
    resources = [
        Resource("chatbot_api", "api", "Chatbot API endpoint"),
        Resource("document_store", "data", "Document storage system"),
        Resource("admin_panel", "admin", "Administration panel"),
    ]
    
    for resource in resources:
        registry.add_resource(resource)
        print(f"Created resource: {resource.name} ({resource.resource_type})")
    
    # Create a role
    print("\n--- Creating Role ---")
    developer_role = Role("api_developer", "Developer with API access")
    developer_role.add_resource("chatbot_api", Permission(read=True, execute=True))
    developer_role.add_resource("document_store", Permission(read=True))
    registry.add_role(developer_role)
    print(f"Created role: {developer_role.name}")
    
    # Create a user
    print("\n--- Creating User ---")
    user = User(
        userid="alice",
        fullname="Alice Johnson",
        emailaddress="alice@example.com",
        password_hash=PasswordEncryption.encrypt_password("SecurePass123!"),
        roles=["api_developer"]
    )
    registry.add_user(user)
    print(f"Created user: {user.userid}")
    
    # Authenticate user
    print("\n--- Authentication ---")
    token = registry.authenticate("alice", "SecurePass123!")
    if token:
        print(f"Authentication successful! Token: {token[:50]}...")
        
        # Verify token
        payload = registry.verify_token(token)
        print(f"Token payload: {json.dumps(payload, indent=2, default=str)}")
    
    # Check permissions
    print("\n--- Permission Checks ---")
    print(f"Alice can read chatbot_api: {registry.check_permission('alice', 'chatbot_api', 'read')}")
    print(f"Alice can delete chatbot_api: {registry.check_permission('alice', 'chatbot_api', 'delete')}")
    print(f"Alice can read document_store: {registry.check_permission('alice', 'document_store', 'read')}")
    
    # Get accessible resources
    print("\n--- Accessible Resources ---")
    accessible = registry.get_accessible_resources("alice")
    print(f"Resources accessible to Alice: {accessible}")


def example_2_pattern_matching():
    """Example 2: Pattern-based permission matching."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Pattern-Based Permissions")
    print("="*80)
    
    registry = get_user_registry()
    
    # Create multiple resources with similar names
    print("\n--- Creating Resources ---")
    resources = [
        Resource("google_search", "external", "Google Search API"),
        Resource("google_maps", "external", "Google Maps API"),
        Resource("google_drive", "external", "Google Drive API"),
        Resource("yahoo_finance", "external", "Yahoo Finance API"),
        Resource("yahoo_news", "external", "Yahoo News API"),
    ]
    
    for resource in resources:
        registry.add_resource(resource)
        print(f"Created resource: {resource.name}")
    
    # Create role with pattern matching
    print("\n--- Creating Role with Pattern ---")
    google_role = Role("google_services_user", "User with access to all Google services")
    google_role.add_resource("google*", Permission.all_permissions())
    registry.add_role(google_role)
    print(f"Created role with pattern: google*")
    
    # Create user with this role
    user = User(
        userid="bob",
        fullname="Bob Smith",
        emailaddress="bob@example.com",
        password_hash=PasswordEncryption.encrypt_password("BobPass456!"),
        roles=["google_services_user"]
    )
    registry.add_user(user)
    print(f"Created user: {user.userid}")
    
    # Check permissions
    print("\n--- Permission Checks ---")
    print(f"Bob can access google_search: {registry.check_permission('bob', 'google_search', 'read')}")
    print(f"Bob can access google_maps: {registry.check_permission('bob', 'google_maps', 'read')}")
    print(f"Bob can access google_drive: {registry.check_permission('bob', 'google_drive', 'create')}")
    print(f"Bob can access yahoo_finance: {registry.check_permission('bob', 'yahoo_finance', 'read')}")
    
    # Get all accessible resources
    print("\n--- Accessible Resources ---")
    accessible = registry.get_accessible_resources("bob")
    print(f"Resources accessible to Bob: {accessible}")
    
    # Wildcard role
    print("\n--- Creating Wildcard Role ---")
    superuser_role = Role("superuser", "User with access to everything")
    superuser_role.add_resource("*", Permission.all_permissions())
    registry.add_role(superuser_role)
    
    user2 = User(
        userid="charlie",
        fullname="Charlie Admin",
        emailaddress="charlie@example.com",
        password_hash=PasswordEncryption.encrypt_password("CharliePass789!"),
        roles=["superuser"]
    )
    registry.add_user(user2)
    
    print(f"Charlie's accessible resources: {len(registry.get_accessible_resources('charlie'))} (all resources)")


def example_3_disabled_resources():
    """Example 3: Working with disabled resources."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Disabled Resources")
    print("="*80)
    
    registry = get_user_registry()
    
    # Create a resource and disable it
    print("\n--- Creating and Disabling Resource ---")
    resource = Resource("legacy_api", "api", "Legacy API (deprecated)")
    registry.add_resource(resource)
    print(f"Created resource: {resource.name}")
    
    # Create role with access to this resource
    role = Role("legacy_user", "User with legacy API access")
    role.add_resource("legacy_api", Permission.all_permissions())
    registry.add_role(role)
    
    # Create user
    user = User(
        userid="david",
        fullname="David Lee",
        emailaddress="david@example.com",
        password_hash=PasswordEncryption.encrypt_password("DavidPass!"),
        roles=["legacy_user"]
    )
    registry.add_user(user)
    
    # Check permissions before disabling
    print("\n--- Before Disabling ---")
    print(f"David can access legacy_api: {registry.check_permission('david', 'legacy_api', 'read')}")
    accessible = registry.get_accessible_resources("david")
    print(f"David's accessible resources: {accessible}")
    
    # Disable the resource
    registry.disable_resource("legacy_api")
    print("\n--- After Disabling ---")
    print(f"David can access legacy_api: {registry.check_permission('david', 'legacy_api', 'read')}")
    accessible = registry.get_accessible_resources("david")
    print(f"David's accessible resources: {accessible}")
    
    # Re-enable the resource
    registry.enable_resource("legacy_api")
    print("\n--- After Re-enabling ---")
    print(f"David can access legacy_api: {registry.check_permission('david', 'legacy_api', 'read')}")


def example_4_cascading_deletions():
    """Example 4: Cascading deletions to maintain data consistency."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Cascading Deletions")
    print("="*80)
    
    registry = get_user_registry()
    
    # Setup: Create resource, role, and user
    print("\n--- Setup ---")
    resource = Resource("temp_api", "api", "Temporary API")
    registry.add_resource(resource)
    
    role = Role("temp_role", "Temporary role")
    role.add_resource("temp_api", Permission.all_permissions())
    registry.add_role(role)
    
    user = User(
        userid="eve",
        fullname="Eve Wilson",
        emailaddress="eve@example.com",
        password_hash=PasswordEncryption.encrypt_password("EvePass!"),
        roles=["temp_role"]
    )
    registry.add_user(user)
    
    print(f"Created: resource={resource.name}, role={role.name}, user={user.userid}")
    
    # Delete resource (should be removed from role)
    print("\n--- Deleting Resource ---")
    print(f"Role has resource before deletion: {role.has_resource('temp_api')}")
    registry.remove_resource("temp_api")
    role = registry.get_role("temp_role")
    print(f"Role has resource after deletion: {role.has_resource('temp_api')}")
    
    # Delete role (should be removed from user)
    print("\n--- Deleting Role ---")
    user = registry.get_user("eve")
    print(f"User has role before deletion: {user.has_role('temp_role')}")
    registry.remove_role("temp_role")
    user = registry.get_user("eve")
    print(f"User has role after deletion: {user.has_role('temp_role')}")


def example_5_json_persistence():
    """Example 5: Using JSON file for persistence."""
    print("\n" + "="*80)
    print("EXAMPLE 5: JSON File Persistence")
    print("="*80)
    
    # Create JSON-backed manager
    print("\n--- Initializing JSON Manager ---")
    json_manager = UserManagerJSON("config/users_example.json")
    json_manager.initialize()
    
    # Create and save data
    print("\n--- Creating Data ---")
    resource = Resource("json_api", "api", "API stored in JSON")
    json_manager.save_resource(resource)
    print(f"Saved resource: {resource.name}")
    
    role = Role("json_role", "Role stored in JSON")
    role.add_resource("json_api", Permission(read=True, execute=True))
    json_manager.save_role(role)
    print(f"Saved role: {role.name}")
    
    user = User(
        userid="frank",
        fullname="Frank Miller",
        emailaddress="frank@example.com",
        password_hash=PasswordEncryption.encrypt_password("FrankPass!"),
        roles=["json_role"]
    )
    json_manager.save_user(user)
    print(f"Saved user: {user.userid}")
    
    # Load data
    print("\n--- Loading Data ---")
    loaded_user = json_manager.load_user("frank")
    print(f"Loaded user: {loaded_user.userid}, roles: {loaded_user.roles}")
    
    loaded_role = json_manager.load_role("json_role")
    print(f"Loaded role: {loaded_role.name}, resources: {list(loaded_role.resources.keys())}")
    
    # List all
    print("\n--- Listing All Data ---")
    users = json_manager.list_users()
    roles = json_manager.list_roles()
    resources = json_manager.list_resources()
    print(f"Total users: {len(users)}")
    print(f"Total roles: {len(roles)}")
    print(f"Total resources: {len(resources)}")
    
    # Convenience methods
    print("\n--- Using Convenience Methods ---")
    json_manager.add_role_to_user("frank", "json_role")
    json_manager.add_resource_to_role("json_role", "json_api", Permission.all_permissions())
    
    user_roles = json_manager.get_user_roles("frank")
    print(f"Frank's roles: {user_roles}")
    
    role_resources = json_manager.get_role_resources("json_role")
    print(f"json_role's resources: {list(role_resources.keys())}")


def example_6_statistics():
    """Example 6: Monitoring and statistics."""
    print("\n" + "="*80)
    print("EXAMPLE 6: Statistics and Monitoring")
    print("="*80)
    
    registry = get_user_registry()
    
    # Get statistics
    print("\n--- Registry Statistics ---")
    stats = registry.get_statistics()
    print(json.dumps(stats, indent=2))
    
    # Perform some authentications
    print("\n--- Performing Authentications ---")
    registry.authenticate("alice", "WrongPassword")  # Failed
    registry.authenticate("alice", "SecurePass123!")  # Success
    registry.authenticate("bob", "BobPass456!")  # Success
    
    # Get updated statistics
    print("\n--- Updated Statistics ---")
    stats = registry.get_statistics()
    print(json.dumps(stats, indent=2))


def example_7_admin_operations():
    """Example 7: Admin user operations."""
    print("\n" + "="*80)
    print("EXAMPLE 7: Admin User Operations")
    print("="*80)
    
    registry = get_user_registry()
    
    # Admin authentication
    print("\n--- Admin Authentication ---")
    admin_token = registry.authenticate("admin", "admin123")
    if admin_token:
        print("Admin authenticated successfully")
        
        # Admin has access to everything
        print("\n--- Admin Permissions ---")
        admin_resources = registry.get_accessible_resources("admin")
        print(f"Admin can access {len(admin_resources)} resources")
        print(f"Sample resources: {admin_resources[:5]}")
        
        # Admin can perform any operation
        print(f"\nAdmin can delete user_management: {registry.check_permission('admin', 'user_management', 'delete')}")
        print(f"Admin can create admin_panel: {registry.check_permission('admin', 'admin_panel', 'create')}")


def example_8_multiple_roles():
    """Example 8: User with multiple roles."""
    print("\n" + "="*80)
    print("EXAMPLE 8: Multiple Roles per User")
    print("="*80)
    
    registry = get_user_registry()
    
    # Create multiple roles
    print("\n--- Creating Roles ---")
    role1 = Role("reader", "Read-only access")
    role1.add_resource("chatbot_api", Permission(read=True))
    registry.add_role(role1)
    
    role2 = Role("executor", "Execution access")
    role2.add_resource("chatbot_api", Permission(execute=True))
    registry.add_role(role2)
    
    # Create user with multiple roles
    user = User(
        userid="grace",
        fullname="Grace Hopper",
        emailaddress="grace@example.com",
        password_hash=PasswordEncryption.encrypt_password("GracePass!"),
        roles=["reader", "executor"]
    )
    registry.add_user(user)
    print(f"Created user {user.userid} with roles: {user.roles}")
    
    # Check aggregated permissions
    print("\n--- Aggregated Permissions ---")
    permissions = registry.get_user_permissions("grace")
    if "chatbot_api" in permissions:
        perm = permissions["chatbot_api"]
        print(f"Grace's permissions on chatbot_api:")
        print(f"  Read: {perm.read}")
        print(f"  Execute: {perm.execute}")
        print(f"  Create: {perm.create}")


def example_9_token_refresh():
    """Example 9: JWT token refresh."""
    print("\n" + "="*80)
    print("EXAMPLE 9: Token Refresh")
    print("="*80)
    
    registry = get_user_registry()
    
    # Authenticate and get token
    print("\n--- Initial Authentication ---")
    token = registry.authenticate("alice", "SecurePass123!")
    if token:
        print(f"Initial token: {token[:50]}...")
        
        # Refresh token
        print("\n--- Refreshing Token ---")
        new_token = registry.refresh_token(token)
        if new_token:
            print(f"Refreshed token: {new_token[:50]}...")
            print("Token refreshed successfully")


def main():
    """Run all examples."""
    print("\n" + "#"*80)
    print("# ABHIKARTA LLM USER MANAGEMENT SYSTEM - COMPREHENSIVE EXAMPLES")
    print("#"*80)
    
    try:
        example_1_basic_operations()
        example_2_pattern_matching()
        example_3_disabled_resources()
        example_4_cascading_deletions()
        example_5_json_persistence()
        example_6_statistics()
        example_7_admin_operations()
        example_8_multiple_roles()
        example_9_token_refresh()
        
        print("\n" + "#"*80)
        print("# ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("#"*80)
        
    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
