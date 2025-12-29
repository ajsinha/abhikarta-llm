# Chain of Thought (CoT) and Tree of Thought (ToT) in Abhikarta-LLM

## A Comprehensive Tutorial Guide

**Version:** 1.4.0  
**Author:** Ashutosh Sinha  
**Copyright © 2025-2030 All Rights Reserved**

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Understanding CoT and ToT](#2-understanding-cot-and-tot)
3. [Setting Up Your Environment](#3-setting-up-your-environment)
4. [Basic Chain of Thought Implementation](#4-basic-chain-of-thought-implementation)
5. [Advanced CoT with Tool Integration](#5-advanced-cot-with-tool-integration)
6. [Tree of Thought Implementation](#6-tree-of-thought-implementation)
7. [CoT and ToT in Workflows](#7-cot-and-tot-in-workflows)
8. [CoT and ToT in Agent Swarms](#8-cot-and-tot-in-agent-swarms)
9. [Best Practices](#9-best-practices)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Introduction

Chain of Thought (CoT) and Tree of Thought (ToT) are advanced prompting techniques that dramatically improve LLM reasoning capabilities. Abhikarta-LLM provides built-in support for both patterns through:

- **Agent Types**: Pre-configured agent templates for CoT and ToT
- **System Prompts**: Optimized prompts that elicit step-by-step reasoning
- **Workflow Nodes**: Visual nodes for integrating reasoning patterns
- **Swarm Choreography**: Master Actors that use CoT/ToT for decision-making

### When to Use Each Pattern

| Pattern | Best For | Complexity | Tokens Used |
|---------|----------|------------|-------------|
| **CoT** | Linear problems, math, logic | Medium | 2-3x base |
| **ToT** | Creative tasks, optimization, exploration | High | 5-10x base |

---

## 2. Understanding CoT and ToT

### 2.1 Chain of Thought (CoT)

CoT prompts the LLM to "think step by step" before giving a final answer. This produces intermediate reasoning steps that improve accuracy.

```
Standard Prompt:
"What is 23 * 47?"
→ Model might answer incorrectly

CoT Prompt:
"What is 23 * 47? Think step by step."
→ Model shows: "23 * 47 = 23 * 40 + 23 * 7 = 920 + 161 = 1081"
```

### 2.2 Tree of Thought (ToT)

ToT extends CoT by exploring multiple reasoning paths simultaneously, then selecting the best path based on evaluation.

```
ToT Structure:
                    [Problem]
                   /    |    \
              [Path A] [Path B] [Path C]
              /    \      |      /    \
          [A1]   [A2]   [B1]  [C1]   [C2]
                    \     |     /
                  [Evaluate & Select Best]
                         |
                    [Solution]
```

---

## 3. Setting Up Your Environment

### 3.1 Prerequisites

```bash
# Install Abhikarta-LLM
pip install abhikarta-llm

# Required dependencies for CoT/ToT
pip install langchain>=0.1.0
pip install openai>=1.0.0  # or anthropic, google-generativeai
```

### 3.2 Configuration

Create or update your `abhikarta.properties`:

```properties
# LLM Provider for reasoning tasks
llm.provider=openai
llm.model=gpt-4
llm.api_key=your-api-key

# CoT/ToT specific settings
cot.max_steps=10
cot.temperature=0.3
tot.branches=3
tot.max_depth=4
tot.evaluation_model=gpt-4
```

### 3.3 Verify Setup

```python
from abhikarta.llm_provider import LLMFacade

# Initialize
llm = LLMFacade.from_config()

# Test CoT prompt
response = llm.complete(
    "What is 156 ÷ 12? Think step by step.",
    temperature=0.3
)
print(response)
```

---

## 4. Basic Chain of Thought Implementation

### 4.1 Creating a CoT Agent via Web UI

1. Navigate to **Agents → Create Agent**
2. Fill in basic details:
   - **Name**: `Math Reasoning Agent`
   - **Description**: `Solves math problems using chain of thought`
   - **Agent Type**: `Chain of Thought (CoT)`

3. Configure the system prompt (auto-filled for CoT type):

```
You are a precise mathematical reasoning agent. For every problem:

1. UNDERSTAND: Restate the problem in your own words
2. PLAN: Identify what operations or steps are needed
3. EXECUTE: Perform each step, showing your work
4. VERIFY: Check your answer by alternative method if possible
5. ANSWER: State the final answer clearly

Always show your complete reasoning process. Never skip steps.
```

4. Set LLM parameters:
   - **Temperature**: `0.2` (lower for deterministic reasoning)
   - **Max Tokens**: `1024`

5. Save and Publish

### 4.2 Creating a CoT Agent via Code

```python
from abhikarta.agent import AgentManager, AgentTemplate
from abhikarta.database import DatabaseFacade

# Initialize
db_facade = DatabaseFacade.from_config()
agent_manager = AgentManager(db_facade)

# Define CoT system prompt
COT_SYSTEM_PROMPT = """You are a logical reasoning agent. For every question:

**Step 1 - Understand**: Clearly state what is being asked
**Step 2 - Identify**: List relevant facts and constraints
**Step 3 - Reason**: Work through the problem step by step
**Step 4 - Conclude**: State your final answer with confidence level

Format your response as:
## Understanding
[Your understanding]

## Known Facts
- Fact 1
- Fact 2

## Reasoning
Step 1: [reasoning]
Step 2: [reasoning]
...

## Conclusion
[Final answer]
"""

# Create agent
agent_id = agent_manager.create_agent(
    name="Logical Reasoning Agent",
    description="Uses CoT for complex reasoning tasks",
    agent_type="chain_of_thought",
    system_prompt=COT_SYSTEM_PROMPT,
    llm_config={
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.2,
        "max_tokens": 2048
    },
    created_by="admin"
)

print(f"Created CoT agent: {agent_id}")
```

### 4.3 Running a CoT Agent

```python
from abhikarta.agent import AgentExecutor

# Initialize executor
executor = AgentExecutor(db_facade)

# Execute with a complex reasoning task
result = executor.execute(
    agent_id=agent_id,
    user_input="""
    A farmer has 3 fields. Field A produces 120 bushels per acre.
    Field B produces 80% of what Field A produces.
    Field C produces 50 bushels more per acre than Field B.
    
    If Field A is 15 acres, Field B is 20 acres, and Field C is 10 acres,
    what is the total production across all fields?
    """,
    context={}
)

print("=== CoT Reasoning ===")
print(result['output'])
```

**Expected Output:**
```
## Understanding
Calculate total bushel production from 3 fields with different productivity rates.

## Known Facts
- Field A: 120 bushels/acre, 15 acres
- Field B: 80% of Field A's rate = 96 bushels/acre, 20 acres
- Field C: Field B + 50 = 146 bushels/acre, 10 acres

## Reasoning
Step 1: Calculate Field A production
  120 bushels/acre × 15 acres = 1,800 bushels

Step 2: Calculate Field B's rate
  80% × 120 = 96 bushels/acre

Step 3: Calculate Field B production
  96 bushels/acre × 20 acres = 1,920 bushels

Step 4: Calculate Field C's rate
  96 + 50 = 146 bushels/acre

Step 5: Calculate Field C production
  146 bushels/acre × 10 acres = 1,460 bushels

Step 6: Sum all fields
  1,800 + 1,920 + 1,460 = 5,180 bushels

## Conclusion
**Total production: 5,180 bushels**
```

---

## 5. Advanced CoT with Tool Integration

### 5.1 CoT Agent with Calculator Tool

```python
from abhikarta.tools import ToolRegistry

# Register calculator tool
@ToolRegistry.register("calculator")
def calculator(expression: str) -> dict:
    """
    Evaluates mathematical expressions safely.
    
    Args:
        expression: Mathematical expression (e.g., "23 * 47 + 15")
    
    Returns:
        dict with 'result' key
    """
    import ast
    import operator
    
    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow
    }
    
    def eval_expr(node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
        else:
            raise ValueError(f"Unsupported operation: {node}")
    
    tree = ast.parse(expression, mode='eval')
    result = eval_expr(tree.body)
    return {"result": result}

# Create CoT agent with tool access
COT_WITH_TOOLS_PROMPT = """You are a mathematical problem solver with access to a calculator tool.

Process:
1. PARSE: Break down the problem into calculable steps
2. CALCULATE: Use the calculator tool for each arithmetic operation
3. COMBINE: Assemble partial results into final answer
4. VERIFY: Double-check critical calculations

Use the calculator tool for ALL arithmetic to ensure accuracy.
Show your reasoning for each step, then use the tool.
"""

agent_id = agent_manager.create_agent(
    name="Math Agent with Tools",
    agent_type="react",  # ReAct for tool usage
    system_prompt=COT_WITH_TOOLS_PROMPT,
    tools=["builtin:calculator"],
    llm_config={"provider": "openai", "model": "gpt-4", "temperature": 0.1},
    created_by="admin"
)
```

### 5.2 CoT with Web Search for Research

```python
# Create research agent that reasons through search results
RESEARCH_COT_PROMPT = """You are a research analyst using chain of thought reasoning.

Process for each question:
1. DECOMPOSE: Break the question into searchable sub-questions
2. SEARCH: Use web_search tool for each sub-question
3. SYNTHESIZE: Combine findings, noting sources
4. REASON: Draw conclusions from evidence
5. ANSWER: Provide final answer with confidence and citations

Always cite your sources. If information conflicts, note the discrepancy.
"""

agent_manager.create_agent(
    name="Research Analyst",
    agent_type="react",
    system_prompt=RESEARCH_COT_PROMPT,
    tools=["builtin:web_search", "builtin:web_fetch"],
    llm_config={"provider": "anthropic", "model": "claude-3-opus", "temperature": 0.3},
    created_by="admin"
)
```

---

## 6. Tree of Thought Implementation

### 6.1 ToT Architecture in Abhikarta

Abhikarta implements ToT using a multi-stage workflow:

```
┌─────────────────────────────────────────────────────────────┐
│                    ToT WORKFLOW                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Problem Input]                                             │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐                                           │
│  │  DECOMPOSE   │  Break into sub-problems                  │
│  └──────┬───────┘                                           │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐                                           │
│  │   BRANCH     │  Generate N solution paths                │
│  └──────┬───────┘                                           │
│    ┌────┼────┐                                              │
│    ▼    ▼    ▼                                              │
│  [P1] [P2] [P3]   Parallel exploration                      │
│    │    │    │                                              │
│    ▼    ▼    ▼                                              │
│  ┌──────────────┐                                           │
│  │  EVALUATE    │  Score each path                          │
│  └──────┬───────┘                                           │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐                                           │
│  │   SELECT     │  Choose best path(s)                      │
│  └──────┬───────┘                                           │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐                                           │
│  │   REFINE     │  Expand selected paths                    │
│  └──────┬───────┘                                           │
│         │                                                    │
│         ▼                                                    │
│  [Final Solution]                                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Creating a ToT Agent

```python
from abhikarta.agent import AgentManager

TOT_SYSTEM_PROMPT = """You are a creative problem solver using Tree of Thought reasoning.

When given a problem, you will explore multiple solution paths in parallel.

## Your Process:

### Phase 1: DECOMPOSE
Break the problem into key components and constraints.

### Phase 2: BRANCH (Generate 3 Approaches)
For each approach, provide:
- **Approach Name**: Brief title
- **Strategy**: How this approach tackles the problem
- **First Steps**: Initial actions to take
- **Potential**: Why this might work
- **Risks**: Why this might fail

### Phase 3: EVALUATE
Rate each approach on:
- Feasibility (1-10)
- Completeness (1-10)
- Elegance (1-10)
Calculate: Total Score = (Feasibility × 2) + Completeness + Elegance

### Phase 4: SELECT & REFINE
Take the highest-scoring approach and develop it fully.

## Output Format:
```
## Problem Decomposition
[Your analysis]

## Branch 1: [Name]
Strategy: ...
First Steps: ...
Potential: ...
Risks: ...

## Branch 2: [Name]
...

## Branch 3: [Name]
...

## Evaluation Matrix
| Approach | Feasibility | Completeness | Elegance | Total |
|----------|-------------|--------------|----------|-------|
| Branch 1 |     X       |      X       |    X     |   X   |
| Branch 2 |     X       |      X       |    X     |   X   |
| Branch 3 |     X       |      X       |    X     |   X   |

## Selected Approach: [Name]
[Full detailed solution]
```
"""

# Create ToT agent
tot_agent_id = agent_manager.create_agent(
    name="Creative Problem Solver",
    description="Uses Tree of Thought for complex creative problems",
    agent_type="tree_of_thought",
    system_prompt=TOT_SYSTEM_PROMPT,
    llm_config={
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.7,  # Higher for creative exploration
        "max_tokens": 4096
    },
    created_by="admin"
)
```

### 6.3 Advanced ToT with Parallel Execution

For complex problems, Abhikarta can execute ToT branches in parallel:

```python
from abhikarta.workflow import WorkflowEngine, WorkflowDefinition

# Define ToT workflow with parallel branches
tot_workflow = WorkflowDefinition(
    name="Advanced ToT Solver",
    description="Parallel Tree of Thought exploration",
    nodes=[
        {
            "node_id": "decompose",
            "node_type": "llm",
            "config": {
                "prompt": "Decompose this problem into components: {{input}}",
                "model": "gpt-4",
                "temperature": 0.3
            }
        },
        {
            "node_id": "branch_1",
            "node_type": "llm",
            "config": {
                "prompt": """Given: {{decompose.output}}
                
                Generate Solution Approach 1 - The CONSERVATIVE approach.
                Focus on proven methods and reliability.""",
                "model": "gpt-4",
                "temperature": 0.5
            },
            "depends_on": ["decompose"]
        },
        {
            "node_id": "branch_2",
            "node_type": "llm",
            "config": {
                "prompt": """Given: {{decompose.output}}
                
                Generate Solution Approach 2 - The INNOVATIVE approach.
                Think outside the box, propose novel solutions.""",
                "model": "gpt-4",
                "temperature": 0.8
            },
            "depends_on": ["decompose"]
        },
        {
            "node_id": "branch_3",
            "node_type": "llm",
            "config": {
                "prompt": """Given: {{decompose.output}}
                
                Generate Solution Approach 3 - The HYBRID approach.
                Combine elements from different domains.""",
                "model": "gpt-4",
                "temperature": 0.6
            },
            "depends_on": ["decompose"]
        },
        {
            "node_id": "evaluate",
            "node_type": "llm",
            "config": {
                "prompt": """Evaluate these three approaches:
                
                APPROACH 1 (Conservative):
                {{branch_1.output}}
                
                APPROACH 2 (Innovative):
                {{branch_2.output}}
                
                APPROACH 3 (Hybrid):
                {{branch_3.output}}
                
                Score each on Feasibility, Completeness, Elegance (1-10).
                Select the best approach and explain why.""",
                "model": "gpt-4",
                "temperature": 0.2
            },
            "depends_on": ["branch_1", "branch_2", "branch_3"]
        },
        {
            "node_id": "refine",
            "node_type": "llm",
            "config": {
                "prompt": """Based on this evaluation:
                {{evaluate.output}}
                
                Fully develop the selected approach into a complete solution.
                Address any weaknesses identified in the evaluation.""",
                "model": "gpt-4",
                "temperature": 0.4
            },
            "depends_on": ["evaluate"]
        }
    ]
)

# Execute workflow
engine = WorkflowEngine(db_facade)
workflow_id = engine.create_workflow(tot_workflow)
result = engine.execute(workflow_id, input_data={"input": "Design a sustainable city transportation system"})
```

---

## 7. CoT and ToT in Workflows

### 7.1 Adding CoT Nodes to Workflows via Visual Designer

1. Open **Workflow Designer**
2. Drag a **LLM Node** onto the canvas
3. Configure as CoT:
   - **Node Type**: LLM Call
   - **System Prompt**: Include "Think step by step" instruction
   - **Temperature**: 0.2-0.4
   - **Output Parsing**: Enable "Extract Reasoning Steps"

### 7.2 CoT Decision Node

```yaml
# workflow_with_cot.yaml
name: Customer Support with CoT
description: Uses CoT reasoning for complex support decisions

nodes:
  - node_id: analyze_ticket
    node_type: llm
    config:
      system_prompt: |
        Analyze this support ticket using step-by-step reasoning:
        
        1. CATEGORIZE: What type of issue is this?
        2. URGENCY: How urgent is this (Low/Medium/High/Critical)?
        3. COMPLEXITY: Simple fix or requires escalation?
        4. SENTIMENT: How frustrated is the customer?
        5. ACTION: What's the best next step?
        
        Think through each step carefully.
      model: gpt-4
      temperature: 0.3
  
  - node_id: route_ticket
    node_type: condition
    config:
      conditions:
        - expression: "'Critical' in analyze_ticket.output"
          target: escalate_immediately
        - expression: "'escalation' in analyze_ticket.output.lower()"
          target: assign_specialist
        - default: auto_respond
    depends_on: [analyze_ticket]
  
  - node_id: auto_respond
    node_type: llm
    config:
      system_prompt: |
        Generate a helpful response based on this analysis:
        {{analyze_ticket.output}}
        
        Be empathetic and solution-focused.
      model: gpt-3.5-turbo
      temperature: 0.5
    depends_on: [route_ticket]
```

---

## 8. CoT and ToT in Agent Swarms

### 8.1 Master Actor with CoT Decision Making

The Master Actor in a swarm can use CoT to decide which agents to invoke:

```python
from abhikarta.swarm import SwarmOrchestrator, SwarmDefinition, MasterActorConfig

# Define Master Actor with CoT reasoning
master_config = MasterActorConfig(
    llm_config={
        "provider": "anthropic",
        "model": "claude-3-opus",
        "temperature": 0.3
    },
    system_prompt="""You are the coordinator of an AI agent swarm. 
    
When you receive a task, reason through it step by step:

1. UNDERSTAND: What exactly needs to be done?
2. DECOMPOSE: What subtasks are involved?
3. MATCH: Which agents have the right capabilities?
4. SEQUENCE: What order should agents work?
5. DELEGATE: Assign specific tasks to specific agents.

Available agents and their capabilities:
{{available_agents}}

Current swarm state:
{{swarm_state}}

Incoming task:
{{task}}

Think step by step, then output your delegation decision as JSON:
{
    "reasoning": "Your step-by-step reasoning",
    "delegations": [
        {"agent": "agent_name", "task": "specific task", "priority": 1-10}
    ]
}
""",
    decision_format="json"
)

# Create swarm with CoT Master
swarm_def = SwarmDefinition(
    name="Research Swarm with CoT Master",
    master_actor=master_config,
    agents=[
        {"name": "researcher", "capabilities": ["web_search", "summarize"]},
        {"name": "analyst", "capabilities": ["analyze_data", "create_charts"]},
        {"name": "writer", "capabilities": ["write_report", "format_document"]}
    ]
)

orchestrator = SwarmOrchestrator(db_facade)
swarm_id = orchestrator.create_swarm(swarm_def)
```

### 8.2 ToT Swarm for Complex Problems

```python
# Define a ToT swarm where each branch is a different agent team
tot_swarm_def = SwarmDefinition(
    name="ToT Innovation Swarm",
    master_actor=MasterActorConfig(
        system_prompt="""You coordinate a Tree of Thought exploration swarm.

For each problem:
1. Create 3 different approach teams
2. Let each team explore their approach in parallel
3. Evaluate results from all teams
4. Select and refine the best solution

Teams available:
- Team Alpha: Conservative, methodical approach
- Team Beta: Creative, innovative approach  
- Team Gamma: Hybrid, balanced approach

Output format:
{
    "phase": "branch|evaluate|refine",
    "teams": [{"name": "...", "task": "..."}],
    "evaluation": {...}  // only in evaluate phase
}
"""
    ),
    agent_pools=[
        {"name": "Team Alpha", "agents": ["alpha_researcher", "alpha_analyst"], "min": 2, "max": 4},
        {"name": "Team Beta", "agents": ["beta_creative", "beta_innovator"], "min": 2, "max": 4},
        {"name": "Team Gamma", "agents": ["gamma_integrator", "gamma_synthesizer"], "min": 2, "max": 4}
    ]
)
```

---

## 9. Best Practices

### 9.1 When to Use CoT vs ToT

| Scenario | Recommended | Reasoning |
|----------|-------------|-----------|
| Math problems | CoT | Linear, single correct answer |
| Code debugging | CoT | Step-by-step analysis needed |
| Creative writing | ToT | Multiple valid approaches |
| Business strategy | ToT | Explore alternatives |
| Classification | CoT | Explain reasoning |
| Design tasks | ToT | Generate options |
| Fact retrieval | Neither | Direct answer sufficient |

### 9.2 Prompt Engineering Tips

**For CoT:**
```
✅ DO: "Think step by step"
✅ DO: "Show your reasoning"
✅ DO: "Work through this carefully"
✅ DO: Provide structured output format

❌ DON'T: "Be quick"
❌ DON'T: "Just give me the answer"
❌ DON'T: Skip verification step
```

**For ToT:**
```
✅ DO: "Generate 3 different approaches"
✅ DO: "Evaluate each approach on criteria X, Y, Z"
✅ DO: "Select the best and explain why"
✅ DO: Allow higher temperature for branching

❌ DON'T: Ask for single answer immediately
❌ DON'T: Use low temperature for all phases
❌ DON'T: Skip the evaluation phase
```

### 9.3 Temperature Settings

| Phase | Recommended Temperature |
|-------|------------------------|
| Problem decomposition | 0.2 - 0.3 |
| CoT reasoning | 0.2 - 0.4 |
| ToT branching | 0.6 - 0.8 |
| ToT evaluation | 0.1 - 0.3 |
| ToT refinement | 0.3 - 0.5 |

### 9.4 Token Budgeting

CoT and ToT use more tokens. Plan accordingly:

```python
# Estimate token usage
def estimate_tokens(task_complexity: str, method: str) -> int:
    base_tokens = {
        "simple": 500,
        "medium": 1000,
        "complex": 2000
    }[task_complexity]
    
    multiplier = {
        "direct": 1,
        "cot": 2.5,
        "tot": 8  # 3 branches + evaluation + refinement
    }[method]
    
    return int(base_tokens * multiplier)

# Example
tokens_needed = estimate_tokens("complex", "tot")
print(f"Estimated tokens: {tokens_needed}")  # ~16,000 tokens
```

---

## 10. Troubleshooting

### 10.1 Common Issues

**Problem: CoT agent not showing reasoning**
```
Solution: Check system prompt includes explicit instruction to show work.
Add: "You MUST show all intermediate steps. Never skip to the answer."
```

**Problem: ToT branches are too similar**
```
Solution: Increase temperature for branching phase (0.7-0.9).
Add explicit differentiation: "Each approach MUST be fundamentally different."
```

**Problem: ToT taking too long**
```
Solution: 
1. Reduce number of branches (3 → 2)
2. Use faster model for branching (gpt-3.5)
3. Use better model only for evaluation (gpt-4)
4. Set max_tokens limit per branch
```

**Problem: Inconsistent JSON output from ToT**
```
Solution: Use structured output parsing:

from abhikarta.utils import JSONOutputParser

parser = JSONOutputParser(schema={
    "type": "object",
    "properties": {
        "approach_name": {"type": "string"},
        "strategy": {"type": "string"},
        "score": {"type": "number"}
    },
    "required": ["approach_name", "strategy", "score"]
})
```

### 10.2 Debugging CoT/ToT

Enable verbose logging:

```python
import logging
logging.getLogger("abhikarta.agent").setLevel(logging.DEBUG)
logging.getLogger("abhikarta.workflow").setLevel(logging.DEBUG)

# This will show:
# - Full prompts sent to LLM
# - Raw responses received
# - Parsing steps
# - Decision points
```

### 10.3 Performance Monitoring

```python
from abhikarta.utils import ExecutionMetrics

# Wrap execution with metrics
with ExecutionMetrics() as metrics:
    result = executor.execute(agent_id, user_input="...")

print(f"Total tokens: {metrics.total_tokens}")
print(f"Reasoning steps: {metrics.steps_count}")
print(f"Time per step: {metrics.avg_step_time}s")
print(f"Cost estimate: ${metrics.estimated_cost}")
```

---

## Quick Reference Card

### CoT One-Liner
```python
result = agent.execute("Problem: X\n\nThink step by step, then give your final answer.")
```

### ToT One-Liner
```python
result = agent.execute("""Problem: X

Generate 3 approaches. Evaluate each. Select best. Refine into solution.""")
```

### Visual Designer Quick Setup

1. **CoT Agent**: Agent Type = "Chain of Thought", Temp = 0.3
2. **ToT Workflow**: 1 Decompose → 3 Branch → 1 Evaluate → 1 Refine

---

## Further Reading

- [Agent Visual Designer Guide](./help_page/agent_visual_designer)
- [Workflow DAG Execution](./help_page/workflow-dags)
- [Agent Swarms](./help_page/swarms)
- [LLM Providers](./help_page/llm-providers)

---

**Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.**
