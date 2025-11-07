"""
PII Detection Module - Standalone Functions

Provides simple standalone functions for detecting PII in text.

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

from typing import List, Dict, Optional
from .pii_detector import PIIDetector, PIIType, PIIMatch, PIIDetectionResult


def detect_pii(
    text: str,
    pii_types: Optional[List[str]] = None,
    confidence_threshold: float = 0.8,
    custom_patterns: Optional[Dict[str, str]] = None
) -> List[PIIMatch]:
    """
    Detect PII in text and return list of matches.
    
    Simple standalone function for PII detection without needing to create a detector object.
    
    Args:
        text: Text to scan for PII
        pii_types: List of PII types to detect. If None, detects all types.
                  Options: 'email', 'phone', 'ssn', 'credit_card', 'ip_address',
                          'person_name', 'address', 'date_of_birth', 'passport',
                          'driver_license', 'bank_account'
        confidence_threshold: Minimum confidence score (0-1) for detection
        custom_patterns: Dictionary of custom regex patterns {name: pattern}
    
    Returns:
        List of PIIMatch objects containing detected PII
    
    Example:
        >>> matches = detect_pii("Email: john@example.com", pii_types=['email'])
        >>> print(f"Found {len(matches)} PII items")
        >>> for match in matches:
        >>>     print(f"{match.pii_type.value}: {match.original_text}")
    """
    if pii_types is None:
        pii_types = ['email', 'phone', 'ssn', 'credit_card', 'ip_address']
    
    detector = PIIDetector(
        detect=pii_types,
        action='alert',  # Just detect, don't modify
        confidence_threshold=confidence_threshold,
        custom_patterns=custom_patterns
    )
    
    result = detector.process(text)
    return result.matches


def detect_emails(text: str) -> List[PIIMatch]:
    """
    Detect email addresses in text.
    
    Args:
        text: Text to scan
    
    Returns:
        List of PIIMatch objects for found emails
    
    Example:
        >>> emails = detect_emails("Contact: john@example.com, jane@example.org")
        >>> print(f"Found {len(emails)} email(s)")
    """
    return detect_pii(text, pii_types=['email'])


def detect_phone_numbers(text: str) -> List[PIIMatch]:
    """
    Detect phone numbers in text.
    
    Args:
        text: Text to scan
    
    Returns:
        List of PIIMatch objects for found phone numbers
    
    Example:
        >>> phones = detect_phone_numbers("Call: 555-123-4567 or 1-800-555-0199")
        >>> print(f"Found {len(phones)} phone number(s)")
    """
    return detect_pii(text, pii_types=['phone'])


def detect_ssn(text: str) -> List[PIIMatch]:
    """
    Detect Social Security Numbers in text.
    
    Args:
        text: Text to scan
    
    Returns:
        List of PIIMatch objects for found SSNs
    
    Example:
        >>> ssns = detect_ssn("SSN: 123-45-6789")
        >>> print(f"Found {len(ssns)} SSN(s)")
    """
    return detect_pii(text, pii_types=['ssn'])


def detect_credit_cards(text: str) -> List[PIIMatch]:
    """
    Detect credit card numbers in text.
    
    Args:
        text: Text to scan
    
    Returns:
        List of PIIMatch objects for found credit cards
    
    Example:
        >>> cards = detect_credit_cards("Card: 4532-1234-5678-9010")
        >>> print(f"Found {len(cards)} credit card(s)")
    """
    return detect_pii(text, pii_types=['credit_card'])


def has_pii(
    text: str,
    pii_types: Optional[List[str]] = None,
    confidence_threshold: float = 0.8
) -> bool:
    """
    Check if text contains any PII.
    
    Args:
        text: Text to check
        pii_types: List of PII types to check for. If None, checks all types.
        confidence_threshold: Minimum confidence score for detection
    
    Returns:
        True if PII found, False otherwise
    
    Example:
        >>> if has_pii("Email me at john@example.com"):
        >>>     print("Warning: PII detected!")
    """
    matches = detect_pii(text, pii_types, confidence_threshold)
    return len(matches) > 0


def count_pii(
    text: str,
    pii_types: Optional[List[str]] = None,
    confidence_threshold: float = 0.8
) -> Dict[str, int]:
    """
    Count PII occurrences by type.
    
    Args:
        text: Text to scan
        pii_types: List of PII types to count. If None, counts all types.
        confidence_threshold: Minimum confidence score for detection
    
    Returns:
        Dictionary mapping PII type to count
    
    Example:
        >>> counts = count_pii("Email: a@b.com, Phone: 555-1234, Email: c@d.com")
        >>> print(counts)
        >>> # Output: {'email': 2, 'phone': 1}
    """
    matches = detect_pii(text, pii_types, confidence_threshold)
    
    counts = {}
    for match in matches:
        pii_type = match.pii_type.value
        counts[pii_type] = counts.get(pii_type, 0) + 1
    
    return counts


def get_pii_locations(
    text: str,
    pii_types: Optional[List[str]] = None,
    confidence_threshold: float = 0.8
) -> List[Dict]:
    """
    Get detailed information about PII locations in text.
    
    Args:
        text: Text to scan
        pii_types: List of PII types to find. If None, finds all types.
        confidence_threshold: Minimum confidence score for detection
    
    Returns:
        List of dictionaries with PII details (type, value, start, end, confidence)
    
    Example:
        >>> locations = get_pii_locations("Email: john@example.com at position 7")
        >>> for loc in locations:
        >>>     print(f"{loc['type']} at position {loc['start']}-{loc['end']}")
    """
    matches = detect_pii(text, pii_types, confidence_threshold)
    
    locations = []
    for match in matches:
        locations.append({
            'type': match.pii_type.value,
            'value': match.original_text,
            'start': match.start,
            'end': match.end,
            'confidence': match.confidence
        })
    
    return locations


def detect_pii_batch(
    texts: List[str],
    pii_types: Optional[List[str]] = None,
    confidence_threshold: float = 0.8
) -> List[List[PIIMatch]]:
    """
    Detect PII in multiple texts efficiently.
    
    Args:
        texts: List of texts to scan
        pii_types: List of PII types to detect. If None, detects all types.
        confidence_threshold: Minimum confidence score for detection
    
    Returns:
        List of lists, where each inner list contains PIIMatch objects for that text
    
    Example:
        >>> texts = ["Email: a@b.com", "Phone: 555-1234", "No PII here"]
        >>> results = detect_pii_batch(texts, pii_types=['email', 'phone'])
        >>> for i, matches in enumerate(results):
        >>>     print(f"Text {i}: Found {len(matches)} PII item(s)")
    """
    if pii_types is None:
        pii_types = ['email', 'phone', 'ssn', 'credit_card', 'ip_address']
    
    detector = PIIDetector(
        detect=pii_types,
        action='alert',
        confidence_threshold=confidence_threshold
    )
    
    results = []
    for text in texts:
        result = detector.process(text)
        results.append(result.matches)
    
    return results


# Convenience functions for common use cases

def find_emails(text: str) -> List[str]:
    """
    Find and return email addresses as strings.
    
    Args:
        text: Text to scan
    
    Returns:
        List of email address strings
    
    Example:
        >>> emails = find_emails("Contact: a@b.com or c@d.org")
        >>> print(emails)
        >>> # Output: ['a@b.com', 'c@d.org']
    """
    matches = detect_emails(text)
    return [match.original_text for match in matches]


def find_phone_numbers(text: str) -> List[str]:
    """
    Find and return phone numbers as strings.
    
    Args:
        text: Text to scan
    
    Returns:
        List of phone number strings
    
    Example:
        >>> phones = find_phone_numbers("Call 555-1234 or 555-5678")
        >>> print(phones)
        >>> # Output: ['555-1234', '555-5678']
    """
    matches = detect_phone_numbers(text)
    return [match.original_text for match in matches]


def scan_for_sensitive_data(text: str) -> Dict:
    """
    Comprehensive scan for all types of sensitive data.
    
    Args:
        text: Text to scan
    
    Returns:
        Dictionary with scan results including matches, counts, and summary
    
    Example:
        >>> results = scan_for_sensitive_data("Email: a@b.com, SSN: 123-45-6789")
        >>> print(f"Total PII items: {results['total_count']}")
        >>> print(f"Types found: {results['types_found']}")
    """
    all_types = ['email', 'phone', 'ssn', 'credit_card', 'ip_address', 
                 'date_of_birth', 'passport', 'driver_license', 'bank_account']
    
    matches = detect_pii(text, pii_types=all_types)
    counts = count_pii(text, pii_types=all_types)
    
    return {
        'has_pii': len(matches) > 0,
        'total_count': len(matches),
        'types_found': list(counts.keys()),
        'counts_by_type': counts,
        'matches': matches,
        'locations': get_pii_locations(text, pii_types=all_types)
    }


__all__ = [
    'detect_pii',
    'detect_emails',
    'detect_phone_numbers',
    'detect_ssn',
    'detect_credit_cards',
    'has_pii',
    'count_pii',
    'get_pii_locations',
    'detect_pii_batch',
    'find_emails',
    'find_phone_numbers',
    'scan_for_sensitive_data'
]
