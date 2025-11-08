"""
Abhikarta LLM Model Provider - JSON File Implementation

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
from pathlib import Path
from typing import Optional, List, Dict, Any
from model_provider import ModelProvider, Model


class ModelProviderJSON(ModelProvider):
    """
    JSON file-backed implementation of ModelProvider.

    This class manages a collection of models from a specific provider, loading
    configuration from JSON files and providing convenient methods for model
    selection based on capabilities and cost.

    Attributes:
        provider (str): Provider identifier (e.g., "anthropic", "openai")
        api_version (str): API version
        base_url (str): Base URL for API requests
        notes (Dict[str, Any]): Additional provider notes
        models (List[Model]): List of Model instances
        enabled (bool): Whether the provider is enabled
    """

    def __init__(self, config_path: str, enabled: bool = True):
        """
        Initialize a ModelProviderJSON instance from JSON file.

        Args:
            config_path: Path to the JSON configuration file
            enabled: Whether the provider is enabled (default: True)

        Raises:
            FileNotFoundError: If the JSON file doesn't exist
            ValueError: If the JSON is invalid or missing required fields
        """
        super().__init__()
        
        self._config_path = Path(config_path)
        if not self._config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        # Load configuration
        self._load_from_file(enabled)

    def _load_from_file(self, enabled: bool = True) -> None:
        """
        Load configuration from JSON file.

        Args:
            enabled: Whether to set provider as enabled
        """
        with self._lock:
            with open(self._config_path, 'r') as f:
                config = json.load(f)

            # Provider configuration
            self.provider = config['provider']
            self.api_version = config.get('api_version', 'v1')
            self.base_url = config.get('base_url')
            self._enabled = enabled
            self.notes = config.get('notes', {})

            # Load models
            self.models = []
            for model_config in config.get('models', []):
                # Add provider name to model config
                model_config['provider'] = self.provider
                model = Model(model_config)
                self.models.append(model)

    def _on_enabled_changed(self, enabled: bool) -> None:
        """
        Handle enabled status change.

        For JSON provider, this only updates in-memory state.
        To persist, would need to write back to JSON file.

        Args:
            enabled: New enabled status
        """
        # In JSON implementation, changes are only in-memory
        # Could optionally write back to file here if needed
        pass

    def reload(self) -> None:
        """
        Reload provider and model data from JSON file.

        This is useful when the JSON file has been updated externally.
        """
        with self._lock:
            current_enabled = self._enabled
            self._load_from_file(current_enabled)


# Convenience function for loading multiple providers
def load_providers(
    config_dir: str,
    provider_names: Optional[List[str]] = None
) -> Dict[str, ModelProviderJSON]:
    """
    Load multiple ModelProviderJSON instances from a directory.

    Args:
        config_dir: Directory containing provider JSON files
        provider_names: Optional list of provider names to load. If None, loads all.

    Returns:
        Dictionary mapping provider names to ModelProviderJSON instances

    Example:
        >>> providers = load_providers("./config", ["anthropic", "openai"])
        >>> anthropic = providers["anthropic"]
    """
    config_path = Path(config_dir)
    providers = {}

    if provider_names:
        # Load specific providers
        for name in provider_names:
            json_file = config_path / f"{name}.json"
            if json_file.exists():
                try:
                    providers[name] = ModelProviderJSON(str(json_file))
                except Exception as e:
                    print(f"Warning: Failed to load provider {name}: {e}")
    else:
        # Load all JSON files in directory
        for json_file in config_path.glob("*.json"):
            try:
                provider = ModelProviderJSON(str(json_file))
                providers[provider.provider] = provider
            except Exception as e:
                print(f"Warning: Failed to load provider from {json_file}: {e}")

    return providers


__all__ = ['ModelProviderJSON', 'load_providers']
