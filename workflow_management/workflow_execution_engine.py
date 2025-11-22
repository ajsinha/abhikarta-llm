"""
Workflow Execution Engine

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha | Email: ajsinha@gmail.com

Legal Notice: This module and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited without explicit 
written permission from the copyright holder.

Patent Pending: Certain architectural patterns and implementations described in this module 
may be subject to patent applications.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import json

from workflow_management.models.workflow_models import (
    WorkflowExecution, NodeExecution, AuditLog, HumanTask,
    ExecutionStatus, NodeExecutionStatus, TaskStatus
)
from workflow_management.workflow_db_handler import WorkflowDBHandler

logger = logging.getLogger(__name__)


class WorkflowExecutionEngine:
    """
    Workflow execution engine that orchestrates workflow execution.
    Supports sequential, parallel, and human-in-the-loop workflows.
    """

    def __init__(self, db_handler: WorkflowDBHandler, max_workers: int = 10):
        """
        Initialize the workflow execution engine.

        Args:
            db_handler: Database handler for workflow operations
            max_workers: Maximum number of parallel worker threads
        """
        self.db_handler = db_handler
        self.max_workers = max_workers
        self.executor_pool = ThreadPoolExecutor(max_workers=max_workers)
        logger.info(f"Workflow execution engine initialized with {max_workers} workers")

    def start_execution(self, workflow_id: str, triggered_by: str,
                       input_parameters: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a new workflow execution.

        Args:
            workflow_id: ID of the workflow to execute
            triggered_by: User ID who triggered the execution
            input_parameters: Input parameters for the workflow

        Returns:
            Execution ID
        """
        try:
            # Get workflow definition
            workflow = self.db_handler.get_workflow(workflow_id)
            if not workflow:
                raise ValueError(f"Workflow not found: {workflow_id}")

            # Create execution record
            execution_id = WorkflowExecution.generate_id()
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_id=workflow_id,
                workflow_version=workflow.version,
                status=ExecutionStatus.PENDING.value,
                started_at=None,
                completed_at=None,
                triggered_by=triggered_by,
                input_parameters=input_parameters,
                execution_metadata={'workflow_name': workflow.name}
            )

            if not self.db_handler.create_execution(execution):
                raise RuntimeError("Failed to create execution record")

            # Log execution start
            self._log_audit(execution_id, "INFO", "Workflow execution created",
                          {'workflow_id': workflow_id, 'triggered_by': triggered_by})

            # Submit execution to thread pool for async processing
            self.executor_pool.submit(self._execute_workflow, 
                                    execution_id, workflow, input_parameters)

            logger.info(f"Started workflow execution: {execution_id}")
            return execution_id

        except Exception as e:
            logger.error(f"Error starting workflow execution: {e}")
            raise

    def _execute_workflow(self, execution_id: str, workflow: Any,
                         input_parameters: Optional[Dict[str, Any]]):
        """
        Execute a workflow asynchronously.

        Args:
            execution_id: Execution ID
            workflow: Workflow definition
            input_parameters: Input parameters
        """
        try:
            # Update execution status to running
            #self.db_handler.update_execution_status(
            #    execution_id, ExecutionStatus.RUNNING.value, started_at=datetime.now())

            self.db_handler.set_execution_started(execution_id)

            self._log_audit(execution_id, "INFO", "Workflow execution started")

            # Parse workflow definition
            definition = workflow.definition_json
            nodes = definition.get('nodes', [])
            edges = definition.get('edges', [])

            # Initialize execution context
            context = {
                'execution_id': execution_id,
                'workflow_id': workflow.workflow_id,
                'input_parameters': input_parameters or {},
                'variables': definition.get('variables', {}),
                'node_outputs': {}
            }

            # Find start node
            start_node = next((n for n in nodes if n.get('node_type') == 'start'), None)
            if not start_node:
                raise ValueError("No start node found in workflow")

            # Execute workflow from start node
            self._execute_from_node(start_node, nodes, edges, context)

            # Update execution status to completed
            self.db_handler.update_execution_status(
                execution_id, ExecutionStatus.COMPLETED.value,
                completed_at=datetime.now(),
                output_results=context.get('node_outputs', {}))


            self._log_audit(execution_id, "INFO", "Workflow execution completed")

        except Exception as e:
            logger.error(f"Error executing workflow {execution_id}: {e}")
            self.db_handler.update_execution_status(
                execution_id, ExecutionStatus.FAILED.value,
                completed_at=datetime.now(),
                error_message=str(e))
            self._log_audit(execution_id, "ERROR", f"Workflow execution failed: {str(e)}")

    def _execute_from_node(self, node: Dict[str, Any], all_nodes: List[Dict[str, Any]],
                          edges: List[Dict[str, Any]], context: Dict[str, Any]):
        """
        Execute workflow starting from a given node.

        Args:
            node: Current node to execute
            all_nodes: All nodes in the workflow
            edges: All edges in the workflow
            context: Execution context
        """
        node_id = node.get('node_id')
        node_type = node.get('node_type')

        # Skip if end node
        if node_type == 'end':
            return

        # Execute current node
        node_output = self._execute_node(node, context)

        # Store node output in context
        context['node_outputs'][node_id] = node_output

        # Find next nodes
        next_edges = [e for e in edges if e.get('source') == node_id]

        if not next_edges:
            return

        # Handle parallel execution
        if node_type == 'parallel':
            self._execute_parallel_branches(next_edges, all_nodes, edges, context)
        else:
            # Sequential execution
            for edge in next_edges:
                # Check edge condition if present
                if self._evaluate_condition(edge.get('condition'), context):
                    target_node_id = edge.get('target')
                    target_node = next((n for n in all_nodes 
                                      if n.get('node_id') == target_node_id), None)
                    if target_node:
                        self._execute_from_node(target_node, all_nodes, edges, context)

    def _execute_node(self, node: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """
        Execute a single node.

        Args:
            node: Node definition
            context: Execution context

        Returns:
            Node output
        """
        node_id = node.get('node_id')
        node_type = node.get('node_type')
        execution_id = context['execution_id']

        # Create node execution record
        node_execution_id = NodeExecution.generate_id()
        node_execution = NodeExecution(
            node_execution_id=node_execution_id,
            execution_id=execution_id,
            node_id=node_id,
            node_type=node_type,
            status=NodeExecutionStatus.RUNNING.value,
            started_at=datetime.now(),
            completed_at=None,
            input_data=self._prepare_node_input(node, context)
        )

        self.db_handler.create_node_execution(node_execution)
        start_time = time.time()

        try:
            # Execute based on node type
            if node_type == 'start':
                output = context.get('input_parameters', {})
            elif node_type == 'human':
                output = self._execute_human_node(node, node_execution, context)
            elif node_type == 'llm':
                output = self._execute_llm_node(node, context)
            elif node_type == 'tool':
                output = self._execute_tool_node(node, context)
            elif node_type == 'conditional':
                output = self._execute_conditional_node(node, context)
            else:
                output = {'status': 'skipped', 'reason': f'Unsupported node type: {node_type}'}

            # Update node execution as completed
            duration_ms = int((time.time() - start_time) * 1000)
            node_execution.status = NodeExecutionStatus.COMPLETED.value
            node_execution.completed_at = datetime.now()
            node_execution.duration_ms = duration_ms
            node_execution.output_data = output

            self.db_handler.update_node_execution(node_execution)
            self._log_audit(execution_id, "INFO", f"Node {node_id} completed",
                          {'node_type': node_type, 'duration_ms': duration_ms})

            return output

        except Exception as e:
            logger.error(f"Error executing node {node_id}: {e}")
            node_execution.status = NodeExecutionStatus.FAILED.value
            node_execution.completed_at = datetime.now()
            node_execution.error_details = {'error': str(e)}
            self.db_handler.update_node_execution(node_execution)
            self._log_audit(execution_id, "ERROR", f"Node {node_id} failed: {str(e)}")
            raise

    def _execute_human_node(self, node: Dict[str, Any], 
                           node_execution: NodeExecution,
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a human-in-the-loop node.

        Args:
            node: Node definition
            node_execution: Node execution record
            context: Execution context

        Returns:
            Node output (blocks until human responds)
        """
        config = node.get('config', {})
        assigned_to = config.get('assigned_to', 'admin')
        task_type = config.get('task_type', 'approval')
        timeout_seconds = config.get('timeout', 3600)

        # Create human task
        task_id = HumanTask.generate_id()
        task = HumanTask(
            task_id=task_id,
            execution_id=context['execution_id'],
            node_execution_id=node_execution.node_execution_id,
            assigned_to=assigned_to,
            task_type=task_type,
            status=TaskStatus.PENDING.value,
            created_at=datetime.now(),
            responded_at=None,
            timeout_at=datetime.fromtimestamp(time.time() + timeout_seconds)
        )

        self.db_handler.create_human_task(task)
        self._log_audit(context['execution_id'], "INFO",
                       f"Human task created: {task_id}",
                       {'assigned_to': assigned_to, 'task_type': task_type})

        # Poll for task completion (in production, use event-driven approach)
        max_wait = timeout_seconds
        poll_interval = 5  # seconds
        elapsed = 0

        while elapsed < max_wait:
            time.sleep(poll_interval)
            elapsed += poll_interval

            # Check task status
            updated_task = self.db_handler.get_human_task(task_id)
            if updated_task and updated_task.status in [
                TaskStatus.COMPLETED.value, 
                TaskStatus.REJECTED.value
            ]:
                return {
                    'status': updated_task.status,
                    'response_data': updated_task.response_data,
                    'comments': updated_task.comments
                }

        # Timeout
        task.status = TaskStatus.TIMEOUT.value
        self.db_handler.update_human_task(task)
        return {'status': 'timeout', 'message': 'Human task timed out'}

    def _execute_llm_node(self, node: Dict[str, Any], 
                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an LLM node (placeholder for actual LLM integration)"""
        config = node.get('config', {})
        prompt = config.get('prompt', '')
        
        # Replace variables in prompt
        for key, value in context.get('variables', {}).items():
            prompt = prompt.replace(f'{{{{{key}}}}}', str(value))
        
        # Placeholder - integrate with actual LLM facade
        return {
            'status': 'completed',
            'prompt': prompt,
            'response': 'LLM response placeholder',
            'model': config.get('model', 'default')
        }

    def _execute_tool_node(self, node: Dict[str, Any],
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool node with actual tool integration"""
        config = node.get('config', {})
        tool_name = config.get('tool_name', '')
        parameters = config.get('parameters', {})
        
        # Import tools dynamically
        try:
            from workflow_management.example_tools import get_tool
            
            # Get tool instance
            tool = get_tool(tool_name)
            
            # Resolve parameter variables from context
            resolved_params = {}
            for key, value in parameters.items():
                if isinstance(value, str) and value.startswith('{{') and value.endswith('}}'):
                    # Extract variable name
                    var_name = value[2:-2].strip()
                    # Look up in context
                    resolved_params[key] = context.get('variables', {}).get(var_name, value)
                else:
                    resolved_params[key] = value
            
            # Execute tool with tracking
            result = tool._execute_with_tracking(**resolved_params)
            
            # Return result
            if result.success:
                return {
                    'status': 'completed',
                    'tool': tool_name,
                    'parameters': resolved_params,
                    'result': result.data,
                    'execution_time': result.execution_time
                }
            else:
                return {
                    'status': 'failed',
                    'tool': tool_name,
                    'parameters': resolved_params,
                    'error': result.error,
                    'error_type': result.error_type
                }
        except ImportError:
            # Fallback if tools not available
            logger.warning(f"Tool import failed, using placeholder for {tool_name}")
            return {
                'status': 'completed',
                'tool': tool_name,
                'parameters': parameters,
                'result': f'Tool {tool_name} executed (placeholder mode)'
            }
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                'status': 'failed',
                'tool': tool_name,
                'parameters': parameters,
                'error': str(e),
                'error_type': type(e).__name__
            }

    def _execute_conditional_node(self, node: Dict[str, Any],
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a conditional node"""
        config = node.get('config', {})
        condition = config.get('condition', '')
        
        result = self._evaluate_condition(condition, context)
        return {
            'status': 'completed',
            'condition': condition,
            'result': result
        }

    def _execute_parallel_branches(self, edges: List[Dict[str, Any]],
                                   all_nodes: List[Dict[str, Any]],
                                   all_edges: List[Dict[str, Any]],
                                   context: Dict[str, Any]):
        """
        Execute multiple branches in parallel.

        Args:
            edges: Edges to parallel branches
            all_nodes: All workflow nodes
            all_edges: All workflow edges
            context: Execution context
        """
        futures = []
        
        for edge in edges:
            target_node_id = edge.get('target')
            target_node = next((n for n in all_nodes 
                              if n.get('node_id') == target_node_id), None)
            if target_node:
                # Create a copy of context for each branch
                branch_context = context.copy()
                future = self.executor_pool.submit(
                    self._execute_from_node, 
                    target_node, all_nodes, all_edges, branch_context
                )
                futures.append(future)
        
        # Wait for all branches to complete
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"Error in parallel branch: {e}")

    def _prepare_node_input(self, node: Dict[str, Any],
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare input data for a node based on input mappings"""
        input_mappings = node.get('input_mappings', {})
        input_data = {}
        
        for key, source in input_mappings.items():
            if source in context.get('node_outputs', {}):
                input_data[key] = context['node_outputs'][source]
            elif source in context.get('variables', {}):
                input_data[key] = context['variables'][source]
        
        return input_data

    def _evaluate_condition(self, condition: Optional[str],
                           context: Dict[str, Any]) -> bool:
        """Evaluate a condition expression"""
        if not condition:
            return True
        
        try:
            # Simple condition evaluation (enhance with proper expression parser)
            # For now, just check if condition is true
            return eval(condition, {}, context)
        except Exception as e:
            logger.warning(f"Error evaluating condition '{condition}': {e}")
            return False

    def _log_audit(self, execution_id: str, level: str, message: str,
                   context_data: Optional[Dict[str, Any]] = None):
        """Create an audit log entry"""
        log = AuditLog(
            log_id=AuditLog.generate_id(),
            execution_id=execution_id,
            timestamp=datetime.now(),
            log_level=level,
            message=message,
            context_data=context_data,
            source='execution_engine'
        )
        self.db_handler.create_audit_log(log)

    def pause_execution(self, execution_id: str) -> bool:
        """Pause a running workflow execution"""
        try:
            self.db_handler.update_execution_status(
                execution_id, ExecutionStatus.PAUSED.value)
            self._log_audit(execution_id, "INFO", "Workflow execution paused")
            return True
        except Exception as e:
            logger.error(f"Error pausing execution: {e}")
            return False

    def resume_execution(self, execution_id: str) -> bool:
        """Resume a paused workflow execution"""
        try:
            self.db_handler.update_execution_status(
                execution_id, ExecutionStatus.RUNNING.value)
            self._log_audit(execution_id, "INFO", "Workflow execution resumed")
            return True
        except Exception as e:
            logger.error(f"Error resuming execution: {e}")
            return False

    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running workflow execution"""
        try:
            self.db_handler.update_execution_status(
                execution_id, ExecutionStatus.CANCELLED.value,
                completed_at=datetime.now())
            self._log_audit(execution_id, "INFO", "Workflow execution cancelled")
            return True
        except Exception as e:
            logger.error(f"Error cancelling execution: {e}")
            return False

    def shutdown(self):
        """Shutdown the execution engine"""
        logger.info("Shutting down workflow execution engine")
        self.executor_pool.shutdown(wait=True)
