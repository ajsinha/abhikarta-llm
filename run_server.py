from contextlib import contextmanager

from db_management.pool_manager import get_pool_manager
from db_management.pool_config import SQLitePoolConfig
from user_management.user_manager_db import UserManagerDB
from user_management.user_manager import UserManager
from user_management.role_management_db import RoleManagementDB
from user_management.resource_management_db import ResourceManagementDB
from web.abhikarta_llm_web import AbhikartaLLMWeb

def main(pool_name):
    user_manager = UserManagerDB(db_connection_pool_name=pool_name)
    role_manager = RoleManagementDB(db_connection_pool_name=pool_name)
    resource_manager = ResourceManagementDB(db_connection_pool_name=pool_name)

    aweb = AbhikartaLLMWeb()


    aweb.set_user_manager(user_manager)
    aweb.set_role_manager(role_manager)
    aweb.set_resource_manager(resource_manager)
    aweb.set_db_connection_pool_name(pool_name)

    aweb.prepare_routes()

    aweb.run()


if __name__ == '__main__':


    pool_name = 'abhikarta-llm.db_management'

    # Get pool manager singleton
    manager = get_pool_manager()

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



    main(pool_name)

    manager.shutdown_all()