"""
Abhikarta LLM Model Registry - Thread-Safe Singleton with Auto-Reload

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

import json
import os
import threading
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from model_provider import ModelProvider, Model
from exceptions import (
    ProviderNotFoundException,
    ProviderDisabledException,
    ModelNotFoundException,
    ModelDisabledException,
    NoModelsAvailableException,
    ConfigurationError
)


class ModelRegistry:
    """
    Thread-safe singleton registry for managing ModelProvider instances.

    This class:
    - Loads all JSON configuration files from a specified directory
    - Creates and manages ModelProvider instances
    - Auto-reloads configurations at configurable intervals
    - Provides convenience methods for accessing models across providers
    - Handles provider and model enable/disable states
    - Tracks file changes to minimize unnecessary reloads

    The registry runs a background thread that periodically checks for:
    - New JSON files (automatically added)
    - Removed JSON files (providers removed from registry)
    - Modified JSON files (providers updated)

    Thread Safety:
        All methods are thread-safe using RLock for reentrant locking.
        Safe for concurrent access from multiple threads.

    Usage:
        >>> registry = ModelRegistry.get_instance("/path/to/configs")
        >>> registry.start_auto_reload(interval_seconds=600)  # 10 minutes
        >>>
        >>> # Get all providers
        >>> providers = registry.get_all_providers()
        >>>
        >>> # Get specific model
        >>> model = registry.get_model_from_provider_by_name("anthropic", "claude-opus-4")
        >>>
        >>> # Find cheapest model for capability
        >>> cheapest = registry.get_cheapest_model_for_capability("vision")
    """

    _instance: Optional['ModelRegistry'] = None
    _instance_lock = threading.RLock()

    def __init__(self, config_directory: str, auto_reload_interval: int = 600):
        """
        Initialize the ModelRegistry.

        Note: Use get_instance() instead of direct initialization to ensure singleton.

        Args:
            config_directory: Directory containing JSON configuration files
            auto_reload_interval: Auto-reload interval in seconds (default: 600 = 10 minutes)

        Raises:
            FileNotFoundError: If the configuration directory doesn't exist
            ConfigurationError: If there are errors loading configurations
        """
        self._config_dir = Path(config_directory)
        if not self._config_dir.exists():
            raise FileNotFoundError(f"Configuration directory not found: {self._config_dir}")
        if not self._config_dir.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {self._config_dir}")

        # Thread safety
        self._lock = threading.RLock()

        # Provider storage
        self._providers: Dict[str, ModelProvider] = {}

        # File tracking for change detection
        self._file_hashes: Dict[str, str] = {}

        # Auto-reload configuration
        self._auto_reload_interval = auto_reload_interval
        self._auto_reload_thread: Optional[threading.Thread] = None
        self._stop_auto_reload = threading.Event()
        self._auto_reload_enabled = False

        # Initial load
        self._load_all_providers()

    @classmethod
    def get_instance(cls, config_directory: str = None, auto_reload_interval: int = 600) -> 'ModelRegistry':
        """
        Get the singleton instance of ModelRegistry.

        Args:
            config_directory: Directory containing JSON configuration files (required on first call)
            auto_reload_interval: Auto-reload interval in seconds (default: 600 = 10 minutes)

        Returns:
            The singleton ModelRegistry instance

        Raises:
            ValueError: If config_directory is None on first call

        Example:
            >>> # First initialization
            >>> registry = ModelRegistry.get_instance("/path/to/configs")
            >>>
            >>> # Subsequent calls
            >>> registry = ModelRegistry.get_instance()  # Uses existing instance
        """
        with cls._instance_lock:
            if cls._instance is None:
                if config_directory is None:
                    raise ValueError("config_directory must be provided on first call to get_instance()")
                cls._instance = cls(config_directory, auto_reload_interval)
            return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance (mainly for testing).

        This will stop any running auto-reload thread and clear the instance.
        """
        with cls._instance_lock:
            if cls._instance is not None:
                cls._instance.stop_auto_reload()
                cls._instance = None

    def _calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate MD5 hash of a file to detect changes.

        Args:
            file_path: Path to the file

        Returns:
            MD5 hash as hex string
        """
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()

    def _load_all_providers(self) -> None:
        """
        Load all provider configurations from JSON files in the config directory.

        This method:
        - Scans for all .json files
        - Loads new providers
        - Updates modified providers
        - Removes providers for deleted files

        Raises:
            ConfigurationError: If there are errors loading configurations
        """
        with self._lock:
            json_files = set(self._config_dir.glob("*.json"))
            current_files = {f.stem: f for f in json_files}

            # Track which providers to remove
            providers_to_remove = set(self._providers.keys()) - set(current_files.keys())

            # Remove providers for deleted files
            for provider_name in providers_to_remove:
                print(f"Removing provider '{provider_name}' (file deleted)")
                del self._providers[provider_name]
                if provider_name in self._file_hashes:
                    del self._file_hashes[provider_name]

            # Load or update providers
            for file_stem, file_path in current_files.items():
                try:
                    # Calculate file hash
                    current_hash = self._calculate_file_hash(file_path)
                    previous_hash = self._file_hashes.get(file_stem)

                    # Only load/reload if file is new or changed
                    if previous_hash is None:
                        # New file
                        print(f"Loading new provider from: {file_path.name}")
                        provider = ModelProvider(str(file_path))
                        self._providers[provider.provider] = provider
                        self._file_hashes[file_stem] = current_hash
                    elif current_hash != previous_hash:
                        # File changed
                        print(f"Reloading modified provider from: {file_path.name}")
                        provider = ModelProvider(str(file_path))
                        self._providers[provider.provider] = provider
                        self._file_hashes[file_stem] = current_hash
                    # else: file unchanged, skip reload

                except Exception as e:
                    print(f"Error loading provider from {file_path.name}: {e}")
                    raise ConfigurationError(str(e), str(file_path))

    def reload_all_providers(self) -> int:
        """
        Manually trigger a reload of all provider configurations.

        This checks for new, modified, and deleted configuration files.

        Returns:
            Number of providers currently loaded

        Example:
            >>> count = registry.reload_all_providers()
            >>> print(f"Loaded {count} providers")
        """
        with self._lock:
            self._load_all_providers()
            return len(self._providers)

    def start_auto_reload(self, interval_seconds: Optional[int] = None) -> None:
        """
        Start the auto-reload background thread.

        Args:
            interval_seconds: Reload interval in seconds (uses configured value if None)

        Example:
            >>> registry.start_auto_reload(600)  # Reload every 10 minutes
            >>> # ... do work ...
            >>> registry.stop_auto_reload()
        """
        with self._lock:
            if self._auto_reload_enabled:
                print("Auto-reload is already running")
                return

            if interval_seconds is not None:
                self._auto_reload_interval = interval_seconds

            self._stop_auto_reload.clear()
            self._auto_reload_thread = threading.Thread(
                target=self._auto_reload_worker,
                daemon=True,
                name="ModelRegistry-AutoReload"
            )
            self._auto_reload_enabled = True
            self._auto_reload_thread.start()
            print(f"Auto-reload started with interval: {self._auto_reload_interval} seconds")

    def stop_auto_reload(self) -> None:
        """
        Stop the auto-reload background thread.

        Example:
            >>> registry.stop_auto_reload()
        """
        with self._lock:
            if not self._auto_reload_enabled:
                return

            self._stop_auto_reload.set()
            self._auto_reload_enabled = False

            if self._auto_reload_thread and self._auto_reload_thread.is_alive():
                self._auto_reload_thread.join(timeout=5)

            print("Auto-reload stopped")

    def _auto_reload_worker(self) -> None:
        """
        Background worker thread for auto-reloading configurations.

        This runs in a separate daemon thread and periodically calls reload_all_providers().
        """
        while not self._stop_auto_reload.is_set():
            try:
                # Wait for the specified interval, but check stop flag periodically
                if self._stop_auto_reload.wait(timeout=self._auto_reload_interval):
                    break  # Stop flag was set

                print("Auto-reload: Checking for configuration changes...")
                self.reload_all_providers()

            except Exception as e:
                print(f"Error in auto-reload worker: {e}")
                # Continue running despite errors

    # ==================================================================================
    # PROVIDER ACCESS METHODS
    # ==================================================================================

    def get_all_providers(self, include_disabled: bool = False) -> Dict[str, ModelProvider]:
        """
        Get all providers in the registry.

        Args:
            include_disabled: Whether to include disabled providers (default: False)

        Returns:
            Dictionary mapping provider names to ModelProvider instances

        Example:
            >>> providers = registry.get_all_providers()
            >>> for name, provider in providers.items():
            ...     print(f"{name}: {provider.get_model_count()} models")
        """
        with self._lock:
            if include_disabled:
                return self._providers.copy()
            return {
                name: provider
                for name, provider in self._providers.items()
                if provider.enabled
            }

    def get_provider_by_name(self, provider_name: str) -> ModelProvider:
        """
        Get a provider by name.

        Args:
            provider_name: Name of the provider

        Returns:
            ModelProvider instance

        Raises:
            ProviderNotFoundException: If provider not found
            ProviderDisabledException: If provider is disabled

        Example:
            >>> provider = registry.get_provider_by_name("anthropic")
            >>> print(provider.api_version)
        """
        with self._lock:
            if provider_name not in self._providers:
                raise ProviderNotFoundException(provider_name)

            provider = self._providers[provider_name]
            if not provider.enabled:
                raise ProviderDisabledException(provider_name)

            return provider

    # ==================================================================================
    # MODEL ACCESS METHODS
    # ==================================================================================

    def get_model_from_provider_by_name(
            self,
            provider_name: str,
            model_name: str
    ) -> Model:
        """
        Get a specific model from a specific provider.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model

        Returns:
            Model instance

        Raises:
            ProviderNotFoundException: If provider not found
            ProviderDisabledException: If provider is disabled
            ModelNotFoundException: If model not found
            ModelDisabledException: If model is disabled

        Example:
            >>> model = registry.get_model_from_provider_by_name(
            ...     "anthropic",
            ...     "claude-opus-4"
            ... )
            >>> print(f"Context window: {model.context_window}")
        """
        provider = self.get_provider_by_name(provider_name)

        with self._lock:
            model = provider.get_model_by_name(model_name)
            if model is None:
                raise ModelNotFoundException(model_name, provider_name)

            if not model.enabled:
                raise ModelDisabledException(model_name, provider_name)

            return model

    def get_model_from_provider_by_name_capability(
            self,
            provider_name: str,
            model_name: str,
            capability: str
    ) -> Model:
        """
        Get a model from a provider only if it has a specific capability.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model
            capability: Required capability

        Returns:
            Model instance

        Raises:
            ProviderNotFoundException: If provider not found
            ProviderDisabledException: If provider is disabled
            ModelNotFoundException: If model not found or doesn't have capability
            ModelDisabledException: If model is disabled

        Example:
            >>> model = registry.get_model_from_provider_by_name_capability(
            ...     "anthropic",
            ...     "claude-opus-4",
            ...     "vision"
            ... )
        """
        model = self.get_model_from_provider_by_name(provider_name, model_name)

        if not model.has_capability(capability):
            raise ModelNotFoundException(
                model_name,
                provider_name
            )

        return model

    # ==================================================================================
    # CROSS-PROVIDER MODEL SEARCH METHODS
    # ==================================================================================

    def get_all_models_for_capability(
            self,
            capability: str,
            include_disabled_providers: bool = False
    ) -> List[Tuple[str, Model]]:
        """
        Get all models across all providers that support a capability.

        Args:
            capability: Required capability
            include_disabled_providers: Whether to include disabled providers

        Returns:
            List of tuples (provider_name, Model instance)

        Example:
            >>> vision_models = registry.get_all_models_for_capability("vision")
            >>> for provider_name, model in vision_models:
            ...     print(f"{provider_name}/{model.name}")
        """
        with self._lock:
            results = []
            providers = self.get_all_providers(include_disabled_providers)

            for provider_name, provider in providers.items():
                models = provider.get_models_for_capability(capability)
                for model in models:
                    results.append((provider_name, model))

            return results

    def get_cheapest_model_for_capability(
            self,
            capability: str,
            input_tokens: int = 100000,
            output_tokens: int = 1000
    ) -> Tuple[str, Model, float]:
        """
        Find the cheapest model across all providers for a given capability.

        Args:
            capability: Required capability
            input_tokens: Number of input tokens for cost calculation (default: 100000)
            output_tokens: Number of output tokens for cost calculation (default: 1000)

        Returns:
            Tuple of (provider_name, Model instance, cost)

        Raises:
            NoModelsAvailableException: If no models support the capability

        Example:
            >>> provider, model, cost = registry.get_cheapest_model_for_capability("chat")
            >>> print(f"Cheapest: {provider}/{model.name} at ${cost:.4f}")
        """
        with self._lock:
            candidates = self.get_all_models_for_capability(capability)

            if not candidates:
                raise NoModelsAvailableException(f"capability '{capability}'")

            # Calculate costs
            costs = []
            for provider_name, model in candidates:
                try:
                    cost = model.calculate_cost(input_tokens, output_tokens)
                    costs.append((cost, provider_name, model))
                except Exception as e:
                    print(f"Warning: Could not calculate cost for {provider_name}/{model.name}: {e}")
                    continue

            if not costs:
                raise NoModelsAvailableException(f"capability '{capability}' (cost calculation failed for all)")

            # Sort by cost and return cheapest
            costs.sort(key=lambda x: x[0])
            cost, provider_name, model = costs[0]
            return provider_name, model, cost

    def get_cheapest_model_for_provider_and_capability(
            self,
            provider_name: str,
            capability: str,
            input_tokens: int = 100000,
            output_tokens: int = 1000
    ) -> Tuple[Model, float]:
        """
        Find the cheapest model from a specific provider for a given capability.

        Args:
            provider_name: Name of the provider
            capability: Required capability
            input_tokens: Number of input tokens for cost calculation (default: 100000)
            output_tokens: Number of output tokens for cost calculation (default: 1000)

        Returns:
            Tuple of (Model instance, cost)

        Raises:
            ProviderNotFoundException: If provider not found
            ProviderDisabledException: If provider is disabled
            NoModelsAvailableException: If no models support the capability

        Example:
            >>> model, cost = registry.get_cheapest_model_for_provider_and_capability(
            ...     "anthropic",
            ...     "vision"
            ... )
            >>> print(f"Cheapest Anthropic vision model: {model.name} at ${cost:.4f}")
        """
        provider = self.get_provider_by_name(provider_name)

        with self._lock:
            cheapest = provider.get_cheapest_model_for_capability(
                capability,
                input_tokens,
                output_tokens
            )

            if cheapest is None:
                raise NoModelsAvailableException(
                    f"capability '{capability}' in provider '{provider_name}'"
                )

            cost = cheapest.calculate_cost(input_tokens, output_tokens)
            return cheapest, cost

    # ==================================================================================
    # UTILITY METHODS
    # ==================================================================================

    def get_provider_count(self, include_disabled: bool = False) -> int:
        """
        Get the count of providers in the registry.

        Args:
            include_disabled: Whether to include disabled providers

        Returns:
            Number of providers
        """
        with self._lock:
            if include_disabled:
                return len(self._providers)
            return sum(1 for p in self._providers.values() if p.enabled)

    def get_total_model_count(self, include_disabled: bool = False) -> int:
        """
        Get the total count of models across all providers.

        Args:
            include_disabled: Whether to include disabled models/providers

        Returns:
            Total number of models
        """
        with self._lock:
            total = 0
            providers = self.get_all_providers(include_disabled)
            for provider in providers.values():
                total += provider.get_model_count(include_disabled)
            return total

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
            providers_info = []
            for name, provider in self._providers.items():
                providers_info.append({
                    'name': name,
                    'enabled': provider.enabled,
                    'model_count': provider.get_model_count(),
                    'api_version': provider.api_version
                })

            return {
                'provider_count': self.get_provider_count(),
                'total_provider_count': len(self._providers),
                'total_model_count': self.get_total_model_count(),
                'auto_reload_enabled': self._auto_reload_enabled,
                'auto_reload_interval': self._auto_reload_interval,
                'config_directory': str(self._config_dir),
                'providers': providers_info
            }

    def __repr__(self) -> str:
        """String representation of the ModelRegistry."""
        with self._lock:
            return (
                f"ModelRegistry("
                f"providers={self.get_provider_count()}, "
                f"models={self.get_total_model_count()}, "
                f"auto_reload={'on' if self._auto_reload_enabled else 'off'})"
            )

    def __str__(self) -> str:
        """Human-readable string representation."""
        with self._lock:
            return (
                f"ModelRegistry with {self.get_provider_count()} providers "
                f"and {self.get_total_model_count()} models"
            )


__all__ = ['ModelRegistry']