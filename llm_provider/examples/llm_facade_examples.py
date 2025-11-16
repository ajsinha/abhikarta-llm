"""
LLM Facade Implementation Examples

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
This file demonstrates practical implementations and usage patterns for the LLM Facade.
It shows how to:
1. Implement concrete facade classes for different providers
2. Use the facade in client applications
3. Handle errors and edge cases
4. Implement advanced features like RAG and tool calling
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional, Iterator,Union
from abc import ABC

# Import the facade and related types
from llm_facade import (
    LLMFacade,
    ModelCapability,
    GenerationConfig,
    Messages,
    ToolDefinition,
    ToolCall,
    ToolResult,
    Document,
    RetrievalResult,
    Embedding,
    CapabilityNotSupportedException,
    RateLimitException,
    ContentFilterException,
    ContextLengthExceededException
)


# ============================================================================
# Example 1: Concrete Provider Implementation - Anthropic
# ============================================================================

class AnthropicFacade(LLMFacade):
    """
    Example implementation of LLMFacade for Anthropic Claude models.

    This demonstrates how to implement the abstract facade for a specific provider,
    handling provider-specific API calls and response formats.
    """

    def __init__(
            self,
            model_name: str,
            api_key: Optional[str] = None,
            base_url: Optional[str] = None,
            timeout: Optional[float] = None,
            max_retries: int = 3,
            **kwargs
    ) -> None:
        """Initialize Anthropic facade."""
        try:
            import anthropic
        except ImportError:
            raise ImportError("Please install anthropic package: pip install anthropic")

        self.model_name = model_name
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.timeout = timeout or 60.0
        self.max_retries = max_retries

        # Detect capabilities based on model
        self._capabilities = self._detect_capabilities()

    def _detect_capabilities(self) -> List[ModelCapability]:
        """Detect model capabilities based on model name."""
        capabilities = [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CHAT_COMPLETION,
            ModelCapability.TOOL_USE,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.JSON_MODE,
            ModelCapability.CODE_GENERATION,
            ModelCapability.STREAMING,
            ModelCapability.REASONING
        ]

        # Claude 3 models have vision capabilities
        if "claude-3" in self.model_name.lower():
            capabilities.extend([
                ModelCapability.VISION,
                ModelCapability.MULTIMODAL,
                ModelCapability.IMAGE_UNDERSTANDING
            ])

        return capabilities

    def get_capabilities(self) -> List[ModelCapability]:
        """Get supported capabilities."""
        return self._capabilities.copy()

    def supports_capability(self, capability: ModelCapability) -> bool:
        """Check if capability is supported."""
        return capability in self._capabilities

    def text_generation(
            self,
            prompt: str,
            *,
            config: Optional[GenerationConfig] = None,
            stream: bool = False,
            **kwargs
    ) -> Union[str, Iterator[str], Dict[str, Any]]:
        """
        Generate text using Claude's message API.

        Note: Anthropic's API doesn't have a separate completion endpoint,
        so we convert the prompt to a message format.
        """
        messages = [{"role": "user", "content": prompt}]
        response = self.chat_completion(
            messages=messages,
            config=config,
            stream=stream,
            **kwargs
        )

        if stream:
            # Return iterator of just content strings
            def content_only():
                for delta in response:
                    if "content" in delta.get("delta", {}):
                        yield delta["delta"]["content"]

            return content_only()
        else:
            return response["content"]

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
    ) -> Union[Dict[str, Any], Iterator[Dict[str, Any]]]:
        """Anthropic chat completion implementation."""

        # Extract system message if present
        system_message = None
        anthropic_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                anthropic_messages.append(msg)

        # Build request parameters
        params = {
            "model": self.model_name,
            "messages": anthropic_messages,
            "max_tokens": (config.max_tokens if config else None) or 1024,
        }

        if system_message:
            params["system"] = system_message

        if config:
            if config.temperature is not None:
                params["temperature"] = config.temperature
            if config.top_p is not None:
                params["top_p"] = config.top_p
            if config.stop_sequences:
                params["stop_sequences"] = config.stop_sequences

        if tools:
            params["tools"] = self._convert_tools_to_anthropic_format(tools)

        if tool_choice and tool_choice != "auto":
            params["tool_choice"] = self._convert_tool_choice(tool_choice)

        try:
            if stream:
                return self._handle_streaming_response(
                    self.client.messages.stream(**params)
                )
            else:
                response = self.client.messages.create(**params)
                return self._normalize_response(response)

        except Exception as e:
            # Transform provider exceptions to facade exceptions
            raise self._transform_exception(e)

    def _convert_tools_to_anthropic_format(
            self,
            tools: List[ToolDefinition]
    ) -> List[Dict[str, Any]]:
        """Convert standard tool definitions to Anthropic format."""
        anthropic_tools = []
        for tool in tools:
            anthropic_tools.append({
                "name": tool["function"]["name"],
                "description": tool["function"]["description"],
                "input_schema": tool["function"]["parameters"]
            })
        return anthropic_tools

    def _normalize_response(self, response) -> Dict[str, Any]:
        """Convert Anthropic response to standard format."""
        # Extract text content
        content = ""
        tool_calls = []

        for block in response.content:
            if hasattr(block, "text"):
                content += block.text
            elif hasattr(block, "type") and block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "type": "function",
                    "function": {
                        "name": block.name,
                        "arguments": json.dumps(block.input)
                    }
                })

        return {
            "content": content,
            "role": "assistant",
            "finish_reason": response.stop_reason,
            "usage": {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            },
            "metadata": {
                "model": response.model,
                "created_at": None,
            },
            "tool_calls": tool_calls if tool_calls else None
        }

    def _handle_streaming_response(self, stream) -> Iterator[Dict[str, Any]]:
        """Handle streaming response from Anthropic."""
        with stream as s:
            for event in s:
                if event.type == "content_block_delta":
                    if hasattr(event.delta, "text"):
                        yield {
                            "delta": {"content": event.delta.text},
                            "finish_reason": None
                        }
                elif event.type == "message_stop":
                    yield {
                        "delta": {},
                        "finish_reason": "stop"
                    }

    def _transform_exception(self, exception: Exception):
        """Transform provider-specific exceptions to facade exceptions."""
        error_message = str(exception)

        if "rate_limit" in error_message.lower():
            return RateLimitException(error_message)
        elif "content_filter" in error_message.lower():
            return ContentFilterException(error_message)
        elif "context_length" in error_message.lower():
            return ContextLengthExceededException(0, 0)  # Would parse actual values
        else:
            return exception

    # Implement remaining abstract methods...
    # For brevity, showing key methods. Full implementation would include all 50+ methods.

    def chat_completion_with_vision(
            self,
            messages: Messages,
            images: Union[Any, List[Any]],
            *,
            config: Optional[GenerationConfig] = None,
            image_detail: str = "auto",
            **kwargs
    ) -> Dict[str, Any]:
        """Chat with vision support."""
        if not self.supports_capability(ModelCapability.VISION):
            raise CapabilityNotSupportedException(
                capability="vision",
                model=self.model_name
            )

        # Convert images to Anthropic format and add to messages
        # Implementation details...
        return self.chat_completion(messages, config=config, **kwargs)

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        context_windows = {
            "claude-3-opus": 200000,
            "claude-3-sonnet": 200000,
            "claude-3-haiku": 200000,
        }

        return {
            "name": self.model_name,
            "provider": "anthropic",
            "version": "3.0",
            "context_length": context_windows.get(self.model_name, 100000),
            "max_output_tokens": 4096,
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "modalities": ["text", "image"] if self.supports_capability(ModelCapability.VISION) else ["text"],
            "pricing": {
                "input_per_1m": 3.0,
                "output_per_1m": 15.0
            }
        }

    # Placeholder implementations for other required methods
    def stream_text_generation(self, prompt: str, **kwargs) -> Iterator[str]:
        return self.text_generation(prompt, stream=True, **kwargs)

    def stream_chat_completion(self, messages: Messages, **kwargs) -> Iterator[Dict[str, Any]]:
        return self.chat_completion(messages, stream=True, **kwargs)

    async def atext_generation(self, prompt: str, **kwargs):
        # Would use async client
        raise NotImplementedError("Async not yet implemented")

    async def achat_completion(self, messages: Messages, **kwargs):
        raise NotImplementedError("Async not yet implemented")

    async def achat_completion_with_vision(self, messages: Messages, images, **kwargs):
        raise NotImplementedError("Async not yet implemented")

    def retrieve_documents(self, query: str, **kwargs) -> RetrievalResult:
        raise NotImplementedError("RAG requires vector store integration")

    def rag_chat(self, messages: Messages, **kwargs):
        raise NotImplementedError("RAG requires vector store integration")

    def rag_generate(self, query: str, **kwargs):
        raise NotImplementedError("RAG requires vector store integration")

    def create_tool_definition(self, name: str, description: str, parameters: Dict[str, Any],
                               required: Optional[List[str]] = None) -> ToolDefinition:
        return {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        }

    def call_tool(self, tool_call: ToolCall, available_tools: Dict[str, Any], **kwargs) -> ToolResult:
        import json

        tool_name = tool_call["function"]["name"]
        if tool_name not in available_tools:
            from llm_facade import ToolNotFoundException
            raise ToolNotFoundException(tool_name)

        try:
            args = json.loads(tool_call["function"]["arguments"])
            result = available_tools[tool_name](**args)
            return {
                "tool_call_id": tool_call["id"],
                "output": result
            }
        except Exception as e:
            from llm_facade import ToolExecutionException
            raise ToolExecutionException(tool_name, str(e))

    def execute_tool_loop(self, messages: Messages, tools: List[ToolDefinition], available_tools: Dict[str, Any],
                          max_iterations: int = 5, **kwargs) -> Dict[str, Any]:
        iteration = 0
        current_messages = messages.copy()

        while iteration < max_iterations:
            response = self.chat_completion(
                current_messages,
                tools=tools,
                **kwargs
            )

            if not response.get("tool_calls"):
                # No more tool calls, return final response
                return response

            # Execute tool calls
            current_messages.append({
                "role": "assistant",
                "content": response["content"],
                "tool_calls": response["tool_calls"]
            })

            for tool_call in response["tool_calls"]:
                result = self.call_tool(tool_call, available_tools)
                current_messages.append({
                    "role": "tool",
                    "tool_call_id": result["tool_call_id"],
                    "content": json.dumps(result["output"])
                })

            iteration += 1

        # Max iterations reached
        return response

    def embed_text(self, texts, **kwargs):
        raise CapabilityNotSupportedException("embeddings", self.model_name)

    def embed_image(self, images, **kwargs):
        raise CapabilityNotSupportedException("image_embeddings", self.model_name)

    def compute_similarity(self, embedding1, embedding2, metric="cosine"):
        import numpy as np
        if metric == "cosine":
            return np.dot(embedding1, embedding2)
        raise NotImplementedError(f"Metric {metric} not implemented")

    def image_generation(self, prompt: str, **kwargs):
        raise CapabilityNotSupportedException("image_generation", self.model_name)

    def image_editing(self, image, prompt: str, **kwargs):
        raise CapabilityNotSupportedException("image_editing", self.model_name)

    def image_variation(self, image, n: int = 1, **kwargs):
        raise CapabilityNotSupportedException("image_variation", self.model_name)

    def image_captioning(self, image, **kwargs) -> str:
        # Use vision capability
        return self.chat_completion_with_vision(
            messages=[{"role": "user", "content": "Describe this image in detail"}],
            images=image,
            **kwargs
        )["content"]

    def audio_transcription(self, audio, **kwargs):
        raise CapabilityNotSupportedException("audio_transcription", self.model_name)

    def audio_translation(self, audio, target_language: str = "en", **kwargs):
        raise CapabilityNotSupportedException("audio_translation", self.model_name)

    def code_generation(self, description: str, **kwargs) -> Dict[str, Any]:
        messages = [{"role": "user", "content": f"Generate code: {description}"}]
        response = self.chat_completion(messages, **kwargs)
        return {
            "code": response["content"],
            "language": kwargs.get("language", "python"),
            "explanation": "Code generated based on description"
        }

    def code_explanation(self, code: str, **kwargs) -> str:
        messages = [{"role": "user", "content": f"Explain this code:\n\n{code}"}]
        return self.chat_completion(messages, **kwargs)["content"]

    def code_review(self, code: str, **kwargs) -> Dict[str, Any]:
        messages = [{"role": "user", "content": f"Review this code:\n\n{code}"}]
        response = self.chat_completion(messages, **kwargs)
        return {
            "issues": [],
            "suggestions": [],
            "summary": response["content"]
        }

    def code_completion(self, code: str, cursor_position: Optional[int] = None, **kwargs) -> List[str]:
        raise NotImplementedError("Code completion not yet implemented")

    def generate_with_schema(self, messages: Messages, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        import json

        # Add schema to system prompt
        schema_prompt = f"Respond with JSON matching this schema: {json.dumps(schema)}"
        messages_with_schema = [
                                   {"role": "system", "content": schema_prompt}
                               ] + messages

        response = self.chat_completion(messages_with_schema, **kwargs)
        return json.loads(response["content"])

    def extract_structured_data(self, text: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        import json
        messages = [{
            "role": "user",
            "content": f"Extract structured data matching schema {json.dumps(schema)} from: {text}"
        }]
        return self.generate_with_schema(messages, schema, **kwargs)

    def moderate_content(self, text: str, **kwargs):
        # Anthropic doesn't have built-in moderation API
        raise NotImplementedError("Content moderation not implemented")

    def classify_text(self, text: str, categories: List[str], **kwargs) -> Dict[str, float]:
        import json
        messages = [{
            "role": "user",
            "content": f"Classify this text into categories {categories}: {text}"
        }]
        response = self.chat_completion(messages, **kwargs)
        return json.loads(response["content"])

    def create_conversation(self, system_prompt: Optional[str] = None, **kwargs) -> str:
        import uuid
        conv_id = str(uuid.uuid4())
        # Would store in database/cache
        return conv_id

    def continue_conversation(self, conversation_id: str, user_message: str, **kwargs) -> Dict[str, Any]:
        # Would retrieve history from storage
        messages = [{"role": "user", "content": user_message}]
        return self.chat_completion(messages, **kwargs)

    def get_conversation_history(self, conversation_id: str, **kwargs) -> Messages:
        # Would retrieve from storage
        return []

    def clear_conversation(self, conversation_id: str, **kwargs) -> bool:
        # Would clear from storage
        return True

    def count_tokens(self, text, **kwargs) -> int:
        # Approximate - would use actual tokenizer
        return len(text.split()) * 1.3

    def truncate_to_max_tokens(self, text: str, max_tokens: int, **kwargs) -> str:
        words = text.split()
        target_words = int(max_tokens / 1.3)
        return " ".join(words[:target_words])

    def estimate_cost(self, input_tokens: int, output_tokens: int, **kwargs) -> Dict[str, float]:
        input_cost = (input_tokens / 1_000_000) * 3.0
        output_cost = (output_tokens / 1_000_000) * 15.0
        return {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": input_cost + output_cost,
            "currency": "USD"
        }

    def get_context_window(self) -> int:
        return self.get_model_info()["context_length"]

    def get_max_output_tokens(self) -> int:
        return self.get_model_info()["max_output_tokens"]

    def batch_generate(self, prompts: List[str], **kwargs) -> List[str]:
        return [self.text_generation(p, **kwargs) for p in prompts]

    def batch_embed(self, texts: List[str], **kwargs) -> List[Embedding]:
        raise CapabilityNotSupportedException("embeddings", self.model_name)

    def create_fine_tuning_job(self, training_file: str, **kwargs) -> str:
        raise NotImplementedError("Fine-tuning not yet supported")

    def get_fine_tuning_status(self, job_id: str, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError("Fine-tuning not yet supported")

    def log_request(self, method: str, input_data: Any, response: Any, **kwargs) -> None:
        # Would log to monitoring system
        pass

    def get_usage_stats(self, period: str = "day", **kwargs) -> Dict[str, Any]:
        # Would retrieve from monitoring system
        return {}

    def format_messages(self, messages: Messages, **kwargs) -> str:
        formatted = ""
        for msg in messages:
            formatted += f"{msg['role']}: {msg['content']}\n\n"
        return formatted

    def parse_tool_calls(self, response: Dict[str, Any], **kwargs) -> List[ToolCall]:
        return response.get("tool_calls", [])

    def validate_config(self, config: Dict[str, Any], **kwargs):
        errors = []
        if config.get("max_tokens", 0) > 4096:
            errors.append("max_tokens exceeds limit of 4096")
        return (len(errors) == 0, errors)

    def health_check(self, **kwargs) -> bool:
        try:
            # Simple health check
            self.chat_completion([{"role": "user", "content": "hi"}], config=GenerationConfig(max_tokens=5))
            return True
        except:
            return False

    def close(self) -> None:
        # Cleanup resources
        pass


# ============================================================================
# Example 2: Client Application Usage
# ============================================================================

def example_basic_usage():
    """Demonstrate basic facade usage."""
    print("=" * 80)
    print("Example 1: Basic Chat Completion")
    print("=" * 80)

    # Initialize facade
    llm = AnthropicFacade(model_name="claude-3-sonnet-20240229")

    # Simple chat
    response = llm.chat_completion([
        {"role": "user", "content": "Explain quantum computing in one paragraph"}
    ])

    print(f"Response: {response['content']}")
    print(f"Tokens used: {response['usage']['total_tokens']}")
    print()


def example_with_config():
    """Demonstrate usage with generation config."""
    print("=" * 80)
    print("Example 2: Using Generation Config")
    print("=" * 80)

    llm = AnthropicFacade(model_name="claude-3-sonnet-20240229")

    config = GenerationConfig(
        max_tokens=500,
        temperature=0.7,
        top_p=0.9,
        stop_sequences=["END"]
    )

    response = llm.chat_completion(
        messages=[
            {"role": "system", "content": "You are a helpful coding assistant"},
            {"role": "user", "content": "Write a Python function to calculate factorial"}
        ],
        config=config
    )

    print(f"Response: {response['content']}")
    print()


def example_streaming():
    """Demonstrate streaming response."""
    print("=" * 80)
    print("Example 3: Streaming Response")
    print("=" * 80)

    llm = AnthropicFacade(model_name="claude-3-sonnet-20240229")

    print("Streaming response: ", end="", flush=True)
    for chunk in llm.stream_chat_completion([
        {"role": "user", "content": "Count from 1 to 10"}
    ]):
        if "content" in chunk.get("delta", {}):
            print(chunk["delta"]["content"], end="", flush=True)

    print("\n")


def example_tool_calling():
    """Demonstrate tool/function calling."""
    print("=" * 80)
    print("Example 4: Tool Calling")
    print("=" * 80)

    llm = AnthropicFacade(model_name="claude-3-sonnet-20240229")

    # Define tools
    def get_weather(location: str, unit: str = "celsius") -> dict:
        """Simulated weather API."""
        return {
            "location": location,
            "temperature": 22,
            "condition": "sunny",
            "unit": unit
        }

    def calculate(expression: str) -> float:
        """Evaluate mathematical expression."""
        return eval(expression)  # Note: Use safely in production!

    # Create tool definitions
    tools = [
        llm.create_tool_definition(
            name="get_weather",
            description="Get current weather for a location",
            parameters={
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                }
            },
            required=["location"]
        ),
        llm.create_tool_definition(
            name="calculate",
            description="Evaluate a mathematical expression",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression"}
                }
            },
            required=["expression"]
        )
    ]

    available_tools = {
        "get_weather": get_weather,
        "calculate": calculate
    }

    # Execute tool loop
    response = llm.execute_tool_loop(
        messages=[
            {"role": "user", "content": "What's the weather in Paris? Also calculate 25 * 4"}
        ],
        tools=tools,
        available_tools=available_tools
    )

    print(f"Final response: {response['content']}")
    print()


def example_error_handling():
    """Demonstrate error handling."""
    print("=" * 80)
    print("Example 5: Error Handling")
    print("=" * 80)

    llm = AnthropicFacade(model_name="claude-3-sonnet-20240229")

    try:
        # Try to use unsupported capability
        llm.image_generation("A beautiful sunset")
    except CapabilityNotSupportedException as e:
        print(f"Caught exception: {e}")
        print(f"Capability '{e.capability}' not supported by model '{e.model}'")

    print()


def example_capability_checking():
    """Demonstrate capability checking."""
    print("=" * 80)
    print("Example 6: Capability Checking")
    print("=" * 80)

    llm = AnthropicFacade(model_name="claude-3-opus-20240229")

    print("Checking capabilities...")

    capabilities_to_check = [
        ModelCapability.CHAT_COMPLETION,
        ModelCapability.VISION,
        ModelCapability.TOOL_USE,
        ModelCapability.EMBEDDINGS,
        ModelCapability.IMAGE_GENERATION
    ]

    for cap in capabilities_to_check:
        supported = llm.supports_capability(cap)
        status = "✓ Supported" if supported else "✗ Not supported"
        print(f"{cap.value}: {status}")

    print()


# ============================================================================
# Example 3: Provider-Agnostic Client Code
# ============================================================================

def provider_agnostic_example(llm: LLMFacade):
    """
    This function works with ANY LLMFacade implementation.

    The same code works whether you pass OpenAIFacade, AnthropicFacade,
    GoogleFacade, etc. This demonstrates the power of the facade pattern.
    """
    print("=" * 80)
    print("Example 7: Provider-Agnostic Code")
    print("=" * 80)

    # Get model info
    info = llm.get_model_info()
    print(f"Using model: {info['name']} from {info['provider']}")
    print(f"Context window: {info['context_length']} tokens")

    # Chat completion (works with any provider)
    response = llm.chat_completion([
        {"role": "user", "content": "Hello! Tell me a fun fact."}
    ])

    print(f"\nResponse: {response['content']}")

    # Check and use capabilities
    if llm.supports_capability(ModelCapability.VISION):
        print("\n✓ This model supports vision!")
    else:
        print("\n✗ This model doesn't support vision")

    print()


# ============================================================================
# Main execution
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "LLM FACADE USAGE EXAMPLES" + " " * 33 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    # Run examples
    example_basic_usage()
    example_with_config()
    example_streaming()
    example_tool_calling()
    example_error_handling()
    example_capability_checking()

    # Provider-agnostic example
    llm = AnthropicFacade(model_name="claude-3-sonnet-20240229")
    provider_agnostic_example(llm)

    print("\n" + "=" * 80)
    print("Examples completed successfully!")
    print("=" * 80 + "\n")