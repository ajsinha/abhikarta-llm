# ReAct, Reflect & Hierarchical Agents in Abhikarta-LLM

## A Comprehensive Tutorial Guide

**Version:** 1.4.0  
**Author:** Ashutosh Sinha  
**Copyright © 2025-2030 All Rights Reserved**

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Understanding Agent Patterns](#2-understanding-agent-patterns)
3. [ReAct Agents](#3-react-agents)
4. [Reflect Agents](#4-reflect-agents)
5. [Hierarchical Agents](#5-hierarchical-agents)
6. [Combining Patterns](#6-combining-patterns)
7. [Implementation in Workflows](#7-implementation-in-workflows)
8. [Implementation in Swarms](#8-implementation-in-swarms)
9. [Best Practices](#9-best-practices)
10. [Complete Examples](#10-complete-examples)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Introduction

Abhikarta-LLM supports three powerful agent patterns that enable sophisticated AI reasoning and task execution:

| Pattern | Core Concept | Strength |
|---------|--------------|----------|
| **ReAct** | Reason + Act in interleaved loop | Tool-using problem solving |
| **Reflect** | Self-critique and improvement | Quality and accuracy |
| **Hierarchical** | Manager delegates to workers | Complex multi-agent coordination |

### When to Use Each Pattern

```
Simple tool task → ReAct
Quality-critical task → Reflect (or ReAct + Reflect)
Complex multi-step project → Hierarchical
Large-scale coordination → Hierarchical + Swarms
```

---

## 2. Understanding Agent Patterns

### 2.1 Pattern Comparison

```
┌─────────────────────────────────────────────────────────────────┐
│                        REACT PATTERN                             │
│                                                                   │
│   Thought → Action → Observation → Thought → Action → ...       │
│      ↑                                              │            │
│      └──────────────────────────────────────────────┘            │
│                     (Loop until done)                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       REFLECT PATTERN                            │
│                                                                   │
│   Generate → Critique → Revise → Critique → Revise → Final      │
│              ↑                              │                    │
│              └──────────────────────────────┘                    │
│                   (Iterate until satisfied)                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     HIERARCHICAL PATTERN                         │
│                                                                   │
│                      [Manager Agent]                             │
│                     /       |       \                            │
│                    ↓        ↓        ↓                           │
│              [Worker 1] [Worker 2] [Worker 3]                    │
│                    ↓        ↓        ↓                           │
│                 [Result] [Result] [Result]                       │
│                    \        |        /                           │
│                     ↘       ↓       ↙                            │
│                      [Manager Aggregates]                        │
│                             ↓                                    │
│                       [Final Output]                             │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Pattern Selection Guide

| Task Characteristics | Recommended Pattern |
|----------------------|---------------------|
| Needs external tools (search, APIs) | ReAct |
| Requires iterative refinement | Reflect |
| Has natural subtask decomposition | Hierarchical |
| Quality is paramount | ReAct + Reflect |
| Multiple specialized skills needed | Hierarchical |
| Large-scale with many subtasks | Hierarchical + Swarms |

---

## 3. ReAct Agents

### 3.1 What is ReAct?

ReAct (Reasoning + Acting) interleaves thinking and tool use in a loop:

1. **Thought**: Reason about what to do next
2. **Action**: Execute a tool or take an action
3. **Observation**: Observe the result
4. **Repeat**: Until task is complete

### 3.2 ReAct Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     REACT EXECUTION                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User Query: "What's the weather in Tokyo and NYC?"         │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ ITERATION 1                                          │    │
│  │ Thought: I need to check weather for both cities.   │    │
│  │          Let me start with Tokyo.                    │    │
│  │ Action: weather_api(city="Tokyo")                    │    │
│  │ Observation: Tokyo: 22°C, Sunny                      │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ ITERATION 2                                          │    │
│  │ Thought: Got Tokyo weather. Now I need NYC.          │    │
│  │ Action: weather_api(city="New York")                 │    │
│  │ Observation: New York: 18°C, Cloudy                  │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ ITERATION 3                                          │    │
│  │ Thought: I have both. Ready to answer.               │    │
│  │ Action: Final Answer                                 │    │
│  │ Output: "Tokyo is 22°C and sunny. NYC is 18°C        │    │
│  │         and cloudy."                                 │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Creating a ReAct Agent via Web UI

1. Navigate to **Agents → Create Agent**
2. Fill in details:
   - **Name**: `Research Assistant`
   - **Agent Type**: `ReAct`
3. Configure System Prompt:

```
You are a ReAct agent that solves problems by interleaving reasoning and action.

## Process
For each step, output in this exact format:

Thought: [Your reasoning about what to do next]
Action: [tool_name(param1="value1", param2="value2")]

After receiving an observation, continue:

Thought: [Your reasoning about the observation]
Action: [next action or "Final Answer: [your response]"]

## Rules
1. ALWAYS start with a Thought
2. ALWAYS follow Thought with Action
3. Wait for Observation before next Thought
4. Use "Final Answer:" when you have enough information
5. Be concise in your thoughts

## Available Tools
{{tools}}
```

4. Add Tools:
   - `builtin:web_search`
   - `builtin:calculator`
   - `builtin:web_fetch`

5. Set **Temperature**: `0.3`
6. Save and Publish

### 3.4 ReAct Agent via Code

```python
from abhikarta.agent import AgentManager
from abhikarta.database import DatabaseFacade

db = DatabaseFacade.from_config()
manager = AgentManager(db)

REACT_SYSTEM_PROMPT = """You are a ReAct agent. Solve problems by alternating between thinking and acting.

## Format (MUST follow exactly)

Thought: I need to [reasoning]
Action: tool_name(param="value")

[Wait for Observation]

Thought: Based on the observation, [reasoning]
Action: tool_name(param="value") OR Final Answer: [response]

## Guidelines
- Think before every action
- One action per thought
- Observe results before next thought
- Use Final Answer when ready to respond
- If a tool fails, think about alternatives

## Tools Available
- web_search(query): Search the internet
- calculator(expression): Compute math
- web_fetch(url): Get webpage content
"""

react_agent_id = manager.create_agent(
    name="ReAct Research Agent",
    description="Solves problems using Reasoning + Acting loop",
    agent_type="react",
    system_prompt=REACT_SYSTEM_PROMPT,
    tools=[
        "builtin:web_search",
        "builtin:calculator",
        "builtin:web_fetch"
    ],
    llm_config={
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.3,
        "max_tokens": 2048
    },
    metadata={
        "max_iterations": 10,
        "stop_on_final_answer": True
    },
    created_by="admin"
)

print(f"Created ReAct agent: {react_agent_id}")
```

### 3.5 Running a ReAct Agent

```python
from abhikarta.agent import AgentExecutor

executor = AgentExecutor(db)

result = executor.execute(
    agent_id=react_agent_id,
    user_input="What is the population of France and Germany combined? Calculate per capita GDP if France GDP is $2.8T and Germany GDP is $4.2T.",
    context={}
)

print("=== ReAct Execution ===")
for step in result['steps']:
    print(f"Thought: {step.get('thought')}")
    print(f"Action: {step.get('action')}")
    print(f"Observation: {step.get('observation')}")
    print("---")
print(f"Final: {result['output']}")
```

**Expected Output:**
```
Thought: I need to find the populations of France and Germany, then calculate combined population and per capita GDP.
Action: web_search(query="France population 2024")
Observation: France population: approximately 68 million
---
Thought: Got France population. Now I need Germany's population.
Action: web_search(query="Germany population 2024")
Observation: Germany population: approximately 84 million
---
Thought: Now I can calculate combined population and per capita GDP.
Action: calculator(expression="68000000 + 84000000")
Observation: 152000000
---
Thought: Combined population is 152 million. Now calculate total GDP and per capita.
Action: calculator(expression="(2.8 + 4.2) * 1000000000000 / 152000000")
Observation: 46052.63
---
Thought: I have all the information needed.
Action: Final Answer: Combined population of France and Germany is 152 million. With combined GDP of $7 trillion, the per capita GDP is approximately $46,053.
```

---

## 4. Reflect Agents

### 4.1 What is Reflect?

Reflect agents improve their output through self-critique and revision:

1. **Generate**: Create initial response
2. **Critique**: Analyze weaknesses and errors
3. **Revise**: Improve based on critique
4. **Iterate**: Repeat until quality threshold met

### 4.2 Reflect Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    REFLECT EXECUTION                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Task: "Write a persuasive email about our new product"     │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ GENERATION (v1)                                      │    │
│  │ [Initial draft with basic structure]                 │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ CRITIQUE                                             │    │
│  │ ✗ Opening is weak - doesn't grab attention          │    │
│  │ ✗ Benefits not clearly stated                        │    │
│  │ ✗ Call-to-action is buried                           │    │
│  │ ✓ Tone is appropriate                                │    │
│  │ Score: 5/10                                          │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ REVISION (v2)                                        │    │
│  │ [Improved draft addressing critique points]          │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ CRITIQUE                                             │    │
│  │ ✓ Strong opening hook                                │    │
│  │ ✓ Benefits clearly highlighted                       │    │
│  │ ✓ CTA is prominent                                   │    │
│  │ ✗ Could use social proof                             │    │
│  │ Score: 8/10 (above threshold)                        │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ FINAL OUTPUT                                         │    │
│  │ [Polished email ready for use]                       │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 Creating a Reflect Agent

```python
REFLECT_SYSTEM_PROMPT = """You are a Reflect agent that improves outputs through self-critique.

## Process

### Step 1: GENERATE
Create your initial response to the task.
Format:

    ## Draft v{n}
    [Your content]

### Step 2: CRITIQUE
Analyze your draft critically.
Format:

    ## Critique of v{n}
    
    ### Strengths
    - [What works well]
    
    ### Weaknesses
    - [What needs improvement]
    
    ### Specific Issues
    1. [Issue]: [Location] - [How to fix]
    2. [Issue]: [Location] - [How to fix]
    
    ### Quality Score: X/10

### Step 3: REVISE
If score < 8, create improved version addressing all issues.
If score >= 8, output final version.

## Critique Dimensions
- **Accuracy**: Are facts correct?
- **Completeness**: Is anything missing?
- **Clarity**: Is it easy to understand?
- **Structure**: Is it well-organized?
- **Tone**: Is it appropriate for audience?
- **Conciseness**: Is it too long/short?

## Rules
1. Be genuinely critical - don't just praise
2. Provide specific, actionable feedback
3. Always include quality score
4. Maximum 3 revision cycles
5. Final output should address all major issues
"""

reflect_agent_id = manager.create_agent(
    name="Reflect Writing Agent",
    description="Improves content through iterative self-critique",
    agent_type="reflect",
    system_prompt=REFLECT_SYSTEM_PROMPT,
    llm_config={
        "provider": "anthropic",
        "model": "claude-3-opus",
        "temperature": 0.5,
        "max_tokens": 4096
    },
    metadata={
        "max_iterations": 3,
        "quality_threshold": 8,
        "critique_dimensions": ["accuracy", "clarity", "completeness"]
    },
    created_by="admin"
)
```

### 4.4 Specialized Reflect Agents

#### Code Review Reflect Agent

```python
CODE_REFLECT_PROMPT = """You are a code review Reflect agent.

## Critique Dimensions for Code
1. **Correctness**: Does it work as intended?
2. **Efficiency**: Is it optimally performant?
3. **Readability**: Is it easy to understand?
4. **Maintainability**: Is it easy to modify?
5. **Security**: Are there vulnerabilities?
6. **Best Practices**: Does it follow conventions?

## Format

### Draft v{n}
    [code block here]

### Code Critique
| Dimension | Score | Issues |
|-----------|-------|--------|
| Correctness | X/10 | [issues] |
| Efficiency | X/10 | [issues] |
| Readability | X/10 | [issues] |
| ... | ... | ... |

**Overall: X/10**

### Revision Notes
[What to fix in next version]
"""
```

#### Research Reflect Agent

```python
RESEARCH_REFLECT_PROMPT = """You are a research quality Reflect agent.

## Critique Dimensions for Research
1. **Source Quality**: Are sources credible?
2. **Coverage**: Is the topic fully explored?
3. **Objectivity**: Are multiple perspectives included?
4. **Recency**: Is information current?
5. **Accuracy**: Are facts verified?
6. **Citations**: Are claims properly attributed?

## Critique Format
For each claim, evaluate:
- Source reliability (High/Medium/Low/Unknown)
- Verification status (Verified/Unverified/Contested)
- Recency (Current/Dated/Historical)

Flag any claims that need additional verification.
"""
```

---

## 5. Hierarchical Agents

### 5.1 What is Hierarchical?

Hierarchical agents use a manager-worker structure:

- **Manager Agent**: Decomposes tasks, delegates, aggregates results
- **Worker Agents**: Execute specific subtasks with specialized skills
- **Communication**: Manager coordinates all worker interactions

### 5.2 Hierarchical Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  HIERARCHICAL EXECUTION                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Task: "Create a market analysis report for EV industry"    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              MANAGER AGENT                           │    │
│  │  "I'll decompose this into research, analysis,       │    │
│  │   and writing subtasks"                              │    │
│  └─────────────────────────────────────────────────────┘    │
│              ↓              ↓              ↓                 │
│        [Delegate]     [Delegate]     [Delegate]              │
│              ↓              ↓              ↓                 │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐   │
│  │ RESEARCHER     │ │ ANALYST        │ │ WRITER         │   │
│  │ "Gather EV     │ │ "Analyze       │ │ "Draft         │   │
│  │  market data"  │ │  trends"       │ │  report"       │   │
│  └───────┬────────┘ └───────┬────────┘ └───────┬────────┘   │
│          ↓                  ↓                  ↓             │
│     [Market Data]      [Analysis]         [Draft]           │
│          ↓                  ↓                  ↓             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              MANAGER AGGREGATES                      │    │
│  │  "Combining research, analysis, and draft into      │    │
│  │   final comprehensive report"                        │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                   │
│                   [Final Report]                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 Creating Hierarchical Agents

#### Step 1: Define Worker Agents

```python
# Research Worker
researcher_id = manager.create_agent(
    name="Research Worker",
    agent_type="react",
    system_prompt="""You are a research specialist. 
Your job is to gather information on assigned topics.

## Capabilities
- Web search for current information
- Fetch and read web pages
- Extract key facts and data

## Output Format
Always structure your research as:

    ## Research: [Topic]
    
    ### Key Findings
    1. [Finding with source]
    2. [Finding with source]
    
    ### Data Points
    - [Metric]: [Value] (Source: [link])
    
    ### Sources
    - [Source 1]
    - [Source 2]
""",
    tools=["builtin:web_search", "builtin:web_fetch"],
    llm_config={"provider": "openai", "model": "gpt-4", "temperature": 0.3},
    created_by="admin"
)

# Analysis Worker
analyst_id = manager.create_agent(
    name="Analysis Worker",
    agent_type="chain_of_thought",
    system_prompt="""You are a data analyst specialist.
Your job is to analyze data and identify patterns.

## Capabilities
- Statistical analysis
- Trend identification
- Comparative analysis

## Output Format

    ## Analysis: [Topic]
    
    ### Key Insights
    1. [Insight with supporting data]
    
    ### Trends
    - [Trend description]
    
    ### Recommendations
    - [Actionable recommendation]
""",
    tools=["builtin:calculator", "builtin:data_transform"],
    llm_config={"provider": "openai", "model": "gpt-4", "temperature": 0.3},
    created_by="admin"
)

# Writer Worker
writer_id = manager.create_agent(
    name="Writer Worker",
    agent_type="reflect",
    system_prompt="""You are a professional writer.
Your job is to create clear, compelling content.

## Capabilities
- Report writing
- Executive summaries
- Data visualization descriptions

## Quality Standards
- Clear and concise
- Well-structured
- Professional tone
- Data-driven
""",
    tools=["builtin:file_write"],
    llm_config={"provider": "anthropic", "model": "claude-3-opus", "temperature": 0.5},
    created_by="admin"
)
```

#### Step 2: Define Manager Agent

```python
MANAGER_SYSTEM_PROMPT = """You are a Manager Agent coordinating a team of specialists.

## Your Team
- **Researcher**: Gathers information (web search, data collection)
- **Analyst**: Analyzes data, finds patterns, generates insights
- **Writer**: Creates polished reports and documents

## Your Responsibilities
1. Decompose complex tasks into subtasks
2. Assign subtasks to appropriate workers
3. Review worker outputs
4. Request revisions if needed
5. Aggregate results into final deliverable

## Delegation Format

    DELEGATE TO: [Worker Name]
    TASK: [Specific task description]
    CONTEXT: [Any relevant context from previous workers]
    EXPECTED OUTPUT: [What you need from them]

## Aggregation Format
After all workers complete:

    AGGREGATING RESULTS
    
    From Researcher:
    [Summary of key findings]
    
    From Analyst:
    [Summary of key insights]
    
    From Writer:
    [Summary of draft]
    
    FINAL SYNTHESIS:
    [Your integrated final output]

## Rules
1. Never do worker tasks yourself - always delegate
2. Be specific in task assignments
3. Ensure workers have needed context
4. Verify quality before accepting outputs
5. Request revisions if outputs are inadequate
"""

manager_agent_id = manager.create_agent(
    name="Project Manager",
    agent_type="hierarchical",
    system_prompt=MANAGER_SYSTEM_PROMPT,
    llm_config={
        "provider": "anthropic",
        "model": "claude-3-opus",
        "temperature": 0.3
    },
    metadata={
        "workers": [researcher_id, analyst_id, writer_id],
        "max_delegation_depth": 2,
        "require_all_workers": False
    },
    created_by="admin"
)
```

### 5.4 Hierarchical Execution

```python
from abhikarta.agent import HierarchicalExecutor

# Initialize with manager and workers
h_executor = HierarchicalExecutor(
    db,
    manager_id=manager_agent_id,
    worker_ids=[researcher_id, analyst_id, writer_id]
)

result = h_executor.execute(
    user_input="""Create a comprehensive market analysis report for the 
    electric vehicle industry in North America. Include market size, 
    key players, trends, and 5-year outlook.""",
    context={
        "output_format": "markdown",
        "max_pages": 10
    }
)

print("=== Hierarchical Execution ===")
print(f"Manager delegations: {len(result['delegations'])}")
for d in result['delegations']:
    print(f"  → {d['worker']}: {d['task'][:50]}...")
print(f"\nFinal output length: {len(result['output'])} chars")
```

### 5.5 Advanced Hierarchical Patterns

#### Multi-Level Hierarchy

```python
# Level 1: Executive Manager
# Level 2: Department Managers  
# Level 3: Workers

executive_manager = manager.create_agent(
    name="Executive Manager",
    agent_type="hierarchical",
    system_prompt="""You manage department managers.
Delegate high-level objectives to:
- Research Manager (for all information gathering)
- Analysis Manager (for all data analysis)
- Delivery Manager (for all outputs)
""",
    metadata={
        "workers": [research_manager_id, analysis_manager_id, delivery_manager_id],
        "hierarchy_level": 1
    },
    created_by="admin"
)

research_manager = manager.create_agent(
    name="Research Manager",
    agent_type="hierarchical",
    system_prompt="""You manage research workers.
Delegate specific research tasks to:
- Web Researcher
- Database Researcher  
- Expert Interviewer
""",
    metadata={
        "workers": [web_researcher_id, db_researcher_id, interviewer_id],
        "hierarchy_level": 2,
        "parent": executive_manager_id
    },
    created_by="admin"
)
```

---

## 6. Combining Patterns

### 6.1 ReAct + Reflect

Use ReAct for tool operations, Reflect for quality:

```python
REACT_REFLECT_PROMPT = """You are a ReAct agent with Reflect capability.

## Phase 1: ReAct (Information Gathering)
Use Thought → Action → Observation loop to gather information.

## Phase 2: Reflect (Quality Improvement)
Once you have all information, enter Reflect mode:
1. Draft your response
2. Critique it
3. Revise until quality >= 8/10

## Mode Switching
After Final Answer in ReAct, switch to Reflect:

    [ENTERING REFLECT MODE]
    Draft v1: [your initial response]
    Critique: [self-evaluation]
    ...
"""
```

### 6.2 Hierarchical + ReAct Workers

```python
# Manager delegates, workers use ReAct
worker_config = {
    "agent_type": "react",
    "tools": ["web_search", "calculator"],
    "max_iterations": 5
}

hierarchical_react_system = {
    "manager": {
        "type": "hierarchical",
        "delegates_to": ["researcher", "analyst"]
    },
    "researcher": {
        "type": "react",
        "tools": ["web_search", "web_fetch"]
    },
    "analyst": {
        "type": "react",
        "tools": ["calculator", "data_transform"]
    }
}
```

### 6.3 Full Stack: Hierarchical + ReAct + Reflect

```python
FULL_STACK_PROMPT = """You are an advanced agent combining all patterns.

## Architecture

    [Manager - Hierarchical]
        ├── [Researcher - ReAct]
        │       └── Uses tools to gather info
        ├── [Analyst - ReAct]  
        │       └── Uses tools to analyze
        └── [Writer - Reflect]
                └── Iterates on quality

## Execution Flow
1. Manager decomposes task (Hierarchical)
2. Research workers gather data (ReAct)
3. Analysis workers process data (ReAct)
4. Writer creates and refines output (Reflect)
5. Manager aggregates and reviews (Hierarchical)
"""
```

---

## 7. Implementation in Workflows

### 7.1 ReAct Workflow Node

```json
{
  "name": "ReAct Research Workflow",
  "nodes": [
    {
      "node_id": "react_research",
      "node_type": "agent",
      "config": {
        "agent_type": "react",
        "tools": ["web_search", "web_fetch", "calculator"],
        "max_iterations": 10,
        "system_prompt": "Use ReAct pattern to research: {{input.topic}}\n\nThought: [reasoning]\nAction: [tool(params)]\n[Observation]\n...\nAction: Final Answer: [comprehensive research]"
      }
    }
  ]
}
```

### 7.2 Reflect Workflow Node

```json
{
  "name": "Reflect Quality Workflow",
  "nodes": [
    {
      "node_id": "initial_draft",
      "node_type": "llm",
      "config": {
        "prompt": "Write a first draft about {{input.topic}}",
        "model": "gpt-4",
        "temperature": 0.7
      }
    },
    {
      "node_id": "critique",
      "node_type": "llm",
      "config": {
        "prompt": "Critique this draft:\n{{initial_draft.output}}\n\nRate each dimension 1-10:\n- Accuracy\n- Clarity\n- Completeness\n\nOverall score and specific improvements needed.",
        "model": "gpt-4",
        "temperature": 0.3
      },
      "depends_on": ["initial_draft"]
    },
    {
      "node_id": "revise",
      "node_type": "llm",
      "config": {
        "prompt": "Revise this draft based on critique:\n\nDRAFT: {{initial_draft.output}}\nCRITIQUE: {{critique.output}}\n\nAddress all issues identified.",
        "model": "gpt-4",
        "temperature": 0.5
      },
      "depends_on": ["critique"]
    }
  ]
}
```

### 7.3 Hierarchical Workflow

```json
{
  "name": "Hierarchical Analysis Workflow",
  "nodes": [
    {
      "node_id": "decompose",
      "node_type": "llm",
      "config": {
        "prompt": "Decompose this task into subtasks for specialists:\n{{input.task}}\n\nAvailable workers: Researcher, Analyst, Writer\n\nOutput JSON:\n{\"subtasks\": [{\"worker\": \"...\", \"task\": \"...\", \"priority\": 1}]}",
        "output_format": "json"
      }
    },
    {
      "node_id": "research_task",
      "node_type": "agent",
      "config": {
        "agent_id": "{{researcher_agent_id}}",
        "input": "{{decompose.output.subtasks[0].task}}"
      },
      "depends_on": ["decompose"],
      "condition": "'Researcher' in decompose.output.subtasks[0].worker"
    },
    {
      "node_id": "analysis_task",
      "node_type": "agent",
      "config": {
        "agent_id": "{{analyst_agent_id}}",
        "input": "Analyze this data:\n{{research_task.output}}"
      },
      "depends_on": ["research_task"]
    },
    {
      "node_id": "aggregate",
      "node_type": "llm",
      "config": {
        "prompt": "Aggregate these results into final output:\n\nResearch: {{research_task.output}}\nAnalysis: {{analysis_task.output}}"
      },
      "depends_on": ["analysis_task"]
    }
  ]
}
```

---

## 8. Implementation in Swarms

### 8.1 ReAct Swarm Workers

```python
from abhikarta.swarm import SwarmDefinition, MasterActorConfig

react_swarm = SwarmDefinition(
    name="ReAct Research Swarm",
    master_actor=MasterActorConfig(
        system_prompt="""Coordinate ReAct workers for research tasks.
Each worker uses Thought-Action-Observation loops.
Aggregate their findings into comprehensive results.""",
        llm_config={"provider": "anthropic", "model": "claude-3-opus"}
    ),
    agent_pools=[
        {
            "name": "WebResearchers",
            "agent_type": "react",
            "tools": ["web_search", "web_fetch"],
            "min_instances": 2,
            "max_instances": 5
        },
        {
            "name": "DataAnalysts",
            "agent_type": "react", 
            "tools": ["calculator", "data_transform"],
            "min_instances": 1,
            "max_instances": 3
        }
    ]
)
```

### 8.2 Hierarchical Swarm

```python
hierarchical_swarm = SwarmDefinition(
    name="Hierarchical Project Swarm",
    master_actor=MasterActorConfig(
        system_prompt="""You are the project director.
        
Manage department leads:
- Research Lead → manages research workers
- Analysis Lead → manages analyst workers
- Delivery Lead → manages writer workers

Delegate high-level objectives to leads.
Leads will further delegate to their workers.""",
        llm_config={"provider": "anthropic", "model": "claude-3-opus"}
    ),
    agent_pools=[
        {
            "name": "ResearchLead",
            "agent_type": "hierarchical",
            "subordinates": ["WebResearcher", "DBResearcher"],
            "min_instances": 1,
            "max_instances": 1
        },
        {
            "name": "WebResearcher",
            "agent_type": "react",
            "tools": ["web_search"],
            "min_instances": 2,
            "max_instances": 4
        },
        {
            "name": "AnalysisLead",
            "agent_type": "hierarchical",
            "subordinates": ["Analyst"],
            "min_instances": 1,
            "max_instances": 1
        },
        {
            "name": "Analyst",
            "agent_type": "react",
            "tools": ["calculator"],
            "min_instances": 1,
            "max_instances": 3
        }
    ]
)
```

---

## 9. Best Practices

### 9.1 Pattern Selection Matrix

| Scenario | Pattern | Why |
|----------|---------|-----|
| API calls needed | ReAct | Tool-action loop |
| Quality critical | Reflect | Self-improvement |
| Many specialists needed | Hierarchical | Delegation |
| Research + Writing | ReAct → Reflect | Gather then polish |
| Large project | Hierarchical + both | Full orchestration |

### 9.2 Common Anti-Patterns

❌ **ReAct Without Stop Condition**
```python
# BAD: Can loop forever
max_iterations = 100

# GOOD: Reasonable limit with fallback
max_iterations = 10
fallback_response = "Unable to complete within iteration limit"
```

❌ **Reflect Without Quality Threshold**
```python
# BAD: May never finish
while not satisfied:
    revise()

# GOOD: Clear exit criteria
max_revisions = 3
quality_threshold = 8
```

❌ **Hierarchical Without Clear Roles**
```python
# BAD: Overlapping responsibilities
workers = ["GeneralWorker1", "GeneralWorker2"]

# GOOD: Specialized roles
workers = ["Researcher", "Analyst", "Writer"]
```

### 9.3 Temperature Guidelines

| Pattern | Phase | Temperature | Reason |
|---------|-------|-------------|--------|
| ReAct | All | 0.2-0.4 | Focused tool selection |
| Reflect | Generate | 0.5-0.7 | Creative initial draft |
| Reflect | Critique | 0.2-0.3 | Objective evaluation |
| Reflect | Revise | 0.4-0.5 | Balanced improvement |
| Hierarchical | Manager | 0.3 | Consistent delegation |
| Hierarchical | Workers | Varies | Depends on task |

---

## 10. Complete Examples

### 10.1 Full ReAct Example

```python
from abhikarta.agent import AgentManager, AgentExecutor
from abhikarta.database import DatabaseFacade

db = DatabaseFacade.from_config()
manager = AgentManager(db)
executor = AgentExecutor(db)

# Create ReAct agent
react_agent = manager.create_agent(
    name="Market Analyst",
    agent_type="react",
    system_prompt="""You solve problems using Thought-Action-Observation.

Thought: [your reasoning]
Action: tool_name(params) OR Final Answer: [response]

Tools: web_search, calculator, web_fetch""",
    tools=["builtin:web_search", "builtin:calculator", "builtin:web_fetch"],
    llm_config={"provider": "openai", "model": "gpt-4", "temperature": 0.3},
    created_by="admin"
)

# Execute
result = executor.execute(
    agent_id=react_agent,
    user_input="What is Apple's current market cap and P/E ratio?",
    context={}
)

print(result['output'])
```

### 10.2 Full Reflect Example

```python
# Create Reflect agent for writing
reflect_agent = manager.create_agent(
    name="Content Improver",
    agent_type="reflect",
    system_prompt="""Improve content through self-critique.

1. DRAFT: Write initial version
2. CRITIQUE: Score 1-10 on clarity, accuracy, engagement
3. REVISE: Fix issues if score < 8
4. REPEAT: Until score >= 8 or 3 iterations

Output format:
## Draft v{n}
[content]

## Critique
- Clarity: X/10
- Accuracy: X/10  
- Engagement: X/10
- Issues: [list]
- Overall: X/10

## Revision Notes
[what to improve]""",
    llm_config={"provider": "anthropic", "model": "claude-3-opus", "temperature": 0.5},
    created_by="admin"
)

result = executor.execute(
    agent_id=reflect_agent,
    user_input="Write a compelling product description for an AI coding assistant",
    context={"max_length": 200}
)

print(result['output'])
```

### 10.3 Full Hierarchical Example

```python
# Create worker agents
researcher = manager.create_agent(
    name="Researcher",
    agent_type="react",
    system_prompt="Research assigned topics using web search.",
    tools=["builtin:web_search"],
    llm_config={"provider": "openai", "model": "gpt-4", "temperature": 0.3},
    created_by="admin"
)

writer = manager.create_agent(
    name="Writer",
    agent_type="reflect",
    system_prompt="Write and refine content through self-critique.",
    llm_config={"provider": "anthropic", "model": "claude-3-opus", "temperature": 0.5},
    created_by="admin"
)

# Create manager
project_manager = manager.create_agent(
    name="Project Manager",
    agent_type="hierarchical",
    system_prompt="""Manage research and writing tasks.

Workers:
- Researcher: For information gathering
- Writer: For content creation

Decompose tasks, delegate appropriately, aggregate results.""",
    llm_config={"provider": "anthropic", "model": "claude-3-opus", "temperature": 0.3},
    metadata={"workers": [researcher, writer]},
    created_by="admin"
)

# Execute hierarchical task
from abhikarta.agent import HierarchicalExecutor

h_exec = HierarchicalExecutor(db, manager_id=project_manager, worker_ids=[researcher, writer])

result = h_exec.execute(
    user_input="Create a blog post about the future of renewable energy",
    context={}
)

print(result['output'])
```

---

## 11. Troubleshooting

### 11.1 ReAct Issues

**Problem: Agent loops without progress**
```
Solution:
1. Add max_iterations limit
2. Check tool availability
3. Add "I cannot find this information" as valid final answer
4. Enable verbose logging to see loop
```

**Problem: Agent uses wrong tool**
```
Solution:
1. Improve tool descriptions
2. Add examples in system prompt
3. Reduce temperature
4. Be more specific in tool names
```

### 11.2 Reflect Issues

**Problem: Agent never satisfied with output**
```
Solution:
1. Set quality_threshold (e.g., 7/10)
2. Limit max_revisions (e.g., 3)
3. Add "good enough" criteria
4. Use separate critique model
```

**Problem: Critiques are too lenient**
```
Solution:
1. Add "be harsh" instruction
2. Require specific issue identification
3. Use lower temperature for critique
4. Provide critique examples
```

### 11.3 Hierarchical Issues

**Problem: Manager does work instead of delegating**
```
Solution:
1. Add explicit "never do worker tasks yourself"
2. List worker capabilities clearly
3. Add delegation format requirement
4. Check worker availability
```

**Problem: Workers don't have enough context**
```
Solution:
1. Manager passes full context in delegation
2. Enable context sharing between workers
3. Add "what you need to know" section
4. Use shared memory/scratchpad
```

### 11.4 Debugging

```python
import logging

# Enable pattern-specific logging
logging.getLogger("abhikarta.agent.react").setLevel(logging.DEBUG)
logging.getLogger("abhikarta.agent.reflect").setLevel(logging.DEBUG)
logging.getLogger("abhikarta.agent.hierarchical").setLevel(logging.DEBUG)

# Shows:
# - ReAct: Each thought-action-observation cycle
# - Reflect: Each draft-critique-revise iteration
# - Hierarchical: Each delegation and aggregation
```

---

## Quick Reference Card

### ReAct One-Liner
```python
# Thought → Action → Observation → Repeat
agent_type="react", tools=[...], max_iterations=10
```

### Reflect One-Liner
```python
# Generate → Critique → Revise → Repeat
agent_type="reflect", quality_threshold=8, max_revisions=3
```

### Hierarchical One-Liner
```python
# Manager → Delegate → Workers → Aggregate
agent_type="hierarchical", workers=[worker_ids], max_depth=2
```

---

## Further Reading

- [Chain of Thought & Tree of Thought](/help/cot-tot)
- [Goal-Based Agents](/help/goal-based-agents)
- [Agent Swarms](/help/swarms)
- [Workflow DAGs](/help/workflow-dags)

---

**Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.**
