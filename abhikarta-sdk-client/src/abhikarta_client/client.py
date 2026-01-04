"""
Abhikarta SDK Client - Main client class for connecting to Abhikarta-LLM server.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass
class ClientConfig:
    """Configuration for Abhikarta API client.
    
    Attributes:
        base_url: Base URL of the Abhikarta server
        api_key: Optional API key for authentication
        timeout: Request timeout in seconds
        verify_ssl: Whether to verify SSL certificates
    """
    base_url: str = "http://localhost:5000"
    api_key: Optional[str] = None
    timeout: int = 300
    verify_ssl: bool = True


class AbhikartaClient:
    """Client for connecting to Abhikarta-LLM server.
    
    This client provides a Pythonic interface to interact with all
    Abhikarta-LLM features including agents, workflows, swarms, and
    AI organizations.
    
    Example:
        >>> from abhikarta_client import AbhikartaClient
        >>> 
        >>> # Basic connection
        >>> client = AbhikartaClient("http://localhost:5000")
        >>> 
        >>> # With API key
        >>> client = AbhikartaClient(
        ...     "http://localhost:5000",
        ...     api_key="your-api-key"
        ... )
        >>> 
        >>> # List all agents
        >>> agents = client.agents.list()
        >>> for agent in agents:
        ...     print(f"{agent['name']}: {agent['agent_type']}")
        >>> 
        >>> # Execute an agent
        >>> result = client.agents.execute(
        ...     agent_id="agent-123",
        ...     prompt="Research AI trends"
        ... )
        >>> print(result['response'])
        >>> 
        >>> # Create a new agent
        >>> new_agent = client.agents.create(
        ...     name="My Research Agent",
        ...     agent_type="react",
        ...     model="llama3.2:3b",
        ...     system_prompt="You are a helpful research assistant."
        ... )
    
    The client uses context manager protocol for proper resource cleanup:
        >>> with AbhikartaClient("http://localhost:5000") as client:
        ...     agents = client.agents.list()
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:5000",
        api_key: Optional[str] = None,
        config: Optional[ClientConfig] = None
    ):
        """Initialize the client.
        
        Args:
            base_url: Server URL (ignored if config is provided)
            api_key: API key for authentication (ignored if config is provided)
            config: Full configuration object (takes precedence)
        """
        if config:
            self.config = config
        else:
            self.config = ClientConfig(base_url=base_url, api_key=api_key)
        
        self._http_client = httpx.Client(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            verify=self.config.verify_ssl
        )
        
        # Initialize sub-clients (lazy import to avoid circular deps)
        from .agents import AgentsClient
        from .workflows import WorkflowsClient
        from .swarms import SwarmsClient
        from .organizations import OrganizationsClient
        from .scripts import ScriptsClient
        
        self.agents = AgentsClient(self)
        self.workflows = WorkflowsClient(self)
        self.swarms = SwarmsClient(self)
        self.organizations = OrganizationsClient(self)
        self.scripts = ScriptsClient(self)
        
        logger.info(f"AbhikartaClient connected to {self.config.base_url}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers including authentication."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make an API request.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            httpx.HTTPStatusError: On HTTP error responses
            httpx.RequestError: On connection errors
        """
        response = self._http_client.request(
            method=method,
            url=endpoint,
            json=data,
            params=params,
            headers=self._get_headers()
        )
        response.raise_for_status()
        
        # Handle empty responses
        if response.status_code == 204:
            return {}
        
        return response.json()
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GET request."""
        return self._request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a POST request."""
        return self._request("POST", endpoint, data=data)
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a PUT request."""
        return self._request("PUT", endpoint, data=data)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request."""
        return self._request("DELETE", endpoint)
    
    def health_check(self) -> bool:
        """Check if the server is healthy.
        
        Returns:
            True if server is responding, False otherwise
        """
        try:
            self.get("/api/health")
            return True
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information and version.
        
        Returns:
            Server info including version, features, etc.
        """
        return self.get("/api/info")
    
    def close(self):
        """Close the HTTP client connection."""
        self._http_client.close()
        logger.debug("AbhikartaClient connection closed")
    
    def __enter__(self) -> "AbhikartaClient":
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.close()


class AsyncAbhikartaClient:
    """Async client for connecting to Abhikarta-LLM server.
    
    Use this client for async/await patterns in your application.
    
    Example:
        >>> import asyncio
        >>> from abhikarta_client import AsyncAbhikartaClient
        >>> 
        >>> async def main():
        ...     async with AsyncAbhikartaClient("http://localhost:5000") as client:
        ...         agents = await client.agents.list()
        ...         print(agents)
        >>> 
        >>> asyncio.run(main())
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:5000",
        api_key: Optional[str] = None,
        config: Optional[ClientConfig] = None
    ):
        """Initialize async client."""
        if config:
            self.config = config
        else:
            self.config = ClientConfig(base_url=base_url, api_key=api_key)
        
        self._http_client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            verify=self.config.verify_ssl
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make an async API request."""
        response = await self._http_client.request(
            method=method,
            url=endpoint,
            json=data,
            params=params,
            headers=self._get_headers()
        )
        response.raise_for_status()
        
        if response.status_code == 204:
            return {}
        
        return response.json()
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make async GET request."""
        return await self._request("GET", endpoint, params=params)
    
    async def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make async POST request."""
        return await self._request("POST", endpoint, data=data)
    
    async def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make async PUT request."""
        return await self._request("PUT", endpoint, data=data)
    
    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make async DELETE request."""
        return await self._request("DELETE", endpoint)
    
    async def health_check(self) -> bool:
        """Check server health asynchronously."""
        try:
            await self.get("/api/health")
            return True
        except Exception:
            return False
    
    async def close(self):
        """Close the async HTTP client."""
        await self._http_client.aclose()
    
    async def __aenter__(self) -> "AsyncAbhikartaClient":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
