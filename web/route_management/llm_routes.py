"""
LLM Routes Module - Handles LLM chat interactions

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha | Email: ajsinha@gmail.com

Legal Notice:
This module and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

Patent Pending: Certain architectural patterns and implementations described in this
module may be subject to patent applications.
"""

from flask import render_template, request, redirect, url_for, session, flash, jsonify, Response, stream_with_context
from web.route_management.abstract_routes import login_required
from web.route_management.abstract_routes import AbstractRoutes
import logging
import json
from typing import Dict, Any, List, Optional
import time
from datetime import datetime


logger = logging.getLogger(__name__)


class LLMRoutes(AbstractRoutes):
    """
    Handles LLM chat interaction routes.

    This class manages:
    - Chat interface rendering
    - Provider and model selection
    - Chat message sending and receiving
    - Conversation history management
    - Streaming responses

    Attributes:
        app: Flask application instance
        llm_facade_factory: Factory for creating LLM facade instances
        model_provider_registry: Registry of model providers
    """

    def __init__(self, app, db_connection_pool_name: str):
        """
        Initialize LLMRoutes.

        Args:
            app: Flask application instance
            db_connection_pool_name: Database connection pool name
        """
        super().__init__(app, db_connection_pool_name)


        # Store active LLM sessions (in production, use Redis or database)
        self._active_sessions: Dict[str, Dict[str, Any]] = {}

        logger.info("LLMRoutes initialized")



    def register_routes(self):
        """Register all LLM-related routes."""

        @self.app.route('/llm/chat', methods=['GET'])
        @login_required
        def llm_chat():
            """Render the chat interface page."""
            userid = session.get('userid')
            logger.info(f"User {userid} accessing chat interface")

            return render_template('chat.html',
                                 fullname=session.get('fullname'),
                                 userid=userid,
                                 roles=session.get('roles', []))

        @self.app.route('/api/llm/providers', methods=['GET'])
        @login_required
        def get_providers():
            """
            Get list of available LLM providers.

            Returns:
                JSON response with list of providers
            """
            try:
                if not self.model_provider_registry:
                    return jsonify({
                        'success': False,
                        'error': 'Model provider registry not initialized'
                    }), 500

                # Reload from database to get latest providers
                # This ensures newly added providers are visible
                try:
                    self.model_provider_registry.reload_from_storage()
                except Exception as reload_error:
                    logger.warning(f"Failed to reload registry: {reload_error}")

                # Get all enabled providers
                providers = self.model_provider_registry.get_all_providers(
                    include_disabled=False  # False = only enabled providers
                )

                provider_list = []
                for provider_name, provider_obj in providers.items():
                    provider_list.append({
                        'name': provider_name,
                        'display_name': provider_name.title(),
                        'enabled': provider_obj.enabled,
                        'model_count': len([m for m in provider_obj.models if m.enabled])
                    })

                # Sort by display name
                provider_list.sort(key=lambda x: x['display_name'])

                logger.info(f"Returning {len(provider_list)} providers")

                return jsonify({
                    'success': True,
                    'providers': provider_list
                })

            except Exception as e:
                logger.error(f"Error getting providers: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/llm/models/<provider_name>', methods=['GET'])
        @login_required
        def get_provider_models(provider_name: str):
            """
            Get list of models for a specific provider.

            Args:
                provider_name: Name of the provider

            Returns:
                JSON response with list of models
            """
            try:
                if not self.model_provider_registry:
                    return jsonify({
                        'success': False,
                        'error': 'Model provider registry not initialized'
                    }), 500

                # Get provider - this raises exceptions if not found or disabled
                try:
                    provider = self.model_provider_registry.get_provider_by_name(provider_name)
                except Exception as e:
                    # Handle ProviderNotFoundException or ProviderDisabledException
                    error_msg = str(e)
                    if 'not found' in error_msg.lower():
                        return jsonify({
                            'success': False,
                            'error': f'Provider {provider_name} not found'
                        }), 404
                    elif 'disabled' in error_msg.lower():
                        return jsonify({
                            'success': False,
                            'error': f'Provider {provider_name} is disabled'
                        }), 403
                    else:
                        return jsonify({
                            'success': False,
                            'error': f'Error accessing provider: {error_msg}'
                        }), 500

                # Get enabled models
                models = provider.get_all_models(include_disabled=False)

                model_list = []
                for model in models:
                    # Build model info
                    model_info = {
                        'name': model.name,
                        'display_name': f"{model.name} ({model.version})",
                        'version': model.version,
                        'description': model.description,
                        'context_window': model.context_window,
                        'max_output': model.max_output,
                        'capabilities': model.capabilities,
                        'cost': model.cost
                    }
                    model_list.append(model_info)

                # Sort by name
                model_list.sort(key=lambda x: x['name'])

                logger.info(f"Returning {len(model_list)} models for provider {provider_name}")

                return jsonify({
                    'success': True,
                    'provider': provider_name,
                    'models': model_list
                })

            except Exception as e:
                logger.error(f"Error getting models for provider {provider_name}: {e}",
                           exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/llm/chat/send', methods=['POST'])
        @login_required
        def send_chat_message():
            """
            Send a chat message to the LLM and get response.

            Request JSON:
                {
                    "provider": "anthropic",
                    "model": "claude-3-opus-20240229",
                    "message": "Hello, world!",
                    "conversation_history": [
                        {"role": "user", "content": "..."},
                        {"role": "assistant", "content": "..."}
                    ],
                    "parameters": {
                        "temperature": 0.7,
                        "max_tokens": 4096
                    }
                }

            Returns:
                JSON response with LLM response
            """
            try:
                data = request.get_json()

                if not data:
                    return jsonify({
                        'success': False,
                        'error': 'No data provided'
                    }), 400

                provider_name = data.get('provider')
                model_name = data.get('model')
                user_message = data.get('message', '').strip()
                conversation_history = data.get('conversation_history', [])
                parameters = data.get('parameters', {})

                # Validate inputs
                if not provider_name or not model_name:
                    return jsonify({
                        'success': False,
                        'error': 'Provider and model are required'
                    }), 400

                if not user_message:
                    return jsonify({
                        'success': False,
                        'error': 'Message cannot be empty'
                    }), 400

                # Build messages array
                messages = []

                # Add conversation history
                if conversation_history:
                    messages.extend(conversation_history)

                # Add current user message
                messages.append({
                    'role': 'user',
                    'content': user_message
                })

                # Get LLM facade instance
                if not self.llm_facade_factory:
                    return jsonify({
                        'success': False,
                        'error': 'LLM facade factory not initialized'
                    }), 500

                # Create LLM facade for this provider and model
                try:
                    llm = self.llm_facade_factory.create_facade(
                        provider_name=provider_name,
                        model_name=model_name
                    )
                except Exception as e:
                    logger.error(f"Error creating LLM facade: {e}", exc_info=True)
                    return jsonify({
                        'success': False,
                        'error': f'Failed to initialize LLM: {str(e)}'
                    }), 500

                # Call LLM
                start_time = time.time()

                try:
                    # Extract generation parameters
                    max_tokens = parameters.get('max_tokens', 4096)
                    temperature = parameters.get('temperature', 0.7)
                    top_p = parameters.get('top_p')

                    # Call chat completion
                    response = llm.chat_completion(
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        top_p=top_p
                    )

                    elapsed_time = time.time() - start_time

                    # Extract response content
                    assistant_message = response.get('content', '')

                    # Extract metadata
                    metadata = response.get('metadata', {})
                    usage = response.get('usage', {})

                    logger.info(
                        f"Chat completed for user {session.get('userid')} - "
                        f"Provider: {provider_name}, Model: {model_name}, "
                        f"Time: {elapsed_time:.2f}s"
                    )

                    return jsonify({
                        'success': True,
                        'response': assistant_message,
                        'metadata': {
                            'model': model_name,
                            'provider': provider_name,
                            'elapsed_time': elapsed_time,
                            'timestamp': datetime.now().isoformat(),
                            'usage': usage,
                            'finish_reason': metadata.get('finish_reason')
                        }
                    })

                except Exception as e:
                    logger.error(f"Error calling LLM: {e}", exc_info=True)
                    return jsonify({
                        'success': False,
                        'error': f'LLM call failed: {str(e)}'
                    }), 500

            except Exception as e:
                logger.error(f"Error in send_chat_message: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/llm/chat/stream', methods=['POST'])
        @login_required
        def stream_chat_message():
            """
            Send a chat message and stream the response.

            Request JSON: Same as send_chat_message

            Returns:
                Server-Sent Events stream with response chunks
            """
            try:
                data = request.get_json()

                if not data:
                    return jsonify({
                        'success': False,
                        'error': 'No data provided'
                    }), 400

                provider_name = data.get('provider')
                model_name = data.get('model')
                user_message = data.get('message', '').strip()
                conversation_history = data.get('conversation_history', [])
                parameters = data.get('parameters', {})

                # Validate inputs
                if not provider_name or not model_name or not user_message:
                    return jsonify({
                        'success': False,
                        'error': 'Provider, model, and message are required'
                    }), 400

                def generate():
                    """Generator function for streaming response."""
                    try:
                        # Build messages array
                        messages = []

                        if conversation_history:
                            messages.extend(conversation_history)

                        messages.append({
                            'role': 'user',
                            'content': user_message
                        })

                        # Get LLM facade instance
                        llm = self.llm_facade_factory.create_llm(
                            provider=provider_name,
                            model=model_name
                        )

                        # Extract parameters
                        max_tokens = parameters.get('max_tokens', 4096)
                        temperature = parameters.get('temperature', 0.7)
                        top_p = parameters.get('top_p')

                        # Call streaming chat completion
                        stream = llm.chat_completion_stream(
                            messages=messages,
                            max_tokens=max_tokens,
                            temperature=temperature,
                            top_p=top_p
                        )

                        # Stream chunks
                        for chunk in stream:
                            if chunk:
                                # Send as Server-Sent Event
                                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

                        # Send completion event
                        yield f"data: {json.dumps({'done': True})}\n\n"

                    except Exception as e:
                        logger.error(f"Error in streaming: {e}", exc_info=True)
                        yield f"data: {json.dumps({'error': str(e)})}\n\n"

                return Response(
                    stream_with_context(generate()),
                    mimetype='text/event-stream',
                    headers={
                        'Cache-Control': 'no-cache',
                        'X-Accel-Buffering': 'no'
                    }
                )

            except Exception as e:
                logger.error(f"Error in stream_chat_message: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/llm/registry/reload', methods=['POST'])
        @login_required
        def reload_registry():
            """
            Manually reload the model registry from database.

            This is useful after adding/updating providers or models in the database.

            Returns:
                JSON response indicating success
            """
            try:
                if not self.model_provider_registry:
                    return jsonify({
                        'success': False,
                        'error': 'Model provider registry not initialized'
                    }), 500

                # Reload from storage
                self.model_provider_registry.reload_from_storage()

                # Get updated counts
                providers = self.model_provider_registry.get_all_providers(include_disabled=False)

                logger.info(f"Registry reloaded by user {session.get('userid')} - {len(providers)} providers loaded")

                return jsonify({
                    'success': True,
                    'message': 'Model registry reloaded successfully',
                    'provider_count': len(providers)
                })

            except Exception as e:
                logger.error(f"Error reloading registry: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        logger.info("LLM routes registered")


__all__ = ['LLMRoutes']