"""
Workflow Executor - Execute DAG-based workflows.

Supports two execution modes:
1. Native execution (original implementation)
2. LangGraph execution (recommended for complex workflows)

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import json
import logging
import time
import uuid
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from .dag_parser import DAGParser, DAGWorkflow, DAGNode
from .node_types import NodeFactory, NodeResult, BaseNode

logger = logging.getLogger(__name__)


@dataclass
class ExecutionStep:
    """Record of a single step execution."""
    step_number: int
    node_id: str
    node_type: str
    status: str
    input_data: Any = None
    output_data: Any = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: int = 0


@dataclass
class WorkflowExecution:
    """Complete workflow execution record."""
    execution_id: str
    workflow_id: str
    status: str = 'pending'
    input_data: Any = None
    output_data: Any = None
    error_message: Optional[str] = None
    steps: List[ExecutionStep] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'execution_id': self.execution_id,
            'workflow_id': self.workflow_id,
            'status': self.status,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'error_message': self.error_message,
            'steps': [
                {
                    'step_number': s.step_number,
                    'node_id': s.node_id,
                    'node_type': s.node_type,
                    'status': s.status,
                    'duration_ms': s.duration_ms,
                    'error_message': s.error_message
                }
                for s in self.steps
            ],
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_ms': self.duration_ms,
            'metadata': self.metadata
        }


class WorkflowExecutor:
    """
    Execute DAG-based workflows with support for:
    - Sequential and parallel node execution
    - Python code execution
    - LLM integration via LangChain
    - HTTP calls
    - Condition branching
    - Step-by-step execution tracking
    - LangGraph execution mode for complex workflows
    """
    
    def __init__(self, db_facade=None, llm_facade=None, user_id: str = None,
                 use_langgraph: bool = True):
        """
        Initialize workflow executor.
        
        Args:
            db_facade: Database facade for logging executions
            llm_facade: LLM facade for LLM node execution (legacy)
            user_id: User ID for audit logging
            use_langgraph: Whether to use LangGraph for execution (default: True)
        """
        self.db_facade = db_facade
        self.llm_facade = llm_facade
        self.user_id = user_id or 'system'
        self.parser = DAGParser()
        self.max_workers = 4
        self.use_langgraph = use_langgraph
        self._execution_callbacks: List[Callable] = []
        
        # Initialize LangGraph executor if enabled
        self._langgraph_executor = None
        if use_langgraph and db_facade:
            try:
                from ..langchain.workflow_graph import WorkflowGraphExecutor
                self._langgraph_executor = WorkflowGraphExecutor(db_facade)
                logger.info("LangGraph workflow executor initialized")
            except ImportError as e:
                logger.warning(f"LangGraph not available, using native execution: {e}")
                self.use_langgraph = False
    
    def execute_workflow(self, workflow: DAGWorkflow, 
                        input_data: Dict[str, Any] = None) -> WorkflowExecution:
        """
        Execute a complete workflow.
        
        Args:
            workflow: DAGWorkflow to execute
            input_data: Input data for the workflow
            
        Returns:
            WorkflowExecution with results
        """
        # Use LangGraph if available and enabled
        if self.use_langgraph and self._langgraph_executor:
            return self._execute_with_langgraph(workflow, input_data)
        
        # Fall back to native execution
        return self._execute_native(workflow, input_data)
    
    def _execute_with_langgraph(self, workflow: DAGWorkflow,
                                input_data: Dict[str, Any] = None) -> WorkflowExecution:
        """Execute workflow using LangGraph."""
        execution = WorkflowExecution(
            execution_id=str(uuid.uuid4()),
            workflow_id=workflow.workflow_id,
            status='running',
            input_data=input_data,
            started_at=datetime.now(),
            metadata={'execution_mode': 'langgraph'}
        )
        
        logger.info(f"Starting LangGraph workflow execution: {execution.execution_id}")
        
        try:
            # Convert workflow to LangGraph config format
            workflow_config = self._workflow_to_langgraph_config(workflow)
            
            # Create and execute graph
            from ..langchain.workflow_graph import create_workflow_graph
            
            graph = create_workflow_graph(
                workflow_config,
                self.db_facade
            )
            
            # Prepare initial state
            initial_state = {
                "input": input_data or {},
                "output": None,
                "current_node": "",
                "executed_nodes": [],
                "node_outputs": {},
                "error": None,
                "status": "running",
                "context": {},
                "variables": {},
                "hitl_pending": False,
                "hitl_message": None,
                "hitl_response": None,
                "execution_id": execution.execution_id,
                "workflow_id": workflow.workflow_id,
                "started_at": datetime.now().isoformat(),
                "messages": []
            }
            
            # Execute graph
            start_time = time.time()
            final_state = graph.invoke(initial_state)
            execution.duration_ms = int((time.time() - start_time) * 1000)
            
            # Extract results
            execution.output_data = final_state.get('output')
            execution.metadata['node_outputs'] = final_state.get('node_outputs', {})
            execution.metadata['executed_nodes'] = final_state.get('executed_nodes', [])
            
            # Create execution steps from executed nodes
            for i, node_id in enumerate(final_state.get('executed_nodes', [])):
                step = ExecutionStep(
                    step_number=i + 1,
                    node_id=node_id,
                    node_type='langgraph_node',
                    status='completed',
                    output_data=final_state.get('node_outputs', {}).get(node_id),
                    completed_at=datetime.now()
                )
                execution.steps.append(step)
            
            if final_state.get('error'):
                execution.status = 'failed'
                execution.error_message = final_state['error']
            elif final_state.get('hitl_pending'):
                execution.status = 'waiting_for_human'
                execution.metadata['hitl_message'] = final_state.get('hitl_message')
            else:
                execution.status = 'completed'
            
            execution.completed_at = datetime.now()
            
        except Exception as e:
            logger.error(f"LangGraph workflow execution failed: {e}", exc_info=True)
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.completed_at = datetime.now()
            execution.duration_ms = int((datetime.now() - execution.started_at).total_seconds() * 1000)
        
        # Log execution to database
        self._save_execution(execution)
        
        return execution
    
    def _workflow_to_langgraph_config(self, workflow: DAGWorkflow) -> Dict:
        """Convert DAGWorkflow to LangGraph configuration format."""
        nodes = []
        edges = []
        
        logger.debug(f"Converting workflow to LangGraph config: {workflow.workflow_id}")
        logger.debug(f"Workflow has {len(workflow.nodes)} nodes and {len(workflow.edges)} edges")
        
        for node in workflow.nodes.values():
            node_config = {
                'id': node.node_id,
                'type': node.node_type,
                'name': node.name,
                'config': node.config or {}
            }
            nodes.append(node_config)
            logger.debug(f"Node: id={node.node_id}, type={node.node_type}, name={node.name}")
        
        for edge in workflow.edges:
            # Handle both dict format and object format for edges
            if isinstance(edge, dict):
                edge_config = {
                    'source': edge.get('source') or edge.get('source_id'),
                    'target': edge.get('target') or edge.get('target_id'),
                }
                if edge.get('condition'):
                    edge_config['condition'] = edge.get('condition')
            else:
                edge_config = {
                    'source': edge.source_id,
                    'target': edge.target_id
                }
                if edge.condition:
                    edge_config['condition'] = edge.condition
            edges.append(edge_config)
            logger.debug(f"Edge: {edge_config.get('source')} -> {edge_config.get('target')}")
        
        config = {
            'nodes': nodes,
            'edges': edges,
            'metadata': workflow.metadata
        }
        
        logger.info(f"LangGraph config: {len(nodes)} nodes, {len(edges)} edges")
        return config
    
    def _execute_native(self, workflow: DAGWorkflow,
                       input_data: Dict[str, Any] = None) -> WorkflowExecution:
        """
        Execute a complete workflow.
        
        Args:
            workflow: DAGWorkflow to execute
            input_data: Input data for the workflow
            
        Returns:
            WorkflowExecution with results
        """
        execution = WorkflowExecution(
            execution_id=str(uuid.uuid4()),
            workflow_id=workflow.workflow_id,
            status='running',
            input_data=input_data,
            started_at=datetime.now()
        )
        
        logger.info(f"Starting workflow execution: {execution.execution_id}")
        
        try:
            # Validate workflow
            errors = workflow.validate()
            if errors:
                raise ValueError(f"Workflow validation failed: {errors}")
            
            # Initialize execution context
            context = {
                'input': input_data or {},
                'workflow': workflow,
                'execution_id': execution.execution_id,
                'node_outputs': {},
                'accumulated_output': {},
                'modules': {}
            }
            
            # Load Python modules if any
            if workflow.python_modules:
                context['modules'] = self._load_python_modules(workflow.python_modules)
            
            # Get execution order
            execution_order = workflow.get_execution_order()
            logger.info(f"Execution order: {execution_order}")
            
            # Execute nodes in order
            step_number = 0
            for node_id in execution_order:
                step_number += 1
                dag_node = workflow.nodes[node_id]
                
                step = self._execute_node(dag_node, context, step_number)
                execution.steps.append(step)
                
                if step.status == 'failed':
                    execution.status = 'failed'
                    execution.error_message = step.error_message
                    break
                
                # Store node output for downstream nodes
                context['node_outputs'][node_id] = step.output_data
                context['accumulated_output'][node_id] = step.output_data
                
                # Update context input for next node
                context['input'] = step.output_data
                
                # Notify callbacks
                self._notify_callbacks('step_completed', step, execution)
            
            # Set final status
            if execution.status != 'failed':
                execution.status = 'completed'
                # Get output from output node or last node
                output_nodes = [n for n in workflow.nodes.values() if n.node_type == 'output']
                if output_nodes:
                    execution.output_data = context['node_outputs'].get(output_nodes[0].node_id)
                else:
                    execution.output_data = context['accumulated_output']
            
        except Exception as e:
            logger.error(f"Workflow execution error: {e}", exc_info=True)
            execution.status = 'failed'
            execution.error_message = str(e)
        
        finally:
            execution.completed_at = datetime.now()
            execution.duration_ms = int(
                (execution.completed_at - execution.started_at).total_seconds() * 1000
            )
            
            # Save to database
            if self.db_facade:
                self._save_execution(execution)
            
            logger.info(f"Workflow execution completed: {execution.execution_id} - {execution.status}")
        
        return execution
    
    def execute_from_json(self, json_str: str, 
                         input_data: Dict[str, Any] = None) -> WorkflowExecution:
        """
        Parse and execute a workflow from JSON.
        
        Args:
            json_str: JSON workflow definition
            input_data: Input data for the workflow
            
        Returns:
            WorkflowExecution with results
        """
        workflow = self.parser.parse_json(json_str)
        
        if not workflow:
            execution = WorkflowExecution(
                execution_id=str(uuid.uuid4()),
                workflow_id='unknown',
                status='failed',
                error_message=f"Failed to parse workflow: {self.parser.get_errors()}",
                started_at=datetime.now(),
                completed_at=datetime.now()
            )
            return execution
        
        return self.execute_workflow(workflow, input_data)
    
    def execute_from_dict(self, workflow_dict: Dict[str, Any],
                         input_data: Dict[str, Any] = None) -> WorkflowExecution:
        """
        Parse and execute a workflow from dictionary.
        
        Args:
            workflow_dict: Workflow definition as dictionary
            input_data: Input data for the workflow
            
        Returns:
            WorkflowExecution with results
        """
        workflow = self.parser.parse_dict(workflow_dict)
        
        if not workflow:
            execution = WorkflowExecution(
                execution_id=str(uuid.uuid4()),
                workflow_id='unknown',
                status='failed',
                error_message=f"Failed to parse workflow: {self.parser.get_errors()}",
                started_at=datetime.now(),
                completed_at=datetime.now()
            )
            return execution
        
        return self.execute_workflow(workflow, input_data)
    
    def _execute_node(self, dag_node: DAGNode, context: Dict[str, Any], 
                     step_number: int) -> ExecutionStep:
        """Execute a single node."""
        step = ExecutionStep(
            step_number=step_number,
            node_id=dag_node.node_id,
            node_type=dag_node.node_type,
            status='running',
            input_data=context.get('input'),
            started_at=datetime.now()
        )
        
        try:
            # Create node instance
            node = NodeFactory.create(
                node_type=dag_node.node_type,
                node_id=dag_node.node_id,
                name=dag_node.name,
                config=dag_node.config,
                python_code=dag_node.python_code,
                llm_facade=self.llm_facade
            )
            
            # Execute node
            result = node.execute(context)
            
            step.output_data = result.output
            step.duration_ms = result.duration_ms
            
            if result.success:
                step.status = 'completed'
            else:
                step.status = 'failed'
                step.error_message = result.error
            
            # Log LLM calls if applicable
            if dag_node.node_type == 'llm' and self.db_facade:
                self._log_llm_call(context, dag_node, result)
            
        except Exception as e:
            logger.error(f"Node execution error ({dag_node.node_id}): {e}", exc_info=True)
            step.status = 'failed'
            step.error_message = str(e)
        
        finally:
            step.completed_at = datetime.now()
            if step.duration_ms == 0:
                step.duration_ms = int(
                    (step.completed_at - step.started_at).total_seconds() * 1000
                )
        
        return step
    
    def _load_python_modules(self, modules: Dict[str, str]) -> Dict[str, Any]:
        """
        Load Python modules from code strings or URIs.
        
        Supports:
        - Inline code strings
        - db://<fragment_id> - Load from database code_fragments table
        - file://<path> - Load from local filesystem
        - s3://<bucket>/<key> - Load from AWS S3
        
        Args:
            modules: Dict mapping module names to code strings or URIs
            
        Returns:
            Dict of loaded module namespaces
        """
        from abhikarta.utils.code_loader import CodeLoader
        
        # Initialize code loader
        code_loader = CodeLoader(db_facade=self.db_facade)
        loaded = {}
        
        for name, code_or_uri in modules.items():
            try:
                # Resolve URI if needed
                code = code_loader.resolve_uri(code_or_uri)
                
                if not code:
                    logger.warning(f"Failed to load module {name} from {code_or_uri}")
                    continue
                
                # Execute the code to create module namespace
                module_namespace = {}
                exec(code, {'__builtins__': __builtins__}, module_namespace)
                loaded[name] = module_namespace
                logger.debug(f"Loaded module: {name}")
                
            except Exception as e:
                logger.warning(f"Failed to load module {name}: {e}")
        
        return loaded
    
    def _save_execution(self, execution: WorkflowExecution):
        """Save execution to database."""
        try:
            # Save main execution record
            self.db_facade.execute("""
                INSERT INTO executions (
                    execution_id, agent_id, user_id, status,
                    input_data, output_data, error_message,
                    started_at, completed_at, duration_ms, trace_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                execution.execution_id,
                execution.workflow_id,
                self.user_id,
                execution.status,
                json.dumps(execution.input_data),
                json.dumps(execution.output_data),
                execution.error_message,
                execution.started_at.isoformat() if execution.started_at else None,
                execution.completed_at.isoformat() if execution.completed_at else None,
                execution.duration_ms,
                json.dumps([s.__dict__ for s in execution.steps], default=str)
            ))
            
            # Save individual steps
            for step in execution.steps:
                self.db_facade.execute("""
                    INSERT INTO execution_steps (
                        execution_id, step_number, node_id, node_type,
                        status, input_data, output_data, error_message,
                        started_at, completed_at, duration_ms
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    execution.execution_id,
                    step.step_number,
                    step.node_id,
                    step.node_type,
                    step.status,
                    json.dumps(step.input_data) if step.input_data else None,
                    json.dumps(step.output_data) if step.output_data else None,
                    step.error_message,
                    step.started_at.isoformat() if step.started_at else None,
                    step.completed_at.isoformat() if step.completed_at else None,
                    step.duration_ms
                ))
                
        except Exception as e:
            logger.error(f"Failed to save execution: {e}", exc_info=True)
    
    def _log_llm_call(self, context: Dict[str, Any], dag_node: DAGNode, 
                     result: NodeResult):
        """Log LLM call to database."""
        try:
            call_id = str(uuid.uuid4())
            self.db_facade.execute("""
                INSERT INTO llm_calls (
                    call_id, execution_id, agent_id, user_id,
                    provider, model, request_type,
                    system_prompt, user_prompt, response_content,
                    input_tokens, output_tokens, total_tokens,
                    latency_ms, status, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                call_id,
                context.get('execution_id'),
                context.get('workflow', {}).workflow_id if hasattr(context.get('workflow', {}), 'workflow_id') else None,
                self.user_id,
                dag_node.config.get('provider', 'openai'),
                dag_node.config.get('model', 'gpt-4o'),
                'completion',
                dag_node.config.get('system_prompt'),
                dag_node.config.get('user_prompt'),
                json.dumps(result.output) if result.output else None,
                result.metadata.get('input_tokens', 0) if result.metadata else 0,
                result.metadata.get('output_tokens', 0) if result.metadata else 0,
                result.metadata.get('tokens_used', 0) if result.metadata else 0,
                result.duration_ms,
                'success' if result.success else 'failed',
                json.dumps(result.metadata) if result.metadata else '{}'
            ))
        except Exception as e:
            logger.error(f"Failed to log LLM call: {e}", exc_info=True)
    
    def add_callback(self, callback: Callable):
        """Add execution callback."""
        self._execution_callbacks.append(callback)
    
    def _notify_callbacks(self, event: str, *args):
        """Notify all callbacks."""
        for callback in self._execution_callbacks:
            try:
                callback(event, *args)
            except Exception as e:
                logger.warning(f"Callback error: {e}")


class WorkflowManager:
    """
    Manage workflow definitions and executions.
    """
    
    def __init__(self, db_facade, llm_facade=None):
        self.db_facade = db_facade
        self.llm_facade = llm_facade
        self.parser = DAGParser()
    
    def create_workflow(self, name: str, description: str, 
                       dag_definition: Dict[str, Any],
                       python_modules: Dict[str, str] = None,
                       created_by: str = 'system') -> Optional[str]:
        """Create a new workflow."""
        workflow_id = str(uuid.uuid4())[:8]
        
        try:
            self.db_facade.execute("""
                INSERT INTO workflows (
                    workflow_id, name, description, dag_definition,
                    python_modules, created_by
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                workflow_id,
                name,
                description,
                json.dumps(dag_definition),
                json.dumps(python_modules or {}),
                created_by
            ))
            return workflow_id
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}", exc_info=True)
            return None
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow by ID."""
        result = self.db_facade.fetch_one(
            "SELECT * FROM workflows WHERE workflow_id = ?",
            (workflow_id,)
        )
        if result:
            result['dag_definition'] = json.loads(result.get('dag_definition', '{}'))
            result['python_modules'] = json.loads(result.get('python_modules', '{}'))
        return result
    
    def list_workflows(self, status: str = None) -> List[Dict[str, Any]]:
        """List all workflows."""
        if status:
            results = self.db_facade.fetch_all(
                "SELECT * FROM workflows WHERE status = ? ORDER BY created_at DESC",
                (status,)
            )
        else:
            results = self.db_facade.fetch_all(
                "SELECT * FROM workflows ORDER BY created_at DESC"
            )
        return results or []
    
    def execute_workflow(self, workflow_id: str, 
                        input_data: Dict[str, Any] = None,
                        user_id: str = 'system') -> WorkflowExecution:
        """Execute a stored workflow."""
        workflow_data = self.get_workflow(workflow_id)
        
        if not workflow_data:
            return WorkflowExecution(
                execution_id=str(uuid.uuid4()),
                workflow_id=workflow_id,
                status='failed',
                error_message=f"Workflow not found: {workflow_id}",
                started_at=datetime.now(),
                completed_at=datetime.now()
            )
        
        # Parse workflow
        dag_def = workflow_data['dag_definition']
        dag_def['workflow_id'] = workflow_id
        dag_def['name'] = workflow_data['name']
        dag_def['python_modules'] = workflow_data.get('python_modules', {})
        
        workflow = self.parser.parse_dict(dag_def)
        
        if not workflow:
            return WorkflowExecution(
                execution_id=str(uuid.uuid4()),
                workflow_id=workflow_id,
                status='failed',
                error_message=f"Failed to parse workflow: {self.parser.get_errors()}",
                started_at=datetime.now(),
                completed_at=datetime.now()
            )
        
        # Execute
        executor = WorkflowExecutor(self.db_facade, self.llm_facade, user_id)
        execution = executor.execute_workflow(workflow, input_data)
        
        # Update workflow stats
        try:
            self.db_facade.execute("""
                UPDATE workflows SET 
                    last_executed_at = CURRENT_TIMESTAMP,
                    execution_count = execution_count + 1
                WHERE workflow_id = ?
            """, (workflow_id,))
        except:
            pass
        
        return execution
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow."""
        try:
            self.db_facade.execute(
                "DELETE FROM workflows WHERE workflow_id = ?",
                (workflow_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete workflow: {e}", exc_info=True)
            return False
