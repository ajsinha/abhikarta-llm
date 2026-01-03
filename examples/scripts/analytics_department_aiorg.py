"""
Example Python Script AI Organization - Analytics Department

This script demonstrates how to define an AI Organization using Abhikarta-LLM's 
Python Script Mode. AI Organizations model hierarchical structures with
delegation patterns and human-in-the-loop integration.

Features demonstrated:
- Hierarchical node structure
- Delegation strategies
- HITL configuration per node
- Human + AI hybrid roles
- Task routing

Version: 1.4.8
Copyright © 2025-2030, All Rights Reserved
"""

# ==============================================================================
# Node Definitions
# ==============================================================================

# Executive level - CEO / Director
ceo_node = {
    "node_id": "ceo",
    "role_name": "Chief Analytics Officer",
    "role_type": "executive",
    "description": "Strategic oversight of analytics operations",
    
    # Agent configuration (AI-powered role)
    "agent_id": "executive_agent",
    "agent_config": {
        "provider": "ollama",
        "model": "mistral",
        "system_prompt": "You are the Chief Analytics Officer. Make strategic decisions about analytics priorities."
    },
    
    # Human oversight
    "human_name": "Jane Smith",
    "human_email": "jane.smith@company.com",
    
    # HITL settings
    "hitl_enabled": True,
    "hitl_approval_required": True,      # CEO must approve major decisions
    "hitl_review_delegation": False,
    "hitl_timeout_hours": 24,
    "hitl_auto_proceed": False,          # Wait for human input
    
    # Notification preferences
    "notification_channels": ["email", "slack"],
    "notification_triggers": ["task_assigned", "decision_required", "escalation"],
    
    # Position for visual display
    "position_x": 400,
    "position_y": 50
}

# Manager level - Department managers
data_manager_node = {
    "node_id": "data_manager",
    "role_name": "Data Engineering Manager",
    "role_type": "manager",
    "description": "Manages data engineering team and pipelines",
    "parent_node_id": "ceo",
    
    "agent_id": "manager_agent",
    "agent_config": {
        "provider": "ollama",
        "model": "mistral",
        "system_prompt": "You manage data engineering tasks. Delegate work to analysts and review their output."
    },
    
    "delegation_strategy": "round_robin",  # Options: round_robin, load_balanced, skill_based
    
    "hitl_enabled": True,
    "hitl_approval_required": False,
    "hitl_review_delegation": True,       # Can review delegated tasks
    "hitl_timeout_hours": 12,
    "hitl_auto_proceed": True,
    
    "notification_channels": ["email", "teams"],
    "position_x": 200,
    "position_y": 150
}

analytics_manager_node = {
    "node_id": "analytics_manager",
    "role_name": "Analytics Manager",
    "role_type": "manager",
    "description": "Manages analytics team and insights generation",
    "parent_node_id": "ceo",
    
    "agent_id": "analytics_manager_agent",
    "agent_config": {
        "provider": "ollama",
        "model": "mistral",
        "system_prompt": "You manage analytics tasks. Prioritize and assign work to analysts."
    },
    
    "delegation_strategy": "skill_based",
    
    "hitl_enabled": True,
    "hitl_approval_required": False,
    "hitl_review_delegation": True,
    "hitl_timeout_hours": 12,
    "hitl_auto_proceed": True,
    
    "notification_channels": ["email", "slack"],
    "position_x": 600,
    "position_y": 150
}

# Analyst level - Individual contributors
data_analyst_1 = {
    "node_id": "data_analyst_1",
    "role_name": "Senior Data Analyst",
    "role_type": "analyst",
    "description": "Handles data analysis and reporting",
    "parent_node_id": "data_manager",
    
    "agent_id": "analyst_agent",
    "agent_config": {
        "provider": "ollama",
        "model": "mistral",
        "system_prompt": "You are a senior data analyst. Analyze data and provide insights."
    },
    
    "skills": ["sql", "python", "visualization", "statistics"],
    
    "hitl_enabled": False,               # Fully autonomous
    "hitl_approval_required": False,
    "hitl_timeout_hours": 8,
    "hitl_auto_proceed": True,
    
    "position_x": 100,
    "position_y": 250
}

data_analyst_2 = {
    "node_id": "data_analyst_2",
    "role_name": "Data Analyst",
    "role_type": "analyst",
    "description": "Data processing and transformation",
    "parent_node_id": "data_manager",
    
    "agent_id": "analyst_agent",
    "agent_config": {
        "provider": "ollama",
        "model": "mistral"
    },
    
    "skills": ["sql", "etl", "data_cleaning"],
    
    "hitl_enabled": False,
    "position_x": 300,
    "position_y": 250
}

insights_analyst = {
    "node_id": "insights_analyst",
    "role_name": "Business Insights Analyst",
    "role_type": "analyst",
    "description": "Generates business insights and recommendations",
    "parent_node_id": "analytics_manager",
    
    "agent_id": "insights_agent",
    "agent_config": {
        "provider": "ollama",
        "model": "mistral",
        "system_prompt": "You analyze business data and provide actionable insights."
    },
    
    "skills": ["business_analysis", "visualization", "storytelling"],
    
    "hitl_enabled": True,
    "hitl_approval_required": False,
    "hitl_review_delegation": False,
    "hitl_timeout_hours": 8,
    "hitl_auto_proceed": True,
    
    "position_x": 500,
    "position_y": 250
}

ml_analyst = {
    "node_id": "ml_analyst",
    "role_name": "ML Analyst",
    "role_type": "analyst",
    "description": "Machine learning model development",
    "parent_node_id": "analytics_manager",
    
    "agent_id": "ml_agent",
    "agent_config": {
        "provider": "ollama",
        "model": "mistral",
        "system_prompt": "You develop and evaluate machine learning models."
    },
    
    "skills": ["machine_learning", "python", "model_evaluation"],
    
    "hitl_enabled": True,
    "hitl_approval_required": True,      # ML models need review
    "hitl_timeout_hours": 24,
    "hitl_auto_proceed": False,
    
    "position_x": 700,
    "position_y": 250
}

# ==============================================================================
# AI Organization Definition (Required)
# ==============================================================================

aiorg = {
    "name": "Analytics Department",
    "description": "AI-powered analytics department with hierarchical delegation",
    "version": "1.0.0",
    
    # Organization structure
    "nodes": [
        ceo_node,
        data_manager_node,
        analytics_manager_node,
        data_analyst_1,
        data_analyst_2,
        insights_analyst,
        ml_analyst
    ],
    
    # Root of the hierarchy
    "root_node_id": "ceo",
    
    # Global configuration
    "config": {
        "default_delegation_strategy": "round_robin",
        "max_delegation_depth": 3,
        "task_timeout_hours": 48,
        "escalation_enabled": True,
        "event_bus_channel": "analytics_dept"
    },
    
    # Task routing rules
    "routing_rules": [
        {
            "condition": {"task_type": "data_pipeline"},
            "route_to": "data_manager"
        },
        {
            "condition": {"task_type": "insight_request"},
            "route_to": "analytics_manager"
        },
        {
            "condition": {"task_type": "ml_project"},
            "route_to": "ml_analyst"
        },
        {
            "condition": {"priority": "high"},
            "route_to": "ceo"
        }
    ],
    
    # Metadata
    "tags": ["analytics", "data", "hierarchical", "python-script"],
    "category": "business"
}

# ==============================================================================
# Export (Required)
# ==============================================================================

__export__ = aiorg


# ==============================================================================
# Optional: Task Handlers
# ==============================================================================

def on_task_created(task: dict) -> dict:
    """Handle new task creation."""
    task_type = task.get('type', 'general')
    
    # Determine initial assignment based on type
    if task_type == 'data_pipeline':
        return {"assign_to": "data_manager"}
    elif task_type == 'insight_request':
        return {"assign_to": "analytics_manager"}
    elif task_type == 'ml_project':
        return {"assign_to": "ml_analyst"}
    else:
        return {"assign_to": "ceo"}


def on_task_delegated(event: dict) -> dict:
    """Handle task delegation events."""
    from_node = event.get('from_node')
    to_node = event.get('to_node')
    task = event.get('task', {})
    
    return {
        "status": "delegated",
        "from": from_node,
        "to": to_node,
        "task_id": task.get('task_id')
    }


def on_task_escalated(event: dict) -> dict:
    """Handle task escalation events."""
    task = event.get('task', {})
    reason = event.get('reason', 'unknown')
    
    return {
        "action": "escalate",
        "task_id": task.get('task_id'),
        "reason": reason,
        "escalate_to": "ceo"
    }


def execute(input_data: dict) -> dict:
    """
    Submit a task to the organization.
    
    Args:
        input_data: Task details including title, description, type
        
    Returns:
        Task creation result
    """
    task_title = input_data.get('title', 'New Task')
    task_type = input_data.get('type', 'general')
    
    # Simulated task submission
    return {
        "task_id": "task_001",
        "status": "created",
        "assigned_to": on_task_created(input_data).get('assign_to'),
        "message": f"Task '{task_title}' created and assigned"
    }
