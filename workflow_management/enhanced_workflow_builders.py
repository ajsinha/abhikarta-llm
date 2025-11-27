"""
Enhanced Workflow Builders with JSON and Python Support

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha | Email: ajsinha@gmail.com

This module provides enhanced workflow builders that support both JSON
definitions and Python/LangGraph code for workflow creation.
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
import json
from langgraph.graph import StateGraph, END


@dataclass
class WorkflowNode:
    """Represents a node in the workflow"""
    node_id: str
    node_type: str
    name: str
    description: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    input_mappings: Dict[str, str] = field(default_factory=dict)
    output_mappings: Dict[str, str] = field(default_factory=dict)
    timeout: int = 300
    retry_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "name": self.name,
            "description": self.description,
            "config": self.config,
            "input_mappings": self.input_mappings,
            "output_mappings": self.output_mappings,
            "timeout": self.timeout,
            "retry_count": self.retry_count
        }


@dataclass
class WorkflowEdge:
    """Represents an edge between nodes"""
    source: str
    target: str
    condition: Optional[str] = None
    priority: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        edge_dict = {
            "source": self.source,
            "target": self.target,
            "priority": self.priority
        }
        if self.condition:
            edge_dict["condition"] = self.condition
        return edge_dict


class EnhancedWorkflowBuilder:
    """
    Enhanced builder class for creating workflows in both JSON and Python formats.

    This builder supports:
    - JSON-based workflow definitions
    - Python/LangGraph code generation
    - Hybrid approaches combining both
    """

    def __init__(self, name: str, description: str, version: str = "1.0.0",
                 workflow_type: str = "json"):
        """
        Initialize workflow builder.

        Args:
            name: Workflow name
            description: Workflow description
            version: Workflow version
            workflow_type: 'json' or 'python' or 'hybrid'
        """
        self.name = name
        self.description = description
        self.version = version
        self.workflow_type = workflow_type
        self.nodes: List[WorkflowNode] = []
        self.edges: List[WorkflowEdge] = []
        self.variables: Dict[str, Any] = {}
        self.python_code: Optional[str] = None

    def add_node(self, node: WorkflowNode) -> 'EnhancedWorkflowBuilder':
        """Add a node to the workflow"""
        self.nodes.append(node)
        return self

    def add_edge(self, edge: WorkflowEdge) -> 'EnhancedWorkflowBuilder':
        """Add an edge to the workflow"""
        self.edges.append(edge)
        return self

    def set_variable(self, key: str, value: Any) -> 'EnhancedWorkflowBuilder':
        """Set a workflow variable"""
        self.variables[key] = value
        return self

    def set_python_code(self, code: str) -> 'EnhancedWorkflowBuilder':
        """
        Set Python code for the workflow.

        Args:
            code: Python code that builds a LangGraph workflow
        """
        self.python_code = code
        self.workflow_type = "python"
        return self

    def build_json(self) -> Dict[str, Any]:
        """Build JSON workflow definition"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "workflow_type": "json",
            "definition": {
                "nodes": [node.to_dict() for node in self.nodes],
                "edges": [edge.to_dict() for edge in self.edges],
                "variables": self.variables
            }
        }

    def build_python(self) -> Dict[str, Any]:
        """Build Python workflow definition"""
        if self.python_code:
            # User-provided Python code
            return {
                "name": self.name,
                "description": self.description,
                "version": self.version,
                "workflow_type": "python",
                "definition": {
                    "python_code": self.python_code,
                    "variables": self.variables
                }
            }
        else:
            # Generate Python code from nodes/edges
            python_code = self._generate_python_code()
            return {
                "name": self.name,
                "description": self.description,
                "version": self.version,
                "workflow_type": "python",
                "definition": {
                    "python_code": python_code,
                    "variables": self.variables
                }
            }

    def build_hybrid(self) -> Dict[str, Any]:
        """Build hybrid workflow with both JSON and Python"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "workflow_type": "hybrid",
            "definition": {
                "json_definition": {
                    "nodes": [node.to_dict() for node in self.nodes],
                    "edges": [edge.to_dict() for edge in self.edges]
                },
                "python_code": self.python_code or self._generate_python_code(),
                "variables": self.variables
            }
        }

    def build(self) -> Dict[str, Any]:
        """Build workflow based on workflow_type"""
        if self.workflow_type == "json":
            return self.build_json()
        elif self.workflow_type == "python":
            return self.build_python()
        elif self.workflow_type == "hybrid":
            return self.build_hybrid()
        else:
            return self.build_json()

    def _generate_python_code(self) -> str:
        """Generate Python/LangGraph code from nodes and edges"""
        code_parts = []

        # Header
        code_parts.append("""
# Auto-generated LangGraph Workflow
from langgraph.graph import StateGraph, END
from typing import Dict, Any

# Initialize graph
graph = StateGraph(WorkflowState)
""")

        # Generate node functions
        for node in self.nodes:
            if node.node_type in ['start', 'end']:
                continue

            node_func = f"""
def {node.node_id}_func(state: WorkflowState) -> WorkflowState:
    \"\"\"Execute {node.name}\"\"\"
    node_func = _create_node_function(execution_id, {{
        'node_id': '{node.node_id}',
        'node_type': '{node.node_type}',
        'config': {json.dumps(node.config, indent=8)}
    }})
    return node_func(state)

graph.add_node("{node.node_id}", {node.node_id}_func)
"""
            code_parts.append(node_func)

        # Add start/end nodes
        code_parts.append("""
graph.add_node("start", lambda state: state)
graph.add_node("end", lambda state: {**state, "status": "completed"})
""")

        # Add edges
        code_parts.append("\n# Add edges\ngraph.set_entry_point('start')\n")
        for edge in self.edges:
            if edge.condition:
                code_parts.append(f"# Conditional edge from {edge.source} to {edge.target}\n")
                code_parts.append(f"# Condition: {edge.condition}\n")
            else:
                code_parts.append(f"graph.add_edge('{edge.source}', '{edge.target}')\n")

        # Compile graph
        code_parts.append("""
graph.add_edge('end', END)

# Compile the graph
compiled_graph = graph.compile()

# Initialize state
initial_state = WorkflowState(
    execution_id=execution_id,
    workflow_id='auto_generated',
    current_node='start',
    messages=[],
    variables={variables},
    node_outputs={{}},
    input_parameters=input_parameters,
    status='running',
    error=None,
    metadata={{}}
)
""".replace("{variables}", json.dumps(self.variables)))

        return "\n".join(code_parts)

    def to_json(self, indent: int = 2) -> str:
        """Convert workflow to JSON string"""
        return json.dumps(self.build(), indent=indent)

    def save_to_file(self, filename: str):
        """Save workflow to file"""
        with open(filename, 'w') as f:
            f.write(self.to_json())


class PythonWorkflowBuilder:
    """
    Builder specifically for Python/LangGraph workflows.

    This builder provides a more Pythonic API for creating workflows
    that will be executed as LangGraph code.
    """

    def __init__(self, name: str, description: str, version: str = "1.0.0"):
        self.name = name
        self.description = description
        self.version = version
        self.python_code_parts = []
        self.imports = set()
        self.variables = {}

    def add_import(self, import_statement: str) -> 'PythonWorkflowBuilder':
        """Add an import statement"""
        self.imports.add(import_statement)
        return self

    def add_code_block(self, code: str) -> 'PythonWorkflowBuilder':
        """Add a code block to the workflow"""
        self.python_code_parts.append(code)
        return self

    def set_variable(self, key: str, value: Any) -> 'PythonWorkflowBuilder':
        """Set a workflow variable"""
        self.variables[key] = value
        return self

    def build(self) -> Dict[str, Any]:
        """Build the Python workflow definition"""
        # Combine imports and code
        imports_str = "\n".join(sorted(self.imports))
        code_str = "\n\n".join(self.python_code_parts)

        full_code = f"{imports_str}\n\n{code_str}"

        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "workflow_type": "python",
            "definition": {
                "python_code": full_code,
                "variables": self.variables
            }
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.build(), indent=indent)


# =============================================================================
# BUILDER HELPER FUNCTIONS
# =============================================================================

def create_start_node() -> WorkflowNode:
    """Create a start node"""
    return WorkflowNode(
        node_id="start",
        node_type="start",
        name="Start",
        description="Workflow entry point"
    )


def create_end_node(node_id: str = "end") -> WorkflowNode:
    """Create an end node"""
    return WorkflowNode(
        node_id=node_id,
        node_type="end",
        name="End",
        description="Workflow completion"
    )


def create_llm_node(node_id: str, name: str, prompt: str,
                    model: str = "claude-3-sonnet") -> WorkflowNode:
    """Create an LLM node"""
    return WorkflowNode(
        node_id=node_id,
        node_type="llm",
        name=name,
        config={
            "prompt": prompt,
            "model": model
        }
    )


def create_tool_node(node_id: str, name: str, tool_name: str,
                     parameters: Dict[str, Any]) -> WorkflowNode:
    """Create a tool execution node"""
    return WorkflowNode(
        node_id=node_id,
        node_type="tool",
        name=name,
        config={
            "tool_name": tool_name,
            "parameters": parameters
        }
    )


def create_human_node(node_id: str, name: str, assigned_to: str,
                      task_type: str = "approval", timeout: int = 3600,
                      instructions: str = "") -> WorkflowNode:
    """Create a human-in-the-loop node"""
    return WorkflowNode(
        node_id=node_id,
        node_type="human",
        name=name,
        config={
            "assigned_to": assigned_to,
            "task_type": task_type,
            "timeout": timeout,
            "instructions": instructions
        }
    )


def create_conditional_node(node_id: str, name: str,
                            condition: str) -> WorkflowNode:
    """Create a conditional node"""
    return WorkflowNode(
        node_id=node_id,
        node_type="conditional",
        name=name,
        config={
            "condition": condition
        }
    )


def create_parallel_node(node_id: str, name: str,
                         strategy: str = "all",
                         max_concurrent: int = 10) -> WorkflowNode:
    """Create a parallel execution node"""
    return WorkflowNode(
        node_id=node_id,
        node_type="parallel",
        name=name,
        config={
            "strategy": strategy,
            "max_concurrent": max_concurrent
        }
    )


# =============================================================================
# QUICK BUILD FUNCTIONS
# =============================================================================

def quick_sequential_workflow(name: str, tool_configs: List[Dict[str, Any]]) -> EnhancedWorkflowBuilder:
    """
    Quickly build a sequential workflow from tool configurations.

    Args:
        name: Workflow name
        tool_configs: List of tool configurations, each with 'tool_name' and 'parameters'

    Returns:
        Configured workflow builder
    """
    builder = EnhancedWorkflowBuilder(name, f"Sequential workflow: {name}")

    builder.add_node(create_start_node())

    prev_node = "start"
    for i, config in enumerate(tool_configs):
        node_id = f"step_{i + 1}"
        node = create_tool_node(
            node_id=node_id,
            name=config.get('name', f'Step {i + 1}'),
            tool_name=config['tool_name'],
            parameters=config['parameters']
        )
        builder.add_node(node)
        builder.add_edge(WorkflowEdge(prev_node, node_id))
        prev_node = node_id

    builder.add_node(create_end_node())
    builder.add_edge(WorkflowEdge(prev_node, "end"))

    return builder


def quick_parallel_workflow(name: str, parallel_branches: List[Dict[str, Any]]) -> EnhancedWorkflowBuilder:
    """
    Quickly build a parallel workflow from branch configurations.

    Args:
        name: Workflow name
        parallel_branches: List of branch configurations

    Returns:
        Configured workflow builder
    """
    builder = EnhancedWorkflowBuilder(name, f"Parallel workflow: {name}")

    builder.add_node(create_start_node())
    builder.add_node(create_parallel_node("parallel_split", "Parallel Split"))
    builder.add_edge(WorkflowEdge("start", "parallel_split"))

    branch_nodes = []
    for i, branch in enumerate(parallel_branches):
        node_id = f"branch_{i + 1}"
        node = create_tool_node(
            node_id=node_id,
            name=branch.get('name', f'Branch {i + 1}'),
            tool_name=branch['tool_name'],
            parameters=branch['parameters']
        )
        builder.add_node(node)
        builder.add_edge(WorkflowEdge("parallel_split", node_id, priority=i + 1))
        branch_nodes.append(node_id)

    builder.add_node(create_parallel_node("parallel_join", "Parallel Join"))
    for node_id in branch_nodes:
        builder.add_edge(WorkflowEdge(node_id, "parallel_join"))

    builder.add_node(create_end_node())
    builder.add_edge(WorkflowEdge("parallel_join", "end"))

    return builder


# Export all classes and functions
__all__ = [
    'EnhancedWorkflowBuilder',
    'PythonWorkflowBuilder',
    'WorkflowNode',
    'WorkflowEdge',
    'create_start_node',
    'create_end_node',
    'create_llm_node',
    'create_tool_node',
    'create_human_node',
    'create_conditional_node',
    'create_parallel_node',
    'quick_sequential_workflow',
    'quick_parallel_workflow'
]