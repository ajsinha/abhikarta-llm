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
    try:
        from langchain import hub
        from langchain.agents import create_react_agent as _create_react_agent
        from langchain.agents import AgentExecutor
    except ImportError:
        raise ImportError("langchain is required. Install with: pip install langchain")
    
    # Get the ReAct prompt from hub or create custom
    if system_prompt:
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        
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
    else:
        prompt = hub.pull("hwchase17/react")
    
    # Create the agent
    agent = _create_react_agent(llm, tools, prompt)
    
    # Create executor with error handling
    return AgentExecutor(
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
    try:
        from langchain.agents import create_tool_calling_agent as _create_tool_calling_agent
        from langchain.agents import AgentExecutor
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    except ImportError:
        raise ImportError("langchain is required. Install with: pip install langchain")
    
    # Create prompt
    system = system_prompt or "You are a helpful AI assistant. Use the available tools to help answer questions."
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create agent
    agent = _create_tool_calling_agent(llm, tools, prompt)
    
    return AgentExecutor(
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
    try:
        from langchain.agents import create_structured_chat_agent as _create_structured_chat_agent
        from langchain.agents import AgentExecutor
        from langchain import hub
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    except ImportError:
        raise ImportError("langchain is required. Install with: pip install langchain")
    
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
    else:
        prompt = hub.pull("hwchase17/structured-chat-agent")
    
    agent = _create_structured_chat_agent(llm, tools, prompt)
    
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10,
        return_intermediate_steps=True
    )


class AgentExecutor:
    """
    High-level agent executor that integrates with the Abhikarta database.
    
    Supports:
    - Multiple agent types (ReAct, tool-calling, structured chat)
    - Automatic tool loading from MCP servers
    - Execution logging to database
    - Human-in-the-loop (HITL) support
    """
    
    AGENT_TYPES = {
        'react': create_react_agent,
        'tool_calling': create_tool_calling_agent,
        'structured_chat': create_structured_chat_agent,
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
        
        try:
            # Load agent configuration
            agent_config = self._load_agent_config(agent_id)
            if not agent_config:
                raise ValueError(f"Agent not found: {agent_id}")
            
            # Apply overrides
            if config_overrides:
                agent_config.update(config_overrides)
            
            result.status = 'running'
            result.metadata['agent_name'] = agent_config.get('name', agent_id)
            
            # Create LLM instance
            llm = self._create_llm(agent_config)
            
            # Create tools
            tools = self._create_tools(agent_config)
            
            # Create agent executor
            agent_type = agent_config.get('agent_type', 'tool_calling')
            system_prompt = agent_config.get('system_prompt', '')
            
            creator_func = self.AGENT_TYPES.get(agent_type, create_tool_calling_agent)
            agent_executor = creator_func(llm, tools, system_prompt)
            
            # Prepare input
            if isinstance(input_data, str):
                agent_input = {"input": input_data}
            else:
                agent_input = input_data
            
            if chat_history:
                agent_input["chat_history"] = chat_history
            
            # Execute agent
            start_time = time.time()
            response = agent_executor.invoke(agent_input)
            result.duration_ms = int((time.time() - start_time) * 1000)
            
            # Extract results
            result.output = response.get('output', str(response))
            
            # Extract intermediate steps
            if 'intermediate_steps' in response:
                for step in response['intermediate_steps']:
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
            
            result.status = 'completed'
            result.completed_at = datetime.utcnow()
            
            # Log execution
            self._log_execution(result, agent_config)
            
        except Exception as e:
            logger.error(f"Agent execution failed: {e}", exc_info=True)
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
            return None
        
        config = dict(agent)
        
        # Parse JSON fields
        for field in ['config_json', 'tools_config', 'parameters_json']:
            if field in config and config[field]:
                try:
                    config[field] = json.loads(config[field])
                except:
                    config[field] = {}
        
        return config
    
    def _create_llm(self, agent_config: Dict) -> Any:
        """Create LLM instance for the agent."""
        from .llm_factory import get_langchain_llm
        
        model_id = agent_config.get('model_id')
        provider_id = agent_config.get('provider_id')
        
        # Get parameters
        params = agent_config.get('parameters_json', {})
        if isinstance(params, str):
            params = json.loads(params)
        
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
