"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.2
"""

"""AWS Bedrock LLM Facade"""
import json
from typing import List, Iterator, Any
from ...core.facade import LLMFacade, Message, CompletionResponse, ChatResponse, ModelInfo
from ...core.exceptions import APIError

class AWSBedrockFacade(LLMFacade):
    def __init__(self, provider, model_name: str, client: Any):
        super().__init__(provider, model_name)
        self.client = client
    
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        try:
            body = json.dumps({
                "prompt": prompt,
                "max_tokens_to_sample": kwargs.get('max_tokens', 1000),
                "temperature": kwargs.get('temperature', 0.7)
            })
            
            response = self.client.invoke_model(
                modelId=self.model_name,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            text = response_body.get('completion', '')
            
            return CompletionResponse(
                text=text,
                model=self.model_name,
                provider='awsbedrock',
                tokens_used=self.count_tokens(prompt + text),
                finish_reason='complete'
            )
        except Exception as e:
            raise APIError(f"AWS Bedrock error: {str(e)}", provider='awsbedrock')
    
    def chat(self, messages: List[Message], **kwargs) -> ChatResponse:
        prompt = "\n".join([f"{m.role}: {m.content}" for m in messages])
        result = self.complete(prompt, **kwargs)
        return ChatResponse(
            message=Message(role='assistant', content=result.text),
            model=self.model_name,
            provider='awsbedrock',
            tokens_used=result.tokens_used,
            finish_reason='complete'
        )
    
    def stream_complete(self, prompt: str, **kwargs) -> Iterator[str]:
        result = self.complete(prompt, **kwargs)
        for word in result.text.split():
            yield word + " "
    
    def stream_chat(self, messages: List[Message], **kwargs) -> Iterator[str]:
        result = self.chat(messages, **kwargs)
        for word in result.message.content.split():
            yield word + " "
    
    def get_model_info(self) -> ModelInfo:
        if self.model_info_cache:
            return self.model_info_cache
        model_config = self.provider.get_model_info(self.model_name)
        self.model_info_cache = ModelInfo(
            name=model_config.get('name', self.model_name),
            version=model_config.get('version', ''),
            description=model_config.get('description', ''),
            context_window=model_config.get('context_window', 100000),
            max_output=model_config.get('max_output', 4096),
            capabilities=model_config.get('capabilities', {}),
            cost=model_config.get('cost', {}),
            metadata={'provider': 'awsbedrock'}
        )
        return self.model_info_cache
    
    def count_tokens(self, text: str) -> int:
        return len(text) // 4
