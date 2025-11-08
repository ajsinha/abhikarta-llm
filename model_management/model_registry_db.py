"""
Abhikarta LLM Model Registry - Database Implementation

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This document and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use of this document or the software
system it describes is strictly prohibited without explicit written permission from the
copyright holder.

This document is provided "as is" without warranty of any kind, either expressed or implied.
The copyright holder shall not be liable for any damages arising from the use of this
document or the software system it describes.

Patent Pending: Certain architectural patterns and implementations described in this
document may be subject to patent applications.
"""

import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from model_registry import ModelRegistry
from model_provider_db import ModelProviderDB
from model_management_db_handler import ModelManagementDBHandler
from exceptions import ConfigurationError


class ModelRegistryDB(ModelRegistry):
    """
    Database-backed implementation of ModelRegistry.

    This singleton class:
    - Manages ModelProviderDB instances loaded from database
    - Provides convenience methods for accessing models across providers
    - Handles provider and model enable/disable states
    - Can load JSON configurations into database
    - Maintains cached provider instances for performance

    Thread Safety:
        All methods are thread-safe using RLock for reentrant locking.
        Safe for concurrent access from multiple threads.

    Usage:
        >>> registry = ModelRegistryDB.get_instance(db_path="/path/to/db.sqlite")
        >>>
        >>> # Load JSON files into database (one-time operation)
        >>> registry.load_json_directory("/path/to/configs")
        >>>
        >>> # Get all providers
        >>> providers = registry.get_all_providers()
        >>>
        >>> # Get specific model
        >>> model = registry.get_model_from_provider_by_name("anthropic", "claude-opus-4")
        >>>
        >>> # Find cheapest model for capability
        >>> provider, model, cost = registry.get_cheapest_model_for_capability("vision")
    """

    _instance: Optional['ModelRegistryDB'] = None
    _instance_lock = threading.RLock()

    def __init__(self, db_path: str):
        """
        Initialize the ModelRegistryDB with database backend.

        Note: Use get_instance() instead of direct initialization to ensure singleton.

        Args:
            db_path: Path to SQLite database file

        Raises:
            ConfigurationError: If there are errors initializing database
        """
        super().__init__()

        # Initialize database handler
        try:
            self._db_handler = ModelManagementDBHandler.get_instance(db_path)
            self._db_handler.initialize_schema()
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize database: {e}")

        # Initial load
        self._load_all_providers()

    @classmethod
    def get_instance(cls, db_path: str = None) -> 'ModelRegistryDB':
        """
        Get the singleton instance of ModelRegistryDB.

        Args:
            db_path: Path to SQLite database (required on first call)

        Returns:
            The singleton ModelRegistryDB instance

        Raises:
            ValueError: If db_path is None on first call

        Example:
            >>> # First initialization
            >>> registry = ModelRegistryDB.get_instance(db_path="/path/to/db.sqlite")
            >>>
            >>> # Subsequent calls
            >>> registry = ModelRegistryDB.get_instance()  # Uses existing instance
        """
        with cls._instance_lock:
            if cls._instance is None:
                if db_path is None:
                    raise ValueError("db_path must be provided on first call to get_instance()")
                cls._instance = cls(db_path)
            return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance (mainly for testing).

        This will clear the instance and database handler.
        """
        with cls._instance_lock:
            if cls._instance is not None:
                ModelManagementDBHandler.reset_instance()
                cls._instance = None

    def _load_all_providers(self) -> None:
        """
        Load all provider configurations from database.

        This method loads all providers into memory cache for fast access.
        """
        with self._lock:
            self._providers.clear()

            provider_data_list = self._db_handler.get_all_providers(include_disabled=True)

            for provider_data in provider_data_list:
                try:
                    provider_name = provider_data['provider']
                    self._providers[provider_name] = ModelProviderDB(provider_name, self._db_handler)
                except Exception as e:
                    print(f"Warning: Failed to load provider {provider_data.get('provider')}: {e}")

    def reload_from_storage(self) -> None:
        """
        Reload all providers from database.

        This is useful when data has been updated in the database by another process.

        Example:
            >>> registry.reload_from_storage()
        """
        with self._lock:
            self._load_all_providers()

    def start_auto_reload(self, interval_minutes: int = 10) -> None:
        """
        Start automatic reloading (no-op for database implementation).

        The database implementation does not require auto-reload because:
        - Changes are persisted immediately to the database
        - Data is always current when queried
        - No external file watching is needed

        This method is provided for API compatibility with ModelRegistryJSON.

        Args:
            interval_minutes: Ignored for database implementation

        Note:
            If you need to detect external database changes, call
            reload_from_storage() manually when needed.

        Example:
            >>> registry.start_auto_reload()  # No effect for DB implementation
        """
        with self._lock:
            print("Note: Auto-reload is not needed for database implementation. "
                  "Database changes are reflected immediately on next query.")

    def stop_auto_reload(self) -> None:
        """
        Stop automatic reloading (no-op for database implementation).

        This method is provided for API compatibility with ModelRegistryJSON.

        Example:
            >>> registry.stop_auto_reload()  # No effect for DB implementation
        """
        pass

    def load_json_directory(self, json_directory: str) -> List[str]:
        """
        Load all JSON files from a directory into the database.

        This is typically done once to populate the database from JSON configurations.

        Args:
            json_directory: Directory containing JSON configuration files

        Returns:
            List of loaded provider names

        Example:
            >>> loaded = registry.load_json_directory("/path/to/configs")
            >>> print(f"Loaded {len(loaded)} providers")
        """
        with self._lock:
            loaded_providers = self._db_handler.load_all_json_files(json_directory)
            # Reload providers after loading JSONs
            self._load_all_providers()
            return loaded_providers

    def load_json_file(self, json_path: str) -> str:
        """
        Load a single JSON file into the database.

        Args:
            json_path: Path to JSON configuration file

        Returns:
            Provider name

        Example:
            >>> provider_name = registry.load_json_file("/path/to/anthropic.json")
        """
        with self._lock:
            provider_name = self._db_handler.insert_provider_from_json(json_path)
            # Reload the specific provider
            self._providers[provider_name] = ModelProviderDB(provider_name, self._db_handler)
            return provider_name

    def get_database_handler(self) -> ModelManagementDBHandler:
        """
        Get the underlying database handler.

        Returns:
            ModelManagementDBHandler instance

        Note:
            This provides direct access to the database for advanced operations.
        """
        return self._db_handler

    def get_registry_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the registry state.

        Returns:
            Dictionary with registry statistics

        Example:
            >>> summary = registry.get_registry_summary()
            >>> print(f"Providers: {summary['provider_count']}")
            >>> print(f"Total models: {summary['total_model_count']}")
        """
        with self._lock:
            base_summary = super().get_registry_summary()
            db_stats = self._db_handler.get_statistics()
            base_summary['database_stats'] = db_stats
            return base_summary

    def __repr__(self) -> str:
        """String representation of the ModelRegistryDB."""
        with self._lock:
            return (
                f"ModelRegistryDB("
                f"providers={self.get_provider_count()}, "
                f"models={self.get_total_model_count()}, "
                f"database=enabled)"
            )

    def __str__(self) -> str:
        """Human-readable string representation."""
        with self._lock:
            return (
                f"ModelRegistry with {self.get_provider_count()} providers "
                f"and {self.get_total_model_count()} models (database-backed)"
            )


__all__ = ['ModelRegistryDB']
