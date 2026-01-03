"""
Example Python Script Agent - Research Assistant

This script demonstrates how to define an AI agent using Abhikarta-LLM's 
Python Script Mode. Instead of using JSON configuration, power users can 
define agents programmatically with full Python flexibility.

Features demonstrated:
- Agent configuration via Python dict
- Custom tool configuration
- LLM provider settings
- HITL (Human-in-the-Loop) configuration
- Tags and metadata

Version: 1.4.8
Copyright © 2025-2030, All Rights Reserved
"""

# ==============================================================================
# Agent Configuration
# ==============================================================================

# System prompt that defines the agent's behavior
SYSTEM_PROMPT = """You are a research assistant specializing in finding, 
analyzing, and synthesizing information from multiple sources.

Your responsibilities:
1. Search for relevant information on the given topic
2. Analyze and cross-reference multiple sources
3. Identify key findings and insights
4. Present findings in a clear, organized manner
5. Cite sources appropriately

Guidelines:
- Be thorough but concise
- Focus on accuracy and factual information
- Highlight conflicting information when found
- Provide confidence levels for conclusions
"""

# Tool configuration for the agent
TOOLS = [
    "web_search",           # Search the web
    "document_reader",      # Read and parse documents
    "summarizer",           # Summarize long content
    "fact_checker"          # Verify facts
]

# LLM configuration
LLM_CONFIG = {
    "provider": "ollama",   # Using local Ollama
    "model": "mistral",     # Mistral 7B model
    "temperature": 0.3,     # Lower temperature for factual responses
    "max_tokens": 2048,
    "top_p": 0.9
}

# Human-in-the-Loop configuration
HITL_CONFIG = {
    "enabled": True,
    "approval_required": False,  # Don't require approval for every action
    "review_threshold": 0.7,     # Request review if confidence < 70%
    "escalation_rules": [
        {
            "condition": "sensitive_topic",
            "action": "require_approval"
        },
        {
            "condition": "high_stakes_decision",
            "action": "notify_supervisor"
        }
    ]
}

# ==============================================================================
# Agent Definition (Required)
# ==============================================================================

# The __export__ variable is required - it defines what this script produces
agent = {
    "name": "Research Assistant",
    "description": "An AI research assistant that helps find and analyze information",
    "agent_type": "react",           # ReAct pattern for reasoning
    "version": "1.0.0",
    
    # Core configuration
    "system_prompt": SYSTEM_PROMPT,
    "tools": TOOLS,
    "llm_config": LLM_CONFIG,
    "hitl_config": HITL_CONFIG,
    
    # Workflow configuration for multi-step tasks
    "workflow": {
        "max_iterations": 10,
        "timeout_seconds": 300,
        "retry_on_error": True,
        "max_retries": 3
    },
    
    # Metadata
    "tags": ["research", "analysis", "python-script"],
    "category": "productivity",
    "difficulty": "intermediate",
    
    # Sample prompts for testing
    "sample_prompts": [
        "Research the latest developments in renewable energy technology",
        "Find and summarize the key points from recent AI safety papers",
        "Compare different approaches to sustainable agriculture"
    ]
}

# ==============================================================================
# Export (Required)
# ==============================================================================

# This is what gets saved to the database
__export__ = agent


# ==============================================================================
# Optional: Custom Execution Logic
# ==============================================================================

def execute(input_data: dict) -> dict:
    """
    Custom execution function (optional).
    
    If defined, this function will be called when the agent is executed
    via the Python Script Mode execute endpoint.
    
    Args:
        input_data: Dictionary containing:
            - prompt: The user's input prompt
            - context: Optional context from previous interactions
            - options: Optional execution options
            
    Returns:
        Dictionary containing:
            - response: The agent's response
            - steps: List of reasoning steps taken
            - sources: List of sources consulted
            - confidence: Confidence score (0-1)
    """
    prompt = input_data.get('prompt', '')
    
    # In a real implementation, this would use the agent's tools
    # and LLM to process the request
    return {
        "response": f"[Research results for: {prompt}]",
        "steps": [
            "1. Analyzed the query",
            "2. Identified key topics",
            "3. Searched for information",
            "4. Synthesized findings"
        ],
        "sources": [],
        "confidence": 0.85
    }


# ==============================================================================
# Optional: Validation
# ==============================================================================

def validate() -> tuple:
    """
    Validate the agent configuration.
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not agent.get('name'):
        return False, "Agent name is required"
    if not agent.get('system_prompt'):
        return False, "System prompt is required"
    if not agent.get('llm_config'):
        return False, "LLM configuration is required"
    
    return True, "Agent configuration is valid"
