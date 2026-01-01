"""
Workflow Routes - Web routes for workflow management.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import json
import logging
from flask import render_template, request, jsonify, session, redirect, url_for

from .abstract_routes import AbstractRoutes, login_required, admin_required

logger = logging.getLogger(__name__)


class WorkflowRoutes(AbstractRoutes):
    """Routes for workflow DAG management."""
    
    def register_routes(self):
        """Register workflow routes."""
        
        # ==================== Web Routes ====================
        
        @self.app.route('/workflows')
        @login_required
        def list_workflows():
            """List all workflows."""
            try:
                workflows = self.db_facade.fetch_all(
                    "SELECT * FROM workflows ORDER BY created_at DESC"
                ) or []
            except:
                workflows = []
            
            return render_template('workflows/list.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   workflows=workflows)
        
        @self.app.route('/workflows/upload', methods=['GET', 'POST'])
        @login_required
        def upload_workflow():
            """Upload a new workflow."""
            if request.method == 'POST':
                try:
                    # Handle file upload
                    if 'workflow_file' in request.files:
                        file = request.files['workflow_file']
                        if file.filename:
                            content = file.read().decode('utf-8')
                            workflow_data = json.loads(content)
                    else:
                        # Handle JSON from form
                        workflow_data = json.loads(request.form.get('dag_json', '{}'))
                    
                    name = request.form.get('name') or workflow_data.get('name', 'Untitled Workflow')
                    description = request.form.get('description') or workflow_data.get('description', '')
                    python_modules = request.form.get('python_modules', '{}')
                    
                    # Parse and validate
                    from abhikarta.workflow import DAGParser
                    parser = DAGParser()
                    workflow = parser.parse_dict(workflow_data)
                    
                    if not workflow:
                        return render_template('workflows/upload.html',
                                             fullname=session.get('fullname'),
                                             userid=session.get('user_id'),
                                             roles=session.get('roles', []),
                                             error=f"Invalid workflow: {parser.get_errors()}")
                    
                    # Save to database
                    import uuid
                    workflow_id = str(uuid.uuid4())[:8]
                    
                    self.db_facade.execute("""
                        INSERT INTO workflows (
                            workflow_id, name, description, dag_definition,
                            python_modules, created_by, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        workflow_id,
                        name,
                        description,
                        json.dumps(workflow_data),
                        python_modules if isinstance(python_modules, str) else json.dumps(python_modules),
                        session.get('user_id'),
                        'draft'
                    ))
                    
                    self.log_audit('create_workflow', 'workflow', workflow_id)
                    return redirect(url_for('workflow_detail', workflow_id=workflow_id))
                    
                except json.JSONDecodeError as e:
                    return render_template('workflows/upload.html',
                                         fullname=session.get('fullname'),
                                         userid=session.get('user_id'),
                                         roles=session.get('roles', []),
                                         error=f"Invalid JSON: {e}")
                except Exception as e:
                    logger.error(f"Error uploading workflow: {e}", exc_info=True)
                    return render_template('workflows/upload.html',
                                         fullname=session.get('fullname'),
                                         userid=session.get('user_id'),
                                         roles=session.get('roles', []),
                                         error=str(e))
            
            return render_template('workflows/upload.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []))
        
        @self.app.route('/workflows/<workflow_id>')
        @login_required
        def workflow_detail(workflow_id):
            """View workflow details."""
            workflow = self.db_facade.fetch_one(
                "SELECT * FROM workflows WHERE workflow_id = ?",
                (workflow_id,)
            )
            
            if not workflow:
                return render_template('errors/404.html'), 404
            
            # Parse DAG definition
            try:
                workflow['dag_definition'] = json.loads(workflow.get('dag_definition', '{}'))
                workflow['python_modules'] = json.loads(workflow.get('python_modules', '{}'))
            except:
                pass
            
            # Get recent executions
            executions = self.db_facade.fetch_all("""
                SELECT * FROM executions 
                WHERE agent_id = ? 
                ORDER BY started_at DESC LIMIT 10
            """, (workflow_id,)) or []
            
            return render_template('workflows/detail.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   workflow=workflow,
                                   executions=executions)
        
        @self.app.route('/workflows/<workflow_id>/execute', methods=['GET', 'POST'])
        @login_required
        def execute_workflow(workflow_id):
            """Execute a workflow."""
            workflow = self.db_facade.fetch_one(
                "SELECT * FROM workflows WHERE workflow_id = ?",
                (workflow_id,)
            )
            
            if not workflow:
                return render_template('errors/404.html'), 404
            
            if request.method == 'POST':
                try:
                    # Get input data
                    input_json = request.form.get('input_data', '{}')
                    input_data = json.loads(input_json)
                    
                    # Execute workflow
                    from abhikarta.workflow import WorkflowExecutor, DAGParser
                    
                    dag_def = json.loads(workflow.get('dag_definition', '{}'))
                    dag_def['workflow_id'] = workflow_id
                    dag_def['name'] = workflow['name']
                    dag_def['python_modules'] = json.loads(workflow.get('python_modules', '{}'))
                    
                    parser = DAGParser()
                    wf = parser.parse_dict(dag_def)
                    
                    if not wf:
                        return jsonify({
                            'success': False,
                            'error': f"Failed to parse workflow: {parser.get_errors()}"
                        })
                    
                    executor = WorkflowExecutor(
                        self.db_facade, 
                        None,  # llm_facade
                        session.get('user_id')
                    )
                    
                    execution = executor.execute_workflow(wf, input_data)
                    
                    self.log_audit('execute_workflow', 'workflow', workflow_id,
                                  {'execution_id': execution.execution_id})
                    
                    return jsonify({
                        'success': True,
                        'execution': execution.to_dict()
                    })
                    
                except Exception as e:
                    logger.error(f"Workflow execution error: {e}", exc_info=True)
                    return jsonify({
                        'success': False,
                        'error': str(e)
                    })
            
            # GET - show execution form
            try:
                input_schema = json.loads(workflow.get('input_schema', '{}'))
            except:
                input_schema = {}
            
            return render_template('workflows/execute.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   workflow=workflow,
                                   input_schema=input_schema)
        
        @self.app.route('/workflows/<workflow_id>/delete', methods=['POST'])
        @admin_required
        def delete_workflow(workflow_id):
            """Delete a workflow."""
            try:
                self.db_facade.execute(
                    "DELETE FROM workflows WHERE workflow_id = ?",
                    (workflow_id,)
                )
                self.log_audit('delete_workflow', 'workflow', workflow_id)
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        # ==================== API Routes ====================
        
        @self.app.route('/api/workflows', methods=['GET'])
        @login_required
        def api_list_workflows():
            """API: List workflows."""
            workflows = self.db_facade.fetch_all(
                "SELECT workflow_id, name, description, status, created_at, execution_count FROM workflows ORDER BY created_at DESC"
            ) or []
            return jsonify({'success': True, 'workflows': workflows})
        
        @self.app.route('/api/workflows', methods=['POST'])
        @login_required
        def api_create_workflow():
            """API: Create workflow."""
            try:
                data = request.get_json()
                
                import uuid
                workflow_id = str(uuid.uuid4())[:8]
                
                self.db_facade.execute("""
                    INSERT INTO workflows (
                        workflow_id, name, description, dag_definition,
                        python_modules, created_by, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    workflow_id,
                    data.get('name', 'Untitled'),
                    data.get('description', ''),
                    json.dumps(data.get('dag_definition', {})),
                    json.dumps(data.get('python_modules', {})),
                    session.get('user_id'),
                    'draft'
                ))
                
                return jsonify({
                    'success': True,
                    'workflow_id': workflow_id
                })
                
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/workflows/<workflow_id>', methods=['GET'])
        @login_required
        def api_get_workflow(workflow_id):
            """API: Get workflow."""
            workflow = self.db_facade.fetch_one(
                "SELECT * FROM workflows WHERE workflow_id = ?",
                (workflow_id,)
            )
            
            if workflow:
                workflow['dag_definition'] = json.loads(workflow.get('dag_definition', '{}'))
                workflow['python_modules'] = json.loads(workflow.get('python_modules', '{}'))
                return jsonify({'success': True, 'workflow': workflow})
            
            return jsonify({'success': False, 'error': 'Workflow not found'}), 404
        
        @self.app.route('/api/workflows/<workflow_id>/execute', methods=['POST'])
        @login_required
        def api_execute_workflow(workflow_id):
            """API: Execute workflow."""
            try:
                data = request.get_json() or {}
                input_data = data.get('input', {})
                
                workflow = self.db_facade.fetch_one(
                    "SELECT * FROM workflows WHERE workflow_id = ?",
                    (workflow_id,)
                )
                
                if not workflow:
                    return jsonify({'success': False, 'error': 'Workflow not found'}), 404
                
                from abhikarta.workflow import WorkflowExecutor, DAGParser
                
                dag_def = json.loads(workflow.get('dag_definition', '{}'))
                dag_def['workflow_id'] = workflow_id
                dag_def['name'] = workflow['name']
                dag_def['python_modules'] = json.loads(workflow.get('python_modules', '{}'))
                
                parser = DAGParser()
                wf = parser.parse_dict(dag_def)
                
                if not wf:
                    return jsonify({
                        'success': False,
                        'error': f"Failed to parse: {parser.get_errors()}"
                    })
                
                executor = WorkflowExecutor(
                    self.db_facade, None, session.get('user_id')
                )
                
                execution = executor.execute_workflow(wf, input_data)
                
                return jsonify({
                    'success': True,
                    'execution': execution.to_dict()
                })
                
            except Exception as e:
                logger.error(f"API workflow execution error: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/workflows/<workflow_id>/validate', methods=['POST'])
        @login_required
        def api_validate_workflow(workflow_id):
            """API: Validate workflow."""
            try:
                data = request.get_json() or {}
                
                from abhikarta.workflow import DAGParser
                parser = DAGParser()
                
                if 'dag_definition' in data:
                    workflow = parser.parse_dict(data['dag_definition'])
                else:
                    # Get from database
                    wf_data = self.db_facade.fetch_one(
                        "SELECT dag_definition FROM workflows WHERE workflow_id = ?",
                        (workflow_id,)
                    )
                    if wf_data:
                        workflow = parser.parse_json(wf_data['dag_definition'])
                    else:
                        return jsonify({'valid': False, 'errors': ['Workflow not found']})
                
                if workflow:
                    errors = workflow.validate()
                    return jsonify({
                        'valid': len(errors) == 0,
                        'errors': errors,
                        'warnings': parser.get_warnings(),
                        'node_count': len(workflow.nodes),
                        'execution_order': workflow.get_execution_order()
                    })
                else:
                    return jsonify({
                        'valid': False,
                        'errors': parser.get_errors()
                    })
                    
            except Exception as e:
                return jsonify({'valid': False, 'errors': [str(e)]})
        
        # =====================================================================
        # Workflow Designer Routes
        # =====================================================================
        
        @self.app.route('/workflows/designer')
        @login_required
        def workflow_designer_new():
            """Create a new workflow with visual designer."""
            return render_template('workflows/designer.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   workflow=None)
        
        @self.app.route('/workflows/<workflow_id>/designer')
        @login_required
        def workflow_designer(workflow_id):
            """Edit workflow with visual designer."""
            workflow = self.db_facade.fetch_one(
                "SELECT * FROM workflows WHERE workflow_id = ?",
                (workflow_id,)
            )
            
            if not workflow:
                return render_template('errors/404.html'), 404
            
            return render_template('workflows/designer.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   workflow=workflow)
        
        # =====================================================================
        # Workflow Template Routes
        # =====================================================================
        
        @self.app.route('/workflows/templates')
        @login_required
        def workflow_templates():
            """Browse workflow template library."""
            from abhikarta.workflow.workflow_template import WorkflowTemplateManager
            
            template_manager = WorkflowTemplateManager()
            templates = template_manager.list_templates()
            categories = template_manager.get_categories()
            industries = template_manager.get_industries()
            
            return render_template('workflows/templates.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   templates=templates,
                                   categories=categories,
                                   industries=industries)
        
        @self.app.route('/workflows/templates/<template_id>')
        @login_required
        def workflow_template_detail(template_id):
            """View workflow template details."""
            from abhikarta.workflow.workflow_template import WorkflowTemplateManager
            
            template_manager = WorkflowTemplateManager()
            template = template_manager.get_template(template_id)
            
            if not template:
                from flask import flash
                flash('Template not found', 'error')
                return redirect(url_for('workflow_templates'))
            
            return render_template('workflows/template_detail.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   template=template)
        
        @self.app.route('/workflows/templates/<template_id>/create')
        @login_required
        def create_workflow_from_template_page(template_id):
            """Show create workflow from template page."""
            from abhikarta.workflow.workflow_template import WorkflowTemplateManager
            
            template_manager = WorkflowTemplateManager()
            template = template_manager.get_template(template_id)
            
            if not template:
                from flask import flash
                flash('Template not found', 'error')
                return redirect(url_for('workflow_templates'))
            
            return render_template('workflows/create_from_template.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   template=template)
        
        @self.app.route('/workflows/templates/create', methods=['POST'])
        @login_required
        def create_workflow_from_template():
            """Create a new workflow from a template."""
            from flask import flash
            from abhikarta.workflow.workflow_template import WorkflowTemplateManager
            import uuid
            from datetime import datetime
            
            template_id = request.form.get('template_id')
            workflow_name = request.form.get('workflow_name', '').strip()
            description = request.form.get('description', '').strip()
            
            if not template_id or not workflow_name:
                flash('Template and workflow name are required', 'error')
                return redirect(url_for('workflow_templates'))
            
            try:
                template_manager = WorkflowTemplateManager()
                template = template_manager.get_template(template_id)
                
                if not template:
                    flash('Template not found', 'error')
                    return redirect(url_for('workflow_templates'))
                
                # Create new workflow from template
                workflow_id = f"wf_{uuid.uuid4().hex[:12]}"
                
                self.db_facade.execute(
                    """INSERT INTO workflows 
                       (workflow_id, name, description, dag_definition, python_modules, status, created_by, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        workflow_id,
                        workflow_name,
                        description or template.description,
                        json.dumps(template.dag_definition),
                        json.dumps(template.python_modules),
                        'draft',
                        session.get('user_id'),
                        datetime.utcnow().isoformat()
                    )
                )
                
                # Increment template use count
                template.use_count += 1
                
                flash(f'Workflow "{workflow_name}" created from template!', 'success')
                logger.info(f"Created workflow {workflow_id} from template {template_id}")
                
                return redirect(url_for('workflow_designer', workflow_id=workflow_id))
                
            except Exception as e:
                logger.error(f"Error creating workflow from template: {e}", exc_info=True)
                flash(f'Error: {str(e)}', 'error')
            
            return redirect(url_for('workflow_templates'))

        @self.app.route('/api/workflows/design', methods=['POST'])
        @login_required
        def save_workflow_design():
            """Save workflow from visual designer."""
            import uuid
            
            try:
                data = request.get_json()
                
                workflow_id = data.get('workflow_id')
                name = data.get('name', 'Untitled Workflow')
                description = data.get('description', '')
                nodes = data.get('nodes', [])
                edges = data.get('edges', [])
                
                # Build dag_definition
                dag_definition = json.dumps({
                    'name': name,
                    'description': description,
                    'nodes': nodes,
                    'edges': edges
                })
                
                if workflow_id:
                    # Update existing
                    self.db_facade.execute("""
                        UPDATE workflows SET 
                            name = ?, description = ?, dag_definition = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE workflow_id = ?
                    """, (name, description, dag_definition, workflow_id))
                else:
                    # Create new
                    workflow_id = str(uuid.uuid4())[:8]
                    self.db_facade.execute("""
                        INSERT INTO workflows (workflow_id, name, description, dag_definition, 
                                             status, created_by, created_at)
                        VALUES (?, ?, ?, ?, 'active', ?, CURRENT_TIMESTAMP)
                    """, (workflow_id, name, description, dag_definition, session.get('user_id')))
                
                self.log_audit('save_workflow_design', 'workflow', workflow_id)
                
                return jsonify({
                    'success': True,
                    'workflow_id': workflow_id
                })
                
            except Exception as e:
                logger.error(f"Error saving workflow design: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)})
        
        # =====================================================================
        # Execution Progress Routes
        # =====================================================================
        
        @self.app.route('/workflows/<workflow_id>/executions/<execution_id>/progress')
        @login_required
        def workflow_execution_progress(workflow_id, execution_id):
            """View workflow execution progress with visual feedback."""
            workflow = self.db_facade.fetch_one(
                "SELECT * FROM workflows WHERE workflow_id = ?",
                (workflow_id,)
            )
            
            execution = self.db_facade.fetch_one(
                "SELECT * FROM executions WHERE execution_id = ?",
                (execution_id,)
            )
            
            if not workflow or not execution:
                return render_template('errors/404.html'), 404
            
            # Get execution steps
            steps = self.db_facade.fetch_all(
                """SELECT * FROM execution_steps 
                   WHERE execution_id = ? 
                   ORDER BY step_number ASC""",
                (execution_id,)
            ) or []
            
            # Calculate progress
            total_steps = len(steps) if steps else 1
            completed_steps = len([s for s in steps if s.get('status') == 'completed'])
            progress_percent = int((completed_steps / total_steps) * 100) if total_steps > 0 else 0
            
            return render_template('user/execution_progress.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   workflow=workflow,
                                   execution=execution,
                                   steps=steps,
                                   total_steps=total_steps,
                                   completed_steps=completed_steps,
                                   progress_percent=progress_percent)
        
        logger.info("Workflow routes registered")
