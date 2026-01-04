"""
Properties Configurator - Singleton for managing application properties.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.

Patent Pending: Certain architectural patterns and implementations described in this
software may be subject to patent applications.

Features:
- Singleton pattern for global configuration access
- Multiple property file support with precedence
- Environment variable overrides
- Command line argument overrides (--key=value)
- ${...} pattern resolution with nesting support
- Auto-reload capability
- Thread-safe operations
"""

import json
import os
import re
import sys
import threading
import time
from typing import Optional, List, Union, Dict, Any
from pathlib import Path
from abhikarta.core import SingletonMeta


class PropertiesConfigurator(metaclass=SingletonMeta):
    """
    Singleton thread-safe class for managing properties from configuration files.
    Supports property value resolution with ${...} patterns and auto-reload.

    Order of precedence (highest to lowest):
    1. Command line arguments (--key=value)
    2. Environment variables
    3. Property files (rightmost file has highest precedence)
    
    Usage:
        # Initialize with property files
        prop_conf = PropertiesConfigurator(properties_files=[
            'config/application.properties',
            'config/database.properties'
        ])
        
        # Get properties
        value = prop_conf.get('database.host', default='localhost')
        port = prop_conf.get_int('server.port', default=5000)
        debug = prop_conf.get_bool('app.debug', default=False)
    
    Note: Singleton behavior is handled by SingletonMeta metaclass.
    """

    def __init__(self, properties_files: Union[str, List[str]] = None, reload_interval: int = 300):
        """
        Initialize the PropertiesConfigurator.

        Args:
            properties_files: List of property file paths OR comma-delimited string
            reload_interval: Interval in seconds for auto-reload (default: 300 = 5 minutes)
        """
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
        self._properties_files = self._parse_file_paths(properties_files)
        self._reload_interval = reload_interval
        self._properties: Dict[str, str] = {}
        self._properties_lock = threading.RLock()
        self._stop_reload = threading.Event()
        self._file_timestamps: Dict[str, float] = {}
        self._property_sources: Dict[str, str] = {}
        self._commandline_args: Dict[str, str] = {}
        
        # Parse command line arguments
        self._parse_commandline_args()
        
        # Initial load
        self._load_properties()
        
        # Start auto-reload thread
        self._reload_thread = threading.Thread(target=self._auto_reload_worker, daemon=True)
        self._reload_thread.start()

    def _parse_file_paths(self, properties_files: Union[str, List[str], None]) -> List[str]:
        """Parse properties files input - handle both string and list formats."""
        if properties_files is None:
            return []
        if isinstance(properties_files, str):
            return [path.strip() for path in properties_files.split(',') if path.strip()]
        if isinstance(properties_files, list):
            return [str(path).strip() for path in properties_files if path]
        return []

    def _parse_commandline_args(self):
        """Parse command line arguments in --key=value format."""
        for arg in sys.argv[1:]:
            if arg.startswith('--') and '=' in arg:
                arg = arg[2:]
                key, value = arg.split('=', 1)
                key = key.strip()
                value = value.strip()
                if key:
                    self._commandline_args[key] = value

    def _load_properties(self):
        """Load properties from all configured files with precedence handling."""
        with self._properties_lock:
            new_properties = {}
            new_sources = {}

            # Process files in order (rightmost has highest precedence)
            for file_path in self._properties_files:
                if not os.path.exists(file_path):
                    continue

                self._file_timestamps[file_path] = os.path.getmtime(file_path)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if not line or line.startswith('#') or line.startswith('//'):
                                continue
                            if '=' not in line:
                                continue
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            if key:
                                new_properties[key] = value
                                new_sources[key] = 'file'
                except Exception as e:
                    print(f"Error loading properties from {file_path}: {e}")

            # Resolve ${...} references
            resolved_properties = self._resolve_all_properties(new_properties)

            # Apply precedence: file < env < commandline
            final_properties = {}
            final_sources = {}

            for key in resolved_properties:
                value = resolved_properties[key]
                source = 'file'

                # Check environment variables
                env_value = os.environ.get(key)
                if env_value is not None:
                    value = env_value
                    source = 'env'

                # Check command line arguments (highest precedence)
                if key in self._commandline_args:
                    value = self._commandline_args[key]
                    source = 'commandline'

                final_properties[key] = value
                final_sources[key] = source

            # Add command-line only keys
            for key, value in self._commandline_args.items():
                if key not in final_properties:
                    final_properties[key] = value
                    final_sources[key] = 'commandline'

            self._properties = final_properties
            self._property_sources = final_sources

    def _resolve_all_properties(self, properties: Dict[str, str]) -> Dict[str, str]:
        """Resolve all ${...} references in properties."""
        resolved = {}
        for key, value in properties.items():
            resolved[key] = self._resolve_value(value, properties, set())
        return resolved

    def _resolve_value(self, value: str, properties: Dict[str, str], visited: set) -> str:
        """Recursively resolve ${...} references in a value."""
        if not value or '${' not in value:
            return value

        max_iterations = 100
        iteration = 0

        while '${' in value and iteration < max_iterations:
            iteration += 1
            pattern = r'\$\{([^{}]+)\}'
            matches = list(re.finditer(pattern, value))

            if not matches:
                break

            for match in reversed(matches):
                placeholder = match.group(0)
                key = match.group(1)

                # Handle default value syntax: ${key:default}
                default_value = None
                if ':' in key:
                    key, default_value = key.split(':', 1)

                # Check for circular reference
                if key in visited:
                    continue

                # Get replacement value
                replacement = None
                
                # Priority: commandline > env > properties
                if key in self._commandline_args:
                    replacement = self._commandline_args[key]
                elif key in os.environ:
                    replacement = os.environ[key]
                elif key in properties:
                    new_visited = visited | {key}
                    replacement = self._resolve_value(properties[key], properties, new_visited)

                if replacement is None:
                    replacement = default_value if default_value else placeholder

                value = value[:match.start()] + replacement + value[match.end():]

        return value

    def _auto_reload_worker(self):
        """Background thread for auto-reloading properties."""
        while not self._stop_reload.wait(self._reload_interval):
            self._check_and_reload()

    def _check_and_reload(self):
        """Check if any property file has changed and reload if needed."""
        needs_reload = False
        for file_path in self._properties_files:
            if os.path.exists(file_path):
                current_mtime = os.path.getmtime(file_path)
                if file_path not in self._file_timestamps or current_mtime > self._file_timestamps[file_path]:
                    needs_reload = True
                    break
        if needs_reload:
            self._load_properties()

    def get(self, key: str, default: str = None) -> Optional[str]:
        """
        Get a property value.

        Args:
            key: Property key
            default: Default value if key not found

        Returns:
            Property value or default
        """
        with self._properties_lock:
            return self._properties.get(key, default)

    def get_int(self, key: str, default: int = None) -> Optional[int]:
        """Get property value as integer."""
        value = self.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def get_float(self, key: str, default: float = None) -> Optional[float]:
        """Get property value as float."""
        value = self.get(key)
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def get_bool(self, key: str, default: bool = None) -> Optional[bool]:
        """Get property value as boolean."""
        value = self.get(key)
        if value is None:
            return default
        return value.lower() in ('true', 'yes', '1', 'on', 'enabled')

    def get_list(self, key: str, delim: str = ',') -> Optional[List[str]]:
        """Get property value as list of strings."""
        value = self.get(key)
        if value is None:
            return None
        return [item.strip() for item in value.split(delim) if item.strip()]

    def get_int_list(self, key: str, delim: str = ',') -> Optional[List[int]]:
        """Get property value as list of integers."""
        str_list = self.get_list(key, delim)
        if str_list is None:
            return None
        result = []
        for item in str_list:
            try:
                result.append(int(item))
            except (ValueError, TypeError):
                continue
        return result if result else None

    def get_source(self, key: str) -> Optional[str]:
        """Get the source of a property value (file, env, or commandline)."""
        with self._properties_lock:
            return self._property_sources.get(key)

    def get_all_properties(self) -> Dict[str, str]:
        """Get all properties."""
        with self._properties_lock:
            return self._properties.copy()

    def get_all_sources(self) -> Dict[str, str]:
        """Get sources for all properties."""
        with self._properties_lock:
            return self._property_sources.copy()

    def get_properties_by_pattern(self, pattern: str) -> Dict[str, str]:
        """Get all properties whose keys match the given regex pattern."""
        with self._properties_lock:
            try:
                regex = re.compile(pattern)
                return {k: v for k, v in self._properties.items() if regex.match(k)}
            except re.error:
                return {}

    def resolve_string_content(self, content: str) -> str:
        """Resolve ${prop_name} patterns in a string."""
        if not content or '${' not in content:
            return content
        with self._properties_lock:
            return self._resolve_value(content, self._properties, set())

    def load_and_resolve_json_file(self, filename: Union[str, Path]) -> Dict[str, Any]:
        """Load a JSON file and resolve ${...} patterns."""
        file_path = Path(filename)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        resolved = self.resolve_string_content(content)
        return json.loads(resolved)

    def reload(self):
        """Force reload of all properties."""
        self._load_properties()

    def stop_reload(self):
        """Stop the auto-reload thread."""
        self._stop_reload.set()
        if hasattr(self, '_reload_thread'):
            self._reload_thread.join(timeout=5)

    def set(self, key: str, value: str, source: str = 'runtime'):
        """
        Set a property value at runtime.

        Args:
            key: Property key
            value: Property value
            source: Source identifier (default: 'runtime')
        """
        with self._properties_lock:
            self._properties[key] = value
            self._property_sources[key] = source
