"""
HTTP Tool - Tool implementation for HTTP/REST API calls.

Allows wrapping any REST API endpoint as a BaseTool.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import logging
import uuid
import json
import requests
from typing import Dict, Any, Optional, List
from enum import Enum

from .base_tool import (
    BaseTool, ToolMetadata, ToolSchema, ToolParameter,
    ToolResult, ToolType, ToolCategory
)

logger = logging.getLogger(__name__)


class HTTPMethod(Enum):
    """HTTP methods supported."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class HTTPTool(BaseTool):
    """
    Tool that wraps an HTTP/REST API endpoint.
    
    Supports all common HTTP methods, authentication,
    headers, query parameters, and request body.
    
    Example:
        tool = HTTPTool(
            name="get_weather",
            description="Get current weather",
            url="https://api.weather.com/current",
            method=HTTPMethod.GET,
            query_params=["city", "units"]
        )
    """
    
    def __init__(self, metadata: ToolMetadata, schema: ToolSchema,
                 url: str, method: HTTPMethod = HTTPMethod.GET,
                 headers: Dict[str, str] = None,
                 auth_token: str = None, auth_type: str = "Bearer",
                 timeout: int = 30, verify_ssl: bool = True,
                 response_path: str = None):
        """
        Initialize HTTPTool.
        
        Args:
            metadata: Tool metadata
            schema: Parameter schema
            url: Base URL (can contain {param} placeholders)
            method: HTTP method
            headers: Default headers
            auth_token: Authentication token
            auth_type: Auth type (Bearer, Basic, etc.)
            timeout: Request timeout
            verify_ssl: Whether to verify SSL
            response_path: JSON path to extract from response
        """
        super().__init__(metadata)
        self._schema = schema
        self._url = url
        self._method = method
        self._headers = headers or {}
        self._auth_token = auth_token
        self._auth_type = auth_type
        self._timeout = timeout
        self._verify_ssl = verify_ssl
        self._response_path = response_path
    
    def execute(self, **kwargs) -> ToolResult:
        """Execute the HTTP request."""
        import time
        start_time = time.time()
        
        try:
            # Build URL with path parameters
            url = self._url
            path_params = {}
            query_params = {}
            body_params = {}
            
            for key, value in kwargs.items():
                if f"{{{key}}}" in url:
                    url = url.replace(f"{{{key}}}", str(value))
                    path_params[key] = value
                elif self._method in (HTTPMethod.GET, HTTPMethod.DELETE):
                    query_params[key] = value
                else:
                    body_params[key] = value
            
            # Build headers
            headers = self._headers.copy()
            if self._auth_token:
                headers["Authorization"] = f"{self._auth_type} {self._auth_token}"
            if body_params:
                headers["Content-Type"] = "application/json"
            
            # Make request
            response = requests.request(
                method=self._method.value,
                url=url,
                params=query_params if query_params else None,
                json=body_params if body_params else None,
                headers=headers,
                timeout=self._timeout,
                verify=self._verify_ssl
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            # Parse response
            try:
                result = response.json()
            except:
                result = response.text
            
            # Extract from path if specified
            if self._response_path and isinstance(result, dict):
                for key in self._response_path.split('.'):
                    if isinstance(result, dict) and key in result:
                        result = result[key]
                    else:
                        break
            
            if response.ok:
                return ToolResult.success_result(
                    result,
                    execution_time,
                    {"status_code": response.status_code}
                )
            else:
                return ToolResult.error_result(
                    f"HTTP {response.status_code}: {result}",
                    execution_time,
                    {"status_code": response.status_code}
                )
                
        except requests.Timeout:
            execution_time = (time.time() - start_time) * 1000
            return ToolResult.error_result(
                f"Request timed out after {self._timeout}s",
                execution_time
            )
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"HTTPTool {self.name} error: {e}")
            return ToolResult.error_result(str(e), execution_time)
    
    def get_schema(self) -> ToolSchema:
        """Get the parameter schema."""
        return self._schema
    
    @classmethod
    def create(cls, name: str, description: str, url: str,
              method: HTTPMethod = HTTPMethod.GET,
              parameters: List[Dict[str, Any]] = None,
              headers: Dict[str, str] = None,
              auth_token: str = None,
              category: ToolCategory = None,
              tags: List[str] = None,
              **kwargs) -> 'HTTPTool':
        """
        Create an HTTPTool with simplified interface.
        
        Args:
            name: Tool name
            description: Tool description
            url: API URL
            method: HTTP method
            parameters: List of parameter definitions
            headers: Default headers
            auth_token: Auth token
            category: Tool category
            tags: Tool tags
            
        Returns:
            HTTPTool instance
        """
        # Build schema
        schema_params = []
        for param in (parameters or []):
            schema_params.append(ToolParameter(
                name=param.get('name'),
                param_type=param.get('type', 'string'),
                description=param.get('description', ''),
                required=param.get('required', True),
                default=param.get('default'),
                enum=param.get('enum')
            ))
        schema = ToolSchema(parameters=schema_params)
        
        metadata = ToolMetadata(
            tool_id=f"http_{uuid.uuid4().hex[:12]}",
            name=name,
            description=description,
            tool_type=ToolType.HTTP,
            category=category or ToolCategory.INTEGRATION,
            source=f"http:{url.split('/')[2] if '/' in url else url}",
            tags=tags or ["http", "api"],
            requires_auth=bool(auth_token)
        )
        
        return cls(
            metadata=metadata,
            schema=schema,
            url=url,
            method=method,
            headers=headers,
            auth_token=auth_token,
            **kwargs
        )


class WebhookTool(HTTPTool):
    """
    Specialized HTTPTool for webhook calls.
    
    Always uses POST method and supports retry logic.
    """
    
    def __init__(self, metadata: ToolMetadata, schema: ToolSchema,
                 url: str, headers: Dict[str, str] = None,
                 secret: str = None, max_retries: int = 3,
                 timeout: int = 10):
        """Initialize WebhookTool."""
        super().__init__(
            metadata=metadata,
            schema=schema,
            url=url,
            method=HTTPMethod.POST,
            headers=headers,
            timeout=timeout
        )
        self._secret = secret
        self._max_retries = max_retries
    
    def execute(self, **kwargs) -> ToolResult:
        """Execute webhook with retry logic."""
        import time
        import hashlib
        import hmac
        
        start_time = time.time()
        last_error = None
        
        for attempt in range(self._max_retries):
            try:
                headers = self._headers.copy()
                headers["Content-Type"] = "application/json"
                
                # Add signature if secret provided
                if self._secret:
                    payload = json.dumps(kwargs, sort_keys=True)
                    signature = hmac.new(
                        self._secret.encode(),
                        payload.encode(),
                        hashlib.sha256
                    ).hexdigest()
                    headers["X-Webhook-Signature"] = signature
                
                response = requests.post(
                    self._url,
                    json=kwargs,
                    headers=headers,
                    timeout=self._timeout
                )
                
                execution_time = (time.time() - start_time) * 1000
                
                if response.ok:
                    try:
                        result = response.json()
                    except:
                        result = response.text
                    
                    return ToolResult.success_result(
                        result,
                        execution_time,
                        {"attempt": attempt + 1}
                    )
                else:
                    last_error = f"HTTP {response.status_code}"
                    
            except Exception as e:
                last_error = str(e)
            
            # Wait before retry
            if attempt < self._max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
        
        execution_time = (time.time() - start_time) * 1000
        return ToolResult.error_result(
            f"Webhook failed after {self._max_retries} attempts: {last_error}",
            execution_time
        )
    
    @classmethod
    def create(cls, name: str, url: str, description: str = None,
              parameters: List[Dict[str, Any]] = None,
              secret: str = None, **kwargs) -> 'WebhookTool':
        """Create a WebhookTool."""
        schema_params = []
        for param in (parameters or []):
            schema_params.append(ToolParameter(
                name=param.get('name'),
                param_type=param.get('type', 'string'),
                description=param.get('description', ''),
                required=param.get('required', True)
            ))
        schema = ToolSchema(parameters=schema_params)
        
        metadata = ToolMetadata(
            tool_id=f"webhook_{uuid.uuid4().hex[:12]}",
            name=name,
            description=description or f"Webhook: {name}",
            tool_type=ToolType.HTTP,
            category=ToolCategory.INTEGRATION,
            source=f"webhook:{url.split('/')[2] if '/' in url else url}",
            tags=["webhook", "http"]
        )
        
        return cls(
            metadata=metadata,
            schema=schema,
            url=url,
            secret=secret,
            **kwargs
        )
