"""
Abhikarta SDK Client - Scripts API

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import AbhikartaClient


class ScriptsClient:
    """Client for Python Script Mode operations."""
    
    def __init__(self, client: "AbhikartaClient"):
        self._client = client
    
    def list(self, entity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all scripts."""
        params = {}
        if entity_type:
            params["entity_type"] = entity_type
        return self._client.get("/api/scripts", params=params)
    
    def get(self, script_id: str) -> Dict[str, Any]:
        """Get a script by ID."""
        return self._client.get(f"/api/scripts/{script_id}")
    
    def create(
        self,
        name: str,
        entity_type: str,
        script_content: str,
        description: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new script."""
        data = {
            "name": name,
            "entity_type": entity_type,
            "script_content": script_content,
            "description": description,
            **kwargs
        }
        return self._client.post("/api/scripts", data=data)
    
    def execute(self, script_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a script."""
        return self._client.post(f"/api/scripts/{script_id}/execute", data=input_data)
    
    def validate(self, script_id: str) -> Dict[str, Any]:
        """Validate a script."""
        return self._client.post(f"/api/scripts/{script_id}/validate")
    
    def delete(self, script_id: str) -> bool:
        """Delete a script."""
        self._client.delete(f"/api/scripts/{script_id}")
        return True
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List available script templates."""
        return self._client.get("/api/scripts/templates")
