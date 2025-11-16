from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
import logging
from tool_management.registry import ToolRegistry

logger = logging.getLogger(__name__)

@dataclass
class MCPToolSchema:
    """Schema information for an MCP tool"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Optional[Dict[str, Any]] = None
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        return {
            'name' : self.name,
            'description': self.description,
            'input_schema': self.input_schema,
            'ouput_schema': self.output_schema
        }



@dataclass
class MCPServerConfig:
    """Configuration for MCP server connection"""
    """Configuration for MCP server connection"""
    server_module: str = None
    base_url: str = None
    mcp_endpoint: str = None
    login_endpoint: str = None
    tool_list_endpoint: str = None
    tool_schema_endpoint_template: str = None
    username: Optional[str] = None
    password: Optional[str] = None
    refresh_interval_seconds: int = 600  # 10 minutes
    timeout_seconds: float = 30.0
    tool_name_suffix: str = None

class MCPServerProxy:
    def __init__(self, config: MCPServerConfig):
        self._config = config
        self._tool_cache: Dict[str, MCPToolSchema] = {}
        self._health_status = 'UNKNOWN'
        self._last_check_time = 'UNKNOWN'
        self.tool_registry = ToolRegistry()

    @abstractmethod
    async def _authenticate(self) -> bool:
        pass

    @abstractmethod
    async def _send_mcp_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def _ping_server(self) -> bool:
        pass

    @abstractmethod
    async def _list_tools(self) -> List[str]:
        pass

    @abstractmethod
    def _get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def _refresh_tool_cache(self):
        pass

    @abstractmethod
    def _periodic_refresh_loop(self):
        pass

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass

    @abstractmethod
    def get_tool_schema(self, tool_name: str) -> Optional[MCPToolSchema]:
        pass

    @abstractmethod
    def list_cached_tools(self) -> List[str]:
        pass

    @abstractmethod
    def get_all_schemas(self) -> Dict[str, MCPToolSchema]:
        pass

    @abstractmethod
    def get_cache_stats(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def force_refresh(self):
        pass

    def base_url(self):
        return self._config.base_url

    def mcp_endpoint(self):
        return self._config.mcp_endpoint

    def server_config_dict(self):
        config_dict = asdict(self._config)
        if 'password' in config_dict.keys():
            config_dict.pop('password')
        return config_dict

    def short_name(self):
        name = self._config.tool_name_suffix
        if name is None:
            name = self._config.base_url
        return name

    def health_status(self):
        return self._health_status

    def set_health_status(self, status):
        self._health_status = status

    def last_check_time(self):
        return self._last_check_time

    def set_last_check_time(self):
        from datetime import datetime

        # Get the current datetime object
        now = datetime.now()

        # Format the datetime object into the desired string format
        formatted_time = now.strftime("%Y:%m:%d %H:%M:%S")

        self._last_check_time = formatted_time

    def mcp_endpoint_url(self):
        url = f"{self._config.base_url}{self._config.mcp_endpoint}"
        return url

    def tool_cache_key(self, tool_name):
        cache_key = f'{tool_name}:{self._config.tool_name_suffix}'
        return cache_key

    def tool_name_from_cache_key(self, cache_key):
        """
            Extract tool name from '<tool_name>:<key>' using the key string.

            Args:
                cache_key: Full string like "yahoo_finance:abhikarta"

            Returns:
                Tool name like "yahoo_finance"

            Raises:
                ValueError: If key not found at the end or format invalid
            """
        key = self._config.tool_name_suffix
        if not key:
            raise ValueError("Key cannot be empty")

        key_len = len(key)
        expected_suffix = f":{key}"

        if not cache_key.endswith(expected_suffix):
            return cache_key

        # Remove ':key' from the end
        tool_name = cache_key[:-key_len - 1]
        return tool_name

class DoNothingMMCPServerProxy(MCPServerProxy):

    _instance = None


    def __new__(cls, config: MCPServerConfig):
        """Singleton pattern implementation"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance


    def __init__(self, config: MCPServerConfig):
        """Initialize the builder (only once)"""
        super().__init__(config)
        if self._initialized:
            return

        self._initialized = True


        logger.info("DoNothingMMCPServerProxy initialized")

    def _authenticate(self) -> bool:
        pass

    def _send_mcp_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def _ping_server(self) -> bool:
        pass

    def _list_tools(self) -> List[str]:
        pass

    def _get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        pass

    def _refresh_tool_cache(self):
        pass

    def _periodic_refresh_loop(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def get_tool_schema(self, tool_name: str) -> Optional[MCPToolSchema]:
        pass

    def list_cached_tools(self) -> List[str]:
        pass

    def get_all_schemas(self) -> Dict[str, MCPToolSchema]:
        pass

    def get_cache_stats(self) -> Dict[str, Any]:
        pass

    def force_refresh(self):
        pass
