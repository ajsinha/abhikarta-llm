"""
Properties File Parser - Java-style .properties file support.

Supports:
- Key=value pairs
- Comments (# or !)
- Dot notation for hierarchy (database.host=localhost)
- Environment variable interpolation (${ENV_VAR} or ${ENV_VAR:default})
- Multi-line values with backslash continuation
- Type coercion (boolean, int, float, list)

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Version: 1.5.3
"""

import os
import re
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class PropertiesParser:
    """
    Parser for Java-style .properties files.
    
    Example properties file:
        # Application settings
        app.name=Abhikarta-LLM
        app.version=1.5.3
        app.debug=false
        
        # Database
        database.type=sqlite
        database.sqlite.path=./data/abhikarta.db
        
        # With environment variables
        database.password=${DB_PASSWORD:secret}
        
        # Lists (comma-separated)
        code_fragments.status_filter=approved,published
    """
    
    # Regex for environment variable interpolation: ${VAR} or ${VAR:default}
    ENV_VAR_PATTERN = re.compile(r'\$\{([^}:]+)(?::([^}]*))?\}')
    
    def __init__(self):
        self._properties: Dict[str, str] = {}
    
    def load(self, filepath: Union[str, Path]) -> Dict[str, str]:
        """
        Load properties from file.
        
        Args:
            filepath: Path to .properties file
            
        Returns:
            Dictionary of properties
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            logger.warning(f"Properties file not found: {filepath}")
            return {}
        
        self._properties = {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self._parse_file(f)
            
            logger.info(f"Loaded {len(self._properties)} properties from {filepath}")
            return self._properties.copy()
            
        except Exception as e:
            logger.error(f"Error loading properties file: {e}")
            return {}
    
    def _parse_file(self, file) -> None:
        """Parse properties file content."""
        current_key = None
        current_value = []
        
        for line_num, line in enumerate(file, 1):
            # Strip trailing whitespace but preserve leading for continuation
            line = line.rstrip()
            
            # Skip empty lines
            if not line.strip():
                if current_key:
                    # End of multi-line value
                    self._set_property(current_key, ''.join(current_value))
                    current_key = None
                    current_value = []
                continue
            
            # Skip comments
            stripped = line.lstrip()
            if stripped.startswith('#') or stripped.startswith('!'):
                continue
            
            # Check for continuation
            if current_key and line.startswith((' ', '\t')):
                # Continuation of previous value
                current_value.append(stripped)
                continue
            
            # End previous multi-line if any
            if current_key:
                self._set_property(current_key, ''.join(current_value))
                current_key = None
                current_value = []
            
            # Parse key=value or key:value
            match = re.match(r'^([^=:]+)[=:](.*)$', line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                
                # Check for line continuation (ends with \)
                if value.endswith('\\'):
                    current_key = key
                    current_value = [value[:-1]]
                else:
                    self._set_property(key, value)
            else:
                logger.warning(f"Invalid property line {line_num}: {line}")
        
        # Handle any remaining multi-line value
        if current_key:
            self._set_property(current_key, ''.join(current_value))
    
    def _set_property(self, key: str, value: str) -> None:
        """Set a property with environment variable interpolation."""
        # Interpolate environment variables
        value = self._interpolate_env(value)
        self._properties[key] = value
    
    def _interpolate_env(self, value: str) -> str:
        """
        Replace ${VAR} or ${VAR:default} with environment variable values.
        
        Args:
            value: String possibly containing ${VAR} patterns
            
        Returns:
            String with environment variables resolved
        """
        def replace_env(match):
            var_name = match.group(1)
            default = match.group(2)
            
            env_value = os.environ.get(var_name)
            if env_value is not None:
                return env_value
            elif default is not None:
                return default
            else:
                logger.warning(f"Environment variable not found: {var_name}")
                return match.group(0)  # Return original if not found
        
        return self.ENV_VAR_PATTERN.sub(replace_env, value)
    
    def get(self, key: str, default: Any = None) -> Optional[str]:
        """Get a property value."""
        return self._properties.get(key, default)
    
    def get_str(self, key: str, default: str = "") -> str:
        """Get property as string."""
        return self._properties.get(key, default)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get property as integer."""
        value = self._properties.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            logger.warning(f"Invalid integer for {key}: {value}")
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get property as float."""
        value = self._properties.get(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            logger.warning(f"Invalid float for {key}: {value}")
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        Get property as boolean.
        
        True values: true, yes, on, 1
        False values: false, no, off, 0
        """
        value = self._properties.get(key)
        if value is None:
            return default
        
        value_lower = value.lower().strip()
        if value_lower in ('true', 'yes', 'on', '1'):
            return True
        elif value_lower in ('false', 'no', 'off', '0'):
            return False
        else:
            logger.warning(f"Invalid boolean for {key}: {value}")
            return default
    
    def get_list(self, key: str, default: List[str] = None, 
                 separator: str = ',') -> List[str]:
        """
        Get property as list (comma-separated by default).
        
        Args:
            key: Property key
            default: Default value if not found
            separator: List separator (default: comma)
            
        Returns:
            List of strings
        """
        if default is None:
            default = []
        
        value = self._properties.get(key)
        if value is None:
            return default
        
        return [item.strip() for item in value.split(separator) if item.strip()]
    
    def get_prefixed(self, prefix: str) -> Dict[str, str]:
        """
        Get all properties with a given prefix.
        
        Args:
            prefix: Key prefix (e.g., "database.")
            
        Returns:
            Dictionary of matching properties with prefix removed
        """
        result = {}
        for key, value in self._properties.items():
            if key.startswith(prefix):
                new_key = key[len(prefix):]
                result[new_key] = value
        return result
    
    def to_nested_dict(self) -> Dict[str, Any]:
        """
        Convert flat properties to nested dictionary using dot notation.
        
        Example:
            database.host=localhost -> {'database': {'host': 'localhost'}}
        """
        result = {}
        
        for key, value in self._properties.items():
            parts = key.split('.')
            current = result
            
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {}
                elif not isinstance(current[part], dict):
                    # Key conflict - existing value is not a dict
                    current[part] = {'_value': current[part]}
                current = current[part]
            
            # Set the final value
            final_key = parts[-1]
            current[final_key] = value
        
        return result
    
    @property
    def properties(self) -> Dict[str, str]:
        """Get all properties as dictionary."""
        return self._properties.copy()
    
    def __contains__(self, key: str) -> bool:
        return key in self._properties
    
    def __getitem__(self, key: str) -> str:
        return self._properties[key]
    
    def __len__(self) -> int:
        return len(self._properties)


def load_properties(filepath: Union[str, Path]) -> PropertiesParser:
    """
    Convenience function to load properties file.
    
    Args:
        filepath: Path to .properties file
        
    Returns:
        PropertiesParser instance with loaded properties
    """
    parser = PropertiesParser()
    parser.load(filepath)
    return parser
