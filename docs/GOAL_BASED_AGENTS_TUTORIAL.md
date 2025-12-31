# Goal-Based Agents in Abhikarta-LLM

## A Comprehensive Tutorial: Autonomous, Planning, and Learning Agents

**Version:** 1.4.6  
**Author:** Ashutosh Sinha  
**Copyright © 2025-2030 All Rights Reserved**

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Understanding Goal-Based Agents](#2-understanding-goal-based-agents)
3. [Setting Up Your Environment](#3-setting-up-your-environment)
4. [Creating Goal-Based Agents](#4-creating-goal-based-agents)
5. [Autonomous Action](#5-autonomous-action)
6. [Planning & Reasoning](#6-planning--reasoning)
7. [Learning & Adaptation](#7-learning--adaptation)
8. [Goal-Based Workflows](#8-goal-based-workflows)
9. [Goal-Based Swarms](#9-goal-based-swarms)
10. [Best Practices](#10-best-practices)
11. [Complete Examples](#11-complete-examples)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Introduction

Goal-Based Agents represent a significant advancement over simple rule-based systems. Instead of following rigid if-then rules, they:

- **Define objectives** and work backward to determine actions
- **Plan autonomously** without constant human guidance
- **Adapt strategies** when initial approaches fail
- **Learn from experience** to improve over time

### Agent Type Comparison

| Agent Type | Decision Making | Complexity | Use Case |
|------------|-----------------|------------|----------|
| **Rule-Based** | Fixed rules | Low | Simple automation |
| **Goal-Based** | Objective-driven | Medium | Complex tasks |
| **Utility-Based** | Maximize utility function | High | Optimization |
| **Learning** | Experience-driven | Very High | Evolving tasks |

Abhikarta-LLM provides native support for Goal-Based Agents through:

- **Plan-and-Execute Agent Type**: Built-in goal decomposition
- **ReAct Pattern**: Reasoning + Acting loop
- **Memory Systems**: Context retention across sessions
- **Tool Integration**: Autonomous tool selection and usage
- **Swarm Choreography**: Multi-agent goal pursuit

---

## 2. Understanding Goal-Based Agents

### 2.1 Core Components

A Goal-Based Agent in Abhikarta consists of:

```
┌─────────────────────────────────────────────────────────────┐
│                    GOAL-BASED AGENT                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │    GOALS     │    │    STATE     │    │   MEMORY     │  │
│  │  (Objectives)│    │  (Current)   │    │ (Experience) │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                   │                   │           │
│         └─────────┬─────────┴─────────┬─────────┘           │
│                   │                   │                      │
│                   ▼                   ▼                      │
│         ┌──────────────┐    ┌──────────────┐                │
│         │   PLANNER    │───▶│   EXECUTOR   │                │
│         │ (Reasoning)  │    │  (Actions)   │                │
│         └──────────────┘    └──────┬───────┘                │
│                                    │                         │
│                   ┌────────────────┼────────────────┐       │
│                   ▼                ▼                ▼       │
│              ┌────────┐      ┌────────┐      ┌────────┐    │
│              │ Tool 1 │      │ Tool 2 │      │ Tool N │    │
│              └────────┘      └────────┘      └────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Goal Types

**Terminal Goals**: Final objectives to achieve
```
"Research and write a comprehensive report on renewable energy trends"
```

**Instrumental Goals**: Sub-goals that help achieve terminal goals
```
1. Search for recent renewable energy data
2. Analyze market trends
3. Identify key players
4. Draft report sections
5. Compile final report
```

**Maintenance Goals**: Ongoing objectives
```
"Keep the report under 5000 words"
"Cite all sources"
"Maintain professional tone"
```

---

## 3. Setting Up Your Environment

### 3.1 Prerequisites

```bash
# Install Abhikarta-LLM
pip install abhikarta-llm

# Required for goal-based agents
pip install langchain>=0.1.0
pip install langgraph>=0.1.0  # For plan-and-execute
```

### 3.2 Configuration

Update `abhikarta.properties`:

```properties
# LLM for planning (needs strong reasoning)
llm.planning.provider=anthropic
llm.planning.model=claude-3-opus
llm.planning.temperature=0.3

# LLM for execution (can be faster/cheaper)
llm.execution.provider=openai
llm.execution.model=gpt-4-turbo
llm.execution.temperature=0.5

# Memory settings
memory.enabled=true
memory.type=persistent
memory.max_entries=1000

# Planning settings
planning.max_iterations=10
planning.replanning_threshold=3
```

### 3.3 Verify Setup

```python
from abhikarta.agent import AgentManager
from abhikarta.database import DatabaseFacade

db = DatabaseFacade.from_config()
manager = AgentManager(db)

# Check available agent types
print(manager.get_agent_types())
# ['react', 'chain_of_thought', 'plan_and_execute', 'goal_based', 'custom']
```

---

## 4. Creating Goal-Based Agents

### 4.1 Via Web UI

1. Navigate to **Agents → Create Agent**
2. Fill in basic details:
   - **Name**: `Research Assistant`
   - **Description**: `Goal-based agent for research tasks`
   - **Agent Type**: `Plan and Execute`

3. Configure the Goal-Based System Prompt:

```
You are an autonomous research assistant with goal-based reasoning.

## Your Capabilities
- Break complex goals into actionable steps
- Use tools autonomously to gather information
- Adjust plans when obstacles arise
- Learn from past attempts to improve

## Goal Processing Framework

### Phase 1: GOAL ANALYSIS
When given a goal, analyze:
1. What is the terminal objective?
2. What constraints exist?
3. What resources/tools are available?
4. What is the success criteria?

### Phase 2: PLAN GENERATION
Create a step-by-step plan:
1. Decompose goal into sub-goals
2. Identify dependencies between steps
3. Estimate effort for each step
4. Identify potential failure points

### Phase 3: EXECUTION
For each step:
1. Select appropriate tool(s)
2. Execute action
3. Evaluate result
4. Adjust plan if needed

### Phase 4: REFLECTION
After completion:
1. Did we achieve the goal?
2. What worked well?
3. What could be improved?
4. What did we learn?

Always show your reasoning at each phase.
```

4. Add Tools:
   - `builtin:web_search`
   - `builtin:web_fetch`
   - `builtin:file_write`
   - `builtin:calculator`

5. Set LLM Parameters:
   - **Temperature**: `0.4`
   - **Max Tokens**: `4096`

6. Save and Publish

### 4.2 Via Code

```python
from abhikarta.agent import AgentManager

GOAL_BASED_PROMPT = """You are a Goal-Based Agent with autonomous planning capabilities.

## Core Directives
1. GOAL FIRST: Always clarify the goal before acting
2. PLAN BEFORE ACT: Create a plan, then execute
3. MONITOR PROGRESS: Track completion of sub-goals
4. ADAPT: Modify plans when circumstances change
5. REFLECT: Learn from successes and failures

## Goal Decomposition Template
```
TERMINAL GOAL: [Main objective]
├── SUB-GOAL 1: [First major step]
│   ├── Task 1.1: [Specific action]
│   └── Task 1.2: [Specific action]
├── SUB-GOAL 2: [Second major step]
│   ├── Task 2.1: [Specific action]
│   └── Task 2.2: [Specific action]
└── SUB-GOAL N: [Final steps]
    └── Task N.1: [Specific action]
```

## Execution Protocol
For each task:
1. STATE: Current situation
2. GOAL: What this task achieves
3. ACTION: Tool or method to use
4. RESULT: Outcome of action
5. NEXT: What follows based on result

## Replanning Triggers
- Task failure after 2 attempts
- New information changes assumptions
- Resource constraints discovered
- Better approach identified
"""

agent_id = manager.create_agent(
    name="Goal-Based Research Agent",
    description="Autonomous agent that plans and executes research goals",
    agent_type="plan_and_execute",
    system_prompt=GOAL_BASED_PROMPT,
    tools=[
        "builtin:web_search",
        "builtin:web_fetch",
        "builtin:file_write",
        "builtin:text_summarize",
        "builtin:calculator"
    ],
    llm_config={
        "provider": "anthropic",
        "model": "claude-3-opus",
        "temperature": 0.4,
        "max_tokens": 4096
    },
    metadata={
        "max_iterations": 15,
        "replanning_enabled": True,
        "memory_enabled": True
    },
    created_by="admin"
)

print(f"Created goal-based agent: {agent_id}")
```

---

## 5. Autonomous Action

Autonomous Action means the agent can break down goals, select tools, and take actions without constant human input.

### 5.1 Tool Selection Logic

Teach your agent to autonomously select tools:

```python
AUTONOMOUS_TOOL_SELECTION_PROMPT = """
## Autonomous Tool Selection

When you need to take action, follow this decision tree:

### Information Gathering
- Need current information? → web_search
- Need full page content? → web_fetch
- Need to read a file? → file_read
- Need structured data? → database_query

### Data Processing  
- Need calculations? → calculator
- Need text analysis? → text_summarize / text_extract
- Need data transformation? → data_transform

### Output Generation
- Need to save results? → file_write
- Need to send notification? → send_notification
- Need to create report? → report_generator

### Decision Criteria
Choose tools based on:
1. Task requirements (what needs to be done)
2. Data format (text, numbers, structured)
3. Output needs (temporary vs persistent)
4. Efficiency (minimize API calls)

NEVER ask the user which tool to use - decide autonomously based on context.
"""
```

### 5.2 Action Execution with Fallbacks

```python
from abhikarta.agent import AgentExecutor

# Configure executor with autonomous retry
executor = AgentExecutor(
    db_facade,
    config={
        "max_retries": 3,
        "retry_strategy": "exponential_backoff",
        "fallback_tools": {
            "web_search": ["web_fetch", "cached_search"],
            "database_query": ["file_read", "api_call"]
        },
        "autonomous_mode": True
    }
)

# Execute with a goal
result = executor.execute(
    agent_id=agent_id,
    user_input="""
    GOAL: Find the top 5 AI companies by market cap and create a comparison table.
    
    CONSTRAINTS:
    - Use only 2024 data
    - Include revenue and employee count
    - Save result to a file
    """,
    context={
        "output_format": "markdown_table",
        "max_companies": 5
    }
)
```

### 5.3 Strategy Adjustment

Configure your agent to adjust strategies when plans fail:

```python
ADAPTIVE_STRATEGY_PROMPT = """
## Strategy Adjustment Protocol

When an action fails, follow this recovery process:

### Level 1: Retry with Variation
- Same tool, different parameters
- Example: web_search("AI companies 2024") → web_search("artificial intelligence firms market cap")

### Level 2: Alternative Tool
- Different tool, same goal
- Example: web_search fails → web_fetch specific URL

### Level 3: Decompose Further
- Break task into smaller pieces
- Example: "Find all info" → "Find revenue" then "Find employees"

### Level 4: Replan
- Reconsider the entire approach
- Generate new plan from current state

### Failure Response Template

    FAILURE DETECTED
    - Action: [what was attempted]
    - Error: [what went wrong]
    - Analysis: [why it failed]
    - Recovery: [Level 1/2/3/4]
    - Next Action: [adjusted approach]

After 3 failures at Level 4, report to user with:
1. What was accomplished
2. What couldn't be done
3. Recommended next steps
"""
```

---

## 6. Planning & Reasoning

### 6.1 Hierarchical Planning

```python
HIERARCHICAL_PLANNING_PROMPT = """
## Hierarchical Goal Planning

### Step 1: Goal Hierarchy Construction
Given a goal, create a hierarchy:

    MISSION: [Ultimate purpose]
    └── GOAL: [What success looks like]
        ├── OBJECTIVE 1: [Major milestone]
        │   ├── Task 1.1: [Actionable item]
        │   ├── Task 1.2: [Actionable item]
        │   └── Checkpoint: [How to verify]
        ├── OBJECTIVE 2: [Major milestone]
        │   ├── Task 2.1: [Actionable item]
        │   └── Checkpoint: [How to verify]
        └── SUCCESS CRITERIA: [How to measure completion]

### Step 2: Dependency Analysis
Identify which tasks depend on others:
- Task 2.1 requires Task 1.2 (sequential)
- Task 1.1 and 1.2 can run in parallel
- Task 3.1 requires all of Objective 1 (milestone dependency)

### Step 3: Critical Path
Identify the longest chain of dependencies - this is your critical path.
Prioritize critical path tasks.

### Step 4: Resource Allocation
For each task, identify:
- Required tools
- Estimated time/tokens
- Potential blockers
- Fallback options
"""

# Create planning-focused agent
planner_agent = manager.create_agent(
    name="Strategic Planner",
    agent_type="plan_and_execute",
    system_prompt=HIERARCHICAL_PLANNING_PROMPT,
    llm_config={
        "provider": "anthropic",
        "model": "claude-3-opus",
        "temperature": 0.3  # Lower for consistent planning
    },
    created_by="admin"
)
```

### 6.2 State-Space Reasoning

Teach agents to reason about current vs goal states:

```python
STATE_SPACE_REASONING_PROMPT = """
## State-Space Reasoning

### Current State Assessment
Before planning, assess:

    CURRENT STATE:
    - Known facts: [What we know]
    - Unknown facts: [What we need to find out]
    - Available resources: [Tools, data, time]
    - Constraints: [Limitations]

### Goal State Definition

    GOAL STATE:
    - Required deliverables: [What must be produced]
    - Quality criteria: [How to measure success]
    - Completion indicators: [How to know we're done]

### Gap Analysis

    GAP: CURRENT → GOAL
    - Missing information: [What to research]
    - Missing resources: [What to acquire]
    - Transformation needed: [What to process]
    - Actions required: [What to do]

### Action Selection
For each gap, select the action that:
1. Maximizes progress toward goal
2. Minimizes resource usage
3. Reduces uncertainty
4. Maintains reversibility (when possible)

### Progress Tracking
After each action:

    STATE UPDATE:
    - Action taken: [What was done]
    - New state: [Current situation]
    - Remaining gap: [What's left]
    - Next priority: [Most important remaining task]
"""
```

### 6.3 Multi-Step Reasoning with Lookahead

```python
LOOKAHEAD_REASONING_PROMPT = """
## Lookahead Planning

Before committing to an action, consider consequences:

### 1-Step Lookahead
For each possible action A:
- What state S' results from A?
- Does S' move closer to goal?
- What new actions become available in S'?

### 2-Step Lookahead
For promising actions:
- If I take A1 → S1, then A2 → S2
- Is S2 better than just taking A1?
- Are there better A2 options from S1?

### Decision Matrix

    | Action | Immediate Result | Future Options | Risk | Score |
    |--------|------------------|----------------|------|-------|
    | A1     | [result]         | [options]      | [risk]| [1-10]|
    | A2     | [result]         | [options]      | [risk]| [1-10]|
    | A3     | [result]         | [options]      | [risk]| [1-10]|

Select action with highest score considering:
- Goal proximity (40%)
- Future flexibility (30%)
- Risk level (30%)
"""
```

---

## 7. Learning & Adaptation

### 7.1 Experience Memory

Configure persistent memory for learning:

```python
from abhikarta.agent import AgentMemory

# Initialize memory system
memory = AgentMemory(
    db_facade,
    config={
        "type": "persistent",
        "max_entries": 1000,
        "similarity_threshold": 0.8,
        "retention_days": 90
    }
)

# Memory-enabled agent prompt
LEARNING_AGENT_PROMPT = """
## Learning from Experience

You have access to memories from past interactions. Use them to improve.

### Memory Retrieval
Before planning, check:
1. Have I solved a similar problem before?
2. What approaches worked/failed?
3. Are there relevant facts I learned?

### Memory Format

    RELEVANT MEMORIES:
    [Memory 1]: Task: [similar task], Approach: [what worked], Outcome: [result]
    [Memory 2]: Task: [similar task], Approach: [what failed], Lesson: [what to avoid]

### Learning Protocol
After each task completion:

    EXPERIENCE LOG:
    - Task: [what was attempted]
    - Approach: [strategy used]
    - Tools: [which tools were effective]
    - Outcome: [success/partial/failure]
    - Lesson: [key takeaway]
    - Reuse: [when to apply this learning]

### Adaptation Rules
1. If a similar task succeeded before → try same approach first
2. If a similar task failed before → avoid that approach
3. If new situation → experiment with caution
4. If pattern emerges → codify as heuristic
"""

# Create learning agent
learning_agent = manager.create_agent(
    name="Learning Research Agent",
    agent_type="plan_and_execute",
    system_prompt=LEARNING_AGENT_PROMPT,
    llm_config={
        "provider": "anthropic",
        "model": "claude-3-opus",
        "temperature": 0.4
    },
    metadata={
        "memory_enabled": True,
        "memory_id": memory.memory_id,
        "learning_rate": "adaptive"
    },
    created_by="admin"
)
```

### 7.2 Context Retention

```python
CONTEXT_RETENTION_PROMPT = """
## Context Retention

### Session Context
Maintain awareness of:
- User preferences learned this session
- Decisions made and rationale
- Intermediate results
- Adjusted constraints

### Cross-Session Context
Remember across sessions:
- User's typical goals
- Preferred output formats
- Successful strategies
- Topics of interest

### Context Application
When starting a new task:

    CONTEXT CHECK:
    - User profile: [known preferences]
    - Related history: [relevant past tasks]
    - Applicable lessons: [what to apply]
    - Customizations: [user-specific adjustments]

### Context Update
After significant interactions:

    CONTEXT UPDATE:
    - New preference: [what was learned]
    - Confidence: [how certain]
    - Applicability: [when to apply]
"""
```

### 7.3 Strategy Refinement Over Time

```python
STRATEGY_REFINEMENT_PROMPT = """
## Strategy Refinement

### Performance Tracking
Track success rates for different strategies:

    STRATEGY PERFORMANCE:
    | Strategy | Uses | Successes | Avg Time | Confidence |
    |----------|------|-----------|----------|------------|
    | A        | 10   | 8         | 30s      | 80%        |
    | B        | 5    | 2         | 45s      | 40%        |
    | C        | 3    | 3         | 20s      | 100%       |

### Strategy Selection
Choose strategies based on:
1. Historical success rate (primary)
2. Task similarity (secondary)
3. Resource constraints (tertiary)
4. Novelty bonus (for exploration)

### Strategy Evolution
Periodically:
1. Identify consistently failing strategies → deprecate
2. Identify consistently succeeding strategies → prefer
3. Identify new patterns → create new strategies
4. Combine successful elements → hybrid strategies

### Exploration vs Exploitation
- 80% of the time: Use best known strategy
- 20% of the time: Try promising alternatives
- This balance shifts based on confidence level
"""
```

---

## 8. Goal-Based Workflows

### 8.1 Goal-Driven Workflow Definition

```json
{
  "name": "Autonomous Research Workflow",
  "description": "Goal-based workflow that plans and executes research autonomously",
  
  "input_schema": {
    "goal": {
      "type": "string",
      "description": "The research goal to achieve"
    },
    "constraints": {
      "type": "object",
      "description": "Any constraints on the research"
    }
  },
  
  "nodes": [
    {
      "node_id": "goal_analysis",
      "node_type": "llm",
      "config": {
        "system_prompt": "Analyze this research goal and produce a structured plan.\n\nGOAL: {{input.goal}}\nCONSTRAINTS: {{input.constraints}}\n\nOutput JSON:\n{\n  \"terminal_goal\": \"...\",\n  \"success_criteria\": [\"...\"],\n  \"sub_goals\": [\n    {\"id\": 1, \"description\": \"...\", \"tasks\": [\"...\"]}\n  ],\n  \"estimated_steps\": N\n}",
        "model": "gpt-4",
        "temperature": 0.3,
        "output_format": "json"
      }
    },
    {
      "node_id": "plan_execution",
      "node_type": "agent",
      "config": {
        "agent_type": "plan_and_execute",
        "tools": ["web_search", "web_fetch", "calculator", "text_summarize"],
        "input": "Execute this research plan:\n{{goal_analysis.output}}\n\nFor each sub-goal, work through the tasks systematically.\nReport progress after each sub-goal."
      },
      "depends_on": ["goal_analysis"]
    },
    {
      "node_id": "quality_check",
      "node_type": "llm",
      "config": {
        "system_prompt": "Evaluate if the research achieved its goals:\n\nORIGINAL GOAL: {{input.goal}}\nSUCCESS CRITERIA: {{goal_analysis.output.success_criteria}}\nRESEARCH RESULTS: {{plan_execution.output}}\n\nOutput JSON:\n{\n  \"goals_met\": true,\n  \"criteria_scores\": {\"criterion\": 8},\n  \"gaps\": [\"...\"],\n  \"recommendations\": [\"...\"]\n}",
        "model": "gpt-4",
        "temperature": 0.2
      },
      "depends_on": ["plan_execution"]
    },
    {
      "node_id": "gap_filling",
      "node_type": "condition",
      "config": {
        "conditions": [
          {"expression": "quality_check.output.goals_met == false", "target": "replan"},
          {"default": "compile_results"}
        ]
      },
      "depends_on": ["quality_check"]
    },
    {
      "node_id": "replan",
      "node_type": "agent",
      "config": {
        "agent_type": "plan_and_execute",
        "input": "The initial research had gaps. Fill them:\nGAPS: {{quality_check.output.gaps}}\nRECOMMENDATIONS: {{quality_check.output.recommendations}}"
      },
      "depends_on": ["gap_filling"]
    },
    {
      "node_id": "compile_results",
      "node_type": "llm",
      "config": {
        "system_prompt": "Compile the final research report:\n{{plan_execution.output}}\n\nAdditional research (if any):\n{{replan.output}}",
        "model": "gpt-4",
        "temperature": 0.5
      },
      "depends_on": ["gap_filling", "replan"]
    }
  ]
}
```

### 8.2 Workflow with HITL Checkpoints

```json
{
  "name": "Supervised Goal Execution",
  "description": "Goal-based workflow with human checkpoints",
  
  "nodes": [
    {
      "node_id": "generate_plan",
      "node_type": "agent",
      "config": {
        "agent_type": "plan_and_execute",
        "input": "Create a detailed plan for: {{input.goal}}"
      }
    },
    {
      "node_id": "approve_plan",
      "node_type": "hitl",
      "config": {
        "task_type": "approval",
        "title": "Approve Research Plan",
        "description": "Review and approve the generated plan before execution",
        "options": ["approve", "reject", "modify"]
      },
      "depends_on": ["generate_plan"]
    },
    {
      "node_id": "execute_plan",
      "node_type": "agent",
      "config": {
        "agent_type": "plan_and_execute",
        "input": "Execute approved plan: {{approve_plan.approved_content}}"
      },
      "depends_on": ["approve_plan"],
      "condition": "approve_plan.decision == 'approve'"
    }
  ]
}
```

---

## 9. Goal-Based Swarms

### 9.1 Multi-Agent Goal Pursuit

```python
from abhikarta.swarm import SwarmOrchestrator, SwarmDefinition, MasterActorConfig

# Define goal-based swarm
goal_swarm = SwarmDefinition(
    name="Research Swarm",
    description="Multi-agent swarm for complex research goals",
    
    master_actor=MasterActorConfig(
        system_prompt="""You coordinate a research swarm to achieve goals.

## Your Role
You are the goal coordinator. You:
1. Receive high-level goals
2. Decompose into agent-appropriate tasks
3. Delegate to specialized agents
4. Aggregate results
5. Verify goal completion

## Available Agents
- Researcher: Web search, data gathering
- Analyst: Data analysis, pattern finding
- Writer: Report writing, summarization
- Validator: Fact-checking, quality assurance

## Coordination Protocol
1. RECEIVE goal from user
2. DECOMPOSE into sub-goals
3. ASSIGN sub-goals to best-fit agents
4. MONITOR progress
5. REBALANCE if agents struggle
6. AGGREGATE results
7. VALIDATE against success criteria
8. REPORT completion or gaps

## Output Format
{
    "phase": "decompose|delegate|aggregate|complete",
    "assignments": [{"agent": "...", "task": "...", "priority": 1-10}],
    "status": {"sub_goal_1": "complete|in_progress|blocked"}
}
""",
        llm_config={
            "provider": "anthropic",
            "model": "claude-3-opus",
            "temperature": 0.3
        }
    ),
    
    agent_pools=[
        {
            "name": "Researcher",
            "agent_template": "research_agent",
            "tools": ["web_search", "web_fetch", "document_reader"],
            "min_instances": 2,
            "max_instances": 5
        },
        {
            "name": "Analyst", 
            "agent_template": "analysis_agent",
            "tools": ["calculator", "data_transform", "chart_generator"],
            "min_instances": 1,
            "max_instances": 3
        },
        {
            "name": "Writer",
            "agent_template": "writing_agent",
            "tools": ["text_summarize", "file_write", "format_converter"],
            "min_instances": 1,
            "max_instances": 2
        },
        {
            "name": "Validator",
            "agent_template": "validation_agent",
            "tools": ["fact_check", "source_verify", "plagiarism_check"],
            "min_instances": 1,
            "max_instances": 1
        }
    ],
    
    event_subscriptions=[
        {"agent": "Researcher", "events": ["research.request", "data.needed"]},
        {"agent": "Analyst", "events": ["analysis.request", "data.ready"]},
        {"agent": "Writer", "events": ["write.request", "analysis.complete"]},
        {"agent": "Validator", "events": ["validate.request", "draft.ready"]}
    ]
)

# Create and execute swarm
orchestrator = SwarmOrchestrator(db_facade)
swarm_id = orchestrator.create_swarm(goal_swarm)

result = orchestrator.execute(
    swarm_id,
    goal="Research the impact of AI on job markets in 2024, analyze trends, and produce a 2000-word report with data visualizations",
    context={
        "deadline": "2 hours",
        "format": "markdown",
        "include_charts": True
    }
)
```

### 9.2 Collaborative Goal Achievement

```python
COLLABORATIVE_GOAL_PROMPT = """
## Collaborative Goal Protocol

### Role: {agent_role}

You are part of a swarm working toward a shared goal.

### Communication Protocol
- Broadcast discoveries that help others
- Request help when blocked
- Report completion of sub-tasks
- Share intermediate results

### Event Types
- `progress.update`: Share current status
- `blocker.encountered`: Signal need for help
- `subtask.complete`: Announce completion
- `data.available`: Share useful data

### Collaboration Rules
1. Don't duplicate work others are doing
2. Build on others' results when available
3. Prioritize bottleneck tasks
4. Share learnings that help the swarm

### Goal Alignment
Always check: "Does this action serve the terminal goal?"
If not, reconsider or request clarification.
"""
```

---

## 10. Best Practices

### 10.1 Goal Definition

| Practice | Good | Bad |
|----------|------|-----|
| Specificity | "Find Q3 2024 revenue for top 5 tech companies" | "Find some company data" |
| Measurability | "Produce a 1000-word summary with 5+ citations" | "Write something good" |
| Achievability | "Analyze publicly available data" | "Access private databases" |
| Constraints | "Use only free tools, complete in 10 minutes" | No constraints specified |

### 10.2 Planning Depth

```
Simple Task (1-3 steps):
  → Direct execution, minimal planning

Medium Task (4-10 steps):
  → 2-level hierarchy: Goals → Tasks

Complex Task (10+ steps):
  → 3-level hierarchy: Mission → Objectives → Tasks
  → Consider parallel execution
  → Add checkpoints

Very Complex Task (50+ steps):
  → Use swarm architecture
  → Break into phases
  → Add HITL checkpoints
```

### 10.3 Autonomy Levels

Configure appropriate autonomy:

```python
AUTONOMY_LEVELS = {
    "full": {
        "human_approval": False,
        "auto_replan": True,
        "tool_selection": "autonomous",
        "error_handling": "automatic"
    },
    "supervised": {
        "human_approval": True,  # For major decisions
        "auto_replan": True,
        "tool_selection": "autonomous",
        "error_handling": "automatic"
    },
    "guided": {
        "human_approval": True,
        "auto_replan": False,  # Human approves replans
        "tool_selection": "suggest",  # Human confirms tool choice
        "error_handling": "report"
    },
    "manual": {
        "human_approval": True,
        "auto_replan": False,
        "tool_selection": "manual",
        "error_handling": "stop"
    }
}
```

### 10.4 Memory Management

```python
# Good memory practices
MEMORY_BEST_PRACTICES = """
## What to Remember
✅ Successful strategies and why they worked
✅ Failed approaches and lessons learned
✅ User preferences and patterns
✅ Domain-specific knowledge gained
✅ Useful intermediate results

## What NOT to Remember
❌ Temporary calculations
❌ Sensitive information
❌ One-time context
❌ Outdated information
❌ Conflicting/uncertain data

## Memory Hygiene
- Review memories periodically
- Remove outdated entries
- Consolidate similar memories
- Validate before applying
"""
```

---

## 11. Complete Examples

### 11.1 Market Research Agent

```python
from abhikarta.agent import AgentManager, AgentExecutor
from abhikarta.database import DatabaseFacade

db = DatabaseFacade.from_config()
manager = AgentManager(db)
executor = AgentExecutor(db)

# Create market research agent
MARKET_RESEARCH_PROMPT = """
You are an autonomous market research agent.

## Capabilities
- Search for market data and trends
- Analyze competitor information
- Generate market reports
- Create data visualizations

## Goal Framework
For each research request:
1. CLARIFY the research objective
2. IDENTIFY data sources needed
3. GATHER information systematically
4. ANALYZE for patterns and insights
5. SYNTHESIZE into actionable findings
6. PRESENT in requested format

## Tools Available
- web_search: Find current market information
- web_fetch: Get detailed page content
- calculator: Compute market metrics
- file_write: Save research results

## Output Standards
- Cite all sources
- Include data dates
- Note confidence levels
- Flag assumptions made
"""

agent_id = manager.create_agent(
    name="Market Research Agent",
    agent_type="plan_and_execute",
    system_prompt=MARKET_RESEARCH_PROMPT,
    tools=["builtin:web_search", "builtin:web_fetch", "builtin:calculator", "builtin:file_write"],
    llm_config={"provider": "anthropic", "model": "claude-3-opus", "temperature": 0.4},
    created_by="admin"
)

# Execute research goal
result = executor.execute(
    agent_id=agent_id,
    user_input="""
    GOAL: Research the electric vehicle market in North America
    
    DELIVERABLES:
    1. Market size and growth rate (2020-2024)
    2. Top 5 manufacturers by market share
    3. Key trends and predictions for 2025
    4. Competitive analysis summary
    
    FORMAT: Markdown report with data tables
    CONSTRAINTS: Use only 2023-2024 data sources
    """,
    context={"output_file": "ev_market_report.md"}
)

print(result['output'])
```

### 11.2 Code Development Agent

```python
CODE_DEVELOPMENT_PROMPT = """
You are an autonomous code development agent.

## Goal Processing
When given a coding task:
1. UNDERSTAND requirements fully
2. DESIGN solution architecture
3. IMPLEMENT incrementally with tests
4. REVIEW for quality and edge cases
5. DOCUMENT the solution

## Development Protocol
```
TASK: [What to build]
├── REQUIREMENTS
│   ├── Functional: [What it must do]
│   └── Non-functional: [Quality attributes]
├── DESIGN
│   ├── Architecture: [High-level structure]
│   ├── Components: [Key modules]
│   └── Interfaces: [How they connect]
├── IMPLEMENTATION
│   ├── Core logic
│   ├── Error handling
│   └── Tests
└── DELIVERY
    ├── Code files
    ├── Documentation
    └── Usage examples
```

## Quality Standards
- All functions documented
- Error cases handled
- Edge cases tested
- Clean, readable code
"""

code_agent = manager.create_agent(
    name="Code Development Agent",
    agent_type="plan_and_execute",
    system_prompt=CODE_DEVELOPMENT_PROMPT,
    tools=[
        "builtin:code_execute",
        "builtin:file_read",
        "builtin:file_write",
        "builtin:web_search"
    ],
    llm_config={"provider": "openai", "model": "gpt-4", "temperature": 0.3},
    created_by="admin"
)

# Execute coding goal
result = executor.execute(
    agent_id=code_agent,
    user_input="""
    GOAL: Create a Python utility for CSV data analysis
    
    REQUIREMENTS:
    - Load CSV files
    - Calculate basic statistics (mean, median, std)
    - Filter rows by column values
    - Export results to JSON
    
    CONSTRAINTS:
    - Use only standard library + pandas
    - Include type hints
    - Write unit tests
    """
)
```

---

## 12. Troubleshooting

### 12.1 Common Issues

**Problem: Agent not making progress**
```
Symptoms: Agent loops without advancing toward goal
Solution:
1. Check goal clarity - is it specific enough?
2. Increase max_iterations
3. Enable verbose logging to see where it's stuck
4. Add explicit progress checkpoints
```

**Problem: Agent takes wrong actions**
```
Symptoms: Tools used don't match task needs
Solution:
1. Improve tool descriptions
2. Add tool selection guidance in prompt
3. Reduce temperature for more focused decisions
4. Add tool usage examples in system prompt
```

**Problem: Plans are too complex**
```
Symptoms: Agent creates 50-step plans for simple tasks
Solution:
1. Add planning constraints ("max 10 steps")
2. Require justification for each step
3. Add "simplicity" as evaluation criterion
4. Use lighter model for simple tasks
```

**Problem: Memory not helping**
```
Symptoms: Agent doesn't use past experience
Solution:
1. Verify memory is enabled in config
2. Check memory retrieval threshold
3. Add explicit "check memory" instruction
4. Verify memories are being stored
```

### 12.2 Debugging

```python
import logging

# Enable detailed logging
logging.getLogger("abhikarta.agent").setLevel(logging.DEBUG)
logging.getLogger("abhikarta.planning").setLevel(logging.DEBUG)

# This shows:
# - Goal decomposition steps
# - Plan generation reasoning
# - Tool selection decisions
# - Execution trace
# - Replanning triggers
```

### 12.3 Performance Tuning

```python
# Optimize for speed
FAST_CONFIG = {
    "planning_model": "gpt-3.5-turbo",  # Faster planning
    "execution_model": "gpt-4-turbo",    # Quality execution
    "max_plan_depth": 2,                  # Shallow plans
    "parallel_execution": True,           # Run independent tasks in parallel
    "cache_enabled": True                 # Cache repeated queries
}

# Optimize for quality
QUALITY_CONFIG = {
    "planning_model": "claude-3-opus",
    "execution_model": "claude-3-opus",
    "max_plan_depth": 4,
    "verification_enabled": True,
    "double_check_enabled": True
}
```

---

## Quick Reference

### Goal-Based Agent Creation Checklist

- [ ] Define clear terminal goal
- [ ] Set measurable success criteria
- [ ] Choose appropriate agent type (plan_and_execute)
- [ ] Configure planning prompt with framework
- [ ] Add relevant tools
- [ ] Set appropriate temperature (0.3-0.5)
- [ ] Enable memory if needed
- [ ] Configure autonomy level
- [ ] Add HITL checkpoints if supervised
- [ ] Test with simple goal first

### Prompt Template

```
You are a Goal-Based Agent.

## Goal Framework
1. ANALYZE: Understand the goal fully
2. PLAN: Decompose into achievable steps
3. EXECUTE: Take actions autonomously
4. MONITOR: Track progress toward goal
5. ADAPT: Adjust when needed
6. COMPLETE: Verify success criteria met

## Current Goal
[GOAL_HERE]

## Available Tools
[TOOL_LIST]

## Constraints
[CONSTRAINTS]

Think step by step. Show your reasoning. Achieve the goal.
```

---

## Further Reading

- [Chain of Thought & Tree of Thought](./COT_TOT_TUTORIAL.md)
- [Agent Swarms Guide](/help/swarms)
- [Workflow DAGs](/help/workflow-dags)
- [Tools System](/help/tools-system)

---

**Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.**
