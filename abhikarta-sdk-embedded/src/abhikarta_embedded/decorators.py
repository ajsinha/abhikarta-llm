"""
Abhikarta SDK Embedded - Decorators for Pythonic agent/workflow definition.

Example:
    >>> @agent(type="react", model="ollama/llama3.2:3b")
    >>> class ResearchAgent:
    ...     system_prompt = "You are a research assistant."
    >>> 
    >>> my_agent = ResearchAgent()
    >>> result = my_agent.run("Research AI trends")
"""

from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type


def tool(name: str = None, description: str = None):
    """Decorator to create a tool from a function.
    
    Example:
        >>> @tool(description="Search the web")
        >>> def web_search(query: str) -> dict:
        ...     return {"results": ["Result 1"]}
    """
    def decorator(func: Callable) -> Callable:
        from .tools import Tool
        tool_name = name or func.__name__
        tool_desc = description or func.__doc__ or ""
        
        # Create tool and attach to function
        func._tool = Tool(tool_name, tool_desc, func)
        func.name = tool_name
        func.description = tool_desc
        return func
    return decorator


def agent(type: str = "react", model: str = "llama3.2:3b", provider: str = "ollama",
          tools: List[Callable] = None, **config):
    """Decorator to create an agent from a class.
    
    Example:
        >>> @agent(type="react", model="ollama/llama3.2:3b")
        >>> class MyAgent:
        ...     system_prompt = "You are helpful."
    """
    def decorator(cls: Type) -> Type:
        original_init = cls.__init__ if hasattr(cls, '__init__') else None
        
        def new_init(self, *args, **kwargs):
            from .agents import Agent
            from .providers import Provider
            
            # Get system prompt from class attribute
            system_prompt = getattr(cls, 'system_prompt', '')
            
            # Create agent
            self._agent = Agent.create(
                agent_type=type,
                name=cls.__name__,
                model=model,
                provider=provider,
                system_prompt=system_prompt,
                **config
            )
            
            # Configure provider
            if "/" in model:
                prov_name, _ = model.split("/", 1)
            else:
                prov_name = provider
            
            try:
                self._agent.provider = Provider.create(prov_name)
            except Exception:
                pass  # Provider will be set later
            
            if original_init:
                original_init(self, *args, **kwargs)
        
        def run(self, prompt: str, **kwargs):
            return self._agent.run(prompt, **kwargs)
        
        cls.__init__ = new_init
        cls.run = run
        return cls
    return decorator


def workflow(name: str = None, **config):
    """Decorator to create a workflow from a class.
    
    Example:
        >>> @workflow
        >>> class DataPipeline:
        ...     @workflow.node(type="input")
        ...     def input_node(self, data): return data
    """
    def decorator(cls: Type) -> Type:
        workflow_name = name or cls.__name__
        
        def new_init(self):
            from .workflows import Workflow
            # Collect node methods
            nodes = []
            for attr_name in dir(cls):
                attr = getattr(cls, attr_name)
                if hasattr(attr, '_node_config'):
                    nodes.append(attr._node_config)
            self._workflow = None  # Would build workflow from nodes
        
        def execute(self, input_data):
            if self._workflow:
                return self._workflow.execute(input_data)
            return {"error": "Workflow not configured"}
        
        cls.__init__ = new_init
        cls.execute = execute
        return cls
    return decorator

# Allow @workflow.node() syntax
def node(type: str = "llm", depends: List[str] = None, **config):
    """Decorator for workflow node methods."""
    def decorator(func: Callable) -> Callable:
        func._node_config = {
            "id": func.__name__,
            "name": func.__name__,
            "node_type": type,
            "depends": depends or [],
            "config": config
        }
        return func
    return decorator

workflow.node = staticmethod(node)


def swarm(name: str = None, strategy: str = "collaborative", **config):
    """Decorator to create a swarm from a class."""
    def decorator(cls: Type) -> Type:
        swarm_name = name or cls.__name__
        
        def new_init(self):
            from .swarms import Swarm
            agents = getattr(cls, 'agents', [])
            self._swarm = Swarm.create(swarm_name, agents, strategy)
        
        def execute(self, task: str, **kwargs):
            return self._swarm.execute(task, **kwargs)
        
        cls.__init__ = new_init
        cls.execute = execute
        return cls
    return decorator


def organization(name: str = None, **config):
    """Decorator to create an organization from a class."""
    def decorator(cls: Type) -> Type:
        org_name = name or cls.__name__
        
        def new_init(self):
            from .orgs import Organization
            nodes = getattr(cls, 'nodes', [])
            root = getattr(cls, 'root_node_id', None)
            self._org = Organization.create(org_name, nodes, root)
        
        def submit_task(self, title: str, description: str, **kwargs):
            return self._org.submit_task(title, description, **kwargs)
        
        cls.__init__ = new_init
        cls.submit_task = submit_task
        return cls
    return decorator
