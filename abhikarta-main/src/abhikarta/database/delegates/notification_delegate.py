"""
Notification Delegate - Database operations for notification system.

Handles all database interactions for:
- Notification channels configuration
- Notification logs
- Webhook endpoints
- Webhook events
- User notification preferences

Copyright © 2025-2030, All Rights Reserved
Author: Ashutosh Sinha (ajsinha@gmail.com)
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from ..database_delegate import DatabaseDelegate

logger = logging.getLogger(__name__)


class NotificationDelegate(DatabaseDelegate):
    """
    Database delegate for notification-related operations.
    
    Manages:
    - notification_channels
    - notification_logs
    - webhook_endpoints
    - webhook_events
    - user_notification_preferences
    """
    
    # =========================================================================
    # NOTIFICATION CHANNELS
    # =========================================================================
    
    def create_channel(
        self,
        channel_type: str,
        name: str,
        config: Dict[str, Any],
        created_by: str = None
    ) -> str:
        """
        Create a new notification channel configuration.
        
        Args:
            channel_type: Type of channel (slack, teams, email, sms)
            name: Display name for the channel
            config: Channel-specific configuration
            created_by: User ID who created this
            
        Returns:
            channel_id
        """
        channel_id = str(uuid.uuid4())
        
        self.db_facade.execute(
            """INSERT INTO notification_channels 
               (channel_id, channel_type, name, config, created_by)
               VALUES (?, ?, ?, ?, ?)""",
            (channel_id, channel_type, name, json.dumps(config), created_by)
        )
        
        logger.info(f"Created notification channel: {name} ({channel_type})")
        return channel_id
    
    def get_channel(self, channel_id: str) -> Optional[Dict]:
        """Get notification channel by ID."""
        row = self.db_facade.fetch_one(
            "SELECT * FROM notification_channels WHERE channel_id = ?",
            (channel_id,)
        )
        if row:
            row = dict(row)
            if row.get('config'):
                row['config'] = json.loads(row['config'])
        return row
    
    def get_channel_by_type(self, channel_type: str) -> Optional[Dict]:
        """Get first active notification channel by type."""
        row = self.db_facade.fetch_one(
            """SELECT * FROM notification_channels 
               WHERE channel_type = ? AND is_active = 1 
               ORDER BY created_at DESC LIMIT 1""",
            (channel_type,)
        )
        if row:
            row = dict(row)
            if row.get('config'):
                row['config'] = json.loads(row['config'])
        return row
    
    def list_channels(self, active_only: bool = True) -> List[Dict]:
        """List all notification channels."""
        query = "SELECT * FROM notification_channels"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY channel_type, name"
        
        rows = self.db_facade.fetch_all(query) or []
        result = []
        for row in rows:
            row = dict(row)
            if row.get('config'):
                row['config'] = json.loads(row['config'])
            result.append(row)
        return result
    
    def update_channel(
        self,
        channel_id: str,
        name: str = None,
        config: Dict = None,
        is_active: bool = None
    ) -> bool:
        """Update notification channel configuration."""
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        
        if config is not None:
            updates.append("config = ?")
            params.append(json.dumps(config))
        
        if is_active is not None:
            updates.append("is_active = ?")
            params.append(1 if is_active else 0)
        
        if not updates:
            return False
        
        params.append(channel_id)
        
        self.db_facade.execute(
            f"UPDATE notification_channels SET {', '.join(updates)} WHERE channel_id = ?",
            tuple(params)
        )
        return True
    
    def delete_channel(self, channel_id: str) -> bool:
        """Delete notification channel."""
        self.db_facade.execute(
            "DELETE FROM notification_channels WHERE channel_id = ?",
            (channel_id,)
        )
        return True
    
    # =========================================================================
    # NOTIFICATION LOGS
    # =========================================================================
    
    def log_notification(
        self,
        notification_id: str,
        channel_type: str,
        title: str,
        body: str,
        level: str = 'info',
        status: str = 'pending',
        recipient: str = None,
        channel_id: str = None,
        source: str = None,
        source_type: str = None,
        correlation_id: str = None,
        error_message: str = None
    ) -> str:
        """
        Log a notification attempt.
        
        Returns:
            notification_id
        """
        self.db_facade.execute(
            """INSERT INTO notification_logs 
               (notification_id, channel_id, channel_type, recipient, title, body,
                level, status, source, source_type, correlation_id, error_message,
                sent_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                notification_id, channel_id, channel_type, recipient, title, body,
                level, status, source, source_type, correlation_id, error_message,
                datetime.now(timezone.utc).isoformat() if status == 'sent' else None
            )
        )
        return notification_id
    
    def update_notification_status(
        self,
        notification_id: str,
        status: str,
        error_message: str = None
    ) -> bool:
        """Update notification delivery status."""
        sent_at = datetime.now(timezone.utc).isoformat() if status == 'sent' else None
        delivered_at = datetime.now(timezone.utc).isoformat() if status == 'delivered' else None
        
        self.db_facade.execute(
            """UPDATE notification_logs 
               SET status = ?, error_message = ?, sent_at = COALESCE(sent_at, ?), 
                   delivered_at = ?
               WHERE notification_id = ?""",
            (status, error_message, sent_at, delivered_at, notification_id)
        )
        return True
    
    def get_notification_logs(
        self,
        limit: int = 100,
        channel_type: str = None,
        status: str = None,
        source: str = None,
        source_type: str = None
    ) -> List[Dict]:
        """Get notification history with optional filters."""
        query = "SELECT * FROM notification_logs WHERE 1=1"
        params = []
        
        if channel_type:
            query += " AND channel_type = ?"
            params.append(channel_type)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if source:
            query += " AND source = ?"
            params.append(source)
        
        if source_type:
            query += " AND source_type = ?"
            params.append(source_type)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        return self.db_facade.fetch_all(query, tuple(params)) or []
    
    def get_notification_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get notification statistics."""
        # Total by channel
        channel_stats = self.db_facade.fetch_all(
            """SELECT channel_type, status, COUNT(*) as count
               FROM notification_logs 
               WHERE created_at >= datetime('now', ?)
               GROUP BY channel_type, status""",
            (f'-{days} days',)
        ) or []
        
        # Daily counts
        daily_stats = self.db_facade.fetch_all(
            """SELECT DATE(created_at) as date, COUNT(*) as count
               FROM notification_logs
               WHERE created_at >= datetime('now', ?)
               GROUP BY DATE(created_at)
               ORDER BY date""",
            (f'-{days} days',)
        ) or []
        
        return {
            'by_channel': channel_stats,
            'daily': daily_stats
        }
    
    # =========================================================================
    # WEBHOOK ENDPOINTS
    # =========================================================================
    
    def create_webhook_endpoint(
        self,
        path: str,
        name: str,
        description: str = None,
        auth_method: str = 'hmac',
        secret_hash: str = None,
        target_type: str = None,
        target_id: str = None,
        rate_limit: int = 100,
        created_by: str = None
    ) -> str:
        """
        Create a new webhook endpoint.
        
        Returns:
            endpoint_id
        """
        endpoint_id = str(uuid.uuid4())
        
        self.db_facade.execute(
            """INSERT INTO webhook_endpoints 
               (endpoint_id, path, name, description, auth_method, secret_hash,
                target_type, target_id, rate_limit, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                endpoint_id, path, name, description, auth_method, secret_hash,
                target_type, target_id, rate_limit, created_by
            )
        )
        
        logger.info(f"Created webhook endpoint: {path}")
        return endpoint_id
    
    def get_webhook_endpoint(self, endpoint_id: str) -> Optional[Dict]:
        """Get webhook endpoint by ID."""
        return self.db_facade.fetch_one(
            "SELECT * FROM webhook_endpoints WHERE endpoint_id = ?",
            (endpoint_id,)
        )
    
    def get_webhook_endpoint_by_path(self, path: str) -> Optional[Dict]:
        """Get webhook endpoint by path."""
        return self.db_facade.fetch_one(
            "SELECT * FROM webhook_endpoints WHERE path = ? AND is_active = 1",
            (path,)
        )
    
    def list_webhook_endpoints(self, active_only: bool = True) -> List[Dict]:
        """List all webhook endpoints."""
        query = "SELECT * FROM webhook_endpoints"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY path"
        
        return self.db_facade.fetch_all(query) or []
    
    def update_webhook_endpoint(
        self,
        endpoint_id: str,
        name: str = None,
        description: str = None,
        auth_method: str = None,
        secret_hash: str = None,
        target_type: str = None,
        target_id: str = None,
        rate_limit: int = None,
        is_active: bool = None
    ) -> bool:
        """Update webhook endpoint configuration."""
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        
        if auth_method is not None:
            updates.append("auth_method = ?")
            params.append(auth_method)
        
        if secret_hash is not None:
            updates.append("secret_hash = ?")
            params.append(secret_hash)
        
        if target_type is not None:
            updates.append("target_type = ?")
            params.append(target_type)
        
        if target_id is not None:
            updates.append("target_id = ?")
            params.append(target_id)
        
        if rate_limit is not None:
            updates.append("rate_limit = ?")
            params.append(rate_limit)
        
        if is_active is not None:
            updates.append("is_active = ?")
            params.append(1 if is_active else 0)
        
        if not updates:
            return False
        
        params.append(endpoint_id)
        
        self.db_facade.execute(
            f"UPDATE webhook_endpoints SET {', '.join(updates)} WHERE endpoint_id = ?",
            tuple(params)
        )
        return True
    
    def delete_webhook_endpoint(self, endpoint_id: str) -> bool:
        """Delete webhook endpoint."""
        self.db_facade.execute(
            "UPDATE webhook_endpoints SET is_active = 0 WHERE endpoint_id = ?",
            (endpoint_id,)
        )
        return True
    
    # =========================================================================
    # WEBHOOK EVENTS
    # =========================================================================
    
    def log_webhook_event(
        self,
        event_id: str,
        endpoint_id: str,
        event_type: str = None,
        payload: Dict = None,
        headers: Dict = None,
        source_ip: str = None,
        verified: bool = False
    ) -> str:
        """
        Log an incoming webhook event.
        
        Returns:
            event_id
        """
        self.db_facade.execute(
            """INSERT INTO webhook_events 
               (event_id, endpoint_id, event_type, payload, headers, source_ip, verified)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                event_id, endpoint_id, event_type,
                json.dumps(payload) if payload else None,
                json.dumps(headers) if headers else None,
                source_ip, 1 if verified else 0
            )
        )
        return event_id
    
    def update_webhook_event_processed(
        self,
        event_id: str,
        process_result: Dict = None,
        error_message: str = None
    ) -> bool:
        """Mark webhook event as processed."""
        self.db_facade.execute(
            """UPDATE webhook_events 
               SET processed = 1, process_result = ?, error_message = ?, 
                   processed_at = CURRENT_TIMESTAMP
               WHERE event_id = ?""",
            (json.dumps(process_result) if process_result else None, error_message, event_id)
        )
        return True
    
    def get_webhook_events(
        self,
        endpoint_id: str = None,
        limit: int = 100,
        verified_only: bool = False
    ) -> List[Dict]:
        """Get webhook event history."""
        query = """
            SELECT we.*, wep.path, wep.name as endpoint_name
            FROM webhook_events we
            LEFT JOIN webhook_endpoints wep ON we.endpoint_id = wep.endpoint_id
            WHERE 1=1
        """
        params = []
        
        if endpoint_id:
            query += " AND we.endpoint_id = ?"
            params.append(endpoint_id)
        
        if verified_only:
            query += " AND we.verified = 1"
        
        query += " ORDER BY we.received_at DESC LIMIT ?"
        params.append(limit)
        
        rows = self.db_facade.fetch_all(query, tuple(params)) or []
        result = []
        for row in rows:
            row = dict(row)
            if row.get('payload'):
                try:
                    row['payload'] = json.loads(row['payload'])
                except:
                    pass
            if row.get('headers'):
                try:
                    row['headers'] = json.loads(row['headers'])
                except:
                    pass
            result.append(row)
        return result
    
    # =========================================================================
    # USER NOTIFICATION PREFERENCES
    # =========================================================================
    
    def get_user_notification_preferences(self, user_id: str) -> List[Dict]:
        """Get all notification preferences for a user."""
        return self.db_facade.fetch_all(
            "SELECT * FROM user_notification_preferences WHERE user_id = ?",
            (user_id,)
        ) or []
    
    def get_user_notification_preference(
        self,
        user_id: str,
        channel_type: str
    ) -> Optional[Dict]:
        """Get user's preference for a specific channel."""
        return self.db_facade.fetch_one(
            """SELECT * FROM user_notification_preferences 
               WHERE user_id = ? AND channel_type = ?""",
            (user_id, channel_type)
        )
    
    def set_user_notification_preference(
        self,
        user_id: str,
        channel_type: str,
        channel_address: str = None,
        enabled: bool = True,
        min_level: str = 'info',
        quiet_hours_start: str = None,
        quiet_hours_end: str = None
    ) -> bool:
        """Set or update user notification preference."""
        # Try update first
        existing = self.get_user_notification_preference(user_id, channel_type)
        
        if existing:
            self.db_facade.execute(
                """UPDATE user_notification_preferences 
                   SET channel_address = ?, enabled = ?, min_level = ?,
                       quiet_hours_start = ?, quiet_hours_end = ?
                   WHERE user_id = ? AND channel_type = ?""",
                (
                    channel_address, 1 if enabled else 0, min_level,
                    quiet_hours_start, quiet_hours_end, user_id, channel_type
                )
            )
        else:
            self.db_facade.execute(
                """INSERT INTO user_notification_preferences 
                   (user_id, channel_type, channel_address, enabled, min_level,
                    quiet_hours_start, quiet_hours_end)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    user_id, channel_type, channel_address, 1 if enabled else 0,
                    min_level, quiet_hours_start, quiet_hours_end
                )
            )
        
        return True
    
    def delete_user_notification_preference(
        self,
        user_id: str,
        channel_type: str
    ) -> bool:
        """Delete user notification preference."""
        self.db_facade.execute(
            """DELETE FROM user_notification_preferences 
               WHERE user_id = ? AND channel_type = ?""",
            (user_id, channel_type)
        )
        return True
