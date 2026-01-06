"""
AI Org Routes - Web routes for AI Organization management.

This module provides routes for:
- AI Org CRUD operations
- Visual org chart designer
- Task management
- HITL dashboard
- Real-time monitoring

Version: 1.4.7
Copyright © 2025-2030, All Rights Reserved
"""

import logging
import json
from datetime import datetime
from functools import wraps
from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, session, jsonify, Response
)

from .abstract_routes import AbstractRoutes, login_required, admin_required

logger = logging.getLogger(__name__)


class AIORGRoutes(AbstractRoutes):
    """Routes for AI Organization management."""
    
    def __init__(self, app):
        """
        Initialize AI Org routes.
        
        Args:
            app: Flask application
        """
        super().__init__(app)
        self.blueprint = Blueprint('aiorg', __name__, url_prefix='/aiorg')
    
    def register_routes(self):
        """Register all AI Org routes."""
        
        # =====================================================================
        # AI ORG LIST & CRUD
        # =====================================================================
        
        @self.app.route('/aiorg')
        @login_required
        def aiorg_list():
            """List all AI Organizations."""
            from abhikarta.aiorg import get_aiorg_db_ops
            
            db_ops = get_aiorg_db_ops(self.db_facade)
            orgs = db_ops.list_orgs(limit=100)
            
            return render_template('aiorg/list.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   orgs=orgs)
        
        @self.app.route('/aiorg/create', methods=['GET', 'POST'])
        @admin_required
        def aiorg_create():
            """Create a new AI Organization."""
            from abhikarta.aiorg import get_aiorg_db_ops
            from abhikarta.aiorg.models import AIOrg, AINode, NodeType
            
            if request.method == 'POST':
                name = request.form.get('name', '').strip()
                description = request.form.get('description', '').strip()
                
                if not name:
                    flash('Organization name is required.', 'error')
                    return render_template('aiorg/create.html',
                                           fullname=session.get('fullname'),
                                           userid=session.get('user_id'),
                                           roles=session.get('roles', []))
                
                db_ops = get_aiorg_db_ops(self.db_facade)
                
                # Create org
                org = AIOrg.create(
                    name=name,
                    description=description,
                    created_by=session.get('user_id', 'admin')
                )
                
                if db_ops.save_org(org):
                    # Create default CEO node
                    ceo_name = request.form.get('ceo_name', 'Chief Executive Officer')
                    ceo_email = request.form.get('ceo_email', '')
                    
                    from abhikarta.aiorg.models import HumanMirror, HITLConfig
                    
                    ceo_node = AINode.create(
                        org_id=org.org_id,
                        role_name=ceo_name,
                        role_type=NodeType.EXECUTIVE,
                        description="Top-level executive responsible for overall task coordination",
                        parent_node_id=None,
                        human_mirror=HumanMirror(name=ceo_name, email=ceo_email),
                        hitl_config=HITLConfig(enabled=True),
                        position_x=400,
                        position_y=50
                    )
                    
                    db_ops.save_node(ceo_node)
                    
                    flash(f'AI Organization "{name}" created successfully!', 'success')
                    return redirect(url_for('aiorg_designer', org_id=org.org_id))
                else:
                    flash('Error creating organization.', 'error')
            
            return render_template('aiorg/create.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []))
        
        @self.app.route('/aiorg/<org_id>')
        @login_required
        def aiorg_detail(org_id):
            """View AI Organization details."""
            from abhikarta.aiorg import get_aiorg_db_ops
            
            db_ops = get_aiorg_db_ops(self.db_facade)
            org = db_ops.get_org(org_id)
            
            if not org:
                flash('Organization not found.', 'error')
                return redirect(url_for('aiorg_list'))
            
            nodes = db_ops.get_org_nodes(org_id)
            tasks = db_ops.get_org_tasks(org_id, limit=20)
            stats = db_ops.get_org_stats(org_id)
            
            # Build tree structure
            node_map = {n.node_id: n for n in nodes}
            root_node = None
            for node in nodes:
                if node.parent_node_id is None:
                    root_node = node
                else:
                    parent = node_map.get(node.parent_node_id)
                    if parent:
                        parent.children.append(node)
            
            return render_template('aiorg/detail.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   org=org,
                                   nodes=nodes,
                                   root_node=root_node,
                                   tasks=tasks,
                                   stats=stats)
        
        @self.app.route('/aiorg/<org_id>/delete', methods=['POST'])
        @admin_required
        def aiorg_delete(org_id):
            """Delete an AI Organization."""
            from abhikarta.aiorg import get_aiorg_db_ops
            
            db_ops = get_aiorg_db_ops(self.db_facade)
            
            if db_ops.delete_org(org_id):
                flash('Organization deleted successfully.', 'success')
            else:
                flash('Error deleting organization.', 'error')
            
            return redirect(url_for('aiorg_list'))
        
        # =====================================================================
        # TEMPLATE LIBRARY
        # =====================================================================
        
        @self.app.route('/aiorg/templates')
        @login_required
        def aiorg_templates():
            """Browse AI Organization template library."""
            from abhikarta.aiorg.aiorg_template import AIOrgTemplateManager
            
            template_manager = AIOrgTemplateManager()
            templates = template_manager.list_templates()
            categories = template_manager.get_categories()
            
            return render_template(
                'aiorg/templates.html',
                templates=templates,
                categories=categories,
                fullname=session.get('fullname'),
                userid=session.get('user_id'),
                roles=session.get('roles', []),
                is_admin=session.get('is_admin', False)
            )
        
        @self.app.route('/aiorg/templates/<template_id>')
        @login_required
        def aiorg_template_detail(template_id):
            """View AI Org template details."""
            from abhikarta.aiorg.aiorg_template import AIOrgTemplateManager
            
            template_manager = AIOrgTemplateManager()
            template = template_manager.get_template(template_id)
            
            if not template:
                flash("Template not found", "warning")
                return redirect(url_for('aiorg_templates'))
            
            return render_template(
                'aiorg/template_detail.html',
                template=template,
                fullname=session.get('fullname'),
                userid=session.get('user_id'),
                roles=session.get('roles', []),
                is_admin=session.get('is_admin', False)
            )
        
        @self.app.route('/aiorg/templates/<template_id>/use', methods=['POST'])
        @admin_required
        def use_aiorg_template(template_id):
            """Create a new AI Org from a template."""
            from abhikarta.aiorg.aiorg_template import AIOrgTemplateManager
            from abhikarta.aiorg import get_aiorg_db_ops
            from abhikarta.aiorg.models import AIOrg, AINode, NodeType
            import uuid
            
            template_manager = AIOrgTemplateManager()
            template = template_manager.get_template(template_id)
            
            if not template:
                flash("Template not found", "warning")
                return redirect(url_for('aiorg_templates'))
            
            try:
                name = request.form.get('name', f"{template.name} (Copy)")
                db_ops = get_aiorg_db_ops(self.db_facade)
                
                # Create org from template definition
                org_def = template.org_definition
                
                # Get current user
                user_id = session.get('user_id', 'system')
                
                # Create the organization
                org = AIOrg.create(
                    name=name,
                    description=template.description,
                    config=org_def.get('structure', {}),
                    created_by=user_id
                )
                
                db_ops.save_org(org)
                
                # Map authority levels to NodeType
                def get_node_type(authority_level):
                    mapping = {
                        'c_suite': NodeType.EXECUTIVE,
                        'executive': NodeType.EXECUTIVE,
                        'director': NodeType.MANAGER,
                        'partner': NodeType.MANAGER,
                        'manager': NodeType.MANAGER,
                        'lead': NodeType.MANAGER,
                        'senior': NodeType.ANALYST,
                        'staff': NodeType.ANALYST,
                        'specialist': NodeType.ANALYST,
                        'analyst': NodeType.ANALYST,
                        'junior': NodeType.ANALYST,
                        'coordinator': NodeType.COORDINATOR
                    }
                    return mapping.get(authority_level.lower(), NodeType.ANALYST) if authority_level else NodeType.ANALYST
                
                # Create roles from template
                for role_def in template.roles:
                    node = AINode.create(
                        org_id=org.org_id,
                        node_type=get_node_type(role_def.get('authority_level', 'staff')),
                        name=role_def.get('name', 'Role'),
                        role=role_def.get('role_id', ''),
                        agent_config=role_def.get('agent_config', {}),
                        reports_to=role_def.get('reports_to')
                    )
                    db_ops.save_node(node)
                
                flash(f"Created AI Organization '{name}' from template", "success")
                return redirect(url_for('aiorg_designer', org_id=org.org_id))
                
            except Exception as e:
                logger.error(f"Error creating AI Org from template: {e}", exc_info=True)
                flash(f"Error: {e}", "danger")
                return redirect(url_for('aiorg_templates'))
        
        # =====================================================================
        # VISUAL DESIGNER
        # =====================================================================
        
        @self.app.route('/aiorg/designer/new', methods=['GET', 'POST'])
        @admin_required
        def aiorg_designer_new():
            """Create new AI Org with visual designer."""
            from abhikarta.aiorg import get_aiorg_db_ops
            from abhikarta.aiorg.models import AIOrg, AINode, NodeType, HumanMirror, HITLConfig
            
            if request.method == 'POST':
                # Handle JSON upload
                if 'json_file' in request.files:
                    file = request.files['json_file']
                    if file and file.filename.endswith('.json'):
                        try:
                            json_data = json.loads(file.read().decode('utf-8'))
                            db_ops = get_aiorg_db_ops(self.db_facade)
                            
                            # Import org from JSON
                            org_data = json_data.get('org', {})
                            nodes_data = json_data.get('nodes', [])
                            
                            # Create org
                            org = AIOrg.create(
                                name=org_data.get('name', 'Imported Org'),
                                description=org_data.get('description', ''),
                                created_by=session.get('user_id', 'admin'),
                                config=org_data.get('config', {})
                            )
                            db_ops.save_org(org)
                            
                            # Create nodes (sorted by hierarchy)
                            id_map = {}
                            
                            # First pass: find root nodes
                            for node_data in nodes_data:
                                if not node_data.get('parent_node_id'):
                                    node = AINode.create(
                                        org_id=org.org_id,
                                        role_name=node_data.get('role_name', 'CEO'),
                                        role_type=NodeType(node_data.get('role_type', 'executive')),
                                        description=node_data.get('description', ''),
                                        parent_node_id=None,
                                        human_mirror=HumanMirror(
                                            name=node_data.get('human_name', ''),
                                            email=node_data.get('human_email', '')
                                        ),
                                        hitl_config=HITLConfig(
                                            enabled=node_data.get('hitl_enabled', False)
                                        ),
                                        position_x=node_data.get('position_x', 400),
                                        position_y=node_data.get('position_y', 50)
                                    )
                                    db_ops.save_node(node)
                                    old_id = node_data.get('node_id', node_data.get('id'))
                                    if old_id:
                                        id_map[old_id] = node.node_id
                            
                            # Second pass: create child nodes
                            for node_data in nodes_data:
                                old_parent = node_data.get('parent_node_id')
                                if old_parent:
                                    new_parent = id_map.get(old_parent)
                                    if new_parent:
                                        node = AINode.create(
                                            org_id=org.org_id,
                                            role_name=node_data.get('role_name', 'Node'),
                                            role_type=NodeType(node_data.get('role_type', 'analyst')),
                                            description=node_data.get('description', ''),
                                            parent_node_id=new_parent,
                                            human_mirror=HumanMirror(
                                                name=node_data.get('human_name', ''),
                                                email=node_data.get('human_email', '')
                                            ),
                                            hitl_config=HITLConfig(
                                                enabled=node_data.get('hitl_enabled', False)
                                            ),
                                            position_x=node_data.get('position_x', 400),
                                            position_y=node_data.get('position_y', 150)
                                        )
                                        db_ops.save_node(node)
                                        old_id = node_data.get('node_id', node_data.get('id'))
                                        if old_id:
                                            id_map[old_id] = node.node_id
                            
                            flash(f'Imported organization "{org.name}" with {len(id_map)} nodes.', 'success')
                            return redirect(url_for('aiorg_designer', org_id=org.org_id))
                            
                        except Exception as e:
                            flash(f'Error importing JSON: {str(e)}', 'error')
                
                # Handle simple form submission
                name = request.form.get('name', '').strip()
                if name:
                    db_ops = get_aiorg_db_ops(self.db_facade)
                    
                    org = AIOrg.create(
                        name=name,
                        description=request.form.get('description', ''),
                        created_by=session.get('user_id', 'admin')
                    )
                    db_ops.save_org(org)
                    
                    # Create default CEO node
                    ceo_node = AINode.create(
                        org_id=org.org_id,
                        role_name=request.form.get('ceo_name', 'Chief Executive Officer'),
                        role_type=NodeType.EXECUTIVE,
                        description='Top-level executive responsible for overall organization',
                        parent_node_id=None,
                        human_mirror=HumanMirror(
                            name=request.form.get('ceo_human_name', ''),
                            email=request.form.get('ceo_email', '')
                        ),
                        hitl_config=HITLConfig(enabled=True, approval_required=True),
                        position_x=400,
                        position_y=50
                    )
                    db_ops.save_node(ceo_node)
                    
                    flash(f'Created organization "{name}". Add more nodes below.', 'success')
                    return redirect(url_for('aiorg_designer', org_id=org.org_id))
                else:
                    flash('Organization name is required.', 'error')
            
            # GET - show new designer form
            # Agents are optional - used for advanced node configuration
            agents = []
            
            return render_template('aiorg/designer_new.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   agents=agents)
        
        @self.app.route('/aiorg/<org_id>/designer')
        @admin_required
        def aiorg_designer(org_id):
            """Visual org chart designer."""
            from abhikarta.aiorg import get_aiorg_db_ops
            
            db_ops = get_aiorg_db_ops(self.db_facade)
            org = db_ops.get_org(org_id)
            
            if not org:
                flash('Organization not found.', 'error')
                return redirect(url_for('aiorg_list'))
            
            nodes = db_ops.get_org_nodes(org_id)
            
            # Agents are optional - used for advanced node configuration
            agents = []
            
            # Convert nodes to JSON for JavaScript
            nodes_json = json.dumps([n.to_dict() for n in nodes])
            
            return render_template('aiorg/designer.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   org=org,
                                   nodes=nodes,
                                   nodes_json=nodes_json,
                                   agents=agents)
        
        @self.app.route('/api/aiorg/<org_id>/nodes', methods=['GET', 'POST'])
        @admin_required
        def api_aiorg_nodes(org_id):
            """API endpoint for node management."""
            from abhikarta.aiorg import get_aiorg_db_ops
            from abhikarta.aiorg.models import AINode, NodeType, HumanMirror, HITLConfig
            
            db_ops = get_aiorg_db_ops(self.db_facade)
            
            if request.method == 'GET':
                nodes = db_ops.get_org_nodes(org_id)
                return jsonify([n.to_dict() for n in nodes])
            
            elif request.method == 'POST':
                data = request.get_json()
                
                human_mirror = HumanMirror(
                    name=data.get('human_name', ''),
                    email=data.get('human_email', ''),
                    teams_id=data.get('human_teams_id'),
                    slack_id=data.get('human_slack_id')
                )
                
                hitl_config = HITLConfig(
                    enabled=data.get('hitl_enabled', False),
                    approval_required=data.get('hitl_approval_required', False),
                    review_delegation=data.get('hitl_review_delegation', False),
                    timeout_hours=data.get('hitl_timeout_hours', 24),
                    auto_proceed=data.get('hitl_auto_proceed', True)
                )
                
                node = AINode.create(
                    org_id=org_id,
                    role_name=data.get('role_name', 'New Role'),
                    role_type=NodeType(data.get('role_type', 'analyst')),
                    description=data.get('description', ''),
                    parent_node_id=data.get('parent_node_id'),
                    agent_config=data.get('agent_config', {}),
                    human_mirror=human_mirror,
                    hitl_config=hitl_config,
                    notification_channels=data.get('notification_channels', ['email']),
                    position_x=data.get('position_x', 0),
                    position_y=data.get('position_y', 0)
                )
                
                if data.get('agent_id'):
                    node.agent_id = data['agent_id']
                
                if db_ops.save_node(node):
                    return jsonify(node.to_dict()), 201
                else:
                    return jsonify({'error': 'Failed to create node'}), 500
        
        @self.app.route('/api/aiorg/<org_id>/nodes/<node_id>', methods=['GET', 'PUT', 'DELETE'])
        @admin_required
        def api_aiorg_node(org_id, node_id):
            """API endpoint for single node operations."""
            from abhikarta.aiorg import get_aiorg_db_ops
            from abhikarta.aiorg.models import NodeType, HumanMirror, HITLConfig
            
            db_ops = get_aiorg_db_ops(self.db_facade)
            
            if request.method == 'GET':
                node = db_ops.get_node(node_id)
                if node:
                    return jsonify(node.to_dict())
                return jsonify({'error': 'Node not found'}), 404
            
            elif request.method == 'PUT':
                node = db_ops.get_node(node_id)
                if not node:
                    return jsonify({'error': 'Node not found'}), 404
                
                data = request.get_json()
                
                # Update fields
                if 'role_name' in data:
                    node.role_name = data['role_name']
                if 'role_type' in data:
                    node.role_type = NodeType(data['role_type'])
                if 'description' in data:
                    node.description = data['description']
                if 'parent_node_id' in data:
                    node.parent_node_id = data['parent_node_id']
                if 'agent_id' in data:
                    node.agent_id = data['agent_id']
                if 'agent_config' in data:
                    node.agent_config = data['agent_config']
                if 'position_x' in data:
                    node.position_x = data['position_x']
                if 'position_y' in data:
                    node.position_y = data['position_y']
                if 'status' in data:
                    node.status = data['status']
                
                # Update human mirror
                if any(k in data for k in ['human_name', 'human_email', 'human_teams_id', 'human_slack_id']):
                    node.human_mirror = HumanMirror(
                        name=data.get('human_name', node.human_mirror.name),
                        email=data.get('human_email', node.human_mirror.email),
                        teams_id=data.get('human_teams_id', node.human_mirror.teams_id),
                        slack_id=data.get('human_slack_id', node.human_mirror.slack_id)
                    )
                
                # Update HITL config
                if any(k.startswith('hitl_') for k in data):
                    node.hitl_config = HITLConfig(
                        enabled=data.get('hitl_enabled', node.hitl_config.enabled),
                        approval_required=data.get('hitl_approval_required', node.hitl_config.approval_required),
                        review_delegation=data.get('hitl_review_delegation', node.hitl_config.review_delegation),
                        timeout_hours=data.get('hitl_timeout_hours', node.hitl_config.timeout_hours),
                        auto_proceed=data.get('hitl_auto_proceed', node.hitl_config.auto_proceed)
                    )
                
                if 'notification_channels' in data:
                    node.notification_channels = data['notification_channels']
                
                node.updated_at = datetime.utcnow()
                
                if db_ops.save_node(node):
                    return jsonify(node.to_dict())
                return jsonify({'error': 'Failed to update node'}), 500
            
            elif request.method == 'DELETE':
                # Check for children
                children = db_ops.get_child_nodes(node_id)
                if children:
                    return jsonify({'error': 'Cannot delete node with children'}), 400
                
                if db_ops.delete_node(node_id):
                    return jsonify({'success': True})
                return jsonify({'error': 'Failed to delete node'}), 500
        
        # =====================================================================
        # TASK MANAGEMENT
        # =====================================================================
        
        @self.app.route('/aiorg/<org_id>/tasks')
        @login_required
        def aiorg_tasks(org_id):
            """List tasks for an organization."""
            from abhikarta.aiorg import get_aiorg_db_ops
            from abhikarta.aiorg.models import TaskStatus
            
            db_ops = get_aiorg_db_ops(self.db_facade)
            org = db_ops.get_org(org_id)
            
            if not org:
                flash('Organization not found.', 'error')
                return redirect(url_for('aiorg_list'))
            
            status_filter = request.args.get('status')
            if status_filter:
                tasks = db_ops.get_org_tasks(org_id, status=TaskStatus(status_filter))
            else:
                tasks = db_ops.get_org_tasks(org_id)
            
            return render_template('aiorg/tasks.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   org=org,
                                   tasks=tasks,
                                   status_filter=status_filter)
        
        @self.app.route('/aiorg/<org_id>/tasks/new', methods=['GET', 'POST'])
        @login_required
        def aiorg_task_create(org_id):
            """Create a new task (submit to CEO)."""
            from abhikarta.aiorg import get_aiorg_db_ops
            from abhikarta.aiorg.models import AITask, TaskPriority
            
            db_ops = get_aiorg_db_ops(self.db_facade)
            org = db_ops.get_org(org_id)
            
            if not org:
                flash('Organization not found.', 'error')
                return redirect(url_for('aiorg_list'))
            
            root_node = db_ops.get_root_node(org_id)
            if not root_node:
                flash('Organization has no CEO node configured.', 'error')
                return redirect(url_for('aiorg_detail', org_id=org_id))
            
            if request.method == 'POST':
                title = request.form.get('title', '').strip()
                description = request.form.get('description', '').strip()
                priority = request.form.get('priority', 'medium')
                
                if not title:
                    flash('Task title is required.', 'error')
                else:
                    # Parse input data from form
                    input_data = {}
                    try:
                        additional_data = request.form.get('input_data', '{}')
                        if additional_data:
                            input_data = json.loads(additional_data)
                    except:
                        pass
                    
                    input_data['submitted_by'] = session.get('user_id', 'anonymous')
                    input_data['submitted_at'] = datetime.utcnow().isoformat()
                    
                    task = AITask.create(
                        org_id=org_id,
                        assigned_node_id=root_node.node_id,
                        title=title,
                        description=description,
                        input_data=input_data,
                        priority=TaskPriority(priority)
                    )
                    
                    if db_ops.save_task(task):
                        flash(f'Task "{title}" submitted successfully!', 'success')
                        
                        # TODO: Trigger task processing via TaskEngine
                        # For now, just save and redirect
                        
                        return redirect(url_for('aiorg_task_detail', org_id=org_id, task_id=task.task_id))
                    else:
                        flash('Error creating task.', 'error')
            
            return render_template('aiorg/task_create.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   org=org,
                                   root_node=root_node)
        
        @self.app.route('/aiorg/<org_id>/tasks/<task_id>')
        @login_required
        def aiorg_task_detail(org_id, task_id):
            """View task details."""
            from abhikarta.aiorg import get_aiorg_db_ops
            
            db_ops = get_aiorg_db_ops(self.db_facade)
            org = db_ops.get_org(org_id)
            task = db_ops.get_task(task_id)
            
            if not org or not task:
                flash('Task not found.', 'error')
                return redirect(url_for('aiorg_tasks', org_id=org_id))
            
            # Get node info
            node = db_ops.get_node(task.assigned_node_id)
            
            # Get subtasks
            subtasks = db_ops.get_subtasks(task_id)
            
            # Get responses
            responses = db_ops.get_task_responses(task_id)
            
            # Get parent task if exists
            parent_task = None
            if task.parent_task_id:
                parent_task = db_ops.get_task(task.parent_task_id)
            
            return render_template('aiorg/task_detail.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   org=org,
                                   task=task,
                                   node=node,
                                   subtasks=subtasks,
                                   responses=responses,
                                   parent_task=parent_task)
        
        # =====================================================================
        # HITL DASHBOARD
        # =====================================================================
        
        @self.app.route('/aiorg/hitl')
        @login_required
        def aiorg_hitl_dashboard():
            """HITL dashboard for current user."""
            from abhikarta.aiorg import get_aiorg_db_ops
            
            db_ops = get_aiorg_db_ops(self.db_facade)
            user_email = session.get('email', '')
            
            # Get nodes where user is human mirror
            user_nodes = db_ops.get_nodes_by_email(user_email)
            
            # Get pending HITL items for user's nodes
            pending_items = []
            recent_actions = []
            
            for node in user_nodes:
                # Get pending tasks for review
                node_tasks = db_ops.get_node_tasks(node.node_id)
                for task in node_tasks:
                    if task.status.value in ['delegated', 'waiting']:
                        pending_items.append({
                            'node': node,
                            'task': task,
                            'type': 'task_review'
                        })
                
                # Get recent HITL actions
                actions = db_ops.get_hitl_actions(node_id=node.node_id, limit=10)
                for action in actions:
                    recent_actions.append({
                        'node': node,
                        'action': action
                    })
            
            # Get orgs for user's nodes
            org_ids = set(n.org_id for n in user_nodes)
            orgs = {}
            for org_id in org_ids:
                org = db_ops.get_org(org_id)
                if org:
                    orgs[org_id] = org
            
            return render_template('aiorg/hitl_dashboard.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   user_nodes=user_nodes,
                                   pending_items=pending_items,
                                   recent_actions=recent_actions,
                                   orgs=orgs)
        
        @self.app.route('/aiorg/hitl/<node_id>/<task_id>', methods=['GET', 'POST'])
        @login_required
        def aiorg_hitl_review(node_id, task_id):
            """HITL review screen for a specific task."""
            from abhikarta.aiorg import get_aiorg_db_ops
            from abhikarta.aiorg.models import AIHITLAction, HITLActionType
            
            db_ops = get_aiorg_db_ops(self.db_facade)
            
            node = db_ops.get_node(node_id)
            task = db_ops.get_task(task_id)
            
            if not node or not task:
                flash('Item not found.', 'error')
                return redirect(url_for('aiorg_hitl_dashboard'))
            
            # Verify user is the human mirror
            user_email = session.get('email', '')
            if node.human_mirror.email != user_email:
                roles = session.get('roles', [])
                if 'admin' not in roles and 'superadmin' not in roles:
                    flash('You are not authorized to review this item.', 'error')
                    return redirect(url_for('aiorg_hitl_dashboard'))
            
            org = db_ops.get_org(node.org_id)
            responses = db_ops.get_task_responses(task_id)
            
            if request.method == 'POST':
                action_type = request.form.get('action_type')
                reason = request.form.get('reason', '')
                message = request.form.get('message', '')
                override_content = request.form.get('override_content', '')
                
                # Create HITL action record
                action = AIHITLAction.create(
                    org_id=node.org_id,
                    node_id=node_id,
                    task_id=task_id,
                    user_id=session.get('user_id', 'unknown'),
                    action_type=HITLActionType(action_type),
                    reason=reason,
                    message=message
                )
                
                if action_type == 'override' and override_content:
                    try:
                        action.modified_content = json.loads(override_content)
                    except:
                        action.modified_content = {'text': override_content}
                    
                    # Store original content
                    if responses:
                        action.original_content = responses[-1].content
                
                action.ip_address = request.remote_addr
                action.user_agent = request.user_agent.string
                
                if db_ops.save_hitl_action(action):
                    flash(f'Action "{action_type}" recorded successfully.', 'success')
                    
                    # TODO: Trigger continuation via HITLManager
                    
                    return redirect(url_for('aiorg_hitl_dashboard'))
                else:
                    flash('Error recording action.', 'error')
            
            return render_template('aiorg/hitl_review.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   org=org,
                                   node=node,
                                   task=task,
                                   responses=responses)
        
        # =====================================================================
        # REAL-TIME MONITOR
        # =====================================================================
        
        @self.app.route('/aiorg/<org_id>/monitor')
        @login_required
        def aiorg_monitor(org_id):
            """Real-time org activity monitor."""
            from abhikarta.aiorg import get_aiorg_db_ops
            
            db_ops = get_aiorg_db_ops(self.db_facade)
            org = db_ops.get_org(org_id)
            
            if not org:
                flash('Organization not found.', 'error')
                return redirect(url_for('aiorg_list'))
            
            nodes = db_ops.get_org_nodes(org_id)
            recent_events = db_ops.get_event_logs(org_id, limit=50)
            stats = db_ops.get_org_stats(org_id)
            
            return render_template('aiorg/monitor.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   org=org,
                                   nodes=nodes,
                                   events=recent_events,
                                   stats=stats)
        
        # =====================================================================
        # IMPORT/EXPORT
        # =====================================================================
        
        @self.app.route('/aiorg/<org_id>/export')
        @admin_required
        def aiorg_export(org_id):
            """Export org chart as JSON."""
            from abhikarta.aiorg import get_aiorg_db_ops
            
            db_ops = get_aiorg_db_ops(self.db_facade)
            org = db_ops.get_org(org_id)
            
            if not org:
                flash('Organization not found.', 'error')
                return redirect(url_for('aiorg_list'))
            
            nodes = db_ops.get_org_nodes(org_id)
            
            export_data = {
                'org': org.to_dict(),
                'nodes': [n.to_dict() for n in nodes],
                'exported_at': datetime.utcnow().isoformat(),
                'version': '1.4.8'
            }
            
            response = Response(
                json.dumps(export_data, indent=2),
                mimetype='application/json',
                headers={
                    'Content-Disposition': f'attachment; filename=aiorg_{org.name}_{datetime.now().strftime("%Y%m%d")}.json'
                }
            )
            return response
        
        @self.app.route('/aiorg/import', methods=['GET', 'POST'])
        @admin_required
        def aiorg_import():
            """Import org chart from JSON."""
            from abhikarta.aiorg import get_aiorg_db_ops
            from abhikarta.aiorg.models import AIOrg, AINode, NodeType, HumanMirror, HITLConfig
            
            if request.method == 'POST':
                if 'file' not in request.files:
                    flash('No file uploaded.', 'error')
                    return redirect(request.url)
                
                file = request.files['file']
                if file.filename == '':
                    flash('No file selected.', 'error')
                    return redirect(request.url)
                
                try:
                    data = json.load(file)
                    
                    db_ops = get_aiorg_db_ops(self.db_facade)
                    
                    # Create new org
                    org_data = data['org']
                    org = AIOrg.create(
                        name=org_data['name'] + ' (Imported)',
                        description=org_data.get('description', ''),
                        created_by=session.get('user_id', 'admin')
                    )
                    
                    if not db_ops.save_org(org):
                        raise Exception("Failed to save org")
                    
                    # Map old node IDs to new ones
                    node_id_map = {}
                    
                    # First pass: create nodes without parent references
                    for node_data in data['nodes']:
                        old_id = node_data['node_id']
                        
                        human_mirror = HumanMirror(
                            name=node_data.get('human_name', ''),
                            email=node_data.get('human_email', ''),
                            teams_id=node_data.get('human_teams_id'),
                            slack_id=node_data.get('human_slack_id')
                        )
                        
                        hitl_config = HITLConfig(
                            enabled=node_data.get('hitl_enabled', False),
                            approval_required=node_data.get('hitl_approval_required', False),
                            review_delegation=node_data.get('hitl_review_delegation', False),
                            timeout_hours=node_data.get('hitl_timeout_hours', 24),
                            auto_proceed=node_data.get('hitl_auto_proceed', True)
                        )
                        
                        node = AINode.create(
                            org_id=org.org_id,
                            role_name=node_data['role_name'],
                            role_type=NodeType(node_data.get('role_type', 'analyst')),
                            description=node_data.get('description', ''),
                            parent_node_id=None,  # Set later
                            human_mirror=human_mirror,
                            hitl_config=hitl_config,
                            notification_channels=node_data.get('notification_channels', ['email']),
                            position_x=node_data.get('position_x', 0),
                            position_y=node_data.get('position_y', 0)
                        )
                        
                        node_id_map[old_id] = node.node_id
                        db_ops.save_node(node)
                    
                    # Second pass: update parent references
                    for node_data in data['nodes']:
                        if node_data.get('parent_node_id'):
                            new_node_id = node_id_map[node_data['node_id']]
                            new_parent_id = node_id_map.get(node_data['parent_node_id'])
                            
                            if new_parent_id:
                                node = db_ops.get_node(new_node_id)
                                node.parent_node_id = new_parent_id
                                db_ops.save_node(node)
                    
                    flash(f'Organization imported successfully as "{org.name}"!', 'success')
                    return redirect(url_for('aiorg_designer', org_id=org.org_id))
                    
                except Exception as e:
                    logger.error(f"Import error: {e}", exc_info=True)
                    flash(f'Error importing: {str(e)}', 'error')
            
            return render_template('aiorg/import.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []))
        
        # =====================================================================
        # API ENDPOINTS
        # =====================================================================
        
        @self.app.route('/api/aiorg/<org_id>/activate', methods=['POST'])
        @admin_required
        def api_aiorg_activate(org_id):
            """Activate an AI Organization."""
            from abhikarta.aiorg import get_aiorg_db_ops
            from abhikarta.aiorg.models import OrgStatus
            
            db_ops = get_aiorg_db_ops(self.db_facade)
            org = db_ops.get_org(org_id)
            
            if not org:
                return jsonify({'error': 'Organization not found'}), 404
            
            org.status = OrgStatus.ACTIVE
            org.updated_at = datetime.utcnow()
            
            if db_ops.save_org(org):
                # TODO: Initialize actors via OrgManager
                return jsonify({'success': True, 'status': 'active'})
            
            return jsonify({'error': 'Failed to activate'}), 500
        
        @self.app.route('/api/aiorg/<org_id>/pause', methods=['POST'])
        @admin_required
        def api_aiorg_pause(org_id):
            """Pause an AI Organization."""
            from abhikarta.aiorg import get_aiorg_db_ops
            from abhikarta.aiorg.models import OrgStatus
            
            db_ops = get_aiorg_db_ops(self.db_facade)
            org = db_ops.get_org(org_id)
            
            if not org:
                return jsonify({'error': 'Organization not found'}), 404
            
            org.status = OrgStatus.PAUSED
            org.updated_at = datetime.utcnow()
            
            if db_ops.save_org(org):
                # TODO: Pause actors via OrgManager
                return jsonify({'success': True, 'status': 'paused'})
            
            return jsonify({'error': 'Failed to pause'}), 500
        
        @self.app.route('/api/aiorg/<org_id>/tasks', methods=['POST'])
        @login_required
        def api_submit_task(org_id):
            """API endpoint to submit a task."""
            from abhikarta.aiorg import get_aiorg_db_ops
            from abhikarta.aiorg.models import AITask, TaskPriority
            
            db_ops = get_aiorg_db_ops(self.db_facade)
            org = db_ops.get_org(org_id)
            
            if not org:
                return jsonify({'error': 'Organization not found'}), 404
            
            root_node = db_ops.get_root_node(org_id)
            if not root_node:
                return jsonify({'error': 'No CEO node configured'}), 400
            
            data = request.get_json()
            
            task = AITask.create(
                org_id=org_id,
                assigned_node_id=root_node.node_id,
                title=data.get('title', 'Untitled Task'),
                description=data.get('description', ''),
                input_data=data.get('input_data', {}),
                priority=TaskPriority(data.get('priority', 'medium'))
            )
            
            task.input_data['submitted_by'] = session.get('user_id', 'api')
            task.input_data['submitted_at'] = datetime.utcnow().isoformat()
            
            if db_ops.save_task(task):
                # TODO: Trigger task processing
                return jsonify(task.to_dict()), 201
            
            return jsonify({'error': 'Failed to create task'}), 500
        
        @self.app.route('/api/aiorg/<org_id>/stats')
        @login_required
        def api_aiorg_stats(org_id):
            """Get organization statistics."""
            from abhikarta.aiorg import get_aiorg_db_ops
            
            db_ops = get_aiorg_db_ops(self.db_facade)
            stats = db_ops.get_org_stats(org_id)
            
            return jsonify(stats)
        
        # =====================================================================
        # EXPORT, EDIT & STATUS ROUTES
        # =====================================================================
        
        @self.app.route('/aiorg/<org_id>/export/json')
        @admin_required
        def export_aiorg_json(org_id):
            """Export AI organization configuration as JSON file."""
            org = self.db_facade.fetch_one(
                "SELECT * FROM ai_orgs WHERE org_id = ?",
                (org_id,)
            )
            if not org:
                flash('Organization not found', 'error')
                return redirect(url_for('aiorg_list'))
            
            org_dict = dict(org)
            if 'config' in org_dict and isinstance(org_dict['config'], str):
                try:
                    org_dict['config'] = json.loads(org_dict['config'])
                except:
                    pass
            
            # Get nodes
            nodes = self.db_facade.fetch_all(
                "SELECT * FROM ai_nodes WHERE org_id = ?",
                (org_id,)
            ) or []
            org_dict['nodes'] = [dict(n) for n in nodes]
            
            response = Response(
                json.dumps(org_dict, indent=2, default=str),
                mimetype='application/json',
                headers={
                    'Content-Disposition': f'attachment; filename=aiorg_{org["name"].lower().replace(" ", "_")}_{org_id}.json'
                }
            )
            return response
        
        @self.app.route('/aiorg/<org_id>/export/python')
        @admin_required
        def export_aiorg_python(org_id):
            """Export AI organization as Python SDK code."""
            from abhikarta_web.utils.export_utils import generate_aiorg_python_code
            
            org = self.db_facade.fetch_one(
                "SELECT * FROM ai_orgs WHERE org_id = ?",
                (org_id,)
            )
            if not org:
                flash('Organization not found', 'error')
                return redirect(url_for('aiorg_list'))
            
            org_dict = dict(org)
            if 'config' in org_dict and isinstance(org_dict['config'], str):
                try:
                    org_dict['config'] = json.loads(org_dict['config'])
                except:
                    pass
            
            python_code = generate_aiorg_python_code(org_dict)
            
            response = Response(
                python_code,
                mimetype='text/x-python',
                headers={
                    'Content-Disposition': f'attachment; filename=aiorg_{org["name"].lower().replace(" ", "_")}.py'
                }
            )
            return response
        
        @self.app.route('/api/aiorg/<org_id>/json')
        @admin_required
        def api_aiorg_json(org_id):
            """API: Get full AI organization JSON configuration."""
            org = self.db_facade.fetch_one(
                "SELECT * FROM ai_orgs WHERE org_id = ?",
                (org_id,)
            )
            if not org:
                return jsonify({'error': 'Organization not found'}), 404
            
            org_dict = dict(org)
            if 'config' in org_dict and isinstance(org_dict['config'], str):
                try:
                    org_dict['config'] = json.loads(org_dict['config'])
                except:
                    pass
            
            # Include nodes
            nodes = self.db_facade.fetch_all(
                "SELECT * FROM ai_nodes WHERE org_id = ?",
                (org_id,)
            ) or []
            org_dict['nodes'] = [dict(n) for n in nodes]
            
            return jsonify(org_dict)
        
        @self.app.route('/api/aiorg/<org_id>/python')
        @admin_required
        def api_aiorg_python(org_id):
            """API: Get AI organization as Python SDK code."""
            from abhikarta_web.utils.export_utils import generate_aiorg_python_code
            
            org = self.db_facade.fetch_one(
                "SELECT * FROM ai_orgs WHERE org_id = ?",
                (org_id,)
            )
            if not org:
                return jsonify({'error': 'Organization not found'}), 404
            
            org_dict = dict(org)
            if 'config' in org_dict and isinstance(org_dict['config'], str):
                try:
                    org_dict['config'] = json.loads(org_dict['config'])
                except:
                    pass
            
            python_code = generate_aiorg_python_code(org_dict)
            return Response(python_code, mimetype='text/plain')
        
        @self.app.route('/api/aiorg/<org_id>/status', methods=['PUT'])
        @admin_required
        def api_change_aiorg_status(org_id):
            """API: Change AI organization status."""
            from abhikarta_web.utils.export_utils import is_valid_transition
            
            try:
                data = request.get_json()
                new_status = data.get('status')
                
                org = self.db_facade.fetch_one(
                    "SELECT status FROM ai_orgs WHERE org_id = ?",
                    (org_id,)
                )
                if not org:
                    return jsonify({'error': 'Organization not found'}), 404
                
                current_status = org['status']
                
                if not is_valid_transition(current_status, new_status):
                    return jsonify({'error': f'Invalid status transition from {current_status} to {new_status}'}), 400
                
                self.db_facade.execute(
                    "UPDATE ai_orgs SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE org_id = ?",
                    (new_status, org_id)
                )
                
                self.log_audit('change_status', 'aiorg', org_id, {'new_status': new_status})
                
                return jsonify({'success': True, 'status': new_status})
                
            except Exception as e:
                logger.error(f"Error changing AI org status: {e}", exc_info=True)
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/aiorg/<org_id>/edit', methods=['GET', 'POST'])
        @admin_required
        def edit_aiorg(org_id):
            """Edit AI organization properties."""
            org = self.db_facade.fetch_one(
                "SELECT * FROM ai_orgs WHERE org_id = ?",
                (org_id,)
            )
            if not org:
                flash('Organization not found', 'error')
                return redirect(url_for('aiorg_list'))
            
            org_dict = dict(org)
            if 'config' in org_dict and isinstance(org_dict['config'], str):
                try:
                    org_dict['config'] = json.loads(org_dict['config'])
                except:
                    pass
            
            if request.method == 'POST':
                try:
                    name = request.form.get('name', '').strip()
                    description = request.form.get('description', '').strip()
                    
                    self.db_facade.execute(
                        """UPDATE ai_orgs 
                           SET name = ?, description = ?, updated_at = CURRENT_TIMESTAMP 
                           WHERE org_id = ?""",
                        (name, description, org_id)
                    )
                    
                    self.log_audit('update_aiorg', 'aiorg', org_id)
                    flash('Organization updated successfully', 'success')
                    return redirect(url_for('view_aiorg', org_id=org_id))
                    
                except Exception as e:
                    logger.error(f"Error updating organization: {e}", exc_info=True)
                    flash(f'Error: {str(e)}', 'error')
            
            return render_template('aiorg/edit.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   org=org_dict)
        
        @self.app.route('/api/aiorg/<org_id>/edit', methods=['POST'])
        @admin_required
        def api_edit_aiorg_json(org_id):
            """API: Update AI organization from JSON."""
            try:
                data = request.get_json()
                
                for field in ['org_id', 'created_at', 'created_by']:
                    if field in data:
                        del data[field]
                
                updates = []
                values = []
                for field in ['name', 'description', 'config']:
                    if field in data:
                        updates.append(f"{field} = ?")
                        value = data[field]
                        if isinstance(value, (dict, list)):
                            value = json.dumps(value)
                        values.append(value)
                
                if updates:
                    updates.append("updated_at = CURRENT_TIMESTAMP")
                    values.append(org_id)
                    
                    self.db_facade.execute(
                        f"UPDATE ai_orgs SET {', '.join(updates)} WHERE org_id = ?",
                        tuple(values)
                    )
                    
                    self.log_audit('update_aiorg_json', 'aiorg', org_id)
                
                return jsonify({'success': True})
                
            except Exception as e:
                logger.error(f"Error updating organization: {e}", exc_info=True)
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/aiorg/<org_id>', methods=['DELETE'])
        @admin_required
        def api_delete_aiorg(org_id):
            """API: Delete an AI organization."""
            try:
                # Delete nodes first
                self.db_facade.execute(
                    "DELETE FROM ai_nodes WHERE org_id = ?",
                    (org_id,)
                )
                # Delete org
                self.db_facade.execute(
                    "DELETE FROM ai_orgs WHERE org_id = ?",
                    (org_id,)
                )
                self.log_audit('delete_aiorg', 'aiorg', org_id)
                return jsonify({'success': True})
            except Exception as e:
                logger.error(f"Error deleting organization: {e}", exc_info=True)
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/aiorg/test', methods=['POST'])
        @login_required
        def api_test_aiorg_design():
            """API: Test an AI organization during design time."""
            import time
            
            try:
                data = request.get_json()
                input_text = data.get('input', '')
                org_config = data.get('org', {})
                nodes = data.get('nodes', [])
                
                if not input_text:
                    return jsonify({'success': False, 'error': 'Input is required'}), 400
                
                start_time = time.time()
                
                # Find an LLM config from nodes
                provider = 'ollama'
                model = 'llama3.2:3b'
                
                for node in nodes:
                    llm_config = node.get('llm_config', {})
                    if llm_config.get('provider'):
                        provider = llm_config.get('provider')
                        model = llm_config.get('model', model)
                        break
                
                # Apply admin defaults
                admin_defaults = {}
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
                    
                    # Create LLM
                    if provider.lower() == 'ollama':
                        base_url = admin_defaults.get('base_url', 'http://localhost:11434')
                        llm = ChatOllama(model=model, base_url=base_url)
                    elif provider.lower() == 'openai':
                        llm = ChatOpenAI(model=model)
                    elif provider.lower() == 'anthropic':
                        llm = ChatAnthropic(model=model)
                    else:
                        llm = ChatOllama(model=model)
                    
                    # Build org simulation prompt
                    org_name = org_config.get('name', 'Unnamed AI Organization')
                    system_prompt = f"You are simulating an AI organization named '{org_name}' with {len(nodes)} AI nodes. Process the user's request as a coordinated organization."
                    
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
                        'nodes_simulated': len(nodes)
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
                logger.error(f"Error in design-time AI org test: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/aiorg/<org_id>/execute', methods=['POST'])
        @login_required
        def api_execute_aiorg(org_id):
            """API: Execute a task through the AI organization."""
            try:
                data = request.get_json()
                task = data.get('task', '')
                
                if not task:
                    return jsonify({'success': False, 'error': 'Task is required'}), 400
                
                import time
                from abhikarta.utils.helpers import generate_execution_id, EntityType as HelperEntityType
                
                # Get org info
                org = self.db_facade.fetch_one(
                    "SELECT * FROM ai_orgs WHERE org_id = ?",
                    (org_id,)
                )
                org_name = org.get('name', '') if org else ''
                
                execution_id = generate_execution_id(HelperEntityType.AIORG, org_name)
                start_time = time.time()
                
                # Start execution logging
                try:
                    from abhikarta.services.execution_logger import get_execution_logger, EntityType
                    exec_logger = get_execution_logger()
                    
                    if exec_logger and exec_logger.config.enabled:
                        exec_log = exec_logger.start_execution(
                            execution_id=execution_id,
                            entity_type=EntityType.AIORG,
                            entity_id=org_id,
                            entity_name=org_name,
                            user_input=task
                        )
                        
                        exec_log.entity_config = {
                            'org_name': org_name,
                            'org_type': org.get('org_type', 'functional') if org else ''
                        }
                        
                        # Get org nodes
                        nodes = self.db_facade.fetch_all(
                            "SELECT node_name, node_type, role FROM ai_nodes WHERE org_id = ?",
                            (org_id,)
                        ) or []
                        
                        exec_log.execution_json = {
                            'org_id': org_id,
                            'name': org_name,
                            'nodes': [dict(n) for n in nodes],
                            'task': task
                        }
                except Exception as log_err:
                    logger.debug(f"Could not start execution logging: {log_err}")
                
                # TODO: Actually execute through AI org orchestrator
                
                return jsonify({
                    'success': True,
                    'execution_id': execution_id,
                    'message': 'Execution started'
                })
                
            except Exception as e:
                logger.error(f"Error executing AI org: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        logger.info("AI Org routes registered")
