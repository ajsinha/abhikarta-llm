"""
Abhikarta SDK Client - Workflows API

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import AbhikartaClient


class RemoteWorkflow:
    """Represents a remote workflow on the Abhikarta server."""
    
    def __init__(self, client: "AbhikartaClient", data: Dict[str, Any]):
        self._client = client
        self._data = data
        self.id = data.get("id") or data.get("workflow_id")
        self.name = data.get("name")
        self.description = data.get("description", "")
        self.nodes = data.get("nodes", [])
        self.edges = data.get("edges", [])
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow with input data."""
        return self._client.post(f"/api/workflows/{self.id}/execute", data=input_data)
    
    def update(self, **kwargs) -> "RemoteWorkflow":
        """Update workflow configuration."""
        result = self._client.put(f"/api/workflows/{self.id}", data=kwargs)
        self._data.update(result)
        return self
    
    def delete(self) -> bool:
        """Delete this workflow."""
        self._client.delete(f"/api/workflows/{self.id}")
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Get workflow data as dictionary."""
        return self._data
    
    def __repr__(self) -> str:
        return f"RemoteWorkflow(id={self.id}, name={self.name})"


class WorkflowsClient:
    """Client for workflow operations."""
    
    def __init__(self, client: "AbhikartaClient"):
        self._client = client
    
    def list(self) -> List[Dict[str, Any]]:
        """List all workflows."""
        return self._client.get("/api/workflows")
    
    def get(self, workflow_id: str) -> RemoteWorkflow:
        """Get a workflow by ID."""
        data = self._client.get(f"/api/workflows/{workflow_id}")
        return RemoteWorkflow(self._client, data)
    
    def create(
        self,
        name: str,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        description: str = "",
        **kwargs
    ) -> RemoteWorkflow:
        """Create a new workflow."""
        data = {
            "name": name,
            "nodes": nodes,
            "edges": edges,
            "description": description,
            **kwargs
        }
        result = self._client.post("/api/workflows", data=data)
        return RemoteWorkflow(self._client, result)
    
    def execute(self, workflow_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow directly by ID."""
        return self._client.post(f"/api/workflows/{workflow_id}/execute", data=input_data)
    
    def delete(self, workflow_id: str) -> bool:
        """Delete a workflow."""
        self._client.delete(f"/api/workflows/{workflow_id}")
        return True
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List available workflow templates."""
        return self._client.get("/api/workflows/templates")
