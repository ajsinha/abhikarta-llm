#!/usr/bin/env python3
"""
Strategic Planning Pipeline Example

A comprehensive strategic planning workflow that:
1. Analyzes current situation
2. Conducts SWOT and PESTLE analyses
3. Identifies strategic issues
4. Generates and evaluates strategic options
5. Develops implementation roadmap
6. Creates risk mitigation plan

Usage:
    python strategic_planning_pipeline.py "Your strategic question"
    python strategic_planning_pipeline.py --interactive
    python strategic_planning_pipeline.py --demo

Copyright © 2025-2030 Abhikarta. All Rights Reserved.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class StrategicPlanStage:
    """Represents a stage in the strategic planning process."""
    name: str
    output: str = ""
    duration_ms: int = 0


class StrategicPlanningPipeline:
    """Strategic planning pipeline implementation."""
    
    def __init__(self, llm_config: Dict[str, Any] = None):
        """Initialize the strategic planning pipeline."""
        self.llm_config = llm_config or {
            "provider": "ollama",
            "model": "llama3.2:3b",
            "base_url": os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
            "temperature": 0.6
        }
        self.llm = None
        self.stages: Dict[str, StrategicPlanStage] = {}
        
    def _create_llm(self):
        """Create LLM instance."""
        if self.llm is not None:
            return self.llm
        try:
            from langchain_ollama import ChatOllama
            self.llm = ChatOllama(
                model=self.llm_config.get("model", "llama3.2:3b"),
                base_url=self.llm_config.get("base_url", "http://localhost:11434"),
                temperature=self.llm_config.get("temperature", 0.6)
            )
            return self.llm
        except ImportError:
            raise ImportError("langchain-ollama required")
    
    def _invoke(self, prompt: str) -> str:
        """Invoke the LLM."""
        llm = self._create_llm()
        response = llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    def _run_stage(self, stage_name: str, prompt: str) -> str:
        """Run a pipeline stage."""
        import time
        logger.info(f"Running stage: {stage_name}")
        start = time.time()
        
        result = self._invoke(prompt)
        
        duration = int((time.time() - start) * 1000)
        self.stages[stage_name] = StrategicPlanStage(
            name=stage_name,
            output=result,
            duration_ms=duration
        )
        
        logger.info(f"Stage {stage_name} completed in {duration}ms")
        return result
    
    def analyze_situation(self, input_text: str) -> str:
        """Analyze the current situation."""
        prompt = f"""Analyze the current strategic situation:

{input_text}

Provide comprehensive analysis:

## CURRENT STATE
- Where are we now?
- Key metrics and indicators
- Recent trends and developments

## CONTEXT
- Market conditions
- Competitive landscape
- Regulatory environment
- Economic factors

## STAKEHOLDERS
- Who is affected by this strategy?
- What are their interests and concerns?
- Who has influence over outcomes?

## KEY CHALLENGES
- Immediate issues to address
- Long-term challenges
- Resource constraints"""
        
        return self._run_stage("situation_analysis", prompt)
    
    def conduct_swot(self, situation: str) -> str:
        """Conduct SWOT analysis."""
        prompt = f"""Conduct a thorough SWOT analysis:

SITUATION CONTEXT:
{situation}

## STRENGTHS (Internal Positives)
- Core competencies and capabilities
- Competitive advantages
- Strong resources or assets
- Positive differentiators

## WEAKNESSES (Internal Negatives)
- Capability gaps
- Resource limitations
- Process inefficiencies
- Competitive disadvantages

## OPPORTUNITIES (External Positives)
- Market trends to leverage
- Emerging customer needs
- Competitor weaknesses to exploit
- Regulatory changes that help

## THREATS (External Negatives)
- Competitive pressures
- Market disruptions
- Regulatory risks
- Economic uncertainties

For each item, rate importance (High/Medium/Low) and time horizon (Short/Medium/Long term)."""
        
        return self._run_stage("swot_analysis", prompt)
    
    def conduct_pestle(self, situation: str) -> str:
        """Conduct PESTLE analysis."""
        prompt = f"""Conduct a PESTLE environmental analysis:

SITUATION CONTEXT:
{situation}

## POLITICAL FACTORS
- Government policies and stability
- Trade regulations and tariffs
- Political trends affecting the sector

## ECONOMIC FACTORS
- Economic growth and cycles
- Interest rates and inflation
- Consumer spending patterns
- Currency and exchange rates

## SOCIAL FACTORS
- Demographic trends
- Cultural attitudes and values
- Lifestyle changes
- Education and skill levels

## TECHNOLOGICAL FACTORS
- Emerging technologies
- Digital transformation trends
- R&D and innovation
- Automation and AI impact

## LEGAL FACTORS
- Regulatory requirements
- Compliance obligations
- Employment laws
- Intellectual property

## ENVIRONMENTAL FACTORS
- Sustainability requirements
- Climate change impact
- Environmental regulations
- Resource availability

Rate each factor by Impact (High/Medium/Low) and Trend (Improving/Stable/Declining)."""
        
        return self._run_stage("pestle_analysis", prompt)
    
    def identify_strategic_issues(self, swot: str, pestle: str) -> str:
        """Identify key strategic issues."""
        prompt = f"""Identify key strategic issues from the analyses:

SWOT ANALYSIS:
{swot[:2000]}

PESTLE ANALYSIS:
{pestle[:2000]}

## CRITICAL STRATEGIC ISSUES

### Priority 1: Must Address Immediately
- Issue description
- Why it's critical
- Implications if not addressed

### Priority 2: Important to Address Soon
- Issue description
- Why it matters
- Recommended timeframe

### Priority 3: Monitor and Plan
- Issue description
- Potential impact
- Trigger points to watch

## KEY STRATEGIC QUESTIONS
- What fundamental choices need to be made?
- What trade-offs must be resolved?
- Where is there uncertainty?

## OPPORTUNITY AREAS
- Where can we create advantage?
- What should we capitalize on?
- Quick wins available?"""
        
        return self._run_stage("strategic_issues", prompt)
    
    def generate_options(self, issues: str) -> str:
        """Generate strategic options."""
        prompt = f"""Generate strategic options to address these issues:

STRATEGIC ISSUES:
{issues}

Develop 4 distinct strategic options:

## OPTION 1: [Name]
**Description:** What this option involves
**Strategic Logic:** Why this makes sense
**Key Initiatives:**
1. Initiative A
2. Initiative B
3. Initiative C
**Resource Requirements:** Time, money, people
**Main Risks:** Key risks involved
**Timeline:** Implementation horizon

## OPTION 2: [Name]
[Same structure]

## OPTION 3: [Name]
[Same structure]

## OPTION 4: [Name]
[Same structure]

Make options meaningfully different - don't just create variations of the same approach."""
        
        return self._run_stage("strategic_options", prompt)
    
    def evaluate_options(self, options: str, issues: str) -> str:
        """Evaluate strategic options."""
        prompt = f"""Evaluate the strategic options:

OPTIONS:
{options}

STRATEGIC ISSUES:
{issues[:1500]}

## EVALUATION CRITERIA

For each option, score 1-10 on:

| Criterion | Option 1 | Option 2 | Option 3 | Option 4 |
|-----------|----------|----------|----------|----------|
| Strategic Fit | | | | |
| Feasibility | | | | |
| Risk-Adjusted Return | | | | |
| Implementation Speed | | | | |
| Resource Efficiency | | | | |
| Sustainability | | | | |
| **TOTAL** | | | | |

## DETAILED EVALUATION

### Option 1
- Strengths:
- Weaknesses:
- Best suited when:

[Repeat for each option]

## RECOMMENDATION
- Recommended option and why
- Key success factors
- Critical dependencies"""
        
        return self._run_stage("option_evaluation", prompt)
    
    def synthesize_strategy(self, evaluation: str) -> str:
        """Synthesize the final strategy."""
        prompt = f"""Synthesize the recommended strategy:

OPTION EVALUATION:
{evaluation}

## STRATEGIC DIRECTION

### Vision
Where we want to be in 3-5 years

### Mission
How we will get there

### Strategic Priorities
1. Priority 1: Description
2. Priority 2: Description
3. Priority 3: Description

### Guiding Principles
- Principle 1
- Principle 2
- Principle 3

## STRATEGIC INITIATIVES

### Initiative 1: [Name]
- Objective:
- Key actions:
- Success metrics:
- Owner:

[Repeat for 3-5 major initiatives]

## SUCCESS METRICS

| Metric | Current | Year 1 Target | Year 3 Target |
|--------|---------|---------------|---------------|
| KPI 1 | | | |
| KPI 2 | | | |
| KPI 3 | | | |"""
        
        return self._run_stage("strategy_synthesis", prompt)
    
    def develop_roadmap(self, strategy: str) -> str:
        """Develop implementation roadmap."""
        prompt = f"""Develop an implementation roadmap:

STRATEGY:
{strategy}

## IMPLEMENTATION ROADMAP

### PHASE 1: QUICK WINS (Months 1-3)
**Objectives:** Build momentum, demonstrate progress
**Key Actions:**
1. Action 1 - Week 1-4
2. Action 2 - Week 4-8
3. Action 3 - Week 8-12
**Milestones:**
- [ ] Milestone 1 (Month 1)
- [ ] Milestone 2 (Month 2)
- [ ] Milestone 3 (Month 3)
**Resources Required:**
**Dependencies:**

### PHASE 2: FOUNDATION (Months 4-12)
**Objectives:** Build core capabilities
**Key Actions:**
**Milestones:**
**Resources Required:**
**Dependencies:**

### PHASE 3: ACCELERATION (Months 13-24)
**Objectives:** Scale and expand
**Key Actions:**
**Milestones:**
**Resources Required:**
**Dependencies:**

### PHASE 4: TRANSFORMATION (Months 25-36)
**Objectives:** Full realization of strategy
**Key Actions:**
**Milestones:**
**Resources Required:**
**Dependencies:**

## GOVERNANCE
- Review cadence
- Decision-making process
- Escalation path"""
        
        return self._run_stage("implementation_roadmap", prompt)
    
    def develop_risk_plan(self, strategy: str, roadmap: str) -> str:
        """Develop risk mitigation plan."""
        prompt = f"""Develop risk mitigation plan:

STRATEGY:
{strategy[:1500]}

ROADMAP:
{roadmap[:1500]}

## RISK REGISTER

### HIGH PRIORITY RISKS

#### Risk 1: [Name]
- **Description:**
- **Probability:** High/Medium/Low
- **Impact:** High/Medium/Low
- **Mitigation Strategy:**
- **Contingency Plan:**
- **Risk Owner:**
- **Review Frequency:**

[Repeat for 3-5 high priority risks]

### MEDIUM PRIORITY RISKS

[Similar structure for medium risks]

## EARLY WARNING INDICATORS
- What signals suggest risks are materializing?
- Monitoring approach

## CONTINGENCY BUDGET
- Reserve allocation
- Trigger points for activation"""
        
        return self._run_stage("risk_mitigation", prompt)
    
    def generate_executive_summary(self) -> str:
        """Generate executive summary."""
        prompt = f"""Generate an executive summary of the strategic plan:

SITUATION: {self.stages.get('situation_analysis', StrategicPlanStage('')).output[:800]}

STRATEGIC ISSUES: {self.stages.get('strategic_issues', StrategicPlanStage('')).output[:800]}

STRATEGY: {self.stages.get('strategy_synthesis', StrategicPlanStage('')).output[:800]}

ROADMAP: {self.stages.get('implementation_roadmap', StrategicPlanStage('')).output[:800]}

## EXECUTIVE SUMMARY

### Strategic Context
[2-3 sentences on the situation and why action is needed]

### Key Findings
[3-4 bullet points on critical insights]

### Recommended Strategy
[Clear statement of strategic direction]

### Implementation Approach
[High-level phasing and timeline]

### Critical Success Factors
[3-4 factors essential for success]

### Immediate Next Steps
1. [Action 1 - Who - When]
2. [Action 2 - Who - When]
3. [Action 3 - Who - When]

### Resource Requirements
[High-level resource needs]

### Expected Outcomes
[What success looks like]"""
        
        return self._run_stage("executive_summary", prompt)
    
    def run(self, strategic_question: str) -> Dict[str, Any]:
        """Run the complete strategic planning pipeline."""
        logger.info("=" * 60)
        logger.info("STRATEGIC PLANNING PIPELINE")
        logger.info("=" * 60)
        
        start_time = datetime.now(timezone.utc)
        
        # Stage 1: Situation Analysis
        logger.info("\n[1/9] Analyzing situation...")
        situation = self.analyze_situation(strategic_question)
        
        # Stage 2-3: SWOT and PESTLE (conceptually parallel)
        logger.info("\n[2/9] Conducting SWOT analysis...")
        swot = self.conduct_swot(situation)
        
        logger.info("\n[3/9] Conducting PESTLE analysis...")
        pestle = self.conduct_pestle(situation)
        
        # Stage 4: Strategic Issues
        logger.info("\n[4/9] Identifying strategic issues...")
        issues = self.identify_strategic_issues(swot, pestle)
        
        # Stage 5: Option Generation
        logger.info("\n[5/9] Generating strategic options...")
        options = self.generate_options(issues)
        
        # Stage 6: Option Evaluation
        logger.info("\n[6/9] Evaluating options...")
        evaluation = self.evaluate_options(options, issues)
        
        # Stage 7: Strategy Synthesis
        logger.info("\n[7/9] Synthesizing strategy...")
        strategy = self.synthesize_strategy(evaluation)
        
        # Stage 8: Roadmap Development
        logger.info("\n[8/9] Developing implementation roadmap...")
        roadmap = self.develop_roadmap(strategy)
        
        # Stage 8b: Risk Mitigation
        logger.info("\n[8b/9] Developing risk mitigation plan...")
        risks = self.develop_risk_plan(strategy, roadmap)
        
        # Stage 9: Executive Summary
        logger.info("\n[9/9] Generating executive summary...")
        exec_summary = self.generate_executive_summary()
        
        end_time = datetime.now(timezone.utc)
        total_duration = (end_time - start_time).total_seconds()
        
        # Compile final output
        final_output = f"""# STRATEGIC PLAN

## Executive Summary
{exec_summary}

---

## Detailed Strategic Plan

### Situation Analysis
{situation}

### SWOT Analysis
{swot}

### PESTLE Analysis
{pestle}

### Strategic Issues
{issues}

### Strategic Options
{options}

### Option Evaluation
{evaluation}

### Recommended Strategy
{strategy}

### Implementation Roadmap
{roadmap}

### Risk Mitigation
{risks}
"""
        
        results = {
            "strategic_question": strategic_question,
            "final_output": final_output,
            "stages": {
                name: {
                    "output_preview": stage.output[:500] + "..." if len(stage.output) > 500 else stage.output,
                    "duration_ms": stage.duration_ms
                }
                for name, stage in self.stages.items()
            },
            "metadata": {
                "total_duration_seconds": total_duration,
                "stages_completed": len(self.stages),
                "completed_at": end_time.isoformat()
            }
        }
        
        logger.info("\n" + "=" * 60)
        logger.info("STRATEGIC PLANNING COMPLETE")
        logger.info(f"Total time: {total_duration:.2f}s")
        logger.info("=" * 60)
        
        return results


def run_demo():
    """Run a demonstration."""
    demo_input = """
    We are a mid-sized technology company with $50M in annual revenue. 
    We've been successful in our core market but growth has slowed to 5% annually.
    Our main competitors are larger and better-funded.
    We're considering whether to:
    1. Double down on our current market
    2. Expand into adjacent markets
    3. Pursue acquisition opportunities
    4. Invest heavily in R&D for next-generation products
    
    Key constraints:
    - Limited capital for major acquisitions
    - Strong technical team but limited sales capacity
    - Board expects return to double-digit growth
    """
    
    pipeline = StrategicPlanningPipeline()
    result = pipeline.run(demo_input)
    
    print("\n" + "=" * 60)
    print("STRATEGIC PLAN OUTPUT")
    print("=" * 60)
    print(result['final_output'][:5000] + "\n\n[...truncated for demo...]")


def run_interactive():
    """Run interactive mode."""
    print("\n" + "=" * 60)
    print("🎯 STRATEGIC PLANNING PIPELINE")
    print("=" * 60)
    print("\nDescribe your strategic situation and question.")
    print("Include context about your organization, market, and challenges.")
    print("\nType 'quit' to exit.\n")
    
    while True:
        print("-" * 40)
        print("Enter your strategic question (or 'quit'):")
        lines = []
        while True:
            line = input()
            if line.lower() == 'quit':
                print("Goodbye!")
                return
            if line == "":
                break
            lines.append(line)
        
        if not lines:
            continue
        
        strategic_question = "\n".join(lines)
        
        pipeline = StrategicPlanningPipeline()
        result = pipeline.run(strategic_question)
        
        print("\n" + "=" * 60)
        print("STRATEGIC PLAN")
        print("=" * 60)
        print(result['final_output'])
        
        # Offer to save
        save = input("\nSave to file? (y/n): ").strip().lower()
        if save == 'y':
            filename = f"strategic_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(filename, 'w') as f:
                f.write(result['final_output'])
            print(f"Saved to: {filename}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Strategic Planning Pipeline')
    parser.add_argument('question', nargs='?', help='Strategic question')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--demo', '-d', action='store_true', help='Run demonstration')
    parser.add_argument('--output', '-o', help='Output file')
    parser.add_argument('--model', default='llama3.2:3b', help='Ollama model')
    parser.add_argument('--base-url', default='http://localhost:11434', help='Ollama URL')
    
    args = parser.parse_args()
    
    if args.demo:
        run_demo()
    elif args.interactive:
        run_interactive()
    elif args.question:
        pipeline = StrategicPlanningPipeline({
            "provider": "ollama",
            "model": args.model,
            "base_url": args.base_url,
            "temperature": 0.6
        })
        result = pipeline.run(args.question)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(result['final_output'])
            print(f"Strategic plan saved to: {args.output}")
        else:
            print(result['final_output'])
    else:
        run_interactive()


if __name__ == "__main__":
    main()
