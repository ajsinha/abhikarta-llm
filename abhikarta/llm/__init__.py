"""
LLM Module - Unified async interface for Large Language Model operations.

This module provides a simplified async-first interface for making LLM calls
across multiple providers. It wraps the LLMFacade with async support for
use in the swarm and agent modules.

Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.
Email: ajsinha@gmail.com

PATENT PENDING - This software contains patentable inventions.
Unauthorized copying, modification, or distribution is prohibited.

Version: 1.3.0

Supported Providers:
    - openai: GPT-4o, GPT-4o-mini, GPT-4-turbo, o1
    - anthropic: Claude 3.5 Sonnet, Claude 3 Opus
    - google: Gemini 1.5 Pro, Gemini 1.5 Flash
    - mistral: Mistral Large, Medium, Small
    - cohere: Command R+, Command R
    - groq: Ultra-fast inference
    - together: Open source models
    - deepseek: DeepSeek Chat, Coder
    - perplexity: Sonar models with search
    - ollama: Local models

Usage:
    from abhikarta.llm import LLMAdapter, LLMResponse, LLMConfig, generate
    
    # Simple usage
    adapter = LLMAdapter(provider='openai', model='gpt-4o')
    response = await adapter.generate(
        prompt="Hello, world!",
        system_prompt="You are a helpful assistant."
    )
    print(response.content)
    
    # Quick one-off call
    response = await generate("Tell me a joke", provider='anthropic')
"""

from .adapter import (
    LLMAdapter,
    LLMResponse,
    LLMConfig,
    generate,
)

__all__ = [
    'LLMAdapter',
    'LLMResponse', 
    'LLMConfig',
    'generate',
]

__version__ = '1.3.0'
