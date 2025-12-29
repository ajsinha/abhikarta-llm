"""
Settings Module - Application configuration management.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.
"""

import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class DatabaseSettings:
    """Database configuration settings."""
    type: str = "sqlite"
    sqlite_path: str = "./data/abhikarta.db"
    pg_host: str = "localhost"
    pg_port: int = 5432
    pg_database: str = "abhikarta"
    pg_user: str = "abhikarta_user"
    pg_password: str = ""


@dataclass
class LLMProviderSettings:
    """LLM provider configuration."""
    enabled: bool = False
    api_key: str = ""
    base_url: str = ""
    default_model: str = ""
    fallback_model: str = ""
    region: str = ""


@dataclass
class Settings:
    """
    Central settings manager for Abhikarta-LLM.
    Loads configuration from YAML file and environment variables.
    """
    # Application settings
    app_name: str = "Abhikarta-LLM"
    app_version: str = "1.3.0"
    debug: bool = False
    secret_key: str = "change-this-secret-key-in-production"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 5000
    
    # Paths
    base_dir: str = ""
    data_dir: str = "./data"
    logs_dir: str = "./logs"
    users_file: str = "./data/users.json"
    
    # Database
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    
    # LLM Providers
    default_llm_provider: str = "openai"
    llm_providers: Dict[str, LLMProviderSettings] = field(default_factory=dict)
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "./logs/abhikarta.log"
    
    @classmethod
    def load(cls, config_path: str = "config.yaml") -> "Settings":
        """
        Load settings from YAML file and environment variables.
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            Settings instance
        """
        settings = cls()
        config_file = Path(config_path)
        
        # Set base directory
        settings.base_dir = str(config_file.parent.absolute())
        
        # Load from YAML if exists
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f) or {}
                settings._load_from_dict(config)
                logger.info(f"Configuration loaded from {config_path}")
            except Exception as e:
                logger.warning(f"Error loading config file: {e}")
        else:
            logger.warning(f"Config file not found: {config_path}, using defaults")
        
        # Override with environment variables
        settings._load_from_env()
        
        # Ensure directories exist
        settings._ensure_directories()
        
        return settings
    
    def _load_from_dict(self, config: Dict[str, Any]) -> None:
        """Load settings from dictionary."""
        # App settings
        app_config = config.get('app', {})
        self.app_name = app_config.get('name', self.app_name)
        self.app_version = app_config.get('version', self.app_version)
        self.debug = app_config.get('debug', self.debug)
        self.secret_key = app_config.get('secret_key', self.secret_key)
        
        # Server settings
        server_config = config.get('server', {})
        self.host = server_config.get('host', self.host)
        self.port = server_config.get('port', self.port)
        
        # Users file
        users_config = config.get('users', {})
        self.users_file = users_config.get('file', self.users_file)
        
        # Database settings
        db_config = config.get('database', {})
        self.database.type = db_config.get('type', self.database.type)
        
        sqlite_config = db_config.get('sqlite', {})
        self.database.sqlite_path = sqlite_config.get('path', self.database.sqlite_path)
        
        pg_config = db_config.get('postgresql', {})
        self.database.pg_host = pg_config.get('host', self.database.pg_host)
        self.database.pg_port = pg_config.get('port', self.database.pg_port)
        self.database.pg_database = pg_config.get('database', self.database.pg_database)
        self.database.pg_user = pg_config.get('user', self.database.pg_user)
        self.database.pg_password = pg_config.get('password', self.database.pg_password)
        
        # LLM settings
        llm_config = config.get('llm', {})
        self.default_llm_provider = llm_config.get('default_provider', self.default_llm_provider)
        
        providers_config = llm_config.get('providers', {})
        for provider_name, provider_config in providers_config.items():
            self.llm_providers[provider_name] = LLMProviderSettings(
                enabled=provider_config.get('enabled', False),
                api_key=provider_config.get('api_key', ''),
                base_url=provider_config.get('base_url', ''),
                default_model=provider_config.get('default_model', ''),
                fallback_model=provider_config.get('fallback_model', ''),
                region=provider_config.get('region', '')
            )
        
        # Logging settings
        logging_config = config.get('logging', {})
        self.log_level = logging_config.get('level', self.log_level)
        self.log_format = logging_config.get('format', self.log_format)
        self.log_file = logging_config.get('file', self.log_file)
    
    def _load_from_env(self) -> None:
        """Override settings from environment variables."""
        # App
        self.debug = os.getenv('DEBUG', str(self.debug)).lower() == 'true'
        self.secret_key = os.getenv('SECRET_KEY', self.secret_key)
        
        # Server
        self.host = os.getenv('HOST', self.host)
        self.port = int(os.getenv('PORT', str(self.port)))
        
        # Database
        self.database.type = os.getenv('DB_TYPE', self.database.type)
        self.database.sqlite_path = os.getenv('SQLITE_PATH', self.database.sqlite_path)
        self.database.pg_host = os.getenv('PG_HOST', self.database.pg_host)
        self.database.pg_port = int(os.getenv('PG_PORT', str(self.database.pg_port)))
        self.database.pg_database = os.getenv('PG_DATABASE', self.database.pg_database)
        self.database.pg_user = os.getenv('PG_USER', self.database.pg_user)
        self.database.pg_password = os.getenv('PG_PASSWORD', self.database.pg_password)
        
        # LLM API Keys
        if 'openai' in self.llm_providers:
            self.llm_providers['openai'].api_key = os.getenv(
                'OPENAI_API_KEY', self.llm_providers['openai'].api_key
            )
        if 'anthropic' in self.llm_providers:
            self.llm_providers['anthropic'].api_key = os.getenv(
                'ANTHROPIC_API_KEY', self.llm_providers['anthropic'].api_key
            )
        if 'ollama' in self.llm_providers:
            self.llm_providers['ollama'].base_url = os.getenv(
                'OLLAMA_BASE_URL', self.llm_providers['ollama'].base_url
            )
    
    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        directories = [self.data_dir, self.logs_dir]
        for dir_path in directories:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def get_database_url(self) -> str:
        """Get database URL based on configuration."""
        if self.database.type == "sqlite":
            return f"sqlite:///{self.database.sqlite_path}"
        elif self.database.type == "postgresql":
            return (
                f"postgresql://{self.database.pg_user}:{self.database.pg_password}"
                f"@{self.database.pg_host}:{self.database.pg_port}/{self.database.pg_database}"
            )
        else:
            raise ValueError(f"Unsupported database type: {self.database.type}")
