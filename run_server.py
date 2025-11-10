from contextlib import contextmanager

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

    '''
    @contextmanager
    def _get_connection():
        """Context manager for database connections with auto-commit."""
        with manager.get_connection_context(pool_name) as conn:
            try:
                yield conn  # Now this yields the actual connection
                conn.commit()  # Auto-commit on success
            except Exception as e:
                conn.rollback()  # Auto-rollback on error
                print(f"Database error: {e}")
                raise

    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()  # Fetch all results
        print("\nFetched data:")
        for row in rows:
            print(row)
    '''
    user_manager_object = UserManagerDB(db_connection_pool_name=pool_name)
    main(user_manager_object)

    manager.shutdown_all()