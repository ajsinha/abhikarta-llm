"""
Audit Logging Module

Comprehensive audit logging for LLM operations including request/response
tracking, user activity, cost tracking, and compliance reporting.

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import threading

logger = logging.getLogger(__name__)


class AuditLevel(Enum):
    """Levels of audit logging detail"""
    NONE = "none"
    METADATA_ONLY = "metadata_only"
    FULL = "full"
    FULL_ENCRYPTED = "full_encrypted"


class EventType(Enum):
    """Types of events to audit"""
    API_CALL = "api_call"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    CONFIGURATION_CHANGE = "configuration_change"
    ERROR = "error"
    PII_DETECTION = "pii_detection"
    CONTENT_FILTER = "content_filter"
    RATE_LIMIT = "rate_limit"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    COST_THRESHOLD = "cost_threshold"
    SECURITY_ALERT = "security_alert"


@dataclass
class AuditEvent:
    """Represents a single audit event"""
    event_id: str
    timestamp: datetime
    event_type: EventType
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    operation: Optional[str] = None
    status: str = "success"
    error_message: Optional[str] = None
    
    # Request/Response data
    request_data: Dict[str, Any] = field(default_factory=dict)
    response_data: Dict[str, Any] = field(default_factory=dict)
    
    # Metrics
    tokens_used: int = 0
    cost: float = 0.0
    latency_ms: float = 0.0
    
    # Security
    pii_detected: bool = False
    content_filtered: bool = False
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['event_type'] = self.event_type.value
        return data
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class AuditLogger:
    """
    Comprehensive audit logger for LLM operations.
    
    Example:
        audit = AuditLogger(
            log_level='FULL',
            log_file='audit.log',
            retention_days=90,
            encryption=True
        )
        
        # Log API call
        event = audit.log_api_call(
            user_id='user123',
            provider='anthropic',
            model='claude-3-opus',
            prompt='Hello',
            response='Hi there!',
            tokens=10,
            cost=0.001
        )
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
            log_level: Level of detail ('NONE', 'METADATA_ONLY', 'FULL', 'FULL_ENCRYPTED')
            log_file: Specific log file path
            log_dir: Directory for log files
            retention_days: Days to retain logs
            encryption: Whether to encrypt sensitive data
            encryption_key: Key for encryption
            rotate_daily: Rotate log files daily
            async_logging: Log asynchronously
        """
        self.log_level = AuditLevel(log_level)
        self.log_dir = Path(log_dir)
        self.log_file = log_file
        self.retention_days = retention_days
        self.encryption = encryption
        self.encryption_key = encryption_key
        self.rotate_daily = rotate_daily
        self.async_logging = async_logging
        
        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize file logger
        self._setup_file_logger()
        
        # Statistics
        self.event_counts = {event_type: 0 for event_type in EventType}
        self.total_events = 0
        self.total_cost = 0.0
        self.total_tokens = 0
        
        # Thread safety
        self._lock = threading.Lock()
    
    def _setup_file_logger(self):
        """Setup file-based logging"""
        if self.log_level == AuditLevel.NONE:
            return
        
        # Create file handler
        if self.log_file:
            log_path = Path(self.log_file)
        else:
            date_str = datetime.now().strftime('%Y-%m-%d')
            log_path = self.log_dir / f"audit_{date_str}.log"
        
        # Configure logger
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not self.encryption or not self.encryption_key:
            return data
        
        # Simple hash-based obfuscation (use proper encryption in production)
        key_bytes = self.encryption_key.encode()
        data_bytes = data.encode()
        
        # XOR with key (simplified - use AES in production)
        encrypted = bytearray()
        for i, byte in enumerate(data_bytes):
            key_byte = key_bytes[i % len(key_bytes)]
            encrypted.append(byte ^ key_byte)
        
        return encrypted.hex()
    
    def _should_log_full_data(self) -> bool:
        """Check if full data should be logged"""
        return self.log_level in [AuditLevel.FULL, AuditLevel.FULL_ENCRYPTED]
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp = datetime.now().isoformat()
        random_data = str(threading.get_ident())
        hash_input = f"{timestamp}:{random_data}".encode()
        return hashlib.sha256(hash_input).hexdigest()[:16]
    
    def log_event(self, event: AuditEvent) -> str:
        """
        Log an audit event.
        
        Args:
            event: AuditEvent to log
            
        Returns:
            Event ID
        """
        if self.log_level == AuditLevel.NONE:
            return event.event_id
        
        with self._lock:
            # Update statistics
            self.total_events += 1
            self.event_counts[event.event_type] += 1
            self.total_tokens += event.tokens_used
            self.total_cost += event.cost
            
            # Prepare log data
            log_data = event.to_dict()
            
            # Handle encryption if needed
            if self.log_level == AuditLevel.FULL_ENCRYPTED:
                if 'request_data' in log_data and log_data['request_data']:
                    log_data['request_data'] = {
                        'encrypted': self._encrypt_data(json.dumps(log_data['request_data']))
                    }
                if 'response_data' in log_data and log_data['response_data']:
                    log_data['response_data'] = {
                        'encrypted': self._encrypt_data(json.dumps(log_data['response_data']))
                    }
            
            # Remove full data if not logging it
            if not self._should_log_full_data():
                log_data.pop('request_data', None)
                log_data.pop('response_data', None)
            
            # Write to log
            logger.info(f"AUDIT: {json.dumps(log_data)}")
        
        return event.event_id
    
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
        error_message: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        **metadata
    ) -> str:
        """
        Log an API call.
        
        Args:
            user_id: User making the request
            provider: LLM provider
            model: Model used
            operation: Operation type
            prompt: Request prompt (if logging full data)
            response: Response text (if logging full data)
            tokens: Tokens used
            cost: Cost incurred
            latency_ms: Request latency
            status: Request status
            error_message: Error message if failed
            session_id: Session ID
            ip_address: Client IP address
            **metadata: Additional metadata
            
        Returns:
            Event ID
        """
        request_data = {}
        response_data = {}
        
        if self._should_log_full_data():
            if prompt:
                request_data['prompt'] = prompt
            if response:
                response_data['response'] = response
        
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(),
            event_type=EventType.API_CALL,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            provider=provider,
            model=model,
            operation=operation,
            status=status,
            error_message=error_message,
            request_data=request_data,
            response_data=response_data,
            tokens_used=tokens,
            cost=cost,
            latency_ms=latency_ms,
            metadata=metadata
        )
        
        return self.log_event(event)
    
    def log_authentication(
        self,
        user_id: str,
        status: str,
        auth_method: str = "api_key",
        ip_address: Optional[str] = None,
        **metadata
    ) -> str:
        """Log authentication attempt"""
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(),
            event_type=EventType.AUTHENTICATION,
            user_id=user_id,
            ip_address=ip_address,
            status=status,
            metadata={'auth_method': auth_method, **metadata}
        )
        return self.log_event(event)
    
    def log_authorization(
        self,
        user_id: str,
        resource: str,
        action: str,
        status: str,
        **metadata
    ) -> str:
        """Log authorization check"""
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(),
            event_type=EventType.AUTHORIZATION,
            user_id=user_id,
            status=status,
            metadata={'resource': resource, 'action': action, **metadata}
        )
        return self.log_event(event)
    
    def log_pii_detection(
        self,
        user_id: str,
        pii_types: List[str],
        action_taken: str,
        **metadata
    ) -> str:
        """Log PII detection"""
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(),
            event_type=EventType.PII_DETECTION,
            user_id=user_id,
            pii_detected=True,
            metadata={'pii_types': pii_types, 'action': action_taken, **metadata}
        )
        return self.log_event(event)
    
    def log_content_filter(
        self,
        user_id: str,
        categories: List[str],
        action_taken: str,
        **metadata
    ) -> str:
        """Log content filtering"""
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(),
            event_type=EventType.CONTENT_FILTER,
            user_id=user_id,
            content_filtered=True,
            metadata={'categories': categories, 'action': action_taken, **metadata}
        )
        return self.log_event(event)
    
    def log_security_alert(
        self,
        alert_type: str,
        severity: str,
        description: str,
        user_id: Optional[str] = None,
        **metadata
    ) -> str:
        """Log security alert"""
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(),
            event_type=EventType.SECURITY_ALERT,
            user_id=user_id,
            status="alert",
            metadata={
                'alert_type': alert_type,
                'severity': severity,
                'description': description,
                **metadata
            }
        )
        return self.log_event(event)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get audit statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'total_events': self.total_events,
            'event_counts': {
                event_type.value: count
                for event_type, count in self.event_counts.items()
                if count > 0
            },
            'total_tokens': self.total_tokens,
            'total_cost': round(self.total_cost, 4),
            'log_level': self.log_level.value
        }
    
    def export_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_types: Optional[List[EventType]] = None,
        user_id: Optional[str] = None,
        output_file: str = "audit_export.json"
    ) -> int:
        """
        Export audit logs to file.
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            event_types: Event types to include
            user_id: Filter by user ID
            output_file: Output file path
            
        Returns:
            Number of events exported
        """
        # This would read from log files and export
        # Implementation would depend on log storage format
        logger.info(f"Exporting audit logs to {output_file}")
        return 0  # Placeholder
    
    def cleanup_old_logs(self) -> int:
        """
        Clean up logs older than retention period.
        
        Returns:
            Number of files deleted
        """
        if self.retention_days <= 0:
            return 0
        
        cutoff_date = datetime.now().timestamp() - (self.retention_days * 86400)
        deleted = 0
        
        for log_file in self.log_dir.glob("audit_*.log"):
            if log_file.stat().st_mtime < cutoff_date:
                log_file.unlink()
                deleted += 1
                logger.info(f"Deleted old audit log: {log_file}")
        
        return deleted
