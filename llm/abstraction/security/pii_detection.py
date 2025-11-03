"""
PII Detection and Redaction Module

Detects and redacts Personally Identifiable Information (PII) from text.

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import re
import hashlib
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum


class PIIType(Enum):
    """Types of PII that can be detected"""
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"
    DATE_OF_BIRTH = "date_of_birth"
    ADDRESS = "address"
    NAME = "name"
    ACCOUNT_NUMBER = "account_number"
    ROUTING_NUMBER = "routing_number"
    API_KEY = "api_key"
    PASSWORD = "password"


class RedactionAction(Enum):
    """Actions to take when PII is detected"""
    REDACT = "redact"  # Replace with [REDACTED]
    MASK = "mask"      # Replace with asterisks
    HASH = "hash"      # Replace with hash
    BLOCK = "block"    # Raise exception
    ALERT = "alert"    # Log alert but allow


@dataclass
class PIIMatch:
    """Represents a detected PII match"""
    pii_type: PIIType
    start: int
    end: int
    value: str
    confidence: float
    
    def __repr__(self):
        return f"PIIMatch({self.pii_type.value}, confidence={self.confidence:.2f})"


class PIIDetector:
    """
    Detects and redacts PII from text using regex patterns and heuristics.
    
    Example:
        detector = PIIDetector(
            detect=[PIIType.EMAIL, PIIType.SSN],
            action=RedactionAction.REDACT
        )
        
        clean_text = detector.redact("My email is john@example.com")
        # Returns: "My email is [REDACTED:EMAIL]"
    """
    
    # Regex patterns for different PII types
    PATTERNS = {
        PIIType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        PIIType.PHONE: r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
        PIIType.SSN: r'\b\d{3}-\d{2}-\d{4}\b',
        PIIType.CREDIT_CARD: r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        PIIType.IP_ADDRESS: r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        PIIType.DATE_OF_BIRTH: r'\b(?:0?[1-9]|1[0-2])[/-](?:0?[1-9]|[12]\d|3[01])[/-](?:19|20)\d{2}\b',
        PIIType.API_KEY: r'\b(?:sk|pk)[-_][a-zA-Z0-9]{32,}\b',
        PIIType.ACCOUNT_NUMBER: r'\b\d{8,17}\b',
        PIIType.ROUTING_NUMBER: r'\b\d{9}\b',
    }
    
    def __init__(
        self,
        detect: Optional[List[PIIType]] = None,
        action: RedactionAction = RedactionAction.REDACT,
        custom_patterns: Optional[Dict[str, str]] = None,
        confidence_threshold: float = 0.8
    ):
        """
        Initialize PII detector.
        
        Args:
            detect: List of PII types to detect (None = all)
            action: Action to take when PII is found
            custom_patterns: Additional regex patterns to detect
            confidence_threshold: Minimum confidence for detection
        """
        self.detect_types = detect or list(PIIType)
        self.action = action
        self.confidence_threshold = confidence_threshold
        self.custom_patterns = custom_patterns or {}
        
        # Compile regex patterns
        self.compiled_patterns = {}
        for pii_type in self.detect_types:
            if pii_type in self.PATTERNS:
                self.compiled_patterns[pii_type] = re.compile(
                    self.PATTERNS[pii_type],
                    re.IGNORECASE
                )
    
    def detect(self, text: str) -> List[PIIMatch]:
        """
        Detect PII in text.
        
        Args:
            text: Text to scan for PII
            
        Returns:
            List of PIIMatch objects
        """
        matches = []
        
        for pii_type, pattern in self.compiled_patterns.items():
            for match in pattern.finditer(text):
                confidence = self._calculate_confidence(pii_type, match.group())
                
                if confidence >= self.confidence_threshold:
                    matches.append(PIIMatch(
                        pii_type=pii_type,
                        start=match.start(),
                        end=match.end(),
                        value=match.group(),
                        confidence=confidence
                    ))
        
        # Sort by position
        matches.sort(key=lambda m: m.start)
        
        return matches
    
    def redact(self, text: str) -> str:
        """
        Redact PII from text based on configured action.
        
        Args:
            text: Text to redact
            
        Returns:
            Redacted text
            
        Raises:
            PIIDetectedException: If action is BLOCK and PII is found
        """
        matches = self.detect(text)
        
        if not matches:
            return text
        
        if self.action == RedactionAction.BLOCK:
            raise PIIDetectedException(
                f"PII detected: {[m.pii_type.value for m in matches]}"
            )
        
        # Build redacted text from end to start (to preserve indices)
        redacted = text
        for match in reversed(matches):
            replacement = self._get_replacement(match)
            redacted = (
                redacted[:match.start] + 
                replacement + 
                redacted[match.end:]
            )
        
        return redacted
    
    def _get_replacement(self, match: PIIMatch) -> str:
        """Get replacement text for a PII match"""
        if self.action == RedactionAction.REDACT:
            return f"[REDACTED:{match.pii_type.value.upper()}]"
        
        elif self.action == RedactionAction.MASK:
            length = len(match.value)
            # Keep first and last character, mask middle
            if length <= 2:
                return '*' * length
            return match.value[0] + '*' * (length - 2) + match.value[-1]
        
        elif self.action == RedactionAction.HASH:
            hashed = hashlib.sha256(match.value.encode()).hexdigest()[:12]
            return f"[HASH:{hashed}]"
        
        elif self.action == RedactionAction.ALERT:
            # Log alert but don't redact
            import logging
            logging.warning(f"PII detected: {match.pii_type.value} at position {match.start}")
            return match.value
        
        return match.value
    
    def _calculate_confidence(self, pii_type: PIIType, value: str) -> float:
        """
        Calculate confidence score for a potential PII match.
        
        Uses heuristics to reduce false positives.
        """
        confidence = 0.9  # Base confidence for regex match
        
        # Type-specific validation
        if pii_type == PIIType.CREDIT_CARD:
            if not self._validate_luhn(value.replace('-', '').replace(' ', '')):
                confidence *= 0.5
        
        elif pii_type == PIIType.SSN:
            # SSN specific rules (e.g., not all 0s, not 666, etc.)
            numbers = value.replace('-', '')
            if numbers == '000000000' or numbers.startswith('666'):
                confidence *= 0.3
        
        elif pii_type == PIIType.EMAIL:
            # Check for common false positives
            if '@' not in value or '.' not in value.split('@')[1]:
                confidence *= 0.5
        
        elif pii_type == PIIType.IP_ADDRESS:
            # Validate IP address ranges
            parts = value.split('.')
            if any(int(p) > 255 for p in parts):
                confidence = 0.0
        
        return confidence
    
    @staticmethod
    def _validate_luhn(card_number: str) -> bool:
        """Validate credit card using Luhn algorithm"""
        try:
            digits = [int(d) for d in card_number]
            checksum = 0
            
            for i, digit in enumerate(reversed(digits)):
                if i % 2 == 1:
                    digit *= 2
                    if digit > 9:
                        digit -= 9
                checksum += digit
            
            return checksum % 10 == 0
        except:
            return False
    
    def get_statistics(self, text: str) -> Dict[str, int]:
        """
        Get statistics about PII detected in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with counts by PII type
        """
        matches = self.detect(text)
        stats = {pii_type.value: 0 for pii_type in PIIType}
        
        for match in matches:
            stats[match.pii_type.value] += 1
        
        return {k: v for k, v in stats.items() if v > 0}


class PIIDetectedException(Exception):
    """Raised when PII is detected and action is BLOCK"""
    pass


class PIIClientWrapper:
    """
    Wrapper for LLMClient that automatically redacts PII.
    
    Example:
        detector = PIIDetector(detect=[PIIType.EMAIL, PIIType.SSN])
        wrapped_client = PIIClientWrapper(client, detector)
        
        # PII automatically redacted
        response = wrapped_client.complete("My SSN is 123-45-6789")
    """
    
    def __init__(self, client, detector: PIIDetector):
        """
        Initialize PII wrapper.
        
        Args:
            client: LLMClient to wrap
            detector: PIIDetector instance
        """
        self.client = client
        self.detector = detector
        self._pii_stats = []
    
    def complete(self, prompt: str, **kwargs) -> str:
        """Complete with PII redaction"""
        # Redact PII from prompt
        clean_prompt = self.detector.redact(prompt)
        
        # Track statistics
        stats = self.detector.get_statistics(prompt)
        if stats:
            self._pii_stats.append({
                'timestamp': __import__('datetime').datetime.now(),
                'method': 'complete',
                'pii_detected': stats
            })
        
        # Call wrapped client
        return self.client.complete(clean_prompt, **kwargs)
    
    def chat(self, message: str, **kwargs) -> str:
        """Chat with PII redaction"""
        clean_message = self.detector.redact(message)
        
        stats = self.detector.get_statistics(message)
        if stats:
            self._pii_stats.append({
                'timestamp': __import__('datetime').datetime.now(),
                'method': 'chat',
                'pii_detected': stats
            })
        
        return self.client.chat(clean_message, **kwargs)
    
    def get_pii_statistics(self) -> List[Dict]:
        """Get PII detection statistics"""
        return self._pii_stats.copy()
    
    def __getattr__(self, name):
        """Delegate other methods to wrapped client"""
        return getattr(self.client, name)


# Convenience function
def create_pii_protected_client(client, detect_types: List[PIIType] = None):
    """
    Create a PII-protected client wrapper.
    
    Args:
        client: LLMClient to protect
        detect_types: List of PII types to detect
        
    Returns:
        PIIClientWrapper instance
    """
    detector = PIIDetector(
        detect=detect_types,
        action=RedactionAction.REDACT
    )
    return PIIClientWrapper(client, detector)
