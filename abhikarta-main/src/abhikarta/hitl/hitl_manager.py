"""
HITL Manager - Human-in-the-Loop task management.

Provides functionality for:
- Creating HITL tasks during workflow/agent execution
- Assigning tasks to users
- Managing task lifecycle (pending -> in_progress -> approved/rejected)
- Adding comments and responses
- Tracking assignment history

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class HITLStatus(Enum):
    """HITL task status values."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class HITLTaskType(Enum):
    """HITL task types."""
    APPROVAL = "approval"           # Simple approve/reject
    DATA_INPUT = "data_input"       # Require user data input
    REVIEW = "review"               # Review and provide feedback
    DECISION = "decision"           # Make a decision from options
    ESCALATION = "escalation"       # Escalated issue
    VERIFICATION = "verification"   # Verify information


class HITLPriority(Enum):
    """HITL task priority levels."""
    CRITICAL = 1
    HIGH = 3
    MEDIUM = 5
    LOW = 7
    MINIMAL = 9


@dataclass
class HITLTask:
    """HITL task entity."""
    task_id: str
    title: str
    task_type: str = "approval"
    description: str = ""
    status: str = "pending"
    priority: int = 5
    execution_id: str = None
    workflow_id: str = None
    agent_id: str = None
    node_id: str = None
    context: Dict = field(default_factory=dict)
    request_data: Any = None
    input_schema: Dict = field(default_factory=dict)
    response_data: Any = None
    resolution: str = None
    assigned_to: str = None
    assigned_at: str = None
    due_at: str = None
    completed_at: str = None
    completed_by: str = None
    created_by: str = None
    created_at: str = None
    updated_at: str = None
    timeout_minutes: int = 1440
    tags: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HITLTask':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class HITLComment:
    """HITL comment entity."""
    comment_id: str
    task_id: str
    user_id: str
    comment: str
    comment_type: str = "comment"  # comment, system, status_change
    attachments: List = field(default_factory=list)
    is_internal: bool = False
    created_at: str = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HITLManager:
    """
    Manage Human-in-the-Loop tasks.
    
    Provides full lifecycle management for HITL tasks including:
    - Task creation and assignment
    - Status management
    - Comments and responses
    - Assignment history tracking
    """
    
    def __init__(self, db_facade):
        """
        Initialize HITL manager.
        
        Args:
            db_facade: Database facade instance
        """
        self.db_facade = db_facade
    
    # =========================================================================
    # TASK CREATION
    # =========================================================================
    
    def create_task(self, title: str, task_type: str = "approval",
                   description: str = "", priority: int = 5,
                   execution_id: str = None, workflow_id: str = None,
                   agent_id: str = None, node_id: str = None,
                   context: Dict = None, request_data: Any = None,
                   input_schema: Dict = None, assigned_to: str = None,
                   due_at: datetime = None, timeout_minutes: int = 1440,
                   created_by: str = None, tags: List[str] = None,
                   metadata: Dict = None) -> HITLTask:
        """
        Create a new HITL task.
        
        Args:
            title: Task title
            task_type: Type of task (approval, data_input, review, etc.)
            description: Detailed description
            priority: Priority level (1-10, 1 is highest)
            execution_id: Associated execution ID
            workflow_id: Associated workflow ID
            agent_id: Associated agent ID
            node_id: Node that triggered HITL
            context: Context data from execution
            request_data: Data requiring human review
            input_schema: JSON Schema for required input
            assigned_to: User to assign to
            due_at: Due date/time
            timeout_minutes: Minutes until expiry
            created_by: User creating the task
            tags: List of tags
            metadata: Additional metadata
            
        Returns:
            Created HITLTask
        """
        task_id = f"hitl_{uuid.uuid4().hex[:16]}"
        now = datetime.now(timezone.utc)
        
        # Calculate due_at if not specified
        if not due_at and timeout_minutes:
            due_at = now + timedelta(minutes=timeout_minutes)
        
        status = "assigned" if assigned_to else "pending"
        
        task = HITLTask(
            task_id=task_id,
            title=title,
            task_type=task_type,
            description=description,
            status=status,
            priority=priority,
            execution_id=execution_id,
            workflow_id=workflow_id,
            agent_id=agent_id,
            node_id=node_id,
            context=context or {},
            request_data=request_data,
            input_schema=input_schema or {},
            assigned_to=assigned_to,
            assigned_at=now.isoformat() if assigned_to else None,
            due_at=due_at.isoformat() if due_at else None,
            created_by=created_by,
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
            timeout_minutes=timeout_minutes,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # Save to database
        self._save_task(task)
        
        # Log assignment if assigned
        if assigned_to:
            self._log_assignment(task_id, None, assigned_to, created_by or 'system',
                               "Initial assignment")
        
        # Add system comment
        self.add_comment(task_id, 'system', f"Task created: {title}", 
                        comment_type='system')
        
        logger.info(f"Created HITL task: {task_id} - {title}")
        
        return task
    
    def _save_task(self, task: HITLTask):
        """Save task to database."""
        self.db_facade.execute(
            """INSERT INTO hitl_tasks 
               (task_id, title, task_type, description, status, priority,
                execution_id, workflow_id, agent_id, node_id, context,
                request_data, input_schema, response_data, resolution,
                assigned_to, assigned_at, due_at, completed_at, completed_by,
                created_by, created_at, updated_at, timeout_minutes, tags, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                task.task_id, task.title, task.task_type, task.description,
                task.status, task.priority, task.execution_id, task.workflow_id,
                task.agent_id, task.node_id,
                json.dumps(task.context), json.dumps(task.request_data),
                json.dumps(task.input_schema), json.dumps(task.response_data),
                task.resolution, task.assigned_to, task.assigned_at,
                task.due_at, task.completed_at, task.completed_by,
                task.created_by, task.created_at, task.updated_at,
                task.timeout_minutes, json.dumps(task.tags), json.dumps(task.metadata)
            )
        )
    
    # =========================================================================
    # TASK RETRIEVAL
    # =========================================================================
    
    def get_task(self, task_id: str) -> Optional[HITLTask]:
        """Get a task by ID."""
        row = self.db_facade.fetch_one(
            "SELECT * FROM hitl_tasks WHERE task_id = ?",
            (task_id,)
        )
        return self._row_to_task(row) if row else None
    
    def get_user_tasks(self, user_id: str, status: str = None,
                      include_unassigned: bool = False) -> List[HITLTask]:
        """
        Get tasks assigned to a user.
        
        Args:
            user_id: User ID
            status: Optional status filter
            include_unassigned: Include unassigned tasks (for reviewers)
            
        Returns:
            List of HITLTask objects
        """
        if include_unassigned:
            if status:
                rows = self.db_facade.fetch_all(
                    """SELECT * FROM hitl_tasks 
                       WHERE (assigned_to = ? OR assigned_to IS NULL) AND status = ?
                       ORDER BY priority ASC, created_at DESC""",
                    (user_id, status)
                )
            else:
                rows = self.db_facade.fetch_all(
                    """SELECT * FROM hitl_tasks 
                       WHERE (assigned_to = ? OR assigned_to IS NULL)
                         AND status NOT IN ('approved', 'rejected', 'cancelled', 'expired')
                       ORDER BY priority ASC, created_at DESC""",
                    (user_id,)
                )
        else:
            if status:
                rows = self.db_facade.fetch_all(
                    """SELECT * FROM hitl_tasks 
                       WHERE assigned_to = ? AND status = ?
                       ORDER BY priority ASC, created_at DESC""",
                    (user_id, status)
                )
            else:
                rows = self.db_facade.fetch_all(
                    """SELECT * FROM hitl_tasks 
                       WHERE assigned_to = ?
                         AND status NOT IN ('approved', 'rejected', 'cancelled', 'expired')
                       ORDER BY priority ASC, created_at DESC""",
                    (user_id,)
                )
        
        return [self._row_to_task(row) for row in (rows or [])]
    
    def get_all_tasks(self, status: str = None, limit: int = 100,
                     offset: int = 0) -> List[HITLTask]:
        """Get all tasks with optional filtering."""
        if status:
            rows = self.db_facade.fetch_all(
                """SELECT * FROM hitl_tasks WHERE status = ?
                   ORDER BY priority ASC, created_at DESC
                   LIMIT ? OFFSET ?""",
                (status, limit, offset)
            )
        else:
            rows = self.db_facade.fetch_all(
                """SELECT * FROM hitl_tasks 
                   ORDER BY priority ASC, created_at DESC
                   LIMIT ? OFFSET ?""",
                (limit, offset)
            )
        
        return [self._row_to_task(row) for row in (rows or [])]
    
    def get_pending_tasks(self, limit: int = 50) -> List[HITLTask]:
        """Get pending/unassigned tasks."""
        rows = self.db_facade.fetch_all(
            """SELECT * FROM hitl_tasks 
               WHERE status IN ('pending', 'assigned')
               ORDER BY priority ASC, created_at DESC
               LIMIT ?""",
            (limit,)
        )
        return [self._row_to_task(row) for row in (rows or [])]
    
    def get_overdue_tasks(self) -> List[HITLTask]:
        """Get overdue tasks."""
        now = datetime.now(timezone.utc).isoformat()
        rows = self.db_facade.fetch_all(
            """SELECT * FROM hitl_tasks 
               WHERE status IN ('pending', 'assigned', 'in_progress')
                 AND due_at < ?
               ORDER BY due_at ASC""",
            (now,)
        )
        return [self._row_to_task(row) for row in (rows or [])]
    
    def _row_to_task(self, row: Dict) -> HITLTask:
        """Convert database row to HITLTask."""
        if not row:
            return None
        
        row = dict(row)
        
        # Parse JSON fields
        for field in ['context', 'request_data', 'input_schema', 'response_data', 
                     'tags', 'metadata']:
            if field in row and row[field]:
                try:
                    row[field] = json.loads(row[field])
                except:
                    row[field] = {} if field != 'tags' else []
        
        return HITLTask.from_dict(row)
    
    # =========================================================================
    # TASK ASSIGNMENT
    # =========================================================================
    
    def assign_task(self, task_id: str, user_id: str, 
                   assigned_by: str, reason: str = None) -> bool:
        """
        Assign a task to a user.
        
        Args:
            task_id: Task ID
            user_id: User to assign to
            assigned_by: User making the assignment
            reason: Optional reason for assignment
            
        Returns:
            True if successful
        """
        task = self.get_task(task_id)
        if not task:
            return False
        
        old_assignee = task.assigned_to
        now = datetime.now(timezone.utc)
        
        # Update task
        self.db_facade.execute(
            """UPDATE hitl_tasks SET
               assigned_to = ?, assigned_at = ?, status = 'assigned', updated_at = ?
               WHERE task_id = ?""",
            (user_id, now.isoformat(), now.isoformat(), task_id)
        )
        
        # Log assignment
        self._log_assignment(task_id, old_assignee, user_id, assigned_by, reason)
        
        # Add comment
        msg = f"Task assigned to {user_id}"
        if reason:
            msg += f": {reason}"
        self.add_comment(task_id, assigned_by, msg, comment_type='system')
        
        logger.info(f"Assigned task {task_id} to {user_id}")
        return True
    
    def unassign_task(self, task_id: str, unassigned_by: str, 
                     reason: str = None) -> bool:
        """Unassign a task."""
        task = self.get_task(task_id)
        if not task:
            return False
        
        now = datetime.now(timezone.utc)
        
        self.db_facade.execute(
            """UPDATE hitl_tasks SET
               assigned_to = NULL, status = 'pending', updated_at = ?
               WHERE task_id = ?""",
            (now.isoformat(), task_id)
        )
        
        msg = "Task unassigned"
        if reason:
            msg += f": {reason}"
        self.add_comment(task_id, unassigned_by, msg, comment_type='system')
        
        return True
    
    def _log_assignment(self, task_id: str, from_user: str, to_user: str,
                       assigned_by: str, reason: str = None):
        """Log assignment change."""
        assignment_id = f"asgn_{uuid.uuid4().hex[:12]}"
        
        self.db_facade.execute(
            """INSERT INTO hitl_assignments
               (assignment_id, task_id, assigned_from, assigned_to, assigned_by, reason)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (assignment_id, task_id, from_user, to_user, assigned_by, reason)
        )
    
    # =========================================================================
    # TASK RESOLUTION
    # =========================================================================
    
    def start_task(self, task_id: str, user_id: str) -> bool:
        """Mark task as in progress."""
        now = datetime.now(timezone.utc)
        
        self.db_facade.execute(
            """UPDATE hitl_tasks SET status = 'in_progress', updated_at = ?
               WHERE task_id = ? AND assigned_to = ?""",
            (now.isoformat(), task_id, user_id)
        )
        
        self.add_comment(task_id, user_id, "Started working on task", 
                        comment_type='system')
        return True
    
    def approve_task(self, task_id: str, user_id: str,
                    response_data: Any = None, comment: str = None) -> bool:
        """
        Approve a task.
        
        Args:
            task_id: Task ID
            user_id: User approving
            response_data: Optional response/input data
            comment: Optional comment
            
        Returns:
            True if successful
        """
        return self._resolve_task(task_id, user_id, 'approved', response_data, comment)
    
    def reject_task(self, task_id: str, user_id: str,
                   response_data: Any = None, comment: str = None) -> bool:
        """
        Reject a task.
        
        Args:
            task_id: Task ID
            user_id: User rejecting
            response_data: Optional response/input data
            comment: Optional comment explaining rejection
            
        Returns:
            True if successful
        """
        return self._resolve_task(task_id, user_id, 'rejected', response_data, comment)
    
    def _resolve_task(self, task_id: str, user_id: str, resolution: str,
                     response_data: Any = None, comment: str = None) -> bool:
        """Resolve a task with approval or rejection."""
        task = self.get_task(task_id)
        if not task:
            return False
        
        now = datetime.now(timezone.utc)
        
        self.db_facade.execute(
            """UPDATE hitl_tasks SET
               status = ?, resolution = ?, response_data = ?,
               completed_at = ?, completed_by = ?, updated_at = ?
               WHERE task_id = ?""",
            (
                resolution, resolution, json.dumps(response_data),
                now.isoformat(), user_id, now.isoformat(), task_id
            )
        )
        
        # Add resolution comment
        msg = f"Task {resolution}"
        if comment:
            msg += f": {comment}"
        self.add_comment(task_id, user_id, msg, comment_type='status_change')
        
        logger.info(f"Task {task_id} {resolution} by {user_id}")
        
        # Update execution if linked
        if task.execution_id:
            self._update_execution_hitl_status(task.execution_id, resolution)
        
        return True
    
    def cancel_task(self, task_id: str, cancelled_by: str, 
                   reason: str = None) -> bool:
        """Cancel a task."""
        now = datetime.now(timezone.utc)
        
        self.db_facade.execute(
            """UPDATE hitl_tasks SET
               status = 'cancelled', resolution = 'cancelled',
               completed_at = ?, completed_by = ?, updated_at = ?
               WHERE task_id = ?""",
            (now.isoformat(), cancelled_by, now.isoformat(), task_id)
        )
        
        msg = "Task cancelled"
        if reason:
            msg += f": {reason}"
        self.add_comment(task_id, cancelled_by, msg, comment_type='system')
        
        return True
    
    def _update_execution_hitl_status(self, execution_id: str, resolution: str):
        """Update linked execution with HITL resolution."""
        try:
            status = 'completed' if resolution == 'approved' else 'failed'
            self.db_facade.execute(
                """UPDATE executions SET 
                   status = ?, metadata = json_set(COALESCE(metadata, '{}'), '$.hitl_resolution', ?)
                   WHERE execution_id = ? AND status = 'waiting_for_human'""",
                (status, resolution, execution_id)
            )
        except Exception as e:
            logger.warning(f"Failed to update execution HITL status: {e}")
    
    # =========================================================================
    # COMMENTS
    # =========================================================================
    
    def add_comment(self, task_id: str, user_id: str, comment: str,
                   comment_type: str = "comment", is_internal: bool = False,
                   attachments: List = None) -> HITLComment:
        """
        Add a comment to a task.
        
        Args:
            task_id: Task ID
            user_id: User adding comment
            comment: Comment text
            comment_type: Type (comment, system, status_change)
            is_internal: Whether comment is internal only
            attachments: Optional attachments
            
        Returns:
            Created HITLComment
        """
        comment_id = f"cmt_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)
        
        hitl_comment = HITLComment(
            comment_id=comment_id,
            task_id=task_id,
            user_id=user_id,
            comment=comment,
            comment_type=comment_type,
            attachments=attachments or [],
            is_internal=is_internal,
            created_at=now.isoformat()
        )
        
        self.db_facade.execute(
            """INSERT INTO hitl_comments
               (comment_id, task_id, user_id, comment, comment_type, 
                attachments, is_internal, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                comment_id, task_id, user_id, comment, comment_type,
                json.dumps(attachments or []), 1 if is_internal else 0,
                now.isoformat()
            )
        )
        
        # Update task timestamp
        self.db_facade.execute(
            "UPDATE hitl_tasks SET updated_at = ? WHERE task_id = ?",
            (now.isoformat(), task_id)
        )
        
        return hitl_comment
    
    def get_comments(self, task_id: str, include_internal: bool = False) -> List[HITLComment]:
        """Get comments for a task."""
        if include_internal:
            rows = self.db_facade.fetch_all(
                """SELECT * FROM hitl_comments 
                   WHERE task_id = ? 
                   ORDER BY created_at ASC""",
                (task_id,)
            )
        else:
            rows = self.db_facade.fetch_all(
                """SELECT * FROM hitl_comments 
                   WHERE task_id = ? AND is_internal = 0
                   ORDER BY created_at ASC""",
                (task_id,)
            )
        
        comments = []
        for row in (rows or []):
            row = dict(row)
            if row.get('attachments'):
                try:
                    row['attachments'] = json.loads(row['attachments'])
                except:
                    row['attachments'] = []
            row['is_internal'] = bool(row.get('is_internal'))
            comments.append(HITLComment(**{k: v for k, v in row.items() 
                                          if k in HITLComment.__dataclass_fields__}))
        
        return comments
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get HITL statistics."""
        if user_id:
            pending = self.db_facade.fetch_one(
                "SELECT COUNT(*) as cnt FROM hitl_tasks WHERE assigned_to = ? AND status IN ('pending', 'assigned')",
                (user_id,)
            )
            in_progress = self.db_facade.fetch_one(
                "SELECT COUNT(*) as cnt FROM hitl_tasks WHERE assigned_to = ? AND status = 'in_progress'",
                (user_id,)
            )
            completed = self.db_facade.fetch_one(
                "SELECT COUNT(*) as cnt FROM hitl_tasks WHERE completed_by = ? AND status IN ('approved', 'rejected')",
                (user_id,)
            )
        else:
            pending = self.db_facade.fetch_one(
                "SELECT COUNT(*) as cnt FROM hitl_tasks WHERE status IN ('pending', 'assigned')"
            )
            in_progress = self.db_facade.fetch_one(
                "SELECT COUNT(*) as cnt FROM hitl_tasks WHERE status = 'in_progress'"
            )
            completed = self.db_facade.fetch_one(
                "SELECT COUNT(*) as cnt FROM hitl_tasks WHERE status IN ('approved', 'rejected')"
            )
        
        overdue = self.db_facade.fetch_one(
            """SELECT COUNT(*) as cnt FROM hitl_tasks 
               WHERE status IN ('pending', 'assigned', 'in_progress')
                 AND due_at < ?""",
            (datetime.now(timezone.utc).isoformat(),)
        )
        
        return {
            'pending': pending['cnt'] if pending else 0,
            'in_progress': in_progress['cnt'] if in_progress else 0,
            'completed': completed['cnt'] if completed else 0,
            'overdue': overdue['cnt'] if overdue else 0
        }
    
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    def expire_overdue_tasks(self) -> int:
        """Mark overdue tasks as expired. Returns count of expired tasks."""
        now = datetime.now(timezone.utc)
        
        result = self.db_facade.execute(
            """UPDATE hitl_tasks SET
               status = 'expired', resolution = 'expired', updated_at = ?
               WHERE status IN ('pending', 'assigned')
                 AND due_at < ?""",
            (now.isoformat(), now.isoformat())
        )
        
        # Get count would depend on db facade implementation
        return 0


# Convenience function for creating HITL tasks from workflow/agent execution
def create_hitl_from_execution(db_facade, execution_id: str, agent_id: str = None,
                               workflow_id: str = None, node_id: str = None,
                               title: str = "Human Review Required",
                               description: str = "", task_type: str = "approval",
                               request_data: Any = None, context: Dict = None,
                               assigned_to: str = None, priority: int = 5,
                               created_by: str = "system") -> HITLTask:
    """
    Create a HITL task from an execution.
    
    This is called by workflow/agent executors when they encounter a HITL node.
    """
    manager = HITLManager(db_facade)
    
    return manager.create_task(
        title=title,
        task_type=task_type,
        description=description,
        priority=priority,
        execution_id=execution_id,
        workflow_id=workflow_id,
        agent_id=agent_id,
        node_id=node_id,
        context=context,
        request_data=request_data,
        assigned_to=assigned_to,
        created_by=created_by
    )
