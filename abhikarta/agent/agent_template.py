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

Version: 1.2.5
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
    prerequisites: List[str] = field(default_factory=list)
    estimated_setup_time: str = "5 minutes"
    documentation_url: str = ""
    uses_code_fragments: bool = False
    code_fragments: List[str] = field(default_factory=list)
    
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
            # ============================================
            # GENERAL PURPOSE AGENTS
            # ============================================
            AgentTemplate(
                template_id="tpl_react_basic",
                name="Basic ReAct Agent",
                description="A simple ReAct agent that reasons and acts iteratively to solve tasks. Perfect for general-purpose automation.",
                category="General",
                agent_type="react",
                icon="bi-arrow-repeat",
                difficulty="beginner",
                estimated_setup_time="5 minutes",
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
                tags=["react", "general", "beginner"],
                prerequisites=["OpenAI API key configured"]
            ),
            AgentTemplate(
                template_id="tpl_conversational",
                name="Conversational Assistant",
                description="A friendly conversational agent for general-purpose chat interactions with memory and context awareness.",
                category="General",
                agent_type="conversational",
                icon="bi-chat-dots",
                difficulty="beginner",
                estimated_setup_time="3 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "User Message"},
                        {"node_id": "memory", "node_type": "memory", "name": "Load Context"},
                        {"node_id": "llm", "node_type": "llm", "name": "Generate Response"},
                        {"node_id": "output", "node_type": "output", "name": "Response"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "memory"},
                        {"edge_id": "e2", "source_node": "memory", "target_node": "llm"},
                        {"edge_id": "e3", "source_node": "llm", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "temperature": 0.8,
                    "max_tokens": 1000,
                    "system_prompt": "You are a friendly and helpful assistant. Engage naturally in conversation while being informative and accurate."
                },
                tools=[],
                sample_prompts=[
                    "Tell me about yourself",
                    "What's the weather like today?",
                    "Can you help me brainstorm ideas for a birthday party?"
                ],
                tags=["conversational", "chat", "beginner"]
            ),
            AgentTemplate(
                template_id="tpl_research_assistant",
                name="Research Assistant",
                description="An agent specialized in conducting research, gathering information from multiple sources, and synthesizing findings into comprehensive reports.",
                category="Research",
                agent_type="react",
                icon="bi-search",
                difficulty="intermediate",
                estimated_setup_time="10 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Research Query"},
                        {"node_id": "plan", "node_type": "llm", "name": "Research Planning"},
                        {"node_id": "search", "node_type": "tool", "name": "Multi-Source Search"},
                        {"node_id": "analyze", "node_type": "llm", "name": "Analyze Sources"},
                        {"node_id": "synthesize", "node_type": "llm", "name": "Synthesize Report"},
                        {"node_id": "output", "node_type": "output", "name": "Research Report"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "plan"},
                        {"edge_id": "e2", "source_node": "plan", "target_node": "search"},
                        {"edge_id": "e3", "source_node": "search", "target_node": "analyze"},
                        {"edge_id": "e4", "source_node": "analyze", "target_node": "synthesize"},
                        {"edge_id": "e5", "source_node": "synthesize", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.3,
                    "max_tokens": 4000,
                    "system_prompt": "You are a thorough research assistant. Gather comprehensive information, cite sources, and present balanced analysis."
                },
                tools=["web_search", "wikipedia", "academic_search", "document_reader"],
                sample_prompts=[
                    "Research the current state of quantum computing and its potential applications",
                    "Compile a report on renewable energy adoption trends worldwide",
                    "Investigate the impact of remote work on employee productivity"
                ],
                tags=["research", "analysis", "academic"]
            ),
            
            # ============================================
            # CUSTOMER SERVICE AGENTS
            # ============================================
            AgentTemplate(
                template_id="tpl_customer_support",
                name="Customer Support Agent",
                description="Conversational agent for customer support with knowledge base retrieval and ticket creation capabilities.",
                category="Customer Service",
                agent_type="conversational",
                icon="bi-headset",
                difficulty="intermediate",
                estimated_setup_time="15 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Customer Query"},
                        {"node_id": "classify", "node_type": "llm", "name": "Intent Classification"},
                        {"node_id": "kb_search", "node_type": "tool", "name": "Knowledge Base"},
                        {"node_id": "escalate", "node_type": "hitl", "name": "Human Escalation"},
                        {"node_id": "respond", "node_type": "llm", "name": "Generate Response"},
                        {"node_id": "output", "node_type": "output", "name": "Response"}
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
                tags=["support", "conversational", "hitl"],
                prerequisites=["Knowledge base populated", "Ticketing system configured"]
            ),
            AgentTemplate(
                template_id="tpl_helpdesk_triage",
                name="IT Helpdesk Triage",
                description="Automated IT helpdesk agent that triages technical issues, provides initial troubleshooting, and routes complex issues to appropriate teams.",
                category="Customer Service",
                agent_type="conversational",
                icon="bi-pc-display-horizontal",
                difficulty="intermediate",
                estimated_setup_time="20 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Issue Report"},
                        {"node_id": "classify", "node_type": "llm", "name": "Issue Classification"},
                        {"node_id": "diagnose", "node_type": "llm", "name": "Initial Diagnosis"},
                        {"node_id": "kb", "node_type": "tool", "name": "Search Solutions"},
                        {"node_id": "troubleshoot", "node_type": "llm", "name": "Troubleshooting Guide"},
                        {"node_id": "route", "node_type": "condition", "name": "Route Decision"},
                        {"node_id": "escalate", "node_type": "hitl", "name": "Escalate to Tech"},
                        {"node_id": "output", "node_type": "output", "name": "Response"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "classify"},
                        {"edge_id": "e2", "source_node": "classify", "target_node": "diagnose"},
                        {"edge_id": "e3", "source_node": "diagnose", "target_node": "kb"},
                        {"edge_id": "e4", "source_node": "kb", "target_node": "troubleshoot"},
                        {"edge_id": "e5", "source_node": "troubleshoot", "target_node": "route"},
                        {"edge_id": "e6", "source_node": "route", "target_node": "output", "condition": "resolved"},
                        {"edge_id": "e7", "source_node": "route", "target_node": "escalate", "condition": "needs_tech"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.2,
                    "max_tokens": 1500,
                    "system_prompt": "You are an IT helpdesk specialist. Diagnose technical issues systematically and provide clear troubleshooting steps."
                },
                tools=["knowledge_base_search", "create_ticket", "check_system_status", "get_user_profile"],
                hitl_config={
                    "enabled": True,
                    "triggers": ["hardware_failure", "security_incident", "network_outage"],
                    "timeout_minutes": 15,
                    "routing_rules": {
                        "network": "network_team",
                        "security": "security_team",
                        "hardware": "desktop_support"
                    }
                },
                sample_prompts=[
                    "My computer won't turn on",
                    "I can't connect to VPN",
                    "My email is not syncing"
                ],
                tags=["helpdesk", "it-support", "triage", "hitl"]
            ),
            AgentTemplate(
                template_id="tpl_complaint_handler",
                name="Complaint Resolution Agent",
                description="Specialized agent for handling customer complaints with empathy, identifying root causes, and proposing appropriate resolutions.",
                category="Customer Service",
                agent_type="conversational",
                icon="bi-exclamation-triangle",
                difficulty="advanced",
                estimated_setup_time="25 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Complaint"},
                        {"node_id": "sentiment", "node_type": "llm", "name": "Sentiment Analysis"},
                        {"node_id": "context", "node_type": "tool", "name": "Get Customer History"},
                        {"node_id": "analyze", "node_type": "llm", "name": "Root Cause Analysis"},
                        {"node_id": "resolve", "node_type": "llm", "name": "Resolution Options"},
                        {"node_id": "approve", "node_type": "hitl", "name": "Manager Approval"},
                        {"node_id": "execute", "node_type": "tool", "name": "Execute Resolution"},
                        {"node_id": "output", "node_type": "output", "name": "Resolution Confirmation"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "sentiment"},
                        {"edge_id": "e2", "source_node": "sentiment", "target_node": "context"},
                        {"edge_id": "e3", "source_node": "context", "target_node": "analyze"},
                        {"edge_id": "e4", "source_node": "analyze", "target_node": "resolve"},
                        {"edge_id": "e5", "source_node": "resolve", "target_node": "approve"},
                        {"edge_id": "e6", "source_node": "approve", "target_node": "execute"},
                        {"edge_id": "e7", "source_node": "execute", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.3,
                    "max_tokens": 2000,
                    "system_prompt": "You are a customer complaint resolution specialist. Show empathy, identify the root cause, and propose fair resolutions that balance customer satisfaction with business policies."
                },
                tools=["get_customer_profile", "get_order_history", "issue_refund", "apply_credit", "create_ticket"],
                hitl_config={
                    "enabled": True,
                    "triggers": ["high_value_customer", "legal_threat", "refund_over_100"],
                    "timeout_minutes": 60,
                    "approval_required_for": ["refund", "credit", "escalation"]
                },
                sample_prompts=[
                    "I received a damaged product and nobody is helping me!",
                    "I've been waiting 3 weeks for my refund",
                    "Your service has been terrible and I want to cancel everything"
                ],
                tags=["complaints", "resolution", "empathy", "hitl", "advanced"]
            ),
            
            # ============================================
            # ANALYTICS & DATA AGENTS
            # ============================================
            AgentTemplate(
                template_id="tpl_data_analyst",
                name="Data Analysis Agent",
                description="Agent for analyzing data, generating insights, and creating visualizations from structured data.",
                category="Analytics",
                agent_type="tool_calling",
                icon="bi-bar-chart-line",
                difficulty="advanced",
                estimated_setup_time="20 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Analysis Request"},
                        {"node_id": "plan", "node_type": "llm", "name": "Analysis Planning"},
                        {"node_id": "query", "node_type": "tool", "name": "Data Query"},
                        {"node_id": "analyze", "node_type": "tool", "name": "Statistical Analysis"},
                        {"node_id": "visualize", "node_type": "tool", "name": "Create Charts"},
                        {"node_id": "summarize", "node_type": "llm", "name": "Insights Summary"},
                        {"node_id": "output", "node_type": "output", "name": "Analysis Report"}
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
                    "max_tokens": 3000,
                    "system_prompt": "You are a data analyst. Analyze data thoroughly, identify trends and patterns, and present insights clearly."
                },
                tools=["sql_query", "pandas_analysis", "chart_generator", "export_report"],
                sample_prompts=[
                    "Analyze sales trends for the last quarter",
                    "Compare customer segments by purchase behavior",
                    "Find correlations between marketing spend and revenue"
                ],
                tags=["analytics", "data", "visualization", "reporting"],
                prerequisites=["Database connection configured", "Data access permissions"]
            ),
            AgentTemplate(
                template_id="tpl_bi_reporter",
                name="Business Intelligence Reporter",
                description="Automated BI agent that generates scheduled reports, tracks KPIs, and alerts on anomalies.",
                category="Analytics",
                agent_type="tool_calling",
                icon="bi-graph-up-arrow",
                difficulty="advanced",
                estimated_setup_time="30 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "trigger", "node_type": "input", "name": "Report Trigger"},
                        {"node_id": "fetch", "node_type": "tool", "name": "Fetch Metrics"},
                        {"node_id": "compare", "node_type": "tool", "name": "Compare to Targets"},
                        {"node_id": "anomaly", "node_type": "llm", "name": "Anomaly Detection"},
                        {"node_id": "narrative", "node_type": "llm", "name": "Generate Narrative"},
                        {"node_id": "format", "node_type": "tool", "name": "Format Report"},
                        {"node_id": "distribute", "node_type": "tool", "name": "Send Report"},
                        {"node_id": "output", "node_type": "output", "name": "Confirmation"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "trigger", "target_node": "fetch"},
                        {"edge_id": "e2", "source_node": "fetch", "target_node": "compare"},
                        {"edge_id": "e3", "source_node": "compare", "target_node": "anomaly"},
                        {"edge_id": "e4", "source_node": "anomaly", "target_node": "narrative"},
                        {"edge_id": "e5", "source_node": "narrative", "target_node": "format"},
                        {"edge_id": "e6", "source_node": "format", "target_node": "distribute"},
                        {"edge_id": "e7", "source_node": "distribute", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.2,
                    "max_tokens": 2500,
                    "system_prompt": "You are a business intelligence analyst. Interpret metrics accurately, highlight important trends, and provide actionable insights."
                },
                tools=["sql_query", "fetch_kpis", "generate_charts", "send_email", "slack_notification"],
                sample_prompts=[
                    "Generate the weekly sales performance report",
                    "Create an executive dashboard for Q4 metrics",
                    "Alert me when revenue drops more than 10% from forecast"
                ],
                tags=["bi", "reporting", "kpi", "automated"]
            ),
            AgentTemplate(
                template_id="tpl_sql_assistant",
                name="SQL Query Assistant",
                description="Natural language to SQL converter that helps users query databases without writing SQL code. Uses code fragments for SQL validation and execution.",
                category="Analytics",
                agent_type="tool_calling",
                icon="bi-database",
                difficulty="intermediate",
                estimated_setup_time="15 minutes",
                uses_code_fragments=True,
                code_fragments=[
                    "db://code_fragments/sql_validator",
                    "db://code_fragments/query_executor",
                    "db://code_fragments/result_formatter"
                ],
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Natural Language Query"},
                        {"node_id": "schema", "node_type": "tool", "name": "Get Schema"},
                        {"node_id": "generate", "node_type": "llm", "name": "Generate SQL"},
                        {"node_id": "validate", "node_type": "code_fragment", "name": "Validate SQL",
                         "config": {"fragment_uri": "db://code_fragments/sql_validator"}},
                        {"node_id": "execute", "node_type": "code_fragment", "name": "Execute Query",
                         "config": {"fragment_uri": "db://code_fragments/query_executor"}},
                        {"node_id": "explain", "node_type": "llm", "name": "Explain Results"},
                        {"node_id": "output", "node_type": "output", "name": "Results"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "schema"},
                        {"edge_id": "e2", "source_node": "schema", "target_node": "generate"},
                        {"edge_id": "e3", "source_node": "generate", "target_node": "validate"},
                        {"edge_id": "e4", "source_node": "validate", "target_node": "execute"},
                        {"edge_id": "e5", "source_node": "execute", "target_node": "explain"},
                        {"edge_id": "e6", "source_node": "explain", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.1,
                    "max_tokens": 1500,
                    "system_prompt": "You are a SQL expert. Convert natural language queries to accurate, efficient SQL. Always explain your queries."
                },
                tools=["get_database_schema", "validate_sql", "execute_sql", "format_results"],
                sample_prompts=[
                    "Show me the top 10 customers by total purchase amount",
                    "How many orders were placed last month by region?",
                    "Find all products that haven't been ordered in 90 days"
                ],
                tags=["sql", "database", "natural-language", "code-fragment"],
                prerequisites=["Database connection configured", "Code fragments configured in Admin > Code Fragments"]
            ),
            
            # ============================================
            # DEVELOPMENT & CODING AGENTS
            # ============================================
            AgentTemplate(
                template_id="tpl_code_reviewer",
                name="Code Review Agent",
                description="Agent that reviews code for best practices, security issues, and optimization opportunities. Uses custom code fragments for static analysis.",
                category="Development",
                agent_type="tool_calling",
                icon="bi-code-slash",
                difficulty="intermediate",
                estimated_setup_time="10 minutes",
                uses_code_fragments=True,
                code_fragments=[
                    "db://code_fragments/code_analyzer",
                    "s3://devops-fragments/security_scanner.py",
                    "db://code_fragments/complexity_checker"
                ],
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Code Input"},
                        {"node_id": "parse", "node_type": "code_fragment", "name": "Parse Code",
                         "config": {"fragment_uri": "db://code_fragments/code_analyzer"}},
                        {"node_id": "security", "node_type": "code_fragment", "name": "Security Scan",
                         "config": {"fragment_uri": "s3://devops-fragments/security_scanner.py"}},
                        {"node_id": "style", "node_type": "tool", "name": "Style Check"},
                        {"node_id": "review", "node_type": "llm", "name": "AI Review"},
                        {"node_id": "output", "node_type": "output", "name": "Review Report"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "parse"},
                        {"edge_id": "e2", "source_node": "parse", "target_node": "security"},
                        {"edge_id": "e3", "source_node": "security", "target_node": "style"},
                        {"edge_id": "e4", "source_node": "style", "target_node": "review"},
                        {"edge_id": "e5", "source_node": "review", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.2,
                    "max_tokens": 3000,
                    "system_prompt": "You are a senior software engineer reviewing code. Focus on security, performance, maintainability, and best practices."
                },
                tools=["code_parser", "security_scanner", "linter", "complexity_analyzer"],
                sample_prompts=[
                    "Review this Python function for security issues",
                    "Check this API endpoint for best practices",
                    "Analyze this code for performance improvements"
                ],
                tags=["coding", "review", "security", "quality", "code-fragment"]
            ),
            AgentTemplate(
                template_id="tpl_code_assistant",
                name="Coding Assistant",
                description="Interactive coding assistant that helps write, debug, and explain code across multiple languages.",
                category="Development",
                agent_type="react",
                icon="bi-terminal",
                difficulty="intermediate",
                estimated_setup_time="5 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Coding Request"},
                        {"node_id": "understand", "node_type": "llm", "name": "Understand Task"},
                        {"node_id": "code", "node_type": "llm", "name": "Write/Fix Code"},
                        {"node_id": "test", "node_type": "tool", "name": "Run Tests"},
                        {"node_id": "explain", "node_type": "llm", "name": "Explain Code"},
                        {"node_id": "output", "node_type": "output", "name": "Code + Explanation"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "understand"},
                        {"edge_id": "e2", "source_node": "understand", "target_node": "code"},
                        {"edge_id": "e3", "source_node": "code", "target_node": "test"},
                        {"edge_id": "e4", "source_node": "test", "target_node": "explain"},
                        {"edge_id": "e5", "source_node": "explain", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.3,
                    "max_tokens": 4000,
                    "system_prompt": "You are an expert programmer. Write clean, efficient, and well-documented code. Explain your solutions clearly."
                },
                tools=["code_executor", "file_operations", "package_search"],
                sample_prompts=[
                    "Write a Python function to merge two sorted lists",
                    "Debug this JavaScript code that's causing an infinite loop",
                    "Explain how this recursive algorithm works"
                ],
                tags=["coding", "development", "debugging"]
            ),
            AgentTemplate(
                template_id="tpl_test_generator",
                name="Test Case Generator",
                description="Automatically generates comprehensive test cases for code, including unit tests, integration tests, and edge cases.",
                category="Development",
                agent_type="tool_calling",
                icon="bi-check2-square",
                difficulty="intermediate",
                estimated_setup_time="10 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Code to Test"},
                        {"node_id": "analyze", "node_type": "llm", "name": "Analyze Code"},
                        {"node_id": "identify", "node_type": "llm", "name": "Identify Test Cases"},
                        {"node_id": "generate", "node_type": "llm", "name": "Generate Tests"},
                        {"node_id": "validate", "node_type": "tool", "name": "Run Tests"},
                        {"node_id": "output", "node_type": "output", "name": "Test Suite"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "analyze"},
                        {"edge_id": "e2", "source_node": "analyze", "target_node": "identify"},
                        {"edge_id": "e3", "source_node": "identify", "target_node": "generate"},
                        {"edge_id": "e4", "source_node": "generate", "target_node": "validate"},
                        {"edge_id": "e5", "source_node": "validate", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.2,
                    "max_tokens": 4000,
                    "system_prompt": "You are a QA engineer. Generate comprehensive test cases covering happy paths, edge cases, error conditions, and boundary values."
                },
                tools=["code_parser", "test_runner", "coverage_analyzer"],
                sample_prompts=[
                    "Generate unit tests for this user authentication module",
                    "Create integration tests for the payment API",
                    "Add edge case tests for this date parsing function"
                ],
                tags=["testing", "qa", "automation", "quality"]
            ),
            AgentTemplate(
                template_id="tpl_api_documentation",
                name="API Documentation Generator",
                description="Automatically generates comprehensive API documentation from code, including examples and error handling.",
                category="Development",
                agent_type="tool_calling",
                icon="bi-file-earmark-code",
                difficulty="intermediate",
                estimated_setup_time="10 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "API Code/Spec"},
                        {"node_id": "parse", "node_type": "tool", "name": "Parse Endpoints"},
                        {"node_id": "analyze", "node_type": "llm", "name": "Analyze Parameters"},
                        {"node_id": "examples", "node_type": "llm", "name": "Generate Examples"},
                        {"node_id": "format", "node_type": "tool", "name": "Format Documentation"},
                        {"node_id": "output", "node_type": "output", "name": "API Docs"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "parse"},
                        {"edge_id": "e2", "source_node": "parse", "target_node": "analyze"},
                        {"edge_id": "e3", "source_node": "analyze", "target_node": "examples"},
                        {"edge_id": "e4", "source_node": "examples", "target_node": "format"},
                        {"edge_id": "e5", "source_node": "format", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.2,
                    "max_tokens": 4000,
                    "system_prompt": "You are a technical writer specializing in API documentation. Create clear, comprehensive docs with practical examples."
                },
                tools=["code_parser", "openapi_generator", "markdown_formatter"],
                sample_prompts=[
                    "Generate OpenAPI documentation for this REST API",
                    "Create documentation for these GraphQL endpoints",
                    "Document all error codes and their meanings"
                ],
                tags=["documentation", "api", "technical-writing"]
            ),
            
            # ============================================
            # CONTENT & WRITING AGENTS
            # ============================================
            AgentTemplate(
                template_id="tpl_content_writer",
                name="Content Writer",
                description="AI-powered content writer for blog posts, articles, and marketing copy with SEO optimization.",
                category="Content",
                agent_type="react",
                icon="bi-pencil-square",
                difficulty="beginner",
                estimated_setup_time="5 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Content Brief"},
                        {"node_id": "research", "node_type": "tool", "name": "Research Topic"},
                        {"node_id": "outline", "node_type": "llm", "name": "Create Outline"},
                        {"node_id": "write", "node_type": "llm", "name": "Write Content"},
                        {"node_id": "seo", "node_type": "tool", "name": "SEO Optimization"},
                        {"node_id": "output", "node_type": "output", "name": "Final Content"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "research"},
                        {"edge_id": "e2", "source_node": "research", "target_node": "outline"},
                        {"edge_id": "e3", "source_node": "outline", "target_node": "write"},
                        {"edge_id": "e4", "source_node": "write", "target_node": "seo"},
                        {"edge_id": "e5", "source_node": "seo", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.7,
                    "max_tokens": 4000,
                    "system_prompt": "You are a professional content writer. Create engaging, informative content that resonates with the target audience."
                },
                tools=["web_search", "keyword_analyzer", "readability_scorer"],
                sample_prompts=[
                    "Write a blog post about the benefits of remote work",
                    "Create marketing copy for a new fitness app",
                    "Write an article explaining blockchain to beginners"
                ],
                tags=["content", "writing", "seo", "marketing"]
            ),
            AgentTemplate(
                template_id="tpl_email_composer",
                name="Email Composer",
                description="Professional email composer that drafts contextually appropriate emails for various business scenarios.",
                category="Content",
                agent_type="conversational",
                icon="bi-envelope",
                difficulty="beginner",
                estimated_setup_time="3 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Email Request"},
                        {"node_id": "context", "node_type": "llm", "name": "Understand Context"},
                        {"node_id": "draft", "node_type": "llm", "name": "Draft Email"},
                        {"node_id": "refine", "node_type": "llm", "name": "Refine & Polish"},
                        {"node_id": "output", "node_type": "output", "name": "Final Email"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "context"},
                        {"edge_id": "e2", "source_node": "context", "target_node": "draft"},
                        {"edge_id": "e3", "source_node": "draft", "target_node": "refine"},
                        {"edge_id": "e4", "source_node": "refine", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "temperature": 0.5,
                    "max_tokens": 1000,
                    "system_prompt": "You are a professional email writer. Draft clear, concise, and appropriately toned emails for business communication."
                },
                tools=[],
                sample_prompts=[
                    "Write a follow-up email after a job interview",
                    "Draft a polite email declining a meeting request",
                    "Compose an apology email for a delayed shipment"
                ],
                tags=["email", "communication", "business"]
            ),
            AgentTemplate(
                template_id="tpl_social_media",
                name="Social Media Content Manager",
                description="Creates engaging social media content across platforms with hashtag optimization and scheduling.",
                category="Content",
                agent_type="react",
                icon="bi-share",
                difficulty="intermediate",
                estimated_setup_time="10 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Content Brief"},
                        {"node_id": "analyze", "node_type": "llm", "name": "Analyze Target"},
                        {"node_id": "create", "node_type": "llm", "name": "Create Posts"},
                        {"node_id": "hashtags", "node_type": "tool", "name": "Optimize Hashtags"},
                        {"node_id": "schedule", "node_type": "tool", "name": "Schedule Posts"},
                        {"node_id": "output", "node_type": "output", "name": "Content Calendar"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "analyze"},
                        {"edge_id": "e2", "source_node": "analyze", "target_node": "create"},
                        {"edge_id": "e3", "source_node": "create", "target_node": "hashtags"},
                        {"edge_id": "e4", "source_node": "hashtags", "target_node": "schedule"},
                        {"edge_id": "e5", "source_node": "schedule", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.8,
                    "max_tokens": 2000,
                    "system_prompt": "You are a social media expert. Create engaging, platform-appropriate content that drives engagement and follows best practices."
                },
                tools=["hashtag_analyzer", "social_scheduler", "image_generator", "trend_analyzer"],
                sample_prompts=[
                    "Create a week of Instagram posts for a coffee shop",
                    "Write 5 LinkedIn posts about leadership",
                    "Generate Twitter threads about AI trends"
                ],
                tags=["social-media", "marketing", "content"]
            ),
            
            # ============================================
            # BANKING & FINANCE AGENTS
            # ============================================
            AgentTemplate(
                template_id="tpl_loan_processor",
                name="Loan Application Processor",
                description="Automated loan processing agent that reviews applications, verifies documents, and makes preliminary decisions.",
                category="Banking",
                agent_type="plan_and_execute",
                icon="bi-bank",
                difficulty="advanced",
                estimated_setup_time="30 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Loan Application"},
                        {"node_id": "verify_docs", "node_type": "tool", "name": "Document Verification"},
                        {"node_id": "credit_check", "node_type": "tool", "name": "Credit Check"},
                        {"node_id": "income_verify", "node_type": "tool", "name": "Income Verification"},
                        {"node_id": "risk_assess", "node_type": "llm", "name": "Risk Assessment"},
                        {"node_id": "decision", "node_type": "llm", "name": "Preliminary Decision"},
                        {"node_id": "review", "node_type": "hitl", "name": "Officer Review"},
                        {"node_id": "output", "node_type": "output", "name": "Decision Notice"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "verify_docs"},
                        {"edge_id": "e2", "source_node": "verify_docs", "target_node": "credit_check"},
                        {"edge_id": "e3", "source_node": "credit_check", "target_node": "income_verify"},
                        {"edge_id": "e4", "source_node": "income_verify", "target_node": "risk_assess"},
                        {"edge_id": "e5", "source_node": "risk_assess", "target_node": "decision"},
                        {"edge_id": "e6", "source_node": "decision", "target_node": "review"},
                        {"edge_id": "e7", "source_node": "review", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.1,
                    "max_tokens": 2000,
                    "system_prompt": "You are a loan underwriting specialist. Assess risk carefully, follow regulatory guidelines, and make fair decisions."
                },
                tools=["document_ocr", "credit_bureau_api", "income_verification", "calculate_dti"],
                hitl_config={
                    "enabled": True,
                    "require_approval_for": ["high_risk", "large_amount", "exception"],
                    "timeout_minutes": 120
                },
                sample_prompts=[
                    "Process loan application #12345 for John Smith",
                    "Review mortgage application with income exceptions",
                    "Assess creditworthiness for small business loan"
                ],
                tags=["banking", "loans", "underwriting", "compliance"]
            ),
            AgentTemplate(
                template_id="tpl_fraud_detector",
                name="Transaction Fraud Detector",
                description="Real-time fraud detection agent that analyzes transactions for suspicious patterns using ML models and rule-based checks. Uses code fragments for scoring and velocity checks.",
                category="Banking",
                agent_type="tool_calling",
                icon="bi-shield-exclamation",
                difficulty="advanced",
                estimated_setup_time="25 minutes",
                uses_code_fragments=True,
                code_fragments=[
                    "s3://ml-models/fraud_ml_model.py",
                    "db://code_fragments/velocity_checker",
                    "db://code_fragments/rule_engine"
                ],
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Transaction Data"},
                        {"node_id": "rules", "node_type": "code_fragment", "name": "Rule-Based Check",
                         "config": {"fragment_uri": "db://code_fragments/rule_engine"}},
                        {"node_id": "ml_score", "node_type": "code_fragment", "name": "ML Risk Score",
                         "config": {"fragment_uri": "s3://ml-models/fraud_ml_model.py"}},
                        {"node_id": "velocity", "node_type": "code_fragment", "name": "Velocity Check",
                         "config": {"fragment_uri": "db://code_fragments/velocity_checker"}},
                        {"node_id": "analyze", "node_type": "llm", "name": "Pattern Analysis"},
                        {"node_id": "decision", "node_type": "condition", "name": "Decision Gate"},
                        {"node_id": "alert", "node_type": "tool", "name": "Generate Alert"},
                        {"node_id": "output", "node_type": "output", "name": "Decision"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "rules"},
                        {"edge_id": "e2", "source_node": "rules", "target_node": "ml_score"},
                        {"edge_id": "e3", "source_node": "ml_score", "target_node": "velocity"},
                        {"edge_id": "e4", "source_node": "velocity", "target_node": "analyze"},
                        {"edge_id": "e5", "source_node": "analyze", "target_node": "decision"},
                        {"edge_id": "e6", "source_node": "decision", "target_node": "alert", "condition": "suspicious"},
                        {"edge_id": "e7", "source_node": "decision", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.1,
                    "max_tokens": 1500,
                    "system_prompt": "You are a fraud analyst. Identify suspicious patterns while minimizing false positives. Explain your reasoning clearly."
                },
                tools=["transaction_rules_engine", "fraud_ml_model", "customer_profile", "alert_system"],
                sample_prompts=[
                    "Analyze this transaction for fraud risk",
                    "Review account activity for the past 24 hours",
                    "Investigate suspicious wire transfer pattern"
                ],
                tags=["fraud", "security", "banking", "ml", "code-fragment"]
            ),
            AgentTemplate(
                template_id="tpl_kyc_verification",
                name="KYC Verification Agent",
                description="Know Your Customer verification agent that validates identity documents and performs background checks.",
                category="Banking",
                agent_type="plan_and_execute",
                icon="bi-person-check",
                difficulty="advanced",
                estimated_setup_time="30 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Customer Documents"},
                        {"node_id": "extract", "node_type": "tool", "name": "Extract Document Data"},
                        {"node_id": "verify_id", "node_type": "tool", "name": "Verify Identity"},
                        {"node_id": "sanctions", "node_type": "tool", "name": "Sanctions Screening"},
                        {"node_id": "pep", "node_type": "tool", "name": "PEP Check"},
                        {"node_id": "assess", "node_type": "llm", "name": "Risk Assessment"},
                        {"node_id": "review", "node_type": "hitl", "name": "Compliance Review"},
                        {"node_id": "output", "node_type": "output", "name": "KYC Decision"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "extract"},
                        {"edge_id": "e2", "source_node": "extract", "target_node": "verify_id"},
                        {"edge_id": "e3", "source_node": "verify_id", "target_node": "sanctions"},
                        {"edge_id": "e4", "source_node": "sanctions", "target_node": "pep"},
                        {"edge_id": "e5", "source_node": "pep", "target_node": "assess"},
                        {"edge_id": "e6", "source_node": "assess", "target_node": "review"},
                        {"edge_id": "e7", "source_node": "review", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.1,
                    "max_tokens": 2000,
                    "system_prompt": "You are a KYC/AML compliance specialist. Verify identities thoroughly while following regulatory requirements."
                },
                tools=["document_ocr", "identity_verification", "sanctions_list", "pep_database", "adverse_media"],
                hitl_config={
                    "enabled": True,
                    "triggers": ["sanctions_match", "pep_match", "document_mismatch"],
                    "timeout_minutes": 240
                },
                sample_prompts=[
                    "Verify KYC documents for new customer account",
                    "Screen business customer against sanctions lists",
                    "Review enhanced due diligence case"
                ],
                tags=["kyc", "compliance", "aml", "banking"]
            ),
            
            # ============================================
            # AUTOMATION & WORKFLOW AGENTS
            # ============================================
            AgentTemplate(
                template_id="tpl_workflow_automation",
                name="Workflow Automation",
                description="Plan-and-execute agent for complex multi-step workflows with approval gates.",
                category="Automation",
                agent_type="plan_and_execute",
                icon="bi-diagram-3",
                difficulty="advanced",
                estimated_setup_time="25 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Workflow Request"},
                        {"node_id": "plan", "node_type": "llm", "name": "Create Plan"},
                        {"node_id": "approve_plan", "node_type": "hitl", "name": "Approve Plan"},
                        {"node_id": "execute", "node_type": "tool_executor", "name": "Execute Steps"},
                        {"node_id": "verify", "node_type": "llm", "name": "Verify Results"},
                        {"node_id": "output", "node_type": "output", "name": "Completion Report"}
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
            ),
            AgentTemplate(
                template_id="tpl_scheduler",
                name="Intelligent Scheduler",
                description="Smart scheduling agent that manages calendars, coordinates meetings, and handles scheduling conflicts.",
                category="Automation",
                agent_type="tool_calling",
                icon="bi-calendar-check",
                difficulty="intermediate",
                estimated_setup_time="15 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Scheduling Request"},
                        {"node_id": "parse", "node_type": "llm", "name": "Parse Request"},
                        {"node_id": "check", "node_type": "tool", "name": "Check Availability"},
                        {"node_id": "optimize", "node_type": "llm", "name": "Find Best Slot"},
                        {"node_id": "book", "node_type": "tool", "name": "Create Event"},
                        {"node_id": "notify", "node_type": "tool", "name": "Send Invites"},
                        {"node_id": "output", "node_type": "output", "name": "Confirmation"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "parse"},
                        {"edge_id": "e2", "source_node": "parse", "target_node": "check"},
                        {"edge_id": "e3", "source_node": "check", "target_node": "optimize"},
                        {"edge_id": "e4", "source_node": "optimize", "target_node": "book"},
                        {"edge_id": "e5", "source_node": "book", "target_node": "notify"},
                        {"edge_id": "e6", "source_node": "notify", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "temperature": 0.3,
                    "max_tokens": 1000,
                    "system_prompt": "You are a scheduling assistant. Find optimal meeting times considering all participants' availability and preferences."
                },
                tools=["calendar_api", "find_availability", "create_event", "send_email"],
                sample_prompts=[
                    "Schedule a 1-hour meeting with the marketing team next week",
                    "Find a time for a client call that works across time zones",
                    "Reschedule my afternoon meetings to tomorrow"
                ],
                tags=["scheduling", "calendar", "productivity"]
            ),
            AgentTemplate(
                template_id="tpl_document_processor",
                name="Document Processing Agent",
                description="Intelligent document processor that extracts information, classifies documents, and routes them appropriately.",
                category="Automation",
                agent_type="tool_calling",
                icon="bi-file-earmark-text",
                difficulty="intermediate",
                estimated_setup_time="15 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Document Upload"},
                        {"node_id": "classify", "node_type": "llm", "name": "Classify Document"},
                        {"node_id": "extract", "node_type": "tool", "name": "Extract Data"},
                        {"node_id": "validate", "node_type": "llm", "name": "Validate Data"},
                        {"node_id": "route", "node_type": "condition", "name": "Route Decision"},
                        {"node_id": "store", "node_type": "tool", "name": "Store Document"},
                        {"node_id": "output", "node_type": "output", "name": "Processing Complete"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "classify"},
                        {"edge_id": "e2", "source_node": "classify", "target_node": "extract"},
                        {"edge_id": "e3", "source_node": "extract", "target_node": "validate"},
                        {"edge_id": "e4", "source_node": "validate", "target_node": "route"},
                        {"edge_id": "e5", "source_node": "route", "target_node": "store"},
                        {"edge_id": "e6", "source_node": "store", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.1,
                    "max_tokens": 2000,
                    "system_prompt": "You are a document processing specialist. Accurately classify and extract information from documents."
                },
                tools=["document_ocr", "pdf_parser", "data_extractor", "document_storage"],
                sample_prompts=[
                    "Process this invoice and extract key fields",
                    "Classify and route incoming mail documents",
                    "Extract contract terms from legal documents"
                ],
                tags=["documents", "ocr", "extraction", "automation"]
            ),
            
            # ============================================
            # HEALTHCARE & MEDICAL AGENTS
            # ============================================
            AgentTemplate(
                template_id="tpl_medical_triage",
                name="Medical Triage Assistant",
                description="Healthcare triage agent that assesses symptoms, provides preliminary guidance, and routes to appropriate care.",
                category="Healthcare",
                agent_type="conversational",
                icon="bi-heart-pulse",
                difficulty="advanced",
                estimated_setup_time="30 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Symptom Report"},
                        {"node_id": "assess", "node_type": "llm", "name": "Symptom Assessment"},
                        {"node_id": "history", "node_type": "tool", "name": "Get Patient History"},
                        {"node_id": "analyze", "node_type": "llm", "name": "Clinical Analysis"},
                        {"node_id": "urgency", "node_type": "llm", "name": "Determine Urgency"},
                        {"node_id": "recommend", "node_type": "llm", "name": "Care Recommendation"},
                        {"node_id": "escalate", "node_type": "hitl", "name": "Clinical Review"},
                        {"node_id": "output", "node_type": "output", "name": "Triage Decision"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "assess"},
                        {"edge_id": "e2", "source_node": "assess", "target_node": "history"},
                        {"edge_id": "e3", "source_node": "history", "target_node": "analyze"},
                        {"edge_id": "e4", "source_node": "analyze", "target_node": "urgency"},
                        {"edge_id": "e5", "source_node": "urgency", "target_node": "recommend"},
                        {"edge_id": "e6", "source_node": "recommend", "target_node": "escalate"},
                        {"edge_id": "e7", "source_node": "escalate", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.1,
                    "max_tokens": 2000,
                    "system_prompt": "You are a medical triage assistant. Assess symptoms carefully, consider patient history, and recommend appropriate care levels. Always err on the side of caution and recommend professional medical evaluation when uncertain."
                },
                tools=["patient_history", "symptom_checker", "care_finder", "appointment_scheduler"],
                hitl_config={
                    "enabled": True,
                    "triggers": ["emergency_symptoms", "unclear_diagnosis", "high_risk_patient"],
                    "timeout_minutes": 15
                },
                sample_prompts=[
                    "I've had a headache for 3 days and feel nauseous",
                    "My child has a fever of 102F and a rash",
                    "I'm experiencing chest discomfort after exercise"
                ],
                tags=["healthcare", "triage", "medical", "hitl"],
                prerequisites=["Medical knowledge base configured", "Clinical review team available"]
            ),
            AgentTemplate(
                template_id="tpl_appointment_scheduler_medical",
                name="Medical Appointment Scheduler",
                description="Healthcare scheduling agent that books appointments, manages referrals, and handles insurance verification.",
                category="Healthcare",
                agent_type="tool_calling",
                icon="bi-calendar-plus",
                difficulty="intermediate",
                estimated_setup_time="20 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Appointment Request"},
                        {"node_id": "verify", "node_type": "tool", "name": "Verify Insurance"},
                        {"node_id": "find", "node_type": "tool", "name": "Find Providers"},
                        {"node_id": "match", "node_type": "llm", "name": "Match Provider"},
                        {"node_id": "schedule", "node_type": "tool", "name": "Book Appointment"},
                        {"node_id": "confirm", "node_type": "tool", "name": "Send Confirmation"},
                        {"node_id": "output", "node_type": "output", "name": "Appointment Details"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "verify"},
                        {"edge_id": "e2", "source_node": "verify", "target_node": "find"},
                        {"edge_id": "e3", "source_node": "find", "target_node": "match"},
                        {"edge_id": "e4", "source_node": "match", "target_node": "schedule"},
                        {"edge_id": "e5", "source_node": "schedule", "target_node": "confirm"},
                        {"edge_id": "e6", "source_node": "confirm", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "temperature": 0.3,
                    "max_tokens": 1000,
                    "system_prompt": "You are a medical scheduling assistant. Help patients find appropriate providers and convenient appointment times."
                },
                tools=["insurance_verification", "provider_search", "appointment_booking", "notification_sender"],
                sample_prompts=[
                    "I need to see a dermatologist next week",
                    "Schedule a follow-up with my cardiologist",
                    "Book a physical exam with my primary care doctor"
                ],
                tags=["healthcare", "scheduling", "appointments"]
            ),
            
            # ============================================
            # LEGAL & COMPLIANCE AGENTS
            # ============================================
            AgentTemplate(
                template_id="tpl_contract_reviewer",
                name="Contract Review Agent",
                description="Legal contract reviewer that identifies key terms, risks, and deviations from standard templates.",
                category="Legal",
                agent_type="tool_calling",
                icon="bi-file-earmark-ruled",
                difficulty="advanced",
                estimated_setup_time="25 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Contract Document"},
                        {"node_id": "extract", "node_type": "tool", "name": "Extract Clauses"},
                        {"node_id": "compare", "node_type": "tool", "name": "Compare to Standard"},
                        {"node_id": "analyze", "node_type": "llm", "name": "Risk Analysis"},
                        {"node_id": "flag", "node_type": "llm", "name": "Flag Issues"},
                        {"node_id": "review", "node_type": "hitl", "name": "Legal Review"},
                        {"node_id": "output", "node_type": "output", "name": "Review Report"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "extract"},
                        {"edge_id": "e2", "source_node": "extract", "target_node": "compare"},
                        {"edge_id": "e3", "source_node": "compare", "target_node": "analyze"},
                        {"edge_id": "e4", "source_node": "analyze", "target_node": "flag"},
                        {"edge_id": "e5", "source_node": "flag", "target_node": "review"},
                        {"edge_id": "e6", "source_node": "review", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.1,
                    "max_tokens": 4000,
                    "system_prompt": "You are a contract review specialist. Identify key terms, risks, obligations, and deviations from standard language. Flag potential issues clearly."
                },
                tools=["document_parser", "clause_extractor", "standard_template_compare", "risk_scorer"],
                hitl_config={
                    "enabled": True,
                    "triggers": ["high_risk_clause", "unusual_terms", "liability_concerns"],
                    "timeout_minutes": 480
                },
                sample_prompts=[
                    "Review this vendor agreement for potential risks",
                    "Compare this NDA to our standard template",
                    "Identify problematic clauses in this service contract"
                ],
                tags=["legal", "contracts", "compliance", "review"]
            ),
            AgentTemplate(
                template_id="tpl_compliance_monitor",
                name="Compliance Monitoring Agent",
                description="Regulatory compliance agent that monitors policies, flags violations, and tracks remediation.",
                category="Legal",
                agent_type="tool_calling",
                icon="bi-shield-check",
                difficulty="advanced",
                estimated_setup_time="30 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Compliance Check"},
                        {"node_id": "gather", "node_type": "tool", "name": "Gather Evidence"},
                        {"node_id": "evaluate", "node_type": "llm", "name": "Evaluate Compliance"},
                        {"node_id": "identify", "node_type": "llm", "name": "Identify Gaps"},
                        {"node_id": "recommend", "node_type": "llm", "name": "Remediation Plan"},
                        {"node_id": "report", "node_type": "tool", "name": "Generate Report"},
                        {"node_id": "output", "node_type": "output", "name": "Compliance Report"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "gather"},
                        {"edge_id": "e2", "source_node": "gather", "target_node": "evaluate"},
                        {"edge_id": "e3", "source_node": "evaluate", "target_node": "identify"},
                        {"edge_id": "e4", "source_node": "identify", "target_node": "recommend"},
                        {"edge_id": "e5", "source_node": "recommend", "target_node": "report"},
                        {"edge_id": "e6", "source_node": "report", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.1,
                    "max_tokens": 3000,
                    "system_prompt": "You are a compliance specialist. Evaluate adherence to regulations, identify gaps, and recommend remediation actions."
                },
                tools=["policy_database", "audit_log_analyzer", "compliance_tracker", "report_generator"],
                sample_prompts=[
                    "Check GDPR compliance for our data processing activities",
                    "Review SOX compliance for financial reporting",
                    "Audit PCI-DSS controls for payment processing"
                ],
                tags=["compliance", "regulatory", "audit", "governance"]
            ),
            
            # ============================================
            # HR & RECRUITMENT AGENTS
            # ============================================
            AgentTemplate(
                template_id="tpl_recruiter",
                name="Recruitment Assistant",
                description="AI recruiter that screens resumes, schedules interviews, and manages candidate communication.",
                category="HR",
                agent_type="conversational",
                icon="bi-people",
                difficulty="intermediate",
                estimated_setup_time="20 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Candidate Application"},
                        {"node_id": "parse", "node_type": "tool", "name": "Parse Resume"},
                        {"node_id": "match", "node_type": "llm", "name": "Job Matching"},
                        {"node_id": "screen", "node_type": "llm", "name": "Initial Screening"},
                        {"node_id": "schedule", "node_type": "tool", "name": "Schedule Interview"},
                        {"node_id": "notify", "node_type": "tool", "name": "Notify Candidate"},
                        {"node_id": "output", "node_type": "output", "name": "Screening Result"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "parse"},
                        {"edge_id": "e2", "source_node": "parse", "target_node": "match"},
                        {"edge_id": "e3", "source_node": "match", "target_node": "screen"},
                        {"edge_id": "e4", "source_node": "screen", "target_node": "schedule"},
                        {"edge_id": "e5", "source_node": "schedule", "target_node": "notify"},
                        {"edge_id": "e6", "source_node": "notify", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.3,
                    "max_tokens": 2000,
                    "system_prompt": "You are a recruitment specialist. Screen candidates objectively based on job requirements. Be professional and respectful in all communications."
                },
                tools=["resume_parser", "job_matcher", "calendar_api", "email_sender", "ats_integration"],
                sample_prompts=[
                    "Screen this resume for the Senior Developer position",
                    "Schedule a phone interview with the top candidate",
                    "Send a rejection email to unqualified applicants"
                ],
                tags=["hr", "recruitment", "hiring", "screening"]
            ),
            AgentTemplate(
                template_id="tpl_hr_assistant",
                name="HR Help Desk",
                description="Employee self-service agent for HR inquiries, policy questions, and benefits information.",
                category="HR",
                agent_type="conversational",
                icon="bi-question-circle",
                difficulty="intermediate",
                estimated_setup_time="15 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Employee Query"},
                        {"node_id": "classify", "node_type": "llm", "name": "Classify Query"},
                        {"node_id": "search", "node_type": "tool", "name": "Search Policies"},
                        {"node_id": "respond", "node_type": "llm", "name": "Generate Response"},
                        {"node_id": "escalate", "node_type": "hitl", "name": "HR Escalation"},
                        {"node_id": "output", "node_type": "output", "name": "Response"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "classify"},
                        {"edge_id": "e2", "source_node": "classify", "target_node": "search"},
                        {"edge_id": "e3", "source_node": "search", "target_node": "respond"},
                        {"edge_id": "e4", "source_node": "respond", "target_node": "output"},
                        {"edge_id": "e5", "source_node": "classify", "target_node": "escalate", "condition": "sensitive"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "temperature": 0.3,
                    "max_tokens": 1000,
                    "system_prompt": "You are an HR assistant. Answer employee questions about policies, benefits, and procedures accurately. Escalate sensitive matters to HR specialists."
                },
                tools=["policy_search", "benefits_lookup", "pto_calculator", "create_hr_ticket"],
                hitl_config={
                    "enabled": True,
                    "triggers": ["discrimination", "harassment", "legal_concern", "sensitive_data"],
                    "timeout_minutes": 60
                },
                sample_prompts=[
                    "How many vacation days do I have left?",
                    "What's the process for requesting parental leave?",
                    "How do I enroll in the 401k plan?"
                ],
                tags=["hr", "employee-service", "policies", "benefits"]
            ),
            
            # ============================================
            # EDUCATION & TRAINING AGENTS
            # ============================================
            AgentTemplate(
                template_id="tpl_tutor",
                name="AI Tutor",
                description="Personalized learning assistant that adapts to student level and provides interactive tutoring.",
                category="Education",
                agent_type="conversational",
                icon="bi-mortarboard",
                difficulty="intermediate",
                estimated_setup_time="10 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Student Question"},
                        {"node_id": "assess", "node_type": "llm", "name": "Assess Level"},
                        {"node_id": "teach", "node_type": "llm", "name": "Explain Concept"},
                        {"node_id": "quiz", "node_type": "llm", "name": "Check Understanding"},
                        {"node_id": "adapt", "node_type": "llm", "name": "Adapt Teaching"},
                        {"node_id": "output", "node_type": "output", "name": "Learning Response"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "assess"},
                        {"edge_id": "e2", "source_node": "assess", "target_node": "teach"},
                        {"edge_id": "e3", "source_node": "teach", "target_node": "quiz"},
                        {"edge_id": "e4", "source_node": "quiz", "target_node": "adapt"},
                        {"edge_id": "e5", "source_node": "adapt", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.6,
                    "max_tokens": 2000,
                    "system_prompt": "You are a patient and encouraging tutor. Adapt explanations to the student's level, use examples, and check understanding. Celebrate progress."
                },
                tools=["knowledge_base", "quiz_generator", "progress_tracker"],
                sample_prompts=[
                    "Explain photosynthesis to me",
                    "Help me understand quadratic equations",
                    "Quiz me on World War II history"
                ],
                tags=["education", "tutoring", "learning", "adaptive"]
            ),
            AgentTemplate(
                template_id="tpl_course_creator",
                name="Course Content Creator",
                description="Educational content creator that generates lesson plans, quizzes, and learning materials.",
                category="Education",
                agent_type="tool_calling",
                icon="bi-journal-richtext",
                difficulty="intermediate",
                estimated_setup_time="15 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Course Brief"},
                        {"node_id": "outline", "node_type": "llm", "name": "Create Outline"},
                        {"node_id": "content", "node_type": "llm", "name": "Generate Content"},
                        {"node_id": "quiz", "node_type": "llm", "name": "Create Assessments"},
                        {"node_id": "format", "node_type": "tool", "name": "Format Materials"},
                        {"node_id": "output", "node_type": "output", "name": "Course Package"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "outline"},
                        {"edge_id": "e2", "source_node": "outline", "target_node": "content"},
                        {"edge_id": "e3", "source_node": "content", "target_node": "quiz"},
                        {"edge_id": "e4", "source_node": "quiz", "target_node": "format"},
                        {"edge_id": "e5", "source_node": "format", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.5,
                    "max_tokens": 4000,
                    "system_prompt": "You are an instructional designer. Create engaging, well-structured educational content with clear learning objectives and assessments."
                },
                tools=["content_formatter", "quiz_builder", "media_search", "lms_integration"],
                sample_prompts=[
                    "Create a 4-week Python programming course for beginners",
                    "Design a leadership training module",
                    "Build a customer service certification program"
                ],
                tags=["education", "content-creation", "e-learning"]
            ),
            
            # ============================================
            # CODE FRAGMENT EXAMPLES
            # ============================================
            AgentTemplate(
                template_id="tpl_data_pipeline_agent",
                name="Data Pipeline Agent",
                description="Advanced data processing agent using custom code fragments for ETL operations, data validation, and transformation.",
                category="Analytics",
                agent_type="tool_calling",
                icon="bi-database-gear",
                difficulty="advanced",
                estimated_setup_time="20 minutes",
                uses_code_fragments=True,
                code_fragments=[
                    "db://code_fragments/pandas_processor",
                    "db://code_fragments/data_validator",
                    "file:///opt/abhikarta/fragments/db_connector.py"
                ],
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Data Source"},
                        {"node_id": "extract", "node_type": "code_fragment", "name": "Extract Data",
                         "config": {"fragment_uri": "db://code_fragments/pandas_processor"}},
                        {"node_id": "validate", "node_type": "code_fragment", "name": "Validate Schema",
                         "config": {"fragment_uri": "db://code_fragments/data_validator"}},
                        {"node_id": "transform", "node_type": "llm", "name": "Plan Transformations"},
                        {"node_id": "execute", "node_type": "code_fragment", "name": "Execute Transform",
                         "config": {"fragment_uri": "file:///opt/abhikarta/fragments/db_connector.py"}},
                        {"node_id": "output", "node_type": "output", "name": "Processed Data"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "extract"},
                        {"edge_id": "e2", "source_node": "extract", "target_node": "validate"},
                        {"edge_id": "e3", "source_node": "validate", "target_node": "transform"},
                        {"edge_id": "e4", "source_node": "transform", "target_node": "execute"},
                        {"edge_id": "e5", "source_node": "execute", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "anthropic",
                    "model": "claude-sonnet-4-20250514",
                    "temperature": 0.3,
                    "max_tokens": 2000,
                    "system_prompt": "You are a data engineering expert. Analyze data requirements and plan optimal transformations."
                },
                tools=["database_query", "file_reader", "schema_validator"],
                sample_prompts=[
                    "Load customer data from PostgreSQL and calculate monthly aggregates",
                    "Transform CSV sales data and validate against schema",
                    "Extract and clean web scraping results"
                ],
                tags=["data", "etl", "pipeline", "code-fragment", "advanced"],
                prerequisites=["Database connections configured", "Code fragments configured in Admin > Code Fragments"]
            ),
            AgentTemplate(
                template_id="tpl_pdf_processor_agent",
                name="PDF Processing Agent",
                description="Intelligent PDF processing agent using OCR and custom extraction code fragments for document analysis.",
                category="Document Processing",
                agent_type="react",
                icon="bi-file-pdf",
                difficulty="intermediate",
                estimated_setup_time="15 minutes",
                uses_code_fragments=True,
                code_fragments=[
                    "db://code_fragments/ocr_extractor",
                    "s3://abhikarta-fragments/pdf_parser.py",
                    "db://code_fragments/table_extractor"
                ],
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "PDF Document"},
                        {"node_id": "ocr", "node_type": "code_fragment", "name": "OCR Extract",
                         "config": {"fragment_uri": "db://code_fragments/ocr_extractor"}},
                        {"node_id": "tables", "node_type": "code_fragment", "name": "Extract Tables",
                         "config": {"fragment_uri": "db://code_fragments/table_extractor"}},
                        {"node_id": "analyze", "node_type": "llm", "name": "Analyze Content"},
                        {"node_id": "structure", "node_type": "llm", "name": "Structure Output"},
                        {"node_id": "output", "node_type": "output", "name": "Extracted Data"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "ocr"},
                        {"edge_id": "e2", "source_node": "ocr", "target_node": "tables"},
                        {"edge_id": "e3", "source_node": "tables", "target_node": "analyze"},
                        {"edge_id": "e4", "source_node": "analyze", "target_node": "structure"},
                        {"edge_id": "e5", "source_node": "structure", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.2,
                    "max_tokens": 3000,
                    "system_prompt": "You are a document analysis expert. Extract and structure information from PDF documents accurately."
                },
                tools=["file_upload", "json_formatter"],
                sample_prompts=[
                    "Extract all financial data from this annual report",
                    "Parse the invoice and extract line items",
                    "Analyze this contract and identify key terms"
                ],
                tags=["pdf", "ocr", "extraction", "code-fragment"],
                prerequisites=["OCR library installed", "Code fragments configured in Admin > Code Fragments"]
            ),
            AgentTemplate(
                template_id="tpl_api_integration_agent",
                name="API Integration Agent",
                description="Connects to external APIs using custom code fragments for authentication, data fetching, and transformation.",
                category="Integration",
                agent_type="tool_calling",
                icon="bi-cloud-arrow-down",
                difficulty="intermediate",
                estimated_setup_time="15 minutes",
                uses_code_fragments=True,
                code_fragments=[
                    "db://code_fragments/oauth_handler",
                    "s3://abhikarta-fragments/api_client.py",
                    "db://code_fragments/response_parser"
                ],
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "API Request"},
                        {"node_id": "auth", "node_type": "code_fragment", "name": "Authenticate",
                         "config": {"fragment_uri": "db://code_fragments/oauth_handler"}},
                        {"node_id": "fetch", "node_type": "code_fragment", "name": "Fetch Data",
                         "config": {"fragment_uri": "s3://abhikarta-fragments/api_client.py"}},
                        {"node_id": "parse", "node_type": "code_fragment", "name": "Parse Response",
                         "config": {"fragment_uri": "db://code_fragments/response_parser"}},
                        {"node_id": "analyze", "node_type": "llm", "name": "Analyze Results"},
                        {"node_id": "output", "node_type": "output", "name": "Integrated Data"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "auth"},
                        {"edge_id": "e2", "source_node": "auth", "target_node": "fetch"},
                        {"edge_id": "e3", "source_node": "fetch", "target_node": "parse"},
                        {"edge_id": "e4", "source_node": "parse", "target_node": "analyze"},
                        {"edge_id": "e5", "source_node": "analyze", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "temperature": 0.3,
                    "max_tokens": 2000,
                    "system_prompt": "You are an API integration specialist. Help fetch and transform data from external APIs."
                },
                tools=["http_client", "json_parser", "webhook_handler"],
                sample_prompts=[
                    "Fetch customer data from Salesforce API",
                    "Integrate with Stripe to get recent transactions",
                    "Pull analytics data from Google Analytics API"
                ],
                tags=["api", "integration", "rest", "code-fragment"],
                prerequisites=["API credentials configured", "Code fragments configured in Admin > Code Fragments"]
            ),
            AgentTemplate(
                template_id="tpl_ml_inference_agent",
                name="ML Inference Agent",
                description="Machine learning inference agent that uses custom code fragments to run predictions on trained models.",
                category="Analytics",
                agent_type="react",
                icon="bi-cpu",
                difficulty="advanced",
                estimated_setup_time="30 minutes",
                uses_code_fragments=True,
                code_fragments=[
                    "s3://ml-models/model_loader.py",
                    "db://code_fragments/feature_processor",
                    "s3://ml-models/prediction_engine.py"
                ],
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Inference Request"},
                        {"node_id": "preprocess", "node_type": "code_fragment", "name": "Preprocess Features",
                         "config": {"fragment_uri": "db://code_fragments/feature_processor"}},
                        {"node_id": "predict", "node_type": "code_fragment", "name": "Run Prediction",
                         "config": {"fragment_uri": "s3://ml-models/prediction_engine.py"}},
                        {"node_id": "interpret", "node_type": "llm", "name": "Interpret Results"},
                        {"node_id": "output", "node_type": "output", "name": "Prediction Output"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "preprocess"},
                        {"edge_id": "e2", "source_node": "preprocess", "target_node": "predict"},
                        {"edge_id": "e3", "source_node": "predict", "target_node": "interpret"},
                        {"edge_id": "e4", "source_node": "interpret", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "anthropic",
                    "model": "claude-sonnet-4-20250514",
                    "temperature": 0.2,
                    "max_tokens": 2000,
                    "system_prompt": "You are an ML engineer. Help interpret model predictions and explain results clearly."
                },
                tools=["model_registry", "feature_store"],
                sample_prompts=[
                    "Predict customer churn probability for user ID 12345",
                    "Run fraud detection model on this transaction",
                    "Get product recommendations for this customer profile"
                ],
                tags=["ml", "inference", "prediction", "code-fragment", "advanced"],
                prerequisites=["ML models deployed", "Code fragments configured in Admin > Code Fragments"]
            ),
            AgentTemplate(
                template_id="tpl_web_scraper_agent",
                name="Web Scraping Agent",
                description="Intelligent web scraping agent using custom code fragments for HTML parsing and data extraction.",
                category="Data Collection",
                agent_type="tool_calling",
                icon="bi-globe2",
                difficulty="intermediate",
                estimated_setup_time="15 minutes",
                uses_code_fragments=True,
                code_fragments=[
                    "db://code_fragments/url_fetcher",
                    "file:///opt/abhikarta/fragments/html_parser.py",
                    "db://code_fragments/content_extractor"
                ],
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Scrape Request"},
                        {"node_id": "fetch", "node_type": "code_fragment", "name": "Fetch Page",
                         "config": {"fragment_uri": "db://code_fragments/url_fetcher"}},
                        {"node_id": "parse", "node_type": "code_fragment", "name": "Parse HTML",
                         "config": {"fragment_uri": "file:///opt/abhikarta/fragments/html_parser.py"}},
                        {"node_id": "extract", "node_type": "llm", "name": "Extract Data"},
                        {"node_id": "structure", "node_type": "transform", "name": "Structure Output"},
                        {"node_id": "output", "node_type": "output", "name": "Scraped Data"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "fetch"},
                        {"edge_id": "e2", "source_node": "fetch", "target_node": "parse"},
                        {"edge_id": "e3", "source_node": "parse", "target_node": "extract"},
                        {"edge_id": "e4", "source_node": "extract", "target_node": "structure"},
                        {"edge_id": "e5", "source_node": "structure", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "temperature": 0.2,
                    "max_tokens": 2000,
                    "system_prompt": "You are a web scraping expert. Extract structured data from web pages accurately."
                },
                tools=["http_client", "json_formatter"],
                sample_prompts=[
                    "Scrape product prices from this e-commerce page",
                    "Extract news articles from this website",
                    "Get company information from LinkedIn profiles"
                ],
                tags=["scraping", "web", "extraction", "code-fragment"],
                prerequisites=["Code fragments configured in Admin > Code Fragments"]
            ),
            AgentTemplate(
                template_id="tpl_report_generator_agent",
                name="Report Generation Agent",
                description="Automated report generation agent using code fragments for data visualization and document formatting.",
                category="Analytics",
                agent_type="tool_calling",
                icon="bi-file-earmark-bar-graph",
                difficulty="intermediate",
                estimated_setup_time="15 minutes",
                uses_code_fragments=True,
                code_fragments=[
                    "db://code_fragments/chart_generator",
                    "s3://abhikarta-fragments/report_formatter.py",
                    "db://code_fragments/pdf_creator"
                ],
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Report Request"},
                        {"node_id": "fetch", "node_type": "tool", "name": "Fetch Data"},
                        {"node_id": "analyze", "node_type": "llm", "name": "Analyze Data"},
                        {"node_id": "charts", "node_type": "code_fragment", "name": "Generate Charts",
                         "config": {"fragment_uri": "db://code_fragments/chart_generator"}},
                        {"node_id": "format", "node_type": "code_fragment", "name": "Format Report",
                         "config": {"fragment_uri": "s3://abhikarta-fragments/report_formatter.py"}},
                        {"node_id": "output", "node_type": "output", "name": "Final Report"}
                    ],
                    "edges": [
                        {"edge_id": "e1", "source_node": "input", "target_node": "fetch"},
                        {"edge_id": "e2", "source_node": "fetch", "target_node": "analyze"},
                        {"edge_id": "e3", "source_node": "analyze", "target_node": "charts"},
                        {"edge_id": "e4", "source_node": "charts", "target_node": "format"},
                        {"edge_id": "e5", "source_node": "format", "target_node": "output"}
                    ]
                },
                llm_config={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.4,
                    "max_tokens": 3000,
                    "system_prompt": "You are a business analyst. Create insightful reports with clear visualizations."
                },
                tools=["database_query", "file_writer"],
                sample_prompts=[
                    "Generate monthly sales report with trends analysis",
                    "Create customer satisfaction dashboard report",
                    "Build quarterly financial summary with charts"
                ],
                tags=["reporting", "charts", "analytics", "code-fragment"],
                prerequisites=["Data sources configured", "Code fragments configured in Admin > Code Fragments"]
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
    
    def get_code_fragment_templates(self) -> List[AgentTemplate]:
        """Get templates that use code fragments."""
        return [t for t in self._templates.values() if t.uses_code_fragments]
    
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
    
    def get_code_fragment_templates(self) -> List[AgentTemplate]:
        """Get templates that use code fragments."""
        return [t for t in self._templates.values() if t.uses_code_fragments]
