"""
Slack Adapter - Slack integration for notifications.

Supports:
- Channel messages (#channel)
- Direct messages (@user)
- Rich formatting (Block Kit)
- File attachments
- Interactive messages
- Thread replies

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
    SlackConfig,
    Action
)

logger = logging.getLogger(__name__)


class SlackAdapter(NotificationAdapter):
    """
    Slack notification adapter using the Web API.
    
    Features:
    - Send to channels and DMs
    - Rich formatting with Block Kit
    - File uploads
    - Interactive components
    - Thread support
    
    Requires:
    - Bot token with chat:write scope
    - Optional: users:read for DM support
    """
    
    # Level to emoji mapping
    LEVEL_EMOJI = {
        NotificationLevel.DEBUG: ":mag:",
        NotificationLevel.INFO: ":information_source:",
        NotificationLevel.SUCCESS: ":white_check_mark:",
        NotificationLevel.WARNING: ":warning:",
        NotificationLevel.ERROR: ":x:",
        NotificationLevel.CRITICAL: ":rotating_light:",
    }
    
    # Level to color mapping (for attachments)
    LEVEL_COLOR = {
        NotificationLevel.DEBUG: "#6c757d",
        NotificationLevel.INFO: "#0dcaf0",
        NotificationLevel.SUCCESS: "#198754",
        NotificationLevel.WARNING: "#ffc107",
        NotificationLevel.ERROR: "#dc3545",
        NotificationLevel.CRITICAL: "#6f42c1",
    }
    
    def __init__(self, config: SlackConfig):
        """
        Initialize Slack adapter.
        
        Args:
            config: Slack configuration
        """
        self.config = config
        self.bot_token = config.bot_token
        self.default_channel = config.default_channel
        self._session: Optional[aiohttp.ClientSession] = None
        self.base_url = "https://slack.com/api"
    
    @property
    def channel_type(self) -> NotificationChannel:
        """Return channel type."""
        return NotificationChannel.SLACK
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.bot_token}",
                    "Content-Type": "application/json; charset=utf-8"
                }
            )
        return self._session
    
    async def close(self) -> None:
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def send(self, message: NotificationMessage) -> NotificationResult:
        """
        Send notification to Slack.
        
        Args:
            message: The notification message
            
        Returns:
            NotificationResult
        """
        notification_id = str(uuid.uuid4())
        
        try:
            # Determine target channel
            channel = message.slack_channel or self.default_channel
            
            # Format message for Slack
            slack_payload = self.format_message(message)
            slack_payload["channel"] = channel
            
            # Send via Web API
            session = await self._get_session()
            async with session.post(
                f"{self.base_url}/chat.postMessage",
                json=slack_payload
            ) as response:
                data = await response.json()
                
                if data.get("ok"):
                    logger.info(f"Slack message sent to {channel}")
                    return NotificationResult(
                        success=True,
                        notification_id=notification_id,
                        channel=NotificationChannel.SLACK,
                        status=NotificationStatus.SENT,
                        message_id=data.get("ts")
                    )
                else:
                    error = data.get("error", "Unknown error")
                    logger.error(f"Slack API error: {error}")
                    return NotificationResult(
                        success=False,
                        notification_id=notification_id,
                        channel=NotificationChannel.SLACK,
                        status=NotificationStatus.FAILED,
                        error=error
                    )
                    
        except Exception as e:
            logger.error(f"Error sending Slack message: {e}")
            return NotificationResult(
                success=False,
                notification_id=notification_id,
                channel=NotificationChannel.SLACK,
                status=NotificationStatus.FAILED,
                error=str(e)
            )
    
    async def validate_config(self) -> bool:
        """
        Validate Slack configuration by testing the API.
        
        Returns:
            True if configuration is valid
        """
        try:
            session = await self._get_session()
            async with session.post(f"{self.base_url}/auth.test") as response:
                data = await response.json()
                
                if data.get("ok"):
                    logger.info(f"Slack auth validated: {data.get('user')}")
                    return True
                else:
                    logger.error(f"Slack auth failed: {data.get('error')}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error validating Slack config: {e}")
            return False
    
    def format_message(self, message: NotificationMessage) -> Dict[str, Any]:
        """
        Format notification message for Slack Block Kit.
        
        Args:
            message: The notification message
            
        Returns:
            Slack message payload
        """
        # If custom blocks provided, use them
        if message.slack_blocks:
            return {
                "blocks": message.slack_blocks,
                "text": message.title  # Fallback text
            }
        
        # Build blocks
        blocks = []
        
        # Header with emoji
        emoji = self.LEVEL_EMOJI.get(message.level, ":bell:")
        blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{emoji} {message.title}",
                "emoji": True
            }
        })
        
        # Main body
        if message.body:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message.body
                }
            })
        
        # Fields (key-value pairs)
        if message.fields:
            field_blocks = []
            for key, value in message.fields.items():
                field_blocks.append({
                    "type": "mrkdwn",
                    "text": f"*{key}:*\n{value}"
                })
            
            # Slack allows max 10 fields per section
            for i in range(0, len(field_blocks), 10):
                blocks.append({
                    "type": "section",
                    "fields": field_blocks[i:i+10]
                })
        
        # Divider before metadata
        blocks.append({"type": "divider"})
        
        # Context (source info and timestamp)
        context_elements = []
        
        if message.source_name or message.source:
            source_text = message.source_name or message.source
            context_elements.append({
                "type": "mrkdwn",
                "text": f"📍 *Source:* {source_text}"
            })
        
        context_elements.append({
            "type": "mrkdwn",
            "text": f"🕐 {message.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}"
        })
        
        blocks.append({
            "type": "context",
            "elements": context_elements
        })
        
        # Action buttons
        if message.actions:
            action_elements = []
            for action in message.actions:
                button = {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": action.label,
                        "emoji": True
                    },
                    "url": action.url
                }
                if action.style == "primary":
                    button["style"] = "primary"
                elif action.style == "danger":
                    button["style"] = "danger"
                action_elements.append(button)
            
            blocks.append({
                "type": "actions",
                "elements": action_elements
            })
        
        return {
            "blocks": blocks,
            "text": f"{emoji} {message.title}: {message.body[:100]}...",  # Fallback
            "unfurl_links": self.config.unfurl_links,
            "unfurl_media": self.config.unfurl_media
        }
    
    def get_rate_limit(self) -> int:
        """Get rate limit for Slack."""
        return self.config.rate_limit
    
    # =========================================================================
    # ADDITIONAL SLACK FEATURES
    # =========================================================================
    
    async def send_to_user(
        self,
        user_id: str,
        message: NotificationMessage
    ) -> NotificationResult:
        """
        Send direct message to a Slack user.
        
        Args:
            user_id: Slack user ID
            message: The notification message
            
        Returns:
            NotificationResult
        """
        notification_id = str(uuid.uuid4())
        
        try:
            session = await self._get_session()
            
            # Open DM channel
            async with session.post(
                f"{self.base_url}/conversations.open",
                json={"users": user_id}
            ) as response:
                data = await response.json()
                
                if not data.get("ok"):
                    return NotificationResult(
                        success=False,
                        notification_id=notification_id,
                        channel=NotificationChannel.SLACK,
                        status=NotificationStatus.FAILED,
                        error=f"Failed to open DM: {data.get('error')}"
                    )
                
                dm_channel = data["channel"]["id"]
            
            # Send message to DM channel
            message.slack_channel = dm_channel
            return await self.send(message)
            
        except Exception as e:
            logger.error(f"Error sending DM: {e}")
            return NotificationResult(
                success=False,
                notification_id=notification_id,
                channel=NotificationChannel.SLACK,
                status=NotificationStatus.FAILED,
                error=str(e)
            )
    
    async def send_thread_reply(
        self,
        channel: str,
        thread_ts: str,
        message: NotificationMessage
    ) -> NotificationResult:
        """
        Send a reply in a thread.
        
        Args:
            channel: Channel ID
            thread_ts: Thread timestamp (parent message ts)
            message: The notification message
            
        Returns:
            NotificationResult
        """
        notification_id = str(uuid.uuid4())
        
        try:
            slack_payload = self.format_message(message)
            slack_payload["channel"] = channel
            slack_payload["thread_ts"] = thread_ts
            
            session = await self._get_session()
            async with session.post(
                f"{self.base_url}/chat.postMessage",
                json=slack_payload
            ) as response:
                data = await response.json()
                
                if data.get("ok"):
                    return NotificationResult(
                        success=True,
                        notification_id=notification_id,
                        channel=NotificationChannel.SLACK,
                        status=NotificationStatus.SENT,
                        message_id=data.get("ts")
                    )
                else:
                    return NotificationResult(
                        success=False,
                        notification_id=notification_id,
                        channel=NotificationChannel.SLACK,
                        status=NotificationStatus.FAILED,
                        error=data.get("error")
                    )
                    
        except Exception as e:
            logger.error(f"Error sending thread reply: {e}")
            return NotificationResult(
                success=False,
                notification_id=notification_id,
                channel=NotificationChannel.SLACK,
                status=NotificationStatus.FAILED,
                error=str(e)
            )
    
    async def update_message(
        self,
        channel: str,
        ts: str,
        message: NotificationMessage
    ) -> NotificationResult:
        """
        Update an existing Slack message.
        
        Args:
            channel: Channel ID
            ts: Message timestamp to update
            message: New message content
            
        Returns:
            NotificationResult
        """
        notification_id = str(uuid.uuid4())
        
        try:
            slack_payload = self.format_message(message)
            slack_payload["channel"] = channel
            slack_payload["ts"] = ts
            
            session = await self._get_session()
            async with session.post(
                f"{self.base_url}/chat.update",
                json=slack_payload
            ) as response:
                data = await response.json()
                
                if data.get("ok"):
                    return NotificationResult(
                        success=True,
                        notification_id=notification_id,
                        channel=NotificationChannel.SLACK,
                        status=NotificationStatus.SENT,
                        message_id=data.get("ts")
                    )
                else:
                    return NotificationResult(
                        success=False,
                        notification_id=notification_id,
                        channel=NotificationChannel.SLACK,
                        status=NotificationStatus.FAILED,
                        error=data.get("error")
                    )
                    
        except Exception as e:
            logger.error(f"Error updating message: {e}")
            return NotificationResult(
                success=False,
                notification_id=notification_id,
                channel=NotificationChannel.SLACK,
                status=NotificationStatus.FAILED,
                error=str(e)
            )
    
    async def list_channels(self) -> List[Dict[str, str]]:
        """
        List available Slack channels.
        
        Returns:
            List of channel dictionaries with id and name
        """
        try:
            session = await self._get_session()
            async with session.get(
                f"{self.base_url}/conversations.list",
                params={"types": "public_channel,private_channel"}
            ) as response:
                data = await response.json()
                
                if data.get("ok"):
                    return [
                        {"id": ch["id"], "name": ch["name"]}
                        for ch in data.get("channels", [])
                    ]
                else:
                    logger.error(f"Error listing channels: {data.get('error')}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error listing channels: {e}")
            return []
