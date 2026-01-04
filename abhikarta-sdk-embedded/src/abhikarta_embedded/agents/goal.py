"""Goal Agent - Goal-oriented planning."""
import time
from .base import BaseAgent, AgentConfig, AgentResult

class GoalAgent(BaseAgent):
    def __init__(self, config: AgentConfig, **kwargs):
        super().__init__(config, **kwargs)
        if not self.config.system_prompt:
            self.config.system_prompt = "You are a goal-oriented agent. Create plans and execute them."
    
    def run(self, prompt: str, **kwargs) -> AgentResult:
        start = time.time()
        messages = [{"role": "system", "content": self.config.system_prompt},
                    {"role": "user", "content": f"Goal: {prompt}\nCreate a plan and execute it."}]
        response = self._call_llm(messages)
        return AgentResult(True, response, 1, [], time.time()-start)
