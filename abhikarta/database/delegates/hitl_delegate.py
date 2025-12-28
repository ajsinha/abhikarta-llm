"""
HITL Delegate - Database operations for HITL Tasks, Comments, Assignments.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Version: 1.2.1
"""

from typing import Any, Dict, List, Optional
import uuid
import json
import logging

from ..database_delegate import DatabaseDelegate

logger = logging.getLogger(__name__)


class HITLDelegate(DatabaseDelegate):
    """
    Delegate for HITL-related database operations.
    
    Handles tables: hitl_tasks, hitl_comments, hitl_assignments
    """
    
    # =========================================================================
    # HITL TASKS
    # =========================================================================
    
    def get_all_tasks(self, status: str = None, assigned_to: str = None,
                      task_type: str = None, limit: int = 100,
                      offset: int = 0) -> List[Dict]:
        """Get HITL tasks with optional filters."""
        query = """SELECT t.*, a.name as agent_name, u.fullname as assignee_name
                   FROM hitl_tasks t
                   LEFT JOIN agents a ON t.agent_id = a.agent_id
                   LEFT JOIN users u ON t.assigned_to = u.user_id"""
        conditions = []
        params = []
        
        if status:
            conditions.append("t.status = ?")
            params.append(status)
        if assigned_to:
            conditions.append("t.assigned_to = ?")
            params.append(assigned_to)
        if task_type:
            conditions.append("t.task_type = ?")
            params.append(task_type)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += f" ORDER BY t.priority, t.created_at DESC LIMIT {limit} OFFSET {offset}"
        return self.fetch_all(query, tuple(params) if params else None) or []
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get task by ID with related info."""
        return self.fetch_one(
            """SELECT t.*, a.name as agent_name, u.fullname as assignee_name,
                      c.fullname as creator_name
               FROM hitl_tasks t
               LEFT JOIN agents a ON t.agent_id = a.agent_id
               LEFT JOIN users u ON t.assigned_to = u.user_id
               LEFT JOIN users c ON t.created_by = c.user_id
               WHERE t.task_id = ?""",
            (task_id,)
        )
    
    def get_pending_tasks(self, assigned_to: str = None) -> List[Dict]:
        """Get pending tasks, optionally for a specific user."""
        query = """SELECT t.*, a.name as agent_name
                   FROM hitl_tasks t
                   LEFT JOIN agents a ON t.agent_id = a.agent_id
                   WHERE t.status = 'pending'"""
        params = []
        
        if assigned_to:
            query += " AND t.assigned_to = ?"
            params.append(assigned_to)
        
        query += " ORDER BY t.priority, t.created_at"
        return self.fetch_all(query, tuple(params) if params else None) or []
    
    def get_tasks_count(self, status: str = None, 
                        assigned_to: str = None) -> int:
        """Get count of tasks."""
        conditions = []
        params = []
        
        if status:
            conditions.append("status = ?")
            params.append(status)
        if assigned_to:
            conditions.append("assigned_to = ?")
            params.append(assigned_to)
        
        where = " AND ".join(conditions) if conditions else None
        return self.get_count("hitl_tasks", where, tuple(params) if params else None)
    
    def create_task(self, title: str, task_type: str = 'approval',
                    execution_id: str = None, workflow_id: str = None,
                    agent_id: str = None, node_id: str = None,
                    description: str = None, status: str = 'pending',
                    priority: int = 5, context: str = '{}',
                    request_data: str = None, input_schema: str = '{}',
                    assigned_to: str = None, due_at: str = None,
                    timeout_minutes: int = 1440, created_by: str = None,
                    tags: str = '[]', metadata: str = '{}') -> Optional[str]:
        """Create a new HITL task and return task_id."""
        task_id = str(uuid.uuid4())
        try:
            self.execute(
                """INSERT INTO hitl_tasks 
                   (task_id, execution_id, workflow_id, agent_id, node_id,
                    task_type, title, description, status, priority, context,
                    request_data, input_schema, assigned_to, due_at,
                    timeout_minutes, created_by, tags, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (task_id, execution_id, workflow_id, agent_id, node_id,
                 task_type, title, description, status, priority, context,
                 request_data, input_schema, assigned_to, due_at,
                 timeout_minutes, created_by, tags, metadata)
            )
            
            # Update assigned_at if assigned
            if assigned_to:
                self.execute(
                    "UPDATE hitl_tasks SET assigned_at = CURRENT_TIMESTAMP WHERE task_id = ?",
                    (task_id,)
                )
            
            return task_id
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """Update task fields."""
        if not kwargs:
            return False
        
        valid_fields = ['title', 'description', 'status', 'priority', 'context',
                        'request_data', 'response_data', 'resolution', 'assigned_to',
                        'due_at', 'tags', 'metadata']
        
        updates = []
        params = []
        for key, value in kwargs.items():
            if key in valid_fields:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if not updates:
            return False
        
        params.append(task_id)
        query = f"UPDATE hitl_tasks SET {', '.join(updates)} WHERE task_id = ?"
        
        try:
            self.execute(query, tuple(params))
            return True
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            return False
    
    def assign_task(self, task_id: str, assigned_to: str, 
                    assigned_by: str = None, reason: str = None) -> bool:
        """Assign task to a user."""
        try:
            # Get current assignee
            task = self.get_task(task_id)
            old_assignee = task.get('assigned_to') if task else None
            
            # Update task
            self.execute(
                """UPDATE hitl_tasks 
                   SET assigned_to = ?, assigned_at = CURRENT_TIMESTAMP
                   WHERE task_id = ?""",
                (assigned_to, task_id)
            )
            
            # Log assignment
            self.log_assignment(task_id, old_assignee, assigned_to, 
                               assigned_by, reason)
            return True
        except Exception as e:
            logger.error(f"Error assigning task: {e}")
            return False
    
    def complete_task(self, task_id: str, completed_by: str,
                      response_data: str = None, resolution: str = None) -> bool:
        """Complete a task."""
        try:
            self.execute(
                """UPDATE hitl_tasks 
                   SET status = 'completed', completed_at = CURRENT_TIMESTAMP,
                       completed_by = ?, response_data = ?, resolution = ?
                   WHERE task_id = ?""",
                (completed_by, response_data, resolution, task_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error completing task: {e}")
            return False
    
    def approve_task(self, task_id: str, approved_by: str,
                     response_data: str = None) -> bool:
        """Approve a task."""
        try:
            self.execute(
                """UPDATE hitl_tasks 
                   SET status = 'approved', completed_at = CURRENT_TIMESTAMP,
                       completed_by = ?, response_data = ?, resolution = 'approved'
                   WHERE task_id = ?""",
                (approved_by, response_data, task_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error approving task: {e}")
            return False
    
    def reject_task(self, task_id: str, rejected_by: str,
                    response_data: str = None, reason: str = None) -> bool:
        """Reject a task."""
        try:
            self.execute(
                """UPDATE hitl_tasks 
                   SET status = 'rejected', completed_at = CURRENT_TIMESTAMP,
                       completed_by = ?, response_data = ?, resolution = ?
                   WHERE task_id = ?""",
                (rejected_by, response_data, reason or 'rejected', task_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error rejecting task: {e}")
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task and related records."""
        try:
            self.execute(
                "DELETE FROM hitl_comments WHERE task_id = ?",
                (task_id,)
            )
            self.execute(
                "DELETE FROM hitl_assignments WHERE task_id = ?",
                (task_id,)
            )
            self.execute(
                "DELETE FROM hitl_tasks WHERE task_id = ?",
                (task_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            return False
    
    # =========================================================================
    # HITL COMMENTS
    # =========================================================================
    
    def get_task_comments(self, task_id: str) -> List[Dict]:
        """Get all comments for a task."""
        return self.fetch_all(
            """SELECT c.*, u.fullname as user_name
               FROM hitl_comments c
               LEFT JOIN users u ON c.user_id = u.user_id
               WHERE c.task_id = ?
               ORDER BY c.created_at""",
            (task_id,)
        ) or []
    
    def add_comment(self, task_id: str, user_id: str, comment: str,
                    comment_type: str = 'comment', attachments: str = '[]',
                    is_internal: int = 0) -> Optional[str]:
        """Add a comment to a task."""
        comment_id = str(uuid.uuid4())
        try:
            self.execute(
                """INSERT INTO hitl_comments 
                   (comment_id, task_id, user_id, comment, comment_type,
                    attachments, is_internal)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (comment_id, task_id, user_id, comment, comment_type,
                 attachments, is_internal)
            )
            return comment_id
        except Exception as e:
            logger.error(f"Error adding comment: {e}")
            return None
    
    def update_comment(self, comment_id: str, comment: str) -> bool:
        """Update a comment."""
        try:
            self.execute(
                """UPDATE hitl_comments 
                   SET comment = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE comment_id = ?""",
                (comment, comment_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error updating comment: {e}")
            return False
    
    def delete_comment(self, comment_id: str) -> bool:
        """Delete a comment."""
        try:
            self.execute(
                "DELETE FROM hitl_comments WHERE comment_id = ?",
                (comment_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting comment: {e}")
            return False
    
    # =========================================================================
    # HITL ASSIGNMENTS
    # =========================================================================
    
    def get_task_assignments(self, task_id: str) -> List[Dict]:
        """Get assignment history for a task."""
        return self.fetch_all(
            """SELECT a.*, 
                      u1.fullname as from_name,
                      u2.fullname as to_name,
                      u3.fullname as by_name
               FROM hitl_assignments a
               LEFT JOIN users u1 ON a.assigned_from = u1.user_id
               LEFT JOIN users u2 ON a.assigned_to = u2.user_id
               LEFT JOIN users u3 ON a.assigned_by = u3.user_id
               WHERE a.task_id = ?
               ORDER BY a.assigned_at DESC""",
            (task_id,)
        ) or []
    
    def log_assignment(self, task_id: str, assigned_from: str,
                       assigned_to: str, assigned_by: str,
                       reason: str = None) -> Optional[str]:
        """Log a task assignment."""
        assignment_id = str(uuid.uuid4())
        try:
            self.execute(
                """INSERT INTO hitl_assignments 
                   (assignment_id, task_id, assigned_from, assigned_to,
                    assigned_by, reason)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (assignment_id, task_id, assigned_from, assigned_to,
                 assigned_by, reason)
            )
            return assignment_id
        except Exception as e:
            logger.error(f"Error logging assignment: {e}")
            return None
