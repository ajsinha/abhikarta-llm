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
    # 9 - Cost Management
    (9, 'content', 'Challenge: AI Cost Management', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 10px; border-radius: 4px;">
        <p style="font-size: 11px; color: #ED1C24; margin: 0; font-weight: 600;">The Problem</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">• LLM API costs spiral unpredictably at scale</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Runaway loops generate unexpected $10K+ bills</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• No visibility into cost-per-feature or per-user</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Development/testing burns production budget</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 10px; border-radius: 4px;">
        <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Our Solution</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">• Ollama default: $0 cost for local development</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Rate limiting: RPM/TPM per user/team/org</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Token quotas with automatic cutoff</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Cost allocation by execution, workflow, agent</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Model tier routing: cheap→expensive escalation</p>
      </div>
    </div>'''),

    # 10 - Architecture Section
    (10, 'section', 'Platform Architecture', 'System design and components'),

    # 11 - Architecture Overview
    (11, 'content', 'Architecture Overview', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 6px 10px; border-radius: 4px; text-align: center;">
        <p style="font-size: 9px; color: #5A7A9C; margin: 0; font-weight: 600;">USER INTERFACES</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 2px 0 0 0;">Web UI (Bootstrap 5) | REST API | Admin Console | CLI (Click/Rich)</p>
      </div>
      <div style="background: #FFF; border: 2px solid #0079C1; padding: 8px; border-radius: 6px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600; text-align: center;">ABHIKARTA-LLM CORE (Flask + SQLAlchemy)</p>
        <div class="row gap-sm" style="margin-top: 6px;">
          <div style="background: #E8F4FC; padding: 6px; border-radius: 4px; flex: 1; text-align: center;">
            <p style="font-size: 8px; color: #0079C1; margin: 0; font-weight: 600;">Agent Engine</p>
            <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Personas, Tools, Memory</p>
          </div>
          <div style="background: #E8F4FC; padding: 6px; border-radius: 4px; flex: 1; text-align: center;">
            <p style="font-size: 8px; color: #0079C1; margin: 0; font-weight: 600;">Workflow DAG</p>
            <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">12+ Node Types</p>
          </div>
          <div style="background: #FFE8E8; padding: 6px; border-radius: 4px; flex: 1; text-align: center;">
            <p style="font-size: 8px; color: #ED1C24; margin: 0; font-weight: 600;">AI Org Manager</p>
            <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Patent Pending</p>
          </div>
          <div style="background: #E8F4FC; padding: 6px; border-radius: 4px; flex: 1; text-align: center;">
            <p style="font-size: 8px; color: #0079C1; margin: 0; font-weight: 600;">Security/RBAC</p>
            <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Model Perms</p>
          </div>
        </div>
      </div>
      <div style="background: #FFF; padding: 6px 10px; border-radius: 4px; text-align: center;">
        <p style="font-size: 9px; color: #5A7A9C; margin: 0; font-weight: 600;">LLM PROVIDERS (11+ Unified)</p>
        <p style="font-size: 8px; color: #ED1C24; margin: 2px 0 0 0;">Ollama (Default) | OpenAI | Anthropic | Google | Azure | AWS | Groq | Mistral | Cohere | Together | HuggingFace</p>
      </div>
    </div>'''),

    # 12 - Core Components with bullets
    (12, 'content', 'Core Components', '''    <div class="row gap-sm" style="height: 100%; flex-wrap: wrap; align-content: flex-start;">
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px; width: 430px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Agent Framework</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• Modular agents: Persona + Tools + Memory + KB</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• 6 reasoning patterns: ReAct, CoT, ToT, Reflexion...</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• MCP tool integration for external services</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Visual designer or JSON/Python creation</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px; width: 430px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Workflow Engine</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• DAG orchestration with topological execution</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• 12+ node types including Python code nodes</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Parallel execution with dependency management</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• HITL nodes for human approval gates</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px; width: 430px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">AI Organization Manager (Patent Pending)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• Digital twin of corporate hierarchy</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Task delegation down, response aggregation up</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Human mirrors for every AI position</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Configurable autonomy levels per node</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px; width: 430px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Security Layer</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• RBAC with role→permission→model mapping</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• API key management with scoped access</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Rate limiting: RPM/TPM quotas</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Complete audit trails for compliance</p>
      </div>
    </div>'''),

    # 13 - Multi-Provider Section
    (13, 'section', 'Multi-Provider LLM Support', 'Unified access to 11+ providers'),

    # 14 - Supported Providers with configuration
    (14, 'content', 'Supported LLM Providers', '''    <div class="col gap-sm" style="height: 100%;">
      <div class="row gap-sm">
        <div style="background: linear-gradient(135deg, #ED1C24, #B81419); padding: 8px; border-radius: 6px; flex: 1; text-align: center;">
          <p style="font-size: 11px; color: #FFF; margin: 0; font-weight: 600;">Ollama (DEFAULT)</p>
          <p style="font-size: 7px; color: #FFD0D0; margin: 2px 0 0 0;">Free, Local, Private</p>
        </div>
        <div style="background: #FFF; padding: 8px; border-radius: 6px; flex: 1; text-align: center;">
          <p style="font-size: 11px; color: #1A3A5C; margin: 0; font-weight: 600;">OpenAI</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">GPT-4o, o1, o3</p>
        </div>
        <div style="background: #FFF; padding: 8px; border-radius: 6px; flex: 1; text-align: center;">
          <p style="font-size: 11px; color: #1A3A5C; margin: 0; font-weight: 600;">Anthropic</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Claude 4.5</p>
        </div>
        <div style="background: #FFF; padding: 8px; border-radius: 6px; flex: 1; text-align: center;">
          <p style="font-size: 11px; color: #1A3A5C; margin: 0; font-weight: 600;">Google</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Gemini 2.0</p>
        </div>
      </div>
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">UI Configuration (Admin → Providers)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• Add/edit providers with API keys securely stored</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Configure base URLs for self-hosted endpoints</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Set rate limits (RPM/TPM) per provider</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Enable/disable providers with one click</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Test connectivity before saving</p>
      </div>
    </div>'''),

    # 15 - Unified API Benefits
    (15, 'content', 'Unified API Benefits', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Key API Endpoints</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• POST /api/v1/complete - Unified completion (any provider)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• POST /api/v1/chat - Multi-turn conversations</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• POST /api/v1/embed - Generate embeddings</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• POST /api/v1/agents/{id}/execute - Run agent</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• POST /api/v1/workflows/{id}/execute - Run workflow</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Benefits</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• Single API, any provider - switch via "provider" parameter</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Consistent error handling across providers</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Automatic retry with exponential backoff</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Streaming support for all providers</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Standardized usage metrics & cost tracking</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• OpenAPI/Swagger documentation at /api/docs</p>
      </div>
    </div>'''),

    # 16 - Agent Framework Section
    (16, 'section', 'Agent Framework', 'Building intelligent AI agents'),

    # 17 - What is an Agent
    (17, 'content', 'What is an AI Agent?', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 10px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Definition</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0; line-height: 1.4;">An AI Agent is an autonomous entity combining an LLM with tools, memory, and reasoning patterns to accomplish tasks. Unlike simple chatbots, agents can plan, use tools, remember context, and iterate until goals are achieved.</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Agent Components</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• <b>Persona</b>: System prompt defining role, expertise, constraints</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>LLM</b>: The language model (any provider/model)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Tools</b>: Functions the agent can call (DB, API, File, MCP...)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Memory</b>: Conversation history, working memory, long-term KB</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Reasoning</b>: Pattern for thinking (ReAct, CoT, ToT...)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>HITL</b>: Human checkpoints for oversight</p>
      </div>
    </div>'''),

    # 18 - Agent Reasoning Patterns
    (18, 'content', 'Agent Reasoning Patterns', '''    <div class="row gap-sm" style="height: 100%; flex-wrap: wrap; align-content: flex-start;">
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 8px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">ReAct (Reason + Act)</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">• Think → Act → Observe → Repeat</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Interleaved reasoning and tool use</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Best for: multi-step tasks with tools</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 8px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Chain-of-Thought (CoT)</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">• Step-by-step reasoning before answer</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Explicit intermediate steps</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Best for: math, logic, analysis</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 8px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Tree-of-Thoughts (ToT)</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">• Explore multiple reasoning paths</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Backtrack on dead ends</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Best for: creative, open-ended problems</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px 8px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #ED1C24; margin: 0; font-weight: 600;">Reflexion</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">• Self-critique and improve</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Learn from mistakes in-context</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Best for: iterative refinement</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px 8px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #ED1C24; margin: 0; font-weight: 600;">Hierarchical</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">• Manager delegates to workers</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Multi-agent coordination</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Best for: complex decomposition</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 8px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Goal-Based</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">• Define goal, plan path, execute</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Dynamic replanning on failure</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Best for: autonomous objectives</p>
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

print(f"Created slides 9-18")
