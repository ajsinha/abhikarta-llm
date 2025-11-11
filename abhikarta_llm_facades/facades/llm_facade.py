"""
Abhikarta LLM Facade - Unified Interface for Language Models

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

Description:
This module defines the LLMFacade abstract base class, which provides a unified,
provider-agnostic interface for interacting with Large Language Models from various
providers including OpenAI, Anthropic, Hugging Face, Cohere, Google, Meta, and others.

The facade pattern ensures that client code remains decoupled from specific provider
implementations, allowing for seamless provider switching and consistent API usage.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Iterator, AsyncIterator, Tuple, Callable
from enum import Enum
from dataclasses import dataclass
from PIL.Image import Image
import io

# ============================================================================
# Type Definitions and Data Classes
# ============================================================================

# Core message types
Messages = List[Dict[str, Any]]  # [{"role": "user"|"assistant"|"system", "content": str|List[dict]}]
TextStream = Union[Iterator[str], AsyncIterator[str]]
DeltaStream = Union[Iterator[Dict[str, Any]], AsyncIterator[Dict[str, Any]]]

# Tool/Function calling types
ToolDefinition = Dict[str, Any]  # JSON Schema for function definition
ToolCall = Dict[str, Any]  # {"id": str, "type": "function", "function": {"name": str, "arguments": str}}
ToolResult = Dict[str, Any]  # {"tool_call_id": str, "output": Any}

# Document and retrieval types
Document = Dict[str, Any]  # {"id": str, "content": str, "metadata": dict, "score": float}
RetrievalResult = List[Tuple[Document, float]]  # List of (document, similarity_score)
Embedding = List[float]  # Dense vector representation

# Image types
ImageInput = Union[Image, bytes, str]  # PIL Image, raw bytes, file path, or URL
ImageOutput = Union[Image, bytes, str]  # Generated image output

# Safety and moderation types
ModerationResult = Dict[str, Any]  # {"flagged": bool, "categories": dict, "scores": dict}
SafetyResult = Dict[str, Any]  # {"safe": bool, "categories": List[str], "severity": str}


class ModelCapability(Enum):
    """Enumeration of LLM capabilities."""
    TEXT_GENERATION = "text_generation"
    CHAT_COMPLETION = "chat_completion"
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"
    TOOL_USE = "tool_use"
    JSON_MODE = "json_mode"
    STRUCTURED_OUTPUT = "structured_output"
    CODE_GENERATION = "code_generation"
    CODE_INTERPRETATION = "code_interpretation"
    EMBEDDINGS = "embeddings"
    IMAGE_GENERATION = "image_generation"
    IMAGE_UNDERSTANDING = "image_understanding"
    IMAGE_EDITING = "image_editing"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    AUDIO_GENERATION = "audio_generation"
    VIDEO_UNDERSTANDING = "video_understanding"
    STREAMING = "streaming"
    FINE_TUNING = "fine_tuning"
    RAG = "rag"
    AGENTS = "agents"
    MULTIMODAL = "multimodal"
    REASONING = "reasoning"
    SEARCH = "search"


class ResponseFormat(Enum):
    """Output format specifications."""
    TEXT = "text"
    JSON = "json_object"
    JSON_SCHEMA = "json_schema"
    MARKDOWN = "markdown"
    HTML = "html"
    CODE = "code"


class SafetyLevel(Enum):
    """Safety filtering levels."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    STRICT = "strict"


@dataclass
class GenerationConfig:
    """Configuration for text generation parameters."""
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    repetition_penalty: Optional[float] = None
    stop_sequences: Optional[List[str]] = None
    seed: Optional[int] = None
    response_format: Optional[ResponseFormat] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class TokenUsage:
    """Token usage statistics for a request."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cached_tokens: Optional[int] = None

    @property
    def cost(self) -> Optional[float]:
        """Calculate cost if pricing info available."""
        return None  # Implemented by concrete classes


@dataclass
class CompletionMetadata:
    """Metadata about a completion request."""
    model: str
    created_at: Optional[str] = None
    finish_reason: Optional[str] = None  # "stop", "length", "tool_calls", "content_filter"
    usage: Optional[TokenUsage] = None
    latency_ms: Optional[float] = None
    provider_metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# LLMFacade Abstract Base Class
# ============================================================================

class LLMFacade(ABC):
    """
    Abstract base class defining a unified, provider-agnostic interface for LLM operations.

    This facade provides a consistent API across different LLM providers including:
    - OpenAI (GPT-4, GPT-3.5)
    - Anthropic (Claude 3 Family)
    - Google (Gemini, PaLM)
    - Meta (Llama 2, Llama 3)
    - Cohere (Command, Command-R)
    - Mistral (Mixtral, Mistral)
    - Hugging Face (Various open models)
    - Local models (via TGI, vLLM, Ollama)

    Design Principles:
    1. Provider Agnostic: All methods work identically regardless of underlying provider
    2. Capability Discovery: Models expose their capabilities for runtime decisions
    3. Graceful Degradation: Methods fail gracefully when features unsupported
    4. Consistent Error Handling: Standardized exceptions across providers
    5. Async Support: Full async/await support for all operations
    6. Streaming First: Native support for streaming responses
    7. Type Safety: Comprehensive type hints for better IDE support

    Usage Example:
        >>> # Client code remains identical across providers
        >>> llm: LLMFacade = get_llm_instance("anthropic", "claude-3-opus")
        >>> response = llm.chat_completion([
        ...     {"role": "user", "content": "Explain quantum computing"}
        ... ])
        >>> print(response["content"])
    """

    # ========================================================================
    # Lifecycle and Configuration
    # ========================================================================

    @abstractmethod
    def __init__(
            self,
            model_name: str,
            api_key: Optional[str] = None,
            base_url: Optional[str] = None,
            timeout: Optional[float] = None,
            max_retries: int = 3,
            **kwargs
    ) -> None:
        """
        Initialize the LLM facade instance.

        Args:
            model_name: Identifier for the specific model (e.g., "gpt-4", "claude-3-opus")
            api_key: API key for authentication (reads from env if None)
            base_url: Custom API endpoint URL (uses default if None)
            timeout: Request timeout in seconds (default: 60)
            max_retries: Number of retry attempts for failed requests
            **kwargs: Provider-specific configuration
                - organization_id: OpenAI organization ID
                - project_id: Google Cloud project ID
                - region: Geographic region for API calls
                - model_version: Specific model version/checkpoint
                - quantization: Model quantization level for local models
                - device: Computation device (cpu, cuda, mps)
                - cache_dir: Directory for model caching
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> List[ModelCapability]:
        """
        Get list of capabilities supported by this model.

        Returns:
            List of ModelCapability enum values indicating supported features

        Example:
            >>> caps = llm.get_capabilities()
            >>> if ModelCapability.VISION in caps:
            ...     llm.chat_completion_with_vision(messages, images)
        """
        pass

    @abstractmethod
    def supports_capability(self, capability: ModelCapability) -> bool:
        """
        Check if model supports a specific capability.

        Args:
            capability: The capability to check

        Returns:
            True if capability is supported, False otherwise
        """
        pass

    # ========================================================================
    # Core Text Generation
    # ========================================================================

    @abstractmethod
    def text_generation(
            self,
            prompt: str,
            *,
            config: Optional[GenerationConfig] = None,
            stream: bool = False,
            **kwargs
    ) -> Union[str, Iterator[str], Dict[str, Any]]:
        """
        Generate text continuation from a raw prompt (completion mode).

        This method is for raw text completion without chat formatting. Use
        chat_completion() for conversational interactions.

        Args:
            prompt: The input text to complete
            config: Generation configuration object
            stream: If True, returns iterator yielding chunks
            **kwargs: Additional provider-specific parameters
                - logprobs: Return log probabilities (OpenAI)
                - echo: Include prompt in output (OpenAI)
                - best_of: Generate N completions and return best (OpenAI)
                - logit_bias: Token bias dictionary (OpenAI)
                - user: End-user identifier for monitoring

        Returns:
            If stream=False: String with generated text or dict with full response
            If stream=True: Iterator yielding text chunks

        Raises:
            ModelNotSupportedException: If text generation not supported
            RateLimitException: If rate limit exceeded
            ContentFilterException: If content blocked by safety filters

        Example:
            >>> response = llm.text_generation(
            ...     "Once upon a time",
            ...     config=GenerationConfig(max_tokens=100, temperature=0.7)
            ... )
            >>> print(response)
        """
        pass

    @abstractmethod
    def chat_completion(
            self,
            messages: Messages,
            *,
            config: Optional[GenerationConfig] = None,
            stream: bool = False,
            tools: Optional[List[ToolDefinition]] = None,
            tool_choice: Optional[Union[str, Dict]] = None,
            parallel_tool_calls: bool = True,
            **kwargs
    ) -> Union[Dict[str, Any], DeltaStream]:
        """
        Perform structured multi-turn chat with optional function/tool calling.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
                Roles: "system", "user", "assistant", "tool"
                Content: String or list of content parts (text, images, etc.)
            config: Generation configuration
            stream: Return streaming iterator of deltas
            tools: List of tool/function definitions (JSON Schema format)
            tool_choice: Control tool selection:
                - "auto": Model decides whether to call tools
                - "none": Never call tools
                - "required": Must call at least one tool
                - {"type": "function", "function": {"name": "my_func"}}: Force specific tool
            parallel_tool_calls: Allow multiple simultaneous tool calls
            **kwargs: Additional parameters
                - response_format: Specify output format (text, json_object, json_schema)
                - metadata: Arbitrary metadata for tracking
                - user: End-user identifier

        Returns:
            If stream=False: Dictionary with:
                - content: String with assistant's response
                - role: "assistant"
                - tool_calls: List of tool call objects (if any)
                - finish_reason: Why generation stopped
                - usage: Token usage statistics
                - metadata: Completion metadata
            If stream=True: Iterator yielding delta dictionaries

        Example:
            >>> response = llm.chat_completion([
            ...     {"role": "system", "content": "You are a helpful assistant."},
            ...     {"role": "user", "content": "What's the weather in London?"}
            ... ], tools=[weather_tool])
            >>>
            >>> if response.get("tool_calls"):
            ...     # Handle tool calls
            ...     for tool_call in response["tool_calls"]:
            ...         result = execute_tool(tool_call)
        """
        pass

    @abstractmethod
    def chat_completion_with_vision(
            self,
            messages: Messages,
            images: Union[ImageInput, List[ImageInput]],
            *,
            config: Optional[GenerationConfig] = None,
            image_detail: str = "auto",  # "low", "high", "auto"
            **kwargs
    ) -> Dict[str, Any]:
        """
        Chat completion with image understanding (multimodal).

        Args:
            messages: Conversation messages
            images: Single image or list of images to analyze
            config: Generation configuration
            image_detail: Level of detail for image processing
            **kwargs: Additional parameters

        Returns:
            Response dictionary similar to chat_completion

        Raises:
            CapabilityNotSupportedException: If vision not supported

        Example:
            >>> with open("chart.png", "rb") as f:
            ...     img_bytes = f.read()
            >>> response = llm.chat_completion_with_vision(
            ...     messages=[{"role": "user", "content": "Analyze this chart"}],
            ...     images=img_bytes
            ... )
        """
        pass

    # ========================================================================
    # Streaming Methods
    # ========================================================================

    @abstractmethod
    def stream_text_generation(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Stream text generation chunks in real-time.

        Convenience method that calls text_generation(..., stream=True).

        Args:
            prompt: Input text
            **kwargs: Same as text_generation

        Returns:
            Iterator yielding text chunks as they are generated

        Example:
            >>> for chunk in llm.stream_text_generation("Write a story"):
            ...     print(chunk, end="", flush=True)
        """
        pass

    @abstractmethod
    def stream_chat_completion(
            self,
            messages: Messages,
            **kwargs
    ) -> Iterator[Dict[str, Any]]:
        """
        Stream chat completion deltas in real-time.

        Convenience method that calls chat_completion(..., stream=True).

        Args:
            messages: Conversation messages
            **kwargs: Same as chat_completion

        Returns:
            Iterator yielding delta dictionaries with:
                - delta: Incremental content or tool call info
                - finish_reason: Set when stream complete (if applicable)

        Example:
            >>> for delta in llm.stream_chat_completion(messages):
            ...     if "content" in delta.get("delta", {}):
            ...         print(delta["delta"]["content"], end="")
        """
        pass

    # ========================================================================
    # Async Variants
    # ========================================================================

    @abstractmethod
    async def atext_generation(
            self,
            prompt: str,
            **kwargs
    ) -> Union[str, AsyncIterator[str], Dict[str, Any]]:
        """
        Asynchronous text generation.

        Args:
            prompt: Input text
            **kwargs: Same as text_generation (including stream parameter)

        Returns:
            String, full response dict, or async iterator if streaming
        """
        pass

    @abstractmethod
    async def achat_completion(
            self,
            messages: Messages,
            **kwargs
    ) -> Union[Dict[str, Any], AsyncIterator[Dict[str, Any]]]:
        """
        Asynchronous chat completion.

        Args:
            messages: Conversation messages
            **kwargs: Same as chat_completion

        Returns:
            Response dictionary or async iterator if streaming
        """
        pass

    @abstractmethod
    async def achat_completion_with_vision(
            self,
            messages: Messages,
            images: Union[ImageInput, List[ImageInput]],
            **kwargs
    ) -> Dict[str, Any]:
        """
        Asynchronous multimodal chat completion.

        Args:
            messages: Conversation messages
            images: Images to analyze
            **kwargs: Same as chat_completion_with_vision

        Returns:
            Response dictionary
        """
        pass

    # ========================================================================
    # Retrieval Augmented Generation (RAG)
    # ========================================================================

    @abstractmethod
    def retrieve_documents(
            self,
            query: str,
            *,
            top_k: int = 5,
            filter: Optional[Dict[str, Any]] = None,
            score_threshold: Optional[float] = None,
            vector_store: Optional[Any] = None,
            rerank: bool = False,
            **kwargs
    ) -> RetrievalResult:
        """
        Retrieve relevant documents from vector store for RAG.

        Args:
            query: Search query (natural language or embedding)
            top_k: Number of documents to retrieve
            filter: Metadata filters (e.g., {"source": "docs", "date": {"$gt": "2023"}})
            score_threshold: Minimum similarity threshold (0.0-1.0)
            vector_store: Optional explicit vector store instance
            rerank: Apply reranking for improved relevance
            **kwargs: Additional retrieval parameters
                - hybrid_search: Combine dense and sparse retrieval
                - mmr: Use maximal marginal relevance for diversity
                - fetch_k: Number of candidates for MMR
                - lambda_mult: MMR diversity parameter

        Returns:
            List of (document, score) tuples sorted by relevance

        Example:
            >>> docs = llm.retrieve_documents(
            ...     "What is machine learning?",
            ...     top_k=3,
            ...     filter={"category": "AI"}
            ... )
            >>> for doc, score in docs:
            ...     print(f"{score:.3f}: {doc['content'][:100]}")
        """
        pass

    @abstractmethod
    def rag_chat(
            self,
            messages: Messages,
            *,
            retrieval_top_k: int = 5,
            retrieval_filter: Optional[Dict] = None,
            context_template: Optional[str] = None,
            include_sources: bool = True,
            citation_style: str = "inline",  # "inline", "footnote", "end"
            config: Optional[GenerationConfig] = None,
            stream: bool = False,
            vector_store: Optional[Any] = None,
            **kwargs
    ) -> Union[Dict[str, Any], Iterator[Dict[str, Any]]]:
        """
        RAG-augmented chat: retrieve relevant context, then generate response.

        Process:
        1. Extract query from last user message
        2. Retrieve relevant documents from vector store
        3. Inject context into prompt
        4. Generate response with context awareness
        5. Optionally include source citations

        Args:
            messages: Conversation history
            retrieval_top_k: Number of documents to retrieve
            retrieval_filter: Metadata filtering for retrieval
            context_template: Custom template for context injection
                Default: "Here is relevant context:\n\n{context}\n\nQuestion: {query}"
            include_sources: Include retrieved document sources in response
            citation_style: How to format citations
            config: Generation configuration
            stream: Stream the response
            vector_store: Explicit vector store instance
            **kwargs: Additional parameters
                - compression: Apply context compression
                - max_context_tokens: Limit context token count
                - rerank: Rerank retrieved documents

        Returns:
            Dictionary with:
                - content: Generated response
                - sources: List of source documents (if include_sources=True)
                - retrieved_docs: Full retrieved document details
                - metadata: Generation metadata

        Example:
            >>> response = llm.rag_chat(
            ...     messages=[
            ...         {"role": "user", "content": "What are the benefits of solar energy?"}
            ...     ],
            ...     retrieval_top_k=5,
            ...     include_sources=True
            ... )
            >>> print(response["content"])
            >>> print("\nSources:", response["sources"])
        """
        pass

    @abstractmethod
    def rag_generate(
            self,
            query: str,
            *,
            system_prompt: Optional[str] = None,
            retrieval_top_k: int = 5,
            context_template: Optional[str] = None,
            include_sources: bool = True,
            config: Optional[GenerationConfig] = None,
            stream: bool = False,
            vector_store: Optional[Any] = None,
            **kwargs
    ) -> Union[str, Dict[str, Any], Iterator[str]]:
        """
        RAG for single-turn generation (non-chat, completion mode).

        Args:
            query: User question or prompt
            system_prompt: System instruction for generation
            retrieval_top_k: Documents to retrieve
            context_template: Template for context injection
            include_sources: Include source information
            config: Generation configuration
            stream: Stream the output
            vector_store: Vector store instance
            **kwargs: Additional parameters

        Returns:
            Generated text string, full response dict, or iterator

        Example:
            >>> answer = llm.rag_generate(
            ...     "Explain photosynthesis",
            ...     retrieval_top_k=3,
            ...     system_prompt="Explain concepts clearly for a high school student"
            ... )
        """
        pass

    # ========================================================================
    # Function/Tool Calling
    # ========================================================================

    @abstractmethod
    def create_tool_definition(
            self,
            name: str,
            description: str,
            parameters: Dict[str, Any],
            required: Optional[List[str]] = None
    ) -> ToolDefinition:
        """
        Create a standardized tool definition in provider's expected format.

        Args:
            name: Function name (snake_case recommended)
            description: Clear description of what the function does
            parameters: JSON Schema describing function parameters
            required: List of required parameter names

        Returns:
            Tool definition dictionary in provider-specific format

        Example:
            >>> tool = llm.create_tool_definition(
            ...     name="get_weather",
            ...     description="Get current weather for a location",
            ...     parameters={
            ...         "type": "object",
            ...         "properties": {
            ...             "location": {"type": "string", "description": "City name"},
            ...             "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            ...         }
            ...     },
            ...     required=["location"]
            ... )
        """
        pass

    @abstractmethod
    def call_tool(
            self,
            tool_call: ToolCall,
            available_tools: Dict[str, Callable],
            **kwargs
    ) -> ToolResult:
        """
        Execute a tool/function requested by the LLM.

        Args:
            tool_call: Tool call object from LLM response with:
                - id: Unique identifier for this tool call
                - type: "function"
                - function: {"name": str, "arguments": str (JSON)}
            available_tools: Mapping of tool names to callable functions
            **kwargs: Additional execution parameters
                - timeout: Maximum execution time
                - sandbox: Execute in sandboxed environment

        Returns:
            Tool result dictionary with:
                - tool_call_id: ID from the tool call
                - output: Result of the function execution (any type)
                - error: Error message if execution failed

        Raises:
            ToolNotFoundException: If requested tool not in available_tools
            ToolExecutionException: If tool execution fails

        Example:
            >>> def get_weather(location: str, unit: str = "celsius") -> dict:
            ...     return {"temp": 22, "condition": "sunny"}
            >>>
            >>> tools = {"get_weather": get_weather}
            >>> result = llm.call_tool(tool_call, tools)
        """
        pass

    @abstractmethod
    def execute_tool_loop(
            self,
            messages: Messages,
            tools: List[ToolDefinition],
            available_tools: Dict[str, Callable],
            max_iterations: int = 5,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Execute automatic tool-calling loop until completion.

        This method handles the complete agentic loop:
        1. Send messages to LLM with available tools
        2. If LLM requests tool calls, execute them
        3. Add tool results to conversation
        4. Repeat until LLM provides final answer (no tool calls)
        5. Return final response

        Args:
            messages: Initial conversation messages
            tools: List of available tool definitions
            available_tools: Mapping of tool names to implementations
            max_iterations: Maximum number of tool-calling rounds
            **kwargs: Configuration parameters
                - allow_parallel_calls: Execute multiple tool calls in parallel
                - on_tool_call: Callback function(tool_call, result)
                - on_iteration: Callback function(iteration, messages)

        Returns:
            Final response dictionary with complete conversation history

        Example:
            >>> response = llm.execute_tool_loop(
            ...     messages=[{"role": "user", "content": "Book a flight to Tokyo"}],
            ...     tools=[search_flights, book_flight, confirm_booking],
            ...     available_tools={"search_flights": search_fn, ...}
            ... )
        """
        pass

    # ========================================================================
    # Embeddings
    # ========================================================================

    @abstractmethod
    def embed_text(
            self,
            texts: Union[str, List[str]],
            *,
            normalize: bool = True,
            embedding_type: str = "document",  # "document", "query"
            truncate: bool = True,
            **kwargs
    ) -> Union[Embedding, List[Embedding]]:
        """
        Generate dense vector embeddings for text.

        Args:
            texts: Single string or list of strings to embed
            normalize: L2-normalize vectors to unit length
            embedding_type: Optimize for "document" or "query" embeddings
            truncate: Truncate text exceeding max length vs raising error
            **kwargs: Provider-specific parameters
                - dimensions: Output dimensionality (if model supports it)
                - encoding_format: "float" or "base64"

        Returns:
            Single embedding list if input is string, else list of embeddings

        Example:
            >>> embeddings = llm.embed_text([
            ...     "Machine learning is a subset of AI",
            ...     "Deep learning uses neural networks"
            ... ])
            >>> # Compute similarity
            >>> import numpy as np
            >>> similarity = np.dot(embeddings[0], embeddings[1])
        """
        pass

    @abstractmethod
    def embed_image(
            self,
            images: Union[ImageInput, List[ImageInput]],
            *,
            normalize: bool = True,
            **kwargs
    ) -> Union[Embedding, List[Embedding]]:
        """
        Generate embeddings for images (multimodal embedding models).

        Args:
            images: Single image or list of images
            normalize: L2-normalize vectors
            **kwargs: Additional parameters
                - resize: Resize images to specific dimensions
                - preprocess: Apply preprocessing

        Returns:
            Single embedding or list of embeddings

        Raises:
            CapabilityNotSupportedException: If image embeddings not supported

        Example:
            >>> img_embedding = llm.embed_image("product.jpg")
            >>> text_embedding = llm.embed_text("blue running shoes")
            >>> # Cross-modal similarity
            >>> similarity = np.dot(img_embedding, text_embedding)
        """
        pass

    @abstractmethod
    def compute_similarity(
            self,
            embedding1: Embedding,
            embedding2: Embedding,
            metric: str = "cosine"  # "cosine", "dot", "euclidean"
    ) -> float:
        """
        Compute similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            metric: Similarity metric to use

        Returns:
            Similarity score (interpretation depends on metric)

        Example:
            >>> emb1 = llm.embed_text("cat")
            >>> emb2 = llm.embed_text("kitten")
            >>> similarity = llm.compute_similarity(emb1, emb2)
            >>> print(f"Similarity: {similarity:.3f}")
        """
        pass

    # ========================================================================
    # Image Generation and Manipulation
    # ========================================================================

    @abstractmethod
    def image_generation(
            self,
            prompt: str,
            *,
            negative_prompt: Optional[str] = None,
            size: str = "1024x1024",
            quality: str = "standard",  # "standard", "hd"
            style: str = "natural",  # "natural", "vivid"
            n: int = 1,
            **kwargs
    ) -> Union[ImageOutput, List[ImageOutput]]:
        """
        Generate images from text prompts (text-to-image).

        Args:
            prompt: Text description of desired image
            negative_prompt: Elements to avoid in generation
            size: Image dimensions (e.g., "512x512", "1024x1024", "1024x1792")
            quality: Generation quality level
            style: Visual style preference
            n: Number of images to generate
            **kwargs: Provider-specific parameters
                - steps: Number of diffusion steps
                - guidance_scale: Prompt adherence strength
                - seed: Random seed for reproducibility
                - scheduler: Diffusion scheduler algorithm

        Returns:
            Single Image/bytes or list if n>1

        Raises:
            CapabilityNotSupportedException: If image generation not supported

        Example:
            >>> image = llm.image_generation(
            ...     "A serene mountain landscape at sunset",
            ...     negative_prompt="people, buildings",
            ...     size="1024x1024",
            ...     quality="hd"
            ... )
        """
        pass

    @abstractmethod
    def image_editing(
            self,
            image: ImageInput,
            prompt: str,
            *,
            mask: Optional[ImageInput] = None,
            **kwargs
    ) -> ImageOutput:
        """
        Edit an image based on text instructions (image-to-image with prompt).

        Args:
            image: Source image to edit
            prompt: Editing instructions
            mask: Optional mask indicating areas to edit (white = edit, black = preserve)
            **kwargs: Additional parameters
                - strength: How much to transform (0.0-1.0)
                - guidance_scale: Prompt adherence

        Returns:
            Edited image

        Example:
            >>> edited = llm.image_editing(
            ...     image="photo.jpg",
            ...     prompt="Change the sky to sunset colors",
            ...     mask="sky_mask.png"
            ... )
        """
        pass

    @abstractmethod
    def image_variation(
            self,
            image: ImageInput,
            n: int = 1,
            **kwargs
    ) -> Union[ImageOutput, List[ImageOutput]]:
        """
        Generate variations of an existing image.

        Args:
            image: Source image
            n: Number of variations
            **kwargs: Additional parameters

        Returns:
            Single image or list of variations
        """
        pass

    @abstractmethod
    def image_captioning(
            self,
            image: ImageInput,
            *,
            max_length: Optional[int] = None,
            style: str = "descriptive",  # "descriptive", "brief", "detailed"
            **kwargs
    ) -> str:
        """
        Generate natural language caption/description for an image.

        Args:
            image: Input image
            max_length: Maximum caption length in tokens
            style: Caption style preference
            **kwargs: Additional parameters

        Returns:
            Text description of the image

        Example:
            >>> caption = llm.image_captioning("vacation.jpg")
            >>> print(caption)
            "A sunny beach with palm trees and crystal clear water"
        """
        pass

    # ========================================================================
    # Audio Processing
    # ========================================================================

    @abstractmethod
    def audio_transcription(
            self,
            audio: Union[bytes, str],
            *,
            language: Optional[str] = None,
            prompt: Optional[str] = None,
            response_format: str = "text",  # "text", "json", "verbose_json", "srt", "vtt"
            temperature: Optional[float] = None,
            **kwargs
    ) -> Union[str, Dict[str, Any]]:
        """
        Transcribe audio to text (speech-to-text).

        Args:
            audio: Audio file path, bytes, or URL
            language: ISO-639-1 language code (e.g., "en", "es")
            prompt: Optional context to improve accuracy
            response_format: Output format
            temperature: Sampling temperature (0.0-1.0)
            **kwargs: Additional parameters
                - timestamps: Include word-level timestamps
                - word_timestamps: Include per-word timing

        Returns:
            Transcribed text string or detailed dictionary

        Example:
            >>> text = llm.audio_transcription(
            ...     "meeting_recording.mp3",
            ...     language="en"
            ... )
        """
        pass

    @abstractmethod
    def audio_translation(
            self,
            audio: Union[bytes, str],
            target_language: str = "en",
            **kwargs
    ) -> str:
        """
        Translate audio from any language to target language.

        Args:
            audio: Audio file path, bytes, or URL
            target_language: Target language code
            **kwargs: Additional parameters

        Returns:
            Translated text
        """
        pass

    # ========================================================================
    # Code Generation and Analysis
    # ========================================================================

    @abstractmethod
    def code_generation(
            self,
            description: str,
            *,
            language: Optional[str] = None,
            framework: Optional[str] = None,
            style_guide: Optional[str] = None,
            include_tests: bool = False,
            include_docs: bool = False,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Generate code from natural language description.

        Args:
            description: Natural language description of desired code
            language: Programming language (auto-detected if None)
            framework: Specific framework/library to use
            style_guide: Code style to follow (e.g., "PEP8", "Google")
            include_tests: Generate unit tests
            include_docs: Include documentation/comments
            **kwargs: Additional parameters

        Returns:
            Dictionary with:
                - code: Generated code string
                - language: Detected/used language
                - tests: Generated tests (if requested)
                - explanation: Code explanation

        Example:
            >>> result = llm.code_generation(
            ...     "Binary search function with type hints",
            ...     language="python",
            ...     include_tests=True
            ... )
            >>> print(result["code"])
        """
        pass

    @abstractmethod
    def code_explanation(
            self,
            code: str,
            *,
            language: Optional[str] = None,
            detail_level: str = "medium",  # "brief", "medium", "detailed"
            **kwargs
    ) -> str:
        """
        Generate natural language explanation of code.

        Args:
            code: Code to explain
            language: Programming language (auto-detected if None)
            detail_level: Explanation verbosity
            **kwargs: Additional parameters

        Returns:
            Natural language explanation
        """
        pass

    @abstractmethod
    def code_review(
            self,
            code: str,
            *,
            language: Optional[str] = None,
            focus_areas: Optional[List[str]] = None,  # ["security", "performance", "style"]
            **kwargs
    ) -> Dict[str, Any]:
        """
        Perform automated code review.

        Args:
            code: Code to review
            language: Programming language
            focus_areas: Specific aspects to review
            **kwargs: Additional parameters

        Returns:
            Dictionary with:
                - issues: List of identified issues
                - suggestions: Improvement suggestions
                - score: Overall code quality score
                - summary: Review summary
        """
        pass

    @abstractmethod
    def code_completion(
            self,
            code: str,
            cursor_position: Optional[int] = None,
            *,
            language: Optional[str] = None,
            max_completions: int = 5,
            **kwargs
    ) -> List[str]:
        """
        Generate code completions for IDE/editor integration.

        Args:
            code: Current code context
            cursor_position: Cursor position for completion (end if None)
            language: Programming language
            max_completions: Maximum number of suggestions
            **kwargs: Additional parameters

        Returns:
            List of completion suggestions
        """
        pass

    # ========================================================================
    # Structured Output
    # ========================================================================

    @abstractmethod
    def generate_with_schema(
            self,
            messages: Messages,
            schema: Dict[str, Any],
            *,
            strict: bool = True,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Generate output conforming to a JSON schema.

        Args:
            messages: Input messages
            schema: JSON Schema defining output structure
            strict: Enforce strict schema adherence
            config: Generation configuration
            **kwargs: Additional parameters

        Returns:
            Parsed JSON object matching the schema

        Example:
            >>> schema = {
            ...     "type": "object",
            ...     "properties": {
            ...         "name": {"type": "string"},
            ...         "age": {"type": "integer"},
            ...         "interests": {"type": "array", "items": {"type": "string"}}
            ...     },
            ...     "required": ["name", "age"]
            ... }
            >>> result = llm.generate_with_schema(
            ...     messages=[{"role": "user", "content": "Extract info about John, 30, likes hiking and reading"}],
            ...     schema=schema
            ... )
        """
        pass

    @abstractmethod
    def extract_structured_data(
            self,
            text: str,
            schema: Dict[str, Any],
            *,
            examples: Optional[List[Dict[str, Any]]] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Extract structured data from unstructured text.

        Args:
            text: Input text to extract from
            schema: JSON Schema for output structure
            examples: Few-shot examples for better extraction
            **kwargs: Additional parameters

        Returns:
            Extracted structured data

        Example:
            >>> text = "John Doe, 35 years old, lives in New York. Email: john@example.com"
            >>> schema = {
            ...     "type": "object",
            ...     "properties": {
            ...         "name": {"type": "string"},
            ...         "age": {"type": "integer"},
            ...         "location": {"type": "string"},
            ...         "email": {"type": "string"}
            ...     }
            ... }
            >>> data = llm.extract_structured_data(text, schema)
        """
        pass

    # ========================================================================
    # Content Safety and Moderation
    # ========================================================================

    @abstractmethod
    def moderate_content(
            self,
            text: str,
            **kwargs
    ) -> ModerationResult:
        """
        Check content for policy violations.

        Args:
            text: Content to moderate
            **kwargs: Additional parameters

        Returns:
            Moderation result with:
                - flagged: Whether content violates policies
                - categories: Violated categories (hate, violence, etc.)
                - category_scores: Confidence scores per category
                - severity: Overall severity level

        Example:
            >>> result = llm.moderate_content(user_input)
            >>> if result["flagged"]:
            ...     print(f"Content flagged: {result['categories']}")
        """
        pass

    @abstractmethod
    def classify_text(
            self,
            text: str,
            categories: List[str],
            *,
            multi_label: bool = False,
            **kwargs
    ) -> Dict[str, float]:
        """
        Classify text into predefined categories.

        Args:
            text: Text to classify
            categories: List of possible categories
            multi_label: Allow multiple categories
            **kwargs: Additional parameters

        Returns:
            Dictionary mapping categories to confidence scores

        Example:
            >>> scores = llm.classify_text(
            ...     "This product is amazing!",
            ...     categories=["positive", "negative", "neutral"]
            ... )
            >>> print(f"Sentiment: {max(scores, key=scores.get)}")
        """
        pass

    # ========================================================================
    # Conversation Management
    # ========================================================================

    @abstractmethod
    def create_conversation(
            self,
            system_prompt: Optional[str] = None,
            **kwargs
    ) -> str:
        """
        Create a new conversation session with persistent state.

        Args:
            system_prompt: System message for the conversation
            **kwargs: Additional configuration
                - max_history: Maximum messages to retain
                - metadata: Arbitrary metadata

        Returns:
            Conversation ID for future reference
        """
        pass

    @abstractmethod
    def continue_conversation(
            self,
            conversation_id: str,
            user_message: str,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Add user message and get assistant response in existing conversation.

        Args:
            conversation_id: ID from create_conversation
            user_message: New user input
            **kwargs: Generation parameters

        Returns:
            Response dictionary with assistant's reply
        """
        pass

    @abstractmethod
    def get_conversation_history(
            self,
            conversation_id: str,
            **kwargs
    ) -> Messages:
        """
        Retrieve full conversation history.

        Args:
            conversation_id: Conversation ID
            **kwargs: Additional parameters
                - limit: Maximum messages to return
                - after: Return messages after specific timestamp

        Returns:
            List of messages
        """
        pass

    @abstractmethod
    def clear_conversation(
            self,
            conversation_id: str,
            **kwargs
    ) -> bool:
        """
        Clear conversation history but keep conversation active.

        Args:
            conversation_id: Conversation ID
            **kwargs: Additional parameters

        Returns:
            Success status
        """
        pass

    # ========================================================================
    # Token Management
    # ========================================================================

    @abstractmethod
    def count_tokens(
            self,
            text: Union[str, Messages],
            **kwargs
    ) -> int:
        """
        Count tokens in text or messages using model's tokenizer.

        Args:
            text: String or list of messages
            **kwargs: Additional parameters

        Returns:
            Number of tokens

        Example:
            >>> token_count = llm.count_tokens("Hello, world!")
            >>> print(f"Tokens: {token_count}")
        """
        pass

    @abstractmethod
    def truncate_to_max_tokens(
            self,
            text: str,
            max_tokens: int,
            *,
            from_end: bool = True,
            **kwargs
    ) -> str:
        """
        Truncate text to fit within token limit.

        Args:
            text: Input text
            max_tokens: Maximum allowed tokens
            from_end: Truncate from end (True) or start (False)
            **kwargs: Additional parameters

        Returns:
            Truncated text
        """
        pass

    @abstractmethod
    def estimate_cost(
            self,
            input_tokens: int,
            output_tokens: int,
            **kwargs
    ) -> Dict[str, float]:
        """
        Estimate cost for token usage.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            **kwargs: Additional parameters

        Returns:
            Dictionary with:
                - input_cost: Cost for input tokens
                - output_cost: Cost for output tokens
                - total_cost: Total cost
                - currency: Currency code (e.g., "USD")
        """
        pass

    # ========================================================================
    # Model Information and Metadata
    # ========================================================================

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get comprehensive model information.

        Returns:
            Dictionary with:
                - name: Model name
                - provider: Provider name
                - version: Model version
                - context_length: Maximum context window
                - max_output_tokens: Maximum output length
                - capabilities: List of supported capabilities
                - modalities: Supported input/output types
                - pricing: Cost information
                - release_date: Model release date
                - description: Model description
        """
        pass

    @abstractmethod
    def get_context_window(self) -> int:
        """
        Get maximum context window size in tokens.

        Returns:
            Context window size
        """
        pass

    @abstractmethod
    def get_max_output_tokens(self) -> int:
        """
        Get maximum output token limit.

        Returns:
            Max output tokens
        """
        pass

    # ========================================================================
    # Batch Processing
    # ========================================================================

    @abstractmethod
    def batch_generate(
            self,
            prompts: List[str],
            *,
            config: Optional[GenerationConfig] = None,
            show_progress: bool = False,
            **kwargs
    ) -> List[str]:
        """
        Process multiple prompts in batch for efficiency.

        Args:
            prompts: List of input prompts
            config: Generation configuration
            show_progress: Show progress bar
            **kwargs: Additional parameters
                - batch_size: Internal batch size
                - max_workers: Parallel workers

        Returns:
            List of generated outputs (same order as inputs)
        """
        pass

    @abstractmethod
    def batch_embed(
            self,
            texts: List[str],
            *,
            batch_size: int = 32,
            show_progress: bool = False,
            **kwargs
    ) -> List[Embedding]:
        """
        Generate embeddings for multiple texts in batch.

        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            show_progress: Show progress bar
            **kwargs: Additional parameters

        Returns:
            List of embeddings
        """
        pass

    # ========================================================================
    # Fine-tuning and Customization
    # ========================================================================

    @abstractmethod
    def create_fine_tuning_job(
            self,
            training_file: str,
            *,
            validation_file: Optional[str] = None,
            hyperparameters: Optional[Dict[str, Any]] = None,
            **kwargs
    ) -> str:
        """
        Create a fine-tuning job for model customization.

        Args:
            training_file: Path to training data file
            validation_file: Optional validation data
            hyperparameters: Training hyperparameters
            **kwargs: Additional parameters

        Returns:
            Fine-tuning job ID

        Raises:
            CapabilityNotSupportedException: If fine-tuning not supported
        """
        pass

    @abstractmethod
    def get_fine_tuning_status(
            self,
            job_id: str,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Check status of fine-tuning job.

        Args:
            job_id: Fine-tuning job ID
            **kwargs: Additional parameters

        Returns:
            Status dictionary with progress information
        """
        pass

    # ========================================================================
    # Observability and Monitoring
    # ========================================================================

    @abstractmethod
    def log_request(
            self,
            method: str,
            input_data: Any,
            response: Any,
            *,
            latency_ms: Optional[float] = None,
            metadata: Optional[Dict[str, Any]] = None,
            **kwargs
    ) -> None:
        """
        Log request for monitoring and debugging.

        Args:
            method: Method name that was called
            input_data: Input data/parameters
            response: Response data
            latency_ms: Request duration
            metadata: Additional metadata (user_id, session_id, etc.)
            **kwargs: Additional logging parameters
        """
        pass

    @abstractmethod
    def get_usage_stats(
            self,
            period: str = "day",  # "hour", "day", "week", "month"
            **kwargs
    ) -> Dict[str, Any]:
        """
        Get usage statistics for monitoring.

        Args:
            period: Time period for stats
            **kwargs: Additional filters

        Returns:
            Dictionary with usage metrics
        """
        pass

    # ========================================================================
    # Utility Methods
    # ========================================================================

    @abstractmethod
    def format_messages(
            self,
            messages: Messages,
            **kwargs
    ) -> str:
        """
        Convert structured messages to single prompt string.

        Useful for models that don't support chat format natively.

        Args:
            messages: Role-based message list
            **kwargs: Formatting options

        Returns:
            Formatted prompt string
        """
        pass

    @abstractmethod
    def parse_tool_calls(
            self,
            response: Dict[str, Any],
            **kwargs
    ) -> List[ToolCall]:
        """
        Extract and parse tool calls from LLM response.

        Args:
            response: Raw LLM response
            **kwargs: Parsing options

        Returns:
            List of parsed tool call objects
        """
        pass

    @abstractmethod
    def validate_config(
            self,
            config: Dict[str, Any],
            **kwargs
    ) -> Tuple[bool, List[str]]:
        """
        Validate configuration parameters.

        Args:
            config: Configuration to validate
            **kwargs: Validation options

        Returns:
            Tuple of (is_valid, error_messages)
        """
        pass

    @abstractmethod
    def health_check(self, **kwargs) -> bool:
        """
        Verify that the model service is reachable and healthy.

        Args:
            **kwargs: Additional check parameters

        Returns:
            True if healthy, False otherwise
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
        Close connections and cleanup resources.

        Should be called when done using the facade instance.
        """
        pass

    # ========================================================================
    # Context Manager Support
    # ========================================================================

    def __enter__(self) -> "LLMFacade":
        """Enable usage as context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Cleanup when exiting context."""
        self.close()

    # ========================================================================
    # Special Methods
    # ========================================================================

    def __repr__(self) -> str:
        """String representation."""
        info = self.get_model_info()
        return f"LLMFacade(provider='{info.get('provider')}', model='{info.get('name')}')"

    def __str__(self) -> str:
        """Human-readable string."""
        info = self.get_model_info()
        return f"{info.get('provider')} - {info.get('name')}"


# ============================================================================
# Facade Exceptions
# ============================================================================

class LLMFacadeException(Exception):
    """Base exception for all LLM facade errors."""
    pass


class CapabilityNotSupportedException(LLMFacadeException):
    """Raised when a capability is not supported by the model."""

    def __init__(self, capability: str, model: str):
        self.capability = capability
        self.model = model
        super().__init__(f"Capability '{capability}' not supported by model '{model}'")


class RateLimitException(LLMFacadeException):
    """Raised when API rate limit is exceeded."""

    def __init__(self, message: str, retry_after: Optional[int] = None):
        self.retry_after = retry_after
        super().__init__(message)


class ContentFilterException(LLMFacadeException):
    """Raised when content is blocked by safety filters."""

    def __init__(self, message: str, category: Optional[str] = None):
        self.category = category
        super().__init__(message)


class ContextLengthExceededException(LLMFacadeException):
    """Raised when input exceeds model's context window."""

    def __init__(self, provided: int, maximum: int):
        self.provided = provided
        self.maximum = maximum
        super().__init__(f"Context length {provided} exceeds maximum {maximum}")


class ToolNotFoundException(LLMFacadeException):
    """Raised when requested tool is not available."""

    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        super().__init__(f"Tool '{tool_name}' not found")


class ToolExecutionException(LLMFacadeException):
    """Raised when tool execution fails."""

    def __init__(self, tool_name: str, error: str):
        self.tool_name = tool_name
        self.error = error
        super().__init__(f"Tool '{tool_name}' execution failed: {error}")


class InvalidResponseException(LLMFacadeException):
    """Raised when LLM returns invalid or unexpected response."""
    pass


class AuthenticationException(LLMFacadeException):
    """Raised when authentication fails."""
    pass


class NetworkException(LLMFacadeException):
    """Raised when network request fails."""
    pass


__all__ = [
    # Main class
    'LLMFacade',
    # Enums
    'ModelCapability',
    'ResponseFormat',
    'SafetyLevel',
    # Data classes
    'GenerationConfig',
    'TokenUsage',
    'CompletionMetadata',
    # Type aliases
    'Messages',
    'TextStream',
    'DeltaStream',
    'ToolDefinition',
    'ToolCall',
    'ToolResult',
    'Document',
    'RetrievalResult',
    'Embedding',
    'ImageInput',
    'ImageOutput',
    'ModerationResult',
    'SafetyResult',
    # Exceptions
    'LLMFacadeException',
    'CapabilityNotSupportedException',
    'RateLimitException',
    'ContentFilterException',
    'ContextLengthExceededException',
    'ToolNotFoundException',
    'ToolExecutionException',
    'InvalidResponseException',
    'AuthenticationException',
    'NetworkException'
]