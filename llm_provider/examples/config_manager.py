"""
Configuration Manager - Runtime JSON/Database Switching

This module allows switching between JSON and Database configuration
sources at runtime via environment variable or command-line argument.

Usage:
    # Via environment variable
    export CONFIG_SOURCE=json  # or 'db'
    python example_anthropic.py
    
    # Via command-line argument
    python example_anthropic.py --config-source json
    python example_anthropic.py --config-source db
"""

import os
import sys
from typing import Optional
from facade_factory import FacadeFactory


class ConfigManager:
    """Manages configuration source selection at runtime."""
    
    @staticmethod
    def get_factory(
        config_source: Optional[str] = None,
        config_path: Optional[str] = None,
        db_handler: Optional[any] = None
    ) -> FacadeFactory:
        """
        Create FacadeFactory with specified or default configuration.
        
        Priority:
        1. Explicit config_source parameter
        2. --config-source command-line argument
        3. CONFIG_SOURCE environment variable
        4. Default to 'json'
        
        Args:
            config_source: 'json' or 'db'
            config_path: Path to JSON config files (for JSON mode)
            db_handler: Database handler (for DB mode)
        
        Returns:
            FacadeFactory instance
        """
        # Determine config source
        source = config_source
        
        if not source:
            # Check command-line arguments
            if '--config-source' in sys.argv:
                idx = sys.argv.index('--config-source')
                if idx + 1 < len(sys.argv):
                    source = sys.argv[idx + 1]
        
        if not source:
            # Check environment variable
            source = os.getenv('CONFIG_SOURCE', 'json')
        
        # Validate source
        if source not in ['json', 'db']:
            raise ValueError(f"Invalid config source: {source}. Must be 'json' or 'db'")
        
        print(f"✓ Using configuration source: {source.upper()}")
        
        # Create factory
        if source == 'json':
            path = config_path or os.getenv('CONFIG_PATH', './config')
            print(f"✓ Config path: {path}")
            return FacadeFactory(config_source='json', config_path=path)
        else:  # db
            if not db_handler:
                # Try to import and create default DB handler
                try:
                    from db_handler import DatabaseHandler
                    connection_string = os.getenv(
                        'DATABASE_URL',
                        'sqlite:///abhikarta_models.db'
                    )
                    db_handler = DatabaseHandler(connection_string)
                    print(f"✓ Database: {connection_string}")
                except ImportError:
                    raise ImportError(
                        "Database handler not available. "
                        "Please provide db_handler parameter or use JSON mode."
                    )
            
            return FacadeFactory(config_source='db', db_handler=db_handler)
    
    @staticmethod
    def print_usage():
        """Print usage instructions."""
        print("""
Configuration Source Selection:

1. Via environment variable:
   export CONFIG_SOURCE=json
   python example_script.py

2. Via command-line:
   python example_script.py --config-source json
   python example_script.py --config-source db

3. Programmatically:
   factory = ConfigManager.get_factory(config_source='json')

Default: JSON configuration from ./config directory
        """)


def get_factory(**kwargs) -> FacadeFactory:
    """Convenience function to get factory."""
    return ConfigManager.get_factory(**kwargs)


if __name__ == "__main__":
    ConfigManager.print_usage()
