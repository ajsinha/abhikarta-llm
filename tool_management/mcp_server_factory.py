from tool_management.mcp_server_proxy import MCPServerConfig
from core.config.properties_configurator import PropertiesConfigurator
from importlib import import_module

def instantiate_from_path(path: str, **kwargs):
    """Instantiate a class from 'module.path.ClassName' with kwargs."""
    module_path, _, class_name = path.rpartition('.')
    module = import_module(module_path)
    cls = getattr(module, class_name)
    return cls(**kwargs)

def build_config_using_key(key: str):

    prop_conf = PropertiesConfigurator()
    do_nothing_server_module = 'tool_management.mcp_server_proxy.DoNothingMMCPServerProxy'
    #
    server_module = prop_conf.get(f'mcp.server.{key}.config.server_module', do_nothing_server_module)
    base_url = prop_conf.get(f'mcp.server.{key}.config.base_url')
    mcp_endpoint = prop_conf.get(f'mcp.server.{key}.config.mcp_endpoint')
    login_endpoint = prop_conf.get(f'mcp.server.{key}.config.login_endpoint')
    tool_list_endpoint = prop_conf.get(f'mcp.server.{key}.config.tool_list_endpoint')
    tool_schema_endpoint_template = prop_conf.get(f'mcp.server.{key}.config.tool_schema_endpoint_template')
    username = prop_conf.get(f'mcp.server.{key}.config.username')
    password = prop_conf.get(f'mcp.server.{key}.config.password')
    refresh_interval_seconds = prop_conf.get_int(f'mcp.server.{key}.config.refresh_interval_seconds', 600)
    timeout_seconds = prop_conf.get_int(f'mcp.server.{key}.config.timeout_seconds', 30)
    tool_name_suffix = prop_conf.get(f'mcp.server.{key}.config.tool_name_suffix')
    #
    config = MCPServerConfig()
    config.base_url = base_url
    config.mcp_endpoint = mcp_endpoint
    config.login_endpoint = login_endpoint
    config.tool_list_endpoint = tool_list_endpoint
    config.tool_schema_endpoint_template = tool_schema_endpoint_template
    config.username = username
    config.password = password
    config.refresh_interval_seconds = refresh_interval_seconds
    config.timeout_seconds = timeout_seconds
    config.tool_name_suffix = tool_name_suffix
    #
    return server_module, config

def build_mcp_server_proxy(server_key: str):
    server_module, config = build_config_using_key(server_key)

    proxy = instantiate_from_path(server_module, config=config)

    return proxy