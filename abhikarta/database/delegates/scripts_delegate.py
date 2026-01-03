"""
Scripts Delegate - Database operations for Python Scripts and Script Executions.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Version: 1.4.8

Handles tables:
- python_scripts: Stores Python script definitions for agents, workflows, swarms, AI orgs
- script_executions: Tracks execution history of scripts
"""

from typing import Any, Dict, List, Optional
import uuid
import json
import logging
from datetime import datetime

from ..database_delegate import DatabaseDelegate

logger = logging.getLogger(__name__)


class ScriptsDelegate(DatabaseDelegate):
    """
    Delegate for Python Script-related database operations.
    
    Handles tables: python_scripts, script_executions
    
    This delegate manages Python Script Mode functionality which allows
    power users to define agents, workflows, swarms, and AI organizations
    using Python code instead of JSON or visual designers.
    """
    
    # =========================================================================
    # PYTHON SCRIPTS
    # =========================================================================
    
    def get_all_scripts(self, entity_type: str = None, created_by: int = None,
                        is_active: bool = True, validation_status: str = None,
                        limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Get all Python scripts with optional filters.
        
        Args:
            entity_type: Filter by entity type ('agent', 'workflow', 'swarm', 'aiorg')
            created_by: Filter by creator user ID
            is_active: Filter by active status (default True)
            validation_status: Filter by validation status ('pending', 'valid', 'invalid')
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of script dictionaries
        """
        query = "SELECT * FROM python_scripts"
        conditions = []
        params = []
        
        if is_active is not None:
            conditions.append("is_active = ?")
            params.append(1 if is_active else 0)
        if entity_type:
            conditions.append("entity_type = ?")
            params.append(entity_type)
        if created_by:
            conditions.append("created_by = ?")
            params.append(created_by)
        if validation_status:
            conditions.append("validation_status = ?")
            params.append(validation_status)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        return self.fetch_all(query, tuple(params)) or []
    
    def get_script(self, script_id: str) -> Optional[Dict]:
        """Get script by ID."""
        return self.fetch_one(
            "SELECT * FROM python_scripts WHERE script_id = ?",
            (script_id,)
        )
    
    def get_script_by_name(self, name: str) -> Optional[Dict]:
        """Get script by name."""
        return self.fetch_one(
            "SELECT * FROM python_scripts WHERE name = ? AND is_active = 1",
            (name,)
        )
    
    def get_scripts_by_entity_type(self, entity_type: str, 
                                    is_active: bool = True) -> List[Dict]:
        """Get all scripts for a specific entity type."""
        query = "SELECT * FROM python_scripts WHERE entity_type = ?"
        params = [entity_type]
        
        if is_active is not None:
            query += " AND is_active = ?"
            params.append(1 if is_active else 0)
        
        query += " ORDER BY updated_at DESC"
        return self.fetch_all(query, tuple(params)) or []
    
    def get_user_scripts(self, user_id: int, entity_type: str = None) -> List[Dict]:
        """Get scripts created by a specific user."""
        query = "SELECT * FROM python_scripts WHERE created_by = ? AND is_active = 1"
        params = [user_id]
        
        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type)
        
        query += " ORDER BY updated_at DESC"
        return self.fetch_all(query, tuple(params)) or []
    
    def get_scripts_count(self, entity_type: str = None, 
                          is_active: bool = True) -> int:
        """Get count of scripts."""
        where_parts = []
        if is_active is not None:
            where_parts.append(f"is_active = {1 if is_active else 0}")
        if entity_type:
            where_parts.append(f"entity_type = '{entity_type}'")
        
        where = " AND ".join(where_parts) if where_parts else None
        return self.get_count("python_scripts", where)
    
    def create_script(self, name: str, entity_type: str, script_content: str,
                      created_by: int, description: str = None,
                      entry_point: str = '__export__',
                      dependencies: str = '[]', tags: str = '[]') -> Optional[str]:
        """
        Create a new Python script and return script_id.
        
        Args:
            name: Script name
            entity_type: Entity type ('agent', 'workflow', 'swarm', 'aiorg')
            script_content: The Python code content
            created_by: User ID of creator
            description: Optional description
            entry_point: Variable name to extract (default '__export__')
            dependencies: JSON array of pip packages
            tags: JSON array of tags
            
        Returns:
            script_id if successful, None otherwise
        """
        script_id = f"script_{uuid.uuid4().hex[:12]}"
        try:
            self.execute(
                """INSERT INTO python_scripts 
                   (script_id, name, description, entity_type, script_content,
                    entry_point, dependencies, validation_status, tags, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)""",
                (script_id, name, description, entity_type, script_content,
                 entry_point, dependencies, tags, created_by)
            )
            return script_id
        except Exception as e:
            logger.error(f"Error creating script: {e}")
            return None
    
    def update_script(self, script_id: str, **kwargs) -> bool:
        """
        Update script fields.
        
        Args:
            script_id: Script ID to update
            **kwargs: Fields to update (name, description, script_content, 
                      entry_point, dependencies, tags, validation_status,
                      validation_message, linked_entity_id)
                      
        Returns:
            True if successful
        """
        if not kwargs:
            return False
        
        valid_fields = ['name', 'description', 'script_content', 'entry_point',
                        'dependencies', 'validation_status', 'validation_message',
                        'linked_entity_id', 'tags']
        
        updates = ["updated_at = CURRENT_TIMESTAMP"]
        params = []
        
        for key, value in kwargs.items():
            if key in valid_fields:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if len(updates) == 1:  # Only updated_at
            return False
        
        params.append(script_id)
        query = f"UPDATE python_scripts SET {', '.join(updates)} WHERE script_id = ?"
        
        try:
            self.execute(query, tuple(params))
            return True
        except Exception as e:
            logger.error(f"Error updating script: {e}")
            return False
    
    def update_script_content(self, script_id: str, script_content: str,
                              version_increment: bool = True) -> bool:
        """
        Update script content and optionally increment version.
        
        Args:
            script_id: Script ID
            script_content: New Python code content
            version_increment: Whether to increment version number
            
        Returns:
            True if successful
        """
        try:
            if version_increment:
                self.execute(
                    """UPDATE python_scripts 
                       SET script_content = ?, version = version + 1,
                           validation_status = 'pending', updated_at = CURRENT_TIMESTAMP
                       WHERE script_id = ?""",
                    (script_content, script_id)
                )
            else:
                self.execute(
                    """UPDATE python_scripts 
                       SET script_content = ?, validation_status = 'pending',
                           updated_at = CURRENT_TIMESTAMP
                       WHERE script_id = ?""",
                    (script_content, script_id)
                )
            return True
        except Exception as e:
            logger.error(f"Error updating script content: {e}")
            return False
    
    def set_validation_status(self, script_id: str, status: str,
                              message: str = None) -> bool:
        """
        Set script validation status.
        
        Args:
            script_id: Script ID
            status: Validation status ('pending', 'valid', 'invalid')
            message: Optional validation message
            
        Returns:
            True if successful
        """
        try:
            self.execute(
                """UPDATE python_scripts 
                   SET validation_status = ?, validation_message = ?,
                       updated_at = CURRENT_TIMESTAMP
                   WHERE script_id = ?""",
                (status, message, script_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error setting validation status: {e}")
            return False
    
    def link_entity(self, script_id: str, entity_id: str) -> bool:
        """
        Link script to a created entity.
        
        Args:
            script_id: Script ID
            entity_id: ID of the created agent/workflow/swarm/aiorg
            
        Returns:
            True if successful
        """
        try:
            self.execute(
                """UPDATE python_scripts 
                   SET linked_entity_id = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE script_id = ?""",
                (entity_id, script_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error linking entity: {e}")
            return False
    
    def deactivate_script(self, script_id: str) -> bool:
        """Deactivate (soft delete) a script."""
        try:
            self.execute(
                """UPDATE python_scripts 
                   SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                   WHERE script_id = ?""",
                (script_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error deactivating script: {e}")
            return False
    
    def activate_script(self, script_id: str) -> bool:
        """Reactivate a deactivated script."""
        try:
            self.execute(
                """UPDATE python_scripts 
                   SET is_active = 1, updated_at = CURRENT_TIMESTAMP
                   WHERE script_id = ?""",
                (script_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error activating script: {e}")
            return False
    
    def delete_script(self, script_id: str) -> bool:
        """Permanently delete a script and its executions."""
        try:
            # Executions are deleted via CASCADE
            self.execute(
                "DELETE FROM python_scripts WHERE script_id = ?",
                (script_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting script: {e}")
            return False
    
    def script_exists(self, script_id: str) -> bool:
        """Check if script exists."""
        return self.exists("python_scripts", "script_id = ?", (script_id,))
    
    def increment_execution_count(self, script_id: str) -> bool:
        """Increment script execution count and update last_executed_at."""
        try:
            self.execute(
                """UPDATE python_scripts 
                   SET execution_count = execution_count + 1,
                       last_executed_at = CURRENT_TIMESTAMP
                   WHERE script_id = ?""",
                (script_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error incrementing execution count: {e}")
            return False
    
    # =========================================================================
    # SCRIPT EXECUTIONS
    # =========================================================================
    
    def get_script_executions(self, script_id: str, limit: int = 50,
                               offset: int = 0) -> List[Dict]:
        """Get execution history for a script."""
        return self.fetch_all(
            """SELECT * FROM script_executions 
               WHERE script_id = ? 
               ORDER BY started_at DESC
               LIMIT ? OFFSET ?""",
            (script_id, limit, offset)
        ) or []
    
    def get_execution(self, execution_id: str) -> Optional[Dict]:
        """Get execution by ID."""
        return self.fetch_one(
            "SELECT * FROM script_executions WHERE execution_id = ?",
            (execution_id,)
        )
    
    def get_user_executions(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get executions by user."""
        return self.fetch_all(
            """SELECT e.*, s.name as script_name, s.entity_type
               FROM script_executions e
               JOIN python_scripts s ON e.script_id = s.script_id
               WHERE e.executed_by = ?
               ORDER BY e.started_at DESC
               LIMIT ?""",
            (user_id, limit)
        ) or []
    
    def get_recent_executions(self, limit: int = 20) -> List[Dict]:
        """Get most recent executions across all scripts."""
        return self.fetch_all(
            """SELECT e.*, s.name as script_name, s.entity_type
               FROM script_executions e
               JOIN python_scripts s ON e.script_id = s.script_id
               ORDER BY e.started_at DESC
               LIMIT ?""",
            (limit,)
        ) or []
    
    def get_executions_count(self, script_id: str = None,
                              status: str = None) -> int:
        """Get count of executions."""
        where_parts = []
        if script_id:
            where_parts.append(f"script_id = '{script_id}'")
        if status:
            where_parts.append(f"status = '{status}'")
        
        where = " AND ".join(where_parts) if where_parts else None
        return self.get_count("script_executions", where)
    
    def create_execution(self, script_id: str, executed_by: int,
                         input_data: str = '{}') -> Optional[str]:
        """
        Create a new script execution record.
        
        Args:
            script_id: Script being executed
            executed_by: User ID executing the script
            input_data: JSON string of input data
            
        Returns:
            execution_id if successful, None otherwise
        """
        execution_id = f"exec_{uuid.uuid4().hex[:12]}"
        try:
            self.execute(
                """INSERT INTO script_executions 
                   (execution_id, script_id, status, input_data, executed_by)
                   VALUES (?, ?, 'running', ?, ?)""",
                (execution_id, script_id, input_data, executed_by)
            )
            # Increment script execution count
            self.increment_execution_count(script_id)
            return execution_id
        except Exception as e:
            logger.error(f"Error creating execution: {e}")
            return None
    
    def complete_execution(self, execution_id: str, output_data: str,
                           stdout: str = None, stderr: str = None,
                           duration_ms: int = None) -> bool:
        """
        Mark execution as completed successfully.
        
        Args:
            execution_id: Execution ID
            output_data: JSON string of output data
            stdout: Captured stdout
            stderr: Captured stderr
            duration_ms: Execution duration in milliseconds
            
        Returns:
            True if successful
        """
        try:
            self.execute(
                """UPDATE script_executions 
                   SET status = 'completed', output_data = ?, stdout = ?,
                       stderr = ?, duration_ms = ?, completed_at = CURRENT_TIMESTAMP
                   WHERE execution_id = ?""",
                (output_data, stdout, stderr, duration_ms, execution_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error completing execution: {e}")
            return False
    
    def fail_execution(self, execution_id: str, error_message: str,
                       stdout: str = None, stderr: str = None,
                       duration_ms: int = None) -> bool:
        """
        Mark execution as failed.
        
        Args:
            execution_id: Execution ID
            error_message: Error message/traceback
            stdout: Captured stdout
            stderr: Captured stderr
            duration_ms: Execution duration in milliseconds
            
        Returns:
            True if successful
        """
        try:
            self.execute(
                """UPDATE script_executions 
                   SET status = 'failed', error_message = ?, stdout = ?,
                       stderr = ?, duration_ms = ?, completed_at = CURRENT_TIMESTAMP
                   WHERE execution_id = ?""",
                (error_message, stdout, stderr, duration_ms, execution_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error failing execution: {e}")
            return False
    
    def delete_old_executions(self, script_id: str, keep_count: int = 100) -> int:
        """
        Delete old executions keeping only the most recent ones.
        
        Args:
            script_id: Script ID
            keep_count: Number of recent executions to keep
            
        Returns:
            Number of deleted executions
        """
        try:
            # Get count of executions to delete
            total = self.get_executions_count(script_id=script_id)
            to_delete = max(0, total - keep_count)
            
            if to_delete > 0:
                self.execute(
                    """DELETE FROM script_executions 
                       WHERE script_id = ? AND execution_id IN (
                           SELECT execution_id FROM script_executions
                           WHERE script_id = ?
                           ORDER BY started_at ASC
                           LIMIT ?
                       )""",
                    (script_id, script_id, to_delete)
                )
            return to_delete
        except Exception as e:
            logger.error(f"Error deleting old executions: {e}")
            return 0
    
    def delete_execution(self, execution_id: str) -> bool:
        """Delete a specific execution."""
        try:
            self.execute(
                "DELETE FROM script_executions WHERE execution_id = ?",
                (execution_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting execution: {e}")
            return False
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_script_stats(self, script_id: str) -> Dict[str, Any]:
        """
        Get statistics for a script.
        
        Returns:
            Dictionary with execution statistics
        """
        result = self.fetch_one(
            """SELECT 
                   COUNT(*) as total_executions,
                   SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful,
                   SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                   AVG(duration_ms) as avg_duration_ms,
                   MAX(started_at) as last_execution
               FROM script_executions
               WHERE script_id = ?""",
            (script_id,)
        )
        return result or {
            'total_executions': 0,
            'successful': 0,
            'failed': 0,
            'avg_duration_ms': None,
            'last_execution': None
        }
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """
        Get overall Python Scripts statistics.
        
        Returns:
            Dictionary with overall statistics
        """
        scripts = self.fetch_one(
            """SELECT 
                   COUNT(*) as total_scripts,
                   SUM(CASE WHEN entity_type = 'agent' THEN 1 ELSE 0 END) as agents,
                   SUM(CASE WHEN entity_type = 'workflow' THEN 1 ELSE 0 END) as workflows,
                   SUM(CASE WHEN entity_type = 'swarm' THEN 1 ELSE 0 END) as swarms,
                   SUM(CASE WHEN entity_type = 'aiorg' THEN 1 ELSE 0 END) as aiorgs,
                   SUM(CASE WHEN validation_status = 'valid' THEN 1 ELSE 0 END) as valid,
                   SUM(CASE WHEN validation_status = 'invalid' THEN 1 ELSE 0 END) as invalid
               FROM python_scripts
               WHERE is_active = 1"""
        ) or {}
        
        executions = self.fetch_one(
            """SELECT 
                   COUNT(*) as total_executions,
                   SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful,
                   SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
               FROM script_executions"""
        ) or {}
        
        return {
            'scripts': scripts,
            'executions': executions
        }
