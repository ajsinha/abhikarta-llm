"""
Abhikarta LLM Model Registry - Abstract Base Class

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
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from model_management.model_provider import ModelProvider, Model
from model_management.exceptions import (
    ProviderNotFoundException,
    ProviderDisabledException,
    ModelNotFoundException,
    ModelDisabledException,
    NoModelsAvailableException
)


class ModelRegistry(ABC):
    """
    Abstract base class for model registry implementations.

    This class defines the interface that all registry implementations must follow,
    whether they use database storage, JSON files, or any other backend.

    The registry provides:
    - Provider management
    - Model querying
    - Cross-provider operations
    - Cost optimization
    - Enable/disable functionality

    Thread Safety:
        All methods must be thread-safe in implementations.
        Safe for concurrent access from multiple threads.
    """

    def __init__(self):
        """Initialize the ModelRegistry base class."""
        self._lock = threading.RLock()
        self._providers: Dict[str, ModelProvider] = {}

    # ==================================================================================
    # ABSTRACT METHODS - Must be implemented by subclasses
    # ==================================================================================

    @abstractmethod
    def _load_all_providers(self) -> None:
        """
        Load all provider configurations from storage.

        This method should populate self._providers with ModelProvider instances.
        """
        pass

    @abstractmethod
    def reload_from_storage(self) -> None:
        """
        Reload all providers from storage.

        This is useful when data has been updated externally.
        """
        pass

    @abstractmethod
    def start_auto_reload(self, interval_minutes: int = 10) -> None:
        """
        Start automatic reloading of data at specified intervals.

        Args:
            interval_minutes: Reload interval in minutes (default: 10)

        Note:
            Implementation-specific. Some implementations may not support
            auto-reload or may implement it as a no-op.

        Example:
            >>> registry.start_auto_reload(interval_minutes=5)
        """
        pass

    @abstractmethod
    def stop_auto_reload(self) -> None:
        """
        Stop automatic reloading of data.

        Note:
            Implementation-specific. Some implementations may not support
            auto-reload or may implement it as a no-op.

        Example:
            >>> registry.stop_auto_reload()
        """
        pass

    # ==================================================================================
    # MODEL CRUD OPERATIONS
    # ==================================================================================

    @abstractmethod
    def create_model(
            self,
            provider_name: str,
            model_data: Dict[str, Any]
    ) -> Model:
        """
        Create a new model for a provider.

        Args:
            provider_name: Name of the provider
            model_data: Dictionary containing model configuration

        Returns:
            The created Model instance

        Raises:
            ProviderNotFoundException: If provider not found
            ModelAlreadyExistsException: If model already exists
            ConfigurationError: If model_data is invalid

        Example:
            >>> model_data = {
            ...     'name': 'new-model-v1',
            ...     'description': 'New model',
            ...     'version': '1.0',
            ...     'enabled': True,
            ...     'context_window': 8192,
            ...     'max_output': 4096,
            ...     'input_cost_per_million': 1.0,
            ...     'output_cost_per_million': 2.0,
            ...     'supports_streaming': True,
            ...     'supports_function_calling': True,
            ...     'capabilities': {'chat': True},
            ...     'release_date': '2024-01-01'
            ... }
            >>> model = registry.create_model('anthropic', model_data)
        """
        pass

    @abstractmethod
    def delete_model(
            self,
            provider_name: str,
            model_name: str
    ) -> None:
        """
        Permanently delete a model from a provider.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model to delete

        Raises:
            ProviderNotFoundException: If provider not found
            ModelNotFoundException: If model not found

        Example:
            >>> registry.delete_model('anthropic', 'old-model-v1')
        """
        pass

    @abstractmethod
    def update_model(
            self,
            provider_name: str,
            model_name: str,
            updates: Dict[str, Any]
    ) -> Model:
        """
        Update multiple attributes of a model at once.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model
            updates: Dictionary of attributes to update

        Returns:
            The updated Model instance

        Raises:
            ProviderNotFoundException: If provider not found
            ModelNotFoundException: If model not found
            ConfigurationError: If updates are invalid

        Example:
            >>> updates = {
            ...     'description': 'Updated description',
            ...     'version': '2.0',
            ...     'context_window': 16384
            ... }
            >>> model = registry.update_model('anthropic', 'claude-opus-4', updates)
        """
        pass

    # ==================================================================================
    # MODEL ATTRIBUTE UPDATES - BASIC PROPERTIES
    # ==================================================================================

    @abstractmethod
    def update_model_description(
            self,
            provider_name: str,
            model_name: str,
            description: str
    ) -> Model:
        """
        Update the description of a model.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model
            description: New description

        Returns:
            The updated Model instance

        Raises:
            ProviderNotFoundException: If provider not found
            ModelNotFoundException: If model not found

        Example:
            >>> model = registry.update_model_description(
            ...     'anthropic',
            ...     'claude-opus-4',
            ...     'Most powerful model with enhanced reasoning'
            ... )
        """
        pass

    @abstractmethod
    def update_model_version(
            self,
            provider_name: str,
            model_name: str,
            version: str
    ) -> Model:
        """
        Update the version of a model.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model
            version: New version string

        Returns:
            The updated Model instance

        Raises:
            ProviderNotFoundException: If provider not found
            ModelNotFoundException: If model not found

        Example:
            >>> model = registry.update_model_version(
            ...     'anthropic',
            ...     'claude-opus-4',
            ...     '2.0'
            ... )
        """
        pass

    @abstractmethod
    def update_model_context_window(
            self,
            provider_name: str,
            model_name: str,
            context_window: int
    ) -> Model:
        """
        Update the context window size of a model.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model
            context_window: New context window size in tokens

        Returns:
            The updated Model instance

        Raises:
            ProviderNotFoundException: If provider not found
            ModelNotFoundException: If model not found
            ValueError: If context_window is invalid

        Example:
            >>> model = registry.update_model_context_window(
            ...     'anthropic',
            ...     'claude-opus-4',
            ...     200000
            ... )
        """
        pass

    @abstractmethod
    def update_model_max_output(
            self,
            provider_name: str,
            model_name: str,
            max_output: int
    ) -> Model:
        """
        Update the maximum output tokens of a model.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model
            max_output: New maximum output tokens

        Returns:
            The updated Model instance

        Raises:
            ProviderNotFoundException: If provider not found
            ModelNotFoundException: If model not found
            ValueError: If max_output is invalid

        Example:
            >>> model = registry.update_model_max_output(
            ...     'anthropic',
            ...     'claude-opus-4',
            ...     8192
            ... )
        """
        pass

    @abstractmethod
    def update_model_costs(
            self,
            provider_name: str,
            model_name: str,
            input_cost_per_million: float,
            output_cost_per_million: float
    ) -> Model:
        """
        Update the costs of a model.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model
            input_cost_per_million: New input cost per million tokens
            output_cost_per_million: New output cost per million tokens

        Returns:
            The updated Model instance

        Raises:
            ProviderNotFoundException: If provider not found
            ModelNotFoundException: If model not found
            ValueError: If costs are invalid

        Example:
            >>> model = registry.update_model_costs(
            ...     'anthropic',
            ...     'claude-opus-4',
            ...     15.0,
            ...     75.0
            ... )
        """
        pass

    # ==================================================================================
    # MODEL ATTRIBUTE UPDATES - CAPABILITIES
    # ==================================================================================

    @abstractmethod
    def add_model_capability(
            self,
            provider_name: str,
            model_name: str,
            capability: str,
            value: Any = True
    ) -> Model:
        """
        Add or update a capability for a model.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model
            capability: Capability name (e.g., 'vision', 'streaming')
            value: Capability value (default: True)

        Returns:
            The updated Model instance

        Raises:
            ProviderNotFoundException: If provider not found
            ModelNotFoundException: If model not found

        Example:
            >>> model = registry.add_model_capability(
            ...     'anthropic',
            ...     'claude-opus-4',
            ...     'vision',
            ...     True
            ... )
        """
        pass

    @abstractmethod
    def remove_model_capability(
            self,
            provider_name: str,
            model_name: str,
            capability: str
    ) -> Model:
        """
        Remove a capability from a model.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model
            capability: Capability name to remove

        Returns:
            The updated Model instance

        Raises:
            ProviderNotFoundException: If provider not found
            ModelNotFoundException: If model not found

        Example:
            >>> model = registry.remove_model_capability(
            ...     'anthropic',
            ...     'claude-opus-4',
            ...     'vision'
            ... )
        """
        pass

    @abstractmethod
    def update_model_capability(
            self,
            provider_name: str,
            model_name: str,
            capability: str,
            value: Any
    ) -> Model:
        """
        Update the value of an existing capability.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model
            capability: Capability name
            value: New capability value

        Returns:
            The updated Model instance

        Raises:
            ProviderNotFoundException: If provider not found
            ModelNotFoundException: If model not found

        Example:
            >>> model = registry.update_model_capability(
            ...     'anthropic',
            ...     'claude-opus-4',
            ...     'max_batch_size',
            ...     100
            ... )
        """
        pass

    @abstractmethod
    def update_model_capabilities(
            self,
            provider_name: str,
            model_name: str,
            capabilities: Dict[str, Any]
    ) -> Model:
        """
        Replace all capabilities of a model.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model
            capabilities: New capabilities dictionary

        Returns:
            The updated Model instance

        Raises:
            ProviderNotFoundException: If provider not found
            ModelNotFoundException: If model not found

        Example:
            >>> capabilities = {
            ...     'chat': True,
            ...     'vision': True,
            ...     'streaming': True,
            ...     'function_calling': True
            ... }
            >>> model = registry.update_model_capabilities(
            ...     'anthropic',
            ...     'claude-opus-4',
            ...     capabilities
            ... )
        """
        pass

    # ==================================================================================
    # MODEL ATTRIBUTE UPDATES - STRENGTHS
    # ==================================================================================

    @abstractmethod
    def add_model_strength(
            self,
            provider_name: str,
            model_name: str,
            strength: str
    ) -> Model:
        """
        Add a strength to a model.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model
            strength: Strength description to add

        Returns:
            The updated Model instance

        Raises:
            ProviderNotFoundException: If provider not found
            ModelNotFoundException: If model not found

        Example:
            >>> model = registry.add_model_strength(
            ...     'anthropic',
            ...     'claude-opus-4',
            ...     'Excellent mathematical reasoning'
            ... )
        """
        pass

    @abstractmethod
    def remove_model_strength(
            self,
            provider_name: str,
            model_name: str,
            strength: str
    ) -> Model:
        """
        Remove a strength from a model.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model
            strength: Strength description to remove

        Returns:
            The updated Model instance

        Raises:
            ProviderNotFoundException: If provider not found
            ModelNotFoundException: If model not found

        Example:
            >>> model = registry.remove_model_strength(
            ...     'anthropic',
            ...     'claude-opus-4',
            ...     'Outdated strength description'
            ... )
        """
        pass

    @abstractmethod
    def update_model_strengths(
            self,
            provider_name: str,
            model_name: str,
            strengths: List[str]
    ) -> Model:
        """
        Replace all strengths of a model.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model
            strengths: New list of strength descriptions

        Returns:
            The updated Model instance

        Raises:
            ProviderNotFoundException: If provider not found
            ModelNotFoundException: If model not found

        Example:
            >>> strengths = [
            ...     'Best-in-class reasoning',
            ...     'Excellent code generation',
            ...     'Multilingual support'
            ... ]
            >>> model = registry.update_model_strengths(
            ...     'anthropic',
            ...     'claude-opus-4',
            ...     strengths
            ... )
        """
        pass

    # ==================================================================================
    # PROVIDER MANAGEMENT
    # ==================================================================================

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
            >>> print(f"Found: {provider.provider}")
        """
        with self._lock:
            if provider_name not in self._providers:
                raise ProviderNotFoundException(provider_name)

            provider = self._providers[provider_name]

            if not provider.enabled:
                raise ProviderDisabledException(provider_name)

            return provider

    def get_all_providers(self, include_disabled: bool = False) -> Dict[str, ModelProvider]:
        """
        Get all providers.

        Args:
            include_disabled: Whether to include disabled providers (default: False)

        Returns:
            Dictionary mapping provider names to ModelProvider instances

        Example:
            >>> providers = registry.get_all_providers()
            >>> for name, provider in providers.items():
            ...     print(f"- {name}: {provider.get_model_count()} models")
        """
        with self._lock:
            if include_disabled:
                return self._providers.copy()
            return {
                name: provider
                for name, provider in self._providers.items()
                if provider.enabled
            }

    def enable_provider(self, provider_name: str) -> bool:
        """
        Enable a provider.

        Args:
            provider_name: Name of the provider

        Returns:
            True if provider was found and enabled, False otherwise

        Example:
            >>> registry.enable_provider("anthropic")
        """
        with self._lock:
            if provider_name in self._providers:
                self._providers[provider_name].enabled = True
                return True
            return False

    def disable_provider(self, provider_name: str) -> bool:
        """
        Disable a provider.

        Args:
            provider_name: Name of the provider

        Returns:
            True if provider was found and disabled, False otherwise

        Example:
            >>> registry.disable_provider("mock")
        """
        with self._lock:
            if provider_name in self._providers:
                self._providers[provider_name].enabled = False
                return True
            return False

    # ==================================================================================
    # MODEL ACCESS METHODS
    # ==================================================================================

    def get_model_from_provider_by_name(
            self,
            provider_name: str,
            model_name: str
    ) -> Model:
        """
        Get a specific model from a provider by name.

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
        Get a specific model from a provider by name and verify it has a capability.

        This method combines model retrieval with capability validation, ensuring
        the model not only exists but also supports the required capability.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model
            capability: Required capability (use ModelCapability enum values)

        Returns:
            Model instance

        Raises:
            ProviderNotFoundException: If provider not found
            ProviderDisabledException: If provider is disabled
            ModelNotFoundException: If model not found
            ModelDisabledException: If model is disabled
            NoModelsAvailableException: If model doesn't have the required capability

        Example:
            >>> model = registry.get_model_from_provider_by_name_capability(
            ...     "google",
            ...     "gemini-1.5-pro",
            ...     "vision"
            ... )
            >>> print(f"Found vision-capable model: {model.name}")
        """
        # First get the model (handles all provider/model exceptions)
        model = self.get_model_from_provider_by_name(provider_name, model_name)

        # Verify the model has the required capability
        if not model.has_capability(capability):
            raise NoModelsAvailableException(
                f"Model '{model_name}' from provider '{provider_name}' "
                f"does not support capability '{capability}'"
            )

        return model

    def get_all_models_from_provider(
            self,
            provider_name: str,
            include_disabled: bool = False
    ) -> List[Model]:
        """
        Get all models from a specific provider.

        Args:
            provider_name: Name of the provider
            include_disabled: Whether to include disabled models

        Returns:
            List of Model instances

        Raises:
            ProviderNotFoundException: If provider not found
            ProviderDisabledException: If provider is disabled (unless include_disabled=True)

        Example:
            >>> models = registry.get_all_models_from_provider("anthropic")
            >>> for model in models:
            ...     print(f"- {model.name}")
        """
        if not include_disabled:
            provider = self.get_provider_by_name(provider_name)
        else:
            with self._lock:
                if provider_name not in self._providers:
                    raise ProviderNotFoundException(provider_name)
                provider = self._providers[provider_name]

        return provider.get_all_models(include_disabled)

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
    # MODEL ENABLE/DISABLE
    # ==================================================================================

    def enable_model(self, provider_name: str, model_name: str) -> bool:
        """
        Enable a specific model.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model

        Returns:
            True if model was found and enabled, False otherwise

        Example:
            >>> registry.enable_model("anthropic", "claude-3-haiku-20240307")
        """
        with self._lock:
            if provider_name not in self._providers:
                return False
            return self._providers[provider_name].enable_model(model_name)

    def disable_model(self, provider_name: str, model_name: str) -> bool:
        """
        Disable a specific model.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model

        Returns:
            True if model was found and disabled, False otherwise

        Example:
            >>> registry.disable_model("anthropic", "claude-instant-1.2")
        """
        with self._lock:
            if provider_name not in self._providers:
                return False
            return self._providers[provider_name].disable_model(model_name)

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
                'providers': providers_info
            }

    def __repr__(self) -> str:
        """String representation of the ModelRegistry."""
        with self._lock:
            return (
                f"ModelRegistry("
                f"providers={self.get_provider_count()}, "
                f"models={self.get_total_model_count()})"
            )

    def __str__(self) -> str:
        """Human-readable string representation."""
        with self._lock:
            return (
                f"ModelRegistry with {self.get_provider_count()} providers "
                f"and {self.get_total_model_count()} models"
            )


__all__ = ['ModelRegistry']
