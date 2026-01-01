"""
LangGraph Workflow Executor - Execute DAG workflows using LangGraph.

LangGraph provides a framework for building stateful, multi-step workflows
with support for:
- Conditional branching
- Parallel execution
- State management
- Human-in-the-loop
- Checkpointing and resumption

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import json
import logging
import time
import uuid
from typing import Dict, Any, Optional, List, Callable, TypedDict, Annotated, Union
from datetime import datetime
from dataclasses import dataclass, field
from operator import add

logger = logging.getLogger(__name__)


# ============================================================================
# Reducer Functions for Concurrent State Updates
# ============================================================================

def last_value(current: Any, new: Any) -> Any:
    """Reducer that keeps the last value (for concurrent updates)."""
    return new


def merge_dicts(current: Dict, new: Dict) -> Dict:
    """Reducer that merges dictionaries (for concurrent updates)."""
    if current is None:
        current = {}
    if new is None:
        return current
    result = dict(current)
    result.update(new)
    return result


def keep_first_error(current: Optional[str], new: Optional[str]) -> Optional[str]:
    """Reducer that keeps the first error encountered."""
    if current:
        return current
    return new


# ============================================================================
# State Definition
# ============================================================================

class WorkflowState(TypedDict, total=False):
    """
    State that flows through the LangGraph workflow.
    
    Each node can read and modify this state. The state is persisted
    and can be checkpointed for resumption.
    
    Fields with Annotated types use reducers to handle concurrent updates
    from parallel node execution.
    """
    # Input/Output - use reducers for concurrent access
    input: Any
    output: Annotated[Any, last_value]
    
    # Execution tracking - concurrent updates possible
    current_node: Annotated[str, last_value]
    executed_nodes: Annotated[List[str], add]
    node_outputs: Annotated[Dict[str, Any], merge_dicts]
    
    # Error handling - keep first error
    error: Annotated[Optional[str], keep_first_error]
    status: Annotated[str, last_value]  # running, completed, failed, waiting_for_human
    
    # Context - merge for concurrent updates
    context: Annotated[Dict[str, Any], merge_dicts]
    variables: Annotated[Dict[str, Any], merge_dicts]
    
    # Human-in-the-loop
    hitl_pending: Annotated[bool, last_value]
    hitl_message: Annotated[Optional[str], last_value]
    hitl_response: Annotated[Optional[str], last_value]
    
    # Metadata - typically not updated concurrently
    execution_id: str
    workflow_id: str
    started_at: str
    
    # Messages (for chat-based workflows)
    messages: Annotated[List[Dict], add]


# ============================================================================
# Workflow Execution Result
# ============================================================================

@dataclass
class WorkflowExecutionResult:
    """Result of a LangGraph workflow execution."""
    execution_id: str
    workflow_id: str
    status: str = 'pending'
    input_data: Any = None
    output: Any = None
    node_outputs: Dict[str, Any] = field(default_factory=dict)
    executed_nodes: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: int = 0
    checkpoints: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'execution_id': self.execution_id,
            'workflow_id': self.workflow_id,
            'status': self.status,
            'input_data': self.input_data,
            'output': self.output,
            'node_outputs': self.node_outputs,
            'executed_nodes': self.executed_nodes,
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_ms': self.duration_ms,
            'metadata': self.metadata
        }


# ============================================================================
# Node Implementations
# ============================================================================

class LangGraphNodeFactory:
    """
    Factory for creating LangGraph node functions from workflow node configurations.
    """
    
    def __init__(self, db_facade, llm_factory=None, tool_factory=None):
        self.db_facade = db_facade
        self.llm_factory = llm_factory
        self.tool_factory = tool_factory
    
    def create_node_function(self, node_config: Dict) -> Callable:
        """
        Create a LangGraph node function from configuration.
        
        Args:
            node_config: Node configuration from workflow definition
            
        Returns:
            Callable that takes WorkflowState and returns updated state
        """
        node_type = node_config.get('type', 'passthrough')
        
        creator_method = getattr(self, f'_create_{node_type}_node', None)
        if creator_method:
            return creator_method(node_config)
        else:
            return self._create_passthrough_node(node_config)
    
    def _create_passthrough_node(self, config: Dict) -> Callable:
        """Create a passthrough node that just passes state through."""
        node_id = config.get('id', 'unknown')
        
        def passthrough_node(state: WorkflowState) -> Dict:
            logger.debug(f"Passthrough node: {node_id}")
            return {
                "current_node": node_id,
                "executed_nodes": [node_id]
            }
        
        return passthrough_node
    
    def _create_llm_node(self, config: Dict) -> Callable:
        """Create an LLM call node."""
        from .llm_factory import get_langchain_llm
        
        node_id = config.get('id', 'llm')
        node_config = config.get('config', {})
        
        def llm_node(state: WorkflowState) -> Dict:
            logger.info(f"Executing LLM node: {node_id}")
            
            try:
                # Get model and provider IDs - handle both naming conventions
                model_id = node_config.get('model_id') or node_config.get('model')
                provider_id = node_config.get('provider_id') or node_config.get('provider')
                
                # Get LLM
                llm = get_langchain_llm(
                    self.db_facade,
                    model_id=model_id,
                    provider_id=provider_id
                )
                
                # Build messages
                messages = []
                
                if node_config.get('system_prompt'):
                    messages.append(("system", node_config['system_prompt']))
                
                # Get input from state - handle various input formats
                input_key = node_config.get('input_key', 'input')
                raw_input = state.get(input_key, state.get('input', ''))
                
                # Extract actual input value intelligently
                input_value = self._extract_input_value(raw_input, state)
                
                logger.info(f"[NODE:{node_id}] Raw input type: {type(raw_input).__name__}")
                logger.info(f"[NODE:{node_id}] Extracted input value: {str(input_value)[:200]}...")
                
                # Apply template if configured
                prompt_template = node_config.get('prompt_template', '{input}')
                try:
                    prompt = prompt_template.format(
                        input=input_value,
                        **state.get('variables', {}),
                        **state.get('node_outputs', {})
                    )
                except KeyError as e:
                    # If template variable not found, use input directly
                    prompt = str(input_value)
                    logger.warning(f"[NODE:{node_id}] Template formatting failed: {e}, using raw input")
                
                messages.append(("human", prompt))
                
                logger.info(f"[NODE:{node_id}] LLM Input prompt: {prompt[:500]}...")
                
                # Invoke LLM
                response = llm.invoke(messages)
                output = response.content if hasattr(response, 'content') else str(response)
                
                logger.info(f"[NODE:{node_id}] LLM Output: {output[:500]}...")
                
                # Store output
                output_key = node_config.get('output_key', node_id)
                
                return {
                    "current_node": node_id,
                    "executed_nodes": [node_id],
                    "node_outputs": {output_key: output},
                    "output": output
                }
                
            except Exception as e:
                logger.error(f"LLM node {node_id} failed: {e}")
                return {
                    "current_node": node_id,
                    "executed_nodes": [node_id],
                    "error": str(e),
                    "status": "failed"
                }
        
        return llm_node
    
    def _extract_input_value(self, raw_input: Any, state: Dict) -> str:
        """
        Extract the actual input value from various formats.
        
        Handles:
        - String input: returns as-is
        - Dict with known keys: extracts value from 'query', 'text', 'input', 'message', 'prompt'
        - Dict from previous node: looks in node_outputs
        - Empty dict: looks for input in state variables
        """
        import json
        
        # If it's already a string, return it
        if isinstance(raw_input, str):
            if raw_input.strip():
                return raw_input
            # Empty string - try to find input elsewhere
        
        # If it's a dict, try to extract meaningful content
        if isinstance(raw_input, dict):
            # Check for common input keys
            for key in ['query', 'text', 'input', 'message', 'prompt', 'question', 'content', 'data']:
                if key in raw_input and raw_input[key]:
                    value = raw_input[key]
                    if isinstance(value, str):
                        return value
                    else:
                        return json.dumps(value, indent=2)
            
            # If dict is not empty but has no common keys, serialize it nicely
            if raw_input:
                return json.dumps(raw_input, indent=2)
        
        # Try to get input from node_outputs (previous node's output)
        node_outputs = state.get('node_outputs', {})
        if node_outputs:
            # Get the most recent output
            for key in reversed(list(node_outputs.keys())):
                value = node_outputs[key]
                if value:
                    if isinstance(value, str):
                        return value
                    elif isinstance(value, dict):
                        # Try to extract from dict
                        for subkey in ['output', 'result', 'data', 'text', 'content']:
                            if subkey in value and value[subkey]:
                                return str(value[subkey])
                        return json.dumps(value, indent=2)
                    else:
                        return str(value)
        
        # Try variables
        variables = state.get('variables', {})
        for key in ['query', 'input', 'text', 'message']:
            if key in variables and variables[key]:
                return str(variables[key])
        
        # Last resort - return empty string with warning
        logger.warning("Could not extract meaningful input value from state")
        return str(raw_input) if raw_input else ""
    
    def _create_agent_node(self, config: Dict) -> Callable:
        """Create an agent execution node."""
        from .agents import AgentExecutor as LangChainAgentExecutor
        
        node_id = config.get('id', 'agent')
        node_config = config.get('config', {})
        
        def agent_node(state: WorkflowState) -> Dict:
            logger.info(f"Executing agent node: {node_id}")
            
            try:
                agent_id = node_config.get('agent_id')
                if not agent_id:
                    raise ValueError("Agent node requires agent_id in config")
                
                # Get input
                input_key = node_config.get('input_key', 'input')
                input_value = state.get(input_key, state.get('input', ''))
                
                # Execute agent
                executor = LangChainAgentExecutor(self.db_facade)
                result = executor.execute_agent(agent_id, input_value)
                
                output_key = node_config.get('output_key', node_id)
                
                return {
                    "current_node": node_id,
                    "executed_nodes": [node_id],
                    "node_outputs": {
                        output_key: result.output,
                        f"{output_key}_details": result.to_dict()
                    },
                    "output": result.output
                }
                
            except Exception as e:
                logger.error(f"Agent node {node_id} failed: {e}")
                return {
                    "current_node": node_id,
                    "executed_nodes": [node_id],
                    "error": str(e),
                    "status": "failed"
                }
        
        return agent_node
    
    def _create_tool_node(self, config: Dict) -> Callable:
        """Create a tool execution node."""
        from .tools import ToolFactory
        
        node_id = config.get('id', 'tool')
        node_config = config.get('config', {})
        
        def tool_node(state: WorkflowState) -> Dict:
            logger.info(f"Executing tool node: {node_id}")
            
            try:
                tool_name = node_config.get('tool_name')
                server_id = node_config.get('server_id')
                
                # Get tool factory
                factory = self.tool_factory or ToolFactory(self.db_facade)
                
                # Use get_tool_by_name which checks both built-in and MCP tools
                tool = factory.get_tool_by_name(tool_name, server_id)
                
                if not tool:
                    raise ValueError(f"Tool not found: {tool_name}")
                
                # Get input - extract meaningful value
                input_key = node_config.get('input_key', 'input')
                raw_input = state.get(input_key, state.get('input', {}))
                tool_input = self._extract_input_value(raw_input, state)
                
                logger.info(f"[NODE:{node_id}] Tool: {tool_name}, Input: {str(tool_input)[:200]}...")
                
                # Execute tool
                result = tool.invoke(tool_input)
                
                logger.info(f"[NODE:{node_id}] Tool output: {str(result)[:500]}...")
                
                output_key = node_config.get('output_key', node_id)
                
                return {
                    "current_node": node_id,
                    "executed_nodes": [node_id],
                    "node_outputs": {output_key: result},
                    "output": result
                }
                
            except Exception as e:
                logger.error(f"Tool node {node_id} failed: {e}")
                return {
                    "current_node": node_id,
                    "executed_nodes": [node_id],
                    "error": str(e),
                    "status": "failed"
                }
        
        return tool_node
    
    def _create_code_node(self, config: Dict) -> Callable:
        """Create a code execution node."""
        node_id = config.get('id', 'code')
        node_config = config.get('config', {})
        
        def code_node(state: WorkflowState) -> Dict:
            logger.info(f"Executing code node: {node_id}")
            
            try:
                code = node_config.get('code', '')
                
                # Get input value
                raw_input = state.get('input')
                input_value = self._extract_input_value(raw_input, state)
                
                logger.info(f"[NODE:{node_id}] Code input: {str(input_value)[:200]}...")
                logger.info(f"[NODE:{node_id}] Code to execute:\n{code[:500]}...")
                
                # Create execution context
                exec_globals = {
                    'state': state,
                    'input': state.get('input'),
                    'input_data': input_value,  # Add extracted input as input_data
                    'input_value': input_value,  # Also as input_value
                    'variables': state.get('variables', {}),
                    'node_outputs': state.get('node_outputs', {}),
                    'json': json,
                    'result': None,
                    'output': None  # Allow setting output directly
                }
                
                # Execute code
                exec(code, exec_globals)
                
                # Get result - check both 'result' and 'output'
                result = exec_globals.get('result') or exec_globals.get('output')
                output_key = node_config.get('output_key', node_id)
                
                logger.info(f"[NODE:{node_id}] Code output: {str(result)[:200] if result else 'None'}...")
                
                return {
                    "current_node": node_id,
                    "executed_nodes": [node_id],
                    "node_outputs": {output_key: result},
                    "output": result
                }
                
            except Exception as e:
                logger.error(f"Code node {node_id} failed: {e}")
                return {
                    "current_node": node_id,
                    "executed_nodes": [node_id],
                    "error": str(e),
                    "status": "failed"
                }
        
        return code_node
    
    def _create_condition_node(self, config: Dict) -> Callable:
        """Create a conditional node that evaluates conditions."""
        node_id = config.get('id', 'condition')
        node_config = config.get('config', {})
        
        def condition_node(state: WorkflowState) -> Dict:
            logger.info(f"Executing condition node: {node_id}")
            
            condition = node_config.get('condition', 'True')
            
            try:
                # Create evaluation context
                eval_context = {
                    'state': state,
                    'input': state.get('input'),
                    'output': state.get('output'),
                    'variables': state.get('variables', {}),
                    'node_outputs': state.get('node_outputs', {}),
                }
                
                result = eval(condition, {"__builtins__": {}}, eval_context)
                
                return {
                    "current_node": node_id,
                    "executed_nodes": [node_id],
                    "node_outputs": {node_id: result},
                    "variables": {f"{node_id}_result": result}
                }
                
            except Exception as e:
                logger.error(f"Condition node {node_id} failed: {e}")
                return {
                    "current_node": node_id,
                    "executed_nodes": [node_id],
                    "node_outputs": {node_id: False},
                    "error": str(e)
                }
        
        return condition_node
    
    def _create_hitl_node(self, config: Dict) -> Callable:
        """Create a human-in-the-loop node that creates a HITL task."""
        node_id = config.get('id', 'hitl')
        node_config = config.get('config', {})
        db_facade = self.db_facade
        
        def hitl_node(state: WorkflowState) -> Dict:
            logger.info(f"Executing HITL node: {node_id}")
            
            title = node_config.get('title', 'Human Review Required')
            message = node_config.get('message', 'Human input required')
            task_type = node_config.get('task_type', 'approval')
            priority = node_config.get('priority', 5)
            assigned_to = node_config.get('assigned_to')
            timeout_minutes = node_config.get('timeout_minutes', 1440)
            
            # Format message with state
            try:
                message = message.format(
                    input=state.get('input'),
                    output=state.get('output'),
                    **state.get('variables', {}),
                    **state.get('node_outputs', {})
                )
            except:
                pass
            
            # Create HITL task in database
            task_id = None
            try:
                from abhikarta.hitl import HITLManager
                
                manager = HITLManager(db_facade)
                task = manager.create_task(
                    title=title,
                    task_type=task_type,
                    description=message,
                    priority=priority,
                    execution_id=state.get('execution_id'),
                    workflow_id=state.get('workflow_id'),
                    node_id=node_id,
                    context={
                        'input': state.get('input'),
                        'output': state.get('output'),
                        'node_outputs': state.get('node_outputs', {})
                    },
                    request_data=state.get('output'),
                    input_schema=node_config.get('input_schema', {}),
                    assigned_to=assigned_to,
                    timeout_minutes=timeout_minutes,
                    created_by='workflow'
                )
                task_id = task.task_id
                logger.info(f"Created HITL task: {task_id}")
                
            except Exception as e:
                logger.error(f"Failed to create HITL task: {e}")
            
            return {
                "current_node": node_id,
                "executed_nodes": [node_id],
                "hitl_pending": True,
                "hitl_message": message,
                "hitl_task_id": task_id,
                "status": "waiting_for_human",
                "node_outputs": {node_id: {"task_id": task_id, "message": message}}
            }
        
        return hitl_node
    
    def _create_rag_node(self, config: Dict) -> Callable:
        """Create a RAG (retrieval-augmented generation) node."""
        node_id = config.get('id', 'rag')
        node_config = config.get('config', {})
        
        def rag_node(state: WorkflowState) -> Dict:
            logger.info(f"Executing RAG node: {node_id}")
            
            try:
                # This is a placeholder - actual implementation would use
                # vector stores, embeddings, etc.
                query = state.get('input', '')
                
                # Simulate retrieval
                retrieved_docs = f"Retrieved context for: {query}"
                
                output_key = node_config.get('output_key', node_id)
                
                return {
                    "current_node": node_id,
                    "executed_nodes": [node_id],
                    "node_outputs": {output_key: retrieved_docs},
                    "context": {"retrieved": retrieved_docs}
                }
                
            except Exception as e:
                logger.error(f"RAG node {node_id} failed: {e}")
                return {
                    "current_node": node_id,
                    "executed_nodes": [node_id],
                    "error": str(e),
                    "status": "failed"
                }
        
        return rag_node


# ============================================================================
# Workflow Graph Builder
# ============================================================================

def create_workflow_graph(workflow_config: Dict, db_facade, 
                         llm_factory=None, tool_factory=None) -> Any:
    """
    Create a LangGraph workflow from configuration.
    
    Args:
        workflow_config: Workflow configuration with nodes and edges
        db_facade: Database facade
        llm_factory: Optional LLM factory
        tool_factory: Optional tool factory
        
    Returns:
        Compiled LangGraph StateGraph
    """
    try:
        from langgraph.graph import StateGraph, END
    except ImportError:
        raise ImportError("langgraph is required. Install with: pip install langgraph")
    
    # Create node factory
    node_factory = LangGraphNodeFactory(db_facade, llm_factory, tool_factory)
    
    # Create state graph
    graph = StateGraph(WorkflowState)
    
    # Extract nodes and edges from config
    raw_nodes = workflow_config.get('nodes', [])
    raw_edges = workflow_config.get('edges', [])
    
    logger.debug(f"Creating workflow graph with {len(raw_nodes)} nodes and {len(raw_edges)} edges")
    
    # Normalize node format - handle both 'id'/'node_id' and 'type'/'node_type'
    nodes = []
    for n in raw_nodes:
        node_id = n.get('id') or n.get('node_id')
        node_type = n.get('type') or n.get('node_type') or 'action'
        normalized = {
            'id': node_id,
            'type': node_type,
            'name': n.get('name') or n.get('title') or node_id,
            'config': n.get('config', {})
        }
        nodes.append(normalized)
        logger.debug(f"Normalized node: id={node_id}, type={node_type}")
    
    # Normalize edge format - handle both 'source'/'from' and 'target'/'to'
    edges = []
    for e in raw_edges:
        source = e.get('source') or e.get('from') or e.get('source_id')
        target = e.get('target') or e.get('to') or e.get('target_id')
        normalized = {
            'source': source,
            'target': target,
            'condition': e.get('condition')
        }
        edges.append(normalized)
        logger.debug(f"Normalized edge: {source} -> {target}")
    
    # Find start/input and end/output nodes
    # Support both 'start'/'end' and 'input'/'output' node types
    start_types = {'start', 'input'}
    end_types = {'end', 'output'}
    hitl_types = {'hitl', 'human', 'human_in_the_loop', 'approval', 'review'}
    
    start_node_id = None
    end_node_ids = []
    hitl_node_ids = set()  # Track HITL nodes for special edge handling
    executable_nodes = []  # Nodes that actually get added to graph
    
    for node in nodes:
        node_id = node.get('id')
        node_type = (node.get('type') or '').lower()
        
        if node_type in start_types:
            start_node_id = node_id
            logger.debug(f"Found start/input node: {node_id}")
        elif node_type in end_types:
            end_node_ids.append(node_id)
            logger.debug(f"Found end/output node: {node_id}")
        else:
            executable_nodes.append(node)
            # Track HITL nodes
            if node_type in hitl_types:
                hitl_node_ids.add(node_id)
                logger.debug(f"Found HITL node: {node_id}")
    
    logger.debug(f"Start node: {start_node_id}, End nodes: {end_node_ids}, HITL nodes: {hitl_node_ids}, Executable: {[n['id'] for n in executable_nodes]}")
    
    # Add executable nodes to graph (skip start/end nodes)
    for node_config in executable_nodes:
        node_id = node_config.get('id')
        if not node_id:
            continue
        
        node_func = node_factory.create_node_function(node_config)
        graph.add_node(node_id, node_func)
        logger.debug(f"Added node to graph: {node_id}")
    
    # Track entry point
    entry_point_set = False
    first_executable_node = executable_nodes[0]['id'] if executable_nodes else None
    
    # Process edges
    for edge in edges:
        source = edge.get('source')
        target = edge.get('target')
        condition = edge.get('condition')
        
        if not source or not target:
            continue
        
        # Handle start/input node - set entry point to target
        if source == start_node_id:
            # Target of start edge is our entry point (if it's an executable node)
            if target not in end_node_ids:
                logger.info(f"Setting entry point to: {target} (from start node edge)")
                graph.set_entry_point(target)
                entry_point_set = True
            continue
        
        # Handle end/output nodes - connect to END
        if target in end_node_ids:
            logger.debug(f"Adding edge to END: {source} -> END")
            graph.add_edge(source, END)
            continue
        
        # Handle conditional edges
        if condition:
            def make_condition(cond, true_target, false_target=None):
                def check_condition(state: WorkflowState) -> str:
                    try:
                        eval_context = {
                            'state': state,
                            'input': state.get('input'),
                            'output': state.get('output'),
                            'node_outputs': state.get('node_outputs', {}),
                        }
                        result = eval(cond, {"__builtins__": {}}, eval_context)
                        return true_target if result else (false_target or END)
                    except:
                        return false_target or END
                return check_condition
            
            false_target = None
            for e in edges:
                if e.get('source') == source and e.get('target') != target:
                    false_target = e.get('target')
                    break
            
            graph.add_conditional_edges(
                source,
                make_condition(condition, target, false_target)
            )
        # Handle HITL node edges - make them conditional to pause when hitl_pending
        elif source in hitl_node_ids:
            def make_hitl_check(next_target):
                def check_hitl(state: WorkflowState) -> str:
                    # If HITL is pending, pause the workflow (go to END)
                    if state.get('hitl_pending'):
                        logger.info(f"HITL pending, pausing workflow at {source}")
                        return END
                    return next_target
                return check_hitl
            
            logger.debug(f"Adding HITL conditional edge: {source} -> {target} (with pause check)")
            graph.add_conditional_edges(source, make_hitl_check(target))
        else:
            logger.debug(f"Adding edge: {source} -> {target}")
            graph.add_edge(source, target)
    
    # Fallback entry point detection
    if not entry_point_set:
        logger.warning("Entry point not set from edges, trying fallbacks...")
        
        # Method 1: First executable node
        if first_executable_node:
            logger.info(f"Setting entry point to first executable node: {first_executable_node}")
            graph.set_entry_point(first_executable_node)
            entry_point_set = True
        
        # Method 2: Find node with no incoming edges (among executable nodes)
        if not entry_point_set:
            incoming = set()
            for edge in edges:
                target = edge.get('target')
                if target and target not in end_node_ids:
                    incoming.add(target)
            
            for node in executable_nodes:
                node_id = node.get('id')
                if node_id not in incoming:
                    logger.info(f"Setting entry point to node with no incoming edges: {node_id}")
                    graph.set_entry_point(node_id)
                    entry_point_set = True
                    break
    
    if not entry_point_set:
        logger.error("Could not determine entry point for workflow!")
        logger.error(f"Nodes: {[n['id'] + ':' + n['type'] for n in nodes]}")
        logger.error(f"Edges: {[(e['source'], e['target']) for e in edges]}")
        raise ValueError("Could not determine workflow entry point. Check that edges connect from input node to other nodes.")
    
    # Compile and return
    return graph.compile()


# ============================================================================
# Workflow Executor
# ============================================================================

class WorkflowGraphExecutor:
    """
    Execute LangGraph workflows with full state management and logging.
    """
    
    def __init__(self, db_facade, llm_factory=None, tool_factory=None):
        self.db_facade = db_facade
        self.llm_factory = llm_factory
        self.tool_factory = tool_factory
    
    def execute_workflow(self, workflow_id: str, input_data: Any,
                        variables: Dict = None,
                        config_overrides: Dict = None) -> WorkflowExecutionResult:
        """
        Execute a workflow by ID.
        
        Args:
            workflow_id: ID of the workflow to execute
            input_data: Input to the workflow
            variables: Optional variables to pass to nodes
            config_overrides: Optional configuration overrides
            
        Returns:
            WorkflowExecutionResult
        """
        execution_id = str(uuid.uuid4())
        result = WorkflowExecutionResult(
            execution_id=execution_id,
            workflow_id=workflow_id,
            input_data=input_data,
            started_at=datetime.utcnow()
        )
        
        try:
            # Load workflow configuration
            workflow = self.db_facade.fetch_one(
                "SELECT * FROM workflows WHERE workflow_id = ?",
                (workflow_id,)
            )
            
            if not workflow:
                raise ValueError(f"Workflow not found: {workflow_id}")
            
            # Parse workflow definition
            definition = workflow.get('definition_json', '{}')
            if isinstance(definition, str):
                definition = json.loads(definition)
            
            result.status = 'running'
            result.metadata['workflow_name'] = workflow.get('name', workflow_id)
            
            # Create and execute graph
            graph = create_workflow_graph(
                definition,
                self.db_facade,
                self.llm_factory,
                self.tool_factory
            )
            
            # Prepare initial state
            initial_state = {
                "input": input_data,
                "output": None,
                "current_node": "",
                "executed_nodes": [],
                "node_outputs": {},
                "error": None,
                "status": "running",
                "context": {},
                "variables": variables or {},
                "hitl_pending": False,
                "hitl_message": None,
                "hitl_response": None,
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "started_at": datetime.utcnow().isoformat(),
                "messages": []
            }
            
            # Execute graph
            start_time = time.time()
            final_state = graph.invoke(initial_state)
            result.duration_ms = int((time.time() - start_time) * 1000)
            
            # Extract results
            result.output = final_state.get('output')
            result.node_outputs = final_state.get('node_outputs', {})
            result.executed_nodes = final_state.get('executed_nodes', [])
            
            if final_state.get('error'):
                result.status = 'failed'
                result.error_message = final_state['error']
            elif final_state.get('hitl_pending'):
                result.status = 'waiting_for_human'
                result.metadata['hitl_message'] = final_state.get('hitl_message')
            else:
                result.status = 'completed'
            
            result.completed_at = datetime.utcnow()
            
            # Log execution
            self._log_execution(result, workflow)
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}", exc_info=True)
            result.status = 'failed'
            result.error_message = str(e)
            result.completed_at = datetime.utcnow()
            result.duration_ms = int((datetime.utcnow() - result.started_at).total_seconds() * 1000)
            
            self._log_execution(result, {})
        
        return result
    
    def resume_workflow(self, execution_id: str, hitl_response: Any) -> WorkflowExecutionResult:
        """
        Resume a workflow that is waiting for human input.
        
        Args:
            execution_id: Execution ID to resume
            hitl_response: Human response/input
            
        Returns:
            WorkflowExecutionResult
        """
        # This would need checkpointing support in LangGraph
        # For now, return a not-implemented error
        raise NotImplementedError("Workflow resumption requires LangGraph checkpointing")
    
    def _log_execution(self, result: WorkflowExecutionResult, workflow: Dict):
        """Log workflow execution to database."""
        try:
            self.db_facade.execute(
                """INSERT INTO workflow_executions
                   (execution_id, workflow_id, status, input_data, output_data,
                    error_message, duration_ms, metadata, started_at, completed_at,
                    created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                (
                    result.execution_id,
                    result.workflow_id,
                    result.status,
                    json.dumps(result.input_data) if result.input_data else None,
                    json.dumps(result.output) if result.output else None,
                    result.error_message,
                    result.duration_ms,
                    json.dumps({
                        'node_outputs': result.node_outputs,
                        'executed_nodes': result.executed_nodes,
                        **result.metadata
                    }),
                    result.started_at.isoformat() if result.started_at else None,
                    result.completed_at.isoformat() if result.completed_at else None
                )
            )
        except Exception as e:
            logger.warning(f"Failed to log workflow execution: {e}")


def execute_workflow_from_config(db_facade, workflow_id: str, input_data: Any,
                                variables: Dict = None) -> WorkflowExecutionResult:
    """
    Convenience function to execute a workflow from database configuration.
    
    Args:
        db_facade: Database facade
        workflow_id: Workflow ID
        input_data: Input data
        variables: Optional variables
        
    Returns:
        WorkflowExecutionResult
    """
    executor = WorkflowGraphExecutor(db_facade)
    return executor.execute_workflow(workflow_id, input_data, variables)
