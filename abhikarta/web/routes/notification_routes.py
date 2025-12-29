"""
Notification Routes - Web routes for notification management.

Provides routes for:
- Notification channel configuration
- Webhook endpoint management
- Notification history viewing
- Test notifications
- User notification preferences

Copyright © 2025-2030, All Rights Reserved
Author: Ashutosh Sinha (ajsinha@gmail.com)
"""

import json
import logging
import uuid
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session, jsonify

from .abstract_routes import AbstractRoutes, login_required, admin_required

logger = logging.getLogger(__name__)


class NotificationRoutes(AbstractRoutes):
    """Routes for notification management."""
    
    def register_routes(self):
        """Register all notification routes."""
        self._register_channel_routes()
        self._register_webhook_routes()
        self._register_api_routes()
        self._register_settings_routes()
    
    # =========================================================================
    # CHANNEL MANAGEMENT ROUTES
    # =========================================================================
    
    def _register_channel_routes(self):
        """Register notification channel routes."""
        
        @self.app.route('/admin/notifications')
        @login_required
        @admin_required
        def notification_channels():
            """List notification channels."""
            try:
                channels = self.db_facade.fetch_all(
                    """SELECT * FROM notification_channels 
                       ORDER BY channel_type, created_at DESC"""
                ) or []
                
                # Get recent notification stats
                stats = self.db_facade.fetch_one(
                    """SELECT 
                         COUNT(*) as total,
                         SUM(CASE WHEN status = 'sent' THEN 1 ELSE 0 END) as sent,
                         SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
                       FROM notification_logs
                       WHERE created_at > datetime('now', '-7 days')"""
                ) or {'total': 0, 'sent': 0, 'failed': 0}
                
                return render_template(
                    'notifications/channels.html',
                    channels=channels,
                    stats=stats,
                    fullname=session.get('fullname'),
                    userid=session.get('user_id'),
                    roles=session.get('roles', []),
                    is_admin=session.get('is_admin', False)
                )
            except Exception as e:
                logger.error(f"Error listing notification channels: {e}")
                flash(f"Error: {e}", "danger")
                return redirect(url_for('user_dashboard'))
        
        @self.app.route('/admin/notifications/channels/new', methods=['GET', 'POST'])
        @login_required
        @admin_required
        def notification_channel_create():
            """Create a new notification channel."""
            if request.method == 'POST':
                try:
                    channel_id = str(uuid.uuid4())
                    channel_type = request.form.get('channel_type')
                    name = request.form.get('name')
                    
                    # Build config based on channel type
                    config = {}
                    if channel_type == 'slack':
                        config = {
                            'bot_token': request.form.get('slack_bot_token'),
                            'default_channel': request.form.get('slack_channel', '#notifications'),
                            'rate_limit': int(request.form.get('rate_limit', 50))
                        }
                    elif channel_type == 'teams':
                        config = {
                            'webhook_url': request.form.get('teams_webhook_url'),
                            'rate_limit': int(request.form.get('rate_limit', 30))
                        }
                    elif channel_type == 'email':
                        config = {
                            'smtp_host': request.form.get('smtp_host'),
                            'smtp_port': int(request.form.get('smtp_port', 587)),
                            'smtp_user': request.form.get('smtp_user'),
                            'smtp_password': request.form.get('smtp_password'),
                            'from_address': request.form.get('from_address'),
                            'from_name': request.form.get('from_name', 'Abhikarta')
                        }
                    
                    self.db_facade.execute(
                        """INSERT INTO notification_channels 
                           (channel_id, channel_type, name, config, is_active, created_by)
                           VALUES (?, ?, ?, ?, 1, ?)""",
                        (channel_id, channel_type, name, json.dumps(config), 
                         session.get('user_id'))
                    )
                    
                    flash(f"Notification channel '{name}' created successfully!", "success")
                    return redirect(url_for('notification_channels'))
                    
                except Exception as e:
                    logger.error(f"Error creating notification channel: {e}")
                    flash(f"Error: {e}", "danger")
            
            return render_template(
                'notifications/channel_create.html',
                fullname=session.get('fullname'),
                userid=session.get('user_id'),
                roles=session.get('roles', []),
                is_admin=session.get('is_admin', False)
            )
        
        @self.app.route('/admin/notifications/channels/<channel_id>/edit', methods=['GET', 'POST'])
        @login_required
        @admin_required
        def notification_channel_edit(channel_id):
            """Edit a notification channel."""
            channel = self.db_facade.fetch_one(
                "SELECT * FROM notification_channels WHERE channel_id = ?",
                (channel_id,)
            )
            
            if not channel:
                flash("Channel not found", "warning")
                return redirect(url_for('notification_channels'))
            
            if request.method == 'POST':
                try:
                    name = request.form.get('name')
                    is_active = 1 if request.form.get('is_active') else 0
                    
                    # Rebuild config
                    config = json.loads(channel['config'])
                    channel_type = channel['channel_type']
                    
                    if channel_type == 'slack':
                        if request.form.get('slack_bot_token'):
                            config['bot_token'] = request.form.get('slack_bot_token')
                        config['default_channel'] = request.form.get('slack_channel', config.get('default_channel'))
                        config['rate_limit'] = int(request.form.get('rate_limit', 50))
                    elif channel_type == 'teams':
                        if request.form.get('teams_webhook_url'):
                            config['webhook_url'] = request.form.get('teams_webhook_url')
                        config['rate_limit'] = int(request.form.get('rate_limit', 30))
                    
                    self.db_facade.execute(
                        """UPDATE notification_channels 
                           SET name = ?, config = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
                           WHERE channel_id = ?""",
                        (name, json.dumps(config), is_active, channel_id)
                    )
                    
                    flash(f"Channel '{name}' updated successfully!", "success")
                    return redirect(url_for('notification_channels'))
                    
                except Exception as e:
                    logger.error(f"Error updating channel: {e}")
                    flash(f"Error: {e}", "danger")
            
            # Parse config for form
            config = json.loads(channel['config']) if channel['config'] else {}
            
            return render_template(
                'notifications/channel_edit.html',
                channel=channel,
                config=config,
                fullname=session.get('fullname'),
                userid=session.get('user_id'),
                roles=session.get('roles', []),
                is_admin=session.get('is_admin', False)
            )
        
        @self.app.route('/admin/notifications/channels/<channel_id>/delete', methods=['POST'])
        @login_required
        @admin_required
        def notification_channel_delete(channel_id):
            """Delete a notification channel."""
            try:
                self.db_facade.execute(
                    "DELETE FROM notification_channels WHERE channel_id = ?",
                    (channel_id,)
                )
                flash("Channel deleted successfully!", "success")
            except Exception as e:
                logger.error(f"Error deleting channel: {e}")
                flash(f"Error: {e}", "danger")
            
            return redirect(url_for('notification_channels'))
        
        @self.app.route('/admin/notifications/logs')
        @login_required
        @admin_required
        def notification_logs():
            """View notification history."""
            try:
                channel_filter = request.args.get('channel')
                status_filter = request.args.get('status')
                
                query = "SELECT * FROM notification_logs WHERE 1=1"
                params = []
                
                if channel_filter:
                    query += " AND channel_type = ?"
                    params.append(channel_filter)
                
                if status_filter:
                    query += " AND status = ?"
                    params.append(status_filter)
                
                query += " ORDER BY created_at DESC LIMIT 200"
                
                logs = self.db_facade.fetch_all(query, tuple(params)) or []
                
                return render_template(
                    'notifications/logs.html',
                    logs=logs,
                    channel_filter=channel_filter,
                    status_filter=status_filter,
                    fullname=session.get('fullname'),
                    userid=session.get('user_id'),
                    roles=session.get('roles', []),
                    is_admin=session.get('is_admin', False)
                )
            except Exception as e:
                logger.error(f"Error loading notification logs: {e}")
                flash(f"Error: {e}", "danger")
                return redirect(url_for('notification_channels'))
    
    # =========================================================================
    # WEBHOOK ROUTES
    # =========================================================================
    
    def _register_webhook_routes(self):
        """Register webhook endpoint routes."""
        
        @self.app.route('/admin/webhooks')
        @login_required
        @admin_required
        def webhook_endpoints():
            """List webhook endpoints."""
            try:
                endpoints = self.db_facade.fetch_all(
                    """SELECT we.*, 
                              (SELECT COUNT(*) FROM webhook_events WHERE endpoint_id = we.endpoint_id) as event_count
                       FROM webhook_endpoints we
                       ORDER BY we.created_at DESC"""
                ) or []
                
                return render_template(
                    'notifications/webhooks.html',
                    endpoints=endpoints,
                    fullname=session.get('fullname'),
                    userid=session.get('user_id'),
                    roles=session.get('roles', []),
                    is_admin=session.get('is_admin', False)
                )
            except Exception as e:
                logger.error(f"Error listing webhook endpoints: {e}")
                flash(f"Error: {e}", "danger")
                return redirect(url_for('user_dashboard'))
        
        @self.app.route('/admin/webhooks/new', methods=['GET', 'POST'])
        @login_required
        @admin_required
        def webhook_create():
            """Create a new webhook endpoint."""
            if request.method == 'POST':
                try:
                    import hashlib
                    
                    endpoint_id = str(uuid.uuid4())
                    path = request.form.get('path')
                    name = request.form.get('name')
                    description = request.form.get('description', '')
                    auth_method = request.form.get('auth_method', 'hmac')
                    secret = request.form.get('secret')
                    target_type = request.form.get('target_type') or None
                    target_id = request.form.get('target_id') or None
                    rate_limit = int(request.form.get('rate_limit', 100))
                    
                    # Ensure path starts with /
                    if not path.startswith('/'):
                        path = '/' + path
                    
                    # Hash the secret
                    secret_hash = None
                    if secret:
                        secret_hash = hashlib.sha256(secret.encode()).hexdigest()
                    
                    self.db_facade.execute(
                        """INSERT INTO webhook_endpoints 
                           (endpoint_id, path, name, description, auth_method, 
                            secret_hash, target_type, target_id, rate_limit, is_active, created_by)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)""",
                        (endpoint_id, path, name, description, auth_method,
                         secret_hash, target_type, target_id, rate_limit, session.get('user_id'))
                    )
                    
                    flash(f"Webhook endpoint '{name}' created successfully!", "success")
                    return redirect(url_for('webhook_endpoints'))
                    
                except Exception as e:
                    logger.error(f"Error creating webhook endpoint: {e}")
                    flash(f"Error: {e}", "danger")
            
            # Get available agents, workflows, swarms for target selection
            agents = self.db_facade.fetch_all(
                "SELECT agent_id, name FROM agents WHERE status = 'active'"
            ) or []
            workflows = self.db_facade.fetch_all(
                "SELECT workflow_id, name FROM workflows WHERE status = 'active'"
            ) or []
            swarms = self.db_facade.fetch_all(
                "SELECT swarm_id, name FROM swarms WHERE status != 'deleted'"
            ) or []
            
            return render_template(
                'notifications/webhook_create.html',
                agents=agents,
                workflows=workflows,
                swarms=swarms,
                fullname=session.get('fullname'),
                userid=session.get('user_id'),
                roles=session.get('roles', []),
                is_admin=session.get('is_admin', False)
            )
        
        @self.app.route('/admin/webhooks/<endpoint_id>')
        @login_required
        @admin_required
        def webhook_view(endpoint_id):
            """View webhook endpoint details and events."""
            try:
                endpoint = self.db_facade.fetch_one(
                    "SELECT * FROM webhook_endpoints WHERE endpoint_id = ?",
                    (endpoint_id,)
                )
                
                if not endpoint:
                    flash("Webhook endpoint not found", "warning")
                    return redirect(url_for('webhook_endpoints'))
                
                # Get recent events
                events = self.db_facade.fetch_all(
                    """SELECT * FROM webhook_events 
                       WHERE endpoint_id = ?
                       ORDER BY received_at DESC LIMIT 50""",
                    (endpoint_id,)
                ) or []
                
                return render_template(
                    'notifications/webhook_view.html',
                    endpoint=endpoint,
                    events=events,
                    fullname=session.get('fullname'),
                    userid=session.get('user_id'),
                    roles=session.get('roles', []),
                    is_admin=session.get('is_admin', False)
                )
            except Exception as e:
                logger.error(f"Error viewing webhook endpoint: {e}")
                flash(f"Error: {e}", "danger")
                return redirect(url_for('webhook_endpoints'))
        
        @self.app.route('/admin/webhooks/<endpoint_id>/edit', methods=['GET', 'POST'])
        @login_required
        @admin_required
        def webhook_edit(endpoint_id):
            """Edit a webhook endpoint."""
            try:
                endpoint = self.db_facade.fetch_one(
                    "SELECT * FROM webhook_endpoints WHERE endpoint_id = ?",
                    (endpoint_id,)
                )
                
                if not endpoint:
                    flash("Webhook endpoint not found", "warning")
                    return redirect(url_for('webhook_endpoints'))
                
                if request.method == 'POST':
                    name = request.form.get('name')
                    description = request.form.get('description', '')
                    auth_method = request.form.get('auth_method', 'hmac')
                    target_type = request.form.get('target_type') or None
                    target_id = request.form.get('target_id') or None
                    rate_limit = int(request.form.get('rate_limit', 100))
                    is_active = 1 if request.form.get('is_active') else 0
                    
                    # Update secret if provided
                    secret = request.form.get('secret')
                    if secret:
                        import hashlib
                        secret_hash = hashlib.sha256(secret.encode()).hexdigest()
                        self.db_facade.execute(
                            """UPDATE webhook_endpoints 
                               SET name = ?, description = ?, auth_method = ?, 
                                   secret_hash = ?, target_type = ?, target_id = ?, 
                                   rate_limit = ?, is_active = ?
                               WHERE endpoint_id = ?""",
                            (name, description, auth_method, secret_hash, 
                             target_type, target_id, rate_limit, is_active, endpoint_id)
                        )
                    else:
                        self.db_facade.execute(
                            """UPDATE webhook_endpoints 
                               SET name = ?, description = ?, auth_method = ?, 
                                   target_type = ?, target_id = ?, rate_limit = ?, is_active = ?
                               WHERE endpoint_id = ?""",
                            (name, description, auth_method, target_type, 
                             target_id, rate_limit, is_active, endpoint_id)
                        )
                    
                    flash(f"Webhook endpoint '{name}' updated!", "success")
                    return redirect(url_for('webhook_endpoints'))
                
                # Get available agents, workflows, swarms for target selection
                agents = self.db_facade.fetch_all(
                    "SELECT agent_id, name FROM agents WHERE status = 'active'"
                ) or []
                workflows = self.db_facade.fetch_all(
                    "SELECT workflow_id, name FROM workflows WHERE status = 'active'"
                ) or []
                swarms = self.db_facade.fetch_all(
                    "SELECT swarm_id, name FROM swarms WHERE status != 'deleted'"
                ) or []
                
                return render_template(
                    'notifications/webhook_edit.html',
                    endpoint=endpoint,
                    agents=agents,
                    workflows=workflows,
                    swarms=swarms,
                    fullname=session.get('fullname'),
                    userid=session.get('user_id'),
                    roles=session.get('roles', []),
                    is_admin=session.get('is_admin', False)
                )
            except Exception as e:
                logger.error(f"Error editing webhook endpoint: {e}")
                flash(f"Error: {e}", "danger")
                return redirect(url_for('webhook_endpoints'))
        
        @self.app.route('/admin/webhooks/events')
        @self.app.route('/admin/webhooks/<endpoint_id>/events')
        @login_required
        @admin_required
        def webhook_events(endpoint_id=None):
            """View webhook events."""
            try:
                endpoint = None
                if endpoint_id:
                    endpoint = self.db_facade.fetch_one(
                        "SELECT * FROM webhook_endpoints WHERE endpoint_id = ?",
                        (endpoint_id,)
                    )
                    events = self.db_facade.fetch_all(
                        """SELECT we.*, wep.name as endpoint_name, wep.path 
                           FROM webhook_events we
                           JOIN webhook_endpoints wep ON we.endpoint_id = wep.endpoint_id
                           WHERE we.endpoint_id = ?
                           ORDER BY we.received_at DESC LIMIT 100""",
                        (endpoint_id,)
                    ) or []
                else:
                    events = self.db_facade.fetch_all(
                        """SELECT we.*, wep.name as endpoint_name, wep.path 
                           FROM webhook_events we
                           JOIN webhook_endpoints wep ON we.endpoint_id = wep.endpoint_id
                           ORDER BY we.received_at DESC LIMIT 100"""
                    ) or []
                
                return render_template(
                    'notifications/webhook_events.html',
                    endpoint=endpoint,
                    events=events,
                    fullname=session.get('fullname'),
                    userid=session.get('user_id'),
                    roles=session.get('roles', []),
                    is_admin=session.get('is_admin', False)
                )
            except Exception as e:
                logger.error(f"Error listing webhook events: {e}")
                flash(f"Error: {e}", "danger")
                return redirect(url_for('webhook_endpoints'))
        
        @self.app.route('/admin/webhooks/<endpoint_id>/delete', methods=['POST'])
        @login_required
        @admin_required
        def webhook_delete(endpoint_id):
            """Delete a webhook endpoint."""
            try:
                self.db_facade.execute(
                    "UPDATE webhook_endpoints SET is_active = 0 WHERE endpoint_id = ?",
                    (endpoint_id,)
                )
                flash("Webhook endpoint deactivated!", "success")
            except Exception as e:
                logger.error(f"Error deleting webhook: {e}")
                flash(f"Error: {e}", "danger")
            
            return redirect(url_for('webhook_endpoints'))
        
        # Public webhook receiver endpoint
        @self.app.route('/api/webhooks/<path:webhook_path>', methods=['POST', 'GET'])
        def receive_webhook(webhook_path):
            """Receive incoming webhook events."""
            try:
                path = f"/api/webhooks/{webhook_path}"
                
                # Find endpoint
                endpoint = self.db_facade.fetch_one(
                    "SELECT * FROM webhook_endpoints WHERE path = ? AND is_active = 1",
                    (path,)
                )
                
                if not endpoint:
                    # Try with leading slash variations
                    endpoint = self.db_facade.fetch_one(
                        "SELECT * FROM webhook_endpoints WHERE path = ? AND is_active = 1",
                        (f"/{webhook_path}",)
                    )
                
                if not endpoint:
                    return jsonify({"error": "Endpoint not found"}), 404
                
                # Log the event
                event_id = str(uuid.uuid4())
                payload = request.get_json(force=True, silent=True) or {}
                headers = dict(request.headers)
                
                # Basic verification (full verification in WebhookReceiver)
                verified = True  # Simplified for now
                
                self.db_facade.execute(
                    """INSERT INTO webhook_events 
                       (event_id, endpoint_id, event_type, payload, headers, source_ip, verified)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (event_id, endpoint['endpoint_id'], 
                     headers.get('X-Event-Type') or payload.get('type'),
                     json.dumps(payload), json.dumps(headers),
                     request.remote_addr, 1 if verified else 0)
                )
                
                # TODO: Dispatch to target agent/workflow/swarm
                
                return jsonify({
                    "success": True,
                    "event_id": event_id,
                    "message": "Webhook received"
                }), 200
                
            except Exception as e:
                logger.error(f"Error receiving webhook: {e}")
                return jsonify({"error": str(e)}), 500
    
    # =========================================================================
    # API ROUTES
    # =========================================================================
    
    def _register_api_routes(self):
        """Register notification API routes."""
        
        @self.app.route('/api/notifications/test/<channel_id>', methods=['POST'])
        @login_required
        def api_test_notification(channel_id):
            """Test a notification channel."""
            try:
                channel = self.db_facade.fetch_one(
                    "SELECT * FROM notification_channels WHERE channel_id = ?",
                    (channel_id,)
                )
                
                if not channel:
                    return jsonify({"success": False, "error": "Channel not found"}), 404
                
                config = json.loads(channel['config']) if channel['config'] else {}
                
                # Import notification module
                from ..notification import (
                    NotificationManager, NotificationMessage, 
                    NotificationLevel, SlackConfig, TeamsConfig
                )
                
                manager = NotificationManager()
                
                # Configure based on type
                if channel['channel_type'] == 'slack':
                    manager.configure_slack(SlackConfig(
                        bot_token=config.get('bot_token', ''),
                        default_channel=config.get('default_channel', '#notifications')
                    ))
                elif channel['channel_type'] == 'teams':
                    manager.configure_teams(TeamsConfig(
                        webhook_url=config.get('webhook_url', '')
                    ))
                
                # Run async test
                import asyncio
                
                async def run_test():
                    return await manager.test_channel(channel['channel_type'])
                
                result = asyncio.run(run_test())
                
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"Error testing notification channel: {e}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route('/api/notifications/send', methods=['POST'])
        @login_required
        def api_send_notification():
            """Send a notification via API."""
            try:
                data = request.get_json()
                
                channels = data.get('channels', ['slack'])
                title = data.get('title', 'Notification')
                body = data.get('body', '')
                level = data.get('level', 'info')
                fields = data.get('fields', {})
                
                # Get channel configs
                from ..notification import (
                    NotificationManager, NotificationMessage,
                    NotificationLevel, SlackConfig, TeamsConfig
                )
                
                manager = NotificationManager(self.db_facade)
                
                for channel_type in channels:
                    channel = self.db_facade.fetch_one(
                        """SELECT * FROM notification_channels 
                           WHERE channel_type = ? AND is_active = 1
                           LIMIT 1""",
                        (channel_type,)
                    )
                    
                    if channel:
                        config = json.loads(channel['config']) if channel['config'] else {}
                        
                        if channel_type == 'slack':
                            manager.configure_slack(SlackConfig(
                                bot_token=config.get('bot_token', ''),
                                default_channel=config.get('default_channel', '#notifications')
                            ))
                        elif channel_type == 'teams':
                            manager.configure_teams(TeamsConfig(
                                webhook_url=config.get('webhook_url', '')
                            ))
                
                # Send notification
                import asyncio
                
                message = NotificationMessage(
                    title=title,
                    body=body,
                    level=NotificationLevel(level),
                    fields=fields,
                    source=session.get('user_id', 'api'),
                    source_type='api'
                )
                
                async def send():
                    return await manager.send(channels, message)
                
                results = asyncio.run(send())
                
                return jsonify({
                    "success": True,
                    "results": [r.to_dict() for r in results]
                })
                
            except Exception as e:
                logger.error(f"Error sending notification: {e}")
                return jsonify({"success": False, "error": str(e)}), 500
    
    # =========================================================================
    # USER SETTINGS ROUTES
    # =========================================================================
    
    def _register_settings_routes(self):
        """Register user notification settings routes."""
        
        @self.app.route('/user/notifications')
        @login_required
        def user_notification_settings():
            """User notification preferences."""
            try:
                user_id = session.get('user_id')
                
                # Get user preferences
                prefs = self.db_facade.fetch_all(
                    """SELECT * FROM user_notification_preferences 
                       WHERE user_id = ?""",
                    (user_id,)
                ) or []
                
                # Get available channels
                channels = self.db_facade.fetch_all(
                    "SELECT DISTINCT channel_type FROM notification_channels WHERE is_active = 1"
                ) or []
                
                return render_template(
                    'notifications/user_settings.html',
                    preferences=prefs,
                    channels=channels,
                    fullname=session.get('fullname'),
                    userid=user_id,
                    roles=session.get('roles', []),
                    is_admin=session.get('is_admin', False)
                )
            except Exception as e:
                logger.error(f"Error loading notification settings: {e}")
                flash(f"Error: {e}", "danger")
                return redirect(url_for('user_dashboard'))
        
        @self.app.route('/user/notifications', methods=['POST'])
        @login_required
        def user_notification_settings_save():
            """Save user notification preferences."""
            try:
                user_id = session.get('user_id')
                
                # Process form data
                for channel_type in ['slack', 'teams', 'email']:
                    enabled = 1 if request.form.get(f'{channel_type}_enabled') else 0
                    address = request.form.get(f'{channel_type}_address', '')
                    min_level = request.form.get(f'{channel_type}_min_level', 'info')
                    
                    # Upsert preference
                    self.db_facade.execute(
                        """INSERT INTO user_notification_preferences 
                           (user_id, channel_type, channel_address, enabled, min_level)
                           VALUES (?, ?, ?, ?, ?)
                           ON CONFLICT(user_id, channel_type) 
                           DO UPDATE SET 
                             channel_address = excluded.channel_address,
                             enabled = excluded.enabled,
                             min_level = excluded.min_level,
                             updated_at = CURRENT_TIMESTAMP""",
                        (user_id, channel_type, address, enabled, min_level)
                    )
                
                flash("Notification preferences saved!", "success")
                
            except Exception as e:
                logger.error(f"Error saving notification settings: {e}")
                flash(f"Error: {e}", "danger")
            
            return redirect(url_for('user_notification_settings'))
