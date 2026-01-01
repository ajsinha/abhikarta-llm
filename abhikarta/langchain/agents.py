"""
LangChain Agents - Agent creation and execution using LangChain.

Supports:
- ReAct agents (reasoning + acting)
- Tool-calling agents (OpenAI function calling, Anthropic tool use)
- Structured chat agents
- Custom agent types

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import json
import logging
import time
import uuid
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# =============================================================================
# LangChain Import Compatibility Layer
# Handles different LangChain versions and Python 3.14 compatibility
# =============================================================================

_langchain_available = False
_LangChainAgentExecutor = None
_create_react_agent_func = None
_create_tool_calling_agent_func = None
_create_structured_chat_agent_func = None
_hub = None
_python_314_mode = False

import sys
if sys.version_info >= (3, 14):
    _python_314_mode = True
    logger.warning("Python 3.14+ detected. Using simplified agent mode due to Pydantic compatibility issues.")

# Try importing LangChain components
if not _python_314_mode:
    try:
        from langchain.agents import AgentExecutor as _LangChainAgentExecutor
        _langchain_available = True
        logger.info("LangChain AgentExecutor imported successfully")
    except ImportError as e:
        logger.warning(f"Could not import AgentExecutor from langchain.agents: {e}")
    except Exception as e:
        logger.warning(f"Error importing langchain.agents (Python 3.14 compatibility?): {e}")
        _python_314_mode = True

    # Try to import create_react_agent
    if not _python_314_mode:
        try:
            from langchain.agents import create_react_agent as _create_react_agent_func
            logger.info("create_react_agent imported from langchain.agents")
        except ImportError:
            try:
                from langchain.agents.react.agent import create_react_agent as _create_react_agent_func
                logger.info("create_react_agent imported from langchain.agents.react.agent")
            except ImportError as e:
                logger.warning(f"Could not import create_react_agent: {e}")

    # Try to import create_tool_calling_agent
    if not _python_314_mode:
        try:
            from langchain.agents import create_tool_calling_agent as _create_tool_calling_agent_func
            logger.info("create_tool_calling_agent imported from langchain.agents")
        except ImportError:
            try:
                from langchain.agents.tool_calling_agent.base import create_tool_calling_agent as _create_tool_calling_agent_func
                logger.info("create_tool_calling_agent imported from langchain.agents.tool_calling_agent.base")
            except ImportError:
                try:
                    from langchain_core.agents import create_tool_calling_agent as _create_tool_calling_agent_func
                    logger.info("create_tool_calling_agent imported from langchain_core.agents")
                except ImportError as e:
                    logger.warning(f"Could not import create_tool_calling_agent: {e}")

    # Try to import create_structured_chat_agent
    if not _python_314_mode:
        try:
            from langchain.agents import create_structured_chat_agent as _create_structured_chat_agent_func
            logger.info("create_structured_chat_agent imported from langchain.agents")
        except ImportError:
            try:
                from langchain.agents.structured_chat.base import create_structured_chat_agent as _create_structured_chat_agent_func
                logger.info("create_structured_chat_agent imported from langchain.agents.structured_chat.base")
            except ImportError as e:
                logger.warning(f"Could not import create_structured_chat_agent: {e}")

    # Try to import hub
    try:
        from langchain import hub as _hub
        logger.info("LangChain hub imported successfully")
    except ImportError:
        try:
            from langchainhub import hub as _hub
            logger.info("langchainhub imported as hub")
        except ImportError as e:
            logger.warning(f"Could not import langchain hub: {e}")

# Python 3.14 mode - use simplified imports that avoid Pydantic v1
if _python_314_mode:
    logger.info("Running in Python 3.14 compatibility mode - using simplified agent execution")
    _langchain_available = True  # We'll use langchain-core directly


@dataclass
class AgentExecutionResult:
    """Result of an agent execution."""
    execution_id: str
    agent_id: str
    status: str = 'pending'  # pending, running, completed, failed
    input_data: Any = None
    output: str = ''
    intermediate_steps: List[Dict] = field(default_factory=list)
    tool_calls: List[Dict] = field(default_factory=list)
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: int = 0
    token_usage: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'execution_id': self.execution_id,
            'agent_id': self.agent_id,
            'status': self.status,
            'input_data': self.input_data,
            'output': self.output,
            'intermediate_steps': self.intermediate_steps,
            'tool_calls': self.tool_calls,
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_ms': self.duration_ms,
            'token_usage': self.token_usage,
            'metadata': self.metadata
        }


def create_react_agent(llm, tools: List, system_prompt: str = None) -> Any:
    """
    Create a ReAct (Reasoning + Acting) agent.
    
    ReAct agents alternate between reasoning about what to do and taking actions.
    They work well with most LLM providers.
    
    Args:
        llm: LangChain LLM instance
        tools: List of LangChain tools
        system_prompt: Optional system prompt
        
    Returns:
        LangChain agent executor
    """
    # Python 3.14 mode - fall back to conversational
    if _python_314_mode:
        logger.warning("Python 3.14 mode: Using conversational agent instead of ReAct")
        return create_conversational_agent(llm, tools, system_prompt)
    
    if not _langchain_available or _LangChainAgentExecutor is None:
        raise ImportError("langchain is required. Install with: pip install langchain langchain-core")
    
    if _create_react_agent_func is None:
        raise ImportError("create_react_agent not available. Install with: pip install langchain>=0.2.0")
    
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    
    # Get the ReAct prompt from hub or create custom
    if system_prompt:
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt + """

You have access to the following tools:
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question"""),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
    elif _hub:
        prompt = _hub.pull("hwchase17/react")
    else:
        # Fallback prompt if hub not available
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question"""),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
    
    # Create the agent
    agent = _create_react_agent_func(llm, tools, prompt)
    
    # Create executor with error handling
    return _LangChainAgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10,
        return_intermediate_steps=True
    )


def create_tool_calling_agent(llm, tools: List, system_prompt: str = None) -> Any:
    """
    Create a tool-calling agent (uses native tool calling for OpenAI/Anthropic/etc).
    
    This is the recommended agent type for LLMs that support native tool/function calling
    like OpenAI, Anthropic Claude, and Google Gemini.
    
    Args:
        llm: LangChain LLM instance
        tools: List of LangChain tools
        system_prompt: Optional system prompt
        
    Returns:
        LangChain agent executor
    """
    # Python 3.14 mode - fall back to conversational
    if _python_314_mode:
        logger.warning("Python 3.14 mode: Using conversational agent instead of tool_calling")
        return create_conversational_agent(llm, tools, system_prompt)
    
    if not _langchain_available or _LangChainAgentExecutor is None:
        raise ImportError("langchain is required. Install with: pip install langchain langchain-core")
    
    if _create_tool_calling_agent_func is None:
        # Fall back to structured chat agent if tool_calling not available
        logger.warning("create_tool_calling_agent not available, falling back to structured_chat")
        return create_structured_chat_agent(llm, tools, system_prompt)
    
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    
    # Create prompt
    system = system_prompt or "You are a helpful AI assistant. Use the available tools to help answer questions."
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create agent
    agent = _create_tool_calling_agent_func(llm, tools, prompt)
    
    return _LangChainAgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10,
        return_intermediate_steps=True
    )


def create_structured_chat_agent(llm, tools: List, system_prompt: str = None) -> Any:
    """
    Create a structured chat agent.
    
    Structured chat agents use a structured output format and work well
    with chat models. Good for multi-turn conversations.
    
    Args:
        llm: LangChain LLM instance
        tools: List of LangChain tools
        system_prompt: Optional system prompt
        
    Returns:
        LangChain agent executor
    """
    # Python 3.14 mode - fall back to conversational
    if _python_314_mode:
        logger.warning("Python 3.14 mode: Using conversational agent instead of structured_chat")
        return create_conversational_agent(llm, tools, system_prompt)
    
    if not _langchain_available or _LangChainAgentExecutor is None:
        raise ImportError("langchain is required. Install with: pip install langchain langchain-core")
    
    if _create_structured_chat_agent_func is None:
        # Fall back to conversational agent if structured_chat not available
        logger.warning("create_structured_chat_agent not available, falling back to conversational")
        return create_conversational_agent(llm, tools, system_prompt)
    
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    
    if system_prompt:
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt + """

Respond to the human as helpfully and accurately as possible. You have access to the following tools:

{tools}

Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).

Valid "action" values: "Final Answer" or {tool_names}

Provide only ONE action per $JSON_BLOB, as shown:

```
{{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}}
```

Follow this format:

Question: input question to answer
Thought: consider previous and subsequent steps
Action:
```
$JSON_BLOB
```
Observation: action result
... (repeat Thought/Action/Observation N times)
Thought: I know what to respond
Action:
```
{{
  "action": "Final Answer",
  "action_input": "Final response to human"
}}
```"""),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}\n\n{agent_scratchpad}"),
        ])
    elif _hub:
        prompt = _hub.pull("hwchase17/structured-chat-agent")
    else:
        # Fallback prompt if hub not available
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Respond to the human as helpfully and accurately as possible. You have access to the following tools:

{tools}

Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).

Valid "action" values: "Final Answer" or {tool_names}

Provide only ONE action per $JSON_BLOB, as shown:

```
{{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}}
```

Follow this format:

Question: input question to answer
Thought: consider previous and subsequent steps
Action:
```
$JSON_BLOB
```
Observation: action result
... (repeat Thought/Action/Observation N times)
Thought: I know what to respond
Action:
```
{{
  "action": "Final Answer",
  "action_input": "Final response to human"
}}
```"""),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}\n\n{agent_scratchpad}"),
        ])
    
    agent = _create_structured_chat_agent_func(llm, tools, prompt)
    
    return _LangChainAgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10,
        return_intermediate_steps=True
    )


def create_conversational_agent(llm, tools: List, system_prompt: str = None) -> Any:
    """
    Create a simple conversational agent.
    
    This agent type is for basic conversation without tool use.
    It simply passes the input to the LLM and returns the response.
    
    Args:
        llm: LangChain LLM instance
        tools: List of LangChain tools (not used for conversational)
        system_prompt: Optional system prompt
        
    Returns:
        A callable that wraps the LLM for conversation
    """
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnablePassthrough
    
    logger.info("[CONVERSATIONAL] Creating conversational agent")
    
    system = system_prompt or "You are a helpful AI assistant. Respond naturally to the user's questions and requests."
    logger.info(f"[CONVERSATIONAL] System prompt: {system[:100]}...")
    
    # Create a simple chat chain
    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
    ])
    
    chain = prompt | llm | StrOutputParser()
    logger.info("[CONVERSATIONAL] Chain created successfully")
    
    # Wrap in a class that mimics AgentExecutor interface
    class ConversationalWrapper:
        def __init__(self, chain):
            self.chain = chain
            
        def invoke(self, inputs):
            """Execute the conversational chain."""
            logger.info(f"[CONVERSATIONAL] Invoking with input: {str(inputs)[:200]}...")
            try:
                result = self.chain.invoke(inputs)
                logger.info(f"[CONVERSATIONAL] Got response: {str(result)[:200]}...")
                return {
                    'output': result,
                    'intermediate_steps': []
                }
            except Exception as e:
                logger.error(f"[CONVERSATIONAL] Error: {e}", exc_info=True)
                return {
                    'output': f"I encountered an error: {str(e)}",
                    'intermediate_steps': []
                }
    
    return ConversationalWrapper(chain)


def create_plan_execute_agent(llm, tools: List, system_prompt: str = None) -> Any:
    """
    Create a plan-and-execute agent.
    
    This agent first creates a plan, then executes each step.
    Falls back to ReAct if plan-execute is not available.
    
    Args:
        llm: LangChain LLM instance
        tools: List of LangChain tools
        system_prompt: Optional system prompt
        
    Returns:
        LangChain agent executor
    """
    try:
        from langchain_experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
        
        planner = load_chat_planner(llm)
        executor = load_agent_executor(llm, tools, verbose=True)
        
        return PlanAndExecute(planner=planner, executor=executor, verbose=True)
    except ImportError:
        logger.warning("Plan-and-execute not available, falling back to ReAct")
        return create_react_agent(llm, tools, system_prompt)


class AgentExecutor:
    """
    High-level agent executor that integrates with the Abhikarta database.
    
    Supports:
    - Multiple agent types (ReAct, tool-calling, structured chat, conversational)
    - Automatic tool loading from MCP servers
    - Execution logging to database
    - Human-in-the-loop (HITL) support
    """
    
    AGENT_TYPES = {
        'react': create_react_agent,
        'tool_calling': create_tool_calling_agent,
        'structured_chat': create_structured_chat_agent,
        'conversational': create_conversational_agent,
        'plan_and_execute': create_plan_execute_agent,
        'plan_execute': create_plan_execute_agent,
    }
    
    def __init__(self, db_facade, llm_factory=None, tool_factory=None):
        """
        Initialize the agent executor.
        
        Args:
            db_facade: Database facade for reading configs and logging
            llm_factory: Optional LLM factory (uses default if not provided)
            tool_factory: Optional tool factory (uses default if not provided)
        """
        self.db_facade = db_facade
        self.llm_factory = llm_factory
        self.tool_factory = tool_factory
    
    def execute_agent(self, agent_id: str, input_data: Any, 
                     chat_history: List = None,
                     config_overrides: Dict = None) -> AgentExecutionResult:
        """
        Execute an agent with the given input.
        
        Args:
            agent_id: ID of the agent to execute
            input_data: Input to the agent (string or dict)
            chat_history: Optional chat history for multi-turn conversations
            config_overrides: Optional configuration overrides
            
        Returns:
            AgentExecutionResult with execution details
        """
        execution_id = str(uuid.uuid4())
        result = AgentExecutionResult(
            execution_id=execution_id,
            agent_id=agent_id,
            input_data=input_data,
            started_at=datetime.utcnow()
        )
        
        logger.info(f"[AGENT:{agent_id}] Starting execution: {execution_id}")
        logger.info(f"[AGENT:{agent_id}] Input: {str(input_data)[:500]}...")
        
        try:
            # Load agent configuration
            agent_config = self._load_agent_config(agent_id)
            if not agent_config:
                raise ValueError(f"Agent not found: {agent_id}")
            
            logger.info(f"[AGENT:{agent_id}] Loaded config for: {agent_config.get('name', agent_id)}")
            logger.info(f"[AGENT:{agent_id}] Agent type: {agent_config.get('agent_type', 'unknown')}")
            
            # Apply overrides
            if config_overrides:
                agent_config.update(config_overrides)
            
            result.status = 'running'
            result.metadata['agent_name'] = agent_config.get('name', agent_id)
            
            # Create LLM instance
            logger.info(f"[AGENT:{agent_id}] Creating LLM instance...")
            llm = self._create_llm(agent_config)
            logger.info(f"[AGENT:{agent_id}] LLM created successfully")
            
            # Create tools
            logger.info(f"[AGENT:{agent_id}] Creating tools...")
            tools = self._create_tools(agent_config)
            logger.info(f"[AGENT:{agent_id}] Tools created: {[t.name if hasattr(t, 'name') else str(t) for t in tools]}")
            
            # Create agent executor
            agent_type = agent_config.get('agent_type', 'tool_calling')
            system_prompt = agent_config.get('system_prompt', '')
            
            logger.info(f"[AGENT:{agent_id}] Creating {agent_type} agent executor...")
            if system_prompt:
                logger.info(f"[AGENT:{agent_id}] System prompt: {system_prompt[:200]}...")
            
            creator_func = self.AGENT_TYPES.get(agent_type, create_tool_calling_agent)
            agent_executor = creator_func(llm, tools, system_prompt)
            logger.info(f"[AGENT:{agent_id}] Agent executor created")
            
            # Prepare input
            if isinstance(input_data, str):
                agent_input = {"input": input_data}
            else:
                agent_input = input_data
            
            if chat_history:
                agent_input["chat_history"] = chat_history
            
            # Execute agent
            logger.info(f"[AGENT:{agent_id}] Invoking agent...")
            start_time = time.time()
            response = agent_executor.invoke(agent_input)
            result.duration_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"[AGENT:{agent_id}] Agent completed in {result.duration_ms}ms")
            
            # Extract results
            result.output = response.get('output', str(response))
            logger.info(f"[AGENT:{agent_id}] Output: {result.output[:500]}...")
            
            # Extract intermediate steps
            if 'intermediate_steps' in response:
                logger.info(f"[AGENT:{agent_id}] Processing {len(response['intermediate_steps'])} intermediate steps")
                for i, step in enumerate(response['intermediate_steps']):
                    if isinstance(step, tuple) and len(step) >= 2:
                        action, observation = step[0], step[1]
                        step_dict = {
                            'action': str(action.tool) if hasattr(action, 'tool') else str(action),
                            'action_input': str(action.tool_input) if hasattr(action, 'tool_input') else '',
                            'observation': str(observation)
                        }
                        result.intermediate_steps.append(step_dict)
                        result.tool_calls.append({
                            'tool': step_dict['action'],
                            'input': step_dict['action_input'],
                            'output': step_dict['observation']
                        })
                        logger.info(f"[AGENT:{agent_id}] Step {i+1}: {step_dict['action']} -> {str(step_dict['observation'])[:200]}...")
            
            result.status = 'completed'
            result.completed_at = datetime.utcnow()
            
            logger.info(f"[AGENT:{agent_id}] Execution completed successfully")
            
            # Log execution
            self._log_execution(result, agent_config)
            
        except Exception as e:
            logger.error(f"[AGENT:{agent_id}] Execution failed: {e}", exc_info=True)
            result.status = 'failed'
            result.error_message = str(e)
            result.completed_at = datetime.utcnow()
            result.duration_ms = int((datetime.utcnow() - result.started_at).total_seconds() * 1000)
            
            # Log failed execution
            self._log_execution(result, {})
        
        return result
    
    def _load_agent_config(self, agent_id: str) -> Optional[Dict]:
        """Load agent configuration from database."""
        agent = self.db_facade.fetch_one(
            "SELECT * FROM agents WHERE agent_id = ?",
            (agent_id,)
        )
        
        if not agent:
            logger.warning(f"[AGENT] Agent not found in database: {agent_id}")
            return None
        
        config = dict(agent)
        logger.info(f"[AGENT] Loaded agent from DB: {config.get('name', agent_id)}")
        
        # Parse the main config field which contains llm_config, workflow, tools, etc.
        main_config = config.get('config', '{}')
        if isinstance(main_config, str):
            try:
                main_config = json.loads(main_config)
            except:
                main_config = {}
        
        # Store parsed config for easy access
        config['config_json'] = main_config
        
        # Extract llm_config, workflow, tools from main config
        if 'llm_config' in main_config:
            config['llm_config'] = main_config['llm_config']
            logger.info(f"[AGENT] Found llm_config: {main_config['llm_config']}")
        if 'workflow' in main_config:
            config['workflow'] = main_config['workflow']
        if 'tools' in main_config:
            config['tools'] = main_config['tools']
        if 'hitl_config' in main_config:
            config['hitl_config'] = main_config['hitl_config']
        
        # Also get system_prompt from main config or workflow
        if 'system_prompt' in main_config:
            config['system_prompt'] = main_config['system_prompt']
        elif 'workflow' in main_config:
            # Try to extract from workflow nodes
            workflow = main_config.get('workflow', {})
            nodes = workflow.get('nodes', [])
            for node in nodes:
                if node.get('node_type') == 'llm' and node.get('config', {}).get('system_prompt'):
                    config['system_prompt'] = node['config']['system_prompt']
                    break
        
        # Parse JSON fields if they exist as columns
        for field in ['config_json', 'tools_config', 'parameters_json']:
            if field in config and config[field] and isinstance(config[field], str):
                try:
                    config[field] = json.loads(config[field])
                except:
                    config[field] = {}
        
        logger.info(f"[AGENT] Agent type: {config.get('agent_type')}")
        logger.info(f"[AGENT] System prompt: {config.get('system_prompt', 'None')[:100]}...")
        
        return config
    
    def _create_llm(self, agent_config: Dict) -> Any:
        """Create LLM instance for the agent."""
        from .llm_factory import get_langchain_llm
        
        model_id = agent_config.get('model_id')
        provider_id = agent_config.get('provider_id')
        
        # Get parameters from agent config
        params = agent_config.get('parameters_json', {})
        if isinstance(params, str):
            params = json.loads(params)
        
        # Also check for llm_config in the config
        config = agent_config.get('config_json', {})
        if isinstance(config, str):
            try:
                config = json.loads(config)
            except:
                config = {}
        
        llm_config = config.get('llm_config', {})
        
        logger.info(f"[AGENT] LLM Config from agent: model_id={model_id}, provider_id={provider_id}")
        logger.info(f"[AGENT] LLM Config from config_json: {llm_config}")
        logger.info(f"[AGENT] Parameters: {params}")
        
        # If we have llm_config with provider/model, use those
        if llm_config.get('provider') and llm_config.get('model'):
            provider = llm_config.get('provider')
            model = llm_config.get('model')
            base_url = llm_config.get('base_url')
            temperature = llm_config.get('temperature', params.get('temperature', 0.7))
            max_tokens = llm_config.get('max_tokens', params.get('max_tokens', 2000))
            
            logger.info(f"[AGENT] Creating LLM from llm_config: provider={provider}, model={model}, base_url={base_url}")
            
            # Create LLM directly based on provider
            if provider == 'ollama':
                try:
                    from langchain_ollama import ChatOllama
                    llm = ChatOllama(
                        model=model,
                        base_url=base_url or 'http://localhost:11434',
                        temperature=temperature
                    )
                    logger.info(f"[AGENT] Created ChatOllama: model={model}, base_url={base_url}")
                    return llm
                except ImportError as e:
                    logger.error(f"[AGENT] Failed to import langchain_ollama: {e}")
                    # Try to provide more diagnostic info
                    try:
                        import importlib.util
                        spec = importlib.util.find_spec('langchain_ollama')
                        if spec is None:
                            logger.error("[AGENT] langchain_ollama package not found in Python path")
                        else:
                            logger.error(f"[AGENT] langchain_ollama found at: {spec.origin}")
                    except Exception as diag_e:
                        logger.error(f"[AGENT] Diagnostic check failed: {diag_e}")
                    
                    # Fall through to factory method
                    logger.warning("[AGENT] Falling back to LLM factory method")
                except Exception as e:
                    logger.error(f"[AGENT] Error creating ChatOllama: {type(e).__name__}: {e}")
                    raise
        
        # Fallback to factory method
        return get_langchain_llm(
            self.db_facade,
            model_id=model_id,
            provider_id=provider_id,
            temperature=params.get('temperature', 0.7),
            max_tokens=params.get('max_tokens', 2000)
        )
    
    def _create_tools(self, agent_config: Dict) -> List:
        """Create tools for the agent."""
        from .tools import ToolFactory
        
        tools = []
        factory = self.tool_factory or ToolFactory(self.db_facade)
        
        tools_config = agent_config.get('tools_config', {})
        if isinstance(tools_config, str):
            tools_config = json.loads(tools_config)
        
        # Add MCP tools if configured
        if tools_config.get('include_mcp', True):
            mcp_server_ids = tools_config.get('mcp_servers', [])
            if mcp_server_ids:
                for server_id in mcp_server_ids:
                    tools.extend(factory.get_mcp_tools(server_id))
            else:
                tools.extend(factory.get_mcp_tools())
        
        # Add code fragment tools
        code_fragments = tools_config.get('code_fragments', [])
        for frag_id in code_fragments:
            try:
                tools.append(factory.get_code_fragment_tool(frag_id))
            except Exception as e:
                logger.warning(f"Failed to load code fragment {frag_id}: {e}")
        
        # Add built-in tools
        builtin_tools = tools_config.get('builtin_tools', [])
        if builtin_tools:
            tools.extend(factory.get_builtin_tools(builtin_tools))
        
        return tools
    
    def _log_execution(self, result: AgentExecutionResult, agent_config: Dict):
        """Log agent execution to database."""
        try:
            self.db_facade.execute(
                """INSERT INTO agent_executions
                   (execution_id, agent_id, status, input_data, output_data,
                    error_message, duration_ms, metadata, started_at, completed_at,
                    created_by, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                (
                    result.execution_id,
                    result.agent_id,
                    result.status,
                    json.dumps(result.input_data) if result.input_data else None,
                    result.output,
                    result.error_message,
                    result.duration_ms,
                    json.dumps({
                        'intermediate_steps': result.intermediate_steps,
                        'tool_calls': result.tool_calls,
                        'token_usage': result.token_usage,
                        **result.metadata
                    }),
                    result.started_at.isoformat() if result.started_at else None,
                    result.completed_at.isoformat() if result.completed_at else None,
                    'system'
                )
            )
        except Exception as e:
            logger.warning(f"Failed to log agent execution: {e}")


def execute_agent_from_config(db_facade, agent_id: str, input_data: Any,
                             chat_history: List = None) -> AgentExecutionResult:
    """
    Convenience function to execute an agent from database configuration.
    
    Args:
        db_facade: Database facade
        agent_id: Agent ID
        input_data: Input to the agent
        chat_history: Optional chat history
        
    Returns:
        AgentExecutionResult
    """
    executor = AgentExecutor(db_facade)
    return executor.execute_agent(agent_id, input_data, chat_history)
