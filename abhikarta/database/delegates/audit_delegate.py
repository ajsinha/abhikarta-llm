"""
Audit Delegate - Database operations for Audit Logs and System Settings.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Version: 1.2.2
"""

from typing import Any, Dict, List, Optional
import uuid
import json
import logging

from ..database_delegate import DatabaseDelegate

logger = logging.getLogger(__name__)


class AuditDelegate(DatabaseDelegate):
    """
    Delegate for audit and system settings database operations.
    
    Handles tables: audit_logs, system_settings, schema_version
    """
    
    # =========================================================================
    # AUDIT LOGS
    # =========================================================================
    
    def get_audit_logs(self, action: str = None, entity_type: str = None,
                       user_id: str = None, limit: int = 100,
                       offset: int = 0) -> List[Dict]:
        """Get audit logs with optional filters."""
        query = """SELECT al.*, u.fullname as user_name
                   FROM audit_logs al
                   LEFT JOIN users u ON al.user_id = u.user_id"""
        conditions = []
        params = []
        
        if action:
            conditions.append("al.action = ?")
            params.append(action)
        if entity_type:
            conditions.append("al.entity_type = ?")
            params.append(entity_type)
        if user_id:
            conditions.append("al.user_id = ?")
            params.append(user_id)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += f" ORDER BY al.created_at DESC LIMIT {limit} OFFSET {offset}"
        return self.fetch_all(query, tuple(params) if params else None) or []
    
    def get_audit_log(self, log_id: str) -> Optional[Dict]:
        """Get audit log by ID."""
        return self.fetch_one(
            """SELECT al.*, u.fullname as user_name
               FROM audit_logs al
               LEFT JOIN users u ON al.user_id = u.user_id
               WHERE al.log_id = ?""",
            (log_id,)
        )
    
    def get_audit_logs_count(self, action: str = None,
                             entity_type: str = None) -> int:
        """Get count of audit logs."""
        conditions = []
        params = []
        
        if action:
            conditions.append("action = ?")
            params.append(action)
        if entity_type:
            conditions.append("entity_type = ?")
            params.append(entity_type)
        
        where = " AND ".join(conditions) if conditions else None
        return self.get_count("audit_logs", where, tuple(params) if params else None)
    
    def get_recent_logs(self, limit: int = 10) -> List[Dict]:
        """Get most recent audit logs."""
        return self.fetch_all(
            """SELECT al.*, u.fullname as user_name
               FROM audit_logs al
               LEFT JOIN users u ON al.user_id = u.user_id
               ORDER BY al.created_at DESC
               LIMIT ?""",
            (limit,)
        ) or []
    
    def get_entity_logs(self, entity_type: str, entity_id: str) -> List[Dict]:
        """Get all logs for a specific entity."""
        return self.fetch_all(
            """SELECT al.*, u.fullname as user_name
               FROM audit_logs al
               LEFT JOIN users u ON al.user_id = u.user_id
               WHERE al.entity_type = ? AND al.entity_id = ?
               ORDER BY al.created_at DESC""",
            (entity_type, entity_id)
        ) or []
    
    def log_action(self, action: str, entity_type: str = None,
                   entity_id: str = None, user_id: str = None,
                   user_ip: str = None, user_agent: str = None,
                   old_value: str = None, new_value: str = None,
                   metadata: str = '{}') -> Optional[str]:
        """Log an audit action and return log_id."""
        log_id = str(uuid.uuid4())
        try:
            self.execute(
                """INSERT INTO audit_logs 
                   (log_id, action, entity_type, entity_id, user_id,
                    user_ip, user_agent, old_value, new_value, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (log_id, action, entity_type, entity_id, user_id,
                 user_ip, user_agent, old_value, new_value, metadata)
            )
            return log_id
        except Exception as e:
            logger.error(f"Error logging action: {e}")
            return None
    
    def get_user_activity(self, user_id: str, days: int = 30) -> List[Dict]:
        """Get user activity for the specified period."""
        return self.fetch_all(
            """SELECT action, entity_type, COUNT(*) as count
               FROM audit_logs
               WHERE user_id = ? 
               AND created_at >= datetime('now', ?)
               GROUP BY action, entity_type
               ORDER BY count DESC""",
            (user_id, f'-{days} days')
        ) or []
    
    def get_activity_summary(self, days: int = 7) -> List[Dict]:
        """Get activity summary grouped by action."""
        return self.fetch_all(
            """SELECT action, COUNT(*) as count,
                      COUNT(DISTINCT user_id) as unique_users
               FROM audit_logs
               WHERE created_at >= datetime('now', ?)
               GROUP BY action
               ORDER BY count DESC""",
            (f'-{days} days',)
        ) or []
    
    def cleanup_old_logs(self, days: int = 90) -> int:
        """Delete audit logs older than specified days. Returns count deleted."""
        try:
            result = self.fetch_one(
                "SELECT COUNT(*) as count FROM audit_logs WHERE created_at < datetime('now', ?)",
                (f'-{days} days',)
            )
            count = result.get('count', 0) if result else 0
            self.execute(
                "DELETE FROM audit_logs WHERE created_at < datetime('now', ?)",
                (f'-{days} days',)
            )
            return count
        except Exception as e:
            logger.error(f"Error cleaning up logs: {e}")
            return 0
    
    # =========================================================================
    # SYSTEM SETTINGS
    # =========================================================================
    
    def get_all_settings(self) -> List[Dict]:
        """Get all system settings."""
        return self.fetch_all(
            "SELECT * FROM system_settings ORDER BY setting_key"
        ) or []
    
    def get_setting(self, setting_key: str) -> Optional[Dict]:
        """Get setting by key."""
        return self.fetch_one(
            "SELECT * FROM system_settings WHERE setting_key = ?",
            (setting_key,)
        )
    
    def get_setting_value(self, setting_key: str, 
                          default: Any = None) -> Any:
        """Get setting value by key, with optional default."""
        setting = self.get_setting(setting_key)
        if not setting:
            return default
        
        value = setting.get('setting_value')
        setting_type = setting.get('setting_type', 'string')
        
        # Convert value based on type
        try:
            if setting_type == 'integer':
                return int(value)
            elif setting_type == 'boolean':
                return value.lower() in ('true', '1', 'yes')
            elif setting_type == 'json':
                return json.loads(value)
            else:
                return value
        except (ValueError, json.JSONDecodeError):
            return default
    
    def set_setting(self, setting_key: str, setting_value: str,
                    setting_type: str = 'string', description: str = None,
                    is_encrypted: int = 0, updated_by: str = None) -> bool:
        """Set or update a system setting."""
        try:
            # Check if exists
            existing = self.get_setting(setting_key)
            
            if existing:
                self.execute(
                    """UPDATE system_settings 
                       SET setting_value = ?, setting_type = ?, description = ?,
                           is_encrypted = ?, updated_at = CURRENT_TIMESTAMP,
                           updated_by = ?
                       WHERE setting_key = ?""",
                    (setting_value, setting_type, description, is_encrypted,
                     updated_by, setting_key)
                )
            else:
                self.execute(
                    """INSERT INTO system_settings 
                       (setting_key, setting_value, setting_type, description,
                        is_encrypted, updated_by)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (setting_key, setting_value, setting_type, description,
                     is_encrypted, updated_by)
                )
            return True
        except Exception as e:
            logger.error(f"Error setting value: {e}")
            return False
    
    def delete_setting(self, setting_key: str) -> bool:
        """Delete a system setting."""
        try:
            self.execute(
                "DELETE FROM system_settings WHERE setting_key = ?",
                (setting_key,)
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting setting: {e}")
            return False
    
    def setting_exists(self, setting_key: str) -> bool:
        """Check if setting exists."""
        return self.exists("system_settings", "setting_key = ?", (setting_key,))
    
    # =========================================================================
    # SCHEMA VERSION
    # =========================================================================
    
    def get_schema_version(self) -> Optional[str]:
        """Get current schema version."""
        result = self.fetch_one(
            "SELECT version FROM schema_version ORDER BY applied_at DESC LIMIT 1"
        )
        return result.get('version') if result else None
    
    def get_schema_history(self) -> List[Dict]:
        """Get schema version history."""
        return self.fetch_all(
            "SELECT * FROM schema_version ORDER BY applied_at DESC"
        ) or []
    
    def record_schema_version(self, version: str, 
                              description: str = None) -> bool:
        """Record a new schema version."""
        try:
            self.execute(
                """INSERT INTO schema_version (version, description)
                   VALUES (?, ?)""",
                (version, description)
            )
            return True
        except Exception as e:
            logger.error(f"Error recording schema version: {e}")
            return False
