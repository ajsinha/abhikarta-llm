"""
Abhikarta SDK Embedded - Standalone AI Agent Development
========================================================

Build AI agents, workflows, swarms, and organizations without a server.
Perfect for standalone applications, notebooks, and embedded use cases.

Quick Start:
    >>> from abhikarta_embedded import Agent
    >>> 
    >>> # Create an agent in 3 lines
    >>> agent = Agent.create("react", model="ollama/llama3.2:3b")
    >>> result = agent.run("What is the capital of France?")
    >>> print(result.response)
    
Using Decorators:
    >>> from abhikarta_embedded import agent, tool
    >>> 
    >>> @tool(description="Search the web")
    >>> def web_search(query: str) -> dict:
    ...     return {"results": ["Result 1", "Result 2"]}
    >>> 
    >>> @agent(type="react", tools=[web_search])
    >>> class ResearchAgent:
    ...     system_prompt = "You are a research assistant."
    >>> 
    >>> my_agent = ResearchAgent()
    >>> result = my_agent.run("Research AI trends")

For server-based usage, see `abhikarta-sdk-client` instead.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Version: 1.4.8
"""

__version__ = "1.4.8"
__author__ = "Ashutosh Sinha"
__email__ = "ajsinha@gmail.com"

# Core
from .core import (
    Abhikarta,
    AbhikartaConfig,
)

# Agents
from .agents import (
    Agent,
    BaseAgent,
    ReActAgent,
    GoalAgent,
    ReflectAgent,
    HierarchicalAgent,
    AgentConfig,
    AgentResult,
)

# Workflows
from .workflows import (
    Workflow,
    BaseWorkflow,
    DAGWorkflow,
    Node,
    Edge,
    WorkflowConfig,
    WorkflowResult,
)

# Swarms
from .swarms import (
    Swarm,
    BaseSwarm,
    SwarmAgent,
    SwarmConfig,
    SwarmResult,
)

# Organizations
from .orgs import (
    Organization,
    BaseOrganization,
    OrgNode,
    OrgTask,
    OrgConfig,
    OrgResult,
)

# Tools
from .tools import (
    Tool,
    BaseTool,
    ToolRegistry,
)

# Providers
from .providers import (
    Provider,
    BaseProvider,
    OllamaProvider,
    OpenAIProvider,
    AnthropicProvider,
    ProviderConfig,
)

# Decorators
from .decorators import (
    agent,
    workflow,
    swarm,
    organization,
    tool,
)

__all__ = [
    # Version
    "__version__",
    "__author__",
    # Core
    "Abhikarta",
    "AbhikartaConfig",
    # Agents
    "Agent",
    "BaseAgent",
    "ReActAgent",
    "GoalAgent",
    "ReflectAgent",
    "HierarchicalAgent",
    "AgentConfig",
    "AgentResult",
    # Workflows
    "Workflow",
    "BaseWorkflow",
    "DAGWorkflow",
    "Node",
    "Edge",
    "WorkflowConfig",
    "WorkflowResult",
    # Swarms
    "Swarm",
    "BaseSwarm",
    "SwarmAgent",
    "SwarmConfig",
    "SwarmResult",
    # Organizations
    "Organization",
    "BaseOrganization",
    "OrgNode",
    "OrgTask",
    "OrgConfig",
    "OrgResult",
    # Tools
    "Tool",
    "BaseTool",
    "ToolRegistry",
    # Providers
    "Provider",
    "BaseProvider",
    "OllamaProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "ProviderConfig",
    # Decorators
    "agent",
    "workflow",
    "swarm",
    "organization",
    "tool",
]
