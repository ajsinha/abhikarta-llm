"""Hierarchical Agent - Task decomposition."""
import time
from .base import BaseAgent, AgentConfig, AgentResult

class HierarchicalAgent(BaseAgent):
    def __init__(self, config: AgentConfig, **kwargs):
        super().__init__(config, **kwargs)
        if not self.config.system_prompt:
            self.config.system_prompt = "You are a hierarchical task orchestrator. Break down complex tasks."
    
    def run(self, prompt: str, **kwargs) -> AgentResult:
        start = time.time()
        messages = [{"role": "system", "content": self.config.system_prompt},
                    {"role": "user", "content": f"Task: {prompt}\nBreak this down into subtasks, execute them, and synthesize results."}]
        response = self._call_llm(messages)
        return AgentResult(True, response, 1, [], time.time()-start)
