"""
AWS Bedrock LLM Facade Implementation

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
AWS Bedrock, supporting multiple foundation models including Claude, Llama,
Jurassic, Command, and Titan.
"""

import os
import json
import time
import asyncio
import base64
from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator, Callable, Tuple
from dataclasses import dataclass
import warnings

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
    ResponseFormat,
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


class AWSBedrockLLMFacade(LLMFacade):
    """
    AWS Bedrock implementation of the LLMFacade interface.

    Supports multiple foundation models through AWS Bedrock:
    - Anthropic Claude (all versions)
    - Meta Llama 2 and 3
    - AI21 Labs Jurassic
    - Cohere Command
    - Amazon Titan
    - Stability AI Stable Diffusion

    Features:
    - Unified interface across providers
    - Streaming responses
    - Vision capabilities (Claude 3)
    - Tool/function calling (Claude 3)
    - Embeddings (Titan, Cohere)
    - Image generation (Stable Diffusion, Titan)

    Example:
        >>> llm = AWSBedrockLLMFacade(
        ...     model_name="anthropic.claude-3-sonnet-20240229-v1:0",
        ...     region_name="us-east-1"
        ... )
        >>> response = llm.chat_completion([
        ...     {"role": "user", "content": "Hello!"}
        ... ])
    """

    # Model configurations
    MODEL_INFO = {
        "anthropic.claude-3-5-sonnet-20241022-v2:0": {
            "provider": "anthropic",
            "max_tokens": 8096,
            "context_window": 200000,
            "supports_vision": True,
            "supports_tools": True
        },
        "anthropic.claude-3-sonnet-20240229-v1:0": {
            "provider": "anthropic",
            "max_tokens": 4096,
            "context_window": 200000,
            "supports_vision": True,
            "supports_tools": True
        },
        "anthropic.claude-3-haiku-20240307-v1:0": {
            "provider": "anthropic",
            "max_tokens": 4096,
            "context_window": 200000,
            "supports_vision": True,
            "supports_tools": True
        },
        "meta.llama3-70b-instruct-v1:0": {
            "provider": "meta",
            "max_tokens": 2048,
            "context_window": 8192,
            "supports_vision": False,
            "supports_tools": False
        },
        "meta.llama3-8b-instruct-v1:0": {
            "provider": "meta",
            "max_tokens": 2048,
            "context_window": 8192,
            "supports_vision": False,
            "supports_tools": False
        },
        "cohere.command-r-plus-v1:0": {
            "provider": "cohere",
            "max_tokens": 4096,
            "context_window": 128000,
            "supports_vision": False,
            "supports_tools": True
        },
        "ai21.j2-ultra-v1": {
            "provider": "ai21",
            "max_tokens": 8192,
            "context_window": 8192,
            "supports_vision": False,
            "supports_tools": False
        },
        "amazon.titan-text-premier-v1:0": {
            "provider": "amazon",
            "max_tokens": 3072,
            "context_window": 32000,
            "supports_vision": False,
            "supports_tools": False
        }
    }

    def __init__(
            self,
            model_name: str,
            api_key: Optional[str] = None,
            base_url: Optional[str] = None,
            timeout: Optional[float] = None,
            max_retries: int = 3,
            region_name: Optional[str] = None,
            **kwargs
    ) -> None:
        """
        Initialize AWS Bedrock LLM Facade.

        Args:
            model_name: Bedrock model identifier (e.g., "anthropic.claude-3-sonnet-20240229-v1:0")
            api_key: Not used (AWS credentials from env/config)
            base_url: Not used for Bedrock
            timeout: Request timeout in seconds (default: 300)
            max_retries: Number of retry attempts for failed requests
            region_name: AWS region (default: us-east-1)
            **kwargs: Additional configuration
                - aws_access_key_id: AWS access key
                - aws_secret_access_key: AWS secret key
                - aws_session_token: AWS session token
                - profile_name: AWS profile name
        """
        self.model_name = model_name
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")
        self.timeout = timeout or 300.0
        self.max_retries = max_retries
        self.kwargs = kwargs

        # Initialize client
        self._initialize_client()

        # Detect provider from model name
        self.provider = self._detect_provider()

        # Model info cache
        self._model_info = None

    def _initialize_client(self):
        """Initialize AWS Bedrock client."""
        try:
            import boto3
            from botocore.config import Config
            
            # Configure boto3
            config = Config(
                region_name=self.region_name,
                retries={'max_attempts': self.max_retries},
                read_timeout=self.timeout,
                connect_timeout=self.timeout
            )
            
            # Create session
            session_kwargs = {}
            if "aws_access_key_id" in self.kwargs:
                session_kwargs["aws_access_key_id"] = self.kwargs["aws_access_key_id"]
            if "aws_secret_access_key" in self.kwargs:
                session_kwargs["aws_secret_access_key"] = self.kwargs["aws_secret_access_key"]
            if "aws_session_token" in self.kwargs:
                session_kwargs["aws_session_token"] = self.kwargs["aws_session_token"]
            if "profile_name" in self.kwargs:
                session_kwargs["profile_name"] = self.kwargs["profile_name"]
            
            session = boto3.Session(**session_kwargs) if session_kwargs else boto3.Session()
            
            # Create clients
            self.client = session.client('bedrock-runtime', config=config)
            
        except ImportError:
            raise ImportError(
                "Please install boto3: pip install boto3"
            )
        except Exception as e:
            raise AuthenticationException(f"Failed to initialize AWS Bedrock client: {e}")

    def _detect_provider(self) -> str:
        """Detect provider from model name."""
        if "anthropic" in self.model_name.lower():
            return "anthropic"
        elif "meta" in self.model_name.lower() or "llama" in self.model_name.lower():
            return "meta"
        elif "cohere" in self.model_name.lower():
            return "cohere"
        elif "ai21" in self.model_name.lower():
            return "ai21"
        elif "amazon" in self.model_name.lower() or "titan" in self.model_name.lower():
            return "amazon"
        elif "stability" in self.model_name.lower():
            return "stability"
        else:
            return "unknown"

    def get_capabilities(self) -> List[ModelCapability]:
        """Get list of capabilities supported by the model."""
        capabilities = [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CHAT_COMPLETION,
            ModelCapability.STREAMING
        ]
        
        model_config = self.MODEL_INFO.get(self.model_name, {})
        
        if model_config.get("supports_tools", False):
            capabilities.extend([
                ModelCapability.FUNCTION_CALLING,
                ModelCapability.TOOL_USE
            ])
        
        if model_config.get("supports_vision", False):
            capabilities.extend([
                ModelCapability.VISION,
                ModelCapability.IMAGE_UNDERSTANDING,
                ModelCapability.MULTIMODAL
            ])
        
        # Provider-specific capabilities
        if self.provider == "anthropic":
            capabilities.extend([
                ModelCapability.CODE_GENERATION,
                ModelCapability.REASONING
            ])
        
        if self.provider in ["amazon", "cohere"]:
            capabilities.append(ModelCapability.EMBEDDINGS)
        
        if self.provider == "stability":
            capabilities.append(ModelCapability.IMAGE_GENERATION)
        
        return capabilities

    def supports_capability(self, capability: ModelCapability) -> bool:
        """Check if model supports a specific capability."""
        return capability in self.get_capabilities()

    def get_model_info(self) -> Dict[str, Any]:
        """Get detailed model information."""
        if self._model_info is None:
            config = self.MODEL_INFO.get(self.model_name, {
                "provider": self.provider,
                "max_tokens": 2048,
                "context_window": 8192,
                "supports_vision": False,
                "supports_tools": False
            })
            
            self._model_info = {
                "provider": f"aws_bedrock_{config['provider']}",
                "name": self.model_name,
                "version": "latest",
                "max_input_tokens": config["context_window"],
                "max_output_tokens": config["max_tokens"],
                "context_window": config["context_window"],
                "supports_streaming": True,
                "supports_functions": config["supports_tools"],
                "supports_vision": config["supports_vision"],
                "modalities": ["text", "image"] if config["supports_vision"] else ["text"]
            }
        
        return self._model_info

    # =========================================================================
    # Core Generation Methods
    # =========================================================================

    def text_generation(
            self,
            prompt: str,
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> str:
        """Generate text completion for a prompt."""
        start_time = time.time()
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            # Build request body based on provider
            body = self._build_request_body(messages, config, **kwargs)
            
            # Invoke model
            response = self.client.invoke_model(
                modelId=self.model_name,
                body=json.dumps(body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            text = self._extract_text_from_response(response_body)
            
            return text
            
        except Exception as e:
            raise self._transform_exception(e)

    async def async_text_generation(
            self,
            prompt: str,
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> str:
        """Generate text completion asynchronously."""
        # AWS Bedrock doesn't have native async, use thread pool
        import concurrent.futures
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                lambda: self.text_generation(prompt, config=config, **kwargs)
            )
        return result

    def stream_text_generation(
            self,
            prompt: str,
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> TextStream:
        """Stream text generation."""
        try:
            messages = [{"role": "user", "content": prompt}]
            body = self._build_request_body(messages, config, **kwargs)
            
            response = self.client.invoke_model_with_response_stream(
                modelId=self.model_name,
                body=json.dumps(body)
            )
            
            for event in response['body']:
                chunk = json.loads(event['chunk']['bytes'].decode())
                text = self._extract_text_from_stream_chunk(chunk)
                if text:
                    yield text
                    
        except Exception as e:
            raise self._transform_exception(e)

    async def async_stream_text_generation(
            self,
            prompt: str,
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> AsyncIterator[str]:
        """Stream text generation asynchronously."""
        # Convert sync generator to async
        for chunk in self.stream_text_generation(prompt, config=config, **kwargs):
            yield chunk

    def chat_completion(
            self,
            messages: Messages,
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """Generate chat completion."""
        start_time = time.time()
        
        try:
            body = self._build_request_body(messages, config, **kwargs)
            
            response = self.client.invoke_model(
                modelId=self.model_name,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            
            return self._format_chat_response(response_body, time.time() - start_time)
            
        except Exception as e:
            raise self._transform_exception(e)

    async def async_chat_completion(
            self,
            messages: Messages,
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """Generate chat completion asynchronously."""
        import concurrent.futures
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                lambda: self.chat_completion(messages, config=config, **kwargs)
            )
        return result

    def stream_chat_completion(
            self,
            messages: Messages,
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> DeltaStream:
        """Stream chat completion with delta updates."""
        try:
            body = self._build_request_body(messages, config, **kwargs)
            
            response = self.client.invoke_model_with_response_stream(
                modelId=self.model_name,
                body=json.dumps(body)
            )
            
            for event in response['body']:
                chunk = json.loads(event['chunk']['bytes'].decode())
                yield {
                    "type": "content_delta",
                    "delta": {"content": self._extract_text_from_stream_chunk(chunk)}
                }
                
        except Exception as e:
            raise self._transform_exception(e)

    async def async_stream_chat_completion(
            self,
            messages: Messages,
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream chat completion asynchronously."""
        for chunk in self.stream_chat_completion(messages, config=config, **kwargs):
            yield chunk

    # =========================================================================
    # Function/Tool Calling
    # =========================================================================

    def chat_completion_with_tools(
            self,
            messages: Messages,
            tools: List[ToolDefinition],
            *,
            tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """Chat completion with tool/function calling support."""
        if not self.supports_capability(ModelCapability.FUNCTION_CALLING):
            raise CapabilityNotSupportedException("function_calling", self.model_name)
        
        start_time = time.time()
        
        try:
            # Build request with tools
            body = self._build_request_body(messages, config, **kwargs)
            
            # Add tools based on provider
            if self.provider == "anthropic":
                body["tools"] = self._convert_tools_to_anthropic_format(tools)
                if tool_choice:
                    body["tool_choice"] = tool_choice
            elif self.provider == "cohere":
                body["tools"] = tools
            
            response = self.client.invoke_model(
                modelId=self.model_name,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            return self._format_chat_response(response_body, time.time() - start_time)
            
        except Exception as e:
            raise self._transform_exception(e)

    async def async_chat_completion_with_tools(
            self,
            messages: Messages,
            tools: List[ToolDefinition],
            *,
            tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """Async chat completion with tools."""
        import concurrent.futures
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                lambda: self.chat_completion_with_tools(messages, tools, tool_choice=tool_choice, config=config, **kwargs)
            )
        return result

    def execute_tool_calls(
            self,
            tool_calls: List[ToolCall],
            available_tools: Dict[str, Callable],
            **kwargs
    ) -> List[ToolResult]:
        """Execute tool calls and return results."""
        results = []
        
        for tool_call in tool_calls:
            if self.provider == "anthropic":
                tool_name = tool_call.get("name")
                tool_input = tool_call.get("input", {})
                tool_id = tool_call.get("id")
            else:
                tool_name = tool_call.get("function", {}).get("name")
                tool_input = json.loads(tool_call.get("function", {}).get("arguments", "{}"))
                tool_id = tool_call.get("id")
            
            if tool_name not in available_tools:
                raise ToolNotFoundException(tool_name)
            
            try:
                func = available_tools[tool_name]
                output = func(**tool_input) if isinstance(tool_input, dict) else func(tool_input)
                
                results.append({
                    "tool_call_id": tool_id,
                    "content": str(output)
                })
                
            except Exception as e:
                raise ToolExecutionException(tool_name, str(e))
        
        return results

    # =========================================================================
    # Vision/Multimodal
    # =========================================================================

    def chat_completion_with_vision(
            self,
            messages: Messages,
            images: List[ImageInput],
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """Chat completion with image understanding."""
        if not self.supports_capability(ModelCapability.VISION):
            raise CapabilityNotSupportedException("vision", self.model_name)
        
        start_time = time.time()
        
        try:
            # Embed images in messages
            processed_messages = self._embed_images_in_messages(messages, images)
            
            body = self._build_request_body(processed_messages, config, **kwargs)
            
            response = self.client.invoke_model(
                modelId=self.model_name,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            return self._format_chat_response(response_body, time.time() - start_time)
            
        except Exception as e:
            raise self._transform_exception(e)

    async def async_chat_completion_with_vision(
            self,
            messages: Messages,
            images: List[ImageInput],
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """Async chat completion with vision."""
        import concurrent.futures
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                lambda: self.chat_completion_with_vision(messages, images, config=config, **kwargs)
            )
        return result

    # =========================================================================
    # Embeddings
    # =========================================================================

    def embed_text(
            self,
            text: Union[str, List[str]],
            **kwargs
    ) -> Union[Embedding, List[Embedding]]:
        """Generate embeddings for text."""
        if not self.supports_capability(ModelCapability.EMBEDDINGS):
            raise CapabilityNotSupportedException("embeddings", self.model_name)
        
        try:
            is_single = isinstance(text, str)
            texts = [text] if is_single else text
            
            embeddings = []
            for t in texts:
                body = {"inputText": t}
                
                response = self.client.invoke_model(
                    modelId=self.model_name,
                    body=json.dumps(body)
                )
                
                response_body = json.loads(response['body'].read())
                embedding = response_body.get("embedding", [])
                embeddings.append(embedding)
            
            return embeddings[0] if is_single else embeddings
            
        except Exception as e:
            raise self._transform_exception(e)

    async def async_embed_text(
            self,
            text: Union[str, List[str]],
            **kwargs
    ) -> Union[Embedding, List[Embedding]]:
        """Generate embeddings asynchronously."""
        import concurrent.futures
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                lambda: self.embed_text(text, **kwargs)
            )
        return result

    # =========================================================================
    # Image Generation
    # =========================================================================

    def generate_image(
            self,
            prompt: str,
            *,
            size: str = "1024x1024",
            **kwargs
    ) -> ImageOutput:
        """Generate image using Stable Diffusion."""
        if not self.supports_capability(ModelCapability.IMAGE_GENERATION):
            raise CapabilityNotSupportedException("image_generation", self.model_name)
        
        try:
            body = {
                "text_prompts": [{"text": prompt}],
                "cfg_scale": kwargs.get("cfg_scale", 7),
                "steps": kwargs.get("steps", 50),
                "seed": kwargs.get("seed", 0)
            }
            
            response = self.client.invoke_model(
                modelId=self.model_name,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            
            # Return base64 image data
            if "artifacts" in response_body:
                return response_body["artifacts"][0]["base64"]
            
            return ""
            
        except Exception as e:
            raise self._transform_exception(e)

    def edit_image(self, image: ImageInput, prompt: str, **kwargs) -> ImageOutput:
        """Image editing not supported."""
        raise CapabilityNotSupportedException("image_editing", self.model_name)

    # =========================================================================
    # Not Supported Methods
    # =========================================================================

    def transcribe_audio(self, audio: Union[bytes, str], **kwargs) -> str:
        """Audio transcription not supported."""
        raise CapabilityNotSupportedException("audio_transcription", self.model_name)

    def generate_audio(self, text: str, **kwargs) -> bytes:
        """Audio generation not supported."""
        raise CapabilityNotSupportedException("audio_generation", self.model_name)

    def moderate_content(
            self,
            content: Union[str, List[str]],
            **kwargs
    ) -> Union[ModerationResult, List[ModerationResult]]:
        """Content moderation not directly supported."""
        if isinstance(content, str):
            return {"flagged": False, "categories": {}, "scores": {}}
        return [{"flagged": False, "categories": {}, "scores": {}} for _ in content]

    def retrieve_documents(self, query: str, **kwargs) -> RetrievalResult:
        """Document retrieval not directly supported."""
        raise CapabilityNotSupportedException("rag", self.model_name)

    def batch_generate(self, prompts: List[str], **kwargs) -> List[str]:
        """Batch generation."""
        return [self.text_generation(p, **kwargs) for p in prompts]

    def batch_embed(self, texts: List[str], **kwargs) -> List[Embedding]:
        """Batch embedding."""
        return self.embed_text(texts, **kwargs)

    def create_fine_tuning_job(self, training_file: str, **kwargs) -> str:
        """Fine-tuning through Bedrock console."""
        raise NotImplementedError("Fine-tuning managed through AWS Console")

    def get_fine_tuning_status(self, job_id: str, **kwargs) -> Dict[str, Any]:
        """Fine-tuning status not available via API."""
        raise NotImplementedError("Fine-tuning status managed through AWS Console")

    # =========================================================================
    # Token Management
    # =========================================================================

    def count_tokens(self, text: str, **kwargs) -> int:
        """Count tokens in text (estimation)."""
        # Bedrock doesn't provide token counting API
        return len(text) // 4

    def count_message_tokens(self, messages: Messages, **kwargs) -> int:
        """Count tokens in messages."""
        text = self.format_messages(messages)
        return self.count_tokens(text)

    def truncate_text(self, text: str, max_tokens: int, **kwargs) -> str:
        """Truncate text to fit within token limit."""
        estimated_chars = max_tokens * 4
        return text[:estimated_chars]

    def get_context_window(self) -> int:
        """Get maximum context window size."""
        return self.get_model_info()["context_window"]

    def get_max_output_tokens(self) -> int:
        """Get maximum output tokens."""
        return self.get_model_info()["max_output_tokens"]

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
        """Log request for monitoring."""
        pass

    def get_usage_stats(self, period: str = "day", **kwargs) -> Dict[str, Any]:
        """Get usage statistics."""
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
            
            if isinstance(content, list):
                # Handle multimodal content
                text_parts = [c.get("text", "") for c in content if c.get("type") == "text"]
                content = " ".join(text_parts)
            
            if role == "system":
                formatted += f"System: {content}\n\n"
            elif role == "user":
                formatted += f"Human: {content}\n\n"
            elif role == "assistant":
                formatted += f"Assistant: {content}\n\n"
        
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
        
        max_tokens = config.get("max_tokens", 0)
        if max_tokens > self.get_max_output_tokens():
            errors.append(f"max_tokens exceeds limit of {self.get_max_output_tokens()}")
        
        return (len(errors) == 0, errors)

    def health_check(self, **kwargs) -> bool:
        """Check if service is healthy."""
        try:
            response = self.text_generation(
                "Hi",
                config=GenerationConfig(max_tokens=5)
            )
            return True
        except:
            return False

    def close(self) -> None:
        """Close connections and cleanup."""
        self.client = None

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _build_request_body(
            self,
            messages: Messages,
            config: Optional[GenerationConfig],
            **kwargs
    ) -> Dict[str, Any]:
        """Build request body based on provider."""
        if self.provider == "anthropic":
            return self._build_anthropic_body(messages, config, **kwargs)
        elif self.provider == "meta":
            return self._build_meta_body(messages, config, **kwargs)
        elif self.provider == "cohere":
            return self._build_cohere_body(messages, config, **kwargs)
        elif self.provider == "ai21":
            return self._build_ai21_body(messages, config, **kwargs)
        elif self.provider == "amazon":
            return self._build_amazon_body(messages, config, **kwargs)
        else:
            # Generic format
            return self._build_generic_body(messages, config, **kwargs)

    def _build_anthropic_body(
            self,
            messages: Messages,
            config: Optional[GenerationConfig],
            **kwargs
    ) -> Dict[str, Any]:
        """Build Anthropic Claude request body."""
        # Extract system message
        system_message = None
        processed_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                processed_messages.append(msg)
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": processed_messages,
            "max_tokens": 4096
        }
        
        if system_message:
            body["system"] = system_message
        
        if config:
            if config.max_tokens:
                body["max_tokens"] = config.max_tokens
            if config.temperature is not None:
                body["temperature"] = config.temperature
            if config.top_p is not None:
                body["top_p"] = config.top_p
            if config.top_k is not None:
                body["top_k"] = config.top_k
            if config.stop_sequences:
                body["stop_sequences"] = config.stop_sequences
        
        return body

    def _build_meta_body(
            self,
            messages: Messages,
            config: Optional[GenerationConfig],
            **kwargs
    ) -> Dict[str, Any]:
        """Build Meta Llama request body."""
        prompt = self.format_messages(messages)
        
        body = {
            "prompt": prompt,
            "max_gen_len": 512
        }
        
        if config:
            if config.max_tokens:
                body["max_gen_len"] = config.max_tokens
            if config.temperature is not None:
                body["temperature"] = config.temperature
            if config.top_p is not None:
                body["top_p"] = config.top_p
        
        return body

    def _build_cohere_body(
            self,
            messages: Messages,
            config: Optional[GenerationConfig],
            **kwargs
    ) -> Dict[str, Any]:
        """Build Cohere Command request body."""
        # Extract last user message as prompt
        prompt = messages[-1]["content"] if messages else ""
        
        # Build chat history
        chat_history = []
        for msg in messages[:-1]:
            chat_history.append({
                "role": "USER" if msg["role"] == "user" else "CHATBOT",
                "message": msg["content"]
            })
        
        body = {
            "message": prompt,
            "chat_history": chat_history
        }
        
        if config:
            if config.max_tokens:
                body["max_tokens"] = config.max_tokens
            if config.temperature is not None:
                body["temperature"] = config.temperature
            if config.top_p is not None:
                body["p"] = config.top_p
        
        return body

    def _build_ai21_body(
            self,
            messages: Messages,
            config: Optional[GenerationConfig],
            **kwargs
    ) -> Dict[str, Any]:
        """Build AI21 Jurassic request body."""
        prompt = self.format_messages(messages)
        
        body = {
            "prompt": prompt,
            "maxTokens": 200
        }
        
        if config:
            if config.max_tokens:
                body["maxTokens"] = config.max_tokens
            if config.temperature is not None:
                body["temperature"] = config.temperature
            if config.top_p is not None:
                body["topP"] = config.top_p
        
        return body

    def _build_amazon_body(
            self,
            messages: Messages,
            config: Optional[GenerationConfig],
            **kwargs
    ) -> Dict[str, Any]:
        """Build Amazon Titan request body."""
        prompt = self.format_messages(messages)
        
        body = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 512,
                "temperature": 0.7,
                "topP": 0.9
            }
        }
        
        if config:
            text_config = body["textGenerationConfig"]
            if config.max_tokens:
                text_config["maxTokenCount"] = config.max_tokens
            if config.temperature is not None:
                text_config["temperature"] = config.temperature
            if config.top_p is not None:
                text_config["topP"] = config.top_p
            if config.stop_sequences:
                text_config["stopSequences"] = config.stop_sequences
        
        return body

    def _build_generic_body(
            self,
            messages: Messages,
            config: Optional[GenerationConfig],
            **kwargs
    ) -> Dict[str, Any]:
        """Build generic request body."""
        return {
            "messages": messages,
            "max_tokens": config.max_tokens if config and config.max_tokens else 512
        }

    def _extract_text_from_response(self, response_body: Dict[str, Any]) -> str:
        """Extract text from response based on provider."""
        if self.provider == "anthropic":
            content = response_body.get("content", [])
            for block in content:
                if block.get("type") == "text":
                    return block.get("text", "")
        elif self.provider == "meta":
            return response_body.get("generation", "")
        elif self.provider == "cohere":
            return response_body.get("text", "")
        elif self.provider == "ai21":
            completions = response_body.get("completions", [])
            if completions:
                return completions[0].get("data", {}).get("text", "")
        elif self.provider == "amazon":
            results = response_body.get("results", [])
            if results:
                return results[0].get("outputText", "")
        
        return ""

    def _extract_text_from_stream_chunk(self, chunk: Dict[str, Any]) -> str:
        """Extract text from stream chunk."""
        if self.provider == "anthropic":
            delta = chunk.get("delta", {})
            return delta.get("text", "")
        elif self.provider == "meta":
            return chunk.get("generation", "")
        elif self.provider == "amazon":
            return chunk.get("outputText", "")
        
        return ""

    def _format_chat_response(
            self,
            response_body: Dict[str, Any],
            latency: float
    ) -> Dict[str, Any]:
        """Format response to standard format."""
        text = self._extract_text_from_response(response_body)
        
        # Extract usage if available
        usage = None
        if self.provider == "anthropic":
            usage_data = response_body.get("usage", {})
            if usage_data:
                usage = TokenUsage(
                    prompt_tokens=usage_data.get("input_tokens", 0),
                    completion_tokens=usage_data.get("output_tokens", 0),
                    total_tokens=usage_data.get("input_tokens", 0) + usage_data.get("output_tokens", 0)
                )
        
        metadata = CompletionMetadata(
            model=self.model_name,
            finish_reason=response_body.get("stop_reason") or response_body.get("finish_reason"),
            usage=usage,
            latency_ms=latency * 1000
        )
        
        # Extract tool calls if present
        tool_calls = None
        if self.provider == "anthropic":
            content = response_body.get("content", [])
            for block in content:
                if block.get("type") == "tool_use":
                    if not tool_calls:
                        tool_calls = []
                    tool_calls.append({
                        "id": block.get("id"),
                        "type": "tool_use",
                        "name": block.get("name"),
                        "input": block.get("input", {})
                    })
        
        return {
            "content": text,
            "role": "assistant",
            "tool_calls": tool_calls,
            "metadata": metadata
        }

    def _convert_tools_to_anthropic_format(
            self,
            tools: List[ToolDefinition]
    ) -> List[Dict[str, Any]]:
        """Convert tools to Anthropic format."""
        anthropic_tools = []
        
        for tool in tools:
            if tool.get("type") == "function":
                func = tool.get("function", {})
                anthropic_tools.append({
                    "name": func.get("name"),
                    "description": func.get("description", ""),
                    "input_schema": func.get("parameters", {})
                })
        
        return anthropic_tools

    def _embed_images_in_messages(
            self,
            messages: Messages,
            images: List[ImageInput]
    ) -> Messages:
        """Embed images into messages."""
        processed_messages = []
        image_idx = 0
        
        for msg in messages:
            if msg["role"] == "user" and image_idx < len(images):
                content = []
                
                # Add images
                for img in images[image_idx:]:
                    img_data = self._process_image(img)
                    content.append(img_data)
                
                # Add text
                if isinstance(msg["content"], str):
                    content.append({"type": "text", "text": msg["content"]})
                
                processed_messages.append({
                    "role": "user",
                    "content": content
                })
                image_idx = len(images)
            else:
                processed_messages.append(msg)
        
        return processed_messages

    def _process_image(self, image: ImageInput) -> Dict[str, Any]:
        """Process image for Bedrock."""
        if isinstance(image, str):
            if image.startswith("http"):
                import requests
                response = requests.get(image)
                image_data = base64.b64encode(response.content).decode()
                media_type = "image/jpeg"
            else:
                with open(image, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode()
                media_type = "image/jpeg"
        elif isinstance(image, bytes):
            image_data = base64.b64encode(image).decode()
            media_type = "image/jpeg"
        else:
            from io import BytesIO
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            image_data = base64.b64encode(buffer.getvalue()).decode()
            media_type = "image/png"
        
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": image_data
            }
        }

    def _transform_exception(self, exception: Exception) -> LLMFacadeException:
        """Transform AWS exceptions to facade exceptions."""
        error_msg = str(exception).lower()
        
        if "throttl" in error_msg or "rate" in error_msg:
            return RateLimitException(str(exception))
        elif "access denied" in error_msg or "unauthorized" in error_msg:
            return AuthenticationException(str(exception))
        elif "timeout" in error_msg:
            return NetworkException(str(exception))
        else:
            return LLMFacadeException(str(exception))


def create_bedrock_llm(
        model_name: str,
        region_name: str = "us-east-1",
        **kwargs
) -> AWSBedrockLLMFacade:
    """
    Create an AWS Bedrock LLM Facade instance.

    Args:
        model_name: Bedrock model identifier
        region_name: AWS region
        **kwargs: Additional configuration

    Returns:
        Configured AWSBedrockLLMFacade instance

    Example:
        >>> llm = create_bedrock_llm(
        ...     "anthropic.claude-3-sonnet-20240229-v1:0",
        ...     region_name="us-west-2"
        ... )
    """
    return AWSBedrockLLMFacade(model_name, region_name=region_name, **kwargs)


__all__ = ['AWSBedrockLLMFacade', 'create_bedrock_llm']
