"""Base Agent classes."""
from __future__ import annotations
import uuid, time, logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from ..core import Abhikarta
    from ..providers import BaseProvider

logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    name: str
    agent_type: str = "react"
    model: str = "llama3.2:3b"
    provider: str = "ollama"
    system_prompt: str = ""
    temperature: float = 0.7
    max_tokens: int = 2048
    tools: List[str] = field(default_factory=list)
    max_iterations: int = 10
    timeout: int = 300
    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "agent_type": self.agent_type, "model": self.model,
                "provider": self.provider, "system_prompt": self.system_prompt}

@dataclass
class AgentResult:
    success: bool
    response: str
    iterations: int = 0
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    execution_time: float = 0.0
    def to_dict(self) -> Dict[str, Any]:
        return {"success": self.success, "response": self.response, "iterations": self.iterations}

class BaseAgent(ABC):
    def __init__(self, config: AgentConfig, provider: Optional["BaseProvider"] = None):
        self.id = str(uuid.uuid4())
        self.config = config
        self.provider = provider
        self.tools = []
    
    @property
    def name(self) -> str:
        return self.config.name
    
    @abstractmethod
    def run(self, prompt: str, **kwargs) -> AgentResult:
        pass
    
    def __call__(self, prompt: str, **kwargs) -> AgentResult:
        return self.run(prompt, **kwargs)
    
    def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        if not self.provider:
            raise ValueError("No provider configured")
        return self.provider.chat(messages, self.config.model, self.config.temperature, self.config.max_tokens)

class Agent:
    """Factory for creating agents."""
    @classmethod
    def create(cls, agent_type: str = "react", name: Optional[str] = None, model: str = "llama3.2:3b",
               provider: str = "ollama", system_prompt: str = "", **kwargs) -> BaseAgent:
        from .react import ReActAgent
        from .goal import GoalAgent
        from .reflect import ReflectAgent
        from .hierarchical import HierarchicalAgent
        registry = {"react": ReActAgent, "goal": GoalAgent, "reflect": ReflectAgent, "hierarchical": HierarchicalAgent}
        if agent_type not in registry:
            raise ValueError(f"Unknown agent type: {agent_type}")
        config = AgentConfig(name=name or f"{agent_type.title()}Agent-{uuid.uuid4().hex[:6]}",
            agent_type=agent_type, model=model, provider=provider, system_prompt=system_prompt, **kwargs)
        return registry[agent_type](config)

class AgentBuilder:
    def __init__(self, app: "Abhikarta", name: str):
        self._app = app
        self._name = name
        self._type = "react"
        self._model = app.config.default_model
        self._provider = app.config.default_provider
        self._system_prompt = ""
        self._tools: List[str] = []
        self._temperature = 0.7
    
    def type(self, agent_type: str) -> "AgentBuilder":
        self._type = agent_type
        return self
    
    def model(self, model: str) -> "AgentBuilder":
        if "/" in model:
            self._provider, self._model = model.split("/", 1)
        else:
            self._model = model
        return self
    
    def system_prompt(self, prompt: str) -> "AgentBuilder":
        self._system_prompt = prompt
        return self
    
    def tool(self, tool_name: str) -> "AgentBuilder":
        self._tools.append(tool_name)
        return self
    
    def temperature(self, temp: float) -> "AgentBuilder":
        self._temperature = temp
        return self
    
    def build(self) -> BaseAgent:
        config = AgentConfig(name=self._name, agent_type=self._type, model=self._model,
            provider=self._provider, system_prompt=self._system_prompt, tools=self._tools, temperature=self._temperature)
        agent = Agent.create(self._type, **config.__dict__)
        agent.provider = self._app.get_provider(self._provider)
        self._app._agents[agent.id] = agent
        return agent
