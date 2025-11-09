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
from model_provider import Model
from model_management_db_handler import ModelManagementDBHandler
from exceptions import ConfigurationError, ModelNotFoundException


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
        >>> registry = ModelRegistryDB.get_instance(db_connection_pool_name="sqllitepool")
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

    def __init__(self, db_connection_pool_name: str):
        """
        Initialize the ModelRegistryDB with database backend.

        Note: Use get_instance() instead of direct initialization to ensure singleton.

        Args:
            db_connection_pool_name: Name of database connection pool

        Raises:
            ConfigurationError: If there are errors initializing database
        """
        super().__init__()

        # Initialize database handler
        try:
            self._db_handler = ModelManagementDBHandler.get_instance(db_connection_pool_name)

        except Exception as e:
            raise ConfigurationError(f"Failed to initialize database: {e}")

        # Initial load
        self._load_all_providers()

    @classmethod
    def get_instance(cls, db_connection_pool_name: str = None) -> 'ModelRegistryDB':
        """
        Get the singleton instance of ModelRegistryDB.

        Args:
            db_connection_pool_name: Path to SQLite database (required on first call)

        Returns:
            The singleton ModelRegistryDB instance

        Raises:
            ValueError: If db_path is None on first call

        Example:
            >>> # First initialization
            >>> registry = ModelRegistryDB.get_instance(db_connection_pool_name="sqlitepool")
            >>>
            >>> # Subsequent calls
            >>> registry = ModelRegistryDB.get_instance()  # Uses existing instance
        """
        with cls._instance_lock:
            if cls._instance is None:
                if db_connection_pool_name is None:
                    raise ValueError("db_path must be provided on first call to get_instance()")
                cls._instance = cls(db_connection_pool_name)
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

    # ==================================================================================
    # MODEL CRUD OPERATIONS
    # ==================================================================================

    def create_model(self, provider_name: str, model_data: Dict[str, Any]) -> Model:
        """Create a new model for a provider."""
        from exceptions import ModelAlreadyExistsException
        from model_provider import Model
        
        provider = self.get_provider_by_name(provider_name)
        
        with self._lock:
            # Check if model already exists
            try:
                existing = self.get_model_from_provider_by_name(provider_name, model_data['name'])
                raise ModelAlreadyExistsException(model_data['name'], provider_name)
            except ModelNotFoundException:
                # Model doesn't exist, safe to create
                pass
            
            # Prepare cost dictionary if individual cost fields are provided
            if 'input_cost_per_million' in model_data or 'output_cost_per_million' in model_data:
                if 'cost' not in model_data:
                    model_data['cost'] = {}
                if 'input_cost_per_million' in model_data:
                    model_data['cost']['input_per_1m'] = model_data['input_cost_per_million']
                if 'output_cost_per_million' in model_data:
                    model_data['cost']['output_per_1m'] = model_data['output_cost_per_million']
            
            # Create the model object to validate data
            model = Model(model_data)
            model.provider = provider_name
            
            # Insert into database using individual parameters
            model_id = self._db_handler.insert_model(
                provider_name=provider_name,
                name=model.name,
                version=model.version,
                description=model.description,
                context_window=model.context_window,
                max_output=model.max_output,
                enabled=model.enabled
            )
            
            # Insert costs
            if model.cost:
                self._db_handler.insert_model_cost(model_id, model.cost)
            
            # Insert capabilities
            if model.capabilities:
                self._db_handler.insert_model_capabilities(model_id, model.capabilities)
            
            # Insert strengths
            if model.strengths:
                self._db_handler.insert_model_strengths(model_id, model.strengths)
            
            # Reload provider to include new model
            self._providers[provider_name] = ModelProviderDB(provider_name, self._db_handler)
            
            return self.get_model_from_provider_by_name(provider_name, model_data['name'])

    def delete_model(self, provider_name: str, model_name: str) -> None:
        """Permanently delete a model from a provider."""
        provider = self.get_provider_by_name(provider_name)
        
        with self._lock:
            # Verify model exists
            model = self.get_model_from_provider_by_name(provider_name, model_name)
            
            # Delete from database
            self._db_handler.delete_model(provider_name, model_name)
            
            # Reload provider
            self._providers[provider_name] = ModelProviderDB(provider_name, self._db_handler)

    def update_model(self, provider_name: str, model_name: str, updates: Dict[str, Any]) -> Model:
        """Update multiple attributes of a model at once."""
        provider = self.get_provider_by_name(provider_name)
        
        with self._lock:
            # Get existing model to verify it exists
            model = self.get_model_from_provider_by_name(provider_name, model_name)
            
            # Handle special cases
            if 'capabilities' in updates:
                # Get model_id
                model_dict = self._db_handler.get_model_by_name(provider_name, model_name)
                if model_dict:
                    # Delete existing capabilities
                    with self._db_handler._get_cursor() as cursor:
                        cursor.execute("DELETE FROM model_capabilities WHERE model_id = ?", (model_dict['id'],))
                    # Insert new capabilities
                    self._db_handler.insert_model_capabilities(model_dict['id'], updates['capabilities'])
                del updates['capabilities']
            
            if 'strengths' in updates:
                # Get model_id
                model_dict = self._db_handler.get_model_by_name(provider_name, model_name)
                if model_dict:
                    # Delete existing strengths
                    with self._db_handler._get_cursor() as cursor:
                        cursor.execute("DELETE FROM model_strengths WHERE model_id = ?", (model_dict['id'],))
                    # Insert new strengths
                    self._db_handler.insert_model_strengths(model_dict['id'], updates['strengths'])
                del updates['strengths']
            
            if 'cost' in updates:
                # Get model_id
                model_dict = self._db_handler.get_model_by_name(provider_name, model_name)
                if model_dict:
                    # Delete existing cost
                    with self._db_handler._get_cursor() as cursor:
                        cursor.execute("DELETE FROM model_costs WHERE model_id = ?", (model_dict['id'],))
                    # Insert new cost
                    self._db_handler.insert_model_cost(model_dict['id'], updates['cost'])
                del updates['cost']
            
            # Update basic fields using **kwargs
            if updates:
                self._db_handler.update_model(provider_name, model_name, **updates)
            
            # Reload provider
            self._providers[provider_name] = ModelProviderDB(provider_name, self._db_handler)
            
            return self.get_model_from_provider_by_name(provider_name, model_name)

    def update_model_description(self, provider_name: str, model_name: str, description: str) -> Model:
        """Update the description of a model."""
        return self.update_model(provider_name, model_name, {'description': description})

    def update_model_version(self, provider_name: str, model_name: str, version: str) -> Model:
        """Update the version of a model."""
        return self.update_model(provider_name, model_name, {'version': version})

    def update_model_context_window(self, provider_name: str, model_name: str, context_window: int) -> Model:
        """Update the context window size of a model."""
        if context_window <= 0:
            raise ValueError("Context window must be positive")
        return self.update_model(provider_name, model_name, {'context_window': context_window})

    def update_model_max_output(self, provider_name: str, model_name: str, max_output: int) -> Model:
        """Update the maximum output tokens of a model."""
        if max_output <= 0:
            raise ValueError("Max output must be positive")
        return self.update_model(provider_name, model_name, {'max_output': max_output})

    def update_model_costs(self, provider_name: str, model_name: str, 
                           input_cost_per_million: float, output_cost_per_million: float) -> Model:
        """Update the costs of a model."""
        if input_cost_per_million < 0 or output_cost_per_million < 0:
            raise ValueError("Costs cannot be negative")
        
        # Get current model to merge with existing cost structure
        model = self.get_model_from_provider_by_name(provider_name, model_name)
        cost = model.cost.copy() if model.cost else {}
        cost['input_per_1m'] = input_cost_per_million
        cost['output_per_1m'] = output_cost_per_million
        
        return self.update_model(provider_name, model_name, {'cost': cost})

    def add_model_capability(self, provider_name: str, model_name: str, 
                            capability: str, value: Any = True) -> Model:
        """Add or update a capability for a model."""
        model = self.get_model_from_provider_by_name(provider_name, model_name)
        capabilities = model.capabilities.copy()
        capabilities[capability] = value
        return self.update_model(provider_name, model_name, {'capabilities': capabilities})

    def remove_model_capability(self, provider_name: str, model_name: str, capability: str) -> Model:
        """Remove a capability from a model."""
        model = self.get_model_from_provider_by_name(provider_name, model_name)
        capabilities = model.capabilities.copy()
        if capability in capabilities:
            del capabilities[capability]
        return self.update_model(provider_name, model_name, {'capabilities': capabilities})

    def update_model_capability(self, provider_name: str, model_name: str, 
                               capability: str, value: Any) -> Model:
        """Update the value of an existing capability."""
        return self.add_model_capability(provider_name, model_name, capability, value)

    def update_model_capabilities(self, provider_name: str, model_name: str, 
                                 capabilities: Dict[str, Any]) -> Model:
        """Replace all capabilities of a model."""
        return self.update_model(provider_name, model_name, {'capabilities': capabilities})

    def add_model_strength(self, provider_name: str, model_name: str, strength: str) -> Model:
        """Add a strength to a model."""
        model = self.get_model_from_provider_by_name(provider_name, model_name)
        strengths = model.strengths.copy() if model.strengths else []
        if strength not in strengths:
            strengths.append(strength)
        return self.update_model(provider_name, model_name, {'strengths': strengths})

    def remove_model_strength(self, provider_name: str, model_name: str, strength: str) -> Model:
        """Remove a strength from a model."""
        model = self.get_model_from_provider_by_name(provider_name, model_name)
        strengths = model.strengths.copy() if model.strengths else []
        if strength in strengths:
            strengths.remove(strength)
        return self.update_model(provider_name, model_name, {'strengths': strengths})

    def update_model_strengths(self, provider_name: str, model_name: str, 
                              strengths: List[str]) -> Model:
        """Replace all strengths of a model."""
        return self.update_model(provider_name, model_name, {'strengths': strengths})

    # ==================================================================================
    # STRING REPRESENTATIONS
    # ==================================================================================

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
