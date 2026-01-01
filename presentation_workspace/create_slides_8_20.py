import os

def content_slide(num, title, content):
    return f'''<!DOCTYPE html>
<html>
<head></head>
<body class="col" style="width: 960px; height: 540px; background: #F4F9FD; padding: 30px 40px; box-sizing: border-box;">
  <div class="row" style="justify-content: space-between; align-items: center; margin-bottom: 8px;">
    <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">{title}</p>
    <p style="font-size: 8px; color: #5A7A9C; margin: 0;">Abhikarta-LLM v1.4.7</p>
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
    # 8 - Architecture Section
    (8, 'section', 'Platform Architecture', 'System design and core components'),

    # 9 - Architecture Overview
    (9, 'content', 'Architecture Overview', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 6px 10px; border-radius: 4px; text-align: center;">
        <p style="font-size: 9px; color: #5A7A9C; margin: 0; font-weight: 600;">USER INTERFACES</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 2px 0 0 0;">Web UI (Bootstrap 5) | REST API (OpenAPI) | Admin Console | CLI (Click/Rich)</p>
      </div>
      <div style="background: #FFF; border: 2px solid #0079C1; padding: 10px; border-radius: 6px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600; text-align: center;">ABHIKARTA-LLM CORE (Flask + SQLAlchemy + Pydantic)</p>
        <div class="row gap-sm" style="margin-top: 8px;">
          <div style="background: #E8F4FC; padding: 8px; border-radius: 4px; flex: 1; text-align: center;">
            <p style="font-size: 8px; color: #0079C1; margin: 0; font-weight: 600;">Agent Engine</p>
            <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">6 reasoning patterns</p>
          </div>
          <div style="background: #E8F4FC; padding: 8px; border-radius: 4px; flex: 1; text-align: center;">
            <p style="font-size: 8px; color: #0079C1; margin: 0; font-weight: 600;">Workflow DAG</p>
            <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">12+ node types</p>
          </div>
          <div style="background: #FFE8E8; padding: 8px; border-radius: 4px; flex: 1; text-align: center;">
            <p style="font-size: 8px; color: #ED1C24; margin: 0; font-weight: 600;">AI Org Manager</p>
            <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Patent Pending</p>
          </div>
          <div style="background: #E8F4FC; padding: 8px; border-radius: 4px; flex: 1; text-align: center;">
            <p style="font-size: 8px; color: #0079C1; margin: 0; font-weight: 600;">Security/RBAC</p>
            <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Model permissions</p>
          </div>
        </div>
      </div>
      <div style="background: #FFF; padding: 6px 10px; border-radius: 4px; text-align: center;">
        <p style="font-size: 9px; color: #ED1C24; margin: 0; font-weight: 600;">LLM PROVIDERS (11+ Unified)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 2px 0 0 0;">Ollama (Default) | OpenAI | Anthropic | Google | Azure | AWS Bedrock | Groq | Mistral | Cohere | Together | HuggingFace</p>
      </div>
    </div>'''),

    # 10 - Core Components with bullets
    (10, 'content', 'Core Components', '''    <div class="row gap-sm" style="height: 100%; flex-wrap: wrap; align-content: flex-start;">
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px; width: 430px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Agent Framework</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li>Modular agents: Persona + Tools + Memory + Knowledge Base</li>
          <li>6 reasoning patterns: ReAct, CoT, ToT, Reflexion, Hierarchical, Goal</li>
          <li>MCP tool integration for external services</li>
          <li>Visual designer or JSON/Python API creation</li>
        </ul>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px; width: 430px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Workflow Engine</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li>DAG orchestration with topological sort execution</li>
          <li>12+ node types including Python code injection</li>
          <li>Parallel execution with automatic dependency management</li>
          <li>HITL nodes for human approval gates</li>
        </ul>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px; width: 430px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">AI Organization Manager (Patent Pending)</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li>Digital twin of corporate hierarchy structure</li>
          <li>Task delegation down, response aggregation up</li>
          <li>Human mirrors for oversight at every AI position</li>
          <li>Configurable autonomy levels per node</li>
        </ul>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px; width: 430px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Security Layer</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li>RBAC with role to permission to model mapping</li>
          <li>API key management with scoped access controls</li>
          <li>Rate limiting: RPM/TPM quotas per user/team</li>
          <li>Complete audit trails for compliance</li>
        </ul>
      </div>
    </div>'''),

    # 11 - Multi-Provider Section
    (11, 'section', 'Multi-Provider LLM Support', 'Unified access to 11+ providers'),

    # 12 - Supported Providers with UI config
    (12, 'content', 'Supported LLM Providers', '''    <div class="col gap-sm" style="height: 100%;">
      <div class="row gap-sm">
        <div style="background: linear-gradient(135deg, #ED1C24, #B81419); padding: 8px; border-radius: 6px; flex: 1; text-align: center;">
          <p style="font-size: 10px; color: #FFF; margin: 0; font-weight: 600;">Ollama (DEFAULT)</p>
          <p style="font-size: 7px; color: #FFD0D0; margin: 2px 0 0 0;">Free, Local, Private</p>
        </div>
        <div style="background: #FFF; padding: 8px; border-radius: 6px; flex: 1; text-align: center;">
          <p style="font-size: 10px; color: #1A3A5C; margin: 0; font-weight: 600;">OpenAI</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">GPT-4o, o1, o3</p>
        </div>
        <div style="background: #FFF; padding: 8px; border-radius: 6px; flex: 1; text-align: center;">
          <p style="font-size: 10px; color: #1A3A5C; margin: 0; font-weight: 600;">Anthropic</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Claude 4.5</p>
        </div>
        <div style="background: #FFF; padding: 8px; border-radius: 6px; flex: 1; text-align: center;">
          <p style="font-size: 10px; color: #1A3A5C; margin: 0; font-weight: 600;">Google</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Gemini 2.0</p>
        </div>
      </div>
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">UI Configuration (Admin - Providers)</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li>Add/edit providers with API keys stored encrypted in database</li>
          <li>Configure custom base URLs for self-hosted or proxy endpoints</li>
          <li>Set rate limits (requests per minute, tokens per minute) per provider</li>
          <li>Enable/disable providers with single click toggle</li>
          <li>Test connectivity and validate credentials before saving</li>
          <li>View usage statistics and cost breakdown per provider</li>
        </ul>
      </div>
    </div>'''),

    # 13 - Unified API Benefits
    (13, 'content', 'Unified API Benefits', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Key API Endpoints</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li>POST /api/v1/complete - Unified completion across any provider/model</li>
          <li>POST /api/v1/chat - Multi-turn conversation with message history</li>
          <li>POST /api/v1/embed - Generate embeddings for RAG applications</li>
          <li>POST /api/v1/agents/[id]/execute - Execute agent with input</li>
          <li>POST /api/v1/workflows/[id]/execute - Run workflow DAG pipeline</li>
          <li>GET /api/v1/executions/[id] - Retrieve execution status and results</li>
        </ul>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Abstraction Benefits</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li>Single API works with any provider - switch via provider parameter</li>
          <li>Consistent error handling, retry logic, and timeout management</li>
          <li>Automatic exponential backoff on rate limits</li>
          <li>Streaming support unified across all providers</li>
          <li>Standardized usage metrics and token counting</li>
          <li>OpenAPI/Swagger documentation at /api/docs</li>
        </ul>
      </div>
    </div>'''),

    # 14 - Agent Framework Section
    (14, 'section', 'Agent Framework', 'Building intelligent AI agents'),

    # 15 - What is an Agent
    (15, 'content', 'What is an AI Agent?', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 10px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Definition</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0; line-height: 1.4;">An AI Agent is an autonomous entity combining an LLM with tools, memory, and reasoning patterns to accomplish complex tasks. Unlike simple chatbots, agents can plan multi-step actions, use external tools, remember context across interactions, and iterate until goals are achieved.</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Agent Components</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li><b>Persona:</b> System prompt defining role, expertise, behavior constraints</li>
          <li><b>LLM:</b> The language model brain (any provider/model combination)</li>
          <li><b>Tools:</b> Functions the agent can invoke (DB, API, File, Search, MCP...)</li>
          <li><b>Memory:</b> Conversation history, working memory, long-term knowledge</li>
          <li><b>Reasoning:</b> Pattern for thinking (ReAct, CoT, ToT, Reflexion...)</li>
          <li><b>HITL:</b> Human-in-the-loop checkpoints for oversight and approval</li>
        </ul>
      </div>
    </div>'''),

    # 16 - Agent Reasoning Patterns
    (16, 'content', 'Agent Reasoning Patterns', '''    <div class="row gap-sm" style="height: 100%; flex-wrap: wrap; align-content: flex-start;">
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 8px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">ReAct (Reason + Act)</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0; padding-left: 12px; line-height: 1.2;">
          <li>Think then Act then Observe then Repeat</li>
          <li>Interleaved reasoning and tool execution</li>
          <li>Best for: multi-step tasks requiring tools</li>
        </ul>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 8px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Chain-of-Thought (CoT)</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0; padding-left: 12px; line-height: 1.2;">
          <li>Step-by-step reasoning before answer</li>
          <li>Explicit intermediate thinking steps</li>
          <li>Best for: math, logic, complex analysis</li>
        </ul>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 8px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Tree-of-Thoughts (ToT)</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0; padding-left: 12px; line-height: 1.2;">
          <li>Explore multiple reasoning paths in parallel</li>
          <li>Backtrack on dead ends, prune bad paths</li>
          <li>Best for: creative, open-ended problems</li>
        </ul>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px 8px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #ED1C24; margin: 0; font-weight: 600;">Reflexion</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0; padding-left: 12px; line-height: 1.2;">
          <li>Self-critique and iteratively improve</li>
          <li>Learn from mistakes within context</li>
          <li>Best for: iterative refinement tasks</li>
        </ul>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px 8px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #ED1C24; margin: 0; font-weight: 600;">Hierarchical</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0; padding-left: 12px; line-height: 1.2;">
          <li>Manager agent delegates to worker agents</li>
          <li>Multi-agent coordination and aggregation</li>
          <li>Best for: complex task decomposition</li>
        </ul>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 8px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Goal-Based</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0; padding-left: 12px; line-height: 1.2;">
          <li>Define goal, plan path, execute steps</li>
          <li>Dynamic replanning on failures</li>
          <li>Best for: autonomous objective completion</li>
        </ul>
      </div>
    </div>'''),

    # 17 - Tool Integration
    (17, 'content', 'Agent Tool Integration', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Built-in Tool Types</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li><b>Database:</b> Query SQLite, PostgreSQL, MySQL with SQL or ORM abstraction</li>
          <li><b>API:</b> Call REST/GraphQL endpoints with configurable auth headers</li>
          <li><b>File:</b> Read/write files, parse PDFs, Excel, CSV, Word documents</li>
          <li><b>Search:</b> Web search, vector similarity search, RAG retrieval</li>
          <li><b>Python:</b> Execute arbitrary Python code in secure sandbox</li>
        </ul>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">MCP (Model Context Protocol) Integration</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li>Connect external MCP servers as agent tools dynamically</li>
          <li>Auto-discovery of MCP tool schemas and parameters</li>
          <li>Pre-built servers: Filesystem, GitHub, Slack, Postgres, Puppeteer, Brave</li>
          <li>Create custom MCP servers in Python (FastMCP) or Node.js</li>
        </ul>
      </div>
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">UI Tool Management (Admin - Tools)</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li>Browse and enable/disable tools per agent from tool library</li>
          <li>Configure tool parameters (endpoints, credentials, limits)</li>
          <li>Test tools with sample inputs before deployment</li>
          <li>View tool usage analytics and error rates</li>
        </ul>
      </div>
    </div>'''),

    # 18 - Agent Creation via UI
    (18, 'content', 'Creating Agents via UI', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Visual Agent Designer (Agents - New Agent)</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li><b>Step 1 - Basic Info:</b> Name, description, category, searchable tags</li>
          <li><b>Step 2 - Provider/Model:</b> Select from dropdown (Ollama default, or cloud)</li>
          <li><b>Step 3 - Persona:</b> Rich text editor for system prompt with variables</li>
          <li><b>Step 4 - Tools:</b> Drag-drop from tool library, configure each tool params</li>
          <li><b>Step 5 - Knowledge Base:</b> Upload documents for RAG, select vector store</li>
          <li><b>Step 6 - Reasoning:</b> Select pattern (ReAct, CoT, ToT, etc.)</li>
          <li><b>Step 7 - HITL:</b> Configure approval checkpoints and notification channels</li>
          <li><b>Step 8 - Test:</b> Interactive chat panel to validate before saving</li>
        </ul>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">UI Features</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li>Live preview of agent behavior during configuration</li>
          <li>Version history with one-click rollback to previous versions</li>
          <li>Clone existing agents as templates for new agents</li>
          <li>Export/import agent definitions as JSON for backup or sharing</li>
        </ul>
      </div>
    </div>'''),

    # 19 - Agent JSON Example
    (19, 'content', 'Agent Definition: JSON Format', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #1A3A5C; padding: 8px; border-radius: 4px;">
        <p style="font-size: 6px; color: #7FDBFF; margin: 0; font-family: monospace; white-space: pre; line-height: 1.2;">{
  "name": "Research Assistant",
  "provider": "ollama",
  "model": "llama3.3:70b",
  "persona": "You are a research assistant. Analyze documents and synthesize findings.",
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
      <div style="background: #FFF; padding: 6px; border-radius: 4px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Python API Usage</p>
        <p style="font-size: 7px; color: #1A3A5C; margin: 3px 0 0 0; font-family: monospace;">from abhikarta import Agent</p>
        <p style="font-size: 7px; color: #1A3A5C; margin: 1px 0 0 0; font-family: monospace;">agent = Agent.from_json("research_agent.json")</p>
        <p style="font-size: 7px; color: #1A3A5C; margin: 1px 0 0 0; font-family: monospace;">result = agent.run("Analyze the Q3 earnings report and summarize key findings")</p>
      </div>
    </div>'''),

    # 20 - Agent HITL and Execution
    (20, 'content', 'Agent HITL and Execution Management', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Human-in-the-Loop for Agents</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li><b>Tool Approval:</b> Require human confirmation before specific tools execute</li>
          <li><b>Output Review:</b> Human reviews agent response before final delivery</li>
          <li><b>Confidence Threshold:</b> Auto-escalate to human if agent confidence low</li>
          <li><b>Notifications:</b> Slack, Teams, Email alerts for pending approvals</li>
          <li><b>Timeout Handling:</b> Auto-escalate if no human response in configured time</li>
        </ul>
      </div>
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Execution Viewer (Agents - Executions)</p>
        <ul style="font-size: 7px; color: #5A7A9C; margin: 3px 0 0 0; padding-left: 14px; line-height: 1.3;">
          <li><b>Timeline View:</b> Step-by-step execution trace with timestamps</li>
          <li><b>Thought Process:</b> View agent reasoning at each iteration</li>
          <li><b>Tool Calls:</b> Input/output of each tool invocation with timing</li>
          <li><b>Token Usage:</b> Tokens consumed and cost per execution</li>
          <li><b>Replay:</b> Re-run execution with different inputs for debugging</li>
          <li><b>Cancel/Override:</b> Stop runaway agents or override outputs</li>
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

print("Created slides 8-20")
