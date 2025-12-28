"""
Agent Delegate - Database operations for Agents, Versions, Templates.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Version: 1.2.2
"""

from typing import Any, Dict, List, Optional
import uuid
import json
import logging

from ..database_delegate import DatabaseDelegate

logger = logging.getLogger(__name__)


class AgentDelegate(DatabaseDelegate):
    """
    Delegate for agent-related database operations.
    
    Handles tables: agents, agent_versions, agent_templates
    """
    
    # =========================================================================
    # AGENTS
    # =========================================================================
    
    def get_all_agents(self, status: str = None, created_by: str = None,
                       agent_type: str = None) -> List[Dict]:
        """Get all agents with optional filters."""
        query = "SELECT * FROM agents"
        conditions = []
        params = []
        
        if status:
            conditions.append("status = ?")
            params.append(status)
        if created_by:
            conditions.append("created_by = ?")
            params.append(created_by)
        if agent_type:
            conditions.append("agent_type = ?")
            params.append(agent_type)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY created_at DESC"
        return self.fetch_all(query, tuple(params) if params else None) or []
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get agent by ID."""
        return self.fetch_one(
            "SELECT * FROM agents WHERE agent_id = ?",
            (agent_id,)
        )
    
    def get_agent_by_name(self, name: str) -> Optional[Dict]:
        """Get agent by name."""
        return self.fetch_one(
            "SELECT * FROM agents WHERE name = ?",
            (name,)
        )
    
    def get_agents_count(self, status: str = None) -> int:
        """Get count of agents."""
        where = f"status = '{status}'" if status else None
        return self.get_count("agents", where)
    
    def get_user_agents(self, user_id: str, status: str = None) -> List[Dict]:
        """Get agents created by a specific user."""
        query = "SELECT * FROM agents WHERE created_by = ?"
        params = [user_id]
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC"
        return self.fetch_all(query, tuple(params)) or []
    
    def create_agent(self, name: str, created_by: str, description: str = None,
                     agent_type: str = 'react', version: str = '1.0.0',
                     status: str = 'draft', config: str = '{}',
                     workflow: str = '{}', llm_config: str = '{}',
                     tools: str = '[]', hitl_config: str = '{}',
                     tags: str = '[]') -> Optional[str]:
        """Create a new agent and return agent_id."""
        agent_id = str(uuid.uuid4())
        try:
            self.execute(
                """INSERT INTO agents 
                   (agent_id, name, description, agent_type, version, status,
                    config, workflow, llm_config, tools, hitl_config, tags, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (agent_id, name, description, agent_type, version, status,
                 config, workflow, llm_config, tools, hitl_config, tags, created_by)
            )
            return agent_id
        except Exception as e:
            logger.error(f"Error creating agent: {e}")
            return None
    
    def update_agent(self, agent_id: str, **kwargs) -> bool:
        """Update agent fields."""
        if not kwargs:
            return False
        
        valid_fields = ['name', 'description', 'agent_type', 'version', 'status',
                        'config', 'workflow', 'llm_config', 'tools', 'hitl_config',
                        'tags', 'published_at', 'deprecated_at']
        
        updates = []
        params = []
        for key, value in kwargs.items():
            if key in valid_fields:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if not updates:
            return False
        
        params.append(agent_id)
        query = f"UPDATE agents SET {', '.join(updates)} WHERE agent_id = ?"
        
        try:
            self.execute(query, tuple(params))
            return True
        except Exception as e:
            logger.error(f"Error updating agent: {e}")
            return False
    
    def publish_agent(self, agent_id: str) -> bool:
        """Publish an agent."""
        try:
            self.execute(
                """UPDATE agents 
                   SET status = 'published', published_at = CURRENT_TIMESTAMP 
                   WHERE agent_id = ?""",
                (agent_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error publishing agent: {e}")
            return False
    
    def deprecate_agent(self, agent_id: str) -> bool:
        """Deprecate an agent."""
        try:
            self.execute(
                """UPDATE agents 
                   SET status = 'deprecated', deprecated_at = CURRENT_TIMESTAMP 
                   WHERE agent_id = ?""",
                (agent_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error deprecating agent: {e}")
            return False
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent."""
        try:
            self.execute("DELETE FROM agents WHERE agent_id = ?", (agent_id,))
            return True
        except Exception as e:
            logger.error(f"Error deleting agent: {e}")
            return False
    
    def agent_exists(self, agent_id: str) -> bool:
        """Check if agent exists."""
        return self.exists("agents", "agent_id = ?", (agent_id,))
    
    # =========================================================================
    # AGENT VERSIONS
    # =========================================================================
    
    def get_agent_versions(self, agent_id: str) -> List[Dict]:
        """Get all versions for an agent."""
        return self.fetch_all(
            """SELECT * FROM agent_versions 
               WHERE agent_id = ? 
               ORDER BY created_at DESC""",
            (agent_id,)
        ) or []
    
    def get_agent_version(self, agent_id: str, version: str) -> Optional[Dict]:
        """Get specific version of an agent."""
        return self.fetch_one(
            """SELECT * FROM agent_versions 
               WHERE agent_id = ? AND version = ?""",
            (agent_id, version)
        )
    
    def get_latest_version(self, agent_id: str) -> Optional[Dict]:
        """Get the latest version of an agent."""
        return self.fetch_one(
            """SELECT * FROM agent_versions 
               WHERE agent_id = ? 
               ORDER BY created_at DESC LIMIT 1""",
            (agent_id,)
        )
    
    def create_agent_version(self, agent_id: str, version: str,
                             config_snapshot: str, workflow_snapshot: str = None,
                             created_by: str = None, 
                             change_notes: str = None) -> bool:
        """Create a new agent version."""
        try:
            self.execute(
                """INSERT INTO agent_versions 
                   (agent_id, version, config_snapshot, workflow_snapshot,
                    created_by, change_notes)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (agent_id, version, config_snapshot, workflow_snapshot,
                 created_by, change_notes)
            )
            return True
        except Exception as e:
            logger.error(f"Error creating agent version: {e}")
            return False
    
    def delete_agent_versions(self, agent_id: str) -> bool:
        """Delete all versions for an agent."""
        try:
            self.execute(
                "DELETE FROM agent_versions WHERE agent_id = ?",
                (agent_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting agent versions: {e}")
            return False
    
    # =========================================================================
    # AGENT TEMPLATES
    # =========================================================================
    
    def get_all_templates(self, category: str = None) -> List[Dict]:
        """Get all agent templates."""
        query = "SELECT * FROM agent_templates"
        params = []
        if category:
            query += " WHERE category = ?"
            params.append(category)
        query += " ORDER BY use_count DESC, name"
        return self.fetch_all(query, tuple(params) if params else None) or []
    
    def get_template(self, template_id: str) -> Optional[Dict]:
        """Get template by ID."""
        return self.fetch_one(
            "SELECT * FROM agent_templates WHERE template_id = ?",
            (template_id,)
        )
    
    def get_template_categories(self) -> List[str]:
        """Get list of unique template categories."""
        results = self.fetch_all(
            "SELECT DISTINCT category FROM agent_templates ORDER BY category"
        ) or []
        return [r['category'] for r in results]
    
    def create_template(self, name: str, category: str, agent_type: str,
                        created_by: str, description: str = None,
                        icon: str = 'bi-robot', difficulty: str = 'intermediate',
                        workflow: str = '{}', llm_config: str = '{}',
                        tools: str = '[]', hitl_config: str = '{}',
                        sample_prompts: str = '[]', tags: str = '[]',
                        is_system: int = 0) -> Optional[str]:
        """Create a new template and return template_id."""
        template_id = str(uuid.uuid4())
        try:
            self.execute(
                """INSERT INTO agent_templates 
                   (template_id, name, description, category, agent_type, icon,
                    difficulty, workflow, llm_config, tools, hitl_config,
                    sample_prompts, tags, is_system, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (template_id, name, description, category, agent_type, icon,
                 difficulty, workflow, llm_config, tools, hitl_config,
                 sample_prompts, tags, is_system, created_by)
            )
            return template_id
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            return None
    
    def update_template(self, template_id: str, **kwargs) -> bool:
        """Update template fields."""
        if not kwargs:
            return False
        
        valid_fields = ['name', 'description', 'category', 'agent_type', 'icon',
                        'difficulty', 'workflow', 'llm_config', 'tools',
                        'hitl_config', 'sample_prompts', 'tags']
        
        updates = []
        params = []
        for key, value in kwargs.items():
            if key in valid_fields:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if not updates:
            return False
        
        params.append(template_id)
        query = f"UPDATE agent_templates SET {', '.join(updates)} WHERE template_id = ?"
        
        try:
            self.execute(query, tuple(params))
            return True
        except Exception as e:
            logger.error(f"Error updating template: {e}")
            return False
    
    def increment_template_usage(self, template_id: str) -> bool:
        """Increment template usage count."""
        try:
            self.execute(
                "UPDATE agent_templates SET use_count = use_count + 1 WHERE template_id = ?",
                (template_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error incrementing template usage: {e}")
            return False
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a template."""
        try:
            self.execute(
                "DELETE FROM agent_templates WHERE template_id = ?",
                (template_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting template: {e}")
            return False
    
    def template_exists(self, template_id: str) -> bool:
        """Check if template exists."""
        return self.exists("agent_templates", "template_id = ?", (template_id,))
