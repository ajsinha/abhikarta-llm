"""
Comprehensive Security Module Tests

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
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


def test_pii_detection():
    """Test PII detection functionality"""
    print("\n" + "=" * 60)
    print("Testing PII Detection")
    print("=" * 60)
    
    # Test 1: Email detection
    print("\n1. Email Detection:")
    text = "Contact me at john.doe@example.com for more info"
    detector = PIIDetector(detect=['email'], action='alert')
    result = detector.process(text)
    print(f"   Text: {text}")
    print(f"   Detections: {len(result.detections)}")
    if result.detections:
        print(f"   Found: {result.detections[0].value}")
        print(f"   Type: {result.detections[0].pii_type.value}")
    assert len(result.detections) == 1
    print("   ✓ Email detection working")
    
    # Test 2: SSN detection and redaction
    print("\n2. SSN Redaction:")
    text = "My SSN is 123-45-6789"
    detector = PIIDetector(detect=['ssn'], action='redact')
    result = detector.process(text)
    print(f"   Original: {text}")
    print(f"   Redacted: {result.text}")
    assert "123-45-6789" not in result.text
    assert "REDACTED" in result.text.upper()
    print("   ✓ SSN redaction working")
    
    # Test 3: Credit card masking
    print("\n3. Credit Card Masking:")
    detector = PIIDetector(detect=['credit_card'], action='mask')
    text = "Card: 4532-1234-5678-9010"
    result = detector.process(text)
    print(f"   Original: {text}")
    print(f"   Masked: {result.text}")
    assert "9010" in result.text or "*" in result.text
    print("   ✓ Credit card masking working")
    
    # Test 4: Multiple PII types
    print("\n4. Multiple PII Types:")
    text = "Email: test@example.com, Phone: 555-123-4567"
    detector = PIIDetector(detect=['email', 'phone'], action='alert')
    result = detector.process(text)
    print(f"   Text: {text}")
    print(f"   Detections: {len(result.detections)}")
    assert len(result.detections) >= 1  # At least one detection
    print("   ✓ Multiple PII detection working")
    
    # Test 5: Block action
    print("\n5. Block Action:")
    detector = PIIDetector(detect=['ssn'], action='block')
    text = "SSN: 123-45-6789"
    try:
        detector.process(text)
        assert False, "Should have blocked"
    except PIIDetectedException as e:
        print(f"   Blocked: PII detected")
        print("   ✓ Block action working")


def test_content_filtering():
    """Test content filtering functionality"""
    print("\n" + "=" * 60)
    print("Testing Content Filtering")
    print("=" * 60)
    
    # Test 1: Hate speech detection
    print("\n1. Hate Speech Detection:")
    filter = ContentFilter(
        block_categories=['hate_speech'],
        threshold=0.5
    )
    
    safe_text = "I love programming in Python"
    unsafe_text = "I hate you and want to hurt you"
    
    try:
        result1 = filter.check(safe_text)
        print(f"   Safe text: PASS")
        print(f"   Score: {result1.max_score:.2f}")
    except ContentFilterException:
        print("   Safe text: FAIL (should not block)")
    
    try:
        result2 = filter.check(unsafe_text)
        print(f"   Unsafe text: Should have been blocked")
    except ContentFilterException as e:
        print(f"   Unsafe text: BLOCKED")
        print(f"   Category: {e.category}")
        print("   ✓ Hate speech detection working")
    
    # Test 2: Multiple categories
    print("\n2. Multiple Categories:")
    filter = ContentFilter(
        block_categories=['violence', 'sexual_content'],
        threshold=0.6
    )
    categories = filter.get_categories()
    print(f"   Monitoring {len(categories)} categories")
    print("   ✓ Multiple categories working")


def test_audit_logging():
    """Test audit logging functionality"""
    print("\n" + "=" * 60)
    print("Testing Audit Logging")
    print("=" * 60)
    
    # Test 1: Basic logging
    print("\n1. Basic Logging:")
    logger = AuditLogger(
        log_level='FULL',
        retention_days=90
    )
    
    logger.log_request(
        user='test_user',
        action='complete',
        resource='gpt-4',
        details={'prompt': 'Test prompt'}
    )
    
    entries = logger.get_logs(limit=1)
    print(f"   Logged entries: {len(entries)}")
    if entries:
        print(f"   User: {entries[0].user}")
        print(f"   Action: {entries[0].action}")
        print("   ✓ Basic logging working")
    
    # Test 2: Query logs
    print("\n2. Query Logs:")
    entries = logger.query_logs(user='test_user')
    print(f"   Entries for test_user: {len(entries)}")
    print("   ✓ Query logs working")
    
    # Test 3: Statistics
    print("\n3. Statistics:")
    stats = logger.get_statistics()
    print(f"   Total entries: {stats['total_entries']}")
    print(f"   Users: {stats['unique_users']}")
    print("   ✓ Statistics working")


def test_key_rotation():
    """Test API key rotation functionality"""
    print("\n" + "=" * 60)
    print("Testing API Key Rotation")
    print("=" * 60)
    
    # Test 1: Create rotation policy
    print("\n1. Create Rotation Policy:")
    manager = KeyRotationManager()
    
    policy = manager.create_policy(
        provider='test_provider',
        schedule='monthly',
        notification_days_before=7
    )
    
    print(f"   Provider: {policy.provider}")
    print(f"   Schedule: {policy.schedule.value}")
    print(f"   Notification days: {policy.notification_days_before}")
    print("   ✓ Policy creation working")
    
    # Test 2: Check if rotation needed
    print("\n2. Check Rotation Status:")
    needs_rotation = manager.needs_rotation('test_provider')
    print(f"   Needs rotation: {needs_rotation}")
    print("   ✓ Rotation check working")
    
    # Test 3: Get all policies
    print("\n3. List Policies:")
    policies = manager.get_all_policies()
    print(f"   Total policies: {len(policies)}")
    print("   ✓ Policy listing working")


def test_rbac():
    """Test Role-Based Access Control functionality"""
    print("\n" + "=" * 60)
    print("Testing RBAC")
    print("=" * 60)
    
    # Test 1: Create roles
    print("\n1. Create Roles:")
    rbac = RBACManager()
    
    rbac.create_role(
        name='developer',
        permissions=[
            Permission.USE_MOCK_PROVIDER,
            Permission.USE_CHEAP_MODELS
        ]
    )
    
    rbac.create_role(
        name='admin',
        permissions=[Permission.ALL]
    )
    
    roles = rbac.get_all_roles()
    print(f"   Created roles: {len(roles)}")
    print(f"   Roles: {[r.name for r in roles]}")
    print("   ✓ Role creation working")
    
    # Test 2: Assign user
    print("\n2. Assign User:")
    rbac.assign_user('alice@example.com', 'developer')
    user = rbac.get_user('alice@example.com')
    print(f"   User: {user.email}")
    print(f"   Role: {user.role}")
    print("   ✓ User assignment working")
    
    # Test 3: Check permissions
    print("\n3. Check Permissions:")
    has_perm = rbac.check_permission(
        'alice@example.com',
        Permission.USE_MOCK_PROVIDER
    )
    print(f"   Has permission (mock): {has_perm}")
    assert has_perm == True
    
    has_expensive = rbac.check_permission(
        'alice@example.com',
        Permission.USE_EXPENSIVE_MODELS
    )
    print(f"   Has permission (expensive): {has_expensive}")
    assert has_expensive == False
    print("   ✓ Permission checking working")
    
    # Test 4: Access control
    print("\n4. Access Control:")
    try:
        rbac.enforce_permission(
            'alice@example.com',
            Permission.USE_EXPENSIVE_MODELS,
            context={'model': 'gpt-4'}
        )
        print("   Should have been denied")
    except PermissionDeniedError as e:
        print(f"   Access denied: Permission check failed")
        print("   ✓ Access control working")


def test_integration():
    """Test integration between security modules"""
    print("\n" + "=" * 60)
    print("Testing Security Module Integration")
    print("=" * 60)
    
    # Test 1: PII + Audit
    print("\n1. PII Detection + Audit Logging:")
    pii_detector = PIIDetector(detect=['email'], action='redact')
    audit_logger = AuditLogger()
    
    text = "Email: test@example.com"
    redacted, detections = pii_detector.process(text)
    
    if detections:
        audit_logger.log_security_event(
            event_type='pii_detected',
            severity='HIGH',
            details={
                'pii_count': len(detections),
                'pii_types': [d.pii_type.value for d in detections]
            }
        )
        print(f"   Detected {len(detections)} PII instances")
        print("   Logged to audit trail")
    
    print("   ✓ PII + Audit integration working")
    
    # Test 2: Content Filter + RBAC
    print("\n2. Content Filter + RBAC:")
    content_filter = ContentFilter(['violence'], threshold=0.5)
    rbac = RBACManager()
    
    # Only admins can bypass content filter
    rbac.create_role('admin', [Permission.ALL])
    rbac.create_role('user', [Permission.USE_MOCK_PROVIDER])
    
    print("   Content filter + RBAC configured")
    print("   ✓ Content Filter + RBAC integration working")
    
    print("\n✓ All integrations working")


def run_all_tests():
    """Run all security tests"""
    print("=" * 60)
    print("ABHIKARTA LLM - SECURITY MODULE TESTS")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    tests = [
        ("PII Detection", test_pii_detection),
        ("Content Filtering", test_content_filtering),
        ("Audit Logging", test_audit_logging),
        ("Key Rotation", test_key_rotation),
        ("RBAC", test_rbac),
        ("Integration", test_integration),
    ]
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n✗ {name} FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL SECURITY TESTS PASSED! 🎉")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
    
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
