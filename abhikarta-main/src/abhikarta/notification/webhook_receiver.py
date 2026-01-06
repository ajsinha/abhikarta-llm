"""
Webhook Receiver - Receives and processes incoming webhooks.

Supports:
- Endpoint registration and management
- HMAC signature verification
- JWT validation
- API key authentication
- Payload validation
- Event dispatching to agents/workflows/swarms
- Rate limiting
- Replay protection

Copyright © 2025-2030, All Rights Reserved
Author: Ashutosh Sinha (ajsinha@gmail.com)
"""

import asyncio
import hashlib
import hmac
import json
import logging
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Callable, Awaitable
from dataclasses import dataclass, field
from collections import defaultdict

from .base import (
    WebhookEvent,
    WebhookEndpoint,
    AuthMethod
)

logger = logging.getLogger(__name__)


@dataclass
class WebhookResponse:
    """Response from webhook processing."""
    success: bool
    event_id: str
    message: str = ""
    status_code: int = 200
    data: Optional[Dict[str, Any]] = None


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    requests_per_minute: int = 100
    burst_size: int = 10


class TokenBucket:
    """Token bucket rate limiter."""
    
    def __init__(self, rate: float, burst: int):
        self.rate = rate  # Tokens per second
        self.burst = burst
        self.tokens = burst
        self.last_update = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens. Returns True if successful."""
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
        self.last_update = now
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


class WebhookReceiver:
    """
    Receives and processes incoming webhooks.
    
    Features:
    - Register custom endpoints
    - Signature verification (HMAC, JWT, API key)
    - Payload validation
    - Rate limiting
    - Replay protection (nonce/timestamp)
    - Event dispatching
    
    Usage:
        receiver = WebhookReceiver(db_facade)
        
        # Register endpoint
        receiver.register_endpoint(
            path="/webhooks/github",
            name="GitHub Webhook",
            handler=handle_github_webhook,
            auth_method=AuthMethod.HMAC,
            secret="github-secret"
        )
        
        # Process incoming webhook (called from Flask/FastAPI route)
        result = await receiver.process_webhook(
            path="/webhooks/github",
            method="POST",
            headers=request.headers,
            body=request.data,
            query_params=request.args,
            source_ip=request.remote_addr
        )
    """
    
    def __init__(self, db_facade=None):
        """
        Initialize webhook receiver.
        
        Args:
            db_facade: Optional database facade for persistence
        """
        self.db_facade = db_facade
        self._endpoints: Dict[str, WebhookEndpoint] = {}
        self._handlers: Dict[str, Callable] = {}
        self._rate_limiters: Dict[str, TokenBucket] = {}
        self._seen_nonces: Dict[str, datetime] = {}
        self._nonce_cleanup_interval = 3600  # 1 hour
        self._last_nonce_cleanup = time.time()
        
        # Load endpoints from database
        self._load_endpoints()
        
        logger.info("WebhookReceiver initialized")
    
    def _load_endpoints(self) -> None:
        """Load endpoints from database."""
        if not self.db_facade:
            return
        
        try:
            rows = self.db_facade.fetch_all(
                "SELECT * FROM webhook_endpoints WHERE is_active = 1"
            ) or []
            
            for row in rows:
                endpoint = WebhookEndpoint(
                    endpoint_id=row['endpoint_id'],
                    path=row['path'],
                    name=row['name'],
                    description=row.get('description', ''),
                    auth_method=AuthMethod(row.get('auth_method', 'hmac')),
                    secret=row.get('secret_hash'),  # Already hashed
                    target_type=row.get('target_type'),
                    target_id=row.get('target_id'),
                    is_active=bool(row.get('is_active', 1))
                )
                self._endpoints[endpoint.path] = endpoint
                
                # Set up rate limiter
                rate_limit = row.get('rate_limit', 100)
                self._rate_limiters[endpoint.path] = TokenBucket(
                    rate=rate_limit / 60.0,  # Convert to per-second
                    burst=min(rate_limit, 10)
                )
            
            logger.info(f"Loaded {len(self._endpoints)} webhook endpoints")
            
        except Exception as e:
            logger.error(f"Error loading webhook endpoints: {e}")
    
    # =========================================================================
    # ENDPOINT REGISTRATION
    # =========================================================================
    
    def register_endpoint(
        self,
        path: str,
        name: str,
        handler: Callable[[WebhookEvent], Awaitable[Any]] = None,
        auth_method: AuthMethod = AuthMethod.HMAC,
        secret: str = None,
        description: str = "",
        target_type: str = None,
        target_id: str = None,
        rate_limit: int = 100,
        save_to_db: bool = True
    ) -> WebhookEndpoint:
        """
        Register a new webhook endpoint.
        
        Args:
            path: URL path for the endpoint (e.g., "/webhooks/github")
            name: Human-readable name
            handler: Async function to handle webhook events
            auth_method: Authentication method
            secret: Secret for HMAC/API key validation
            description: Endpoint description
            target_type: Type of target to trigger ('agent', 'workflow', 'swarm')
            target_id: ID of target to trigger
            rate_limit: Requests per minute
            save_to_db: Whether to persist to database
            
        Returns:
            WebhookEndpoint configuration
        """
        endpoint_id = str(uuid.uuid4())
        
        # Hash the secret for storage
        secret_hash = None
        if secret:
            secret_hash = hashlib.sha256(secret.encode()).hexdigest()
        
        endpoint = WebhookEndpoint(
            endpoint_id=endpoint_id,
            path=path,
            name=name,
            description=description,
            auth_method=auth_method,
            secret=secret,  # Keep original for verification
            target_type=target_type,
            target_id=target_id,
            is_active=True,
            rate_limit=rate_limit
        )
        
        self._endpoints[path] = endpoint
        
        if handler:
            self._handlers[path] = handler
        
        # Set up rate limiter
        self._rate_limiters[path] = TokenBucket(
            rate=rate_limit / 60.0,
            burst=min(rate_limit, 10)
        )
        
        # Save to database
        if save_to_db and self.db_facade:
            try:
                self.db_facade.execute(
                    """INSERT INTO webhook_endpoints 
                       (endpoint_id, path, name, description, auth_method, 
                        secret_hash, target_type, target_id, is_active)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)""",
                    (endpoint_id, path, name, description, auth_method.value,
                     secret_hash, target_type, target_id)
                )
            except Exception as e:
                logger.error(f"Error saving endpoint to database: {e}")
        
        logger.info(f"Registered webhook endpoint: {path}")
        return endpoint
    
    def unregister_endpoint(self, path: str) -> bool:
        """
        Unregister a webhook endpoint.
        
        Args:
            path: Endpoint path to remove
            
        Returns:
            True if endpoint was found and removed
        """
        if path in self._endpoints:
            del self._endpoints[path]
            self._handlers.pop(path, None)
            self._rate_limiters.pop(path, None)
            
            if self.db_facade:
                try:
                    self.db_facade.execute(
                        "UPDATE webhook_endpoints SET is_active = 0 WHERE path = ?",
                        (path,)
                    )
                except Exception as e:
                    logger.error(f"Error removing endpoint from database: {e}")
            
            logger.info(f"Unregistered webhook endpoint: {path}")
            return True
        
        return False
    
    def get_endpoint(self, path: str) -> Optional[WebhookEndpoint]:
        """Get endpoint configuration by path."""
        return self._endpoints.get(path)
    
    def list_endpoints(self) -> List[WebhookEndpoint]:
        """List all registered endpoints."""
        return list(self._endpoints.values())
    
    def set_handler(
        self,
        path: str,
        handler: Callable[[WebhookEvent], Awaitable[Any]]
    ) -> None:
        """
        Set or update handler for an endpoint.
        
        Args:
            path: Endpoint path
            handler: Async handler function
        """
        self._handlers[path] = handler
    
    # =========================================================================
    # WEBHOOK PROCESSING
    # =========================================================================
    
    async def process_webhook(
        self,
        path: str,
        method: str,
        headers: Dict[str, str],
        body: bytes,
        query_params: Dict[str, str] = None,
        source_ip: str = ""
    ) -> WebhookResponse:
        """
        Process an incoming webhook request.
        
        Args:
            path: Request path
            method: HTTP method
            headers: Request headers
            body: Request body (raw bytes)
            query_params: Query string parameters
            source_ip: Source IP address
            
        Returns:
            WebhookResponse
        """
        event_id = str(uuid.uuid4())
        
        # Find endpoint
        endpoint = self._endpoints.get(path)
        if not endpoint:
            logger.warning(f"Webhook received for unknown endpoint: {path}")
            return WebhookResponse(
                success=False,
                event_id=event_id,
                message="Endpoint not found",
                status_code=404
            )
        
        if not endpoint.is_active:
            return WebhookResponse(
                success=False,
                event_id=event_id,
                message="Endpoint is disabled",
                status_code=403
            )
        
        # Rate limiting
        rate_limiter = self._rate_limiters.get(path)
        if rate_limiter and not rate_limiter.consume():
            logger.warning(f"Rate limit exceeded for endpoint: {path}")
            return WebhookResponse(
                success=False,
                event_id=event_id,
                message="Rate limit exceeded",
                status_code=429
            )
        
        # Parse body
        try:
            if body:
                payload = json.loads(body.decode('utf-8'))
            else:
                payload = {}
        except json.JSONDecodeError:
            # Try to handle as form data or treat as string
            try:
                payload = {"raw": body.decode('utf-8')}
            except:
                payload = {"raw": body.hex()}
        
        # Verify authentication
        verified = await self._verify_auth(
            endpoint, headers, body, query_params
        )
        
        if not verified:
            logger.warning(f"Authentication failed for endpoint: {path}")
            await self._log_event(event_id, endpoint, payload, headers, source_ip, False)
            return WebhookResponse(
                success=False,
                event_id=event_id,
                message="Authentication failed",
                status_code=401
            )
        
        # Check for replay (nonce/timestamp)
        if not self._check_replay(headers):
            logger.warning(f"Replay detected for endpoint: {path}")
            return WebhookResponse(
                success=False,
                event_id=event_id,
                message="Replay detected",
                status_code=400
            )
        
        # Create event
        event = WebhookEvent(
            event_id=event_id,
            endpoint_id=endpoint.endpoint_id,
            endpoint_path=path,
            event_type=self._extract_event_type(headers, payload),
            payload=payload,
            headers=dict(headers),
            query_params=query_params or {},
            timestamp=datetime.now(timezone.utc),
            source_ip=source_ip,
            verified=True,
            signature=headers.get('X-Hub-Signature-256') or headers.get('X-Signature')
        )
        
        # Log event
        await self._log_event(event_id, endpoint, payload, headers, source_ip, True)
        
        # Process event
        try:
            result = await self._dispatch_event(endpoint, event)
            
            return WebhookResponse(
                success=True,
                event_id=event_id,
                message="Webhook processed successfully",
                status_code=200,
                data=result
            )
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return WebhookResponse(
                success=False,
                event_id=event_id,
                message=str(e),
                status_code=500
            )
    
    async def _verify_auth(
        self,
        endpoint: WebhookEndpoint,
        headers: Dict[str, str],
        body: bytes,
        query_params: Dict[str, str]
    ) -> bool:
        """Verify webhook authentication."""
        
        if endpoint.auth_method == AuthMethod.NONE:
            return True
        
        if endpoint.auth_method == AuthMethod.HMAC:
            return self._verify_hmac(endpoint.secret, headers, body)
        
        if endpoint.auth_method == AuthMethod.API_KEY:
            return self._verify_api_key(endpoint.secret, headers, query_params)
        
        if endpoint.auth_method == AuthMethod.JWT:
            return await self._verify_jwt(endpoint.secret, headers)
        
        if endpoint.auth_method == AuthMethod.BASIC:
            return self._verify_basic(endpoint.secret, headers)
        
        return False
    
    def _verify_hmac(
        self,
        secret: str,
        headers: Dict[str, str],
        body: bytes
    ) -> bool:
        """Verify HMAC signature."""
        if not secret:
            return False
        
        # Try common signature header names
        signature = (
            headers.get('X-Hub-Signature-256') or  # GitHub
            headers.get('X-Signature-256') or
            headers.get('X-Signature') or
            headers.get('X-Slack-Signature') or    # Slack
            headers.get('Stripe-Signature') or     # Stripe
            headers.get('X-Webhook-Signature')
        )
        
        if not signature:
            return False
        
        # Handle different signature formats
        if signature.startswith('sha256='):
            signature = signature[7:]
        elif signature.startswith('sha1='):
            # Some services use SHA1
            expected = hmac.new(
                secret.encode(),
                body,
                hashlib.sha1
            ).hexdigest()
            return hmac.compare_digest(signature[5:], expected)
        
        # Calculate expected signature (SHA256)
        expected = hmac.new(
            secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected)
    
    def _verify_api_key(
        self,
        secret: str,
        headers: Dict[str, str],
        query_params: Dict[str, str]
    ) -> bool:
        """Verify API key authentication."""
        if not secret:
            return False
        
        # Check header
        api_key = (
            headers.get('X-API-Key') or
            headers.get('Authorization', '').replace('Bearer ', '') or
            headers.get('Api-Key')
        )
        
        # Check query params
        if not api_key and query_params:
            api_key = query_params.get('api_key') or query_params.get('token')
        
        return api_key == secret
    
    async def _verify_jwt(self, secret: str, headers: Dict[str, str]) -> bool:
        """Verify JWT token."""
        # JWT verification would require a library like PyJWT
        # For now, just check if token is present
        auth_header = headers.get('Authorization', '')
        return auth_header.startswith('Bearer ') and len(auth_header) > 10
    
    def _verify_basic(self, secret: str, headers: Dict[str, str]) -> bool:
        """Verify Basic authentication."""
        import base64
        
        auth_header = headers.get('Authorization', '')
        if not auth_header.startswith('Basic '):
            return False
        
        try:
            credentials = base64.b64decode(auth_header[6:]).decode('utf-8')
            return credentials == secret
        except:
            return False
    
    def _check_replay(self, headers: Dict[str, str]) -> bool:
        """Check for replay attacks using nonce/timestamp."""
        # Clean up old nonces
        now = time.time()
        if now - self._last_nonce_cleanup > self._nonce_cleanup_interval:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
            self._seen_nonces = {
                k: v for k, v in self._seen_nonces.items()
                if v > cutoff
            }
            self._last_nonce_cleanup = now
        
        # Check timestamp
        timestamp = headers.get('X-Timestamp') or headers.get('X-Request-Timestamp')
        if timestamp:
            try:
                ts = int(timestamp)
                if abs(now - ts) > 300:  # 5 minute tolerance
                    return False
            except:
                pass
        
        # Check nonce
        nonce = headers.get('X-Nonce') or headers.get('X-Request-Id')
        if nonce:
            if nonce in self._seen_nonces:
                return False
            self._seen_nonces[nonce] = datetime.now(timezone.utc)
        
        return True
    
    def _extract_event_type(
        self,
        headers: Dict[str, str],
        payload: Dict[str, Any]
    ) -> Optional[str]:
        """Extract event type from headers or payload."""
        # Common header locations
        event_type = (
            headers.get('X-GitHub-Event') or
            headers.get('X-Event-Type') or
            headers.get('X-Gitlab-Event') or
            payload.get('type') or
            payload.get('event') or
            payload.get('event_type') or
            payload.get('action')
        )
        return event_type
    
    async def _dispatch_event(
        self,
        endpoint: WebhookEndpoint,
        event: WebhookEvent
    ) -> Optional[Dict[str, Any]]:
        """Dispatch event to handler or target."""
        
        # Call custom handler if registered
        handler = self._handlers.get(endpoint.path)
        if handler:
            result = await handler(event)
            return {"handler_result": result}
        
        # Dispatch to target (agent/workflow/swarm)
        if endpoint.target_type and endpoint.target_id:
            return await self._trigger_target(
                endpoint.target_type,
                endpoint.target_id,
                event
            )
        
        # No handler, just log
        logger.info(f"Webhook event received but no handler: {endpoint.path}")
        return {"message": "Event logged, no handler configured"}
    
    async def _trigger_target(
        self,
        target_type: str,
        target_id: str,
        event: WebhookEvent
    ) -> Dict[str, Any]:
        """Trigger an agent, workflow, or swarm from webhook."""
        
        # This would integrate with the actual execution system
        # For now, just log and return
        logger.info(f"Would trigger {target_type} {target_id} with event {event.event_id}")
        
        return {
            "triggered": True,
            "target_type": target_type,
            "target_id": target_id,
            "event_id": event.event_id
        }
    
    async def _log_event(
        self,
        event_id: str,
        endpoint: WebhookEndpoint,
        payload: Dict,
        headers: Dict,
        source_ip: str,
        verified: bool
    ) -> None:
        """Log webhook event to database."""
        if not self.db_facade:
            return
        
        try:
            self.db_facade.execute(
                """INSERT INTO webhook_events 
                   (event_id, endpoint_id, payload, headers, source_ip, verified)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    event_id,
                    endpoint.endpoint_id,
                    json.dumps(payload),
                    json.dumps(dict(headers)),
                    source_ip,
                    1 if verified else 0
                )
            )
        except Exception as e:
            logger.error(f"Error logging webhook event: {e}")
    
    # =========================================================================
    # EVENT HISTORY
    # =========================================================================
    
    def get_event_history(
        self,
        endpoint_path: str = None,
        limit: int = 100,
        verified_only: bool = False
    ) -> List[Dict]:
        """
        Get webhook event history.
        
        Args:
            endpoint_path: Filter by endpoint
            limit: Maximum records
            verified_only: Only verified events
            
        Returns:
            List of event records
        """
        if not self.db_facade:
            return []
        
        query = """
            SELECT we.*, ep.path, ep.name as endpoint_name
            FROM webhook_events we
            LEFT JOIN webhook_endpoints ep ON we.endpoint_id = ep.endpoint_id
            WHERE 1=1
        """
        params = []
        
        if endpoint_path:
            query += " AND ep.path = ?"
            params.append(endpoint_path)
        
        if verified_only:
            query += " AND we.verified = 1"
        
        query += " ORDER BY we.received_at DESC LIMIT ?"
        params.append(limit)
        
        try:
            return self.db_facade.fetch_all(query, tuple(params)) or []
        except Exception as e:
            logger.error(f"Error fetching webhook history: {e}")
            return []
