"""
Abhikarta SDK Client - Swarms API

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import AbhikartaClient


class RemoteSwarm:
    """Represents a remote swarm on the Abhikarta server."""
    
    def __init__(self, client: "AbhikartaClient", data: Dict[str, Any]):
        self._client = client
        self._data = data
        self.id = data.get("id") or data.get("swarm_id")
        self.name = data.get("name")
        self.strategy = data.get("strategy", "")
        self.agents = data.get("agents", [])
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute the swarm with a task."""
        data = {"task": task, **kwargs}
        return self._client.post(f"/api/swarms/{self.id}/execute", data=data)
    
    def delete(self) -> bool:
        """Delete this swarm."""
        self._client.delete(f"/api/swarms/{self.id}")
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return self._data
    
    def __repr__(self) -> str:
        return f"RemoteSwarm(id={self.id}, name={self.name})"


class SwarmsClient:
    """Client for swarm operations."""
    
    def __init__(self, client: "AbhikartaClient"):
        self._client = client
    
    def list(self) -> List[Dict[str, Any]]:
        """List all swarms."""
        return self._client.get("/api/swarms")
    
    def get(self, swarm_id: str) -> RemoteSwarm:
        """Get a swarm by ID."""
        data = self._client.get(f"/api/swarms/{swarm_id}")
        return RemoteSwarm(self._client, data)
    
    def create(
        self,
        name: str,
        agents: List[Dict[str, Any]],
        strategy: str = "event_driven",
        **kwargs
    ) -> RemoteSwarm:
        """Create a new swarm."""
        data = {"name": name, "agents": agents, "strategy": strategy, **kwargs}
        result = self._client.post("/api/swarms", data=data)
        return RemoteSwarm(self._client, result)
    
    def execute(self, swarm_id: str, task: str, **kwargs) -> Dict[str, Any]:
        """Execute a swarm directly by ID."""
        data = {"task": task, **kwargs}
        return self._client.post(f"/api/swarms/{swarm_id}/execute", data=data)
    
    def delete(self, swarm_id: str) -> bool:
        """Delete a swarm."""
        self._client.delete(f"/api/swarms/{swarm_id}")
        return True
