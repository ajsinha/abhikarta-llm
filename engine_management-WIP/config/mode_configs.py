"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


from typing import Dict, Any

# Default configurations for each execution mode

CHAT_CONFIG = {
    "context_window_size": 10,
    "llm_params": {
        "temperature": 0.7,
        "max_tokens": 2000
    }
}

REACT_CONFIG = {
    "max_iterations": 10,
    "tool_timeout": 30,
    "llm_params": {
        "temperature": 0.5,
        "max_tokens": 1500
    }
}

DAG_CONFIG = {
    "parallel_execution": True,
    "max_parallel_nodes": 5,
    "node_timeout": 60
}

RAG_CONFIG = {
    "top_k": 5,
    "similarity_threshold": 0.7,
    "rerank": True,
    "llm_params": {
        "temperature": 0.3,
        "max_tokens": 1500
    }
}

PLANNING_CONFIG = {
    "plan_type": "sequential",
    "adaptive": True,
    "llm_params": {
        "temperature": 0.3,
        "max_tokens": 2000
    }
}

AUTONOMOUS_CONFIG = {
    "max_iterations": 20,
    "decision_temperature": 0.5,
    "safety_checks": True
}

HITL_CONFIG = {
    "approval_timeout": 300,  # 5 minutes
    "require_feedback": False
}

BACKGROUND_CONFIG = {
    "batch_size": 10,
    "max_retries": 3,
    "retry_delay": 5
}

COT_CONFIG = {
    "reasoning_depth": 3,
    "llm_params": {
        "temperature": 0.7,
        "max_tokens": 2500
    }
}

TOOL_CONFIG = {
    "max_tool_calls": 10,
    "tool_timeout": 30,
    "parallel_tools": False
}

MULTI_AGENT_CONFIG = {
    "max_agents": 5,
    "coordination_strategy": "round_robin",
    "llm_params": {
        "temperature": 0.6,
        "max_tokens": 1500
    }
}

HYBRID_CONFIG = {
    "allow_mode_switching": True,
    "default_mode": "chat"
}

LISTENING_CONFIG = {
    "kafka_poll_interval": 1.0,
    "batch_processing": True,
    "error_handling": "log_and_continue"
}

# Mode configuration lookup
MODE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "chat": CHAT_CONFIG,
    "react": REACT_CONFIG,
    "dag": DAG_CONFIG,
    "rag": RAG_CONFIG,
    "planning": PLANNING_CONFIG,
    "autonomous": AUTONOMOUS_CONFIG,
    "hitl": HITL_CONFIG,
    "background": BACKGROUND_CONFIG,
    "cot": COT_CONFIG,
    "tool": TOOL_CONFIG,
    "multi_agent": MULTI_AGENT_CONFIG,
    "hybrid": HYBRID_CONFIG,
    "listening": LISTENING_CONFIG
}

def get_mode_config(mode: str) -> Dict[str, Any]:
    """Get configuration for a specific mode"""
    return MODE_CONFIGS.get(mode, {}).copy()

def merge_configs(base: Dict, overrides: Dict) -> Dict:
    """Deep merge configuration dictionaries"""
    result = base.copy()
    
    for key, value in overrides.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result
