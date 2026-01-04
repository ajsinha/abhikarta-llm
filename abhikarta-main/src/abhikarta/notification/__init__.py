"""
Abhikarta-LLM Notification Module

Enterprise notification system supporting:
- Slack integration
- Microsoft Teams integration
- Email notifications
- SMS notifications (via Twilio)
- Webhook endpoints for receiving external events

Version: 1.4.0
Copyright © 2025-2030, All Rights Reserved
Author: Ashutosh Sinha (ajsinha@gmail.com)
"""

from .base import (
    NotificationLevel,
    NotificationMessage,
    NotificationResult,
    NotificationChannel,
    Action,
    Attachment,
    WebhookEvent,
    WebhookEndpoint,
    AuthMethod,
    ChannelConfig,
    SlackConfig,
    TeamsConfig,
    EmailConfig
)

from .manager import NotificationManager
from .slack_adapter import SlackAdapter
from .teams_adapter import TeamsAdapter
from .webhook_receiver import WebhookReceiver

__all__ = [
    # Enums and Models
    'NotificationLevel',
    'NotificationMessage',
    'NotificationResult',
    'NotificationChannel',
    'Action',
    'Attachment',
    'WebhookEvent',
    'WebhookEndpoint',
    'AuthMethod',
    'ChannelConfig',
    'SlackConfig',
    'TeamsConfig',
    'EmailConfig',
    
    # Core Classes
    'NotificationManager',
    'SlackAdapter',
    'TeamsAdapter',
    'WebhookReceiver',
]

__version__ = "1.4.8"
