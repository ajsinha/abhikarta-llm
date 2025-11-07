"""
Abhikarta LLM Model Provider and Model Classes

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
import threading
from typing import Optional, List, Dict, Any
from pathlib import Path
from model_management import ModelCapability


class Model:
    """
    Represents a single LLM model with its configuration and capabilities.

    This class encapsulates all information about a specific model including its
    name, version, capabilities, cost structure, and operational parameters.

    Attributes:
        name (str): Unique identifier for the model
        version (str): Model version
        description (str): Human-readable description
        provider (str): Original model provider (if different from hosting provider)
        strengths (List[str]): Model's key strengths and use cases
        context_window (int): Maximum input tokens
        max_output (int): Maximum output tokens
        parameters (Optional[str]): Model size (e.g., "70B", "7B")
        license (Optional[str]): Licensing information
        cost (Dict[str, Any]): Pricing structure
        performance (Dict[str, Any]): Performance metrics (if available)
        capabilities (Dict[str, Any]): Feature flags and metadata
        enabled (bool): Whether the model is enabled for use
        _raw_config (Dict[str, Any]): Original configuration from JSON
    """

    def __init__(self, config: Dict[str, Any], enabled: bool = True):
        """
        Initialize a Model instance from configuration dictionary.

        Args:
            config: Dictionary containing model configuration from JSON
            enabled: Whether the model is enabled (default: True)

        Raises:
            KeyError: If required fields are missing from config
            ValueError: If config values are invalid
        """
        # Thread safety lock
        self._lock = threading.RLock()

        # Required fields
        self.name: str = config['name']
        self.version: str = config['version']
        self.description: str = config['description']
        self.context_window: int = config['context_window']
        self.max_output: int = config['max_output']
        self.capabilities: Dict[str, Any] = config['capabilities']
        self.cost: Dict[str, Any] = config['cost']

        # Optional fields with defaults
        self.provider: Optional[str] = config.get('provider')
        self.model_id: Optional[str] = config.get('model_id')
        self.strengths: List[str] = config.get('strengths', [])
        self.parameters: Optional[str] = config.get('parameters')
        self.license: Optional[str] = config.get('license')
        self.performance: Dict[str, Any] = config.get('performance', {})

        # State
        self._enabled: bool = enabled

        # Store raw config for reference
        self._raw_config: Dict[str, Any] = config.copy()

    @property
    def enabled(self) -> bool:
        """Thread-safe getter for enabled status."""
        with self._lock:
            return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        """Thread-safe setter for enabled status."""
        with self._lock:
            self._enabled = value

    def has_capability(self, capability: str) -> bool:
        """
        Check if the model has a specific capability.

        Args:
            capability: The capability to check (use ModelCapability enum values)

        Returns:
            True if the model has the capability, False otherwise

        Example:
            >>> model.has_capability(ModelCapability.VISION.value)
            True
        """
        return self.capabilities.get(capability, False) is True

    def has_all_capabilities(self, capabilities: List[str]) -> bool:
        """
        Check if the model has all specified capabilities.

        Args:
            capabilities: List of capability strings to check

        Returns:
            True if the model has all capabilities, False otherwise

        Example:
            >>> model.has_all_capabilities([
            ...     ModelCapability.VISION.value,
            ...     ModelCapability.FUNCTION_CALLING.value
            ... ])
            True
        """
        return all(self.has_capability(cap) for cap in capabilities)

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate the cost for a given number of input and output tokens.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Total cost in USD

        Note:
            Handles different pricing scales (per 1K, per 1M) automatically
        """
        input_cost = 0.0
        output_cost = 0.0

        # Handle per 1K pricing
        if 'input_per_1k' in self.cost:
            input_cost = (input_tokens / 1000) * self.cost['input_per_1k']
            output_cost = (output_tokens / 1000) * self.cost['output_per_1k']

        # Handle per 1M pricing
        elif 'input_per_1m' in self.cost:
            input_cost = (input_tokens / 1_000_000) * self.cost['input_per_1m']
            output_cost = (output_tokens / 1_000_000) * self.cost['output_per_1m']

        # Handle tiered pricing (Google style)
        elif 'input_per_1m_0_128k' in self.cost:
            if input_tokens <= 128_000:
                input_cost = (input_tokens / 1_000_000) * self.cost['input_per_1m_0_128k']
            else:
                first_tier = (128_000 / 1_000_000) * self.cost['input_per_1m_0_128k']
                second_tier = ((input_tokens - 128_000) / 1_000_000) * self.cost['input_per_1m_128k_plus']
                input_cost = first_tier + second_tier

            output_cost = (output_tokens / 1_000_000) * self.cost['output_per_1m']

        return input_cost + output_cost

    def get_capability_value(self, capability: str) -> Any:
        """
        Get the value of a capability (useful for metadata fields).

        Args:
            capability: The capability to retrieve

        Returns:
            The capability value (could be bool, int, array, etc.)

        Example:
            >>> model.get_capability_value(ModelCapability.DIMENSIONS.value)
            1536
        """
        return self.capabilities.get(capability)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Model to a dictionary representation.

        Returns:
            Dictionary with all model information
        """
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'provider': self.provider,
            'model_id': self.model_id,
            'strengths': self.strengths,
            'context_window': self.context_window,
            'max_output': self.max_output,
            'parameters': self.parameters,
            'license': self.license,
            'cost': self.cost,
            'performance': self.performance,
            'capabilities': self.capabilities,
            'enabled': self.enabled
        }

    def __repr__(self) -> str:
        """String representation of the Model."""
        status = "enabled" if self.enabled else "disabled"
        return f"Model(name='{self.name}', version='{self.version}', {status})"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.name} (v{self.version}) - {self.description}"


class ModelProvider:
    """
    Represents an LLM provider with its configuration and available models.

    This class manages a collection of models from a specific provider, loading
    configuration from JSON files and providing convenient methods for model
    selection based on capabilities and cost.

    Attributes:
        provider (str): Provider identifier (e.g., "anthropic", "openai")
        api_version (str): API version
        base_url (str): Base URL for API requests
        notes (Dict[str, str]): Provider-specific documentation
        models (List[Model]): List of Model instances
        enabled (bool): Whether the provider is enabled
        config_path (Path): Path to the configuration JSON file
        _raw_config (Dict[str, Any]): Original configuration from JSON
    """

    def __init__(self, config_path: str, enabled: bool = True):
        """
        Initialize a ModelProvider by loading configuration from a JSON file.

        Args:
            config_path: Path to the JSON configuration file
            enabled: Whether the provider is enabled (default: True)

        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            json.JSONDecodeError: If the JSON is malformed
            KeyError: If required fields are missing

        Example:
            >>> provider = ModelProvider("config/anthropic.json")
            >>> print(provider.provider)
            'anthropic'
        """
        # Thread safety lock - must be created before any other operations
        self._lock = threading.RLock()

        self.config_path = Path(config_path)
        self._enabled = enabled
        self._load_config()

    @property
    def enabled(self) -> bool:
        """Thread-safe getter for enabled status."""
        with self._lock:
            return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        """Thread-safe setter for enabled status."""
        with self._lock:
            self._enabled = value

    def _load_config(self) -> None:
        """
        Load configuration from the JSON file.

        This is an internal method called by __init__ and reload().

        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            json.JSONDecodeError: If the JSON is malformed
            KeyError: If required fields are missing
        """
        with self._lock:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Store raw config
            self._raw_config = config

            # Required fields
            self.provider: str = config['provider']
            self.api_version: str = config['api_version']
            self.base_url: Optional[str] = config.get('base_url')

            # Optional fields
            self.notes: Dict[str, str] = config.get('notes', {})
            self.model_families: Dict[str, Any] = config.get('model_families', {})
            self.prompt_caching: Dict[str, Any] = config.get('prompt_caching', {})
            self.extended_thinking: Dict[str, Any] = config.get('extended_thinking', {})
            self.batch_api: Dict[str, Any] = config.get('batch_api', {})
            self.vision_capabilities: Dict[str, Any] = config.get('vision_capabilities', {})
            self.tool_use: Dict[str, Any] = config.get('tool_use', {})
            self.deployment_options: Dict[str, Any] = config.get('deployment_options', {})
            self.best_practices: Dict[str, Any] = config.get('best_practices', {})

            # Load models
            self.models: List[Model] = []
            for model_config in config.get('models', []):
                try:
                    model = Model(model_config, enabled=True)
                    self.models.append(model)
                except (KeyError, ValueError) as e:
                    # Log warning but continue loading other models
                    print(f"Warning: Failed to load model from {self.provider}: {e}")
                    continue

    def reload(self) -> None:
        """
        Reload the configuration from the JSON file.

        This method re-reads the configuration file and updates all internal data.
        Useful for picking up configuration changes without restarting the application.

        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            json.JSONDecodeError: If the JSON is malformed

        Example:
            >>> provider.reload()
            >>> print(f"Reloaded {len(provider.models)} models")
        """
        self._load_config()

    def get_model_by_name(self, model_name: str) -> Optional[Model]:
        """
        Get a model by its name.

        Args:
            model_name: The name of the model to retrieve

        Returns:
            Model instance if found and enabled, None otherwise

        Example:
            >>> model = provider.get_model_by_name("claude-3-7-sonnet-20250219")
            >>> if model:
            ...     print(model.description)
        """
        for model in self.models:
            if model.name == model_name and model.enabled:
                return model
        return None

    def get_model_by_name_and_capability(
            self,
            model_name: str,
            capability: str
    ) -> Optional[Model]:
        """
        Get a model by name only if it supports the requested capability.

        Args:
            model_name: The name of the model to retrieve
            capability: The required capability (use ModelCapability enum values)

        Returns:
            Model instance if found, enabled, and has capability, None otherwise

        Example:
            >>> model = provider.get_model_by_name_and_capability(
            ...     "claude-3-5-sonnet-20241022",
            ...     ModelCapability.VISION.value
            ... )
            >>> if model:
            ...     print(f"{model.name} supports vision")
        """
        model = self.get_model_by_name(model_name)
        if model and model.has_capability(capability):
            return model
        return None

    def get_cheapest_model_for_capability(
            self,
            capability: str,
            input_tokens: int = 1000,
            output_tokens: int = 500
    ) -> Optional[Model]:
        """
        Get the most cost-effective model that supports a capability.

        Args:
            capability: The required capability (use ModelCapability enum values)
            input_tokens: Expected input tokens for cost calculation (default: 1000)
            output_tokens: Expected output tokens for cost calculation (default: 500)

        Returns:
            The cheapest Model with the capability, or None if no models support it

        Example:
            >>> cheapest = provider.get_cheapest_model_for_capability(
            ...     ModelCapability.CHAT.value,
            ...     input_tokens=5000,
            ...     output_tokens=1000
            ... )
            >>> if cheapest:
            ...     cost = cheapest.calculate_cost(5000, 1000)
            ...     print(f"Cheapest: {cheapest.name} at ${cost:.4f}")
        """
        candidates = self.get_models_for_capability(capability)

        if not candidates:
            return None

        # Calculate cost for each candidate
        costs = []
        for model in candidates:
            try:
                cost = model.calculate_cost(input_tokens, output_tokens)
                costs.append((cost, model))
            except Exception as e:
                # Skip models with invalid cost configurations
                print(f"Warning: Could not calculate cost for {model.name}: {e}")
                continue

        if not costs:
            return None

        # Sort by cost and return cheapest
        costs.sort(key=lambda x: x[0])
        return costs[0][1]

    def get_models_for_capability(self, capability: str) -> List[Model]:
        """
        Get all models that support a specific capability.

        Args:
            capability: The required capability (use ModelCapability enum values)

        Returns:
            List of Model instances that support the capability (may be empty)

        Example:
            >>> vision_models = provider.get_models_for_capability(
            ...     ModelCapability.VISION.value
            ... )
            >>> for model in vision_models:
            ...     print(f"- {model.name}")
        """
        return [
            model for model in self.models
            if model.enabled and model.has_capability(capability)
        ]

    def get_models_for_capabilities(self, capabilities: List[str]) -> List[Model]:
        """
        Get all models that support ALL specified capabilities.

        Args:
            capabilities: List of required capabilities

        Returns:
            List of Model instances that support all capabilities (may be empty)

        Example:
            >>> multimodal_models = provider.get_models_for_capabilities([
            ...     ModelCapability.VISION.value,
            ...     ModelCapability.FUNCTION_CALLING.value
            ... ])
        """
        return [
            model for model in self.models
            if model.enabled and model.has_all_capabilities(capabilities)
        ]

    def get_all_models(self, include_disabled: bool = False) -> List[Model]:
        """
        Get all models from this provider.

        Args:
            include_disabled: Whether to include disabled models (default: False)

        Returns:
            List of Model instances

        Example:
            >>> all_models = provider.get_all_models()
            >>> print(f"Provider has {len(all_models)} enabled models")
        """
        if include_disabled:
            return self.models
        return [model for model in self.models if model.enabled]

    def get_model_count(self, include_disabled: bool = False) -> int:
        """
        Get the count of models.

        Args:
            include_disabled: Whether to include disabled models (default: False)

        Returns:
            Number of models
        """
        return len(self.get_all_models(include_disabled))

    def enable_model(self, model_name: str) -> bool:
        """
        Enable a specific model.

        Args:
            model_name: Name of the model to enable

        Returns:
            True if model was found and enabled, False otherwise

        Example:
            >>> provider.enable_model("claude-3-haiku-20240307")
        """
        for model in self.models:
            if model.name == model_name:
                model.enabled = True
                return True
        return False

    def disable_model(self, model_name: str) -> bool:
        """
        Disable a specific model.

        Args:
            model_name: Name of the model to disable

        Returns:
            True if model was found and disabled, False otherwise

        Example:
            >>> provider.disable_model("claude-instant-1.2")
        """
        for model in self.models:
            if model.name == model_name:
                model.enabled = False
                return True
        return False

    def get_capabilities_summary(self) -> Dict[str, int]:
        """
        Get a summary of capabilities across all enabled models.

        Returns:
            Dictionary mapping capability names to count of models supporting it

        Example:
            >>> summary = provider.get_capabilities_summary()
            >>> print(f"Vision-capable models: {summary.get('vision', 0)}")
        """
        summary: Dict[str, int] = {}

        for model in self.models:
            if not model.enabled:
                continue

            for capability, value in model.capabilities.items():
                if value is True:  # Only count boolean True capabilities
                    summary[capability] = summary.get(capability, 0) + 1

        return summary

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the ModelProvider to a dictionary representation.

        Returns:
            Dictionary with provider and model information
        """
        return {
            'provider': self.provider,
            'api_version': self.api_version,
            'base_url': self.base_url,
            'enabled': self.enabled,
            'model_count': self.get_model_count(),
            'models': [model.to_dict() for model in self.models if model.enabled],
            'notes': self.notes
        }

    def __repr__(self) -> str:
        """String representation of the ModelProvider."""
        status = "enabled" if self.enabled else "disabled"
        model_count = self.get_model_count()
        return f"ModelProvider(provider='{self.provider}', models={model_count}, {status})"

    def __str__(self) -> str:
        """Human-readable string representation."""
        model_count = self.get_model_count()
        return f"{self.provider} Provider (API v{self.api_version}) - {model_count} models"


# Convenience function for loading multiple providers
def load_providers(config_dir: str, provider_names: Optional[List[str]] = None) -> Dict[str, ModelProvider]:
    """
    Load multiple ModelProvider instances from a directory.

    Args:
        config_dir: Directory containing provider JSON files
        provider_names: Optional list of provider names to load. If None, loads all.

    Returns:
        Dictionary mapping provider names to ModelProvider instances

    Example:
        >>> providers = load_providers("./config", ["anthropic", "openai"])
        >>> anthropic = providers["anthropic"]
    """
    from pathlib import Path

    config_path = Path(config_dir)
    providers = {}

    if provider_names:
        # Load specific providers
        for name in provider_names:
            json_file = config_path / f"{name}.json"
            if json_file.exists():
                try:
                    providers[name] = ModelProvider(str(json_file))
                except Exception as e:
                    print(f"Warning: Failed to load provider {name}: {e}")
    else:
        # Load all JSON files in directory
        for json_file in config_path.glob("*.json"):
            try:
                provider = ModelProvider(str(json_file))
                providers[provider.provider] = provider
            except Exception as e:
                print(f"Warning: Failed to load provider from {json_file}: {e}")

    return providers


__all__ = ['Model', 'ModelProvider', 'load_providers']