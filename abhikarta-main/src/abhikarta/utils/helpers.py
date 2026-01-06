"""
Helpers Module - Common utility functions.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

import uuid
import time
import re
from datetime import datetime
from typing import Optional
from enum import Enum


class EntityType(Enum):
    """Entity types for execution ID generation."""
    WORKFLOW = 'wflow'
    AGENT = 'agent'
    SWARM = 'swarm'
    AIORG = 'aiorg'


def sanitize_name(name: str, max_length: int = 30) -> str:
    """
    Sanitize entity name for use in execution ID.
    
    - Converts to lowercase
    - Replaces spaces and special characters with underscores
    - Removes consecutive underscores
    - Truncates to max_length
    
    Args:
        name: Entity name to sanitize
        max_length: Maximum length for name portion
        
    Returns:
        Sanitized name string
    """
    if not name:
        return ""
    
    # Convert to lowercase and replace non-alphanumeric chars with underscore
    sanitized = re.sub(r'[^a-z0-9]+', '_', name.lower())
    
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    
    # Replace multiple underscores with single
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Truncate
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip('_')
    
    return sanitized


def generate_execution_id(entity_type: EntityType, entity_name: str = None) -> str:
    """
    Generate a traceable execution ID.
    
    Format: <type>_<name>_<uuid> or <type>_<uuid> if name not available
    
    Examples:
        - wflow_adaptive_learning_loop_a1b2c3d4e5f6
        - agent_research_assistant_7890abcd
        - swarm_b2c3d4e5
        - aiorg_customer_support_team_f6g7h8i9
    
    Args:
        entity_type: Type of entity (workflow, agent, swarm, aiorg)
        entity_name: Optional name of the entity
        
    Returns:
        Traceable execution ID string
    """
    # Get short UUID (first 8 chars is usually sufficient for uniqueness in this context)
    short_uuid = uuid.uuid4().hex[:12]
    
    # Get entity type prefix
    if isinstance(entity_type, EntityType):
        prefix = entity_type.value
    elif isinstance(entity_type, str):
        # Map string to EntityType
        type_map = {
            'workflow': 'wflow',
            'wflow': 'wflow',
            'agent': 'agent',
            'swarm': 'swarm',
            'aiorg': 'aiorg',
            'ai_org': 'aiorg',
        }
        prefix = type_map.get(entity_type.lower(), entity_type.lower()[:5])
    else:
        prefix = 'exec'
    
    # Build execution ID
    if entity_name:
        sanitized_name = sanitize_name(entity_name)
        if sanitized_name:
            return f"{prefix}_{sanitized_name}_{short_uuid}"
    
    return f"{prefix}_{short_uuid}"


def parse_execution_id(execution_id: str) -> dict:
    """
    Parse a traceable execution ID to extract components.
    
    Args:
        execution_id: Execution ID to parse
        
    Returns:
        Dictionary with 'entity_type', 'entity_name', 'uuid' keys
    """
    result = {
        'entity_type': None,
        'entity_name': None,
        'uuid': None,
        'raw': execution_id
    }
    
    if not execution_id:
        return result
    
    # Check for new traceable format
    parts = execution_id.split('_')
    
    if len(parts) >= 2:
        # First part is entity type
        type_map = {
            'wflow': 'workflow',
            'agent': 'agent',
            'swarm': 'swarm',
            'aiorg': 'aiorg',
        }
        
        if parts[0] in type_map:
            result['entity_type'] = type_map[parts[0]]
            result['uuid'] = parts[-1]
            
            # Middle parts are the name (if more than 2 parts)
            if len(parts) > 2:
                result['entity_name'] = '_'.join(parts[1:-1])
        else:
            # Old UUID format
            result['uuid'] = execution_id
    else:
        # Single part - treat as UUID
        result['uuid'] = execution_id
    
    return result


def generate_id(prefix: str = "") -> str:
    """
    Generate a unique identifier.
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        Unique identifier string
    """
    unique_part = f"{uuid.uuid4().hex[:12]}_{int(time.time())}"
    if prefix:
        return f"{prefix}_{unique_part}"
    return unique_part


def get_timestamp() -> str:
    """
    Get current timestamp in ISO format.
    
    Returns:
        ISO formatted timestamp string
    """
    return datetime.now().isoformat()


def format_datetime(dt: Optional[datetime], format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime object to string.
    
    Args:
        dt: Datetime object
        format_str: Format string
        
    Returns:
        Formatted datetime string
    """
    if dt is None:
        return ""
    return dt.strftime(format_str)


def safe_get(data: dict, *keys, default=None):
    """
    Safely get nested dictionary value.
    
    Args:
        data: Dictionary to search
        keys: Keys to traverse
        default: Default value if not found
        
    Returns:
        Value at nested key or default
    """
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key, default)
        else:
            return default
    return result


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.
    
    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
