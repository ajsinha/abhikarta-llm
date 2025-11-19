"""
Abhikarta Google AI (Gemini) Facade - Dynamic Configuration Implementation

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

import os
import json
from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator

from llm_provider.base_provider_facade import BaseProviderFacade
from llm_provider.llm_facade import *


class GoogleFacade(BaseProviderFacade):
    """Google AI (Gemini) facade with dynamic configuration."""

    def _initialize_client(self):
        """Initialize Google Generative AI client."""
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("Google Generative AI SDK not installed. Install with: pip install google-generativeai")

        api_key = self.api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise AuthenticationException("Google API key required")

        genai.configure(api_key=api_key)
        self.genai = genai
        self.model_client = genai.GenerativeModel(self.model_name)

    def chat_completion(self, messages: Messages, temperature: Optional[float] = None,
                       max_tokens: Optional[int] = None, tools: Optional[List[ToolDefinition]] = None,
                       **kwargs) -> Dict[str, Any]:
        if not self.supports_capability(ModelCapability.CHAT_COMPLETION):
            raise CapabilityNotSupportedException("chat", self.model_name)

        # Convert messages to Gemini format
        gemini_messages = self._convert_messages(messages)

        # Generation config
        gen_config = {}
        if temperature is not None:
            gen_config['temperature'] = temperature
        if max_tokens:
            gen_config['max_output_tokens'] = max_tokens

        # Tools
        gemini_tools = None
        if tools:
            gemini_tools = self._convert_tools(tools)

        try:
            response = self.model_client.generate_content(
                gemini_messages,
                generation_config=self.genai.GenerationConfig(**gen_config) if gen_config else None,
                tools=gemini_tools,
                **kwargs
            )

            return self._convert_response(response)
        except Exception as e:
            raise InvalidResponseException(f"Google AI API error: {str(e)}")

    async def achat_completion(self, messages: Messages, **kwargs) -> Dict[str, Any]:
        import asyncio
        return await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.chat_completion(messages, **kwargs)
        )

    def stream_chat_completion(self, messages: Messages, **kwargs) -> Iterator[str]:
        if not self.supports_capability(ModelCapability.STREAMING):
            raise CapabilityNotSupportedException("streaming", self.model_name)

        gemini_messages = self._convert_messages(messages)

        try:
            response = self.model_client.generate_content(
                gemini_messages,
                stream=True,
                **kwargs
            )

            for chunk in response:
                if hasattr(chunk, 'text'):
                    yield chunk.text
        except Exception as e:
            raise InvalidResponseException(f"Google AI streaming error: {str(e)}")

    async def astream_chat_completion(self, messages: Messages, **kwargs) -> AsyncIterator[str]:
        import asyncio
        for chunk in self.stream_chat_completion(messages, **kwargs):
            yield chunk
            await asyncio.sleep(0)

    def chat_completion_with_vision(self, messages: Messages, images: List[ImageInput], **kwargs) -> Dict[str, Any]:
        if not self.supports_capability(ModelCapability.VISION):
            raise CapabilityNotSupportedException("vision", self.model_name)

        # Process images
        processed_images = []
        for img in images:
            if isinstance(img, str):
                if img.startswith('http'):
                    # URL - Gemini can handle directly
                    processed_images.append(img)
                else:
                    # Base64
                    import base64
                    from PIL import Image
                    import io
                    img_data = base64.b64decode(img)
                    pil_img = Image.open(io.BytesIO(img_data))
                    processed_images.append(pil_img)
            elif isinstance(img, bytes):
                from PIL import Image
                import io
                pil_img = Image.open(io.BytesIO(img))
                processed_images.append(pil_img)
            else:
                # Assume PIL Image
                processed_images.append(img)

        # Create content with images
        content = []

        # Add last user message text
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                content.append(msg.get('content', ''))
                break

        # Add images
        content.extend(processed_images)

        try:
            response = self.model_client.generate_content(content, **kwargs)
            return self._convert_response(response)
        except Exception as e:
            raise InvalidResponseException(f"Google AI vision error: {str(e)}")

    def _convert_messages(self, messages: Messages) -> List[Dict[str, Any]]:
        """Convert standard messages to Gemini format."""
        gemini_messages = []

        for msg in messages:
            role = msg.get('role')
            content = msg.get('content', '')

            # Map roles
            if role == 'system':
                # Gemini doesn't have system role, prepend to first user message
                gemini_messages.append({
                    "role": "user",
                    "parts": [{"text": f"System: {content}"}]
                })
            elif role == 'user':
                gemini_messages.append({
                    "role": "user",
                    "parts": [{"text": content}]
                })
            elif role == 'assistant':
                gemini_messages.append({
                    "role": "model",
                    "parts": [{"text": content}]
                })

        return gemini_messages

    def _convert_tools(self, tools: List[ToolDefinition]) -> List[Any]:
        """Convert standard tool definitions to Gemini format."""
        gemini_tools = []

        for tool in tools:
            if tool.get('type') == 'function':
                func = tool['function']
                gemini_tools.append(
                    self.genai.Tool(
                        function_declarations=[
                            self.genai.FunctionDeclaration(
                                name=func['name'],
                                description=func.get('description', ''),
                                parameters=func.get('parameters', {})
                            )
                        ]
                    )
                )

        return gemini_tools if gemini_tools else None

    def _convert_response(self, response) -> Dict[str, Any]:
        """Convert Gemini response to standard format."""
        content = ""
        tool_calls = []

        # Extract content
        if hasattr(response, 'text'):
            content = response.text
        elif hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'text'):
                        content += part.text

        # Extract tool calls
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call'):
                        fc = part.function_call
                        tool_calls.append({
                            "id": fc.name,
                            "type": "function",
                            "function": {
                                "name": fc.name,
                                "arguments": json.dumps(dict(fc.args))
                            }
                        })

        # Token usage
        usage = None
        if hasattr(response, 'usage_metadata'):
            usage = {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count
            }

        # Metadata
        metadata = {
            "model": self.model_name
        }

        # Add finish_reason if available
        if hasattr(response, 'candidates') and response.candidates:
            finish_reason = str(response.candidates[0].finish_reason)
            metadata["finish_reason"] = finish_reason

        return {
            "content": content,
            "tool_calls": tool_calls if tool_calls else None,
            "usage": usage,
            "metadata": metadata,
            "raw_response": response
        }

    def generate_embeddings(
        self,
        texts: Union[str, List[str]],
        **kwargs
    ) -> Union[Embedding, List[Embedding]]:
        if not self.supports_capability(ModelCapability.EMBEDDINGS):
            raise CapabilityNotSupportedException("embeddings", self.model_name)

        is_single = isinstance(texts, str)
        if is_single:
            texts = [texts]

        try:
            result = self.genai.embed_content(
                model=self.model_name,
                content=texts,
                **kwargs
            )

            embeddings = result['embedding'] if is_single else result['embeddings']
            return embeddings[0] if is_single else embeddings
        except Exception as e:
            raise InvalidResponseException(f"Google AI embeddings error: {str(e)}")

    async def agenerate_embeddings(
        self,
        texts: Union[str, List[str]],
        **kwargs
    ) -> Union[Embedding, List[Embedding]]:
        import asyncio
        return await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.generate_embeddings(texts, **kwargs)
        )

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
        return response.get("tool_calls", [])

    def count_tokens(self, text: str, **kwargs) -> int:
        try:
            result = self.model_client.count_tokens(text)
            return result.total_tokens
        except:
            return len(text) // 4

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


__all__ = ['GoogleFacade']