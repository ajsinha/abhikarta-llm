"""
Swarm Routes - Web routes for swarm management.

Provides routes for:
- Listing and viewing swarms
- Visual swarm designer
- Starting/stopping swarms
- Monitoring swarm execution
- API endpoints for swarm operations

Version: 1.3.0
Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import json
import logging
from datetime import datetime
from functools import wraps
from flask import (
    render_template, request, redirect, url_for,
    flash, jsonify, session
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
        self._register_designer_routes()
        self._register_execution_routes()
        self._register_api_routes()
    
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
                logger.error(f"Error listing swarms: {e}")
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
                logger.error(f"Error viewing swarm: {e}")
                flash(f"Error: {e}", "danger")
                return redirect(url_for('list_swarms'))
    
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
                "SELECT agent_id, name, description FROM agents WHERE status = 'active'"
            ) or []
            
            return render_template(
                'swarms/designer.html',
                swarm=None,
                available_agents=agents,
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
                    "SELECT agent_id, name, description FROM agents WHERE status = 'active'"
                ) or []
                
                return render_template(
                    'swarms/designer.html',
                    swarm=swarm,
                    swarm_agents=swarm_agents,
                    triggers=triggers,
                    available_agents=agents,
                    fullname=session.get('fullname'),
                    userid=session.get('user_id'),
                    roles=session.get('roles', []),
                    is_admin=session.get('is_admin', False)
                )
            except Exception as e:
                logger.error(f"Error opening swarm designer: {e}")
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
                logger.error(f"Error monitoring swarm: {e}")
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
                logger.error(f"Error viewing execution: {e}")
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
                logger.error(f"Error creating swarm: {e}")
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
                logger.error(f"Error updating swarm: {e}")
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
                logger.error(f"Error deleting swarm: {e}")
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
                logger.error(f"Error starting swarm: {e}")
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
                logger.error(f"Error stopping swarm: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/swarms/<swarm_id>/execute', methods=['POST'])
        @login_required
        def api_execute_swarm(swarm_id):
            """API: Execute a user query through the swarm."""
            try:
                data = request.get_json()
                query = data.get('query', '')
                
                import uuid
                execution_id = str(uuid.uuid4())
                
                # Create execution record
                self.db_facade.execute(
                    """INSERT INTO swarm_executions
                       (execution_id, swarm_id, trigger_type, trigger_data, status, user_id)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (execution_id, swarm_id, 'user_query',
                     json.dumps({'query': query}), 'pending',
                     session.get('user_id'))
                )
                
                # TODO: Actually execute through orchestrator
                
                return jsonify({
                    'success': True,
                    'execution_id': execution_id,
                    'message': 'Execution started'
                })
            except Exception as e:
                logger.error(f"Error executing swarm: {e}")
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
