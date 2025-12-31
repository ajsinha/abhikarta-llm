import os

def content_slide(num, title, content):
    return f'''<!DOCTYPE html>
<html>
<head></head>
<body class="col" style="width: 960px; height: 540px; background: #F4F9FD; padding: 30px 40px; box-sizing: border-box;">
  <div class="row" style="justify-content: space-between; align-items: center; margin-bottom: 8px;">
    <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">{title}</p>
    <p style="font-size: 8px; color: #5A7A9C; margin: 0;">Abhikarta-LLM v1.4.6</p>
  </div>
  <div style="background: #0079C1; height: 2px; margin-bottom: 8px; border-radius: 2px;"></div>
  <div class="fill-height" style="overflow: hidden;">
{content}
  </div>
  <div class="row" style="justify-content: space-between; align-items: center; margin-top: 6px;">
    <p style="font-size: 6px; color: #5A7A9C; margin: 0;">Copyright 2025-2030 Ashutosh Sinha | Patent Pending</p>
    <p style="font-size: 6px; color: #5A7A9C; margin: 0;">{num}</p>
  </div>
</body>
</html>'''

def section_slide(num, title, subtitle):
    return f'''<!DOCTYPE html>
<html>
<head></head>
<body class="col center" style="width: 960px; height: 540px; background: #0079C1; padding: 50px; box-sizing: border-box;">
  <p style="font-size: 12px; color: #FFFFFF; margin: 0; opacity: 0.7;">Section</p>
  <h1 style="font-size: 30px; color: #FFFFFF; margin: 10px 0 0 0; font-weight: 700;">{title}</h1>
  <p style="font-size: 12px; color: #FFFFFF; margin: 8px 0 0 0; opacity: 0.8;">{subtitle}</p>
  <p style="font-size: 8px; color: #FFFFFF; margin: 30px 0 0 0; opacity: 0.6;">Copyright 2025-2030 Ashutosh Sinha | Patent Pending | Slide {num}</p>
</body>
</html>'''

slides = [
    # 21 - Workflow Section
    (21, 'section', 'Workflow DAG System', 'Visual pipeline orchestration'),

    # 22 - Workflow Overview
    (22, 'content', 'Workflow DAG Overview', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 10px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">What is a Workflow DAG?</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 4px 0 0 0; line-height: 1.4;">A Directed Acyclic Graph (DAG) represents multi-step AI pipelines where nodes are processing steps and edges define data flow. Workflows enable parallel execution, conditional branching, error handling, and human approval gates.</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Key Capabilities</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li><b>12+ Node Types:</b> LLM, Agent, Tool, Python, Condition, Human, Transform...</li>
          <li><b>Parallel Execution:</b> Nodes without dependencies run concurrently</li>
          <li><b>Conditional Branching:</b> Route data based on output values or expressions</li>
          <li><b>Error Handling:</b> Per-node retry, fallback paths, or fail-fast options</li>
          <li><b>State Management:</b> Persist workflow state for pause/resume</li>
          <li><b>HITL Nodes:</b> Pause workflow for human input or approval at any step</li>
        </ul>
      </div>
    </div>'''),

    # 23 - Workflow Node Types
    (23, 'content', 'Workflow Node Types', '''    <div class="row gap-sm" style="height: 100%; flex-wrap: wrap; align-content: flex-start;">
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px; border-radius: 4px; width: 210px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">LLM Node</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Direct LLM completion with prompt template and variable substitution</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px; border-radius: 4px; width: 210px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Agent Node</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Run a full agent with tools, memory, reasoning pattern</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px; border-radius: 4px; width: 210px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Tool Node</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Execute single tool (DB query, API call, file op)</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px; border-radius: 4px; width: 210px;">
        <p style="font-size: 9px; color: #ED1C24; margin: 0; font-weight: 600;">Python Node</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Custom Python code with access to workflow context</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px; border-radius: 4px; width: 210px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Transform Node</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Data transformation (JSON parse, merge, filter)</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px; border-radius: 4px; width: 210px;">
        <p style="font-size: 9px; color: #ED1C24; margin: 0; font-weight: 600;">Condition Node</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Branch workflow based on expression evaluation</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px; border-radius: 4px; width: 210px;">
        <p style="font-size: 9px; color: #ED1C24; margin: 0; font-weight: 600;">Human Node</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Pause for human input, review, or approval</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px; border-radius: 4px; width: 210px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Subworkflow Node</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Embed another workflow as reusable component</p>
      </div>
    </div>'''),

    # 24 - Workflow UI Creation
    (24, 'content', 'Creating Workflows via UI', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Visual Workflow Designer (Workflows - New Workflow)</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li><b>Canvas:</b> Drag-drop nodes from palette onto infinite canvas</li>
          <li><b>Connect:</b> Draw edges between node outputs and inputs visually</li>
          <li><b>Configure:</b> Click any node to edit parameters in sidebar panel</li>
          <li><b>Python Code:</b> Add Python nodes with Monaco editor, syntax highlight</li>
          <li><b>Import Code:</b> Reference existing Python files from your project</li>
          <li><b>Variables:</b> Define workflow inputs, pass data between nodes</li>
          <li><b>Validate:</b> Check for cycles, missing connections, type mismatches</li>
          <li><b>Test Run:</b> Execute with sample inputs, view step-by-step results</li>
        </ul>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Python Code Integration</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li>Inline Python with full access to workflow context variables</li>
          <li>Import existing Python modules from project directory</li>
          <li>pip install custom packages per workflow environment</li>
          <li>Sandbox execution with configurable timeout and memory limits</li>
        </ul>
      </div>
    </div>'''),

    # 25 - Workflow JSON
    (25, 'content', 'Workflow Definition: JSON Format', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #1A3A5C; padding: 8px; border-radius: 4px;">
        <p style="font-size: 6px; color: #7FDBFF; margin: 0; font-family: monospace; white-space: pre; line-height: 1.2;">{
  "name": "Document Analysis Pipeline",
  "nodes": [
    {"id": "extract", "type": "tool", "tool": "file_read", "config": {"path": "{{input.file}}"}},
    {"id": "summarize", "type": "llm", "provider": "ollama", "model": "llama3.3",
     "prompt": "Summarize the following document:\\n{{extract.output}}"},
    {"id": "check", "type": "condition", "expression": "len(summarize.output) > 100"},
    {"id": "approve", "type": "human", "message": "Review summary:", "timeout": 3600},
    {"id": "notify", "type": "tool", "tool": "slack_send", "config": {"channel": "#reports"}}
  ],
  "edges": [
    {"from": "extract", "to": "summarize"}, {"from": "summarize", "to": "check"},
    {"from": "check", "to": "approve", "condition": "true"}, {"from": "approve", "to": "notify"}
  ]
}</p>
      </div>
      <div style="background: #FFF; padding: 6px; border-radius: 4px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Python Execution</p>
        <p style="font-size: 7px; color: #1A3A5C; margin: 3px 0 0 0; font-family: monospace;">from abhikarta import Workflow</p>
        <p style="font-size: 7px; color: #1A3A5C; margin: 1px 0 0 0; font-family: monospace;">result = Workflow.from_json("pipeline.json").run({"file": "report.pdf"})</p>
      </div>
    </div>'''),

    # 26 - Workflow HITL and Execution
    (26, 'content', 'Workflow HITL and Execution Management', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Human-in-the-Loop for Workflows</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li><b>Human Nodes:</b> Pause workflow until human provides input or data</li>
          <li><b>Approval Gates:</b> Block progression until human approves previous step output</li>
          <li><b>Timeout Handling:</b> Auto-escalate or take default action if no response</li>
          <li><b>Override:</b> Human can modify AI output before workflow continues</li>
          <li><b>Notifications:</b> Multi-channel alerts (Slack, Teams, Email) for pending items</li>
        </ul>
      </div>
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Execution Dashboard (Workflows - Executions)</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li><b>Visual Progress:</b> DAG view with node status colors (running, success, failed)</li>
          <li><b>Node Details:</b> Click any node to see full input/output and timing</li>
          <li><b>Logs:</b> Real-time streaming logs per node execution</li>
          <li><b>Retry:</b> Re-run failed nodes without restarting entire workflow</li>
          <li><b>Cancel:</b> Abort running workflows gracefully</li>
          <li><b>History:</b> Search and filter all past executions with full audit trail</li>
        </ul>
      </div>
    </div>'''),

    # 27 - Swarms Section
    (27, 'section', 'Agent Swarms', 'Dynamic multi-agent coordination'),

    # 28 - What is a Swarm
    (28, 'content', 'What is an Agent Swarm?', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 10px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Definition</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 4px 0 0 0; line-height: 1.4;">An Agent Swarm is a collection of autonomous agents that collaborate dynamically on tasks. Unlike fixed workflows, swarms use event-driven coordination where agents discover and respond to work based on their capabilities, availability, and specializations.</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Key Characteristics</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li><b>Event-Driven:</b> Agents react to events rather than following predefined sequences</li>
          <li><b>Self-Organizing:</b> Agents claim tasks based on capabilities and availability</li>
          <li><b>Emergent Behavior:</b> Complex outcomes arise from simple agent rules</li>
          <li><b>Scalable:</b> Add or remove agents without restructuring the system</li>
          <li><b>Fault Tolerant:</b> Other agents compensate when one fails</li>
        </ul>
      </div>
      <div style="background: #FFE8E8; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Use Cases</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Research teams, Customer service pools, Data processing clusters, Market analysis, Competitive intelligence</p>
      </div>
    </div>'''),

    # 29 - Swarm UI and Messaging
    (29, 'content', 'Swarm Creation and Messaging Integration', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Creating Swarms via UI (Swarms - New Swarm)</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li><b>Define Swarm:</b> Name, description, coordination strategy selection</li>
          <li><b>Add Agents:</b> Select which agents participate in the swarm pool</li>
          <li><b>Configure Routing:</b> Capability matching rules, priority ordering</li>
          <li><b>Set Coordination:</b> Choreography (LLM-directed) or Orchestration (rule-based)</li>
          <li><b>Monitor:</b> Real-time dashboard of agent activity and task distribution</li>
        </ul>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Messaging Integration</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li><b>Kafka:</b> High-throughput event streaming for large-scale swarms</li>
          <li><b>RabbitMQ:</b> Message queuing with flexible routing patterns</li>
          <li><b>ActiveMQ:</b> Enterprise JMS messaging integration</li>
          <li><b>Built-in pub/sub:</b> In-memory messaging for development and small deployments</li>
          <li><b>Backpressure:</b> Automatic load balancing when agents are overwhelmed</li>
        </ul>
      </div>
    </div>'''),

    # 30 - AI Org Section
    (30, 'section', 'AI Organizations', 'Patent-pending hierarchical governance'),

    # 31 - What is AI Org
    (31, 'content', 'What is an AI Organization?', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 10px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Definition (Patent Pending)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 4px 0 0 0; line-height: 1.4;">An AI Organization is a digital twin of a corporate hierarchy where each position is occupied by an AI agent. Tasks flow down the org chart (delegation) and responses flow up (aggregation), mirroring how real organizations coordinate complex work.</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Problems Solved</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li><b>Accountability:</b> Clear ownership chain for every AI decision</li>
          <li><b>Delegation:</b> Complex tasks decomposed naturally along org lines</li>
          <li><b>Human Oversight:</b> Every AI position has a human mirror for escalation</li>
          <li><b>Compliance:</b> Matches regulatory expectations of org structure</li>
          <li><b>Scalability:</b> Grow AI teams the same way you grow human teams</li>
        </ul>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Key Features</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Task delegation down the hierarchy | Response aggregation up | Human mirrors | Configurable autonomy levels per position | HITL at any level</p>
      </div>
    </div>'''),

    # 32 - AI Org UI Creation
    (32, 'content', 'Creating AI Organizations via UI', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Organization Designer (AI Orgs - New Organization)</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li><b>Create Org:</b> Name, description, select industry template if desired</li>
          <li><b>Add Positions:</b> Define roles (CEO, VP, Manager, Analyst, Specialist...)</li>
          <li><b>Build Hierarchy:</b> Drag positions to set reporting relationships visually</li>
          <li><b>Assign Agents:</b> Map which agent fills each position in the org</li>
          <li><b>Set Human Mirrors:</b> Assign human overseers (email/Slack) per position</li>
          <li><b>Configure Autonomy:</b> Per-position autonomy level (autonomous to supervised)</li>
          <li><b>Define Workflows:</b> Attach workflows that positions can execute</li>
        </ul>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">UI Management Features</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li>Interactive org chart with drag-drop position editing</li>
          <li>Real-time task flow visualization through hierarchy</li>
          <li>Pending approvals dashboard for human mirrors</li>
          <li>Position performance metrics and utilization stats</li>
        </ul>
      </div>
    </div>'''),

    # 33 - AI Org JSON
    (33, 'content', 'AI Organization: JSON Definition', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #1A3A5C; padding: 8px; border-radius: 4px;">
        <p style="font-size: 6px; color: #7FDBFF; margin: 0; font-family: monospace; white-space: pre; line-height: 1.2;">{
  "name": "Research Division",
  "positions": [
    {"id": "director", "title": "Research Director", "agent": "strategic_agent",
     "human_mirror": "john.smith@company.com", "autonomy": "supervised"},
    {"id": "lead_ai", "title": "AI Team Lead", "agent": "ai_specialist",
     "reports_to": "director", "autonomy": "semi_autonomous"},
    {"id": "analyst1", "title": "Research Analyst", "agent": "research_agent",
     "reports_to": "lead_ai", "autonomy": "autonomous"},
    {"id": "analyst2", "title": "Data Analyst", "agent": "data_agent",
     "reports_to": "lead_ai", "autonomy": "autonomous"}
  ],
  "delegation_rules": {"strategy_tasks": ["director"], "analysis_tasks": ["analyst1", "analyst2"]},
  "hitl": {"require_approval": ["budget_decisions", "external_communications"]}
}</p>
      </div>
      <div style="background: #FFF; padding: 6px; border-radius: 4px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Benefits</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Mirrors real org structure | Clear accountability | Scalable AI teams | Regulatory compliant | Human oversight built-in | Natural task decomposition</p>
      </div>
    </div>'''),

    # 34 - RBAC Section
    (34, 'section', 'RBAC and Security', 'Enterprise-grade access control'),

    # 35 - RBAC Details
    (35, 'content', 'Role-Based Access Control', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">RBAC Model</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li><b>Users:</b> Individual accounts with email authentication or SSO</li>
          <li><b>Roles:</b> Admin, Developer, Analyst, Viewer (plus custom roles)</li>
          <li><b>Permissions:</b> Granular actions per resource type (create, read, execute, delete)</li>
          <li><b>Model Access:</b> Control which LLM models each role can use</li>
          <li><b>Usage Limits:</b> RPM/TPM quotas configurable per role</li>
          <li><b>Resource Scoping:</b> Limit access to specific agents, workflows, or orgs</li>
        </ul>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Security Features</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li><b>API Keys:</b> Scoped keys with expiration and permission inheritance</li>
          <li><b>Audit Logs:</b> Every action recorded with user, timestamp, IP, details</li>
          <li><b>Rate Limiting:</b> Prevent abuse and control costs at user/team/org level</li>
          <li><b>Data Isolation:</b> Multi-tenant data separation in database</li>
          <li><b>SSO Ready:</b> SAML and OIDC integration for enterprise identity</li>
          <li><b>Encryption:</b> API keys and credentials encrypted at rest</li>
        </ul>
      </div>
    </div>'''),
]

for num, stype, title, content in slides:
    filename = f"slide{num:02d}.html"
    if stype == 'section':
        html = section_slide(num, title, content)
    else:
        html = content_slide(num, title, content)
    with open(filename, 'w') as f:
        f.write(html)

print("Created slides 21-35")
