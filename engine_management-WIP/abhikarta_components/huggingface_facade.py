"""
HuggingFace LLM Facade Implementation

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This module and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

Patent Pending: Certain architectural patterns and implementations described in this
module may be subject to patent applications.

Description:
This module provides a concrete implementation of the LLMFacade interface for
Hugging Face models, supporting both API-based inference and local model execution.
"""

import os
import json
import time
import asyncio
from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator, Callable, Tuple
from dataclasses import dataclass
import warnings

# Import the base facade
import sys

sys.path.append('/mnt/user-data/outputs')
from llm_facade import (
    LLMFacade,
    ModelCapability,
    GenerationConfig,
    TokenUsage,
    CompletionMetadata,
    Messages,
    TextStream,
    DeltaStream,
    ToolDefinition,
    ToolCall,
    ToolResult,
    Document,
    RetrievalResult,
    Embedding,
    ImageInput,
    ImageOutput,
    ModerationResult,
    SafetyResult,
    LLMFacadeException,
    CapabilityNotSupportedException,
    RateLimitException,
    ContentFilterException,
    ContextLengthExceededException,
    ToolNotFoundException,
    ToolExecutionException,
    InvalidResponseException,
    AuthenticationException,
    NetworkException
)


class HuggingFaceLLMFacade(LLMFacade):
    """
    HuggingFace implementation of the LLMFacade interface.

    Supports both API-based inference via Inference API and local model execution
    via transformers library. Automatically detects model capabilities based on
    model architecture and configuration.

    Features:
    - Text generation and chat completion
    - Embeddings (for compatible models)
    - Automatic capability detection
    - Support for custom model configurations
    - Streaming support
    - Async operations

    Example:
        >>> llm = HuggingFaceLLMFacade(
        ...     model_name="meta-llama/Llama-2-7b-chat-hf",
        ...     api_key="hf_..."
        ... )
        >>> response = llm.chat_completion([
        ...     {"role": "user", "content": "Hello!"}
        ... ])
    """

    # Model configuration mappings
    CHAT_MODELS = {
        "llama-2-7b-chat", "llama-2-13b-chat", "llama-2-70b-chat",
        "llama-3", "llama-3.1", "llama-3.2",
        "mistral-7b-instruct", "mixtral-8x7b-instruct",
        "codellama", "starcoder", "wizardcoder",
        "falcon-7b-instruct", "falcon-40b-instruct",
        "vicuna", "alpaca", "gpt-j", "gpt-neox"
    }

    EMBEDDING_MODELS = {
        "sentence-transformers", "all-mpnet-base-v2", "all-MiniLM",
        "bge-", "e5-", "instructor-", "gte-"
    }

    CODE_MODELS = {
        "codellama", "starcoder", "wizardcoder", "codegen", "santacoder"
    }

    def __init__(
            self,
            model_name: str,
            api_key: Optional[str] = None,
            base_url: Optional[str] = None,
            timeout: Optional[float] = None,
            max_retries: int = 3,
            use_local: bool = False,
            device: str = "auto",
            **kwargs
    ) -> None:
        """
        Initialize HuggingFace LLM Facade.

        Args:
            model_name: HuggingFace model identifier (e.g., "meta-llama/Llama-2-7b-chat-hf")
            api_key: HuggingFace API token (reads from HF_TOKEN env var if None)
            base_url: Custom inference endpoint URL (optional)
            timeout: Request timeout in seconds (default: 120)
            max_retries: Number of retry attempts for failed requests
            use_local: Use local model execution instead of API (requires transformers)
            device: Device for local execution ("cpu", "cuda", "mps", "auto")
            **kwargs: Additional configuration
                - trust_remote_code: Allow remote code execution (default: False)
                - load_in_8bit: Use 8-bit quantization for local models
                - load_in_4bit: Use 4-bit quantization for local models
                - torch_dtype: Torch data type for local models
        """
        self.model_name = model_name
        self.api_key = api_key or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
        self.base_url = base_url
        self.timeout = timeout or 120.0
        self.max_retries = max_retries
        self.use_local = use_local
        self.device = device
        self.kwargs = kwargs

        # Initialize client
        self.client = None
        self.tokenizer = None
        self.model = None

        if use_local:
            self._initialize_local_model()
        else:
            self._initialize_api_client()

        # Detect capabilities
        self._capabilities = self._detect_capabilities()

        # Model info cache
        self._model_info = None

    def _initialize_api_client(self):
        """Initialize HuggingFace Inference API client."""
        try:
            from huggingface_hub import InferenceClient
            self.client = InferenceClient(
                model=self.model_name,
                token=self.api_key,
                timeout=self.timeout
            )
        except ImportError:
            raise ImportError(
                "Please install huggingface_hub: pip install huggingface_hub"
            )
        except Exception as e:
            raise AuthenticationException(f"Failed to initialize HuggingFace client: {e}")

    def _initialize_local_model(self):
        """Initialize local model using transformers."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                token=self.api_key,
                trust_remote_code=self.kwargs.get("trust_remote_code", False)
            )

            # Configure model loading
            load_kwargs = {
                "token": self.api_key,
                "trust_remote_code": self.kwargs.get("trust_remote_code", False)
            }

            # Handle quantization
            if self.kwargs.get("load_in_8bit"):
                load_kwargs["load_in_8bit"] = True
            elif self.kwargs.get("load_in_4bit"):
                load_kwargs["load_in_4bit"] = True

            # Set dtype
            if "torch_dtype" in self.kwargs:
                load_kwargs["torch_dtype"] = self.kwargs["torch_dtype"]
            else:
                load_kwargs["torch_dtype"] = torch.float16

            # Set device
            if self.device == "auto":
                load_kwargs["device_map"] = "auto"
            else:
                load_kwargs["device_map"] = self.device

            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **load_kwargs
            )

        except ImportError:
            raise ImportError(
                "Please install transformers and torch: pip install transformers torch"
            )
        except Exception as e:
            raise LLMFacadeException(f"Failed to load local model: {e}")

    def _detect_capabilities(self) -> List[ModelCapability]:
        """Detect model capabilities based on model name and type."""
        capabilities = [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.STREAMING
        ]

        model_lower = self.model_name.lower()

        # Check if it's a chat model
        if any(chat_model in model_lower for chat_model in self.CHAT_MODELS):
            capabilities.append(ModelCapability.CHAT_COMPLETION)

        # Check if it's an embedding model
        if any(emb_model in model_lower for emb_model in self.EMBEDDING_MODELS):
            capabilities.append(ModelCapability.EMBEDDINGS)

        # Check if it's a code model
        if any(code_model in model_lower for code_model in self.CODE_MODELS):
            capabilities.extend([
                ModelCapability.CODE_GENERATION,
                ModelCapability.CHAT_COMPLETION
            ])

        # Most modern models support some form of reasoning
        if "llama-3" in model_lower or "mixtral" in model_lower:
            capabilities.append(ModelCapability.REASONING)

        return list(set(capabilities))  # Remove duplicates

    def get_capabilities(self) -> List[ModelCapability]:
        """Get list of supported capabilities."""
        return self._capabilities.copy()

    def supports_capability(self, capability: ModelCapability) -> bool:
        """Check if a specific capability is supported."""
        return capability in self._capabilities

    # =========================================================================
    # Core Text Generation
    # =========================================================================

    def text_generation(
            self,
            prompt: str,
            *,
            config: Optional[GenerationConfig] = None,
            stream: bool = False,
            **kwargs
    ) -> Union[str, Iterator[str], Dict[str, Any]]:
        """
        Generate text completion from a prompt.

        Args:
            prompt: Input text to complete
            config: Generation configuration
            stream: Return streaming iterator
            **kwargs: Additional parameters

        Returns:
            Generated text, stream iterator, or full response dict
        """
        try:
            # Build parameters
            params = self._build_generation_params(config, **kwargs)

            if self.use_local:
                return self._local_text_generation(prompt, params, stream)
            else:
                return self._api_text_generation(prompt, params, stream)

        except Exception as e:
            raise self._transform_exception(e)

    def _api_text_generation(
            self,
            prompt: str,
            params: Dict[str, Any],
            stream: bool
    ) -> Union[str, Iterator[str]]:
        """Text generation using API."""
        if stream:
            # Return streaming iterator
            def stream_generator():
                for token in self.client.text_generation(
                        prompt,
                        stream=True,
                        **params
                ):
                    yield token

            return stream_generator()
        else:
            # Return full text
            response = self.client.text_generation(
                prompt,
                stream=False,
                **params
            )
            return response

    def _local_text_generation(
            self,
            prompt: str,
            params: Dict[str, Any],
            stream: bool
    ) -> Union[str, Iterator[str]]:
        """Text generation using local model."""
        import torch

        # Tokenize input
        inputs = self.tokenizer(prompt, return_tensors="pt")
        if self.device != "auto":
            inputs = inputs.to(self.device)

        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                **params,
                pad_token_id=self.tokenizer.eos_token_id
            )

        # Decode
        generated_text = self.tokenizer.decode(
            outputs[0][len(inputs.input_ids[0]):],
            skip_special_tokens=True
        )

        return generated_text

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
        Perform chat completion with role-based messages.

        Args:
            messages: List of message dictionaries
            config: Generation configuration
            stream: Return streaming iterator
            tools: Tool definitions (limited support)
            tool_choice: Tool selection strategy
            parallel_tool_calls: Allow parallel tool calls
            **kwargs: Additional parameters

        Returns:
            Response dictionary or stream iterator
        """
        if not self.supports_capability(ModelCapability.CHAT_COMPLETION):
            # Fall back to text generation with formatted prompt
            formatted_prompt = self.format_messages(messages)
            text_response = self.text_generation(
                formatted_prompt,
                config=config,
                stream=stream,
                **kwargs
            )

            if stream:
                # Wrap in chat format
                def chat_stream():
                    for chunk in text_response:
                        yield {
                            "delta": {"content": chunk},
                            "finish_reason": None
                        }
                    yield {
                        "delta": {},
                        "finish_reason": "stop"
                    }

                return chat_stream()
            else:
                return {
                    "content": text_response,
                    "role": "assistant",
                    "finish_reason": "stop",
                    "usage": self._estimate_token_usage(messages, text_response),
                    "metadata": {
                        "model": self.model_name,
                        "created_at": None
                    }
                }

        # For chat models, use chat template
        try:
            # Apply chat template
            formatted_prompt = self._apply_chat_template(messages)

            # Generate response
            params = self._build_generation_params(config, **kwargs)

            if stream:
                return self._stream_chat_completion(formatted_prompt, params)
            else:
                response_text = self._api_text_generation(formatted_prompt, params, False)

                return {
                    "content": response_text,
                    "role": "assistant",
                    "finish_reason": "stop",
                    "usage": self._estimate_token_usage(messages, response_text),
                    "metadata": {
                        "model": self.model_name,
                        "created_at": None
                    },
                    "tool_calls": None
                }

        except Exception as e:
            raise self._transform_exception(e)

    def _apply_chat_template(self, messages: Messages) -> str:
        """Apply chat template to messages."""
        if self.use_local and self.tokenizer:
            # Use tokenizer's chat template if available
            try:
                return self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
            except:
                pass

        # Fall back to manual formatting
        return self.format_messages(messages)

    def _stream_chat_completion(
            self,
            prompt: str,
            params: Dict[str, Any]
    ) -> Iterator[Dict[str, Any]]:
        """Stream chat completion."""
        for chunk in self._api_text_generation(prompt, params, stream=True):
            yield {
                "delta": {"content": chunk},
                "finish_reason": None
            }

        yield {
            "delta": {},
            "finish_reason": "stop"
        }

    def chat_completion_with_vision(
            self,
            messages: Messages,
            images: Union[ImageInput, List[ImageInput]],
            *,
            config: Optional[GenerationConfig] = None,
            image_detail: str = "auto",
            **kwargs
    ) -> Dict[str, Any]:
        """
        Chat completion with vision (not supported by most HF models).

        Raises:
            CapabilityNotSupportedException: Vision not supported
        """
        raise CapabilityNotSupportedException(
            capability="vision",
            model=self.model_name
        )

    # =========================================================================
    # Streaming Methods
    # =========================================================================

    def stream_text_generation(self, prompt: str, **kwargs) -> Iterator[str]:
        """Stream text generation."""
        return self.text_generation(prompt, stream=True, **kwargs)

    def stream_chat_completion(self, messages: Messages, **kwargs) -> Iterator[Dict[str, Any]]:
        """Stream chat completion."""
        return self.chat_completion(messages, stream=True, **kwargs)

    # =========================================================================
    # Async Variants
    # =========================================================================

    async def atext_generation(
            self,
            prompt: str,
            **kwargs
    ) -> Union[str, AsyncIterator[str], Dict[str, Any]]:
        """Async text generation."""
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.text_generation(prompt, **kwargs)
        )

    async def achat_completion(
            self,
            messages: Messages,
            **kwargs
    ) -> Union[Dict[str, Any], AsyncIterator[Dict[str, Any]]]:
        """Async chat completion."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.chat_completion(messages, **kwargs)
        )

    async def achat_completion_with_vision(
            self,
            messages: Messages,
            images: Union[ImageInput, List[ImageInput]],
            **kwargs
    ) -> Dict[str, Any]:
        """Async vision chat (not supported)."""
        raise CapabilityNotSupportedException("vision", self.model_name)

    # =========================================================================
    # RAG Operations
    # =========================================================================

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
        """Retrieve documents (requires vector store integration)."""
        if vector_store is None:
            raise ValueError("Vector store required for document retrieval")

        # Delegate to vector store
        return vector_store.similarity_search(
            query,
            k=top_k,
            filter=filter,
            score_threshold=score_threshold
        )

    def rag_chat(
            self,
            messages: Messages,
            *,
            retrieval_top_k: int = 5,
            retrieval_filter: Optional[Dict] = None,
            context_template: Optional[str] = None,
            include_sources: bool = True,
            citation_style: str = "inline",
            config: Optional[GenerationConfig] = None,
            stream: bool = False,
            vector_store: Optional[Any] = None,
            **kwargs
    ) -> Union[Dict[str, Any], Iterator[Dict[str, Any]]]:
        """RAG-augmented chat."""
        if vector_store is None:
            raise ValueError("Vector store required for RAG")

        # Extract query from last user message
        query = messages[-1]["content"]

        # Retrieve documents
        docs = self.retrieve_documents(
            query,
            top_k=retrieval_top_k,
            filter=retrieval_filter,
            vector_store=vector_store
        )

        # Format context
        context = "\n\n".join([doc["content"] for doc, _ in docs])

        # Apply template
        if context_template is None:
            context_template = "Context:\n{context}\n\nQuestion: {question}"

        augmented_content = context_template.format(
            context=context,
            question=query
        )

        # Update last message
        augmented_messages = messages[:-1] + [
            {"role": "user", "content": augmented_content}
        ]

        # Generate response
        response = self.chat_completion(
            augmented_messages,
            config=config,
            stream=stream,
            **kwargs
        )

        # Add sources if requested
        if not stream and include_sources:
            response["sources"] = [doc["metadata"] for doc, _ in docs]
            response["retrieved_docs"] = docs

        return response

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
        """RAG for single-turn generation."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": query})

        return self.rag_chat(
            messages,
            retrieval_top_k=retrieval_top_k,
            context_template=context_template,
            include_sources=include_sources,
            config=config,
            stream=stream,
            vector_store=vector_store,
            **kwargs
        )

    # =========================================================================
    # Tool/Function Calling
    # =========================================================================

    def create_tool_definition(
            self,
            name: str,
            description: str,
            parameters: Dict[str, Any],
            required: Optional[List[str]] = None
    ) -> ToolDefinition:
        """Create tool definition."""
        return {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
                "required": required or []
            }
        }

    def call_tool(
            self,
            tool_call: ToolCall,
            available_tools: Dict[str, Callable],
            **kwargs
    ) -> ToolResult:
        """Execute a tool."""
        tool_name = tool_call["function"]["name"]

        if tool_name not in available_tools:
            raise ToolNotFoundException(tool_name)

        try:
            args = json.loads(tool_call["function"]["arguments"])
            result = available_tools[tool_name](**args)

            return {
                "tool_call_id": tool_call.get("id", ""),
                "output": result
            }
        except Exception as e:
            raise ToolExecutionException(tool_name, str(e))

    def execute_tool_loop(
            self,
            messages: Messages,
            tools: List[ToolDefinition],
            available_tools: Dict[str, Callable],
            max_iterations: int = 5,
            **kwargs
    ) -> Dict[str, Any]:
        """Execute tool loop (basic implementation)."""
        # Note: Most HF models don't natively support tool calling
        # This is a simplified implementation
        warnings.warn(
            "Tool calling support is limited for HuggingFace models. "
            "Using simplified implementation."
        )

        # Just run normal chat completion
        return self.chat_completion(messages, **kwargs)

    # =========================================================================
    # Embeddings
    # =========================================================================

    def embed_text(
            self,
            texts: Union[str, List[str]],
            *,
            normalize: bool = True,
            embedding_type: str = "document",
            truncate: bool = True,
            **kwargs
    ) -> Union[Embedding, List[Embedding]]:
        """Generate text embeddings."""
        if not self.supports_capability(ModelCapability.EMBEDDINGS):
            raise CapabilityNotSupportedException("embeddings", self.model_name)

        is_single = isinstance(texts, str)
        if is_single:
            texts = [texts]

        try:
            if self.use_local:
                embeddings = self._local_embed_text(texts, normalize)
            else:
                embeddings = self._api_embed_text(texts, normalize)

            return embeddings[0] if is_single else embeddings

        except Exception as e:
            raise self._transform_exception(e)

    def _api_embed_text(
            self,
            texts: List[str],
            normalize: bool
    ) -> List[Embedding]:
        """Generate embeddings using API."""
        from huggingface_hub import InferenceClient

        embeddings = []
        for text in texts:
            emb = self.client.feature_extraction(text)
            if normalize:
                # Normalize to unit length
                import numpy as np
                emb = np.array(emb)
                emb = emb / np.linalg.norm(emb)
                emb = emb.tolist()
            embeddings.append(emb)

        return embeddings

    def _local_embed_text(
            self,
            texts: List[str],
            normalize: bool
    ) -> List[Embedding]:
        """Generate embeddings using local model."""
        import torch

        embeddings = []
        for text in texts:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
            if self.device != "auto":
                inputs = inputs.to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use mean pooling
                emb = outputs.last_hidden_state.mean(dim=1).squeeze()

                if normalize:
                    emb = torch.nn.functional.normalize(emb, p=2, dim=0)

                embeddings.append(emb.cpu().tolist())

        return embeddings

    def embed_image(
            self,
            images: Union[ImageInput, List[ImageInput]],
            *,
            normalize: bool = True,
            **kwargs
    ) -> Union[Embedding, List[Embedding]]:
        """Generate image embeddings (not supported)."""
        raise CapabilityNotSupportedException("image_embeddings", self.model_name)

    def compute_similarity(
            self,
            embedding1: Embedding,
            embedding2: Embedding,
            metric: str = "cosine"
    ) -> float:
        """Compute similarity between embeddings."""
        import numpy as np

        emb1 = np.array(embedding1)
        emb2 = np.array(embedding2)

        if metric == "cosine":
            return float(np.dot(emb1, emb2))
        elif metric == "dot":
            return float(np.dot(emb1, emb2))
        elif metric == "euclidean":
            return float(-np.linalg.norm(emb1 - emb2))
        else:
            raise ValueError(f"Unknown metric: {metric}")

    # =========================================================================
    # Image Operations (Not Supported)
    # =========================================================================

    def image_generation(self, prompt: str, **kwargs) -> ImageOutput:
        """Generate image (not supported)."""
        raise CapabilityNotSupportedException("image_generation", self.model_name)

    def image_editing(self, image: ImageInput, prompt: str, **kwargs) -> ImageOutput:
        """Edit image (not supported)."""
        raise CapabilityNotSupportedException("image_editing", self.model_name)

    def image_variation(self, image: ImageInput, n: int = 1, **kwargs) -> Union[ImageOutput, List[ImageOutput]]:
        """Generate image variations (not supported)."""
        raise CapabilityNotSupportedException("image_variation", self.model_name)

    def image_captioning(self, image: ImageInput, **kwargs) -> str:
        """Generate image caption (not supported)."""
        raise CapabilityNotSupportedException("image_captioning", self.model_name)

    # =========================================================================
    # Audio Operations (Not Supported)
    # =========================================================================

    def audio_transcription(self, audio: Union[bytes, str], **kwargs) -> Union[str, Dict[str, Any]]:
        """Transcribe audio (not supported)."""
        raise CapabilityNotSupportedException("audio_transcription", self.model_name)

    def audio_translation(self, audio: Union[bytes, str], target_language: str = "en", **kwargs) -> str:
        """Translate audio (not supported)."""
        raise CapabilityNotSupportedException("audio_translation", self.model_name)

    # =========================================================================
    # Code Operations
    # =========================================================================

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
        """Generate code from description."""
        prompt = f"Generate {language or 'Python'} code for: {description}"

        if framework:
            prompt += f"\nUse {framework} framework."
        if style_guide:
            prompt += f"\nFollow {style_guide} style guide."
        if include_tests:
            prompt += "\nInclude unit tests."
        if include_docs:
            prompt += "\nInclude documentation."

        code = self.text_generation(prompt, **kwargs)

        return {
            "code": code,
            "language": language or "python",
            "explanation": f"Generated code for: {description}"
        }

    def code_explanation(
            self,
            code: str,
            *,
            language: Optional[str] = None,
            detail_level: str = "medium",
            **kwargs
    ) -> str:
        """Explain code."""
        prompt = f"Explain this {language or 'code'} in {detail_level} detail:\n\n{code}"
        return self.text_generation(prompt, **kwargs)

    def code_review(
            self,
            code: str,
            *,
            language: Optional[str] = None,
            focus_areas: Optional[List[str]] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """Review code."""
        prompt = f"Review this {language or 'code'}:\n\n{code}"

        if focus_areas:
            prompt += f"\n\nFocus on: {', '.join(focus_areas)}"

        review = self.text_generation(prompt, **kwargs)

        return {
            "issues": [],
            "suggestions": [],
            "summary": review
        }

    def code_completion(
            self,
            code: str,
            cursor_position: Optional[int] = None,
            *,
            language: Optional[str] = None,
            max_completions: int = 5,
            **kwargs
    ) -> List[str]:
        """Generate code completions."""
        if cursor_position is not None:
            code = code[:cursor_position]

        completion = self.text_generation(code, **kwargs)
        return [completion]

    # =========================================================================
    # Structured Output
    # =========================================================================

    def generate_with_schema(
            self,
            messages: Messages,
            schema: Dict[str, Any],
            *,
            strict: bool = True,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """Generate output matching JSON schema."""
        # Add schema to prompt
        schema_prompt = f"Respond with JSON matching this schema: {json.dumps(schema)}"

        messages_with_schema = [
                                   {"role": "system", "content": schema_prompt}
                               ] + messages

        response = self.chat_completion(messages_with_schema, config=config, **kwargs)

        # Try to parse JSON from response
        content = response["content"]
        try:
            # Extract JSON if wrapped in markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            return json.loads(content)
        except:
            raise InvalidResponseException("Failed to parse JSON response")

    def extract_structured_data(
            self,
            text: str,
            schema: Dict[str, Any],
            *,
            examples: Optional[List[Dict[str, Any]]] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """Extract structured data from text."""
        prompt = f"Extract data matching schema {json.dumps(schema)} from:\n\n{text}"

        messages = [{"role": "user", "content": prompt}]
        return self.generate_with_schema(messages, schema, **kwargs)

    # =========================================================================
    # Content Safety
    # =========================================================================

    def moderate_content(self, text: str, **kwargs) -> ModerationResult:
        """Moderate content (not supported)."""
        raise CapabilityNotSupportedException("content_moderation", self.model_name)

    def classify_text(
            self,
            text: str,
            categories: List[str],
            *,
            multi_label: bool = False,
            **kwargs
    ) -> Dict[str, float]:
        """Classify text into categories."""
        prompt = f"Classify this text into categories {categories}:\n\n{text}\n\nRespond with JSON."

        response = self.text_generation(prompt, **kwargs)

        try:
            return json.loads(response)
        except:
            # Fall back to uniform distribution
            return {cat: 1.0 / len(categories) for cat in categories}

    # =========================================================================
    # Conversation Management
    # =========================================================================

    def create_conversation(
            self,
            system_prompt: Optional[str] = None,
            **kwargs
    ) -> str:
        """Create conversation (not persisted)."""
        import uuid
        return str(uuid.uuid4())

    def continue_conversation(
            self,
            conversation_id: str,
            user_message: str,
            **kwargs
    ) -> Dict[str, Any]:
        """Continue conversation."""
        messages = [{"role": "user", "content": user_message}]
        return self.chat_completion(messages, **kwargs)

    def get_conversation_history(
            self,
            conversation_id: str,
            **kwargs
    ) -> Messages:
        """Get conversation history (not persisted)."""
        return []

    def clear_conversation(self, conversation_id: str, **kwargs) -> bool:
        """Clear conversation."""
        return True

    # =========================================================================
    # Token Management
    # =========================================================================

    def count_tokens(self, text: Union[str, Messages], **kwargs) -> int:
        """Count tokens in text."""
        if isinstance(text, list):
            text = self.format_messages(text)

        if self.use_local and self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Rough estimate: ~4 characters per token
            return len(text) // 4

    def truncate_to_max_tokens(
            self,
            text: str,
            max_tokens: int,
            *,
            from_end: bool = True,
            **kwargs
    ) -> str:
        """Truncate text to token limit."""
        if self.use_local and self.tokenizer:
            tokens = self.tokenizer.encode(text)
            if len(tokens) <= max_tokens:
                return text

            if from_end:
                tokens = tokens[:max_tokens]
            else:
                tokens = tokens[-max_tokens:]

            return self.tokenizer.decode(tokens)
        else:
            # Rough truncation by characters
            char_limit = max_tokens * 4
            if from_end:
                return text[:char_limit]
            else:
                return text[-char_limit:]

    def estimate_cost(
            self,
            input_tokens: int,
            output_tokens: int,
            **kwargs
    ) -> Dict[str, float]:
        """Estimate cost (free for most HF models)."""
        return {
            "input_cost": 0.0,
            "output_cost": 0.0,
            "total_cost": 0.0,
            "currency": "USD"
        }

    # =========================================================================
    # Model Information
    # =========================================================================

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        if self._model_info is None:
            self._model_info = {
                "name": self.model_name,
                "provider": "huggingface",
                "version": "unknown",
                "context_length": self._estimate_context_length(),
                "max_output_tokens": 2048,
                "capabilities": [cap.value for cap in self.get_capabilities()],
                "modalities": self._get_modalities(),
                "pricing": {
                    "input_per_1m": 0.0,
                    "output_per_1m": 0.0,
                    "note": "Most HuggingFace models are free to use"
                },
                "use_local": self.use_local
            }

        return self._model_info.copy()

    def _estimate_context_length(self) -> int:
        """Estimate context length based on model."""
        model_lower = self.model_name.lower()

        if "llama-3" in model_lower:
            return 8192
        elif "llama-2" in model_lower:
            return 4096
        elif "mixtral" in model_lower:
            return 32768
        elif "mistral" in model_lower:
            return 8192
        else:
            return 2048

    def _get_modalities(self) -> List[str]:
        """Get supported modalities."""
        modalities = ["text"]
        if self.supports_capability(ModelCapability.VISION):
            modalities.append("image")
        return modalities

    def get_context_window(self) -> int:
        """Get context window size."""
        return self.get_model_info()["context_length"]

    def get_max_output_tokens(self) -> int:
        """Get max output tokens."""
        return self.get_model_info()["max_output_tokens"]

    # =========================================================================
    # Batch Processing
    # =========================================================================

    def batch_generate(
            self,
            prompts: List[str],
            *,
            config: Optional[GenerationConfig] = None,
            show_progress: bool = False,
            **kwargs
    ) -> List[str]:
        """Process multiple prompts in batch."""
        results = []

        iterator = enumerate(prompts)
        if show_progress:
            try:
                from tqdm import tqdm
                iterator = tqdm(iterator, total=len(prompts))
            except ImportError:
                pass

        for i, prompt in iterator:
            result = self.text_generation(prompt, config=config, **kwargs)
            results.append(result)

        return results

    def batch_embed(
            self,
            texts: List[str],
            *,
            batch_size: int = 32,
            show_progress: bool = False,
            **kwargs
    ) -> List[Embedding]:
        """Generate embeddings in batch."""
        if not self.supports_capability(ModelCapability.EMBEDDINGS):
            raise CapabilityNotSupportedException("embeddings", self.model_name)

        embeddings = []

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.embed_text(batch, **kwargs)
            embeddings.extend(batch_embeddings)

        return embeddings

    # =========================================================================
    # Fine-tuning (Not Implemented)
    # =========================================================================

    def create_fine_tuning_job(
            self,
            training_file: str,
            *,
            validation_file: Optional[str] = None,
            hyperparameters: Optional[Dict[str, Any]] = None,
            **kwargs
    ) -> str:
        """Create fine-tuning job (not implemented)."""
        raise NotImplementedError("Fine-tuning not yet supported")

    def get_fine_tuning_status(self, job_id: str, **kwargs) -> Dict[str, Any]:
        """Get fine-tuning status (not implemented)."""
        raise NotImplementedError("Fine-tuning not yet supported")

    # =========================================================================
    # Observability
    # =========================================================================

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
        """Log request (basic implementation)."""
        # Could integrate with logging system
        pass

    def get_usage_stats(self, period: str = "day", **kwargs) -> Dict[str, Any]:
        """Get usage statistics (not implemented)."""
        return {}

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def format_messages(self, messages: Messages, **kwargs) -> str:
        """Convert messages to formatted prompt."""
        formatted = ""

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                formatted += f"System: {content}\n\n"
            elif role == "user":
                formatted += f"User: {content}\n\n"
            elif role == "assistant":
                formatted += f"Assistant: {content}\n\n"

        formatted += "Assistant:"
        return formatted

    def parse_tool_calls(self, response: Dict[str, Any], **kwargs) -> List[ToolCall]:
        """Parse tool calls from response."""
        return response.get("tool_calls", [])

    def validate_config(
            self,
            config: Dict[str, Any],
            **kwargs
    ) -> Tuple[bool, List[str]]:
        """Validate configuration."""
        errors = []

        if config.get("max_tokens", 0) > 4096:
            errors.append("max_tokens exceeds recommended limit of 4096")

        if config.get("temperature", 1.0) > 2.0:
            errors.append("temperature should be between 0.0 and 2.0")

        return (len(errors) == 0, errors)

    def health_check(self, **kwargs) -> bool:
        """Check if service is healthy."""
        try:
            # Try a simple generation
            test_response = self.text_generation(
                "test",
                config=GenerationConfig(max_tokens=5)
            )
            return True
        except:
            return False

    def close(self) -> None:
        """Close connections and cleanup."""
        self.client = None
        self.model = None
        self.tokenizer = None

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _build_generation_params(
            self,
            config: Optional[GenerationConfig],
            **kwargs
    ) -> Dict[str, Any]:
        """Build generation parameters."""
        params = {}

        if config:
            if config.max_tokens is not None:
                params["max_new_tokens"] = config.max_tokens
            if config.temperature is not None:
                params["temperature"] = config.temperature
            if config.top_p is not None:
                params["top_p"] = config.top_p
            if config.top_k is not None:
                params["top_k"] = config.top_k
            if config.repetition_penalty is not None:
                params["repetition_penalty"] = config.repetition_penalty
            if config.stop_sequences:
                params["stop_sequences"] = config.stop_sequences

        # Add any additional kwargs
        params.update(kwargs)

        return params

    def _estimate_token_usage(
            self,
            messages: Messages,
            response: str
    ) -> TokenUsage:
        """Estimate token usage."""
        prompt_text = self.format_messages(messages)
        prompt_tokens = self.count_tokens(prompt_text)
        completion_tokens = self.count_tokens(response)

        return TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens
        )

    def _transform_exception(self, exception: Exception) -> LLMFacadeException:
        """Transform provider exceptions to facade exceptions."""
        error_msg = str(exception).lower()

        if "rate limit" in error_msg or "429" in error_msg:
            return RateLimitException(str(exception))
        elif "unauthorized" in error_msg or "401" in error_msg:
            return AuthenticationException(str(exception))
        elif "timeout" in error_msg:
            return NetworkException(str(exception))
        else:
            return LLMFacadeException(str(exception))


# Convenience function for creating HuggingFace facade
def create_huggingface_llm(
        model_name: str,
        use_local: bool = False,
        **kwargs
) -> HuggingFaceLLMFacade:
    """
    Create a HuggingFace LLM Facade instance.

    Args:
        model_name: HuggingFace model identifier
        use_local: Use local model instead of API
        **kwargs: Additional configuration

    Returns:
        Configured HuggingFaceLLMFacade instance

    Example:
        >>> llm = create_huggingface_llm(
        ...     "meta-llama/Llama-2-7b-chat-hf",
        ...     use_local=False
        ... )
    """
    return HuggingFaceLLMFacade(model_name, use_local=use_local, **kwargs)


__all__ = ['HuggingFaceLLMFacade', 'create_huggingface_llm']