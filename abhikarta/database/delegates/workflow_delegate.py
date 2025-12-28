"""
Workflow Delegate - Database operations for Workflows and Workflow Nodes.

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


class WorkflowDelegate(DatabaseDelegate):
    """
    Delegate for workflow-related database operations.
    
    Handles tables: workflows, workflow_nodes
    """
    
    # =========================================================================
    # WORKFLOWS
    # =========================================================================
    
    def get_all_workflows(self, status: str = None, 
                          created_by: str = None) -> List[Dict]:
        """Get all workflows with optional filters."""
        query = "SELECT * FROM workflows"
        conditions = []
        params = []
        
        if status:
            conditions.append("status = ?")
            params.append(status)
        if created_by:
            conditions.append("created_by = ?")
            params.append(created_by)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY created_at DESC"
        return self.fetch_all(query, tuple(params) if params else None) or []
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict]:
        """Get workflow by ID."""
        return self.fetch_one(
            "SELECT * FROM workflows WHERE workflow_id = ?",
            (workflow_id,)
        )
    
    def get_workflow_by_name(self, name: str) -> Optional[Dict]:
        """Get workflow by name."""
        return self.fetch_one(
            "SELECT * FROM workflows WHERE name = ?",
            (name,)
        )
    
    def get_workflows_count(self, status: str = None) -> int:
        """Get count of workflows."""
        where = f"status = '{status}'" if status else None
        return self.get_count("workflows", where)
    
    def get_user_workflows(self, user_id: str) -> List[Dict]:
        """Get workflows created by a user."""
        return self.fetch_all(
            "SELECT * FROM workflows WHERE created_by = ? ORDER BY created_at DESC",
            (user_id,)
        ) or []
    
    def create_workflow(self, name: str, dag_definition: str, created_by: str,
                        description: str = None, version: str = '1.0.0',
                        workflow_type: str = 'dag', python_modules: str = '{}',
                        entry_point: str = None, input_schema: str = '{}',
                        output_schema: str = '{}', dependencies: str = '[]',
                        environment: str = '{}', status: str = 'draft',
                        tags: str = '[]') -> Optional[str]:
        """Create a new workflow and return workflow_id."""
        workflow_id = str(uuid.uuid4())
        try:
            self.execute(
                """INSERT INTO workflows 
                   (workflow_id, name, description, version, workflow_type,
                    dag_definition, python_modules, entry_point, input_schema,
                    output_schema, dependencies, environment, status, tags, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (workflow_id, name, description, version, workflow_type,
                 dag_definition, python_modules, entry_point, input_schema,
                 output_schema, dependencies, environment, status, tags, created_by)
            )
            return workflow_id
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            return None
    
    def update_workflow(self, workflow_id: str, **kwargs) -> bool:
        """Update workflow fields."""
        if not kwargs:
            return False
        
        valid_fields = ['name', 'description', 'version', 'workflow_type',
                        'dag_definition', 'python_modules', 'entry_point',
                        'input_schema', 'output_schema', 'dependencies',
                        'environment', 'status', 'tags']
        
        updates = []
        params = []
        for key, value in kwargs.items():
            if key in valid_fields:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if not updates:
            return False
        
        params.append(workflow_id)
        query = f"UPDATE workflows SET {', '.join(updates)} WHERE workflow_id = ?"
        
        try:
            self.execute(query, tuple(params))
            return True
        except Exception as e:
            logger.error(f"Error updating workflow: {e}")
            return False
    
    def update_workflow_stats(self, workflow_id: str, 
                              duration_ms: int = None) -> bool:
        """Update workflow execution statistics."""
        try:
            workflow = self.get_workflow(workflow_id)
            if not workflow:
                return False
            
            execution_count = workflow.get('execution_count', 0) + 1
            current_avg = workflow.get('avg_duration_ms', 0) or 0
            
            # Calculate new average
            if duration_ms and current_avg:
                new_avg = int(((current_avg * (execution_count - 1)) + duration_ms) / execution_count)
            else:
                new_avg = duration_ms or current_avg
            
            self.execute(
                """UPDATE workflows 
                   SET execution_count = ?, avg_duration_ms = ?, 
                       last_executed_at = CURRENT_TIMESTAMP
                   WHERE workflow_id = ?""",
                (execution_count, new_avg, workflow_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error updating workflow stats: {e}")
            return False
    
    def publish_workflow(self, workflow_id: str) -> bool:
        """Publish a workflow."""
        return self.update_workflow(workflow_id, status='published')
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow and its nodes."""
        try:
            self.execute(
                "DELETE FROM workflow_nodes WHERE workflow_id = ?",
                (workflow_id,)
            )
            self.execute(
                "DELETE FROM workflows WHERE workflow_id = ?",
                (workflow_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting workflow: {e}")
            return False
    
    def workflow_exists(self, workflow_id: str) -> bool:
        """Check if workflow exists."""
        return self.exists("workflows", "workflow_id = ?", (workflow_id,))
    
    # =========================================================================
    # WORKFLOW NODES
    # =========================================================================
    
    def get_workflow_nodes(self, workflow_id: str) -> List[Dict]:
        """Get all nodes for a workflow."""
        return self.fetch_all(
            "SELECT * FROM workflow_nodes WHERE workflow_id = ? ORDER BY id",
            (workflow_id,)
        ) or []
    
    def get_node(self, node_id: str) -> Optional[Dict]:
        """Get node by ID."""
        return self.fetch_one(
            "SELECT * FROM workflow_nodes WHERE node_id = ?",
            (node_id,)
        )
    
    def create_node(self, workflow_id: str, name: str, node_type: str,
                    config: str = '{}', python_code: str = None,
                    position_x: int = 0, position_y: int = 0,
                    dependencies: str = '[]') -> Optional[str]:
        """Create a new workflow node and return node_id."""
        node_id = str(uuid.uuid4())
        try:
            self.execute(
                """INSERT INTO workflow_nodes 
                   (node_id, workflow_id, name, node_type, config,
                    python_code, position_x, position_y, dependencies)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (node_id, workflow_id, name, node_type, config,
                 python_code, position_x, position_y, dependencies)
            )
            return node_id
        except Exception as e:
            logger.error(f"Error creating node: {e}")
            return None
    
    def update_node(self, node_id: str, **kwargs) -> bool:
        """Update node fields."""
        if not kwargs:
            return False
        
        valid_fields = ['name', 'node_type', 'config', 'python_code',
                        'position_x', 'position_y', 'dependencies']
        
        updates = []
        params = []
        for key, value in kwargs.items():
            if key in valid_fields:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if not updates:
            return False
        
        params.append(node_id)
        query = f"UPDATE workflow_nodes SET {', '.join(updates)} WHERE node_id = ?"
        
        try:
            self.execute(query, tuple(params))
            return True
        except Exception as e:
            logger.error(f"Error updating node: {e}")
            return False
    
    def delete_node(self, node_id: str) -> bool:
        """Delete a workflow node."""
        try:
            self.execute(
                "DELETE FROM workflow_nodes WHERE node_id = ?",
                (node_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting node: {e}")
            return False
    
    def delete_workflow_nodes(self, workflow_id: str) -> bool:
        """Delete all nodes for a workflow."""
        try:
            self.execute(
                "DELETE FROM workflow_nodes WHERE workflow_id = ?",
                (workflow_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting workflow nodes: {e}")
            return False
    
    def get_nodes_count(self, workflow_id: str) -> int:
        """Get count of nodes in a workflow."""
        return self.get_count("workflow_nodes", "workflow_id = ?", (workflow_id,))
