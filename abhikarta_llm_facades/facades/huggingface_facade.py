"""
HuggingFace LLM Facade Implementation

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This module and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

This document is provided "as is" without warranty of any kind, either expressed or implied.
The copyright holder shall not be liable for any damages arising from the use of this
document or the software system it describes.

Patent Pending: Certain architectural patterns and implementations described in this
module may be subject to patent applications.

Description:
This module provides a concrete implementation of the LLMFacade interface for
Hugging Face models, supporting both API-based inference and local model execution.
"""

import os
import time
from typing import List, Dict, Any, Optional, Union, Iterator

from .llm_facade_base import LLMFacadeBase
from .llm_facade import (
    ModelCapability,
    GenerationConfig,
    Messages,
    TextStream,
    ToolDefinition,
    Embedding,
    LLMFacadeException,
    AuthenticationException,
)


class HuggingfaceFacade(LLMFacadeBase):
    """
    HuggingFace implementation of the LLMFacade interface.

    Supports both API-based inference via Inference API and local model execution
    via transformers library. Automatically detects model capabilities based on
    model architecture and configuration.

    Features:
    - Text generation and chat completion
    - Embeddings (for compatible models)
    - Automatic capability detection
    - Support for custom model configurations
    - Streaming support
    - Local and API-based inference

    Example:
        >>> from huggingface_facade import HuggingfaceFacade
        >>> llm = HuggingfaceFacade(
        ...     model_name="meta-llama/Llama-2-7b-chat-hf",
        ...     api_key="hf_..."
        ... )
        >>> response = llm.chat_completion([
        ...     {"role": "user", "content": "Hello!"}
        ... ])
        >>> print(response["content"])
    """

    # Model configuration mappings for capability detection
    CHAT_MODELS = {
        "llama-2", "llama-3", "llama-3.1", "llama-3.2",
        "mistral", "mixtral", "codellama", "starcoder", "wizardcoder",
        "falcon", "vicuna", "alpaca", "chat", "instruct"
    }

    EMBEDDING_MODELS = {
        "sentence-transformers", "all-mpnet", "all-MiniLM",
        "bge-", "e5-", "instructor-", "gte-", "embed"
    }

    CODE_MODELS = {
        "codellama", "starcoder", "wizardcoder", "codegen", "santacoder", "code"
    }

    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        use_local: bool = False,
        device: str = "auto",
        **kwargs
    ):
        """
        Initialize HuggingFace LLM Facade.

        Args:
            model_name: HuggingFace model identifier (e.g., "meta-llama/Llama-2-7b-chat-hf")
            api_key: HuggingFace API token (reads from HF_TOKEN env var if None)
            base_url: Custom inference endpoint URL (optional)
            timeout: Request timeout in seconds (default: 120)
            max_retries: Number of retry attempts for failed requests
            use_local: Use local model execution instead of API (requires transformers)
            device: Device for local execution ("cpu", "cuda", "mps", "auto")
            **kwargs: Additional configuration
                - trust_remote_code: Allow remote code execution (default: False)
                - load_in_8bit: Use 8-bit quantization for local models
                - load_in_4bit: Use 4-bit quantization for local models
                - torch_dtype: Torch data type for local models
        """
        # Get API key from environment if not provided
        api_key = api_key or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
        
        # Initialize base class
        super().__init__(
            provider_name="huggingface",
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
            timeout=timeout or 120.0,
            max_retries=max_retries,
            **kwargs
        )
        
        # HuggingFace-specific attributes
        self.use_local = use_local
        self.device = device
        
        # Client/model holders
        self.client = None
        self.tokenizer = None
        self.model = None
        
        # Initialize client or local model
        if use_local:
            self._initialize_local_model()
        else:
            self._initialize_api_client()
        
        # Detect and cache capabilities
        self._capabilities_cache = self._detect_capabilities()
    
    def _initialize_api_client(self):
        """Initialize HuggingFace Inference API client."""
        try:
            from huggingface_hub import InferenceClient
            
            self.client = InferenceClient(
                model=self.model_name,
                token=self.api_key,
                timeout=self.timeout
            )
            
            self.logger.info(
                f"Initialized HuggingFace API client for {self.model_name}"
            )
            
        except ImportError:
            raise ImportError(
                "Please install huggingface_hub: pip install huggingface_hub"
            )
        except Exception as e:
            raise AuthenticationException(
                f"Failed to initialize HuggingFace client: {e}"
            )
    
    def _initialize_local_model(self):
        """Initialize local model using transformers."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            self.logger.info(f"Loading local model: {self.model_name}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                token=self.api_key,
                trust_remote_code=self.kwargs.get("trust_remote_code", False)
            )
            
            # Configure model loading
            load_kwargs = {
                "token": self.api_key,
                "trust_remote_code": self.kwargs.get("trust_remote_code", False)
            }
            
            # Handle quantization
            if self.kwargs.get("load_in_8bit"):
                load_kwargs["load_in_8bit"] = True
            elif self.kwargs.get("load_in_4bit"):
                load_kwargs["load_in_4bit"] = True
            
            # Set dtype
            if "torch_dtype" in self.kwargs:
                load_kwargs["torch_dtype"] = self.kwargs["torch_dtype"]
            else:
                load_kwargs["torch_dtype"] = torch.float16
            
            # Set device
            if self.device == "auto":
                load_kwargs["device_map"] = "auto"
            else:
                load_kwargs["device_map"] = self.device
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **load_kwargs
            )
            
            self.logger.info(f"Successfully loaded local model: {self.model_name}")
            
        except ImportError:
            raise ImportError(
                "Please install transformers and torch: pip install transformers torch"
            )
        except Exception as e:
            raise LLMFacadeException(f"Failed to load local model: {e}")
    
    def _detect_capabilities(self) -> List[ModelCapability]:
        """Detect model capabilities based on model name and type."""
        capabilities = [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.STREAMING
        ]
        
        model_lower = self.model_name.lower()
        
        # Check if it's a chat model
        if any(keyword in model_lower for keyword in self.CHAT_MODELS):
            capabilities.append(ModelCapability.CHAT_COMPLETION)
        
        # Check if it's an embedding model
        if any(keyword in model_lower for keyword in self.EMBEDDING_MODELS):
            capabilities.append(ModelCapability.EMBEDDINGS)
        
        # Check if it's a code model
        if any(keyword in model_lower for keyword in self.CODE_MODELS):
            capabilities.extend([
                ModelCapability.CODE_GENERATION,
                ModelCapability.CHAT_COMPLETION
            ])
        
        # Modern models support reasoning
        if any(keyword in model_lower for keyword in ["llama-3", "mixtral", "mistral-large"]):
            capabilities.append(ModelCapability.REASONING)
        
        return list(set(capabilities))  # Remove duplicates
    
    def get_capabilities(self) -> List[ModelCapability]:
        """Get list of supported capabilities."""
        if self._capabilities_cache:
            return self._capabilities_cache.copy()
        return super().get_capabilities()
    
    def _format_chat_prompt(self, messages: Messages) -> str:
        """Format messages into a prompt string for the model."""
        # Check if model has a specific chat template
        if self.tokenizer and hasattr(self.tokenizer, 'apply_chat_template'):
            try:
                return self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
            except Exception as e:
                self.logger.warning(f"Could not use chat template: {e}")
        
        # Fallback to generic formatting
        return self.format_messages(messages)
    
    def chat_completion(
        self,
        messages: Messages,
        tools: Optional[List[ToolDefinition]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate chat completion using HuggingFace model.
        
        Args:
            messages: List of message dictionaries
            tools: Optional tool definitions (not widely supported)
            tool_choice: Tool selection strategy
            config: Generation configuration
            **kwargs: Additional parameters
        
        Returns:
            Dictionary with completion result
        """
        self._check_capability(ModelCapability.CHAT_COMPLETION)
        
        start_time = time.time()
        
        try:
            # Format messages into prompt
            prompt = self._format_chat_prompt(messages)
            
            # Build generation parameters
            gen_params = {}
            
            if config:
                config_dict = config.to_dict()
                if config_dict.get("max_tokens"):
                    gen_params["max_new_tokens"] = config_dict["max_tokens"]
                if config_dict.get("temperature") is not None:
                    gen_params["temperature"] = config_dict["temperature"]
                if config_dict.get("top_p") is not None:
                    gen_params["top_p"] = config_dict["top_p"]
                if config_dict.get("top_k") is not None:
                    gen_params["top_k"] = config_dict["top_k"]
                if config_dict.get("repetition_penalty") is not None:
                    gen_params["repetition_penalty"] = config_dict["repetition_penalty"]
            
            # Generate response
            if self.use_local:
                content = self._generate_local(prompt, gen_params)
            else:
                content = self._generate_api(prompt, gen_params)
            
            # Build result
            result = {
                "content": content.strip(),
                "role": "assistant",
                "finish_reason": "stop",
                "usage": {
                    "prompt_tokens": self.count_tokens(prompt),
                    "completion_tokens": self.count_tokens(content),
                    "total_tokens": self.count_tokens(prompt) + self.count_tokens(content)
                }
            }
            
            # Log request
            latency = (time.time() - start_time) * 1000
            self.log_request("chat_completion", messages, result, latency)
            
            return result
            
        except Exception as e:
            self._handle_error(e)
    
    def completion(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> str:
        """
        Generate text completion.
        
        Args:
            prompt: Input prompt
            config: Generation configuration
            **kwargs: Additional parameters
        
        Returns:
            Generated text
        """
        try:
            # Build generation parameters
            gen_params = {}
            
            if config:
                config_dict = config.to_dict()
                if config_dict.get("max_tokens"):
                    gen_params["max_new_tokens"] = config_dict["max_tokens"]
                if config_dict.get("temperature") is not None:
                    gen_params["temperature"] = config_dict["temperature"]
                if config_dict.get("top_p") is not None:
                    gen_params["top_p"] = config_dict["top_p"]
            
            # Generate
            if self.use_local:
                return self._generate_local(prompt, gen_params)
            else:
                return self._generate_api(prompt, gen_params)
                
        except Exception as e:
            self._handle_error(e)
    
    def _generate_api(self, prompt: str, params: Dict[str, Any]) -> str:
        """Generate text using HuggingFace Inference API."""
        try:
            response = self.client.text_generation(
                prompt,
                **params,
                return_full_text=False
            )
            return response
        except Exception as e:
            raise LLMFacadeException(f"API generation failed: {e}")
    
    def _generate_local(self, prompt: str, params: Dict[str, Any]) -> str:
        """Generate text using local model."""
        try:
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            # Move to device
            if self.model.device.type != "cpu":
                inputs = inputs.to(self.model.device)
            
            # Generate
            outputs = self.model.generate(
                **inputs,
                **params,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Decode output
            generated_text = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],
                skip_special_tokens=True
            )
            
            return generated_text
            
        except Exception as e:
            raise LLMFacadeException(f"Local generation failed: {e}")
    
    def stream_chat_completion(
        self,
        messages: Messages,
        tools: Optional[List[ToolDefinition]] = None,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> Iterator[str]:
        """
        Stream chat completion responses.
        
        Args:
            messages: List of message dictionaries
            tools: Optional tool definitions
            config: Generation configuration
            **kwargs: Additional parameters
        
        Yields:
            Text chunks as they are generated
        """
        self._check_capability(ModelCapability.STREAMING)
        
        try:
            prompt = self._format_chat_prompt(messages)
            
            # Build generation parameters
            gen_params = {}
            if config:
                config_dict = config.to_dict()
                if config_dict.get("max_tokens"):
                    gen_params["max_new_tokens"] = config_dict["max_tokens"]
                if config_dict.get("temperature") is not None:
                    gen_params["temperature"] = config_dict["temperature"]
            
            # Stream from API (local streaming not implemented)
            if self.use_local:
                # For local models, return full generation as single chunk
                yield self._generate_local(prompt, gen_params)
            else:
                # Stream from API
                for chunk in self.client.text_generation(
                    prompt,
                    stream=True,
                    return_full_text=False,
                    **gen_params
                ):
                    if chunk:
                        yield chunk
                        
        except Exception as e:
            self._handle_error(e)
    
    def get_embeddings(
        self,
        texts: Union[str, List[str]],
        model: Optional[str] = None,
        **kwargs
    ) -> List[Embedding]:
        """
        Generate embeddings for text(s).
        
        Args:
            texts: Single text or list of texts
            model: Embedding model name (uses current model if None)
            **kwargs: Additional parameters
        
        Returns:
            List of embedding vectors
        """
        self._check_capability(ModelCapability.EMBEDDINGS)
        
        if isinstance(texts, str):
            texts = [texts]
        
        try:
            embeddings = []
            
            if self.use_local:
                # Use sentence-transformers for local embeddings
                from sentence_transformers import SentenceTransformer
                
                model_obj = SentenceTransformer(self.model_name)
                embeddings = model_obj.encode(texts).tolist()
                
            else:
                # Use Inference API
                for text in texts:
                    embedding = self.client.feature_extraction(text)
                    # Average pooling if needed
                    if hasattr(embedding, 'shape') and len(embedding.shape) > 1:
                        import numpy as np
                        embedding = np.array(embedding).mean(axis=0)
                    embeddings.append(list(embedding))
            
            return embeddings
            
        except Exception as e:
            self._handle_error(e)
    
    def count_tokens(self, text: str, **kwargs) -> int:
        """
        Count tokens using HuggingFace tokenizer if available.
        
        Args:
            text: Text to count tokens for
            **kwargs: Additional parameters
        
        Returns:
            Token count
        """
        if self.tokenizer:
            try:
                return len(self.tokenizer.encode(text))
            except Exception as e:
                self.logger.warning(f"Could not count tokens: {e}")
        
        # Fall back to base class estimation
        return super().count_tokens(text, **kwargs)
    
    def close(self):
        """Close connections and cleanup resources."""
        if self.model is not None:
            # Clear model from memory
            self.model = None
            self.tokenizer = None
            
            # Clear GPU cache if using CUDA
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except:
                pass
        
        super().close()


__all__ = ['HuggingfaceFacade']
