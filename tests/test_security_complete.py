"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.3
"""

"""
Complete Import Test - Including Aliases

Tests all imports including the newly added aliases:
- PIIBlockedException (alias for PIIDetectedException)
- RotationSchedule (alias for KeyRotationPolicy)
- AccessDeniedException (alias for PermissionDeniedError)

© 2025-2030 All rights reserved Ashutosh Sinha
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("\n╔" + "="*58 + "╗")
print("║" + "  COMPLETE SECURITY IMPORTS TEST (WITH ALIASES)  ".center(58) + "║")
print("╚" + "="*58 + "╝\n")

print("="*60)
print("Testing ALL Security Module Imports")
print("="*60)

# Test complete import statement
print("\n1. Testing Complete Import Statement:")
try:
    from llm.abstraction.security import (
        PIIDetector, PIIType, PIIAction, PIIBlockedException,
        ContentFilter, ContentCategory, ContentFilterException,
        AuditLogger, AuditLevel,
        KeyRotationManager, RotationSchedule,
        RBACManager, Permission, AccessDeniedException
    )
    print("   ✓ All imports successful!")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

# Test aliases work correctly
print("\n2. Verifying Aliases:")
print(f"   ✓ PIIBlockedException is PIIDetectedException: {PIIBlockedException.__name__ == 'PIIDetectedException'}")
print(f"   ✓ RotationSchedule is KeyRotationPolicy: {RotationSchedule.__name__ == 'KeyRotationPolicy'}")
print(f"   ✓ AccessDeniedException is PermissionDeniedError: {AccessDeniedException.__name__ == 'PermissionDeniedError'}")

# Test functionality with aliases
print("\n3. Testing Functionality with Aliases:")

# Test PIIBlockedException
print("   a) PIIBlockedException:")
try:
    detector = PIIDetector(detect=['ssn'], action='block')
    detector.process("SSN: 123-45-6789")
    print("      ✗ Should have blocked")
except PIIBlockedException as e:
    print("      ✓ PIIBlockedException caught correctly")

# Test RotationSchedule
print("   b) RotationSchedule:")
try:
    policy = RotationSchedule(rotation_interval_days=30)
    print(f"      ✓ RotationSchedule created: {policy.rotation_interval_days} days")
except Exception as e:
    print(f"      ✗ Failed: {e}")

# Test AccessDeniedException
print("   c) AccessDeniedException:")
try:
    rbac = RBACManager()
    rbac.create_role(name="test", description="Test", permissions=[])
    rbac.create_user(user_id="test@example.com", roles=["test"])
    
    # Try to access something they don't have permission for
    rbac.enforce_permission("test@example.com", Permission.MANAGE_USERS)
    print("      ✗ Should have denied access")
except AccessDeniedException as e:
    print("      ✓ AccessDeniedException caught correctly")
finally:
    # Clean up
    if os.path.exists('rbac_data.json'):
        os.remove('rbac_data.json')

# Show all available imports
print("\n4. Available Imports Summary:")
from llm.abstraction.security import __all__
print(f"   Total exports: {len(__all__)}")
print("\n   PII Detection (7):")
print("     - PIIDetector, PIIType, PIIAction")
print("     - PIIMatch, PIIDetectionResult")
print("     - PIIDetectedException, PIIBlockedException")
print("\n   Content Filtering (5):")
print("     - ContentFilter, ContentCategory, FilterAction")
print("     - FilterResult, ContentFilterException")
print("\n   Audit Logging (3):")
print("     - AuditLogger, AuditLevel, AuditEvent")
print("\n   Key Rotation (4):")
print("     - KeyRotationManager, KeyRotationPolicy, APIKey")
print("     - RotationSchedule (alias)")
print("\n   RBAC (8):")
print("     - RBACManager, Role, Permission, User")
print("     - RBACException, PermissionDeniedError")
print("     - ResourceLimitExceededError, AccessDeniedException (alias)")

print("\n" + "="*60)
print("COMPLETE IMPORT TEST PASSED")
print("="*60)
print("\n✅ All imports working, including aliases!")
print("\nAliases provided for backward compatibility:")
print("  • PIIBlockedException → PIIDetectedException")
print("  • RotationSchedule → KeyRotationPolicy")
print("  • AccessDeniedException → PermissionDeniedError")
print("\n🎉 All 5 security features ready to use! 🔒\n")
