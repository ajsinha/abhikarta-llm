from db_management.pool_manager import get_pool_manager
from db_management.pool_config import SQLitePoolConfig


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

    # Create a test table
    with manager.get_connection_context(pool_name) as conn:
        cursor = conn.cursor()
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()
        print("Created users table")

    manager.shutdown_all()