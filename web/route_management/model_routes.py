"""
Model Management Routes Module - Handles model and provider management

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
from web.route_management.abstract_routes import admin_required, login_required
from werkzeug.utils import secure_filename
import logging
from typing import Optional
from model_management.model_management_db_handler import ModelManagementDBHandler
from model_management.model_registry_db import ModelRegistryDB
from web.route_management.abstract_routes import AbstractRoutes
import json
import os
import tempfile

logger = logging.getLogger(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'json'}

def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class ModelRoutes(AbstractRoutes):
    """
    Handles model and provider management routes for the application.

    This class manages routes for:
    - Viewing providers and models (all authenticated users)
    - Creating/editing/deleting providers (admin only)
    - Creating/editing/deleting models (admin only)
    - Bulk JSON upload for providers and models (admin only)

    Attributes:
        app: Flask application instance
        db_handler: ModelManagementDBHandler instance for database operations
        registry: ModelRegistryDB instance for model registry operations
    """

    def __init__(self, app, db_connection_pool_name: str):
        """
        Initialize ModelRoutes.

        Args:
            app: Flask application instance
            db_connection_pool_name: Database connection pool name
        """
        super().__init__(app, db_connection_pool_name)
        self.db_handler = ModelManagementDBHandler.get_instance(db_connection_pool_name)
        self.registry = ModelRegistryDB.get_instance(db_connection_pool_name)
        logger.info("ModelRoutes initialized")

    def register_routes(self):
        """Register all model and provider management routes."""

        # ==================================================================================
        # JSON UPLOAD ROUTES (Admin Only)
        # ==================================================================================

        @self.app.route('/admin/provider/upload-json', methods=['GET'])
        @admin_required
        def upload_provider_json():
            """Display JSON upload page (admin only)."""
            return render_template('providers/upload_provider_json.html',
                                 fullname=session.get('fullname'),
                                 userid=session.get('userid'),
                                 roles=session.get('roles', []),
                                 is_admin=session.get('is_admin', False))

        @self.app.route('/api/admin/provider/upload-json', methods=['POST'])
        @admin_required
        def process_provider_json():
            """
            Process uploaded JSON file to create provider and models (admin only).
            
            Expected JSON structure:
            {
                "provider": "provider_name",
                "api_version": "v1",
                "base_url": "https://api.example.com",
                "notes": {...},
                "models": [
                    {
                        "name": "model-name",
                        "version": "1.0",
                        "description": "Model description",
                        "strengths": ["coding", "reasoning"],
                        "context_window": 100000,
                        "max_output": 4096,
                        "cost": {
                            "input_per_1m": 3.0,
                            "output_per_1m": 15.0
                        },
                        "capabilities": {
                            "chat": true,
                            "streaming": true,
                            "vision": true
                        }
                    }
                ]
            }
            
            Returns:
                JSON response with success status and details
            """
            try:
                # Check if file is present
                if 'json_file' not in request.files:
                    return jsonify({
                        'success': False,
                        'message': 'No file uploaded'
                    }), 400
                
                file = request.files['json_file']
                
                # Check if file is selected
                if file.filename == '':
                    return jsonify({
                        'success': False,
                        'message': 'No file selected'
                    }), 400
                
                # Validate file extension
                if not allowed_file(file.filename):
                    return jsonify({
                        'success': False,
                        'message': 'Invalid file type. Only JSON files are allowed'
                    }), 400
                
                # Read and parse JSON
                try:
                    json_data = json.load(file)
                except json.JSONDecodeError as e:
                    return jsonify({
                        'success': False,
                        'message': f'Invalid JSON format: {str(e)}'
                    }), 400
                
                # Validate required fields
                if 'provider' not in json_data:
                    return jsonify({
                        'success': False,
                        'message': 'Missing required field: provider'
                    }), 400
                
                if 'api_version' not in json_data:
                    return jsonify({
                        'success': False,
                        'message': 'Missing required field: api_version'
                    }), 400
                
                if 'models' not in json_data or not isinstance(json_data['models'], list):
                    return jsonify({
                        'success': False,
                        'message': 'Missing or invalid models array'
                    }), 400
                
                if len(json_data['models']) == 0:
                    return jsonify({
                        'success': False,
                        'message': 'Models array cannot be empty'
                    }), 400
                
                # Extract provider information
                provider_name = json_data['provider']
                api_version = json_data['api_version']
                base_url = json_data.get('base_url')
                notes = json_data.get('notes', {})
                enabled = json_data.get('enabled', True)
                
                # Check if provider exists
                existing_provider = self.db_handler.get_provider_by_name(provider_name)
                
                if existing_provider:
                    # Update existing provider
                    logger.info(f'Updating existing provider: {provider_name}')
                    success = self.db_handler.update_provider(
                        provider_name=provider_name,
                        api_version=api_version,
                        base_url=base_url,
                        notes=notes if notes else None,
                        enabled=enabled
                    )

                    if not success:
                        return jsonify({
                            'success': False,
                            'message': f'Failed to update provider "{provider_name}"'
                        }), 500

                    provider_action = 'updated'
                else:
                    # Create new provider
                    logger.info(f'Creating new provider: {provider_name}')
                    provider_id = self.db_handler.insert_provider(
                        provider=provider_name,
                        api_version=api_version,
                        base_url=base_url,
                        notes=notes if notes else None,
                        enabled=enabled
                    )

                    if not provider_id:
                        return jsonify({
                            'success': False,
                            'message': f'Failed to create provider "{provider_name}"'
                        }), 500

                    provider_action = 'created'

                # Process models
                models_created = 0
                models_updated = 0
                models_failed = []

                for model_data in json_data['models']:
                    try:
                        # Validate model required fields
                        if 'name' not in model_data:
                            models_failed.append({
                                'model': 'Unknown',
                                'reason': 'Missing name field'
                            })
                            continue

                        model_name = model_data['name']

                        # Extract model information with reasonable defaults
                        version = model_data.get('version', '1.0')
                        description = model_data.get('description', f'Model {model_name}')
                        model_id = model_data.get('model_id')

                        # Required fields with defaults (if not provided)
                        context_window = model_data.get('context_window', 8192)  # Default: 8K context
                        max_output = model_data.get('max_output', 4096)  # Default: 4K max output

                        # Optional fields
                        parameters = model_data.get('parameters')
                        license_info = model_data.get('license')
                        model_enabled = model_data.get('enabled', True)

                        # Check if model already exists
                        existing_model = self.db_handler.get_model_by_name(provider_name, model_name)

                        if existing_model:
                            # UPDATE existing model
                            logger.info(f'Model "{model_name}" already exists, updating')

                            # Update model basic info
                            update_success = self.db_handler.update_model(
                                provider_name=provider_name,
                                model_name=model_name,
                                version=version,
                                description=description,
                                model_id=model_id,
                                context_window=context_window,
                                max_output=max_output,
                                parameters=parameters,
                                license=license_info,
                                enabled=model_enabled
                            )

                            if not update_success:
                                models_failed.append({
                                    'model': model_name,
                                    'reason': 'Failed to update model'
                                })
                                continue

                            db_model_id = existing_model['id']

                            # Delete and re-insert capabilities, strengths, and costs
                            # This ensures they're always up to date
                            with self.db_handler._get_connection() as conn:
                                with self.db_handler._get_cursor(conn) as cursor:
                                    cursor.execute("DELETE FROM model_capabilities WHERE model_id = ?", (db_model_id,))
                                    cursor.execute("DELETE FROM model_strengths WHERE model_id = ?", (db_model_id,))
                                    cursor.execute("DELETE FROM model_costs WHERE model_id = ?", (db_model_id,))

                            # Insert updated capabilities
                            capabilities = model_data.get('capabilities', {})
                            if capabilities:
                                self.db_handler.insert_model_capabilities(db_model_id, capabilities)

                            # Insert updated strengths
                            strengths = model_data.get('strengths', [])
                            if strengths:
                                self.db_handler.insert_model_strengths(db_model_id, strengths)

                            # Insert updated costs
                            cost = model_data.get('cost', {})
                            if cost:
                                self.db_handler.insert_model_cost(db_model_id, cost)

                            models_updated += 1
                            logger.info(f'Model "{model_name}" updated successfully')
                        else:
                            # CREATE new model
                            logger.info(f'Creating new model: {model_name}')

                            new_model_id = self.db_handler.insert_model(
                                provider_name=provider_name,
                                name=model_name,
                                version=version,
                                description=description,
                                model_id=model_id,
                                context_window=context_window,
                                max_output=max_output,
                                parameters=parameters,
                                license=license_info,
                                enabled=model_enabled
                            )

                            if not new_model_id:
                                models_failed.append({
                                    'model': model_name,
                                    'reason': 'Failed to insert model'
                                })
                                continue

                            # Insert capabilities
                            capabilities = model_data.get('capabilities', {})
                            if capabilities:
                                self.db_handler.insert_model_capabilities(new_model_id, capabilities)

                            # Insert strengths
                            strengths = model_data.get('strengths', [])
                            if strengths:
                                self.db_handler.insert_model_strengths(new_model_id, strengths)

                            # Insert costs
                            cost = model_data.get('cost', {})
                            if cost:
                                self.db_handler.insert_model_cost(new_model_id, cost)

                            models_created += 1
                            logger.info(f'Model "{model_name}" created successfully')

                    except Exception as model_error:
                        logger.error(f'Error processing model {model_data.get("name", "unknown")}: {model_error}')
                        models_failed.append({
                            'model': model_data.get('name', 'Unknown'),
                            'reason': str(model_error)
                        })

                # Reload registry
                self.registry.reload_from_storage()

                # Prepare response
                response_data = {
                    'success': True,
                    'message': f'Provider {provider_action} successfully',
                    'provider': provider_name,
                    'provider_action': provider_action,
                    'models_created': models_created,
                    'models_updated': models_updated,
                    'models_failed': len(models_failed)
                }

                if models_failed:
                    response_data['failed_models'] = models_failed

                logger.info(f'JSON upload completed: {provider_name} - {models_created} models created, {models_updated} updated, {len(models_failed)} failed')

                return jsonify(response_data), 200

            except Exception as e:
                logger.error(f'Error processing JSON upload: {e}')
                return jsonify({
                    'success': False,
                    'message': f'Error processing upload: {str(e)}'
                }), 500

        # ==================================================================================
        # PROVIDER ROUTES (View - All Users, Manage - Admin Only)
        # ==================================================================================

        @self.app.route('/providers')
        @login_required
        def list_providers():
            """List all providers (accessible to all authenticated users)."""
            providers = self.db_handler.get_all_providers(include_disabled=True)

            # Get model counts for each provider
            for provider in providers:
                models = self.db_handler.get_models_by_provider(provider['provider'], include_disabled=True)
                provider['model_count'] = len(models)
                provider['enabled_model_count'] = len([m for m in models if m.get('enabled', True)])

            return render_template('providers/list_providers.html',
                                 fullname=session.get('fullname'),
                                 userid=session.get('userid'),
                                 roles=session.get('roles', []),
                                 is_admin=session.get('is_admin', False),
                                 providers=providers)

        @self.app.route('/provider/<provider_name>')
        @login_required
        def view_provider(provider_name):
            """View provider details (accessible to all authenticated users)."""
            provider = self.db_handler.get_provider_by_name(provider_name)
            if not provider:
                flash(f'Provider "{provider_name}" not found', 'error')
                return redirect(url_for('list_providers'))

            # Get models for this provider
            models = self.db_handler.get_models_by_provider(provider_name, include_disabled=True)

            # Parse notes if JSON
            if provider.get('notes'):
                try:
                    provider['notes_dict'] = json.loads(provider['notes'])
                except:
                    provider['notes_dict'] = {}
            else:
                provider['notes_dict'] = {}

            return render_template('providers/view_provider.html',
                                 fullname=session.get('fullname'),
                                 userid=session.get('userid'),
                                 roles=session.get('roles', []),
                                 is_admin=session.get('is_admin', False),
                                 provider=provider,
                                 models=models)

        @self.app.route('/admin/provider/create', methods=['GET', 'POST'])
        @admin_required
        def create_provider():
            """Create a new provider (admin only)."""
            if request.method == 'POST':
                provider_name = request.form.get('provider', '').strip()
                api_version = request.form.get('api_version', '').strip()
                base_url = request.form.get('base_url', '').strip()
                enabled = request.form.get('enabled') == 'true'

                # Parse notes from form
                notes = {}
                notes_fields = ['description', 'api_key_required', 'rate_limits', 'documentation_url']
                for field in notes_fields:
                    value = request.form.get(f'notes_{field}', '').strip()
                    if value:
                        notes[field] = value

                # Validation
                if not provider_name:
                    flash('Provider name is required', 'error')
                    return render_template('providers/create_provider.html',
                                         fullname=session.get('fullname'),
                                         userid=session.get('userid'),
                                         roles=session.get('roles', []))

                # Check if provider already exists
                existing = self.db_handler.get_provider_by_name(provider_name)
                if existing:
                    flash(f'Provider "{provider_name}" already exists', 'error')
                    return render_template('providers/create_provider.html',
                                         fullname=session.get('fullname'),
                                         userid=session.get('userid'),
                                         roles=session.get('roles', []))

                try:
                    # Insert provider
                    provider_id = self.db_handler.insert_provider(
                        provider=provider_name,
                        api_version=api_version or 'v1',
                        base_url=base_url or None,
                        notes=notes if notes else None,
                        enabled=enabled
                    )

                    # Reload registry
                    self.registry.reload_from_storage()

                    flash(f'Provider "{provider_name}" created successfully', 'success')
                    logger.info(f'Provider "{provider_name}" created by {session.get("userid")}')
                    return redirect(url_for('view_provider', provider_name=provider_name))

                except Exception as e:
                    flash(f'Error creating provider: {str(e)}', 'error')
                    logger.error(f'Error creating provider: {e}')

            # GET request or failed POST
            return render_template('providers/create_provider.html',
                                 fullname=session.get('fullname'),
                                 userid=session.get('userid'),
                                 roles=session.get('roles', []),
                                 is_admin=session.get('is_admin', False))

        @self.app.route('/admin/provider/<provider_name>/edit', methods=['GET', 'POST'])
        @admin_required
        def edit_provider(provider_name):
            """Edit an existing provider (admin only)."""
            provider = self.db_handler.get_provider_by_name(provider_name)
            if not provider:
                flash(f'Provider "{provider_name}" not found', 'error')
                return redirect(url_for('list_providers'))

            # Parse notes if JSON
            if provider.get('notes'):
                try:
                    provider['notes_dict'] = json.loads(provider['notes'])
                except:
                    provider['notes_dict'] = {}
            else:
                provider['notes_dict'] = {}

            if request.method == 'POST':
                api_version = request.form.get('api_version', '').strip()
                base_url = request.form.get('base_url', '').strip()
                enabled = request.form.get('enabled') == 'true'

                # Parse notes from form
                notes = {}
                notes_fields = ['description', 'api_key_required', 'rate_limits', 'documentation_url']
                for field in notes_fields:
                    value = request.form.get(f'notes_{field}', '').strip()
                    if value:
                        notes[field] = value

                try:
                    # Update provider
                    success = self.db_handler.update_provider(
                        provider_name=provider_name,
                        api_version=api_version or 'v1',
                        base_url=base_url or None,
                        notes=notes if notes else None,
                        enabled=enabled
                    )

                    if success:
                        # Reload registry
                        self.registry.reload_from_storage()

                        flash(f'Provider "{provider_name}" updated successfully', 'success')
                        logger.info(f'Provider "{provider_name}" updated by {session.get("userid")}')
                        return redirect(url_for('view_provider', provider_name=provider_name))
                    else:
                        flash(f'Failed to update provider "{provider_name}"', 'error')

                except Exception as e:
                    flash(f'Error updating provider: {str(e)}', 'error')
                    logger.error(f'Error updating provider: {e}')

            # GET request or failed POST
            return render_template('providers/edit_provider.html',
                                 fullname=session.get('fullname'),
                                 userid=session.get('userid'),
                                 roles=session.get('roles', []),
                                 is_admin=session.get('is_admin', False),
                                 provider=provider)

        @self.app.route('/api/admin/provider/<provider_name>', methods=['DELETE'])
        @admin_required
        def delete_provider(provider_name):
            """Delete a provider and all its models (admin only)."""
            try:
                success = self.db_handler.delete_provider(provider_name)

                if success:
                    # Reload registry
                    self.registry.reload_from_storage()

                    logger.info(f'Provider "{provider_name}" deleted by {session.get("userid")}')
                    return jsonify({'success': True, 'message': f'Provider "{provider_name}" deleted'})
                else:
                    return jsonify({'success': False, 'message': f'Provider "{provider_name}" not found'}), 404

            except Exception as e:
                logger.error(f'Error deleting provider: {e}')
                return jsonify({'success': False, 'message': str(e)}), 500

        # ==================================================================================
        # MODEL ROUTES (View - All Users, Manage - Admin Only)
        # ==================================================================================

        @self.app.route('/models', endpoint='manage_models_page')
        @login_required
        def manage_models():
            """Manage models page (accessible to all authenticated users)."""
            return render_template('models/manage_models.html',
                                 fullname=session.get('fullname'),
                                 userid=session.get('userid'),
                                 roles=session.get('roles', []),
                                 is_admin=session.get('is_admin', False))

        @self.app.route('/provider/<provider_name>/models')
        @login_required
        def list_models(provider_name):
            """List all models for a provider (accessible to all authenticated users)."""
            provider = self.db_handler.get_provider_by_name(provider_name)
            if not provider:
                flash(f'Provider "{provider_name}" not found', 'error')
                return redirect(url_for('list_providers'))

            models = self.db_handler.get_models_by_provider(provider_name, include_disabled=True)

            return render_template('models/list_models.html',
                                 fullname=session.get('fullname'),
                                 userid=session.get('userid'),
                                 roles=session.get('roles', []),
                                 is_admin=session.get('is_admin', False),
                                 provider=provider,
                                 models=models)

        @self.app.route('/provider/<provider_name>/model/<model_name>')
        @login_required
        def view_model(provider_name, model_name):
            """View model details (accessible to all authenticated users)."""
            provider = self.db_handler.get_provider_by_name(provider_name)
            if not provider:
                flash(f'Provider "{provider_name}" not found', 'error')
                return redirect(url_for('list_providers'))

            model = self.db_handler.get_model_by_name(provider_name, model_name)
            if not model:
                flash(f'Model "{model_name}" not found', 'error')
                return redirect(url_for('view_provider', provider_name=provider_name))

            # Get additional model data
            model_id = model['id']
            model['capabilities'] = self.db_handler.get_model_capabilities(model_id)
            model['strengths'] = self.db_handler.get_model_strengths(model_id)
            model['cost'] = self.db_handler.get_model_cost(model_id)

            return render_template('models/view_model.html',
                                 fullname=session.get('fullname'),
                                 userid=session.get('userid'),
                                 roles=session.get('roles', []),
                                 is_admin=session.get('is_admin', False),
                                 provider=provider,
                                 model=model)

        @self.app.route('/admin/provider/<provider_name>/model/create', methods=['GET', 'POST'])
        @admin_required
        def create_model(provider_name):
            """Create a new model for a provider (admin only)."""
            provider = self.db_handler.get_provider_by_name(provider_name)
            if not provider:
                flash(f'Provider "{provider_name}" not found', 'error')
                return redirect(url_for('list_providers'))

            if request.method == 'POST':
                model_name = request.form.get('name', '').strip()
                version = request.form.get('version', '').strip()
                description = request.form.get('description', '').strip()
                model_id = request.form.get('model_id', '').strip()
                context_window = request.form.get('context_window', type=int)
                max_output = request.form.get('max_output', type=int)
                parameters = request.form.get('parameters', '').strip()
                license_info = request.form.get('license', '').strip()
                enabled = request.form.get('enabled') == 'true'

                # Parse capabilities
                capabilities = {}
                cap_fields = ['chat', 'completion', 'streaming', 'vision', 'function_calling',
                             'tool_use', 'json_mode', 'embedding']
                for field in cap_fields:
                    if request.form.get(f'cap_{field}'):
                        capabilities[field] = True

                # Parse strengths
                strengths_text = request.form.get('strengths', '').strip()
                strengths = [s.strip() for s in strengths_text.split('\n') if s.strip()]

                # Parse costs
                input_cost = request.form.get('input_cost', type=float)
                output_cost = request.form.get('output_cost', type=float)

                # Validation
                if not model_name:
                    flash('Model name is required', 'error')
                    return render_template('models/create_model.html',
                                         fullname=session.get('fullname'),
                                         userid=session.get('userid'),
                                         roles=session.get('roles', []),
                                         provider=provider)

                # Check if model already exists
                existing = self.db_handler.get_model_by_name(provider_name, model_name)
                if existing:
                    flash(f'Model "{model_name}" already exists for provider "{provider_name}"', 'error')
                    return render_template('models/create_model.html',
                                         fullname=session.get('fullname'),
                                         userid=session.get('userid'),
                                         roles=session.get('roles', []),
                                         provider=provider)

                try:
                    # Insert model with defaults for required fields
                    new_model_id = self.db_handler.insert_model(
                        provider_name=provider_name,
                        name=model_name,
                        version=version if version else '1.0',
                        description=description if description else f'Model {model_name}',
                        model_id=model_id if model_id else None,
                        context_window=context_window if context_window else 8192,
                        max_output=max_output if max_output else 4096,
                        parameters=parameters if parameters else None,
                        license=license_info if license_info else None,
                        enabled=enabled
                    )

                    # Insert capabilities
                    if capabilities:
                        self.db_handler.insert_model_capabilities(new_model_id, capabilities)

                    # Insert strengths
                    if strengths:
                        self.db_handler.insert_model_strengths(new_model_id, strengths)

                    # Insert costs
                    if input_cost is not None or output_cost is not None:
                        cost_data = {}
                        if input_cost is not None:
                            cost_data['input_per_1m'] = input_cost
                        if output_cost is not None:
                            cost_data['output_per_1m'] = output_cost
                        self.db_handler.insert_model_cost(new_model_id, cost_data)

                    # Reload registry
                    self.registry.reload_from_storage()

                    flash(f'Model "{model_name}" created successfully', 'success')
                    logger.info(f'Model "{model_name}" created by {session.get("userid")}')
                    return redirect(url_for('view_model', provider_name=provider_name, model_name=model_name))

                except Exception as e:
                    flash(f'Error creating model: {str(e)}', 'error')
                    logger.error(f'Error creating model: {e}')

            # GET request or failed POST
            return render_template('models/create_model.html',
                                 fullname=session.get('fullname'),
                                 userid=session.get('userid'),
                                 roles=session.get('roles', []),
                                 is_admin=session.get('is_admin', False),
                                 provider=provider)

        @self.app.route('/admin/provider/<provider_name>/model/<model_name>/edit', methods=['GET', 'POST'])
        @admin_required
        def edit_model(provider_name, model_name):
            """Edit an existing model (admin only)."""
            provider = self.db_handler.get_provider_by_name(provider_name)
            if not provider:
                flash(f'Provider "{provider_name}" not found', 'error')
                return redirect(url_for('list_providers'))

            model = self.db_handler.get_model_by_name(provider_name, model_name)
            if not model:
                flash(f'Model "{model_name}" not found', 'error')
                return redirect(url_for('list_models', provider_name=provider_name))

            # Get additional model data
            model_id = model['id']
            model['capabilities'] = self.db_handler.get_model_capabilities(model_id)
            model['strengths'] = self.db_handler.get_model_strengths(model_id)
            model['cost'] = self.db_handler.get_model_cost(model_id)

            if request.method == 'POST':
                version = request.form.get('version', '').strip()
                description = request.form.get('description', '').strip()
                model_id_str = request.form.get('model_id', '').strip()
                context_window = request.form.get('context_window', type=int)
                max_output = request.form.get('max_output', type=int)
                parameters = request.form.get('parameters', '').strip()
                license_info = request.form.get('license', '').strip()
                enabled = request.form.get('enabled') == 'true'

                # Parse capabilities
                capabilities = {}
                cap_fields = ['chat', 'completion', 'streaming', 'vision', 'function_calling',
                             'tool_use', 'json_mode', 'embedding']
                for field in cap_fields:
                    if request.form.get(f'cap_{field}'):
                        capabilities[field] = True

                # Parse strengths
                strengths_text = request.form.get('strengths', '').strip()
                strengths = [s.strip() for s in strengths_text.split('\n') if s.strip()]

                # Parse costs
                input_cost = request.form.get('input_cost', type=float)
                output_cost = request.form.get('output_cost', type=float)

                try:
                    # Update model
                    success = self.db_handler.update_model(
                        provider_name=provider_name,
                        model_name=model_name,
                        version=version if version else None,
                        description=description if description else None,
                        model_id=model_id_str if model_id_str else None,
                        context_window=context_window if context_window else None,
                        max_output=max_output if max_output else None,
                        parameters=parameters if parameters else None,
                        license=license_info if license_info else None,
                        enabled=enabled
                    )

                    if success:
                        # Update capabilities
                        self.db_handler.delete_model_capabilities(model_id)
                        if capabilities:
                            self.db_handler.insert_model_capabilities(model_id, capabilities)

                        # Update strengths
                        self.db_handler.delete_model_strengths(model_id)
                        if strengths:
                            self.db_handler.insert_model_strengths(model_id, strengths)

                        # Update costs
                        if input_cost is not None or output_cost is not None:
                            cost_data = {}
                            if input_cost is not None:
                                cost_data['input_per_1m'] = input_cost
                            if output_cost is not None:
                                cost_data['output_per_1m'] = output_cost
                            self.db_handler.insert_model_cost(model_id, cost_data)

                        # Reload registry
                        self.registry.reload_from_storage()

                        flash(f'Model "{model_name}" updated successfully', 'success')
                        logger.info(f'Model "{model_name}" updated by {session.get("userid")}')
                        return redirect(url_for('view_model', provider_name=provider_name, model_name=model_name))
                    else:
                        flash(f'Failed to update model "{model_name}"', 'error')

                except Exception as e:
                    flash(f'Error updating model: {str(e)}', 'error')
                    logger.error(f'Error updating model: {e}')

            # GET request or failed POST
            return render_template('models/edit_model.html',
                                 fullname=session.get('fullname'),
                                 userid=session.get('userid'),
                                 roles=session.get('roles', []),
                                 provider=provider,
                                 model=model)

        @self.app.route('/api/admin/provider/<provider_name>/model/<model_name>', methods=['DELETE'])
        @admin_required
        def delete_model(provider_name, model_name):
            """Delete a model (admin only)."""
            try:
                success = self.db_handler.delete_model(provider_name, model_name)

                if success:
                    # Reload registry
                    self.registry.reload_from_storage()

                    logger.info(f'Model "{model_name}" deleted by {session.get("userid")}')
                    return jsonify({'success': True, 'message': f'Model "{model_name}" deleted'})
                else:
                    return jsonify({'success': False, 'message': f'Model "{model_name}" not found'}), 404

            except Exception as e:
                logger.error(f'Error deleting model: {e}')
                return jsonify({'success': False, 'message': str(e)}), 500

        # ==================================================================================
        # SEARCH AND QUERY ROUTES (All authenticated users)
        # ==================================================================================

        @self.app.route('/models/search')
        @login_required
        def search_models():
            """Search models by capability or other criteria."""
            capability = request.args.get('capability', '').strip()
            provider_filter = request.args.get('provider', '').strip()
            enabled_only = request.args.get('enabled_only', 'true') == 'true'

            results = []

            if capability:
                # Search by capability
                models = self.db_handler.get_models_with_capability(capability, enabled_only)
                results = models
            elif provider_filter:
                # Search by provider
                models = self.db_handler.get_models_by_provider(provider_filter, not enabled_only)
                results = models
            else:
                # Get all models
                providers = self.db_handler.get_all_providers(not enabled_only)
                for provider in providers:
                    models = self.db_handler.get_models_by_provider(provider['provider'], not enabled_only)
                    results.extend(models)

            return render_template('models/search_models.html',
                                 fullname=session.get('fullname'),
                                 userid=session.get('userid'),
                                 roles=session.get('roles', []),
                                 is_admin=session.get('is_admin', False),
                                 results=results,
                                 capability=capability,
                                 provider_filter=provider_filter,
                                 enabled_only=enabled_only)

        logger.info("Model management routes registered")