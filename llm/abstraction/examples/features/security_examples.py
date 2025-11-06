"""
Security Features Examples

Demonstrates all 5 security features:
1. PII Detection & Redaction
2. Content Filtering
3. Audit Logging
4. API Key Rotation
5. Role-Based Access Control (RBAC)

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
llm_config_path = '/home/ashutosh/PycharmProjects/abhikarta-llm/config/llm_config.json'

from llm.abstraction import LLMClientFactory
from llm.abstraction.security import (
    PIIDetector, PIIAction,
    ContentFilter,
    AuditLogger,
    KeyRotationManager,
    RBACManager, Permission,
    redact_pii
)


def example_pii_detection():
    """Example 1: PII Detection and Redaction"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: PII DETECTION & REDACTION")
    print("=" * 70)
    
    print("\n📧 Protecting Privacy with PII Detection\n")
    
    # Simple redaction
    print("1. Simple Redaction:")
    text = "My email is john.doe@example.com and SSN is 123-45-6789"
    print(f"   Original: {text}")
    
    redacted = redact_pii(text)
    print(f"   Redacted: {redacted}")
    
    # Advanced detection with multiple types
    print("\n2. Detect Multiple PII Types:")
    detector = PIIDetector(
        detect=['email', 'phone', 'ssn', 'credit_card'],
        action='redact'
    )
    
    text = """
    Contact Information:
    Email: alice@company.com
    Phone: 555-123-4567
    SSN: 987-65-4321
    Card: 4532-1234-5678-9010
    """
    
    redacted, detections = detector.process(text)
    print(f"   Found {len(detections)} PII instances:")
    for d in detections:
        print(f"   - {d.pii_type.value}: {d.value} (confidence: {d.confidence:.2f})")
    
    print(f"\n   Redacted text:\n{redacted}")
    
    # Masking instead of full redaction
    print("\n3. Partial Masking (for display purposes):")
    masker = PIIDetector(detect=['credit_card', 'ssn'], action='mask')
    
    text = "Card: 4532-1234-5678-9010, SSN: 123-45-6789"
    masked, _ = masker.process(text)
    
    print(f"   Original: {text}")
    print(f"   Masked:   {masked}")
    
    # Integration with LLM client
    print("\n4. Automatic PII Protection in LLM Calls:")
    factory = LLMClientFactory()
    factory.initialize()
    
    client = factory.create_default_client()
    pii_detector = PIIDetector(detect=['email', 'phone'], action='redact')
    
    # User prompt with PII
    user_prompt = "Send an email to bob@example.com about the call at 555-1234"
    
    # Redact before sending to LLM
    safe_prompt, _ = pii_detector.process(user_prompt)
    
    print(f"   User prompt: {user_prompt}")
    print(f"   Safe prompt: {safe_prompt}")
    
    response = client.complete(safe_prompt)
    print(f"   Response: {response[:100]}...")
    
    print("\n✅ PII Protection Active!")


def example_content_filtering():
    """Example 2: Content Filtering"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: CONTENT FILTERING")
    print("=" * 70)
    
    print("\n🛡️  Blocking Harmful Content\n")
    
    # Basic content filter
    print("1. Basic Content Filter:")
    filter = ContentFilter(
        block_categories=['hate_speech', 'violence'],
        threshold=0.6
    )
    
    # Test safe content
    safe_texts = [
        "I love programming in Python!",
        "Let's work together on this project",
        "The weather is nice today"
    ]
    
    print("   Testing safe content:")
    for text in safe_texts:
        try:
            result = filter.check(text)
            print(f"   ✓ '{text[:40]}...' - PASS (score: {result.max_score:.2f})")
        except Exception as e:
            print(f"   ✗ '{text[:40]}...' - BLOCKED")
    
    # Custom thresholds per category
    print("\n2. Category-Specific Thresholds:")
    filter = ContentFilter(
        block_categories=['violence', 'sexual_content', 'self_harm'],
        threshold=0.7,
        category_thresholds={
            'violence': 0.5,      # More strict
            'self_harm': 0.3      # Very strict
        }
    )
    
    print(f"   Monitoring {len(filter.get_categories())} categories")
    print("   Different thresholds per category configured")
    
    # Integration with LLM
    print("\n3. Content Filter + LLM Integration:")
    factory = LLMClientFactory()
    factory.initialize()
    client = factory.create_default_client()
    
    content_filter = ContentFilter(['violence'], threshold=0.5)
    
    prompts = [
        "Write a story about friendship",
        "How to make a bomb"  # Should be blocked
    ]
    
    for prompt in prompts:
        try:
            # Check content before sending
            content_filter.check(prompt)
            print(f"   ✓ Prompt allowed: '{prompt}'")
            response = client.complete(prompt)
            print(f"     Response: {response[:60]}...")
        except Exception as e:
            print(f"   ✗ Prompt blocked: '{prompt}'")
            print(f"     Reason: {e}")
    
    print("\n✅ Content Filter Active!")


def example_audit_logging():
    """Example 3: Audit Logging"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: AUDIT LOGGING")
    print("=" * 70)
    
    print("\n📝 Complete Activity Tracking\n")
    
    # Initialize audit logger
    print("1. Initialize Audit Logger:")
    logger = AuditLogger(
        log_level='FULL',
        retention_days=90,
        encryption=True
    )
    
    print("   Audit logger initialized")
    print("   - Log level: FULL")
    print("   - Retention: 90 days")
    print("   - Encryption: Enabled")
    
    # Log various activities
    print("\n2. Log LLM Activities:")
    
    # Log request
    logger.log_request(
        user='alice@company.com',
        action='complete',
        resource='gpt-4',
        details={
            'prompt': 'Analyze this data...',
            'max_tokens': 1000,
            'temperature': 0.7
        }
    )
    print("   ✓ Logged: API request")
    
    # Log response
    logger.log_response(
        user='alice@company.com',
        action='complete',
        resource='gpt-4',
        success=True,
        details={
            'tokens_used': 750,
            'cost': 0.015,
            'latency_ms': 1234
        }
    )
    print("   ✓ Logged: API response")
    
    # Log security event
    logger.log_security_event(
        event_type='pii_detected',
        severity='HIGH',
        details={
            'pii_types': ['email', 'ssn'],
            'count': 2,
            'action_taken': 'redacted'
        }
    )
    print("   ✓ Logged: Security event")
    
    # Query logs
    print("\n3. Query Audit Logs:")
    
    # Get recent logs
    recent = logger.get_logs(limit=5)
    print(f"   Recent entries: {len(recent)}")
    
    # Query by user
    user_logs = logger.query_logs(user='alice@company.com')
    print(f"   Alice's activities: {len(user_logs)}")
    
    # Get statistics
    stats = logger.get_statistics()
    print(f"\n   Statistics:")
    print(f"   - Total entries: {stats['total_entries']}")
    print(f"   - Unique users: {stats['unique_users']}")
    print(f"   - Date range: {stats['date_range']['start']} to {stats['date_range']['end']}")
    
    # Export logs
    print("\n4. Export Audit Trail:")
    logger.export_logs('audit_trail.json', format='json')
    print("   ✓ Exported to: audit_trail.json")
    
    print("\n✅ Full Audit Trail Maintained!")


def example_key_rotation():
    """Example 4: API Key Rotation"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: API KEY ROTATION")
    print("=" * 70)
    
    print("\n🔑 Automated Key Management\n")
    
    # Initialize key rotation manager
    print("1. Setup Key Rotation:")
    manager = KeyRotationManager()
    
    # Create rotation policies
    policies = [
        ('anthropic', 'monthly', 7),
        ('openai', 'quarterly', 14),
        ('google', 'monthly', 7),
    ]
    
    for provider, schedule, notification in policies:
        policy = manager.create_policy(
            provider=provider,
            schedule=schedule,
            notification_days_before=notification,
            auto_rotate=False  # Manual approval required
        )
        print(f"   ✓ Policy created: {provider}")
        print(f"     - Schedule: {schedule}")
        print(f"     - Notification: {notification} days before")
    
    # Check rotation status
    print("\n2. Check Rotation Status:")
    for provider in ['anthropic', 'openai', 'google']:
        needs_rotation = manager.needs_rotation(provider)
        days_until = manager.days_until_rotation(provider)
        
        status = "⚠️  NEEDS ROTATION" if needs_rotation else "✓ OK"
        print(f"   {provider}: {status}")
        if days_until is not None:
            print(f"     Days until rotation: {days_until}")
    
    # Get upcoming rotations
    print("\n3. Upcoming Rotations:")
    upcoming = manager.get_upcoming_rotations(days=30)
    print(f"   Rotations in next 30 days: {len(upcoming)}")
    for rotation in upcoming:
        print(f"   - {rotation['provider']}: {rotation['scheduled_date']}")
    
    # Manual rotation
    print("\n4. Manual Key Rotation:")
    print("   Rotating anthropic key...")
    
    # In production, this would:
    # 1. Generate new key in provider dashboard
    # 2. Update environment variables
    # 3. Verify new key works
    # 4. Deactivate old key after grace period
    
    new_key = "sk-ant-new-key-123456"  # Example
    manager.rotate_key(
        provider='anthropic',
        new_key=new_key,
        verify=False  # Skip verification for example
    )
    
    print("   ✓ Key rotated successfully")
    print("   ✓ Old key will be deactivated in 24 hours")
    
    print("\n✅ API Keys Secure and Up-to-Date!")


def example_rbac():
    """Example 5: Role-Based Access Control"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: ROLE-BASED ACCESS CONTROL (RBAC)")
    print("=" * 70)
    
    print("\n🔐 Fine-Grained Access Control\n")
    
    # Initialize RBAC
    print("1. Setup Roles and Permissions:")
    rbac = RBACManager()
    
    # Create roles
    rbac.create_role(
        name='developer',
        permissions=[
            Permission.USE_MOCK_PROVIDER,
            Permission.USE_CHEAP_MODELS,
            Permission.READ_HISTORY
        ],
        description='Standard developer access'
    )
    
    rbac.create_role(
        name='analyst',
        permissions=[
            Permission.USE_CHEAP_MODELS,
            Permission.USE_MEDIUM_MODELS,
            Permission.READ_HISTORY,
            Permission.EXPORT_DATA
        ],
        description='Data analyst access'
    )
    
    rbac.create_role(
        name='admin',
        permissions=[Permission.ALL],
        description='Full administrative access'
    )
    
    print("   ✓ Created 3 roles: developer, analyst, admin")
    
    # Assign users
    print("\n2. Assign Users to Roles:")
    users = [
        ('alice@company.com', 'developer'),
        ('bob@company.com', 'analyst'),
        ('charlie@company.com', 'admin'),
    ]
    
    for email, role in users:
        rbac.assign_user(email, role)
        print(f"   ✓ {email} → {role}")
    
    # Check permissions
    print("\n3. Check Access Permissions:")
    
    test_cases = [
        ('alice@company.com', Permission.USE_MOCK_PROVIDER, True),
        ('alice@company.com', Permission.USE_EXPENSIVE_MODELS, False),
        ('bob@company.com', Permission.USE_MEDIUM_MODELS, True),
        ('charlie@company.com', Permission.ALL, True),
    ]
    
    for user, permission, expected in test_cases:
        has_permission = rbac.check_permission(user, permission)
        status = "✓" if has_permission == expected else "✗"
        print(f"   {status} {user} → {permission.value}: {has_permission}")
    
    # Enforce access control
    print("\n4. Enforce Access Control:")
    
    factory = LLMClientFactory()
    factory.initialize()
    
    # Alice tries to use expensive model
    print("\n   Alice (developer) tries to use GPT-4:")
    try:
        rbac.enforce_permission(
            'alice@company.com',
            Permission.USE_EXPENSIVE_MODELS,
            context={'model': 'gpt-4', 'estimated_cost': 0.05}
        )
        print("   ✓ Access granted")
    except Exception as e:
        print(f"   ✗ Access denied: {e}")
    
    # Alice can use cheap models
    print("\n   Alice (developer) tries to use mock provider:")
    try:
        rbac.enforce_permission(
            'alice@company.com',
            Permission.USE_MOCK_PROVIDER
        )
        print("   ✓ Access granted")
        
        client = factory.create_default_client()
        response = client.complete("Hello!")
        print(f"   Response: {response[:50]}...")
    except Exception as e:
        print(f"   ✗ Access denied: {e}")
    
    # Usage statistics
    print("\n5. Access Statistics:")
    stats = rbac.get_statistics()
    print(f"   Total users: {stats['total_users']}")
    print(f"   Total roles: {stats['total_roles']}")
    print(f"   Role distribution:")
    for role, count in stats['users_by_role'].items():
        print(f"   - {role}: {count} users")
    
    print("\n✅ Access Control Enforced!")


def example_integrated_security():
    """Example: All Security Features Together"""
    print("\n" + "=" * 70)
    print("BONUS: INTEGRATED SECURITY EXAMPLE")
    print("=" * 70)
    
    print("\n🔒 Complete Security Pipeline\n")
    
    # Initialize all security components
    print("1. Initialize Security Components:")
    
    pii_detector = PIIDetector(detect=['email', 'ssn', 'phone'], action='redact')
    content_filter = ContentFilter(['violence', 'hate_speech'], threshold=0.6)
    audit_logger = AuditLogger(log_level='FULL')
    rbac = RBACManager()
    
    # Setup RBAC
    rbac.create_role('user', [Permission.USE_MOCK_PROVIDER])
    rbac.assign_user('test@example.com', 'user')
    
    print("   ✓ PII Detector ready")
    print("   ✓ Content Filter ready")
    print("   ✓ Audit Logger ready")
    print("   ✓ RBAC ready")
    
    # Secure LLM pipeline
    print("\n2. Secure LLM Request Pipeline:")
    
    user_email = 'test@example.com'
    user_prompt = "My SSN is 123-45-6789. Email me at test@example.com"
    
    try:
        # Step 1: Check RBAC
        print(f"\n   Step 1: Check permissions for {user_email}")
        rbac.enforce_permission(user_email, Permission.USE_MOCK_PROVIDER)
        print("   ✓ Permission granted")
        
        # Step 2: Content filter
        print(f"\n   Step 2: Content filtering")
        content_filter.check(user_prompt)
        print("   ✓ Content approved")
        
        # Step 3: PII detection and redaction
        print(f"\n   Step 3: PII detection")
        safe_prompt, detections = pii_detector.process(user_prompt)
        print(f"   Original: {user_prompt}")
        print(f"   Redacted: {safe_prompt}")
        print(f"   ✓ {len(detections)} PII instances redacted")
        
        # Step 4: Make LLM request
        print(f"\n   Step 4: LLM request")
        factory = LLMClientFactory()
        factory.initialize()
        client = factory.create_default_client()
        
        response = client.complete(safe_prompt)
        print(f"   ✓ Response received: {response[:50]}...")
        
        # Step 5: Audit logging
        print(f"\n   Step 5: Audit logging")
        audit_logger.log_request(
            user=user_email,
            action='complete',
            resource='mock-model',
            details={
                'original_prompt': user_prompt,
                'safe_prompt': safe_prompt,
                'pii_detected': len(detections),
                'pii_types': [d.pii_type.value for d in detections]
            }
        )
        print("   ✓ Activity logged")
        
        print("\n✅ SECURE REQUEST COMPLETED!")
        print("   All security checks passed")
        print("   PII protected")
        print("   Content filtered")
        print("   Access controlled")
        print("   Fully audited")
        
    except Exception as e:
        print(f"\n✗ Request blocked: {e}")
        audit_logger.log_security_event(
            event_type='access_denied',
            severity='HIGH',
            details={'user': user_email, 'reason': str(e)}
        )


def main():
    """Run all security examples"""
    print("=" * 70)
    print("ABHIKARTA LLM - SECURITY FEATURES EXAMPLES")
    print("=" * 70)
    print("\nDemonstrating 5 Security Features:")
    print("1. PII Detection & Redaction")
    print("2. Content Filtering")
    print("3. Audit Logging")
    print("4. API Key Rotation")
    print("5. Role-Based Access Control (RBAC)")
    print("\n" + "=" * 70)
    
    try:
        example_pii_detection()
        example_content_filtering()
        example_audit_logging()
        example_key_rotation()
        example_rbac()
        example_integrated_security()
        
        print("\n" + "=" * 70)
        print("🎉 ALL SECURITY EXAMPLES COMPLETED SUCCESSFULLY! 🎉")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
