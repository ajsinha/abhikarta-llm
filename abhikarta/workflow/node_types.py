"""
Node Types - Define executable node types for workflow DAGs.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import logging
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Enumeration of supported node types."""
    INPUT = "input"
    OUTPUT = "output"
    LLM = "llm"
    TOOL = "tool"
    TOOL_EXECUTOR = "tool_executor"
    CONDITION = "condition"
    LOOP = "loop"
    PARALLEL = "parallel"
    HITL = "hitl"
    APPROVAL = "approval"
    MEMORY = "memory"
    RETRIEVAL = "retrieval"
    PYTHON = "python"
    HTTP = "http"
    TRANSFORM = "transform"
    AGGREGATE = "aggregate"
    SPLIT = "split"
    JOIN = "join"
    DELAY = "delay"
    RETRY = "retry"


@dataclass
class NodeResult:
    """Result of node execution."""
    success: bool
    output: Any = None
    error: Optional[str] = None
    duration_ms: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseNode(ABC):
    """Base class for all workflow nodes."""
    
    def __init__(self, node_id: str, name: str, config: Dict[str, Any] = None):
        self.node_id = node_id
        self.name = name
        self.config = config or {}
        self.execution_count = 0
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> NodeResult:
        """
        Execute the node.
        
        Args:
            context: Execution context with input data and state
            
        Returns:
            NodeResult with output or error
        """
        pass
    
    def validate(self) -> List[str]:
        """Validate node configuration. Returns list of errors."""
        return []


class InputNode(BaseNode):
    """Input node - entry point for workflow data."""
    
    def execute(self, context: Dict[str, Any]) -> NodeResult:
        start = time.time()
        try:
            # Pass through input data
            input_data = context.get('input', {})
            
            # Apply any transformations from config
            if self.config.get('schema'):
                # Validate against schema if provided
                pass
            
            return NodeResult(
                success=True,
                output=input_data,
                duration_ms=int((time.time() - start) * 1000)
            )
        except Exception as e:
            return NodeResult(success=False, error=str(e))


class OutputNode(BaseNode):
    """Output node - collects and formats final output."""
    
    def execute(self, context: Dict[str, Any]) -> NodeResult:
        start = time.time()
        try:
            # Collect output from previous nodes
            output = context.get('accumulated_output', {})
            
            # Apply output formatting
            if self.config.get('format'):
                output = self._format_output(output, self.config['format'])
            
            return NodeResult(
                success=True,
                output=output,
                duration_ms=int((time.time() - start) * 1000)
            )
        except Exception as e:
            return NodeResult(success=False, error=str(e))
    
    def _format_output(self, data: Any, format_spec: str) -> Any:
        if format_spec == 'json':
            return json.dumps(data, indent=2)
        elif format_spec == 'text':
            return str(data)
        return data


class PythonNode(BaseNode):
    """Python node - executes Python code."""
    
    def __init__(self, node_id: str, name: str, config: Dict[str, Any] = None, 
                 python_code: str = None):
        super().__init__(node_id, name, config)
        self.python_code = python_code or config.get('code', '')
    
    def execute(self, context: Dict[str, Any]) -> NodeResult:
        start = time.time()
        
        if not self.python_code:
            return NodeResult(success=False, error="No Python code provided")
        
        try:
            # Create execution namespace
            local_vars = {
                'input_data': context.get('input', {}),
                'context': context,
                'config': self.config,
                'output': None
            }
            
            # Add any imported modules from context
            if 'modules' in context:
                local_vars.update(context['modules'])
            
            # Execute the code
            exec(self.python_code, {'__builtins__': __builtins__}, local_vars)
            
            # Get output
            output = local_vars.get('output') or local_vars.get('result')
            
            return NodeResult(
                success=True,
                output=output,
                duration_ms=int((time.time() - start) * 1000),
                metadata={'code_lines': len(self.python_code.split('\n'))}
            )
            
        except Exception as e:
            logger.error(f"Python node execution error: {e}")
            return NodeResult(
                success=False,
                error=str(e),
                duration_ms=int((time.time() - start) * 1000)
            )
    
    def validate(self) -> List[str]:
        errors = []
        if not self.python_code:
            errors.append(f"Node '{self.node_id}' has no Python code")
        else:
            try:
                compile(self.python_code, '<string>', 'exec')
            except SyntaxError as e:
                errors.append(f"Syntax error in node '{self.node_id}': {e}")
        return errors


class LLMNode(BaseNode):
    """LLM node - calls language model."""
    
    def __init__(self, node_id: str, name: str, config: Dict[str, Any] = None,
                 llm_facade=None):
        super().__init__(node_id, name, config)
        self.llm_facade = llm_facade
    
    def execute(self, context: Dict[str, Any]) -> NodeResult:
        start = time.time()
        
        try:
            # Get LLM configuration
            provider = self.config.get('provider', 'openai')
            model = self.config.get('model', 'gpt-4o')
            temperature = self.config.get('temperature', 0.7)
            max_tokens = self.config.get('max_tokens', 2000)
            
            # Build prompt
            system_prompt = self.config.get('system_prompt', '')
            user_prompt = self.config.get('user_prompt', '')
            
            # Substitute variables from context
            input_data = context.get('input', {})
            if isinstance(input_data, dict):
                for key, value in input_data.items():
                    user_prompt = user_prompt.replace(f'{{{key}}}', str(value))
            
            # This would call the actual LLM facade
            # For now, return placeholder
            output = {
                'provider': provider,
                'model': model,
                'prompt': user_prompt,
                'response': f"[LLM Response would appear here - {model}]"
            }
            
            return NodeResult(
                success=True,
                output=output,
                duration_ms=int((time.time() - start) * 1000),
                metadata={
                    'provider': provider,
                    'model': model,
                    'tokens_used': 0
                }
            )
            
        except Exception as e:
            return NodeResult(success=False, error=str(e))


class ConditionNode(BaseNode):
    """Condition node - branching logic."""
    
    def execute(self, context: Dict[str, Any]) -> NodeResult:
        start = time.time()
        
        try:
            condition = self.config.get('condition', 'True')
            input_data = context.get('input', {})
            
            # Evaluate condition
            result = eval(condition, {'input': input_data, 'context': context})
            
            return NodeResult(
                success=True,
                output={'condition_result': bool(result)},
                duration_ms=int((time.time() - start) * 1000),
                metadata={'branch': 'true' if result else 'false'}
            )
            
        except Exception as e:
            return NodeResult(success=False, error=str(e))


class TransformNode(BaseNode):
    """Transform node - data transformation."""
    
    def execute(self, context: Dict[str, Any]) -> NodeResult:
        start = time.time()
        
        try:
            input_data = context.get('input', {})
            transform_type = self.config.get('transform_type', 'passthrough')
            
            if transform_type == 'passthrough':
                output = input_data
            elif transform_type == 'extract':
                key = self.config.get('key')
                output = input_data.get(key) if isinstance(input_data, dict) else input_data
            elif transform_type == 'map':
                mapping = self.config.get('mapping', {})
                output = {mapping.get(k, k): v for k, v in input_data.items()}
            elif transform_type == 'filter':
                keys = self.config.get('keys', [])
                output = {k: v for k, v in input_data.items() if k in keys}
            else:
                output = input_data
            
            return NodeResult(
                success=True,
                output=output,
                duration_ms=int((time.time() - start) * 1000)
            )
            
        except Exception as e:
            return NodeResult(success=False, error=str(e))


class HTTPNode(BaseNode):
    """HTTP node - makes HTTP requests."""
    
    def execute(self, context: Dict[str, Any]) -> NodeResult:
        start = time.time()
        
        try:
            import urllib.request
            import urllib.parse
            
            url = self.config.get('url', '')
            method = self.config.get('method', 'GET')
            headers = self.config.get('headers', {})
            body = self.config.get('body')
            
            # Substitute variables
            input_data = context.get('input', {})
            if isinstance(input_data, dict):
                for key, value in input_data.items():
                    url = url.replace(f'{{{key}}}', str(value))
            
            # Make request
            req = urllib.request.Request(url, method=method)
            for k, v in headers.items():
                req.add_header(k, v)
            
            if body and method in ['POST', 'PUT', 'PATCH']:
                req.data = json.dumps(body).encode('utf-8')
                req.add_header('Content-Type', 'application/json')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                response_data = response.read().decode('utf-8')
                try:
                    output = json.loads(response_data)
                except:
                    output = response_data
            
            return NodeResult(
                success=True,
                output=output,
                duration_ms=int((time.time() - start) * 1000),
                metadata={'status_code': 200, 'url': url}
            )
            
        except Exception as e:
            return NodeResult(success=False, error=str(e))


class DelayNode(BaseNode):
    """Delay node - adds delay to workflow."""
    
    def execute(self, context: Dict[str, Any]) -> NodeResult:
        start = time.time()
        
        try:
            delay_seconds = self.config.get('delay_seconds', 1)
            time.sleep(delay_seconds)
            
            return NodeResult(
                success=True,
                output=context.get('input'),
                duration_ms=int((time.time() - start) * 1000)
            )
            
        except Exception as e:
            return NodeResult(success=False, error=str(e))


class NodeFactory:
    """Factory for creating node instances."""
    
    NODE_CLASSES = {
        'input': InputNode,
        'output': OutputNode,
        'python': PythonNode,
        'llm': LLMNode,
        'condition': ConditionNode,
        'transform': TransformNode,
        'http': HTTPNode,
        'delay': DelayNode,
    }
    
    @classmethod
    def create(cls, node_type: str, node_id: str, name: str, 
               config: Dict[str, Any] = None, **kwargs) -> BaseNode:
        """
        Create a node instance.
        
        Args:
            node_type: Type of node to create
            node_id: Unique identifier for the node
            name: Display name
            config: Node configuration
            **kwargs: Additional node-specific arguments
            
        Returns:
            Node instance
        """
        node_class = cls.NODE_CLASSES.get(node_type, PythonNode)
        
        if node_type == 'python':
            return node_class(node_id, name, config, 
                            python_code=kwargs.get('python_code'))
        elif node_type == 'llm':
            return node_class(node_id, name, config,
                            llm_facade=kwargs.get('llm_facade'))
        else:
            return node_class(node_id, name, config)
    
    @classmethod
    def register(cls, node_type: str, node_class: type):
        """Register a custom node type."""
        cls.NODE_CLASSES[node_type] = node_class
