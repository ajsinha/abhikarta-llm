"""
Abhikarta Facade Registration - Provider Facade Registration

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
This module registers all provider-specific facades with the FacadeFactory.
Import this module to automatically register all available facades.
"""

from llm_provider.llm_facade_factory import LLMFacadeFactory

# Import all facade implementations
from llm_provider.facade_impl.anthropic_facade import AnthropicFacade
from llm_provider.facade_impl.openai_facade import OpenAIFacade
from llm_provider.facade_impl.google_facade import GoogleFacade
from llm_provider.facade_impl.cohere_facade import CohereFacade
from llm_provider.facade_impl.mistral_facade import MistralFacade
from llm_provider.facade_impl.groq_facade import GroqFacade
from llm_provider.facade_impl.meta_facade import MetaFacade
from llm_provider.facade_impl.huggingface_facade import HuggingFaceFacade
from llm_provider.facade_impl.together_facade import TogetherFacade
from llm_provider.facade_impl.ollama_facade import OllamaFacade
from llm_provider.facade_impl.awsbedrock_facade import AWSBedrockFacade
from llm_provider.facade_impl.mock_facade import MockFacade

# Register all provider facades
LLMFacadeFactory.register_facade("anthropic", AnthropicFacade)
LLMFacadeFactory.register_facade("openai", OpenAIFacade)
LLMFacadeFactory.register_facade("google", GoogleFacade)
LLMFacadeFactory.register_facade("cohere", CohereFacade)
LLMFacadeFactory.register_facade("mistral", MistralFacade)
LLMFacadeFactory.register_facade("groq", GroqFacade)
LLMFacadeFactory.register_facade("meta", MetaFacade)
LLMFacadeFactory.register_facade("huggingface", HuggingFaceFacade)
LLMFacadeFactory.register_facade("together", TogetherFacade)
LLMFacadeFactory.register_facade("ollama", OllamaFacade)
LLMFacadeFactory.register_facade("awsbedrock", AWSBedrockFacade)
LLMFacadeFactory.register_facade("replicate", MetaFacade)  # Meta uses Replicate
LLMFacadeFactory.register_facade("mock", MockFacade)

# Total providers registered: 13
print(f"✓ Registered {len(LLMFacadeFactory.get_registered_providers())} provider facades")

__all__ = []  # This is a registration-only module
