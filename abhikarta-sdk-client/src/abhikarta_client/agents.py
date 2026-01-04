"""
Abhikarta SDK Client - Agents API

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import AbhikartaClient


class RemoteAgent:
    """Represents a remote agent on the Abhikarta server.
    
    Example:
        >>> agent = client.agents.get("agent-123")
        >>> result = agent.execute("What is AI?")
        >>> print(result['response'])
    """
    
    def __init__(self, client: "AbhikartaClient", data: Dict[str, Any]):
        self._client = client
        self._data = data
        self.id = data.get("id") or data.get("agent_id")
        self.name = data.get("name")
        self.agent_type = data.get("agent_type")
        self.model = data.get("model")
        self.provider = data.get("provider")
        self.system_prompt = data.get("system_prompt", "")
    
    def execute(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Execute the agent with a prompt.
        
        Args:
            prompt: Input prompt for the agent
            **kwargs: Additional execution parameters
            
        Returns:
            Execution result with 'response' key
        """
        data = {"prompt": prompt, **kwargs}
        return self._client.post(f"/api/agents/{self.id}/execute", data=data)
    
    def update(self, **kwargs) -> "RemoteAgent":
        """Update agent configuration.
        
        Args:
            **kwargs: Fields to update (name, system_prompt, etc.)
            
        Returns:
            Updated agent instance
        """
        result = self._client.put(f"/api/agents/{self.id}", data=kwargs)
        self._data.update(result)
        return self
    
    def delete(self) -> bool:
        """Delete this agent."""
        self._client.delete(f"/api/agents/{self.id}")
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Get agent data as dictionary."""
        return self._data
    
    def __repr__(self) -> str:
        return f"RemoteAgent(id={self.id}, name={self.name}, type={self.agent_type})"


class AgentsClient:
    """Client for agent operations.
    
    Provides methods to list, create, get, update, delete, and execute agents.
    
    Example:
        >>> # List all agents
        >>> agents = client.agents.list()
        >>> 
        >>> # Create a new agent
        >>> agent = client.agents.create(
        ...     name="Research Agent",
        ...     agent_type="react",
        ...     model="llama3.2:3b"
        ... )
        >>> 
        >>> # Execute agent
        >>> result = client.agents.execute("agent-id", prompt="Hello!")
    """
    
    def __init__(self, client: "AbhikartaClient"):
        self._client = client
    
    def list(self, agent_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all agents.
        
        Args:
            agent_type: Optional filter by agent type (react, goal, reflect, hierarchical)
            
        Returns:
            List of agent dictionaries
        """
        params = {}
        if agent_type:
            params["agent_type"] = agent_type
        return self._client.get("/api/agents", params=params)
    
    def get(self, agent_id: str) -> RemoteAgent:
        """Get an agent by ID.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            RemoteAgent instance
        """
        data = self._client.get(f"/api/agents/{agent_id}")
        return RemoteAgent(self._client, data)
    
    def create(
        self,
        name: str,
        agent_type: str = "react",
        model: str = "llama3.2:3b",
        provider: str = "ollama",
        system_prompt: str = "",
        tools: Optional[List[str]] = None,
        **kwargs
    ) -> RemoteAgent:
        """Create a new agent.
        
        Args:
            name: Agent name
            agent_type: Type (react, goal, reflect, hierarchical)
            model: LLM model name
            provider: LLM provider (ollama, openai, anthropic)
            system_prompt: System prompt for the agent
            tools: List of tool names to enable
            **kwargs: Additional configuration
            
        Returns:
            Created RemoteAgent instance
        """
        data = {
            "name": name,
            "agent_type": agent_type,
            "model": model,
            "provider": provider,
            "system_prompt": system_prompt,
            "tools": tools or [],
            **kwargs
        }
        result = self._client.post("/api/agents", data=data)
        return RemoteAgent(self._client, result)
    
    def execute(self, agent_id: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Execute an agent directly by ID.
        
        Args:
            agent_id: Agent identifier
            prompt: Input prompt
            **kwargs: Additional execution parameters
            
        Returns:
            Execution result
        """
        data = {"prompt": prompt, **kwargs}
        return self._client.post(f"/api/agents/{agent_id}/execute", data=data)
    
    def delete(self, agent_id: str) -> bool:
        """Delete an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if deleted successfully
        """
        self._client.delete(f"/api/agents/{agent_id}")
        return True
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List available agent templates."""
        return self._client.get("/api/agents/templates")
    
    def create_from_template(self, template_id: str, name: str, **kwargs) -> RemoteAgent:
        """Create an agent from a template.
        
        Args:
            template_id: Template identifier
            name: Name for the new agent
            **kwargs: Override template defaults
            
        Returns:
            Created RemoteAgent instance
        """
        data = {"template_id": template_id, "name": name, **kwargs}
        result = self._client.post("/api/agents/from-template", data=data)
        return RemoteAgent(self._client, result)
