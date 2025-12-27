"""
Agent Routes Module - Handles agent management routes and functionality

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This document and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use of this document or the software
system it describes is strictly prohibited without explicit written permission from the
copyright holder. This document is provided "as is" without warranty of any kind, either
expressed or implied. The copyright holder shall not be liable for any damages arising
from the use of this document or the software system it describes.

Patent Pending: Certain architectural patterns and implementations described in this
document may be subject to patent applications.
"""

from flask import render_template, request, redirect, url_for, session, flash, jsonify
import logging
import json

from .abstract_routes import AbstractRoutes, admin_required, login_required
from abhikarta.agent import AgentManager, AgentTemplateManager

logger = logging.getLogger(__name__)


# Color mapping for agent types
AGENT_TYPE_COLORS = {
    'react': '#6f42c1',
    'plan_and_execute': '#0d6efd',
    'tool_calling': '#fd7e14',
    'conversational': '#20c997',
    'retrieval': '#17a2b8',
    'custom': '#6c757d'
}


class AgentRoutes(AbstractRoutes):
    """
    Handles agent management routes including:
    - Agent CRUD operations
    - Visual Agent Designer
    - Template Library
    - Agent testing and execution
    """
    
    def __init__(self, app):
        """Initialize AgentRoutes with managers."""
        super().__init__(app)
        self.agent_manager = None
        self.template_manager = None
        logger.info("AgentRoutes initialized")
    
    def _ensure_managers(self):
        """Ensure agent and template managers are initialized."""
        if self.agent_manager is None:
            self.agent_manager = AgentManager(self.db_facade)
        if self.template_manager is None:
            self.template_manager = AgentTemplateManager(self.db_facade)
    
    def register_routes(self):
        """Register all agent routes."""
        
        # ============================================
        # AGENT LIST AND MANAGEMENT
        # ============================================
        
        @self.app.route('/admin/agents')
        @admin_required
        def admin_agents():
            """List all agents for admin management."""
            self._ensure_managers()
            
            agents = self.agent_manager.list_agents()
            stats = self.agent_manager.get_statistics()
            agent_types = self.agent_manager.get_agent_types()
            
            return render_template('agents/list.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   agents=agents,
                                   stats=stats,
                                   agent_types=agent_types)
        
        @self.app.route('/admin/agents/new')
        @admin_required
        def agent_create():
            """Display create agent form."""
            self._ensure_managers()
            agent_types = self.agent_manager.get_agent_types()
            
            return render_template('agents/create.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   agent_types=agent_types)
        
        @self.app.route('/admin/agents/create', methods=['POST'])
        @admin_required
        def create_agent():
            """Create a new agent."""
            self._ensure_managers()
            
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            agent_type = request.form.get('agent_type', 'react')
            llm_provider = request.form.get('llm_provider', 'openai')
            model = request.form.get('model', 'gpt-4o')
            
            if not name:
                flash('Agent name is required', 'error')
                return redirect(url_for('admin_agents'))
            
            try:
                agent = self.agent_manager.create_agent(
                    name=name,
                    description=description,
                    agent_type=agent_type,
                    created_by=session.get('user_id'),
                    config={
                        'llm_config': {
                            'provider': llm_provider,
                            'model': model
                        }
                    }
                )
                
                flash(f'Agent "{name}" created successfully!', 'success')
                self.log_audit('create_agent', 'agent', agent.agent_id)
                
                # Redirect to designer
                return redirect(url_for('agent_designer', agent_id=agent.agent_id))
                
            except Exception as e:
                logger.error(f"Error creating agent: {e}")
                flash(f'Error creating agent: {str(e)}', 'error')
                return redirect(url_for('admin_agents'))
        
        @self.app.route('/agents/<agent_id>')
        @login_required
        def view_agent(agent_id):
            """View agent details."""
            self._ensure_managers()
            
            agent = self.agent_manager.get_agent(agent_id)
            if not agent:
                flash('Agent not found', 'error')
                return redirect(url_for('admin_agents'))
            
            return render_template('agents/detail.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   agent=agent)
        
        # ============================================
        # VISUAL AGENT DESIGNER
        # ============================================
        
        @self.app.route('/admin/agents/<agent_id>/designer')
        @admin_required
        def agent_designer(agent_id):
            """Visual agent designer interface."""
            self._ensure_managers()
            
            agent = self.agent_manager.get_agent(agent_id)
            if not agent:
                flash('Agent not found', 'error')
                return redirect(url_for('admin_agents'))
            
            # Get LLM providers and models for dropdowns
            providers = self.db_facade.fetch_all(
                "SELECT * FROM llm_providers WHERE is_active = 1 ORDER BY name"
            ) or []
            models = self.db_facade.fetch_all(
                "SELECT * FROM llm_models WHERE is_active = 1 ORDER BY provider_id, display_name"
            ) or []
            
            return render_template('agents/designer.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   agent=agent,
                                   providers=providers,
                                   models=models)
        
        @self.app.route('/admin/agents/designer/new')
        @admin_required
        def new_agent_designer():
            """Visual designer for a new agent (unsaved)."""
            # Get LLM providers and models for dropdowns
            providers = self.db_facade.fetch_all(
                "SELECT * FROM llm_providers WHERE is_active = 1 ORDER BY name"
            ) or []
            models = self.db_facade.fetch_all(
                "SELECT * FROM llm_models WHERE is_active = 1 ORDER BY provider_id, display_name"
            ) or []
            
            return render_template('agents/designer.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   agent=None,
                                   providers=providers,
                                   models=models)
        
        # ============================================
        # TEMPLATE LIBRARY
        # ============================================
        
        @self.app.route('/admin/agents/templates')
        @admin_required
        def agent_templates():
            """Browse template library."""
            self._ensure_managers()
            
            templates = self.template_manager.list_templates()
            categories = self.template_manager.get_categories()
            
            # Helper function for template colors
            def get_color(agent_type):
                return AGENT_TYPE_COLORS.get(agent_type, '#6c757d')
            
            return render_template('agents/templates.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   templates=templates,
                                   categories=categories,
                                   get_color=get_color)
        
        @self.app.route('/admin/agents/templates/create', methods=['POST'])
        @admin_required
        def create_agent_from_template():
            """Create a new agent from a template."""
            self._ensure_managers()
            
            template_id = request.form.get('template_id')
            agent_name = request.form.get('agent_name', '').strip()
            description = request.form.get('description', '').strip()
            
            if not template_id or not agent_name:
                flash('Template and agent name are required', 'error')
                return redirect(url_for('agent_templates'))
            
            try:
                agent = self.template_manager.create_agent_from_template(
                    template_id=template_id,
                    name=agent_name,
                    created_by=session.get('user_id'),
                    agent_manager=self.agent_manager
                )
                
                if agent:
                    if description:
                        agent.description = description
                        self.agent_manager.update_agent(agent.agent_id, 
                                                        {'description': description})
                    
                    flash(f'Agent "{agent_name}" created from template!', 'success')
                    self.log_audit('create_from_template', 'agent', agent.agent_id,
                                   {'template': template_id})
                    return redirect(url_for('agent_designer', agent_id=agent.agent_id))
                else:
                    flash('Template not found', 'error')
                    
            except Exception as e:
                logger.error(f"Error creating agent from template: {e}")
                flash(f'Error: {str(e)}', 'error')
            
            return redirect(url_for('agent_templates'))
        
        # ============================================
        # AGENT TESTING
        # ============================================
        
        @self.app.route('/agents/<agent_id>/test')
        @login_required
        def test_agent(agent_id):
            """Agent testing interface."""
            self._ensure_managers()
            
            agent = self.agent_manager.get_agent(agent_id)
            if not agent:
                flash('Agent not found', 'error')
                return redirect(url_for('admin_agents'))
            
            return render_template('agents/test.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   agent=agent)
        
        # Note: User agent routes (/user/agents, /user/agents/<id>/execute) 
        # are registered in UserRoutes to avoid duplication
        
        # ============================================
        # API ENDPOINTS
        # ============================================
        
        @self.app.route('/api/agents/<agent_id>/workflow', methods=['PUT'])
        @admin_required
        def api_update_agent_workflow(agent_id):
            """API: Update agent workflow (from visual designer)."""
            self._ensure_managers()
            
            try:
                data = request.get_json()
                workflow = data.get('workflow', {})
                
                agent = self.agent_manager.update_workflow(agent_id, workflow)
                
                if agent:
                    return jsonify({
                        'success': True,
                        'message': 'Workflow updated',
                        'agent_id': agent_id
                    })
                else:
                    return jsonify({'error': 'Agent not found'}), 404
                    
            except Exception as e:
                logger.error(f"Error updating workflow: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/agents/<agent_id>', methods=['DELETE'])
        @admin_required
        def api_delete_agent(agent_id):
            """API: Delete an agent."""
            self._ensure_managers()
            
            try:
                if self.agent_manager.delete_agent(agent_id):
                    self.log_audit('delete_agent', 'agent', agent_id)
                    return jsonify({'success': True})
                else:
                    return jsonify({'error': 'Failed to delete agent'}), 500
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/agents/<agent_id>/status', methods=['PUT'])
        @admin_required
        def api_change_agent_status(agent_id):
            """API: Change agent status."""
            self._ensure_managers()
            
            try:
                data = request.get_json()
                new_status = data.get('status')
                
                agent = self.agent_manager.change_status(
                    agent_id, new_status, session.get('user_id')
                )
                
                if agent:
                    self.log_audit('change_status', 'agent', agent_id, 
                                   {'new_status': new_status})
                    return jsonify({
                        'success': True,
                        'status': agent.status
                    })
                else:
                    return jsonify({'error': 'Invalid status transition'}), 400
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/templates/<template_id>')
        @login_required
        def api_get_template(template_id):
            """API: Get template details."""
            self._ensure_managers()
            
            template = self.template_manager.get_template(template_id)
            if template:
                return jsonify(template.to_dict())
            return jsonify({'error': 'Template not found'}), 404
        
        logger.info("Agent routes registered")
