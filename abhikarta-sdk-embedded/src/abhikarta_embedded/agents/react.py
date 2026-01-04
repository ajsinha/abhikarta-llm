"""ReAct Agent - Reasoning and Acting."""
import re, json, time
from typing import Any, Dict
from .base import BaseAgent, AgentConfig, AgentResult

class ReActAgent(BaseAgent):
    DEFAULT_PROMPT = "You are a ReAct agent. Think step by step, then act."
    
    def __init__(self, config: AgentConfig, **kwargs):
        super().__init__(config, **kwargs)
        if not self.config.system_prompt:
            self.config.system_prompt = self.DEFAULT_PROMPT
    
    def run(self, prompt: str, **kwargs) -> AgentResult:
        start = time.time()
        messages = [{"role": "system", "content": self.config.system_prompt}, {"role": "user", "content": prompt}]
        for i in range(self.config.max_iterations):
            response = self._call_llm(messages)
            if "Final Answer:" in response:
                answer = response.split("Final Answer:")[-1].strip()
                return AgentResult(True, answer, i+1, [], time.time()-start)
            messages.append({"role": "assistant", "content": response})
            messages.append({"role": "user", "content": "Continue or provide Final Answer:"})
        return AgentResult(False, "Max iterations reached", self.config.max_iterations, [], time.time()-start)
