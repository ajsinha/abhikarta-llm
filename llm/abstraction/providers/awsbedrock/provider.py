"""AWS Bedrock LLM Provider"""
import os
from typing import Any, Dict, List
from ...core.provider import LLMProvider
from ...core.facade import LLMFacade
from ...core.exceptions import ModelNotFoundError, InvalidCredentialsError, ProviderInitializationError
from .facade import AWSBedrockFacade

class AWSBedrockProvider(LLMProvider):
    def __init__(self):
        super().__init__()
        self.provider_name = "awsbedrock"
        self.client = None
    
    def initialize(self, config: Dict[str, Any]) -> None:
        self.config = config
        
        try:
            import boto3
            self.client = boto3.client(
                'bedrock-runtime',
                region_name=os.environ.get('AWS_REGION', 'us-east-1'),
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
            )
            self.initialized = True
        except ImportError:
            raise ProviderInitializationError("boto3 not installed. Install with: pip install boto3")
        except Exception as e:
            raise ProviderInitializationError(f"Failed to initialize AWS Bedrock: {str(e)}")
    
    def create_facade(self, model_name: str) -> LLMFacade:
        if model_name not in self.list_available_models():
            raise ModelNotFoundError(f"Model '{model_name}' not found")
        return AWSBedrockFacade(self, model_name, self.client)
    
    def list_available_models(self) -> List[str]:
        return [model['name'] for model in self.config.get('models', [])]
    
    def validate_credentials(self) -> bool:
        return self.initialized
    
    def get_provider_name(self) -> str:
        return self.provider_name
