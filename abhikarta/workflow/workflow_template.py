"""
Workflow Template Manager - Template library for workflow DAGs.

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
class WorkflowTemplate:
    """Workflow template definition."""
    template_id: str
    name: str
    description: str
    category: str
    icon: str = "bi-diagram-3"
    difficulty: str = "intermediate"
    dag_definition: Dict[str, Any] = field(default_factory=dict)
    python_modules: List[str] = field(default_factory=list)
    sample_inputs: List[Dict[str, Any]] = field(default_factory=list)
    expected_outputs: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    is_system: bool = True
    created_by: str = "system"
    created_at: str = ""
    use_count: int = 0
    prerequisites: List[str] = field(default_factory=list)
    estimated_duration: str = "< 1 minute"
    uses_code_fragments: bool = False
    code_fragments: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class WorkflowTemplateManager:
    """Manages workflow templates including built-in and custom templates."""
    
    def __init__(self, db_facade=None):
        """Initialize with optional database facade."""
        self.db_facade = db_facade
        self._templates: Dict[str, WorkflowTemplate] = {}
        self._init_builtin_templates()
        logger.info("WorkflowTemplateManager initialized")
    
    def _init_builtin_templates(self):
        """Initialize 5 built-in generic workflow templates."""
        builtin = [
            # Template 1: Sequential Processing Pipeline
            WorkflowTemplate(
                template_id="wf_tpl_sequential",
                name="Sequential Processing Pipeline",
                description="A basic sequential workflow that processes data through multiple steps. Demonstrates input->process->output pattern.",
                category="Data Processing",
                icon="bi-arrow-right",
                difficulty="beginner",
                estimated_duration="30 seconds",
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Data Input",
                         "position": {"x": 100, "y": 200}, "config": {}},
                        {"node_id": "validate", "node_type": "python", "name": "Validate Data",
                         "position": {"x": 300, "y": 200},
                         "config": {"code": "# Validate input data\nif not input_data:\n    raise ValueError('No input provided')\noutput = {'valid': True, 'data': input_data}"}},
                        {"node_id": "transform", "node_type": "transform", "name": "Transform",
                         "position": {"x": 500, "y": 200},
                         "config": {"transform_type": "passthrough"}},
                        {"node_id": "process", "node_type": "llm", "name": "LLM Process",
                         "position": {"x": 700, "y": 200},
                         "config": {"provider": "ollama", "model": "llama3.2:3b", "system_prompt": "Process the input data and generate output."}},
                        {"node_id": "output", "node_type": "output", "name": "Result",
                         "position": {"x": 900, "y": 200}, "config": {}}
                    ],
                    "edges": [
                        {"source": "input", "target": "validate"},
                        {"source": "validate", "target": "transform"},
                        {"source": "transform", "target": "process"},
                        {"source": "process", "target": "output"}
                    ]
                },
                sample_inputs=[{"data": "Sample input data"}],
                expected_outputs=["Processed result"],
                tags=["sequential", "pipeline", "beginner", "basic"],
                prerequisites=["LLM provider configured"]
            ),
            
            # Template 2: Parallel Fan-Out/Fan-In
            WorkflowTemplate(
                template_id="wf_tpl_parallel",
                name="Parallel Fan-Out/Fan-In",
                description="A workflow that splits work into parallel branches, processes them concurrently, and merges results. Demonstrates parallel execution.",
                category="Data Processing",
                icon="bi-diagram-3",
                difficulty="intermediate",
                estimated_duration="1 minute",
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Input Data",
                         "position": {"x": 100, "y": 250}, "config": {}},
                        {"node_id": "split", "node_type": "split", "name": "Fan Out",
                         "position": {"x": 300, "y": 250},
                         "config": {"split_type": "items"}},
                        {"node_id": "branch1", "node_type": "llm", "name": "Process Branch A",
                         "position": {"x": 550, "y": 100},
                         "config": {"provider": "ollama", "model": "llama3.2:3b", "system_prompt": "Process this item with approach A."}},
                        {"node_id": "branch2", "node_type": "llm", "name": "Process Branch B",
                         "position": {"x": 550, "y": 250},
                         "config": {"provider": "ollama", "model": "llama3.2:3b", "system_prompt": "Process this item with approach B."}},
                        {"node_id": "branch3", "node_type": "python", "name": "Python Process",
                         "position": {"x": 550, "y": 400},
                         "config": {"code": "# Custom Python processing\nresult = str(input_data).upper()\noutput = {'processed': result}"}},
                        {"node_id": "join", "node_type": "join", "name": "Fan In",
                         "position": {"x": 800, "y": 250},
                         "config": {"join_type": "all"}},
                        {"node_id": "aggregate", "node_type": "llm", "name": "Aggregate Results",
                         "position": {"x": 1000, "y": 250},
                         "config": {"provider": "ollama", "model": "llama3.2:3b", "system_prompt": "Combine all branch results into a unified response."}},
                        {"node_id": "output", "node_type": "output", "name": "Final Output",
                         "position": {"x": 1200, "y": 250}, "config": {}}
                    ],
                    "edges": [
                        {"source": "input", "target": "split"},
                        {"source": "split", "target": "branch1"},
                        {"source": "split", "target": "branch2"},
                        {"source": "split", "target": "branch3"},
                        {"source": "branch1", "target": "join"},
                        {"source": "branch2", "target": "join"},
                        {"source": "branch3", "target": "join"},
                        {"source": "join", "target": "aggregate"},
                        {"source": "aggregate", "target": "output"}
                    ]
                },
                sample_inputs=[{"items": ["item1", "item2", "item3"]}],
                expected_outputs=["Aggregated results from all branches"],
                tags=["parallel", "fan-out", "fan-in", "concurrent", "intermediate"],
                prerequisites=["LLM provider configured"]
            ),
            
            # Template 3: Conditional Branching with Code Injection
            WorkflowTemplate(
                template_id="wf_tpl_conditional",
                name="Conditional Branching Workflow",
                description="A workflow with conditional logic that routes to different paths based on conditions. Shows inline Python code injection and decision making.",
                category="Logic Flow",
                icon="bi-signpost-split",
                difficulty="intermediate",
                estimated_duration="45 seconds",
                uses_code_fragments=False,
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Request",
                         "position": {"x": 100, "y": 250}, "config": {}},
                        {"node_id": "analyze", "node_type": "python", "name": "Analyze Input",
                         "position": {"x": 300, "y": 250},
                         "config": {"code": "# Analyze and classify input\ndata = input_data or {}\nsize = len(str(data))\nif size > 1000:\n    classification = 'large'\nelif size > 100:\n    classification = 'medium'\nelse:\n    classification = 'small'\noutput = {'classification': classification, 'size': size, 'data': data}"}},
                        {"node_id": "condition1", "node_type": "condition", "name": "Is Large?",
                         "position": {"x": 500, "y": 250},
                         "config": {"condition": "input.get('classification') == 'large'"}},
                        {"node_id": "large_handler", "node_type": "llm", "name": "Large Data Handler",
                         "position": {"x": 700, "y": 100},
                         "config": {"provider": "ollama", "model": "llama3.2:3b", "system_prompt": "Handle large data with chunking strategy."}},
                        {"node_id": "condition2", "node_type": "condition", "name": "Is Medium?",
                         "position": {"x": 700, "y": 400},
                         "config": {"condition": "input.get('classification') == 'medium'"}},
                        {"node_id": "medium_handler", "node_type": "llm", "name": "Medium Data Handler",
                         "position": {"x": 900, "y": 300},
                         "config": {"provider": "ollama", "model": "llama3.2:3b", "system_prompt": "Handle medium-sized data normally."}},
                        {"node_id": "small_handler", "node_type": "llm", "name": "Small Data Handler",
                         "position": {"x": 900, "y": 500},
                         "config": {"provider": "ollama", "model": "llama3.2:3b", "system_prompt": "Handle small data with quick processing."}},
                        {"node_id": "merge", "node_type": "aggregate", "name": "Merge Results",
                         "position": {"x": 1100, "y": 250},
                         "config": {"aggregate_type": "merge"}},
                        {"node_id": "output", "node_type": "output", "name": "Result",
                         "position": {"x": 1300, "y": 250}, "config": {}}
                    ],
                    "edges": [
                        {"source": "input", "target": "analyze"},
                        {"source": "analyze", "target": "condition1"},
                        {"source": "condition1", "target": "large_handler"},
                        {"source": "condition1", "target": "condition2"},
                        {"source": "condition2", "target": "medium_handler"},
                        {"source": "condition2", "target": "small_handler"},
                        {"source": "large_handler", "target": "merge"},
                        {"source": "medium_handler", "target": "merge"},
                        {"source": "small_handler", "target": "merge"},
                        {"source": "merge", "target": "output"}
                    ]
                },
                sample_inputs=[{"data": "Test data of varying sizes"}],
                expected_outputs=["Processed result based on data size"],
                tags=["conditional", "branching", "python", "logic", "intermediate"],
                prerequisites=["LLM provider configured", "Python execution enabled"]
            ),
            
            # Template 4: Human-in-the-Loop Approval Workflow
            WorkflowTemplate(
                template_id="wf_tpl_hitl",
                name="Human-in-the-Loop Approval",
                description="A workflow with human review checkpoints. Demonstrates HITL pattern for critical decision points requiring human approval.",
                category="Approval Flow",
                icon="bi-person-check",
                difficulty="advanced",
                estimated_duration="Depends on approval time",
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Request",
                         "position": {"x": 100, "y": 200}, "config": {}},
                        {"node_id": "draft", "node_type": "llm", "name": "Generate Draft",
                         "position": {"x": 300, "y": 200},
                         "config": {"provider": "ollama", "model": "llama3.2:3b", "system_prompt": "Generate a draft based on the request."}},
                        {"node_id": "review1", "node_type": "hitl", "name": "Draft Review",
                         "position": {"x": 500, "y": 200},
                         "config": {"task_type": "review", "instructions": "Review the generated draft and provide feedback or approve."}},
                        {"node_id": "revise", "node_type": "llm", "name": "Revise Draft",
                         "position": {"x": 700, "y": 200},
                         "config": {"provider": "ollama", "model": "llama3.2:3b", "system_prompt": "Incorporate feedback and improve the draft."}},
                        {"node_id": "review2", "node_type": "hitl", "name": "Final Approval",
                         "position": {"x": 900, "y": 200},
                         "config": {"task_type": "approval", "instructions": "Final approval before publishing."}},
                        {"node_id": "finalize", "node_type": "python", "name": "Finalize",
                         "position": {"x": 1100, "y": 200},
                         "config": {"code": "# Finalize the approved content\noutput = {'status': 'approved', 'content': input_data, 'timestamp': __import__('datetime').datetime.now().isoformat()}"}},
                        {"node_id": "output", "node_type": "output", "name": "Final Output",
                         "position": {"x": 1300, "y": 200}, "config": {}}
                    ],
                    "edges": [
                        {"source": "input", "target": "draft"},
                        {"source": "draft", "target": "review1"},
                        {"source": "review1", "target": "revise"},
                        {"source": "revise", "target": "review2"},
                        {"source": "review2", "target": "finalize"},
                        {"source": "finalize", "target": "output"}
                    ]
                },
                sample_inputs=[{"request": "Create a marketing proposal"}],
                expected_outputs=["Approved and finalized content"],
                tags=["hitl", "approval", "human-review", "advanced"],
                prerequisites=["LLM provider configured", "HITL enabled"]
            ),
            
            # Template 5: Code Fragment Integration Workflow
            WorkflowTemplate(
                template_id="wf_tpl_code_fragments",
                name="Code Fragment Integration",
                description="A workflow that uses code fragments from the library. Demonstrates dynamic code loading and modular execution with tool integration.",
                category="Integration",
                icon="bi-file-code",
                difficulty="advanced",
                estimated_duration="1-2 minutes",
                uses_code_fragments=True,
                code_fragments=["db://code_fragments/data_validator", "db://code_fragments/output_formatter"],
                dag_definition={
                    "nodes": [
                        {"node_id": "input", "node_type": "input", "name": "Raw Data",
                         "position": {"x": 100, "y": 200}, "config": {}},
                        {"node_id": "validate", "node_type": "code_fragment", "name": "Validate (Fragment)",
                         "position": {"x": 300, "y": 200},
                         "config": {"fragment_name": "data_validator"}},
                        {"node_id": "fetch", "node_type": "tool", "name": "Fetch External Data",
                         "position": {"x": 500, "y": 200},
                         "config": {"tool_name": "web_fetch"}},
                        {"node_id": "combine", "node_type": "python", "name": "Combine Data",
                         "position": {"x": 700, "y": 200},
                         "config": {"code": "# Combine validated data with fetched data\nvalidated = context.get('validated_data', {})\nfetched = input_data or {}\noutput = {**validated, **fetched, 'combined': True}"}},
                        {"node_id": "analyze", "node_type": "llm", "name": "Analyze Combined",
                         "position": {"x": 900, "y": 200},
                         "config": {"provider": "ollama", "model": "llama3.2:3b", "system_prompt": "Analyze the combined data and provide insights."}},
                        {"node_id": "format", "node_type": "code_fragment", "name": "Format (Fragment)",
                         "position": {"x": 1100, "y": 200},
                         "config": {"fragment_name": "output_formatter"}},
                        {"node_id": "output", "node_type": "output", "name": "Formatted Result",
                         "position": {"x": 1300, "y": 200}, "config": {}}
                    ],
                    "edges": [
                        {"source": "input", "target": "validate"},
                        {"source": "validate", "target": "fetch"},
                        {"source": "fetch", "target": "combine"},
                        {"source": "combine", "target": "analyze"},
                        {"source": "analyze", "target": "format"},
                        {"source": "format", "target": "output"}
                    ]
                },
                sample_inputs=[{"raw_data": "Input to process"}],
                expected_outputs=["Formatted and processed output"],
                tags=["code-fragment", "integration", "modular", "tool", "advanced"],
                prerequisites=["LLM provider configured", "Code fragments created", "Tools configured"]
            )
        ]
        
        for template in builtin:
            from abhikarta.utils.helpers import get_timestamp
            template.created_at = get_timestamp()
            self._templates[template.template_id] = template
    
    # ============================================
    # PUBLIC API
    # ============================================
    
    def list_templates(self, category: str = None, difficulty: str = None) -> List[WorkflowTemplate]:
        """List available templates with optional filters."""
        templates = list(self._templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        if difficulty:
            templates = [t for t in templates if t.difficulty == difficulty]
        
        return sorted(templates, key=lambda t: t.name)
    
    def get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """Get a specific template by ID."""
        return self._templates.get(template_id)
    
    def get_categories(self) -> List[str]:
        """Get list of unique categories."""
        return sorted(set(t.category for t in self._templates.values()))
    
    def get_industries(self) -> List[str]:
        """Get list of industries (for compatibility, returns empty)."""
        return []
    
    def search_templates(self, query: str) -> List[WorkflowTemplate]:
        """Search templates by name, description, or tags."""
        query = query.lower()
        results = []
        
        for template in self._templates.values():
            if query in template.name.lower() or \
               query in template.description.lower() or \
               any(query in tag.lower() for tag in template.tags):
                results.append(template)
        
        return results
