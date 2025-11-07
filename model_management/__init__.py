"""
Abhikarta LLM Model Configuration System

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

from enum import Enum, auto
from typing import Dict, List, Optional, Any


class ModelCapability(str, Enum):
    """
    Enumeration of all LLM model capabilities across all supported providers.

    This enum provides a standardized way to query and compare capabilities across
    different LLM providers including Anthropic, OpenAI, Google, Meta, Mistral,
    Cohere, Groq, HuggingFace, Together AI, Replicate, AWS Bedrock, and Ollama.

    Usage:
        >>> from model_management import ModelCapability
        >>> if ModelCapability.VISION in model.capabilities:
        >>>     # Process image input
        >>>     pass
    """

    # ==================================================================================
    # CORE TEXT CAPABILITIES
    # ==================================================================================

    CHAT = "chat"
    """Conversational chat interactions with multi-turn dialogue support."""

    COMPLETION = "completion"
    """Text completion/generation from a prompt."""

    STREAMING = "streaming"
    """Real-time token-by-token streaming of responses via SSE or WebSocket."""

    # ==================================================================================
    # FUNCTION & TOOL CAPABILITIES
    # ==================================================================================

    FUNCTION_CALLING = "function_calling"
    """Ability to call external functions/APIs with structured parameters."""

    TOOL_USE = "tool_use"
    """Advanced tool use and integration with external systems."""

    WEB_SEARCH = "web_search"
    """Built-in web search capabilities for real-time information retrieval."""

    GROUNDING = "grounding"
    """Ground responses in real-time data sources (Google Search, custom data)."""

    GROUNDED_GENERATION = "grounded_generation"
    """Generate responses grounded in provided documents or data sources."""

    # ==================================================================================
    # MULTIMODAL CAPABILITIES
    # ==================================================================================

    VISION = "vision"
    """Image understanding and analysis capabilities."""

    AUDIO_INPUT = "audio_input"
    """Process audio input (speech, sounds, music)."""

    AUDIO_OUTPUT = "audio_output"
    """Generate audio output (speech synthesis, sounds)."""

    VIDEO_INPUT = "video_input"
    """Process and understand video content."""

    MULTIMODAL = "multimodal"
    """General multimodal capabilities (text + image + audio + video)."""

    # ==================================================================================
    # AUDIO PROCESSING CAPABILITIES
    # ==================================================================================

    AUDIO_TRANSCRIPTION = "audio_transcription"
    """Transcribe audio to text (speech-to-text)."""

    AUDIO_TRANSLATION = "audio_translation"
    """Translate audio from one language to another."""

    SPEECH_TO_TEXT = "speech_to_text"
    """Convert spoken language to written text."""

    TEXT_TO_SPEECH = "text_to_speech"
    """Convert written text to spoken language."""

    TRANSCRIPTION = "transcription"
    """General audio transcription capabilities."""

    TRANSLATION = "translation"
    """Language translation capabilities."""

    DIARIZATION = "diarization"
    """Speaker diarization (identify different speakers in audio)."""

    TIMESTAMP = "timestamp"
    """Timestamp generation for transcriptions."""

    WORD_TIMESTAMPS = "word_timestamps"
    """Word-level timestamps in transcriptions."""

    WORD_LEVEL_TIMESTAMPS = "word_level_timestamps"
    """Detailed word-level timing information."""

    VOICES = "voices"
    """Multiple voice options for text-to-speech."""

    AUDIO_GENERATION = "audio_generation"
    """Generate audio content (music, sound effects)."""

    # ==================================================================================
    # IMAGE CAPABILITIES
    # ==================================================================================

    IMAGE_GENERATION = "image_generation"
    """Generate images from text descriptions."""

    IMAGE_EDITING = "image_editing"
    """Edit existing images based on instructions."""

    IMAGE_VARIATIONS = "image_variations"
    """Create variations of existing images."""

    IMAGE_CAPTIONING = "image_captioning"
    """Generate captions/descriptions for images."""

    IMAGE_ENHANCEMENT = "image_enhancement"
    """Enhance image quality, resolution, or characteristics."""

    INPAINTING = "inpainting"
    """Fill in masked areas of images."""

    OUTPAINTING = "outpainting"
    """Extend images beyond their original boundaries."""

    UPSCALING = "upscaling"
    """Increase image resolution while maintaining quality."""

    BACKGROUND_REMOVAL = "background_removal"
    """Remove backgrounds from images."""

    ASPECT_RATIOS = "aspect_ratios"
    """Support for multiple aspect ratios in image generation."""

    # ==================================================================================
    # VIDEO CAPABILITIES
    # ==================================================================================

    VIDEO_GENERATION = "video_generation"
    """Generate video content from text or images."""

    # ==================================================================================
    # CODE CAPABILITIES
    # ==================================================================================

    CODE_EXECUTION = "code_execution"
    """Execute code (Python, etc.) within the model context."""

    FILL_IN_MIDDLE = "fill_in_middle"
    """Fill in middle sections of code (code completion at cursor position)."""

    # ==================================================================================
    # REASONING & THINKING CAPABILITIES
    # ==================================================================================

    EXTENDED_THINKING = "extended_thinking"
    """Extended reasoning with visible thinking process (Claude 3.7, O1)."""

    THINKING_MODE = "thinking_mode"
    """Special thinking mode for complex problem-solving."""

    # ==================================================================================
    # STRUCTURED OUTPUT CAPABILITIES
    # ==================================================================================

    JSON_MODE = "json_mode"
    """Guarantee valid JSON output with schema validation."""

    # ==================================================================================
    # OPTIMIZATION CAPABILITIES
    # ==================================================================================

    PROMPT_CACHING = "prompt_caching"
    """Cache repeated context for cost and latency reduction."""

    CACHING = "caching"
    """General caching capabilities."""

    BATCH_API = "batch_api"
    """Asynchronous batch processing for high-volume requests."""

    QUANTIZATION = "quantization"
    """Support for quantized models (GPTQ, AWQ, GGUF) for efficiency."""

    # ==================================================================================
    # EMBEDDING CAPABILITIES
    # ==================================================================================

    EMBEDDINGS = "embeddings"
    """Generate vector embeddings for semantic search and similarity."""

    EMBEDDING = "embedding"
    """General embedding generation capability."""

    DIMENSIONS = "dimensions"
    """Embedding dimension size (metadata, not boolean)."""

    EMBEDDING_TYPES = "embedding_types"
    """Multiple embedding types (search, classification, clustering)."""

    # ==================================================================================
    # SEARCH & RETRIEVAL CAPABILITIES
    # ==================================================================================

    RERANKING = "reranking"
    """Rerank search results for improved relevance."""

    RELEVANCE_SCORING = "relevance_scoring"
    """Score document relevance for search queries."""

    QUESTION_ANSWERING = "question_answering"
    """Answer questions based on provided context."""

    # ==================================================================================
    # SAFETY & MODERATION CAPABILITIES
    # ==================================================================================

    MODERATION = "moderation"
    """Content moderation and safety filtering."""

    GUARDRAILS = "guardrails"
    """Configurable safety guardrails for enterprise deployment."""

    CATEGORIES = "categories"
    """Moderation categories (hate, violence, sexual, etc.)."""

    # ==================================================================================
    # CUSTOMIZATION CAPABILITIES
    # ==================================================================================

    FINE_TUNING = "fine_tuning"
    """Support for fine-tuning on custom datasets."""

    TUNING = "tuning"
    """General model tuning and customization."""

    # ==================================================================================
    # CITATION & ATTRIBUTION CAPABILITIES
    # ==================================================================================

    CITATIONS = "citations"
    """Provide citations for generated content."""

    ATTRIBUTION = "attribution"
    """Source attribution for information."""

    # ==================================================================================
    # DOCUMENT PROCESSING CAPABILITIES
    # ==================================================================================

    MAX_DOCUMENTS = "max_documents"
    """Maximum number of documents that can be processed (metadata)."""

    # ==================================================================================
    # LANGUAGE CAPABILITIES
    # ==================================================================================

    LANGUAGES = "languages"
    """Supported languages (metadata, not boolean)."""

    # ==================================================================================
    # TASK TYPE CAPABILITIES
    # ==================================================================================

    TASK_TYPES = "task_types"
    """Supported task types (metadata, not boolean)."""

    # ==================================================================================
    # PROMPT CAPABILITIES
    # ==================================================================================

    PROMPT_GENERATION = "prompt_generation"
    """Generate optimized prompts for specific tasks."""

    # ==================================================================================
    # STATUS CAPABILITIES
    # ==================================================================================

    DEPRECATED = "deprecated"
    """Model is deprecated and may be removed (status flag)."""

    @classmethod
    def get_core_capabilities(cls) -> List['ModelCapability']:
        """
        Get list of core text-based capabilities.

        Returns:
            List of core capability enums (chat, completion, streaming)
        """
        return [
            cls.CHAT,
            cls.COMPLETION,
            cls.STREAMING
        ]

    @classmethod
    def get_multimodal_capabilities(cls) -> List['ModelCapability']:
        """
        Get list of multimodal capabilities.

        Returns:
            List of multimodal capability enums (vision, audio, video)
        """
        return [
            cls.VISION,
            cls.AUDIO_INPUT,
            cls.AUDIO_OUTPUT,
            cls.VIDEO_INPUT,
            cls.MULTIMODAL
        ]

    @classmethod
    def get_tool_capabilities(cls) -> List['ModelCapability']:
        """
        Get list of tool and function calling capabilities.

        Returns:
            List of tool-related capability enums
        """
        return [
            cls.FUNCTION_CALLING,
            cls.TOOL_USE,
            cls.WEB_SEARCH,
            cls.GROUNDING,
            cls.GROUNDED_GENERATION
        ]

    @classmethod
    def get_optimization_capabilities(cls) -> List['ModelCapability']:
        """
        Get list of performance optimization capabilities.

        Returns:
            List of optimization capability enums
        """
        return [
            cls.PROMPT_CACHING,
            cls.CACHING,
            cls.BATCH_API,
            cls.QUANTIZATION
        ]

    @classmethod
    def get_reasoning_capabilities(cls) -> List['ModelCapability']:
        """
        Get list of advanced reasoning capabilities.

        Returns:
            List of reasoning capability enums
        """
        return [
            cls.EXTENDED_THINKING,
            cls.THINKING_MODE
        ]

    @classmethod
    def get_audio_capabilities(cls) -> List['ModelCapability']:
        """
        Get list of audio processing capabilities.

        Returns:
            List of audio-related capability enums
        """
        return [
            cls.AUDIO_INPUT,
            cls.AUDIO_OUTPUT,
            cls.AUDIO_TRANSCRIPTION,
            cls.AUDIO_TRANSLATION,
            cls.SPEECH_TO_TEXT,
            cls.TEXT_TO_SPEECH,
            cls.TRANSCRIPTION,
            cls.TRANSLATION,
            cls.DIARIZATION,
            cls.AUDIO_GENERATION
        ]

    @classmethod
    def get_image_capabilities(cls) -> List['ModelCapability']:
        """
        Get list of image processing capabilities.

        Returns:
            List of image-related capability enums
        """
        return [
            cls.IMAGE_GENERATION,
            cls.IMAGE_EDITING,
            cls.IMAGE_VARIATIONS,
            cls.IMAGE_CAPTIONING,
            cls.IMAGE_ENHANCEMENT,
            cls.INPAINTING,
            cls.OUTPAINTING,
            cls.UPSCALING,
            cls.BACKGROUND_REMOVAL
        ]

    @classmethod
    def get_embedding_capabilities(cls) -> List['ModelCapability']:
        """
        Get list of embedding capabilities.

        Returns:
            List of embedding-related capability enums
        """
        return [
            cls.EMBEDDINGS,
            cls.EMBEDDING,
            cls.RERANKING,
            cls.RELEVANCE_SCORING
        ]

    @classmethod
    def is_metadata_field(cls, capability: 'ModelCapability') -> bool:
        """
        Check if a capability is a metadata field rather than a boolean capability.

        Args:
            capability: The capability to check

        Returns:
            True if the capability is metadata (not boolean)
        """
        metadata_fields = {
            cls.DIMENSIONS,
            cls.EMBEDDING_TYPES,
            cls.MAX_DOCUMENTS,
            cls.LANGUAGES,
            cls.TASK_TYPES,
            cls.ASPECT_RATIOS,
            cls.VOICES,
            cls.CATEGORIES
        }
        return capability in metadata_fields


class ProviderType(str, Enum):
    """
    Enumeration of supported LLM providers.
    """

    ANTHROPIC = "anthropic"
    """Anthropic (Claude models)"""

    OPENAI = "openai"
    """OpenAI (GPT models)"""

    GOOGLE = "google"
    """Google (Gemini models)"""

    META = "meta"
    """Meta (Llama models via various platforms)"""

    MISTRAL = "mistral"
    """Mistral AI"""

    COHERE = "cohere"
    """Cohere"""

    GROQ = "groq"
    """Groq (LPU-accelerated inference)"""

    HUGGINGFACE = "huggingface"
    """HuggingFace (open-source models)"""

    TOGETHER = "together"
    """Together AI"""

    REPLICATE = "replicate"
    """Replicate"""

    AWS_BEDROCK = "awsbedrock"
    """AWS Bedrock"""

    OLLAMA = "ollama"
    """Ollama (local deployment)"""

    MOCK = "mock"
    """Mock provider for testing"""


# Version information
__version__ = "1.0.0"
__author__ = "Ashutosh Sinha"
__email__ = "ajsinha@gmail.com"
__copyright__ = "Copyright © 2025-2030, All Rights Reserved"

# Export public API
__all__ = [
    "ModelCapability",
    "ProviderType",
    "__version__",
    "__author__",
    "__email__",
    "__copyright__"
]