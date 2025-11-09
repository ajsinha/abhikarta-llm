from db_management.pool_manager import get_pool_manager
from db_management.pool_config import SQLitePoolConfig
from user_management.user_manager_db import UserManagerDB
from user_management.user_manager import UserManager
from web.abhikarta_llm_web import AbhikartaLLMWeb

def main(user_manager_object: UserManager):
    aweb = AbhikartaLLMWeb(user_manager_object)
    aweb.run()


if __name__ == '__main__':


    pool_name = 'abhikarta-llm.db_management'

    # Get pool manager singleton
    manager = get_pool_manager()

    # Create SQLite pool configuration
    config = SQLitePoolConfig(
        pool_name=pool_name,
        database_path='/home/ashutosh/PycharmProjects/abhikarta-llm/data/abhikarta-llm.db',
        min_connections=2,
        max_connections=10,
        max_idle_connections=5,
        connection_timeout=30.0,
        idle_timeout=300.0
    )




    # Create pool
    manager.create_pool(config)
    print(f"Created pool: {config.pool_name}")

    user_manager_object = UserManagerDB(db_connection_pool_name=pool_name)
    main(user_manager_object)

    manager.shutdown_all()