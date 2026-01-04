"""
MCP Server - Model for MCP server configuration and state.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class MCPServerStatus(Enum):
    """Status of an MCP server."""
    UNKNOWN = "unknown"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    DISABLED = "disabled"


class MCPTransportType(Enum):
    """Transport protocol for MCP server communication."""
    HTTP = "http"
    HTTPS = "https"
    WEBSOCKET = "websocket"
    STDIO = "stdio"
    SSE = "sse"


class MCPAuthType(Enum):
    """Authentication type for MCP servers."""
    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC = "basic"
    OAUTH2 = "oauth2"
    CUSTOM = "custom"


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""
    # Identity
    server_id: str
    name: str
    description: str = ""
    
    # Connection
    url: str = ""
    transport: MCPTransportType = MCPTransportType.HTTP
    timeout_seconds: int = 30
    
    # Authentication
    auth_type: MCPAuthType = MCPAuthType.NONE
    auth_token: str = ""
    auth_header: str = "Authorization"
    auth_config: Dict[str, Any] = field(default_factory=dict)
    auth_endpoint: str = ""  # For basic auth - endpoint to call for login
    
    # Endpoints
    tools_endpoint: str = "/api/tools"
    call_endpoint: str = "/api/tools/call"
    health_endpoint: str = "/health"
    
    # Behavior
    auto_connect: bool = True
    retry_count: int = 3
    retry_delay_seconds: float = 1.0
    
    # Metadata
    version: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['transport'] = self.transport.value
        data['auth_type'] = self.auth_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPServerConfig':
        """Create from dictionary."""
        if 'transport' in data and isinstance(data['transport'], str):
            data['transport'] = MCPTransportType(data['transport'])
        if 'auth_type' in data and isinstance(data['auth_type'], str):
            data['auth_type'] = MCPAuthType(data['auth_type'])
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    @classmethod
    def from_db_record(cls, record: Dict[str, Any]) -> 'MCPServerConfig':
        """Create from database record."""
        import json
        
        auth_config = record.get('auth_config', '{}')
        if isinstance(auth_config, str):
            try:
                auth_config = json.loads(auth_config)
            except:
                auth_config = {}
        
        tags = record.get('tags', '[]')
        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except:
                tags = []
        
        metadata = record.get('metadata', '{}')
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        
        # Handle both 'url' and 'base_url' column names
        url = record.get('url') or record.get('base_url', '')
        
        # Get auth token from auth_config if not in separate column
        auth_token = record.get('auth_token', '')
        if not auth_token and auth_config:
            auth_token = auth_config.get('token') or auth_config.get('api_key', '')
        
        # Handle auto_connect as int or bool
        auto_connect = record.get('auto_connect', True)
        if isinstance(auto_connect, int):
            auto_connect = bool(auto_connect)
        
        # Handle is_active column (maps to auto_connect behavior)
        is_active = record.get('is_active', 1)
        if isinstance(is_active, int):
            is_active = bool(is_active)
        
        return cls(
            server_id=record.get('server_id'),
            name=record.get('name', ''),
            description=record.get('description', ''),
            url=url,
            transport=MCPTransportType(record.get('transport', 'http')),
            timeout_seconds=record.get('timeout_seconds', 30),
            auth_type=MCPAuthType(record.get('auth_type', 'none')),
            auth_token=auth_token,
            auth_header=record.get('auth_header', 'Authorization'),
            auth_config=auth_config,
            auth_endpoint=record.get('auth_endpoint', ''),
            tools_endpoint=record.get('tools_endpoint', '/api/tools'),
            call_endpoint=record.get('call_endpoint', '/api/tools/call'),
            health_endpoint=record.get('health_endpoint', '/health'),
            auto_connect=auto_connect and is_active,
            retry_count=record.get('retry_count', 3),
            retry_delay_seconds=record.get('retry_delay_seconds', 1.0),
            version=record.get('version', ''),
            tags=tags,
            metadata=metadata
        )


@dataclass
class MCPServerState:
    """Runtime state of an MCP server."""
    status: MCPServerStatus = MCPServerStatus.UNKNOWN
    last_connected: Optional[datetime] = None
    last_error: str = ""
    error_count: int = 0
    tool_count: int = 0
    tools_loaded: bool = False
    latency_ms: float = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'status': self.status.value,
            'last_connected': self.last_connected.isoformat() if self.last_connected else None,
            'last_error': self.last_error,
            'error_count': self.error_count,
            'tool_count': self.tool_count,
            'tools_loaded': self.tools_loaded,
            'latency_ms': self.latency_ms
        }


@dataclass
class MCPToolDefinition:
    """Definition of a tool from an MCP server."""
    name: str
    description: str = ""
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPToolDefinition':
        return cls(
            name=data.get('name', ''),
            description=data.get('description', ''),
            input_schema=data.get('inputSchema', data.get('input_schema', {})),
            output_schema=data.get('outputSchema', data.get('output_schema', {}))
        )


@dataclass
class MCPServer:
    """
    Complete MCP server representation.
    
    Combines configuration and runtime state.
    """
    config: MCPServerConfig
    state: MCPServerState = field(default_factory=MCPServerState)
    tools: List[MCPToolDefinition] = field(default_factory=list)
    
    @property
    def server_id(self) -> str:
        return self.config.server_id
    
    @property
    def name(self) -> str:
        return self.config.name
    
    @property
    def url(self) -> str:
        return self.config.url
    
    @property
    def is_connected(self) -> bool:
        return self.state.status == MCPServerStatus.CONNECTED
    
    @property
    def is_enabled(self) -> bool:
        return self.state.status != MCPServerStatus.DISABLED
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'config': self.config.to_dict(),
            'state': self.state.to_dict(),
            'tools': [t.to_dict() for t in self.tools]
        }
    
    @classmethod
    def from_config(cls, config: MCPServerConfig) -> 'MCPServer':
        """Create server from config only."""
        return cls(config=config)
