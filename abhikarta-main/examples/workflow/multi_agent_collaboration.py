#!/usr/bin/env python3
"""
Multi-Agent Collaboration System Example

This example demonstrates a sophisticated multi-agent system where specialized 
agents collaborate on complex tasks:

1. Coordinator Agent - Orchestrates the workflow
2. Research Agent - Gathers information
3. Analysis Agent - Analyzes data and identifies patterns
4. Writer Agent - Creates content
5. Critic Agent - Reviews and provides feedback

The agents communicate through a structured message protocol and work together
to produce high-quality outputs through iterative refinement.

Usage:
    python multi_agent_collaboration.py "Your complex task here"
    python multi_agent_collaboration.py --interactive

Copyright © 2025-2030 Abhikarta. All Rights Reserved.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Roles that agents can have."""
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    WRITER = "writer"
    CRITIC = "critic"


@dataclass
class AgentMessage:
    """Message passed between agents."""
    sender: str
    recipient: str
    message_type: str  # task, result, feedback, question
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass 
class AgentResult:
    """Result from an agent's work."""
    agent_id: str
    phase: str
    output: str
    confidence: float = 0.8
    suggestions: List[str] = field(default_factory=list)
    duration_ms: int = 0


class BaseAgent:
    """Base class for all agents."""
    
    def __init__(self, agent_id: str, name: str, role: AgentRole, llm_config: Dict[str, Any]):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.llm_config = llm_config
        self.llm = None
        self.message_history: List[AgentMessage] = []
        
    def _create_llm(self):
        """Create LLM instance."""
        if self.llm is not None:
            return self.llm
        try:
            from langchain_ollama import ChatOllama
            self.llm = ChatOllama(
                model=self.llm_config.get("model", "llama3.2:3b"),
                base_url=self.llm_config.get("base_url", "http://localhost:11434"),
                temperature=self.llm_config.get("temperature", 0.7)
            )
            return self.llm
        except ImportError:
            raise ImportError("langchain-ollama required")
    
    def _invoke(self, prompt: str) -> str:
        """Invoke the LLM."""
        llm = self._create_llm()
        response = llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    def receive_message(self, message: AgentMessage):
        """Receive a message from another agent."""
        self.message_history.append(message)
        logger.debug(f"[{self.name}] Received message from {message.sender}: {message.message_type}")
    
    def send_message(self, recipient: str, message_type: str, content: str, metadata: Dict = None) -> AgentMessage:
        """Send a message to another agent."""
        msg = AgentMessage(
            sender=self.agent_id,
            recipient=recipient,
            message_type=message_type,
            content=content,
            metadata=metadata or {}
        )
        logger.debug(f"[{self.name}] Sending {message_type} to {recipient}")
        return msg
    
    def execute(self, task: str, context: Dict[str, Any] = None) -> AgentResult:
        """Execute the agent's task. Override in subclasses."""
        raise NotImplementedError


class CoordinatorAgent(BaseAgent):
    """Coordinator agent that orchestrates the workflow."""
    
    def __init__(self, llm_config: Dict[str, Any]):
        super().__init__("coordinator", "Coordinator Agent", AgentRole.COORDINATOR, llm_config)
        self.system_prompt = """You are the Coordinator Agent responsible for orchestrating multi-agent collaboration.

Your responsibilities:
1. Analyze incoming tasks and break them into subtasks
2. Delegate work to specialized agents
3. Synthesize results from all agents
4. Ensure quality and consistency
5. Make final decisions

When analyzing a task, provide:
- Task decomposition (subtasks for each agent)
- Execution order
- Dependencies between subtasks
- Success criteria"""

    def analyze_task(self, task: str) -> Dict[str, Any]:
        """Analyze task and create execution plan."""
        prompt = f"""{self.system_prompt}

TASK: {task}

Create a detailed execution plan in JSON format:
{{
    "task_summary": "brief summary",
    "subtasks": [
        {{"agent": "researcher", "task": "specific research task", "priority": 1}},
        {{"agent": "analyst", "task": "specific analysis task", "priority": 2}},
        {{"agent": "writer", "task": "specific writing task", "priority": 3}},
        {{"agent": "critic", "task": "specific review task", "priority": 4}}
    ],
    "success_criteria": ["criterion 1", "criterion 2"],
    "expected_output_format": "description"
}}"""
        
        response = self._invoke(prompt)
        return {"plan": response, "original_task": task}
    
    def synthesize_results(self, results: Dict[str, AgentResult], original_task: str) -> str:
        """Synthesize all agent results into final output."""
        results_summary = "\n\n".join([
            f"=== {agent.upper()} RESULT ===\n{result.output}"
            for agent, result in results.items()
        ])
        
        prompt = f"""{self.system_prompt}

ORIGINAL TASK: {original_task}

AGENT RESULTS:
{results_summary}

Synthesize all agent contributions into a comprehensive, cohesive final output.
Ensure:
1. All relevant findings are included
2. Analysis insights are integrated
3. Writing is polished and professional
4. Critic feedback has been addressed
5. Output is well-structured and actionable"""
        
        return self._invoke(prompt)
    
    def execute(self, task: str, context: Dict[str, Any] = None) -> AgentResult:
        """Execute coordinator tasks."""
        import time
        start = time.time()
        
        if context and context.get("phase") == "synthesis":
            output = self.synthesize_results(context.get("results", {}), task)
        else:
            analysis = self.analyze_task(task)
            output = analysis["plan"]
        
        return AgentResult(
            agent_id=self.agent_id,
            phase=context.get("phase", "planning") if context else "planning",
            output=output,
            duration_ms=int((time.time() - start) * 1000)
        )


class ResearchAgent(BaseAgent):
    """Research agent that gathers information."""
    
    def __init__(self, llm_config: Dict[str, Any]):
        super().__init__("researcher", "Research Agent", AgentRole.RESEARCHER, llm_config)
        self.system_prompt = """You are a Research Agent specialized in gathering and synthesizing information.

Your responsibilities:
1. Identify key research questions
2. Gather relevant information
3. Verify facts and cross-reference sources
4. Organize findings clearly
5. Highlight knowledge gaps

Output format:
- Key Research Questions
- Findings (organized by topic)
- Sources/References
- Confidence Level
- Areas Needing Further Research"""

    def execute(self, task: str, context: Dict[str, Any] = None) -> AgentResult:
        """Execute research task."""
        import time
        start = time.time()
        
        prompt = f"""{self.system_prompt}

RESEARCH TASK: {task}

Additional Context: {json.dumps(context) if context else 'None'}

Conduct thorough research and provide structured findings."""
        
        output = self._invoke(prompt)
        
        return AgentResult(
            agent_id=self.agent_id,
            phase="research",
            output=output,
            duration_ms=int((time.time() - start) * 1000)
        )


class AnalysisAgent(BaseAgent):
    """Analysis agent that identifies patterns and insights."""
    
    def __init__(self, llm_config: Dict[str, Any]):
        super().__init__("analyst", "Analysis Agent", AgentRole.ANALYST, llm_config)
        self.system_prompt = """You are an Analysis Agent specialized in data analysis and pattern recognition.

Your responsibilities:
1. Analyze provided information
2. Identify patterns and trends
3. Draw logical conclusions
4. Quantify findings where possible
5. Highlight correlations and causations

Output format:
- Key Patterns Identified
- Statistical Insights
- Correlations
- Conclusions
- Recommendations"""

    def execute(self, task: str, context: Dict[str, Any] = None) -> AgentResult:
        """Execute analysis task."""
        import time
        start = time.time()
        
        research_data = context.get("research_output", "") if context else ""
        
        prompt = f"""{self.system_prompt}

ANALYSIS TASK: {task}

RESEARCH DATA TO ANALYZE:
{research_data}

Provide detailed analysis with insights and patterns."""
        
        output = self._invoke(prompt)
        
        return AgentResult(
            agent_id=self.agent_id,
            phase="analysis",
            output=output,
            duration_ms=int((time.time() - start) * 1000)
        )


class WriterAgent(BaseAgent):
    """Writer agent that creates content."""
    
    def __init__(self, llm_config: Dict[str, Any]):
        super().__init__("writer", "Writer Agent", AgentRole.WRITER, llm_config)
        self.system_prompt = """You are a Writer Agent specialized in creating clear, compelling content.

Your responsibilities:
1. Transform research and analysis into readable content
2. Structure information logically
3. Use clear, professional language
4. Create engaging narratives
5. Ensure completeness and accuracy

Output format:
- Well-structured document with clear sections
- Executive summary
- Detailed content
- Conclusions and recommendations"""

    def execute(self, task: str, context: Dict[str, Any] = None) -> AgentResult:
        """Execute writing task."""
        import time
        start = time.time()
        
        research = context.get("research_output", "") if context else ""
        analysis = context.get("analysis_output", "") if context else ""
        feedback = context.get("critic_feedback", "") if context else ""
        
        prompt = f"""{self.system_prompt}

WRITING TASK: {task}

RESEARCH FINDINGS:
{research[:2000]}

ANALYSIS INSIGHTS:
{analysis[:2000]}

{"CRITIC FEEDBACK TO ADDRESS:" + feedback if feedback else ""}

Create a comprehensive, well-written document."""
        
        output = self._invoke(prompt)
        
        return AgentResult(
            agent_id=self.agent_id,
            phase="writing",
            output=output,
            duration_ms=int((time.time() - start) * 1000)
        )


class CriticAgent(BaseAgent):
    """Critic agent that reviews and provides feedback."""
    
    def __init__(self, llm_config: Dict[str, Any]):
        super().__init__("critic", "Critic Agent", AgentRole.CRITIC, llm_config)
        self.system_prompt = """You are a Critic Agent specialized in quality review and feedback.

Your responsibilities:
1. Review content for quality and accuracy
2. Identify strengths and weaknesses
3. Provide constructive feedback
4. Suggest specific improvements
5. Rate overall quality

Output format:
- Quality Score (1-10)
- Strengths
- Areas for Improvement
- Specific Suggestions
- Final Verdict (APPROVED/NEEDS_REVISION)"""

    def execute(self, task: str, context: Dict[str, Any] = None) -> AgentResult:
        """Execute review task."""
        import time
        start = time.time()
        
        content_to_review = context.get("writer_output", "") if context else ""
        
        prompt = f"""{self.system_prompt}

REVIEW TASK: {task}

CONTENT TO REVIEW:
{content_to_review}

Provide detailed critique and feedback."""
        
        output = self._invoke(prompt)
        
        # Check if revision needed
        needs_revision = "NEEDS_REVISION" in output.upper()
        
        return AgentResult(
            agent_id=self.agent_id,
            phase="review",
            output=output,
            suggestions=["Revision needed"] if needs_revision else [],
            duration_ms=int((time.time() - start) * 1000)
        )


class MultiAgentSystem:
    """Orchestrates multi-agent collaboration."""
    
    def __init__(self, llm_config: Dict[str, Any] = None):
        self.llm_config = llm_config or {
            "provider": "ollama",
            "model": "llama3.2:3b",
            "base_url": os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
            "temperature": 0.7
        }
        
        # Initialize agents
        self.coordinator = CoordinatorAgent(self.llm_config)
        self.researcher = ResearchAgent(self.llm_config)
        self.analyst = AnalysisAgent(self.llm_config)
        self.writer = WriterAgent(self.llm_config)
        self.critic = CriticAgent(self.llm_config)
        
        self.results: Dict[str, AgentResult] = {}
        self.max_iterations = 3
    
    def execute(self, task: str) -> Dict[str, Any]:
        """Execute multi-agent collaboration on a task."""
        logger.info("=" * 70)
        logger.info("MULTI-AGENT COLLABORATION SYSTEM")
        logger.info("=" * 70)
        logger.info(f"Task: {task[:100]}...")
        
        start_time = datetime.now(timezone.utc)
        
        # Phase 1: Coordinator analyzes task
        logger.info("\n[Phase 1] Coordinator analyzing task...")
        coord_result = self.coordinator.execute(task)
        self.results["coordinator_plan"] = coord_result
        logger.info("Task analysis complete")
        
        # Phase 2: Research
        logger.info("\n[Phase 2] Research Agent gathering information...")
        research_result = self.researcher.execute(task)
        self.results["researcher"] = research_result
        logger.info("Research complete")
        
        # Phase 3: Analysis
        logger.info("\n[Phase 3] Analysis Agent analyzing findings...")
        analysis_result = self.analyst.execute(task, {"research_output": research_result.output})
        self.results["analyst"] = analysis_result
        logger.info("Analysis complete")
        
        # Phase 4: Writing (with potential iteration)
        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1
            logger.info(f"\n[Phase 4.{iteration}] Writer Agent creating content...")
            
            writer_context = {
                "research_output": research_result.output,
                "analysis_output": analysis_result.output,
                "critic_feedback": self.results.get("critic", AgentResult("", "", "")).output if iteration > 1 else ""
            }
            writer_result = self.writer.execute(task, writer_context)
            self.results["writer"] = writer_result
            logger.info("Writing complete")
            
            # Phase 5: Review
            logger.info(f"\n[Phase 5.{iteration}] Critic Agent reviewing content...")
            critic_result = self.critic.execute(task, {"writer_output": writer_result.output})
            self.results["critic"] = critic_result
            logger.info("Review complete")
            
            # Check if approved
            if "APPROVED" in critic_result.output.upper() or not critic_result.suggestions:
                logger.info("Content approved by critic")
                break
            elif iteration < self.max_iterations:
                logger.info("Content needs revision, iterating...")
        
        # Phase 6: Final synthesis
        logger.info("\n[Phase 6] Coordinator synthesizing final output...")
        final_result = self.coordinator.execute(task, {
            "phase": "synthesis",
            "results": self.results
        })
        self.results["final"] = final_result
        
        end_time = datetime.now(timezone.utc)
        
        # Compile output
        output = {
            "task": task,
            "final_output": final_result.output,
            "agent_contributions": {
                agent_id: {
                    "phase": result.phase,
                    "output_preview": result.output[:500] + "..." if len(result.output) > 500 else result.output,
                    "duration_ms": result.duration_ms
                }
                for agent_id, result in self.results.items()
            },
            "metadata": {
                "total_duration_seconds": (end_time - start_time).total_seconds(),
                "iterations": iteration,
                "agents_used": list(self.results.keys()),
                "completed_at": end_time.isoformat()
            }
        }
        
        logger.info("\n" + "=" * 70)
        logger.info("COLLABORATION COMPLETE")
        logger.info(f"Total time: {output['metadata']['total_duration_seconds']:.2f}s")
        logger.info(f"Iterations: {output['metadata']['iterations']}")
        logger.info("=" * 70)
        
        return output


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Multi-Agent Collaboration System')
    parser.add_argument('task', nargs='?', help='Task for agents to work on')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--model', default='llama3.2:3b', help='Ollama model')
    parser.add_argument('--base-url', default='http://localhost:11434', help='Ollama URL')
    
    args = parser.parse_args()
    
    llm_config = {
        "provider": "ollama",
        "model": args.model,
        "base_url": args.base_url,
        "temperature": 0.7
    }
    
    system = MultiAgentSystem(llm_config)
    
    if args.interactive:
        print("\nMulti-Agent Collaboration System")
        print("=" * 40)
        print("Enter your task (or 'quit' to exit):\n")
        
        while True:
            task = input("> ").strip()
            if task.lower() in ['quit', 'exit', 'q']:
                break
            if task:
                result = system.execute(task)
                print("\n" + "=" * 40)
                print("FINAL OUTPUT")
                print("=" * 40)
                print(result['final_output'])
                print()
    else:
        task = args.task or "Analyze the current trends in artificial intelligence and provide strategic recommendations for organizations looking to adopt AI technologies."
        
        result = system.execute(task)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            logger.info(f"Results saved to: {args.output}")
        else:
            print("\n" + "=" * 70)
            print("FINAL OUTPUT")
            print("=" * 70)
            print(result['final_output'])


if __name__ == "__main__":
    main()
