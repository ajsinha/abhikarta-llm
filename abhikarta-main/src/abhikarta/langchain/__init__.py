"""
LangChain Integration Module - LLM providers, agents, and tools using LangChain.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import sys
import logging

logger = logging.getLogger(__name__)

# Lazy imports to handle Python 3.14 compatibility issues
_llm_factory_module = None
_tools_module = None
_agents_module = None
_workflow_graph_module = None

def _get_llm_factory():
    global _llm_factory_module
    if _llm_factory_module is None:
        from . import llm_factory as _llm_factory_module
    return _llm_factory_module

def _get_tools():
    global _tools_module
    if _tools_module is None:
        from . import tools as _tools_module
    return _tools_module

def _get_agents():
    global _agents_module
    if _agents_module is None:
        from . import agents as _agents_module
    return _agents_module

def _get_workflow_graph():
    global _workflow_graph_module
    if _workflow_graph_module is None:
        from . import workflow_graph as _workflow_graph_module
    return _workflow_graph_module

# For direct imports, provide lazy getters
def __getattr__(name):
    """Lazy attribute loading to avoid import errors on Python 3.14."""
    if name == 'LLMFactory':
        return _get_llm_factory().LLMFactory
    elif name == 'get_langchain_llm':
        return _get_llm_factory().get_langchain_llm
    elif name == 'ToolFactory':
        return _get_tools().ToolFactory
    elif name == 'MCPToolAdapter':
        return _get_tools().MCPToolAdapter
    elif name == 'create_langchain_tool':
        return _get_tools().create_langchain_tool
    elif name == 'AgentExecutor':
        return _get_agents().AgentExecutor
    elif name == 'create_react_agent':
        return _get_agents().create_react_agent
    elif name == 'create_tool_calling_agent':
        return _get_agents().create_tool_calling_agent
    elif name == 'WorkflowGraphExecutor':
        return _get_workflow_graph().WorkflowGraphExecutor
    elif name == 'create_workflow_graph':
        return _get_workflow_graph().create_workflow_graph
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    'LLMFactory',
    'get_langchain_llm',
    'ToolFactory',
    'MCPToolAdapter',
    'create_langchain_tool',
    'AgentExecutor',
    'create_react_agent',
    'create_tool_calling_agent',
    'WorkflowGraphExecutor',
    'create_workflow_graph'
]
