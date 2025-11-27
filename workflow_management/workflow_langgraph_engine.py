"""
LangGraph-Based Workflow Execution Engine

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha | Email: ajsinha@gmail.com

This module provides a LangGraph-based execution engine that integrates with
the existing database schema and UI while leveraging LangGraph's StateGraph
for robust workflow orchestration.

Legal Notice: This module and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited without explicit
written permission from the copyright holder.

Patent Pending: Certain architectural patterns and implementations described in this module
may be subject to patent applications.
"""

import logging
from typing import Dict, Any, Optional, List, TypedDict, Annotated
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import json
import operator

from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from workflow_management.models.workflow_models import (
    WorkflowExecution, NodeExecution, AuditLog, HumanTask,
    ExecutionStatus, NodeExecutionStatus, TaskStatus
)
from workflow_management.workflow_db_handler import WorkflowDBHandler

logger = logging.getLogger(__name__)


def merge_dicts(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two dictionaries for parallel state updates.
    Used as a reducer for dict fields that can be updated by parallel branches.
    """
    if left is None:
        return right if right is not None else {}
    if right is None:
        return left
    # Create a new dict with merged values
    result = {**left, **right}
    return result


class WorkflowState(TypedDict):
    """
    State object for workflow execution in LangGraph.

    Fields with Annotated[..., reducer] can be safely updated by parallel branches.
    Fields without annotation should only be updated by single nodes.
    """
    execution_id: str
    workflow_id: str
    current_node: str
    messages: Annotated[List[BaseMessage], operator.add]
    variables: Annotated[Dict[str, Any], merge_dicts]
    node_outputs: Annotated[Dict[str, Any], merge_dicts]
    input_parameters: Dict[str, Any]
    status: str
    error: Optional[str]
    metadata: Annotated[Dict[str, Any], merge_dicts]


class LangGraphWorkflowEngine:
    """
    LangGraph-based workflow execution engine with database observability.

    This engine uses LangGraph's StateGraph for execution while maintaining
    full integration with the existing database schema for observability,
    audit logging, and UI integration.
    """

    def __init__(self, db_handler: WorkflowDBHandler, max_workers: int = 10):
        """
        Initialize the LangGraph workflow engine.

        Args:
            db_handler: Database handler for workflow operations
            max_workers: Maximum number of parallel worker threads
        """
        self.db_handler = db_handler
        self.max_workers = max_workers
        self.executor_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.active_graphs: Dict[str, StateGraph] = {}
        logger.info(f"LangGraph workflow engine initialized with {max_workers} workers")

    def start_execution(self, workflow_id: str, triggered_by: str,
                       input_parameters: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a new workflow execution using LangGraph.

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
            self.executor_pool.submit(self._execute_workflow_langgraph,
                                    execution_id, workflow, input_parameters)

            logger.info(f"Started LangGraph workflow execution: {execution_id}")
            return execution_id

        except Exception as e:
            logger.error(f"Error starting workflow execution: {e}")
            raise

    def _execute_workflow_langgraph(self, execution_id: str, workflow: Any,
                                   input_parameters: Optional[Dict[str, Any]]):
        """
        Execute a workflow using LangGraph's StateGraph.

        Args:
            execution_id: Execution ID
            workflow: Workflow definition
            input_parameters: Input parameters
        """
        try:
            # Update execution status to running
            self.db_handler.set_execution_started(execution_id)
            self._log_audit(execution_id, "INFO", "Workflow execution started with LangGraph")

            # Parse workflow definition
            definition = workflow.definition_json

            # Check if workflow has Python code or JSON definition
            if 'python_code' in definition:
                # Execute Python-defined workflow
                result = self._execute_python_workflow(
                    execution_id, definition, input_parameters)
            else:
                # Execute JSON-defined workflow
                result = self._execute_json_workflow(
                    execution_id, definition, input_parameters)

            # Update execution status to completed
            self.db_handler.update_execution_status(
                execution_id, ExecutionStatus.COMPLETED.value,
                completed_at=datetime.now(),
                output_results=result)

            self._log_audit(execution_id, "INFO", "Workflow execution completed successfully")

        except Exception as e:
            logger.error(f"Error executing workflow {execution_id}: {e}")
            self.db_handler.update_execution_status(
                execution_id, ExecutionStatus.FAILED.value,
                completed_at=datetime.now(),
                error_message=str(e))
            self._log_audit(execution_id, "ERROR", f"Workflow execution failed: {str(e)}")

    def _execute_json_workflow(self, execution_id: str, definition: Dict[str, Any],
                              input_parameters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute a JSON-defined workflow using LangGraph.

        Args:
            execution_id: Execution ID
            definition: Workflow definition dictionary
            input_parameters: Input parameters

        Returns:
            Execution results
        """
        nodes = definition.get('nodes', [])
        edges = definition.get('edges', [])
        variables = definition.get('variables', {})

        # Build LangGraph StateGraph from JSON definition
        graph = StateGraph(WorkflowState)

        # Initialize state
        initial_state = WorkflowState(
            execution_id=execution_id,
            workflow_id=definition.get('workflow_id', ''),
            current_node='start',
            messages=[],
            variables={**variables, **(input_parameters or {})},
            node_outputs={},
            input_parameters=input_parameters or {},
            status='running',
            error=None,
            metadata={}
        )

        # Add nodes to graph
        node_map = {node['node_id']: node for node in nodes}

        for node in nodes:
            node_id = node['node_id']
            node_type = node['node_type']

            if node_type == 'start':
                # Start node just passes state through without modifications
                graph.add_node(node_id, lambda state: {})
            elif node_type == 'end':
                # End node marks completion - only update status
                graph.add_node(node_id, lambda state: {'status': 'completed'})
            else:
                # Create node function with database tracking
                graph.add_node(
                    node_id,
                    self._create_node_function(execution_id, node)
                )

        # Add edges to graph
        for edge in edges:
            source = edge['source']
            target = edge['target']
            condition = edge.get('condition')

            if condition:
                # Conditional edge
                graph.add_conditional_edges(
                    source,
                    self._create_condition_function(condition),
                    {True: target, False: END}
                )
            else:
                # Regular edge
                graph.add_edge(source, target)

        # Set entry point
        start_node = next((n['node_id'] for n in nodes if n['node_type'] == 'start'), None)
        if start_node:
            graph.set_entry_point(start_node)

        # Set finish point
        end_nodes = [n['node_id'] for n in nodes if n['node_type'] == 'end']
        for end_node in end_nodes:
            graph.add_edge(end_node, END)

        # Compile and run the graph
        compiled_graph = graph.compile()
        self.active_graphs[execution_id] = compiled_graph

        # Execute the graph
        final_state = compiled_graph.invoke(initial_state)

        return {
            'node_outputs': final_state.get('node_outputs', {}),
            'variables': final_state.get('variables', {}),
            'status': final_state.get('status', 'completed')
        }

    def _execute_python_workflow(self, execution_id: str, definition: Dict[str, Any],
                                 input_parameters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute a Python-defined workflow using LangGraph.

        Args:
            execution_id: Execution ID
            definition: Workflow definition with Python code
            input_parameters: Input parameters

        Returns:
            Execution results
        """
        python_code = definition.get('python_code', '')

        # Create execution namespace
        namespace = {
            'StateGraph': StateGraph,
            'END': END,
            'execution_id': execution_id,
            'input_parameters': input_parameters or {},
            'db_handler': self.db_handler,
            '_create_node_function': self._create_node_function,
            '_log_audit': self._log_audit,
            'WorkflowState': WorkflowState,
        }

        # Execute Python code to build graph
        exec(python_code, namespace)

        # Get the compiled graph from namespace
        compiled_graph = namespace.get('compiled_graph')
        if not compiled_graph:
            raise ValueError("Python code must define 'compiled_graph' variable")

        self.active_graphs[execution_id] = compiled_graph

        # Initialize state
        initial_state = namespace.get('initial_state', WorkflowState(
            execution_id=execution_id,
            workflow_id=definition.get('workflow_id', ''),
            current_node='start',
            messages=[],
            variables=input_parameters or {},
            node_outputs={},
            input_parameters=input_parameters or {},
            status='running',
            error=None,
            metadata={}
        ))

        # Execute the graph
        final_state = compiled_graph.invoke(initial_state)

        return {
            'node_outputs': final_state.get('node_outputs', {}),
            'variables': final_state.get('variables', {}),
            'status': final_state.get('status', 'completed')
        }

    def _create_node_function(self, execution_id: str, node: Dict[str, Any]):
        """
        Create a node function that executes the node and tracks in database.

        Args:
            execution_id: Execution ID
            node: Node definition

        Returns:
            Node function for LangGraph
        """
        node_id = node['node_id']
        node_type = node['node_type']

        def node_function(state: WorkflowState) -> WorkflowState:
            """Execute node and update state"""
            # Create node execution record
            node_execution_id = NodeExecution.generate_id()
            node_execution = NodeExecution(
                node_execution_id=node_execution_id,
                execution_id=execution_id,
                node_id=node_id,
                node_type=node_type,
                status=NodeExecutionStatus.RUNNING.value,
                started_at=datetime.now(),
                input_data=state.get('variables', {})
            )
            self.db_handler.create_node_execution(node_execution)

            start_time = datetime.now()

            try:
                # Execute node based on type
                if node_type == 'llm':
                    output = self._execute_llm_node(node, state)
                elif node_type == 'tool':
                    output = self._execute_tool_node(node, state)
                elif node_type == 'human':
                    output = self._execute_human_node(execution_id, node_execution_id, node, state)
                elif node_type == 'conditional':
                    output = self._execute_conditional_node(node, state)
                elif node_type == 'parallel':
                    output = self._execute_parallel_node(node, state)
                else:
                    output = {'status': 'completed', 'message': f'Node {node_id} executed'}

                # Calculate duration
                end_time = datetime.now()
                duration_ms = int((end_time - start_time).total_seconds() * 1000)

                # Update node execution as completed
                self.db_handler.set_node_completed(
                    node_execution_id,
                    output_data=output,
                    duration_ms=duration_ms
                )

                # Update state - ONLY return fields that changed
                # LangGraph will merge these updates using the reducers defined in WorkflowState

                # Log success
                self._log_audit(
                    execution_id, "INFO",
                    f"Node {node_id} completed successfully",
                    {'node_type': node_type, 'duration_ms': duration_ms}
                )

                # Note: We don't update 'current_node' here to allow parallel branches
                # to execute without conflicts. current_node will be set by sequential nodes.
                return {
                    'node_outputs': {node_id: output},
                    'messages': [AIMessage(content=f"Completed node {node_id}")]
                }

            except Exception as e:
                # Update node execution with error
                end_time = datetime.now()
                duration_ms = int((end_time - start_time).total_seconds() * 1000)

                # Update node execution as failed
                self.db_handler.set_node_failed(
                    node_execution_id,
                    error_details={'error': str(e), 'error_type': type(e).__name__}
                )

                self._log_audit(
                    execution_id, "ERROR",
                    f"Node {node_id} failed: {str(e)}",
                    {'node_type': node_type}
                )

                raise

        return node_function

    def _execute_llm_node(self, node: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute an LLM node"""
        config = node.get('config', {})
        prompt = config.get('prompt', '')
        model = config.get('model', 'claude-3-sonnet')

        # Replace variables in prompt
        for key, value in state.get('variables', {}).items():
            prompt = prompt.replace(f'{{{{{key}}}}}', str(value))

        # TODO: Integrate with actual LLM facade
        return {
            'status': 'completed',
            'prompt': prompt,
            'response': f'LLM response from {model}',
            'model': model
        }

    def _execute_tool_node(self, node: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute a tool node"""
        config = node.get('config', {})
        tool_name = config.get('tool_name', '')
        parameters = config.get('parameters', {})

        try:
            from workflow_management.example_tools import get_tool

            # Get tool instance
            tool = get_tool(tool_name)

            # Resolve parameter variables from state
            resolved_params = {}
            for key, value in parameters.items():
                if isinstance(value, str) and value.startswith('{{') and value.endswith('}}'):
                    var_name = value[2:-2].strip()
                    resolved_params[key] = state.get('variables', {}).get(var_name, value)
                else:
                    resolved_params[key] = value

            # Execute tool
            result = tool._execute_with_tracking(**resolved_params)

            if result.success:
                return {
                    'status': 'completed',
                    'tool': tool_name,
                    'result': result.data,
                    'execution_time': result.execution_time
                }
            else:
                return {
                    'status': 'failed',
                    'tool': tool_name,
                    'error': result.error
                }
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                'status': 'failed',
                'tool': tool_name,
                'error': str(e)
            }

    def _execute_human_node(self, execution_id: str, node_execution_id: str,
                           node: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute a human-in-the-loop node"""
        config = node.get('config', {})

        # Create human task
        task_id = HumanTask.generate_id()
        task = HumanTask(
            task_id=task_id,
            execution_id=execution_id,
            node_execution_id=node_execution_id,
            assigned_to=config.get('assigned_to', 'admin'),
            task_type=config.get('task_type', 'approval'),
            status=TaskStatus.PENDING.value,
            created_at=datetime.now(),
            timeout_at=datetime.now() if config.get('timeout') else None
        )

        self.db_handler.create_human_task(task)

        self._log_audit(
            execution_id, "INFO",
            f"Human task created: {task_id}",
            {'assigned_to': task.assigned_to, 'task_type': task.task_type}
        )

        # Wait for human response (in real implementation, this would be async)
        return {
            'status': 'waiting_for_human',
            'task_id': task_id,
            'assigned_to': task.assigned_to,
            'task_type': task.task_type
        }

    def _execute_conditional_node(self, node: Dict[str, Any],
                                  state: WorkflowState) -> Dict[str, Any]:
        """Execute a conditional node"""
        config = node.get('config', {})
        condition = config.get('condition', '')

        result = self._evaluate_condition(condition, state)
        return {
            'status': 'completed',
            'condition': condition,
            'result': result
        }

    def _execute_parallel_node(self, node: Dict[str, Any],
                              state: WorkflowState) -> Dict[str, Any]:
        """Execute a parallel node"""
        # Parallel execution is handled by LangGraph's concurrent execution
        return {
            'status': 'completed',
            'message': 'Parallel node executed'
        }

    def _create_condition_function(self, condition: str):
        """Create a condition function for conditional edges"""
        def condition_func(state: WorkflowState) -> bool:
            try:
                return eval(condition, {}, state)
            except Exception as e:
                logger.warning(f"Error evaluating condition '{condition}': {e}")
                return False
        return condition_func

    def _evaluate_condition(self, condition: str, state: WorkflowState) -> bool:
        """Evaluate a condition expression"""
        if not condition:
            return True

        try:
            return eval(condition, {}, state)
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
            source='langgraph_engine'
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
        logger.info("Shutting down LangGraph workflow execution engine")
        self.executor_pool.shutdown(wait=True)