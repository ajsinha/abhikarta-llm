"""
Abhikarta AWS Bedrock Facade

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

import os
import json
from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator

from base_provider_facade import BaseProviderFacade
from llm_facade import *


class AWSBedrockFacade(BaseProviderFacade):
    """AWS Bedrock facade for Claude, Llama, and other models on AWS."""
    
    def _initialize_client(self):
        """Initialize AWS Bedrock client."""
        try:
            import boto3
        except ImportError:
            raise ImportError("Boto3 not installed. Install with: pip install boto3")
        
        # AWS credentials from environment or IAM role
        region = self.kwargs.get('region', os.getenv('AWS_REGION', 'us-east-1'))
        
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=region
        )
    
    def chat_completion(self, messages: Messages, temperature: Optional[float] = None,
                       max_tokens: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        if not self.supports_capability(ModelCapability.CHAT_COMPLETION):
            raise CapabilityNotSupportedException("chat", self.model_name)
        
        # Format request based on model type
        if 'claude' in self.model_name.lower():
            body = self._format_claude_request(messages, temperature, max_tokens)
        elif 'llama' in self.model_name.lower():
            body = self._format_llama_request(messages, temperature, max_tokens)
        else:
            body = self._format_generic_request(messages, temperature, max_tokens)
        
        try:
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_name,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            return self._convert_response(response_body)
        
        except Exception as e:
            raise InvalidResponseException(f"AWS Bedrock API error: {str(e)}")
    
    async def achat_completion(self, messages: Messages, **kwargs) -> Dict[str, Any]:
        import asyncio
        return await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.chat_completion(messages, **kwargs)
        )
    
    def stream_chat_completion(self, messages: Messages, **kwargs) -> Iterator[str]:
        if not self.supports_capability(ModelCapability.STREAMING):
            raise CapabilityNotSupportedException("streaming", self.model_name)
        
        body = self._format_claude_request(messages, kwargs.get('temperature'), kwargs.get('max_tokens'))
        
        try:
            response = self.bedrock_runtime.invoke_model_with_response_stream(
                modelId=self.model_name,
                body=json.dumps(body)
            )
            
            for event in response['body']:
                chunk = json.loads(event['chunk']['bytes'])
                if 'delta' in chunk and 'text' in chunk['delta']:
                    yield chunk['delta']['text']
        
        except Exception as e:
            raise InvalidResponseException(f"AWS Bedrock streaming error: {str(e)}")
    
    async def astream_chat_completion(self, messages: Messages, **kwargs) -> AsyncIterator[str]:
        import asyncio
        for chunk in self.stream_chat_completion(messages, **kwargs):
            yield chunk
            await asyncio.sleep(0)
    
    def _format_claude_request(self, messages: Messages, temperature: Optional[float], max_tokens: Optional[int]) -> Dict:
        """Format request for Claude models on Bedrock."""
        anthropic_messages = []
        system = None
        
        for msg in messages:
            role = msg.get('role')
            content = msg.get('content', '')
            
            if role == 'system':
                system = content
            else:
                anthropic_messages.append({
                    "role": role,
                    "content": content
                })
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": anthropic_messages,
            "max_tokens": max_tokens or 1000
        }
        
        if system:
            body['system'] = system
        if temperature is not None:
            body['temperature'] = temperature
        
        return body
    
    def _format_llama_request(self, messages: Messages, temperature: Optional[float], max_tokens: Optional[int]) -> Dict:
        """Format request for Llama models on Bedrock."""
        prompt = self._format_llama_prompt(messages)
        
        return {
            "prompt": prompt,
            "max_gen_len": max_tokens or 512,
            "temperature": temperature or 0.5,
            "top_p": 0.9
        }
    
    def _format_llama_prompt(self, messages: Messages) -> str:
        """Format messages for Llama."""
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
    
    def _format_generic_request(self, messages: Messages, temperature: Optional[float], max_tokens: Optional[int]) -> Dict:
        """Generic request format."""
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        return {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": max_tokens or 512,
                "temperature": temperature or 0.5
            }
        }
    
    def _convert_response(self, response_body: Dict) -> Dict[str, Any]:
        """Convert Bedrock response to standard format."""
        # Different models return different formats
        if 'content' in response_body:
            # Claude format
            content = response_body['content'][0]['text']
            usage = response_body.get('usage', {})
            token_usage = TokenUsage(
                prompt_tokens=usage.get('input_tokens', 0),
                completion_tokens=usage.get('output_tokens', 0),
                total_tokens=usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
            )
        elif 'generation' in response_body:
            # Llama format
            content = response_body['generation']
            token_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
        elif 'results' in response_body:
            # Generic format
            content = response_body['results'][0]['outputText']
            token_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
        else:
            content = str(response_body)
            token_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
        
        return {
            "content": content,
            "tool_calls": None,
            "usage": token_usage,
            "metadata": CompletionMetadata(model=self.model_name, usage=token_usage),
            "raw_response": response_body
        }
    
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
    
    def chat_completion_with_vision(self, messages: Messages, images: List[ImageInput], **kwargs) -> Dict[str, Any]:
        raise CapabilityNotSupportedException("vision", self.model_name)
    
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


__all__ = ['AWSBedrockFacade']
