"""
Abhikarta LLM Model Management Database Handler

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This module and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

Patent Pending: Certain architectural patterns and implementations described in this
module may be subject to patent applications.
"""
import logging
import json
import sqlite3
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager
from db_management.pool_manager import get_pool_manager

logger = logging.getLogger(__name__)

class ModelManagementDBHandler:
    """
    Singleton database handler for managing LLM model and provider data.
    
    This class provides a thread-safe interface to store and retrieve:
    - Provider configurations
    - Model specifications
    - Model capabilities
    - Cost information
    - Model strengths and metadata
    
    The handler uses SQLite as the backend database and maintains connection
    pooling for efficient concurrent access.
    
    Thread Safety:
        All public methods are thread-safe using RLock for reentrant locking.
    
    Usage:
        >>> handler = ModelManagementDBHandler.get_instance("/path/to/db_management.sqlite")
        >>> handler.initialize_schema()
        >>> handler.insert_provider_from_json("/path/to/provider.json")
        >>> models = handler.get_models_by_provider("anthropic")
    """
    
    _instance: Optional['ModelManagementDBHandler'] = None
    _instance_lock = threading.RLock()
    

    
    def __init__(self, db_connection_pool_name: str):
        """
        Initialize the database handler.
        
        Note: Use get_instance() instead of direct initialization to ensure singleton.
        
        Args:
            db_connection_pool_name: Name of database connection pool
        """
        self._db_connection_pool_name = db_connection_pool_name
        self._connection_pool_manager = get_pool_manager()
        self._lock = threading.RLock()
        self._local = threading.local()
        
    @classmethod
    def get_instance(cls, db_path: str = None) -> 'ModelManagementDBHandler':
        """
        Get the singleton instance of ModelManagementDBHandler.
        
        Args:
            db_path: Path to SQLite database (required on first call)
            
        Returns:
            The singleton ModelManagementDBHandler instance
            
        Raises:
            ValueError: If db_path is None on first call
        """
        with cls._instance_lock:
            if cls._instance is None:
                if db_path is None:
                    raise ValueError("db_path must be provided on first call to get_instance()")
                cls._instance = cls(db_path)
            return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (mainly for testing)."""
        with cls._instance_lock:
            if cls._instance is not None:
                cls._instance.close_all_connections()
                cls._instance = None

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections with auto-commit."""
        with self._connection_pool_manager.get_connection_context(self._db_connection_pool_name) as conn:
            try:
                yield conn  # Now this yields the actual connection
                conn.commit()  # Auto-commit on success
            except Exception as e:
                conn.rollback()  # Auto-rollback on error
                print(f"Database error: {e}")
                raise

    @contextmanager
    def _get_cursor(self, conn):
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    
    def close_all_connections(self) -> None:
        """Close all thread-local connections."""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
    
    def initialize_schema(self) -> None:
        """
        Initialize the database schema.
        
        Creates all tables, indexes, and constraints if they don't exist.
        This method is idempotent and safe to call multiple times.
        """
        pass
    
    def clear_all_data(self) -> None:
        """
        Clear all data from the database (keeping schema intact).
        
        Warning: This will delete all providers, models, and related data.
        """
        with self._lock:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("DELETE FROM model_performance")
                    cursor.execute("DELETE FROM model_costs")
                    cursor.execute("DELETE FROM model_capabilities")
                    cursor.execute("DELETE FROM model_strengths")
                    cursor.execute("DELETE FROM models")
                    cursor.execute("DELETE FROM providers")
    
    # ==================================================================================
    # PROVIDER OPERATIONS
    # ==================================================================================
    
    def insert_provider(
        self,
        provider: str,
        api_version: str,
        base_url: Optional[str] = None,
        notes: Optional[Dict[str, Any]] = None,
        enabled: bool = True
    ) -> int:
        """
        Insert a new provider into the database.
        
        Args:
            provider: Provider identifier
            api_version: API version
            base_url: Base URL for API
            notes: Additional notes (will be JSON serialized)
            enabled: Whether provider is enabled
            
        Returns:
            Provider ID
        """
        with self._lock:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    notes_json = json.dumps(notes) if notes else None
                    cursor.execute("""
                        INSERT INTO providers (provider, api_version, base_url, notes, enabled)
                        VALUES (?, ?, ?, ?, ?)
                    """, (provider, api_version, base_url, notes_json, enabled))
                    return cursor.lastrowid
    
    def update_provider(
        self,
        provider_name: str,
        api_version: Optional[str] = None,
        base_url: Optional[str] = None,
        notes: Optional[Dict[str, Any]] = None,
        enabled: Optional[bool] = None
    ) -> bool:
        """
        Update an existing provider.
        
        Args:
            provider_name: Provider identifier
            api_version: New API version (optional)
            base_url: New base URL (optional)
            notes: New notes (optional)
            enabled: New enabled status (optional)
            
        Returns:
            True if provider was updated, False if not found
        """
        with self._lock:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    updates = []
                    params = []

                    if api_version is not None:
                        updates.append("api_version = ?")
                        params.append(api_version)
                    if base_url is not None:
                        updates.append("base_url = ?")
                        params.append(base_url)
                    if notes is not None:
                        updates.append("notes = ?")
                        params.append(json.dumps(notes))
                    if enabled is not None:
                        updates.append("enabled = ?")
                        params.append(enabled)

                    if not updates:
                        return False

                    updates.append("updated_at = CURRENT_TIMESTAMP")
                    params.append(provider_name)

                    sql = f"UPDATE providers SET {', '.join(updates)} WHERE provider = ?"
                    cursor.execute(sql, params)
                    return cursor.rowcount > 0
    
    def get_provider_by_name(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """
        Get provider by name.
        
        Args:
            provider_name: Provider identifier
            
        Returns:
            Provider dictionary or None if not found
        """
        with self._lock:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        SELECT * FROM providers WHERE provider = ?
                    """, (provider_name,))
                    row = cursor.fetchone()
                    if row:
                        return self._row_to_dict(row)
                    return None
    
    def get_all_providers(self, include_disabled: bool = False) -> List[Dict[str, Any]]:
        """
        Get all providers.
        
        Args:
            include_disabled: Whether to include disabled providers
            
        Returns:
            List of provider dictionaries
        """
        with self._lock:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    if include_disabled:
                        cursor.execute("SELECT * FROM providers ORDER BY provider")
                    else:
                        cursor.execute("SELECT * FROM providers WHERE enabled = 1 ORDER BY provider")
                    return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def delete_provider(self, provider_name: str) -> bool:
        """
        Delete a provider and all its models.
        
        Args:
            provider_name: Provider identifier
            
        Returns:
            True if provider was deleted, False if not found
        """
        with self._lock:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("DELETE FROM providers WHERE provider = ?", (provider_name,))
                    return cursor.rowcount > 0
    
    # ==================================================================================
    # MODEL OPERATIONS
    # ==================================================================================
    
    def insert_model(
        self,
        provider_name: str,
        name: str,
        version: str,
        description: str,
        context_window: int,
        max_output: int,
        model_id: Optional[str] = None,
        replicate_model: Optional[str] = None,
        parameters: Optional[str] = None,
        license: Optional[str] = None,
        enabled: bool = True
    ) -> int:
        """
        Insert a new model into the database.
        
        Args:
            provider_name: Provider identifier
            name: Model name
            version: Model version
            description: Model description
            context_window: Context window size
            max_output: Maximum output tokens
            model_id: Model ID (optional)
            replicate_model: Replicate model identifier (optional)
            parameters: Model parameters (optional)
            license: License information (optional)
            enabled: Whether model is enabled
            
        Returns:
            Model ID
            
        Raises:
            ValueError: If provider not found
        """
        with self._lock:
            provider = self.get_provider_by_name(provider_name)
            if not provider:
                raise ValueError(f"Provider '{provider_name}' not found")

            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        INSERT INTO models (
                            provider_id, name, version, description, model_id, replicate_model,
                            context_window, max_output, parameters, license, enabled
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        provider['id'], name, version, description, model_id, replicate_model,
                        context_window, max_output, parameters, license, enabled
                    ))
                    return cursor.lastrowid
    
    def update_model(
        self,
        provider_name: str,
        model_name: str,
        **kwargs
    ) -> bool:
        """
        Update an existing model.
        
        Args:
            provider_name: Provider identifier
            model_name: Model name
            **kwargs: Fields to update
            
        Returns:
            True if model was updated, False if not found
        """
        with self._lock:
            provider = self.get_provider_by_name(provider_name)
            if not provider:
                return False

            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    updates = []
                    params = []

                    for key, value in kwargs.items():
                        if key in ['version', 'description', 'model_id', 'replicate_model',
                                   'context_window', 'max_output', 'parameters', 'license', 'enabled']:
                            updates.append(f"{key} = ?")
                            params.append(value)

                    if not updates:
                        return False

                    updates.append("updated_at = CURRENT_TIMESTAMP")
                    params.extend([provider['id'], model_name])

                    sql = f"UPDATE models SET {', '.join(updates)} WHERE provider_id = ? AND name = ?"
                    cursor.execute(sql, params)
                    return cursor.rowcount > 0
    
    def get_model_by_name(
        self,
        provider_name: str,
        model_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific model by provider and name.
        
        Args:
            provider_name: Provider identifier
            model_name: Model name
            
        Returns:
            Model dictionary with all related data or None if not found
        """
        with self._lock:
            provider = self.get_provider_by_name(provider_name)
            if not provider:
                return None

            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        SELECT * FROM models 
                        WHERE provider_id = ? AND name = ?
                    """, (provider['id'], model_name))
                    row = cursor.fetchone()
                    if not row:
                        return None

                    model = self._row_to_dict(row)
                    model['provider'] = provider_name

                    # Get strengths
                    model['strengths'] = self._get_model_strengths(model['id'])

                    # Get capabilities
                    model['capabilities'] = self._get_model_capabilities(model['id'])

                    # Get cost
                    model['cost'] = self._get_model_cost(model['id'])

                    # Get performance
                    model['performance'] = self._get_model_performance(model['id'])

                    return model
    
    def get_models_by_provider(
        self,
        provider_name: str,
        include_disabled: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all models for a specific provider.
        
        Args:
            provider_name: Provider identifier
            include_disabled: Whether to include disabled models
            
        Returns:
            List of model dictionaries
        """
        with self._lock:
            provider = self.get_provider_by_name(provider_name)
            if not provider:
                return []

            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    if include_disabled:
                        cursor.execute("""
                            SELECT * FROM models WHERE provider_id = ? ORDER BY name
                        """, (provider['id'],))
                    else:
                        cursor.execute("""
                            SELECT * FROM models WHERE provider_id = ? AND enabled = 1 ORDER BY name
                        """, (provider['id'],))

                    models = []
                    for row in cursor.fetchall():
                        model = self._row_to_dict(row)
                        model['provider'] = provider_name
                        model['strengths'] = self._get_model_strengths(model['id'])
                        model['capabilities'] = self._get_model_capabilities(model['id'])
                        model['cost'] = self._get_model_cost(model['id'])
                        model['performance'] = self._get_model_performance(model['id'])
                        models.append(model)

                    return models
    
    def get_all_models(self, include_disabled: bool = False) -> List[Dict[str, Any]]:
        """
        Get all models from all providers.
        
        Args:
            include_disabled: Whether to include disabled models
            
        Returns:
            List of model dictionaries
        """
        with self._lock:
            models = []
            providers = self.get_all_providers(include_disabled=True)
            
            for provider in providers:
                if not include_disabled and not provider['enabled']:
                    continue
                provider_models = self.get_models_by_provider(
                    provider['provider'],
                    include_disabled
                )
                models.extend(provider_models)
            
            return models
    
    def delete_model(self, provider_name: str, model_name: str) -> bool:
        """
        Delete a model.
        
        Args:
            provider_name: Provider identifier
            model_name: Model name
            
        Returns:
            True if model was deleted, False if not found
        """
        with self._lock:
            provider = self.get_provider_by_name(provider_name)
            if not provider:
                return False

            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        DELETE FROM models WHERE provider_id = ? AND name = ?
                    """, (provider['id'], model_name))
                    return cursor.rowcount > 0
    
    # ==================================================================================
    # MODEL STRENGTHS OPERATIONS
    # ==================================================================================
    
    def insert_model_strengths(self, model_id: int, strengths: List[str]) -> None:
        """
        Insert strengths for a model.
        
        Args:
            model_id: Model ID
            strengths: List of strength strings
        """
        with self._lock:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    for strength in strengths:
                        cursor.execute("""
                            INSERT OR IGNORE INTO model_strengths (model_id, strength)
                            VALUES (?, ?)
                        """, (model_id, strength))
    
    def _get_model_strengths(self, model_id: int) -> List[str]:
        """Get all strengths for a model."""
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cursor:
                cursor.execute("""
                    SELECT strength FROM model_strengths WHERE model_id = ?
                """, (model_id,))
                return [row['strength'] for row in cursor.fetchall()]
    
    # ==================================================================================
    # MODEL CAPABILITIES OPERATIONS
    # ==================================================================================
    
    def insert_model_capabilities(
        self,
        model_id: int,
        capabilities: Dict[str, Any]
    ) -> None:
        """
        Insert capabilities for a model.
        
        Args:
            model_id: Model ID
            capabilities: Dictionary of capabilities
        """
        with self._lock:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    for key, value in capabilities.items():
                        value_str = json.dumps(value) if not isinstance(value, (str, int, float, bool)) else str(value)
                        cursor.execute("""
                            INSERT OR REPLACE INTO model_capabilities (model_id, capability_name, capability_value)
                            VALUES (?, ?, ?)
                        """, (model_id, key, value_str))
    
    def _get_model_capabilities(self, model_id: int) -> Dict[str, Any]:
        """Get all capabilities for a model."""
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cursor:
                cursor.execute("""
                    SELECT capability_name, capability_value FROM model_capabilities WHERE model_id = ?
                """, (model_id,))
                capabilities = {}
                for row in cursor.fetchall():
                    name = row['capability_name']
                    value = row['capability_value']
                    # Try to parse as JSON, fallback to string
                    try:
                        capabilities[name] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        # Try to parse as boolean
                        if value.lower() in ('true', '1'):
                            capabilities[name] = True
                        elif value.lower() in ('false', '0'):
                            capabilities[name] = False
                        else:
                            capabilities[name] = value
                return capabilities
    
    def get_models_by_capability(
        self,
        capability_name: str,
        capability_value: Any = True
    ) -> List[Dict[str, Any]]:
        """
        Get all models that have a specific capability.
        
        Args:
            capability_name: Capability name (e.g., 'vision', 'function_calling')
            capability_value: Expected capability value (default: True)
            
        Returns:
            List of model dictionaries
        """
        with self._lock:
            value_str = json.dumps(capability_value) if not isinstance(capability_value, (str, int, float, bool)) else str(capability_value)

            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        SELECT DISTINCT m.* 
                        FROM models m
                        INNER JOIN model_capabilities mc ON m.id = mc.model_id
                        WHERE mc.capability_name = ? AND mc.capability_value = ? AND m.enabled = 1
                    """, (capability_name, value_str))

                    models = []
                    for row in cursor.fetchall():
                        model = self._row_to_dict(row)
                        # Get provider name
                        cursor.execute("SELECT provider FROM providers WHERE id = ?", (model['provider_id'],))
                        provider_row = cursor.fetchone()
                        model['provider'] = provider_row['provider'] if provider_row else None
                        model['strengths'] = self._get_model_strengths(model['id'])
                        model['capabilities'] = self._get_model_capabilities(model['id'])
                        model['cost'] = self._get_model_cost(model['id'])
                        model['performance'] = self._get_model_performance(model['id'])
                        models.append(model)

                    return models
    
    # ==================================================================================
    # MODEL COST OPERATIONS
    # ==================================================================================
    
    def insert_model_cost(self, model_id: int, cost: Dict[str, Any]) -> None:
        """
        Insert cost information for a model.
        
        Args:
            model_id: Model ID
            cost: Cost dictionary
        """
        with self._lock:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        INSERT OR REPLACE INTO model_costs (
                            model_id, input_per_1k, output_per_1k,
                            input_per_1m, output_per_1m,
                            input_per_1m_0_128k, input_per_1m_128k_plus,
                            cost_json
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        model_id,
                        cost.get('input_per_1k'),
                        cost.get('output_per_1k'),
                        cost.get('input_per_1m'),
                        cost.get('output_per_1m'),
                        cost.get('input_per_1m_0_128k'),
                        cost.get('input_per_1m_128k_plus'),
                        json.dumps(cost)
                    ))
    
    def _get_model_cost(self, model_id: int) -> Dict[str, Any]:
        """Get cost information for a model."""
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cursor:
                cursor.execute("""
                    SELECT cost_json FROM model_costs WHERE model_id = ?
                """, (model_id,))
                row = cursor.fetchone()
                if row and row['cost_json']:
                    return json.loads(row['cost_json'])
                return {}
    
    def get_cheapest_model_for_capability(
        self,
        capability_name: str,
        input_tokens: int = 100000,
        output_tokens: int = 1000
    ) -> Optional[Tuple[Dict[str, Any], float]]:
        """
        Find the cheapest model with a specific capability.
        
        Args:
            capability_name: Required capability
            input_tokens: Number of input tokens for cost calculation
            output_tokens: Number of output tokens for cost calculation
            
        Returns:
            Tuple of (model dict, cost) or None if no models found
        """
        models = self.get_models_by_capability(capability_name)
        if not models:
            return None
        
        cheapest = None
        lowest_cost = float('inf')
        
        for model in models:
            cost_info = model.get('cost', {})
            calculated_cost = self._calculate_cost(cost_info, input_tokens, output_tokens)
            if calculated_cost < lowest_cost:
                lowest_cost = calculated_cost
                cheapest = model
        
        return (cheapest, lowest_cost) if cheapest else None
    
    def get_cheapest_model_for_provider(
        self,
        provider_name: str,
        capability_name: Optional[str] = None,
        input_tokens: int = 100000,
        output_tokens: int = 1000
    ) -> Optional[Tuple[Dict[str, Any], float]]:
        """
        Find the cheapest model from a specific provider.
        
        Args:
            provider_name: Provider identifier
            capability_name: Optional capability requirement
            input_tokens: Number of input tokens for cost calculation
            output_tokens: Number of output tokens for cost calculation
            
        Returns:
            Tuple of (model dict, cost) or None if no models found
        """
        models = self.get_models_by_provider(provider_name)
        
        if capability_name:
            models = [m for m in models if m.get('capabilities', {}).get(capability_name) is True]
        
        if not models:
            return None
        
        cheapest = None
        lowest_cost = float('inf')
        
        for model in models:
            cost_info = model.get('cost', {})
            calculated_cost = self._calculate_cost(cost_info, input_tokens, output_tokens)
            if calculated_cost < lowest_cost:
                lowest_cost = calculated_cost
                cheapest = model
        
        return (cheapest, lowest_cost) if cheapest else None
    
    @staticmethod
    def _calculate_cost(cost: Dict[str, Any], input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for given tokens."""
        input_cost = 0.0
        output_cost = 0.0
        
        if 'input_per_1k' in cost:
            input_cost = (input_tokens / 1000) * cost['input_per_1k']
            output_cost = (output_tokens / 1000) * cost['output_per_1k']
        elif 'input_per_1m' in cost:
            input_cost = (input_tokens / 1_000_000) * cost['input_per_1m']
            output_cost = (output_tokens / 1_000_000) * cost['output_per_1m']
        elif 'input_per_1m_0_128k' in cost:
            if input_tokens <= 128_000:
                input_cost = (input_tokens / 1_000_000) * cost['input_per_1m_0_128k']
            else:
                first_tier = (128_000 / 1_000_000) * cost['input_per_1m_0_128k']
                second_tier = ((input_tokens - 128_000) / 1_000_000) * cost['input_per_1m_128k_plus']
                input_cost = first_tier + second_tier
            output_cost = (output_tokens / 1_000_000) * cost['output_per_1m']
        
        return input_cost + output_cost
    
    # ==================================================================================
    # MODEL PERFORMANCE OPERATIONS
    # ==================================================================================
    
    def insert_model_performance(self, model_id: int, performance: Dict[str, Any]) -> None:
        """
        Insert performance information for a model.
        
        Args:
            model_id: Model ID
            performance: Performance dictionary
        """
        with self._lock:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("""
                        INSERT OR REPLACE INTO model_performance (model_id, performance_json)
                        VALUES (?, ?)
                    """, (model_id, json.dumps(performance)))
    
    def _get_model_performance(self, model_id: int) -> Dict[str, Any]:
        """Get performance information for a model."""
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cursor:
                cursor.execute("""
                    SELECT performance_json FROM model_performance WHERE model_id = ?
                """, (model_id,))
                row = cursor.fetchone()
                if row and row['performance_json']:
                    return json.loads(row['performance_json'])
                return {}
    
    # ==================================================================================
    # BULK OPERATIONS - JSON IMPORT
    # ==================================================================================
    
    def insert_provider_from_json(self, json_path: str) -> str:
        """
        Load a provider and all its models from a JSON file.
        
        Args:
            json_path: Path to the JSON configuration file
            
        Returns:
            Provider name
            
        Raises:
            FileNotFoundError: If JSON file not found
            ValueError: If JSON is invalid
        """
        with self._lock:
            path = Path(json_path)
            if not path.exists():
                raise FileNotFoundError(f"JSON file not found: {json_path}")
            
            with open(path, 'r') as f:
                config = json.load(f)
            
            # Insert or update provider
            provider_name = config['provider']
            existing = self.get_provider_by_name(provider_name)
            
            if existing:
                # Update existing provider
                self.update_provider(
                    provider_name,
                    api_version=config.get('api_version'),
                    base_url=config.get('base_url'),
                    notes=config.get('notes'),
                    enabled=True
                )
                provider_id = existing['id']
            else:
                # Insert new provider
                provider_id = self.insert_provider(
                    provider=provider_name,
                    api_version=config.get('api_version', 'v1'),
                    base_url=config.get('base_url'),
                    notes=config.get('notes'),
                    enabled=True
                )
            
            # Insert or update models
            for model_config in config.get('models', []):
                model_name = model_config['name']
                existing_model = self.get_model_by_name(provider_name, model_name)
                
                if existing_model:
                    # Update existing model
                    model_id = existing_model['id']
                    self.update_model(
                        provider_name,
                        model_name,
                        version=model_config.get('version'),
                        description=model_config.get('description'),
                        model_id=model_config.get('model_id'),
                        replicate_model=model_config.get('replicate_model'),
                        context_window=model_config.get('context_window'),
                        max_output=model_config.get('max_output'),
                        parameters=model_config.get('parameters'),
                        license=model_config.get('license'),
                        enabled=True
                    )
                else:
                    # Insert new model
                    model_id = self.insert_model(
                        provider_name=provider_name,
                        name=model_name,
                        version=model_config.get('version', '1.0'),
                        description=model_config.get('description', ''),
                        context_window=model_config.get('context_window', 4096),
                        max_output=model_config.get('max_output', 2048),
                        model_id=model_config.get('model_id'),
                        replicate_model=model_config.get('replicate_model'),
                        parameters=model_config.get('parameters'),
                        license=model_config.get('license'),
                        enabled=True
                    )
                
                # Insert strengths
                if 'strengths' in model_config:
                    self.insert_model_strengths(model_id, model_config['strengths'])
                
                # Insert capabilities
                if 'capabilities' in model_config:
                    self.insert_model_capabilities(model_id, model_config['capabilities'])
                
                # Insert cost
                if 'cost' in model_config:
                    self.insert_model_cost(model_id, model_config['cost'])
                
                # Insert performance
                if 'performance' in model_config:
                    self.insert_model_performance(model_id, model_config['performance'])
            
            return provider_name
    
    def load_all_json_files(self, json_directory: str) -> List[str]:
        """
        Load all JSON files from a directory.
        
        Args:
            json_directory: Directory containing JSON files
            
        Returns:
            List of loaded provider names
        """
        with self._lock:
            directory = Path(json_directory)
            if not directory.exists():
                raise FileNotFoundError(f"Directory not found: {json_directory}")
            
            loaded_providers = []
            for json_file in directory.glob("*.json"):
                try:
                    provider_name = self.insert_provider_from_json(str(json_file))
                    loaded_providers.append(provider_name)
                    print(f"Loaded provider: {provider_name} from {json_file.name}")
                except Exception as e:
                    print(f"Error loading {json_file.name}: {e}")
            
            return loaded_providers
    
    # ==================================================================================
    # UTILITY METHODS
    # ==================================================================================
    
    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        """Convert SQLite Row to dictionary."""
        return {key: row[key] for key in row.keys()}
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self._lock:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute("SELECT COUNT(*) as count FROM providers WHERE enabled = 1")
                    provider_count = cursor.fetchone()['count']

                    cursor.execute("SELECT COUNT(*) as count FROM providers")
                    total_provider_count = cursor.fetchone()['count']

                    cursor.execute("SELECT COUNT(*) as count FROM models WHERE enabled = 1")
                    model_count = cursor.fetchone()['count']

                    cursor.execute("SELECT COUNT(*) as count FROM models")
                    total_model_count = cursor.fetchone()['count']

                    return {
                        'enabled_providers': provider_count,
                        'total_providers': total_provider_count,
                        'enabled_models': model_count,
                        'total_models': total_model_count,
                        'db_connection_pool_name': self._db_connection_pool_name
                    }


__all__ = ['ModelManagementDBHandler']
