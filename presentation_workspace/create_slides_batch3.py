import os

def content_slide(num, title, content):
    return f'''<!DOCTYPE html>
<html>
<head></head>
<body class="col" style="width: 960px; height: 540px; background: #F4F9FD; padding: 20px 30px; box-sizing: border-box;">
  <div class="row" style="justify-content: space-between; align-items: center; margin-bottom: 10px;">
    <p style="font-size: 15px; color: #0079C1; margin: 0; font-weight: 600;">{title}</p>
    <p style="font-size: 9px; color: #5A7A9C; margin: 0;">Abhikarta-LLM v1.4.6</p>
  </div>
  <div style="background: #0079C1; height: 2px; margin-bottom: 10px; border-radius: 2px;"></div>
  <div class="fill-height" style="overflow: hidden;">
{content}
  </div>
  <div class="row" style="justify-content: space-between; align-items: center; margin-top: 8px;">
    <p style="font-size: 7px; color: #5A7A9C; margin: 0;">Copyright © 2025-2030 Ashutosh Sinha | Patent Pending</p>
    <p style="font-size: 7px; color: #5A7A9C; margin: 0;">{num}</p>
  </div>
</body>
</html>'''

def section_slide(num, title, subtitle):
    return f'''<!DOCTYPE html>
<html>
<head></head>
<body class="col center" style="width: 960px; height: 540px; background: #0079C1; padding: 40px; box-sizing: border-box;">
  <p style="font-size: 13px; color: #FFFFFF; margin: 0; opacity: 0.7;">Section</p>
  <h1 style="font-size: 32px; color: #FFFFFF; margin: 10px 0 0 0; font-weight: 700;">{title}</h1>
  <p style="font-size: 13px; color: #FFFFFF; margin: 8px 0 0 0; opacity: 0.8;">{subtitle}</p>
  <p style="font-size: 8px; color: #FFFFFF; margin: 30px 0 0 0; opacity: 0.6;">Copyright © 2025-2030 Ashutosh Sinha | Patent Pending | Slide {num}</p>
</body>
</html>'''

slides = [
    # 19 - Tool Integration
    (19, 'content', 'Agent Tool Integration', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Built-in Tool Types</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• <b>Database</b>: Query SQLite, PostgreSQL, MySQL with SQL or ORM</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>API</b>: Call REST/GraphQL endpoints with auth</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>File</b>: Read/write files, parse PDFs, Excel, CSV</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Search</b>: Web search, vector search, RAG retrieval</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Python</b>: Execute Python code in sandbox</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">MCP (Model Context Protocol) Integration</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• Connect external MCP servers as agent tools</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Auto-discovery of MCP tool schemas</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Pre-built: Filesystem, GitHub, Slack, Postgres, Puppeteer</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Custom MCP servers via Python or Node.js</p>
      </div>
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">UI Tool Management (Admin → Tools)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• Browse/enable tools per agent • Configure tool parameters • Test tools before save • View tool usage analytics</p>
      </div>
    </div>'''),

    # 20 - Agent Creation via UI
    (20, 'content', 'Creating Agents via UI', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Visual Agent Designer (Agents → New)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">1. <b>Basic Info</b>: Name, description, category, tags</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">2. <b>Provider/Model</b>: Select from dropdown (Ollama default)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">3. <b>Persona</b>: Rich text editor for system prompt</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">4. <b>Tools</b>: Drag-drop from tool library, configure params</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">5. <b>Knowledge Base</b>: Upload docs for RAG</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">6. <b>Reasoning</b>: Select pattern (ReAct, CoT, etc.)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">7. <b>HITL</b>: Configure approval checkpoints</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">8. <b>Test</b>: Interactive chat to validate before save</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">UI Features</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• Live preview of agent behavior • Version history with rollback • Clone existing agents • Export/import JSON</p>
      </div>
    </div>'''),

    # 21 - Agent JSON Example
    (21, 'content', 'Agent Definition: JSON Format', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #1A3A5C; padding: 8px; border-radius: 4px;">
        <p style="font-size: 7px; color: #7FDBFF; margin: 0; font-family: monospace; white-space: pre; line-height: 1.3;">{
  "name": "Research Assistant",
  "provider": "ollama",
  "model": "llama3.3:70b",
  "persona": "You are a research assistant. Analyze documents, search the web, and synthesize findings.",
  "reasoning_pattern": "react",
  "tools": [
    {"type": "web_search", "config": {"max_results": 5}},
    {"type": "file_read", "config": {"allowed_extensions": [".pdf", ".docx"]}},
    {"type": "mcp", "server": "github", "config": {"repo": "myorg/myrepo"}}
  ],
  "knowledge_base": {"vector_store": "chroma", "collection": "research_docs"},
  "hitl": {"approval_required": ["web_search"], "notify_channels": ["slack"]},
  "max_iterations": 10,
  "temperature": 0.7
}</p>
      </div>
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Creating via Python</p>
        <p style="font-size: 7px; color: #1A3A5C; margin: 3px 0 0 0; font-family: monospace;">from abhikarta import Agent, Tool</p>
        <p style="font-size: 7px; color: #1A3A5C; margin: 1px 0 0 0; font-family: monospace;">agent = Agent.from_json("agent.json")  # or Agent.create(...)</p>
        <p style="font-size: 7px; color: #1A3A5C; margin: 1px 0 0 0; font-family: monospace;">result = agent.run("Analyze Q3 earnings report")</p>
      </div>
    </div>'''),

    # 22 - Agent HITL and Execution
    (22, 'content', 'Agent HITL & Execution Management', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Human-in-the-Loop for Agents</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• <b>Tool Approval</b>: Require human OK before specific tools run</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Output Review</b>: Human reviews agent response before delivery</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Confidence Threshold</b>: Escalate if agent unsure</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Notifications</b>: Slack, Teams, Email alerts for approvals</p>
      </div>
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Execution Viewer (Agents → Executions)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• <b>Timeline</b>: Step-by-step execution trace</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Thought Process</b>: View agent's reasoning at each step</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Tool Calls</b>: Input/output of each tool invocation</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Tokens/Cost</b>: Usage metrics per execution</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Replay</b>: Re-run with different inputs</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Cancel/Override</b>: Stop runaway agents</p>
      </div>
    </div>'''),

    # 23 - Workflow Section
    (23, 'section', 'Workflow DAG System', 'Visual pipeline orchestration'),

    # 24 - Workflow Overview
    (24, 'content', 'Workflow DAG Overview', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">What is a Workflow DAG?</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0; line-height: 1.4;">A Directed Acyclic Graph (DAG) represents multi-step AI pipelines where nodes are processing steps and edges define data flow. Workflows enable parallel execution, conditional logic, and human checkpoints.</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Key Capabilities</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• <b>12+ Node Types</b>: LLM, Agent, Tool, Python, Condition, Human, Transform...</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Parallel Execution</b>: Nodes without dependencies run concurrently</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Conditional Branching</b>: Route based on output values</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Error Handling</b>: Retry, fallback, or fail-fast per node</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>State Management</b>: Persist workflow state for resume</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>HITL Nodes</b>: Pause for human approval at any step</p>
      </div>
    </div>'''),

    # 25 - Workflow Node Types
    (25, 'content', 'Workflow Node Types', '''    <div class="row gap-sm" style="height: 100%; flex-wrap: wrap; align-content: flex-start;">
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">LLM Node</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Direct LLM completion with prompt template</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Agent Node</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Run a full agent with tools & memory</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Tool Node</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Execute a single tool (DB, API, File)</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #ED1C24; margin: 0; font-weight: 600;">Python Node</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Custom Python code in sandbox</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Transform Node</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Data transformation (JSON, parse, merge)</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #ED1C24; margin: 0; font-weight: 600;">Condition Node</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Branch based on value/expression</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #ED1C24; margin: 0; font-weight: 600;">Human Node</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Pause for human input/approval</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Subworkflow Node</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Embed another workflow as node</p>
      </div>
    </div>'''),

    # 26 - Workflow UI Creation
    (26, 'content', 'Creating Workflows via UI', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Visual Workflow Designer (Workflows → New)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">1. <b>Canvas</b>: Drag-drop nodes from palette onto canvas</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">2. <b>Connect</b>: Draw edges between node outputs and inputs</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">3. <b>Configure</b>: Click node to edit parameters in sidebar</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">4. <b>Python Code</b>: Add Python nodes with inline editor + syntax highlight</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">5. <b>Variables</b>: Define workflow inputs and pass between nodes</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">6. <b>Validate</b>: Check for cycles, missing connections</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">7. <b>Test Run</b>: Execute with sample inputs before deploy</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Python Code Integration</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• Inline Python with access to workflow context</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Import existing Python files from project</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• pip install custom packages per workflow</p>
      </div>
    </div>'''),

    # 27 - Workflow JSON Example
    (27, 'content', 'Workflow Definition: JSON Format', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #1A3A5C; padding: 8px; border-radius: 4px;">
        <p style="font-size: 6px; color: #7FDBFF; margin: 0; font-family: monospace; white-space: pre; line-height: 1.2;">{
  "name": "Document Analysis Pipeline",
  "nodes": [
    {"id": "extract", "type": "tool", "tool": "file_read", "config": {"path": "{{input.file}}"}},
    {"id": "summarize", "type": "llm", "provider": "ollama", "model": "llama3.3", 
     "prompt": "Summarize: {{extract.output}}"},
    {"id": "check", "type": "condition", "expression": "len(summarize.output) > 100"},
    {"id": "approve", "type": "human", "message": "Review summary:", "timeout": 3600},
    {"id": "notify", "type": "tool", "tool": "slack_send", "config": {"channel": "#reports"}}
  ],
  "edges": [
    {"from": "extract", "to": "summarize"},
    {"from": "summarize", "to": "check"},
    {"from": "check", "to": "approve", "condition": "true"},
    {"from": "approve", "to": "notify"}
  ],
  "hitl": {"nodes": ["approve"], "notify": ["slack", "email"]}
}</p>
      </div>
      <div style="background: #FFF; padding: 6px; border-radius: 4px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Python Execution</p>
        <p style="font-size: 7px; color: #1A3A5C; margin: 2px 0 0 0; font-family: monospace;">result = Workflow.from_json("pipeline.json").run({"file": "report.pdf"})</p>
      </div>
    </div>'''),

    # 28 - Workflow HITL and Execution
    (28, 'content', 'Workflow HITL & Execution Management', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Human-in-the-Loop for Workflows</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• <b>Human Nodes</b>: Pause workflow until human provides input</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Approval Gates</b>: Block progression until approved</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Timeout Handling</b>: Auto-escalate if no response</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Override</b>: Human can modify AI output before continue</p>
      </div>
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Execution Dashboard (Workflows → Executions)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• <b>Visual Progress</b>: DAG view with node status colors</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Node Details</b>: Click any node to see input/output</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Logs</b>: Real-time streaming logs per node</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Retry</b>: Re-run failed nodes without full restart</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Cancel</b>: Abort running workflows</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>History</b>: All past executions with search/filter</p>
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

print(f"Created slides 19-28")
