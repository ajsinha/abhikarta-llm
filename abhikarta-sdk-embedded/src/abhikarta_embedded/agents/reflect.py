"""Reflect Agent - Self-reflecting quality improvement."""
import time
from .base import BaseAgent, AgentConfig, AgentResult

class ReflectAgent(BaseAgent):
    def __init__(self, config: AgentConfig, **kwargs):
        super().__init__(config, **kwargs)
        if not self.config.system_prompt:
            self.config.system_prompt = "You are a self-reflecting agent. Generate, evaluate, and improve your responses."
    
    def run(self, prompt: str, **kwargs) -> AgentResult:
        start = time.time()
        # Generate initial response
        messages = [{"role": "system", "content": self.config.system_prompt}, {"role": "user", "content": prompt}]
        response = self._call_llm(messages)
        # Reflect and improve
        messages.append({"role": "assistant", "content": response})
        messages.append({"role": "user", "content": "Evaluate and improve your response."})
        improved = self._call_llm(messages)
        return AgentResult(True, improved, 2, [], time.time()-start)
