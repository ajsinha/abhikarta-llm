"""
Abhikarta-LLM Test Suite

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestConfig:
    """Test configuration module."""
    
    def test_settings_load(self):
        """Test settings can be loaded."""
        from abhikarta.config import Settings
        settings = Settings.load()
        assert settings.app_name == "Abhikarta-LLM"
        assert settings.app_version == "1.0.0"


class TestUserFacade:
    """Test user management facade."""
    
    def test_user_facade_init(self):
        """Test user facade initialization."""
        from abhikarta.user_management import UserFacade
        facade = UserFacade('./data/users.json')
        assert facade is not None
    
    def test_authenticate_valid_user(self):
        """Test authentication with valid credentials."""
        from abhikarta.user_management import UserFacade
        facade = UserFacade('./data/users.json')
        user = facade.authenticate('admin', 'admin123')
        assert user is not None
        assert user['user_id'] == 'admin'
    
    def test_authenticate_invalid_user(self):
        """Test authentication with invalid credentials."""
        from abhikarta.user_management import UserFacade
        facade = UserFacade('./data/users.json')
        user = facade.authenticate('admin', 'wrongpassword')
        assert user is None
    
    def test_list_users(self):
        """Test listing users."""
        from abhikarta.user_management import UserFacade
        facade = UserFacade('./data/users.json')
        users = facade.list_users()
        assert len(users) > 0


class TestDatabaseFacade:
    """Test database facade."""
    
    def test_sqlite_handler(self):
        """Test SQLite handler initialization."""
        from abhikarta.database.sqlite_handler import SQLiteHandler
        handler = SQLiteHandler(':memory:')
        handler.connect()
        handler.init_schema()
        
        # Test query
        result = handler.fetch_all("SELECT * FROM roles")
        assert len(result) > 0
        
        handler.disconnect()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
