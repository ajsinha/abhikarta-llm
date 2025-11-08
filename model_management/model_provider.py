"""
Abhikarta LLM Model Provider - Abstract Base Class

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

import threading
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class Model:
    """
    Represents a single LLM model with its configuration and capabilities.

    This class encapsulates all information about a specific model including its
    name, version, capabilities, cost structure, and operational parameters.

    Attributes:
        name (str): Unique identifier for the model
        version (str): Model version
        description (str): Human-readable description
        provider (str): Original model provider
        strengths (List[str]): Model's key strengths and use cases
        context_window (int): Maximum input tokens
        max_output (int): Maximum output tokens
        parameters (Optional[str]): Model size (e.g., "70B", "7B")
        license (Optional[str]): Licensing information
        cost (Dict[str, Any]): Pricing structure
        performance (Dict[str, Any]): Performance metrics (if available)
        capabilities (Dict[str, Any]): Feature flags and metadata
        enabled (bool): Whether the model is enabled for use
    """

    def __init__(self, model_data: Dict[str, Any]):
        """
        Initialize a Model instance from data dictionary.

        Args:
            model_data: Dictionary containing model data

        Raises:
            KeyError: If required fields are missing from model_data
            ValueError: If model_data values are invalid
        """
        # Thread safety lock
        self._lock = threading.RLock()

        # Required fields
        self.name: str = model_data['name']
        self.version: str = model_data['version']
        self.description: str = model_data['description']
        self.context_window: int = model_data['context_window']
        self.max_output: int = model_data['max_output']
        self.capabilities: Dict[str, Any] = model_data.get('capabilities', {})
        self.cost: Dict[str, Any] = model_data.get('cost', {})

        # Optional fields with defaults
        self.provider: Optional[str] = model_data.get('provider')
        self.model_id: Optional[str] = model_data.get('model_id')
        self.replicate_model: Optional[str] = model_data.get('replicate_model')
        self.strengths: List[str] = model_data.get('strengths', [])
        self.parameters: Optional[str] = model_data.get('parameters')
        self.license: Optional[str] = model_data.get('license')
        self.performance: Dict[str, Any] = model_data.get('performance', {})

        # State
        self._enabled: bool = model_data.get('enabled', True)

        # Store ID if provided (for database implementations)
        self.id: Optional[int] = model_data.get('id')

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
        result = {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'provider': self.provider,
            'model_id': self.model_id,
            'replicate_model': self.replicate_model,
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
        if self.id is not None:
            result['id'] = self.id
        return result

    def __repr__(self) -> str:
        """String representation of the Model."""
        status = "enabled" if self.enabled else "disabled"
        return f"Model(name='{self.name}', version='{self.version}', {status})"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.name} (v{self.version}) - {self.description}"


class ModelProvider(ABC):
    """
    Abstract base class for LLM provider implementations.

    This class defines the interface that all provider implementations must follow,
    whether they use database storage, JSON files, or any other backend.

    Attributes:
        provider (str): Provider identifier (e.g., "anthropic", "openai")
        api_version (str): API version
        base_url (str): Base URL for API requests
        notes (Dict[str, Any]): Additional provider notes
        models (List[Model]): List of Model instances
        enabled (bool): Whether the provider is enabled
    """

    def __init__(self):
        """Initialize the ModelProvider base class."""
        self._lock = threading.RLock()
        self.provider: str = ""
        self.api_version: str = ""
        self.base_url: Optional[str] = None
        self._enabled: bool = True
        self.notes: Dict[str, Any] = {}
        self.models: List[Model] = []

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
            self._on_enabled_changed(value)

    @abstractmethod
    def _on_enabled_changed(self, enabled: bool) -> None:
        """
        Hook method called when enabled status changes.
        
        Implementations should override this to persist the change.
        
        Args:
            enabled: New enabled status
        """
        pass

    @abstractmethod
    def reload(self) -> None:
        """
        Reload provider and model data from storage.
        
        This is useful when data has been updated externally.
        """
        pass

    def get_model_by_name(self, model_name: str) -> Optional[Model]:
        """
        Get a model by its name.

        Args:
            model_name: Name of the model to retrieve

        Returns:
            Model instance or None if not found

        Example:
            >>> model = provider.get_model_by_name("claude-opus-4")
            >>> if model:
            ...     print(f"Found: {model.name}")
        """
        with self._lock:
            for model in self.models:
                if model.name == model_name:
                    return model
            return None

    def get_cheapest_model_for_capability(
        self,
        capability: str,
        input_tokens: int = 100000,
        output_tokens: int = 1000
    ) -> Optional[Model]:
        """
        Find the cheapest model that supports a specific capability.

        Args:
            capability: Required capability (use ModelCapability enum values)
            input_tokens: Number of input tokens for cost calculation (default: 100000)
            output_tokens: Number of output tokens for cost calculation (default: 1000)

        Returns:
            Cheapest Model instance or None if no models support the capability

        Example:
            >>> cheapest = provider.get_cheapest_model_for_capability(
            ...     ModelCapability.VISION.value,
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


__all__ = ['Model', 'ModelProvider']
