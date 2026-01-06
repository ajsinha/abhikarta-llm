"""
Settings Module - Application configuration management using PropertiesConfigurator.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Version: 1.5.3 - Standardized to use PropertiesConfigurator (no YAML)

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
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
class CodeFragmentsSettings:
    """
    Code fragments sync configuration.
    
    Controls how code fragments are synced to local Python modules.
    """
    # Enable/disable sync service
    enabled: bool = True
    
    # Target path for code_fragments module
    # Default: {project_root}/code_fragments
    target_path: str = ""
    
    # Sync interval in seconds (default 5 minutes)
    sync_interval_seconds: int = 300
    
    # Sync fragments on startup
    sync_on_startup: bool = True
    
    # Enable background watcher
    watch_enabled: bool = True
    
    # Status filter - only sync these statuses
    status_filter: List[str] = field(default_factory=lambda: ["approved", "published"])
    
    # Reload strategy: 'graceful' or 'immediate'
    reload_strategy: str = "graceful"
    
    # Max wait for graceful reload in seconds
    max_wait_seconds: int = 30
    
    # S3 source configuration
    s3_enabled: bool = False
    s3_bucket: str = ""
    s3_prefix: str = ""
    
    # Filesystem source configuration
    filesystem_enabled: bool = False
    filesystem_paths: List[str] = field(default_factory=list)


@dataclass
class Settings:
    """
    Central settings manager for Abhikarta-LLM.
    
    Loads configuration from PropertiesConfigurator (application.properties).
    All configuration is managed through properties files - no YAML.
    """
    # Application settings
    app_name: str = "Abhikarta-LLM"
    app_version: str = "1.5.3"
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
    default_llm_provider: str = "ollama"
    default_llm_model: str = "llama3.2:3b"
    llm_providers: Dict[str, LLMProviderSettings] = field(default_factory=dict)
    
    # Code Fragments Sync (v1.5.2)
    code_fragments: CodeFragmentsSettings = field(default_factory=CodeFragmentsSettings)
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "./logs/abhikarta.log"
    
    @classmethod
    def load_from_properties(cls, prop_conf) -> "Settings":
        """
        Load settings from PropertiesConfigurator.
        
        Args:
            prop_conf: PropertiesConfigurator instance
            
        Returns:
            Settings instance
        """
        settings = cls()
        
        # Application settings
        settings.app_name = prop_conf.get('app.name', settings.app_name)
        settings.app_version = prop_conf.get('app.version', settings.app_version)
        settings.debug = prop_conf.get_bool('app.debug', settings.debug)
        settings.secret_key = prop_conf.get('app.secret.key', settings.secret_key)
        
        # Server settings
        settings.host = prop_conf.get('server.host', settings.host)
        settings.port = prop_conf.get_int('server.port', settings.port)
        
        # Paths
        settings.data_dir = prop_conf.get('data.dir', settings.data_dir)
        settings.logs_dir = prop_conf.get('logs.dir', settings.logs_dir)
        settings.users_file = prop_conf.get('users.file', settings.users_file)
        
        # Database settings
        settings.database.type = prop_conf.get('database.type', settings.database.type)
        settings.database.sqlite_path = prop_conf.get('database.sqlite.path', settings.database.sqlite_path)
        settings.database.pg_host = prop_conf.get('database.postgresql.host', settings.database.pg_host)
        settings.database.pg_port = prop_conf.get_int('database.postgresql.port', settings.database.pg_port)
        settings.database.pg_database = prop_conf.get('database.postgresql.database', settings.database.pg_database)
        settings.database.pg_user = prop_conf.get('database.postgresql.user', settings.database.pg_user)
        settings.database.pg_password = prop_conf.get('database.postgresql.password', settings.database.pg_password)
        
        # LLM settings
        settings.default_llm_provider = prop_conf.get('llm.default.provider', settings.default_llm_provider)
        
        # Load LLM providers
        settings._load_llm_providers(prop_conf)
        
        # Logging settings
        settings.log_level = prop_conf.get('logging.level', settings.log_level)
        settings.log_format = prop_conf.get('logging.format', settings.log_format)
        settings.log_file = prop_conf.get('logging.file', settings.log_file)
        
        # Code Fragments Sync settings (v1.5.2)
        settings._load_code_fragments_settings(prop_conf)
        
        # Ensure directories exist
        settings._ensure_directories()
        
        logger.info(f"Settings loaded from PropertiesConfigurator")
        return settings
    
    def _load_llm_providers(self, prop_conf) -> None:
        """Load LLM provider settings from properties."""
        providers = ['openai', 'anthropic', 'ollama', 'bedrock', 'google', 'cohere', 
                     'mistral', 'groq', 'together', 'deepseek', 'xai']
        
        for provider in providers:
            prefix = f'llm.{provider}'
            enabled = prop_conf.get_bool(f'{prefix}.enabled', False)
            
            if enabled or prop_conf.get(f'{prefix}.api.key'):
                self.llm_providers[provider] = LLMProviderSettings(
                    enabled=enabled,
                    api_key=prop_conf.get(f'{prefix}.api.key', ''),
                    base_url=prop_conf.get(f'{prefix}.base.url', ''),
                    default_model=prop_conf.get(f'{prefix}.default.model', ''),
                    fallback_model=prop_conf.get(f'{prefix}.fallback.model', ''),
                    region=prop_conf.get(f'{prefix}.region', '')
                )
    
    def _load_code_fragments_settings(self, prop_conf) -> None:
        """Load code fragments sync settings from properties."""
        prefix = 'code.fragments'
        
        self.code_fragments.enabled = prop_conf.get_bool(
            f'{prefix}.enabled', self.code_fragments.enabled)
        self.code_fragments.target_path = prop_conf.get(
            f'{prefix}.target.path', self.code_fragments.target_path)
        self.code_fragments.sync_interval_seconds = prop_conf.get_int(
            f'{prefix}.sync.interval.seconds', self.code_fragments.sync_interval_seconds)
        self.code_fragments.sync_on_startup = prop_conf.get_bool(
            f'{prefix}.sync.on.startup', self.code_fragments.sync_on_startup)
        self.code_fragments.watch_enabled = prop_conf.get_bool(
            f'{prefix}.watch.enabled', self.code_fragments.watch_enabled)
        
        # Status filter (comma-separated list)
        status_filter = prop_conf.get_list(f'{prefix}.status.filter')
        if status_filter:
            self.code_fragments.status_filter = status_filter
        
        self.code_fragments.reload_strategy = prop_conf.get(
            f'{prefix}.reload.strategy', self.code_fragments.reload_strategy)
        self.code_fragments.max_wait_seconds = prop_conf.get_int(
            f'{prefix}.max.wait.seconds', self.code_fragments.max_wait_seconds)
        
        # S3 source
        self.code_fragments.s3_enabled = prop_conf.get_bool(
            f'{prefix}.s3.enabled', self.code_fragments.s3_enabled)
        self.code_fragments.s3_bucket = prop_conf.get(
            f'{prefix}.s3.bucket', self.code_fragments.s3_bucket)
        self.code_fragments.s3_prefix = prop_conf.get(
            f'{prefix}.s3.prefix', self.code_fragments.s3_prefix)
        
        # Filesystem source
        self.code_fragments.filesystem_enabled = prop_conf.get_bool(
            f'{prefix}.filesystem.enabled', self.code_fragments.filesystem_enabled)
        filesystem_paths = prop_conf.get_list(f'{prefix}.filesystem.paths')
        if filesystem_paths:
            self.code_fragments.filesystem_paths = filesystem_paths
    
    @classmethod
    def load(cls, config_path: str = None) -> "Settings":
        """
        Load settings - attempts to use PropertiesConfigurator if available.
        
        This is a convenience method that works with or without PropertiesConfigurator.
        For full functionality, use load_from_properties() with an initialized
        PropertiesConfigurator instance.
        
        Args:
            config_path: Optional path (ignored, kept for backward compatibility)
            
        Returns:
            Settings instance
        """
        settings = cls()
        
        # Try to get PropertiesConfigurator singleton if already initialized
        try:
            from abhikarta.core.config import PropertiesConfigurator
            # PropertiesConfigurator is a singleton, so if it's initialized,
            # we can get it without arguments
            prop_conf = PropertiesConfigurator.__new__(PropertiesConfigurator)
            if hasattr(prop_conf, '_initialized') and prop_conf._initialized:
                return cls.load_from_properties(prop_conf)
        except Exception:
            pass
        
        # Fall back to environment variables only
        settings._load_from_env()
        settings._ensure_directories()
        
        logger.warning("PropertiesConfigurator not available, using environment variables only")
        return settings
    
    def _load_from_env(self) -> None:
        """Load settings from environment variables (fallback)."""
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


def get_settings(prop_conf=None) -> Settings:
    """
    Get Settings instance.
    
    Args:
        prop_conf: Optional PropertiesConfigurator instance
        
    Returns:
        Settings instance
    """
    if prop_conf:
        return Settings.load_from_properties(prop_conf)
    return Settings.load()
