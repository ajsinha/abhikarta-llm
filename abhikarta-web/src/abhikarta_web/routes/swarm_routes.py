"""
Swarm Routes - Web routes for swarm management.

Provides routes for:
- Listing and viewing swarms
- Visual swarm designer
- Starting/stopping swarms
- Monitoring swarm execution
- API endpoints for swarm operations

Version: 1.4.8
Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import json
import logging
from datetime import datetime
from functools import wraps
from flask import (
    render_template, request, redirect, url_for,
    flash, jsonify, session, Response
)

from .abstract_routes import AbstractRoutes, login_required, admin_required

logger = logging.getLogger(__name__)


class SwarmRoutes(AbstractRoutes):
    """
    Routes for swarm management.
    """
    
    def register_routes(self):
        """Register all swarm routes."""
        self._register_list_routes()
        self._register_template_routes()
        self._register_designer_routes()
        self._register_execution_routes()
        self._register_api_routes()
        self._register_export_routes()
    
    # =========================================================================
    # LIST ROUTES
    # =========================================================================
    
    def _register_list_routes(self):
        """Register list and view routes."""
        
        @self.app.route('/swarms')
        @login_required
        def list_swarms():
            """List all swarms."""
            try:
                swarms = self.db_facade.fetch_all(
                    """SELECT s.*, 
                              (SELECT COUNT(*) FROM swarm_agents WHERE swarm_id = s.swarm_id) as agent_count,
                              (SELECT COUNT(*) FROM swarm_triggers WHERE swarm_id = s.swarm_id) as trigger_count
                       FROM swarms s 
                       WHERE s.status != 'deleted'
                       ORDER BY s.updated_at DESC"""
                ) or []
                
                return render_template(
                    'swarms/list.html',
                    swarms=swarms,
                    fullname=session.get('fullname'),
                    userid=session.get('user_id'),
                    roles=session.get('roles', []),
                    is_admin=session.get('is_admin', False)
                )
            except Exception as e:
                logger.error(f"Error listing swarms: {e}", exc_info=True)
                flash(f"Error loading swarms: {e}", "danger")
                return redirect(url_for('dashboard'))
        
        @self.app.route('/swarms/<swarm_id>')
        @login_required
        def view_swarm(swarm_id):
            """View swarm details."""
            try:
                swarm = self.db_facade.fetch_one(
                    "SELECT * FROM swarms WHERE swarm_id = ?",
                    (swarm_id,)
                )
                
                if not swarm:
                    flash("Swarm not found", "warning")
                    return redirect(url_for('list_swarms'))
                
                # Convert to mutable dict and parse config_json
                swarm = dict(swarm)
                if swarm.get('config_json'):
                    try:
                        swarm['config'] = json.loads(swarm['config_json'])
                    except:
                        swarm['config'] = {}
                else:
                    swarm['config'] = {}
                
                # Get agents
                agents = self.db_facade.fetch_all(
                    "SELECT * FROM swarm_agents WHERE swarm_id = ? ORDER BY role, agent_name",
                    (swarm_id,)
                ) or []
                
                # Get triggers
                triggers = self.db_facade.fetch_all(
                    "SELECT * FROM swarm_triggers WHERE swarm_id = ?",
                    (swarm_id,)
                ) or []
                
                # Get recent executions
                executions = self.db_facade.fetch_all(
                    """SELECT * FROM swarm_executions 
                       WHERE swarm_id = ? 
                       ORDER BY started_at DESC LIMIT 20""",
                    (swarm_id,)
                ) or []
                
                return render_template(
                    'swarms/view.html',
                    swarm=swarm,
                    agents=agents,
                    triggers=triggers,
                    executions=executions,
                    fullname=session.get('fullname'),
                    userid=session.get('user_id'),
                    roles=session.get('roles', []),
                    is_admin=session.get('is_admin', False)
                )
            except Exception as e:
                logger.error(f"Error viewing swarm: {e}", exc_info=True)
                flash(f"Error: {e}", "danger")
                return redirect(url_for('list_swarms'))
        
        @self.app.route('/swarms/new', methods=['GET', 'POST'])
        @login_required
        def swarm_create():
            """Simple form to create a new swarm."""
            if request.method == 'POST':
                try:
                    import uuid
                    swarm_id = str(uuid.uuid4())
                    name = request.form.get('name', 'New Swarm')
                    description = request.form.get('description', '')
                    
                    # Parse agent selections
                    agent_ids = request.form.getlist('agents')
                    
                    # Parse trigger config
                    trigger_type = request.form.get('trigger_type', 'user_query')
                    trigger_config = {}
                    if trigger_type == 'kafka':
                        trigger_config = {
                            'topic': request.form.get('kafka_topic', 'swarm-events'),
                            'group': request.form.get('kafka_group', 'swarm-consumer')
                        }
                    elif trigger_type == 'schedule':
                        trigger_config = {
                            'cron': request.form.get('cron_expression', '0 * * * *')
                        }
                    elif trigger_type == 'http':
                        trigger_config = {
                            'endpoint': request.form.get('http_endpoint', f'/api/swarm/{swarm_id}/webhook')
                        }
                    
                    # Build config
                    config = {
                        'triggers': [{
                            'type': trigger_type,
                            'name': f'{trigger_type.title()} Trigger',
                            'config': trigger_config
                        }],
                        'agents': []
                    }
                    
                    # Create swarm
                    self.db_facade.execute(
                        """INSERT INTO swarms 
                           (swarm_id, name, description, status, config_json, created_by)
                           VALUES (?, ?, ?, 'draft', ?, ?)""",
                        (swarm_id, name, description, json.dumps(config), session.get('user_id'))
                    )
                    
                    # Add trigger
                    self.db_facade.execute(
                        """INSERT INTO swarm_triggers 
                           (trigger_id, swarm_id, trigger_type, name, config_json)
                           VALUES (?, ?, ?, ?, ?)""",
                        (str(uuid.uuid4()), swarm_id, trigger_type, 
                         f'{trigger_type.title()} Trigger', json.dumps(trigger_config))
                    )
                    
                    # Add selected agents
                    for agent_id in agent_ids:
                        agent = self.db_facade.fetch_one(
                            "SELECT name FROM agents WHERE agent_id = ?", (agent_id,)
                        )
                        if agent:
                            self.db_facade.execute(
                                """INSERT INTO swarm_agents 
                                   (membership_id, swarm_id, agent_id, agent_name, role, subscriptions_json)
                                   VALUES (?, ?, ?, ?, 'worker', '["task.*"]')""",
                                (str(uuid.uuid4()), swarm_id, agent_id, agent['name'])
                            )
                    
                    flash(f"Swarm '{name}' created successfully!", "success")
                    return redirect(url_for('view_swarm', swarm_id=swarm_id))
                    
                except Exception as e:
                    logger.error(f"Error creating swarm: {e}", exc_info=True)
                    flash(f"Error creating swarm: {e}", "danger")
            
            # GET - show form
            try:
                agents = self.db_facade.fetch_all(
                    "SELECT agent_id, name, description FROM agents WHERE status IN ('active', 'approved', 'published', 'draft') ORDER BY name"
                ) or []
            except:
                agents = []
            
            return render_template(
                'swarms/create.html',
                agents=agents,
                fullname=session.get('fullname'),
                userid=session.get('user_id'),
                roles=session.get('roles', []),
                is_admin=session.get('is_admin', False)
            )
        
        @self.app.route('/swarms/<swarm_id>/edit', methods=['GET', 'POST'])
        @login_required
        def edit_swarm(swarm_id):
            """Edit an existing swarm."""
            swarm = self.db_facade.fetch_one(
                "SELECT * FROM swarms WHERE swarm_id = ?", (swarm_id,)
            )
            if not swarm:
                flash("Swarm not found", "danger")
                return redirect(url_for('list_swarms'))
            
            if request.method == 'POST':
                try:
                    name = request.form.get('name', swarm['name'])
                    description = request.form.get('description', swarm.get('description', ''))
                    
                    self.db_facade.execute(
                        """UPDATE swarms 
                           SET name = ?, description = ?, updated_at = CURRENT_TIMESTAMP
                           WHERE swarm_id = ?""",
                        (name, description, swarm_id)
                    )
                    
                    flash(f"Swarm '{name}' updated successfully!", "success")
                    return redirect(url_for('view_swarm', swarm_id=swarm_id))
                    
                except Exception as e:
                    logger.error(f"Error updating swarm: {e}", exc_info=True)
                    flash(f"Error updating swarm: {e}", "danger")
            
            # GET - show edit form
            try:
                agents = self.db_facade.fetch_all(
                    "SELECT agent_id, name, description FROM agents WHERE status IN ('active', 'approved', 'published', 'draft') ORDER BY name"
                ) or []
                swarm_agents = self.db_facade.fetch_all(
                    "SELECT agent_id FROM swarm_agents WHERE swarm_id = ?", (swarm_id,)
                ) or []
                selected_agent_ids = [a['agent_id'] for a in swarm_agents]
            except:
                agents = []
                selected_agent_ids = []
            
            return render_template(
                'swarms/edit.html',
                swarm=swarm,
                agents=agents,
                selected_agent_ids=selected_agent_ids,
                fullname=session.get('fullname'),
                userid=session.get('user_id'),
                roles=session.get('roles', []),
                is_admin=session.get('is_admin', False)
            )
        
        @self.app.route('/swarms/<swarm_id>/start', methods=['POST'])
        @login_required
        def start_swarm(swarm_id):
            """Start a swarm."""
            try:
                self.db_facade.execute(
                    """UPDATE swarms 
                       SET status = 'running', updated_at = CURRENT_TIMESTAMP
                       WHERE swarm_id = ?""",
                    (swarm_id,)
                )
                flash("Swarm started successfully!", "success")
            except Exception as e:
                logger.error(f"Error starting swarm: {e}", exc_info=True)
                flash(f"Error starting swarm: {e}", "danger")
            
            return redirect(url_for('view_swarm', swarm_id=swarm_id))
        
        @self.app.route('/swarms/<swarm_id>/stop', methods=['POST'])
        @login_required
        def stop_swarm(swarm_id):
            """Stop a swarm."""
            try:
                self.db_facade.execute(
                    """UPDATE swarms 
                       SET status = 'stopped', updated_at = CURRENT_TIMESTAMP
                       WHERE swarm_id = ?""",
                    (swarm_id,)
                )
                flash("Swarm stopped successfully!", "success")
            except Exception as e:
                logger.error(f"Error stopping swarm: {e}", exc_info=True)
                flash(f"Error stopping swarm: {e}", "danger")
            
            return redirect(url_for('view_swarm', swarm_id=swarm_id))
        
        @self.app.route('/swarms/<swarm_id>/executions')
        @login_required
        def swarm_executions(swarm_id):
            """List executions for a swarm."""
            swarm = self.db_facade.fetch_one(
                "SELECT * FROM swarms WHERE swarm_id = ?", (swarm_id,)
            )
            if not swarm:
                flash("Swarm not found", "danger")
                return redirect(url_for('list_swarms'))
            
            executions = self.db_facade.fetch_all(
                """SELECT * FROM swarm_executions 
                   WHERE swarm_id = ? 
                   ORDER BY started_at DESC 
                   LIMIT 100""",
                (swarm_id,)
            ) or []
            
            return render_template(
                'swarms/executions.html',
                swarm=swarm,
                executions=executions,
                fullname=session.get('fullname'),
                userid=session.get('user_id'),
                roles=session.get('roles', []),
                is_admin=session.get('is_admin', False)
            )
    
    # =========================================================================
    # TEMPLATE ROUTES
    # =========================================================================
    
    def _register_template_routes(self):
        """Register swarm template library routes."""
        
        @self.app.route('/swarms/templates')
        @login_required
        def swarm_templates():
            """Browse swarm template library."""
            from abhikarta.swarm.swarm_template import SwarmTemplateManager
            
            template_manager = SwarmTemplateManager()
            templates = template_manager.list_templates()
            categories = template_manager.get_categories()
            
            return render_template(
                'swarms/templates.html',
                templates=templates,
                categories=categories,
                fullname=session.get('fullname'),
                userid=session.get('user_id'),
                roles=session.get('roles', []),
                is_admin=session.get('is_admin', False)
            )
        
        @self.app.route('/swarms/templates/<template_id>')
        @login_required
        def swarm_template_detail(template_id):
            """View swarm template details."""
            from abhikarta.swarm.swarm_template import SwarmTemplateManager
            
            template_manager = SwarmTemplateManager()
            template = template_manager.get_template(template_id)
            
            if not template:
                flash("Template not found", "warning")
                return redirect(url_for('swarm_templates'))
            
            return render_template(
                'swarms/template_detail.html',
                template=template,
                fullname=session.get('fullname'),
                userid=session.get('user_id'),
                roles=session.get('roles', []),
                is_admin=session.get('is_admin', False)
            )
        
        @self.app.route('/swarms/templates/<template_id>/use', methods=['POST'])
        @login_required
        def use_swarm_template(template_id):
            """Create a new swarm from a template."""
            from abhikarta.swarm.swarm_template import SwarmTemplateManager
            import uuid
            
            template_manager = SwarmTemplateManager()
            template = template_manager.get_template(template_id)
            
            if not template:
                flash("Template not found", "warning")
                return redirect(url_for('swarm_templates'))
            
            try:
                # Create new swarm from template
                swarm_id = str(uuid.uuid4())
                name = request.form.get('name', f"{template.name} (Copy)")
                
                # Get swarm definition from template
                swarm_def = template.swarm_definition
                config = template.config if hasattr(template, 'config') else {}
                
                # Insert swarm record
                self.db_facade.execute(
                    """INSERT INTO swarms (swarm_id, name, description, definition_json, config_json, status, created_by)
                       VALUES (?, ?, ?, ?, ?, 'draft', ?)""",
                    (swarm_id, name, template.description, json.dumps(swarm_def), json.dumps(config), session.get('user_id'))
                )
                
                flash(f"Created swarm '{name}' from template", "success")
                return redirect(url_for('swarm_designer', swarm_id=swarm_id))
                
            except Exception as e:
                logger.error(f"Error creating swarm from template: {e}", exc_info=True)
                flash(f"Error: {e}", "danger")
                return redirect(url_for('swarm_templates'))
    
    # =========================================================================
    # DESIGNER ROUTES
    # =========================================================================
    
    def _register_designer_routes(self):
        """Register visual designer routes."""
        
        @self.app.route('/swarms/designer')
        @login_required
        def swarm_designer_new():
            """Open swarm designer for new swarm."""
            # Get available agents
            agents = self.db_facade.fetch_all(
                "SELECT agent_id, name, description FROM agents WHERE status IN ('active', 'approved', 'published', 'draft')"
            ) or []
            
            return render_template(
                'swarms/designer.html',
                swarm=None,
                agents=agents,
                fullname=session.get('fullname'),
                userid=session.get('user_id'),
                roles=session.get('roles', []),
                is_admin=session.get('is_admin', False)
            )
        
        @self.app.route('/swarms/designer/<swarm_id>')
        @login_required
        def swarm_designer(swarm_id):
            """Open swarm designer for existing swarm."""
            try:
                swarm = self.db_facade.fetch_one(
                    "SELECT * FROM swarms WHERE swarm_id = ?",
                    (swarm_id,)
                )
                
                if not swarm:
                    flash("Swarm not found", "warning")
                    return redirect(url_for('list_swarms'))
                
                # Convert to mutable dict and parse config_json
                swarm = dict(swarm)
                if swarm.get('config_json'):
                    try:
                        swarm['config_json'] = json.loads(swarm['config_json'])
                    except:
                        swarm['config_json'] = {}
                else:
                    swarm['config_json'] = {}
                
                # Get swarm agents
                swarm_agents = self.db_facade.fetch_all(
                    "SELECT * FROM swarm_agents WHERE swarm_id = ?",
                    (swarm_id,)
                ) or []
                
                # Get triggers
                triggers = self.db_facade.fetch_all(
                    "SELECT * FROM swarm_triggers WHERE swarm_id = ?",
                    (swarm_id,)
                ) or []
                
                # Get available agents
                agents = self.db_facade.fetch_all(
                    "SELECT agent_id, name, description FROM agents WHERE status IN ('active', 'approved', 'published', 'draft')"
                ) or []
                
                return render_template(
                    'swarms/designer.html',
                    swarm=swarm,
                    swarm_agents=swarm_agents,
                    triggers=triggers,
                    agents=agents,
                    fullname=session.get('fullname'),
                    userid=session.get('user_id'),
                    roles=session.get('roles', []),
                    is_admin=session.get('is_admin', False)
                )
            except Exception as e:
                logger.error(f"Error opening swarm designer: {e}", exc_info=True)
                flash(f"Error: {e}", "danger")
                return redirect(url_for('list_swarms'))
    
    # =========================================================================
    # EXECUTION ROUTES
    # =========================================================================
    
    def _register_execution_routes(self):
        """Register execution and monitoring routes."""
        
        @self.app.route('/swarms/<swarm_id>/monitor')
        @login_required
        def monitor_swarm(swarm_id):
            """Monitor a running swarm."""
            try:
                swarm = self.db_facade.fetch_one(
                    "SELECT * FROM swarms WHERE swarm_id = ?",
                    (swarm_id,)
                )
                
                if not swarm:
                    flash("Swarm not found", "warning")
                    return redirect(url_for('list_swarms'))
                
                # Get recent events
                events = self.db_facade.fetch_all(
                    """SELECT * FROM swarm_events 
                       WHERE swarm_id = ? 
                       ORDER BY created_at DESC LIMIT 100""",
                    (swarm_id,)
                ) or []
                
                # Get recent decisions
                decisions = self.db_facade.fetch_all(
                    """SELECT * FROM swarm_decisions 
                       WHERE swarm_id = ? 
                       ORDER BY created_at DESC LIMIT 50""",
                    (swarm_id,)
                ) or []
                
                return render_template(
                    'swarms/monitor.html',
                    swarm=swarm,
                    events=events,
                    decisions=decisions,
                    fullname=session.get('fullname'),
                    userid=session.get('user_id'),
                    roles=session.get('roles', []),
                    is_admin=session.get('is_admin', False)
                )
            except Exception as e:
                logger.error(f"Error monitoring swarm: {e}", exc_info=True)
                flash(f"Error: {e}", "danger")
                return redirect(url_for('list_swarms'))
        
        @self.app.route('/swarms/<swarm_id>/execution/<execution_id>')
        @login_required
        def view_swarm_execution(swarm_id, execution_id):
            """View execution details."""
            try:
                execution = self.db_facade.fetch_one(
                    "SELECT * FROM swarm_executions WHERE execution_id = ?",
                    (execution_id,)
                )
                
                if not execution:
                    flash("Execution not found", "warning")
                    return redirect(url_for('view_swarm', swarm_id=swarm_id))
                
                # Get events for this execution
                events = self.db_facade.fetch_all(
                    """SELECT * FROM swarm_events 
                       WHERE execution_id = ? 
                       ORDER BY created_at""",
                    (execution_id,)
                ) or []
                
                # Get decisions
                decisions = self.db_facade.fetch_all(
                    """SELECT * FROM swarm_decisions 
                       WHERE execution_id = ? 
                       ORDER BY created_at""",
                    (execution_id,)
                ) or []
                
                return render_template(
                    'swarms/execution.html',
                    execution=execution,
                    events=events,
                    decisions=decisions,
                    swarm_id=swarm_id,
                    fullname=session.get('fullname'),
                    userid=session.get('user_id'),
                    roles=session.get('roles', []),
                    is_admin=session.get('is_admin', False)
                )
            except Exception as e:
                logger.error(f"Error viewing execution: {e}", exc_info=True)
                flash(f"Error: {e}", "danger")
                return redirect(url_for('view_swarm', swarm_id=swarm_id))
    
    # =========================================================================
    # API ROUTES
    # =========================================================================
    
    def _register_api_routes(self):
        """Register API endpoints for swarm operations."""
        
        @self.app.route('/api/swarms', methods=['GET'])
        @login_required
        def api_list_swarms():
            """API: List all swarms."""
            try:
                swarms = self.db_facade.fetch_all(
                    "SELECT * FROM swarms WHERE status != 'deleted' ORDER BY updated_at DESC"
                ) or []
                
                return jsonify({
                    'success': True,
                    'swarms': [dict(s) for s in swarms],
                    'count': len(swarms)
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/swarms', methods=['POST'])
        @login_required
        def api_create_swarm():
            """API: Create a new swarm."""
            try:
                data = request.get_json()
                
                import uuid
                swarm_id = str(uuid.uuid4())
                
                self.db_facade.execute(
                    """INSERT INTO swarms 
                       (swarm_id, name, description, status, category, tags,
                        definition_json, config_json, created_by)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (swarm_id, data.get('name', 'New Swarm'),
                     data.get('description', ''),
                     'draft',
                     data.get('category', 'general'),
                     json.dumps(data.get('tags', [])),
                     json.dumps(data.get('definition', {})),
                     json.dumps(data.get('config', {})),
                     session.get('user_id'))
                )
                
                return jsonify({
                    'success': True,
                    'swarm_id': swarm_id,
                    'message': 'Swarm created successfully'
                })
            except Exception as e:
                logger.error(f"Error creating swarm: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/swarms/save', methods=['POST'])
        @login_required
        def api_save_swarm():
            """API: Save swarm from designer (create or update)."""
            try:
                data = request.get_json()
                import uuid
                
                swarm_id = data.get('swarm_id')
                name = data.get('name', 'New Swarm')
                triggers = data.get('triggers', [])
                agents = data.get('agents', [])
                layout = data.get('layout', {})
                
                # Build config
                config = {
                    'triggers': triggers,
                    'agents': agents,
                    'layout': layout
                }
                
                if swarm_id:
                    # Check if swarm exists
                    existing = self.db_facade.fetch_one(
                        "SELECT swarm_id FROM swarms WHERE swarm_id = ?", (swarm_id,)
                    )
                    
                    if existing:
                        # Update existing swarm
                        self.db_facade.execute(
                            """UPDATE swarms 
                               SET name = ?, config_json = ?, updated_at = CURRENT_TIMESTAMP
                               WHERE swarm_id = ?""",
                            (name, json.dumps(config), swarm_id)
                        )
                        
                        # Update swarm_agents - delete old, insert new
                        self.db_facade.execute(
                            "DELETE FROM swarm_agents WHERE swarm_id = ?", (swarm_id,)
                        )
                        
                        for agent in agents:
                            self.db_facade.execute(
                                """INSERT INTO swarm_agents 
                                   (membership_id, swarm_id, agent_id, agent_name, role, subscriptions_json, min_instances, max_instances)
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                                (str(uuid.uuid4()), swarm_id, agent.get('agent_id'), 
                                 agent.get('name', 'Agent'), agent.get('role', 'worker'),
                                 json.dumps(agent.get('subscriptions', ['task.*'])),
                                 agent.get('pool_size', {}).get('min', 1),
                                 agent.get('pool_size', {}).get('max', 3))
                            )
                        
                        # Update triggers - delete old, insert new
                        self.db_facade.execute(
                            "DELETE FROM swarm_triggers WHERE swarm_id = ?", (swarm_id,)
                        )
                        
                        for trigger in triggers:
                            self.db_facade.execute(
                                """INSERT INTO swarm_triggers 
                                   (trigger_id, swarm_id, trigger_type, name, config_json)
                                   VALUES (?, ?, ?, ?, ?)""",
                                (str(uuid.uuid4()), swarm_id, trigger.get('type', 'user_query'),
                                 trigger.get('name', 'Trigger'), json.dumps(trigger.get('config', {})))
                            )
                        
                        return jsonify({
                            'success': True,
                            'swarm_id': swarm_id,
                            'message': 'Swarm updated successfully'
                        })
                
                # Create new swarm
                swarm_id = str(uuid.uuid4())
                
                self.db_facade.execute(
                    """INSERT INTO swarms 
                       (swarm_id, name, description, status, config_json, created_by)
                       VALUES (?, ?, ?, 'draft', ?, ?)""",
                    (swarm_id, name, '', json.dumps(config), session.get('user_id'))
                )
                
                # Add agents
                for agent in agents:
                    self.db_facade.execute(
                        """INSERT INTO swarm_agents 
                           (membership_id, swarm_id, agent_id, agent_name, role, subscriptions_json, min_instances, max_instances)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (str(uuid.uuid4()), swarm_id, agent.get('agent_id'),
                         agent.get('name', 'Agent'), agent.get('role', 'worker'),
                         json.dumps(agent.get('subscriptions', ['task.*'])),
                         agent.get('pool_size', {}).get('min', 1),
                         agent.get('pool_size', {}).get('max', 3))
                    )
                
                # Add triggers
                for trigger in triggers:
                    self.db_facade.execute(
                        """INSERT INTO swarm_triggers 
                           (trigger_id, swarm_id, trigger_type, name, config_json)
                           VALUES (?, ?, ?, ?, ?)""",
                        (str(uuid.uuid4()), swarm_id, trigger.get('type', 'user_query'),
                         trigger.get('name', 'Trigger'), json.dumps(trigger.get('config', {})))
                    )
                
                return jsonify({
                    'success': True,
                    'swarm_id': swarm_id,
                    'message': 'Swarm created successfully'
                })
                
            except Exception as e:
                logger.error(f"Error saving swarm: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/swarms/<swarm_id>', methods=['PUT'])
        @login_required
        def api_update_swarm(swarm_id):
            """API: Update a swarm."""
            try:
                data = request.get_json()
                
                self.db_facade.execute(
                    """UPDATE swarms SET
                       name = ?, description = ?, category = ?, tags = ?,
                       definition_json = ?, config_json = ?, updated_at = ?
                       WHERE swarm_id = ?""",
                    (data.get('name'), data.get('description'),
                     data.get('category', 'general'),
                     json.dumps(data.get('tags', [])),
                     json.dumps(data.get('definition', {})),
                     json.dumps(data.get('config', {})),
                     datetime.utcnow().isoformat(),
                     swarm_id)
                )
                
                return jsonify({
                    'success': True,
                    'message': 'Swarm updated successfully'
                })
            except Exception as e:
                logger.error(f"Error updating swarm: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/swarms/<swarm_id>', methods=['DELETE'])
        @login_required
        def api_delete_swarm(swarm_id):
            """API: Delete a swarm."""
            try:
                self.db_facade.execute(
                    "UPDATE swarms SET status = 'deleted' WHERE swarm_id = ?",
                    (swarm_id,)
                )
                
                return jsonify({
                    'success': True,
                    'message': 'Swarm deleted successfully'
                })
            except Exception as e:
                logger.error(f"Error deleting swarm: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/swarms/<swarm_id>/start', methods=['POST'])
        @login_required
        def api_start_swarm(swarm_id):
            """API: Start a swarm."""
            try:
                # Update status
                self.db_facade.execute(
                    "UPDATE swarms SET status = 'active' WHERE swarm_id = ?",
                    (swarm_id,)
                )
                
                # TODO: Actually start the swarm through orchestrator
                
                return jsonify({
                    'success': True,
                    'message': 'Swarm started successfully'
                })
            except Exception as e:
                logger.error(f"Error starting swarm: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/swarms/<swarm_id>/stop', methods=['POST'])
        @login_required
        def api_stop_swarm(swarm_id):
            """API: Stop a swarm."""
            try:
                self.db_facade.execute(
                    "UPDATE swarms SET status = 'inactive' WHERE swarm_id = ?",
                    (swarm_id,)
                )
                
                # TODO: Actually stop the swarm through orchestrator
                
                return jsonify({
                    'success': True,
                    'message': 'Swarm stopped successfully'
                })
            except Exception as e:
                logger.error(f"Error stopping swarm: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/swarms/<swarm_id>/execute', methods=['POST'])
        @login_required
        def api_execute_swarm(swarm_id):
            """API: Execute a user query through the swarm."""
            try:
                data = request.get_json()
                query = data.get('query', '')
                
                import uuid
                import time
                from abhikarta.utils.helpers import generate_execution_id, EntityType as HelperEntityType
                
                # Get swarm info for execution ID
                swarm = self.db_facade.fetch_one(
                    "SELECT * FROM swarms WHERE swarm_id = ?",
                    (swarm_id,)
                )
                swarm_name = swarm.get('name', '') if swarm else ''
                
                execution_id = generate_execution_id(HelperEntityType.SWARM, swarm_name)
                start_time = time.time()
                
                # Create execution record
                self.db_facade.execute(
                    """INSERT INTO swarm_executions
                       (execution_id, swarm_id, trigger_type, trigger_data, status, user_id)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (execution_id, swarm_id, 'user_query',
                     json.dumps({'query': query}), 'running',
                     session.get('user_id'))
                )
                
                # Start execution logging
                try:
                    from abhikarta.services.execution_logger import get_execution_logger, EntityType
                    exec_logger = get_execution_logger()
                    
                    if exec_logger and exec_logger.config.enabled:
                        exec_log = exec_logger.start_execution(
                            execution_id=execution_id,
                            entity_type=EntityType.SWARM,
                            entity_id=swarm_id,
                            entity_name=swarm_name,
                            user_input=query
                        )
                        
                        exec_log.entity_config = {
                            'swarm_name': swarm_name,
                            'trigger_type': 'user_query'
                        }
                        
                        # Get swarm agents
                        agents = self.db_facade.fetch_all(
                            "SELECT agent_name, role FROM swarm_agents WHERE swarm_id = ?",
                            (swarm_id,)
                        ) or []
                        
                        exec_log.execution_json = {
                            'swarm_id': swarm_id,
                            'name': swarm_name,
                            'agents': [dict(a) for a in agents],
                            'query': query
                        }
                except Exception as log_err:
                    logger.debug(f"Could not start execution logging: {log_err}")
                
                # TODO: Actually execute through orchestrator
                # For now, mark as pending and return
                
                return jsonify({
                    'success': True,
                    'execution_id': execution_id,
                    'message': 'Execution started'
                })
            except Exception as e:
                logger.error(f"Error executing swarm: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/swarms/<swarm_id>/agents', methods=['GET'])
        @login_required
        def api_get_swarm_agents(swarm_id):
            """API: Get agents in a swarm."""
            try:
                agents = self.db_facade.fetch_all(
                    "SELECT * FROM swarm_agents WHERE swarm_id = ?",
                    (swarm_id,)
                ) or []
                
                return jsonify({
                    'success': True,
                    'agents': [dict(a) for a in agents]
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/swarms/<swarm_id>/agents', methods=['POST'])
        @login_required
        def api_add_swarm_agent(swarm_id):
            """API: Add agent to swarm."""
            try:
                data = request.get_json()
                
                import uuid
                membership_id = str(uuid.uuid4())
                
                self.db_facade.execute(
                    """INSERT INTO swarm_agents
                       (membership_id, swarm_id, agent_id, agent_name, role,
                        description, subscriptions_json, max_instances, min_instances)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (membership_id, swarm_id, data.get('agent_id'),
                     data.get('agent_name', ''), data.get('role', 'worker'),
                     data.get('description', ''),
                     json.dumps(data.get('subscriptions', [])),
                     data.get('max_instances', 10),
                     data.get('min_instances', 0))
                )
                
                return jsonify({
                    'success': True,
                    'membership_id': membership_id
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/swarms/<swarm_id>/triggers', methods=['GET'])
        @login_required
        def api_get_swarm_triggers(swarm_id):
            """API: Get triggers for a swarm."""
            try:
                triggers = self.db_facade.fetch_all(
                    "SELECT * FROM swarm_triggers WHERE swarm_id = ?",
                    (swarm_id,)
                ) or []
                
                return jsonify({
                    'success': True,
                    'triggers': [dict(t) for t in triggers]
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/swarms/<swarm_id>/triggers', methods=['POST'])
        @login_required
        def api_add_swarm_trigger(swarm_id):
            """API: Add trigger to swarm."""
            try:
                data = request.get_json()
                
                import uuid
                trigger_id = str(uuid.uuid4())
                
                self.db_facade.execute(
                    """INSERT INTO swarm_triggers
                       (trigger_id, swarm_id, trigger_type, name, description,
                        config_json, filter_expression)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (trigger_id, swarm_id, data.get('trigger_type', 'user_query'),
                     data.get('name', ''), data.get('description', ''),
                     json.dumps(data.get('config', {})),
                     data.get('filter_expression'))
                )
                
                return jsonify({
                    'success': True,
                    'trigger_id': trigger_id
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/swarms/<swarm_id>/events', methods=['GET'])
        @login_required
        def api_get_swarm_events(swarm_id):
            """API: Get recent events for a swarm."""
            try:
                limit = request.args.get('limit', 100, type=int)
                
                events = self.db_facade.fetch_all(
                    """SELECT * FROM swarm_events 
                       WHERE swarm_id = ? 
                       ORDER BY created_at DESC LIMIT ?""",
                    (swarm_id, limit)
                ) or []
                
                return jsonify({
                    'success': True,
                    'events': [dict(e) for e in events]
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/swarms/<swarm_id>/metrics', methods=['GET'])
        @login_required
        def api_get_swarm_metrics(swarm_id):
            """API: Get swarm metrics."""
            try:
                swarm = self.db_facade.fetch_one(
                    "SELECT * FROM swarms WHERE swarm_id = ?",
                    (swarm_id,)
                )
                
                if not swarm:
                    return jsonify({'success': False, 'error': 'Swarm not found'}), 404
                
                # Get execution stats
                exec_stats = self.db_facade.fetch_one(
                    """SELECT COUNT(*) as total,
                              SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                              SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                              AVG(duration_ms) as avg_duration
                       FROM swarm_executions WHERE swarm_id = ?""",
                    (swarm_id,)
                )
                
                # Get event count
                event_count = self.db_facade.fetch_one(
                    "SELECT COUNT(*) as count FROM swarm_events WHERE swarm_id = ?",
                    (swarm_id,)
                )
                
                return jsonify({
                    'success': True,
                    'metrics': {
                        'total_executions': exec_stats['total'] if exec_stats else 0,
                        'completed_executions': exec_stats['completed'] if exec_stats else 0,
                        'failed_executions': exec_stats['failed'] if exec_stats else 0,
                        'avg_duration_ms': exec_stats['avg_duration'] if exec_stats else 0,
                        'total_events': event_count['count'] if event_count else 0,
                        'status': swarm['status'],
                    }
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
    
    # =========================================================================
    # EXPORT, EDIT & STATUS ROUTES
    # =========================================================================
    
    def _register_export_routes(self):
        """Register export, edit and status change routes."""
        
        @self.app.route('/swarms/<swarm_id>/export/json')
        @admin_required
        def export_swarm_json(swarm_id):
            """Export swarm configuration as JSON file."""
            swarm = self.db_facade.fetch_one(
                "SELECT * FROM swarms WHERE swarm_id = ?",
                (swarm_id,)
            )
            if not swarm:
                flash('Swarm not found', 'error')
                return redirect(url_for('list_swarms'))
            
            swarm_dict = dict(swarm)
            for field in ['definition_json', 'config_json', 'tags']:
                if field in swarm_dict and isinstance(swarm_dict[field], str):
                    try:
                        swarm_dict[field] = json.loads(swarm_dict[field])
                    except:
                        pass
            
            response = Response(
                json.dumps(swarm_dict, indent=2, default=str),
                mimetype='application/json',
                headers={
                    'Content-Disposition': f'attachment; filename=swarm_{swarm["name"].lower().replace(" ", "_")}_{swarm_id}.json'
                }
            )
            return response
        
        @self.app.route('/swarms/<swarm_id>/export/python')
        @admin_required
        def export_swarm_python(swarm_id):
            """Export swarm as Python SDK code."""
            from abhikarta_web.utils.export_utils import generate_swarm_python_code
            
            swarm = self.db_facade.fetch_one(
                "SELECT * FROM swarms WHERE swarm_id = ?",
                (swarm_id,)
            )
            if not swarm:
                flash('Swarm not found', 'error')
                return redirect(url_for('list_swarms'))
            
            swarm_dict = dict(swarm)
            for field in ['definition_json', 'config_json', 'tags']:
                if field in swarm_dict and isinstance(swarm_dict[field], str):
                    try:
                        swarm_dict[field] = json.loads(swarm_dict[field])
                    except:
                        pass
            
            python_code = generate_swarm_python_code(swarm_dict)
            
            response = Response(
                python_code,
                mimetype='text/x-python',
                headers={
                    'Content-Disposition': f'attachment; filename=swarm_{swarm["name"].lower().replace(" ", "_")}.py'
                }
            )
            return response
        
        @self.app.route('/api/swarms/<swarm_id>/json')
        @admin_required
        def api_swarm_json(swarm_id):
            """API: Get full swarm JSON configuration."""
            swarm = self.db_facade.fetch_one(
                "SELECT * FROM swarms WHERE swarm_id = ?",
                (swarm_id,)
            )
            if not swarm:
                return jsonify({'error': 'Swarm not found'}), 404
            
            swarm_dict = dict(swarm)
            for field in ['definition_json', 'config_json', 'tags']:
                if field in swarm_dict and isinstance(swarm_dict[field], str):
                    try:
                        swarm_dict[field] = json.loads(swarm_dict[field])
                    except:
                        pass
            
            return jsonify(swarm_dict)
        
        @self.app.route('/api/swarms/<swarm_id>/python')
        @admin_required
        def api_swarm_python(swarm_id):
            """API: Get swarm as Python SDK code."""
            from abhikarta_web.utils.export_utils import generate_swarm_python_code
            
            swarm = self.db_facade.fetch_one(
                "SELECT * FROM swarms WHERE swarm_id = ?",
                (swarm_id,)
            )
            if not swarm:
                return jsonify({'error': 'Swarm not found'}), 404
            
            swarm_dict = dict(swarm)
            for field in ['definition_json', 'config_json', 'tags']:
                if field in swarm_dict and isinstance(swarm_dict[field], str):
                    try:
                        swarm_dict[field] = json.loads(swarm_dict[field])
                    except:
                        pass
            
            python_code = generate_swarm_python_code(swarm_dict)
            return Response(python_code, mimetype='text/plain')
        
        @self.app.route('/api/swarms/<swarm_id>/status', methods=['PUT'])
        @admin_required
        def api_change_swarm_status(swarm_id):
            """API: Change swarm status."""
            from abhikarta_web.utils.export_utils import is_valid_transition
            
            try:
                data = request.get_json()
                new_status = data.get('status')
                
                swarm = self.db_facade.fetch_one(
                    "SELECT status FROM swarms WHERE swarm_id = ?",
                    (swarm_id,)
                )
                if not swarm:
                    return jsonify({'error': 'Swarm not found'}), 404
                
                current_status = swarm['status']
                
                if not is_valid_transition(current_status, new_status):
                    return jsonify({'error': f'Invalid status transition from {current_status} to {new_status}'}), 400
                
                self.db_facade.execute(
                    "UPDATE swarms SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE swarm_id = ?",
                    (new_status, swarm_id)
                )
                
                self.log_audit('change_status', 'swarm', swarm_id, {'new_status': new_status})
                
                return jsonify({'success': True, 'status': new_status})
                
            except Exception as e:
                logger.error(f"Error changing swarm status: {e}", exc_info=True)
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/swarms/<swarm_id>/edit', methods=['POST'])
        @admin_required
        def api_edit_swarm_json(swarm_id):
            """API: Update swarm from JSON."""
            try:
                data = request.get_json()
                
                for field in ['swarm_id', 'created_at', 'created_by']:
                    if field in data:
                        del data[field]
                
                updates = []
                values = []
                for field in ['name', 'description', 'definition_json', 'config_json', 'tags', 'category']:
                    if field in data:
                        updates.append(f"{field} = ?")
                        value = data[field]
                        if isinstance(value, (dict, list)):
                            value = json.dumps(value)
                        values.append(value)
                
                if updates:
                    updates.append("updated_at = CURRENT_TIMESTAMP")
                    values.append(swarm_id)
                    
                    self.db_facade.execute(
                        f"UPDATE swarms SET {', '.join(updates)} WHERE swarm_id = ?",
                        tuple(values)
                    )
                    
                    self.log_audit('update_swarm_json', 'swarm', swarm_id)
                
                return jsonify({'success': True})
                
            except Exception as e:
                logger.error(f"Error updating swarm: {e}", exc_info=True)
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/swarms/test', methods=['POST'])
        @login_required
        def api_test_swarm_design():
            """API: Test a swarm during design time (before saving)."""
            import time
            
            try:
                data = request.get_json()
                input_text = data.get('input', '')
                swarm_config = data.get('swarm', {})
                agents = data.get('agents', [])
                
                if not input_text:
                    return jsonify({'success': False, 'error': 'Input is required'}), 400
                
                start_time = time.time()
                
                # For design-time testing, we simulate swarm behavior
                # by executing the first LLM-capable agent with the input
                output = None
                provider = 'ollama'
                model = 'llama3.2:3b'
                
                # Find an LLM config from agents
                for agent_def in agents:
                    llm_config = agent_def.get('llm_config', {})
                    if llm_config.get('provider'):
                        provider = llm_config.get('provider')
                        model = llm_config.get('model', model)
                        break
                
                # Apply admin defaults if not set
                try:
                    from abhikarta.services.llm_config_resolver import get_llm_config_resolver
                    resolver = get_llm_config_resolver(self.db_facade)
                    admin_defaults = resolver.get_admin_defaults()
                    if not provider or provider == 'ollama':
                        provider = admin_defaults.get('provider', provider)
                        model = admin_defaults.get('model', model)
                except:
                    pass
                
                try:
                    from langchain_ollama import ChatOllama
                    from langchain_openai import ChatOpenAI
                    from langchain_anthropic import ChatAnthropic
                    from langchain_core.messages import HumanMessage, SystemMessage
                    
                    # Create LLM based on provider
                    if provider.lower() == 'ollama':
                        base_url = admin_defaults.get('base_url', 'http://localhost:11434') if admin_defaults else 'http://localhost:11434'
                        llm = ChatOllama(model=model, base_url=base_url)
                    elif provider.lower() == 'openai':
                        llm = ChatOpenAI(model=model)
                    elif provider.lower() == 'anthropic':
                        llm = ChatAnthropic(model=model)
                    else:
                        llm = ChatOllama(model=model)
                    
                    # Build prompt for swarm simulation
                    swarm_name = swarm_config.get('name', 'Unnamed Swarm')
                    system_prompt = f"You are simulating a swarm named '{swarm_name}' with {len(agents)} agents. Process the user's request as a coordinated team."
                    
                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=input_text)
                    ]
                    
                    response = llm.invoke(messages)
                    output = response.content if hasattr(response, 'content') else str(response)
                    
                    duration_ms = int((time.time() - start_time) * 1000)
                    
                    return jsonify({
                        'success': True,
                        'output': output,
                        'status': 'completed',
                        'duration_ms': duration_ms,
                        'provider': provider,
                        'model': model,
                        'agents_simulated': len(agents)
                    })
                    
                except ImportError as ie:
                    return jsonify({
                        'success': False,
                        'error': f'LLM library not available: {str(ie)}',
                        'status': 'failed'
                    }), 500
                except Exception as exec_err:
                    error_msg = str(exec_err)
                    if 'not found' in error_msg.lower() or '404' in error_msg:
                        error_msg = f"Model '{model}' not found. Run 'ollama pull {model}' to install it."
                    
                    return jsonify({
                        'success': False,
                        'error': error_msg,
                        'status': 'failed',
                        'duration_ms': int((time.time() - start_time) * 1000)
                    }), 500
                    
            except Exception as e:
                logger.error(f"Error in design-time swarm test: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        logger.info("Swarm export routes registered")
