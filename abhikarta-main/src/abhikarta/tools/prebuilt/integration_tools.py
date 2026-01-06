"""
Integration and API Tools Library - Tools for external integrations.

This module provides tools for:
- HTTP/REST API calls
- Webhook notifications
- Email/SMS notifications
- Database operations
- File processing

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import logging
import json
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode, urlparse

from ..base_tool import (
    BaseTool, ToolMetadata, ToolSchema, ToolParameter,
    ToolResult, ToolType, ToolCategory
)
from ..function_tool import FunctionTool

logger = logging.getLogger(__name__)


# =============================================================================
# HTTP/API TOOLS
# =============================================================================

def make_http_request(url: str, method: str = "GET", headers: Dict[str, str] = None,
                     body: Dict[str, Any] = None, timeout: int = 30) -> Dict[str, Any]:
    """
    Make an HTTP request (simulated for safety).
    
    Args:
        url: Target URL
        method: HTTP method (GET, POST, PUT, DELETE)
        headers: Request headers
        body: Request body for POST/PUT
        timeout: Timeout in seconds
        
    Returns:
        Response details
    """
    # Simulated HTTP request for safety
    parsed = urlparse(url)
    return {
        "status": "simulated",
        "message": "HTTP requests are simulated for safety. In production, configure actual HTTP client.",
        "request": {
            "url": url,
            "method": method.upper(),
            "host": parsed.netloc,
            "path": parsed.path,
            "headers": headers or {},
            "has_body": body is not None
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def build_query_string(params: Dict[str, Any]) -> str:
    """
    Build URL query string from parameters.
    
    Args:
        params: Dictionary of parameters
        
    Returns:
        URL-encoded query string
    """
    # Filter None values
    filtered = {k: v for k, v in params.items() if v is not None}
    return urlencode(filtered)


def parse_json_response(json_string: str, extract_path: str = None) -> Dict[str, Any]:
    """
    Parse JSON response and optionally extract nested value.
    
    Args:
        json_string: JSON string to parse
        extract_path: Dot-notation path to extract (e.g., "data.items.0.name")
        
    Returns:
        Parsed JSON or extracted value
    """
    try:
        data = json.loads(json_string)
        
        if extract_path:
            parts = extract_path.split('.')
            current = data
            for part in parts:
                if isinstance(current, dict):
                    current = current.get(part)
                elif isinstance(current, list) and part.isdigit():
                    idx = int(part)
                    current = current[idx] if idx < len(current) else None
                else:
                    current = None
                if current is None:
                    break
            return {"extracted": current, "path": extract_path}
        
        return {"parsed": data, "type": type(data).__name__}
    except json.JSONDecodeError as e:
        return {"error": str(e), "position": e.pos}


def validate_api_response(response: Dict[str, Any], expected_fields: List[str],
                         status_field: str = "status", 
                         success_values: List[str] = None) -> Dict[str, Any]:
    """
    Validate API response structure and status.
    
    Args:
        response: API response dictionary
        expected_fields: List of required fields
        status_field: Field containing status
        success_values: Valid success status values
        
    Returns:
        Validation result
    """
    success_values = success_values or ["success", "ok", "200", True]
    
    result = {
        "valid": True,
        "missing_fields": [],
        "status_valid": True,
        "warnings": []
    }
    
    # Check required fields
    for field in expected_fields:
        if field not in response:
            result["missing_fields"].append(field)
            result["valid"] = False
    
    # Check status
    if status_field in response:
        status = response[status_field]
        if status not in success_values and str(status).lower() not in [str(v).lower() for v in success_values]:
            result["status_valid"] = False
            result["valid"] = False
            result["actual_status"] = status
    
    return result


# =============================================================================
# NOTIFICATION TOOLS
# =============================================================================

def format_email_template(template: str, variables: Dict[str, Any]) -> str:
    """
    Format an email template with variables.
    
    Args:
        template: Email template with {{variable}} placeholders
        variables: Dictionary of variable values
        
    Returns:
        Formatted email content
    """
    result = template
    for key, value in variables.items():
        placeholder = "{{" + key + "}}"
        result = result.replace(placeholder, str(value))
    
    # Check for unfilled placeholders
    remaining = re.findall(r'\{\{(\w+)\}\}', result)
    if remaining:
        return f"Warning: Unfilled placeholders: {remaining}\n\n{result}"
    
    return result


def create_notification(notification_type: str, recipient: str, subject: str,
                       message: str, priority: str = "normal",
                       metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Create a notification record.
    
    Args:
        notification_type: Type (email, sms, push, webhook)
        recipient: Recipient address/number
        subject: Notification subject
        message: Notification message
        priority: Priority level (low, normal, high, urgent)
        metadata: Additional metadata
        
    Returns:
        Notification record
    """
    import uuid
    
    return {
        "notification_id": f"NOTIF-{uuid.uuid4().hex[:12].upper()}",
        "type": notification_type,
        "recipient": recipient,
        "subject": subject,
        "message": message[:500],  # Truncate for preview
        "priority": priority,
        "status": "queued",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {}
    }


def format_sms_message(message: str, max_length: int = 160) -> Dict[str, Any]:
    """
    Format and validate SMS message.
    
    Args:
        message: SMS message content
        max_length: Maximum message length
        
    Returns:
        Formatted message details
    """
    # Remove non-SMS compatible characters
    cleaned = re.sub(r'[^\x00-\x7F]+', '', message)
    
    segments = (len(cleaned) + max_length - 1) // max_length
    
    return {
        "original_length": len(message),
        "cleaned_length": len(cleaned),
        "segments": segments,
        "truncated": len(cleaned) > max_length,
        "message": cleaned[:max_length] if len(cleaned) > max_length else cleaned,
        "full_message": cleaned
    }


# =============================================================================
# DATA TRANSFORMATION TOOLS
# =============================================================================

def map_fields(source: Dict[str, Any], field_mapping: Dict[str, str]) -> Dict[str, Any]:
    """
    Map fields from source to target using mapping.
    
    Args:
        source: Source dictionary
        field_mapping: Mapping of source_field -> target_field
        
    Returns:
        Mapped dictionary
    """
    result = {}
    for source_field, target_field in field_mapping.items():
        if source_field in source:
            result[target_field] = source[source_field]
    return result


def flatten_nested_dict(nested_dict: Dict[str, Any], separator: str = ".") -> Dict[str, Any]:
    """
    Flatten nested dictionary to single level.
    
    Args:
        nested_dict: Nested dictionary
        separator: Key separator
        
    Returns:
        Flattened dictionary
    """
    result = {}
    
    def flatten(obj, prefix=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_key = f"{prefix}{separator}{key}" if prefix else key
                flatten(value, new_key)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_key = f"{prefix}{separator}{i}" if prefix else str(i)
                flatten(item, new_key)
        else:
            result[prefix] = obj
    
    flatten(nested_dict)
    return result


def unflatten_dict(flat_dict: Dict[str, Any], separator: str = ".") -> Dict[str, Any]:
    """
    Unflatten dictionary back to nested structure.
    
    Args:
        flat_dict: Flattened dictionary
        separator: Key separator
        
    Returns:
        Nested dictionary
    """
    result = {}
    
    for key, value in flat_dict.items():
        parts = key.split(separator)
        current = result
        
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                # Check if next part is numeric (list)
                next_part = parts[i + 1]
                if next_part.isdigit():
                    current[part] = []
                else:
                    current[part] = {}
            current = current[part]
        
        current[parts[-1]] = value
    
    return result


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any], 
               strategy: str = "override") -> Dict[str, Any]:
    """
    Merge two dictionaries with specified strategy.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        strategy: Merge strategy (override, keep_first, merge_lists)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result:
            if strategy == "override":
                result[key] = value
            elif strategy == "keep_first":
                pass  # Keep original
            elif strategy == "merge_lists":
                if isinstance(result[key], list) and isinstance(value, list):
                    result[key] = result[key] + value
                else:
                    result[key] = value
        else:
            result[key] = value
    
    return result


def filter_dict_keys(data: Dict[str, Any], include_keys: List[str] = None,
                    exclude_keys: List[str] = None) -> Dict[str, Any]:
    """
    Filter dictionary keys.
    
    Args:
        data: Source dictionary
        include_keys: Keys to include (if specified, only these)
        exclude_keys: Keys to exclude
        
    Returns:
        Filtered dictionary
    """
    if include_keys:
        return {k: v for k, v in data.items() if k in include_keys}
    elif exclude_keys:
        return {k: v for k, v in data.items() if k not in exclude_keys}
    return data.copy()


# =============================================================================
# LIST/ARRAY TOOLS
# =============================================================================

def filter_list(items: List[Dict[str, Any]], field: str, operator: str,
               value: Any) -> List[Dict[str, Any]]:
    """
    Filter list of dictionaries based on field condition.
    
    Args:
        items: List of dictionaries
        field: Field to filter on
        operator: Comparison operator (eq, ne, gt, lt, gte, lte, contains, in)
        value: Value to compare
        
    Returns:
        Filtered list
    """
    result = []
    
    for item in items:
        item_value = item.get(field)
        match = False
        
        if operator == "eq":
            match = item_value == value
        elif operator == "ne":
            match = item_value != value
        elif operator == "gt":
            match = item_value is not None and item_value > value
        elif operator == "lt":
            match = item_value is not None and item_value < value
        elif operator == "gte":
            match = item_value is not None and item_value >= value
        elif operator == "lte":
            match = item_value is not None and item_value <= value
        elif operator == "contains":
            match = value in str(item_value) if item_value else False
        elif operator == "in":
            match = item_value in value if isinstance(value, (list, tuple)) else False
        
        if match:
            result.append(item)
    
    return result


def sort_list(items: List[Dict[str, Any]], sort_key: str,
             descending: bool = False) -> List[Dict[str, Any]]:
    """
    Sort list of dictionaries by key.
    
    Args:
        items: List of dictionaries
        sort_key: Key to sort by
        descending: Sort in descending order
        
    Returns:
        Sorted list
    """
    return sorted(items, key=lambda x: x.get(sort_key, 0), reverse=descending)


def group_by(items: List[Dict[str, Any]], group_key: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group list items by key value.
    
    Args:
        items: List of dictionaries
        group_key: Key to group by
        
    Returns:
        Dictionary with groups
    """
    groups = {}
    for item in items:
        key_value = str(item.get(group_key, "unknown"))
        if key_value not in groups:
            groups[key_value] = []
        groups[key_value].append(item)
    return groups


def aggregate_list(items: List[Dict[str, Any]], field: str,
                  operation: str) -> Dict[str, Any]:
    """
    Aggregate values in list.
    
    Args:
        items: List of dictionaries
        field: Field to aggregate
        operation: Operation (sum, avg, min, max, count)
        
    Returns:
        Aggregation result
    """
    values = [item.get(field, 0) for item in items if field in item]
    
    if not values:
        return {"result": None, "count": 0, "operation": operation}
    
    if operation == "sum":
        result = sum(values)
    elif operation == "avg":
        result = sum(values) / len(values)
    elif operation == "min":
        result = min(values)
    elif operation == "max":
        result = max(values)
    elif operation == "count":
        result = len(values)
    else:
        result = None
    
    return {
        "result": round(result, 2) if isinstance(result, float) else result,
        "count": len(values),
        "operation": operation,
        "field": field
    }


def paginate_list(items: List[Any], page: int = 1, 
                 page_size: int = 10) -> Dict[str, Any]:
    """
    Paginate a list.
    
    Args:
        items: List to paginate
        page: Page number (1-indexed)
        page_size: Items per page
        
    Returns:
        Paginated result
    """
    total_items = len(items)
    total_pages = (total_items + page_size - 1) // page_size
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    return {
        "items": items[start_idx:end_idx],
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1
    }


# =============================================================================
# WORKFLOW HELPER TOOLS
# =============================================================================

def create_workflow_context(initial_data: Dict[str, Any] = None,
                           workflow_id: str = None) -> Dict[str, Any]:
    """
    Create a workflow execution context.
    
    Args:
        initial_data: Initial context data
        workflow_id: Workflow identifier
        
    Returns:
        Workflow context
    """
    import uuid
    
    return {
        "execution_id": f"EXEC-{uuid.uuid4().hex[:12].upper()}",
        "workflow_id": workflow_id or "unknown",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "status": "running",
        "data": initial_data or {},
        "steps_completed": [],
        "current_step": None,
        "errors": []
    }


def update_workflow_context(context: Dict[str, Any], step_name: str,
                           step_result: Any, success: bool = True) -> Dict[str, Any]:
    """
    Update workflow context with step result.
    
    Args:
        context: Current context
        step_name: Completed step name
        step_result: Step result data
        success: Whether step succeeded
        
    Returns:
        Updated context
    """
    updated = context.copy()
    updated["steps_completed"].append({
        "step": step_name,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "success": success
    })
    
    if isinstance(step_result, dict):
        updated["data"].update(step_result)
    else:
        updated["data"][step_name] = step_result
    
    if not success:
        updated["errors"].append({
            "step": step_name,
            "error": str(step_result)
        })
    
    return updated


def evaluate_condition(context: Dict[str, Any], condition: str) -> bool:
    """
    Evaluate a condition expression against context.
    
    Args:
        context: Data context
        condition: Condition expression
        
    Returns:
        Boolean result
    """
    # Safe evaluation of simple conditions
    try:
        # Handle common patterns
        if ">=" in condition:
            parts = condition.split(">=")
            left = context.get(parts[0].strip(), 0)
            right = float(parts[1].strip())
            return left >= right
        elif "<=" in condition:
            parts = condition.split("<=")
            left = context.get(parts[0].strip(), 0)
            right = float(parts[1].strip())
            return left <= right
        elif ">" in condition:
            parts = condition.split(">")
            left = context.get(parts[0].strip(), 0)
            right = float(parts[1].strip())
            return left > right
        elif "<" in condition:
            parts = condition.split("<")
            left = context.get(parts[0].strip(), 0)
            right = float(parts[1].strip())
            return left < right
        elif "==" in condition:
            parts = condition.split("==")
            left = context.get(parts[0].strip())
            right = parts[1].strip().strip("'\"")
            return str(left) == right
        elif "!=" in condition:
            parts = condition.split("!=")
            left = context.get(parts[0].strip())
            right = parts[1].strip().strip("'\"")
            return str(left) != right
        
        return False
    except Exception:
        return False


# =============================================================================
# REGISTER ALL INTEGRATION TOOLS
# =============================================================================

def get_integration_tools() -> List[FunctionTool]:
    """Get all integration tools."""
    tools = []
    
    # HTTP/API tools
    tools.append(FunctionTool.from_function(
        make_http_request,
        name="make_http_request",
        description="Make an HTTP request to an API endpoint",
        category=ToolCategory.INTEGRATION
    ))
    tools.append(FunctionTool.from_function(
        build_query_string,
        name="build_query_string",
        description="Build URL query string from parameters",
        category=ToolCategory.INTEGRATION
    ))
    tools.append(FunctionTool.from_function(
        parse_json_response,
        name="parse_json_response",
        description="Parse JSON response and extract nested values",
        category=ToolCategory.INTEGRATION
    ))
    tools.append(FunctionTool.from_function(
        validate_api_response,
        name="validate_api_response",
        description="Validate API response structure and status",
        category=ToolCategory.INTEGRATION
    ))
    
    # Notification tools
    tools.append(FunctionTool.from_function(
        format_email_template,
        name="format_email_template",
        description="Format email template with variables",
        category=ToolCategory.COMMUNICATION
    ))
    tools.append(FunctionTool.from_function(
        create_notification,
        name="create_notification",
        description="Create notification record (email, SMS, push)",
        category=ToolCategory.COMMUNICATION
    ))
    tools.append(FunctionTool.from_function(
        format_sms_message,
        name="format_sms_message",
        description="Format and validate SMS message",
        category=ToolCategory.COMMUNICATION
    ))
    
    # Data transformation tools
    tools.append(FunctionTool.from_function(
        map_fields,
        name="map_fields",
        description="Map fields from source to target using mapping",
        category=ToolCategory.DATA
    ))
    tools.append(FunctionTool.from_function(
        flatten_nested_dict,
        name="flatten_nested_dict",
        description="Flatten nested dictionary to single level",
        category=ToolCategory.DATA
    ))
    tools.append(FunctionTool.from_function(
        unflatten_dict,
        name="unflatten_dict",
        description="Unflatten dictionary back to nested structure",
        category=ToolCategory.DATA
    ))
    tools.append(FunctionTool.from_function(
        merge_dicts,
        name="merge_dicts",
        description="Merge two dictionaries with strategy",
        category=ToolCategory.DATA
    ))
    tools.append(FunctionTool.from_function(
        filter_dict_keys,
        name="filter_dict_keys",
        description="Filter dictionary keys by include/exclude lists",
        category=ToolCategory.DATA
    ))
    
    # List/array tools
    tools.append(FunctionTool.from_function(
        filter_list,
        name="filter_list",
        description="Filter list based on field condition",
        category=ToolCategory.DATA
    ))
    tools.append(FunctionTool.from_function(
        sort_list,
        name="sort_list",
        description="Sort list of dictionaries by key",
        category=ToolCategory.DATA
    ))
    tools.append(FunctionTool.from_function(
        group_by,
        name="group_by",
        description="Group list items by key value",
        category=ToolCategory.DATA
    ))
    tools.append(FunctionTool.from_function(
        aggregate_list,
        name="aggregate_list",
        description="Aggregate values in list (sum, avg, min, max)",
        category=ToolCategory.DATA
    ))
    tools.append(FunctionTool.from_function(
        paginate_list,
        name="paginate_list",
        description="Paginate a list with page info",
        category=ToolCategory.DATA
    ))
    
    # Workflow helper tools
    tools.append(FunctionTool.from_function(
        create_workflow_context,
        name="create_workflow_context",
        description="Create workflow execution context",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        update_workflow_context,
        name="update_workflow_context",
        description="Update workflow context with step result",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        evaluate_condition,
        name="evaluate_condition",
        description="Evaluate condition expression against context",
        category=ToolCategory.UTILITY
    ))
    
    return tools


def register_integration_tools(registry) -> int:
    """Register all integration tools."""
    tools = get_integration_tools()
    count = 0
    for tool in tools:
        # Set source metadata to indicate prebuilt
        if tool.metadata:
            tool.metadata.source = f"prebuilt:integration:{tool.name}"
        if registry.register(tool):
            count += 1
    logger.info(f"Registered {count} integration tools")
    return count
