"""
Mock LLM Facade Implementation

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
This module provides a mock implementation of the LLMFacade interface for
testing, development, and offline scenarios without requiring actual API calls.
"""

import time
import asyncio
import random
from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator, Callable, Tuple

from llm_facade import (
    LLMFacade, ModelCapability, GenerationConfig, TokenUsage, CompletionMetadata,
    Messages, TextStream, DeltaStream, ToolDefinition, ToolCall, ToolResult,
    Document, RetrievalResult, Embedding, ImageInput, ImageOutput,
    ModerationResult, SafetyResult, ResponseFormat, LLMFacadeException,
    CapabilityNotSupportedException, RateLimitException, ContentFilterException,
    ContextLengthExceededException, ToolNotFoundException, ToolExecutionException,
    InvalidResponseException, AuthenticationException, NetworkException
)


class MockLLMFacade(LLMFacade):
    """
    Mock implementation of the LLMFacade interface.

    Provides deterministic or randomized responses for:
    - Testing LLM integrations
    - Development without API costs
    - Offline development
    - CI/CD pipelines
    - Load testing
    - Response simulation

    Features:
    - Configurable response patterns
    - Simulated latency
    - All capabilities supported
    - Error simulation
    - Token counting
    - Deterministic or random mode

    Example:
        >>> llm = MockLLMFacade(
        ...     model_name="mock-gpt-4",
        ...     deterministic=True,
        ...     simulate_latency=True
        ... )
        >>> response = llm.chat_completion([
        ...     {"role": "user", "content": "Hello!"}
        ... ])
    """

    def __init__(self, model_name: str = "mock-llm", api_key: Optional[str] = None,
                 base_url: Optional[str] = None, timeout: Optional[float] = None,
                 max_retries: int = 3, deterministic: bool = False,
                 simulate_latency: bool = False, error_rate: float = 0.0,
                 **kwargs) -> None:
        """
        Initialize Mock LLM Facade.

        Args:
            model_name: Mock model identifier
            api_key: Not required (accepts any value)
            base_url: Not used
            timeout: Simulated timeout
            max_retries: Not used
            deterministic: If True, always return same response
            simulate_latency: If True, add realistic delays
            error_rate: Probability of simulating errors (0.0-1.0)
            **kwargs: Additional config
                - default_response: Default text response
                - response_templates: Dict of response templates
        """
        self.model_name = model_name
        self.deterministic = deterministic
        self.simulate_latency = simulate_latency
        self.error_rate = error_rate
        self.kwargs = kwargs
        
        # Default responses
        self.default_response = kwargs.get(
            "default_response",
            "This is a mock response from the LLM. In production, this would be a real AI-generated response."
        )
        
        self.response_templates = kwargs.get("response_templates", {})
        
        # Call counters for testing
        self.call_count = 0
        self.total_tokens = 0
        
        self._model_info = None

    def _simulate_delay(self):
        """Simulate realistic API latency."""
        if self.simulate_latency:
            delay = random.uniform(0.1, 2.0) if not self.deterministic else 0.5
            time.sleep(delay)

    def _should_error(self):
        """Determine if should simulate an error."""
        return random.random() < self.error_rate

    def _generate_response(self, prompt: str, max_tokens: int = 100) -> str:
        """Generate a mock response."""
        if self.deterministic:
            return self.default_response[:max_tokens * 4]
        
        # Check for templates
        for keyword, template in self.response_templates.items():
            if keyword.lower() in prompt.lower():
                return template
        
        # Generate varied response
        responses = [
            f"Mock response to: {prompt[:50]}...",
            "This is a simulated AI response for testing purposes.",
            f"I understand you asked about '{prompt[:30]}...'. Here's a mock answer.",
            "Mock LLM: Processing your request and generating a test response.",
        ]
        
        return random.choice(responses) if not self.deterministic else responses[0]

    def get_capabilities(self) -> List[ModelCapability]:
        """Mock supports all capabilities."""
        return [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CHAT_COMPLETION,
            ModelCapability.STREAMING,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.TOOL_USE,
            ModelCapability.JSON_MODE,
            ModelCapability.CODE_GENERATION,
            ModelCapability.VISION,
            ModelCapability.IMAGE_UNDERSTANDING,
            ModelCapability.IMAGE_GENERATION,
            ModelCapability.EMBEDDINGS,
            ModelCapability.REASONING,
            ModelCapability.MULTIMODAL
        ]

    def supports_capability(self, capability: ModelCapability) -> bool:
        """Mock supports everything."""
        return True

    def get_model_info(self) -> Dict[str, Any]:
        """Get mock model information."""
        if self._model_info is None:
            self._model_info = {
                "provider": "mock",
                "name": self.model_name,
                "version": "1.0.0",
                "max_input_tokens": 100000,
                "max_output_tokens": 4096,
                "context_window": 100000,
                "supports_streaming": True,
                "supports_functions": True,
                "supports_vision": True,
                "modalities": ["text", "image", "audio", "video"],
                "is_mock": True
            }
        return self._model_info

    def text_generation(self, prompt: str, *, config: Optional[GenerationConfig] = None,
                       **kwargs) -> str:
        """Generate mock text."""
        self._simulate_delay()
        self.call_count += 1
        
        if self._should_error():
            raise NetworkException("Mock network error")
        
        max_tokens = config.max_tokens if config and config.max_tokens else 100
        response = self._generate_response(prompt, max_tokens)
        
        self.total_tokens += len(response) // 4
        return response

    async def async_text_generation(self, prompt: str, *, config: Optional[GenerationConfig] = None,
                                    **kwargs) -> str:
        """Async mock generation."""
        if self.simulate_latency:
            await asyncio.sleep(0.5 if self.deterministic else random.uniform(0.1, 1.0))
        
        return self.text_generation(prompt, config=config, **kwargs)

    def stream_text_generation(self, prompt: str, *, config: Optional[GenerationConfig] = None,
                               **kwargs) -> TextStream:
        """Stream mock text."""
        response = self.text_generation(prompt, config=config, **kwargs)
        
        # Simulate streaming by yielding chunks
        chunk_size = 10
        for i in range(0, len(response), chunk_size):
            chunk = response[i:i + chunk_size]
            if self.simulate_latency:
                time.sleep(0.05)
            yield chunk

    async def async_stream_text_generation(self, prompt: str, *,
                                          config: Optional[GenerationConfig] = None,
                                          **kwargs) -> AsyncIterator[str]:
        """Async stream mock text."""
        response = self.text_generation(prompt, config=config, **kwargs)
        
        chunk_size = 10
        for i in range(0, len(response), chunk_size):
            chunk = response[i:i + chunk_size]
            if self.simulate_latency:
                await asyncio.sleep(0.05)
            yield chunk

    def chat_completion(self, messages: Messages, *, config: Optional[GenerationConfig] = None,
                       **kwargs) -> Dict[str, Any]:
        """Mock chat completion."""
        start_time = time.time()
        self._simulate_delay()
        
        last_message = messages[-1]["content"] if messages else "Hello"
        response_text = self._generate_response(last_message)
        
        usage = TokenUsage(
            prompt_tokens=sum(len(m.get("content", "")) // 4 for m in messages),
            completion_tokens=len(response_text) // 4,
            total_tokens=0
        )
        usage.total_tokens = usage.prompt_tokens + usage.completion_tokens
        
        metadata = CompletionMetadata(
            model=self.model_name,
            finish_reason="stop",
            usage=usage,
            latency_ms=(time.time() - start_time) * 1000
        )
        
        return {
            "content": response_text,
            "role": "assistant",
            "tool_calls": None,
            "metadata": metadata
        }

    async def async_chat_completion(self, messages: Messages, *,
                                    config: Optional[GenerationConfig] = None,
                                    **kwargs) -> Dict[str, Any]:
        """Async mock chat completion."""
        if self.simulate_latency:
            await asyncio.sleep(0.5 if self.deterministic else random.uniform(0.1, 1.0))
        
        return self.chat_completion(messages, config=config, **kwargs)

    def stream_chat_completion(self, messages: Messages, *, config: Optional[GenerationConfig] = None,
                               **kwargs) -> DeltaStream:
        """Stream mock chat."""
        result = self.chat_completion(messages, config=config, **kwargs)
        content = result["content"]
        
        chunk_size = 10
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            if self.simulate_latency:
                time.sleep(0.05)
            yield {"type": "content_delta", "delta": {"content": chunk}}

    async def async_stream_chat_completion(self, messages: Messages, *,
                                          config: Optional[GenerationConfig] = None,
                                          **kwargs) -> AsyncIterator[Dict[str, Any]]:
        """Async stream mock chat."""
        result = self.chat_completion(messages, config=config, **kwargs)
        content = result["content"]
        
        chunk_size = 10
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            if self.simulate_latency:
                await asyncio.sleep(0.05)
            yield {"type": "content_delta", "delta": {"content": chunk}}

    def chat_completion_with_tools(self, messages: Messages, tools: List[ToolDefinition], *,
                                   tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
                                   config: Optional[GenerationConfig] = None,
                                   **kwargs) -> Dict[str, Any]:
        """Mock tool calling."""
        # Simulate calling first tool
        if tools:
            tool = tools[0]
            func = tool.get("function", {})
            
            tool_calls = [{
                "id": "mock_call_123",
                "type": "function",
                "function": {
                    "name": func.get("name"),
                    "arguments": "{}"
                }
            }]
            
            result = self.chat_completion(messages, config=config, **kwargs)
            result["tool_calls"] = tool_calls
            return result
        
        return self.chat_completion(messages, config=config, **kwargs)

    async def async_chat_completion_with_tools(self, messages: Messages, tools: List[ToolDefinition], *,
                                              tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
                                              config: Optional[GenerationConfig] = None,
                                              **kwargs) -> Dict[str, Any]:
        """Async mock tool calling."""
        return self.chat_completion_with_tools(messages, tools, tool_choice=tool_choice,
                                              config=config, **kwargs)

    def execute_tool_calls(self, tool_calls: List[ToolCall], available_tools: Dict[str, Callable],
                          **kwargs) -> List[ToolResult]:
        """Mock tool execution."""
        results = []
        for tool_call in tool_calls:
            results.append({
                "tool_call_id": tool_call.get("id", "mock_id"),
                "content": "Mock tool execution result"
            })
        return results

    def chat_completion_with_vision(self, messages: Messages, images: List[ImageInput], *,
                                    config: Optional[GenerationConfig] = None,
                                    **kwargs) -> Dict[str, Any]:
        """Mock vision."""
        result = self.chat_completion(messages, config=config, **kwargs)
        result["content"] = f"Mock vision analysis: I can see {len(images)} image(s). " + result["content"]
        return result

    async def async_chat_completion_with_vision(self, messages: Messages, images: List[ImageInput], *,
                                               config: Optional[GenerationConfig] = None,
                                               **kwargs) -> Dict[str, Any]:
        """Async mock vision."""
        return self.chat_completion_with_vision(messages, images, config=config, **kwargs)

    def embed_text(self, text: Union[str, List[str]], **kwargs) -> Union[Embedding, List[Embedding]]:
        """Mock embeddings."""
        is_single = isinstance(text, str)
        texts = [text] if is_single else text
        
        embeddings = []
        for t in texts:
            # Generate deterministic embedding based on text
            embedding = [random.random() if not self.deterministic else 0.5 for _ in range(1536)]
            embeddings.append(embedding)
        
        return embeddings[0] if is_single else embeddings

    async def async_embed_text(self, text: Union[str, List[str]],
                              **kwargs) -> Union[Embedding, List[Embedding]]:
        """Async mock embeddings."""
        return self.embed_text(text, **kwargs)

    def generate_image(self, prompt: str, **kwargs) -> ImageOutput:
        """Mock image generation."""
        return f"mock://generated-image-{hash(prompt)}.png"

    def edit_image(self, image: ImageInput, prompt: str, **kwargs) -> ImageOutput:
        """Mock image editing."""
        return f"mock://edited-image-{hash(prompt)}.png"

    def transcribe_audio(self, audio: Union[bytes, str], **kwargs) -> str:
        """Mock transcription."""
        return "This is a mock transcription of the audio file."

    def generate_audio(self, text: str, **kwargs) -> bytes:
        """Mock audio generation."""
        return b"mock_audio_data"

    def moderate_content(self, content: Union[str, List[str]],
                        **kwargs) -> Union[ModerationResult, List[ModerationResult]]:
        """Mock moderation."""
        result = {"flagged": False, "categories": {}, "scores": {}}
        
        if isinstance(content, str):
            return result
        return [result for _ in content]

    def retrieve_documents(self, query: str, **kwargs) -> RetrievalResult:
        """Mock RAG."""
        docs = [
            ({"id": "doc1", "content": "Mock document 1", "metadata": {}}, 0.95),
            ({"id": "doc2", "content": "Mock document 2", "metadata": {}}, 0.85),
        ]
        return docs

    def batch_generate(self, prompts: List[str], **kwargs) -> List[str]:
        """Mock batch generation."""
        return [self.text_generation(p, **kwargs) for p in prompts]

    def batch_embed(self, texts: List[str], **kwargs) -> List[Embedding]:
        """Mock batch embedding."""
        return self.embed_text(texts, **kwargs)

    def create_fine_tuning_job(self, training_file: str, **kwargs) -> str:
        """Mock fine-tuning."""
        return "mock_job_12345"

    def get_fine_tuning_status(self, job_id: str, **kwargs) -> Dict[str, Any]:
        """Mock fine-tuning status."""
        return {
            "id": job_id,
            "status": "completed",
            "model": "mock-fine-tuned-model",
            "created_at": int(time.time()),
            "finished_at": int(time.time()),
            "error": None
        }

    def count_tokens(self, text: str, **kwargs) -> int:
        """Mock token counting."""
        return len(text) // 4

    def count_message_tokens(self, messages: Messages, **kwargs) -> int:
        """Mock message token counting."""
        return sum(len(m.get("content", "")) // 4 for m in messages)

    def truncate_text(self, text: str, max_tokens: int, **kwargs) -> str:
        """Mock truncation."""
        return text[:max_tokens * 4]

    def get_context_window(self) -> int:
        """Mock context window."""
        return 100000

    def get_max_output_tokens(self) -> int:
        """Mock max output."""
        return 4096

    def log_request(self, method: str, input_data: Any, response: Any, *,
                   latency_ms: Optional[float] = None, metadata: Optional[Dict[str, Any]] = None,
                   **kwargs) -> None:
        """Mock logging."""
        pass

    def get_usage_stats(self, period: str = "day", **kwargs) -> Dict[str, Any]:
        """Mock usage stats."""
        return {
            "total_requests": self.call_count,
            "total_tokens": self.total_tokens,
            "period": period
        }

    def format_messages(self, messages: Messages, **kwargs) -> str:
        """Format messages."""
        return "\n".join(f"{m['role']}: {m['content']}" for m in messages)

    def parse_tool_calls(self, response: Dict[str, Any], **kwargs) -> List[ToolCall]:
        """Parse tool calls."""
        return response.get("tool_calls", [])

    def validate_config(self, config: Dict[str, Any], **kwargs) -> Tuple[bool, List[str]]:
        """Validate config."""
        return (True, [])

    def health_check(self, **kwargs) -> bool:
        """Health check."""
        return True

    def close(self) -> None:
        """Close (no-op)."""
        pass


def create_mock_llm(model_name: str = "mock-llm", deterministic: bool = False,
                   simulate_latency: bool = False, **kwargs) -> MockLLMFacade:
    """
    Create a Mock LLM Facade instance.

    Args:
        model_name: Mock model identifier
        deterministic: If True, always return same response
        simulate_latency: If True, add realistic delays
        **kwargs: Additional configuration

    Returns:
        Configured MockLLMFacade instance

    Example:
        >>> llm = create_mock_llm(deterministic=True)
        >>> response = llm.text_generation("Test")
    """
    return MockLLMFacade(model_name, deterministic=deterministic,
                        simulate_latency=simulate_latency, **kwargs)


__all__ = ['MockLLMFacade', 'create_mock_llm']
