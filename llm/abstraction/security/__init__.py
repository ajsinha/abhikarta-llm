"""
Security Module for Abhikarta LLM

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

from .pii_detector import (
    PIIDetector,
    PIIType,
    PIIAction,
    PIIMatch,
    PIIDetectionResult,
    PIIDetectedException
)

# Import standalone PII detection functions
from .detect_pii import (
    detect_pii,
    detect_emails,
    detect_phone_numbers,
    detect_ssn,
    detect_credit_cards,
    has_pii,
    count_pii,
    get_pii_locations,
    find_emails,
    find_phone_numbers,
    scan_for_sensitive_data
)

# Import standalone PII redaction functions
from .redact_pii import (
    redact_pii,
    mask_pii,
    hash_pii,
    redact_emails,
    redact_phone_numbers,
    redact_ssn,
    redact_credit_cards,
    redact_all_pii,
    sanitize_text,
    clean_text_for_llm
)

from .content_filter import (
    ContentFilter,
    ContentCategory,
    FilterAction,
    FilterResult,
    ContentFilterException
)

from .audit_logger import (
    AuditLogger,
    AuditLevel,
    AuditEvent
)

from .key_rotation import (
    KeyRotationManager,
    KeyRotationPolicy,
    APIKey
)

from .rbac import (
    RBACManager,
    Role,
    Permission,
    User,
    RBACException,
    PermissionDeniedError,
    ResourceLimitExceededError
)

# Aliases for backward compatibility
PIIBlockedException = PIIDetectedException
AccessDeniedException = PermissionDeniedError
RotationSchedule = KeyRotationPolicy

__all__ = [
    # PII Detection - Classes
    'PIIDetector',
    'PIIType',
    'PIIAction',
    'PIIMatch',
    'PIIDetectionResult',
    'PIIDetectedException',
    'PIIBlockedException',  # Alias
    
    # PII Detection - Functions
    'detect_pii',
    'detect_emails',
    'detect_phone_numbers',
    'detect_ssn',
    'detect_credit_cards',
    'has_pii',
    'count_pii',
    'get_pii_locations',
    'find_emails',
    'find_phone_numbers',
    'scan_for_sensitive_data',
    
    # PII Redaction - Functions
    'redact_pii',
    'mask_pii',
    'hash_pii',
    'redact_emails',
    'redact_phone_numbers',
    'redact_ssn',
    'redact_credit_cards',
    'redact_all_pii',
    'sanitize_text',
    'clean_text_for_llm',
    
    # Content Filtering
    'ContentFilter',
    'ContentCategory',
    'FilterAction',
    'FilterResult',
    'ContentFilterException',
    
    # Audit Logging
    'AuditLogger',
    'AuditLevel',
    'AuditEvent',
    
    # Key Rotation
    'KeyRotationManager',
    'KeyRotationPolicy',
    'APIKey',
    'RotationSchedule',  # Alias
    
    # RBAC
    'RBACManager',
    'Role',
    'Permission',
    'User',
    'RBACException',
    'PermissionDeniedError',
    'ResourceLimitExceededError',
    'AccessDeniedException',  # Alias
]
