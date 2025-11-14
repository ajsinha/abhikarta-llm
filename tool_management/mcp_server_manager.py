import threading
from tool_management.mcp_server_proxy import MCPServerProxy
from typing import Dict
from core import SingletonMeta

class MCPServerManager(metaclass=SingletonMeta):

    def __init__(self):
        """Initialize the builder (only once)"""
        self._lock = threading.RLock()
        self._registered_servers: Dict[str, MCPServerProxy] = {}


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
        for x in self._registered_servers.keys():
            server_proxy = self._registered_servers[x]
            server_proxy.start()

    def stop_all(self):
        for x in self._registered_servers.keys():
            server_proxy = self._registered_servers[x]
            server_proxy.stop()
