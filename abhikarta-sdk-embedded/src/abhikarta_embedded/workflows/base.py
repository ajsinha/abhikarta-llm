"""Base Workflow classes."""
from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from ..core import Abhikarta

class NodeType(Enum):
    INPUT = "input"
    OUTPUT = "output"
    LLM = "llm"
    CODE = "code"
    TRANSFORM = "transform"

@dataclass
class Node:
    id: str
    name: str
    node_type: NodeType
    config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "node_type": self.node_type.value, "config": self.config}

@dataclass
class Edge:
    source: str
    target: str
    condition: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {"source": self.source, "target": self.target, "condition": self.condition}

@dataclass
class WorkflowConfig:
    name: str
    description: str = ""
    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    timeout: int = 300

@dataclass
class WorkflowResult:
    success: bool
    output: Any
    node_results: List[Dict] = field(default_factory=list)
    execution_time: float = 0.0

class BaseWorkflow(ABC):
    def __init__(self, config: WorkflowConfig):
        self.id = str(uuid.uuid4())
        self.config = config
    
    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> WorkflowResult:
        pass

class DAGWorkflow(BaseWorkflow):
    def __init__(self, config: WorkflowConfig, provider=None):
        super().__init__(config)
        self.provider = provider
    
    def execute(self, input_data: Dict[str, Any]) -> WorkflowResult:
        import time
        start = time.time()
        # Simple sequential execution
        data = input_data
        for node in self.config.nodes:
            if node.node_type == NodeType.LLM and self.provider:
                prompt = node.config.get("prompt", "{input}").format(input=str(data))
                data = self.provider.chat([{"role": "user", "content": prompt}])
        return WorkflowResult(True, data, [], time.time() - start)

class Workflow:
    @classmethod
    def create(cls, name: str, nodes: List[Dict], edges: List[Dict], **kwargs) -> DAGWorkflow:
        node_objs = [Node(n["id"], n["name"], NodeType(n["node_type"]), n.get("config", {})) for n in nodes]
        edge_objs = [Edge(e["source"], e["target"], e.get("condition")) for e in edges]
        config = WorkflowConfig(name, nodes=node_objs, edges=edge_objs, **kwargs)
        return DAGWorkflow(config)

class WorkflowBuilder:
    def __init__(self, app: "Abhikarta", name: str):
        self._app = app
        self._name = name
        self._nodes: List[Node] = []
        self._edges: List[Edge] = []
    
    def node(self, node_id: str, name: str, node_type: str, **config) -> "WorkflowBuilder":
        self._nodes.append(Node(node_id, name, NodeType(node_type), config))
        return self
    
    def edge(self, source: str, target: str) -> "WorkflowBuilder":
        self._edges.append(Edge(source, target))
        return self
    
    def build(self) -> DAGWorkflow:
        config = WorkflowConfig(self._name, nodes=self._nodes, edges=self._edges)
        workflow = DAGWorkflow(config, self._app.get_provider())
        self._app._workflows[workflow.id] = workflow
        return workflow
