"""
PII Redaction Module - Standalone Functions

Provides simple standalone functions for redacting PII in text.

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

from typing import List, Dict, Optional, Tuple
from .pii_detector import PIIDetector, PIIType, PIIMatch, PIIDetectionResult


def redact_pii(
    text: str,
    pii_types: Optional[List[str]] = None,
    confidence_threshold: float = 0.8,
    custom_patterns: Optional[Dict[str, str]] = None,
    preserve_format: bool = False
) -> str:
    """
    Redact PII from text, replacing with [TYPE_REDACTED] markers.
    
    Simple standalone function for PII redaction without needing to create a detector object.
    
    Args:
        text: Text to redact PII from
        pii_types: List of PII types to redact. If None, redacts common types.
                  Options: 'email', 'phone', 'ssn', 'credit_card', 'ip_address',
                          'person_name', 'address', 'date_of_birth', 'passport',
                          'driver_license', 'bank_account'
        confidence_threshold: Minimum confidence score (0-1) for redaction
        custom_patterns: Dictionary of custom regex patterns {name: pattern}
        preserve_format: If True, maintains original text length with asterisks
    
    Returns:
        Redacted text with PII replaced
    
    Example:
        >>> text = "Email me at john@example.com or call 555-1234"
        >>> redacted = redact_pii(text, pii_types=['email', 'phone'])
        >>> print(redacted)
        >>> # Output: "Email me at [EMAIL_REDACTED] or call [PHONE_REDACTED]"
    """
    if pii_types is None:
        pii_types = ['email', 'phone', 'ssn', 'credit_card']
    
    detector = PIIDetector(
        detect=pii_types,
        action='redact',
        confidence_threshold=confidence_threshold,
        custom_patterns=custom_patterns,
        preserve_format=preserve_format
    )
    
    result = detector.process(text)
    return result.redacted_text


def mask_pii(
    text: str,
    pii_types: Optional[List[str]] = None,
    confidence_threshold: float = 0.8,
    visible_chars: int = 4
) -> str:
    """
    Mask PII in text, showing only last few characters.
    
    Args:
        text: Text to mask PII in
        pii_types: List of PII types to mask. If None, masks common types.
        confidence_threshold: Minimum confidence score for masking
        visible_chars: Number of characters to leave visible at end
    
    Returns:
        Text with PII masked (e.g., ****-****-****-1234)
    
    Example:
        >>> text = "Credit card: 4532-1234-5678-9010"
        >>> masked = mask_pii(text, pii_types=['credit_card'])
        >>> print(masked)
        >>> # Output: "Credit card: ****-****-****-9010"
    """
    if pii_types is None:
        pii_types = ['credit_card', 'ssn', 'phone', 'bank_account']
    
    detector = PIIDetector(
        detect=pii_types,
        action='mask',
        confidence_threshold=confidence_threshold
    )
    
    result = detector.process(text)
    return result.redacted_text


def hash_pii(
    text: str,
    pii_types: Optional[List[str]] = None,
    confidence_threshold: float = 0.8
) -> str:
    """
    Replace PII with cryptographic hashes for pseudonymization.
    
    Args:
        text: Text to hash PII in
        pii_types: List of PII types to hash. If None, hashes all types.
        confidence_threshold: Minimum confidence score for hashing
    
    Returns:
        Text with PII replaced by SHA-256 hashes
    
    Example:
        >>> text = "User email: john@example.com"
        >>> hashed = hash_pii(text, pii_types=['email'])
        >>> print(hashed)
        >>> # Output: "User email: [HASH:a3f2...]"
    """
    if pii_types is None:
        pii_types = ['email', 'phone', 'ssn', 'credit_card', 'ip_address']
    
    detector = PIIDetector(
        detect=pii_types,
        action='hash',
        confidence_threshold=confidence_threshold
    )
    
    result = detector.process(text)
    return result.redacted_text


def redact_emails(text: str) -> str:
    """
    Redact email addresses from text.
    
    Args:
        text: Text to redact emails from
    
    Returns:
        Text with emails redacted
    
    Example:
        >>> redacted = redact_emails("Contact: john@example.com")
        >>> print(redacted)
        >>> # Output: "Contact: [EMAIL_REDACTED]"
    """
    return redact_pii(text, pii_types=['email'])


def redact_phone_numbers(text: str) -> str:
    """
    Redact phone numbers from text.
    
    Args:
        text: Text to redact phone numbers from
    
    Returns:
        Text with phone numbers redacted
    
    Example:
        >>> redacted = redact_phone_numbers("Call: 555-123-4567")
        >>> print(redacted)
        >>> # Output: "Call: [PHONE_REDACTED]"
    """
    return redact_pii(text, pii_types=['phone'])


def redact_ssn(text: str) -> str:
    """
    Redact Social Security Numbers from text.
    
    Args:
        text: Text to redact SSNs from
    
    Returns:
        Text with SSNs redacted
    
    Example:
        >>> redacted = redact_ssn("SSN: 123-45-6789")
        >>> print(redacted)
        >>> # Output: "SSN: [SSN_REDACTED]"
    """
    return redact_pii(text, pii_types=['ssn'])


def redact_credit_cards(text: str) -> str:
    """
    Redact credit card numbers from text.
    
    Args:
        text: Text to redact credit cards from
    
    Returns:
        Text with credit cards redacted
    
    Example:
        >>> redacted = redact_credit_cards("Card: 4532-1234-5678-9010")
        >>> print(redacted)
        >>> # Output: "Card: [CREDIT_CARD_REDACTED]"
    """
    return redact_pii(text, pii_types=['credit_card'])


def redact_all_pii(text: str, confidence_threshold: float = 0.8) -> str:
    """
    Redact all types of PII from text.
    
    Args:
        text: Text to redact all PII from
        confidence_threshold: Minimum confidence score for redaction
    
    Returns:
        Text with all PII redacted
    
    Example:
        >>> text = "Email: a@b.com, Phone: 555-1234, SSN: 123-45-6789"
        >>> redacted = redact_all_pii(text)
        >>> print(redacted)
        >>> # Output: "Email: [EMAIL_REDACTED], Phone: [PHONE_REDACTED], SSN: [SSN_REDACTED]"
    """
    all_types = ['email', 'phone', 'ssn', 'credit_card', 'ip_address',
                 'date_of_birth', 'passport', 'driver_license', 'bank_account']
    
    return redact_pii(text, pii_types=all_types, confidence_threshold=confidence_threshold)


def sanitize_text(
    text: str,
    pii_types: Optional[List[str]] = None,
    replacement: str = "[REDACTED]"
) -> str:
    """
    Sanitize text by removing PII with a custom replacement.
    
    Args:
        text: Text to sanitize
        pii_types: List of PII types to remove. If None, removes common types.
        replacement: Custom replacement string
    
    Returns:
        Sanitized text
    
    Example:
        >>> text = "User email: john@example.com"
        >>> sanitized = sanitize_text(text, replacement="***")
        >>> print(sanitized)
        >>> # Output: "User email: ***"
    """
    if pii_types is None:
        pii_types = ['email', 'phone', 'ssn', 'credit_card']
    
    # Redact first
    redacted = redact_pii(text, pii_types=pii_types)
    
    # Replace all [TYPE_REDACTED] patterns with custom replacement
    import re
    sanitized = re.sub(r'\[.*?_REDACTED\]', replacement, redacted)
    
    return sanitized


def redact_pii_with_details(
    text: str,
    pii_types: Optional[List[str]] = None,
    confidence_threshold: float = 0.8
) -> Tuple[str, List[PIIMatch]]:
    """
    Redact PII and return both redacted text and details about what was redacted.
    
    Args:
        text: Text to redact PII from
        pii_types: List of PII types to redact
        confidence_threshold: Minimum confidence score for redaction
    
    Returns:
        Tuple of (redacted_text, list of PIIMatch objects)
    
    Example:
        >>> text = "Email: john@example.com, Phone: 555-1234"
        >>> redacted, matches = redact_pii_with_details(text)
        >>> print(f"Redacted: {redacted}")
        >>> print(f"Removed {len(matches)} PII items")
    """
    if pii_types is None:
        pii_types = ['email', 'phone', 'ssn', 'credit_card']
    
    detector = PIIDetector(
        detect=pii_types,
        action='redact',
        confidence_threshold=confidence_threshold
    )
    
    result = detector.process(text)
    return result.redacted_text, result.matches


def safe_redact(
    text: str,
    pii_types: Optional[List[str]] = None,
    on_error: str = "original"
) -> str:
    """
    Safely redact PII with error handling.
    
    Args:
        text: Text to redact PII from
        pii_types: List of PII types to redact
        on_error: What to return on error - "original" or "empty"
    
    Returns:
        Redacted text, or fallback on error
    
    Example:
        >>> text = "Email: john@example.com"
        >>> redacted = safe_redact(text, pii_types=['email'])
        >>> print(redacted)
    """
    try:
        return redact_pii(text, pii_types=pii_types)
    except Exception as e:
        if on_error == "empty":
            return ""
        else:
            return text


def redact_pii_batch(
    texts: List[str],
    pii_types: Optional[List[str]] = None,
    confidence_threshold: float = 0.8
) -> List[str]:
    """
    Redact PII from multiple texts efficiently.
    
    Args:
        texts: List of texts to redact
        pii_types: List of PII types to redact
        confidence_threshold: Minimum confidence score for redaction
    
    Returns:
        List of redacted texts
    
    Example:
        >>> texts = ["Email: a@b.com", "Phone: 555-1234", "No PII"]
        >>> redacted = redact_pii_batch(texts)
        >>> for original, clean in zip(texts, redacted):
        >>>     print(f"{original} -> {clean}")
    """
    if pii_types is None:
        pii_types = ['email', 'phone', 'ssn', 'credit_card']
    
    detector = PIIDetector(
        detect=pii_types,
        action='redact',
        confidence_threshold=confidence_threshold
    )
    
    redacted_texts = []
    for text in texts:
        result = detector.process(text)
        redacted_texts.append(result.redacted_text)
    
    return redacted_texts


def create_redacted_summary(
    text: str,
    pii_types: Optional[List[str]] = None
) -> Dict:
    """
    Create a summary of PII redaction with statistics.
    
    Args:
        text: Text to analyze
        pii_types: List of PII types to check
    
    Returns:
        Dictionary with redacted text and statistics
    
    Example:
        >>> text = "Email: a@b.com, Phone: 555-1234, SSN: 123-45-6789"
        >>> summary = create_redacted_summary(text)
        >>> print(summary['redacted_text'])
        >>> print(f"Redacted {summary['total_redacted']} items")
    """
    if pii_types is None:
        pii_types = ['email', 'phone', 'ssn', 'credit_card', 'ip_address']
    
    detector = PIIDetector(
        detect=pii_types,
        action='redact'
    )
    
    result = detector.process(text)
    
    # Count by type
    counts = {}
    for match in result.matches:
        pii_type = match.pii_type.value
        counts[pii_type] = counts.get(pii_type, 0) + 1
    
    return {
        'original_text': text,
        'redacted_text': result.redacted_text,
        'total_redacted': len(result.matches),
        'types_redacted': list(counts.keys()),
        'counts_by_type': counts,
        'matches': result.matches
    }


# Convenience function for common use case
def clean_text_for_llm(text: str) -> str:
    """
    Clean text for safe LLM processing by redacting sensitive PII.
    
    Redacts: emails, phones, SSNs, credit cards, IP addresses
    
    Args:
        text: User input text
    
    Returns:
        Cleaned text safe for LLM processing
    
    Example:
        >>> user_input = "My email is secret@example.com and SSN is 123-45-6789"
        >>> clean = clean_text_for_llm(user_input)
        >>> # Now safe to send to LLM
        >>> response = llm_client.complete(clean)
    """
    return redact_pii(
        text,
        pii_types=['email', 'phone', 'ssn', 'credit_card', 'ip_address'],
        confidence_threshold=0.7  # Slightly lower threshold for safety
    )


__all__ = [
    'redact_pii',
    'mask_pii',
    'hash_pii',
    'redact_emails',
    'redact_phone_numbers',
    'redact_ssn',
    'redact_credit_cards',
    'redact_all_pii',
    'sanitize_text',
    'redact_pii_with_details',
    'safe_redact',
    'redact_pii_batch',
    'create_redacted_summary',
    'clean_text_for_llm'
]
