"""
Data Processing Tools Library - Tools for data manipulation and analysis.

This module provides tools for:
- JSON/XML/CSV transformations
- Data validation and cleaning
- Statistical analysis
- Data aggregation

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import logging
import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from collections import Counter
import statistics

from ..base_tool import ToolCategory
from ..function_tool import FunctionTool

logger = logging.getLogger(__name__)


# =============================================================================
# DATA TRANSFORMATION TOOLS
# =============================================================================

def flatten_json(data: Dict[str, Any], separator: str = ".") -> Dict[str, Any]:
    """
    Flatten nested JSON to single level with dot notation keys.
    
    Args:
        data: Nested dictionary
        separator: Key separator (default ".")
        
    Returns:
        Flattened dictionary
    """
    def _flatten(obj, parent_key=""):
        items = {}
        if isinstance(obj, dict):
            for k, v in obj.items():
                new_key = f"{parent_key}{separator}{k}" if parent_key else k
                items.update(_flatten(v, new_key))
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                new_key = f"{parent_key}{separator}{i}" if parent_key else str(i)
                items.update(_flatten(v, new_key))
        else:
            items[parent_key] = obj
        return items
    
    return _flatten(data)


def unflatten_json(data: Dict[str, Any], separator: str = ".") -> Dict[str, Any]:
    """
    Unflatten dot notation keys back to nested structure.
    
    Args:
        data: Flattened dictionary
        separator: Key separator
        
    Returns:
        Nested dictionary
    """
    result = {}
    for key, value in data.items():
        parts = key.split(separator)
        current = result
        for i, part in enumerate(parts[:-1]):
            if part.isdigit():
                part = int(part)
            if part not in current:
                # Check if next part is digit for list
                next_part = parts[i + 1]
                current[part] = [] if next_part.isdigit() else {}
            current = current[part]
        
        final_key = parts[-1]
        if final_key.isdigit():
            final_key = int(final_key)
        current[final_key] = value
    
    return result


def merge_json(base: Dict[str, Any], override: Dict[str, Any], 
               deep: bool = True) -> Dict[str, Any]:
    """
    Merge two JSON objects with override priority.
    
    Args:
        base: Base dictionary
        override: Override dictionary (takes precedence)
        deep: Deep merge nested objects
        
    Returns:
        Merged dictionary
    """
    result = base.copy()
    
    for key, value in override.items():
        if deep and key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_json(result[key], value, deep=True)
        else:
            result[key] = value
    
    return result


def extract_json_paths(data: Dict[str, Any], paths: List[str]) -> Dict[str, Any]:
    """
    Extract specific paths from JSON.
    
    Args:
        data: Source dictionary
        paths: List of dot-notation paths to extract
        
    Returns:
        Dictionary with extracted values
    """
    result = {}
    
    for path in paths:
        parts = path.split(".")
        current = data
        try:
            for part in parts:
                if part.isdigit():
                    current = current[int(part)]
                else:
                    current = current[part]
            result[path] = current
        except (KeyError, IndexError, TypeError):
            result[path] = None
    
    return result


def filter_json_array(data: List[Dict[str, Any]], conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Filter JSON array by conditions.
    
    Args:
        data: List of dictionaries
        conditions: Filter conditions {field: value} or {field: {op: value}}
        
    Returns:
        Filtered list
    """
    def matches(item, conditions):
        for field, condition in conditions.items():
            value = item.get(field)
            
            if isinstance(condition, dict):
                # Complex condition
                op = list(condition.keys())[0]
                target = condition[op]
                
                if op == "eq" and value != target:
                    return False
                elif op == "ne" and value == target:
                    return False
                elif op == "gt" and not (value is not None and value > target):
                    return False
                elif op == "gte" and not (value is not None and value >= target):
                    return False
                elif op == "lt" and not (value is not None and value < target):
                    return False
                elif op == "lte" and not (value is not None and value <= target):
                    return False
                elif op == "in" and value not in target:
                    return False
                elif op == "contains" and target not in str(value):
                    return False
                elif op == "startswith" and not str(value).startswith(target):
                    return False
            else:
                # Simple equality
                if value != condition:
                    return False
        return True
    
    return [item for item in data if matches(item, conditions)]


def sort_json_array(data: List[Dict[str, Any]], sort_by: str, 
                   descending: bool = False) -> List[Dict[str, Any]]:
    """
    Sort JSON array by field.
    
    Args:
        data: List of dictionaries
        sort_by: Field to sort by
        descending: Sort in descending order
        
    Returns:
        Sorted list
    """
    return sorted(data, key=lambda x: x.get(sort_by, ""), reverse=descending)


def group_json_array(data: List[Dict[str, Any]], group_by: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group JSON array by field value.
    
    Args:
        data: List of dictionaries
        group_by: Field to group by
        
    Returns:
        Dictionary with groups
    """
    groups = {}
    for item in data:
        key = str(item.get(group_by, "undefined"))
        if key not in groups:
            groups[key] = []
        groups[key].append(item)
    return groups


def aggregate_json_array(data: List[Dict[str, Any]], field: str, 
                        operation: str = "sum") -> Dict[str, Any]:
    """
    Aggregate values in JSON array.
    
    Args:
        data: List of dictionaries
        field: Field to aggregate
        operation: sum, avg, min, max, count
        
    Returns:
        Aggregation result
    """
    values = [item.get(field) for item in data if item.get(field) is not None]
    numeric_values = [v for v in values if isinstance(v, (int, float))]
    
    result = {
        "field": field,
        "operation": operation,
        "count": len(values)
    }
    
    if operation == "sum":
        result["result"] = sum(numeric_values) if numeric_values else 0
    elif operation == "avg":
        result["result"] = statistics.mean(numeric_values) if numeric_values else 0
    elif operation == "min":
        result["result"] = min(numeric_values) if numeric_values else None
    elif operation == "max":
        result["result"] = max(numeric_values) if numeric_values else None
    elif operation == "count":
        result["result"] = len(values)
    
    return result


# =============================================================================
# DATA VALIDATION TOOLS
# =============================================================================

def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate JSON against a simple schema.
    
    Args:
        data: Data to validate
        schema: Schema definition with types and required fields
        
    Returns:
        Validation result
    """
    errors = []
    
    # Check required fields
    required = schema.get("required", [])
    for field in required:
        if field not in data or data[field] is None:
            errors.append(f"Missing required field: {field}")
    
    # Check types
    properties = schema.get("properties", {})
    for field, spec in properties.items():
        if field in data and data[field] is not None:
            expected_type = spec.get("type")
            value = data[field]
            
            type_map = {
                "string": str,
                "number": (int, float),
                "integer": int,
                "boolean": bool,
                "array": list,
                "object": dict
            }
            
            if expected_type in type_map:
                if not isinstance(value, type_map[expected_type]):
                    errors.append(f"Field '{field}' should be {expected_type}, got {type(value).__name__}")
            
            # Check enum
            if "enum" in spec and value not in spec["enum"]:
                errors.append(f"Field '{field}' must be one of {spec['enum']}")
            
            # Check min/max
            if "minimum" in spec and isinstance(value, (int, float)) and value < spec["minimum"]:
                errors.append(f"Field '{field}' must be >= {spec['minimum']}")
            if "maximum" in spec and isinstance(value, (int, float)) and value > spec["maximum"]:
                errors.append(f"Field '{field}' must be <= {spec['maximum']}")
            
            # Check pattern
            if "pattern" in spec and isinstance(value, str):
                if not re.match(spec["pattern"], value):
                    errors.append(f"Field '{field}' does not match pattern {spec['pattern']}")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "error_count": len(errors)
    }


def detect_data_types(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Detect data types in a dataset.
    
    Args:
        data: List of records
        
    Returns:
        Type information for each field
    """
    if not data:
        return {"error": "Empty dataset"}
    
    type_info = {}
    
    # Collect all keys
    all_keys = set()
    for record in data:
        all_keys.update(record.keys())
    
    for key in all_keys:
        values = [record.get(key) for record in data if key in record]
        non_null_values = [v for v in values if v is not None]
        
        types = set()
        for v in non_null_values:
            if isinstance(v, bool):
                types.add("boolean")
            elif isinstance(v, int):
                types.add("integer")
            elif isinstance(v, float):
                types.add("float")
            elif isinstance(v, str):
                types.add("string")
            elif isinstance(v, list):
                types.add("array")
            elif isinstance(v, dict):
                types.add("object")
        
        type_info[key] = {
            "types": list(types),
            "nullable": len(values) > len(non_null_values),
            "null_count": len(values) - len(non_null_values),
            "sample_values": non_null_values[:3] if non_null_values else []
        }
    
    return type_info


def find_duplicates(data: List[Dict[str, Any]], key_fields: List[str]) -> Dict[str, Any]:
    """
    Find duplicate records based on key fields.
    
    Args:
        data: List of records
        key_fields: Fields to use as composite key
        
    Returns:
        Duplicate analysis
    """
    seen = {}
    duplicates = []
    
    for i, record in enumerate(data):
        key = tuple(str(record.get(f, "")) for f in key_fields)
        if key in seen:
            duplicates.append({
                "key": dict(zip(key_fields, key)),
                "indices": [seen[key], i]
            })
        else:
            seen[key] = i
    
    return {
        "total_records": len(data),
        "unique_records": len(seen),
        "duplicate_count": len(duplicates),
        "duplicates": duplicates[:10]  # Return first 10
    }


def detect_outliers(data: List[Dict[str, Any]], field: str, 
                   method: str = "iqr") -> Dict[str, Any]:
    """
    Detect outliers in numeric data.
    
    Args:
        data: List of records
        field: Numeric field to analyze
        method: Detection method (iqr, zscore)
        
    Returns:
        Outlier analysis
    """
    values = [record.get(field) for record in data 
              if isinstance(record.get(field), (int, float))]
    
    if not values:
        return {"error": "No numeric values found"}
    
    outliers = []
    
    if method == "iqr":
        sorted_values = sorted(values)
        q1 = sorted_values[len(sorted_values) // 4]
        q3 = sorted_values[(3 * len(sorted_values)) // 4]
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        for i, record in enumerate(data):
            value = record.get(field)
            if isinstance(value, (int, float)):
                if value < lower_bound or value > upper_bound:
                    outliers.append({"index": i, "value": value})
    
    elif method == "zscore":
        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0
        
        if stdev > 0:
            for i, record in enumerate(data):
                value = record.get(field)
                if isinstance(value, (int, float)):
                    zscore = (value - mean) / stdev
                    if abs(zscore) > 3:
                        outliers.append({"index": i, "value": value, "zscore": zscore})
    
    return {
        "field": field,
        "method": method,
        "total_values": len(values),
        "outlier_count": len(outliers),
        "outliers": outliers[:20]
    }


# =============================================================================
# STATISTICAL TOOLS
# =============================================================================

def calculate_statistics(values: List[float]) -> Dict[str, Any]:
    """
    Calculate comprehensive statistics for numeric data.
    
    Args:
        values: List of numeric values
        
    Returns:
        Statistical summary
    """
    if not values:
        return {"error": "Empty dataset"}
    
    numeric = [v for v in values if isinstance(v, (int, float))]
    
    if not numeric:
        return {"error": "No numeric values"}
    
    sorted_vals = sorted(numeric)
    n = len(sorted_vals)
    
    result = {
        "count": n,
        "sum": sum(sorted_vals),
        "mean": statistics.mean(sorted_vals),
        "min": min(sorted_vals),
        "max": max(sorted_vals),
        "range": max(sorted_vals) - min(sorted_vals)
    }
    
    if n > 1:
        result["median"] = statistics.median(sorted_vals)
        result["stdev"] = statistics.stdev(sorted_vals)
        result["variance"] = statistics.variance(sorted_vals)
    
    # Percentiles
    result["percentiles"] = {
        "25th": sorted_vals[n // 4],
        "50th": sorted_vals[n // 2],
        "75th": sorted_vals[(3 * n) // 4],
        "90th": sorted_vals[int(n * 0.9)],
        "95th": sorted_vals[int(n * 0.95)]
    }
    
    return result


def calculate_correlation(data: List[Dict[str, Any]], field1: str, 
                         field2: str) -> Dict[str, Any]:
    """
    Calculate Pearson correlation between two fields.
    
    Args:
        data: List of records
        field1: First numeric field
        field2: Second numeric field
        
    Returns:
        Correlation result
    """
    pairs = [(r.get(field1), r.get(field2)) for r in data
             if isinstance(r.get(field1), (int, float)) 
             and isinstance(r.get(field2), (int, float))]
    
    if len(pairs) < 2:
        return {"error": "Insufficient data points"}
    
    x = [p[0] for p in pairs]
    y = [p[1] for p in pairs]
    
    n = len(pairs)
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    
    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    denom_x = sum((x[i] - mean_x) ** 2 for i in range(n)) ** 0.5
    denom_y = sum((y[i] - mean_y) ** 2 for i in range(n)) ** 0.5
    
    if denom_x == 0 or denom_y == 0:
        return {"error": "Cannot calculate correlation (zero variance)"}
    
    correlation = numerator / (denom_x * denom_y)
    
    # Interpret correlation
    if abs(correlation) >= 0.7:
        strength = "strong"
    elif abs(correlation) >= 0.4:
        strength = "moderate"
    else:
        strength = "weak"
    
    direction = "positive" if correlation > 0 else "negative"
    
    return {
        "field1": field1,
        "field2": field2,
        "correlation": round(correlation, 4),
        "strength": strength,
        "direction": direction,
        "data_points": n
    }


def frequency_analysis(data: List[Any], top_n: int = 10) -> Dict[str, Any]:
    """
    Analyze frequency of values.
    
    Args:
        data: List of values
        top_n: Number of top values to return
        
    Returns:
        Frequency analysis
    """
    counter = Counter(data)
    total = len(data)
    
    top_items = counter.most_common(top_n)
    
    return {
        "total_count": total,
        "unique_count": len(counter),
        "top_values": [
            {
                "value": item[0],
                "count": item[1],
                "percentage": round(item[1] / total * 100, 2)
            }
            for item in top_items
        ]
    }


# =============================================================================
# DATA CLEANING TOOLS
# =============================================================================

def clean_data_record(record: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean a data record based on rules.
    
    Args:
        record: Data record
        rules: Cleaning rules per field
        
    Returns:
        Cleaned record
    """
    result = record.copy()
    
    for field, rule in rules.items():
        if field not in result:
            continue
            
        value = result[field]
        
        # Trim strings
        if rule.get("trim") and isinstance(value, str):
            value = value.strip()
        
        # Lowercase
        if rule.get("lowercase") and isinstance(value, str):
            value = value.lower()
        
        # Uppercase
        if rule.get("uppercase") and isinstance(value, str):
            value = value.upper()
        
        # Replace nullish
        if rule.get("default") is not None and (value is None or value == ""):
            value = rule["default"]
        
        # Type conversion
        if rule.get("type"):
            try:
                if rule["type"] == "string":
                    value = str(value) if value is not None else None
                elif rule["type"] == "integer":
                    value = int(float(value)) if value is not None else None
                elif rule["type"] == "float":
                    value = float(value) if value is not None else None
                elif rule["type"] == "boolean":
                    value = bool(value) if value is not None else None
            except (ValueError, TypeError):
                pass
        
        # Pattern replacement
        if rule.get("replace") and isinstance(value, str):
            for pattern, replacement in rule["replace"].items():
                value = re.sub(pattern, replacement, value)
        
        result[field] = value
    
    return result


def normalize_values(data: List[Dict[str, Any]], field: str, 
                    method: str = "minmax") -> List[Dict[str, Any]]:
    """
    Normalize numeric values in dataset.
    
    Args:
        data: List of records
        field: Field to normalize
        method: minmax or zscore
        
    Returns:
        Data with normalized values
    """
    values = [r.get(field) for r in data if isinstance(r.get(field), (int, float))]
    
    if not values:
        return data
    
    result = []
    normalized_field = f"{field}_normalized"
    
    if method == "minmax":
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val
        
        for record in data:
            new_record = record.copy()
            value = record.get(field)
            if isinstance(value, (int, float)) and range_val > 0:
                new_record[normalized_field] = (value - min_val) / range_val
            result.append(new_record)
    
    elif method == "zscore":
        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 1
        
        for record in data:
            new_record = record.copy()
            value = record.get(field)
            if isinstance(value, (int, float)) and stdev > 0:
                new_record[normalized_field] = (value - mean) / stdev
            result.append(new_record)
    
    return result


def fill_missing_values(data: List[Dict[str, Any]], field: str, 
                       strategy: str = "mean") -> List[Dict[str, Any]]:
    """
    Fill missing values in dataset.
    
    Args:
        data: List of records
        field: Field to fill
        strategy: mean, median, mode, constant
        
    Returns:
        Data with filled values
    """
    values = [r.get(field) for r in data if r.get(field) is not None]
    
    fill_value = None
    
    if strategy == "mean" and values:
        numeric = [v for v in values if isinstance(v, (int, float))]
        fill_value = statistics.mean(numeric) if numeric else None
    elif strategy == "median" and values:
        numeric = [v for v in values if isinstance(v, (int, float))]
        fill_value = statistics.median(numeric) if numeric else None
    elif strategy == "mode" and values:
        fill_value = Counter(values).most_common(1)[0][0]
    
    result = []
    for record in data:
        new_record = record.copy()
        if new_record.get(field) is None and fill_value is not None:
            new_record[field] = fill_value
        result.append(new_record)
    
    return result


# =============================================================================
# REGISTER DATA PROCESSING TOOLS
# =============================================================================

def get_data_processing_tools() -> List[FunctionTool]:
    """Get all data processing tools."""
    tools = []
    
    # Transformation tools
    tools.append(FunctionTool.from_function(
        flatten_json, name="flatten_json",
        description="Flatten nested JSON to single level with dot notation",
        category=ToolCategory.DATA
    ))
    tools.append(FunctionTool.from_function(
        merge_json, name="merge_json",
        description="Merge two JSON objects with override priority",
        category=ToolCategory.DATA
    ))
    tools.append(FunctionTool.from_function(
        extract_json_paths, name="extract_json_paths",
        description="Extract specific paths from JSON object",
        category=ToolCategory.DATA
    ))
    tools.append(FunctionTool.from_function(
        filter_json_array, name="filter_json_array",
        description="Filter JSON array by conditions",
        category=ToolCategory.DATA
    ))
    tools.append(FunctionTool.from_function(
        sort_json_array, name="sort_json_array",
        description="Sort JSON array by field",
        category=ToolCategory.DATA
    ))
    tools.append(FunctionTool.from_function(
        group_json_array, name="group_json_array",
        description="Group JSON array by field value",
        category=ToolCategory.DATA
    ))
    tools.append(FunctionTool.from_function(
        aggregate_json_array, name="aggregate_json_array",
        description="Aggregate values in JSON array (sum, avg, min, max, count)",
        category=ToolCategory.DATA
    ))
    
    # Validation tools
    tools.append(FunctionTool.from_function(
        validate_json_schema, name="validate_json_schema",
        description="Validate JSON against a schema",
        category=ToolCategory.DATA
    ))
    tools.append(FunctionTool.from_function(
        detect_data_types, name="detect_data_types",
        description="Detect data types in a dataset",
        category=ToolCategory.DATA
    ))
    tools.append(FunctionTool.from_function(
        find_duplicates, name="find_duplicates",
        description="Find duplicate records in dataset",
        category=ToolCategory.DATA
    ))
    tools.append(FunctionTool.from_function(
        detect_outliers, name="detect_outliers",
        description="Detect outliers in numeric data",
        category=ToolCategory.DATA
    ))
    
    # Statistical tools
    tools.append(FunctionTool.from_function(
        calculate_statistics, name="calculate_statistics",
        description="Calculate comprehensive statistics for numeric data",
        category=ToolCategory.DATA
    ))
    tools.append(FunctionTool.from_function(
        calculate_correlation, name="calculate_correlation",
        description="Calculate correlation between two fields",
        category=ToolCategory.DATA
    ))
    tools.append(FunctionTool.from_function(
        frequency_analysis, name="frequency_analysis",
        description="Analyze frequency of values",
        category=ToolCategory.DATA
    ))
    
    # Cleaning tools
    tools.append(FunctionTool.from_function(
        clean_data_record, name="clean_data_record",
        description="Clean a data record based on rules",
        category=ToolCategory.DATA
    ))
    tools.append(FunctionTool.from_function(
        normalize_values, name="normalize_values",
        description="Normalize numeric values (minmax or zscore)",
        category=ToolCategory.DATA
    ))
    tools.append(FunctionTool.from_function(
        fill_missing_values, name="fill_missing_values",
        description="Fill missing values with mean, median, or mode",
        category=ToolCategory.DATA
    ))
    
    return tools


def register_data_processing_tools(registry) -> int:
    """Register all data processing tools."""
    tools = get_data_processing_tools()
    count = 0
    for tool in tools:
        if registry.register(tool):
            count += 1
    logger.info(f"Registered {count} data processing tools")
    return count
