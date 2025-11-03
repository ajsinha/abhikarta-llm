"""
Custom Exceptions for LLM Abstraction System

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""


class LLMException(Exception):
    """Base exception for all LLM-related errors"""
    pass


class ProviderError(LLMException):
    """Error related to LLM provider operations"""
    pass


class ProviderNotFoundError(ProviderError):
    """Provider could not be found or loaded"""
    pass


class ProviderInitializationError(ProviderError):
    """Provider failed to initialize"""
    pass


class InvalidCredentialsError(ProviderError):
    """API credentials are invalid or missing"""
    pass


class ModelError(LLMException):
    """Error related to model operations"""
    pass


class ModelNotFoundError(ModelError):
    """Model not available or not supported"""
    pass


class ConfigurationError(LLMException):
    """Configuration-related errors"""
    pass


class InvalidConfigurationError(ConfigurationError):
    """Configuration is invalid or malformed"""
    pass


class MissingConfigurationError(ConfigurationError):
    """Required configuration is missing"""
    pass


class APIError(LLMException):
    """API call failed"""
    def __init__(self, message: str, status_code: int = None, provider: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.provider = provider


class RateLimitError(APIError):
    """API rate limit exceeded"""
    pass


class TimeoutError(APIError):
    """API request timed out"""
    pass


class ValidationError(LLMException):
    """Input validation failed"""
    pass


class HistoryError(LLMException):
    """Error in history management"""
    pass
