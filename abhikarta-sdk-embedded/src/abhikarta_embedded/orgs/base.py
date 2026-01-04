"""Base Organization classes."""
from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from ..core import Abhikarta

@dataclass
class OrgNode:
    node_id: str
    role_name: str
    role_type: str  # executive, manager, specialist
    description: str = ""
    parent_node_id: Optional[str] = None

@dataclass
class OrgTask:
    task_id: str
    title: str
    description: str
    status: str = "pending"
    result: Optional[str] = None

@dataclass
class OrgConfig:
    name: str
    nodes: List[OrgNode] = field(default_factory=list)
    root_node_id: Optional[str] = None

@dataclass
class OrgResult:
    success: bool
    response: str
    task_results: List[Dict] = field(default_factory=list)

class BaseOrganization(ABC):
    def __init__(self, config: OrgConfig):
        self.id = str(uuid.uuid4())
        self.config = config
    
    @abstractmethod
    def submit_task(self, title: str, description: str, **kwargs) -> OrgResult:
        pass

class Organization(BaseOrganization):
    def __init__(self, config: OrgConfig, provider=None):
        super().__init__(config)
        self.provider = provider
    
    def submit_task(self, title: str, description: str, **kwargs) -> OrgResult:
        if not self.provider:
            return OrgResult(False, "No provider configured", [])
        # Route through hierarchy
        results = []
        for node in self.config.nodes:
            prompt = f"You are {node.role_name} ({node.role_type}). Task: {title}\nDescription: {description}"
            result = self.provider.chat([{"role": "user", "content": prompt}])
            results.append({"node": node.role_name, "result": result})
        final = results[-1]["result"] if results else "No nodes"
        return OrgResult(True, final, results)
    
    @classmethod
    def create(cls, name: str, nodes: List[Dict], root_node_id: str = None, **kwargs) -> "Organization":
        node_objs = [OrgNode(n["node_id"], n["role_name"], n["role_type"], n.get("description", ""), n.get("parent_node_id")) for n in nodes]
        return cls(OrgConfig(name, node_objs, root_node_id))

class OrganizationBuilder:
    def __init__(self, app: "Abhikarta", name: str):
        self._app = app
        self._name = name
        self._nodes: List[OrgNode] = []
        self._root_node_id = None
    
    def node(self, node_id: str, role_name: str, role_type: str, parent_id: str = None, **kwargs) -> "OrganizationBuilder":
        self._nodes.append(OrgNode(node_id, role_name, role_type, kwargs.get("description", ""), parent_id))
        return self
    
    def root(self, node_id: str) -> "OrganizationBuilder":
        self._root_node_id = node_id
        return self
    
    def build(self) -> Organization:
        config = OrgConfig(self._name, self._nodes, self._root_node_id)
        org = Organization(config, self._app.get_provider())
        self._app._organizations[org.id] = org
        return org
