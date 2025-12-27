"""
DAG Parser - Parse and validate DAG workflow definitions.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import json
import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class DAGNode:
    """Represents a node in the DAG workflow."""
    node_id: str
    name: str
    node_type: str
    config: Dict[str, Any] = field(default_factory=dict)
    python_code: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    position: Dict[str, int] = field(default_factory=lambda: {'x': 0, 'y': 0})
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'node_id': self.node_id,
            'name': self.name,
            'node_type': self.node_type,
            'config': self.config,
            'python_code': self.python_code,
            'dependencies': self.dependencies,
            'position': self.position
        }


@dataclass
class DAGWorkflow:
    """Represents a complete DAG workflow."""
    workflow_id: str
    name: str
    description: str = ""
    version: str = "1.0.0"
    nodes: Dict[str, DAGNode] = field(default_factory=dict)
    edges: List[Dict[str, str]] = field(default_factory=list)
    entry_point: Optional[str] = None
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    python_modules: Dict[str, str] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)
    
    def get_execution_order(self) -> List[str]:
        """Get topologically sorted execution order."""
        visited = set()
        order = []
        
        def visit(node_id: str):
            if node_id in visited:
                return
            visited.add(node_id)
            
            node = self.nodes.get(node_id)
            if node:
                for dep in node.dependencies:
                    visit(dep)
                order.append(node_id)
        
        # Start from entry point or all nodes without dependencies
        if self.entry_point and self.entry_point in self.nodes:
            visit(self.entry_point)
        else:
            for node_id in self.nodes:
                visit(node_id)
        
        return order
    
    def validate(self) -> List[str]:
        """Validate the workflow and return list of errors."""
        errors = []
        
        # Check for empty workflow
        if not self.nodes:
            errors.append("Workflow has no nodes")
            return errors
        
        # Check for cycles
        if self._has_cycle():
            errors.append("Workflow contains cycles - DAG must be acyclic")
        
        # Validate node references
        for node_id, node in self.nodes.items():
            for dep in node.dependencies:
                if dep not in self.nodes:
                    errors.append(f"Node '{node_id}' references unknown dependency '{dep}'")
        
        # Validate edge references
        for edge in self.edges:
            if edge.get('source') not in self.nodes:
                errors.append(f"Edge references unknown source node '{edge.get('source')}'")
            if edge.get('target') not in self.nodes:
                errors.append(f"Edge references unknown target node '{edge.get('target')}'")
        
        # Validate entry point
        if self.entry_point and self.entry_point not in self.nodes:
            errors.append(f"Entry point '{self.entry_point}' not found in nodes")
        
        return errors
    
    def _has_cycle(self) -> bool:
        """Check if the DAG has any cycles."""
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {node_id: WHITE for node_id in self.nodes}
        
        def dfs(node_id: str) -> bool:
            color[node_id] = GRAY
            node = self.nodes.get(node_id)
            if node:
                for dep in node.dependencies:
                    if dep in color:
                        if color[dep] == GRAY:
                            return True
                        if color[dep] == WHITE and dfs(dep):
                            return True
            color[node_id] = BLACK
            return False
        
        for node_id in self.nodes:
            if color[node_id] == WHITE:
                if dfs(node_id):
                    return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'workflow_id': self.workflow_id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'nodes': {k: v.to_dict() for k, v in self.nodes.items()},
            'edges': self.edges,
            'entry_point': self.entry_point,
            'input_schema': self.input_schema,
            'output_schema': self.output_schema,
            'python_modules': self.python_modules,
            'environment': self.environment
        }


class DAGParser:
    """
    Parser for DAG workflow definitions.
    
    Supports JSON workflow definitions with embedded Python modules.
    """
    
    SUPPORTED_NODE_TYPES = [
        'input', 'output', 'llm', 'tool', 'tool_executor',
        'condition', 'loop', 'parallel', 'hitl', 'approval',
        'memory', 'retrieval', 'python', 'http', 'transform',
        'aggregate', 'split', 'join', 'delay', 'retry'
    ]
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def parse_json(self, json_str: str) -> Optional[DAGWorkflow]:
        """
        Parse a JSON workflow definition.
        
        Args:
            json_str: JSON string containing workflow definition
            
        Returns:
            DAGWorkflow object or None if parsing fails
        """
        self.errors = []
        self.warnings = []
        
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {e}")
            return None
        
        return self.parse_dict(data)
    
    def parse_dict(self, data: Dict[str, Any]) -> Optional[DAGWorkflow]:
        """
        Parse a dictionary workflow definition.
        
        Args:
            data: Dictionary containing workflow definition
            
        Returns:
            DAGWorkflow object or None if parsing fails
        """
        self.errors = []
        self.warnings = []
        
        # Validate required fields
        if 'workflow_id' not in data and 'id' not in data:
            self.errors.append("Missing required field: workflow_id")
        if 'name' not in data:
            self.errors.append("Missing required field: name")
        if 'nodes' not in data:
            self.errors.append("Missing required field: nodes")
        
        if self.errors:
            return None
        
        # Create workflow
        workflow = DAGWorkflow(
            workflow_id=data.get('workflow_id') or data.get('id'),
            name=data['name'],
            description=data.get('description', ''),
            version=data.get('version', '1.0.0'),
            entry_point=data.get('entry_point'),
            input_schema=data.get('input_schema', {}),
            output_schema=data.get('output_schema', {}),
            python_modules=data.get('python_modules', {}),
            environment=data.get('environment', {})
        )
        
        # Parse nodes
        nodes_data = data.get('nodes', {})
        if isinstance(nodes_data, list):
            # Convert list format to dict format
            nodes_data = {n.get('node_id') or n.get('id'): n for n in nodes_data}
        
        for node_id, node_data in nodes_data.items():
            node = self._parse_node(node_id, node_data)
            if node:
                workflow.nodes[node_id] = node
        
        # Parse edges
        edges = data.get('edges', [])
        for edge in edges:
            if isinstance(edge, dict):
                workflow.edges.append(edge)
                # Update dependencies based on edges
                target = edge.get('target')
                source = edge.get('source')
                if target in workflow.nodes and source:
                    if source not in workflow.nodes[target].dependencies:
                        workflow.nodes[target].dependencies.append(source)
        
        # Validate workflow
        validation_errors = workflow.validate()
        self.errors.extend(validation_errors)
        
        if self.errors:
            logger.warning(f"Workflow parsing completed with errors: {self.errors}")
        
        return workflow
    
    def _parse_node(self, node_id: str, data: Dict[str, Any]) -> Optional[DAGNode]:
        """Parse a single node definition."""
        node_type = data.get('type') or data.get('node_type', 'python')
        
        if node_type not in self.SUPPORTED_NODE_TYPES:
            self.warnings.append(f"Unknown node type '{node_type}' for node '{node_id}'")
        
        return DAGNode(
            node_id=node_id,
            name=data.get('name', node_id),
            node_type=node_type,
            config=data.get('config', {}),
            python_code=data.get('python_code') or data.get('code'),
            dependencies=data.get('dependencies', []),
            position={
                'x': data.get('position', {}).get('x', 0),
                'y': data.get('position', {}).get('y', 0)
            }
        )
    
    def parse_file(self, file_path: str) -> Optional[DAGWorkflow]:
        """
        Parse a workflow from a JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            DAGWorkflow object or None if parsing fails
        """
        try:
            with open(file_path, 'r') as f:
                return self.parse_json(f.read())
        except FileNotFoundError:
            self.errors.append(f"File not found: {file_path}")
            return None
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return None
    
    def get_errors(self) -> List[str]:
        """Get parsing errors."""
        return self.errors
    
    def get_warnings(self) -> List[str]:
        """Get parsing warnings."""
        return self.warnings
