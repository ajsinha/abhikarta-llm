"""
LLM Logger - Service for logging all LLM calls to the database.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class LLMCallRecord:
    """Record of an LLM call."""
    call_id: str
    user_id: str
    provider: str
    model: str
    request_type: str = 'completion'
    execution_id: Optional[str] = None
    agent_id: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None
    messages: Optional[List[Dict]] = None
    response_content: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_estimate: float = 0.0
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    latency_ms: int = 0
    status: str = 'success'
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'call_id': self.call_id,
            'user_id': self.user_id,
            'provider': self.provider,
            'model': self.model,
            'request_type': self.request_type,
            'execution_id': self.execution_id,
            'agent_id': self.agent_id,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'total_tokens': self.total_tokens,
            'cost_estimate': self.cost_estimate,
            'latency_ms': self.latency_ms,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# Cost estimates per 1M tokens (approximate)
COST_PER_MILLION_TOKENS = {
    'openai': {
        'gpt-4o': {'input': 2.50, 'output': 10.00},
        'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
        'gpt-4-turbo': {'input': 10.00, 'output': 30.00},
        'gpt-3.5-turbo': {'input': 0.50, 'output': 1.50},
    },
    'anthropic': {
        'claude-3-5-sonnet-20241022': {'input': 3.00, 'output': 15.00},
        'claude-3-opus-20240229': {'input': 15.00, 'output': 75.00},
        'claude-3-haiku-20240307': {'input': 0.25, 'output': 1.25},
    },
    'ollama': {
        'default': {'input': 0.0, 'output': 0.0},  # Local, no cost
    }
}


class LLMLogger:
    """
    Service for logging all LLM calls to the database.
    
    Usage:
        llm_logger = LLMLogger(db_facade)
        
        # Log a call
        record = llm_logger.log_call(
            user_id='user123',
            provider='openai',
            model='gpt-4o',
            system_prompt='You are helpful.',
            user_prompt='Hello',
            response_content='Hi there!',
            input_tokens=10,
            output_tokens=5
        )
    """
    
    def __init__(self, db_facade=None):
        self.db_facade = db_facade
    
    def log_call(
        self,
        user_id: str,
        provider: str,
        model: str,
        request_type: str = 'completion',
        execution_id: str = None,
        agent_id: str = None,
        system_prompt: str = None,
        user_prompt: str = None,
        messages: List[Dict] = None,
        response_content: str = None,
        tool_calls: List[Dict] = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        temperature: float = None,
        max_tokens: int = None,
        latency_ms: int = 0,
        status: str = 'success',
        error_message: str = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[LLMCallRecord]:
        """
        Log an LLM call to the database.
        
        Args:
            user_id: ID of the user making the call
            provider: LLM provider (openai, anthropic, ollama)
            model: Model name
            request_type: Type of request (completion, chat, embedding)
            execution_id: Associated execution ID if any
            agent_id: Associated agent ID if any
            system_prompt: System prompt used
            user_prompt: User prompt used
            messages: Full messages array for chat
            response_content: Response from LLM
            tool_calls: Tool calls made by LLM
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            temperature: Temperature setting
            max_tokens: Max tokens setting
            latency_ms: Request latency in milliseconds
            status: success or failed
            error_message: Error message if failed
            metadata: Additional metadata
            
        Returns:
            LLMCallRecord object
        """
        call_id = str(uuid.uuid4())
        total_tokens = input_tokens + output_tokens
        cost_estimate = self._calculate_cost(provider, model, input_tokens, output_tokens)
        
        record = LLMCallRecord(
            call_id=call_id,
            user_id=user_id,
            provider=provider,
            model=model,
            request_type=request_type,
            execution_id=execution_id,
            agent_id=agent_id,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            messages=messages,
            response_content=response_content,
            tool_calls=tool_calls,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_estimate=cost_estimate,
            temperature=temperature,
            max_tokens=max_tokens,
            latency_ms=latency_ms,
            status=status,
            error_message=error_message,
            metadata=metadata or {},
            created_at=datetime.now()
        )
        
        # Save to database
        if self.db_facade:
            try:
                self._save_to_db(record)
            except Exception as e:
                logger.error(f"Failed to save LLM call to database: {e}")
        
        return record
    
    def _calculate_cost(self, provider: str, model: str, 
                       input_tokens: int, output_tokens: int) -> float:
        """Calculate estimated cost for the LLM call."""
        provider_costs = COST_PER_MILLION_TOKENS.get(provider, {})
        model_costs = provider_costs.get(model, provider_costs.get('default', {'input': 0, 'output': 0}))
        
        input_cost = (input_tokens / 1_000_000) * model_costs.get('input', 0)
        output_cost = (output_tokens / 1_000_000) * model_costs.get('output', 0)
        
        return round(input_cost + output_cost, 6)
    
    def _save_to_db(self, record: LLMCallRecord):
        """Save LLM call record to database."""
        self.db_facade.execute("""
            INSERT INTO llm_calls (
                call_id, execution_id, agent_id, user_id,
                provider, model, request_type,
                system_prompt, user_prompt, messages,
                response_content, tool_calls,
                input_tokens, output_tokens, total_tokens,
                cost_estimate, temperature, max_tokens,
                latency_ms, status, error_message, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.call_id,
            record.execution_id,
            record.agent_id,
            record.user_id,
            record.provider,
            record.model,
            record.request_type,
            record.system_prompt,
            record.user_prompt,
            json.dumps(record.messages) if record.messages else None,
            record.response_content,
            json.dumps(record.tool_calls) if record.tool_calls else None,
            record.input_tokens,
            record.output_tokens,
            record.total_tokens,
            record.cost_estimate,
            record.temperature,
            record.max_tokens,
            record.latency_ms,
            record.status,
            record.error_message,
            json.dumps(record.metadata)
        ))
    
    def get_calls_by_user(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get LLM calls for a user."""
        if not self.db_facade:
            return []
        
        return self.db_facade.fetch_all("""
            SELECT * FROM llm_calls 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (user_id, limit)) or []
    
    def get_calls_by_execution(self, execution_id: str) -> List[Dict]:
        """Get LLM calls for an execution."""
        if not self.db_facade:
            return []
        
        return self.db_facade.fetch_all("""
            SELECT * FROM llm_calls 
            WHERE execution_id = ? 
            ORDER BY created_at ASC
        """, (execution_id,)) or []
    
    def get_usage_stats(self, user_id: str = None, 
                       days: int = 30) -> Dict[str, Any]:
        """Get usage statistics."""
        if not self.db_facade:
            return {}
        
        if user_id:
            result = self.db_facade.fetch_one("""
                SELECT 
                    COUNT(*) as total_calls,
                    SUM(input_tokens) as total_input_tokens,
                    SUM(output_tokens) as total_output_tokens,
                    SUM(total_tokens) as total_tokens,
                    SUM(cost_estimate) as total_cost,
                    AVG(latency_ms) as avg_latency
                FROM llm_calls 
                WHERE user_id = ? 
                AND created_at > datetime('now', ?)
            """, (user_id, f'-{days} days'))
        else:
            result = self.db_facade.fetch_one("""
                SELECT 
                    COUNT(*) as total_calls,
                    SUM(input_tokens) as total_input_tokens,
                    SUM(output_tokens) as total_output_tokens,
                    SUM(total_tokens) as total_tokens,
                    SUM(cost_estimate) as total_cost,
                    AVG(latency_ms) as avg_latency
                FROM llm_calls 
                WHERE created_at > datetime('now', ?)
            """, (f'-{days} days',))
        
        return result or {}
    
    def get_provider_breakdown(self, user_id: str = None, 
                              days: int = 30) -> List[Dict]:
        """Get breakdown by provider."""
        if not self.db_facade:
            return []
        
        if user_id:
            return self.db_facade.fetch_all("""
                SELECT 
                    provider,
                    model,
                    COUNT(*) as calls,
                    SUM(total_tokens) as tokens,
                    SUM(cost_estimate) as cost
                FROM llm_calls 
                WHERE user_id = ? 
                AND created_at > datetime('now', ?)
                GROUP BY provider, model
                ORDER BY calls DESC
            """, (user_id, f'-{days} days')) or []
        else:
            return self.db_facade.fetch_all("""
                SELECT 
                    provider,
                    model,
                    COUNT(*) as calls,
                    SUM(total_tokens) as tokens,
                    SUM(cost_estimate) as cost
                FROM llm_calls 
                WHERE created_at > datetime('now', ?)
                GROUP BY provider, model
                ORDER BY calls DESC
            """, (f'-{days} days',)) or []


# Singleton instance
_llm_logger_instance = None


def get_llm_logger(db_facade=None) -> LLMLogger:
    """Get or create the LLM logger singleton."""
    global _llm_logger_instance
    if _llm_logger_instance is None:
        _llm_logger_instance = LLMLogger(db_facade)
    elif db_facade and _llm_logger_instance.db_facade is None:
        _llm_logger_instance.db_facade = db_facade
    return _llm_logger_instance
