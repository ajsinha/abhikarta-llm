"""
AI Org Database Operations - Persistence layer for AI Organizations.

This module provides database operations using the delegate pattern
to support both SQLite and PostgreSQL.

Version: 1.4.7
Copyright © 2025-2030, All Rights Reserved
"""

import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from .models import (
    AIOrg, AINode, AITask, AIResponse, AIHITLAction,
    AIEventLog, HITLQueueItem, OrgStatus, NodeType, TaskStatus,
    TaskPriority, ResponseType, HITLActionType, DelegationStrategy
)

logger = logging.getLogger(__name__)


def _timestamp_now() -> str:
    """
    Get current timestamp in SQLite-compatible format.
    
    Uses space separator instead of T for Python 3.14 compatibility.
    Format: YYYY-MM-DD HH:MM:SS.ffffff
    """
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')


class AIORGDBOps:
    """
    Database operations for AI Org module.
    
    Uses the delegate pattern - actual database access is through
    the provided db_facade which abstracts SQLite/PostgreSQL.
    
    Transaction handling:
    - SQLite: Auto-commits per execute(), explicit commit/rollback available
    - PostgreSQL: Requires explicit commit/rollback for transaction control
    """
    
    def __init__(self, db_facade):
        """
        Initialize with database facade.
        
        Args:
            db_facade: Database facade instance (SQLite or Postgres)
        """
        self.db = db_facade
        self._ensure_tables()
    
    def _ensure_tables(self):
        """
        Ensure AI Org tables exist.
        
        Tables should be created by the main schema initialization.
        This is a fallback for cases where schema wasn't initialized
        or for runtime table verification.
        """
        try:
            # Try a simple query to check if tables exist
            self.db.fetch_one("SELECT 1 FROM ai_orgs LIMIT 1")
        except Exception:
            # Tables don't exist, create them
            logger.info("AI Org tables not found, creating...")
            self._create_tables()
    
    def _create_tables(self):
        """
        Create AI Org tables.
        
        Uses CREATE TABLE IF NOT EXISTS for idempotency.
        Schema matches the official sqlite_schema.py / postgres_schema.py
        """
        logger.info("Creating AI Org tables...")
        
        # Determine if we need to commit manually (PostgreSQL)
        needs_commit = not getattr(self.db, 'is_auto_commit', True)
        
        try:
            # AI Organizations table - matches sqlite_schema.py
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS ai_orgs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    org_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'draft',
                    config TEXT DEFAULT '{}',
                    event_bus_channel TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # AI Nodes table - matches sqlite_schema.py
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS ai_nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_id TEXT UNIQUE NOT NULL,
                    org_id TEXT NOT NULL,
                    parent_node_id TEXT,
                    role_name TEXT NOT NULL,
                    role_type TEXT DEFAULT 'analyst',
                    description TEXT,
                    agent_id TEXT,
                    agent_config TEXT DEFAULT '{}',
                    human_name TEXT,
                    human_email TEXT,
                    human_teams_id TEXT,
                    human_slack_id TEXT,
                    hitl_enabled INTEGER DEFAULT 0,
                    hitl_approval_required INTEGER DEFAULT 0,
                    hitl_review_delegation INTEGER DEFAULT 0,
                    hitl_timeout_hours INTEGER DEFAULT 24,
                    hitl_auto_proceed INTEGER DEFAULT 1,
                    notification_channels TEXT DEFAULT '["email"]',
                    notification_triggers TEXT DEFAULT '[]',
                    position_x INTEGER DEFAULT 0,
                    position_y INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    current_task_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (org_id) REFERENCES ai_orgs(org_id) ON DELETE CASCADE
                )
            """)
            
            # AI Tasks table - matches sqlite_schema.py
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS ai_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT UNIQUE NOT NULL,
                    org_id TEXT NOT NULL,
                    parent_task_id TEXT,
                    assigned_node_id TEXT,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT DEFAULT 'medium',
                    input_data TEXT DEFAULT '{}',
                    output_data TEXT,
                    context TEXT DEFAULT '{}',
                    attachments TEXT DEFAULT '[]',
                    status TEXT DEFAULT 'pending',
                    delegation_strategy TEXT DEFAULT 'parallel',
                    expected_responses INTEGER DEFAULT 0,
                    received_responses INTEGER DEFAULT 0,
                    deadline TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (org_id) REFERENCES ai_orgs(org_id) ON DELETE CASCADE,
                    FOREIGN KEY (assigned_node_id) REFERENCES ai_nodes(node_id) ON DELETE SET NULL
                )
            """)
            
            # AI Responses table - matches sqlite_schema.py
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS ai_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    response_id TEXT UNIQUE NOT NULL,
                    task_id TEXT NOT NULL,
                    node_id TEXT NOT NULL,
                    response_type TEXT DEFAULT 'analysis',
                    content TEXT DEFAULT '{}',
                    summary TEXT,
                    reasoning TEXT,
                    confidence_score REAL DEFAULT 0.0,
                    quality_score REAL DEFAULT 0.0,
                    is_human_modified INTEGER DEFAULT 0,
                    original_ai_content TEXT,
                    modification_reason TEXT,
                    modified_by TEXT,
                    modified_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES ai_tasks(task_id) ON DELETE CASCADE,
                    FOREIGN KEY (node_id) REFERENCES ai_nodes(node_id) ON DELETE CASCADE
                )
            """)
            
            # AI HITL Actions table - matches sqlite_schema.py
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS ai_hitl_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_id TEXT UNIQUE NOT NULL,
                    org_id TEXT NOT NULL,
                    node_id TEXT NOT NULL,
                    task_id TEXT,
                    response_id TEXT,
                    user_id TEXT,
                    action_type TEXT NOT NULL,
                    original_content TEXT,
                    modified_content TEXT,
                    reason TEXT,
                    message TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (org_id) REFERENCES ai_orgs(org_id) ON DELETE CASCADE,
                    FOREIGN KEY (task_id) REFERENCES ai_tasks(task_id) ON DELETE SET NULL,
                    FOREIGN KEY (node_id) REFERENCES ai_nodes(node_id) ON DELETE CASCADE
                )
            """)
            
            # AI Event Logs table - matches sqlite_schema.py
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS ai_event_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE NOT NULL,
                    org_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    source_node_id TEXT,
                    target_node_id TEXT,
                    task_id TEXT,
                    payload TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (org_id) REFERENCES ai_orgs(org_id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes
            try:
                self.db.execute("CREATE INDEX IF NOT EXISTS idx_ai_orgs_status ON ai_orgs(status)")
                self.db.execute("CREATE INDEX IF NOT EXISTS idx_ai_orgs_created_by ON ai_orgs(created_by)")
                self.db.execute("CREATE INDEX IF NOT EXISTS idx_ai_nodes_org_id ON ai_nodes(org_id)")
                self.db.execute("CREATE INDEX IF NOT EXISTS idx_ai_nodes_parent_node_id ON ai_nodes(parent_node_id)")
                self.db.execute("CREATE INDEX IF NOT EXISTS idx_ai_nodes_human_email ON ai_nodes(human_email)")
                self.db.execute("CREATE INDEX IF NOT EXISTS idx_ai_tasks_org_id ON ai_tasks(org_id)")
                self.db.execute("CREATE INDEX IF NOT EXISTS idx_ai_tasks_assigned_node_id ON ai_tasks(assigned_node_id)")
                self.db.execute("CREATE INDEX IF NOT EXISTS idx_ai_tasks_status ON ai_tasks(status)")
                self.db.execute("CREATE INDEX IF NOT EXISTS idx_ai_responses_task_id ON ai_responses(task_id)")
                self.db.execute("CREATE INDEX IF NOT EXISTS idx_ai_responses_node_id ON ai_responses(node_id)")
                self.db.execute("CREATE INDEX IF NOT EXISTS idx_ai_hitl_actions_org_id ON ai_hitl_actions(org_id)")
                self.db.execute("CREATE INDEX IF NOT EXISTS idx_ai_hitl_actions_task_id ON ai_hitl_actions(task_id)")
                self.db.execute("CREATE INDEX IF NOT EXISTS idx_ai_event_logs_org_id ON ai_event_logs(org_id)")
                self.db.execute("CREATE INDEX IF NOT EXISTS idx_ai_event_logs_event_type ON ai_event_logs(event_type)")
            except Exception as e:
                logger.warning(f"Index creation warning (may already exist): {e}")
            
            # Commit if needed (PostgreSQL)
            if needs_commit:
                self.db.commit()
                
            logger.info("AI Org tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating AI Org tables: {e}")
            if needs_commit:
                self.db.rollback()
            raise
    
    # =========================================================================
    # AI ORG OPERATIONS
    # =========================================================================
    
    def save_org(self, org: AIOrg) -> bool:
        """
        Save or update an AI Organization.
        
        Args:
            org: AIOrg instance
            
        Returns:
            True if successful
        """
        try:
            data = org.to_dict()
            data['config'] = json.dumps(data['config']) if data['config'] else '{}'
            
            # Check if exists
            existing = self.get_org(org.org_id)
            
            if existing:
                # Update
                self.db.execute("""
                    UPDATE ai_orgs 
                    SET name = ?, description = ?, status = ?, config = ?,
                        event_bus_channel = ?, updated_at = ?
                    WHERE org_id = ?
                """, (
                    data['name'], data['description'], data['status'],
                    data['config'], data['event_bus_channel'],
                    _timestamp_now(), org.org_id
                ))
            else:
                # Insert
                self.db.execute("""
                    INSERT INTO ai_orgs 
                    (org_id, name, description, status, config, event_bus_channel,
                     created_by, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data['org_id'], data['name'], data['description'],
                    data['status'], data['config'], data['event_bus_channel'],
                    data['created_by'], data['created_at'], data['updated_at']
                ))
            
            return True
        except Exception as e:
            logger.error(f"Error saving org {org.org_id}: {e}")
            return False
    
    def get_org(self, org_id: str) -> Optional[AIOrg]:
        """
        Get an AI Organization by ID.
        
        Args:
            org_id: Organization ID
            
        Returns:
            AIOrg instance or None
        """
        try:
            result = self.db.fetch_one(
                "SELECT * FROM ai_orgs WHERE org_id = ?",
                (org_id,)
            )
            
            if result:
                # result is already a dict from fetch_one
                data = result if isinstance(result, dict) else dict(result)
                data['config'] = json.loads(data['config']) if data.get('config') else {}
                return AIOrg.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"Error getting org {org_id}: {e}")
            return None
    
    def list_orgs(
        self,
        status: Optional[OrgStatus] = None,
        created_by: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AIOrg]:
        """
        List AI Organizations with optional filters.
        
        Args:
            status: Filter by status
            created_by: Filter by creator
            limit: Maximum results
            offset: Offset for pagination
            
        Returns:
            List of AIOrg instances
        """
        try:
            query = "SELECT * FROM ai_orgs WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status.value)
            
            if created_by:
                query += " AND created_by = ?"
                params.append(created_by)
            
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            results = self.db.fetch_all(query, tuple(params))
            
            orgs = []
            for row in results:
                # row is already a dict from fetch_all
                data = row if isinstance(row, dict) else dict(row)
                data['config'] = json.loads(data['config']) if data.get('config') else {}
                orgs.append(AIOrg.from_dict(data))
            
            return orgs
        except Exception as e:
            logger.error(f"Error listing orgs: {e}")
            return []
    
    def delete_org(self, org_id: str) -> bool:
        """
        Delete an AI Organization and all related data.
        
        Args:
            org_id: Organization ID
            
        Returns:
            True if successful
        """
        try:
            # Delete in order to respect foreign keys
            self.db.execute("DELETE FROM ai_hitl_actions WHERE org_id = ?", (org_id,))
            self.db.execute("DELETE FROM ai_responses WHERE task_id IN (SELECT task_id FROM ai_tasks WHERE org_id = ?)", (org_id,))
            self.db.execute("DELETE FROM ai_tasks WHERE org_id = ?", (org_id,))
            self.db.execute("DELETE FROM ai_nodes WHERE org_id = ?", (org_id,))
            self.db.execute("DELETE FROM ai_event_logs WHERE org_id = ?", (org_id,))
            self.db.execute("DELETE FROM ai_orgs WHERE org_id = ?", (org_id,))
            
            return True
        except Exception as e:
            logger.error(f"Error deleting org {org_id}: {e}")
            return False
    
    # =========================================================================
    # AI NODE OPERATIONS
    # =========================================================================
    
    def save_node(self, node: AINode) -> bool:
        """
        Save or update an AI Node.
        
        Args:
            node: AINode instance
            
        Returns:
            True if successful
        """
        try:
            data = node.to_dict()
            data['agent_config'] = json.dumps(data['agent_config']) if data['agent_config'] else '{}'
            data['notification_channels'] = json.dumps(data['notification_channels'])
            data['notification_triggers'] = json.dumps(data['notification_triggers'])
            
            existing = self.get_node(node.node_id)
            
            if existing:
                self.db.execute("""
                    UPDATE ai_nodes 
                    SET parent_node_id = ?, role_name = ?, role_type = ?,
                        description = ?, agent_id = ?, agent_config = ?,
                        human_name = ?, human_email = ?, human_teams_id = ?,
                        human_slack_id = ?, hitl_enabled = ?, hitl_approval_required = ?,
                        hitl_review_delegation = ?, hitl_timeout_hours = ?,
                        hitl_auto_proceed = ?, notification_channels = ?,
                        notification_triggers = ?, position_x = ?, position_y = ?,
                        status = ?, current_task_id = ?, updated_at = ?
                    WHERE node_id = ?
                """, (
                    data['parent_node_id'], data['role_name'], data['role_type'],
                    data['description'], data['agent_id'], data['agent_config'],
                    data['human_name'], data['human_email'], data['human_teams_id'],
                    data['human_slack_id'], data['hitl_enabled'], data['hitl_approval_required'],
                    data['hitl_review_delegation'], data['hitl_timeout_hours'],
                    data['hitl_auto_proceed'], data['notification_channels'],
                    data['notification_triggers'], data['position_x'], data['position_y'],
                    data['status'], data['current_task_id'],
                    _timestamp_now(), node.node_id
                ))
            else:
                self.db.execute("""
                    INSERT INTO ai_nodes 
                    (node_id, org_id, parent_node_id, role_name, role_type,
                     description, agent_id, agent_config, human_name, human_email,
                     human_teams_id, human_slack_id, hitl_enabled, hitl_approval_required,
                     hitl_review_delegation, hitl_timeout_hours, hitl_auto_proceed,
                     notification_channels, notification_triggers, position_x, position_y,
                     status, current_task_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data['node_id'], data['org_id'], data['parent_node_id'],
                    data['role_name'], data['role_type'], data['description'],
                    data['agent_id'], data['agent_config'], data['human_name'],
                    data['human_email'], data['human_teams_id'], data['human_slack_id'],
                    data['hitl_enabled'], data['hitl_approval_required'],
                    data['hitl_review_delegation'], data['hitl_timeout_hours'],
                    data['hitl_auto_proceed'], data['notification_channels'],
                    data['notification_triggers'], data['position_x'], data['position_y'],
                    data['status'], data['current_task_id'],
                    data['created_at'], data['updated_at']
                ))
            
            return True
        except Exception as e:
            logger.error(f"Error saving node {node.node_id}: {e}")
            return False
    
    def get_node(self, node_id: str) -> Optional[AINode]:
        """Get an AI Node by ID."""
        try:
            result = self.db.fetch_one(
                "SELECT * FROM ai_nodes WHERE node_id = ?",
                (node_id,)
            )
            
            if result:
                data = dict(result)
                data['agent_config'] = json.loads(data['agent_config']) if data['agent_config'] else {}
                data['notification_channels'] = json.loads(data['notification_channels']) if data['notification_channels'] else []
                data['notification_triggers'] = json.loads(data['notification_triggers']) if data['notification_triggers'] else []
                return AINode.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"Error getting node {node_id}: {e}")
            return None
    
    def get_org_nodes(self, org_id: str) -> List[AINode]:
        """Get all nodes for an organization."""
        try:
            results = self.db.fetch_all(
                "SELECT * FROM ai_nodes WHERE org_id = ? ORDER BY position_y, position_x",
                (org_id,)
            )
            
            nodes = []
            for row in results:
                data = dict(row)
                data['agent_config'] = json.loads(data['agent_config']) if data['agent_config'] else {}
                data['notification_channels'] = json.loads(data['notification_channels']) if data['notification_channels'] else []
                data['notification_triggers'] = json.loads(data['notification_triggers']) if data['notification_triggers'] else []
                nodes.append(AINode.from_dict(data))
            
            return nodes
        except Exception as e:
            logger.error(f"Error getting nodes for org {org_id}: {e}")
            return []
    
    def get_child_nodes(self, parent_node_id: str) -> List[AINode]:
        """Get all child nodes of a parent node."""
        try:
            results = self.db.fetch_all(
                "SELECT * FROM ai_nodes WHERE parent_node_id = ?",
                (parent_node_id,)
            )
            
            nodes = []
            for row in results:
                data = dict(row)
                data['agent_config'] = json.loads(data['agent_config']) if data['agent_config'] else {}
                data['notification_channels'] = json.loads(data['notification_channels']) if data['notification_channels'] else []
                data['notification_triggers'] = json.loads(data['notification_triggers']) if data['notification_triggers'] else []
                nodes.append(AINode.from_dict(data))
            
            return nodes
        except Exception as e:
            logger.error(f"Error getting children of {parent_node_id}: {e}")
            return []
    
    def get_root_node(self, org_id: str) -> Optional[AINode]:
        """Get the root node (CEO) of an organization."""
        try:
            result = self.db.fetch_one(
                "SELECT * FROM ai_nodes WHERE org_id = ? AND parent_node_id IS NULL",
                (org_id,)
            )
            
            if result:
                data = dict(result)
                data['agent_config'] = json.loads(data['agent_config']) if data['agent_config'] else {}
                data['notification_channels'] = json.loads(data['notification_channels']) if data['notification_channels'] else []
                data['notification_triggers'] = json.loads(data['notification_triggers']) if data['notification_triggers'] else []
                return AINode.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"Error getting root node for org {org_id}: {e}")
            return None
    
    def delete_node(self, node_id: str) -> bool:
        """Delete an AI Node."""
        try:
            self.db.execute("DELETE FROM ai_nodes WHERE node_id = ?", (node_id,))
            return True
        except Exception as e:
            logger.error(f"Error deleting node {node_id}: {e}")
            return False
    
    def get_nodes_by_email(self, email: str) -> List[AINode]:
        """Get all nodes where user is human mirror."""
        try:
            results = self.db.fetch_all(
                "SELECT * FROM ai_nodes WHERE human_email = ?",
                (email,)
            )
            
            nodes = []
            for row in results:
                data = dict(row)
                data['agent_config'] = json.loads(data['agent_config']) if data['agent_config'] else {}
                data['notification_channels'] = json.loads(data['notification_channels']) if data['notification_channels'] else []
                data['notification_triggers'] = json.loads(data['notification_triggers']) if data['notification_triggers'] else []
                nodes.append(AINode.from_dict(data))
            
            return nodes
        except Exception as e:
            logger.error(f"Error getting nodes for email {email}: {e}")
            return []
    
    # =========================================================================
    # AI TASK OPERATIONS
    # =========================================================================
    
    def save_task(self, task: AITask) -> bool:
        """Save or update an AI Task."""
        try:
            data = task.to_dict()
            data['input_data'] = json.dumps(data['input_data']) if data['input_data'] else '{}'
            data['output_data'] = json.dumps(data['output_data']) if data['output_data'] else None
            data['context'] = json.dumps(data['context']) if data['context'] else '{}'
            data['attachments'] = json.dumps(data['attachments']) if data['attachments'] else '[]'
            
            existing = self.get_task(task.task_id)
            
            if existing:
                self.db.execute("""
                    UPDATE ai_tasks 
                    SET status = ?, delegation_strategy = ?, expected_responses = ?,
                        received_responses = ?, output_data = ?, started_at = ?,
                        completed_at = ?, error_message = ?, retry_count = ?, updated_at = ?
                    WHERE task_id = ?
                """, (
                    data['status'], data['delegation_strategy'],
                    data['expected_responses'], data['received_responses'],
                    data['output_data'], data['started_at'], data['completed_at'],
                    data['error_message'], data['retry_count'],
                    _timestamp_now(), task.task_id
                ))
            else:
                self.db.execute("""
                    INSERT INTO ai_tasks 
                    (task_id, org_id, parent_task_id, assigned_node_id, title,
                     description, priority, input_data, output_data, context,
                     attachments, status, delegation_strategy, expected_responses,
                     received_responses, deadline, started_at, completed_at,
                     error_message, retry_count, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data['task_id'], data['org_id'], data['parent_task_id'],
                    data['assigned_node_id'], data['title'], data['description'],
                    data['priority'], data['input_data'], data['output_data'],
                    data['context'], data['attachments'], data['status'],
                    data['delegation_strategy'], data['expected_responses'],
                    data['received_responses'], data['deadline'], data['started_at'],
                    data['completed_at'], data['error_message'], data['retry_count'],
                    data['created_at'], data['updated_at']
                ))
            
            return True
        except Exception as e:
            logger.error(f"Error saving task {task.task_id}: {e}")
            return False
    
    def get_task(self, task_id: str) -> Optional[AITask]:
        """Get an AI Task by ID."""
        try:
            result = self.db.fetch_one(
                "SELECT * FROM ai_tasks WHERE task_id = ?",
                (task_id,)
            )
            
            if result:
                data = dict(result)
                data['input_data'] = json.loads(data['input_data']) if data['input_data'] else {}
                data['output_data'] = json.loads(data['output_data']) if data['output_data'] else None
                data['context'] = json.loads(data['context']) if data['context'] else {}
                data['attachments'] = json.loads(data['attachments']) if data['attachments'] else []
                return AITask.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"Error getting task {task_id}: {e}")
            return None
    
    def get_org_tasks(
        self,
        org_id: str,
        status: Optional[TaskStatus] = None,
        limit: int = 100
    ) -> List[AITask]:
        """Get tasks for an organization."""
        try:
            query = "SELECT * FROM ai_tasks WHERE org_id = ?"
            params = [org_id]
            
            if status:
                query += " AND status = ?"
                params.append(status.value)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            results = self.db.fetch_all(query, tuple(params))
            
            tasks = []
            for row in results:
                data = dict(row)
                data['input_data'] = json.loads(data['input_data']) if data['input_data'] else {}
                data['output_data'] = json.loads(data['output_data']) if data['output_data'] else None
                data['context'] = json.loads(data['context']) if data['context'] else {}
                data['attachments'] = json.loads(data['attachments']) if data['attachments'] else []
                tasks.append(AITask.from_dict(data))
            
            return tasks
        except Exception as e:
            logger.error(f"Error getting tasks for org {org_id}: {e}")
            return []
    
    def get_subtasks(self, parent_task_id: str) -> List[AITask]:
        """Get subtasks of a parent task."""
        try:
            results = self.db.fetch_all(
                "SELECT * FROM ai_tasks WHERE parent_task_id = ?",
                (parent_task_id,)
            )
            
            tasks = []
            for row in results:
                data = dict(row)
                data['input_data'] = json.loads(data['input_data']) if data['input_data'] else {}
                data['output_data'] = json.loads(data['output_data']) if data['output_data'] else None
                data['context'] = json.loads(data['context']) if data['context'] else {}
                data['attachments'] = json.loads(data['attachments']) if data['attachments'] else []
                tasks.append(AITask.from_dict(data))
            
            return tasks
        except Exception as e:
            logger.error(f"Error getting subtasks of {parent_task_id}: {e}")
            return []
    
    def get_node_tasks(self, node_id: str, status: Optional[TaskStatus] = None) -> List[AITask]:
        """Get tasks assigned to a node."""
        try:
            query = "SELECT * FROM ai_tasks WHERE assigned_node_id = ?"
            params = [node_id]
            
            if status:
                query += " AND status = ?"
                params.append(status.value)
            
            query += " ORDER BY created_at DESC"
            
            results = self.db.fetch_all(query, tuple(params))
            
            tasks = []
            for row in results:
                data = dict(row)
                data['input_data'] = json.loads(data['input_data']) if data['input_data'] else {}
                data['output_data'] = json.loads(data['output_data']) if data['output_data'] else None
                data['context'] = json.loads(data['context']) if data['context'] else {}
                data['attachments'] = json.loads(data['attachments']) if data['attachments'] else []
                tasks.append(AITask.from_dict(data))
            
            return tasks
        except Exception as e:
            logger.error(f"Error getting tasks for node {node_id}: {e}")
            return []
    
    # =========================================================================
    # AI RESPONSE OPERATIONS
    # =========================================================================
    
    def save_response(self, response: AIResponse) -> bool:
        """Save an AI Response."""
        try:
            data = response.to_dict()
            data['content'] = json.dumps(data['content']) if data['content'] else '{}'
            data['original_ai_content'] = json.dumps(data['original_ai_content']) if data['original_ai_content'] else None
            
            self.db.execute("""
                INSERT INTO ai_responses 
                (response_id, task_id, node_id, response_type, content, summary,
                 reasoning, confidence_score, quality_score, is_human_modified,
                 original_ai_content, modification_reason, modified_by, modified_at,
                 created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['response_id'], data['task_id'], data['node_id'],
                data['response_type'], data['content'], data['summary'],
                data['reasoning'], data['confidence_score'], data['quality_score'],
                data['is_human_modified'], data['original_ai_content'],
                data['modification_reason'], data['modified_by'],
                data['modified_at'], data['created_at']
            ))
            
            return True
        except Exception as e:
            logger.error(f"Error saving response {response.response_id}: {e}")
            return False
    
    def get_response(self, response_id: str) -> Optional[AIResponse]:
        """Get an AI Response by ID."""
        try:
            result = self.db.fetch_one(
                "SELECT * FROM ai_responses WHERE response_id = ?",
                (response_id,)
            )
            
            if result:
                data = dict(result)
                data['content'] = json.loads(data['content']) if data['content'] else {}
                data['original_ai_content'] = json.loads(data['original_ai_content']) if data['original_ai_content'] else None
                return AIResponse.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"Error getting response {response_id}: {e}")
            return None
    
    def get_task_responses(self, task_id: str) -> List[AIResponse]:
        """Get all responses for a task."""
        try:
            results = self.db.fetch_all(
                "SELECT * FROM ai_responses WHERE task_id = ? ORDER BY created_at",
                (task_id,)
            )
            
            responses = []
            for row in results:
                data = dict(row)
                data['content'] = json.loads(data['content']) if data['content'] else {}
                data['original_ai_content'] = json.loads(data['original_ai_content']) if data['original_ai_content'] else None
                responses.append(AIResponse.from_dict(data))
            
            return responses
        except Exception as e:
            logger.error(f"Error getting responses for task {task_id}: {e}")
            return []
    
    # =========================================================================
    # HITL OPERATIONS
    # =========================================================================
    
    def save_hitl_action(self, action: AIHITLAction) -> bool:
        """Save a HITL action."""
        try:
            data = action.to_dict()
            data['original_content'] = json.dumps(data['original_content']) if data['original_content'] else None
            data['modified_content'] = json.dumps(data['modified_content']) if data['modified_content'] else None
            
            self.db.execute("""
                INSERT INTO ai_hitl_actions 
                (action_id, org_id, node_id, task_id, response_id, user_id,
                 action_type, original_content, modified_content, reason,
                 message, ip_address, user_agent, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['action_id'], data['org_id'], data['node_id'],
                data['task_id'], data['response_id'], data['user_id'],
                data['action_type'], data['original_content'],
                data['modified_content'], data['reason'], data['message'],
                data['ip_address'], data['user_agent'], data['created_at']
            ))
            
            return True
        except Exception as e:
            logger.error(f"Error saving HITL action: {e}")
            return False
    
    def get_hitl_actions(
        self,
        org_id: Optional[str] = None,
        node_id: Optional[str] = None,
        task_id: Optional[str] = None,
        limit: int = 100
    ) -> List[AIHITLAction]:
        """Get HITL actions with optional filters."""
        try:
            query = "SELECT * FROM ai_hitl_actions WHERE 1=1"
            params = []
            
            if org_id:
                query += " AND org_id = ?"
                params.append(org_id)
            
            if node_id:
                query += " AND node_id = ?"
                params.append(node_id)
            
            if task_id:
                query += " AND task_id = ?"
                params.append(task_id)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            results = self.db.fetch_all(query, tuple(params))
            
            actions = []
            for row in results:
                data = dict(row)
                data['original_content'] = json.loads(data['original_content']) if data['original_content'] else None
                data['modified_content'] = json.loads(data['modified_content']) if data['modified_content'] else None
                actions.append(AIHITLAction.from_dict(data))
            
            return actions
        except Exception as e:
            logger.error(f"Error getting HITL actions: {e}")
            return []
    
    # =========================================================================
    # EVENT LOG OPERATIONS
    # =========================================================================
    
    def save_event_log(self, event: AIEventLog) -> bool:
        """Save an event log entry."""
        try:
            data = event.to_dict()
            data['payload'] = json.dumps(data['payload']) if data['payload'] else '{}'
            
            self.db.execute("""
                INSERT INTO ai_event_logs 
                (event_id, org_id, event_type, source_node_id, target_node_id,
                 task_id, payload, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['event_id'], data['org_id'], data['event_type'],
                data['source_node_id'], data['target_node_id'],
                data['task_id'], data['payload'], data['created_at']
            ))
            
            return True
        except Exception as e:
            logger.error(f"Error saving event log: {e}")
            return False
    
    def get_event_logs(
        self,
        org_id: str,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[AIEventLog]:
        """Get event logs for an org."""
        try:
            query = "SELECT * FROM ai_event_logs WHERE org_id = ?"
            params = [org_id]
            
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            results = self.db.fetch_all(query, tuple(params))
            
            events = []
            for row in results:
                data = dict(row)
                data['payload'] = json.loads(data['payload']) if data['payload'] else {}
                events.append(AIEventLog(
                    event_id=data['event_id'],
                    org_id=data['org_id'],
                    event_type=data['event_type'],
                    source_node_id=data.get('source_node_id'),
                    target_node_id=data.get('target_node_id'),
                    task_id=data.get('task_id'),
                    payload=data['payload'],
                    created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(timezone.utc)
                ))
            
            return events
        except Exception as e:
            logger.error(f"Error getting event logs: {e}")
            return []
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_org_stats(self, org_id: str) -> Dict[str, Any]:
        """Get statistics for an organization."""
        try:
            # Node count
            result = self.db.fetch_one(
                "SELECT COUNT(*) as count FROM ai_nodes WHERE org_id = ?",
                (org_id,)
            )
            node_count = result['count'] if result else 0
            
            # Task counts by status
            task_stats = self.db.fetch_all("""
                SELECT status, COUNT(*) as count 
                FROM ai_tasks WHERE org_id = ?
                GROUP BY status
            """, (org_id,))
            
            task_by_status = {row['status']: row['count'] for row in (task_stats or [])}
            
            # HITL actions count
            result = self.db.fetch_one(
                "SELECT COUNT(*) as count FROM ai_hitl_actions WHERE org_id = ?",
                (org_id,)
            )
            hitl_count = result['count'] if result else 0
            
            return {
                "node_count": node_count,
                "task_by_status": task_by_status,
                "total_tasks": sum(task_by_status.values()) if task_by_status else 0,
                "hitl_actions": hitl_count
            }
        except Exception as e:
            logger.error(f"Error getting org stats: {e}")
            return {}


# SQL Schema for AI Org tables
AIORG_SQLITE_SCHEMA = """
-- AI Organizations
CREATE TABLE IF NOT EXISTS ai_orgs (
    org_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'draft',
    config TEXT,
    event_bus_channel TEXT,
    created_by TEXT NOT NULL,
    created_at TEXT,
    updated_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_ai_orgs_status ON ai_orgs(status);
CREATE INDEX IF NOT EXISTS idx_ai_orgs_created_by ON ai_orgs(created_by);

-- AI Nodes
CREATE TABLE IF NOT EXISTS ai_nodes (
    node_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL REFERENCES ai_orgs(org_id),
    parent_node_id TEXT REFERENCES ai_nodes(node_id),
    role_name TEXT NOT NULL,
    role_type TEXT NOT NULL,
    description TEXT,
    agent_id TEXT,
    agent_config TEXT,
    human_name TEXT,
    human_email TEXT,
    human_teams_id TEXT,
    human_slack_id TEXT,
    hitl_enabled INTEGER DEFAULT 0,
    hitl_approval_required INTEGER DEFAULT 0,
    hitl_review_delegation INTEGER DEFAULT 0,
    hitl_timeout_hours INTEGER DEFAULT 24,
    hitl_auto_proceed INTEGER DEFAULT 1,
    notification_channels TEXT,
    notification_triggers TEXT,
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    current_task_id TEXT,
    created_at TEXT,
    updated_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_ai_nodes_org ON ai_nodes(org_id);
CREATE INDEX IF NOT EXISTS idx_ai_nodes_parent ON ai_nodes(parent_node_id);
CREATE INDEX IF NOT EXISTS idx_ai_nodes_email ON ai_nodes(human_email);

-- AI Tasks
CREATE TABLE IF NOT EXISTS ai_tasks (
    task_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL REFERENCES ai_orgs(org_id),
    parent_task_id TEXT REFERENCES ai_tasks(task_id),
    assigned_node_id TEXT NOT NULL REFERENCES ai_nodes(node_id),
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT DEFAULT 'medium',
    input_data TEXT,
    output_data TEXT,
    context TEXT,
    attachments TEXT,
    status TEXT DEFAULT 'pending',
    delegation_strategy TEXT,
    expected_responses INTEGER DEFAULT 0,
    received_responses INTEGER DEFAULT 0,
    deadline TEXT,
    started_at TEXT,
    completed_at TEXT,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_ai_tasks_org ON ai_tasks(org_id);
CREATE INDEX IF NOT EXISTS idx_ai_tasks_parent ON ai_tasks(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_ai_tasks_node ON ai_tasks(assigned_node_id);
CREATE INDEX IF NOT EXISTS idx_ai_tasks_status ON ai_tasks(status);

-- AI Responses
CREATE TABLE IF NOT EXISTS ai_responses (
    response_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES ai_tasks(task_id),
    node_id TEXT NOT NULL REFERENCES ai_nodes(node_id),
    response_type TEXT NOT NULL,
    content TEXT,
    summary TEXT,
    reasoning TEXT,
    confidence_score REAL,
    quality_score REAL,
    is_human_modified INTEGER DEFAULT 0,
    original_ai_content TEXT,
    modification_reason TEXT,
    modified_by TEXT,
    modified_at TEXT,
    created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_ai_responses_task ON ai_responses(task_id);
CREATE INDEX IF NOT EXISTS idx_ai_responses_node ON ai_responses(node_id);

-- AI HITL Actions
CREATE TABLE IF NOT EXISTS ai_hitl_actions (
    action_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL REFERENCES ai_orgs(org_id),
    node_id TEXT NOT NULL REFERENCES ai_nodes(node_id),
    task_id TEXT REFERENCES ai_tasks(task_id),
    response_id TEXT REFERENCES ai_responses(response_id),
    user_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    original_content TEXT,
    modified_content TEXT,
    reason TEXT,
    message TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_ai_hitl_org ON ai_hitl_actions(org_id);
CREATE INDEX IF NOT EXISTS idx_ai_hitl_node ON ai_hitl_actions(node_id);
CREATE INDEX IF NOT EXISTS idx_ai_hitl_user ON ai_hitl_actions(user_id);

-- AI Event Logs
CREATE TABLE IF NOT EXISTS ai_event_logs (
    event_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL REFERENCES ai_orgs(org_id),
    event_type TEXT NOT NULL,
    source_node_id TEXT,
    target_node_id TEXT,
    task_id TEXT,
    payload TEXT,
    created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_ai_events_org ON ai_event_logs(org_id);
CREATE INDEX IF NOT EXISTS idx_ai_events_type ON ai_event_logs(event_type);

-- HITL Queue
CREATE TABLE IF NOT EXISTS ai_hitl_queue (
    item_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    node_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    review_type TEXT NOT NULL,
    content TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT,
    expires_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_ai_hitl_queue_status ON ai_hitl_queue(status);
CREATE INDEX IF NOT EXISTS idx_ai_hitl_queue_node ON ai_hitl_queue(node_id);
"""


AIORG_POSTGRES_SCHEMA = """
-- AI Organizations
CREATE TABLE IF NOT EXISTS ai_orgs (
    org_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    config JSONB,
    event_bus_channel VARCHAR(100),
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ai_orgs_status ON ai_orgs(status);
CREATE INDEX IF NOT EXISTS idx_ai_orgs_created_by ON ai_orgs(created_by);

-- AI Nodes
CREATE TABLE IF NOT EXISTS ai_nodes (
    node_id VARCHAR(36) PRIMARY KEY,
    org_id VARCHAR(36) NOT NULL REFERENCES ai_orgs(org_id),
    parent_node_id VARCHAR(36) REFERENCES ai_nodes(node_id),
    role_name VARCHAR(100) NOT NULL,
    role_type VARCHAR(20) NOT NULL,
    description TEXT,
    agent_id VARCHAR(36),
    agent_config JSONB,
    human_name VARCHAR(255),
    human_email VARCHAR(255),
    human_teams_id VARCHAR(255),
    human_slack_id VARCHAR(255),
    hitl_enabled BOOLEAN DEFAULT FALSE,
    hitl_approval_required BOOLEAN DEFAULT FALSE,
    hitl_review_delegation BOOLEAN DEFAULT FALSE,
    hitl_timeout_hours INTEGER DEFAULT 24,
    hitl_auto_proceed BOOLEAN DEFAULT TRUE,
    notification_channels JSONB,
    notification_triggers JSONB,
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    current_task_id VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ai_nodes_org ON ai_nodes(org_id);
CREATE INDEX IF NOT EXISTS idx_ai_nodes_parent ON ai_nodes(parent_node_id);
CREATE INDEX IF NOT EXISTS idx_ai_nodes_email ON ai_nodes(human_email);

-- AI Tasks
CREATE TABLE IF NOT EXISTS ai_tasks (
    task_id VARCHAR(36) PRIMARY KEY,
    org_id VARCHAR(36) NOT NULL REFERENCES ai_orgs(org_id),
    parent_task_id VARCHAR(36) REFERENCES ai_tasks(task_id),
    assigned_node_id VARCHAR(36) NOT NULL REFERENCES ai_nodes(node_id),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'medium',
    input_data JSONB,
    output_data JSONB,
    context JSONB,
    attachments JSONB,
    status VARCHAR(30) DEFAULT 'pending',
    delegation_strategy VARCHAR(20),
    expected_responses INTEGER DEFAULT 0,
    received_responses INTEGER DEFAULT 0,
    deadline TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ai_tasks_org ON ai_tasks(org_id);
CREATE INDEX IF NOT EXISTS idx_ai_tasks_parent ON ai_tasks(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_ai_tasks_node ON ai_tasks(assigned_node_id);
CREATE INDEX IF NOT EXISTS idx_ai_tasks_status ON ai_tasks(status);

-- AI Responses
CREATE TABLE IF NOT EXISTS ai_responses (
    response_id VARCHAR(36) PRIMARY KEY,
    task_id VARCHAR(36) NOT NULL REFERENCES ai_tasks(task_id),
    node_id VARCHAR(36) NOT NULL REFERENCES ai_nodes(node_id),
    response_type VARCHAR(30) NOT NULL,
    content JSONB NOT NULL,
    summary TEXT,
    reasoning TEXT,
    confidence_score FLOAT,
    quality_score FLOAT,
    is_human_modified BOOLEAN DEFAULT FALSE,
    original_ai_content JSONB,
    modification_reason TEXT,
    modified_by VARCHAR(100),
    modified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ai_responses_task ON ai_responses(task_id);
CREATE INDEX IF NOT EXISTS idx_ai_responses_node ON ai_responses(node_id);

-- AI HITL Actions
CREATE TABLE IF NOT EXISTS ai_hitl_actions (
    action_id VARCHAR(36) PRIMARY KEY,
    org_id VARCHAR(36) NOT NULL REFERENCES ai_orgs(org_id),
    node_id VARCHAR(36) NOT NULL REFERENCES ai_nodes(node_id),
    task_id VARCHAR(36) REFERENCES ai_tasks(task_id),
    response_id VARCHAR(36) REFERENCES ai_responses(response_id),
    user_id VARCHAR(100) NOT NULL,
    action_type VARCHAR(30) NOT NULL,
    original_content JSONB,
    modified_content JSONB,
    reason TEXT,
    message TEXT,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ai_hitl_org ON ai_hitl_actions(org_id);
CREATE INDEX IF NOT EXISTS idx_ai_hitl_node ON ai_hitl_actions(node_id);
CREATE INDEX IF NOT EXISTS idx_ai_hitl_user ON ai_hitl_actions(user_id);

-- AI Event Logs
CREATE TABLE IF NOT EXISTS ai_event_logs (
    event_id VARCHAR(36) PRIMARY KEY,
    org_id VARCHAR(36) NOT NULL REFERENCES ai_orgs(org_id),
    event_type VARCHAR(50) NOT NULL,
    source_node_id VARCHAR(36),
    target_node_id VARCHAR(36),
    task_id VARCHAR(36),
    payload JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ai_events_org ON ai_event_logs(org_id);
CREATE INDEX IF NOT EXISTS idx_ai_events_type ON ai_event_logs(event_type);

-- HITL Queue
CREATE TABLE IF NOT EXISTS ai_hitl_queue (
    item_id VARCHAR(36) PRIMARY KEY,
    org_id VARCHAR(36) NOT NULL,
    node_id VARCHAR(36) NOT NULL,
    task_id VARCHAR(36) NOT NULL,
    review_type VARCHAR(30) NOT NULL,
    content JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ai_hitl_queue_status ON ai_hitl_queue(status);
CREATE INDEX IF NOT EXISTS idx_ai_hitl_queue_node ON ai_hitl_queue(node_id);
"""
