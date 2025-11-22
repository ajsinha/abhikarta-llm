"""
Workflow Database Handler

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha | Email: ajsinha@gmail.com

Legal Notice: This module and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited without explicit 
written permission from the copyright holder.

Patent Pending: Certain architectural patterns and implementations described in this module 
may be subject to patent applications.
"""

from contextlib import contextmanager
from db_management.pool_manager import get_pool_manager
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import logging
import traceback
from db_management.db_aware import DBAware

from workflow_management.models.workflow_models import (
    Workflow, WorkflowExecution, NodeExecution, HumanTask,
    WorkflowVariable, AuditLog
)

logger = logging.getLogger(__name__)


def _parse_datetime(value: Any) -> Optional[datetime]:
    """
    Parse a datetime value from database, handling both datetime objects and strings.
    
    Args:
        value: Value from database (could be datetime, string, or None)
        
    Returns:
        datetime object or None
    """
    if value is None:
        return None
    
    # Already a datetime object
    if isinstance(value, datetime):
        return value
    
    # Parse string
    if isinstance(value, str):
        # Try common datetime formats
        for fmt in [
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d'
        ]:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        
        # If all parsing fails, log and return None
        logger.warning(f"Could not parse datetime string: {value}")
    
    return None


class WorkflowDBHandler(DBAware):
    """Database handler for workflow operations"""

    def __init__(self, db_connection_pool_name: str):
        """
        Initialize the workflow database handler.

        Args:
            db_connection_pool_name: Database connection pool name
        """
        DBAware.__init__(self, db_connection_pool_name)




    # ===================== Workflow Operations =====================

    def create_workflow(self, workflow: Workflow) -> bool:
        """Create a new workflow"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        INSERT INTO wf_workflows 
                        (workflow_id, name, description, version, definition_json, 
                         status, created_by, created_at, updated_at, tags)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        workflow.workflow_id,
                        workflow.name,
                        workflow.description,
                        workflow.version,
                        json.dumps(workflow.definition_json),
                        workflow.status,
                        workflow.created_by,
                        workflow.created_at,
                        workflow.updated_at,
                        json.dumps(workflow.tags) if workflow.tags else None
                    ))
                    logger.info(f"Created workflow: {workflow.workflow_id}")
                    return True
        except Exception as e:
            logger.error(f"Error creating workflow: {e}\n{traceback.format_exc()}")
            return False

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow by ID"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        SELECT workflow_id, name, description, version, definition_json,
                               status, created_by, created_at, updated_at, tags
                        FROM wf_workflows
                        WHERE workflow_id = ?
                    """, (workflow_id,))
                    
                    row = cursor.fetchone()
                    if row:
                        return Workflow(
                            workflow_id=row[0],
                            name=row[1],
                            description=row[2],
                            version=row[3],
                            definition_json=json.loads(row[4]),
                            status=row[5],
                            created_by=row[6],
                            created_at=_parse_datetime(row[7]),
                            updated_at=_parse_datetime(row[8]),
                            tags=json.loads(row[9]) if row[9] else None
                        )
                    return None
        except Exception as e:
            logger.error(f"Error getting workflow: {e}\n{traceback.format_exc()}")
            return None

    def list_workflows(self, status: Optional[str] = None, 
                      created_by: Optional[str] = None,
                      limit: int = 100, offset: int = 0) -> List[Workflow]:
        """List workflows with optional filters"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    query = """
                        SELECT workflow_id, name, description, version, definition_json,
                               status, created_by, created_at, updated_at, tags
                        FROM wf_workflows
                        WHERE 1=1
                    """
                    params = []
                    
                    if status:
                        query += " AND status = ?"
                        params.append(status)
                    
                    if created_by:
                        query += " AND created_by = ?"
                        params.append(created_by)
                    
                    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
                    params.extend([limit, offset])
                    
                    cursor.execute(query, params)
                    
                    workflows = []
                    for row in cursor.fetchall():
                        workflows.append(Workflow(
                            workflow_id=row[0],
                            name=row[1],
                            description=row[2],
                            version=row[3],
                            definition_json=json.loads(row[4]),
                            status=row[5],
                            created_by=row[6],
                            created_at=_parse_datetime(row[7]),
                            updated_at=_parse_datetime(row[8]),
                            tags=json.loads(row[9]) if row[9] else None
                        ))
                    return workflows
        except Exception as e:
            logger.error(f"Error listing workflows: {e}\n{traceback.format_exc()}")
            return []

    def update_workflow(self, workflow: Workflow) -> bool:
        """Update an existing workflow"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        UPDATE wf_workflows
                        SET description = ?, definition_json = ?, status = ?,
                            tags = ?, updated_at = ?
                        WHERE workflow_id = ?
                    """, (
                        workflow.description,
                        json.dumps(workflow.definition_json),
                        workflow.status,
                        json.dumps(workflow.tags) if workflow.tags else None,
                        datetime.now(),
                        workflow.workflow_id
                    ))
                    logger.info(f"Updated workflow: {workflow.workflow_id}")
                    return True
        except Exception as e:
            logger.error(f"Error updating workflow: {e}\n{traceback.format_exc()}")
            return False

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("DELETE FROM wf_workflows WHERE workflow_id = ?", 
                                 (workflow_id,))
                    logger.info(f"Deleted workflow: {workflow_id}")
                    return True
        except Exception as e:
            logger.error(f"Error deleting workflow: {e}\n{traceback.format_exc()}")
            return False

    # ===================== Execution Operations =====================

    def create_execution(self, execution: WorkflowExecution) -> bool:
        """Create a new workflow execution"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        INSERT INTO wf_executions
                        (execution_id, workflow_id, workflow_version, status,
                         started_at, completed_at, triggered_by, input_parameters,
                         output_results, error_message, execution_metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        execution.execution_id,
                        execution.workflow_id,
                        execution.workflow_version,
                        execution.status,
                        execution.started_at,
                        execution.completed_at,
                        execution.triggered_by,
                        json.dumps(execution.input_parameters) if execution.input_parameters else None,
                        json.dumps(execution.output_results) if execution.output_results else None,
                        execution.error_message,
                        json.dumps(execution.execution_metadata) if execution.execution_metadata else None
                    ))
                    logger.info(f"Created execution: {execution.execution_id}")
                    return True
        except Exception as e:
            logger.error(f"Error creating execution: {e}\n{traceback.format_exc()}")
            return False

    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get an execution by ID"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        SELECT execution_id, workflow_id, workflow_version, status,
                               started_at, completed_at, triggered_by, input_parameters,
                               output_results, error_message, execution_metadata
                        FROM wf_executions
                        WHERE execution_id = ?
                    """, (execution_id,))
                    
                    row = cursor.fetchone()
                    if row:
                        return WorkflowExecution(
                            execution_id=row[0],
                            workflow_id=row[1],
                            workflow_version=row[2],
                            status=row[3],
                            started_at=_parse_datetime(row[4]),
                            completed_at=_parse_datetime(row[5]),
                            triggered_by=row[6],
                            input_parameters=json.loads(row[7]) if row[7] else None,
                            output_results=json.loads(row[8]) if row[8] else None,
                            error_message=row[9],
                            execution_metadata=json.loads(row[10]) if row[10] else None
                        )
                    return None
        except Exception as e:
            logger.error(f"Error getting execution: {e}\n{traceback.format_exc()}")
            return None

    def update_execution_status(self, execution_id: str, status: str,
                               completed_at: Optional[datetime] = None,
                               error_message: Optional[str] = None,
                               output_results: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update execution status (DEPRECATED - use specific update methods instead).
        
        Kept for backward compatibility. Use:
        - set_execution_started() to mark execution as started
        - set_execution_completed() to mark as completed
        - set_execution_failed() to mark as failed
        """
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        UPDATE wf_executions
                        SET status = ?, completed_at = ?, error_message = ?,
                            output_results = ?
                        WHERE execution_id = ?
                    """, (
                        status,
                        completed_at,
                        error_message,
                        json.dumps(output_results) if output_results else None,
                        execution_id
                    ))
                    logger.info(f"Updated execution status: {execution_id} -> {status}")
                    return True
        except Exception as e:
            logger.error(f"Error updating execution status: {e}\n{traceback.format_exc()}")
            return False

    def set_execution_started(self, execution_id: str) -> bool:
        """Mark execution as started with current timestamp"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        UPDATE wf_executions
                        SET status = 'running', started_at = ?
                        WHERE execution_id = ?
                    """, (datetime.now(), execution_id))
                    logger.info(f"Execution started: {execution_id}")
                    return True
        except Exception as e:
            logger.error(f"Error setting execution started: {e}\n{traceback.format_exc()}")
            return False

    def set_execution_completed(self, execution_id: str, 
                                output_results: Optional[Dict[str, Any]] = None) -> bool:
        """Mark execution as completed with current timestamp"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        UPDATE wf_executions
                        SET status = 'completed', completed_at = ?, output_results = ?
                        WHERE execution_id = ?
                    """, (
                        datetime.now(),
                        json.dumps(output_results) if output_results else None,
                        execution_id
                    ))
                    logger.info(f"Execution completed: {execution_id}")
                    return True
        except Exception as e:
            logger.error(f"Error setting execution completed: {e}\n{traceback.format_exc()}")
            return False

    def set_execution_failed(self, execution_id: str, error_message: str) -> bool:
        """Mark execution as failed with error message and timestamp"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        UPDATE wf_executions
                        SET status = 'failed', completed_at = ?, error_message = ?
                        WHERE execution_id = ?
                    """, (datetime.now(), error_message, execution_id))
                    logger.info(f"Execution failed: {execution_id}")
                    return True
        except Exception as e:
            logger.error(f"Error setting execution failed: {e}\n{traceback.format_exc()}")
            return False

    def set_execution_paused(self, execution_id: str) -> bool:
        """Mark execution as paused"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        UPDATE wf_executions
                        SET status = 'paused'
                        WHERE execution_id = ?
                    """, (execution_id,))
                    logger.info(f"Execution paused: {execution_id}")
                    return True
        except Exception as e:
            logger.error(f"Error setting execution paused: {e}\n{traceback.format_exc()}")
            return False

    def set_execution_cancelled(self, execution_id: str) -> bool:
        """Mark execution as cancelled with timestamp"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        UPDATE wf_executions
                        SET status = 'cancelled', completed_at = ?
                        WHERE execution_id = ?
                    """, (datetime.now(), execution_id))
                    logger.info(f"Execution cancelled: {execution_id}")
                    return True
        except Exception as e:
            logger.error(f"Error setting execution cancelled: {e}\n{traceback.format_exc()}")
            return False

    def list_executions(self, workflow_id: Optional[str] = None,
                       status: Optional[str] = None,
                       triggered_by: Optional[str] = None,
                       limit: int = 100, offset: int = 0) -> List[WorkflowExecution]:
        """List workflow executions with optional filters"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    query = """
                        SELECT execution_id, workflow_id, workflow_version, status,
                               started_at, completed_at, triggered_by, input_parameters,
                               output_results, error_message, execution_metadata
                        FROM wf_executions
                        WHERE 1=1
                    """
                    params = []
                    
                    if workflow_id:
                        query += " AND workflow_id = ?"
                        params.append(workflow_id)
                    
                    if status:
                        query += " AND status = ?"
                        params.append(status)
                    
                    if triggered_by:
                        query += " AND triggered_by = ?"
                        params.append(triggered_by)
                    
                    query += " ORDER BY started_at DESC LIMIT ? OFFSET ?"
                    params.extend([limit, offset])
                    
                    cursor.execute(query, params)
                    
                    executions = []
                    for row in cursor.fetchall():
                        executions.append(WorkflowExecution(
                            execution_id=row[0],
                            workflow_id=row[1],
                            workflow_version=row[2],
                            status=row[3],
                            started_at=_parse_datetime(row[4]),
                            completed_at=_parse_datetime(row[5]),
                            triggered_by=row[6],
                            input_parameters=json.loads(row[7]) if row[7] else None,
                            output_results=json.loads(row[8]) if row[8] else None,
                            error_message=row[9],
                            execution_metadata=json.loads(row[10]) if row[10] else None
                        ))
                    return executions
        except Exception as e:
            logger.error(f"Error listing executions: {e}\n{traceback.format_exc()}")
            return []

    # ===================== Node Execution Operations =====================

    def create_node_execution(self, node_execution: NodeExecution) -> bool:
        """Create a new node execution"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        INSERT INTO wf_node_executions
                        (node_execution_id, execution_id, node_id, node_type, status,
                         started_at, completed_at, duration_ms, input_data, output_data,
                         error_details, retry_count, iteration_index)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        node_execution.node_execution_id,
                        node_execution.execution_id,
                        node_execution.node_id,
                        node_execution.node_type,
                        node_execution.status,
                        node_execution.started_at,
                        node_execution.completed_at,
                        node_execution.duration_ms,
                        json.dumps(node_execution.input_data) if node_execution.input_data else None,
                        json.dumps(node_execution.output_data) if node_execution.output_data else None,
                        json.dumps(node_execution.error_details) if node_execution.error_details else None,
                        node_execution.retry_count,
                        node_execution.iteration_index
                    ))
                    return True
        except Exception as e:
            logger.error(f"Error creating node execution: {e}\n{traceback.format_exc()}")
            return False

    def update_node_execution(self, node_execution: NodeExecution) -> bool:
        """
        Update a node execution (DEPRECATED - use specific update methods instead).
        
        Kept for backward compatibility. Use:
        - set_node_started() to mark node as started
        - set_node_completed() to mark as completed
        - set_node_failed() to mark as failed
        """
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        UPDATE wf_node_executions
                        SET status = ?, completed_at = ?, duration_ms = ?,
                            output_data = ?, error_details = ?, retry_count = ?
                        WHERE node_execution_id = ?
                    """, (
                        node_execution.status,
                        node_execution.completed_at,
                        node_execution.duration_ms,
                        json.dumps(node_execution.output_data) if node_execution.output_data else None,
                        json.dumps(node_execution.error_details) if node_execution.error_details else None,
                        node_execution.retry_count,
                        node_execution.node_execution_id
                    ))
                    return True
        except Exception as e:
            logger.error(f"Error updating node execution: {e}\n{traceback.format_exc()}")
            return False

    def set_node_started(self, node_execution_id: str) -> bool:
        """Mark node execution as started with current timestamp"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        UPDATE wf_node_executions
                        SET status = 'running', started_at = ?
                        WHERE node_execution_id = ?
                    """, (datetime.now(), node_execution_id))
                    logger.info(f"Node execution started: {node_execution_id}")
                    return True
        except Exception as e:
            logger.error(f"Error setting node started: {e}\n{traceback.format_exc()}")
            return False

    def set_node_completed(self, node_execution_id: str, 
                          output_data: Optional[Dict[str, Any]] = None,
                          duration_ms: Optional[int] = None) -> bool:
        """Mark node execution as completed with output and duration"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        UPDATE wf_node_executions
                        SET status = 'completed', completed_at = ?,
                            output_data = ?, duration_ms = ?
                        WHERE node_execution_id = ?
                    """, (
                        datetime.now(),
                        json.dumps(output_data) if output_data else None,
                        duration_ms,
                        node_execution_id
                    ))
                    logger.info(f"Node execution completed: {node_execution_id}")
                    return True
        except Exception as e:
            logger.error(f"Error setting node completed: {e}\n{traceback.format_exc()}")
            return False

    def set_node_failed(self, node_execution_id: str, 
                       error_details: Optional[Dict[str, Any]] = None) -> bool:
        """Mark node execution as failed with error details"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        UPDATE wf_node_executions
                        SET status = 'failed', completed_at = ?,
                            error_details = ?
                        WHERE node_execution_id = ?
                    """, (
                        datetime.now(),
                        json.dumps(error_details) if error_details else None,
                        node_execution_id
                    ))
                    logger.info(f"Node execution failed: {node_execution_id}")
                    return True
        except Exception as e:
            logger.error(f"Error setting node failed: {e}\n{traceback.format_exc()}")
            return False

    def get_node_executions(self, execution_id: str) -> List[NodeExecution]:
        """Get all node executions for a workflow execution"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        SELECT node_execution_id, execution_id, node_id, node_type, status,
                               started_at, completed_at, duration_ms, input_data, output_data,
                               error_details, retry_count, iteration_index
                        FROM wf_node_executions
                        WHERE execution_id = ?
                        ORDER BY started_at
                    """, (execution_id,))
                    
                    node_executions = []
                    for row in cursor.fetchall():
                        node_executions.append(NodeExecution(
                            node_execution_id=row[0],
                            execution_id=row[1],
                            node_id=row[2],
                            node_type=row[3],
                            status=row[4],
                            started_at=_parse_datetime(row[5]),
                            completed_at=_parse_datetime(row[6]),
                            duration_ms=row[7],
                            input_data=json.loads(row[8]) if row[8] else None,
                            output_data=json.loads(row[9]) if row[9] else None,
                            error_details=json.loads(row[10]) if row[10] else None,
                            retry_count=row[11],
                            iteration_index=row[12]
                        ))
                    return node_executions
        except Exception as e:
            logger.error(f"Error getting node executions: {e}\n{traceback.format_exc()}")
            return []

    # ===================== Human Task Operations =====================

    def create_human_task(self, task: HumanTask) -> bool:
        """Create a new human task"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        INSERT INTO wf_human_tasks
                        (task_id, execution_id, node_execution_id, assigned_to, task_type,
                         status, created_at, responded_at, response_data, comments, timeout_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        task.task_id,
                        task.execution_id,
                        task.node_execution_id,
                        task.assigned_to,
                        task.task_type,
                        task.status,
                        task.created_at,
                        task.responded_at,
                        json.dumps(task.response_data) if task.response_data else None,
                        task.comments,
                        task.timeout_at
                    ))
                    return True
        except Exception as e:
            logger.error(f"Error creating human task: {e}\n{traceback.format_exc()}")
            return False

    def get_human_task(self, task_id: str) -> Optional[HumanTask]:
        """Get a human task by ID"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        SELECT task_id, execution_id, node_execution_id, assigned_to, task_type,
                               status, created_at, responded_at, response_data, comments, timeout_at
                        FROM wf_human_tasks
                        WHERE task_id = ?
                    """, (task_id,))
                    
                    row = cursor.fetchone()
                    if row:
                        return HumanTask(
                            task_id=row[0],
                            execution_id=row[1],
                            node_execution_id=row[2],
                            assigned_to=row[3],
                            task_type=row[4],
                            status=row[5],
                            created_at=_parse_datetime(row[6]),
                            responded_at=_parse_datetime(row[7]),
                            response_data=json.loads(row[8]) if row[8] else None,
                            comments=row[9],
                            timeout_at=_parse_datetime(row[10])
                        )
                    return None
        except Exception as e:
            logger.error(f"Error getting human task: {e}\n{traceback.format_exc()}")
            return None

    def update_human_task(self, task: HumanTask) -> bool:
        """Update a human task"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        UPDATE wf_human_tasks
                        SET status = ?, responded_at = ?, response_data = ?, comments = ?
                        WHERE task_id = ?
                    """, (
                        task.status,
                        task.responded_at,
                        json.dumps(task.response_data) if task.response_data else None,
                        task.comments,
                        task.task_id
                    ))
                    return True
        except Exception as e:
            logger.error(f"Error updating human task: {e}\n{traceback.format_exc()}")
            return False

    def list_user_tasks(self, assigned_to: str, status: Optional[str] = None,
                       limit: int = 100, offset: int = 0) -> List[HumanTask]:
        """List tasks assigned to a user"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    query = """
                        SELECT task_id, execution_id, node_execution_id, assigned_to, task_type,
                               status, created_at, responded_at, response_data, comments, timeout_at
                        FROM wf_human_tasks
                        WHERE assigned_to = ?
                    """
                    params = [assigned_to]
                    
                    if status:
                        query += " AND status = ?"
                        params.append(status)
                    
                    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
                    params.extend([limit, offset])
                    
                    cursor.execute(query, params)
                    
                    tasks = []
                    for row in cursor.fetchall():
                        tasks.append(HumanTask(
                            task_id=row[0],
                            execution_id=row[1],
                            node_execution_id=row[2],
                            assigned_to=row[3],
                            task_type=row[4],
                            status=row[5],
                            created_at=_parse_datetime(row[6]),
                            responded_at=_parse_datetime(row[7]),
                            response_data=json.loads(row[8]) if row[8] else None,
                            comments=row[9],
                            timeout_at=_parse_datetime(row[10])
                        ))
                    return tasks
        except Exception as e:
            logger.error(f"Error listing user tasks: {e}\n{traceback.format_exc()}")
            return []

    # ===================== Audit Log Operations =====================

    def create_audit_log(self, log: AuditLog) -> bool:
        """Create an audit log entry"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        INSERT INTO wf_audit_logs
                        (log_id, execution_id, timestamp, log_level, message, 
                         context_data, source)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        log.log_id,
                        log.execution_id,
                        log.timestamp,
                        log.log_level,
                        log.message,
                        json.dumps(log.context_data) if log.context_data else None,
                        log.source
                    ))
                    return True
        except Exception as e:
            logger.error(f"Error creating audit log: {e}\n{traceback.format_exc()}")
            return False

    def get_audit_logs(self, execution_id: str, 
                       log_level: Optional[str] = None,
                       limit: int = 1000) -> List[AuditLog]:
        """Get audit logs for an execution"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    query = """
                        SELECT log_id, execution_id, timestamp, log_level, message,
                               context_data, source
                        FROM wf_audit_logs
                        WHERE execution_id = ?
                    """
                    params = [execution_id]
                    
                    if log_level:
                        query += " AND log_level = ?"
                        params.append(log_level)
                    
                    query += " ORDER BY timestamp DESC LIMIT ?"
                    params.append(limit)
                    
                    cursor.execute(query, params)
                    
                    logs = []
                    for row in cursor.fetchall():
                        logs.append(AuditLog(
                            log_id=row[0],
                            execution_id=row[1],
                            timestamp=_parse_datetime(row[2]),
                            log_level=row[3],
                            message=row[4],
                            context_data=json.loads(row[5]) if row[5] else None,
                            source=row[6]
                        ))
                    return logs
        except Exception as e:
            logger.error(f"Error getting audit logs: {e}\n{traceback.format_exc()}")
            return []

    # ===================== Analytics Operations =====================

    def get_execution_statistics(self, workflow_id: Optional[str] = None,
                                 days: int = 30) -> Dict[str, Any]:
        """Get execution statistics"""
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    query = """
                        SELECT 
                            COUNT(*) as total_executions,
                            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                            SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) as running,
                            AVG(CASE 
                                WHEN completed_at IS NOT NULL AND started_at IS NOT NULL 
                                THEN (julianday(completed_at) - julianday(started_at)) * 86400000
                                ELSE NULL 
                            END) as avg_duration_ms
                        FROM wf_executions
                        WHERE started_at >= datetime('now', '-' || ? || ' days')
                    """
                    params = [days]
                    
                    if workflow_id:
                        query += " AND workflow_id = ?"
                        params.append(workflow_id)
                    
                    cursor.execute(query, params)
                    row = cursor.fetchone()
                    
                    if row:
                        return {
                            'total_executions': row[0] or 0,
                            'completed': row[1] or 0,
                            'failed': row[2] or 0,
                            'running': row[3] or 0,
                            'avg_duration_ms': row[4] or 0,
                            'success_rate': (row[1] / row[0] * 100) if row[0] > 0 else 0
                        }
                    return {}
        except Exception as e:
            logger.error(f"Error getting execution statistics: {e}\n{traceback.format_exc()}")
            return {}
