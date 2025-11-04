"""
Providers Package

Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.4
"""

# Import providers
try:
    from .openai.provider import OpenAIProvider
except:
    OpenAIProvider = None

try:
    from .anthropic.provider import AnthropicProvider
except:
    AnthropicProvider = None

try:
    from .google.provider import GoogleProvider
except:
    GoogleProvider = None

try:
    from .mock.provider import MockProvider
except:
    MockProvider = None

try:
    from .huggingface.provider import HuggingFaceProvider
except:
    HuggingFaceProvider = None

try:
    from .cohere.provider import CohereProvider
except:
    CohereProvider = None

try:
    from .replicate.provider import ReplicateProvider
except:
    ReplicateProvider = None

try:
    from .awsbedrock.provider import AWSBedrockProvider
except:
    AWSBedrockProvider = None

try:
    from .meta.provider import MetaProvider
except:
    MetaProvider = None

try:
    from .groq import GroqProvider
except:
    GroqProvider = None

try:
    from .mistral import MistralProvider
except:
    MistralProvider = None

try:
    from .together import TogetherProvider
except:
    TogetherProvider = None

try:
    from .ollama import OllamaProvider
except:
    OllamaProvider = None


# Provider registry
PROVIDER_REGISTRY = {}
for name, cls in [
    ('openai', OpenAIProvider),
    ('anthropic', AnthropicProvider),
    ('google', GoogleProvider),
    ('mock', MockProvider),
    ('huggingface', HuggingFaceProvider),
    ('cohere', CohereProvider),
    ('replicate', ReplicateProvider),
    ('awsbedrock', AWSBedrockProvider),
    ('meta', MetaProvider),
    ('groq', GroqProvider),
    ('mistral', MistralProvider),
    ('together', TogetherProvider),
    ('ollama', OllamaProvider),
]:
    if cls:
        PROVIDER_REGISTRY[name] = cls


def get_provider(provider_name: str, config: dict):
    """Get provider instance"""
    provider_name = provider_name.lower()
    
    if provider_name not in PROVIDER_REGISTRY:
        available = ', '.join(PROVIDER_REGISTRY.keys())
        raise ValueError(f"Unknown provider: '{provider_name}'. Available: {available}")
    
    provider_class = PROVIDER_REGISTRY[provider_name]
    
    try:
        provider = provider_class(config)
    except TypeError:
        provider = provider_class()
        if hasattr(provider, 'initialize'):
            provider.initialize(config)
    
    return provider


__all__ = ['get_provider', 'PROVIDER_REGISTRY'] + [
    name for name, cls in [
        ('OpenAIProvider', OpenAIProvider),
        ('AnthropicProvider', AnthropicProvider),
        ('GoogleProvider', GoogleProvider),
        ('MockProvider', MockProvider),
        ('HuggingFaceProvider', HuggingFaceProvider),
        ('CohereProvider', CohereProvider),
        ('ReplicateProvider', ReplicateProvider),
        ('GroqProvider', GroqProvider),
        ('MistralProvider', MistralProvider),
        ('TogetherProvider', TogetherProvider),
        ('OllamaProvider', OllamaProvider),
    ] if cls
]
