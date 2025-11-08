"""
Abhikarta LLM - Tool Management Framework
Parameter System

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

This module provides a comprehensive parameter management system with JSON Schema support.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from .types import ParameterType
from .exceptions import ParameterValidationError


@dataclass
class ToolParameter:
    """
    Represents a single parameter for a tool.
    
    Supports full JSON Schema specification for complex parameter validation.
    """
    name: str
    param_type: Union[ParameterType, str]
    description: str
    required: bool = False
    default: Any = None
    
    # Validation constraints
    enum: Optional[List[Any]] = None
    minimum: Optional[Union[int, float]] = None
    maximum: Optional[Union[int, float]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    
    # Nested structures
    properties: Optional[Dict[str, 'ToolParameter']] = None  # For objects
    items: Optional['ToolParameter'] = None  # For arrays
    additional_properties: bool = True
    
    # Documentation
    examples: Optional[List[Any]] = None
    deprecated: bool = False
    
    def __post_init__(self):
        """Normalize parameter type"""
        if isinstance(self.param_type, str):
            try:
                self.param_type = ParameterType(self.param_type)
            except ValueError:
                # Keep as string for custom types
                pass
    
    def to_json_schema(self) -> Dict[str, Any]:
        """
        Convert parameter to JSON Schema format.
        
        Returns:
            Dictionary representing the JSON Schema for this parameter
        """
        schema = {
            "type": self.param_type.value if isinstance(self.param_type, ParameterType) else self.param_type,
            "description": self.description
        }
        
        # Add constraints
        if self.enum is not None:
            schema["enum"] = self.enum
        if self.default is not None:
            schema["default"] = self.default
        if self.minimum is not None:
            schema["minimum"] = self.minimum
        if self.maximum is not None:
            schema["maximum"] = self.maximum
        if self.min_length is not None:
            schema["minLength"] = self.min_length
        if self.max_length is not None:
            schema["maxLength"] = self.max_length
        if self.pattern is not None:
            schema["pattern"] = self.pattern
        if self.examples is not None:
            schema["examples"] = self.examples
        if self.deprecated:
            schema["deprecated"] = True
        
        # Handle nested structures
        if self.properties is not None:
            schema["properties"] = {
                k: v.to_json_schema() for k, v in self.properties.items()
            }
            if not self.additional_properties:
                schema["additionalProperties"] = False
        
        if self.items is not None:
            schema["items"] = self.items.to_json_schema()
        
        return schema
    
    def validate(self, value: Any) -> bool:
        """
        Validate a value against this parameter's constraints.
        
        Args:
            value: Value to validate
            
        Returns:
            True if valid
            
        Raises:
            ParameterValidationError: If validation fails
        """
        # Check enum
        if self.enum is not None and value not in self.enum:
            raise ParameterValidationError(
                f"Value must be one of {self.enum}",
                self.name
            )
        
        # Type-specific validation
        param_type = self.param_type.value if isinstance(self.param_type, ParameterType) else self.param_type
        
        if param_type in ["number", "integer"]:
            if not isinstance(value, (int, float)):
                raise ParameterValidationError(
                    f"Expected number, got {type(value).__name__}",
                    self.name
                )
            if self.minimum is not None and value < self.minimum:
                raise ParameterValidationError(
                    f"Value {value} is less than minimum {self.minimum}",
                    self.name
                )
            if self.maximum is not None and value > self.maximum:
                raise ParameterValidationError(
                    f"Value {value} is greater than maximum {self.maximum}",
                    self.name
                )
        
        elif param_type == "string":
            if not isinstance(value, str):
                raise ParameterValidationError(
                    f"Expected string, got {type(value).__name__}",
                    self.name
                )
            if self.min_length is not None and len(value) < self.min_length:
                raise ParameterValidationError(
                    f"String length {len(value)} is less than minimum {self.min_length}",
                    self.name
                )
            if self.max_length is not None and len(value) > self.max_length:
                raise ParameterValidationError(
                    f"String length {len(value)} is greater than maximum {self.max_length}",
                    self.name
                )
            if self.pattern is not None:
                import re
                if not re.match(self.pattern, value):
                    raise ParameterValidationError(
                        f"String does not match pattern {self.pattern}",
                        self.name
                    )
        
        elif param_type == "boolean":
            if not isinstance(value, bool):
                raise ParameterValidationError(
                    f"Expected boolean, got {type(value).__name__}",
                    self.name
                )
        
        elif param_type == "array":
            if not isinstance(value, (list, tuple)):
                raise ParameterValidationError(
                    f"Expected array, got {type(value).__name__}",
                    self.name
                )
            if self.items is not None:
                for item in value:
                    self.items.validate(item)
        
        elif param_type == "object":
            if not isinstance(value, dict):
                raise ParameterValidationError(
                    f"Expected object, got {type(value).__name__}",
                    self.name
                )
            if self.properties is not None:
                for key, param in self.properties.items():
                    if key in value:
                        param.validate(value[key])
                    elif param.required:
                        raise ParameterValidationError(
                            f"Required property '{key}' is missing",
                            self.name
                        )
        
        return True


class ParameterSet:
    """
    Manages a collection of parameters for a tool.
    """
    
    def __init__(self):
        self._parameters: Dict[str, ToolParameter] = {}
    
    def add(self, parameter: ToolParameter) -> 'ParameterSet':
        """
        Add a parameter to the set.
        
        Args:
            parameter: ToolParameter to add
            
        Returns:
            Self for method chaining
        """
        self._parameters[parameter.name] = parameter
        return self
    
    def remove(self, name: str) -> 'ParameterSet':
        """Remove a parameter by name"""
        if name in self._parameters:
            del self._parameters[name]
        return self
    
    def get(self, name: str) -> Optional[ToolParameter]:
        """Get a parameter by name"""
        return self._parameters.get(name)
    
    def list_all(self) -> List[ToolParameter]:
        """Get all parameters"""
        return list(self._parameters.values())
    
    def list_required(self) -> List[ToolParameter]:
        """Get all required parameters"""
        return [p for p in self._parameters.values() if p.required]
    
    def validate_values(self, **kwargs) -> Dict[str, Any]:
        """
        Validate provided parameter values.
        
        Args:
            **kwargs: Parameter values to validate
            
        Returns:
            Dictionary of validated parameters with defaults applied
            
        Raises:
            ParameterValidationError: If validation fails
        """
        # Check for required parameters
        required_params = {p.name for p in self.list_required()}
        provided_params = set(kwargs.keys())
        missing = required_params - provided_params
        
        if missing:
            raise ParameterValidationError(
                f"Missing required parameters: {', '.join(missing)}"
            )
        
        # Check for unknown parameters
        known_params = set(self._parameters.keys())
        unknown = provided_params - known_params
        
        if unknown:
            raise ParameterValidationError(
                f"Unknown parameters: {', '.join(unknown)}"
            )
        
        # Validate each provided parameter
        validated = {}
        for name, value in kwargs.items():
            param = self._parameters[name]
            param.validate(value)
            validated[name] = value
        
        # Apply defaults for missing optional parameters
        for name, param in self._parameters.items():
            if name not in validated and param.default is not None:
                validated[name] = param.default
        
        return validated
    
    def to_json_schema(self) -> Dict[str, Any]:
        """
        Convert parameter set to JSON Schema format.
        
        Returns:
            Dictionary with 'properties' and 'required' fields
        """
        return {
            "type": "object",
            "properties": {
                name: param.to_json_schema()
                for name, param in self._parameters.items()
            },
            "required": [p.name for p in self.list_required()]
        }
