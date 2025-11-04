"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.3
"""

"""HuggingFace LLM Facade"""
from typing import List, Iterator, Any
from ...core.facade import LLMFacade, Message, CompletionResponse, ChatResponse, ModelInfo
from ...core.exceptions import APIError

class HuggingFaceFacade(LLMFacade):
    def __init__(self, provider, model_name: str, client: Any):
        super().__init__(provider, model_name)
        self.client = client
    
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        try:
            result = self.client.text_generation(
                prompt,
                model=self.model_name,
                max_new_tokens=kwargs.get('max_tokens', 1000)
            )
            return CompletionResponse(
                text=result,
                model=self.model_name,
                provider='huggingface',
                tokens_used=self.count_tokens(prompt + result),
                finish_reason='complete'
            )
        except Exception as e:
            raise APIError(f"HuggingFace error: {str(e)}", provider='huggingface')
    
    def chat(self, messages: List[Message], **kwargs) -> ChatResponse:
        prompt = "\n".join([f"{m.role}: {m.content}" for m in messages])
        result = self.complete(prompt, **kwargs)
        return ChatResponse(
            message=Message(role='assistant', content=result.text),
            model=self.model_name,
            provider='huggingface',
            tokens_used=result.tokens_used,
            finish_reason='complete'
        )
    
    def stream_complete(self, prompt: str, **kwargs) -> Iterator[str]:
        try:
            for token in self.client.text_generation(
                prompt,
                model=self.model_name,
                max_new_tokens=kwargs.get('max_tokens', 1000),
                stream=True
            ):
                yield token
        except Exception as e:
            raise APIError(f"HuggingFace streaming error: {str(e)}", provider='huggingface')
    
    def stream_chat(self, messages: List[Message], **kwargs) -> Iterator[str]:
        prompt = "\n".join([f"{m.role}: {m.content}" for m in messages])
        return self.stream_complete(prompt, **kwargs)
    
    def get_model_info(self) -> ModelInfo:
        if self.model_info_cache:
            return self.model_info_cache
        model_config = self.provider.get_model_info(self.model_name)
        self.model_info_cache = ModelInfo(
            name=model_config.get('name', self.model_name),
            version=model_config.get('version', ''),
            description=model_config.get('description', ''),
            context_window=model_config.get('context_window', 2048),
            max_output=model_config.get('max_output', 1024),
            capabilities=model_config.get('capabilities', {}),
            cost=model_config.get('cost', {}),
            metadata={'provider': 'huggingface'}
        )
        return self.model_info_cache
    
    def count_tokens(self, text: str) -> int:
        return len(text) // 4
