from contextlib import contextmanager

from db_management.pool_manager import get_pool_manager
from db_management.pool_config import SQLitePoolConfig
from user_management.user_manager_db import UserManagerDB
from user_management.user_manager import UserManager
from user_management.role_management_db import RoleManagementDB
from user_management.resource_management_db import ResourceManagementDB
from web.abhikarta_llm_web import AbhikartaLLMWeb
from model_management.model_registry_db import ModelRegistryDB
from llm_provider.llm_facade_factory import LLMFacadeFactory

def run_webserver(pool_name, mcp_server_manager):
    from core.config.properties_configurator import PropertiesConfigurator

    prop_conf = PropertiesConfigurator()

    user_manager = UserManagerDB(db_connection_pool_name=pool_name)
    role_manager = RoleManagementDB(db_connection_pool_name=pool_name)
    resource_manager = ResourceManagementDB(db_connection_pool_name=pool_name)

    model_registry = ModelRegistryDB(pool_name)
    model_registry.start_auto_reload(interval_minutes=5)

    llm_facade_factory = LLMFacadeFactory(config_source="db", db_connection_pool_name=pool_name)

    aweb = AbhikartaLLMWeb("my very very secret key")


    aweb.set_model_registry(model_registry)
    aweb.set_llm_facade_factory(llm_facade_factory)

    aweb.set_user_manager(user_manager)
    aweb.set_role_manager(role_manager)
    aweb.set_resource_manager(resource_manager)
    aweb.set_db_connection_pool_name(pool_name)

    aweb.prepare_routes()

    port = prop_conf.get_int('server.port')
    aweb.run(port=port)

def prepare_database_pools():
    # Get pool manager singleton
    manager = get_pool_manager()

    pool_name = 'abhikarta-llm.db_management'

    # Create SQLite pool configuration
    config = SQLitePoolConfig(
        pool_name=pool_name,
        database_path='/home/ashutosh/PycharmProjects/abhikarta-llm/data/abhikarta-llm.db',

        # Pool settings
        min_connections=1,
        max_connections=5,
        max_idle_connections=2,
        connection_timeout=30.0,
        idle_timeout=300.0,

        # ⭐ Critical fixes
        timeout=30.0,  # 6x longer timeout
        busy_timeout=30000,  # 30 seconds in milliseconds
        enable_wal_mode=True,  # 🌟 KEY FIX - enables concurrency
        journal_mode="WAL",  # Write-Ahead Logging
        synchronous="NORMAL",  # Safe with WAL
        cache_size=-2000,  # 2MB cache
        isolation_level="DEFERRED",  # Better than None
        check_same_thread=False  # Required for pooling
    )

    # Create pool
    manager.create_pool(config)
    print(f"Created pool: {config.pool_name}")

    return pool_name,manager
def create_mcp_servers():
    import asyncio
    from tool_management.mcp_server_manager import MCPServerManager
    from tool_management.mcp_server_factory import build_mcp_server_proxy
    from core.config.properties_configurator import PropertiesConfigurator

    prop_conf = PropertiesConfigurator()
    mcp_server_manager = MCPServerManager()

    mcp_server_names = prop_conf.get_list('mcp.server.names', delim=',')
    for mcp_server_name in mcp_server_names:
        server_proxy = build_mcp_server_proxy(mcp_server_name)
        asyncio.run(server_proxy._refresh_tool_cache())
        mcp_server_manager.add_mcp_server(server_proxy)

    return mcp_server_manager

def set_llm_provider_facade_factory(pool_name: str):
    import llm_provider.register_llm_facades
    from llm_provider.llm_facade_factory import LLMFacadeFactory
    LLMFacadeFactory(config_source="db", db_connection_pool_name=pool_name)

def prepare_prop_conf():
    from core.config.properties_configurator import PropertiesConfigurator
    prop_files = [
        '/home/ashutosh/PycharmProjects/abhikarta-llm/config/mcp_server.properties',
        '/home/ashutosh/PycharmProjects/abhikarta-llm/config/llm.properties',
        '/home/ashutosh/PycharmProjects/abhikarta-llm/config/application.properties'
    ]
    prop_conf = PropertiesConfigurator(properties_files=prop_files)

    return prop_conf

if __name__ == '__main__':
    prepare_prop_conf()
    pool_name,pool_manager = prepare_database_pools()
    set_llm_provider_facade_factory(pool_name)

    mcp_server_manager = create_mcp_servers()
    mcp_server_manager.start_all()

    run_webserver(pool_name, mcp_server_manager)

    mcp_server_manager.stop_all()
    pool_manager.shutdown_all()

