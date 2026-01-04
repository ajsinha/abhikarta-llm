"""
Script Template Manager - Manages Python script templates.

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
    agent_type: str = ""  # For agent templates: react, goal, reflect, hierarchical
    is_system: bool = True
    created_by: str = "system"
    created_at: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ScriptTemplateManager:
    """Manages script templates including built-in and custom templates."""
    
    def __init__(self, db_facade=None):
        """Initialize with optional database facade."""
        self.db_facade = db_facade
        self._templates: Dict[str, ScriptTemplate] = {}
        self._load_json_templates()
        logger.info(f"ScriptTemplateManager initialized with {len(self._templates)} templates")
    
    def _load_json_templates(self):
        """Load script templates from JSON files in entity_definitions/scripts directory."""
        # Path: script_template.py -> utils -> abhikarta -> src -> abhikarta-main/entity_definitions
        current_dir = os.path.dirname(os.path.abspath(__file__))
        abhikarta_dir = os.path.dirname(current_dir)
        src_dir = os.path.dirname(abhikarta_dir)
        main_dir = os.path.dirname(src_dir)  # abhikarta-main/
        templates_dir = os.path.join(main_dir, 'entity_definitions', 'scripts')
        
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
                    agent_type=data.get('agent_type', ''),
                    is_system=True,
                    created_by='system',
                    created_at=datetime.now().isoformat()
                )
                
                self._templates[template.template_id] = template
                logger.debug(f"Loaded script template: {template.name}")
                
            except Exception as e:
                logger.error(f"Error loading script template from {json_file}: {e}")
    
    def get_all_templates(self) -> List[ScriptTemplate]:
        """Get all available templates."""
        return list(self._templates.values())
    
    def get_template(self, template_id: str) -> Optional[ScriptTemplate]:
        """Get a specific template by ID."""
        return self._templates.get(template_id)
    
    def get_templates_by_type(self, entity_type: str) -> List[ScriptTemplate]:
        """Get templates filtered by entity type."""
        return [t for t in self._templates.values() if t.entity_type == entity_type]
    
    def get_templates_by_agent_type(self, agent_type: str) -> List[ScriptTemplate]:
        """Get agent templates filtered by agent type (react, goal, etc.)."""
        return [t for t in self._templates.values() 
                if t.entity_type == 'agent' and t.agent_type == agent_type]
    
    def get_categories(self, entity_type: str = None) -> List[str]:
        """Get list of unique categories."""
        if entity_type:
            templates = self.get_templates_by_type(entity_type)
        else:
            templates = list(self._templates.values())
        return list(set(t.category for t in templates))
    
    def search_templates(self, query: str, entity_type: str = None) -> List[ScriptTemplate]:
        """Search templates by name, description, or tags."""
        query_lower = query.lower()
        results = []
        
        for template in self._templates.values():
            if entity_type and template.entity_type != entity_type:
                continue
            
            if (query_lower in template.name.lower() or
                query_lower in template.description.lower() or
                any(query_lower in tag.lower() for tag in template.tags)):
                results.append(template)
        
        return results
    
    def increment_use_count(self, template_id: str) -> bool:
        """Increment the use count for a template."""
        template = self._templates.get(template_id)
        if template:
            template.use_count += 1
            return True
        return False
    
    def add_custom_template(self, template_data: Dict[str, Any]) -> Optional[ScriptTemplate]:
        """Add a custom template."""
        try:
            template = ScriptTemplate(
                template_id=template_data.get('template_id', f"custom_{datetime.now().strftime('%Y%m%d%H%M%S')}"),
                name=template_data.get('name', 'Custom Template'),
                description=template_data.get('description', ''),
                entity_type=template_data.get('entity_type', 'agent'),
                category=template_data.get('category', 'custom'),
                difficulty=template_data.get('difficulty', 'intermediate'),
                icon=template_data.get('icon', 'bi-file-earmark-code'),
                tags=template_data.get('tags', ['custom']),
                script_content=template_data.get('script_content', ''),
                agent_type=template_data.get('agent_type', ''),
                is_system=False,
                created_by=template_data.get('created_by', 'user'),
                created_at=datetime.now().isoformat()
            )
            
            self._templates[template.template_id] = template
            return template
        except Exception as e:
            logger.error(f"Error adding custom template: {e}")
            return None


# Global instance
_script_template_manager: Optional[ScriptTemplateManager] = None


def get_script_template_manager(db_facade=None) -> ScriptTemplateManager:
    """Get or create the global script template manager."""
    global _script_template_manager
    if _script_template_manager is None:
        _script_template_manager = ScriptTemplateManager(db_facade)
    return _script_template_manager
