"""
Script Template Manager - Template library for Python Script Mode.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Version: 1.4.8
"""

import json
import logging
import os
import glob
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class ScriptTemplate:
    """Script template definition."""
    template_id: str
    name: str
    description: str
    entity_type: str  # agent, workflow, swarm, aiorg
    category: str
    difficulty: str = "intermediate"
    icon: str = "bi-file-earmark-code"
    tags: List[str] = field(default_factory=list)
    script_content: str = ""
    use_count: int = 0
    is_system: bool = True
    created_by: str = "system"
    created_at: str = ""
    agent_type: str = ""  # For agent templates: react, goal, reflect, hierarchical
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ScriptTemplateManager:
    """Manages script templates for Python Script Mode."""
    
    def __init__(self, db_facade=None):
        """Initialize with optional database facade."""
        self.db_facade = db_facade
        self._templates: Dict[str, ScriptTemplate] = {}
        self._load_json_templates()
        logger.info(f"ScriptTemplateManager initialized with {len(self._templates)} templates")
    
    def _load_json_templates(self):
        """Load script templates from JSON files in entity_definitions/scripts directory."""
        # Find templates directory relative to this file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        abhikarta_dir = os.path.dirname(script_dir)
        project_dir = os.path.dirname(abhikarta_dir)
        templates_dir = os.path.join(project_dir, 'entity_definitions', 'scripts')
        
        if not os.path.exists(templates_dir):
            logger.warning(f"Script templates directory not found: {templates_dir}")
            return
        
        json_files = glob.glob(os.path.join(templates_dir, '*.json'))
        logger.info(f"Found {len(json_files)} JSON script template files in {templates_dir}")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Create ScriptTemplate from JSON
                template = ScriptTemplate(
                    template_id=data.get('template_id', os.path.basename(json_file).replace('.json', '')),
                    name=data.get('name', 'Unnamed Template'),
                    description=data.get('description', ''),
                    entity_type=data.get('entity_type', 'agent'),
                    category=data.get('category', 'general'),
                    difficulty=data.get('difficulty', 'intermediate'),
                    icon=data.get('icon', 'bi-file-earmark-code'),
                    tags=data.get('tags', []),
                    script_content=data.get('script_content', ''),
                    use_count=data.get('use_count', 0),
                    is_system=True,
                    created_by='system',
                    created_at=datetime.now().isoformat(),
                    agent_type=data.get('agent_type', '')
                )
                
                self._templates[template.template_id] = template
                logger.debug(f"Loaded script template: {template.name}")
                
            except Exception as e:
                logger.error(f"Error loading script template from {json_file}: {e}")
    
    def get_all_templates(self) -> List[ScriptTemplate]:
        """Get all script templates."""
        return list(self._templates.values())
    
    def get_templates_by_type(self, entity_type: str) -> List[ScriptTemplate]:
        """Get templates filtered by entity type."""
        return [t for t in self._templates.values() if t.entity_type == entity_type]
    
    def get_template(self, template_id: str) -> Optional[ScriptTemplate]:
        """Get a specific template by ID."""
        return self._templates.get(template_id)
    
    def get_template_content(self, template_id: str) -> Optional[str]:
        """Get just the script content for a template."""
        template = self._templates.get(template_id)
        return template.script_content if template else None
    
    def get_categories(self) -> List[str]:
        """Get unique categories across all templates."""
        categories = set()
        for template in self._templates.values():
            categories.add(template.category)
        return sorted(list(categories))
    
    def get_agent_types(self) -> List[str]:
        """Get unique agent types for agent templates."""
        agent_types = set()
        for template in self._templates.values():
            if template.entity_type == 'agent' and template.agent_type:
                agent_types.add(template.agent_type)
        return sorted(list(agent_types))
    
    def search_templates(self, query: str, entity_type: str = None) -> List[ScriptTemplate]:
        """Search templates by name, description, or tags."""
        query = query.lower()
        results = []
        
        for template in self._templates.values():
            if entity_type and template.entity_type != entity_type:
                continue
            
            # Search in name, description, and tags
            if (query in template.name.lower() or 
                query in template.description.lower() or
                any(query in tag.lower() for tag in template.tags)):
                results.append(template)
        
        return results
    
    def increment_use_count(self, template_id: str):
        """Increment the use count for a template."""
        if template_id in self._templates:
            self._templates[template_id].use_count += 1
    
    def to_dict_list(self, templates: List[ScriptTemplate] = None) -> List[Dict[str, Any]]:
        """Convert templates to list of dictionaries."""
        if templates is None:
            templates = self.get_all_templates()
        return [t.to_dict() for t in templates]


# Global instance
_script_template_manager = None


def get_script_template_manager(db_facade=None) -> ScriptTemplateManager:
    """Get or create the global script template manager instance."""
    global _script_template_manager
    if _script_template_manager is None:
        _script_template_manager = ScriptTemplateManager(db_facade)
    return _script_template_manager
