"""
Example Python Script Swarm - Content Creation Team

This script demonstrates how to define an agent swarm using Abhikarta-LLM's 
Python Script Mode. Swarms coordinate multiple specialized agents working
together on complex tasks using event-driven choreography.

Features demonstrated:
- Multiple agent roles
- Event-driven coordination
- Auto-scaling configuration
- Trigger definitions
- Communication patterns

Version: 1.4.8
Copyright © 2025-2030, All Rights Reserved
"""

# ==============================================================================
# Agent Role Definitions
# ==============================================================================

# Lead researcher - finds and gathers information
researcher_agent = {
    "role": "researcher",
    "agent_id": "content_researcher",  # ID of existing agent, or define inline
    "agent_name": "Lead Researcher",
    "description": "Researches topics and gathers source material",
    "subscriptions": ["task_assigned", "revision_requested"],
    "publishes": ["research_complete", "sources_found"],
    "min_instances": 1,
    "max_instances": 3,
    "auto_scale": True,
    "idle_timeout": 300
}

# Content writer - creates initial drafts
writer_agent = {
    "role": "writer",
    "agent_id": "content_writer",
    "agent_name": "Content Writer",
    "description": "Creates content based on research",
    "subscriptions": ["research_complete", "revision_requested"],
    "publishes": ["draft_ready", "content_updated"],
    "min_instances": 1,
    "max_instances": 2,
    "auto_scale": True,
    "idle_timeout": 300
}

# Editor - reviews and improves content
editor_agent = {
    "role": "editor",
    "agent_id": "content_editor",
    "agent_name": "Content Editor",
    "description": "Reviews, edits, and improves content quality",
    "subscriptions": ["draft_ready", "content_updated"],
    "publishes": ["edit_complete", "revision_requested"],
    "min_instances": 1,
    "max_instances": 1,
    "auto_scale": False,
    "idle_timeout": 600
}

# Quality reviewer - final quality check
reviewer_agent = {
    "role": "reviewer",
    "agent_id": "quality_reviewer",
    "agent_name": "Quality Reviewer",
    "description": "Final quality assurance and approval",
    "subscriptions": ["edit_complete"],
    "publishes": ["approved", "rejected"],
    "min_instances": 1,
    "max_instances": 1,
    "auto_scale": False,
    "idle_timeout": 600
}

# ==============================================================================
# Trigger Definitions
# ==============================================================================

triggers = [
    {
        "trigger_id": "new_content_request",
        "trigger_type": "api",
        "name": "New Content Request",
        "description": "Triggered when new content is requested via API",
        "config": {
            "endpoint": "/api/content/request",
            "method": "POST"
        },
        "is_active": True
    },
    {
        "trigger_id": "scheduled_content",
        "trigger_type": "schedule",
        "name": "Scheduled Content",
        "description": "Generates content on a schedule",
        "config": {
            "cron": "0 9 * * MON",  # Every Monday at 9 AM
            "timezone": "UTC"
        },
        "is_active": False
    },
    {
        "trigger_id": "content_queue",
        "trigger_type": "queue",
        "name": "Content Queue",
        "description": "Processes content requests from queue",
        "config": {
            "queue_name": "content_requests",
            "batch_size": 5
        },
        "is_active": True
    }
]

# ==============================================================================
# Swarm Definition (Required)
# ==============================================================================

swarm = {
    "name": "Content Creation Team",
    "description": "Collaborative swarm for creating high-quality content",
    "version": "1.0.0",
    
    # Coordination strategy
    "strategy": "event_driven",  # Options: event_driven, hierarchical, consensus
    
    # Agent configuration
    "agents": [
        researcher_agent,
        writer_agent,
        editor_agent,
        reviewer_agent
    ],
    
    # Trigger configuration
    "triggers": triggers,
    
    # Event routing rules
    "event_routing": {
        "task_assigned": ["researcher"],
        "research_complete": ["writer"],
        "draft_ready": ["editor"],
        "edit_complete": ["reviewer"],
        "revision_requested": ["writer", "researcher"],
        "approved": ["_output"],
        "rejected": ["writer"]
    },
    
    # Global configuration
    "config": {
        "max_iterations": 5,           # Max revision cycles
        "timeout_minutes": 60,         # Overall timeout
        "quality_threshold": 0.8,      # Minimum quality score
        "parallel_tasks": 3,           # Max concurrent tasks
        "event_bus": {
            "type": "memory",          # memory, kafka, rabbitmq
            "retention_hours": 24
        }
    },
    
    # Metadata
    "tags": ["content", "creative", "team", "python-script"],
    "category": "creative"
}

# ==============================================================================
# Export (Required)
# ==============================================================================

__export__ = swarm


# ==============================================================================
# Optional: Event Handlers
# ==============================================================================

def on_task_assigned(event: dict) -> dict:
    """Handle new task assignment."""
    task = event.get('data', {})
    return {
        "action": "start_research",
        "topic": task.get('topic'),
        "requirements": task.get('requirements', [])
    }


def on_research_complete(event: dict) -> dict:
    """Handle research completion, pass to writer."""
    research = event.get('data', {})
    return {
        "action": "create_draft",
        "research": research,
        "outline": research.get('outline', [])
    }


def on_draft_ready(event: dict) -> dict:
    """Handle draft completion, pass to editor."""
    draft = event.get('data', {})
    return {
        "action": "edit_content",
        "content": draft.get('content'),
        "metadata": draft.get('metadata', {})
    }


def on_edit_complete(event: dict) -> dict:
    """Handle editing completion, pass to reviewer."""
    edited = event.get('data', {})
    return {
        "action": "review_content",
        "content": edited.get('content'),
        "changes": edited.get('changes', [])
    }


def execute(input_data: dict) -> dict:
    """
    Execute the swarm with a content request.
    
    Args:
        input_data: Dictionary with content request details
        
    Returns:
        Final content output
    """
    topic = input_data.get('topic', 'General topic')
    
    # Simulated swarm execution
    return {
        "status": "completed",
        "content": f"Generated content about: {topic}",
        "quality_score": 0.92,
        "iterations": 2,
        "agents_involved": ["researcher", "writer", "editor", "reviewer"]
    }
