"""
Swarm Database Delegate - Database operations for swarm management.

Handles all swarm-related database operations including:
- Swarm definitions CRUD
- Agent pool configurations
- Trigger configurations
- Execution history and metrics

Version: 1.3.0
Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SwarmDelegate:
    """
    Database delegate for swarm operations.
    
    Provides all database operations related to swarms, including
    swarm definitions, agent memberships, triggers, and execution history.
    """
    
    def __init__(self, db_facade):
        """
        Initialize the swarm delegate.
        
        Args:
            db_facade: Database facade instance
        """
        self.db = db_facade
    
    # =========================================================================
    # Schema Creation
    # =========================================================================
    
    def create_tables(self) -> None:
        """Create all swarm-related tables."""
        
        # Main swarms table
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS swarms (
                swarm_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                version TEXT DEFAULT '1.0.0',
                category TEXT DEFAULT 'general',
                status TEXT DEFAULT 'draft',
                
                -- Configuration JSON
                config_json TEXT,
                
                -- Full definition JSON (for complex nested structures)
                definition_json TEXT,
                
                -- Metadata
                tags TEXT,
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Statistics
                total_executions INTEGER DEFAULT 0,
                successful_executions INTEGER DEFAULT 0,
                failed_executions INTEGER DEFAULT 0,
                total_events_processed INTEGER DEFAULT 0,
                avg_execution_time REAL DEFAULT 0.0,
                
                -- Soft delete
                is_deleted INTEGER DEFAULT 0
            )
        """)
        
        # Swarm agent memberships
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS swarm_agent_memberships (
                membership_id TEXT PRIMARY KEY,
                swarm_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                agent_name TEXT,
                
                -- Role and configuration
                role TEXT DEFAULT 'worker',
                description TEXT,
                
                -- Pool configuration
                min_instances INTEGER DEFAULT 0,
                max_instances INTEGER DEFAULT 10,
                auto_scale INTEGER DEFAULT 1,
                idle_timeout INTEGER DEFAULT 300,
                
                -- Event subscriptions JSON
                subscriptions_json TEXT,
                
                -- State
                is_active INTEGER DEFAULT 1,
                current_instances INTEGER DEFAULT 0,
                total_tasks_processed INTEGER DEFAULT 0,
                
                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (swarm_id) REFERENCES swarms(swarm_id),
                FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
            )
        """)
        
        # Swarm triggers
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS swarm_triggers (
                trigger_id TEXT PRIMARY KEY,
                swarm_id TEXT NOT NULL,
                trigger_type TEXT NOT NULL,
                name TEXT,
                description TEXT,
                
                -- Configuration JSON
                config_json TEXT,
                
                -- Filtering
                filter_expression TEXT,
                
                -- State
                is_active INTEGER DEFAULT 1,
                last_triggered TIMESTAMP,
                trigger_count INTEGER DEFAULT 0,
                
                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (swarm_id) REFERENCES swarms(swarm_id)
            )
        """)
        
        # Agent pool instances (for round-robin tracking)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS swarm_agent_instances (
                instance_id TEXT PRIMARY KEY,
                swarm_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                membership_id TEXT NOT NULL,
                
                -- State
                status TEXT DEFAULT 'idle',
                current_task_id TEXT,
                tasks_completed INTEGER DEFAULT 0,
                tasks_failed INTEGER DEFAULT 0,
                
                -- Round-robin tracking
                last_used TIMESTAMP,
                use_count INTEGER DEFAULT 0,
                
                -- Performance
                avg_task_time REAL DEFAULT 0.0,
                
                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (swarm_id) REFERENCES swarms(swarm_id),
                FOREIGN KEY (membership_id) REFERENCES swarm_agent_memberships(membership_id)
            )
        """)
        
        # Swarm execution history
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS swarm_executions (
                execution_id TEXT PRIMARY KEY,
                swarm_id TEXT NOT NULL,
                correlation_id TEXT,
                
                -- Trigger info
                trigger_type TEXT,
                trigger_id TEXT,
                trigger_data TEXT,
                
                -- Execution state
                status TEXT DEFAULT 'pending',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                duration_ms INTEGER,
                
                -- Results
                result_json TEXT,
                error_message TEXT,
                
                -- Metrics
                events_processed INTEGER DEFAULT 0,
                agents_used INTEGER DEFAULT 0,
                iterations INTEGER DEFAULT 0,
                
                -- User info
                user_id TEXT,
                
                FOREIGN KEY (swarm_id) REFERENCES swarms(swarm_id)
            )
        """)
        
        # Swarm events log
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS swarm_events_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT,
                swarm_id TEXT NOT NULL,
                execution_id TEXT,
                
                -- Event details
                event_type TEXT,
                source TEXT,
                target TEXT,
                payload_json TEXT,
                
                -- Metadata
                priority INTEGER DEFAULT 1,
                correlation_id TEXT,
                parent_id TEXT,
                
                -- Timestamp
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (swarm_id) REFERENCES swarms(swarm_id)
            )
        """)
        
        # Create indexes
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_swarms_status ON swarms(status)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_swarms_category ON swarms(category)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_swarm_memberships_swarm ON swarm_agent_memberships(swarm_id)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_swarm_triggers_swarm ON swarm_triggers(swarm_id)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_swarm_instances_swarm ON swarm_agent_instances(swarm_id)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_swarm_instances_agent ON swarm_agent_instances(agent_id)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_swarm_executions_swarm ON swarm_executions(swarm_id)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_swarm_events_execution ON swarm_events_log(execution_id)")
        
        logger.info("Swarm tables created successfully")
    
    # =========================================================================
    # Swarm CRUD Operations
    # =========================================================================
    
    def create_swarm(self, swarm_id: str, name: str, description: str = "",
                    config: Dict = None, definition: Dict = None,
                    category: str = "general", tags: List[str] = None,
                    created_by: str = "") -> bool:
        """Create a new swarm."""
        try:
            self.db.execute(
                """INSERT INTO swarms 
                   (swarm_id, name, description, config_json, definition_json, 
                    category, tags, created_by, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'draft')""",
                (swarm_id, name, description,
                 json.dumps(config or {}),
                 json.dumps(definition or {}),
                 category,
                 json.dumps(tags or []),
                 created_by)
            )
            return True
        except Exception as e:
            logger.error(f"Error creating swarm: {e}")
            return False
    
    def get_swarm(self, swarm_id: str) -> Optional[Dict]:
        """Get a swarm by ID."""
        row = self.db.fetch_one(
            "SELECT * FROM swarms WHERE swarm_id = ? AND is_deleted = 0",
            (swarm_id,)
        )
        if row:
            return self._row_to_swarm_dict(row)
        return None
    
    def update_swarm(self, swarm_id: str, **kwargs) -> bool:
        """Update swarm fields."""
        allowed_fields = ['name', 'description', 'config_json', 'definition_json',
                         'category', 'tags', 'status', 'version']
        
        updates = []
        values = []
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                if field in ['config_json', 'definition_json'] and isinstance(value, dict):
                    value = json.dumps(value)
                elif field == 'tags' and isinstance(value, list):
                    value = json.dumps(value)
                values.append(value)
        
        if not updates:
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(swarm_id)
        
        try:
            self.db.execute(
                f"UPDATE swarms SET {', '.join(updates)} WHERE swarm_id = ?",
                tuple(values)
            )
            return True
        except Exception as e:
            logger.error(f"Error updating swarm: {e}")
            return False
    
    def delete_swarm(self, swarm_id: str, hard_delete: bool = False) -> bool:
        """Delete a swarm (soft delete by default)."""
        try:
            if hard_delete:
                # Delete related records first
                self.db.execute("DELETE FROM swarm_events_log WHERE swarm_id = ?", (swarm_id,))
                self.db.execute("DELETE FROM swarm_executions WHERE swarm_id = ?", (swarm_id,))
                self.db.execute("DELETE FROM swarm_agent_instances WHERE swarm_id = ?", (swarm_id,))
                self.db.execute("DELETE FROM swarm_triggers WHERE swarm_id = ?", (swarm_id,))
                self.db.execute("DELETE FROM swarm_agent_memberships WHERE swarm_id = ?", (swarm_id,))
                self.db.execute("DELETE FROM swarms WHERE swarm_id = ?", (swarm_id,))
            else:
                self.db.execute(
                    "UPDATE swarms SET is_deleted = 1, status = 'deleted', updated_at = CURRENT_TIMESTAMP WHERE swarm_id = ?",
                    (swarm_id,)
                )
            return True
        except Exception as e:
            logger.error(f"Error deleting swarm: {e}")
            return False
    
    def list_swarms(self, status: str = None, category: str = None,
                   limit: int = 100, offset: int = 0) -> List[Dict]:
        """List swarms with optional filtering."""
        query = "SELECT * FROM swarms WHERE is_deleted = 0"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        rows = self.db.fetch_all(query, tuple(params)) or []
        return [self._row_to_swarm_dict(row) for row in rows]
    
    def update_swarm_status(self, swarm_id: str, status: str) -> bool:
        """Update swarm status."""
        try:
            self.db.execute(
                "UPDATE swarms SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE swarm_id = ?",
                (status, swarm_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error updating swarm status: {e}")
            return False
    
    def update_swarm_stats(self, swarm_id: str, success: bool = True,
                          execution_time: float = 0.0, events: int = 0) -> bool:
        """Update swarm execution statistics."""
        try:
            if success:
                self.db.execute(
                    """UPDATE swarms SET 
                       total_executions = total_executions + 1,
                       successful_executions = successful_executions + 1,
                       total_events_processed = total_events_processed + ?,
                       avg_execution_time = (avg_execution_time * total_executions + ?) / (total_executions + 1),
                       updated_at = CURRENT_TIMESTAMP
                       WHERE swarm_id = ?""",
                    (events, execution_time, swarm_id)
                )
            else:
                self.db.execute(
                    """UPDATE swarms SET 
                       total_executions = total_executions + 1,
                       failed_executions = failed_executions + 1,
                       updated_at = CURRENT_TIMESTAMP
                       WHERE swarm_id = ?""",
                    (swarm_id,)
                )
            return True
        except Exception as e:
            logger.error(f"Error updating swarm stats: {e}")
            return False
    
    # =========================================================================
    # Agent Membership Operations
    # =========================================================================
    
    def add_agent_membership(self, membership_id: str, swarm_id: str, agent_id: str,
                            agent_name: str = "", role: str = "worker",
                            description: str = "", subscriptions: List[Dict] = None,
                            min_instances: int = 0, max_instances: int = 10,
                            auto_scale: bool = True, idle_timeout: int = 300) -> bool:
        """Add an agent to a swarm."""
        try:
            self.db.execute(
                """INSERT INTO swarm_agent_memberships 
                   (membership_id, swarm_id, agent_id, agent_name, role, description,
                    subscriptions_json, min_instances, max_instances, auto_scale, idle_timeout)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (membership_id, swarm_id, agent_id, agent_name, role, description,
                 json.dumps(subscriptions or []), min_instances, max_instances,
                 1 if auto_scale else 0, idle_timeout)
            )
            return True
        except Exception as e:
            logger.error(f"Error adding agent membership: {e}")
            return False
    
    def get_swarm_memberships(self, swarm_id: str) -> List[Dict]:
        """Get all agent memberships for a swarm."""
        rows = self.db.fetch_all(
            "SELECT * FROM swarm_agent_memberships WHERE swarm_id = ? AND is_active = 1",
            (swarm_id,)
        ) or []
        return [self._row_to_membership_dict(row) for row in rows]
    
    def update_membership(self, membership_id: str, **kwargs) -> bool:
        """Update an agent membership."""
        allowed_fields = ['role', 'description', 'subscriptions_json', 'min_instances',
                         'max_instances', 'auto_scale', 'idle_timeout', 'is_active']
        
        updates = []
        values = []
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                if field == 'subscriptions_json' and isinstance(value, list):
                    value = json.dumps(value)
                values.append(value)
        
        if not updates:
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(membership_id)
        
        try:
            self.db.execute(
                f"UPDATE swarm_agent_memberships SET {', '.join(updates)} WHERE membership_id = ?",
                tuple(values)
            )
            return True
        except Exception as e:
            logger.error(f"Error updating membership: {e}")
            return False
    
    def remove_agent_membership(self, membership_id: str) -> bool:
        """Remove an agent from a swarm."""
        try:
            self.db.execute(
                "DELETE FROM swarm_agent_instances WHERE membership_id = ?",
                (membership_id,)
            )
            self.db.execute(
                "DELETE FROM swarm_agent_memberships WHERE membership_id = ?",
                (membership_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error removing membership: {e}")
            return False
    
    # =========================================================================
    # Agent Instance Pool Operations (Round-Robin)
    # =========================================================================
    
    def create_agent_instance(self, instance_id: str, swarm_id: str, 
                             agent_id: str, membership_id: str) -> bool:
        """Create a new agent instance in the pool."""
        try:
            self.db.execute(
                """INSERT INTO swarm_agent_instances 
                   (instance_id, swarm_id, agent_id, membership_id, status)
                   VALUES (?, ?, ?, ?, 'idle')""",
                (instance_id, swarm_id, agent_id, membership_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error creating agent instance: {e}")
            return False
    
    def get_next_available_instance(self, swarm_id: str, agent_id: str) -> Optional[Dict]:
        """
        Get next available instance using round-robin.
        
        Selects the idle instance that was least recently used.
        """
        row = self.db.fetch_one(
            """SELECT * FROM swarm_agent_instances 
               WHERE swarm_id = ? AND agent_id = ? AND status = 'idle'
               ORDER BY COALESCE(last_used, '1970-01-01') ASC, use_count ASC
               LIMIT 1""",
            (swarm_id, agent_id)
        )
        return dict(row) if row else None
    
    def mark_instance_busy(self, instance_id: str, task_id: str) -> bool:
        """Mark an instance as busy with a task."""
        try:
            self.db.execute(
                """UPDATE swarm_agent_instances 
                   SET status = 'busy', current_task_id = ?, 
                       last_used = CURRENT_TIMESTAMP, use_count = use_count + 1,
                       updated_at = CURRENT_TIMESTAMP
                   WHERE instance_id = ?""",
                (task_id, instance_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error marking instance busy: {e}")
            return False
    
    def mark_instance_idle(self, instance_id: str, task_success: bool = True,
                          task_time: float = 0.0) -> bool:
        """Mark an instance as idle after completing a task."""
        try:
            if task_success:
                self.db.execute(
                    """UPDATE swarm_agent_instances 
                       SET status = 'idle', current_task_id = NULL,
                           tasks_completed = tasks_completed + 1,
                           avg_task_time = (avg_task_time * tasks_completed + ?) / (tasks_completed + 1),
                           updated_at = CURRENT_TIMESTAMP
                       WHERE instance_id = ?""",
                    (task_time, instance_id)
                )
            else:
                self.db.execute(
                    """UPDATE swarm_agent_instances 
                       SET status = 'idle', current_task_id = NULL,
                           tasks_failed = tasks_failed + 1,
                           updated_at = CURRENT_TIMESTAMP
                       WHERE instance_id = ?""",
                    (instance_id,)
                )
            return True
        except Exception as e:
            logger.error(f"Error marking instance idle: {e}")
            return False
    
    def get_pool_status(self, swarm_id: str, agent_id: str = None) -> Dict:
        """Get pool status for a swarm or specific agent."""
        if agent_id:
            rows = self.db.fetch_all(
                "SELECT status, COUNT(*) as count FROM swarm_agent_instances WHERE swarm_id = ? AND agent_id = ? GROUP BY status",
                (swarm_id, agent_id)
            ) or []
        else:
            rows = self.db.fetch_all(
                "SELECT agent_id, status, COUNT(*) as count FROM swarm_agent_instances WHERE swarm_id = ? GROUP BY agent_id, status",
                (swarm_id,)
            ) or []
        
        return [dict(r) for r in rows]
    
    def remove_instance(self, instance_id: str) -> bool:
        """Remove an agent instance from the pool."""
        try:
            self.db.execute(
                "DELETE FROM swarm_agent_instances WHERE instance_id = ?",
                (instance_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error removing instance: {e}")
            return False
    
    # =========================================================================
    # Trigger Operations
    # =========================================================================
    
    def add_trigger(self, trigger_id: str, swarm_id: str, trigger_type: str,
                   name: str = "", description: str = "", config: Dict = None,
                   filter_expression: str = None) -> bool:
        """Add a trigger to a swarm."""
        try:
            self.db.execute(
                """INSERT INTO swarm_triggers 
                   (trigger_id, swarm_id, trigger_type, name, description, config_json, filter_expression)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (trigger_id, swarm_id, trigger_type, name, description,
                 json.dumps(config or {}), filter_expression)
            )
            return True
        except Exception as e:
            logger.error(f"Error adding trigger: {e}")
            return False
    
    def get_swarm_triggers(self, swarm_id: str) -> List[Dict]:
        """Get all triggers for a swarm."""
        rows = self.db.fetch_all(
            "SELECT * FROM swarm_triggers WHERE swarm_id = ?",
            (swarm_id,)
        ) or []
        return [self._row_to_trigger_dict(row) for row in rows]
    
    def update_trigger(self, trigger_id: str, **kwargs) -> bool:
        """Update a trigger."""
        allowed_fields = ['name', 'description', 'config_json', 'filter_expression', 'is_active']
        
        updates = []
        values = []
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                if field == 'config_json' and isinstance(value, dict):
                    value = json.dumps(value)
                values.append(value)
        
        if not updates:
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(trigger_id)
        
        try:
            self.db.execute(
                f"UPDATE swarm_triggers SET {', '.join(updates)} WHERE trigger_id = ?",
                tuple(values)
            )
            return True
        except Exception as e:
            logger.error(f"Error updating trigger: {e}")
            return False
    
    def record_trigger_fired(self, trigger_id: str) -> bool:
        """Record that a trigger has fired."""
        try:
            self.db.execute(
                """UPDATE swarm_triggers 
                   SET last_triggered = CURRENT_TIMESTAMP, trigger_count = trigger_count + 1
                   WHERE trigger_id = ?""",
                (trigger_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error recording trigger: {e}")
            return False
    
    def remove_trigger(self, trigger_id: str) -> bool:
        """Remove a trigger from a swarm."""
        try:
            self.db.execute(
                "DELETE FROM swarm_triggers WHERE trigger_id = ?",
                (trigger_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error removing trigger: {e}")
            return False
    
    # =========================================================================
    # Execution History Operations
    # =========================================================================
    
    def start_execution(self, execution_id: str, swarm_id: str,
                       trigger_type: str, trigger_id: str = None,
                       trigger_data: Any = None, correlation_id: str = None,
                       user_id: str = None) -> bool:
        """Record start of a swarm execution."""
        try:
            self.db.execute(
                """INSERT INTO swarm_executions 
                   (execution_id, swarm_id, correlation_id, trigger_type, trigger_id,
                    trigger_data, status, started_at, user_id)
                   VALUES (?, ?, ?, ?, ?, ?, 'running', CURRENT_TIMESTAMP, ?)""",
                (execution_id, swarm_id, correlation_id, trigger_type, trigger_id,
                 json.dumps(trigger_data) if trigger_data else None, user_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error starting execution: {e}")
            return False
    
    def complete_execution(self, execution_id: str, success: bool,
                          result: Any = None, error: str = None,
                          events_processed: int = 0, agents_used: int = 0,
                          iterations: int = 0) -> bool:
        """Record completion of a swarm execution."""
        try:
            status = 'completed' if success else 'failed'
            # Calculate duration in milliseconds
            self.db.execute(
                """UPDATE swarm_executions 
                   SET status = ?, completed_at = CURRENT_TIMESTAMP,
                       duration_ms = CAST((julianday(CURRENT_TIMESTAMP) - julianday(started_at)) * 86400000 AS INTEGER),
                       result_json = ?, error_message = ?,
                       events_processed = ?, agents_used = ?, iterations = ?
                   WHERE execution_id = ?""",
                (status, json.dumps(result) if result else None, error,
                 events_processed, agents_used, iterations, execution_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error completing execution: {e}")
            return False
    
    def get_executions(self, swarm_id: str, limit: int = 50, 
                      status: str = None) -> List[Dict]:
        """Get execution history for a swarm."""
        query = "SELECT * FROM swarm_executions WHERE swarm_id = ?"
        params = [swarm_id]
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY started_at DESC LIMIT ?"
        params.append(limit)
        
        rows = self.db.fetch_all(query, tuple(params)) or []
        return [dict(r) for r in rows]
    
    def get_execution(self, execution_id: str) -> Optional[Dict]:
        """Get a specific execution."""
        row = self.db.fetch_one(
            "SELECT * FROM swarm_executions WHERE execution_id = ?",
            (execution_id,)
        )
        return dict(row) if row else None
    
    # =========================================================================
    # Event Logging
    # =========================================================================
    
    def log_event(self, event_id: str, swarm_id: str, execution_id: str,
                 event_type: str, source: str, target: str = None,
                 payload: Any = None, priority: int = 1,
                 correlation_id: str = None, parent_id: str = None) -> bool:
        """Log a swarm event."""
        try:
            self.db.execute(
                """INSERT INTO swarm_events_log 
                   (event_id, swarm_id, execution_id, event_type, source, target,
                    payload_json, priority, correlation_id, parent_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (event_id, swarm_id, execution_id, event_type, source, target,
                 json.dumps(payload) if payload else None, priority,
                 correlation_id, parent_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error logging event: {e}")
            return False
    
    def get_execution_events(self, execution_id: str, limit: int = 1000) -> List[Dict]:
        """Get events for a specific execution."""
        rows = self.db.fetch_all(
            """SELECT * FROM swarm_events_log 
               WHERE execution_id = ? 
               ORDER BY timestamp ASC LIMIT ?""",
            (execution_id, limit)
        ) or []
        return [dict(r) for r in rows]
    
    def cleanup_old_events(self, days: int = 30) -> int:
        """Clean up old event logs."""
        try:
            result = self.db.execute(
                """DELETE FROM swarm_events_log 
                   WHERE timestamp < datetime('now', ?)""",
                (f'-{days} days',)
            )
            return result.rowcount if hasattr(result, 'rowcount') else 0
        except Exception as e:
            logger.error(f"Error cleaning up events: {e}")
            return 0
    
    # =========================================================================
    # Helper Methods
    # =========================================================================
    
    def _row_to_swarm_dict(self, row) -> Dict:
        """Convert database row to swarm dictionary."""
        d = dict(row)
        
        # Parse JSON fields
        if d.get('config_json'):
            try:
                d['config'] = json.loads(d['config_json'])
            except:
                d['config'] = {}
        
        if d.get('definition_json'):
            try:
                d['definition'] = json.loads(d['definition_json'])
            except:
                d['definition'] = {}
        
        if d.get('tags'):
            try:
                d['tags'] = json.loads(d['tags'])
            except:
                d['tags'] = []
        
        return d
    
    def _row_to_membership_dict(self, row) -> Dict:
        """Convert database row to membership dictionary."""
        d = dict(row)
        
        if d.get('subscriptions_json'):
            try:
                d['subscriptions'] = json.loads(d['subscriptions_json'])
            except:
                d['subscriptions'] = []
        
        d['auto_scale'] = bool(d.get('auto_scale', 0))
        d['is_active'] = bool(d.get('is_active', 1))
        
        return d
    
    def _row_to_trigger_dict(self, row) -> Dict:
        """Convert database row to trigger dictionary."""
        d = dict(row)
        
        if d.get('config_json'):
            try:
                d['config'] = json.loads(d['config_json'])
            except:
                d['config'] = {}
        
        d['is_active'] = bool(d.get('is_active', 1))
        
        return d
