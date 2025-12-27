"""
Agent Template Manager - Template library management.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.

Patent Pending: Certain architectural patterns and implementations described in this
software may be subject to patent applications.
"""

import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class AgentTemplate:
    """Agent template definition."""
    template_id: str
    name: str
    description: str
    category: str
    agent_type: str
    icon: str = "bi-robot"
    difficulty: str = "intermediate"  # beginner, intermediate, advanced
    workflow: Dict[str, Any] = field(default_factory=dict)
    llm_config: Dict[str, Any] = field(default_factory=dict)
    tools: List[str] = field(default_factory=list)
    hitl_config: Dict[str, Any] = field(default_factory=dict)
    sample_prompts: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    is_system: bool = True
    created_by: str = "system"
    created_at: str = ""
    use_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AgentTemplateManager:
    """
    Manages agent templates including built-in and custom templates.
    """
    
    def __init__(self, db_facade=None):
        """Initialize with optional database facade."""
        self.db_facade = db_facade
        self._templates: Dict[str, AgentTemplate] = {}
        self._init_builtin_templates()
        logger.info("AgentTemplateManager initialized")
    
    def _init_builtin_templates(self):
        """Initialize built-in system templates."""
        builtin = [
            AgentTemplate(
                template_id="tpl_react_basic",
                name="Basic ReAct Agent",
                description="A simple ReAct agent that reasons and acts iteratively to solve tasks. Perfect for general-purpose automation.",
                category="General",
                agent_type="react",
                icon="bi-arrow-repeat",
                difficulty="beginner",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "User Input", 
                         "position": {"x": 100, "y": 200}},
                        {"node_id": "llm", "node_type": "llm", "name": "LLM Reasoning",
                         "position": {"x": 350, "y": 200}},
                        {"node_id": "tools", "node_type": "tool_executor", "name": "Execute Tools",
                         "position": {"x": 600, "y": 200}},
                        {"node_id": "output", "node_type": "output", "name": "Response",
                         "position": {"x": 850, "y": 200}}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "llm"},
                        {"edge_id": "e2", "source_node": "llm", "target_node": "tools"},
                        {"edge_id": "e3", "source_node": "tools", "target_node": "llm", 
                         "label": "Continue"},
                        {"edge_id": "e4", "source_node": "llm", "target_node": "output",
                         "condition": "is_final"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                tools=["web_search", "calculator"],
                sample_prompts=[
                    "Search for the latest news about AI and summarize the top 3 stories",
                    "Calculate the compound interest on $10,000 at 5% for 10 years"
                ],
                tags=["react", "general", "beginner"]
            ),
            AgentTemplate(
                template_id="tpl_customer_support",
                name="Customer Support Agent",
                description="Conversational agent for customer support with knowledge base retrieval and ticket creation capabilities.",
                category="Customer Service",
                agent_type="conversational",
                icon="bi-headset",
                difficulty="intermediate",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Customer Query",
                         "position": {"x": 100, "y": 200}},
                        {"node_id": "classify", "node_type": "llm", "name": "Intent Classification",
                         "position": {"x": 300, "y": 200}},
                        {"node_id": "kb_search", "node_type": "tool", "name": "Knowledge Base",
                         "position": {"x": 500, "y": 100}},
                        {"node_id": "escalate", "node_type": "hitl", "name": "Human Escalation",
                         "position": {"x": 500, "y": 300}},
                        {"node_id": "respond", "node_type": "llm", "name": "Generate Response",
                         "position": {"x": 700, "y": 200}},
                        {"node_id": "output", "node_type": "output", "name": "Response",
                         "position": {"x": 900, "y": 200}}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "classify"},
                        {"edge_id": "e2", "source_node": "classify", "target_node": "kb_search",
                         "condition": "is_faq"},
                        {"edge_id": "e3", "source_node": "classify", "target_node": "escalate",
                         "condition": "needs_human"},
                        {"edge_id": "e4", "source_node": "kb_search", "target_node": "respond"},
                        {"edge_id": "e5", "source_node": "escalate", "target_node": "respond"},
                        {"edge_id": "e6", "source_node": "respond", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.3,
                    "max_tokens": 1000,
                    "system_prompt": "You are a helpful customer support agent. Be polite, professional, and solution-oriented."
                },
                tools=["knowledge_base_search", "create_ticket", "get_order_status"],
                hitl_config={
                    "enabled": True,
                    "triggers": ["complex_issue", "complaint", "refund_request"],
                    "timeout_minutes": 30
                },
                sample_prompts=[
                    "I want to return my order #12345",
                    "How do I reset my password?",
                    "I'm having trouble with my subscription"
                ],
                tags=["support", "conversational", "hitl"]
            ),
            AgentTemplate(
                template_id="tpl_data_analyst",
                name="Data Analysis Agent",
                description="Agent for analyzing data, generating insights, and creating visualizations from structured data.",
                category="Analytics",
                agent_type="tool_calling",
                icon="bi-bar-chart-line",
                difficulty="advanced",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Analysis Request",
                         "position": {"x": 100, "y": 200}},
                        {"node_id": "plan", "node_type": "llm", "name": "Analysis Planning",
                         "position": {"x": 300, "y": 200}},
                        {"node_id": "query", "node_type": "tool", "name": "Data Query",
                         "position": {"x": 500, "y": 100}},
                        {"node_id": "analyze", "node_type": "tool", "name": "Statistical Analysis",
                         "position": {"x": 500, "y": 300}},
                        {"node_id": "visualize", "node_type": "tool", "name": "Create Charts",
                         "position": {"x": 700, "y": 200}},
                        {"node_id": "summarize", "node_type": "llm", "name": "Insights Summary",
                         "position": {"x": 900, "y": 200}},
                        {"node_id": "output", "node_type": "output", "name": "Report",
                         "position": {"x": 1100, "y": 200}}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "plan"},
                        {"edge_id": "e2", "source_node": "plan", "target_node": "query"},
                        {"edge_id": "e3", "source_node": "query", "target_node": "analyze"},
                        {"edge_id": "e4", "source_node": "analyze", "target_node": "visualize"},
                        {"edge_id": "e5", "source_node": "visualize", "target_node": "summarize"},
                        {"edge_id": "e6", "source_node": "summarize", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.2,
                    "max_tokens": 3000
                },
                tools=["sql_query", "pandas_analysis", "chart_generator", "statistics"],
                sample_prompts=[
                    "Analyze sales trends for Q4 and identify top-performing products",
                    "Create a correlation matrix for customer demographics",
                    "Generate a monthly revenue forecast based on historical data"
                ],
                tags=["analytics", "data", "visualization", "advanced"]
            ),
            AgentTemplate(
                template_id="tpl_research_assistant",
                name="Research Assistant",
                description="RAG-powered research agent that searches, retrieves, and synthesizes information from multiple sources.",
                category="Research",
                agent_type="retrieval",
                icon="bi-search",
                difficulty="intermediate",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Research Query",
                         "position": {"x": 100, "y": 200}},
                        {"node_id": "decompose", "node_type": "llm", "name": "Query Decomposition",
                         "position": {"x": 300, "y": 200}},
                        {"node_id": "search", "node_type": "tool", "name": "Multi-Source Search",
                         "position": {"x": 500, "y": 100}},
                        {"node_id": "retrieve", "node_type": "tool", "name": "Document Retrieval",
                         "position": {"x": 500, "y": 300}},
                        {"node_id": "synthesize", "node_type": "llm", "name": "Synthesize Findings",
                         "position": {"x": 700, "y": 200}},
                        {"node_id": "output", "node_type": "output", "name": "Research Report",
                         "position": {"x": 900, "y": 200}}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "decompose"},
                        {"edge_id": "e2", "source_node": "decompose", "target_node": "search"},
                        {"edge_id": "e3", "source_node": "decompose", "target_node": "retrieve"},
                        {"edge_id": "e4", "source_node": "search", "target_node": "synthesize"},
                        {"edge_id": "e5", "source_node": "retrieve", "target_node": "synthesize"},
                        {"edge_id": "e6", "source_node": "synthesize", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "anthropic",
                    "model": "claude-3-5-sonnet-20241022",
                    "temperature": 0.4,
                    "max_tokens": 4000
                },
                tools=["web_search", "arxiv_search", "wikipedia", "document_qa"],
                sample_prompts=[
                    "Research the latest developments in quantum computing",
                    "Compare different approaches to renewable energy storage",
                    "Summarize recent papers on large language models"
                ],
                tags=["research", "rag", "retrieval"]
            ),
            AgentTemplate(
                template_id="tpl_code_assistant",
                name="Code Assistant",
                description="Developer assistant for code generation, review, debugging, and documentation.",
                category="Development",
                agent_type="tool_calling",
                icon="bi-code-slash",
                difficulty="intermediate",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Code Request",
                         "position": {"x": 100, "y": 200}},
                        {"node_id": "analyze", "node_type": "llm", "name": "Analyze Request",
                         "position": {"x": 300, "y": 200}},
                        {"node_id": "generate", "node_type": "llm", "name": "Generate Code",
                         "position": {"x": 500, "y": 100}},
                        {"node_id": "review", "node_type": "llm", "name": "Code Review",
                         "position": {"x": 500, "y": 300}},
                        {"node_id": "test", "node_type": "tool", "name": "Run Tests",
                         "position": {"x": 700, "y": 200}},
                        {"node_id": "output", "node_type": "output", "name": "Final Code",
                         "position": {"x": 900, "y": 200}}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "analyze"},
                        {"edge_id": "e2", "source_node": "analyze", "target_node": "generate"},
                        {"edge_id": "e3", "source_node": "generate", "target_node": "review"},
                        {"edge_id": "e4", "source_node": "review", "target_node": "test"},
                        {"edge_id": "e5", "source_node": "test", "target_node": "generate",
                         "condition": "tests_failed"},
                        {"edge_id": "e6", "source_node": "test", "target_node": "output",
                         "condition": "tests_passed"}
                    ]
                },
                llm_config={
                    "provider": "anthropic",
                    "model": "claude-3-5-sonnet-20241022",
                    "temperature": 0.2,
                    "max_tokens": 4000
                },
                tools=["code_executor", "file_operations", "git_operations"],
                sample_prompts=[
                    "Write a Python function to merge two sorted arrays",
                    "Review this code for security vulnerabilities",
                    "Add unit tests for the user authentication module"
                ],
                tags=["coding", "development", "testing"]
            ),
            AgentTemplate(
                template_id="tpl_workflow_automation",
                name="Workflow Automation",
                description="Plan-and-execute agent for complex multi-step workflows with approval gates.",
                category="Automation",
                agent_type="plan_and_execute",
                icon="bi-diagram-3",
                difficulty="advanced",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Workflow Request",
                         "position": {"x": 100, "y": 200}},
                        {"node_id": "plan", "node_type": "llm", "name": "Create Plan",
                         "position": {"x": 300, "y": 200}},
                        {"node_id": "approve_plan", "node_type": "hitl", "name": "Approve Plan",
                         "position": {"x": 500, "y": 200}},
                        {"node_id": "execute", "node_type": "tool_executor", "name": "Execute Steps",
                         "position": {"x": 700, "y": 200}},
                        {"node_id": "verify", "node_type": "llm", "name": "Verify Results",
                         "position": {"x": 900, "y": 200}},
                        {"node_id": "output", "node_type": "output", "name": "Completion Report",
                         "position": {"x": 1100, "y": 200}}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "plan"},
                        {"edge_id": "e2", "source_node": "plan", "target_node": "approve_plan"},
                        {"edge_id": "e3", "source_node": "approve_plan", "target_node": "execute"},
                        {"edge_id": "e4", "source_node": "approve_plan", "target_node": "plan",
                         "condition": "rejected"},
                        {"edge_id": "e5", "source_node": "execute", "target_node": "verify"},
                        {"edge_id": "e6", "source_node": "verify", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.3,
                    "max_tokens": 2000
                },
                tools=["api_caller", "file_operations", "email_sender", "scheduler"],
                hitl_config={
                    "enabled": True,
                    "require_plan_approval": True,
                    "cost_threshold": 10.00,
                    "timeout_minutes": 60
                },
                sample_prompts=[
                    "Automate the monthly report generation and distribution",
                    "Set up a data pipeline to sync customer records",
                    "Create a backup routine for critical databases"
                ],
                tags=["automation", "workflow", "hitl", "advanced"]
            )
        ]
        
        for template in builtin:
            from abhikarta.utils.helpers import get_timestamp
            template.created_at = get_timestamp()
            self._templates[template.template_id] = template
    
    def get_template(self, template_id: str) -> Optional[AgentTemplate]:
        """Get a template by ID."""
        return self._templates.get(template_id)
    
    def list_templates(self, category: str = None, 
                       difficulty: str = None,
                       agent_type: str = None) -> List[AgentTemplate]:
        """
        List templates with optional filters.
        
        Args:
            category: Filter by category
            difficulty: Filter by difficulty level
            agent_type: Filter by agent type
            
        Returns:
            List of matching templates
        """
        templates = list(self._templates.values())
        
        if category:
            templates = [t for t in templates if t.category.lower() == category.lower()]
        if difficulty:
            templates = [t for t in templates if t.difficulty == difficulty]
        if agent_type:
            templates = [t for t in templates if t.agent_type == agent_type]
        
        return sorted(templates, key=lambda t: t.name)
    
    def get_categories(self) -> List[str]:
        """Get list of unique categories."""
        categories = set(t.category for t in self._templates.values())
        return sorted(categories)
    
    def create_agent_from_template(self, template_id: str, name: str,
                                    created_by: str, 
                                    agent_manager) -> Optional['Agent']:
        """
        Create a new agent from a template.
        
        Args:
            template_id: Template ID
            name: Name for the new agent
            created_by: User ID
            agent_manager: AgentManager instance
            
        Returns:
            New Agent or None
        """
        template = self.get_template(template_id)
        if not template:
            return None
        
        # Increment use count
        template.use_count += 1
        
        # Create agent with template config
        agent = agent_manager.create_agent(
            name=name,
            description=template.description,
            agent_type=template.agent_type,
            created_by=created_by,
            config={
                'workflow': template.workflow,
                'llm_config': template.llm_config,
                'tools': template.tools.copy(),
                'hitl_config': template.hitl_config,
                'from_template': template_id
            }
        )
        
        if agent:
            agent.workflow = template.workflow
            agent.llm_config = template.llm_config
            agent.tools = template.tools.copy()
            agent.hitl_config = template.hitl_config
            agent.tags = template.tags.copy()
        
        return agent
    
    def save_as_template(self, agent: 'Agent', template_name: str,
                         category: str, created_by: str) -> AgentTemplate:
        """
        Save an agent as a custom template.
        
        Args:
            agent: Agent to save as template
            template_name: Name for the template
            category: Template category
            created_by: User ID
            
        Returns:
            New AgentTemplate
        """
        from abhikarta.utils.helpers import generate_id, get_timestamp
        
        template = AgentTemplate(
            template_id=generate_id("tpl"),
            name=template_name,
            description=agent.description,
            category=category,
            agent_type=agent.agent_type,
            workflow=agent.workflow,
            llm_config=agent.llm_config,
            tools=agent.tools.copy(),
            hitl_config=agent.hitl_config,
            tags=agent.tags.copy(),
            is_system=False,
            created_by=created_by,
            created_at=get_timestamp()
        )
        
        self._templates[template.template_id] = template
        logger.info(f"Created custom template: {template.template_id}")
        
        return template
