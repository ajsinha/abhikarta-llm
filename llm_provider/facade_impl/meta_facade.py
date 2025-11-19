"""
Abhikarta Meta/Replicate Facade - Llama models via Replicate

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

import os
from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator

from llm_provider.base_provider_facade import BaseProviderFacade
from llm_provider.llm_facade import *


class MetaFacade(BaseProviderFacade):
    """Meta Llama models via Replicate API."""
    
    def __init__(self, provider, model_name: str, **kwargs):
        """Initialize Meta facade."""
        # Call parent init
        super().__init__(provider, model_name, **kwargs)

        # Initialize the client
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Replicate client."""
        try:
            import replicate
        except ImportError:
            raise ImportError("Replicate SDK not installed. Install with: pip install replicate")

        api_key = self.api_key or os.getenv("REPLICATE_API_TOKEN")
        if not api_key:
            raise AuthenticationException("Replicate API token required")

        os.environ["REPLICATE_API_TOKEN"] = api_key
        self.replicate = replicate

    def chat_completion(self, messages: Messages, temperature: Optional[float] = None,
                       max_tokens: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        if not self.supports_capability(ModelCapability.CHAT_COMPLETION):
            raise CapabilityNotSupportedException("chat", self.model_name)

        # Get replicate model path from model metadata
        replicate_model = self.model.get_custom_field('replicate_model')
        if not replicate_model:
            replicate_model = f"meta/{self.model_name}"

        # Format prompt
        prompt = self._format_messages_for_llama(messages)

        input_params = {
            "prompt": prompt,
            "max_new_tokens": max_tokens or 512,
        }

        if temperature is not None:
            input_params['temperature'] = temperature

        input_params.update(kwargs)

        try:
            output = self.replicate.run(replicate_model, input=input_params)

            # Collect output
            content = "".join(output) if isinstance(output, Iterator) else str(output)

            return {
                "content": content,
                "tool_calls": None,
                "usage": {
                    "prompt_tokens": len(prompt) // 4,
                    "completion_tokens": len(content) // 4,
                    "total_tokens": (len(prompt) + len(content)) // 4
                },
                "metadata": {
                    "model": self.model_name
                },
                "raw_response": output
            }
        except Exception as e:
            raise InvalidResponseException(f"Replicate API error: {str(e)}")

    async def achat_completion(self, messages: Messages, **kwargs) -> Dict[str, Any]:
        import asyncio
        return await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.chat_completion(messages, **kwargs)
        )

    def stream_chat_completion(self, messages: Messages, **kwargs) -> Iterator[str]:
        if not self.supports_capability(ModelCapability.STREAMING):
            raise CapabilityNotSupportedException("streaming", self.model_name)

        replicate_model = self.model.get_custom_field('replicate_model') or f"meta/{self.model_name}"
        prompt = self._format_messages_for_llama(messages)

        input_params = {"prompt": prompt}
        input_params.update(kwargs)

        try:
            for output in self.replicate.stream(replicate_model, input=input_params):
                yield str(output)
        except Exception as e:
            raise InvalidResponseException(f"Replicate streaming error: {str(e)}")

    async def astream_chat_completion(self, messages: Messages, **kwargs) -> AsyncIterator[str]:
        import asyncio
        for chunk in self.stream_chat_completion(messages, **kwargs):
            yield chunk
            await asyncio.sleep(0)

    def _format_messages_for_llama(self, messages: Messages) -> str:
        """Format messages for Llama models."""
        parts = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')

            if role == 'system':
                parts.append(f"<<SYS>>\n{content}\n<</SYS>>")
            elif role == 'user':
                parts.append(f"[INST] {content} [/INST]")
            elif role == 'assistant':
                parts.append(content)

        return "\n\n".join(parts)

    def chat_completion_with_vision(self, messages: Messages, images: List[ImageInput], **kwargs) -> Dict[str, Any]:
        if not self.supports_capability(ModelCapability.VISION):
            raise CapabilityNotSupportedException("vision", self.model_name)
        # Vision models would need special handling
        raise NotImplementedError("Vision support for Llama models via Replicate needs model-specific implementation")

    def text_completion(self, prompt: str, **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        response = self.chat_completion(messages, **kwargs)
        return response["content"]

    async def atext_completion(self, prompt: str, **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        response = await self.achat_completion(messages, **kwargs)
        return response["content"]

    def stream_text_completion(self, prompt: str, **kwargs) -> TextStream:
        messages = [{"role": "user", "content": prompt}]
        return self.stream_chat_completion(messages, **kwargs)

    async def astream_text_completion(self, prompt: str, **kwargs) -> TextStream:
        messages = [{"role": "user", "content": prompt}]
        async for chunk in self.astream_chat_completion(messages, **kwargs):
            yield chunk

    def parse_tool_calls(self, response: Dict[str, Any], **kwargs) -> List[ToolCall]:
        return []

    def count_tokens(self, text: str, **kwargs) -> int:
        return len(text) // 4

    def generate_embeddings(self, texts: Union[str, List[str]], **kwargs) -> Union[Embedding, List[Embedding]]:
        raise CapabilityNotSupportedException("embeddings", self.model_name)

    async def agenerate_embeddings(self, texts: Union[str, List[str]], **kwargs) -> Union[Embedding, List[Embedding]]:
        raise CapabilityNotSupportedException("embeddings", self.model_name)

    def generate_image(self, prompt: str, **kwargs) -> ImageOutput:
        raise CapabilityNotSupportedException("image_generation", self.model_name)

    async def agenerate_image(self, prompt: str, **kwargs) -> ImageOutput:
        raise CapabilityNotSupportedException("image_generation", self.model_name)

    def moderate_content(self, content: str, **kwargs) -> ModerationResult:
        raise CapabilityNotSupportedException("moderation", self.model_name)

    async def amoderate_content(self, content: str, **kwargs) -> ModerationResult:
        raise CapabilityNotSupportedException("moderation", self.model_name)

    def log_request(self, method: str, input_data: Any, response: Any, latency_ms: float, metadata: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        pass

    def get_usage_stats(self, period: str = "day", **kwargs) -> Dict[str, Any]:
        return {"message": "Usage stats not implemented"}


__all__ = ['MetaFacade']