import threading
from tool_management.mcp_server_proxy import MCPServerProxy
from typing import Dict
from core import SingletonMeta

class MCPServerManager(metaclass=SingletonMeta):

    def __init__(self):
        """Initialize the builder (only once)"""
        self._lock = threading.RLock()
        self._registered_servers: Dict[str, MCPServerProxy] = {}

    def mcp_server_by_name(self, name):
        with self._lock:
            return self._registered_servers[name]
    def mcp_tool_list(self, name):
        mcp_server_proxy = self.mcp_server_by_name(name)
        if mcp_server_proxy is None:
            return []
        else:
            return mcp_server_proxy.list_cached_tools()
    def add_mcp_server(self, server_proxy: MCPServerProxy):
        with self._lock:
            self._registered_servers[server_proxy.short_name()] = server_proxy

    def status_all(self):
        status_dict = {}
        for x in self._registered_servers.keys():
            name = self._registered_servers[x].short_name()
            status = self._registered_servers[x].health_status()
            last_check_time = self._registered_servers[x].last_check_time()

            status_dict[name] = {'name': name, 'status': status, 'last_check_time':last_check_time}
        return status_dict

    def start_all(self):
        import asyncio
        for x in self._registered_servers.keys():
            server_proxy = self._registered_servers[x]
            asyncio.run(server_proxy.start())


    def stop_all(self):
        import asyncio
        for x in self._registered_servers.keys():
            server_proxy = self._registered_servers[x]
            asyncio.run(server_proxy.stop())

    def get_tools_for_server_proxy(self, server_proxy_name: str):
        server_proxy = self._registered_servers[server_proxy_name]
        return server_proxy.get_all_schemas()
