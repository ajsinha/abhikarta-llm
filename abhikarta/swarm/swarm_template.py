"""
Swarm Template Manager - Template library for agent swarms.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Version: 1.4.7
"""

import json
import os
import glob
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class SwarmTemplate:
    """Swarm template definition."""
    template_id: str
    name: str
    description: str
    category: str
    icon: str = "bi-people"
    difficulty: str = "intermediate"
    config: Dict[str, Any] = field(default_factory=dict)
    swarm_definition: Dict[str, Any] = field(default_factory=dict)
    agents: List[Dict[str, Any]] = field(default_factory=list)
    triggers: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)
    sample_inputs: List[Dict[str, Any]] = field(default_factory=list)
    expected_outputs: List[str] = field(default_factory=list)
    is_system: bool = True
    created_by: str = "system"
    created_at: str = ""
    use_count: int = 0
    prerequisites: List[str] = field(default_factory=list)
    estimated_setup_time: str = "10 minutes"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SwarmTemplateManager:
    """Manages swarm templates including built-in and custom templates."""
    
    def __init__(self, db_facade=None):
        """Initialize with optional database facade."""
        self.db_facade = db_facade
        self._templates: Dict[str, SwarmTemplate] = {}
        self._init_builtin_templates()
        self._load_json_templates()
        logger.info(f"SwarmTemplateManager initialized with {len(self._templates)} templates")
    
    def _init_builtin_templates(self):
        """Initialize built-in swarm templates - 2 fundamental templates."""
        builtin = self._get_fundamental_swarms()
        
        for template in builtin:
            from abhikarta.utils.helpers import get_timestamp
            template.created_at = get_timestamp()
            self._templates[template.template_id] = template
    
    def _load_json_templates(self):
        """Load swarm templates from JSON files in entity_definitions/swarms directory."""
        # Find templates directory relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        abhikarta_dir = os.path.dirname(current_dir)
        project_dir = os.path.dirname(abhikarta_dir)
        templates_dir = os.path.join(project_dir, 'entity_definitions', 'swarms')
        
        if not os.path.exists(templates_dir):
            logger.warning(f"Swarm templates directory not found: {templates_dir}")
            return
        
        json_files = glob.glob(os.path.join(templates_dir, '*.json'))
        logger.info(f"Found {len(json_files)} JSON swarm template files in {templates_dir}")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                swarm_data = data.get('swarm', {})
                
                # Create SwarmTemplate from JSON
                template = SwarmTemplate(
                    template_id=data.get('template_id', os.path.basename(json_file).replace('.json', '')),
                    name=data.get('name', 'Unnamed Template'),
                    description=data.get('description', ''),
                    category=data.get('category', 'general'),
                    icon=data.get('icon', 'bi-grid-3x3'),
                    difficulty=data.get('difficulty', 'intermediate'),
                    swarm_definition=swarm_data,
                    agents=swarm_data.get('agents', []),
                    config=swarm_data.get('coordinator', {}),
                    sample_inputs=data.get('sample_inputs', []),
                    expected_outputs=data.get('expected_outputs', []),
                    tags=data.get('tags', []),
                    use_cases=data.get('use_cases', []),
                    prerequisites=data.get('prerequisites', []),
                    estimated_setup_time=data.get('estimated_duration', '< 5 minutes'),
                    is_system=True,
                    created_by='system'
                )
                
                from abhikarta.utils.helpers import get_timestamp
                template.created_at = get_timestamp()
                self._templates[template.template_id] = template
                logger.debug(f"Loaded swarm template: {template.template_id} - {template.name}")
                
            except Exception as e:
                logger.error(f"Error loading swarm template from {json_file}: {e}")
    
    def _get_fundamental_swarms(self) -> List[SwarmTemplate]:
        """2 fundamental swarm templates."""
        return [
            # 1. Research Swarm - Multiple agents collaborating on research
            SwarmTemplate(
                template_id="swarm_tpl_research",
                name="Research Swarm",
                description="A collaborative swarm of agents for research tasks. Includes a coordinator, web researcher, document analyst, and synthesizer working together.",
                category="Research",
                icon="bi-search",
                difficulty="intermediate",
                estimated_setup_time="15 minutes",
                config={
                    "max_concurrent_tasks": 5,
                    "timeout_seconds": 300,
                    "retry_on_failure": True,
                    "max_retries": 3,
                    "event_bus_type": "in_memory"
                },
                agents=[
                    {
                        "agent_id": "coordinator",
                        "name": "Research Coordinator",
                        "role": "Coordinator",
                        "subscriptions": ["task.new", "research.complete", "error.*"],
                        "pool_size": {"min": 1, "max": 1},
                        "config": {"provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "system_prompt": "You coordinate research tasks among the team.",
                            "can_delegate": True
                        }
                    },
                    {
                        "agent_id": "web_researcher",
                        "name": "Web Researcher",
                        "role": "Worker",
                        "subscriptions": ["research.web", "search.request"],
                        "pool_size": {"min": 1, "max": 3},
                        "config": {"provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "system_prompt": "You search the web for information.",
                            "tools": ["web_search", "web_scrape"]
                        }
                    },
                    {
                        "agent_id": "doc_analyst",
                        "name": "Document Analyst",
                        "role": "Worker",
                        "subscriptions": ["research.document", "analyze.request"],
                        "pool_size": {"min": 1, "max": 2},
                        "config": {"provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "system_prompt": "You analyze documents and extract insights.",
                            "tools": ["document_parser"]
                        }
                    },
                    {
                        "agent_id": "synthesizer",
                        "name": "Research Synthesizer",
                        "role": "Worker",
                        "subscriptions": ["research.synthesize", "compile.request"],
                        "pool_size": {"min": 1, "max": 1},
                        "config": {"provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "system_prompt": "You synthesize research findings into reports."
                        }
                    }
                ],
                triggers=[
                    {
                        "type": "user_query",
                        "config": {"prompt_template": "Research: {query}"},
                        "enabled": True
                    },
                    {
                        "type": "http",
                        "config": {"endpoint": "/api/swarm/research/trigger"},
                        "enabled": True
                    }
                ],
                tags=["research", "collaboration", "web-search"],
                prerequisites=["At least one LLM provider configured", "Web search tools enabled"]
            ),
            
            # 2. Task Processing Swarm - Pipeline-style processing
            SwarmTemplate(
                template_id="swarm_tpl_task_pipeline",
                name="Task Processing Pipeline",
                description="A pipeline-style swarm for processing tasks through multiple stages. Includes intake, processing, validation, and completion agents.",
                category="Processing",
                icon="bi-arrow-right-circle",
                difficulty="beginner",
                estimated_setup_time="10 minutes",
                config={
                    "max_concurrent_tasks": 10,
                    "timeout_seconds": 180,
                    "retry_on_failure": True,
                    "max_retries": 2,
                    "event_bus_type": "in_memory"
                },
                agents=[
                    {
                        "agent_id": "intake",
                        "name": "Intake Agent",
                        "role": "Coordinator",
                        "subscriptions": ["task.new", "task.submitted"],
                        "pool_size": {"min": 1, "max": 2},
                        "config": {"provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "system_prompt": "You receive and validate incoming tasks.",
                            "validation_schema": {}
                        }
                    },
                    {
                        "agent_id": "processor",
                        "name": "Task Processor",
                        "role": "Worker",
                        "subscriptions": ["task.validated", "process.request"],
                        "pool_size": {"min": 2, "max": 5},
                        "config": {"provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "system_prompt": "You process tasks according to their requirements."
                        }
                    },
                    {
                        "agent_id": "validator",
                        "name": "Quality Validator",
                        "role": "Worker",
                        "subscriptions": ["task.processed", "validate.request"],
                        "pool_size": {"min": 1, "max": 2},
                        "config": {"provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "system_prompt": "You validate the quality of processed tasks."
                        }
                    },
                    {
                        "agent_id": "completer",
                        "name": "Completion Agent",
                        "role": "Worker",
                        "subscriptions": ["task.validated", "complete.request"],
                        "pool_size": {"min": 1, "max": 1},
                        "config": {"provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "system_prompt": "You finalize and deliver completed tasks."
                        }
                    }
                ],
                triggers=[
                    {
                        "type": "http",
                        "config": {"endpoint": "/api/swarm/pipeline/submit"},
                        "enabled": True
                    },
                    {
                        "type": "schedule",
                        "config": {"cron": "0 */6 * * *"},
                        "enabled": False
                    }
                ],
                tags=["pipeline", "processing", "automation"],
                prerequisites=["At least one LLM provider configured"]
            )
        ]
    
    # ==================== CRUD Operations ====================
    
    def list_templates(self, category: str = None, difficulty: str = None) -> List[SwarmTemplate]:
        """List templates with optional filtering."""
        templates = list(self._templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        if difficulty:
            templates = [t for t in templates if t.difficulty == difficulty]
        
        return sorted(templates, key=lambda t: t.use_count, reverse=True)
    
    def get_template(self, template_id: str) -> Optional[SwarmTemplate]:
        """Get a template by ID."""
        return self._templates.get(template_id)
    
    def get_categories(self) -> List[str]:
        """Get unique categories."""
        return sorted(set(t.category for t in self._templates.values()))
    
    def search_templates(self, query: str) -> List[SwarmTemplate]:
        """Search templates by name, description, or tags."""
        query_lower = query.lower()
        results = []
        for t in self._templates.values():
            if (query_lower in t.name.lower() or 
                query_lower in t.description.lower() or
                any(query_lower in tag for tag in t.tags)):
                results.append(t)
        return results
    
    def create_swarm_from_template(self, template_id: str, name: str,
                                  description: str = None) -> Optional[Dict[str, Any]]:
        """Create a swarm definition from a template."""
        template = self.get_template(template_id)
        if not template:
            return None
        
        import uuid
        
        swarm_def = {
            "swarm_id": str(uuid.uuid4()),
            "name": name,
            "description": description or template.description,
            "version": "1.0.0",
            "config": template.config,
            "agents": template.agents,
            "triggers": template.triggers,
            "tags": template.tags,
            "category": template.category,
            "status": "draft"
        }
        
        # Increment use count
        template.use_count += 1
        
        return swarm_def
