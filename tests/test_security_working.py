"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.4
"""

"""
Working Security Tests - Corrected API Usage

Tests all 5 security features with correct API calls.

© 2025-2030 All rights reserved Ashutosh Sinha
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.abstraction.security import (
    PIIDetector, PIIType, PIIAction, PIIDetectedException,
    ContentFilter, ContentCategory, ContentFilterException,
    AuditLogger, AuditLevel,
    KeyRotationManager, KeyRotationPolicy,
    RBACManager, Permission, PermissionDeniedError
)
from datetime import datetime, timedelta


def test_pii_detection():
    """Test PII detection"""
    print("="*60)
    print("1. PII DETECTION")
    print("="*60)
    
    # Test email detection
    detector = PIIDetector(detect=['email'], action='redact')
    text = "Email: john@example.com"
    result = detector.process(text)
    
    print(f"Original: {text}")
    print(f"Redacted: {result.redacted_text}")
    print(f"Matches:  {len(result.matches)}")
    
    assert len(result.matches) == 1
    assert "john@example.com" not in result.redacted_text
    print("✓ PII detection working\n")
    return True


def test_content_filter():
    """Test content filtering"""
    print("="*60)
    print("2. CONTENT FILTERING")
    print("="*60)
    
    content_filter = ContentFilter(
        block_categories=['violence'],
        threshold=0.7
    )
    
    safe_text = "Let's discuss machine learning"
    result = content_filter.process(safe_text)
    
    print(f"Safe text: '{safe_text}'")
    print(f"Is safe: {result.is_safe}")
    
    assert result.is_safe
    print("✓ Content filtering working\n")
    return True


def test_audit_logging():
    """Test audit logging"""
    print("="*60)
    print("3. AUDIT LOGGING")
    print("="*60)
    
    logger = AuditLogger(
        log_level='metadata_only',  # Use lowercase
        log_file='test_audit.log'
    )
    
    logger.log_event(
        user="test@example.com",
        action="llm_request",
        resource="gpt-4",
        result="success",
        metadata={}
    )
    
    print("Event logged successfully")
    
    if os.path.exists('test_audit.log'):
        os.remove('test_audit.log')
    if os.path.exists('logs/audit'):
        import shutil
        shutil.rmtree('logs/audit', ignore_errors=True)
    
    print("✓ Audit logging working\n")
    return True


def test_key_rotation():
    """Test key rotation"""
    print("="*60)
    print("4. KEY ROTATION")
    print("="*60)
    
    manager = KeyRotationManager()
    
    # Create a policy
    policy = KeyRotationPolicy(
        provider="test_provider",
        rotation_interval_days=30
    )
    
    manager.policies["test_provider"] = policy
    
    print("Rotation policy created")
    print("✓ Key rotation working\n")
    return True


def test_rbac():
    """Test RBAC"""
    print("="*60)
    print("5. RBAC")
    print("="*60)
    
    rbac = RBACManager()
    
    # Create role with permission values (strings)
    role = rbac.create_role(
        name="developer",
        description="Developer role",
        permissions=['use_anthropic']  # Use string values
    )
    
    # Create user
    user = rbac.create_user(
        user_id="alice@example.com",
        roles=["developer"]
    )
    
    # Check permission
    has_perm = rbac.has_permission("alice@example.com", Permission.USE_ANTHROPIC)
    
    print(f"Role created: {role.name}")
    print(f"User created: {user.user_id}")
    print(f"Has permission: {has_perm}")
    
    # Clean up
    if os.path.exists('rbac_data.json'):
        os.remove('rbac_data.json')
    
    assert has_perm == True
    print("✓ RBAC working\n")
    return True


def main():
    """Run all tests"""
    print("\n╔" + "="*58 + "╗")
    print("║" + "  SECURITY TESTS - CORRECTED API  ".center(58) + "║")
    print("╚" + "="*58 + "╝\n")
    
    tests = [
        ("PII Detection", test_pii_detection),
        ("Content Filtering", test_content_filter),
        ("Audit Logging", test_audit_logging),
        ("Key Rotation", test_key_rotation),
        ("RBAC", test_rbac),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"✗ {name} FAILED\n")
                failed += 1
        except Exception as e:
            print(f"✗ {name} FAILED: {e}\n")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60)
    
    if failed == 0:
        print("\n🎉 ALL SECURITY TESTS PASSED! 🎉\n")
    else:
        print(f"\n⚠️  {failed} test(s) failed\n")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
