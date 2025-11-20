"""
LLM Routes Module - Handles LLM chat interactions with session management

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
import uuid

from llm_provider.facade_cache_manager import FacadeCacheManager

logger = logging.getLogger(__name__)


class LLMRoutes(AbstractRoutes):
    """
    Handles LLM chat interaction routes with session-based facade caching.

    This class manages:
    - Chat interface rendering
    - Provider and model selection
    - Chat message sending and receiving
    - Conversation history management
    - Streaming responses
    - Session lifecycle and facade caching
    - Automatic cleanup on session end

    Attributes:
        app: Flask application instance
        llm_facade_factory: Factory for creating LLM facade instances
        model_provider_registry: Registry of model providers
        facade_cache: Cache manager for LLM facades
    """

    def __init__(self, app, db_connection_pool_name: str):
        """
        Initialize LLMRoutes.

        Args:
            app: Flask application instance
            db_connection_pool_name: Database connection pool name
        """
        super().__init__(app, db_connection_pool_name)

        # Initialize facade cache manager
        self.facade_cache = FacadeCacheManager(default_ttl_minutes=60)

        # Store active chat sessions (in production, use Redis or database)
        self._active_chat_sessions: Dict[str, Dict[str, Any]] = {}

        self.facade_cache: FacadeCacheManager = None

        logger.info("LLMRoutes initialized with facade caching")

    def set_facade_cache(self, facade_cache):
        self.facade_cache = facade_cache

    def _generate_chat_session_id(self) -> str:
        """
        Generate a unique chat session ID.

        Returns:
            Unique session identifier
        """
        return f"chat_{uuid.uuid4().hex[:16]}_{int(time.time())}"

    def _get_or_create_chat_session(self) -> str:
        """
        Get current chat session ID or create new one.

        Returns:
            Chat session ID
        """
        chat_session_id = session.get('chat_session_id')

        if not chat_session_id:
            chat_session_id = self._generate_chat_session_id()
            session['chat_session_id'] = chat_session_id
            session['chat_session_created_at'] = datetime.now().isoformat()

            # Track active session
            self._active_chat_sessions[chat_session_id] = {
                'user_id': session.get('userid'),
                'created_at': datetime.now(),
                'last_activity': datetime.now()
            }

            logger.info(f"Created new chat session: {chat_session_id} for user {session.get('userid')}")
        else:
            # Update last activity
            if chat_session_id in self._active_chat_sessions:
                self._active_chat_sessions[chat_session_id]['last_activity'] = datetime.now()

        return chat_session_id

    def _end_chat_session(self, chat_session_id: str) -> bool:
        """
        End a chat session and clean up resources.

        Args:
            chat_session_id: Chat session to end

        Returns:
            True if session was ended, False if not found
        """
        try:
            # Evict all facades for this session
            evicted = self.facade_cache.evict_session(chat_session_id)

            # Remove from active sessions
            if chat_session_id in self._active_chat_sessions:
                del self._active_chat_sessions[chat_session_id]

            # Clear from Flask session
            if session.get('chat_session_id') == chat_session_id:
                session.pop('chat_session_id', None)
                session.pop('chat_session_created_at', None)

            logger.info(
                f"Ended chat session {chat_session_id}: "
                f"Evicted {evicted} facade(s)"
            )

            return True

        except Exception as e:
            logger.error(f"Error ending chat session {chat_session_id}: {e}", exc_info=True)
            return False

    def _get_cached_facade(self, chat_session_id: str, provider_name: str,
                          model_name: str):
        """
        Get or create cached LLM facade for session.

        Args:
            chat_session_id: Chat session identifier
            provider_name: Provider name
            model_name: Model name

        Returns:
            LLM facade instance
        """
        def create_facade():
            """Factory function to create new facade."""
            return self.llm_facade_factory.create_facade(
                provider_name=provider_name,
                model_name=model_name
            )

        return self.facade_cache.get_or_create(
            chat_session_id=chat_session_id,
            provider_name=provider_name,
            model_name=model_name,
            factory_func=create_facade
        )

    def register_routes(self):
        """Register all LLM-related routes."""

        @self.app.route('/llm/chat', methods=['GET'])
        @login_required
        def llm_chat():
            """Render the chat interface page."""
            userid = session.get('userid')

            # Get or create chat session
            chat_session_id = self._get_or_create_chat_session()

            logger.info(
                f"User {userid} accessing chat interface "
                f"(session: {chat_session_id})"
            )

            return render_template('chat.html',
                                 fullname=session.get('fullname'),
                                 userid=userid,
                                 roles=session.get('roles', []),
                                 chat_session_id=chat_session_id)

        @self.app.route('/api/llm/chat/new', methods=['POST'])
        @login_required
        def new_chat_session():
            """
            Create a new chat session.

            Returns:
                JSON response with new session ID
            """
            try:
                # End current session if exists
                current_session_id = session.get('chat_session_id')
                if current_session_id:
                    self._end_chat_session(current_session_id)

                # Create new session
                chat_session_id = self._generate_chat_session_id()
                session['chat_session_id'] = chat_session_id
                session['chat_session_created_at'] = datetime.now().isoformat()

                # Track active session
                self._active_chat_sessions[chat_session_id] = {
                    'user_id': session.get('userid'),
                    'created_at': datetime.now(),
                    'last_activity': datetime.now()
                }

                logger.info(f"New chat session created: {chat_session_id}")

                return jsonify({
                    'success': True,
                    'chat_session_id': chat_session_id,
                    'message': 'New chat session created'
                })

            except Exception as e:
                logger.error(f"Error creating new chat session: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/llm/chat/end', methods=['POST'])
        @login_required
        def end_chat_session():
            """
            End current chat session and clean up resources.

            Returns:
                JSON response indicating success
            """
            try:
                chat_session_id = session.get('chat_session_id')

                if not chat_session_id:
                    return jsonify({
                        'success': False,
                        'error': 'No active chat session'
                    }), 400

                # End the session
                success = self._end_chat_session(chat_session_id)

                if success:
                    return jsonify({
                        'success': True,
                        'message': 'Chat session ended successfully'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to end chat session'
                    }), 500

            except Exception as e:
                logger.error(f"Error ending chat session: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/llm/chat/session/info', methods=['GET'])
        @login_required
        def get_session_info():
            """
            Get information about current chat session.

            Returns:
                JSON with session info and cache statistics
            """
            try:
                chat_session_id = session.get('chat_session_id')

                if not chat_session_id:
                    return jsonify({
                        'success': False,
                        'error': 'No active chat session'
                    }), 400

                # Get session info
                session_info = self._active_chat_sessions.get(chat_session_id, {})

                # Get cache stats
                cache_stats = self.facade_cache.get_stats()

                # Get facades for this session
                session_facades = cache_stats.get('facades_by_session', {}).get(chat_session_id, 0)

                return jsonify({
                    'success': True,
                    'chat_session_id': chat_session_id,
                    'created_at': session.get('chat_session_created_at'),
                    'cached_facades': session_facades,
                    'cache_stats': {
                        'total_cached_facades': cache_stats.get('total_cached_facades', 0),
                        'active_sessions': cache_stats.get('active_sessions', 0)
                    }
                })

            except Exception as e:
                logger.error(f"Error getting session info: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

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
                try:
                    self.model_provider_registry.reload_from_storage()
                except Exception as reload_error:
                    logger.warning(f"Failed to reload registry: {reload_error}")

                # Get all enabled providers
                providers = self.model_provider_registry.get_all_providers(
                    include_disabled=False
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

                # Get provider
                try:
                    provider = self.model_provider_registry.get_provider_by_name(provider_name)
                except Exception as e:
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
            Send a chat message and get response.

            Request JSON:
            {
                "provider": "provider_name",
                "model": "model_name",
                "message": "user message",
                "conversation_history": [...],  # Optional
                "parameters": {...}  # Optional generation parameters
            }

            Returns:
                JSON response with assistant reply and metadata
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

                # Get or create chat session
                chat_session_id = self._get_or_create_chat_session()

                # Build messages array
                messages = []

                if conversation_history:
                    messages.extend(conversation_history)

                messages.append({
                    'role': 'user',
                    'content': user_message
                })

                # Check if factory is initialized
                if not self.llm_facade_factory:
                    return jsonify({
                        'success': False,
                        'error': 'LLM facade factory not initialized'
                    }), 500

                # Get or create cached facade
                try:
                    llm = self._get_cached_facade(
                        chat_session_id=chat_session_id,
                        provider_name=provider_name,
                        model_name=model_name
                    )
                except Exception as e:
                    logger.error(f"Error getting LLM facade: {e}", exc_info=True)
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
                        f"Session: {chat_session_id}, "
                        f"Time: {elapsed_time:.2f}s"
                    )

                    return jsonify({
                        'success': True,
                        'response': assistant_message,
                        'metadata': {
                            'model': model_name,
                            'provider': provider_name,
                            'chat_session_id': chat_session_id,
                            'elapsed_time': elapsed_time,
                            'timestamp': datetime.now().isoformat(),
                            'usage': usage,
                            'finish_reason': metadata.get('finish_reason'),
                            'cached_facade': True  # Indicates facade was reused
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

                # Get or create chat session
                chat_session_id = self._get_or_create_chat_session()

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

                        # Get cached facade
                        llm = self._get_cached_facade(
                            chat_session_id=chat_session_id,
                            provider_name=provider_name,
                            model_name=model_name
                        )

                        # Extract parameters
                        max_tokens = parameters.get('max_tokens', 4096)
                        temperature = parameters.get('temperature', 0.7)
                        top_p = parameters.get('top_p')

                        # Call streaming chat completion
                        stream = llm.stream_chat_completion(
                            messages=messages,
                            max_tokens=max_tokens,
                            temperature=temperature,
                            top_p=top_p
                        )

                        # Stream chunks
                        for chunk in stream:
                            if chunk:
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

        logger.info("LLM routes registered with session management")


__all__ = ['LLMRoutes']