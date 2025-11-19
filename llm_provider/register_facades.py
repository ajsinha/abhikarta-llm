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

from llm_provider.facade_factory import FacadeFactory

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
FacadeFactory.register_facade("anthropic", AnthropicFacade)
FacadeFactory.register_facade("openai", OpenAIFacade)
FacadeFactory.register_facade("google", GoogleFacade)
FacadeFactory.register_facade("cohere", CohereFacade)
FacadeFactory.register_facade("mistral", MistralFacade)
FacadeFactory.register_facade("groq", GroqFacade)
FacadeFactory.register_facade("meta", MetaFacade)
FacadeFactory.register_facade("huggingface", HuggingFaceFacade)
FacadeFactory.register_facade("together", TogetherFacade)
FacadeFactory.register_facade("ollama", OllamaFacade)
FacadeFactory.register_facade("awsbedrock", AWSBedrockFacade)
FacadeFactory.register_facade("replicate", MetaFacade)  # Meta uses Replicate
FacadeFactory.register_facade("mock", MockFacade)

# Total providers registered: 13
print(f"✓ Registered {len(FacadeFactory.get_registered_providers())} provider facades")

__all__ = []  # This is a registration-only module
