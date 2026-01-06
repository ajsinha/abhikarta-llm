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

from flask import render_template, request, redirect, url_for, session, flash, jsonify, Response
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


def generate_agent_python_code(agent) -> str:
    """
    Generate Python SDK code for an agent configuration.
    
    Args:
        agent: Agent object with configuration
        
    Returns:
        Python code string
    """
    code_lines = [
        '"""',
        f'Agent: {agent.name}',
        f'Description: {agent.description}',
        f'Type: {agent.agent_type}',
        f'Generated from Abhikarta-LLM',
        '"""',
        '',
        'from abhikarta_client import AbhikartaClient',
        'from abhikarta_embedded import Agent, Workflow',
        '',
        '# Initialize client (for remote execution)',
        'client = AbhikartaClient(',
        '    base_url="http://localhost:5000",',
        '    api_key="your_api_key_here"',
        ')',
        '',
        '# Agent configuration',
        f'AGENT_ID = "{agent.agent_id}"',
        f'AGENT_NAME = "{agent.name}"',
        '',
        '# LLM Configuration',
        'llm_config = ' + json.dumps(agent.llm_config or {}, indent=4),
        '',
        '# Tools',
        'tools = ' + json.dumps(agent.tools or [], indent=4),
        '',
    ]
    
    # Add workflow if exists
    if agent.workflow:
        code_lines.extend([
            '# Workflow Definition',
            'workflow = ' + json.dumps(
                agent.workflow if isinstance(agent.workflow, dict) else {},
                indent=4,
                default=str
            ),
            '',
        ])
    
    # Add full config
    code_lines.extend([
        '# Full Agent Configuration',
        'agent_config = ' + json.dumps(agent.to_dict(), indent=4, default=str),
        '',
        '',
        '# ============================================',
        '# Option 1: Use existing agent via API',
        '# ============================================',
        '',
        'def run_existing_agent(input_text: str):',
        '    """Execute the agent via API."""',
        '    result = client.agents.execute(',
        f'        agent_id="{agent.agent_id}",',
        '        input=input_text',
        '    )',
        '    return result',
        '',
        '',
        '# ============================================',
        '# Option 2: Create agent programmatically',
        '# ============================================',
        '',
        'def create_agent_from_config():',
        '    """Create agent using SDK."""',
        '    agent = Agent(',
        f'        name="{agent.name}",',
        f'        description="{agent.description}",',
        f'        agent_type="{agent.agent_type}",',
        '        llm_config=llm_config,',
        '        tools=tools',
        '    )',
        '    return agent',
        '',
        '',
        '# ============================================',
        '# Option 3: Local embedded execution',
        '# ============================================',
        '',
        'def run_local():', 
        '    """Run agent locally using embedded SDK."""',
        '    from abhikarta_embedded import create_agent',
        '    ',
        '    agent = create_agent(',
        '        config=agent_config,',
        '        llm_config=llm_config',
        '    )',
        '    ',
        '    result = agent.run("Your input here")',
        '    return result',
        '',
        '',
        'if __name__ == "__main__":',
        '    # Example usage',
        '    print(f"Agent: {AGENT_NAME}")',
        '    print(f"ID: {AGENT_ID}")',
        '    ',
        '    # Run via API',
        '    # result = run_existing_agent("Hello, agent!")',
        '    # print(result)',
        '',
    ])
    
    return '\n'.join(code_lines)


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
            
            # Get optional status filter
            status_filter = request.args.get('status', '')
            
            if status_filter:
                agents = self.agent_manager.list_agents(status=status_filter)
            else:
                agents = self.agent_manager.list_agents()
            
            stats = self.agent_manager.get_statistics()
            agent_types = self.agent_manager.get_agent_types()
            
            return render_template('agents/list.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   agents=agents,
                                   stats=stats,
                                   agent_types=agent_types,
                                   status_filter=status_filter)
        
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
                logger.error(f"Error creating agent: {e}", exc_info=True)
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
        
        @self.app.route('/admin/agents/templates/<template_id>')
        @admin_required
        def agent_template_detail(template_id):
            """View template details."""
            self._ensure_managers()
            
            template = self.template_manager.get_template(template_id)
            if not template:
                flash('Template not found', 'error')
                return redirect(url_for('agent_templates'))
            
            # Helper function for template colors
            def get_color(agent_type):
                return AGENT_TYPE_COLORS.get(agent_type, '#6c757d')
            
            return render_template('agents/template_detail.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   template=template,
                                   get_color=get_color)
        
        @self.app.route('/admin/agents/templates/<template_id>/create')
        @admin_required
        def create_agent_from_template_page(template_id):
            """Show create agent from template page."""
            self._ensure_managers()
            
            template = self.template_manager.get_template(template_id)
            if not template:
                flash('Template not found', 'error')
                return redirect(url_for('agent_templates'))
            
            # Helper function for template colors
            def get_color(agent_type):
                return AGENT_TYPE_COLORS.get(agent_type, '#6c757d')
            
            return render_template('agents/create_from_template.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   template=template,
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
                    
                    # Apply admin-configured LLM defaults using the resolver
                    try:
                        from abhikarta.services.llm_config_resolver import get_llm_config_resolver
                        resolver = get_llm_config_resolver(self.db_facade)
                        admin_defaults = resolver.get_admin_defaults()
                        
                        # Update agent llm_config with admin defaults for missing values
                        current_config = agent.llm_config or {}
                        
                        if not current_config.get('provider'):
                            current_config['provider'] = admin_defaults.get('provider', 'ollama')
                        if not current_config.get('model'):
                            current_config['model'] = admin_defaults.get('model', 'llama3.2:3b')
                        if not current_config.get('base_url'):
                            current_config['base_url'] = admin_defaults.get('base_url', '')
                        if current_config.get('temperature') is None:
                            current_config['temperature'] = admin_defaults.get('temperature', 0.7)
                        
                        self.agent_manager.update_agent(agent.agent_id, 
                                                        {'llm_config': current_config})
                        
                        logger.info(f"Applied admin LLM defaults to agent: {admin_defaults.get('provider')}, {admin_defaults.get('model')}")
                            
                    except Exception as prov_err:
                        logger.warning(f"Could not apply provider settings: {prov_err}")
                    
                    flash(f'Agent "{agent_name}" created from template!', 'success')
                    self.log_audit('create_from_template', 'agent', agent.agent_id,
                                   {'template': template_id})
                    return redirect(url_for('agent_designer', agent_id=agent.agent_id))
                else:
                    flash('Template not found', 'error')
                    
            except Exception as e:
                logger.error(f"Error creating agent from template: {e}", exc_info=True)
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
                logger.error(f"Error updating workflow: {e}", exc_info=True)
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
        
        # ============================================
        # AGENT EXPORT & EDIT ROUTES
        # ============================================
        
        @self.app.route('/admin/agents/<agent_id>/export/json')
        @admin_required
        def export_agent_json(agent_id):
            """Export agent configuration as JSON file."""
            self._ensure_managers()
            
            agent = self.agent_manager.get_agent(agent_id)
            if not agent:
                flash('Agent not found', 'error')
                return redirect(url_for('admin_agents'))
            
            agent_dict = agent.to_dict()
            
            # Create downloadable JSON response
            response = Response(
                json.dumps(agent_dict, indent=2, default=str),
                mimetype='application/json',
                headers={
                    'Content-Disposition': f'attachment; filename=agent_{agent.name.lower().replace(" ", "_")}_{agent_id}.json'
                }
            )
            return response
        
        @self.app.route('/admin/agents/<agent_id>/export/python')
        @admin_required
        def export_agent_python(agent_id):
            """Export agent as Python SDK code."""
            self._ensure_managers()
            
            agent = self.agent_manager.get_agent(agent_id)
            if not agent:
                flash('Agent not found', 'error')
                return redirect(url_for('admin_agents'))
            
            # Generate Python SDK code
            python_code = generate_agent_python_code(agent)
            
            # Create downloadable Python file
            response = Response(
                python_code,
                mimetype='text/x-python',
                headers={
                    'Content-Disposition': f'attachment; filename=agent_{agent.name.lower().replace(" ", "_")}.py'
                }
            )
            return response
        
        @self.app.route('/api/agents/<agent_id>/json')
        @admin_required
        def api_agent_json(agent_id):
            """API: Get full agent JSON configuration."""
            self._ensure_managers()
            
            agent = self.agent_manager.get_agent(agent_id)
            if not agent:
                return jsonify({'error': 'Agent not found'}), 404
            
            return jsonify(agent.to_dict())
        
        @self.app.route('/api/agents/<agent_id>/python')
        @admin_required
        def api_agent_python(agent_id):
            """API: Get agent as Python SDK code."""
            self._ensure_managers()
            
            agent = self.agent_manager.get_agent(agent_id)
            if not agent:
                return jsonify({'error': 'Agent not found'}), 404
            
            python_code = generate_agent_python_code(agent)
            return Response(python_code, mimetype='text/plain')
        
        @self.app.route('/admin/agents/<agent_id>/edit', methods=['GET', 'POST'])
        @admin_required
        def edit_agent(agent_id):
            """Edit agent properties."""
            self._ensure_managers()
            
            agent = self.agent_manager.get_agent(agent_id)
            if not agent:
                flash('Agent not found', 'error')
                return redirect(url_for('admin_agents'))
            
            if request.method == 'POST':
                try:
                    # Get form data
                    name = request.form.get('name', '').strip()
                    description = request.form.get('description', '').strip()
                    tags = request.form.get('tags', '').strip()
                    
                    # Parse tags
                    tag_list = [t.strip() for t in tags.split(',') if t.strip()]
                    
                    # Build updates dict
                    updates = {
                        'name': name,
                        'description': description,
                        'tags': tag_list
                    }
                    
                    # Update agent
                    updated = self.agent_manager.update_agent(agent_id, updates)
                    
                    if updated:
                        self.log_audit('update_agent', 'agent', agent_id)
                        flash('Agent updated successfully', 'success')
                    else:
                        flash('Failed to update agent', 'error')
                    
                    return redirect(url_for('view_agent', agent_id=agent_id))
                    
                except Exception as e:
                    logger.error(f"Error updating agent: {e}", exc_info=True)
                    flash(f'Error: {str(e)}', 'error')
            
            agent_types = self.agent_manager.get_agent_types()
            
            return render_template('agents/edit.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   agent=agent,
                                   agent_types=agent_types)
        
        @self.app.route('/admin/agents/<agent_id>/edit/json', methods=['POST'])
        @admin_required
        def edit_agent_json(agent_id):
            """Update agent from raw JSON."""
            self._ensure_managers()
            
            try:
                data = request.get_json()
                
                # Don't allow changing agent_id or status via JSON edit
                if 'agent_id' in data:
                    del data['agent_id']
                if 'status' in data:
                    del data['status']
                if 'created_at' in data:
                    del data['created_at']
                if 'created_by' in data:
                    del data['created_by']
                
                # Update agent with provided fields
                updated = self.agent_manager.update_agent(agent_id, data)
                
                if updated:
                    self.log_audit('update_agent_json', 'agent', agent_id)
                    return jsonify({'success': True, 'agent': updated.to_dict()})
                else:
                    return jsonify({'error': 'Failed to update agent'}), 500
                    
            except Exception as e:
                logger.error(f"Error updating agent from JSON: {e}", exc_info=True)
                return jsonify({'error': str(e)}), 500
        
        logger.info("Agent routes registered")
