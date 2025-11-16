"""
Configuration Switcher - Runtime switching between JSON and Database config

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import register_facades
from facade_factory import FacadeFactory


class ConfigSwitcher:
    """
    Utility to switch between JSON and Database configuration at runtime.
    
    Usage:
        switcher = ConfigSwitcher()
        
        # Use JSON config
        factory = switcher.get_factory("json")
        
        # Switch to DB config
        factory = switcher.get_factory("db")
    """
    
    def __init__(self, json_path: str = "./config", db_connection: str = None):
        """
        Initialize configuration switcher.
        
        Args:
            json_path: Path to JSON configuration files
            db_connection: Database connection string (optional)
        """
        self.json_path = json_path
        self.db_connection = db_connection
        self.current_mode = None
    
    def get_factory(self, mode: str = "json") -> FacadeFactory:
        """
        Get FacadeFactory with specified configuration mode.
        
        Args:
            mode: Either "json" or "db"
        
        Returns:
            Configured FacadeFactory instance
        
        Example:
            factory = switcher.get_factory("json")
            facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
        """
        if mode not in ["json", "db"]:
            raise ValueError(f"Invalid mode: {mode}. Use 'json' or 'db'")
        
        self.current_mode = mode
        
        if mode == "json":
            return self._get_json_factory()
        else:
            return self._get_db_factory()
    
    def _get_json_factory(self) -> FacadeFactory:
        """Get factory configured for JSON."""
        print(f"📁 Using JSON configuration from: {self.json_path}")
        
        return FacadeFactory(
            config_source="json",
            config_path=self.json_path
        )
    
    def _get_db_factory(self) -> FacadeFactory:
        """Get factory configured for Database."""
        if not self.db_connection:
            print("⚠️  No database connection configured, falling back to JSON")
            return self._get_json_factory()
        
        print(f"🗄️  Using Database configuration")
        
        # Import database handler (implement based on your DB setup)
        from db_handler import DatabaseHandler
        
        db_handler = DatabaseHandler(self.db_connection)
        
        return FacadeFactory(
            config_source="db",
            db_handler=db_handler
        )
    
    def switch_mode(self, mode: str) -> FacadeFactory:
        """
        Switch configuration mode and return new factory.
        
        Args:
            mode: Either "json" or "db"
        
        Returns:
            New FacadeFactory instance with switched configuration
        """
        print(f"🔄 Switching from {self.current_mode} to {mode}")
        return self.get_factory(mode)


def demonstrate_switching():
    """Demonstrate runtime configuration switching."""
    print("="*60)
    print("Configuration Switching Demonstration")
    print("="*60)
    
    switcher = ConfigSwitcher(json_path="../config")
    
    # Start with JSON
    print("\n1️⃣  Creating factory with JSON configuration...")
    factory_json = switcher.get_factory("json")
    
    try:
        facade = factory_json.create_facade("mock", "mock-advanced")
        response = facade.chat_completion(
            [{"role": "user", "content": "Test with JSON config"}],
            max_tokens=50
        )
        print(f"✓ JSON Config Response: {response['content'][:50]}...")
    except Exception as e:
        print(f"✗ Error with JSON: {e}")
    
    # Switch to DB (will fall back to JSON if no DB configured)
    print("\n2️⃣  Switching to Database configuration...")
    factory_db = switcher.switch_mode("db")
    
    try:
        facade = factory_db.create_facade("mock", "mock-advanced")
        response = facade.chat_completion(
            [{"role": "user", "content": "Test with DB config"}],
            max_tokens=50
        )
        print(f"✓ DB Config Response: {response['content'][:50]}...")
    except Exception as e:
        print(f"✗ Error with DB: {e}")
    
    # Switch back to JSON
    print("\n3️⃣  Switching back to JSON configuration...")
    factory_json = switcher.switch_mode("json")
    
    print("\n✅ Configuration switching demonstrated!")


if __name__ == "__main__":
    demonstrate_switching()
