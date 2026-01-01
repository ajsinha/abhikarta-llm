#!/usr/bin/env python3
"""
Decision Support System Agent Example

An analytical agent that helps users make better decisions through:
1. Problem structuring and definition
2. Option generation and evaluation
3. Criteria weighting and trade-off analysis
4. Bias detection and mitigation
5. Risk assessment and recommendation

Usage:
    python decision_support_system.py --interactive
    python decision_support_system.py "Should I accept the job offer?"

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

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DecisionPhase(Enum):
    """Phases of decision support process."""
    PROBLEM_DEFINITION = "problem_definition"
    OPTION_GENERATION = "option_generation"
    CRITERIA_DEVELOPMENT = "criteria_development"
    EVALUATION = "evaluation"
    BIAS_CHECK = "bias_check"
    RECOMMENDATION = "recommendation"


@dataclass
class DecisionOption:
    """Represents a decision option."""
    name: str
    description: str = ""
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    risk_level: str = "medium"
    scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class DecisionCriteria:
    """Represents evaluation criteria."""
    name: str
    weight: float = 1.0
    description: str = ""
    must_have: bool = False


@dataclass
class DecisionAnalysis:
    """Complete decision analysis."""
    problem_statement: str = ""
    options: List[DecisionOption] = field(default_factory=list)
    criteria: List[DecisionCriteria] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    stakeholders: List[str] = field(default_factory=list)
    timeline: str = ""
    biases_identified: List[str] = field(default_factory=list)
    recommendation: str = ""


class DecisionSupportSystem:
    """Decision support system agent implementation."""
    
    SYSTEM_PROMPT = """You are a Decision Support System that helps users make well-informed decisions.

CORE PRINCIPLES:

1. NEVER DECIDE FOR THE USER
   - Present balanced analysis
   - Highlight trade-offs
   - Empower informed choice

2. STRUCTURED ANALYSIS
   - Follow decision-making framework
   - Be systematic and thorough
   - Document assumptions

3. BIAS AWARENESS
   - Identify potential biases
   - Present counter-arguments
   - Challenge assumptions

4. UNCERTAINTY ACKNOWLEDGMENT
   - Note what's unknown
   - Quantify confidence where possible
   - Present scenarios

DECISION FRAMEWORK:

Phase 1: PROBLEM DEFINITION
- What exactly needs deciding?
- What are the constraints?
- Who are the stakeholders?
- What's the timeline?
- What are the success criteria?

Phase 2: OPTION GENERATION
- List all possible options
- Include 'do nothing' option
- Consider creative alternatives
- Identify hybrid options

Phase 3: CRITERIA DEVELOPMENT
- What factors matter?
- Must-haves vs. nice-to-haves
- Weight by importance
- Consider short & long term

Phase 4: EVALUATION
- Score options against criteria
- Identify trade-offs
- Assess risks
- Consider scenarios

Phase 5: BIAS CHECK
- Confirmation bias?
- Sunk cost fallacy?
- Anchoring?
- Status quo bias?
- Availability heuristic?

Phase 6: RECOMMENDATION
- Summarize analysis
- Present top options
- Highlight key considerations
- Support user's decision

OUTPUT FORMAT:

📋 DECISION SUMMARY
[Clear statement of the decision]

🎯 CRITERIA (weighted 1-10)
1. [Criterion] (weight: X) - [description]
2. ...

📊 OPTIONS ANALYSIS
Option A: [name]
  - Score: X/10
  - Pros: ...
  - Cons: ...
  - Risk: low/medium/high

Option B: ...

⚖️ KEY TRADE-OFFS
- [Trade-off 1]
- [Trade-off 2]

⚠️ RISKS
- [Risk 1]: [mitigation]
- [Risk 2]: [mitigation]

🎭 BIAS CHECK
- [Potential bias]: [how to address]

💡 RECOMMENDATION
[Balanced recommendation empowering user choice]

📝 NEXT STEPS
1. [Action item]
2. [Action item]"""

    def __init__(self, llm_config: Dict[str, Any] = None):
        """Initialize the decision support system."""
        self.llm_config = llm_config or {
            "provider": "ollama",
            "model": "llama3.2:3b",
            "base_url": os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
            "temperature": 0.5
        }
        self.llm = None
        self.analysis = DecisionAnalysis()
        self.conversation_history: List[Dict[str, str]] = []
        self.current_phase = DecisionPhase.PROBLEM_DEFINITION
        
    def _create_llm(self):
        """Create LLM instance."""
        if self.llm is not None:
            return self.llm
        try:
            from langchain_ollama import ChatOllama
            self.llm = ChatOllama(
                model=self.llm_config.get("model", "llama3.2:3b"),
                base_url=self.llm_config.get("base_url", "http://localhost:11434"),
                temperature=self.llm_config.get("temperature", 0.5)
            )
            return self.llm
        except ImportError:
            raise ImportError("langchain-ollama required")
    
    def _invoke(self, prompt: str) -> str:
        """Invoke the LLM."""
        llm = self._create_llm()
        response = llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    def _build_context(self) -> str:
        """Build context from conversation history."""
        if not self.conversation_history:
            return ""
        
        recent = self.conversation_history[-8:]
        context_parts = ["CONVERSATION HISTORY:"]
        for entry in recent:
            context_parts.append(f"User: {entry.get('user', '')}")
            context_parts.append(f"Advisor: {entry.get('advisor', '')[:300]}...")
        
        return "\n".join(context_parts)
    
    def start_analysis(self, decision_statement: str) -> str:
        """Start a new decision analysis."""
        self.analysis = DecisionAnalysis(problem_statement=decision_statement)
        self.conversation_history = []
        self.current_phase = DecisionPhase.PROBLEM_DEFINITION
        
        prompt = f"""{self.SYSTEM_PROMPT}

A user needs help with this decision:
"{decision_statement}"

Begin by understanding the problem. Ask clarifying questions about:
1. The specific decision being made
2. Key constraints (time, budget, resources)
3. Who is affected (stakeholders)
4. What success looks like

Be conversational and helpful. Ask 2-3 focused questions."""
        
        response = self._invoke(prompt)
        
        self.conversation_history.append({
            "user": decision_statement,
            "advisor": response
        })
        
        return response
    
    def process_input(self, user_input: str) -> str:
        """Process user input and continue analysis."""
        context = self._build_context()
        
        prompt = f"""{self.SYSTEM_PROMPT}

DECISION BEING ANALYZED:
{self.analysis.problem_statement}

CURRENT PHASE: {self.current_phase.value}

{context}

USER'S INPUT:
{user_input}

Continue the decision support conversation:
1. Acknowledge and incorporate their input
2. If enough info, advance to next phase
3. If not, ask clarifying questions
4. Stay focused on helping them decide

Phases: problem_definition -> option_generation -> criteria_development -> evaluation -> bias_check -> recommendation

Be helpful, balanced, and thorough."""
        
        response = self._invoke(prompt)
        
        self.conversation_history.append({
            "user": user_input,
            "advisor": response
        })
        
        # Simple phase advancement based on response content
        self._update_phase(response)
        
        return response
    
    def _update_phase(self, response: str):
        """Update current phase based on conversation progress."""
        response_lower = response.lower()
        
        if "options" in response_lower and self.current_phase == DecisionPhase.PROBLEM_DEFINITION:
            self.current_phase = DecisionPhase.OPTION_GENERATION
        elif "criteria" in response_lower and self.current_phase == DecisionPhase.OPTION_GENERATION:
            self.current_phase = DecisionPhase.CRITERIA_DEVELOPMENT
        elif "score" in response_lower or "evaluation" in response_lower:
            self.current_phase = DecisionPhase.EVALUATION
        elif "bias" in response_lower:
            self.current_phase = DecisionPhase.BIAS_CHECK
        elif "recommendation" in response_lower:
            self.current_phase = DecisionPhase.RECOMMENDATION
    
    def generate_full_analysis(self) -> str:
        """Generate complete decision analysis."""
        context = self._build_context()
        
        prompt = f"""{self.SYSTEM_PROMPT}

DECISION:
{self.analysis.problem_statement}

CONVERSATION CONTEXT:
{context}

Generate a COMPLETE decision analysis following this format:

📋 DECISION SUMMARY
[Restate the decision clearly]

🎯 EVALUATION CRITERIA (weight 1-10)
[List criteria with weights]

📊 OPTIONS ANALYSIS
[Analyze each option with pros, cons, risks, scores]

⚖️ KEY TRADE-OFFS
[Main trade-offs between top options]

⚠️ RISK ASSESSMENT
[Key risks and mitigations]

🎭 BIAS CHECK
[Potential biases the user should consider]

💡 RECOMMENDATION
[Balanced recommendation - don't decide for them]

📝 NEXT STEPS
[Concrete action items]

Provide thorough, balanced analysis."""
        
        return self._invoke(prompt)
    
    def get_quick_analysis(self, decision: str) -> str:
        """Get quick single-turn analysis."""
        prompt = f"""{self.SYSTEM_PROMPT}

Provide a quick but thorough decision analysis for:
"{decision}"

Include all sections:
- Decision Summary
- Options (at least 3)
- Criteria
- Quick evaluation
- Key trade-offs
- Recommendation

Be concise but comprehensive."""
        
        return self._invoke(prompt)
    
    def check_biases(self) -> str:
        """Check for potential biases in the analysis."""
        context = self._build_context()
        
        prompt = f"""Based on this decision conversation:

{context}

Identify potential cognitive biases that might be affecting this decision:

1. CONFIRMATION BIAS
   - Are they only considering supporting evidence?
   - What contrary evidence should they consider?

2. SUNK COST FALLACY
   - Are past investments unfairly influencing the decision?
   - What would they decide if starting fresh?

3. ANCHORING
   - Is an initial number/option unduly influencing them?
   - What if we removed that anchor?

4. STATUS QUO BIAS
   - Is fear of change affecting the analysis?
   - What's the cost of NOT changing?

5. AVAILABILITY HEURISTIC
   - Are recent/vivid experiences over-weighted?
   - What base rates should they consider?

Provide specific, actionable bias-checking advice."""
        
        return self._invoke(prompt)
    
    def get_analysis_status(self) -> Dict[str, Any]:
        """Get current analysis status."""
        return {
            "problem_statement": self.analysis.problem_statement,
            "current_phase": self.current_phase.value,
            "conversation_turns": len(self.conversation_history),
            "options_identified": len(self.analysis.options),
            "criteria_defined": len(self.analysis.criteria)
        }


def run_interactive(dss: DecisionSupportSystem):
    """Run interactive decision support session."""
    print("\n" + "=" * 60)
    print("🎯 DECISION SUPPORT SYSTEM")
    print("=" * 60)
    print("\nI'll help you analyze a decision systematically.")
    print("\nCommands:")
    print("  /analyze   - Generate full analysis")
    print("  /biases    - Check for cognitive biases")
    print("  /status    - Show analysis status")
    print("  /new       - Start new decision")
    print("  /quit      - Exit")
    print("\nWhat decision do you need help with?\n")
    
    decision = input("📋 Decision: ").strip()
    if decision.lower() in ['quit', 'exit']:
        return
    
    response = dss.start_analysis(decision)
    print(f"\n🎯 Advisor: {response}\n")
    
    while True:
        try:
            user_input = input("👤 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break
        
        if not user_input:
            continue
        
        # Handle commands
        if user_input.startswith('/'):
            cmd = user_input.lower().split()[0]
            
            if cmd in ['/quit', '/exit']:
                break
            elif cmd == '/analyze':
                print("\n📊 Generating full analysis...\n")
                analysis = dss.generate_full_analysis()
                print(analysis)
            elif cmd == '/biases':
                print("\n🎭 Checking for biases...\n")
                biases = dss.check_biases()
                print(biases)
            elif cmd == '/status':
                status = dss.get_analysis_status()
                print("\n📈 Analysis Status:")
                for key, value in status.items():
                    print(f"  {key}: {value}")
            elif cmd == '/new':
                decision = input("\n📋 New decision: ").strip()
                response = dss.start_analysis(decision)
                print(f"\n🎯 Advisor: {response}")
            else:
                print(f"Unknown command: {cmd}")
            print()
            continue
        
        response = dss.process_input(user_input)
        print(f"\n🎯 Advisor: {response}\n")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Decision Support System')
    parser.add_argument('decision', nargs='?', help='Decision to analyze')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--quick', '-q', action='store_true', help='Quick analysis')
    parser.add_argument('--model', default='llama3.2:3b', help='Ollama model')
    parser.add_argument('--base-url', default='http://localhost:11434', help='Ollama URL')
    
    args = parser.parse_args()
    
    llm_config = {
        "provider": "ollama",
        "model": args.model,
        "base_url": args.base_url,
        "temperature": 0.5
    }
    
    dss = DecisionSupportSystem(llm_config)
    
    if args.quick and args.decision:
        analysis = dss.get_quick_analysis(args.decision)
        print(analysis)
    elif args.decision and not args.interactive:
        response = dss.start_analysis(args.decision)
        print(f"\n{response}")
        run_interactive(dss)
    else:
        run_interactive(dss)


if __name__ == "__main__":
    main()
