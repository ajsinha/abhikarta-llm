"""
MCP Client - Client for communicating with MCP servers.

Handles HTTP, WebSocket, and SSE connections.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import logging
import json
import time
import requests
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

from .server import (
    MCPServerConfig, MCPServerState, MCPServerStatus,
    MCPTransportType, MCPAuthType, MCPToolDefinition
)

logger = logging.getLogger(__name__)


class MCPClientBase(ABC):
    """Base class for MCP clients."""
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self._session = None
        self._auth_token = None  # Token obtained from auth endpoint
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to server."""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Close connection to server."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected."""
        pass
    
    @abstractmethod
    def list_tools(self) -> List[MCPToolDefinition]:
        """Get list of available tools."""
        pass
    
    @abstractmethod
    def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the server."""
        pass
    
    @abstractmethod
    def health_check(self) -> tuple[bool, float]:
        """Check server health. Returns (healthy, latency_ms)."""
        pass
    
    def _authenticate_basic(self) -> Optional[str]:
        """
        Authenticate using basic auth by calling the auth endpoint.
        
        Returns the token to use for subsequent requests.
        Expected response format:
        {
            'token': 'jwt-token-here',
            'user': {
                'user_id': '123',
                'user_name': 'admin',
                'roles': ['admin']
            }
        }
        Or just the raw token string if not JSON.
        """
        if not self.config.auth_endpoint:
            logger.warning("Basic auth configured but no auth_endpoint specified")
            return None
        
        try:
            auth_url = f"{self.config.url.rstrip('/')}{self.config.auth_endpoint}"
            auth_data = self.config.auth_config
            
            # Prepare credentials
            payload = {
                'username': auth_data.get('username', ''),
                'password': auth_data.get('password', '')
            }
            
            response = requests.post(
                auth_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.config.timeout_seconds
            )
            
            if response.status_code != 200:
                logger.error(f"Auth endpoint returned {response.status_code}")
                return None
            
            # Try to parse as JSON
            try:
                data = response.json()
                if isinstance(data, dict):
                    # Extract token from JSON response
                    token = data.get('token') or data.get('access_token')
                    if token:
                        logger.info(f"Successfully authenticated with {self.config.name}")
                        return token
                    else:
                        logger.error("Auth response missing 'token' field")
                        return None
                else:
                    # Response is just the token
                    return str(data)
            except json.JSONDecodeError:
                # Response is raw token string
                token = response.text.strip()
                if token:
                    logger.info(f"Successfully authenticated with {self.config.name} (raw token)")
                    return token
                return None
                
        except Exception as e:
            logger.error(f"Error authenticating with {self.config.name}: {e}")
            return None
    
    def _build_headers(self) -> Dict[str, str]:
        """Build request headers with authentication."""
        headers = {"Content-Type": "application/json"}
        
        if self.config.auth_type == MCPAuthType.BEARER_TOKEN:
            headers[self.config.auth_header] = f"Bearer {self.config.auth_token}"
        elif self.config.auth_type == MCPAuthType.API_KEY:
            header_name = self.config.auth_config.get('header', 'X-API-Key') if self.config.auth_config else 'X-API-Key'
            key = self.config.auth_config.get('key', self.config.auth_token) if self.config.auth_config else self.config.auth_token
            headers[header_name] = key
        elif self.config.auth_type == MCPAuthType.BASIC:
            # For basic auth, we use the token obtained from auth endpoint
            if self._auth_token:
                headers["Authorization"] = f"Bearer {self._auth_token}"
            elif self.config.auth_token:
                # Fallback to direct basic auth if no auth endpoint
                import base64
                credentials = self.config.auth_token
                encoded = base64.b64encode(credentials.encode()).decode()
                headers["Authorization"] = f"Basic {encoded}"
        
        return headers


class HTTPMCPClient(MCPClientBase):
    """HTTP-based MCP client."""
    
    def __init__(self, config: MCPServerConfig):
        super().__init__(config)
        self._connected = False
    
    def connect(self) -> bool:
        """
        Connect to MCP server.
        
        For basic auth with auth_endpoint:
        1. Call auth endpoint with credentials
        2. Extract token from response
        3. Use token as bearer token for subsequent calls
        """
        # If basic auth with endpoint, authenticate first
        if self.config.auth_type == MCPAuthType.BASIC and self.config.auth_endpoint:
            token = self._authenticate_basic()
            if not token:
                logger.error(f"Failed to authenticate with {self.config.name}")
                self._connected = False
                return False
            self._auth_token = token
            logger.info(f"Authenticated with {self.config.name}, token obtained")
        
        # Test connection by performing health check
        healthy, latency = self.health_check()
        self._connected = healthy
        return healthy
    
    def disconnect(self):
        """Close HTTP session."""
        if self._session:
            self._session.close()
            self._session = None
        self._connected = False
        self._auth_token = None
    
    def is_connected(self) -> bool:
        return self._connected
    
    def _get_session(self) -> requests.Session:
        """Get or create HTTP session."""
        if not self._session:
            self._session = requests.Session()
            self._session.headers.update(self._build_headers())
        return self._session
    
    def list_tools(self) -> List[MCPToolDefinition]:
        """Fetch tool list from server."""
        try:
            url = f"{self.config.url.rstrip('/')}{self.config.tools_endpoint}"
            
            response = self._get_session().get(
                url,
                timeout=self.config.timeout_seconds
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to list tools: HTTP {response.status_code}")
                return []
            
            data = response.json()
            tools_list = data.get('tools', data) if isinstance(data, dict) else data
            
            return [MCPToolDefinition.from_dict(t) for t in tools_list]
            
        except Exception as e:
            logger.error(f"Error listing tools from {self.config.name}: {e}")
            return []
    
    def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the server."""
        try:
            url = f"{self.config.url.rstrip('/')}{self.config.call_endpoint}"
            
            payload = {
                "tool": tool_name,
                "parameters": parameters
            }
            
            start_time = time.time()
            
            response = self._get_session().post(
                url,
                json=payload,
                timeout=self.config.timeout_seconds
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                result = response.json()
                result['execution_time_ms'] = execution_time
                return result
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'execution_time_ms': execution_time
                }
                
        except requests.Timeout:
            return {
                'success': False,
                'error': f"Request timed out after {self.config.timeout_seconds}s"
            }
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {'success': False, 'error': str(e)}
    
    def health_check(self) -> tuple[bool, float]:
        """Check server health. Uses authenticated session if configured."""
        try:
            url = f"{self.config.url.rstrip('/')}{self.config.health_endpoint}"
            
            start_time = time.time()
            # Use session to include authentication headers
            response = self._get_session().get(url, timeout=5)
            latency = (time.time() - start_time) * 1000
            
            return response.status_code == 200, latency
            
        except Exception as e:
            logger.debug(f"Health check failed for {self.config.name}: {e}")
            return False, 0


class WebSocketMCPClient(MCPClientBase):
    """WebSocket-based MCP client."""
    
    def __init__(self, config: MCPServerConfig):
        super().__init__(config)
        self._ws = None
        self._message_id = 0
        self._pending_responses: Dict[int, Any] = {}
    
    def connect(self) -> bool:
        """Establish WebSocket connection."""
        try:
            import websocket
            
            url = self.config.url.replace('http://', 'ws://').replace('https://', 'wss://')
            headers = self._build_headers()
            
            self._ws = websocket.create_connection(
                url,
                header=[f"{k}: {v}" for k, v in headers.items()],
                timeout=self.config.timeout_seconds
            )
            
            return True
            
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close WebSocket connection."""
        if self._ws:
            try:
                self._ws.close()
            except:
                pass
            self._ws = None
    
    def is_connected(self) -> bool:
        return self._ws is not None and self._ws.connected
    
    def list_tools(self) -> List[MCPToolDefinition]:
        """Request tool list via WebSocket."""
        if not self.is_connected():
            if not self.connect():
                return []
        
        try:
            self._message_id += 1
            msg_id = self._message_id
            
            request = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "method": "tools/list"
            }
            
            self._ws.send(json.dumps(request))
            response = json.loads(self._ws.recv())
            
            if 'result' in response:
                tools = response['result'].get('tools', [])
                return [MCPToolDefinition.from_dict(t) for t in tools]
            
            return []
            
        except Exception as e:
            logger.error(f"Error listing tools via WebSocket: {e}")
            return []
    
    def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool via WebSocket."""
        if not self.is_connected():
            if not self.connect():
                return {'success': False, 'error': 'Not connected'}
        
        try:
            self._message_id += 1
            msg_id = self._message_id
            
            request = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": parameters
                }
            }
            
            start_time = time.time()
            self._ws.send(json.dumps(request))
            response = json.loads(self._ws.recv())
            execution_time = (time.time() - start_time) * 1000
            
            if 'result' in response:
                return {
                    'success': True,
                    'result': response['result'],
                    'execution_time_ms': execution_time
                }
            elif 'error' in response:
                return {
                    'success': False,
                    'error': response['error'].get('message', 'Unknown error'),
                    'execution_time_ms': execution_time
                }
            
            return {'success': False, 'error': 'Invalid response'}
            
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {'success': False, 'error': str(e)}
    
    def health_check(self) -> tuple[bool, float]:
        """Check connection health."""
        if self.is_connected():
            return True, 0
        
        start_time = time.time()
        connected = self.connect()
        latency = (time.time() - start_time) * 1000
        
        return connected, latency


def create_mcp_client(config: MCPServerConfig) -> MCPClientBase:
    """
    Factory function to create appropriate MCP client.
    
    Args:
        config: Server configuration
        
    Returns:
        MCPClientBase implementation
    """
    if config.transport in (MCPTransportType.HTTP, MCPTransportType.HTTPS):
        return HTTPMCPClient(config)
    elif config.transport == MCPTransportType.WEBSOCKET:
        return WebSocketMCPClient(config)
    else:
        # Default to HTTP
        return HTTPMCPClient(config)
