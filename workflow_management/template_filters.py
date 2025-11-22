"""
Workflow Template Filters

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

Custom Jinja2 filters for workflow templates to handle datetime formatting.
"""

from datetime import datetime
from typing import Any, Optional, Union


def parse_datetime(value: Any) -> Optional[datetime]:
    """
    Parse a value into a datetime object.
    
    Args:
        value: Either a datetime object or a string representation
        
    Returns:
        datetime object or None
    """
    if value is None:
        return None
    
    # Already a datetime object
    if isinstance(value, datetime):
        return value
    
    # Try to parse string
    if isinstance(value, str):
        # Try common datetime string formats
        for fmt in [
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M',
            '%Y-%m-%d'
        ]:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    
    return None


def format_datetime(value: Any, format_string: str = '%Y-%m-%d %H:%M') -> str:
    """
    Format a datetime value, handling both datetime objects and strings.
    
    Args:
        value: Either a datetime object or a string representation
        format_string: The strftime format string to use
        
    Returns:
        Formatted datetime string or the original string/N/A
    """
    if value is None:
        return 'N/A'
    
    # If it's already a datetime object, format it
    if isinstance(value, datetime):
        return value.strftime(format_string)
    
    # If it's a string, try to parse and format it
    if isinstance(value, str):
        # Try to parse it
        dt = parse_datetime(value)
        if dt:
            return dt.strftime(format_string)
        # If parsing failed but string looks reasonable, return as-is
        if len(value) <= 25:  # Reasonable length for datetime string
            return value
    
    # For any other type, return string representation
    return str(value)


def datetime_diff_minutes(end: Any, start: Any) -> Optional[float]:
    """
    Calculate difference between two datetimes in minutes.
    
    Args:
        end: End datetime (string or datetime object)
        start: Start datetime (string or datetime object)
        
    Returns:
        Difference in minutes or None if calculation fails
    """
    try:
        end_dt = parse_datetime(end)
        start_dt = parse_datetime(start)
        
        if end_dt and start_dt:
            diff = end_dt - start_dt
            return diff.total_seconds() / 60
    except Exception:
        pass
    
    return None


def datetime_diff_seconds(end: Any, start: Any) -> Optional[float]:
    """
    Calculate difference between two datetimes in seconds.
    
    Args:
        end: End datetime (string or datetime object)
        start: Start datetime (string or datetime object)
        
    Returns:
        Difference in seconds or None if calculation fails
    """
    try:
        end_dt = parse_datetime(end)
        start_dt = parse_datetime(start)
        
        if end_dt and start_dt:
            diff = end_dt - start_dt
            return diff.total_seconds()
    except Exception:
        pass
    
    return None


def format_duration(seconds: Optional[float]) -> str:
    """
    Format a duration in seconds to human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string (e.g., "2h 30m", "45s")
    """
    if seconds is None or seconds < 0:
        return 'N/A'
    
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        if minutes > 0:
            return f"{hours}h {minutes}m"
        return f"{hours}h"


def register_template_filters(app):
    """
    Register custom template filters with Flask app.
    
    Args:
        app: Flask application instance
    """
    # Datetime formatting
    app.jinja_env.filters['format_datetime'] = format_datetime
    app.jinja_env.filters['dt'] = format_datetime  # Short alias
    
    # Datetime parsing
    app.jinja_env.filters['parse_datetime'] = parse_datetime
    
    # Datetime calculations
    app.jinja_env.filters['datetime_diff_minutes'] = datetime_diff_minutes
    app.jinja_env.filters['datetime_diff_seconds'] = datetime_diff_seconds
    app.jinja_env.filters['duration_minutes'] = lambda e, s: datetime_diff_minutes(e, s)
    app.jinja_env.filters['duration_seconds'] = lambda e, s: datetime_diff_seconds(e, s)
    
    # Duration formatting
    app.jinja_env.filters['format_duration'] = format_duration
