"""
Abhikarta LLM Model Registry - JSON File Implementation with Auto-Reload

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

import hashlib
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from model_registry import ModelRegistry
from model_provider_json import ModelProviderJSON
from exceptions import ConfigurationError


class ModelRegistryJSON(ModelRegistry):
    """
    JSON file-backed implementation of ModelRegistry with auto-reload.

    This singleton class:
    - Loads all JSON configuration files from a specified directory
    - Creates and manages ModelProviderJSON instances
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
        >>> registry = ModelRegistryJSON.get_instance("/path/to/configs")
        >>> registry.start_auto_reload(interval_seconds=600)  # 10 minutes
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

    _instance: Optional['ModelRegistryJSON'] = None
    _instance_lock = threading.RLock()

    def __init__(self, config_directory: str, auto_reload_interval_minutes: int = 10):
        """
        Initialize the ModelRegistryJSON.

        Note: Use get_instance() instead of direct initialization to ensure singleton.

        Args:
            config_directory: Directory containing JSON configuration files
            auto_reload_interval_minutes: Auto-reload interval in minutes (default: 10)

        Raises:
            FileNotFoundError: If the configuration directory doesn't exist
            ConfigurationError: If there are errors loading configurations
        """
        super().__init__()

        self._config_dir = Path(config_directory)
        if not self._config_dir.exists():
            raise FileNotFoundError(f"Configuration directory not found: {self._config_dir}")
        if not self._config_dir.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {self._config_dir}")

        # File tracking for change detection
        self._file_hashes: Dict[str, str] = {}

        # Auto-reload configuration (stored in minutes, converted to seconds for thread)
        self._auto_reload_interval_minutes = auto_reload_interval_minutes
        self._auto_reload_interval_seconds = auto_reload_interval_minutes * 60
        self._auto_reload_thread: Optional[threading.Thread] = None
        self._stop_auto_reload = threading.Event()
        self._auto_reload_enabled = False

        # Initial load
        self._load_all_providers()

    @classmethod
    def get_instance(cls, config_directory: str = None, auto_reload_interval_minutes: int = 10) -> 'ModelRegistryJSON':
        """
        Get the singleton instance of ModelRegistryJSON.

        Args:
            config_directory: Directory containing JSON configuration files (required on first call)
            auto_reload_interval_minutes: Auto-reload interval in minutes (default: 10)

        Returns:
            The singleton ModelRegistryJSON instance

        Raises:
            ValueError: If config_directory is None on first call

        Example:
            >>> # First initialization
            >>> registry = ModelRegistryJSON.get_instance("/path/to/configs")
            >>>
            >>> # Subsequent calls
            >>> registry = ModelRegistryJSON.get_instance()  # Uses existing instance
        """
        with cls._instance_lock:
            if cls._instance is None:
                if config_directory is None:
                    raise ValueError("config_directory must be provided on first call to get_instance()")
                cls._instance = cls(config_directory, auto_reload_interval_minutes)
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
                        provider = ModelProviderJSON(str(file_path))
                        self._providers[provider.provider] = provider
                        self._file_hashes[file_stem] = current_hash
                    elif current_hash != previous_hash:
                        # File changed
                        print(f"Reloading modified provider from: {file_path.name}")
                        provider = ModelProviderJSON(str(file_path))
                        self._providers[provider.provider] = provider
                        self._file_hashes[file_stem] = current_hash
                    # else: file unchanged, skip

                except Exception as e:
                    print(f"Error loading provider from {file_path.name}: {e}")
                    raise ConfigurationError(f"Failed to load {file_path.name}", str(file_path))

    def reload_from_storage(self) -> None:
        """
        Reload all providers from JSON files.

        This is useful when JSON files have been updated externally.

        Example:
            >>> registry.reload_from_storage()
        """
        with self._lock:
            self._load_all_providers()

    def start_auto_reload(self, interval_minutes: int = 10) -> None:
        """
        Start the auto-reload background thread.

        Args:
            interval_minutes: Reload interval in minutes (default: 10)

        Example:
            >>> registry.start_auto_reload(interval_minutes=5)  # Check every 5 minutes
        """
        with self._lock:
            if self._auto_reload_enabled:
                print("Auto-reload already running")
                return

            # Update interval
            self._auto_reload_interval_minutes = interval_minutes
            self._auto_reload_interval_seconds = interval_minutes * 60

            self._stop_auto_reload.clear()
            self._auto_reload_thread = threading.Thread(
                target=self._auto_reload_worker,
                daemon=True,
                name="ModelRegistry-AutoReload"
            )
            self._auto_reload_thread.start()
            self._auto_reload_enabled = True
            print(f"Auto-reload started with interval: {interval_minutes} minutes "
                  f"({self._auto_reload_interval_seconds} seconds)")

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
            if self._auto_reload_thread and self._auto_reload_thread.is_alive():
                self._auto_reload_thread.join(timeout=5)
            self._auto_reload_enabled = False
            print("Auto-reload stopped")

    def _auto_reload_worker(self) -> None:
        """
        Background worker that periodically reloads configurations.

        This runs in a separate daemon thread.
        """
        while not self._stop_auto_reload.is_set():
            # Sleep for the interval (but check stop flag periodically)
            for _ in range(self._auto_reload_interval_seconds):
                if self._stop_auto_reload.is_set():
                    return
                time.sleep(1)

            # Reload configurations
            try:
                self._load_all_providers()
            except Exception as e:
                print(f"Error during auto-reload: {e}")

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
            base_summary.update({
                'auto_reload_enabled': self._auto_reload_enabled,
                'auto_reload_interval_minutes': self._auto_reload_interval_minutes,
                'auto_reload_interval_seconds': self._auto_reload_interval_seconds,
                'config_directory': str(self._config_dir)
            })
            return base_summary

    def __repr__(self) -> str:
        """String representation of the ModelRegistryJSON."""
        with self._lock:
            return (
                f"ModelRegistryJSON("
                f"providers={self.get_provider_count()}, "
                f"models={self.get_total_model_count()}, "
                f"auto_reload={'on' if self._auto_reload_enabled else 'off'})"
            )

    def __str__(self) -> str:
        """Human-readable string representation."""
        with self._lock:
            return (
                f"ModelRegistry with {self.get_provider_count()} providers "
                f"and {self.get_total_model_count()} models (JSON-backed)"
            )


__all__ = ['ModelRegistryJSON']
