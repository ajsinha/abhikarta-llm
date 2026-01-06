"""
LLM Configuration Resolver Service

Provides consistent LLM configuration across the application by:
1. Loading admin-configured defaults from the database
2. Merging user overrides with admin defaults
3. Ensuring execution always has valid LLM configuration

The resolution priority is:
1. User-provided values (highest priority)
2. Admin-configured defaults (fallback)
3. System defaults (last resort)

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Version: 1.5.3
"""

import json
import logging
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# System defaults - used only when no admin config exists
SYSTEM_DEFAULTS = {
    'provider': 'ollama',
    'model': 'llama3.2:3b',
    'base_url': 'http://localhost:11434',
    'temperature': 0.7,
    'max_tokens': 2048,
    'top_p': 1.0,
    'frequency_penalty': 0.0,
    'presence_penalty': 0.0,
}


@dataclass
class LLMConfig:
    """Resolved LLM configuration with all required fields."""
    provider: str = 'ollama'
    provider_type: str = 'ollama'
    model: str = 'llama3.2:3b'
    base_url: str = ''
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    api_key: Optional[str] = None
    system_prompt: Optional[str] = None
    
    # Track which values came from admin defaults
    _admin_defaults_applied: Dict[str, bool] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            'provider': self.provider,
            'provider_type': self.provider_type,
            'model': self.model,
            'base_url': self.base_url,
            'temperature': self.temperature,
        }
        if self.max_tokens:
            result['max_tokens'] = self.max_tokens
        if self.top_p != 1.0:
            result['top_p'] = self.top_p
        if self.system_prompt:
            result['system_prompt'] = self.system_prompt
        return result
    
    def to_node_config(self) -> Dict[str, Any]:
        """Convert to node config format for workflow/agent nodes."""
        return {
            'provider': self.provider_type or self.provider,
            'model': self.model,
            'base_url': self.base_url,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'system_prompt': self.system_prompt,
        }


class LLMConfigResolver:
    """
    Resolves LLM configuration by merging user overrides with admin defaults.
    
    Usage:
        resolver = LLMConfigResolver(db_facade)
        
        # Get admin defaults for a provider
        defaults = resolver.get_provider_defaults('ollama')
        
        # Resolve user config with admin defaults
        config = resolver.resolve({
            'provider': 'ollama',
            'model': 'llama3.2:3b',
            # base_url not provided - will use admin default
        })
    """
    
    def __init__(self, db_facade=None):
        """
        Initialize resolver with database facade.
        
        Args:
            db_facade: Database facade for accessing llm_providers table
        """
        self.db_facade = db_facade
        self._provider_cache: Dict[str, Dict] = {}
        self._default_provider_cache: Optional[Dict] = None
    
    def clear_cache(self):
        """Clear cached provider data."""
        self._provider_cache.clear()
        self._default_provider_cache = None
    
    def get_default_provider(self) -> Optional[Dict]:
        """Get the admin-configured default provider."""
        if self._default_provider_cache is not None:
            return self._default_provider_cache
        
        if not self.db_facade:
            return None
        
        try:
            # Try to get default provider
            provider = self.db_facade.llm.get_default_provider()
            
            if not provider:
                # Get first active provider
                providers = self.db_facade.llm.get_all_providers(active_only=True)
                if providers:
                    provider = providers[0]
            
            if provider:
                self._default_provider_cache = self._enrich_provider(provider)
                
            return self._default_provider_cache
            
        except Exception as e:
            logger.warning(f"Failed to get default provider: {e}")
            return None
    
    def get_provider(self, provider_id: str) -> Optional[Dict]:
        """Get provider configuration by ID."""
        if provider_id in self._provider_cache:
            return self._provider_cache[provider_id]
        
        if not self.db_facade:
            return None
        
        try:
            provider = self.db_facade.llm.get_provider(provider_id)
            if provider:
                enriched = self._enrich_provider(provider)
                self._provider_cache[provider_id] = enriched
                return enriched
            return None
        except Exception as e:
            logger.warning(f"Failed to get provider {provider_id}: {e}")
            return None
    
    def get_provider_by_type(self, provider_type: str) -> Optional[Dict]:
        """Get provider configuration by type (ollama, openai, etc.)."""
        if not self.db_facade:
            return None
        
        try:
            providers = self.db_facade.llm.get_all_providers(active_only=True)
            for p in providers:
                if p.get('provider_type', '').lower() == provider_type.lower():
                    return self._enrich_provider(p)
            return None
        except Exception as e:
            logger.warning(f"Failed to get provider by type {provider_type}: {e}")
            return None
    
    def _enrich_provider(self, provider: Dict) -> Dict:
        """Enrich provider with parsed config and default model."""
        result = dict(provider)
        
        # Parse config JSON
        config = provider.get('config', '{}')
        if isinstance(config, str):
            try:
                config = json.loads(config)
            except:
                config = {}
        result['parsed_config'] = config
        
        # Get default model for this provider
        try:
            provider_id = provider.get('provider_id')
            if provider_id and self.db_facade:
                models = self.db_facade.llm.get_provider_models(provider_id, active_only=True)
                if models:
                    # Find default model
                    for m in models:
                        if m.get('is_default'):
                            result['default_model'] = m.get('model_id')
                            break
                    if 'default_model' not in result and models:
                        result['default_model'] = models[0].get('model_id')
        except Exception as e:
            logger.debug(f"Failed to get default model: {e}")
        
        return result
    
    def get_provider_defaults(self, provider_id_or_type: str) -> Dict[str, Any]:
        """
        Get admin-configured defaults for a specific provider.
        
        Args:
            provider_id_or_type: Provider ID or type (ollama, openai, etc.)
            
        Returns:
            Dictionary with default values for this provider
        """
        # Try by ID first, then by type
        provider = self.get_provider(provider_id_or_type)
        if not provider:
            provider = self.get_provider_by_type(provider_id_or_type)
        
        if not provider:
            # Return system defaults for unknown provider
            return dict(SYSTEM_DEFAULTS)
        
        parsed_config = provider.get('parsed_config', {})
        
        return {
            'provider': provider.get('provider_type', provider_id_or_type),
            'provider_id': provider.get('provider_id'),
            'model': provider.get('default_model', SYSTEM_DEFAULTS['model']),
            'base_url': provider.get('api_endpoint', '') or SYSTEM_DEFAULTS['base_url'],
            'temperature': parsed_config.get('temperature', SYSTEM_DEFAULTS['temperature']),
            'max_tokens': parsed_config.get('max_tokens', SYSTEM_DEFAULTS['max_tokens']),
            'top_p': parsed_config.get('top_p', SYSTEM_DEFAULTS['top_p']),
            'frequency_penalty': parsed_config.get('frequency_penalty', SYSTEM_DEFAULTS['frequency_penalty']),
            'presence_penalty': parsed_config.get('presence_penalty', SYSTEM_DEFAULTS['presence_penalty']),
        }
    
    def get_admin_defaults(self) -> Dict[str, Any]:
        """
        Get admin-configured defaults from the default provider.
        
        Returns:
            Dictionary with all default LLM configuration values
        """
        default_provider = self.get_default_provider()
        
        if not default_provider:
            logger.info("No admin-configured provider found, using system defaults")
            return dict(SYSTEM_DEFAULTS)
        
        parsed_config = default_provider.get('parsed_config', {})
        
        return {
            'provider': default_provider.get('provider_type', SYSTEM_DEFAULTS['provider']),
            'provider_id': default_provider.get('provider_id'),
            'model': default_provider.get('default_model', SYSTEM_DEFAULTS['model']),
            'base_url': default_provider.get('api_endpoint', '') or SYSTEM_DEFAULTS['base_url'],
            'temperature': parsed_config.get('temperature', SYSTEM_DEFAULTS['temperature']),
            'max_tokens': parsed_config.get('max_tokens'),
            'top_p': parsed_config.get('top_p', SYSTEM_DEFAULTS['top_p']),
            'frequency_penalty': parsed_config.get('frequency_penalty', SYSTEM_DEFAULTS['frequency_penalty']),
            'presence_penalty': parsed_config.get('presence_penalty', SYSTEM_DEFAULTS['presence_penalty']),
        }
    
    def resolve(self, user_config: Dict[str, Any], 
                use_provider_defaults: bool = True) -> LLMConfig:
        """
        Resolve user configuration with admin defaults.
        
        User-provided values take priority. Missing or empty values
        are filled from admin defaults.
        
        Args:
            user_config: User-provided configuration (may have missing values)
            use_provider_defaults: If True, use provider-specific defaults when
                                   provider is specified but base_url is missing
            
        Returns:
            Fully resolved LLMConfig with all required fields
        """
        # Start with admin defaults
        admin_defaults = self.get_admin_defaults()
        
        # If user specified a provider, get provider-specific defaults
        user_provider = user_config.get('provider') or user_config.get('provider_type')
        if user_provider and use_provider_defaults:
            provider_defaults = self.get_provider_defaults(user_provider)
            # Merge provider defaults with admin defaults
            admin_defaults.update({k: v for k, v in provider_defaults.items() if v})
        
        # Track which values came from admin defaults
        admin_applied = {}
        
        def get_value(key: str, default_key: str = None):
            """Get value from user config or admin defaults."""
            user_val = user_config.get(key)
            
            # Check if user provided a meaningful value
            # Empty string, None, or 0 for numeric fields means "use default"
            if user_val is not None and user_val != '':
                admin_applied[key] = False
                return user_val
            
            # Use admin default
            admin_applied[key] = True
            return admin_defaults.get(default_key or key, SYSTEM_DEFAULTS.get(key))
        
        # Resolve each field
        provider = get_value('provider') or get_value('provider_type')
        provider_type = user_config.get('provider_type') or provider
        
        resolved = LLMConfig(
            provider=provider,
            provider_type=provider_type,
            model=get_value('model'),
            base_url=get_value('base_url') or '',
            temperature=float(get_value('temperature') or SYSTEM_DEFAULTS['temperature']),
            max_tokens=get_value('max_tokens'),
            top_p=float(get_value('top_p') or SYSTEM_DEFAULTS['top_p']),
            frequency_penalty=float(get_value('frequency_penalty') or 0),
            presence_penalty=float(get_value('presence_penalty') or 0),
            api_key=user_config.get('api_key'),
            system_prompt=user_config.get('system_prompt'),
        )
        resolved._admin_defaults_applied = admin_applied
        
        logger.debug(f"Resolved LLM config: provider={resolved.provider}, model={resolved.model}, "
                    f"base_url={resolved.base_url}, temp={resolved.temperature}")
        
        return resolved
    
    def resolve_node_config(self, node_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve a workflow/agent node's LLM configuration.
        
        This is the main method to use at execution time.
        It takes a node's config and returns a fully resolved config
        with admin defaults applied for any missing values.
        
        Args:
            node_config: Node configuration dictionary
            
        Returns:
            Resolved configuration dictionary ready for LLM creation
        """
        resolved = self.resolve(node_config)
        return resolved.to_node_config()
    
    def apply_defaults_to_nodes(self, dag_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply admin defaults to all LLM nodes in a workflow/agent definition.
        
        This is used when creating entities from templates to pre-populate
        admin defaults while still allowing user overrides.
        
        Args:
            dag_definition: Workflow or agent DAG definition
            
        Returns:
            Updated definition with admin defaults applied to LLM nodes
        """
        import copy
        result = copy.deepcopy(dag_definition)
        admin_defaults = self.get_admin_defaults()
        
        nodes = result.get('nodes', [])
        for node in nodes:
            node_type = node.get('type', '').lower()
            if node_type == 'llm':
                config = node.get('config', {})
                
                # Apply admin defaults for missing values
                if not config.get('provider') and not config.get('provider_type'):
                    config['provider'] = admin_defaults.get('provider', 'ollama')
                
                if not config.get('model'):
                    config['model'] = admin_defaults.get('model', 'llama3.2:3b')
                
                if not config.get('base_url'):
                    config['base_url'] = admin_defaults.get('base_url', '')
                
                if config.get('temperature') is None:
                    config['temperature'] = admin_defaults.get('temperature', 0.7)
                
                node['config'] = config
        
        # Also update top-level llm_config if present
        if 'llm_config' in result:
            llm_config = result['llm_config']
            if not llm_config.get('provider'):
                llm_config['provider'] = admin_defaults.get('provider', 'ollama')
            if not llm_config.get('model'):
                llm_config['model'] = admin_defaults.get('model', 'llama3.2:3b')
            if not llm_config.get('base_url'):
                llm_config['base_url'] = admin_defaults.get('base_url', '')
        
        return result


# Global resolver instance (initialized on first use)
_global_resolver: Optional[LLMConfigResolver] = None


def get_llm_config_resolver(db_facade=None) -> LLMConfigResolver:
    """
    Get the global LLM config resolver instance.
    
    Args:
        db_facade: Database facade (required on first call)
        
    Returns:
        LLMConfigResolver instance
    """
    global _global_resolver
    
    if _global_resolver is None:
        _global_resolver = LLMConfigResolver(db_facade)
    elif db_facade and _global_resolver.db_facade is None:
        _global_resolver.db_facade = db_facade
    
    return _global_resolver


def init_llm_config_resolver(db_facade) -> LLMConfigResolver:
    """
    Initialize the global LLM config resolver.
    
    Should be called during application startup.
    
    Args:
        db_facade: Database facade
        
    Returns:
        Initialized LLMConfigResolver instance
    """
    global _global_resolver
    _global_resolver = LLMConfigResolver(db_facade)
    logger.info("LLM Config Resolver initialized")
    return _global_resolver


def resolve_llm_config(user_config: Dict[str, Any], db_facade=None) -> Dict[str, Any]:
    """
    Convenience function to resolve LLM config with admin defaults.
    
    Args:
        user_config: User-provided configuration
        db_facade: Optional database facade
        
    Returns:
        Resolved configuration dictionary
    """
    resolver = get_llm_config_resolver(db_facade)
    return resolver.resolve_node_config(user_config)
