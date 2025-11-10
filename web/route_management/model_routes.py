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
import logging
from typing import Optional
from model_management.model_management_db_handler import ModelManagementDBHandler
from model_management.model_registry_db import ModelRegistryDB
from web.route_management.abstract_routes import AbstractRoutes
import json

logger = logging.getLogger(__name__)


class ModelRoutes(AbstractRoutes):
    """
    Handles model and provider management routes for the application.

    This class manages routes for:
    - Viewing providers and models (all authenticated users)
    - Creating/editing/deleting providers (admin only)
    - Creating/editing/deleting models (admin only)

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
                    return render_template('providers/create_provider.html',
                                         fullname=session.get('fullname'),
                                         userid=session.get('userid'),
                                         roles=session.get('roles', []))
            
            # GET request
            return render_template('providers/create_provider.html',
                                 fullname=session.get('fullname'),
                                 userid=session.get('userid'),
                                 roles=session.get('roles', []))

        @self.app.route('/admin/provider/<provider_name>/edit', methods=['GET', 'POST'])
        @admin_required
        def edit_provider(provider_name):
            """Edit an existing provider (admin only)."""
            provider = self.db_handler.get_provider_by_name(provider_name)
            if not provider:
                flash(f'Provider "{provider_name}" not found', 'error')
                return redirect(url_for('list_providers'))
            
            # Parse notes
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
                        api_version=api_version if api_version else None,
                        base_url=base_url if base_url else None,
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
                                 provider=provider)

        @self.app.route('/api/admin/provider/<provider_name>', methods=['DELETE'])
        @admin_required
        def delete_provider(provider_name):
            """Delete a provider (admin only)."""
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
                return redirect(url_for('list_models', provider_name=provider_name))
            
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
            """Create a new model (admin only)."""
            provider = self.db_handler.get_provider_by_name(provider_name)
            if not provider:
                flash(f'Provider "{provider_name}" not found', 'error')
                return redirect(url_for('list_providers'))
            
            if request.method == 'POST':
                model_name = request.form.get('name', '').strip()
                version = request.form.get('version', '1.0').strip()
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
                    flash(f'Model "{model_name}" already exists', 'error')
                    return render_template('models/create_model.html',
                                         fullname=session.get('fullname'),
                                         userid=session.get('userid'),
                                         roles=session.get('roles', []),
                                         provider=provider)
                
                try:
                    # Insert model
                    new_model_id = self.db_handler.insert_model(
                        provider_name=provider_name,
                        name=model_name,
                        version=version,
                        description=description,
                        context_window=context_window or 4096,
                        max_output=max_output or 2048,
                        model_id=model_id or None,
                        parameters=parameters or None,
                        license=license_info or None,
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
                    return render_template('models/create_model.html',
                                         fullname=session.get('fullname'),
                                         userid=session.get('userid'),
                                         roles=session.get('roles', []),
                                         provider=provider)
            
            # GET request
            return render_template('models/create_model.html',
                                 fullname=session.get('fullname'),
                                 userid=session.get('userid'),
                                 roles=session.get('roles', []),
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
