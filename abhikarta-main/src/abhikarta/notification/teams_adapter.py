"""
Teams Adapter - Microsoft Teams integration for notifications.

Supports:
- Incoming Webhook messages
- Adaptive Cards
- MessageCard format
- @mentions
- Action buttons

Copyright © 2025-2030, All Rights Reserved
Author: Ashutosh Sinha (ajsinha@gmail.com)
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

import aiohttp

from .base import (
    NotificationAdapter,
    NotificationChannel,
    NotificationMessage,
    NotificationResult,
    NotificationStatus,
    NotificationLevel,
    TeamsConfig,
    Action
)

logger = logging.getLogger(__name__)


class TeamsAdapter(NotificationAdapter):
    """
    Microsoft Teams notification adapter using Incoming Webhooks.
    
    Features:
    - Send to channel via webhook
    - Adaptive Card formatting
    - MessageCard legacy format
    - Action buttons
    - Rich formatting
    
    Requires:
    - Incoming Webhook URL for the target channel
    
    Setup:
    1. In Teams, go to the channel
    2. Click "..." → Connectors
    3. Add "Incoming Webhook"
    4. Copy the webhook URL
    """
    
    # Level to theme color mapping
    LEVEL_COLOR = {
        NotificationLevel.DEBUG: "6c757d",
        NotificationLevel.INFO: "0076D7",
        NotificationLevel.SUCCESS: "2DC72D",
        NotificationLevel.WARNING: "FFC107",
        NotificationLevel.ERROR: "DC3545",
        NotificationLevel.CRITICAL: "6f42c1",
    }
    
    # Level to icon mapping (for Adaptive Cards)
    LEVEL_ICON = {
        NotificationLevel.DEBUG: "🔍",
        NotificationLevel.INFO: "ℹ️",
        NotificationLevel.SUCCESS: "✅",
        NotificationLevel.WARNING: "⚠️",
        NotificationLevel.ERROR: "❌",
        NotificationLevel.CRITICAL: "🚨",
    }
    
    def __init__(self, config: TeamsConfig):
        """
        Initialize Teams adapter.
        
        Args:
            config: Teams configuration
        """
        self.config = config
        self.webhook_url = config.webhook_url
        self.theme_color = config.theme_color
        self._session: Optional[aiohttp.ClientSession] = None
    
    @property
    def channel_type(self) -> NotificationChannel:
        """Return channel type."""
        return NotificationChannel.TEAMS
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={"Content-Type": "application/json"}
            )
        return self._session
    
    async def close(self) -> None:
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def send(self, message: NotificationMessage) -> NotificationResult:
        """
        Send notification to Microsoft Teams.
        
        Args:
            message: The notification message
            
        Returns:
            NotificationResult
        """
        notification_id = str(uuid.uuid4())
        
        try:
            # Format message for Teams
            if message.teams_card:
                payload = message.teams_card
            else:
                payload = self.format_message(message)
            
            # Send via webhook
            session = await self._get_session()
            async with session.post(
                self.webhook_url,
                json=payload
            ) as response:
                # Teams returns 200 OK with "1" for success
                if response.status == 200:
                    text = await response.text()
                    if text == "1":
                        logger.info("Teams message sent successfully")
                        return NotificationResult(
                            success=True,
                            notification_id=notification_id,
                            channel=NotificationChannel.TEAMS,
                            status=NotificationStatus.SENT,
                            message_id=notification_id
                        )
                    else:
                        logger.warning(f"Teams webhook response: {text}")
                        return NotificationResult(
                            success=True,  # Still treat as success
                            notification_id=notification_id,
                            channel=NotificationChannel.TEAMS,
                            status=NotificationStatus.SENT,
                            message_id=notification_id
                        )
                else:
                    error = await response.text()
                    logger.error(f"Teams webhook error: {response.status} - {error}")
                    return NotificationResult(
                        success=False,
                        notification_id=notification_id,
                        channel=NotificationChannel.TEAMS,
                        status=NotificationStatus.FAILED,
                        error=f"HTTP {response.status}: {error}"
                    )
                    
        except Exception as e:
            logger.error(f"Error sending Teams message: {e}")
            return NotificationResult(
                success=False,
                notification_id=notification_id,
                channel=NotificationChannel.TEAMS,
                status=NotificationStatus.FAILED,
                error=str(e)
            )
    
    async def validate_config(self) -> bool:
        """
        Validate Teams configuration.
        
        Note: We can't fully validate without sending a message,
        so we just check if the webhook URL looks valid.
        
        Returns:
            True if configuration appears valid
        """
        if not self.webhook_url:
            return False
        
        # Basic URL validation
        if not self.webhook_url.startswith("https://"):
            return False
        
        if "webhook.office.com" not in self.webhook_url and \
           "outlook.office.com" not in self.webhook_url and \
           "office365.com" not in self.webhook_url:
            logger.warning("Webhook URL doesn't look like a Teams webhook")
        
        return True
    
    def format_message(self, message: NotificationMessage) -> Dict[str, Any]:
        """
        Format notification message as Teams Adaptive Card.
        
        Args:
            message: The notification message
            
        Returns:
            Teams message payload (Adaptive Card wrapped in message)
        """
        level_color = self.LEVEL_COLOR.get(message.level, "0076D7")
        level_icon = self.LEVEL_ICON.get(message.level, "ℹ️")
        
        # Build Adaptive Card body
        body = []
        
        # Title container with icon
        body.append({
            "type": "Container",
            "style": "emphasis",
            "items": [
                {
                    "type": "ColumnSet",
                    "columns": [
                        {
                            "type": "Column",
                            "width": "auto",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": level_icon,
                                    "size": "Large"
                                }
                            ]
                        },
                        {
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": message.title,
                                    "weight": "Bolder",
                                    "size": "Large",
                                    "wrap": True
                                }
                            ]
                        }
                    ]
                }
            ]
        })
        
        # Body text
        if message.body:
            body.append({
                "type": "TextBlock",
                "text": message.body,
                "wrap": True,
                "spacing": "Medium"
            })
        
        # Fields as FactSet
        if message.fields:
            facts = [
                {"title": key, "value": str(value)}
                for key, value in message.fields.items()
            ]
            body.append({
                "type": "FactSet",
                "facts": facts,
                "spacing": "Medium"
            })
        
        # Source and timestamp
        body.append({
            "type": "Container",
            "separator": True,
            "spacing": "Medium",
            "items": [
                {
                    "type": "ColumnSet",
                    "columns": [
                        {
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": f"📍 Source: {message.source_name or message.source}",
                                    "isSubtle": True,
                                    "size": "Small"
                                }
                            ]
                        },
                        {
                            "type": "Column",
                            "width": "auto",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": f"🕐 {message.timestamp.strftime('%Y-%m-%d %H:%M UTC')}",
                                    "isSubtle": True,
                                    "size": "Small"
                                }
                            ]
                        }
                    ]
                }
            ]
        })
        
        # Build actions
        actions = []
        if message.actions:
            for action in message.actions:
                actions.append({
                    "type": "Action.OpenUrl",
                    "title": action.label,
                    "url": action.url
                })
        
        # Construct the Adaptive Card
        adaptive_card = {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "body": body
        }
        
        if actions:
            adaptive_card["actions"] = actions
        
        # Wrap in Teams message format
        return {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "contentUrl": None,
                    "content": adaptive_card
                }
            ]
        }
    
    def format_message_card(self, message: NotificationMessage) -> Dict[str, Any]:
        """
        Format as legacy MessageCard format.
        
        Use this for older Teams/Outlook integrations.
        
        Args:
            message: The notification message
            
        Returns:
            MessageCard payload
        """
        level_color = self.LEVEL_COLOR.get(message.level, "0076D7")
        level_icon = self.LEVEL_ICON.get(message.level, "ℹ️")
        
        card = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": level_color,
            "summary": message.title,
            "sections": [
                {
                    "activityTitle": f"{level_icon} {message.title}",
                    "activitySubtitle": message.source_name or message.source,
                    "activityImage": None,
                    "text": message.body,
                    "markdown": True
                }
            ]
        }
        
        # Add facts for fields
        if message.fields:
            card["sections"][0]["facts"] = [
                {"name": key, "value": str(value)}
                for key, value in message.fields.items()
            ]
        
        # Add actions
        if message.actions:
            card["potentialAction"] = [
                {
                    "@type": "OpenUri",
                    "name": action.label,
                    "targets": [
                        {"os": "default", "uri": action.url}
                    ]
                }
                for action in message.actions
            ]
        
        return card
    
    def get_rate_limit(self) -> int:
        """Get rate limit for Teams."""
        return self.config.rate_limit
    
    # =========================================================================
    # ADDITIONAL TEAMS FEATURES
    # =========================================================================
    
    async def send_card(
        self,
        card: Dict[str, Any],
        card_type: str = "adaptive"
    ) -> NotificationResult:
        """
        Send a custom card to Teams.
        
        Args:
            card: Card payload
            card_type: "adaptive" or "message"
            
        Returns:
            NotificationResult
        """
        notification_id = str(uuid.uuid4())
        
        try:
            if card_type == "adaptive":
                payload = {
                    "type": "message",
                    "attachments": [
                        {
                            "contentType": "application/vnd.microsoft.card.adaptive",
                            "content": card
                        }
                    ]
                }
            else:
                payload = card
            
            session = await self._get_session()
            async with session.post(self.webhook_url, json=payload) as response:
                if response.status == 200:
                    return NotificationResult(
                        success=True,
                        notification_id=notification_id,
                        channel=NotificationChannel.TEAMS,
                        status=NotificationStatus.SENT,
                        message_id=notification_id
                    )
                else:
                    error = await response.text()
                    return NotificationResult(
                        success=False,
                        notification_id=notification_id,
                        channel=NotificationChannel.TEAMS,
                        status=NotificationStatus.FAILED,
                        error=f"HTTP {response.status}: {error}"
                    )
                    
        except Exception as e:
            logger.error(f"Error sending Teams card: {e}")
            return NotificationResult(
                success=False,
                notification_id=notification_id,
                channel=NotificationChannel.TEAMS,
                status=NotificationStatus.FAILED,
                error=str(e)
            )
    
    @staticmethod
    def create_progress_card(
        title: str,
        steps: List[Dict[str, Any]],
        current_step: int,
        source: str = ""
    ) -> Dict[str, Any]:
        """
        Create a progress indicator card.
        
        Args:
            title: Card title
            steps: List of step dictionaries with 'name' and 'status'
            current_step: Current step index (0-based)
            source: Source name
            
        Returns:
            Adaptive Card payload
        """
        body = [
            {
                "type": "TextBlock",
                "text": title,
                "weight": "Bolder",
                "size": "Large"
            }
        ]
        
        for i, step in enumerate(steps):
            if i < current_step:
                icon = "✅"
                color = "Good"
            elif i == current_step:
                icon = "▶️"
                color = "Accent"
            else:
                icon = "⏳"
                color = "Default"
            
            body.append({
                "type": "TextBlock",
                "text": f"{icon} {step['name']}",
                "color": color,
                "spacing": "Small"
            })
        
        if source:
            body.append({
                "type": "TextBlock",
                "text": f"Source: {source}",
                "isSubtle": True,
                "size": "Small",
                "separator": True
            })
        
        return {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "body": body
        }
    
    @staticmethod
    def create_approval_card(
        title: str,
        description: str,
        approve_url: str,
        reject_url: str,
        details: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Create an approval request card.
        
        Args:
            title: Request title
            description: Request description
            approve_url: URL for approval action
            reject_url: URL for rejection action
            details: Additional detail fields
            
        Returns:
            Adaptive Card payload
        """
        body = [
            {
                "type": "TextBlock",
                "text": "🔔 Approval Required",
                "weight": "Bolder",
                "size": "Large"
            },
            {
                "type": "TextBlock",
                "text": title,
                "weight": "Bolder",
                "spacing": "Medium"
            },
            {
                "type": "TextBlock",
                "text": description,
                "wrap": True
            }
        ]
        
        if details:
            body.append({
                "type": "FactSet",
                "facts": [
                    {"title": k, "value": v}
                    for k, v in details.items()
                ],
                "spacing": "Medium"
            })
        
        return {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "body": body,
            "actions": [
                {
                    "type": "Action.OpenUrl",
                    "title": "✅ Approve",
                    "url": approve_url,
                    "style": "positive"
                },
                {
                    "type": "Action.OpenUrl",
                    "title": "❌ Reject",
                    "url": reject_url,
                    "style": "destructive"
                }
            ]
        }
