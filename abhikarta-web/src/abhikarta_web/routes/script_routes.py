"""
Python Script Mode Routes
Version: 1.4.8

Provides UI and API endpoints for creating, validating, saving, and executing
Python scripts that define agents, workflows, swarms, and AI organizations.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

import json
import traceback
import ast
import sys
from io import StringIO
from datetime import datetime, timezone
from flask import render_template, request, redirect, url_for, flash, jsonify, session
import logging

from .abstract_routes import AbstractRoutes, login_required, admin_required
from abhikarta.database.delegates import ScriptsDelegate

logger = logging.getLogger(__name__)


def validate_python_syntax(code: str) -> tuple:
    """Validate Python syntax without executing."""
    try:
        ast.parse(code)
        return True, "Syntax is valid"
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"


def validate_script_structure(code: str, entity_type: str) -> tuple:
    """Validate script structure for the entity type."""
    warnings = []
    
    if '__export__' not in code:
        return False, "Script must define '__export__' variable with the entity definition", []
    
    return True, "Script structure is valid", warnings


def safe_execute_script(code: str, entry_point: str = '__export__') -> tuple:
    """Safely execute a script and extract the exported entity."""
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()
    
    try:
        namespace = {'__builtins__': __builtins__, '__name__': '__main__'}
        exec(code, namespace)
        
        if entry_point not in namespace:
            return False, f"Entry point '{entry_point}' not found", sys.stdout.getvalue(), sys.stderr.getvalue()
        
        result = namespace[entry_point]
        return True, result, sys.stdout.getvalue(), sys.stderr.getvalue()
        
    except Exception as e:
        tb = traceback.format_exc()
        return False, f"{type(e).__name__}: {str(e)}\n{tb}", sys.stdout.getvalue(), sys.stderr.getvalue()
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def get_agent_template():
    return '''"""
Research Assistant Agent - Python Script Mode
==============================================
A production-ready AI research assistant with web search, document analysis,
and HITL (Human-in-the-Loop) capabilities.

This script demonstrates:
- Custom Tool classes with execute methods
- AgentConfig dataclass for type-safe configuration
- Prompt templates with variable substitution
- Custom execution logic with error handling
- Validation and testing utilities
"""

import os
import json
import re
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Callable
from enum import Enum


# ==============================================================================
# ENUMS AND CONSTANTS
# ==============================================================================

class AgentType(Enum):
    """Supported agent reasoning patterns."""
    REACT = "react"           # Reasoning and Acting
    GOAL = "goal"             # Goal-oriented planning
    REFLECT = "reflect"       # Self-reflection
    HIERARCHICAL = "hierarchical"  # Task decomposition


class ToolCategory(Enum):
    """Tool categories for organization."""
    SEARCH = "search"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    UTILITY = "utility"


# ==============================================================================
# TOOL DEFINITIONS - Define custom tools as classes
# ==============================================================================

@dataclass
class ToolDefinition:
    """Base class for tool definitions."""
    name: str
    description: str
    category: ToolCategory
    parameters: Dict[str, Any] = field(default_factory=dict)
    required_params: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "parameters": self.parameters,
            "required": self.required_params
        }


class WebSearchTool(ToolDefinition):
    """Web search tool for finding information online."""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web for current information on any topic",
            category=ToolCategory.SEARCH,
            parameters={
                "query": {"type": "string", "description": "Search query"},
                "num_results": {"type": "integer", "default": 5},
                "date_filter": {"type": "string", "enum": ["day", "week", "month", "year"]}
            },
            required_params=["query"]
        )
    
    def execute(self, query: str, num_results: int = 5, **kwargs) -> Dict[str, Any]:
        """Execute web search and return results."""
        # In production, this would call actual search API
        return {
            "status": "success",
            "query": query,
            "results": [
                {"title": f"Result {i+1} for: {query}", "url": f"https://example.com/{i}"}
                for i in range(num_results)
            ],
            "timestamp": datetime.now().isoformat()
        }


class DocumentReaderTool(ToolDefinition):
    """Tool for reading and parsing documents."""
    
    def __init__(self):
        super().__init__(
            name="document_reader",
            description="Read and extract text from documents (PDF, DOCX, TXT)",
            category=ToolCategory.ANALYSIS,
            parameters={
                "file_path": {"type": "string", "description": "Path to document"},
                "extract_tables": {"type": "boolean", "default": True},
                "extract_images": {"type": "boolean", "default": False}
            },
            required_params=["file_path"]
        )
    
    def execute(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """Read document and extract content."""
        return {
            "status": "success",
            "file_path": file_path,
            "content": f"[Extracted content from {file_path}]",
            "metadata": {"pages": 1, "word_count": 500}
        }


class SummarizerTool(ToolDefinition):
    """Tool for summarizing long content."""
    
    def __init__(self):
        super().__init__(
            name="summarizer",
            description="Generate concise summaries of long text content",
            category=ToolCategory.GENERATION,
            parameters={
                "text": {"type": "string", "description": "Text to summarize"},
                "max_length": {"type": "integer", "default": 200},
                "style": {"type": "string", "enum": ["bullet", "paragraph", "executive"]}
            },
            required_params=["text"]
        )
    
    def execute(self, text: str, max_length: int = 200, style: str = "paragraph", **kwargs) -> Dict[str, Any]:
        """Summarize the provided text."""
        summary = text[:max_length] + "..." if len(text) > max_length else text
        return {
            "status": "success",
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary),
            "style": style
        }


class FactCheckerTool(ToolDefinition):
    """Tool for verifying facts against trusted sources."""
    
    def __init__(self):
        super().__init__(
            name="fact_checker",
            description="Verify claims against trusted sources and databases",
            category=ToolCategory.ANALYSIS,
            parameters={
                "claim": {"type": "string", "description": "Claim to verify"},
                "sources": {"type": "array", "items": {"type": "string"}}
            },
            required_params=["claim"]
        )
    
    def execute(self, claim: str, sources: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Check if a claim is factually accurate."""
        return {
            "status": "success",
            "claim": claim,
            "verdict": "unverified",
            "confidence": 0.75,
            "sources_checked": sources or ["wikipedia", "news"]
        }


# ==============================================================================
# CONFIGURATION CLASSES
# ==============================================================================

@dataclass
class LLMConfig:
    """LLM provider configuration."""
    provider: str = "ollama"
    model: str = "llama3.2:3b"
    temperature: float = 0.3
    max_tokens: int = 2048
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HITLConfig:
    """Human-in-the-Loop configuration."""
    enabled: bool = True
    approval_required: bool = False
    review_threshold: float = 0.7
    timeout_minutes: int = 60
    escalation_rules: List[Dict[str, str]] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.escalation_rules:
            self.escalation_rules = [
                {"condition": "sensitive_topic", "action": "require_approval"},
                {"condition": "high_stakes_decision", "action": "notify_supervisor"},
                {"condition": "low_confidence", "action": "request_review"}
            ]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorkflowConfig:
    """Workflow execution settings."""
    max_iterations: int = 10
    timeout_seconds: int = 300
    retry_on_error: bool = True
    max_retries: int = 3
    checkpoint_enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ==============================================================================
# PROMPT TEMPLATES
# ==============================================================================

class PromptTemplate:
    """Template class for generating prompts with variable substitution."""
    
    def __init__(self, template: str, variables: List[str] = None):
        self.template = template
        self.variables = variables or self._extract_variables(template)
    
    def _extract_variables(self, template: str) -> List[str]:
        """Extract variable names from template."""
        return re.findall(r'\\{(\\w+)\\}', template)
    
    def render(self, **kwargs) -> str:
        """Render template with provided variables."""
        result = self.template
        for key, value in kwargs.items():
            result = result.replace(f'{{{key}}}', str(value))
        return result
    
    def validate(self, **kwargs) -> bool:
        """Check if all required variables are provided."""
        return all(var in kwargs for var in self.variables)


# System prompt template
SYSTEM_PROMPT = PromptTemplate("""You are a research assistant specializing in {domain}.

Your responsibilities:
1. Search for relevant information on the given topic
2. Analyze and cross-reference multiple sources  
3. Identify key findings and insights
4. Present findings in a clear, organized manner
5. Cite sources appropriately

Current task focus: {task_focus}

Guidelines:
- Be thorough but concise
- Focus on accuracy and factual information
- Highlight conflicting information when found
- Provide confidence levels (0-100%) for conclusions
- Always cite your sources

Output format: {output_format}
""")


# ==============================================================================
# AGENT BUILDER CLASS
# ==============================================================================

class AgentBuilder:
    """Builder pattern for constructing agent configurations."""
    
    def __init__(self, name: str):
        self.name = name
        self.description = ""
        self.agent_type = AgentType.REACT
        self.system_prompt = ""
        self.tools: List[ToolDefinition] = []
        self.llm_config = LLMConfig()
        self.hitl_config = HITLConfig()
        self.workflow_config = WorkflowConfig()
        self.tags: List[str] = []
        self.metadata: Dict[str, Any] = {}
    
    def with_description(self, description: str) -> 'AgentBuilder':
        self.description = description
        return self
    
    def with_type(self, agent_type: AgentType) -> 'AgentBuilder':
        self.agent_type = agent_type
        return self
    
    def with_system_prompt(self, prompt: str) -> 'AgentBuilder':
        self.system_prompt = prompt
        return self
    
    def with_tool(self, tool: ToolDefinition) -> 'AgentBuilder':
        self.tools.append(tool)
        return self
    
    def with_tools(self, tools: List[ToolDefinition]) -> 'AgentBuilder':
        self.tools.extend(tools)
        return self
    
    def with_llm_config(self, config: LLMConfig) -> 'AgentBuilder':
        self.llm_config = config
        return self
    
    def with_hitl_config(self, config: HITLConfig) -> 'AgentBuilder':
        self.hitl_config = config
        return self
    
    def with_tags(self, tags: List[str]) -> 'AgentBuilder':
        self.tags = tags
        return self
    
    def with_metadata(self, key: str, value: Any) -> 'AgentBuilder':
        self.metadata[key] = value
        return self
    
    def build(self) -> Dict[str, Any]:
        return asdict(self)
'''


def get_workflow_template():
    return '''"""
Document Analysis Workflow - Python Script Mode
================================================
A comprehensive workflow that processes documents through multiple
analysis stages including entity extraction, sentiment analysis,
and key points summarization using parallel processing.

Features:
- Multi-node DAG workflow
- Parallel processing branches
- LLM-powered analysis nodes
- Result aggregation
- Executive summary generation

Modify this template to create your own workflow!
"""

# ==============================================================================
# NODE DEFINITIONS - Each node is a processing step in the workflow
# ==============================================================================

# Input Node - Receives the document for analysis
input_node = {
    "node_id": "input",
    "name": "Document Input",
    "node_type": "input",
    "description": "Receives document for analysis",
    "config": {
        "accepted_types": ["pdf", "docx", "txt", "html"],
        "max_size_mb": 50
    }
}

# Text Extraction Node - Extracts text from the document
extract_node = {
    "node_id": "extract",
    "name": "Text Extraction",
    "node_type": "code",
    "description": "Extract text content from document",
    "config": {
        "extract_tables": True,
        "extract_images": False,
        "preserve_formatting": True
    }
}

# Entity Extraction Node (Parallel Branch 1)
entity_node = {
    "node_id": "entities",
    "name": "Entity Extraction",
    "node_type": "llm",
    "description": "Extract named entities from text",
    "config": {
        "provider": "ollama",
        "model": "llama3.2:3b",
        "prompt_template": "Extract all named entities (people, organizations, locations, dates) from:\\n\\n{text}"
    }
}

# Sentiment Analysis Node (Parallel Branch 2)
sentiment_node = {
    "node_id": "sentiment",
    "name": "Sentiment Analysis",
    "node_type": "llm",
    "description": "Analyze sentiment of the text",
    "config": {
        "provider": "ollama",
        "model": "llama3.2:3b",
        "prompt_template": "Analyze the sentiment. Rate from -1 (negative) to +1 (positive):\\n\\n{text}"
    }
}

# Key Points Extraction Node (Parallel Branch 3)
keypoints_node = {
    "node_id": "keypoints",
    "name": "Key Points",
    "node_type": "llm",
    "description": "Extract key points and main ideas",
    "config": {
        "provider": "ollama",
        "model": "llama3.2:3b",
        "prompt_template": "Extract the 5-10 most important key points from:\\n\\n{text}"
    }
}

# Aggregation Node - Combines results from parallel branches
aggregate_node = {
    "node_id": "aggregate",
    "name": "Aggregate Results",
    "node_type": "code",
    "description": "Combine all analysis results",
    "config": {
        "merge_strategy": "combine",
        "format": "structured"
    }
}

# Summary Generation Node - Creates executive summary
summary_node = {
    "node_id": "summary",
    "name": "Generate Summary",
    "node_type": "llm",
    "description": "Generate executive summary",
    "config": {
        "provider": "ollama",
        "model": "llama3.2:3b",
        "prompt_template": """Based on the analysis, generate an executive summary:

Entities: {entities}
Sentiment: {sentiment}
Key Points: {keypoints}

Generate a concise executive summary (max 200 words)."""
    }
}

# Output Node - Final results
output_node = {
    "node_id": "output",
    "name": "Analysis Output",
    "node_type": "output",
    "description": "Final analysis results",
    "config": {
        "format": "json",
        "include_metadata": True
    }
}

# ==============================================================================
# EDGE DEFINITIONS - Define the DAG connections between nodes
# ==============================================================================

edges = [
    # Input to extraction
    {"source": "input", "target": "extract"},
    
    # Extraction to parallel analysis nodes (fan-out)
    {"source": "extract", "target": "entities"},
    {"source": "extract", "target": "sentiment"},
    {"source": "extract", "target": "keypoints"},
    
    # Parallel nodes to aggregation (fan-in)
    {"source": "entities", "target": "aggregate"},
    {"source": "sentiment", "target": "aggregate"},
    {"source": "keypoints", "target": "aggregate"},
    
    # Aggregation to summary
    {"source": "aggregate", "target": "summary"},
    
    # Summary to output
    {"source": "summary", "target": "output"}
]

# ==============================================================================
# WORKFLOW DEFINITION - The complete workflow configuration
# ==============================================================================

workflow = {
    "name": "Document Analysis Pipeline",
    "description": "Comprehensive document analysis with parallel processing",
    "version": "1.0.0",
    "workflow_type": "dag",
    
    # All nodes in the workflow
    "nodes": [
        input_node,
        extract_node,
        entity_node,
        sentiment_node,
        keypoints_node,
        aggregate_node,
        summary_node,
        output_node
    ],
    
    # Node connections
    "edges": edges,
    
    # Input/output schemas
    "input_schema": {
        "type": "object",
        "properties": {
            "document": {"type": "string", "description": "Document content or path"},
            "options": {"type": "object", "description": "Processing options"}
        },
        "required": ["document"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "entities": {"type": "array"},
            "sentiment": {"type": "object"},
            "key_points": {"type": "array"}
        }
    },
    
    # Execution settings
    "environment": {
        "timeout_seconds": 600,
        "max_parallel": 3,
        "retry_failed_nodes": True,
        "max_retries": 2
    },
    
    # Metadata
    "tags": ["document", "analysis", "nlp", "python-script"],
    "category": "data-processing"
}

# ==============================================================================
# EXPORT - Required! This is what gets saved to the database
# ==============================================================================

__export__ = workflow


# ==============================================================================
# OPTIONAL: Custom Node Functions
# ==============================================================================

def extract_text(input_data: dict) -> dict:
    """Custom text extraction logic."""
    document = input_data.get('document', '')
    return {
        "text": document,
        "metadata": {"length": len(document), "type": "text"}
    }


def aggregate_results(entities: dict, sentiment: dict, keypoints: dict) -> dict:
    """Aggregate parallel processing results."""
    return {
        "entities": entities.get('entities', []),
        "sentiment": sentiment.get('sentiment', {}),
        "key_points": keypoints.get('points', []),
        "analysis_complete": True
    }


def execute(input_data: dict) -> dict:
    """Custom workflow execution."""
    document = input_data.get('document', '')
    return {
        "summary": "Executive summary of the document...",
        "entities": ["Entity1", "Entity2"],
        "sentiment": {"score": 0.5, "label": "neutral"},
        "key_points": ["Point 1", "Point 2", "Point 3"]
    }
'''


def get_swarm_template():
    return '''"""
Content Creation Swarm - Python Script Mode
============================================
A collaborative swarm of AI agents that work together to create
high-quality content through research, writing, editing, and review.

Features:
- Multiple specialized agent roles
- Event-driven coordination
- Auto-scaling configuration
- API and scheduled triggers
- Quality control workflow

Modify this template to create your own swarm!
"""

# ==============================================================================
# AGENT ROLE DEFINITIONS - Each role is a specialized agent in the swarm
# ==============================================================================

# Lead Researcher - Finds and gathers information
researcher_agent = {
    "role": "researcher",
    "agent_id": "content_researcher",       # ID of existing agent or define inline
    "agent_name": "Lead Researcher",
    "description": "Researches topics and gathers source material",
    "subscriptions": ["task_assigned", "revision_requested"],
    "publishes": ["research_complete", "sources_found"],
    "min_instances": 1,
    "max_instances": 3,
    "auto_scale": True,
    "idle_timeout": 300
}

# Content Writer - Creates initial drafts
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

# Editor - Reviews and improves content
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

# Quality Reviewer - Final quality check
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
# TRIGGER DEFINITIONS - How the swarm is activated
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
            "cron": "0 9 * * MON",      # Every Monday at 9 AM
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
# SWARM DEFINITION - The complete swarm configuration
# ==============================================================================

swarm = {
    "name": "Content Creation Team",
    "description": "Collaborative swarm for creating high-quality content",
    "version": "1.0.0",
    
    # Coordination strategy
    "strategy": "event_driven",     # Options: event_driven, hierarchical, consensus
    
    # Agent configuration
    "agents": [
        researcher_agent,
        writer_agent,
        editor_agent,
        reviewer_agent
    ],
    
    # Trigger configuration
    "triggers": triggers,
    
    # Event routing rules - which roles receive which events
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
        "max_iterations": 5,            # Max revision cycles
        "timeout_minutes": 60,          # Overall timeout
        "quality_threshold": 0.8,       # Minimum quality score
        "parallel_tasks": 3,            # Max concurrent tasks
        "event_bus": {
            "type": "memory",           # Options: memory, kafka, rabbitmq
            "retention_hours": 24
        }
    },
    
    # Metadata
    "tags": ["content", "creative", "team", "python-script"],
    "category": "creative"
}

# ==============================================================================
# EXPORT - Required! This is what gets saved to the database
# ==============================================================================

__export__ = swarm


# ==============================================================================
# OPTIONAL: Event Handlers
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


def execute(input_data: dict) -> dict:
    """Execute the swarm with a content request."""
    topic = input_data.get('topic', 'General topic')
    return {
        "status": "completed",
        "content": f"Generated content about: {topic}",
        "quality_score": 0.92,
        "iterations": 2,
        "agents_involved": ["researcher", "writer", "editor", "reviewer"]
    }
'''


def get_aiorg_template():
    return '''"""
Analytics Department AI Organization - Python Script Mode
==========================================================
A hierarchical AI organization modeling an analytics department with
executives, managers, and analysts. Includes delegation strategies
and human-in-the-loop integration.

Features:
- Hierarchical node structure (CEO -> Managers -> Analysts)
- Delegation strategies per role
- HITL configuration for oversight
- Human + AI hybrid roles
- Skill-based task routing

Modify this template to create your own AI organization!
"""

# ==============================================================================
# NODE DEFINITIONS - Each node represents a role in the organization
# ==============================================================================

# Executive Level - Chief Analytics Officer
ceo_node = {
    "node_id": "ceo",
    "role_name": "Chief Analytics Officer",
    "role_type": "executive",
    "description": "Strategic oversight of analytics operations",
    
    # AI Agent configuration
    "agent_id": "executive_agent",
    "agent_config": {
        "provider": "ollama",
        "model": "llama3.2:3b",
        "system_prompt": "You are the Chief Analytics Officer. Make strategic decisions about analytics priorities."
    },
    
    # Human oversight (optional - for hybrid roles)
    "human_name": "Jane Smith",
    "human_email": "jane.smith@company.com",
    
    # HITL settings - CEO must approve major decisions
    "hitl_enabled": True,
    "hitl_approval_required": True,
    "hitl_review_delegation": False,
    "hitl_timeout_hours": 24,
    "hitl_auto_proceed": False,
    
    # Notification preferences
    "notification_channels": ["email", "slack"],
    "notification_triggers": ["task_assigned", "decision_required", "escalation"],
    
    # Position for visual display
    "position_x": 400,
    "position_y": 50
}

# Manager Level - Data Engineering Manager
data_manager_node = {
    "node_id": "data_manager",
    "role_name": "Data Engineering Manager",
    "role_type": "manager",
    "description": "Manages data engineering team and pipelines",
    "parent_node_id": "ceo",
    
    "agent_id": "manager_agent",
    "agent_config": {
        "provider": "ollama",
        "model": "llama3.2:3b",
        "system_prompt": "You manage data engineering tasks. Delegate work to analysts."
    },
    
    "delegation_strategy": "round_robin",   # Options: round_robin, load_balanced, skill_based
    
    "hitl_enabled": True,
    "hitl_approval_required": False,
    "hitl_review_delegation": True,
    "hitl_timeout_hours": 12,
    "hitl_auto_proceed": True,
    
    "notification_channels": ["email", "teams"],
    "position_x": 200,
    "position_y": 150
}

# Manager Level - Analytics Manager
analytics_manager_node = {
    "node_id": "analytics_manager",
    "role_name": "Analytics Manager",
    "role_type": "manager",
    "description": "Manages analytics team and insights generation",
    "parent_node_id": "ceo",
    
    "agent_id": "analytics_manager_agent",
    "agent_config": {
        "provider": "ollama",
        "model": "llama3.2:3b",
        "system_prompt": "You manage analytics tasks. Prioritize and assign work."
    },
    
    "delegation_strategy": "skill_based",
    
    "hitl_enabled": True,
    "hitl_approval_required": False,
    "hitl_review_delegation": True,
    "hitl_timeout_hours": 12,
    
    "notification_channels": ["email", "slack"],
    "position_x": 600,
    "position_y": 150
}

# Analyst Level - Senior Data Analyst
data_analyst_1 = {
    "node_id": "data_analyst_1",
    "role_name": "Senior Data Analyst",
    "role_type": "analyst",
    "description": "Handles data analysis and reporting",
    "parent_node_id": "data_manager",
    
    "agent_id": "analyst_agent",
    "agent_config": {
        "provider": "ollama",
        "model": "llama3.2:3b",
        "system_prompt": "You are a senior data analyst. Analyze data and provide insights."
    },
    
    "skills": ["sql", "python", "visualization", "statistics"],
    
    "hitl_enabled": False,      # Fully autonomous
    "position_x": 100,
    "position_y": 250
}

# Analyst Level - ML Analyst
ml_analyst = {
    "node_id": "ml_analyst",
    "role_name": "ML Analyst",
    "role_type": "analyst",
    "description": "Machine learning model development",
    "parent_node_id": "analytics_manager",
    
    "agent_id": "ml_agent",
    "agent_config": {
        "provider": "ollama",
        "model": "llama3.2:3b",
        "system_prompt": "You develop and evaluate machine learning models."
    },
    
    "skills": ["machine_learning", "python", "model_evaluation"],
    
    "hitl_enabled": True,
    "hitl_approval_required": True,     # ML models need review
    "hitl_timeout_hours": 24,
    
    "position_x": 700,
    "position_y": 250
}

# ==============================================================================
# AI ORGANIZATION DEFINITION - The complete organization configuration
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
    
    # Task routing rules - automatic assignment based on conditions
    "routing_rules": [
        {
            "condition": {"task_type": "data_pipeline"},
            "route_to": "data_manager"
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
# EXPORT - Required! This is what gets saved to the database
# ==============================================================================

__export__ = aiorg


# ==============================================================================
# OPTIONAL: Task Handlers
# ==============================================================================

def on_task_created(task: dict) -> dict:
    """Handle new task creation and determine initial assignment."""
    task_type = task.get('type', 'general')
    
    if task_type == 'data_pipeline':
        return {"assign_to": "data_manager"}
    elif task_type == 'ml_project':
        return {"assign_to": "ml_analyst"}
    else:
        return {"assign_to": "ceo"}


def on_task_delegated(event: dict) -> dict:
    """Handle task delegation events."""
    return {
        "status": "delegated",
        "from": event.get('from_node'),
        "to": event.get('to_node'),
        "task_id": event.get('task', {}).get('task_id')
    }


def execute(input_data: dict) -> dict:
    """Submit a task to the organization."""
    task_title = input_data.get('title', 'New Task')
    return {
        "task_id": "task_001",
        "status": "created",
        "assigned_to": on_task_created(input_data).get('assign_to'),
        "message": f"Task \\'{task_title}\\' created and assigned"
    }
'''


class ScriptRoutes(AbstractRoutes):
    """Handles Python Script Mode routes."""
    
    def __init__(self, app):
        super().__init__(app)
        self._scripts_delegate = None
        logger.info("ScriptRoutes initialized")
    
    def _get_delegate(self):
        """Get or create ScriptsDelegate instance."""
        if self._scripts_delegate is None and self.db_facade is not None:
            self._scripts_delegate = ScriptsDelegate(self.db_facade)
        return self._scripts_delegate
    
    def register_routes(self):
        """Register all script routes."""
        
        @self.app.route('/scripts')
        @login_required
        def list_scripts():
            delegate = self._get_delegate()
            entity_type = request.args.get('type', '')
            
            if delegate:
                if entity_type:
                    scripts = delegate.get_scripts_by_entity_type(entity_type)
                else:
                    scripts = delegate.get_all_scripts()
            else:
                scripts = []
            
            return render_template('scripts/list.html', scripts=scripts or [], entity_type=entity_type)
        
        @self.app.route('/scripts/create')
        @login_required
        def create_script():
            entity_type = request.args.get('type', 'agent')
            templates = {
                'agent': get_agent_template(),
                'workflow': get_workflow_template(),
                'swarm': get_swarm_template(),
                'aiorg': get_aiorg_template()
            }
            return render_template('scripts/create.html', 
                                 entity_type=entity_type,
                                 template_code=templates.get(entity_type, templates['agent']))
        
        @self.app.route('/scripts/<script_id>')
        @login_required
        def view_script(script_id):
            delegate = self._get_delegate()
            if not delegate:
                flash('Database not available.', 'error')
                return redirect(url_for('list_scripts'))
            
            script = delegate.get_script(script_id)
            if not script:
                flash('Script not found.', 'error')
                return redirect(url_for('list_scripts'))
            executions = delegate.get_script_executions(script_id, limit=20)
            return render_template('scripts/view.html', script=script, executions=executions or [])
        
        @self.app.route('/scripts/<script_id>/edit')
        @login_required
        def edit_script(script_id):
            delegate = self._get_delegate()
            if not delegate:
                flash('Database not available.', 'error')
                return redirect(url_for('list_scripts'))
            
            script = delegate.get_script(script_id)
            if not script:
                flash('Script not found.', 'error')
                return redirect(url_for('list_scripts'))
            return render_template('scripts/edit.html', script=script)
        
        @self.app.route('/api/scripts', methods=['POST'])
        @login_required
        def api_create_script():
            try:
                data = request.get_json()
                name = data.get('name', '').strip()
                description = data.get('description', '').strip()
                entity_type = data.get('entity_type', 'agent')
                script_content = data.get('script_content', '')
                entry_point = data.get('entry_point', '__export__')
                tags = data.get('tags', [])
                
                if not name or not script_content:
                    return jsonify({'success': False, 'error': 'Name and script content required'}), 400
                
                is_valid, msg = validate_python_syntax(script_content)
                if not is_valid:
                    return jsonify({'success': False, 'error': msg, 'validation_status': 'invalid'}), 400
                
                is_valid, msg, warnings = validate_script_structure(script_content, entity_type)
                validation_status = 'valid' if is_valid else 'invalid'
                
                delegate = self._get_delegate()
                if not delegate:
                    return jsonify({'success': False, 'error': 'Database not available'}), 500
                
                user_id = session.get('user_id')
                # Get user's numeric ID if user_id is a string
                if isinstance(user_id, str) and self.db_facade:
                    user = self.db_facade.fetch_one("SELECT id FROM users WHERE user_id = ?", (user_id,))
                    user_id = user.get('id') if user else None
                
                script_id = delegate.create_script(
                    name=name,
                    entity_type=entity_type,
                    script_content=script_content,
                    created_by=user_id,
                    description=description,
                    entry_point=entry_point,
                    tags=json.dumps(tags)
                )
                
                if script_id:
                    # Set validation status
                    delegate.set_validation_status(script_id, validation_status, msg)
                    return jsonify({'success': True, 'script_id': script_id, 'validation_status': validation_status})
                else:
                    return jsonify({'success': False, 'error': 'Failed to create script'}), 500
                    
            except Exception as e:
                logger.error(f"Error creating script: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/scripts/<script_id>', methods=['PUT'])
        @login_required
        def api_update_script(script_id):
            try:
                data = request.get_json()
                delegate = self._get_delegate()
                if not delegate:
                    return jsonify({'success': False, 'error': 'Database not available'}), 500
                
                script = delegate.get_script(script_id)
                if not script:
                    return jsonify({'success': False, 'error': 'Script not found'}), 404
                
                script_content = data.get('script_content', '')
                is_valid, msg = validate_python_syntax(script_content)
                if not is_valid:
                    return jsonify({'success': False, 'error': msg}), 400
                
                # Update with version increment
                success = delegate.update_script(
                    script_id,
                    name=data.get('name'),
                    description=data.get('description'),
                    script_content=script_content,
                    entry_point=data.get('entry_point', '__export__'),
                    tags=json.dumps(data.get('tags', []))
                )
                
                if success:
                    delegate.set_validation_status(script_id, 'valid', msg)
                    new_version = (script.get('version') or 1) + 1
                    return jsonify({'success': True, 'version': new_version})
                else:
                    return jsonify({'success': False, 'error': 'Failed to update script'}), 500
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/scripts/<script_id>', methods=['DELETE'])
        @login_required
        def api_delete_script(script_id):
            try:
                delegate = self._get_delegate()
                if not delegate:
                    return jsonify({'success': False, 'error': 'Database not available'}), 500
                
                success = delegate.deactivate_script(script_id)
                if success:
                    return jsonify({'success': True})
                else:
                    return jsonify({'success': False, 'error': 'Failed to delete script'}), 500
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/scripts/<script_id>/execute', methods=['POST'])
        @login_required
        def api_execute_script(script_id):
            try:
                delegate = self._get_delegate()
                if not delegate:
                    return jsonify({'success': False, 'error': 'Database not available'}), 500
                
                script = delegate.get_script(script_id)
                if not script:
                    return jsonify({'success': False, 'error': 'Script not found'}), 404
                
                user_id = session.get('user_id')
                # Get user's numeric ID if user_id is a string
                if isinstance(user_id, str) and self.db_facade:
                    user = self.db_facade.fetch_one("SELECT id FROM users WHERE user_id = ?", (user_id,))
                    user_id = user.get('id') if user else None
                
                execution_id = delegate.create_execution(script_id, user_id, '{}')
                if not execution_id:
                    return jsonify({'success': False, 'error': 'Failed to create execution record'}), 500
                
                start = datetime.now(timezone.utc)
                success, result, stdout, stderr = safe_execute_script(
                    script['script_content'], 
                    script.get('entry_point') or '__export__'
                )
                duration = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
                
                if success:
                    try:
                        output = result if isinstance(result, dict) else {'value': str(result)}
                    except:
                        output = {'value': str(result)}
                    
                    delegate.complete_execution(
                        execution_id, 
                        json.dumps(output), 
                        stdout, stderr, duration
                    )
                    return jsonify({
                        'success': True, 
                        'execution_id': execution_id, 
                        'output': output, 
                        'stdout': stdout, 
                        'stderr': stderr, 
                        'duration_ms': duration
                    })
                else:
                    delegate.fail_execution(execution_id, result, stdout, stderr, duration)
                    return jsonify({
                        'success': False, 
                        'execution_id': execution_id, 
                        'error': result, 
                        'stdout': stdout, 
                        'stderr': stderr
                    }), 400
            except Exception as e:
                logger.error(f"Error executing script: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/scripts/validate-code', methods=['POST'])
        @login_required
        def api_validate_code():
            try:
                data = request.get_json()
                code = data.get('code', '')
                is_valid, msg = validate_python_syntax(code)
                if not is_valid:
                    return jsonify({'success': True, 'validation_status': 'invalid', 'message': msg})
                
                is_valid, msg, warnings = validate_script_structure(code, data.get('entity_type', 'agent'))
                return jsonify({'success': True, 'validation_status': 'valid' if is_valid else 'invalid', 'message': msg, 'warnings': warnings})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        # ======================================================================
        # TEMPLATE API ENDPOINTS
        # ======================================================================
        
        @self.app.route('/api/scripts/templates')
        @login_required
        def api_get_script_templates():
            """Get all available script templates."""
            try:
                from abhikarta.scripts import get_script_template_manager
                manager = get_script_template_manager()
                
                entity_type = request.args.get('type')
                agent_type = request.args.get('agent_type')
                
                if agent_type:
                    templates = manager.get_templates_by_agent_type(agent_type)
                elif entity_type:
                    templates = manager.get_templates_by_type(entity_type)
                else:
                    templates = manager.get_all_templates()
                
                return jsonify({
                    'success': True,
                    'templates': [t.to_dict() for t in templates],
                    'count': len(templates)
                })
            except Exception as e:
                logger.error(f"Error getting script templates: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/scripts/templates/<template_id>')
        @login_required
        def api_get_script_template(template_id):
            """Get a specific script template."""
            try:
                from abhikarta.scripts import get_script_template_manager
                manager = get_script_template_manager()
                
                template = manager.get_template(template_id)
                if not template:
                    return jsonify({'success': False, 'error': 'Template not found'}), 404
                
                # Increment use count
                manager.increment_use_count(template_id)
                
                return jsonify({
                    'success': True,
                    'template': template.to_dict()
                })
            except Exception as e:
                logger.error(f"Error getting script template {template_id}: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/scripts/templates')
        @login_required
        def script_templates():
            """Script templates library page."""
            from abhikarta.scripts import get_script_template_manager
            manager = get_script_template_manager()
            
            entity_type = request.args.get('type')
            if entity_type:
                templates = manager.get_templates_by_type(entity_type)
            else:
                templates = manager.get_all_templates()
            
            categories = manager.get_categories()
            
            return render_template('scripts/templates.html',
                                 templates=templates,
                                 categories=categories,
                                 selected_type=entity_type)
        
        @self.app.route('/scripts/templates/<template_id>')
        @login_required
        def script_template_detail(template_id):
            """View a specific script template."""
            from abhikarta.scripts import get_script_template_manager
            manager = get_script_template_manager()
            
            template = manager.get_template(template_id)
            if not template:
                flash('Template not found.', 'error')
                return redirect(url_for('script_templates'))
            
            return render_template('scripts/template_detail.html', template=template)
        
        @self.app.route('/scripts/create-from-template/<template_id>')
        @login_required
        def create_script_from_template(template_id):
            """Create a new script from a template."""
            from abhikarta.scripts import get_script_template_manager
            manager = get_script_template_manager()
            
            template = manager.get_template(template_id)
            if not template:
                flash('Template not found.', 'error')
                return redirect(url_for('script_templates'))
            
            # Increment use count
            manager.increment_use_count(template_id)
            
            return render_template('scripts/create.html',
                                 entity_type=template.entity_type,
                                 template_code=template.script_content,
                                 from_template=template)
        
        logger.info("Script routes registered")
