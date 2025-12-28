"""
Execution Delegate - Database operations for Executions and Execution Steps.

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


class ExecutionDelegate(DatabaseDelegate):
    """
    Delegate for execution-related database operations.
    
    Handles tables: executions, execution_steps
    """
    
    # =========================================================================
    # EXECUTIONS
    # =========================================================================
    
    def get_all_executions(self, user_id: str = None, agent_id: str = None,
                           status: str = None, limit: int = 100,
                           offset: int = 0) -> List[Dict]:
        """Get executions with optional filters."""
        query = """SELECT e.*, a.name as agent_name 
                   FROM executions e
                   LEFT JOIN agents a ON e.agent_id = a.agent_id"""
        conditions = []
        params = []
        
        if user_id:
            conditions.append("e.user_id = ?")
            params.append(user_id)
        if agent_id:
            conditions.append("e.agent_id = ?")
            params.append(agent_id)
        if status:
            conditions.append("e.status = ?")
            params.append(status)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += f" ORDER BY e.started_at DESC LIMIT {limit} OFFSET {offset}"
        return self.fetch_all(query, tuple(params) if params else None) or []
    
    def get_execution(self, execution_id: str) -> Optional[Dict]:
        """Get execution by ID with agent info."""
        return self.fetch_one(
            """SELECT e.*, a.name as agent_name 
               FROM executions e
               LEFT JOIN agents a ON e.agent_id = a.agent_id
               WHERE e.execution_id = ?""",
            (execution_id,)
        )
    
    def get_executions_count(self, user_id: str = None, agent_id: str = None,
                             status: str = None) -> int:
        """Get count of executions."""
        conditions = []
        params = []
        
        if user_id:
            conditions.append("user_id = ?")
            params.append(user_id)
        if agent_id:
            conditions.append("agent_id = ?")
            params.append(agent_id)
        if status:
            conditions.append("status = ?")
            params.append(status)
        
        where = " AND ".join(conditions) if conditions else None
        return self.get_count("executions", where, tuple(params) if params else None)
    
    def get_recent_executions(self, user_id: str = None, 
                              limit: int = 10) -> List[Dict]:
        """Get recent executions."""
        query = """SELECT e.*, a.name as agent_name 
                   FROM executions e
                   LEFT JOIN agents a ON e.agent_id = a.agent_id"""
        params = []
        
        if user_id:
            query += " WHERE e.user_id = ?"
            params.append(user_id)
        
        query += f" ORDER BY e.started_at DESC LIMIT {limit}"
        return self.fetch_all(query, tuple(params) if params else None) or []
    
    def create_execution(self, agent_id: str, user_id: str,
                         agent_version: str = None, status: str = 'pending',
                         input_data: str = None, execution_config: str = '{}',
                         trace_data: str = '[]') -> Optional[str]:
        """Create a new execution and return execution_id."""
        execution_id = str(uuid.uuid4())
        try:
            self.execute(
                """INSERT INTO executions 
                   (execution_id, agent_id, agent_version, user_id, status,
                    input_data, execution_config, trace_data)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (execution_id, agent_id, agent_version, user_id, status,
                 input_data, execution_config, trace_data)
            )
            return execution_id
        except Exception as e:
            logger.error(f"Error creating execution: {e}")
            return None
    
    def update_execution(self, execution_id: str, **kwargs) -> bool:
        """Update execution fields."""
        if not kwargs:
            return False
        
        valid_fields = ['status', 'output_data', 'error_message', 'completed_at',
                        'duration_ms', 'tokens_used', 'cost_estimate', 'trace_data']
        
        updates = []
        params = []
        for key, value in kwargs.items():
            if key in valid_fields:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if not updates:
            return False
        
        params.append(execution_id)
        query = f"UPDATE executions SET {', '.join(updates)} WHERE execution_id = ?"
        
        try:
            self.execute(query, tuple(params))
            return True
        except Exception as e:
            logger.error(f"Error updating execution: {e}")
            return False
    
    def start_execution(self, execution_id: str) -> bool:
        """Mark execution as running."""
        return self.update_execution(execution_id, status='running')
    
    def complete_execution(self, execution_id: str, output_data: str = None,
                           duration_ms: int = None, tokens_used: int = 0,
                           cost_estimate: float = 0.0) -> bool:
        """Mark execution as completed."""
        try:
            self.execute(
                """UPDATE executions 
                   SET status = 'completed', output_data = ?, 
                       completed_at = CURRENT_TIMESTAMP, duration_ms = ?,
                       tokens_used = ?, cost_estimate = ?
                   WHERE execution_id = ?""",
                (output_data, duration_ms, tokens_used, cost_estimate, execution_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error completing execution: {e}")
            return False
    
    def fail_execution(self, execution_id: str, error_message: str,
                       duration_ms: int = None) -> bool:
        """Mark execution as failed."""
        try:
            self.execute(
                """UPDATE executions 
                   SET status = 'failed', error_message = ?, 
                       completed_at = CURRENT_TIMESTAMP, duration_ms = ?
                   WHERE execution_id = ?""",
                (error_message, duration_ms, execution_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error failing execution: {e}")
            return False
    
    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel an execution."""
        try:
            self.execute(
                """UPDATE executions 
                   SET status = 'cancelled', completed_at = CURRENT_TIMESTAMP
                   WHERE execution_id = ?""",
                (execution_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error cancelling execution: {e}")
            return False
    
    def delete_execution(self, execution_id: str) -> bool:
        """Delete an execution and its steps."""
        try:
            self.execute(
                "DELETE FROM execution_steps WHERE execution_id = ?",
                (execution_id,)
            )
            self.execute(
                "DELETE FROM executions WHERE execution_id = ?",
                (execution_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting execution: {e}")
            return False
    
    def get_execution_stats(self, user_id: str = None,
                            days: int = 30) -> Dict[str, Any]:
        """Get execution statistics."""
        query = """SELECT 
                       COUNT(*) as total_executions,
                       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                       SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                       SUM(tokens_used) as total_tokens,
                       SUM(cost_estimate) as total_cost,
                       AVG(duration_ms) as avg_duration
                   FROM executions
                   WHERE started_at >= datetime('now', ?)"""
        
        params = [f'-{days} days']
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        result = self.fetch_one(query, tuple(params))
        return result or {}
    
    # =========================================================================
    # EXECUTION STEPS
    # =========================================================================
    
    def get_execution_steps(self, execution_id: str) -> List[Dict]:
        """Get all steps for an execution."""
        return self.fetch_all(
            """SELECT * FROM execution_steps 
               WHERE execution_id = ? 
               ORDER BY step_number""",
            (execution_id,)
        ) or []
    
    def get_step(self, execution_id: str, step_number: int) -> Optional[Dict]:
        """Get specific step by number."""
        return self.fetch_one(
            """SELECT * FROM execution_steps 
               WHERE execution_id = ? AND step_number = ?""",
            (execution_id, step_number)
        )
    
    def create_step(self, execution_id: str, step_number: int,
                    node_id: str = None, node_type: str = None,
                    status: str = 'pending', input_data: str = None) -> bool:
        """Create a new execution step."""
        try:
            self.execute(
                """INSERT INTO execution_steps 
                   (execution_id, step_number, node_id, node_type, status,
                    input_data, started_at)
                   VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                (execution_id, step_number, node_id, node_type, status, input_data)
            )
            return True
        except Exception as e:
            logger.error(f"Error creating step: {e}")
            return False
    
    def update_step(self, execution_id: str, step_number: int, **kwargs) -> bool:
        """Update step fields."""
        if not kwargs:
            return False
        
        valid_fields = ['status', 'output_data', 'error_message',
                        'completed_at', 'duration_ms']
        
        updates = []
        params = []
        for key, value in kwargs.items():
            if key in valid_fields:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if not updates:
            return False
        
        params.extend([execution_id, step_number])
        query = f"""UPDATE execution_steps 
                    SET {', '.join(updates)} 
                    WHERE execution_id = ? AND step_number = ?"""
        
        try:
            self.execute(query, tuple(params))
            return True
        except Exception as e:
            logger.error(f"Error updating step: {e}")
            return False
    
    def complete_step(self, execution_id: str, step_number: int,
                      output_data: str = None, duration_ms: int = None) -> bool:
        """Mark step as completed."""
        try:
            self.execute(
                """UPDATE execution_steps 
                   SET status = 'completed', output_data = ?, 
                       completed_at = CURRENT_TIMESTAMP, duration_ms = ?
                   WHERE execution_id = ? AND step_number = ?""",
                (output_data, duration_ms, execution_id, step_number)
            )
            return True
        except Exception as e:
            logger.error(f"Error completing step: {e}")
            return False
    
    def fail_step(self, execution_id: str, step_number: int,
                  error_message: str, duration_ms: int = None) -> bool:
        """Mark step as failed."""
        try:
            self.execute(
                """UPDATE execution_steps 
                   SET status = 'failed', error_message = ?, 
                       completed_at = CURRENT_TIMESTAMP, duration_ms = ?
                   WHERE execution_id = ? AND step_number = ?""",
                (error_message, duration_ms, execution_id, step_number)
            )
            return True
        except Exception as e:
            logger.error(f"Error failing step: {e}")
            return False
    
    def get_steps_count(self, execution_id: str) -> int:
        """Get count of steps in an execution."""
        return self.get_count("execution_steps", "execution_id = ?", (execution_id,))
    
    def delete_execution_steps(self, execution_id: str) -> bool:
        """Delete all steps for an execution."""
        try:
            self.execute(
                "DELETE FROM execution_steps WHERE execution_id = ?",
                (execution_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting execution steps: {e}")
            return False
