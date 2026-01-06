"""
DAG Parser - Parse and validate DAG workflow definitions.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha

Version: 1.5.2-fix2 (edge format fix for from/to)
"""

import json
import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Log version on module load
logger.info("DAG Parser v1.5.2-fix2 loaded (supports from/to edge format)")


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
    metadata: Dict[str, Any] = field(default_factory=dict)
    
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
        
        logger.info(f"Validating workflow with {len(self.nodes)} nodes and {len(self.edges)} edges")
        logger.debug(f"Node IDs: {list(self.nodes.keys())}")
        
        # Check for cycles - this is a warning, not error, since LangGraph supports cycles
        # through conditional edges (used for iterative workflows)
        if self._has_cycle():
            logger.info("Workflow contains cycles - this is allowed for iterative workflows with conditional edges")
        
        # Validate node references
        for node_id, node in self.nodes.items():
            for dep in node.dependencies:
                if dep not in self.nodes:
                    errors.append(f"Node '{node_id}' references unknown dependency '{dep}'")
        
        # Validate edge references - be strict but informative
        valid_edge_count = 0
        for i, edge in enumerate(self.edges):
            source = edge.get('source')
            target = edge.get('target')
            
            # Log detailed debug info for each edge
            logger.debug(f"Validating edge {i}: source='{source}', target='{target}'")
            
            # Skip completely invalid edges (shouldn't exist but handle gracefully)
            if source is None or target is None:
                logger.warning(f"Edge {i} has None values - source='{source}', target='{target}', skipping")
                continue
            
            valid_edge_count += 1
            
            # Check source exists
            if source not in self.nodes:
                errors.append(f"Edge {i}: source node '{source}' not found in workflow nodes")
                logger.warning(f"Edge {i}: source '{source}' not in nodes {list(self.nodes.keys())[:10]}...")
            
            # Check target exists  
            if target not in self.nodes:
                errors.append(f"Edge {i}: target node '{target}' not found in workflow nodes")
                logger.warning(f"Edge {i}: target '{target}' not in nodes {list(self.nodes.keys())[:10]}...")
        
        logger.info(f"Edge validation: {valid_edge_count} valid edges out of {len(self.edges)} total")
        
        # Validate entry point
        if self.entry_point:
            if self.entry_point not in self.nodes:
                errors.append(f"Entry point '{self.entry_point}' not found in nodes")
                logger.warning(f"Entry point '{self.entry_point}' not in nodes: {list(self.nodes.keys())}")
            else:
                logger.debug(f"Entry point '{self.entry_point}' validated successfully")
        
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
        # I/O nodes
        'input', 'output', 'start', 'end',
        # LLM/AI nodes
        'llm', 'agent', 'rag',
        # Tool nodes
        'tool', 'tool_executor',
        # Control flow nodes
        'condition', 'loop', 'parallel',
        # Human interaction nodes
        'hitl', 'human', 'human_in_the_loop', 'approval', 'review',
        # Data processing nodes
        'memory', 'retrieval', 'transform', 'aggregate', 'aggregator',
        'split', 'join',
        # Code execution nodes
        'python', 'code', 'function',
        # Integration nodes  
        'http', 'delay', 'retry',
        # Routing nodes
        'router',
        # Generic/passthrough nodes
        'action', 'passthrough'
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
        
        logger.info(f"Parsing workflow definition with keys: {list(data.keys())}")
        
        # Validate required fields
        if 'workflow_id' not in data and 'id' not in data:
            self.errors.append("Missing required field: workflow_id")
        if 'name' not in data:
            self.errors.append("Missing required field: name")
        if 'nodes' not in data:
            self.errors.append("Missing required field: nodes")
        
        if self.errors:
            return None
        
        # Build metadata dict
        metadata = data.get('metadata', {})
        if 'entry_point' in data:
            metadata['entry_point'] = data['entry_point']
        if 'output_node' in data:
            metadata['output_node'] = data['output_node']
        # Store the entire dag_definition for reference
        metadata['dag_definition'] = data
        
        # Create workflow
        # Try to get entry_point from multiple sources
        entry_point = data.get('entry_point')
        if not entry_point:
            # Try from dag_definition in metadata
            if metadata.get('dag_definition') and isinstance(metadata['dag_definition'], dict):
                entry_point = metadata['dag_definition'].get('entry_point')
                if entry_point:
                    logger.info(f"Recovered entry_point from metadata: {entry_point}")
        
        workflow = DAGWorkflow(
            workflow_id=data.get('workflow_id') or data.get('id'),
            name=data['name'],
            description=data.get('description', ''),
            version=data.get('version', '1.0.0'),
            entry_point=entry_point,
            input_schema=data.get('input_schema', {}),
            output_schema=data.get('output_schema', {}),
            python_modules=data.get('python_modules', {}),
            environment=data.get('environment', {}),
            metadata=metadata
        )
        
        # Parse nodes
        nodes_data = data.get('nodes', {})
        if isinstance(nodes_data, list):
            # Convert list format to dict format, filtering out nodes without valid IDs
            valid_nodes = {}
            for n in nodes_data:
                node_id = n.get('node_id') or n.get('id')
                if node_id:  # Only include nodes with valid IDs
                    valid_nodes[node_id] = n
                else:
                    logger.warning(f"Skipping node without ID: {n.get('name', 'unnamed')}")
            nodes_data = valid_nodes
        
        logger.info(f"Parsing {len(nodes_data)} nodes")
        
        for node_id, node_data in nodes_data.items():
            if not node_id:  # Skip None keys
                continue
            node = self._parse_node(node_id, node_data)
            if node:
                workflow.nodes[node_id] = node
        
        logger.info(f"Loaded {len(workflow.nodes)} nodes: {list(workflow.nodes.keys())}")
        
        # Parse edges - filter out invalid edges strictly
        raw_edges = data.get('edges', [])
        logger.info(f"Parsing {len(raw_edges)} edges from workflow definition")
        
        # Debug: log the type and content of raw_edges
        logger.info(f"raw_edges type: {type(raw_edges)}")
        if raw_edges:
            logger.info(f"First raw_edge type: {type(raw_edges[0])}, value: {raw_edges[0]}")
            # Check if edges might be nested
            if isinstance(raw_edges[0], dict) and 'edges' in raw_edges[0]:
                logger.warning(f"Edges appear to be nested! Extracting inner edges...")
                raw_edges = raw_edges[0].get('edges', [])
        else:
            # Try to recover edges from metadata if available
            logger.warning(f"No edges in main data, checking metadata...")
            if metadata.get('dag_definition') and isinstance(metadata['dag_definition'], dict):
                recovered_edges = metadata['dag_definition'].get('edges', [])
                if recovered_edges:
                    logger.info(f"Recovered {len(recovered_edges)} edges from metadata['dag_definition']")
                    raw_edges = recovered_edges
        
        valid_edges = []
        for i, edge in enumerate(raw_edges):
            # Log each edge for debugging (first 5)
            if i < 5:
                logger.info(f"Edge {i}: type={type(edge)}, content={edge}")
            
            # Handle case where edge might be a JSON string
            if isinstance(edge, str):
                logger.warning(f"Edge {i} is a string, attempting JSON parse: {edge[:100]}...")
                try:
                    edge = json.loads(edge)
                except json.JSONDecodeError:
                    logger.error(f"Edge {i} could not be parsed as JSON: {edge}")
                    continue
            
            if not isinstance(edge, dict):
                logger.warning(f"Edge {i} is not a dict: type={type(edge)}, value={edge}")
                continue
            
            # Handle BOTH edge formats:
            # Format 1 (template/JSON): {"source": "node1", "target": "node2"}
            # Format 2 (designer UI): {"from": "node1", "to": "node2", "fromPort": "output", "toPort": "input"}
            source = edge.get('source') or edge.get('from')
            target = edge.get('target') or edge.get('to')
            
            # Log the extracted source/target for first 5
            if i < 5:
                logger.info(f"Edge {i} extracted: source='{source}', target='{target}'")
            
            # Strictly require both source and target
            if not source or not target:
                logger.warning(f"Skipping edge {i}: source='{source}', target='{target}' - one or both are empty/None")
                continue
            
            # Add the edge
            valid_edge = {'source': source, 'target': target}
            if edge.get('condition'):
                valid_edge['condition'] = edge['condition']
            valid_edges.append(valid_edge)
            
            # Update dependencies based on edges
            if target in workflow.nodes:
                if source not in workflow.nodes[target].dependencies:
                    workflow.nodes[target].dependencies.append(source)
        
        workflow.edges = valid_edges
        logger.info(f"Loaded {len(valid_edges)} valid edges")
        
        # Log edge summary for debugging
        if valid_edges:
            edge_summary = [(e['source'], e['target'], e.get('condition', '')) for e in valid_edges[:5]]
            logger.info(f"First 5 edges: {edge_summary}")
        
        # Validate workflow
        validation_errors = workflow.validate()
        self.errors.extend(validation_errors)
        
        if self.errors:
            logger.warning(f"Workflow parsing completed with errors: {self.errors}")
        else:
            logger.info(f"Workflow parsed successfully")
        
        logger.info(f"Parsed workflow: {workflow.workflow_id}, {len(workflow.nodes)} nodes, {len(workflow.edges)} edges, entry_point={workflow.entry_point}")
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
