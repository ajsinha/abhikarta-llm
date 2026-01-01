"""
AI Organization Template Manager - Template library for AI Organizations.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Version: 1.0.0
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class AIOrgTemplate:
    """AI Organization template definition."""
    template_id: str
    name: str
    description: str
    category: str
    icon: str = "bi-diagram-3"
    difficulty: str = "intermediate"
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    org_config: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    is_system: bool = True
    created_by: str = "system"
    created_at: str = ""
    use_count: int = 0
    prerequisites: List[str] = field(default_factory=list)
    estimated_setup_time: str = "15 minutes"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AIOrgTemplateManager:
    """Manages AI Organization templates including built-in and custom templates."""
    
    def __init__(self, db_facade=None):
        """Initialize with optional database facade."""
        self.db_facade = db_facade
        self._templates: Dict[str, AIOrgTemplate] = {}
        self._init_builtin_templates()
        logger.info("AIOrgTemplateManager initialized")
    
    def _init_builtin_templates(self):
        """Initialize built-in AI Org templates - 2 fundamental templates."""
        builtin = self._get_fundamental_orgs()
        
        for template in builtin:
            from abhikarta.utils.helpers import get_timestamp
            template.created_at = get_timestamp()
            self._templates[template.template_id] = template
    
    def _get_fundamental_orgs(self) -> List[AIOrgTemplate]:
        """2 fundamental AI Organization templates."""
        return [
            # 1. Simple Hierarchical Org - CEO > Managers > Workers
            AIOrgTemplate(
                template_id="aiorg_tpl_hierarchical",
                name="Hierarchical Organization",
                description="A simple hierarchical organization with a CEO, department managers, and workers. Tasks flow top-down with reporting bottom-up.",
                category="Standard",
                icon="bi-diagram-3",
                difficulty="beginner",
                estimated_setup_time="10 minutes",
                org_config={
                    "delegation_strategy": "top_down",
                    "default_hitl_mode": "approval",
                    "notification_channels": ["email"]
                },
                nodes=[
                    {
                        "node_id": "ceo_1",
                        "role_name": "CEO",
                        "role_type": "executive",
                        "description": "Chief Executive Officer - oversees all operations and makes strategic decisions.",
                        "parent_node_id": None,
                        "position_x": 400,
                        "position_y": 50,
                        "agent_config": {
                            "provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "system_prompt": "You are the CEO. Make strategic decisions and delegate tasks.",
                            "can_delegate": True,
                            "approval_required": False
                        },
                        "hitl_config": {
                            "enabled": True,
                            "mode": "approval",
                            "threshold": "high_impact"
                        }
                    },
                    {
                        "node_id": "ops_mgr_1",
                        "role_name": "Operations Manager",
                        "role_type": "manager",
                        "description": "Manages day-to-day operations and operational staff.",
                        "parent_node_id": "ceo_1",
                        "position_x": 200,
                        "position_y": 200,
                        "agent_config": {
                            "provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "system_prompt": "You manage operations. Coordinate tasks and ensure efficiency.",
                            "can_delegate": True
                        },
                        "hitl_config": {
                            "enabled": True,
                            "mode": "review"
                        }
                    },
                    {
                        "node_id": "tech_mgr_1",
                        "role_name": "Technical Manager",
                        "role_type": "manager",
                        "description": "Manages technical projects and engineering staff.",
                        "parent_node_id": "ceo_1",
                        "position_x": 600,
                        "position_y": 200,
                        "agent_config": {
                            "provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "system_prompt": "You manage technical projects. Guide development and review work.",
                            "can_delegate": True
                        },
                        "hitl_config": {
                            "enabled": True,
                            "mode": "review"
                        }
                    },
                    {
                        "node_id": "ops_worker_1",
                        "role_name": "Operations Analyst",
                        "role_type": "worker",
                        "description": "Handles operational analysis and reporting.",
                        "parent_node_id": "ops_mgr_1",
                        "position_x": 100,
                        "position_y": 350,
                        "agent_config": {
                            "provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "system_prompt": "You analyze operations data and create reports.",
                            "tools": ["data_analysis", "report_generator"]
                        },
                        "hitl_config": {
                            "enabled": False
                        }
                    },
                    {
                        "node_id": "ops_worker_2",
                        "role_name": "Process Coordinator",
                        "role_type": "worker",
                        "description": "Coordinates business processes and workflows.",
                        "parent_node_id": "ops_mgr_1",
                        "position_x": 300,
                        "position_y": 350,
                        "agent_config": {
                            "provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "system_prompt": "You coordinate processes and ensure smooth workflows."
                        },
                        "hitl_config": {
                            "enabled": False
                        }
                    },
                    {
                        "node_id": "tech_worker_1",
                        "role_name": "Developer",
                        "role_type": "worker",
                        "description": "Develops software and implements solutions.",
                        "parent_node_id": "tech_mgr_1",
                        "position_x": 500,
                        "position_y": 350,
                        "agent_config": {
                            "provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "system_prompt": "You write code and implement technical solutions.",
                            "tools": ["code_executor", "git"]
                        },
                        "hitl_config": {
                            "enabled": False
                        }
                    },
                    {
                        "node_id": "tech_worker_2",
                        "role_name": "QA Engineer",
                        "role_type": "worker",
                        "description": "Tests and validates software quality.",
                        "parent_node_id": "tech_mgr_1",
                        "position_x": 700,
                        "position_y": 350,
                        "agent_config": {
                            "provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "system_prompt": "You test software and ensure quality.",
                            "tools": ["test_runner"]
                        },
                        "hitl_config": {
                            "enabled": False
                        }
                    }
                ],
                tags=["hierarchical", "standard", "management"],
                prerequisites=["At least one LLM provider configured"]
            ),
            
            # 2. Flat Team Org - Lead + Specialists
            AIOrgTemplate(
                template_id="aiorg_tpl_flat_team",
                name="Flat Team Organization",
                description="A flat team structure with a team lead and specialist members. Emphasizes collaboration and direct communication.",
                category="Agile",
                icon="bi-people",
                difficulty="beginner",
                estimated_setup_time="8 minutes",
                org_config={
                    "delegation_strategy": "collaborative",
                    "default_hitl_mode": "notification",
                    "notification_channels": ["slack"]
                },
                nodes=[
                    {
                        "node_id": "lead_1",
                        "role_name": "Team Lead",
                        "role_type": "manager",
                        "description": "Team lead who facilitates and coordinates. First among equals.",
                        "parent_node_id": None,
                        "position_x": 400,
                        "position_y": 50,
                        "agent_config": {
                            "provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "system_prompt": "You are the team lead. Facilitate collaboration and remove blockers.",
                            "can_delegate": True,
                            "leadership_style": "servant"
                        },
                        "hitl_config": {
                            "enabled": True,
                            "mode": "notification"
                        }
                    },
                    {
                        "node_id": "specialist_1",
                        "role_name": "Research Specialist",
                        "role_type": "specialist",
                        "description": "Expert in research and information gathering.",
                        "parent_node_id": "lead_1",
                        "position_x": 150,
                        "position_y": 200,
                        "agent_config": {
                            "provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "system_prompt": "You are a research specialist. Find and analyze information.",
                            "tools": ["web_search", "document_analyzer"],
                            "expertise": ["research", "analysis"]
                        },
                        "hitl_config": {
                            "enabled": False
                        }
                    },
                    {
                        "node_id": "specialist_2",
                        "role_name": "Content Specialist",
                        "role_type": "specialist",
                        "description": "Expert in content creation and writing.",
                        "parent_node_id": "lead_1",
                        "position_x": 350,
                        "position_y": 200,
                        "agent_config": {
                            "provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "system_prompt": "You are a content specialist. Create and refine content.",
                            "expertise": ["writing", "editing", "content"]
                        },
                        "hitl_config": {
                            "enabled": False
                        }
                    },
                    {
                        "node_id": "specialist_3",
                        "role_name": "Technical Specialist",
                        "role_type": "specialist",
                        "description": "Expert in technical implementation.",
                        "parent_node_id": "lead_1",
                        "position_x": 550,
                        "position_y": 200,
                        "agent_config": {
                            "provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "system_prompt": "You are a technical specialist. Implement solutions.",
                            "tools": ["code_executor"],
                            "expertise": ["development", "integration"]
                        },
                        "hitl_config": {
                            "enabled": False
                        }
                    },
                    {
                        "node_id": "specialist_4",
                        "role_name": "QA Specialist",
                        "role_type": "specialist",
                        "description": "Expert in quality assurance and testing.",
                        "parent_node_id": "lead_1",
                        "position_x": 650,
                        "position_y": 200,
                        "agent_config": {
                            "provider": "ollama", "model": "llama3.2:3b", "base_url": "http://192.168.2.36:11434", "system_prompt": "You are a QA specialist. Validate quality and test.",
                            "tools": ["test_runner"],
                            "expertise": ["testing", "quality"]
                        },
                        "hitl_config": {
                            "enabled": False
                        }
                    }
                ],
                tags=["flat", "agile", "team", "collaborative"],
                prerequisites=["At least one LLM provider configured"]
            )
        ]
    
    # ==================== CRUD Operations ====================
    
    def list_templates(self, category: str = None, difficulty: str = None) -> List[AIOrgTemplate]:
        """List templates with optional filtering."""
        templates = list(self._templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        if difficulty:
            templates = [t for t in templates if t.difficulty == difficulty]
        
        return sorted(templates, key=lambda t: t.use_count, reverse=True)
    
    def get_template(self, template_id: str) -> Optional[AIOrgTemplate]:
        """Get a template by ID."""
        return self._templates.get(template_id)
    
    def get_categories(self) -> List[str]:
        """Get unique categories."""
        return sorted(set(t.category for t in self._templates.values()))
    
    def search_templates(self, query: str) -> List[AIOrgTemplate]:
        """Search templates by name, description, or tags."""
        query_lower = query.lower()
        results = []
        for t in self._templates.values():
            if (query_lower in t.name.lower() or 
                query_lower in t.description.lower() or
                any(query_lower in tag for tag in t.tags)):
                results.append(t)
        return results
    
    def create_org_from_template(self, template_id: str, name: str,
                                description: str = None) -> Optional[Dict[str, Any]]:
        """Create an AI Organization definition from a template."""
        template = self.get_template(template_id)
        if not template:
            return None
        
        import uuid
        
        org_def = {
            "org_id": str(uuid.uuid4()),
            "name": name,
            "description": description or template.description,
            "nodes": template.nodes,
            "config": template.org_config,
            "tags": template.tags,
            "category": template.category,
            "status": "draft"
        }
        
        # Increment use count
        template.use_count += 1
        
        return org_def
