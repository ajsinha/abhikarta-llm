"""
PII Detection and Redaction Module

Detects and redacts Personally Identifiable Information (PII) from prompts
before sending to LLM providers.

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import re
import hashlib
import logging
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class PIIType(Enum):
    """Types of PII that can be detected"""
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    PERSON_NAME = "person_name"
    ADDRESS = "address"
    DATE_OF_BIRTH = "date_of_birth"
    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"
    BANK_ACCOUNT = "bank_account"
    CUSTOM = "custom"


class PIIAction(Enum):
    """Actions to take when PII is detected"""
    REDACT = "redact"
    BLOCK = "block"
    ALERT = "alert"
    HASH = "hash"
    MASK = "mask"


@dataclass
class PIIPattern:
    """Pattern definition for PII detection"""
    pii_type: PIIType
    pattern: str
    confidence: float = 1.0
    description: str = ""


@dataclass
class PIIMatch:
    """Represents a detected PII match"""
    pii_type: PIIType
    original_text: str
    start: int
    end: int
    confidence: float
    redacted_text: Optional[str] = None


@dataclass
class PIIDetectionResult:
    """Result of PII detection"""
    original_text: str
    redacted_text: str
    matches: List[PIIMatch] = field(default_factory=list)
    was_blocked: bool = False
    alerts_sent: List[str] = field(default_factory=list)


class PIIDetector:
    """
    Detects and handles PII in text.
    
    Example:
        detector = PIIDetector(
            detect=['email', 'ssn', 'credit_card'],
            action='redact',
            confidence_threshold=0.8
        )
        
        result = detector.process("My email is john@example.com and SSN is 123-45-6789")
        print(result.redacted_text)
        # Output: "My email is [EMAIL_REDACTED] and SSN is [SSN_REDACTED]"
    """
    
    # Built-in PII patterns
    PATTERNS = {
        PIIType.EMAIL: PIIPattern(
            PIIType.EMAIL,
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            1.0,
            "Email address"
        ),
        PIIType.PHONE: PIIPattern(
            PIIType.PHONE,
            r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
            0.95,
            "Phone number"
        ),
        PIIType.SSN: PIIPattern(
            PIIType.SSN,
            r'\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b',
            1.0,
            "Social Security Number"
        ),
        PIIType.CREDIT_CARD: PIIPattern(
            PIIType.CREDIT_CARD,
            r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})\b',
            0.9,
            "Credit card number"
        ),
        PIIType.IP_ADDRESS: PIIPattern(
            PIIType.IP_ADDRESS,
            r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            0.85,
            "IP address"
        ),
        PIIType.DATE_OF_BIRTH: PIIPattern(
            PIIType.DATE_OF_BIRTH,
            r'\b(?:0[1-9]|1[0-2])[/-](?:0[1-9]|[12][0-9]|3[01])[/-](?:19|20)\d{2}\b',
            0.8,
            "Date of birth"
        ),
        PIIType.PASSPORT: PIIPattern(
            PIIType.PASSPORT,
            r'\b[A-Z]{1,2}[0-9]{6,9}\b',
            0.7,
            "Passport number"
        ),
        PIIType.BANK_ACCOUNT: PIIPattern(
            PIIType.BANK_ACCOUNT,
            r'\b\d{8,17}\b',
            0.6,
            "Bank account number"
        ),
    }
    
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
            detect: List of PII types to detect (e.g., ['email', 'ssn'])
            action: Action to take ('redact', 'block', 'alert', 'hash', 'mask')
            confidence_threshold: Minimum confidence to trigger action
            custom_patterns: Custom regex patterns to detect
            alert_callback: Function to call when PII is detected
            preserve_format: Keep original length with masks
        """
        self.detect_types = self._parse_detect_types(detect)
        self.action = PIIAction(action)
        self.confidence_threshold = confidence_threshold
        self.alert_callback = alert_callback
        self.preserve_format = preserve_format
        self.custom_patterns = self._parse_custom_patterns(custom_patterns or {})
        
        # Statistics
        self.detections_count = 0
        self.blocks_count = 0
        self.alerts_count = 0
    
    def _parse_detect_types(self, detect: Optional[List[str]]) -> Set[PIIType]:
        """Parse detection type strings to PIIType enums"""
        if detect is None:
            return set(PIIType)  # Detect all by default
        
        types = set()
        for item in detect:
            try:
                types.add(PIIType(item))
            except ValueError:
                logger.warning(f"Unknown PII type: {item}")
        
        return types
    
    def _parse_custom_patterns(self, patterns: Dict[str, str]) -> List[PIIPattern]:
        """Parse custom pattern definitions"""
        custom = []
        for name, pattern in patterns.items():
            custom.append(PIIPattern(
                PIIType.CUSTOM,
                pattern,
                0.9,
                f"Custom pattern: {name}"
            ))
        return custom
    
    def detect(self, text: str) -> List[PIIMatch]:
        """
        Detect PII in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of PIIMatch objects
        """
        matches = []
        
        # Check built-in patterns
        for pii_type in self.detect_types:
            if pii_type in self.PATTERNS:
                pattern = self.PATTERNS[pii_type]
                for match in re.finditer(pattern.pattern, text):
                    if pattern.confidence >= self.confidence_threshold:
                        matches.append(PIIMatch(
                            pii_type=pii_type,
                            original_text=match.group(0),
                            start=match.start(),
                            end=match.end(),
                            confidence=pattern.confidence
                        ))
        
        # Check custom patterns
        for pattern in self.custom_patterns:
            for match in re.finditer(pattern.pattern, text):
                if pattern.confidence >= self.confidence_threshold:
                    matches.append(PIIMatch(
                        pii_type=PIIType.CUSTOM,
                        original_text=match.group(0),
                        start=match.start(),
                        end=match.end(),
                        confidence=pattern.confidence
                    ))
        
        # Sort by position
        matches.sort(key=lambda m: m.start)
        
        return matches
    
    def redact(self, text: str, matches: List[PIIMatch]) -> str:
        """
        Redact PII from text.
        
        Args:
            text: Original text
            matches: List of PII matches
            
        Returns:
            Redacted text
        """
        if not matches:
            return text
        
        result = []
        last_end = 0
        
        for match in matches:
            # Add text before match
            result.append(text[last_end:match.start])
            
            # Add redacted placeholder
            if self.preserve_format:
                # Preserve length with asterisks
                redacted = '*' * len(match.original_text)
            else:
                redacted = f"[{match.pii_type.value.upper()}_REDACTED]"
            
            result.append(redacted)
            match.redacted_text = redacted
            last_end = match.end
        
        # Add remaining text
        result.append(text[last_end:])
        
        return ''.join(result)
    
    def hash_pii(self, text: str, matches: List[PIIMatch]) -> str:
        """
        Replace PII with hashed values.
        
        Args:
            text: Original text
            matches: List of PII matches
            
        Returns:
            Text with hashed PII
        """
        if not matches:
            return text
        
        result = []
        last_end = 0
        
        for match in matches:
            result.append(text[last_end:match.start])
            
            # Create hash of PII
            hash_obj = hashlib.sha256(match.original_text.encode())
            hashed = hash_obj.hexdigest()[:16]
            result.append(f"[{match.pii_type.value.upper()}_{hashed}]")
            
            last_end = match.end
        
        result.append(text[last_end:])
        
        return ''.join(result)
    
    def mask_pii(self, text: str, matches: List[PIIMatch]) -> str:
        """
        Mask PII (show first/last characters only).
        
        Args:
            text: Original text
            matches: List of PII matches
            
        Returns:
            Text with masked PII
        """
        if not matches:
            return text
        
        result = []
        last_end = 0
        
        for match in matches:
            result.append(text[last_end:match.start])
            
            original = match.original_text
            if len(original) <= 4:
                masked = '*' * len(original)
            else:
                # Show first 2 and last 2 characters
                masked = original[:2] + '*' * (len(original) - 4) + original[-2:]
            
            result.append(masked)
            match.redacted_text = masked
            last_end = match.end
        
        result.append(text[last_end:])
        
        return ''.join(result)
    
    def process(self, text: str) -> PIIDetectionResult:
        """
        Process text according to configured action.
        
        Args:
            text: Text to process
            
        Returns:
            PIIDetectionResult with processed text and metadata
            
        Raises:
            PIIDetectedException: If action is 'block' and PII is found
        """
        # Detect PII
        matches = self.detect(text)
        
        if matches:
            self.detections_count += len(matches)
            logger.info(f"Detected {len(matches)} PII instances in text")
        
        # Take action based on configuration
        redacted_text = text
        was_blocked = False
        alerts = []
        
        if matches:
            if self.action == PIIAction.REDACT:
                redacted_text = self.redact(text, matches)
            
            elif self.action == PIIAction.HASH:
                redacted_text = self.hash_pii(text, matches)
            
            elif self.action == PIIAction.MASK:
                redacted_text = self.mask_pii(text, matches)
            
            elif self.action == PIIAction.BLOCK:
                self.blocks_count += 1
                was_blocked = True
                logger.warning(f"Blocked text containing {len(matches)} PII instances")
            
            elif self.action == PIIAction.ALERT:
                alert_msg = f"PII detected: {len(matches)} instances"
                alerts.append(alert_msg)
                self.alerts_count += 1
                
                if self.alert_callback:
                    self.alert_callback(matches)
        
        return PIIDetectionResult(
            original_text=text,
            redacted_text=redacted_text,
            matches=matches,
            was_blocked=was_blocked,
            alerts_sent=alerts
        )
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get detection statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'total_detections': self.detections_count,
            'total_blocks': self.blocks_count,
            'total_alerts': self.alerts_count
        }


class PIIDetectedException(Exception):
    """Raised when PII is detected and action is 'block'"""
    
    def __init__(self, matches: List[PIIMatch]):
        self.matches = matches
        types = ', '.join(set(m.pii_type.value for m in matches))
        super().__init__(f"PII detected and blocked: {types}")
