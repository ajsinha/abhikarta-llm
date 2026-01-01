"""
Agent Template Manager - Template library management.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Version: 1.4.6
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
    difficulty: str = "intermediate"
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
    """Manages agent templates including built-in and custom templates."""
    
    def __init__(self, db_facade=None):
        """Initialize with optional database facade."""
        self.db_facade = db_facade
        self._templates: Dict[str, AgentTemplate] = {}
        self._init_builtin_templates()
        logger.info("AgentTemplateManager initialized")
    
    def _init_builtin_templates(self):
        """Initialize built-in system templates - 2 per agent type."""
        builtin = self._get_react_templates() + \
                  self._get_conversational_templates() + \
                  self._get_tool_calling_templates() + \
                  self._get_plan_execute_templates() + \
                  self._get_retrieval_templates() + \
                  self._get_custom_templates()
        
        for template in builtin:
            from abhikarta.utils.helpers import get_timestamp
            template.created_at = get_timestamp()
            self._templates[template.template_id] = template
    
    def _get_react_templates(self) -> List[AgentTemplate]:
        """ReAct agent templates - 2 templates."""
        return [
            # Template 1: Basic ReAct - Sequential reasoning
            AgentTemplate(
                template_id="tpl_react_sequential",
                name="ReAct Sequential Reasoner",
                description="A ReAct agent that uses thought-action-observation loop to solve tasks sequentially. Demonstrates basic reasoning flow.",
                category="General",
                agent_type="react",
                icon="bi-arrow-repeat",
                difficulty="beginner",
                estimated_setup_time="5 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "User Query",
                         "position": {"x": 100, "y": 200}, "config": {}},
                        {"node_id": "think", "node_type": "llm", "name": "Think",
                         "position": {"x": 300, "y": 200}, 
                         "config": {"system_prompt": "Analyze the query and decide what action to take."}},
                        {"node_id": "act", "node_type": "tool", "name": "Act",
                         "position": {"x": 500, "y": 200}, "config": {}},
                        {"node_id": "observe", "node_type": "transform", "name": "Observe",
                         "position": {"x": 700, "y": 200}, "config": {"transform_type": "passthrough"}},
                        {"node_id": "output", "node_type": "output", "name": "Response",
                         "position": {"x": 900, "y": 200}, "config": {}}
                    ],
                    "edges": [
                        {"source": "input", "target": "think"},
                        {"source": "think", "target": "act"},
                        {"source": "act", "target": "observe"},
                        {"source": "observe", "target": "output"}
                    ]
                },
                llm_config={"provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "temperature": 0.7},
                tools=["web_search", "calculator"],
                sample_prompts=["Research the latest trends in renewable energy", "Calculate compound interest on $10000 at 5% for 10 years"],
                tags=["react", "reasoning", "sequential", "beginner"],
                prerequisites=["LLM provider configured"]
            ),
            
            # Template 2: ReAct with Parallel Tool Execution
            AgentTemplate(
                template_id="tpl_react_parallel",
                name="ReAct Parallel Executor",
                description="A ReAct agent that can execute multiple tools in parallel, then synthesize results. Demonstrates parallel execution pattern.",
                category="General",
                agent_type="react",
                icon="bi-diagram-3",
                difficulty="intermediate",
                estimated_setup_time="10 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "User Query",
                         "position": {"x": 100, "y": 250}, "config": {}},
                        {"node_id": "planner", "node_type": "llm", "name": "Plan Actions",
                         "position": {"x": 300, "y": 250}, 
                         "config": {"system_prompt": "Analyze query and plan parallel actions."}},
                        {"node_id": "split", "node_type": "split", "name": "Split Tasks",
                         "position": {"x": 500, "y": 250}, "config": {"split_type": "items"}},
                        {"node_id": "tool1", "node_type": "tool", "name": "Tool A",
                         "position": {"x": 700, "y": 150}, "config": {}},
                        {"node_id": "tool2", "node_type": "tool", "name": "Tool B",
                         "position": {"x": 700, "y": 350}, "config": {}},
                        {"node_id": "join", "node_type": "join", "name": "Aggregate",
                         "position": {"x": 900, "y": 250}, "config": {"join_type": "all"}},
                        {"node_id": "synthesize", "node_type": "llm", "name": "Synthesize",
                         "position": {"x": 1100, "y": 250}, 
                         "config": {"system_prompt": "Combine results into cohesive response."}},
                        {"node_id": "output", "node_type": "output", "name": "Response",
                         "position": {"x": 1300, "y": 250}, "config": {}}
                    ],
                    "edges": [
                        {"source": "input", "target": "planner"},
                        {"source": "planner", "target": "split"},
                        {"source": "split", "target": "tool1"},
                        {"source": "split", "target": "tool2"},
                        {"source": "tool1", "target": "join"},
                        {"source": "tool2", "target": "join"},
                        {"source": "join", "target": "synthesize"},
                        {"source": "synthesize", "target": "output"}
                    ]
                },
                llm_config={"provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "temperature": 0.5},
                tools=["web_search", "code_executor", "file_reader"],
                sample_prompts=["Compare pricing from multiple sources", "Gather data from different APIs and summarize"],
                tags=["react", "parallel", "multi-tool", "intermediate"],
                prerequisites=["LLM provider configured", "Multiple tools available"]
            )
        ]
    
    def _get_conversational_templates(self) -> List[AgentTemplate]:
        """Conversational agent templates - 2 templates."""
        return [
            # Template 1: Basic Conversational Agent
            AgentTemplate(
                template_id="tpl_conversational_basic",
                name="Basic Conversational Agent",
                description="A simple conversational agent with memory. Maintains context across multiple turns.",
                category="General",
                agent_type="conversational",
                icon="bi-chat-dots",
                difficulty="beginner",
                estimated_setup_time="5 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "User Message",
                         "position": {"x": 100, "y": 200}, "config": {}},
                        {"node_id": "memory", "node_type": "transform", "name": "Load Context",
                         "position": {"x": 300, "y": 200}, 
                         "config": {"transform_type": "passthrough"}},
                        {"node_id": "llm", "node_type": "llm", "name": "Generate Response",
                         "position": {"x": 500, "y": 200},
                         "config": {"system_prompt": "You are a helpful assistant. Use conversation history for context."}},
                        {"node_id": "output", "node_type": "output", "name": "Assistant Response",
                         "position": {"x": 700, "y": 200}, "config": {}}
                    ],
                    "edges": [
                        {"source": "input", "target": "memory"},
                        {"source": "memory", "target": "llm"},
                        {"source": "llm", "target": "output"}
                    ]
                },
                llm_config={"provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "temperature": 0.8},
                tools=[],
                sample_prompts=["Hello, who are you?", "Tell me more about that", "Can you explain it differently?"],
                tags=["conversational", "chat", "memory", "beginner"],
                prerequisites=["LLM provider configured"]
            ),
            
            # Template 2: Conversational with Code Injection
            AgentTemplate(
                template_id="tpl_conversational_code",
                name="Conversational Agent with Python",
                description="A conversational agent that can execute inline Python code for calculations and data processing.",
                category="General",
                agent_type="conversational",
                icon="bi-code-slash",
                difficulty="intermediate",
                estimated_setup_time="10 minutes",
                uses_code_fragments=True,
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "User Message",
                         "position": {"x": 100, "y": 200}, "config": {}},
                        {"node_id": "classify", "node_type": "llm", "name": "Classify Intent",
                         "position": {"x": 300, "y": 200},
                         "config": {"system_prompt": "Classify if this needs code execution or just conversation."}},
                        {"node_id": "condition", "node_type": "condition", "name": "Needs Code?",
                         "position": {"x": 500, "y": 200}, 
                         "config": {"condition": "'code' in input.get('intent', '')"}},
                        {"node_id": "python", "node_type": "python", "name": "Execute Python",
                         "position": {"x": 700, "y": 100},
                         "config": {"code": "# Dynamic code execution\nimport json\ndata = input_data\nresult = eval(data.get('expression', '1+1'))\noutput = {'result': result}"}},
                        {"node_id": "chat", "node_type": "llm", "name": "Chat Response",
                         "position": {"x": 700, "y": 300},
                         "config": {"system_prompt": "Respond conversationally."}},
                        {"node_id": "aggregate", "node_type": "aggregate", "name": "Combine",
                         "position": {"x": 900, "y": 200}, "config": {"aggregate_type": "merge"}},
                        {"node_id": "output", "node_type": "output", "name": "Response",
                         "position": {"x": 1100, "y": 200}, "config": {}}
                    ],
                    "edges": [
                        {"source": "input", "target": "classify"},
                        {"source": "classify", "target": "condition"},
                        {"source": "condition", "target": "python"},
                        {"source": "condition", "target": "chat"},
                        {"source": "python", "target": "aggregate"},
                        {"source": "chat", "target": "aggregate"},
                        {"source": "aggregate", "target": "output"}
                    ]
                },
                llm_config={"provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "temperature": 0.5},
                tools=["code_executor"],
                sample_prompts=["Calculate 15% of 2500", "What is the factorial of 10?", "Just chat with me"],
                tags=["conversational", "python", "code", "branching", "intermediate"],
                prerequisites=["LLM provider configured", "Python execution enabled"]
            )
        ]
    
    def _get_tool_calling_templates(self) -> List[AgentTemplate]:
        """Tool-calling agent templates - 2 templates."""
        return [
            # Template 1: Single Tool Agent
            AgentTemplate(
                template_id="tpl_tool_single",
                name="Single Tool Agent",
                description="An agent optimized for calling a single tool efficiently. Simple and fast execution.",
                category="General",
                agent_type="tool_calling",
                icon="bi-wrench",
                difficulty="beginner",
                estimated_setup_time="5 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Request",
                         "position": {"x": 100, "y": 200}, "config": {}},
                        {"node_id": "prepare", "node_type": "llm", "name": "Prepare Parameters",
                         "position": {"x": 300, "y": 200},
                         "config": {"system_prompt": "Extract tool parameters from user request."}},
                        {"node_id": "tool", "node_type": "tool", "name": "Execute Tool",
                         "position": {"x": 500, "y": 200}, "config": {}},
                        {"node_id": "format", "node_type": "llm", "name": "Format Output",
                         "position": {"x": 700, "y": 200},
                         "config": {"system_prompt": "Format tool output for user."}},
                        {"node_id": "output", "node_type": "output", "name": "Result",
                         "position": {"x": 900, "y": 200}, "config": {}}
                    ],
                    "edges": [
                        {"source": "input", "target": "prepare"},
                        {"source": "prepare", "target": "tool"},
                        {"source": "tool", "target": "format"},
                        {"source": "format", "target": "output"}
                    ]
                },
                llm_config={"provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "temperature": 0.3},
                tools=["web_search"],
                sample_prompts=["Search for Python tutorials", "Find the weather in New York"],
                tags=["tool-calling", "single-tool", "fast", "beginner"],
                prerequisites=["LLM provider configured", "At least one tool configured"]
            ),
            
            # Template 2: Multi-Tool Chain Agent
            AgentTemplate(
                template_id="tpl_tool_chain",
                name="Multi-Tool Chain Agent",
                description="An agent that chains multiple tools together, passing output from one to the next. Demonstrates tool orchestration.",
                category="General",
                agent_type="tool_calling",
                icon="bi-link-45deg",
                difficulty="intermediate",
                estimated_setup_time="15 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Request",
                         "position": {"x": 100, "y": 200}, "config": {}},
                        {"node_id": "planner", "node_type": "llm", "name": "Plan Tool Chain",
                         "position": {"x": 300, "y": 200},
                         "config": {"system_prompt": "Plan the sequence of tools to call."}},
                        {"node_id": "tool1", "node_type": "tool", "name": "Tool 1: Fetch",
                         "position": {"x": 500, "y": 200}, 
                         "config": {"tool_name": "web_fetch"}},
                        {"node_id": "transform", "node_type": "python", "name": "Transform Data",
                         "position": {"x": 700, "y": 200},
                         "config": {"code": "# Transform output for next tool\noutput = {'processed': input_data}"}},
                        {"node_id": "tool2", "node_type": "tool", "name": "Tool 2: Process",
                         "position": {"x": 900, "y": 200}, 
                         "config": {"tool_name": "text_analyzer"}},
                        {"node_id": "summarize", "node_type": "llm", "name": "Summarize",
                         "position": {"x": 1100, "y": 200},
                         "config": {"system_prompt": "Summarize the results."}},
                        {"node_id": "output", "node_type": "output", "name": "Result",
                         "position": {"x": 1300, "y": 200}, "config": {}}
                    ],
                    "edges": [
                        {"source": "input", "target": "planner"},
                        {"source": "planner", "target": "tool1"},
                        {"source": "tool1", "target": "transform"},
                        {"source": "transform", "target": "tool2"},
                        {"source": "tool2", "target": "summarize"},
                        {"source": "summarize", "target": "output"}
                    ]
                },
                llm_config={"provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "temperature": 0.5},
                tools=["web_fetch", "text_analyzer", "code_executor"],
                sample_prompts=["Fetch a webpage and analyze its content", "Get data from API and process it"],
                tags=["tool-calling", "chain", "orchestration", "intermediate"],
                prerequisites=["LLM provider configured", "Multiple tools configured"]
            )
        ]
    
    def _get_plan_execute_templates(self) -> List[AgentTemplate]:
        """Plan-and-execute agent templates - 2 templates."""
        return [
            # Template 1: Basic Plan-Execute
            AgentTemplate(
                template_id="tpl_plan_execute_basic",
                name="Basic Plan-Execute Agent",
                description="An agent that first creates a plan, then executes steps sequentially. Shows planning pattern.",
                category="General",
                agent_type="plan_and_execute",
                icon="bi-list-check",
                difficulty="intermediate",
                estimated_setup_time="10 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Task",
                         "position": {"x": 100, "y": 200}, "config": {}},
                        {"node_id": "plan", "node_type": "llm", "name": "Create Plan",
                         "position": {"x": 300, "y": 200},
                         "config": {"system_prompt": "Break down the task into sequential steps. Output as JSON list."}},
                        {"node_id": "step1", "node_type": "llm", "name": "Execute Step 1",
                         "position": {"x": 500, "y": 200},
                         "config": {"system_prompt": "Execute the first step of the plan."}},
                        {"node_id": "step2", "node_type": "llm", "name": "Execute Step 2",
                         "position": {"x": 700, "y": 200},
                         "config": {"system_prompt": "Execute the second step using previous result."}},
                        {"node_id": "step3", "node_type": "llm", "name": "Execute Step 3",
                         "position": {"x": 900, "y": 200},
                         "config": {"system_prompt": "Execute the third step using previous results."}},
                        {"node_id": "output", "node_type": "output", "name": "Final Result",
                         "position": {"x": 1100, "y": 200}, "config": {}}
                    ],
                    "edges": [
                        {"source": "input", "target": "plan"},
                        {"source": "plan", "target": "step1"},
                        {"source": "step1", "target": "step2"},
                        {"source": "step2", "target": "step3"},
                        {"source": "step3", "target": "output"}
                    ]
                },
                llm_config={"provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "temperature": 0.5},
                tools=[],
                sample_prompts=["Write a 3-paragraph essay about AI", "Create a project plan for a website"],
                tags=["plan-execute", "sequential", "planning", "intermediate"],
                prerequisites=["LLM provider configured"]
            ),
            
            # Template 2: Plan-Execute with HITL
            AgentTemplate(
                template_id="tpl_plan_execute_hitl",
                name="Plan-Execute with Human Review",
                description="A plan-execute agent with human-in-the-loop approval at critical steps. Demonstrates HITL pattern.",
                category="General",
                agent_type="plan_and_execute",
                icon="bi-person-check",
                difficulty="advanced",
                estimated_setup_time="15 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Task",
                         "position": {"x": 100, "y": 200}, "config": {}},
                        {"node_id": "plan", "node_type": "llm", "name": "Create Plan",
                         "position": {"x": 300, "y": 200},
                         "config": {"system_prompt": "Create a detailed execution plan."}},
                        {"node_id": "review_plan", "node_type": "hitl", "name": "Approve Plan",
                         "position": {"x": 500, "y": 200},
                         "config": {"task_type": "approval", "instructions": "Review and approve the execution plan."}},
                        {"node_id": "execute", "node_type": "llm", "name": "Execute Plan",
                         "position": {"x": 700, "y": 200},
                         "config": {"system_prompt": "Execute the approved plan."}},
                        {"node_id": "review_result", "node_type": "hitl", "name": "Approve Result",
                         "position": {"x": 900, "y": 200},
                         "config": {"task_type": "approval", "instructions": "Review and approve the final result."}},
                        {"node_id": "output", "node_type": "output", "name": "Approved Result",
                         "position": {"x": 1100, "y": 200}, "config": {}}
                    ],
                    "edges": [
                        {"source": "input", "target": "plan"},
                        {"source": "plan", "target": "review_plan"},
                        {"source": "review_plan", "target": "execute"},
                        {"source": "execute", "target": "review_result"},
                        {"source": "review_result", "target": "output"}
                    ]
                },
                llm_config={"provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "temperature": 0.5},
                tools=[],
                hitl_config={"enabled": True, "approval_required": True, "timeout_hours": 24},
                sample_prompts=["Draft a contract amendment", "Create a proposal for client review"],
                tags=["plan-execute", "hitl", "approval", "advanced"],
                prerequisites=["LLM provider configured", "HITL enabled"]
            )
        ]
    
    def _get_retrieval_templates(self) -> List[AgentTemplate]:
        """Retrieval agent templates - 2 templates."""
        return [
            # Template 1: Basic RAG Agent
            AgentTemplate(
                template_id="tpl_retrieval_basic",
                name="Basic RAG Agent",
                description="A Retrieval-Augmented Generation agent. Retrieves relevant documents and uses them to answer queries.",
                category="General",
                agent_type="retrieval",
                icon="bi-search",
                difficulty="intermediate",
                estimated_setup_time="10 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Query",
                         "position": {"x": 100, "y": 200}, "config": {}},
                        {"node_id": "embed", "node_type": "python", "name": "Create Embedding",
                         "position": {"x": 300, "y": 200},
                         "config": {"code": "# Create embedding for query\noutput = {'query': input_data, 'embedding': 'vector'}"}},
                        {"node_id": "retrieve", "node_type": "tool", "name": "Vector Search",
                         "position": {"x": 500, "y": 200},
                         "config": {"tool_name": "vector_search"}},
                        {"node_id": "augment", "node_type": "transform", "name": "Build Context",
                         "position": {"x": 700, "y": 200},
                         "config": {"transform_type": "passthrough"}},
                        {"node_id": "generate", "node_type": "llm", "name": "Generate Answer",
                         "position": {"x": 900, "y": 200},
                         "config": {"system_prompt": "Answer using the retrieved context. Cite sources."}},
                        {"node_id": "output", "node_type": "output", "name": "Answer",
                         "position": {"x": 1100, "y": 200}, "config": {}}
                    ],
                    "edges": [
                        {"source": "input", "target": "embed"},
                        {"source": "embed", "target": "retrieve"},
                        {"source": "retrieve", "target": "augment"},
                        {"source": "augment", "target": "generate"},
                        {"source": "generate", "target": "output"}
                    ]
                },
                llm_config={"provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "temperature": 0.3},
                tools=["vector_search", "embeddings"],
                sample_prompts=["What does our policy say about refunds?", "Find relevant documentation"],
                tags=["retrieval", "rag", "search", "intermediate"],
                prerequisites=["LLM provider configured", "Vector store configured"]
            ),
            
            # Template 2: Multi-Source RAG Agent
            AgentTemplate(
                template_id="tpl_retrieval_multi",
                name="Multi-Source RAG Agent",
                description="A RAG agent that searches multiple sources in parallel and synthesizes results. Shows parallel retrieval.",
                category="General",
                agent_type="retrieval",
                icon="bi-layers",
                difficulty="advanced",
                estimated_setup_time="20 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Query",
                         "position": {"x": 100, "y": 250}, "config": {}},
                        {"node_id": "split", "node_type": "split", "name": "Fan Out",
                         "position": {"x": 300, "y": 250}, "config": {}},
                        {"node_id": "source1", "node_type": "tool", "name": "Search Docs",
                         "position": {"x": 500, "y": 100},
                         "config": {"tool_name": "doc_search"}},
                        {"node_id": "source2", "node_type": "tool", "name": "Search Web",
                         "position": {"x": 500, "y": 250},
                         "config": {"tool_name": "web_search"}},
                        {"node_id": "source3", "node_type": "tool", "name": "Search DB",
                         "position": {"x": 500, "y": 400},
                         "config": {"tool_name": "db_search"}},
                        {"node_id": "join", "node_type": "join", "name": "Merge Results",
                         "position": {"x": 700, "y": 250}, "config": {"join_type": "merge"}},
                        {"node_id": "rerank", "node_type": "python", "name": "Rerank",
                         "position": {"x": 900, "y": 250},
                         "config": {"code": "# Rerank results by relevance\noutput = sorted(input_data, key=lambda x: x.get('score', 0), reverse=True)[:5]"}},
                        {"node_id": "generate", "node_type": "llm", "name": "Generate Answer",
                         "position": {"x": 1100, "y": 250},
                         "config": {"system_prompt": "Synthesize answer from multiple sources."}},
                        {"node_id": "output", "node_type": "output", "name": "Answer",
                         "position": {"x": 1300, "y": 250}, "config": {}}
                    ],
                    "edges": [
                        {"source": "input", "target": "split"},
                        {"source": "split", "target": "source1"},
                        {"source": "split", "target": "source2"},
                        {"source": "split", "target": "source3"},
                        {"source": "source1", "target": "join"},
                        {"source": "source2", "target": "join"},
                        {"source": "source3", "target": "join"},
                        {"source": "join", "target": "rerank"},
                        {"source": "rerank", "target": "generate"},
                        {"source": "generate", "target": "output"}
                    ]
                },
                llm_config={"provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "temperature": 0.3},
                tools=["doc_search", "web_search", "db_search", "embeddings"],
                sample_prompts=["Research this topic comprehensively", "Find all information about X"],
                tags=["retrieval", "rag", "parallel", "multi-source", "advanced"],
                prerequisites=["LLM provider configured", "Multiple search tools configured"]
            )
        ]
    
    def _get_custom_templates(self) -> List[AgentTemplate]:
        """Custom agent templates - 2 templates."""
        return [
            # Template 1: Code Fragment Agent
            AgentTemplate(
                template_id="tpl_custom_code_fragment",
                name="Code Fragment Agent",
                description="An agent that loads and executes code from the code fragments library. Demonstrates dynamic code injection.",
                category="General",
                agent_type="custom",
                icon="bi-file-code",
                difficulty="advanced",
                estimated_setup_time="15 minutes",
                uses_code_fragments=True,
                code_fragments=["db://code_fragments/data_processor", "db://code_fragments/formatter"],
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Input Data",
                         "position": {"x": 100, "y": 200}, "config": {}},
                        {"node_id": "preprocess", "node_type": "code_fragment", "name": "Preprocess",
                         "position": {"x": 300, "y": 200},
                         "config": {"fragment_name": "data_processor"}},
                        {"node_id": "analyze", "node_type": "llm", "name": "Analyze",
                         "position": {"x": 500, "y": 200},
                         "config": {"system_prompt": "Analyze the processed data."}},
                        {"node_id": "postprocess", "node_type": "code_fragment", "name": "Format Output",
                         "position": {"x": 700, "y": 200},
                         "config": {"fragment_name": "formatter"}},
                        {"node_id": "output", "node_type": "output", "name": "Result",
                         "position": {"x": 900, "y": 200}, "config": {}}
                    ],
                    "edges": [
                        {"source": "input", "target": "preprocess"},
                        {"source": "preprocess", "target": "analyze"},
                        {"source": "analyze", "target": "postprocess"},
                        {"source": "postprocess", "target": "output"}
                    ]
                },
                llm_config={"provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "temperature": 0.5},
                tools=[],
                sample_prompts=["Process this data file", "Transform and analyze this input"],
                tags=["custom", "code-fragment", "dynamic", "advanced"],
                prerequisites=["LLM provider configured", "Code fragments created"]
            ),
            
            # Template 2: Conditional Branching Agent
            AgentTemplate(
                template_id="tpl_custom_branching",
                name="Conditional Branching Agent",
                description="An agent with complex conditional logic and multiple execution paths. Demonstrates advanced branching.",
                category="General",
                agent_type="custom",
                icon="bi-signpost-split",
                difficulty="advanced",
                estimated_setup_time="20 minutes",
                workflow={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Request",
                         "position": {"x": 100, "y": 250}, "config": {}},
                        {"node_id": "classify", "node_type": "llm", "name": "Classify Request",
                         "position": {"x": 300, "y": 250},
                         "config": {"system_prompt": "Classify request type: 'simple', 'complex', or 'urgent'."}},
                        {"node_id": "check_type", "node_type": "condition", "name": "Check Type",
                         "position": {"x": 500, "y": 250},
                         "config": {"condition": "input.get('type') == 'urgent'"}},
                        {"node_id": "urgent_path", "node_type": "llm", "name": "Urgent Handler",
                         "position": {"x": 700, "y": 100},
                         "config": {"system_prompt": "Handle urgent request immediately."}},
                        {"node_id": "check_complex", "node_type": "condition", "name": "Is Complex?",
                         "position": {"x": 700, "y": 400},
                         "config": {"condition": "input.get('type') == 'complex'"}},
                        {"node_id": "complex_path", "node_type": "llm", "name": "Complex Handler",
                         "position": {"x": 900, "y": 300},
                         "config": {"system_prompt": "Handle complex request with detailed analysis."}},
                        {"node_id": "simple_path", "node_type": "llm", "name": "Simple Handler",
                         "position": {"x": 900, "y": 500},
                         "config": {"system_prompt": "Handle simple request quickly."}},
                        {"node_id": "aggregate", "node_type": "aggregate", "name": "Collect Results",
                         "position": {"x": 1100, "y": 250}, "config": {"aggregate_type": "merge"}},
                        {"node_id": "output", "node_type": "output", "name": "Response",
                         "position": {"x": 1300, "y": 250}, "config": {}}
                    ],
                    "edges": [
                        {"source": "input", "target": "classify"},
                        {"source": "classify", "target": "check_type"},
                        {"source": "check_type", "target": "urgent_path"},
                        {"source": "check_type", "target": "check_complex"},
                        {"source": "check_complex", "target": "complex_path"},
                        {"source": "check_complex", "target": "simple_path"},
                        {"source": "urgent_path", "target": "aggregate"},
                        {"source": "complex_path", "target": "aggregate"},
                        {"source": "simple_path", "target": "aggregate"},
                        {"source": "aggregate", "target": "output"}
                    ]
                },
                llm_config={"provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "temperature": 0.5},
                tools=[],
                sample_prompts=["Handle this task based on its priority", "Process this with appropriate urgency"],
                tags=["custom", "branching", "conditional", "advanced"],
                prerequisites=["LLM provider configured"]
            )
        ]
    
    # ============================================
    # PUBLIC API
    # ============================================
    
    def list_templates(self, category: str = None, agent_type: str = None,
                       difficulty: str = None) -> List[AgentTemplate]:
        """List available templates with optional filters."""
        templates = list(self._templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        if agent_type:
            templates = [t for t in templates if t.agent_type == agent_type]
        if difficulty:
            templates = [t for t in templates if t.difficulty == difficulty]
        
        return sorted(templates, key=lambda t: t.name)
    
    def get_template(self, template_id: str) -> Optional[AgentTemplate]:
        """Get a specific template by ID."""
        return self._templates.get(template_id)
    
    def get_categories(self) -> List[str]:
        """Get list of unique categories."""
        return sorted(set(t.category for t in self._templates.values()))
    
    def get_agent_types(self) -> List[str]:
        """Get list of unique agent types."""
        return sorted(set(t.agent_type for t in self._templates.values()))
    
    def search_templates(self, query: str) -> List[AgentTemplate]:
        """Search templates by name, description, or tags."""
        query = query.lower()
        results = []
        
        for template in self._templates.values():
            if query in template.name.lower() or \
               query in template.description.lower() or \
               any(query in tag.lower() for tag in template.tags):
                results.append(template)
        
        return results
    
    def create_agent_from_template(self, template_id: str, name: str,
                                   description: str = None,
                                   created_by: str = None,
                                   agent_manager = None) -> Optional[Any]:
        """Create a new agent from a template.
        
        Args:
            template_id: ID of the template to use
            name: Name for the new agent
            description: Optional description (defaults to template description)
            created_by: User ID creating the agent
            agent_manager: Optional AgentManager to persist the agent
            
        Returns:
            Created Agent object or None if template not found
        """
        template = self.get_template(template_id)
        if not template:
            logger.error(f"Template not found: {template_id}")
            return None
        
        import copy
        
        logger.info(f"Creating agent '{name}' from template '{template_id}'")
        logger.info(f"Template llm_config: {template.llm_config}")
        logger.info(f"Template agent_type: {template.agent_type}")
        
        # If we have an agent manager, use it to create the agent
        if agent_manager:
            agent = agent_manager.create_agent(
                name=name,
                description=description or template.description,
                agent_type=template.agent_type,
                workflow=copy.deepcopy(template.workflow),
                llm_config=copy.deepcopy(template.llm_config),
                tools=template.tools.copy(),
                hitl_config=copy.deepcopy(template.hitl_config),
                created_by=created_by or "system"
            )
            logger.info(f"Agent created with ID: {agent.agent_id}")
            logger.info(f"Agent config: {agent.config}")
        else:
            # Create agent object without persisting
            from .agent_manager import Agent
            import uuid
            
            agent = Agent(
                agent_id=str(uuid.uuid4()),
                name=name,
                description=description or template.description,
                agent_type=template.agent_type,
                version="1.0.0",
                workflow=copy.deepcopy(template.workflow),
                llm_config=copy.deepcopy(template.llm_config),
                tools=template.tools.copy(),
                hitl_config=copy.deepcopy(template.hitl_config),
                created_by=created_by or "system"
            )
            logger.info(f"Agent created (in memory): {agent.agent_id}")
        
        # Increment use count
        template.use_count += 1
        
        return agent
