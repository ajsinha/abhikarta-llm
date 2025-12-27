"""
LangChain LLM Factory - Create LangChain LLM instances from provider configurations.

Supports: OpenAI, Anthropic, Google, Azure, AWS Bedrock, Ollama, Mistral, Cohere,
          Together AI, Groq, HuggingFace

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import logging
from typing import Dict, Any, Optional, Union
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LLMFactory:
    """
    Factory for creating LangChain LLM instances from database configurations.
    
    Supports dynamic provider/model loading from the llm_providers and llm_models tables.
    """
    
    # Mapping of provider types to LangChain classes
    PROVIDER_MAPPING = {
        'openai': 'langchain_openai.ChatOpenAI',
        'anthropic': 'langchain_anthropic.ChatAnthropic',
        'google': 'langchain_google_genai.ChatGoogleGenerativeAI',
        'azure_openai': 'langchain_openai.AzureChatOpenAI',
        'bedrock': 'langchain_aws.ChatBedrock',
        'ollama': 'langchain_ollama.ChatOllama',
        'mistral': 'langchain_mistralai.ChatMistralAI',
        'cohere': 'langchain_cohere.ChatCohere',
        'together': 'langchain_together.ChatTogether',
        'groq': 'langchain_groq.ChatGroq',
        'huggingface': 'langchain_huggingface.ChatHuggingFace',
        'fireworks': 'langchain_fireworks.ChatFireworks',
    }
    
    @classmethod
    def create_llm(cls, provider_config: Dict[str, Any], model_config: Dict[str, Any], 
                   **kwargs) -> Any:
        """
        Create a LangChain LLM instance from provider and model configurations.
        
        Args:
            provider_config: Provider configuration from llm_providers table
            model_config: Model configuration from llm_models table
            **kwargs: Additional parameters to pass to the LLM
            
        Returns:
            LangChain BaseChatModel instance
        """
        provider_type = provider_config.get('provider_type', '').lower()
        
        if provider_type not in cls.PROVIDER_MAPPING:
            raise ValueError(f"Unsupported provider type: {provider_type}")
        
        # Get the appropriate creator method
        creator_method = getattr(cls, f'_create_{provider_type}_llm', None)
        if creator_method:
            return creator_method(provider_config, model_config, **kwargs)
        else:
            return cls._create_generic_llm(provider_type, provider_config, model_config, **kwargs)
    
    @classmethod
    def _create_openai_llm(cls, provider_config: Dict, model_config: Dict, **kwargs):
        """Create OpenAI LLM instance."""
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError("langchain-openai is required. Install with: pip install langchain-openai")
        
        import json
        config = json.loads(provider_config.get('config_json', '{}'))
        model_params = json.loads(model_config.get('parameters_json', '{}'))
        
        return ChatOpenAI(
            model=model_config.get('model_id', 'gpt-4o'),
            api_key=config.get('api_key'),
            base_url=config.get('base_url'),
            temperature=model_params.get('temperature', kwargs.get('temperature', 0.7)),
            max_tokens=model_params.get('max_tokens', kwargs.get('max_tokens', 2000)),
            **kwargs
        )
    
    @classmethod
    def _create_anthropic_llm(cls, provider_config: Dict, model_config: Dict, **kwargs):
        """Create Anthropic LLM instance."""
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError:
            raise ImportError("langchain-anthropic is required. Install with: pip install langchain-anthropic")
        
        import json
        config = json.loads(provider_config.get('config_json', '{}'))
        model_params = json.loads(model_config.get('parameters_json', '{}'))
        
        return ChatAnthropic(
            model=model_config.get('model_id', 'claude-3-5-sonnet-20241022'),
            api_key=config.get('api_key'),
            temperature=model_params.get('temperature', kwargs.get('temperature', 0.7)),
            max_tokens=model_params.get('max_tokens', kwargs.get('max_tokens', 2000)),
            **kwargs
        )
    
    @classmethod
    def _create_google_llm(cls, provider_config: Dict, model_config: Dict, **kwargs):
        """Create Google Generative AI LLM instance."""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError:
            raise ImportError("langchain-google-genai is required. Install with: pip install langchain-google-genai")
        
        import json
        config = json.loads(provider_config.get('config_json', '{}'))
        model_params = json.loads(model_config.get('parameters_json', '{}'))
        
        return ChatGoogleGenerativeAI(
            model=model_config.get('model_id', 'gemini-1.5-pro'),
            google_api_key=config.get('api_key'),
            temperature=model_params.get('temperature', kwargs.get('temperature', 0.7)),
            max_output_tokens=model_params.get('max_tokens', kwargs.get('max_tokens', 2000)),
            **kwargs
        )
    
    @classmethod
    def _create_azure_openai_llm(cls, provider_config: Dict, model_config: Dict, **kwargs):
        """Create Azure OpenAI LLM instance."""
        try:
            from langchain_openai import AzureChatOpenAI
        except ImportError:
            raise ImportError("langchain-openai is required. Install with: pip install langchain-openai")
        
        import json
        config = json.loads(provider_config.get('config_json', '{}'))
        model_params = json.loads(model_config.get('parameters_json', '{}'))
        
        return AzureChatOpenAI(
            azure_deployment=model_config.get('model_id'),
            api_key=config.get('api_key'),
            azure_endpoint=config.get('endpoint'),
            api_version=config.get('api_version', '2024-02-15-preview'),
            temperature=model_params.get('temperature', kwargs.get('temperature', 0.7)),
            max_tokens=model_params.get('max_tokens', kwargs.get('max_tokens', 2000)),
            **kwargs
        )
    
    @classmethod
    def _create_bedrock_llm(cls, provider_config: Dict, model_config: Dict, **kwargs):
        """Create AWS Bedrock LLM instance."""
        try:
            from langchain_aws import ChatBedrock
        except ImportError:
            raise ImportError("langchain-aws is required. Install with: pip install langchain-aws")
        
        import json
        config = json.loads(provider_config.get('config_json', '{}'))
        model_params = json.loads(model_config.get('parameters_json', '{}'))
        
        return ChatBedrock(
            model_id=model_config.get('model_id', 'anthropic.claude-3-sonnet-20240229-v1:0'),
            region_name=config.get('region', 'us-east-1'),
            credentials_profile_name=config.get('profile'),
            model_kwargs={
                'temperature': model_params.get('temperature', kwargs.get('temperature', 0.7)),
                'max_tokens': model_params.get('max_tokens', kwargs.get('max_tokens', 2000)),
            },
            **kwargs
        )
    
    @classmethod
    def _create_ollama_llm(cls, provider_config: Dict, model_config: Dict, **kwargs):
        """Create Ollama LLM instance."""
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            raise ImportError("langchain-ollama is required. Install with: pip install langchain-ollama")
        
        import json
        config = json.loads(provider_config.get('config_json', '{}'))
        model_params = json.loads(model_config.get('parameters_json', '{}'))
        
        return ChatOllama(
            model=model_config.get('model_id', 'llama3.2'),
            base_url=config.get('base_url', 'http://localhost:11434'),
            temperature=model_params.get('temperature', kwargs.get('temperature', 0.7)),
            num_predict=model_params.get('max_tokens', kwargs.get('max_tokens', 2000)),
            **kwargs
        )
    
    @classmethod
    def _create_mistral_llm(cls, provider_config: Dict, model_config: Dict, **kwargs):
        """Create Mistral AI LLM instance."""
        try:
            from langchain_mistralai import ChatMistralAI
        except ImportError:
            raise ImportError("langchain-mistralai is required. Install with: pip install langchain-mistralai")
        
        import json
        config = json.loads(provider_config.get('config_json', '{}'))
        model_params = json.loads(model_config.get('parameters_json', '{}'))
        
        return ChatMistralAI(
            model=model_config.get('model_id', 'mistral-large-latest'),
            api_key=config.get('api_key'),
            temperature=model_params.get('temperature', kwargs.get('temperature', 0.7)),
            max_tokens=model_params.get('max_tokens', kwargs.get('max_tokens', 2000)),
            **kwargs
        )
    
    @classmethod
    def _create_cohere_llm(cls, provider_config: Dict, model_config: Dict, **kwargs):
        """Create Cohere LLM instance."""
        try:
            from langchain_cohere import ChatCohere
        except ImportError:
            raise ImportError("langchain-cohere is required. Install with: pip install langchain-cohere")
        
        import json
        config = json.loads(provider_config.get('config_json', '{}'))
        model_params = json.loads(model_config.get('parameters_json', '{}'))
        
        return ChatCohere(
            model=model_config.get('model_id', 'command-r-plus'),
            cohere_api_key=config.get('api_key'),
            temperature=model_params.get('temperature', kwargs.get('temperature', 0.7)),
            max_tokens=model_params.get('max_tokens', kwargs.get('max_tokens', 2000)),
            **kwargs
        )
    
    @classmethod
    def _create_together_llm(cls, provider_config: Dict, model_config: Dict, **kwargs):
        """Create Together AI LLM instance."""
        try:
            from langchain_together import ChatTogether
        except ImportError:
            raise ImportError("langchain-together is required. Install with: pip install langchain-together")
        
        import json
        config = json.loads(provider_config.get('config_json', '{}'))
        model_params = json.loads(model_config.get('parameters_json', '{}'))
        
        return ChatTogether(
            model=model_config.get('model_id', 'meta-llama/Llama-3-70b-chat-hf'),
            api_key=config.get('api_key'),
            temperature=model_params.get('temperature', kwargs.get('temperature', 0.7)),
            max_tokens=model_params.get('max_tokens', kwargs.get('max_tokens', 2000)),
            **kwargs
        )
    
    @classmethod
    def _create_groq_llm(cls, provider_config: Dict, model_config: Dict, **kwargs):
        """Create Groq LLM instance."""
        try:
            from langchain_groq import ChatGroq
        except ImportError:
            raise ImportError("langchain-groq is required. Install with: pip install langchain-groq")
        
        import json
        config = json.loads(provider_config.get('config_json', '{}'))
        model_params = json.loads(model_config.get('parameters_json', '{}'))
        
        return ChatGroq(
            model=model_config.get('model_id', 'llama-3.1-70b-versatile'),
            api_key=config.get('api_key'),
            temperature=model_params.get('temperature', kwargs.get('temperature', 0.7)),
            max_tokens=model_params.get('max_tokens', kwargs.get('max_tokens', 2000)),
            **kwargs
        )
    
    @classmethod
    def _create_huggingface_llm(cls, provider_config: Dict, model_config: Dict, **kwargs):
        """Create HuggingFace LLM instance."""
        try:
            from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
        except ImportError:
            raise ImportError("langchain-huggingface is required. Install with: pip install langchain-huggingface")
        
        import json
        config = json.loads(provider_config.get('config_json', '{}'))
        model_params = json.loads(model_config.get('parameters_json', '{}'))
        
        # Create endpoint first
        endpoint = HuggingFaceEndpoint(
            repo_id=model_config.get('model_id', 'meta-llama/Meta-Llama-3-8B-Instruct'),
            huggingfacehub_api_token=config.get('api_key'),
            temperature=model_params.get('temperature', kwargs.get('temperature', 0.7)),
            max_new_tokens=model_params.get('max_tokens', kwargs.get('max_tokens', 2000)),
        )
        
        return ChatHuggingFace(llm=endpoint, **kwargs)
    
    @classmethod
    def _create_generic_llm(cls, provider_type: str, provider_config: Dict, 
                           model_config: Dict, **kwargs):
        """Create LLM using generic approach for unsupported providers."""
        # Fallback to OpenAI-compatible endpoint
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError("langchain-openai is required for generic LLM support")
        
        import json
        config = json.loads(provider_config.get('config_json', '{}'))
        model_params = json.loads(model_config.get('parameters_json', '{}'))
        
        return ChatOpenAI(
            model=model_config.get('model_id'),
            api_key=config.get('api_key'),
            base_url=config.get('base_url'),
            temperature=model_params.get('temperature', kwargs.get('temperature', 0.7)),
            max_tokens=model_params.get('max_tokens', kwargs.get('max_tokens', 2000)),
            **kwargs
        )


def get_langchain_llm(db_facade, model_id: str = None, provider_id: str = None, 
                      **kwargs) -> Any:
    """
    Convenience function to get a LangChain LLM from database configuration.
    
    Args:
        db_facade: Database facade instance
        model_id: Optional specific model ID to use
        provider_id: Optional provider ID (if model_id not specified, uses default model)
        **kwargs: Additional parameters for LLM
        
    Returns:
        LangChain BaseChatModel instance
    """
    import json
    
    # Get model configuration
    if model_id:
        model = db_facade.fetch_one(
            "SELECT * FROM llm_models WHERE model_id = ? AND is_active = 1",
            (model_id,)
        )
        if not model:
            raise ValueError(f"Model not found or inactive: {model_id}")
        provider_id = model.get('provider_id')
    elif provider_id:
        # Get default model for provider
        model = db_facade.fetch_one(
            """SELECT * FROM llm_models 
               WHERE provider_id = ? AND is_default = 1 AND is_active = 1""",
            (provider_id,)
        )
        if not model:
            model = db_facade.fetch_one(
                "SELECT * FROM llm_models WHERE provider_id = ? AND is_active = 1",
                (provider_id,)
            )
        if not model:
            raise ValueError(f"No active models found for provider: {provider_id}")
    else:
        # Get system default model
        model = db_facade.fetch_one(
            "SELECT * FROM llm_models WHERE is_default = 1 AND is_active = 1"
        )
        if not model:
            model = db_facade.fetch_one(
                "SELECT * FROM llm_models WHERE is_active = 1"
            )
        if not model:
            raise ValueError("No active LLM models configured")
        provider_id = model.get('provider_id')
    
    # Get provider configuration
    provider = db_facade.fetch_one(
        "SELECT * FROM llm_providers WHERE provider_id = ? AND is_active = 1",
        (provider_id,)
    )
    if not provider:
        raise ValueError(f"Provider not found or inactive: {provider_id}")
    
    return LLMFactory.create_llm(dict(provider), dict(model), **kwargs)


class LangChainCallbackHandler:
    """
    Custom callback handler for logging LangChain LLM calls to the database.
    """
    
    def __init__(self, db_facade, execution_id: str = None):
        self.db_facade = db_facade
        self.execution_id = execution_id
        self.start_time = None
    
    def on_llm_start(self, serialized: Dict, prompts: list, **kwargs):
        """Called when LLM starts processing."""
        import time
        self.start_time = time.time()
        logger.debug(f"LLM started with {len(prompts)} prompts")
    
    def on_llm_end(self, response, **kwargs):
        """Called when LLM finishes processing."""
        import time
        import uuid
        
        duration_ms = int((time.time() - self.start_time) * 1000) if self.start_time else 0
        
        # Log to database
        try:
            token_usage = getattr(response, 'llm_output', {}).get('token_usage', {})
            
            self.db_facade.execute(
                """INSERT INTO llm_call_logs 
                   (log_id, execution_id, model, provider, input_tokens, output_tokens,
                    total_tokens, latency_ms, status, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                (
                    str(uuid.uuid4()),
                    self.execution_id,
                    kwargs.get('model', 'unknown'),
                    kwargs.get('provider', 'unknown'),
                    token_usage.get('prompt_tokens', 0),
                    token_usage.get('completion_tokens', 0),
                    token_usage.get('total_tokens', 0),
                    duration_ms,
                    'success'
                )
            )
        except Exception as e:
            logger.warning(f"Failed to log LLM call: {e}")
    
    def on_llm_error(self, error: Exception, **kwargs):
        """Called when LLM encounters an error."""
        logger.error(f"LLM error: {error}")
