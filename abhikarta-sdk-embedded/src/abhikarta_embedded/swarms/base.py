"""Base Swarm classes."""
from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from ..core import Abhikarta

@dataclass
class SwarmAgent:
    agent_id: str
    role: str
    name: str
    config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SwarmConfig:
    name: str
    strategy: str = "collaborative"
    agents: List[SwarmAgent] = field(default_factory=list)

@dataclass
class SwarmResult:
    success: bool
    response: str
    agent_results: List[Dict] = field(default_factory=list)
    execution_time: float = 0.0

class BaseSwarm(ABC):
    def __init__(self, config: SwarmConfig):
        self.id = str(uuid.uuid4())
        self.config = config
    
    @abstractmethod
    def execute(self, task: str, **kwargs) -> SwarmResult:
        pass

class Swarm(BaseSwarm):
    def __init__(self, config: SwarmConfig, provider=None):
        super().__init__(config)
        self.provider = provider
    
    def execute(self, task: str, **kwargs) -> SwarmResult:
        import time
        start = time.time()
        results = []
        for agent in self.config.agents:
            if self.provider:
                prompt = f"You are {agent.name} ({agent.role}). Task: {task}"
                result = self.provider.chat([{"role": "user", "content": prompt}])
                results.append({"agent": agent.name, "result": result})
        final = "\n".join([f"{r['agent']}: {r['result'][:200]}" for r in results])
        return SwarmResult(True, final, results, time.time() - start)
    
    @classmethod
    def create(cls, name: str, agents: List[Dict], strategy: str = "collaborative", **kwargs) -> "Swarm":
        agent_objs = [SwarmAgent(a.get("id", str(uuid.uuid4())[:8]), a["role"], a["name"], a.get("config", {})) for a in agents]
        return cls(SwarmConfig(name, strategy, agent_objs))

class SwarmBuilder:
    def __init__(self, app: "Abhikarta", name: str):
        self._app = app
        self._name = name
        self._agents: List[SwarmAgent] = []
        self._strategy = "collaborative"
    
    def agent(self, role: str, name: str, **config) -> "SwarmBuilder":
        self._agents.append(SwarmAgent(str(uuid.uuid4())[:8], role, name, config))
        return self
    
    def strategy(self, strategy: str) -> "SwarmBuilder":
        self._strategy = strategy
        return self
    
    def build(self) -> Swarm:
        config = SwarmConfig(self._name, self._strategy, self._agents)
        swarm = Swarm(config, self._app.get_provider())
        self._app._swarms[swarm.id] = swarm
        return swarm
