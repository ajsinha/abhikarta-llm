# Abhikarta LLM Security Framework
## Comprehensive Technical Documentation

---

**Version:** 1.0  
**Date:** November 7, 2025  
**Status:** Confidential - Internal Use Only

---

## Copyright and Legal Notice

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email:** ajsinha@gmail.com  
**GitHub:** https://www.github.com/ajsinha/abhikarta

### Legal Notice

This document and the associated software architecture are proprietary and confidential. Unauthorized copying, distribution, modification, or use of this document or the software system it describes is strictly prohibited without explicit written permission from the copyright holder. 

This document is provided "as is" without warranty of any kind, either expressed or implied. The copyright holder shall not be liable for any damages arising from the use of this document or the software system it describes.

**Patent Pending:** Certain architectural patterns and implementations described in this document may be subject to patent applications.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Core Components](#core-components)
   - 3.1 [PII Detection and Redaction](#pii-detection-and-redaction)
   - 3.2 [Content Filtering](#content-filtering)
   - 3.3 [Audit Logging](#audit-logging)
   - 3.4 [API Key Rotation](#api-key-rotation)
   - 3.5 [Role-Based Access Control (RBAC)](#role-based-access-control)
4. [System Architecture Diagrams](#system-architecture-diagrams)
5. [Implementation Guide](#implementation-guide)
6. [Usage Examples](#usage-examples)
7. [API Reference](#api-reference)
8. [Security Best Practices](#security-best-practices)
9. [Performance Considerations](#performance-considerations)
10. [Compliance and Regulations](#compliance-and-regulations)
11. [Troubleshooting](#troubleshooting)
12. [Appendix](#appendix)

---

## 1. Executive Summary

The **Abhikarta LLM Security Framework** is a comprehensive, enterprise-grade security solution designed to protect Large Language Model (LLM) applications from data breaches, unauthorized access, and compliance violations. This framework provides a multi-layered defense strategy that addresses the unique security challenges posed by AI systems.

### Key Features

- **PII Detection & Redaction**: Automatic identification and removal of personally identifiable information
- **Content Filtering**: Real-time filtering of harmful, inappropriate, or policy-violating content
- **Audit Logging**: Comprehensive tracking of all LLM operations for compliance and forensics
- **Key Rotation**: Automated API key management with zero-downtime rotation
- **RBAC**: Granular role-based access control for resource management
- **Multi-Provider Support**: Compatible with Anthropic, OpenAI, and other LLM providers

### Use Cases

- **Healthcare Applications**: HIPAA-compliant LLM systems with PHI protection
- **Financial Services**: PCI-DSS compliant systems with credit card data protection
- **Enterprise Chatbots**: Secure internal tools with proper access control
- **Customer Service**: Content-filtered responses with audit trails
- **Government Systems**: High-security deployments with comprehensive logging

---

## 2. Architecture Overview

The Abhikarta Security Framework employs a **layered security architecture** that intercepts and protects data at multiple points in the LLM pipeline.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Input                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SECURITY LAYER 1                             │
│                   ┌─────────────────────┐                        │
│                   │  Content Filter     │                        │
│                   │  (Harmful Content)  │                        │
│                   └─────────────────────┘                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SECURITY LAYER 2                             │
│                   ┌─────────────────────┐                        │
│                   │   PII Detector      │                        │
│                   │  (Data Protection)  │                        │
│                   └─────────────────────┘                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SECURITY LAYER 3                             │
│                   ┌─────────────────────┐                        │
│                   │   RBAC Manager      │                        │
│                   │ (Access Control)    │                        │
│                   └─────────────────────┘                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AUDIT LOGGING                                │
│                   (All Operations Tracked)                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LLM Provider                                │
│              (Anthropic, OpenAI, etc.)                           │
│                   ┌─────────────────────┐                        │
│                   │  Key Rotation       │                        │
│                   │   (API Security)    │                        │
│                   └─────────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

### Security Principles

1. **Defense in Depth**: Multiple independent layers of security
2. **Least Privilege**: Minimal access rights for users and processes
3. **Zero Trust**: Verify all requests regardless of source
4. **Audit Everything**: Complete logging for accountability
5. **Fail Secure**: System fails to secure state, not open state

---

## 3. Core Components

### 3.1 PII Detection and Redaction

The PII Detection module identifies and protects personally identifiable information using advanced pattern matching and validation algorithms.

#### Supported PII Types

| PII Type | Description | Example | Validation Method |
|----------|-------------|---------|-------------------|
| EMAIL | Email addresses | john@example.com | Regex + domain validation |
| PHONE | Phone numbers | (555) 123-4567 | Regex + format validation |
| SSN | Social Security Numbers | 123-45-6789 | Regex + checksum validation |
| CREDIT_CARD | Credit card numbers | 4532-1234-5678-9010 | Luhn algorithm |
| IP_ADDRESS | IP addresses | 192.168.1.1 | Range validation |
| DATE_OF_BIRTH | Dates of birth | 01/15/1990 | Date validation |
| PASSPORT | Passport numbers | AB1234567 | Format validation |
| BANK_ACCOUNT | Bank account numbers | 123456789012 | Length + format |

#### Detection Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Input Text                                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │  Pattern Matching Engine      │
            │  ┌─────────────────────────┐  │
            │  │ Regex Patterns          │  │
            │  └─────────────────────────┘  │
            │  ┌─────────────────────────┐  │
            │  │ Keyword Detection       │  │
            │  └─────────────────────────┘  │
            │  ┌─────────────────────────┐  │
            │  │ Custom Patterns         │  │
            │  └─────────────────────────┘  │
            └───────────────┬───────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │  Validation Layer             │
            │  ┌─────────────────────────┐  │
            │  │ Luhn Algorithm (Cards)  │  │
            │  │ Format Validators       │  │
            │  │ Confidence Scoring      │  │
            │  └─────────────────────────┘  │
            └───────────────┬───────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │  Action Handler               │
            │  ┌─────────────────────────┐  │
            │  │ REDACT → [EMAIL_REDACTED]│ │
            │  │ MASK   → j***@e***.com  │  │
            │  │ HASH   → [HASH:a3f2...] │  │
            │  │ BLOCK  → Raise Exception│  │
            │  │ ALERT  → Log Warning    │  │
            │  └─────────────────────────┘  │
            └───────────────┬───────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Protected Output                             │
└─────────────────────────────────────────────────────────────────┘
```

#### Code Example: Basic PII Detection

```python
from abhikarta.security import PIIDetector, PIIType, PIIAction

# Initialize detector
detector = PIIDetector(
    detect=['email', 'phone', 'ssn', 'credit_card'],
    action='redact',
    confidence_threshold=0.8
)

# Process text
text = """
Contact John at john.doe@example.com or call (555) 123-4567.
His SSN is 123-45-6789 and credit card is 4532-1234-5678-9010.
"""

result = detector.process(text)

print(result.redacted_text)
# Output:
# Contact John at [EMAIL_REDACTED] or call [PHONE_REDACTED].
# His SSN is [SSN_REDACTED] and credit card is [CREDIT_CARD_REDACTED].

print(f"Detected {len(result.matches)} PII items")
for match in result.matches:
    print(f"- {match.pii_type.value} with confidence {match.confidence}")
```

#### Code Example: Custom PII Patterns

```python
# Add custom patterns for organization-specific data
custom_patterns = {
    'employee_id': r'\bEMP-\d{6}\b',
    'project_code': r'\bPROJ-[A-Z]{3}-\d{4}\b'
}

detector = PIIDetector(
    detect=['email', 'phone'],
    custom_patterns=custom_patterns,
    action='mask'
)

text = "Employee EMP-123456 is working on PROJ-ABC-2024"
result = detector.process(text)
print(result.redacted_text)
```

#### Standalone Functions

```python
from abhikarta.security import (
    detect_pii,      # Detect PII without modification
    redact_pii,      # Redact PII from text
    mask_pii,        # Mask PII (show partial)
    hash_pii,        # Hash PII for pseudonymization
    has_pii,         # Check if text contains PII
    count_pii,       # Count PII by type
    clean_text_for_llm  # Quick cleanup for LLM input
)

# Quick check
if has_pii(user_input):
    print("Warning: PII detected!")

# Clean text before sending to LLM
clean_input = clean_text_for_llm(user_input)
response = llm_client.complete(clean_input)

# Get PII statistics
counts = count_pii(text)
print(f"Found {counts.get('email', 0)} emails and {counts.get('phone', 0)} phones")
```

---

### 3.2 Content Filtering

The Content Filter module protects against harmful, inappropriate, or policy-violating content before it reaches LLM providers or users.

#### Filtered Content Categories

```
┌─────────────────────────────────────────────────────────────────┐
│                   CONTENT CATEGORIES                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  HIGH RISK (Block Immediately)                                   │
│  ├─ HATE_SPEECH         : Discriminatory content                │
│  ├─ VIOLENCE            : Violent or threatening content         │
│  ├─ SELF_HARM           : Self-harm or suicide content          │
│  ├─ SEXUAL_CONTENT      : Explicit sexual content               │
│  └─ ILLEGAL_ACTIVITY    : Instructions for illegal acts         │
│                                                                  │
│  MEDIUM RISK (Warn or Sanitize)                                 │
│  ├─ HARASSMENT          : Bullying or harassment                │
│  ├─ PERSONAL_ATTACKS    : Ad hominem attacks                    │
│  ├─ DISCRIMINATION      : Discriminatory language               │
│  └─ PROFANITY           : Profane language                      │
│                                                                  │
│  LOW RISK (Log or Monitor)                                      │
│  ├─ SPAM                : Spam content                          │
│  ├─ MISINFORMATION      : Potentially false information         │
│  └─ MALWARE             : Malicious URLs or code                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Filter Actions

| Action | Description | Use Case |
|--------|-------------|----------|
| BLOCK | Reject request completely | High-risk content |
| WARN | Allow with warning | Medium-risk content |
| SANITIZE | Remove harmful parts | Mixed content |
| LOG | Log for review | Low-risk monitoring |

#### Code Example: Content Filtering

```python
from abhikarta.security import ContentFilter, ContentCategory, FilterAction

# Initialize filter
content_filter = ContentFilter(
    block_categories=[
        'hate_speech',
        'violence',
        'sexual_content',
        'self_harm',
        'illegal_activity'
    ],
    threshold=0.8,
    action='block',
    whitelist=['medical terms', 'educational content']
)

# Process user input
user_input = "How do I make a bomb?"

try:
    result = content_filter.process(user_input)
    
    if result.was_blocked:
        print("Content blocked due to policy violation")
        print(f"Categories: {[m.category.value for m in result.matches]}")
    else:
        # Safe to proceed
        llm_response = llm_client.complete(result.filtered_text)
        
except ContentFilterException as e:
    print(f"Content filter exception: {e}")
    # Log incident
    # Return error to user
```

#### Code Example: Custom Filter Rules

```python
from abhikarta.security import FilterRule, ContentCategory

# Define custom rule
custom_rule = FilterRule(
    name="company_secrets",
    category=ContentCategory.ILLEGAL_ACTIVITY,
    patterns=[
        r'\b(confidential|proprietary|trade secret)\b',
        r'\bProject\s+Titan\b'  # Company code name
    ],
    keywords=['internal only', 'do not share'],
    confidence=0.95,
    enabled=True
)

# Add to filter
content_filter.add_rule(custom_rule)

# Test
text = "Our confidential Project Titan data shows..."
result = content_filter.process(text)
if result.was_blocked:
    print("Company confidential information detected!")
```

#### Statistics and Monitoring

```python
# Get filtering statistics
stats = content_filter.get_statistics()
print(f"Total checks: {stats['total_checks']}")
print(f"Total blocks: {stats['total_blocks']}")
print(f"Total warnings: {stats['total_warnings']}")

# Category breakdown
for category, count in stats['category_counts'].items():
    print(f"- {category}: {count}")
```

---

### 3.3 Audit Logging

The Audit Logger provides comprehensive tracking of all LLM operations for compliance, security monitoring, and forensic analysis.

#### Audit Event Types

```
┌─────────────────────────────────────────────────────────────────┐
│                      AUDIT EVENT TYPES                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  OPERATIONAL EVENTS                                              │
│  ├─ API_CALL            : LLM API requests/responses            │
│  ├─ CACHE_HIT           : Cache hit events                      │
│  ├─ CACHE_MISS          : Cache miss events                     │
│  └─ CONFIGURATION_CHANGE: System config changes                 │
│                                                                  │
│  SECURITY EVENTS                                                 │
│  ├─ AUTHENTICATION      : Login attempts                        │
│  ├─ AUTHORIZATION       : Access control checks                 │
│  ├─ PII_DETECTION       : PII detected/redacted                 │
│  ├─ CONTENT_FILTER      : Content filtered/blocked              │
│  ├─ SECURITY_ALERT      : Security incidents                    │
│  └─ RATE_LIMIT          : Rate limit violations                 │
│                                                                  │
│  FINANCIAL EVENTS                                                │
│  ├─ COST_THRESHOLD      : Cost limit warnings                   │
│  └─ TOKEN_USAGE         : Token consumption tracking            │
│                                                                  │
│  ERROR EVENTS                                                    │
│  └─ ERROR               : System errors                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Audit Levels

| Level | Data Logged | Use Case |
|-------|-------------|----------|
| NONE | No logging | Development/testing |
| METADATA_ONLY | Metadata without content | Production (privacy) |
| FULL | Complete request/response | Debugging/investigation |
| FULL_ENCRYPTED | Encrypted full data | High-security environments |

#### Code Example: Basic Audit Logging

```python
from abhikarta.security import AuditLogger, AuditLevel

# Initialize audit logger
audit = AuditLogger(
    log_level='FULL',
    log_dir='logs/audit',
    retention_days=90,
    encryption=True,
    encryption_key='your-encryption-key-here',
    rotate_daily=True
)

# Log API call
event_id = audit.log_api_call(
    user_id='user123',
    provider='anthropic',
    model='claude-sonnet-4-20250514',
    operation='completion',
    prompt='Hello, how are you?',
    response='I am doing well, thank you!',
    tokens=25,
    cost=0.0025,
    latency_ms=342.5,
    status='success',
    session_id='session_abc123',
    ip_address='192.168.1.100'
)

print(f"Logged event: {event_id}")
```

#### Code Example: Security Event Logging

```python
# Log authentication attempt
audit.log_authentication(
    user_id='john.doe',
    status='success',
    auth_method='api_key',
    ip_address='10.0.0.5'
)

# Log authorization check
audit.log_authorization(
    user_id='john.doe',
    resource='model:claude-opus',
    action='complete',
    status='allowed'
)

# Log PII detection
audit.log_pii_detection(
    user_id='john.doe',
    pii_types=['email', 'ssn'],
    action_taken='redacted'
)

# Log content filter event
audit.log_content_filter(
    user_id='john.doe',
    categories=['violence', 'hate_speech'],
    action_taken='blocked'
)

# Log security alert
audit.log_security_alert(
    alert_type='suspicious_activity',
    severity='high',
    description='Multiple failed auth attempts from same IP',
    user_id='unknown',
    ip_address='203.0.113.42'
)
```

#### Audit Data Structure

```python
# Example audit event structure
{
    "event_id": "a3f2d8e1b4c5",
    "timestamp": "2025-11-07T14:32:15.123Z",
    "event_type": "api_call",
    "user_id": "user123",
    "session_id": "session_abc123",
    "ip_address": "192.168.1.100",
    "provider": "anthropic",
    "model": "claude-sonnet-4-20250514",
    "operation": "completion",
    "status": "success",
    "tokens_used": 25,
    "cost": 0.0025,
    "latency_ms": 342.5,
    "pii_detected": false,
    "content_filtered": false,
    "metadata": {
        "user_agent": "Mozilla/5.0...",
        "request_source": "web_app"
    }
}
```

#### Statistics and Reporting

```python
# Get audit statistics
stats = audit.get_statistics()
print(f"Total events logged: {stats['total_events']}")
print(f"Total tokens used: {stats['total_tokens']}")
print(f"Total cost: ${stats['total_cost']}")

# Event breakdown
for event_type, count in stats['event_counts'].items():
    print(f"- {event_type}: {count}")

# Export logs for compliance
audit.export_logs(
    start_date=datetime(2025, 10, 1),
    end_date=datetime(2025, 10, 31),
    event_types=['api_call', 'security_alert'],
    output_file='october_audit_report.json'
)

# Cleanup old logs
deleted_count = audit.cleanup_old_logs()
print(f"Deleted {deleted_count} old log files")
```

---

### 3.4 API Key Rotation

The Key Rotation Manager provides automated API key management with zero-downtime rotation to enhance security and comply with security policies.

#### Key Rotation Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   KEY ROTATION LIFECYCLE                         │
└─────────────────────────────────────────────────────────────────┘

TIME PERIOD         KEY STATUS                  ACTION
────────────────────────────────────────────────────────────────────

Day 0-7            ┌─────────────┐
                   │   KEY_OLD   │ ─────────┐
                   │  (Active)   │          │  Both keys active
                   └─────────────┘          │  (Transition period)
                   ┌─────────────┐          │
                   │   KEY_NEW   │ ─────────┘
                   │  (Active)   │
                   └─────────────┘

Day 7              ┌─────────────┐
                   │   KEY_OLD   │ ────────> Deactivated
                   │ (Inactive)  │
                   └─────────────┘
                   ┌─────────────┐
                   │   KEY_NEW   │ ────────> Primary key
                   │  (Primary)  │
                   └─────────────┘

Day 90             ┌─────────────┐
                   │   KEY_NEW   │ ────────> Rotation due
                   │  (Primary)  │
                   └─────────────┘
                          │
                          ▼
                   Generate KEY_NEXT
                   Start new cycle
```

#### Rotation Policy Configuration

```python
from abhikarta.security import KeyRotationManager, KeyRotationPolicy

# Define rotation policy
policy = KeyRotationPolicy(
    rotation_interval_days=90,    # Rotate every 90 days
    warning_days_before=7,        # Warn 7 days before expiry
    auto_rotate=True,             # Enable auto-rotation
    keep_old_key_days=7,          # Keep old key active for 7 days
    max_key_age_days=365          # Force rotation after 365 days
)

# Initialize key manager
key_manager = KeyRotationManager(
    storage_path='.keys',
    policy=policy,
    notification_callback=send_notification
)
```

#### Code Example: Register and Rotate Keys

```python
# Register API key for a provider
key_manager.register_provider(
    provider='anthropic',
    api_key='sk-ant-api03-abc123...',
)

# Get active key for use
active_key = key_manager.get_active_key('anthropic')
print(f"Using API key: {active_key[:20]}...")

# Manual rotation when needed
new_key = generate_new_api_key()  # Your key generation logic
success = key_manager.rotate_key(
    provider='anthropic',
    new_key=new_key,
    immediate=False  # Gradual rollover
)

if success:
    print("Key rotation initiated successfully")
```

#### Code Example: Monitoring and Notifications

```python
# Check key status
status = key_manager.get_status()
for provider, info in status.items():
    print(f"Provider: {provider}")
    print(f"  Active: {info['active']}")
    print(f"  Age: {info['age_days']} days")
    print(f"  Days until expiry: {info['days_until_expiry']}")
    print(f"  Should rotate: {info['should_rotate']}")
    print(f"  Rotation count: {info['rotation_count']}")

# Manual check and notify
key_manager.check_and_notify()

# Notification callback
def send_notification(event, provider, key_id, **kwargs):
    if event == 'key_expired':
        send_alert(f"URGENT: API key for {provider} has expired!")
    elif event == 'rotation_recommended':
        send_email(f"Please rotate API key for {provider}")
    elif event == 'expiry_warning':
        days = kwargs.get('days_remaining')
        send_email(f"Key for {provider} expires in {days} days")

# Cleanup old inactive keys
key_manager.cleanup_old_keys(days_old=180)
```

#### Zero-Downtime Rotation Strategy

```
PHASE 1: PREPARATION (Day 0)
┌─────────────────────────────────────────────────────────────────┐
│  1. Generate new API key through provider portal                │
│  2. Validate new key with test request                          │
│  3. Add new key to rotation manager                             │
│  4. Both old and new keys are now active                        │
└─────────────────────────────────────────────────────────────────┘

PHASE 2: TRANSITION (Day 0-7)
┌─────────────────────────────────────────────────────────────────┐
│  1. New deployments use new key                                 │
│  2. Existing sessions continue with old key                     │
│  3. Monitor for any issues                                      │
│  4. Gradually shift traffic to new key                          │
└─────────────────────────────────────────────────────────────────┘

PHASE 3: COMPLETION (Day 7)
┌─────────────────────────────────────────────────────────────────┐
│  1. Deactivate old key                                          │
│  2. All traffic now uses new key                                │
│  3. Archive old key metadata                                    │
│  4. Update documentation                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

### 3.5 Role-Based Access Control (RBAC)

The RBAC Manager provides granular access control for LLM resources, ensuring users can only access authorized models and operations within their quota limits.

#### RBAC Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                       RBAC STRUCTURE                             │
└─────────────────────────────────────────────────────────────────┘

ORGANIZATION
    │
    ├── ROLES
    │   ├── Admin
    │   │   └── All Permissions
    │   │
    │   ├── Developer
    │   │   ├── model:read
    │   │   ├── model:complete
    │   │   └── logs:read
    │   │
    │   ├── Analyst
    │   │   ├── model:read
    │   │   └── logs:read
    │   │
    │   └── User
    │       └── model:complete (limited)
    │
    ├── USERS
    │   ├── User 1 → [Developer, Analyst]
    │   ├── User 2 → [User]
    │   └── User 3 → [Admin]
    │
    └── RESOURCES
        ├── Models
        │   ├── claude-opus
        │   ├── claude-sonnet
        │   └── claude-haiku
        │
        └── Operations
            ├── complete
            ├── chat
            └── embed
```

#### Permission Types

| Permission | Resource | Actions | Description |
|------------|----------|---------|-------------|
| model:read | Models | View model info | Read model details |
| model:complete | Models | Generate completions | Use model for completions |
| model:chat | Models | Chat interactions | Use model for chat |
| model:admin | Models | All operations | Full model access |
| logs:read | Logs | View logs | Read audit logs |
| logs:write | Logs | Modify logs | Modify log settings |
| user:read | Users | View users | Read user info |
| user:write | Users | Manage users | Manage user accounts |

#### Code Example: RBAC Setup

```python
from abhikarta.security import RBACManager, Role, Permission, User

# Initialize RBAC
rbac = RBACManager()

# Define roles
admin_role = Role(
    name='admin',
    permissions=[
        'model:*',      # All model operations
        'logs:*',       # All log operations
        'user:*'        # All user operations
    ],
    description='Full system access'
)

developer_role = Role(
    name='developer',
    permissions=[
        'model:read',
        'model:complete',
        'model:chat',
        'logs:read'
    ],
    max_requests_per_day=10000,
    max_cost_per_day=100.0,
    allowed_models=['claude-sonnet-4', 'claude-haiku'],
    description='Developer access'
)

user_role = Role(
    name='user',
    permissions=['model:complete'],
    max_requests_per_day=100,
    max_cost_per_day=5.0,
    allowed_models=['claude-haiku'],
    description='Basic user access'
)

# Register roles
rbac.add_role(admin_role)
rbac.add_role(developer_role)
rbac.add_role(user_role)
```

#### Code Example: User Management

```python
# Create users
admin_user = User(
    user_id='admin001',
    username='alice@example.com',
    roles=['admin'],
    metadata={'department': 'Engineering'}
)

dev_user = User(
    user_id='dev001',
    username='bob@example.com',
    roles=['developer'],
    metadata={'team': 'AI Team'}
)

basic_user = User(
    user_id='user001',
    username='charlie@example.com',
    roles=['user'],
    metadata={'subscription': 'free'}
)

# Add users to RBAC
rbac.add_user(admin_user)
rbac.add_user(dev_user)
rbac.add_user(basic_user)
```

#### Code Example: Access Control

```python
# Check permissions before operation
try:
    # Check if user can access model
    rbac.check_permission(
        user_id='dev001',
        resource='model:claude-sonnet-4',
        action='complete'
    )
    
    # Check quota
    rbac.check_quota(
        user_id='dev001',
        tokens=1000,
        cost=0.10
    )
    
    # Permission granted - proceed with operation
    response = llm_client.complete(prompt)
    
    # Track usage
    rbac.track_usage(
        user_id='dev001',
        resource='model:claude-sonnet-4',
        tokens=1000,
        cost=0.10
    )
    
except PermissionDeniedError as e:
    print(f"Access denied: {e}")
    
except ResourceLimitExceededError as e:
    print(f"Quota exceeded: {e}")
```

#### Code Example: Dynamic Access Control

```python
# Wrapper for automatic RBAC enforcement
class SecureLLMClient:
    def __init__(self, client, rbac_manager, user_id):
        self.client = client
        self.rbac = rbac_manager
        self.user_id = user_id
    
    def complete(self, prompt, model='claude-sonnet-4', **kwargs):
        # Check permissions
        self.rbac.check_permission(
            user_id=self.user_id,
            resource=f'model:{model}',
            action='complete'
        )
        
        # Check quota
        estimated_cost = self._estimate_cost(prompt, model)
        self.rbac.check_quota(
            user_id=self.user_id,
            cost=estimated_cost
        )
        
        # Make request
        response = self.client.complete(prompt, model=model, **kwargs)
        
        # Track usage
        self.rbac.track_usage(
            user_id=self.user_id,
            resource=f'model:{model}',
            tokens=response.usage['total_tokens'],
            cost=response.usage['cost']
        )
        
        return response
    
    def _estimate_cost(self, prompt, model):
        # Estimate cost based on prompt length and model
        token_count = len(prompt.split()) * 1.3  # Rough estimate
        return token_count * self._get_model_price(model)

# Usage
secure_client = SecureLLMClient(
    client=base_llm_client,
    rbac_manager=rbac,
    user_id='dev001'
)

response = secure_client.complete("Hello, how are you?")
```

#### Usage Statistics and Monitoring

```python
# Get user statistics
user_stats = rbac.get_user_stats('dev001')
print(f"Requests today: {user_stats['requests_today']}")
print(f"Cost today: ${user_stats['cost_today']:.2f}")
print(f"Tokens used: {user_stats['tokens_used']}")
print(f"Quota remaining: {user_stats['quota_remaining']:.1%}")

# Get role statistics
role_stats = rbac.get_role_stats('developer')
print(f"Total users with role: {role_stats['user_count']}")
print(f"Total requests: {role_stats['total_requests']}")
print(f"Average cost per user: ${role_stats['avg_cost_per_user']:.2f}")

# List users exceeding quota
quota_violations = rbac.get_quota_violations()
for violation in quota_violations:
    print(f"User {violation['user_id']} exceeded {violation['quota_type']}")
```

---

## 4. System Architecture Diagrams

### 4.1 Complete Security Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          USER APPLICATION                                 │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
                                  │ User Input
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                     ABHIKARTA SECURITY FRAMEWORK                          │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  STAGE 1: INPUT VALIDATION                                      │    │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │    │
│  │  │ Content Filter   │  │  PII Detector    │  │ Input Length │ │    │
│  │  │ (Block Harmful)  │→ │  (Redact PII)    │→ │   Validator  │ │    │
│  │  └──────────────────┘  └──────────────────┘  └──────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                  │                                        │
│                                  ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  STAGE 2: ACCESS CONTROL                                        │    │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │    │
│  │  │  RBAC Manager    │  │ Quota Checker    │  │ Rate Limiter │ │    │
│  │  │ (Authorization)  │→ │ (Cost Control)   │→ │   (Throttle) │ │    │
│  │  └──────────────────┘  └──────────────────┘  └──────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                  │                                        │
│                                  ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  STAGE 3: AUDIT & LOGGING                                       │    │
│  │  ┌──────────────────────────────────────────────────────────┐  │    │
│  │  │  Audit Logger (Log all operations)                       │  │    │
│  │  └──────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                  │                                        │
└──────────────────────────────────┼────────────────────────────────────────┘
                                   │
                                   │ Sanitized Request
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         LLM PROVIDER                                      │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Key Rotation Manager (Secure API Key Management)               │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Anthropic / OpenAI / Other Provider API                        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────┬─────────────────────────────────────────┘
                                  │
                                  │ Response
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                     ABHIKARTA SECURITY FRAMEWORK                          │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  STAGE 4: OUTPUT VALIDATION                                     │    │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │    │
│  │  │ Content Filter   │  │  PII Detector    │  │ Output Length│ │    │
│  │  │ (Filter Output)  │→ │  (Check Leaks)   │→ │   Validator  │ │    │
│  │  └──────────────────┘  └──────────────────┘  └──────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                  │                                        │
│                                  ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  STAGE 5: USAGE TRACKING                                        │    │
│  │  ┌──────────────────────────────────────────────────────────┐  │    │
│  │  │  Update Quotas, Log Usage, Track Costs                   │  │    │
│  │  └──────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
                                  │ Safe Response
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                          USER APPLICATION                                 │
└──────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Multi-Tenant Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        TENANT ISOLATION MODEL                            │
└─────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────┐
                              │  API Gateway │
                              └───────┬──────┘
                                      │
                   ┌──────────────────┼──────────────────┐
                   │                  │                  │
           ┌───────▼───────┐  ┌──────▼──────┐  ┌───────▼───────┐
           │   TENANT A    │  │   TENANT B  │  │   TENANT C    │
           └───────┬───────┘  └──────┬──────┘  └───────┬───────┘
                   │                  │                  │
    ┌──────────────┼──────────────────┼──────────────────┼──────────────┐
    │              │                  │                  │              │
    │  ┌───────────▼──────────────────▼──────────────────▼───────────┐ │
    │  │        ABHIKARTA SECURITY FRAMEWORK (Shared)                 │ │
    │  └──────────────────────────────────────────────────────────────┘ │
    │                                                                    │
    │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐     │
    │  │ Tenant A       │  │ Tenant B       │  │ Tenant C       │     │
    │  │ - Config       │  │ - Config       │  │ - Config       │     │
    │  │ - RBAC Rules   │  │ - RBAC Rules   │  │ - RBAC Rules   │     │
    │  │ - Quotas       │  │ - Quotas       │  │ - Quotas       │     │
    │  │ - Audit Logs   │  │ - Audit Logs   │  │ - Audit Logs   │     │
    │  │ - API Keys     │  │ - API Keys     │  │ - API Keys     │     │
    │  └────────────────┘  └────────────────┘  └────────────────┘     │
    │                                                                    │
    └────────────────────────────────────────────────────────────────────┘

ISOLATION GUARANTEES:
├─ Each tenant has separate configuration
├─ RBAC policies are tenant-scoped
├─ Audit logs are segregated by tenant
├─ API keys are tenant-specific
├─ Quotas and rate limits per tenant
└─ Zero cross-tenant data leakage
```

### 4.3 Data Flow with PII Protection

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      PII PROTECTION DATA FLOW                            │
└─────────────────────────────────────────────────────────────────────────┘

USER INPUT: "My email is john@example.com and SSN is 123-45-6789"
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  PII DETECTION                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Pattern Matching:                                   │  │
│  │  ✓ Email detected: john@example.com                 │  │
│  │  ✓ SSN detected: 123-45-6789                        │  │
│  │  Confidence: 0.95                                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  PII REDACTION (Action: REDACT)                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Redacted Output:                                    │  │
│  │  "My email is [EMAIL_REDACTED] and                  │  │
│  │   SSN is [SSN_REDACTED]"                            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  AUDIT LOGGING                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Event: PII_DETECTION                                │  │
│  │  User: user123                                       │  │
│  │  PII Types: [email, ssn]                            │  │
│  │  Action: redacted                                    │  │
│  │  Timestamp: 2025-11-07T14:32:15Z                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  LLM PROCESSING                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Input: "My email is [EMAIL_REDACTED] and           │  │
│  │          SSN is [SSN_REDACTED]"                      │  │
│  │                                                       │  │
│  │  Model processes sanitized input safely              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
SAFE OUTPUT: "I can help you with that. Please note..."
```

---

## 5. Implementation Guide

### 5.1 Quick Start

#### Installation

```bash
# Install from PyPI (when published)
pip install abhikarta-security

# Or install from source
git clone https://github.com/ajsinha/abhikarta.git
cd abhikarta
pip install -e .
```

#### Basic Setup

```python
from abhikarta.security import (
    PIIDetector,
    ContentFilter,
    AuditLogger,
    RBACManager,
    KeyRotationManager
)

# Initialize all components
pii_detector = PIIDetector(
    detect=['email', 'phone', 'ssn', 'credit_card'],
    action='redact'
)

content_filter = ContentFilter(
    block_categories=['hate_speech', 'violence', 'self_harm'],
    threshold=0.8,
    action='block'
)

audit_logger = AuditLogger(
    log_level='METADATA_ONLY',
    log_dir='logs/audit',
    retention_days=90
)

rbac_manager = RBACManager()

key_manager = KeyRotationManager(
    storage_path='.keys',
    notification_callback=send_notification
)

print("Abhikarta Security Framework initialized successfully!")
```

### 5.2 Integration with LLM Clients

#### Anthropic Claude Integration

```python
import anthropic
from abhikarta.security import clean_text_for_llm, ContentFilter, AuditLogger

class SecureClaudeClient:
    def __init__(self, api_key, user_id):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.user_id = user_id
        self.pii_detector = PIIDetector(action='redact')
        self.content_filter = ContentFilter(action='block')
        self.audit_logger = AuditLogger(log_level='FULL')
    
    def complete(self, prompt, **kwargs):
        # Step 1: Filter content
        filter_result = self.content_filter.process(prompt)
        if filter_result.was_blocked:
            raise Exception("Content policy violation")
        
        # Step 2: Redact PII
        clean_prompt = clean_text_for_llm(filter_result.filtered_text)
        
        # Step 3: Make request
        start_time = time.time()
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": clean_prompt}],
            **kwargs
        )
        latency = (time.time() - start_time) * 1000
        
        # Step 4: Audit log
        self.audit_logger.log_api_call(
            user_id=self.user_id,
            provider='anthropic',
            model='claude-sonnet-4-20250514',
            operation='complete',
            prompt=clean_prompt,
            response=message.content[0].text,
            tokens=message.usage.input_tokens + message.usage.output_tokens,
            cost=self._calculate_cost(message.usage),
            latency_ms=latency
        )
        
        return message.content[0].text
    
    def _calculate_cost(self, usage):
        # Pricing: $3 per MTok input, $15 per MTok output
        input_cost = (usage.input_tokens / 1_000_000) * 3
        output_cost = (usage.output_tokens / 1_000_000) * 15
        return input_cost + output_cost

# Usage
client = SecureClaudeClient(api_key='your-key', user_id='user123')
response = client.complete("Tell me about quantum computing")
print(response)
```

#### OpenAI Integration

```python
from openai import OpenAI
from abhikarta.security import PIIDetector, ContentFilter, AuditLogger

class SecureOpenAIClient:
    def __init__(self, api_key, user_id):
        self.client = OpenAI(api_key=api_key)
        self.user_id = user_id
        self.pii_detector = PIIDetector(action='redact')
        self.content_filter = ContentFilter(action='block')
        self.audit_logger = AuditLogger(log_level='FULL')
    
    def chat(self, messages, **kwargs):
        # Process each message
        clean_messages = []
        for msg in messages:
            # Filter content
            filter_result = self.content_filter.process(msg['content'])
            if filter_result.was_blocked:
                raise Exception("Content policy violation")
            
            # Redact PII
            clean_content = self.pii_detector.redact(filter_result.filtered_text)
            
            clean_messages.append({
                'role': msg['role'],
                'content': clean_content
            })
        
        # Make request
        start_time = time.time()
        response = self.client.chat.completions.create(
            model='gpt-4',
            messages=clean_messages,
            **kwargs
        )
        latency = (time.time() - start_time) * 1000
        
        # Audit log
        self.audit_logger.log_api_call(
            user_id=self.user_id,
            provider='openai',
            model='gpt-4',
            operation='chat',
            tokens=response.usage.total_tokens,
            cost=self._calculate_cost(response.usage),
            latency_ms=latency
        )
        
        return response.choices[0].message.content
    
    def _calculate_cost(self, usage):
        # GPT-4 pricing
        input_cost = (usage.prompt_tokens / 1_000) * 0.03
        output_cost = (usage.completion_tokens / 1_000) * 0.06
        return input_cost + output_cost

# Usage
client = SecureOpenAIClient(api_key='your-key', user_id='user123')
response = client.chat([
    {'role': 'user', 'content': 'Explain machine learning'}
])
print(response)
```

### 5.3 Web Application Integration

#### Flask Example

```python
from flask import Flask, request, jsonify
from abhikarta.security import (
    PIIDetector,
    ContentFilter,
    RBACManager,
    AuditLogger
)

app = Flask(__name__)

# Initialize security components
pii_detector = PIIDetector(action='redact')
content_filter = ContentFilter(action='block')
rbac = RBACManager()
audit = AuditLogger(log_level='METADATA_ONLY')

@app.before_request
def authenticate():
    # Get user from token
    token = request.headers.get('Authorization')
    user = validate_token(token)  # Your auth logic
    
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    request.user = user

@app.route('/api/complete', methods=['POST'])
def complete():
    data = request.json
    prompt = data.get('prompt')
    model = data.get('model', 'claude-haiku')
    
    try:
        # Check RBAC permissions
        rbac.check_permission(
            user_id=request.user.id,
            resource=f'model:{model}',
            action='complete'
        )
        
        # Filter content
        filter_result = content_filter.process(prompt)
        if filter_result.was_blocked:
            return jsonify({'error': 'Content policy violation'}), 400
        
        # Redact PII
        clean_prompt = pii_detector.redact(filter_result.filtered_text)
        
        # Make LLM request
        response = llm_client.complete(clean_prompt, model=model)
        
        # Track usage
        rbac.track_usage(
            user_id=request.user.id,
            resource=f'model:{model}',
            tokens=response.usage['total_tokens'],
            cost=response.usage['cost']
        )
        
        # Audit log
        audit.log_api_call(
            user_id=request.user.id,
            provider='anthropic',
            model=model,
            tokens=response.usage['total_tokens'],
            cost=response.usage['cost']
        )
        
        return jsonify({
            'response': response.text,
            'usage': response.usage
        })
        
    except PermissionDeniedError as e:
        return jsonify({'error': str(e)}), 403
        
    except ResourceLimitExceededError as e:
        return jsonify({'error': str(e)}), 429

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    # Check admin permission
    try:
        rbac.check_permission(
            user_id=request.user.id,
            resource='system',
            action='admin'
        )
    except PermissionDeniedError:
        return jsonify({'error': 'Admin access required'}), 403
    
    # Get statistics
    stats = {
        'content_filter': content_filter.get_statistics(),
        'audit': audit.get_statistics(),
        'rbac': rbac.get_stats()
    }
    
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```

#### FastAPI Example

```python
from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
from abhikarta.security import (
    PIIDetector,
    ContentFilter,
    RBACManager,
    AuditLogger
)

app = FastAPI(title="Secure LLM API")

# Initialize security
pii_detector = PIIDetector(action='redact')
content_filter = ContentFilter(action='block')
rbac = RBACManager()
audit = AuditLogger(log_level='METADATA_ONLY')

class CompletionRequest(BaseModel):
    prompt: str
    model: str = 'claude-haiku'
    max_tokens: int = 1024

class CompletionResponse(BaseModel):
    response: str
    usage: dict

async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Validate token and get user
    user = validate_token(authorization)  # Your auth logic
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return user

@app.post("/api/complete", response_model=CompletionResponse)
async def complete(
    request: CompletionRequest,
    user=Depends(get_current_user)
):
    try:
        # Check permissions
        rbac.check_permission(
            user_id=user.id,
            resource=f'model:{request.model}',
            action='complete'
        )
        
        # Filter and sanitize
        filter_result = content_filter.process(request.prompt)
        if filter_result.was_blocked:
            raise HTTPException(
                status_code=400,
                detail="Content policy violation"
            )
        
        clean_prompt = pii_detector.redact(filter_result.filtered_text)
        
        # Make LLM request
        response = await llm_client.complete(
            clean_prompt,
            model=request.model,
            max_tokens=request.max_tokens
        )
        
        # Track and audit
        rbac.track_usage(
            user_id=user.id,
            resource=f'model:{request.model}',
            tokens=response.usage['total_tokens'],
            cost=response.usage['cost']
        )
        
        audit.log_api_call(
            user_id=user.id,
            provider='anthropic',
            model=request.model,
            tokens=response.usage['total_tokens'],
            cost=response.usage['cost']
        )
        
        return CompletionResponse(
            response=response.text,
            usage=response.usage
        )
        
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
        
    except ResourceLimitExceededError as e:
        raise HTTPException(status_code=429, detail=str(e))

@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": "1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 6. Usage Examples

### 6.1 Healthcare Application (HIPAA Compliance)

```python
from abhikarta.security import PIIDetector, ContentFilter, AuditLogger

class HIPAACompliantChatbot:
    """
    HIPAA-compliant chatbot with strict PHI protection
    """
    def __init__(self):
        # Configure PII detection for PHI
        self.pii_detector = PIIDetector(
            detect=[
                'ssn',
                'date_of_birth',
                'phone',
                'email',
                'address',
                'medical_record_number',
                'health_plan_number'
            ],
            action='redact',
            confidence_threshold=0.7  # Lower threshold for healthcare
        )
        
        # Configure content filter
        self.content_filter = ContentFilter(
            block_categories=['self_harm', 'violence'],
            action='warn'
        )
        
        # Configure audit with encryption
        self.audit = AuditLogger(
            log_level='FULL_ENCRYPTED',
            encryption=True,
            encryption_key=get_encryption_key(),
            retention_days=2555  # 7 years for HIPAA
        )
    
    def process_query(self, patient_id, query):
        # Log the interaction
        event_id = self.audit.log_api_call(
            user_id=patient_id,
            provider='anthropic',
            model='claude-sonnet-4',
            operation='chat',
            prompt=query,
            status='processing'
        )
        
        try:
            # Filter content
            filter_result = self.content_filter.process(query)
            
            # Redact PHI
            pii_result = self.pii_detector.process(filter_result.filtered_text)
            
            # Log if PHI was detected
            if pii_result.matches:
                self.audit.log_pii_detection(
                    user_id=patient_id,
                    pii_types=[m.pii_type.value for m in pii_result.matches],
                    action_taken='redacted'
                )
            
            # Process with LLM
            response = self.llm_client.complete(pii_result.redacted_text)
            
            return {
                'response': response,
                'phi_detected': len(pii_result.matches) > 0,
                'event_id': event_id
            }
            
        except Exception as e:
            self.audit.log_security_alert(
                alert_type='processing_error',
                severity='high',
                description=str(e),
                user_id=patient_id
            )
            raise

# Usage
chatbot = HIPAACompliantChatbot()
result = chatbot.process_query(
    patient_id='P123456',
    query='My blood pressure is high and my SSN is 123-45-6789'
)

print(result['response'])
# Note: SSN will be redacted in processing
```

### 6.2 Financial Services Application

```python
from abhikarta.security import (
    PIIDetector,
    ContentFilter,
    RBACManager,
    AuditLogger
)

class FinancialAdvisorBot:
    """
    PCI-DSS compliant financial advisor with strict controls
    """
    def __init__(self):
        # Configure for financial data
        self.pii_detector = PIIDetector(
            detect=[
                'credit_card',
                'bank_account',
                'routing_number',
                'ssn',
                'account_number'
            ],
            action='block',  # Never process financial data
            confidence_threshold=0.9
        )
        
        self.content_filter = ContentFilter(
            block_categories=['illegal_activity', 'fraud'],
            custom_rules=[
                FilterRule(
                    name='investment_fraud',
                    category=ContentCategory.ILLEGAL_ACTIVITY,
                    patterns=[
                        r'\bguaranteed\s+returns\b',
                        r'\brisk-free\s+investment\b'
                    ],
                    confidence=0.95
                )
            ],
            action='block'
        )
        
        self.rbac = RBACManager()
        self.audit = AuditLogger(
            log_level='FULL',
            retention_days=2555  # 7 years for financial records
        )
    
    def get_advice(self, customer_id, question):
        # Check customer authorization
        try:
            self.rbac.check_permission(
                user_id=customer_id,
                resource='financial_advice',
                action='request'
            )
        except PermissionDeniedError:
            self.audit.log_authorization(
                user_id=customer_id,
                resource='financial_advice',
                action='request',
                status='denied'
            )
            raise
        
        # Check for financial data leakage
        pii_result = self.pii_detector.process(question)
        if pii_result.was_blocked:
            self.audit.log_security_alert(
                alert_type='financial_data_detected',
                severity='critical',
                description='Customer attempted to share financial account data',
                user_id=customer_id
            )
            return {
                'error': 'Please do not share account numbers or card details. '
                        'Our system does not need this information.'
            }
        
        # Filter content
        filter_result = self.content_filter.process(question)
        if filter_result.was_blocked:
            return {
                'error': 'Your question contains content that violates our policies.'
            }
        
        # Get LLM advice
        response = self.llm_client.complete(filter_result.filtered_text)
        
        # Audit the transaction
        self.audit.log_api_call(
            user_id=customer_id,
            provider='anthropic',
            model='claude-opus',
            operation='financial_advice',
            status='success',
            metadata={
                'advice_category': 'general',
                'compliance_approved': True
            }
        )
        
        return {'advice': response}

# Usage
advisor = FinancialAdvisorBot()
result = advisor.get_advice(
    customer_id='C789012',
    question='Should I invest in tech stocks?'
)
print(result['advice'])
```

### 6.3 Enterprise Multi-Tenant SaaS

```python
from abhikarta.security import (
    PIIDetector,
    ContentFilter,
    RBACManager,
    KeyRotationManager,
    AuditLogger
)

class EnterpriseLLMPlatform:
    """
    Multi-tenant LLM platform with complete security stack
    """
    def __init__(self):
        # Initialize all security components
        self.pii_detector = PIIDetector(action='redact')
        self.content_filter = ContentFilter(action='warn')
        self.rbac = RBACManager()
        self.key_manager = KeyRotationManager()
        self.audit = AuditLogger(log_level='METADATA_ONLY')
        
        # Register API keys by tenant
        self.setup_tenants()
    
    def setup_tenants(self):
        # Setup tenant configurations
        tenants = {
            'acme-corp': {
                'api_key': 'sk-ant-acme...',
                'max_cost_per_day': 500.0,
                'allowed_models': ['claude-sonnet-4', 'claude-haiku']
            },
            'globex': {
                'api_key': 'sk-ant-globex...',
                'max_cost_per_day': 1000.0,
                'allowed_models': ['claude-opus', 'claude-sonnet-4']
            }
        }
        
        for tenant_id, config in tenants.items():
            # Register API key
            self.key_manager.register_provider(
                provider=f'anthropic_{tenant_id}',
                api_key=config['api_key']
            )
            
            # Setup RBAC roles
            self.setup_tenant_roles(tenant_id, config)
    
    def setup_tenant_roles(self, tenant_id, config):
        # Admin role
        admin_role = Role(
            name=f'{tenant_id}_admin',
            permissions=['model:*', 'user:*', 'logs:*'],
            max_cost_per_day=config['max_cost_per_day'],
            allowed_models=config['allowed_models']
        )
        
        # User role
        user_role = Role(
            name=f'{tenant_id}_user',
            permissions=['model:complete'],
            max_requests_per_day=1000,
            max_cost_per_day=config['max_cost_per_day'] * 0.1,
            allowed_models=config['allowed_models']
        )
        
        self.rbac.add_role(admin_role)
        self.rbac.add_role(user_role)
    
    def complete(self, tenant_id, user_id, prompt, model='claude-haiku'):
        # Validate tenant and user
        full_user_id = f'{tenant_id}_{user_id}'
        
        try:
            # Check permissions
            self.rbac.check_permission(
                user_id=full_user_id,
                resource=f'model:{model}',
                action='complete'
            )
            
            # Check quota
            self.rbac.check_quota(user_id=full_user_id)
            
            # Security processing
            filter_result = self.content_filter.process(prompt)
            clean_prompt = self.pii_detector.redact(filter_result.filtered_text)
            
            # Get tenant-specific API key
            api_key = self.key_manager.get_active_key(f'anthropic_{tenant_id}')
            
            # Make request
            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model=model,
                max_tokens=1024,
                messages=[{"role": "user", "content": clean_prompt}]
            )
            
            # Track usage
            cost = self._calculate_cost(message.usage, model)
            self.rbac.track_usage(
                user_id=full_user_id,
                resource=f'model:{model}',
                tokens=message.usage.input_tokens + message.usage.output_tokens,
                cost=cost
            )
            
            # Audit
            self.audit.log_api_call(
                user_id=full_user_id,
                provider='anthropic',
                model=model,
                tokens=message.usage.input_tokens + message.usage.output_tokens,
                cost=cost,
                metadata={'tenant_id': tenant_id}
            )
            
            return {
                'response': message.content[0].text,
                'usage': {
                    'tokens': message.usage.input_tokens + message.usage.output_tokens,
                    'cost': cost
                }
            }
            
        except Exception as e:
            self.audit.log_security_alert(
                alert_type='request_error',
                severity='medium',
                description=str(e),
                user_id=full_user_id
            )
            raise
    
    def _calculate_cost(self, usage, model):
        # Model-specific pricing
        pricing = {
            'claude-opus': {'input': 15, 'output': 75},
            'claude-sonnet-4': {'input': 3, 'output': 15},
            'claude-haiku': {'input': 0.25, 'output': 1.25}
        }
        
        rates = pricing.get(model, pricing['claude-haiku'])
        input_cost = (usage.input_tokens / 1_000_000) * rates['input']
        output_cost = (usage.output_tokens / 1_000_000) * rates['output']
        
        return input_cost + output_cost

# Usage
platform = EnterpriseLLMPlatform()

# Tenant A user request
result = platform.complete(
    tenant_id='acme-corp',
    user_id='user123',
    prompt='Explain quantum computing',
    model='claude-sonnet-4'
)

print(result['response'])
print(f"Cost: ${result['usage']['cost']:.4f}")
```

---

## 7. API Reference

### 7.1 PIIDetector Class

```python
class PIIDetector:
    """
    Detects and handles PII in text.
    """
    
    def __init__(
        self,
        detect: List[str] = None,
        action: str = 'redact',
        confidence_threshold: float = 0.8,
        custom_patterns: Dict[str, str] = None,
        alert_callback = None,
        preserve_format: bool = False
    ):
        """
        Initialize PII detector.
        
        Args:
            detect: List of PII types to detect
                   Options: 'email', 'phone', 'ssn', 'credit_card',
                           'ip_address', 'date_of_birth', 'passport',
                           'driver_license', 'bank_account'
            action: Action to take when PII is found
                   Options: 'redact', 'block', 'alert', 'hash', 'mask'
            confidence_threshold: Minimum confidence score (0-1)
            custom_patterns: Custom regex patterns {name: pattern}
            alert_callback: Function to call when PII is detected
            preserve_format: Keep original length with masks
        """
    
    def process(self, text: str) -> PIIDetectionResult:
        """
        Process text according to configured action.
        
        Args:
            text: Text to process
            
        Returns:
            PIIDetectionResult with processed text and metadata
        """
    
    def detect(self, text: str) -> List[PIIMatch]:
        """
        Detect PII in text without modification.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of PIIMatch objects
        """
```

### 7.2 ContentFilter Class

```python
class ContentFilter:
    """
    Filters harmful and inappropriate content.
    """
    
    def __init__(
        self,
        block_categories: List[str] = None,
        threshold: float = 0.8,
        action: str = 'block',
        custom_rules: List[FilterRule] = None,
        whitelist: List[str] = None,
        case_sensitive: bool = False
    ):
        """
        Initialize content filter.
        
        Args:
            block_categories: Categories to filter
                            Options: 'hate_speech', 'violence', 'sexual_content',
                                    'self_harm', 'harassment', 'illegal_activity',
                                    'profanity', 'spam', 'misinformation'
            threshold: Confidence threshold for blocking
            action: Action to take ('block', 'warn', 'sanitize', 'log')
            custom_rules: Custom filter rules
            whitelist: Words/phrases to never filter
            case_sensitive: Whether matching is case-sensitive
        """
    
    def process(self, text: str) -> FilterResult:
        """
        Process text through content filter.
        
        Args:
            text: Text to filter
            
        Returns:
            FilterResult with processed text and metadata
        """
    
    def add_rule(self, rule: FilterRule) -> None:
        """Add a custom filter rule"""
    
    def get_statistics(self) -> Dict[str, any]:
        """Get filtering statistics"""
```

### 7.3 AuditLogger Class

```python
class AuditLogger:
    """
    Comprehensive audit logger for LLM operations.
    """
    
    def __init__(
        self,
        log_level: str = 'METADATA_ONLY',
        log_file: Optional[str] = None,
        log_dir: str = 'logs/audit',
        retention_days: int = 90,
        encryption: bool = False,
        encryption_key: Optional[str] = None,
        rotate_daily: bool = True,
        async_logging: bool = True
    ):
        """
        Initialize audit logger.
        
        Args:
            log_level: Level of detail
                      Options: 'NONE', 'METADATA_ONLY', 'FULL', 'FULL_ENCRYPTED'
            log_file: Specific log file path
            log_dir: Directory for log files
            retention_days: Days to retain logs
            encryption: Whether to encrypt sensitive data
            encryption_key: Key for encryption
            rotate_daily: Rotate log files daily
            async_logging: Log asynchronously
        """
    
    def log_api_call(
        self,
        user_id: str,
        provider: str,
        model: str,
        operation: str = "completion",
        prompt: Optional[str] = None,
        response: Optional[str] = None,
        tokens: int = 0,
        cost: float = 0.0,
        latency_ms: float = 0.0,
        status: str = "success",
        **metadata
    ) -> str:
        """Log an API call"""
    
    def log_security_alert(
        self,
        alert_type: str,
        severity: str,
        description: str,
        user_id: Optional[str] = None,
        **metadata
    ) -> str:
        """Log security alert"""
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get audit statistics"""
```

### 7.4 RBACManager Class

```python
class RBACManager:
    """
    Role-Based Access Control Manager.
    """
    
    def __init__(self):
        """Initialize RBAC manager"""
    
    def add_role(self, role: Role) -> None:
        """Add a role definition"""
    
    def add_user(self, user: User) -> None:
        """Add a user"""
    
    def check_permission(
        self,
        user_id: str,
        resource: str,
        action: str
    ) -> bool:
        """
        Check if user has permission.
        
        Raises:
            PermissionDeniedError: If permission denied
        """
    
    def check_quota(
        self,
        user_id: str,
        tokens: int = 0,
        cost: float = 0.0
    ) -> bool:
        """
        Check if user within quota limits.
        
        Raises:
            ResourceLimitExceededError: If quota exceeded
        """
    
    def track_usage(
        self,
        user_id: str,
        resource: str,
        tokens: int = 0,
        cost: float = 0.0
    ) -> None:
        """Track resource usage"""
```

### 7.5 KeyRotationManager Class

```python
class KeyRotationManager:
    """
    Manages API key rotation with zero-downtime strategy.
    """
    
    def __init__(
        self,
        storage_path: str = ".keys",
        policy: Optional[KeyRotationPolicy] = None,
        notification_callback: Optional[Callable] = None
    ):
        """
        Initialize key rotation manager.
        
        Args:
            storage_path: Path to store key metadata
            policy: Rotation policy
            notification_callback: Function to call for notifications
        """
    
    def register_provider(
        self,
        provider: str,
        api_key: str,
        rotation_generator: Optional[Callable[[], str]] = None
    ) -> None:
        """Register a provider for key rotation"""
    
    def get_active_key(self, provider: str) -> Optional[str]:
        """Get the active API key for a provider"""
    
    def rotate_key(
        self,
        provider: str,
        new_key: str,
        immediate: bool = False
    ) -> bool:
        """Rotate API key for a provider"""
    
    def get_status(self) -> Dict:
        """Get status of all keys"""
```

---

## 8. Security Best Practices

### 8.1 Defense in Depth

Always implement multiple layers of security:

```python
# ❌ BAD: Single layer
response = llm_client.complete(user_input)

# ✅ GOOD: Multiple layers
# Layer 1: Content filtering
filter_result = content_filter.process(user_input)
if filter_result.was_blocked:
    raise ContentFilterException()

# Layer 2: PII redaction
clean_input = pii_detector.redact(filter_result.filtered_text)

# Layer 3: RBAC check
rbac.check_permission(user_id, 'model:complete', 'execute')

# Layer 4: Audit logging
audit.log_api_call(user_id, 'anthropic', 'claude-sonnet-4')

# Now make request
response = llm_client.complete(clean_input)
```

### 8.2 Least Privilege

Grant minimum necessary permissions:

```python
# ❌ BAD: Overly permissive
user_role = Role(
    name='basic_user',
    permissions=['*']  # All permissions
)

# ✅ GOOD: Minimal permissions
user_role = Role(
    name='basic_user',
    permissions=[
        'model:complete'  # Only completion permission
    ],
    allowed_models=['claude-haiku'],  # Only cheapest model
    max_requests_per_day=100,  # Rate limit
    max_cost_per_day=1.0  # Cost limit
)
```

### 8.3 Input Validation

Always validate and sanitize inputs:

```python
# ❌ BAD: No validation
def process_request(prompt):
    return llm_client.complete(prompt)

# ✅ GOOD: Comprehensive validation
def process_request(prompt, max_length=10000):
    # Length check
    if len(prompt) > max_length:
        raise ValueError("Prompt too long")
    
    # Character validation
    if not prompt.isprintable():
        raise ValueError("Invalid characters in prompt")
    
    # Content filtering
    filter_result = content_filter.process(prompt)
    if filter_result.was_blocked:
        raise ContentFilterException("Policy violation")
    
    # PII redaction
    clean_prompt = pii_detector.redact(filter_result.filtered_text)
    
    return llm_client.complete(clean_prompt)
```

### 8.4 Secure Configuration

Store sensitive configuration securely:

```python
# ❌ BAD: Hardcoded secrets
api_key = "sk-ant-api03-abc123..."
encryption_key = "mysecretkey"

# ✅ GOOD: Environment variables or secrets manager
import os
from secrets import token_hex

api_key = os.environ.get('ANTHROPIC_API_KEY')
encryption_key = os.environ.get('ENCRYPTION_KEY') or token_hex(32)

# Or use secrets manager
from cloud_secrets_manager import get_secret
api_key = get_secret('anthropic-api-key')
```

### 8.5 Regular Audits

Implement regular security audits:

```python
from datetime import datetime, timedelta

class SecurityAuditor:
    def __init__(self, audit_logger, rbac_manager):
        self.audit = audit_logger
        self.rbac = rbac_manager
    
    def run_daily_audit(self):
        """Run daily security audit"""
        print("=== Daily Security Audit ===")
        
        # Check for suspicious activity
        suspicious = self._check_suspicious_activity()
        if suspicious:
            print(f"⚠️ Found {len(suspicious)} suspicious events")
        
        # Check quota violations
        violations = self.rbac.get_quota_violations()
        if violations:
            print(f"⚠️ Found {len(violations)} quota violations")
        
        # Check key rotation status
        key_status = self.key_manager.get_status()
        for provider, status in key_status.items():
            if status['should_rotate']:
                print(f"⚠️ Key for {provider} should be rotated")
        
        # Generate report
        report = self._generate_audit_report()
        self._send_report(report)
    
    def _check_suspicious_activity(self):
        # Check for patterns like:
        # - Multiple failed auth attempts
        # - Unusual usage spikes
        # - Access from new locations
        # - PII leakage attempts
        pass
    
    def _generate_audit_report(self):
        stats = {
            'audit': self.audit.get_statistics(),
            'rbac': self.rbac.get_stats(),
            'timestamp': datetime.now().isoformat()
        }
        return stats

# Schedule daily
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
auditor = SecurityAuditor(audit_logger, rbac_manager)
scheduler.add_job(auditor.run_daily_audit, 'cron', hour=2)  # 2 AM daily
scheduler.start()
```

### 8.6 Incident Response

Have a plan for security incidents:

```python
class IncidentResponse:
    def __init__(self):
        self.audit = AuditLogger(log_level='FULL')
        self.notification_service = NotificationService()
    
    def handle_pii_breach(self, user_id, pii_types):
        """Handle PII breach incident"""
        # 1. Log the incident
        incident_id = self.audit.log_security_alert(
            alert_type='pii_breach',
            severity='critical',
            description=f'PII breach detected: {pii_types}',
            user_id=user_id
        )
        
        # 2. Notify security team
        self.notification_service.send_alert(
            channel='security-team',
            severity='critical',
            message=f'PII Breach Incident {incident_id}',
            details={'user_id': user_id, 'pii_types': pii_types}
        )
        
        # 3. Revoke access
        self.rbac.revoke_user_access(user_id)
        
        # 4. Trigger investigation
        self._start_investigation(incident_id)
        
        return incident_id
    
    def handle_content_violation(self, user_id, categories):
        """Handle content policy violation"""
        # Similar incident handling...
        pass
```

---

## 9. Performance Considerations

### 9.1 Caching Strategies

Implement caching to reduce overhead:

```python
from functools import lru_cache
import hashlib

class CachedPIIDetector:
    def __init__(self):
        self.detector = PIIDetector()
    
    @lru_cache(maxsize=10000)
    def _cached_detect(self, text_hash):
        return self.detector.detect(self._get_original_text(text_hash))
    
    def detect(self, text):
        # Cache detection results based on text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return self._cached_detect(text_hash)
```

### 9.2 Async Processing

Use async operations for better performance:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncSecurityPipeline:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.pii_detector = PIIDetector()
        self.content_filter = ContentFilter()
    
    async def process(self, text):
        loop = asyncio.get_event_loop()
        
        # Run both checks in parallel
        pii_task = loop.run_in_executor(
            self.executor,
            self.pii_detector.process,
            text
        )
        
        filter_task = loop.run_in_executor(
            self.executor,
            self.content_filter.process,
            text
        )
        
        # Wait for both
        pii_result, filter_result = await asyncio.gather(
            pii_task,
            filter_task
        )
        
        return pii_result, filter_result

# Usage
async def main():
    pipeline = AsyncSecurityPipeline()
    pii_result, filter_result = await pipeline.process(user_input)
```

### 9.3 Batch Processing

Process multiple requests efficiently:

```python
def batch_process_requests(requests, batch_size=32):
    """Process requests in batches for efficiency"""
    pii_detector = PIIDetector()
    content_filter = ContentFilter()
    
    results = []
    for i in range(0, len(requests), batch_size):
        batch = requests[i:i+batch_size]
        
        # Process batch
        batch_results = []
        for request in batch:
            # Run security checks
            filter_result = content_filter.process(request['prompt'])
            pii_result = pii_detector.process(filter_result.filtered_text)
            
            batch_results.append({
                'clean_prompt': pii_result.redacted_text,
                'pii_detected': len(pii_result.matches) > 0,
                'content_filtered': filter_result.was_blocked
            })
        
        results.extend(batch_results)
    
    return results
```

### 9.4 Performance Monitoring

Monitor security overhead:

```python
import time
from contextlib import contextmanager

@contextmanager
def performance_monitor(operation_name):
    start = time.time()
    yield
    duration = (time.time() - start) * 1000
    print(f"{operation_name}: {duration:.2f}ms")

# Usage
with performance_monitor("PII Detection"):
    pii_result = pii_detector.process(text)

with performance_monitor("Content Filtering"):
    filter_result = content_filter.process(text)

with performance_monitor("RBAC Check"):
    rbac.check_permission(user_id, resource, action)
```

---

## 10. Compliance and Regulations

### 10.1 GDPR Compliance

```python
class GDPRCompliantSystem:
    """
    System configured for GDPR compliance
    """
    def __init__(self):
        # Right to erasure
        self.enable_data_deletion = True
        
        # Data minimization
        self.pii_detector = PIIDetector(
            detect=['email', 'phone', 'address', 'name'],
            action='redact'
        )
        
        # Audit requirements
        self.audit = AuditLogger(
            log_level='FULL',
            retention_days=2555  # 7 years
        )
        
        # Consent management
        self.consent_manager = ConsentManager()
    
    def process_with_consent(self, user_id, data, purpose):
        # Check consent
        if not self.consent_manager.has_consent(user_id, purpose):
            raise ConsentRequiredError(
                f"User {user_id} has not consented to {purpose}"
            )
        
        # Log processing
        self.audit.log_api_call(
            user_id=user_id,
            operation='data_processing',
            metadata={
                'purpose': purpose,
                'legal_basis': 'consent'
            }
        )
        
        # Process data
        return self.process_data(data)
    
    def handle_deletion_request(self, user_id):
        """Handle GDPR right to erasure"""
        # Delete user data
        self.delete_user_data(user_id)
        
        # Anonymize logs
        self.audit.anonymize_user_logs(user_id)
        
        # Log deletion
        self.audit.log_security_alert(
            alert_type='data_deletion',
            severity='info',
            description=f'User {user_id} data deleted per GDPR request'
        )
```

### 10.2 HIPAA Compliance

```python
class HIPAACompliantSystem:
    """
    System configured for HIPAA compliance
    """
    def __init__(self):
        # PHI protection
        self.pii_detector = PIIDetector(
            detect=[
                'ssn', 'date_of_birth', 'phone', 'email',
                'address', 'medical_record_number'
            ],
            action='redact',
            confidence_threshold=0.7  # Lower threshold
        )
        
        # Encryption at rest and in transit
        self.audit = AuditLogger(
            log_level='FULL_ENCRYPTED',
            encryption=True,
            encryption_key=get_encryption_key(),
            retention_days=2555  # 7 years
        )
        
        # Access controls
        self.rbac = RBACManager()
        self.setup_hipaa_roles()
    
    def setup_hipaa_roles(self):
        # Minimum necessary access
        healthcare_provider = Role(
            name='healthcare_provider',
            permissions=['patient:read', 'patient:write'],
            description='Healthcare provider with patient access'
        )
        
        administrative_staff = Role(
            name='administrative_staff',
            permissions=['patient:read'],
            description='Administrative staff with limited access'
        )
        
        self.rbac.add_role(healthcare_provider)
        self.rbac.add_role(administrative_staff)
    
    def process_phi(self, user_id, phi_data):
        """Process Protected Health Information"""
        # Verify authorization
        self.rbac.check_permission(user_id, 'patient', 'read')
        
        # Redact PHI
        result = self.pii_detector.process(phi_data)
        
        # Audit access
        self.audit.log_api_call(
            user_id=user_id,
            operation='phi_access',
            metadata={
                'phi_types': [m.pii_type.value for m in result.matches],
                'access_reason': 'treatment'
            }
        )
        
        return result.redacted_text
```

### 10.3 PCI-DSS Compliance

```python
class PCIDSSCompliantSystem:
    """
    System configured for PCI-DSS compliance
    """
    def __init__(self):
        # Never store card data
        self.pii_detector = PIIDetector(
            detect=['credit_card', 'bank_account', 'routing_number'],
            action='block',  # Block, never process
            confidence_threshold=0.95
        )
        
        # Comprehensive logging
        self.audit = AuditLogger(
            log_level='FULL',
            retention_days=365  # 1 year minimum
        )
        
        # Quarterly key rotation
        self.key_manager = KeyRotationManager(
            policy=KeyRotationPolicy(
                rotation_interval_days=90,
                warning_days_before=14
            )
        )
    
    def process_transaction(self, user_id, transaction_data):
        """Process transaction without storing card data"""
        # Block any card data
        try:
            result = self.pii_detector.process(transaction_data)
        except PIIDetectedException:
            self.audit.log_security_alert(
                alert_type='card_data_detected',
                severity='critical',
                description='Attempt to process card data directly',
                user_id=user_id
            )
            raise ValueError(
                "Card data detected. Use tokenized payment processor."
            )
        
        # Log transaction
        self.audit.log_api_call(
            user_id=user_id,
            operation='transaction',
            status='success'
        )
```

---

## 11. Troubleshooting

### 11.1 Common Issues

#### Issue: False Positive PII Detection

```python
# Problem: Legitimate text being flagged as PII
text = "Call 555-HELP for assistance"  # Flagged as phone number

# Solution 1: Adjust confidence threshold
detector = PIIDetector(
    detect=['phone'],
    confidence_threshold=0.95  # Higher threshold
)

# Solution 2: Use whitelist
detector = PIIDetector(
    detect=['phone'],
    whitelist=['555-HELP', '1-800-SUPPORT']
)

# Solution 3: Custom validation
class SmartPIIDetector(PIIDetector):
    def _calculate_confidence(self, pii_type, value):
        confidence = super()._calculate_confidence(pii_type, value)
        
        # Lower confidence for vanity numbers
        if pii_type == PIIType.PHONE and not value.replace('-', '').isdigit():
            confidence *= 0.3
        
        return confidence
```

#### Issue: Performance Degradation

```python
# Problem: Security checks slowing down requests

# Solution 1: Use caching
from functools import lru_cache

class CachedSecurityPipeline:
    @lru_cache(maxsize=1000)
    def check_content(self, text_hash):
        return self.content_filter.process(self._get_text(text_hash))
    
    def process(self, text):
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return self.check_content(text_hash)

# Solution 2: Async processing
async def process_async(text):
    tasks = [
        asyncio.create_task(check_pii(text)),
        asyncio.create_task(check_content(text)),
        asyncio.create_task(check_rbac(user_id))
    ]
    results = await asyncio.gather(*tasks)
    return results

# Solution 3: Optimize regex patterns
# Use compiled patterns and minimize backtracking
import re
pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
```

#### Issue: Quota Exceeded Errors

```python
# Problem: Users hitting rate limits unexpectedly

# Solution 1: Implement grace periods
class GracefulRBACManager(RBACManager):
    def check_quota(self, user_id, **kwargs):
        try:
            super().check_quota(user_id, **kwargs)
        except ResourceLimitExceededError as e:
            # Allow 10% grace over limit
            if self._within_grace_period(user_id):
                logger.warning(f"User {user_id} in grace period")
                return True
            raise

# Solution 2: Better quota tracking
def track_quota_with_prediction(user_id):
    usage = rbac.get_user_stats(user_id)
    
    # Predict if user will exceed quota
    if usage['cost_today'] > usage['max_cost_per_day'] * 0.9:
        notify_user(user_id, "Approaching quota limit")

# Solution 3: Tiered limits
tiered_role = Role(
    name='premium_user',
    max_requests_per_day=10000,  # Higher limit
    max_cost_per_day=100.0,
    burst_limit=100  # Allow short bursts
)
```

### 11.2 Debugging Tips

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('abhikarta.security')
logger.setLevel(logging.DEBUG)

# Add debug handlers
class DebugPIIDetector(PIIDetector):
    def process(self, text):
        logger.debug(f"Processing text length: {len(text)}")
        result = super().process(text)
        logger.debug(f"Found {len(result.matches)} PII matches")
        for match in result.matches:
            logger.debug(f"  - {match}")
        return result

# Test individual components
def test_pii_detection():
    test_cases = [
        "Email: john@example.com",
        "SSN: 123-45-6789",
        "Phone: (555) 123-4567"
    ]
    
    detector = PIIDetector()
    for test in test_cases:
        result = detector.process(test)
        print(f"Input: {test}")
        print(f"Output: {result.redacted_text}")
        print(f"Matches: {len(result.matches)}")
        print()
```

### 11.3 Support and Resources

For issues or questions:

- **GitHub Issues**: https://github.com/ajsinha/abhikarta/issues
- **Email Support**: ajsinha@gmail.com
- **Documentation**: https://abhikarta.readthedocs.io

---

## 12. Appendix

### 12.1 Glossary

| Term | Definition |
|------|------------|
| PII | Personally Identifiable Information |
| PHI | Protected Health Information |
| RBAC | Role-Based Access Control |
| HIPAA | Health Insurance Portability and Accountability Act |
| GDPR | General Data Protection Regulation |
| PCI-DSS | Payment Card Industry Data Security Standard |
| LLM | Large Language Model |
| API | Application Programming Interface |
| Redaction | Removing or obscuring sensitive data |
| Pseudonymization | Replacing identifying data with pseudonyms |
| Zero-downtime | No service interruption during updates |

### 12.2 Regex Patterns Reference

```python
# Email
r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# Phone (US)
r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b'

# SSN
r'\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b'

# Credit Card
r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\b'

# IPv4
r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'

# Date (MM/DD/YYYY)
r'\b(?:0[1-9]|1[0-2])[/-](?:0[1-9]|[12][0-9]|3[01])[/-](?:19|20)\d{2}\b'
```

### 12.3 Configuration Examples

#### Development Configuration

```python
# development_config.py
from abhikarta.security import PIIDetector, ContentFilter, AuditLogger

config = {
    'pii_detection': {
        'enabled': True,
        'action': 'warn',  # Don't block in dev
        'confidence_threshold': 0.7
    },
    'content_filtering': {
        'enabled': True,
        'action': 'warn',
        'threshold': 0.8
    },
    'audit_logging': {
        'enabled': True,
        'log_level': 'FULL',  # Full logging in dev
        'retention_days': 7
    },
    'rbac': {
        'enabled': False,  # Disabled in dev
        'enforce_quotas': False
    }
}
```

#### Production Configuration

```python
# production_config.py
config = {
    'pii_detection': {
        'enabled': True,
        'action': 'redact',  # Strict in production
        'confidence_threshold': 0.8
    },
    'content_filtering': {
        'enabled': True,
        'action': 'block',  # Block violations
        'threshold': 0.8
    },
    'audit_logging': {
        'enabled': True,
        'log_level': 'METADATA_ONLY',  # Privacy-conscious
        'retention_days': 90,
        'encryption': True
    },
    'rbac': {
        'enabled': True,
        'enforce_quotas': True,
        'strict_mode': True
    },
    'key_rotation': {
        'enabled': True,
        'auto_rotate': True,
        'rotation_interval_days': 90
    }
}
```

### 12.4 Changelog

#### Version 1.0 (November 2025)
- Initial release
- PII detection for 12+ data types
- Content filtering with 12 categories
- Comprehensive audit logging
- API key rotation with zero-downtime
- RBAC with quota management
- Multi-tenant support
- HIPAA, GDPR, PCI-DSS compliance features

---

## Document End

**Thank you for using the Abhikarta LLM Security Framework.**

For the latest updates and documentation, visit:
- **GitHub**: https://github.com/ajsinha/abhikarta
- **Email**: ajsinha@gmail.com

---

**Copyright © 2025-2030, All Rights Reserved - Ashutosh Sinha**