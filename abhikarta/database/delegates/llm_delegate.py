"""
LLM Delegate - Database operations for LLM Providers, Models, Permissions, Calls.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Version: 1.2.1
"""

from typing import Any, Dict, List, Optional
import uuid
import json
import logging

from ..database_delegate import DatabaseDelegate

logger = logging.getLogger(__name__)


class LLMDelegate(DatabaseDelegate):
    """
    Delegate for LLM-related database operations.
    
    Handles tables: llm_providers, llm_models, model_permissions, llm_calls
    """
    
    # =========================================================================
    # LLM PROVIDERS
    # =========================================================================
    
    def get_all_providers(self, active_only: bool = False) -> List[Dict]:
        """Get all LLM providers."""
        query = "SELECT * FROM llm_providers"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY name"
        return self.fetch_all(query) or []
    
    def get_provider(self, provider_id: str) -> Optional[Dict]:
        """Get provider by ID."""
        return self.fetch_one(
            "SELECT * FROM llm_providers WHERE provider_id = ?",
            (provider_id,)
        )
    
    def get_default_provider(self) -> Optional[Dict]:
        """Get the default provider."""
        return self.fetch_one(
            "SELECT * FROM llm_providers WHERE is_default = 1 AND is_active = 1"
        )
    
    def create_provider(self, provider_id: str, name: str, provider_type: str,
                        description: str = None, api_endpoint: str = None,
                        api_key_name: str = None, is_active: int = 1,
                        is_default: int = 0, config: str = '{}',
                        rate_limit_rpm: int = 60, rate_limit_tpm: int = 100000,
                        created_by: str = None) -> bool:
        """Create a new LLM provider."""
        try:
            self.execute(
                """INSERT INTO llm_providers 
                   (provider_id, name, description, provider_type, api_endpoint,
                    api_key_name, is_active, is_default, config, rate_limit_rpm,
                    rate_limit_tpm, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (provider_id, name, description, provider_type, api_endpoint,
                 api_key_name, is_active, is_default, config, rate_limit_rpm,
                 rate_limit_tpm, created_by)
            )
            return True
        except Exception as e:
            logger.error(f"Error creating provider: {e}")
            return False
    
    def update_provider(self, provider_id: str, **kwargs) -> bool:
        """Update provider fields."""
        if not kwargs:
            return False
        
        valid_fields = ['name', 'description', 'provider_type', 'api_endpoint',
                        'api_key_name', 'is_active', 'is_default', 'config',
                        'rate_limit_rpm', 'rate_limit_tpm']
        
        updates = []
        params = []
        for key, value in kwargs.items():
            if key in valid_fields:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if not updates:
            return False
        
        params.append(provider_id)
        query = f"UPDATE llm_providers SET {', '.join(updates)} WHERE provider_id = ?"
        
        try:
            self.execute(query, tuple(params))
            return True
        except Exception as e:
            logger.error(f"Error updating provider: {e}")
            return False
    
    def set_default_provider(self, provider_id: str) -> bool:
        """Set a provider as default (clears other defaults)."""
        try:
            self.execute("UPDATE llm_providers SET is_default = 0")
            self.execute(
                "UPDATE llm_providers SET is_default = 1 WHERE provider_id = ?",
                (provider_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error setting default provider: {e}")
            return False
    
    def delete_provider(self, provider_id: str) -> bool:
        """Delete a provider."""
        try:
            self.execute(
                "DELETE FROM llm_providers WHERE provider_id = ?",
                (provider_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting provider: {e}")
            return False
    
    def provider_exists(self, provider_id: str) -> bool:
        """Check if provider exists."""
        return self.exists("llm_providers", "provider_id = ?", (provider_id,))
    
    # =========================================================================
    # LLM MODELS
    # =========================================================================
    
    def get_all_models(self, active_only: bool = False, 
                       provider_id: str = None) -> List[Dict]:
        """Get all LLM models, optionally filtered by provider."""
        query = """SELECT m.*, p.name as provider_name 
                   FROM llm_models m
                   LEFT JOIN llm_providers p ON m.provider_id = p.provider_id"""
        
        conditions = []
        params = []
        
        if active_only:
            conditions.append("m.is_active = 1")
        if provider_id:
            conditions.append("m.provider_id = ?")
            params.append(provider_id)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY p.name, m.name"
        return self.fetch_all(query, tuple(params) if params else None) or []
    
    def get_model(self, model_id: str) -> Optional[Dict]:
        """Get model by ID with provider info."""
        return self.fetch_one(
            """SELECT m.*, p.name as provider_name 
               FROM llm_models m
               LEFT JOIN llm_providers p ON m.provider_id = p.provider_id
               WHERE m.model_id = ?""",
            (model_id,)
        )
    
    def get_default_model(self) -> Optional[Dict]:
        """Get the default model."""
        return self.fetch_one(
            """SELECT m.*, p.name as provider_name 
               FROM llm_models m
               LEFT JOIN llm_providers p ON m.provider_id = p.provider_id
               WHERE m.is_default = 1 AND m.is_active = 1"""
        )
    
    def get_provider_models(self, provider_id: str, 
                            active_only: bool = True) -> List[Dict]:
        """Get all models for a specific provider."""
        query = "SELECT * FROM llm_models WHERE provider_id = ?"
        if active_only:
            query += " AND is_active = 1"
        query += " ORDER BY name"
        return self.fetch_all(query, (provider_id,)) or []
    
    def create_model(self, model_id: str, provider_id: str, name: str,
                     display_name: str = None, description: str = None,
                     model_type: str = 'chat', context_window: int = 4096,
                     max_output_tokens: int = 4096, input_cost_per_1k: float = 0.0,
                     output_cost_per_1k: float = 0.0, supports_vision: int = 0,
                     supports_functions: int = 0, supports_streaming: int = 1,
                     is_active: int = 1, is_default: int = 0,
                     config: str = '{}') -> bool:
        """Create a new LLM model."""
        try:
            self.execute(
                """INSERT INTO llm_models 
                   (model_id, provider_id, name, display_name, description,
                    model_type, context_window, max_output_tokens, input_cost_per_1k,
                    output_cost_per_1k, supports_vision, supports_functions,
                    supports_streaming, is_active, is_default, config)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (model_id, provider_id, name, display_name, description,
                 model_type, context_window, max_output_tokens, input_cost_per_1k,
                 output_cost_per_1k, supports_vision, supports_functions,
                 supports_streaming, is_active, is_default, config)
            )
            return True
        except Exception as e:
            logger.error(f"Error creating model: {e}")
            return False
    
    def update_model(self, model_id: str, **kwargs) -> bool:
        """Update model fields."""
        if not kwargs:
            return False
        
        valid_fields = ['provider_id', 'name', 'display_name', 'description',
                        'model_type', 'context_window', 'max_output_tokens',
                        'input_cost_per_1k', 'output_cost_per_1k', 'supports_vision',
                        'supports_functions', 'supports_streaming', 'is_active',
                        'is_default', 'config']
        
        updates = []
        params = []
        for key, value in kwargs.items():
            if key in valid_fields:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if not updates:
            return False
        
        params.append(model_id)
        query = f"UPDATE llm_models SET {', '.join(updates)} WHERE model_id = ?"
        
        try:
            self.execute(query, tuple(params))
            return True
        except Exception as e:
            logger.error(f"Error updating model: {e}")
            return False
    
    def set_default_model(self, model_id: str) -> bool:
        """Set a model as default (clears other defaults)."""
        try:
            self.execute("UPDATE llm_models SET is_default = 0")
            self.execute(
                "UPDATE llm_models SET is_default = 1 WHERE model_id = ?",
                (model_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error setting default model: {e}")
            return False
    
    def delete_model(self, model_id: str) -> bool:
        """Delete a model."""
        try:
            self.execute("DELETE FROM llm_models WHERE model_id = ?", (model_id,))
            return True
        except Exception as e:
            logger.error(f"Error deleting model: {e}")
            return False
    
    def model_exists(self, model_id: str) -> bool:
        """Check if model exists."""
        return self.exists("llm_models", "model_id = ?", (model_id,))
    
    # =========================================================================
    # MODEL PERMISSIONS
    # =========================================================================
    
    def get_model_permissions(self, model_id: str) -> List[Dict]:
        """Get all permissions for a model."""
        return self.fetch_all(
            """SELECT mp.*, r.display_name as role_display_name
               FROM model_permissions mp
               LEFT JOIN roles r ON mp.role_name = r.role_name
               WHERE mp.model_id = ?""",
            (model_id,)
        ) or []
    
    def get_role_permissions(self, role_name: str) -> List[Dict]:
        """Get all model permissions for a role."""
        return self.fetch_all(
            """SELECT mp.*, m.display_name as model_display_name
               FROM model_permissions mp
               LEFT JOIN llm_models m ON mp.model_id = m.model_id
               WHERE mp.role_name = ?""",
            (role_name,)
        ) or []
    
    def can_use_model(self, role_name: str, model_id: str) -> bool:
        """Check if a role can use a specific model."""
        result = self.fetch_one(
            """SELECT can_use FROM model_permissions 
               WHERE model_id = ? AND role_name = ?""",
            (model_id, role_name)
        )
        return result.get('can_use', 0) == 1 if result else False
    
    def set_model_permission(self, model_id: str, role_name: str,
                             can_use: int = 1, daily_limit: int = -1,
                             monthly_limit: int = -1, created_by: str = None) -> bool:
        """Set or update model permission for a role."""
        try:
            # Try to update first
            self.execute(
                """INSERT OR REPLACE INTO model_permissions 
                   (model_id, role_name, can_use, daily_limit, monthly_limit, created_by)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (model_id, role_name, can_use, daily_limit, monthly_limit, created_by)
            )
            return True
        except Exception as e:
            logger.error(f"Error setting model permission: {e}")
            return False
    
    def delete_model_permission(self, model_id: str, role_name: str) -> bool:
        """Delete a model permission."""
        try:
            self.execute(
                "DELETE FROM model_permissions WHERE model_id = ? AND role_name = ?",
                (model_id, role_name)
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting model permission: {e}")
            return False
    
    def delete_all_model_permissions(self, model_id: str) -> bool:
        """Delete all permissions for a model."""
        try:
            self.execute(
                "DELETE FROM model_permissions WHERE model_id = ?",
                (model_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting model permissions: {e}")
            return False
    
    # =========================================================================
    # LLM CALLS
    # =========================================================================
    
    def log_llm_call(self, user_id: str, provider: str, model: str,
                     execution_id: str = None, agent_id: str = None,
                     request_type: str = 'completion', system_prompt: str = None,
                     user_prompt: str = None, messages: str = None,
                     response_content: str = None, tool_calls: str = None,
                     input_tokens: int = 0, output_tokens: int = 0,
                     cost_estimate: float = 0.0, temperature: float = None,
                     max_tokens: int = None, latency_ms: int = None,
                     status: str = 'success', error_message: str = None,
                     metadata: str = '{}') -> Optional[str]:
        """Log an LLM API call and return call_id."""
        call_id = str(uuid.uuid4())
        total_tokens = input_tokens + output_tokens
        
        try:
            self.execute(
                """INSERT INTO llm_calls 
                   (call_id, execution_id, agent_id, user_id, provider, model,
                    request_type, system_prompt, user_prompt, messages,
                    response_content, tool_calls, input_tokens, output_tokens,
                    total_tokens, cost_estimate, temperature, max_tokens,
                    latency_ms, status, error_message, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (call_id, execution_id, agent_id, user_id, provider, model,
                 request_type, system_prompt, user_prompt, messages,
                 response_content, tool_calls, input_tokens, output_tokens,
                 total_tokens, cost_estimate, temperature, max_tokens,
                 latency_ms, status, error_message, metadata)
            )
            return call_id
        except Exception as e:
            logger.error(f"Error logging LLM call: {e}")
            return None
    
    def get_llm_call(self, call_id: str) -> Optional[Dict]:
        """Get LLM call by ID."""
        return self.fetch_one(
            "SELECT * FROM llm_calls WHERE call_id = ?",
            (call_id,)
        )
    
    def get_llm_calls(self, user_id: str = None, agent_id: str = None,
                      execution_id: str = None, provider: str = None,
                      limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get LLM calls with optional filters."""
        query = "SELECT * FROM llm_calls"
        conditions = []
        params = []
        
        if user_id:
            conditions.append("user_id = ?")
            params.append(user_id)
        if agent_id:
            conditions.append("agent_id = ?")
            params.append(agent_id)
        if execution_id:
            conditions.append("execution_id = ?")
            params.append(execution_id)
        if provider:
            conditions.append("provider = ?")
            params.append(provider)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += f" ORDER BY created_at DESC LIMIT {limit} OFFSET {offset}"
        return self.fetch_all(query, tuple(params) if params else None) or []
    
    def get_llm_calls_count(self, user_id: str = None, agent_id: str = None,
                            execution_id: str = None) -> int:
        """Get count of LLM calls."""
        conditions = []
        params = []
        
        if user_id:
            conditions.append("user_id = ?")
            params.append(user_id)
        if agent_id:
            conditions.append("agent_id = ?")
            params.append(agent_id)
        if execution_id:
            conditions.append("execution_id = ?")
            params.append(execution_id)
        
        where = " AND ".join(conditions) if conditions else None
        return self.get_count("llm_calls", where, tuple(params) if params else None)
    
    def get_llm_usage_stats(self, user_id: str = None, 
                            days: int = 30) -> Dict[str, Any]:
        """Get LLM usage statistics."""
        query = """SELECT 
                       COUNT(*) as total_calls,
                       SUM(input_tokens) as total_input_tokens,
                       SUM(output_tokens) as total_output_tokens,
                       SUM(total_tokens) as total_tokens,
                       SUM(cost_estimate) as total_cost,
                       AVG(latency_ms) as avg_latency
                   FROM llm_calls
                   WHERE created_at >= datetime('now', ?)"""
        
        params = [f'-{days} days']
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        result = self.fetch_one(query, tuple(params))
        return result or {}
    
    def get_usage_by_provider(self, days: int = 30) -> List[Dict]:
        """Get LLM usage grouped by provider."""
        return self.fetch_all(
            """SELECT provider, 
                      COUNT(*) as call_count,
                      SUM(total_tokens) as total_tokens,
                      SUM(cost_estimate) as total_cost
               FROM llm_calls
               WHERE created_at >= datetime('now', ?)
               GROUP BY provider
               ORDER BY call_count DESC""",
            (f'-{days} days',)
        ) or []
    
    def get_usage_by_model(self, days: int = 30) -> List[Dict]:
        """Get LLM usage grouped by model."""
        return self.fetch_all(
            """SELECT model, provider,
                      COUNT(*) as call_count,
                      SUM(total_tokens) as total_tokens,
                      SUM(cost_estimate) as total_cost
               FROM llm_calls
               WHERE created_at >= datetime('now', ?)
               GROUP BY model, provider
               ORDER BY call_count DESC""",
            (f'-{days} days',)
        ) or []
