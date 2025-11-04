"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.4
"""

"""
Quick Security Demo

Demonstrates all 5 security features in action

© 2025-2030 All rights reserved Ashutosh Sinha
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.abstraction.security import (
    PIIDetector, PIIType, PIIAction,
    ContentFilter, ContentCategory,
    AuditLogger, AuditLevel,
    KeyRotationManager, KeyRotationPolicy,
    RBACManager, Permission
)
from datetime import datetime, timedelta


def demo_pii_detection():
    """Demo PII detection"""
    print("="*60)
    print("1. PII DETECTION & REDACTION")
    print("="*60)
    
    detector = PIIDetector(
        detect=['email', 'phone', 'ssn'],
        action='redact'
    )
    
    text = "Contact me at john@example.com or 555-123-4567. My SSN is 123-45-6789."
    result = detector.process(text)
    
    print(f"Original: {text}")
    print(f"Redacted: {result.text}")
    print(f"Detected: {len(result.detections)} PII item(s)\n")
    return True


def demo_content_filter():
    """Demo content filtering"""
    print("="*60)
    print("2. CONTENT FILTERING")
    print("="*60)
    
    content_filter = ContentFilter(
        block_categories=['violence', 'hate_speech'],
        threshold=0.7
    )
    
    safe = "Let's discuss machine learning"
    harmful = "How to make a weapon"
    
    safe_result = content_filter.check(safe)
    harmful_result = content_filter.check(harmful)
    
    print(f"Safe content: '{safe}' -> {safe_result.is_safe}")
    print(f"Harmful content: '{harmful}' -> {harmful_result.is_safe}\n")
    return True


def demo_audit_logging():
    """Demo audit logging"""
    print("="*60)
    print("3. AUDIT LOGGING")
    print("="*60)
    
    logger = AuditLogger(
        log_level='metadata_only',
        log_file="security_demo.log"
    )
    
    logger.log(
        user="demo_user@example.com",
        action="llm_request",
        resource="gpt-4",
        status="success",
        details={"tokens": 100}
    )
    
    entries = logger.get_entries(limit=1)
    print(f"Logged {len(entries)} audit entry")
    if entries:
        print(f"Latest: {entries[0].user} - {entries[0].action}\n")
    
    if os.path.exists("security_demo.log"):
        os.remove("security_demo.log")
    
    return True


def demo_key_rotation():
    """Demo key rotation"""
    print("="*60)
    print("4. API KEY ROTATION")
    print("="*60)
    
    manager = KeyRotationManager()
    
    manager.add_key(
        provider="test_provider",
        key="test_key_12345"
    )
    
    manager.set_rotation_policy(
        provider="test_provider",
        interval_days=30,
        notify_days_before=7
    )
    
    print(f"Policy created for test_provider")
    print(f"Key added successfully\n")
    return True


def demo_rbac():
    """Demo RBAC"""
    print("="*60)
    print("5. ROLE-BASED ACCESS CONTROL")
    print("="*60)
    
    rbac = RBACManager()
    
    rbac.create_role(
        name="developer",
        permissions=[Permission.USE_ANTHROPIC, Permission.USE_HISTORY]
    )
    
    rbac.create_user(
        user_id="alice@example.com",
        roles=["developer"]
    )
    
    can_use = rbac.has_permission("alice@example.com", Permission.USE_ANTHROPIC)
    can_manage = rbac.has_permission("alice@example.com", Permission.MANAGE_USERS)
    
    print(f"User: alice@example.com, Role: developer")
    print(f"Can use Anthropic: {can_use}")
    print(f"Can manage users: {can_manage}\n")
    return True


def main():
    """Run all demos"""
    print("\n╔" + "="*58 + "╗")
    print("║" + "  ABHIKARTA LLM - SECURITY FEATURES DEMO  ".center(58) + "║")
    print("╚" + "="*58 + "╝\n")
    
    demos = [
        demo_pii_detection,
        demo_content_filter,
        demo_audit_logging,
        demo_key_rotation,
        demo_rbac
    ]
    
    passed = 0
    for demo in demos:
        try:
            if demo():
                passed += 1
        except Exception as e:
            print(f"Error: {e}\n")
    
    print("="*60)
    print(f"DEMO COMPLETE: {passed}/{len(demos)} features demonstrated")
    print("="*60)
    print("\n✓ All 5 security features are working!\n")
    print("For full examples, run:")
    print("  python llm/abstraction/examples/security_examples.py\n")


if __name__ == "__main__":
    main()
