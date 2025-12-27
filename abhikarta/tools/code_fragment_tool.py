"""
Code Fragment Tool - Tool implementation for database code fragments.

Wraps code fragments stored in the database as executable tools.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import logging
import uuid
import json
from typing import Dict, Any, Optional, List

from .base_tool import (
    BaseTool, ToolMetadata, ToolSchema, ToolParameter,
    ToolResult, ToolType, ToolCategory
)

logger = logging.getLogger(__name__)


class CodeFragmentTool(BaseTool):
    """
    Tool that wraps a code fragment from the database.
    
    Supports Python code fragments with configurable input/output handling.
    Code is executed in a sandboxed environment with access to specified libraries.
    """
    
    def __init__(self, metadata: ToolMetadata, schema: ToolSchema,
                 code: str, language: str = "python",
                 allowed_imports: List[str] = None,
                 timeout_seconds: int = 30):
        """
        Initialize CodeFragmentTool.
        
        Args:
            metadata: Tool metadata
            schema: Parameter schema
            code: The code to execute
            language: Programming language (currently only Python)
            allowed_imports: List of allowed module imports
            timeout_seconds: Execution timeout
        """
        super().__init__(metadata)
        self._schema = schema
        self._code = code
        self._language = language
        self._allowed_imports = allowed_imports or [
            'json', 'math', 'datetime', 're', 'collections',
            'itertools', 'functools', 'operator', 'string'
        ]
        self._timeout_seconds = timeout_seconds
    
    @property
    def code(self) -> str:
        """Get the code fragment."""
        return self._code
    
    @property
    def language(self) -> str:
        """Get the language."""
        return self._language
    
    def execute(self, **kwargs) -> ToolResult:
        """Execute the code fragment."""
        import time
        start_time = time.time()
        
        if self._language != "python":
            return ToolResult.error_result(
                f"Language {self._language} not supported"
            )
        
        try:
            # Build execution environment
            safe_globals = self._build_safe_globals()
            safe_globals['input_data'] = kwargs
            safe_globals['params'] = kwargs
            
            # Execute code
            exec(self._code, safe_globals)
            
            # Get result
            result = safe_globals.get('result', safe_globals.get('output'))
            
            execution_time = (time.time() - start_time) * 1000
            
            return ToolResult.success_result(result, execution_time)
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"CodeFragmentTool {self.name} error: {e}")
            return ToolResult.error_result(str(e), execution_time)
    
    def _build_safe_globals(self) -> Dict[str, Any]:
        """Build a safe execution environment."""
        safe_globals = {
            '__builtins__': {
                'abs': abs, 'all': all, 'any': any, 'bool': bool,
                'dict': dict, 'enumerate': enumerate, 'filter': filter,
                'float': float, 'frozenset': frozenset, 'int': int,
                'isinstance': isinstance, 'issubclass': issubclass,
                'len': len, 'list': list, 'map': map, 'max': max,
                'min': min, 'print': print, 'range': range, 'reversed': reversed,
                'round': round, 'set': set, 'sorted': sorted, 'str': str,
                'sum': sum, 'tuple': tuple, 'type': type, 'zip': zip,
                'True': True, 'False': False, 'None': None,
                'Exception': Exception, 'ValueError': ValueError,
                'TypeError': TypeError, 'KeyError': KeyError,
            }
        }
        
        # Import allowed modules
        for module_name in self._allowed_imports:
            try:
                safe_globals[module_name] = __import__(module_name)
            except ImportError:
                pass
        
        return safe_globals
    
    def get_schema(self) -> ToolSchema:
        """Get the parameter schema."""
        return self._schema
    
    @classmethod
    def from_db_fragment(cls, fragment: Dict[str, Any]) -> 'CodeFragmentTool':
        """
        Create from database code fragment record.
        
        Args:
            fragment: Database record with fragment data
            
        Returns:
            CodeFragmentTool instance
        """
        # Parse input schema
        input_schema = fragment.get('input_schema', '{}')
        if isinstance(input_schema, str):
            try:
                input_schema = json.loads(input_schema)
            except:
                input_schema = {}
        
        schema = ToolSchema.from_json_schema(input_schema)
        
        # Parse tags
        tags = fragment.get('tags', [])
        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except:
                tags = []
        
        # Determine category
        fragment_type = fragment.get('fragment_type', 'utility')
        category_map = {
            'utility': ToolCategory.UTILITY,
            'data': ToolCategory.DATA,
            'integration': ToolCategory.INTEGRATION,
            'ai': ToolCategory.AI
        }
        category = category_map.get(fragment_type, ToolCategory.UTILITY)
        
        metadata = ToolMetadata(
            tool_id=f"frag_{fragment.get('fragment_id', uuid.uuid4().hex[:8])}",
            name=fragment.get('name', 'unknown'),
            description=fragment.get('description', ''),
            tool_type=ToolType.CODE_FRAGMENT,
            category=category,
            version=fragment.get('version', '1.0.0'),
            source=f"db:{fragment.get('uri', '')}",
            tags=['code_fragment'] + tags
        )
        
        return cls(
            metadata=metadata,
            schema=schema,
            code=fragment.get('code', ''),
            language=fragment.get('language', 'python')
        )
    
    @classmethod
    def create(cls, name: str, code: str, description: str = None,
              parameters: List[Dict[str, Any]] = None,
              category: ToolCategory = None,
              tags: List[str] = None) -> 'CodeFragmentTool':
        """
        Create a CodeFragmentTool directly.
        
        Args:
            name: Tool name
            code: Python code
            description: Tool description
            parameters: List of parameter definitions
            category: Tool category
            tags: Tool tags
            
        Returns:
            CodeFragmentTool instance
        """
        # Build schema
        schema_params = []
        for param in (parameters or []):
            schema_params.append(ToolParameter(
                name=param.get('name'),
                param_type=param.get('type', 'string'),
                description=param.get('description', ''),
                required=param.get('required', True),
                default=param.get('default')
            ))
        schema = ToolSchema(parameters=schema_params)
        
        metadata = ToolMetadata(
            tool_id=f"code_{uuid.uuid4().hex[:12]}",
            name=name,
            description=description or f"Code: {name}",
            tool_type=ToolType.CODE_FRAGMENT,
            category=category or ToolCategory.UTILITY,
            source="inline",
            tags=tags or ["code"]
        )
        
        return cls(
            metadata=metadata,
            schema=schema,
            code=code
        )


class PythonExpressionTool(CodeFragmentTool):
    """
    Simplified tool for single Python expressions.
    """
    
    def __init__(self, name: str, expression: str, description: str = None,
                 parameters: List[ToolParameter] = None):
        """
        Initialize with a single expression.
        
        Args:
            name: Tool name
            expression: Python expression to evaluate
            description: Tool description
            parameters: Input parameters
        """
        code = f"result = {expression}"
        
        schema = ToolSchema(parameters=parameters or [])
        
        metadata = ToolMetadata(
            tool_id=f"expr_{uuid.uuid4().hex[:12]}",
            name=name,
            description=description or f"Evaluate: {expression}",
            tool_type=ToolType.CODE_FRAGMENT,
            category=ToolCategory.UTILITY,
            source="expression",
            tags=["expression", "python"]
        )
        
        super().__init__(
            metadata=metadata,
            schema=schema,
            code=code
        )
    
    @classmethod
    def create(cls, name: str, expression: str,
              parameters: List[Dict[str, Any]] = None,
              description: str = None) -> 'PythonExpressionTool':
        """Create from expression string."""
        params = []
        for param in (parameters or []):
            params.append(ToolParameter(
                name=param.get('name'),
                param_type=param.get('type', 'string'),
                description=param.get('description', ''),
                required=param.get('required', True)
            ))
        
        return cls(name, expression, description, params)
