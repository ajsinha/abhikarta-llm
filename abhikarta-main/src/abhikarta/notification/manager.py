"""
Notification Manager - Central orchestrator for all notifications.

Handles routing, queuing, retry logic, and logging for all notification channels.

Copyright © 2025-2030, All Rights Reserved
Author: Ashutosh Sinha (ajsinha@gmail.com)
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass, field

from .base import (
    NotificationMessage,
    NotificationResult,
    NotificationChannel,
    NotificationLevel,
    NotificationStatus,
    NotificationAdapter,
    ChannelConfig,
    SlackConfig,
    TeamsConfig,
    EmailConfig
)

logger = logging.getLogger(__name__)


@dataclass
class RetryPolicy:
    """Retry policy for failed notifications."""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0


@dataclass
class NotificationQueueItem:
    """Item in the notification queue."""
    notification_id: str
    message: NotificationMessage
    channels: List[NotificationChannel]
    priority: int = 0
    retry_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


class NotificationManager:
    """
    Central notification manager that routes messages to appropriate channels.
    
    Features:
    - Multi-channel support (Slack, Teams, Email, SMS)
    - Priority-based routing
    - Retry with exponential backoff
    - Rate limiting per channel
    - Audit logging
    - Async operation
    
    Usage:
        manager = NotificationManager()
        manager.configure_slack(SlackConfig(bot_token="xoxb-..."))
        manager.configure_teams(TeamsConfig(webhook_url="https://..."))
        
        await manager.send(
            channels=["slack", "teams"],
            message=NotificationMessage(title="Alert", body="Something happened")
        )
    """
    
    def __init__(self, db_facade=None):
        """
        Initialize the notification manager.
        
        Args:
            db_facade: Optional database facade for logging notifications
        """
        self.db_facade = db_facade
        self._adapters: Dict[NotificationChannel, NotificationAdapter] = {}
        self._configs: Dict[NotificationChannel, ChannelConfig] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
        self._retry_policy = RetryPolicy()
        self._rate_limiters: Dict[NotificationChannel, asyncio.Semaphore] = {}
        self._running = False
        self._worker_task: Optional[asyncio.Task] = None
        
        logger.info("NotificationManager initialized")
    
    # =========================================================================
    # CONFIGURATION
    # =========================================================================
    
    def configure_slack(self, config: SlackConfig) -> None:
        """
        Configure Slack notifications.
        
        Args:
            config: Slack configuration
        """
        from .slack_adapter import SlackAdapter
        
        if config.validate():
            adapter = SlackAdapter(config)
            self._adapters[NotificationChannel.SLACK] = adapter
            self._configs[NotificationChannel.SLACK] = config
            self._rate_limiters[NotificationChannel.SLACK] = asyncio.Semaphore(config.rate_limit)
            logger.info("Slack adapter configured")
        else:
            logger.warning("Invalid Slack configuration")
    
    def configure_teams(self, config: TeamsConfig) -> None:
        """
        Configure Microsoft Teams notifications.
        
        Args:
            config: Teams configuration
        """
        from .teams_adapter import TeamsAdapter
        
        if config.validate():
            adapter = TeamsAdapter(config)
            self._adapters[NotificationChannel.TEAMS] = adapter
            self._configs[NotificationChannel.TEAMS] = config
            self._rate_limiters[NotificationChannel.TEAMS] = asyncio.Semaphore(config.rate_limit)
            logger.info("Teams adapter configured")
        else:
            logger.warning("Invalid Teams configuration")
    
    def configure_email(self, config: EmailConfig) -> None:
        """
        Configure email notifications.
        
        Args:
            config: Email configuration
        """
        # Email adapter implementation would go here
        self._configs[NotificationChannel.EMAIL] = config
        logger.info("Email adapter configured")
    
    def configure_from_dict(self, config: Dict[str, Any]) -> None:
        """
        Configure all channels from a dictionary.
        
        Args:
            config: Configuration dictionary
        """
        if 'slack' in config:
            slack_config = SlackConfig(**config['slack'])
            self.configure_slack(slack_config)
        
        if 'teams' in config:
            teams_config = TeamsConfig(**config['teams'])
            self.configure_teams(teams_config)
        
        if 'email' in config:
            email_config = EmailConfig(**config['email'])
            self.configure_email(email_config)
    
    def get_configured_channels(self) -> List[str]:
        """Get list of configured channel names."""
        return [ch.value for ch in self._adapters.keys()]
    
    def is_channel_configured(self, channel: str) -> bool:
        """Check if a channel is configured."""
        try:
            ch = NotificationChannel(channel)
            return ch in self._adapters
        except ValueError:
            return False
    
    # =========================================================================
    # SENDING NOTIFICATIONS
    # =========================================================================
    
    async def send(
        self,
        channels: List[str],
        message: NotificationMessage,
        priority: int = 0,
        wait: bool = True
    ) -> List[NotificationResult]:
        """
        Send a notification to multiple channels.
        
        Args:
            channels: List of channel names ('slack', 'teams', etc.)
            message: The notification message
            priority: Priority level (higher = more urgent)
            wait: If True, wait for all sends to complete
            
        Returns:
            List of NotificationResult for each channel
        """
        notification_id = str(uuid.uuid4())
        results = []
        
        # Convert channel strings to enums
        target_channels = []
        for ch_name in channels:
            try:
                channel = NotificationChannel(ch_name)
                if channel in self._adapters:
                    target_channels.append(channel)
                else:
                    logger.warning(f"Channel {ch_name} not configured, skipping")
                    results.append(NotificationResult(
                        success=False,
                        notification_id=notification_id,
                        channel=channel,
                        status=NotificationStatus.FAILED,
                        error=f"Channel {ch_name} not configured"
                    ))
            except ValueError:
                logger.warning(f"Unknown channel: {ch_name}")
        
        if not target_channels:
            logger.warning("No valid channels to send to")
            return results
        
        # Send to each channel
        if wait:
            tasks = [
                self._send_to_channel(notification_id, channel, message)
                for channel in target_channels
            ]
            channel_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for channel, result in zip(target_channels, channel_results):
                if isinstance(result, Exception):
                    results.append(NotificationResult(
                        success=False,
                        notification_id=notification_id,
                        channel=channel,
                        status=NotificationStatus.FAILED,
                        error=str(result)
                    ))
                else:
                    results.append(result)
        else:
            # Queue for async processing
            for channel in target_channels:
                await self._queue.put(NotificationQueueItem(
                    notification_id=notification_id,
                    message=message,
                    channels=[channel],
                    priority=priority
                ))
            results.append(NotificationResult(
                success=True,
                notification_id=notification_id,
                channel=target_channels[0],
                status=NotificationStatus.PENDING
            ))
        
        return results
    
    async def send_to_slack(
        self,
        message: NotificationMessage,
        channel: str = None
    ) -> NotificationResult:
        """
        Send notification to Slack.
        
        Args:
            message: The notification message
            channel: Override default Slack channel
            
        Returns:
            NotificationResult
        """
        if channel:
            message.slack_channel = channel
        
        results = await self.send(["slack"], message)
        return results[0] if results else NotificationResult(
            success=False,
            notification_id="",
            channel=NotificationChannel.SLACK,
            status=NotificationStatus.FAILED,
            error="Send failed"
        )
    
    async def send_to_teams(self, message: NotificationMessage) -> NotificationResult:
        """
        Send notification to Microsoft Teams.
        
        Args:
            message: The notification message
            
        Returns:
            NotificationResult
        """
        results = await self.send(["teams"], message)
        return results[0] if results else NotificationResult(
            success=False,
            notification_id="",
            channel=NotificationChannel.TEAMS,
            status=NotificationStatus.FAILED,
            error="Send failed"
        )
    
    async def broadcast(
        self,
        message: NotificationMessage
    ) -> List[NotificationResult]:
        """
        Broadcast notification to all configured channels.
        
        Args:
            message: The notification message
            
        Returns:
            List of NotificationResult for each channel
        """
        channels = [ch.value for ch in self._adapters.keys()]
        return await self.send(channels, message)
    
    async def _send_to_channel(
        self,
        notification_id: str,
        channel: NotificationChannel,
        message: NotificationMessage,
        retry_count: int = 0
    ) -> NotificationResult:
        """
        Internal method to send to a specific channel with retry logic.
        """
        adapter = self._adapters.get(channel)
        if not adapter:
            return NotificationResult(
                success=False,
                notification_id=notification_id,
                channel=channel,
                status=NotificationStatus.FAILED,
                error=f"No adapter for channel {channel.value}"
            )
        
        # Apply rate limiting
        semaphore = self._rate_limiters.get(channel)
        if semaphore:
            async with semaphore:
                return await self._execute_send(
                    notification_id, adapter, channel, message, retry_count
                )
        else:
            return await self._execute_send(
                notification_id, adapter, channel, message, retry_count
            )
    
    async def _execute_send(
        self,
        notification_id: str,
        adapter: NotificationAdapter,
        channel: NotificationChannel,
        message: NotificationMessage,
        retry_count: int
    ) -> NotificationResult:
        """Execute the actual send with retry logic."""
        try:
            result = await adapter.send(message)
            result.notification_id = notification_id
            
            # Log to database
            await self._log_notification(notification_id, channel, message, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending to {channel.value}: {e}")
            
            # Retry logic
            if retry_count < self._retry_policy.max_retries:
                delay = min(
                    self._retry_policy.base_delay * (self._retry_policy.exponential_base ** retry_count),
                    self._retry_policy.max_delay
                )
                logger.info(f"Retrying {channel.value} in {delay}s (attempt {retry_count + 1})")
                await asyncio.sleep(delay)
                return await self._send_to_channel(
                    notification_id, channel, message, retry_count + 1
                )
            
            result = NotificationResult(
                success=False,
                notification_id=notification_id,
                channel=channel,
                status=NotificationStatus.FAILED,
                error=str(e)
            )
            await self._log_notification(notification_id, channel, message, result)
            return result
    
    # =========================================================================
    # LOGGING
    # =========================================================================
    
    async def _log_notification(
        self,
        notification_id: str,
        channel: NotificationChannel,
        message: NotificationMessage,
        result: NotificationResult
    ) -> None:
        """Log notification to database."""
        if not self.db_facade:
            return
        
        try:
            self.db_facade.execute(
                """INSERT INTO notification_logs 
                   (notification_id, channel_type, recipient, title, body, level, 
                    status, error_message, source, source_type, correlation_id, sent_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    notification_id,
                    channel.value,
                    message.recipient_email or message.recipient_user_id or '',
                    message.title,
                    message.body,
                    message.level.value,
                    result.status.value,
                    result.error,
                    message.source,
                    message.source_type,
                    message.correlation_id,
                    datetime.utcnow().isoformat() if result.success else None
                )
            )
        except Exception as e:
            logger.error(f"Failed to log notification: {e}")
    
    def get_notification_history(
        self,
        limit: int = 100,
        channel: str = None,
        status: str = None
    ) -> List[Dict]:
        """
        Get notification history from database.
        
        Args:
            limit: Maximum number of records
            channel: Filter by channel
            status: Filter by status
            
        Returns:
            List of notification records
        """
        if not self.db_facade:
            return []
        
        query = "SELECT * FROM notification_logs WHERE 1=1"
        params = []
        
        if channel:
            query += " AND channel_type = ?"
            params.append(channel)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        try:
            return self.db_facade.fetch_all(query, tuple(params)) or []
        except Exception as e:
            logger.error(f"Error fetching notification history: {e}")
            return []
    
    # =========================================================================
    # CHANNEL TESTING
    # =========================================================================
    
    async def test_channel(self, channel: str) -> Dict[str, Any]:
        """
        Test a notification channel configuration.
        
        Args:
            channel: Channel name to test
            
        Returns:
            Test result dictionary
        """
        try:
            ch = NotificationChannel(channel)
            adapter = self._adapters.get(ch)
            
            if not adapter:
                return {
                    "success": False,
                    "channel": channel,
                    "error": "Channel not configured"
                }
            
            # Validate configuration
            config_valid = await adapter.validate_config()
            
            if not config_valid:
                return {
                    "success": False,
                    "channel": channel,
                    "error": "Configuration validation failed"
                }
            
            # Send test message
            test_message = NotificationMessage(
                title="🧪 Test Notification",
                body="This is a test message from Abhikarta-LLM notification system.",
                level=NotificationLevel.INFO,
                source="notification_manager",
                source_type="system",
                fields={
                    "Test Time": datetime.utcnow().isoformat(),
                    "Channel": channel
                }
            )
            
            result = await adapter.send(test_message)
            
            return {
                "success": result.success,
                "channel": channel,
                "message_id": result.message_id,
                "error": result.error
            }
            
        except ValueError:
            return {
                "success": False,
                "channel": channel,
                "error": f"Unknown channel: {channel}"
            }
        except Exception as e:
            return {
                "success": False,
                "channel": channel,
                "error": str(e)
            }
    
    async def test_all_channels(self) -> Dict[str, Dict]:
        """Test all configured channels."""
        results = {}
        for channel in self._adapters.keys():
            results[channel.value] = await self.test_channel(channel.value)
        return results
    
    # =========================================================================
    # BACKGROUND WORKER
    # =========================================================================
    
    async def start_worker(self) -> None:
        """Start background worker for async notification processing."""
        if self._running:
            return
        
        self._running = True
        self._worker_task = asyncio.create_task(self._process_queue())
        logger.info("Notification worker started")
    
    async def stop_worker(self) -> None:
        """Stop the background worker."""
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("Notification worker stopped")
    
    async def _process_queue(self) -> None:
        """Process notification queue."""
        while self._running:
            try:
                item = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                
                for channel in item.channels:
                    await self._send_to_channel(
                        item.notification_id,
                        channel,
                        item.message,
                        item.retry_count
                    )
                
                self._queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing notification queue: {e}")
    
    # =========================================================================
    # CONTEXT MANAGER
    # =========================================================================
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_worker()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop_worker()
