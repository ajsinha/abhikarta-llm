"""
Abhikarta SDK Client - Organizations API

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import AbhikartaClient


class RemoteOrganization:
    """Represents a remote AI organization on the Abhikarta server."""
    
    def __init__(self, client: "AbhikartaClient", data: Dict[str, Any]):
        self._client = client
        self._data = data
        self.id = data.get("id") or data.get("org_id")
        self.name = data.get("name")
        self.nodes = data.get("nodes", [])
        self.root_node_id = data.get("root_node_id")
    
    def submit_task(self, title: str, description: str, **kwargs) -> Dict[str, Any]:
        """Submit a task to the organization."""
        data = {"title": title, "description": description, **kwargs}
        return self._client.post(f"/api/aiorgs/{self.id}/tasks", data=data)
    
    def get_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks for this organization."""
        return self._client.get(f"/api/aiorgs/{self.id}/tasks")
    
    def delete(self) -> bool:
        """Delete this organization."""
        self._client.delete(f"/api/aiorgs/{self.id}")
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return self._data
    
    def __repr__(self) -> str:
        return f"RemoteOrganization(id={self.id}, name={self.name})"


class OrganizationsClient:
    """Client for AI organization operations."""
    
    def __init__(self, client: "AbhikartaClient"):
        self._client = client
    
    def list(self) -> List[Dict[str, Any]]:
        """List all organizations."""
        return self._client.get("/api/aiorgs")
    
    def get(self, org_id: str) -> RemoteOrganization:
        """Get an organization by ID."""
        data = self._client.get(f"/api/aiorgs/{org_id}")
        return RemoteOrganization(self._client, data)
    
    def create(
        self,
        name: str,
        nodes: List[Dict[str, Any]],
        root_node_id: Optional[str] = None,
        **kwargs
    ) -> RemoteOrganization:
        """Create a new organization."""
        data = {"name": name, "nodes": nodes, **kwargs}
        if root_node_id:
            data["root_node_id"] = root_node_id
        result = self._client.post("/api/aiorgs", data=data)
        return RemoteOrganization(self._client, result)
    
    def delete(self, org_id: str) -> bool:
        """Delete an organization."""
        self._client.delete(f"/api/aiorgs/{org_id}")
        return True
