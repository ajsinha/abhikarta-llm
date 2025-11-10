"""
Abhikarta LLM Model Provider - Database Implementation

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This module and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

Patent Pending: Certain architectural patterns and implementations described in this
module may be subject to patent applications.
"""

import json
from typing import Optional, List, Dict, Any
from model_management.model_provider import ModelProvider, Model
from model_management.model_management_db_handler import ModelManagementDBHandler


class ModelProviderDB(ModelProvider):
    """
    Database-backed implementation of ModelProvider.

    This class manages a collection of models from a specific provider, loading
    configuration from a database and providing convenient methods for model
    selection based on capabilities and cost.

    Attributes:
        provider (str): Provider identifier (e.g., "anthropic", "openai")
        api_version (str): API version
        base_url (str): Base URL for API requests
        notes (Dict[str, Any]): Additional provider notes
        models (List[Model]): List of Model instances
        enabled (bool): Whether the provider is enabled
    """

    def __init__(self, provider_name: str, db_handler: ModelManagementDBHandler):
        """
        Initialize a ModelProviderDB instance from database.

        Args:
            provider_name: Name of the provider
            db_handler: Database handler instance

        Raises:
            ValueError: If provider not found in database
        """
        super().__init__()
        self._db_handler = db_handler

        # Load provider data from database
        provider_data = db_handler.get_provider_by_name(provider_name)
        if not provider_data:
            raise ValueError(f"Provider '{provider_name}' not found in database")

        # Provider attributes
        self.id: int = provider_data['id']
        self.provider: str = provider_data['provider']
        self.api_version: str = provider_data['api_version']
        self.base_url: Optional[str] = provider_data.get('base_url')
        self._enabled: bool = provider_data.get('enabled', True)

        # Parse notes
        notes_json = provider_data.get('notes')
        self.notes: Dict[str, Any] = json.loads(notes_json) if notes_json else {}

        # Load models
        self._load_models()

    def _load_models(self) -> None:
        """Load all models for this provider from database."""
        with self._lock:
            model_data_list = self._db_handler.get_models_by_provider(
                self.provider,
                include_disabled=True
            )
            self.models = [Model(model_data) for model_data in model_data_list]

    def _on_enabled_changed(self, enabled: bool) -> None:
        """
        Update enabled status in database when changed.

        Args:
            enabled: New enabled status
        """
        self._db_handler.update_provider(self.provider, enabled=enabled)

    def reload(self) -> None:
        """
        Reload provider and model data from database.

        This is useful when data has been updated in the database by another process.
        """
        with self._lock:
            provider_data = self._db_handler.get_provider_by_name(self.provider)
            if provider_data:
                self.api_version = provider_data['api_version']
                self.base_url = provider_data.get('base_url')
                self._enabled = provider_data.get('enabled', True)

                notes_json = provider_data.get('notes')
                self.notes = json.loads(notes_json) if notes_json else {}

            self._load_models()


# Convenience function for loading multiple providers
def load_providers(
    db_handler: ModelManagementDBHandler,
    provider_names: Optional[List[str]] = None
) -> Dict[str, ModelProviderDB]:
    """
    Load multiple ModelProviderDB instances from database.

    Args:
        db_handler: Database handler instance
        provider_names: Optional list of provider names to load. If None, loads all.

    Returns:
        Dictionary mapping provider names to ModelProviderDB instances

    Example:
        >>> handler = ModelManagementDBHandler.get_instance("/path/to/db_management.sqlite")
        >>> providers = load_providers(handler, ["anthropic", "openai"])
        >>> anthropic = providers["anthropic"]
    """
    providers = {}

    if provider_names:
        # Load specific providers
        for name in provider_names:
            try:
                providers[name] = ModelProviderDB(name, db_handler)
            except Exception as e:
                print(f"Warning: Failed to load provider {name}: {e}")
    else:
        # Load all providers
        all_provider_data = db_handler.get_all_providers()
        for provider_data in all_provider_data:
            try:
                provider_name = provider_data['provider']
                providers[provider_name] = ModelProviderDB(provider_name, db_handler)
            except Exception as e:
                print(f"Warning: Failed to load provider {provider_data.get('provider')}: {e}")

    return providers


__all__ = ['ModelProviderDB', 'load_providers']
