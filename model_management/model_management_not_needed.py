"""
Abhikarta LLM Model Management - Core Enums and Constants

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

from enum import Enum


class ModelCapability(Enum):
    """
    Enumeration of standard model capabilities.
    
    These capabilities are used to filter and query models based on their features.
    Use the .value attribute to get the string representation for database queries.
    
    Example:
        >>> capability = ModelCapability.VISION.value
        >>> models = registry.get_all_models_for_capability(capability)
    """
    
    # Core capabilities
    CHAT = "chat"
    COMPLETION = "completion"
    STREAMING = "streaming"
    
    # Advanced capabilities
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"
    TOOL_USE = "tool_use"
    JSON_MODE = "json_mode"
    
    # Embedding capabilities
    EMBEDDING = "embedding"
    DIMENSIONS = "dimensions"
    
    # Specialized capabilities
    CODE_GENERATION = "code_generation"
    MULTIMODAL = "multimodal"
    LONG_CONTEXT = "long_context"
    REASONING = "reasoning"
    
    # Audio/Speech capabilities
    AUDIO_INPUT = "audio_input"
    AUDIO_OUTPUT = "audio_output"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    
    # Image capabilities
    IMAGE_GENERATION = "image_generation"
    IMAGE_EDITING = "image_editing"
    IMAGE_UNDERSTANDING = "image_understanding"
    
    # Document capabilities
    DOCUMENT_PARSING = "document_parsing"
    PDF_SUPPORT = "pdf_support"
    
    # Fine-tuning
    FINE_TUNABLE = "fine_tunable"
    
    def __str__(self) -> str:
        """String representation returns the value."""
        return self.value


class CostUnit(Enum):
    """
    Enumeration of cost calculation units.
    
    Different providers use different pricing scales.
    """
    
    PER_1K_TOKENS = "per_1k"
    PER_1M_TOKENS = "per_1m"
    PER_TOKEN = "per_token"
    PER_REQUEST = "per_request"
    PER_SECOND = "per_second"
    PER_IMAGE = "per_image"
    
    def __str__(self) -> str:
        return self.value


class ModelSize(Enum):
    """
    Enumeration of model size categories.
    """
    
    TINY = "tiny"           # < 1B parameters
    SMALL = "small"         # 1B - 7B parameters
    MEDIUM = "medium"       # 7B - 20B parameters
    LARGE = "large"         # 20B - 100B parameters
    XLARGE = "xlarge"       # 100B+ parameters
    
    def __str__(self) -> str:
        return self.value


class ProviderType(Enum):
    """
    Enumeration of provider types.
    """
    
    CLOUD_API = "cloud_api"
    LOCAL = "local"
    SELF_HOSTED = "self_hosted"
    HYBRID = "hybrid"
    
    def __str__(self) -> str:
        return self.value


# Standard capability aliases for convenience
CHAT_CAPABILITY = ModelCapability.CHAT.value
VISION_CAPABILITY = ModelCapability.VISION.value
FUNCTION_CALLING_CAPABILITY = ModelCapability.FUNCTION_CALLING.value
STREAMING_CAPABILITY = ModelCapability.STREAMING.value
EMBEDDING_CAPABILITY = ModelCapability.EMBEDDING.value


__all__ = [
    'ModelCapability',
    'CostUnit',
    'ModelSize',
    'ProviderType',
    'CHAT_CAPABILITY',
    'VISION_CAPABILITY',
    'FUNCTION_CALLING_CAPABILITY',
    'STREAMING_CAPABILITY',
    'EMBEDDING_CAPABILITY'
]
