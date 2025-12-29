"""
Notification Module - Base Classes and Data Models

Defines the core data structures for the notification system.

Copyright © 2025-2030, All Rights Reserved
Author: Ashutosh Sinha (ajsinha@gmail.com)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import json


# =============================================================================
# ENUMS
# =============================================================================

class NotificationLevel(Enum):
    """Notification severity levels."""
    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    
    @property
    def color(self) -> str:
        """Get color for this level."""
        colors = {
            "debug": "#6c757d",      # Gray
            "info": "#0dcaf0",       # Cyan
            "success": "#198754",    # Green
            "warning": "#ffc107",    # Yellow
            "error": "#dc3545",      # Red
            "critical": "#6f42c1"    # Purple
        }
        return colors.get(self.value, "#0dcaf0")
    
    @property
    def emoji(self) -> str:
        """Get emoji for this level."""
        emojis = {
            "debug": "🔍",
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "critical": "🚨"
        }
        return emojis.get(self.value, "ℹ️")


class NotificationChannel(Enum):
    """Supported notification channels."""
    SLACK = "slack"
    TEAMS = "teams"
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"


class AuthMethod(Enum):
    """Webhook authentication methods."""
    NONE = "none"
    HMAC = "hmac"
    JWT = "jwt"
    API_KEY = "api_key"
    BASIC = "basic"


class NotificationStatus(Enum):
    """Notification delivery status."""
    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Action:
    """Actionable button/link in a notification."""
    label: str
    url: str
    style: str = "default"  # default, primary, danger


@dataclass
class Attachment:
    """File attachment for notifications."""
    filename: str
    content: bytes = None
    content_type: str = "application/octet-stream"
    url: str = None  # Alternative: URL to file


@dataclass
class NotificationMessage:
    """
    Unified notification message format.
    
    Works across all channels with automatic formatting adaptation.
    """
    title: str
    body: str
    level: NotificationLevel = NotificationLevel.INFO
    
    # Optional rich content
    fields: Optional[Dict[str, str]] = None  # Key-value pairs displayed as table
    actions: Optional[List[Action]] = None   # Buttons/links
    attachments: Optional[List[Attachment]] = None
    
    # Metadata
    source: str = "system"              # agent_id, workflow_id, swarm_id
    source_type: str = "system"         # agent, workflow, swarm, system
    source_name: str = ""               # Human-readable name
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None  # For tracking across systems
    
    # Channel-specific overrides (optional)
    slack_channel: Optional[str] = None     # Override default Slack channel
    slack_blocks: Optional[List[Dict]] = None  # Custom Slack Block Kit
    teams_card: Optional[Dict] = None       # Custom Teams Adaptive Card
    email_html: Optional[str] = None        # Custom HTML for email
    
    # Recipients
    recipient_user_id: Optional[str] = None   # Specific user
    recipient_email: Optional[str] = None     # Email address
    recipient_phone: Optional[str] = None     # Phone number for SMS
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "title": self.title,
            "body": self.body,
            "level": self.level.value,
            "fields": self.fields,
            "actions": [{"label": a.label, "url": a.url, "style": a.style} for a in (self.actions or [])],
            "source": self.source,
            "source_type": self.source_type,
            "source_name": self.source_name,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "slack_channel": self.slack_channel,
            "recipient_user_id": self.recipient_user_id,
            "recipient_email": self.recipient_email
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class NotificationResult:
    """Result of a notification send operation."""
    success: bool
    notification_id: str
    channel: NotificationChannel
    status: NotificationStatus
    message_id: Optional[str] = None  # Channel-specific message ID
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "notification_id": self.notification_id,
            "channel": self.channel.value,
            "status": self.status.value,
            "message_id": self.message_id,
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class WebhookEvent:
    """Represents an incoming webhook event."""
    event_id: str
    endpoint_id: str
    endpoint_path: str
    event_type: Optional[str]
    payload: Dict[str, Any]
    headers: Dict[str, str]
    query_params: Dict[str, str]
    timestamp: datetime
    source_ip: str
    verified: bool
    signature: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "endpoint_id": self.endpoint_id,
            "endpoint_path": self.endpoint_path,
            "event_type": self.event_type,
            "payload": self.payload,
            "headers": dict(self.headers),
            "query_params": dict(self.query_params),
            "timestamp": self.timestamp.isoformat(),
            "source_ip": self.source_ip,
            "verified": self.verified
        }


@dataclass
class WebhookEndpoint:
    """Configuration for a webhook endpoint."""
    endpoint_id: str
    path: str
    name: str
    description: str = ""
    auth_method: AuthMethod = AuthMethod.HMAC
    secret: Optional[str] = None  # For HMAC/API key
    
    # Target configuration
    target_type: Optional[str] = None  # 'agent', 'workflow', 'swarm'
    target_id: Optional[str] = None
    
    # Processing options
    is_active: bool = True
    validate_payload: bool = True
    allowed_ips: Optional[List[str]] = None
    rate_limit: Optional[int] = None  # Requests per minute
    
    # Metadata
    created_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


# =============================================================================
# CONFIGURATION CLASSES
# =============================================================================

@dataclass
class ChannelConfig:
    """Base configuration for notification channels."""
    enabled: bool = True
    rate_limit: int = 60  # Requests per minute
    retry_count: int = 3
    timeout_seconds: int = 30


@dataclass
class SlackConfig(ChannelConfig):
    """Slack-specific configuration."""
    bot_token: str = ""          # xoxb-...
    app_token: str = ""          # xapp-... (for Socket Mode)
    signing_secret: str = ""     # For webhook verification
    default_channel: str = "#notifications"
    
    # Optional features
    use_socket_mode: bool = False
    unfurl_links: bool = True
    unfurl_media: bool = True
    
    def validate(self) -> bool:
        """Validate configuration."""
        return bool(self.bot_token and self.default_channel)


@dataclass
class TeamsConfig(ChannelConfig):
    """Microsoft Teams configuration."""
    webhook_url: str = ""        # Incoming webhook URL
    tenant_id: str = ""          # For Graph API (optional)
    client_id: str = ""          # For Graph API (optional)
    client_secret: str = ""      # For Graph API (optional)
    
    # Card formatting
    theme_color: str = "0076D7"  # Default blue
    
    def validate(self) -> bool:
        """Validate configuration."""
        return bool(self.webhook_url)


@dataclass
class EmailConfig(ChannelConfig):
    """Email (SMTP) configuration."""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    use_tls: bool = True
    use_ssl: bool = False
    from_address: str = ""
    from_name: str = "Abhikarta Notifications"
    
    def validate(self) -> bool:
        """Validate configuration."""
        return bool(self.smtp_host and self.smtp_user and self.from_address)


@dataclass 
class SMSConfig(ChannelConfig):
    """SMS (Twilio) configuration."""
    account_sid: str = ""
    auth_token: str = ""
    from_number: str = ""
    
    def validate(self) -> bool:
        """Validate configuration."""
        return bool(self.account_sid and self.auth_token and self.from_number)


# =============================================================================
# ABSTRACT BASE ADAPTER
# =============================================================================

from abc import ABC, abstractmethod


class NotificationAdapter(ABC):
    """
    Abstract base class for notification adapters.
    
    Each channel (Slack, Teams, Email, SMS) implements this interface.
    """
    
    @property
    @abstractmethod
    def channel_type(self) -> NotificationChannel:
        """Return the channel type this adapter handles."""
        pass
    
    @abstractmethod
    async def send(self, message: NotificationMessage) -> NotificationResult:
        """
        Send a notification through this channel.
        
        Args:
            message: The notification to send
            
        Returns:
            NotificationResult with success/failure info
        """
        pass
    
    @abstractmethod
    async def validate_config(self) -> bool:
        """
        Validate the adapter configuration.
        
        Returns:
            True if configuration is valid and channel is reachable
        """
        pass
    
    @abstractmethod
    def format_message(self, message: NotificationMessage) -> Any:
        """
        Format the message for this channel.
        
        Args:
            message: The notification message
            
        Returns:
            Channel-specific formatted message
        """
        pass
    
    def get_rate_limit(self) -> int:
        """Get rate limit for this channel (requests per minute)."""
        return 60
    
    async def test_connection(self) -> bool:
        """Test if the channel is reachable."""
        return await self.validate_config()
