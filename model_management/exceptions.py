"""
Abhikarta LLM Model Registry Exceptions

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This module and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

This document is provided "as is" without warranty of any kind, either expressed or implied.
The copyright holder shall not be liable for any damages arising from the use of this
document or the software system it describes.

Patent Pending: Certain architectural patterns and implementations described in this
module may be subject to patent applications.
"""


class ModelRegistryException(Exception):
    """Base exception for all model registry related errors."""
    pass


class ProviderNotFoundException(ModelRegistryException):
    """Raised when a requested provider is not found in the registry."""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        super().__init__(f"Provider '{provider_name}' not found in registry")


class ProviderDisabledException(ModelRegistryException):
    """Raised when attempting to access a disabled provider."""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        super().__init__(f"Provider '{provider_name}' is disabled")


class ModelNotFoundException(ModelRegistryException):
    """Raised when a requested model is not found."""

    def __init__(self, model_name: str, provider_name: str = None):
        self.model_name = model_name
        self.provider_name = provider_name
        if provider_name:
            super().__init__(f"Model '{model_name}' not found in provider '{provider_name}'")
        else:
            super().__init__(f"Model '{model_name}' not found")


class ModelDisabledException(ModelRegistryException):
    """Raised when attempting to access a disabled model."""

    def __init__(self, model_name: str, provider_name: str = None):
        self.model_name = model_name
        self.provider_name = provider_name
        if provider_name:
            super().__init__(f"Model '{model_name}' in provider '{provider_name}' is disabled")
        else:
            super().__init__(f"Model '{model_name}' is disabled")


class ModelAlreadyExistsException(ModelRegistryException):
    """Raised when trying to create a model that already exists."""

    def __init__(self, model_name: str, provider_name: str):
        self.model_name = model_name
        self.provider_name = provider_name
        super().__init__(f"Model '{model_name}' already exists in provider '{provider_name}'")


class NoModelsAvailableException(ModelRegistryException):
    """Raised when no models are available for a specific capability or criteria."""

    def __init__(self, criteria: str):
        self.criteria = criteria
        super().__init__(f"No models available for criteria: {criteria}")


class ConfigurationError(ModelRegistryException):
    """Raised when there is an error in configuration files."""

    def __init__(self, message: str, file_path: str = None):
        self.file_path = file_path
        if file_path:
            super().__init__(f"Configuration error in '{file_path}': {message}")
        else:
            super().__init__(f"Configuration error: {message}")


__all__ = [
    'ModelRegistryException',
    'ProviderNotFoundException',
    'ProviderDisabledException',
    'ModelNotFoundException',
    'ModelDisabledException',
    'ModelAlreadyExistsException',
    'NoModelsAvailableException',
    'ConfigurationError'
]