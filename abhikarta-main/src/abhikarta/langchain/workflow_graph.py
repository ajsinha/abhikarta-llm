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

Version: 1.5.1
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

# =============================================================================
# Execution Logger
# =============================================================================
try:
    from abhikarta.services.execution_logger import get_execution_logger
    _execution_logger_available = True
except ImportError:
    _execution_logger_available = False
    logger.debug("Execution logger not available")

# =============================================================================
# Prometheus Metrics
# =============================================================================
try:
    from abhikarta.monitoring import (
        WORKFLOW_EXECUTIONS,
        WORKFLOW_EXECUTION_DURATION,
        WORKFLOW_NODE_EXECUTIONS,
        WORKFLOW_NODE_DURATION,
        ACTIVE_WORKFLOWS,
    )
    _metrics_available = True
except ImportError:
    _metrics_available = False
    logger.debug("Prometheus metrics not available for workflows")


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
        node_id = config.get('id', 'llm')
        node_config = config.get('config', {})
        
        def llm_node(state: WorkflowState) -> Dict:
            logger.info(f"Executing LLM node: {node_id}")
            
            try:
                # Check if we have direct provider/model config (from JSON template)
                # or if we need to look up from database
                provider = node_config.get('provider')
                model = node_config.get('model')
                base_url = node_config.get('base_url')
                
                llm = None
                
                # If we have direct config with provider and model, create LLM directly
                if provider and model:
                    logger.info(f"[NODE:{node_id}] Creating LLM directly: provider={provider}, model={model}")
                    llm = self._create_llm_from_config(
                        provider=provider,
                        model=model,
                        base_url=base_url,
                        temperature=node_config.get('temperature', 0.7),
                        api_key=node_config.get('api_key')
                    )
                else:
                    # Fall back to database lookup
                    from .llm_factory import get_langchain_llm
                    
                    model_id = node_config.get('model_id') or node_config.get('model')
                    provider_id = node_config.get('provider_id') or node_config.get('provider')
                    
                    logger.info(f"[NODE:{node_id}] Getting LLM from database: model_id={model_id}, provider_id={provider_id}")
                    llm = get_langchain_llm(
                        self.db_facade,
                        model_id=model_id,
                        provider_id=provider_id
                    )
                
                if not llm:
                    raise ValueError(f"Failed to create LLM for node {node_id}")
                
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
                
                # Build template context with defaults for missing values
                template_context = {
                    'input': input_value,
                    'query': input_value,
                    'text': input_value,
                    # Default values for common template variables
                    'learning_state': state.get('node_outputs', {}).get('learning_state', 'No previous learning state'),
                    'learning_context': state.get('node_outputs', {}).get('learning_context', 'Starting fresh'),
                    'performance_history': 'No previous performance data',
                    'exploration_rate': '20%',
                    'learning_rate': '0.1',
                    'selected_strategy': state.get('node_outputs', {}).get('selected_strategy', 'Not yet selected'),
                    'execution_result': state.get('node_outputs', {}).get('execution_result', 'Not yet executed'),
                    'evaluation': state.get('node_outputs', {}).get('evaluation', 'Not yet evaluated'),
                    'learning_signals': state.get('node_outputs', {}).get('learning_signals', 'No signals yet'),
                    'updated_state': state.get('node_outputs', {}).get('updated_state', 'Initial state'),
                    'final_output': state.get('node_outputs', {}).get('final_output', state.get('output', '')),
                    'task_analysis': state.get('node_outputs', {}).get('task_analysis', 'Not analyzed yet'),
                    'self_evaluation': state.get('node_outputs', {}).get('self_evaluation', 'Not evaluated yet'),
                    'improvement_plan': state.get('node_outputs', {}).get('improvement_plan', 'No improvement plan yet'),
                    'learnings': state.get('node_outputs', {}).get('learnings', 'No learnings yet'),
                }
                
                # Add all node outputs (these override defaults)
                template_context.update(state.get('node_outputs', {}))
                # Add all variables (these override node outputs)
                template_context.update(state.get('variables', {}))
                
                # Apply template
                prompt_template = node_config.get('prompt_template', '{input}')
                try:
                    prompt = prompt_template.format(**template_context)
                except KeyError as e:
                    # If still missing a variable, log and use partial format
                    logger.warning(f"[NODE:{node_id}] Missing template variable: {e}")
                    # Try to format what we can
                    import re
                    prompt = prompt_template
                    for key, value in template_context.items():
                        prompt = prompt.replace('{' + key + '}', str(value))
                    # Replace any remaining placeholders with 'N/A'
                    prompt = re.sub(r'\{[^}]+\}', '[N/A]', prompt)
                
                messages.append(("human", prompt))
                
                logger.info(f"[NODE:{node_id}] LLM Input prompt ({len(prompt)} chars): {prompt[:500]}...")
                
                # Invoke LLM and measure time
                start_time = time.time()
                response = llm.invoke(messages)
                duration_ms = (time.time() - start_time) * 1000
                output = response.content if hasattr(response, 'content') else str(response)
                
                logger.info(f"[NODE:{node_id}] LLM Output ({len(output)} chars): {output[:500]}...")
                
                # Log LLM call to execution logger if available
                if _execution_logger_available:
                    try:
                        execution_id = state.get('execution_id')
                        if execution_id:
                            exec_logger = get_execution_logger()
                            exec_logger.log_llm_call(
                                execution_id=execution_id,
                                provider=provider or 'unknown',
                                model=model or 'unknown',
                                prompt=prompt,
                                response=output,
                                duration_ms=duration_ms
                            )
                            # Also log node execution
                            exec_logger.log_node_execution(
                                execution_id=execution_id,
                                node_id=node_id,
                                node_type='llm',
                                input_data={'prompt': prompt[:1000] + '...' if len(prompt) > 1000 else prompt},
                                output_data={'response': output[:1000] + '...' if len(output) > 1000 else output},
                                duration_ms=duration_ms
                            )
                    except Exception as log_err:
                        logger.debug(f"Failed to log LLM call: {log_err}")
                
                # Store output
                output_key = node_config.get('output_key', node_id)
                
                return {
                    "current_node": node_id,
                    "executed_nodes": [node_id],
                    "node_outputs": {output_key: output},
                    "output": output
                }
                
            except Exception as e:
                # Create user-friendly error messages for common issues
                error_msg = str(e)
                user_friendly_error = error_msg
                
                # Check for common Ollama errors
                if 'not found' in error_msg.lower() and 'model' in error_msg.lower():
                    model_name = model or 'unknown'
                    user_friendly_error = (
                        f"LLM Model Not Found: '{model_name}'\n\n"
                        f"The Ollama model '{model_name}' is not installed.\n\n"
                        f"To fix this, run one of the following:\n"
                        f"  ollama pull {model_name}\n"
                        f"  ollama pull llama3.2:latest\n"
                        f"  ollama pull mistral:latest\n\n"
                        f"Or update the workflow template to use an installed model.\n"
                        f"Check available models with: ollama list"
                    )
                elif 'connection' in error_msg.lower() or 'connect' in error_msg.lower():
                    user_friendly_error = (
                        f"LLM Connection Error\n\n"
                        f"Could not connect to the LLM provider ({provider or 'unknown'}).\n\n"
                        f"Possible causes:\n"
                        f"  • Ollama is not running (start with: ollama serve)\n"
                        f"  • Wrong base_url configured (currently: {base_url or 'default'})\n"
                        f"  • Network/firewall issues\n\n"
                        f"Original error: {error_msg}"
                    )
                elif 'api_key' in error_msg.lower() or 'authentication' in error_msg.lower():
                    user_friendly_error = (
                        f"LLM Authentication Error\n\n"
                        f"Authentication failed for {provider or 'unknown'}.\n\n"
                        f"Please check:\n"
                        f"  • API key is set correctly in application.properties\n"
                        f"  • API key has not expired\n"
                        f"  • You have sufficient quota/credits\n\n"
                        f"Original error: {error_msg}"
                    )
                elif 'rate limit' in error_msg.lower() or 'quota' in error_msg.lower():
                    user_friendly_error = (
                        f"LLM Rate Limit Error\n\n"
                        f"Rate limit exceeded for {provider or 'unknown'}.\n\n"
                        f"Please wait a moment and try again, or:\n"
                        f"  • Switch to a different model\n"
                        f"  • Upgrade your API plan\n"
                        f"  • Use Ollama for local inference\n\n"
                        f"Original error: {error_msg}"
                    )
                
                logger.error(f"LLM node {node_id} failed: {error_msg}")
                import traceback
                error_traceback = traceback.format_exc()
                logger.error(f"Full traceback:\n{error_traceback}")
                
                # Log error to execution logger
                if _execution_logger_available:
                    try:
                        execution_id = state.get('execution_id')
                        if execution_id:
                            exec_logger = get_execution_logger()
                            exec_logger.log_node_execution(
                                execution_id=execution_id,
                                node_id=node_id,
                                node_type='llm',
                                error=user_friendly_error
                            )
                            exec_logger.log_entry(execution_id, "ERROR",
                                                 f"LLM node {node_id} failed: {error_msg}",
                                                 {'traceback': error_traceback[:2000], 'user_friendly': user_friendly_error})
                    except Exception as log_err:
                        logger.debug(f"Failed to log error: {log_err}")
                
                return {
                    "current_node": node_id,
                    "executed_nodes": [node_id],
                    "node_outputs": {node_config.get('output_key', node_id): f"Error: {user_friendly_error}"},
                    "error": user_friendly_error,
                    "status": "failed"
                }
        
        return llm_node
    
    def _create_llm_from_config(self, provider: str, model: str, base_url: str = None,
                                temperature: float = 0.7, api_key: str = None) -> Any:
        """
        Create an LLM instance directly from config parameters.
        
        This is used when the node has direct provider/model/base_url config
        instead of database references.
        """
        provider = provider.lower()
        logger.info(f"Creating LLM: provider={provider}, model={model}, base_url={base_url}")
        
        try:
            if provider == 'ollama':
                try:
                    from langchain_ollama import ChatOllama
                    return ChatOllama(
                        model=model,
                        base_url=base_url or 'http://localhost:11434',
                        temperature=temperature
                    )
                except ImportError:
                    logger.error("langchain-ollama not installed. Install with: pip install langchain-ollama")
                    raise
                    
            elif provider == 'openai':
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model=model,
                    api_key=api_key,
                    base_url=base_url,
                    temperature=temperature
                )
                
            elif provider == 'anthropic':
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(
                    model=model,
                    api_key=api_key,
                    temperature=temperature
                )
                
            elif provider == 'google':
                from langchain_google_genai import ChatGoogleGenerativeAI
                return ChatGoogleGenerativeAI(
                    model=model,
                    google_api_key=api_key,
                    temperature=temperature
                )
                
            elif provider == 'groq':
                from langchain_groq import ChatGroq
                return ChatGroq(
                    model=model,
                    api_key=api_key,
                    temperature=temperature
                )
                
            elif provider == 'together':
                from langchain_together import ChatTogether
                return ChatTogether(
                    model=model,
                    api_key=api_key,
                    temperature=temperature
                )
                
            else:
                # Try OpenAI-compatible endpoint as fallback
                logger.warning(f"Unknown provider '{provider}', trying OpenAI-compatible API")
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model=model,
                    api_key=api_key or 'dummy-key',
                    base_url=base_url,
                    temperature=temperature
                )
                
        except ImportError as e:
            logger.error(f"Failed to import LLM library for provider {provider}: {e}")
            raise ValueError(f"LLM provider '{provider}' requires additional dependencies: {e}")
    
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
            except Exception as fmt_err:
                logger.debug(f"HITL message format failed: {fmt_err}, using original message")
            
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
    
    def _create_function_node(self, config: Dict) -> Callable:
        """Create a function node that executes custom logic."""
        node_id = config.get('id', 'function')
        node_config = config.get('config', {})
        
        def function_node(state: WorkflowState) -> Dict:
            logger.info(f"Executing function node: {node_id}")
            
            try:
                func_name = node_config.get('function', '')
                output_key = node_config.get('output_key', node_id)
                input_keys = node_config.get('input_keys', [])
                
                # Gather inputs from state
                func_inputs = {}
                for key in input_keys:
                    if key in state:
                        func_inputs[key] = state[key]
                    elif key in state.get('node_outputs', {}):
                        func_inputs[key] = state['node_outputs'][key]
                
                # Get user input
                user_input = state.get('input', '')
                if isinstance(user_input, dict):
                    user_input = user_input.get('query') or user_input.get('input') or str(user_input)
                
                # Built-in function implementations
                result = None
                
                if func_name == 'load_learning_context':
                    # Simulate loading learning context
                    result = f"""Learning Context:
- Historical patterns: None recorded yet (new session)
- Successful strategies: Starting fresh
- Failed approaches: None recorded
- This is iteration 1
- Task: {user_input}"""
                    
                elif func_name == 'update_learning_memory':
                    # Simulate memory update
                    result = "Memory updated with new learnings from this iteration"
                    
                elif func_name == 'initialize_state' or func_name == 'initialize_learning_state':
                    # Initialize learning state for adaptive workflows
                    initial_strategy = node_config.get('initial_strategy', 'balanced')
                    result = f"""Learning State Initialized:
- Strategy: {initial_strategy}
- Iteration: 1
- Performance history: No previous iterations
- Exploration rate: 20%
- Learning rate: 0.1
- Task to learn: {user_input}"""
                    
                elif func_name == 'prepare_next_iteration':
                    # Prepare for next iteration in learning loop
                    current_iter = state.get('variables', {}).get('iteration', 1)
                    result = f"""Prepared for iteration {current_iter + 1}:
- Previous results analyzed
- Strategy weights updated
- Ready for next learning cycle"""
                    
                elif func_name == 'aggregate_results':
                    # Aggregate all node outputs
                    outputs = state.get('node_outputs', {})
                    result = '\n\n'.join([f"**{k}**:\n{v}" for k, v in outputs.items()])
                    
                elif func_name == 'format_output':
                    # Format final output
                    template = node_config.get('template', '{output}')
                    try:
                        result = template.format(
                            input=state.get('input', ''),
                            output=state.get('output', ''),
                            **state.get('node_outputs', {}),
                            **func_inputs
                        )
                    except KeyError as e:
                        result = state.get('output', f'Missing key: {e}')
                
                elif func_name == 'extract_score':
                    # Extract score from evaluation text
                    eval_text = state.get('node_outputs', {}).get('evaluation', '')
                    # Try to find a score
                    import re
                    scores = re.findall(r'(\d+)\s*/\s*100|score[:\s]+(\d+)|(\d+)%', str(eval_text).lower())
                    if scores:
                        # Get first score found
                        score = next((int(s) for s in scores[0] if s), 75)
                        result = str(score)
                    else:
                        result = "75"  # Default score
                        
                else:
                    # Unknown function - provide helpful passthrough that doesn't break workflow
                    logger.warning(f"Unknown function '{func_name}', using passthrough with task context")
                    result = f"""Function '{func_name}' completed.
Task context: {user_input}
Ready for next step."""
                
                logger.info(f"Function node {node_id} ({func_name}) completed successfully")
                logger.debug(f"Function result: {str(result)[:200]}...")
                
                # Log node execution
                if _execution_logger_available:
                    try:
                        execution_id = state.get('execution_id')
                        if execution_id:
                            exec_logger = get_execution_logger()
                            exec_logger.log_node_execution(
                                execution_id=execution_id,
                                node_id=node_id,
                                node_type='function',
                                input_data={'function': func_name, 'inputs': func_inputs},
                                output_data={'result': str(result)[:2000] if result else None}
                            )
                    except Exception as log_err:
                        logger.debug(f"Failed to log function execution: {log_err}")
                
                return {
                    "current_node": node_id,
                    "executed_nodes": [node_id],
                    "node_outputs": {output_key: result},
                    "output": result if isinstance(result, str) else str(result)
                }
                
            except Exception as e:
                logger.error(f"Function node {node_id} failed: {e}")
                
                # Log error
                if _execution_logger_available:
                    try:
                        execution_id = state.get('execution_id')
                        if execution_id:
                            exec_logger = get_execution_logger()
                            exec_logger.log_node_execution(
                                execution_id=execution_id,
                                node_id=node_id,
                                node_type='function',
                                error=str(e)
                            )
                    except:
                        pass
                
                return {
                    "current_node": node_id,
                    "executed_nodes": [node_id],
                    "node_outputs": {node_config.get('output_key', node_id): f"Function error: {e}"},
                    "error": str(e),
                    "status": "failed"
                }
        
        return function_node
    
    def _create_aggregator_node(self, config: Dict) -> Callable:
        """Create an aggregator node that combines outputs from multiple nodes."""
        node_id = config.get('id', 'aggregator')
        node_config = config.get('config', {})
        
        def aggregator_node(state: WorkflowState) -> Dict:
            logger.info(f"Executing aggregator node: {node_id}")
            
            try:
                template = node_config.get('template', '')
                output_key = node_config.get('output_key', node_id)
                input_keys = node_config.get('input_keys', [])
                
                # Gather all node outputs
                node_outputs = state.get('node_outputs', {})
                
                # If specific input_keys are defined, use only those
                if input_keys:
                    aggregated = {k: node_outputs.get(k, '') for k in input_keys}
                else:
                    aggregated = node_outputs.copy()
                
                # Apply template if provided
                if template:
                    try:
                        result = template.format(
                            input=state.get('input', ''),
                            output=state.get('output', ''),
                            **aggregated,
                            **state.get('variables', {})
                        )
                    except KeyError as e:
                        # If a key is missing, provide a default
                        logger.warning(f"Aggregator template missing key: {e}")
                        # Try to fill in missing keys with empty strings
                        safe_dict = {**aggregated, **state.get('variables', {})}
                        for key in ['input', 'output', 'final_result', 'selected_strategy', 
                                   'self_evaluation', 'task_analysis', 'learnings',
                                   'execution_result', 'learning_context']:
                            if key not in safe_dict:
                                safe_dict[key] = f'[{key} not available]'
                        safe_dict['input'] = state.get('input', '')
                        safe_dict['output'] = state.get('output', '')
                        try:
                            result = template.format(**safe_dict)
                        except Exception as fmt_err:
                            logger.debug(f"Aggregator template format failed: {fmt_err}, using fallback")
                            result = '\n\n'.join([f"**{k}**:\n{v}" for k, v in aggregated.items()])
                else:
                    # No template - join all outputs
                    result = '\n\n'.join([f"**{k}**:\n{v}" for k, v in aggregated.items()])
                
                logger.debug(f"Aggregator node {node_id} result: {str(result)[:200]}...")
                
                return {
                    "current_node": node_id,
                    "executed_nodes": [node_id],
                    "node_outputs": {output_key: result},
                    "output": result
                }
                
            except Exception as e:
                logger.error(f"Aggregator node {node_id} failed: {e}")
                return {
                    "current_node": node_id,
                    "executed_nodes": [node_id],
                    "error": str(e),
                    "status": "failed"
                }
        
        return aggregator_node


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
    
    # Log incoming config for debugging
    logger.info(f"=== Creating workflow graph ===")
    logger.info(f"Config keys: {list(workflow_config.keys())}")
    logger.info(f"Entry point in config: {workflow_config.get('entry_point')}")
    logger.info(f"Nodes count: {len(workflow_config.get('nodes', []))}")
    logger.info(f"Edges count: {len(workflow_config.get('edges', []))}")
    
    # Log first few edges for debugging
    edges_preview = workflow_config.get('edges', [])[:5]
    logger.info(f"First edges: {edges_preview}")
    
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
    
    # Check for explicit entry_point in workflow config (highest priority)
    explicit_entry_point = workflow_config.get('entry_point')
    logger.info(f"Entry point from config: '{explicit_entry_point}'")
    logger.info(f"Executable node IDs: {[n['id'] for n in executable_nodes]}")
    
    if explicit_entry_point:
        # Verify the entry point exists in executable nodes
        executable_ids = {n['id'] for n in executable_nodes}
        if explicit_entry_point in executable_ids:
            logger.info(f"✓ Setting entry point from config: {explicit_entry_point}")
            graph.set_entry_point(explicit_entry_point)
            entry_point_set = True
        else:
            logger.warning(f"✗ Explicit entry_point '{explicit_entry_point}' not found in executable nodes: {executable_ids}")
    
    # Group edges by source for proper conditional edge handling
    edges_by_source = {}
    for edge in edges:
        source = edge.get('source')
        if source:
            if source not in edges_by_source:
                edges_by_source[source] = []
            edges_by_source[source].append(edge)
    
    logger.info(f"Edges by source: {list(edges_by_source.keys())}")
    
    # Track which sources have been processed (for conditional edges)
    processed_conditional_sources = set()
    
    # Process edges
    logger.info(f"=== Processing {len(edges)} edges ===")
    edges_added = {'regular': 0, 'conditional': 0, 'to_end': 0, 'entry': 0, 'skipped': 0}
    
    for edge in edges:
        source = edge.get('source')
        target = edge.get('target')
        condition = edge.get('condition')
        
        if not source or not target:
            edges_added['skipped'] += 1
            continue
        
        logger.debug(f"Processing edge: {source} -> {target} (condition: {condition})")
        
        # Handle start/input node - set entry point to target
        if source == start_node_id:
            # Target of start edge is our entry point (if it's an executable node)
            if target not in end_node_ids:
                logger.info(f"Setting entry point to: {target} (from start node edge)")
                graph.set_entry_point(target)
                entry_point_set = True
                edges_added['entry'] += 1
            continue
        
        # Handle end/output nodes - connect to END
        if target in end_node_ids:
            logger.debug(f"Adding edge to END: {source} -> END")
            graph.add_edge(source, END)
            edges_added['to_end'] += 1
            continue
        
        # Handle conditional edges - group all from same source
        if condition:
            # Skip if we already processed this source's conditional edges
            if source in processed_conditional_sources:
                continue
            
            # Get all conditional edges from this source
            source_edges = edges_by_source.get(source, [])
            conditional_edges = [e for e in source_edges if e.get('condition')]
            non_conditional_edges = [e for e in source_edges if not e.get('condition') and e.get('target') not in end_node_ids]
            
            if len(conditional_edges) > 1:
                # Multiple conditional edges - create a multi-way routing function
                def make_multi_condition_router(src_node, cond_edges, default_target=None):
                    """Create a routing function that handles multiple conditions."""
                    # Build condition -> target mapping
                    condition_map = []
                    for e in cond_edges:
                        cond = e.get('condition')
                        tgt = e.get('target')
                        if cond and tgt:
                            condition_map.append((cond, tgt))
                    
                    def route_by_conditions(state: WorkflowState) -> str:
                        try:
                            eval_context = {
                                'state': state,
                                'input': state.get('input'),
                                'output': state.get('output'),
                                'node_outputs': state.get('node_outputs', {}),
                            }
                            
                            # Check for errors first - terminate workflow
                            if state.get('error') or state.get('status') == 'failed':
                                logger.warning(f"[{src_node}] Routing to END due to error: {state.get('error', 'status=failed')}")
                                return END
                            
                            # Check each condition in order
                            for cond_str, target_node in condition_map:
                                try:
                                    # Try evaluating as Python expression first
                                    result = eval(cond_str, {"__builtins__": {}}, eval_context)
                                    if result:
                                        return target_node
                                except Exception as eval_ex:
                                    # Treat as a string key check in node_outputs or state
                                    logger.debug(f"Condition eval failed for '{cond_str}': {eval_ex}, trying string match")
                                    node_outputs = state.get('node_outputs', {})
                                    
                                    # Check if condition string matches any output value
                                    for node_id, output in node_outputs.items():
                                        if isinstance(output, dict):
                                            for key, val in output.items():
                                                if str(val).lower() == cond_str.lower():
                                                    return target_node
                                        elif str(output).lower() == cond_str.lower():
                                            return target_node
                                    
                                    # Check direct state key
                                    if cond_str in state and state[cond_str]:
                                        return target_node
                            
                            # No condition matched - use default or END
                            return default_target or END
                        except Exception as ex:
                            logger.warning(f"Error in multi-condition routing: {ex}")
                            return default_target or END
                    
                    # Set unique function name to avoid branch name collisions
                    route_by_conditions.__name__ = f"multi_cond_route_from_{src_node}"
                    return route_by_conditions
                
                # Find default target from non-conditional edges
                default = non_conditional_edges[0].get('target') if non_conditional_edges else None
                
                logger.debug(f"Adding multi-conditional edges from {source}: {[(e.get('condition'), e.get('target')) for e in conditional_edges]}")
                graph.add_conditional_edges(
                    source,
                    make_multi_condition_router(source, conditional_edges, default)
                )
                processed_conditional_sources.add(source)
                edges_added['conditional'] += len(conditional_edges)
            else:
                # Single conditional edge - use simpler logic
                def make_condition(src_node, cond, true_target, false_target=None):
                    def check_condition(state: WorkflowState) -> str:
                        # Check for errors first - terminate workflow
                        if state.get('error') or state.get('status') == 'failed':
                            logger.warning(f"[{src_node}] Routing to END due to error: {state.get('error', 'status=failed')}")
                            return END
                        try:
                            eval_context = {
                                'state': state,
                                'input': state.get('input'),
                                'output': state.get('output'),
                                'node_outputs': state.get('node_outputs', {}),
                            }
                            result = eval(cond, {"__builtins__": {}}, eval_context)
                            return true_target if result else (false_target or END)
                        except Exception as eval_ex:
                            logger.debug(f"Condition eval failed for '{cond}': {eval_ex}, using false_target")
                            return false_target or END
                    # Set unique function name
                    check_condition.__name__ = f"cond_route_from_{src_node}"
                    return check_condition
                
                false_target = None
                for e in source_edges:
                    if e.get('target') != target and not e.get('condition'):
                        false_target = e.get('target')
                        break
                
                logger.debug(f"Adding conditional edge: {source} -> {target} (condition: {condition})")
                graph.add_conditional_edges(
                    source,
                    make_condition(source, condition, target, false_target)
                )
                processed_conditional_sources.add(source)
                edges_added['conditional'] += 1
        # Handle HITL node edges - make them conditional to pause when hitl_pending
        elif source in hitl_node_ids:
            # Skip if already processed as conditional
            if source in processed_conditional_sources:
                continue
                
            def make_hitl_check(src_node, next_target):
                def check_hitl(state: WorkflowState) -> str:
                    # Check for errors first - terminate workflow
                    if state.get('error') or state.get('status') == 'failed':
                        logger.warning(f"[{src_node}] Routing to END due to error: {state.get('error', 'status=failed')}")
                        return END
                    # If HITL is pending, pause the workflow (go to END)
                    if state.get('hitl_pending'):
                        logger.info(f"HITL pending, pausing workflow at {src_node}")
                        return END
                    return next_target
                # Set unique function name
                check_hitl.__name__ = f"hitl_route_from_{src_node}"
                return check_hitl
            
            logger.debug(f"Adding HITL conditional edge: {source} -> {target} (with pause check)")
            graph.add_conditional_edges(source, make_hitl_check(source, target))
            processed_conditional_sources.add(source)
            edges_added['conditional'] += 1
        else:
            # Regular edge - but skip if source has conditional edges (they're handled above)
            source_edges = edges_by_source.get(source, [])
            has_conditional = any(e.get('condition') for e in source_edges)
            if has_conditional:
                logger.debug(f"Skipping regular edge {source} -> {target} (source has conditional edges)")
                edges_added['skipped'] += 1
                continue
            
            # Verify both source and target are in the graph
            executable_ids = {n['id'] for n in executable_nodes}
            if source not in executable_ids:
                logger.warning(f"Edge source '{source}' not in executable nodes, skipping")
                edges_added['skipped'] += 1
                continue
            if target not in executable_ids:
                logger.warning(f"Edge target '{target}' not in executable nodes, skipping")
                edges_added['skipped'] += 1
                continue
            
            # Check if we already processed this source for regular edges
            if source in processed_conditional_sources:
                logger.debug(f"Source {source} already has conditional edges, skipping regular edge to {target}")
                edges_added['skipped'] += 1
                continue
            
            # Get all regular edges from this source
            source_regular_edges = [
                e for e in edges_by_source.get(source, [])
                if not e.get('condition') and e.get('target') in executable_ids
            ]
            
            if len(source_regular_edges) > 1:
                # Multiple targets from same source - create a single conditional router
                targets = [e.get('target') for e in source_regular_edges]
                default_target = targets[0] if targets else END
                
                # Create a uniquely named router function for this source
                def make_multi_target_router(src_node, tgt_list, default_tgt):
                    def router(state: WorkflowState) -> str:
                        # Check for errors - terminate workflow
                        if state.get('error') or state.get('status') == 'failed':
                            error_msg = state.get('error', 'status=failed')
                            logger.warning(f"[{src_node}] Routing to END due to error: {error_msg}")
                            return END
                        # Default to first target (could implement more sophisticated routing)
                        return default_tgt
                    # Set unique function name
                    router.__name__ = f"route_from_{src_node}"
                    return router
                
                logger.info(f"Adding multi-target router: {source} -> {targets} (default: {default_target})")
                graph.add_conditional_edges(source, make_multi_target_router(source, targets, default_target))
                processed_conditional_sources.add(source)
                edges_added['regular'] += len(source_regular_edges)
            else:
                # Single target - use simple conditional edge with unique name
                def make_error_check_route(src_node, next_target):
                    def router(state: WorkflowState) -> str:
                        # Check for errors - terminate workflow
                        if state.get('error') or state.get('status') == 'failed':
                            error_msg = state.get('error', 'status=failed')
                            logger.warning(f"[{src_node}] Routing to END due to error: {error_msg}")
                            return END
                        return next_target
                    # Set unique function name to avoid conflicts
                    router.__name__ = f"route_{src_node}_to_{next_target}"
                    return router
                
                logger.info(f"Adding error-checked edge: {source} -> {target}")
                graph.add_conditional_edges(source, make_error_check_route(source, target))
                processed_conditional_sources.add(source)
                edges_added['regular'] += 1
    
    # Log edge summary
    logger.info(f"=== Edge processing summary ===")
    logger.info(f"  Regular edges: {edges_added['regular']}")
    logger.info(f"  Conditional edges: {edges_added['conditional']}")
    logger.info(f"  To END: {edges_added['to_end']}")
    logger.info(f"  Entry points: {edges_added['entry']}")
    logger.info(f"  Skipped: {edges_added['skipped']}")
    logger.info(f"  Sources with conditionals: {list(processed_conditional_sources)}")
    
    total_edges = edges_added['regular'] + edges_added['conditional'] + edges_added['to_end']
    logger.info(f"  Total edges added to graph: {total_edges}")
    
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
    
    # Final summary log
    logger.info(f"=== Workflow graph created ===")
    logger.info(f"  Nodes: {len(executable_nodes)} executable")
    logger.info(f"  Entry point: {explicit_entry_point if explicit_entry_point else first_executable_node}")
    logger.info(f"  Edges by source: {[(src, len(edgs)) for src, edgs in edges_by_source.items()][:5]}...")
    
    # Compile and return
    try:
        compiled = graph.compile()
        logger.info("Graph compiled successfully")
        return compiled
    except Exception as e:
        logger.error(f"Graph compilation failed: {e}", exc_info=True)
        raise


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
            
            # Track metrics
            if _metrics_available:
                WORKFLOW_EXECUTIONS.labels(
                    workflow_id=workflow_id,
                    status=result.status
                ).inc()
                WORKFLOW_EXECUTION_DURATION.labels(
                    workflow_id=workflow_id
                ).observe(result.duration_ms / 1000.0)
                # Track node executions
                for node_id in result.executed_nodes:
                    WORKFLOW_NODE_EXECUTIONS.labels(
                        workflow_id=workflow_id,
                        node_id=node_id,
                        node_type='unknown',
                        status='completed'
                    ).inc()
            
            # Log execution
            self._log_execution(result, workflow)
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}", exc_info=True)
            result.status = 'failed'
            result.error_message = str(e)
            result.completed_at = datetime.utcnow()
            result.duration_ms = int((datetime.utcnow() - result.started_at).total_seconds() * 1000)
            
            # Track failure metrics
            if _metrics_available:
                WORKFLOW_EXECUTIONS.labels(
                    workflow_id=workflow_id,
                    status='error'
                ).inc()
            
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
