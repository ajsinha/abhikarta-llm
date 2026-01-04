import os

def content_slide(num, title, content):
    return f'''<!DOCTYPE html>
<html>
<head></head>
<body class="col" style="width: 960px; height: 540px; background: #F4F9FD; padding: 20px 30px; box-sizing: border-box;">
  <div class="row" style="justify-content: space-between; align-items: center; margin-bottom: 10px;">
    <p style="font-size: 15px; color: #0079C1; margin: 0; font-weight: 600;">{title}</p>
    <p style="font-size: 9px; color: #5A7A9C; margin: 0;">Abhikarta-LLM v1.4.7</p>
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

def thank_you_slide(num):
    return f'''<!DOCTYPE html>
<html>
<head></head>
<body class="col center" style="width: 960px; height: 540px; background: #F4F9FD; padding: 40px; box-sizing: border-box;">
  <h1 style="font-size: 42px; color: #0079C1; margin: 0; font-weight: 700;">Thank You</h1>
  <p style="font-size: 18px; color: #1A3A5C; margin: 12px 0 0 0;">Abhikarta-LLM</p>
  <p style="font-size: 12px; color: #5A7A9C; margin: 6px 0 0 0;">Enterprise AI Orchestration Platform v1.4.7</p>
  <div class="row gap" style="margin-top: 20px;">
    <div style="background: #E8F4FC; padding: 10px 16px; border-radius: 6px; text-align: center;">
      <p style="font-size: 16px; color: #ED1C24; margin: 0; font-weight: 600;">11+ Providers</p>
    </div>
    <div style="background: #E8F4FC; padding: 10px 16px; border-radius: 6px; text-align: center;">
      <p style="font-size: 16px; color: #0079C1; margin: 0; font-weight: 600;">100+ Models</p>
    </div>
  </div>
  <p style="font-size: 8px; color: #5A7A9C; margin: 24px 0 0 0;">Copyright © 2025-2030 Ashutosh Sinha | All Rights Reserved | Patent Pending | Slide {num}</p>
</body>
</html>'''

slides = [
    # 41 - Use Case: Customer Service
    (41, 'content', 'Use Case: Customer Service Bot', '''    <div class="row gap-sm" style="height: 100%;">
      <div class="col gap-sm" style="flex: 1;">
        <div style="background: #FFF; padding: 6px; border-radius: 4px;">
          <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Key Benefits</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">• 70% auto-resolution rate</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• 24/7 availability</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Consistent quality</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Escalation to humans</p>
        </div>
        <div style="background: #FFF; border-left: 2px solid #ED1C24; padding: 6px; border-radius: 4px;">
          <p style="font-size: 9px; color: #ED1C24; margin: 0; font-weight: 600;">Implementation</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">• RAG over FAQ + docs</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• CRM tool integration</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Sentiment detection</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• HITL for complaints</p>
        </div>
      </div>
      <div style="flex: 1.2; background: #1A3A5C; padding: 6px; border-radius: 4px;">
        <p style="font-size: 6px; color: #7FDBFF; margin: 0; font-family: monospace; white-space: pre; line-height: 1.2;">{"name": "Support Bot",
 "provider": "ollama",
 "tools": [
   {"type": "rag", "kb": "faq_docs"},
   {"type": "api", "endpoint": "crm"}
 ],
 "hitl": {
   "escalate_on": ["angry", "refund"],
   "notify": ["slack"]
 }
}</p>
      </div>
    </div>'''),

    # 42 - Use Case: Document Analysis
    (42, 'content', 'Use Case: Document Analysis', '''    <div class="row gap-sm" style="height: 100%;">
      <div class="col gap-sm" style="flex: 1;">
        <div style="background: #FFF; padding: 6px; border-radius: 4px;">
          <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Key Benefits</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">• 90% faster review</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Improved accuracy</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Consistent extraction</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Audit trail</p>
        </div>
        <div style="background: #FFF; border-left: 2px solid #ED1C24; padding: 6px; border-radius: 4px;">
          <p style="font-size: 9px; color: #ED1C24; margin: 0; font-weight: 600;">Implementation</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">• DAG workflow pipeline</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• PDF/DOCX parsing</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Parallel extraction</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Human approval gate</p>
        </div>
      </div>
      <div style="flex: 1.2; background: #1A3A5C; padding: 6px; border-radius: 4px;">
        <p style="font-size: 6px; color: #7FDBFF; margin: 0; font-family: monospace; white-space: pre; line-height: 1.2;">{"name": "Contract Review",
 "nodes": [
   {"id": "parse", "type": "tool",
    "tool": "file_read"},
   {"id": "extract", "type": "llm",
    "prompt": "Extract terms..."},
   {"id": "review", "type": "human",
    "message": "Review extraction"},
   {"id": "save", "type": "tool",
    "tool": "db_insert"}
 ]
}</p>
      </div>
    </div>'''),

    # 43 - Use Case: Research & Reports
    (43, 'content', 'Use Case: Research & Reports', '''    <div class="row gap-sm" style="height: 100%;">
      <div class="col gap-sm" style="flex: 1;">
        <div style="background: #FFF; padding: 6px; border-radius: 4px;">
          <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Key Benefits</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">• Hours → minutes</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Comprehensive coverage</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Multi-source synthesis</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Consistent formatting</p>
        </div>
        <div style="background: #FFF; border-left: 2px solid #ED1C24; padding: 6px; border-radius: 4px;">
          <p style="font-size: 9px; color: #ED1C24; margin: 0; font-weight: 600;">Implementation</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">• AI Org with researcher swarm</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Web search + RAG tools</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Director aggregates</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Human reviews final</p>
        </div>
      </div>
      <div style="flex: 1.2; background: #1A3A5C; padding: 6px; border-radius: 4px;">
        <p style="font-size: 6px; color: #7FDBFF; margin: 0; font-family: monospace; white-space: pre; line-height: 1.2;">{"name": "Research Team",
 "positions": [
   {"id": "director",
    "agent": "synthesizer",
    "autonomy": "supervised"},
   {"id": "analyst1",
    "agent": "web_researcher",
    "reports_to": "director"},
   {"id": "analyst2",
    "agent": "db_researcher",
    "reports_to": "director"}
 ]
}</p>
      </div>
    </div>'''),

    # 44 - Use Case: Developer Productivity
    (44, 'content', 'Use Case: Developer Productivity', '''    <div class="row gap-sm" style="height: 100%;">
      <div class="col gap-sm" style="flex: 1;">
        <div style="background: #FFF; padding: 6px; border-radius: 4px;">
          <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Key Benefits</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">• Faster code reviews</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Auto documentation</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Test generation</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Code privacy (local)</p>
        </div>
        <div style="background: #FFF; border-left: 2px solid #ED1C24; padding: 6px; border-radius: 4px;">
          <p style="font-size: 9px; color: #ED1C24; margin: 0; font-weight: 600;">Implementation</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">• Ollama for code privacy</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• GitHub MCP tool</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Python code execution</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• PR comment integration</p>
        </div>
      </div>
      <div style="flex: 1.2; background: #1A3A5C; padding: 6px; border-radius: 4px;">
        <p style="font-size: 6px; color: #7FDBFF; margin: 0; font-family: monospace; white-space: pre; line-height: 1.2;">{"name": "Code Reviewer",
 "provider": "ollama",
 "model": "codellama:34b",
 "tools": [
   {"type": "mcp",
    "server": "github"},
   {"type": "python",
    "sandbox": true}
 ],
 "persona": "Senior code reviewer..."
}</p>
      </div>
    </div>'''),

    # 45 - Use Case: Risk & Compliance
    (45, 'content', 'Use Case: Risk & Compliance', '''    <div class="row gap-sm" style="height: 100%;">
      <div class="col gap-sm" style="flex: 1;">
        <div style="background: #FFF; padding: 6px; border-radius: 4px;">
          <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Key Benefits</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">• 24/7 monitoring</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Pattern detection</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Comprehensive audit</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Regulatory ready</p>
        </div>
        <div style="background: #FFF; border-left: 2px solid #ED1C24; padding: 6px; border-radius: 4px;">
          <p style="font-size: 9px; color: #ED1C24; margin: 0; font-weight: 600;">Implementation</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">• Swarm for monitoring</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• DB + email analysis</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Instant alerts</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">• Human review queue</p>
        </div>
      </div>
      <div style="flex: 1.2; background: #1A3A5C; padding: 6px; border-radius: 4px;">
        <p style="font-size: 6px; color: #7FDBFF; margin: 0; font-family: monospace; white-space: pre; line-height: 1.2;">{"name": "Compliance Swarm",
 "agents": [
   "transaction_monitor",
   "email_analyzer",
   "policy_checker"
 ],
 "coordination": "event_driven",
 "triggers": [
   {"event": "new_transaction"},
   {"event": "email_received"}
 ],
 "hitl": {"flag_threshold": 0.8}
}</p>
      </div>
    </div>'''),

    # 46 - Appendix Section
    (46, 'section', 'Appendix', 'Competitive analysis & acknowledgements'),

    # 47 - Competitive Comparison
    (47, 'content', 'Competitive Comparison', '''    <div class="col gap-sm" style="height: 100%;">
      <div class="row gap-sm" style="align-items: center;">
        <div style="background: #FFF; padding: 4px 6px; border-radius: 4px; width: 140px;"><p style="font-size: 8px; color: #0079C1; margin: 0; font-weight: 600;">Feature</p></div>
        <div style="background: #ED1C24; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 8px; color: #FFF; margin: 0; font-weight: 600;">Abhikarta</p></div>
        <div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 8px; color: #1A3A5C; margin: 0;">LangChain</p></div>
        <div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 8px; color: #1A3A5C; margin: 0;">AutoGen</p></div>
        <div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 8px; color: #1A3A5C; margin: 0;">CrewAI</p></div>
      </div>
      <div class="row gap-sm"><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; width: 140px;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Multi-Provider</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #0079C1; margin: 0; font-weight: 600;">11+ Native</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Via Plugins</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Limited</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Limited</p></div></div>
      <div class="row gap-sm"><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; width: 140px;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Visual Workflow</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #0079C1; margin: 0; font-weight: 600;">Built-in DAG</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">LangGraph</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #ED1C24; margin: 0;">Code Only</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #ED1C24; margin: 0;">Code Only</p></div></div>
      <div class="row gap-sm"><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; width: 140px;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">AI Org Hierarchy</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #0079C1; margin: 0; font-weight: 600;">Full (Patent)</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #ED1C24; margin: 0;">None</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Basic</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Basic</p></div></div>
      <div class="row gap-sm"><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; width: 140px;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Enterprise RBAC</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #0079C1; margin: 0; font-weight: 600;">Full + Model</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #ED1C24; margin: 0;">None</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #ED1C24; margin: 0;">None</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #ED1C24; margin: 0;">None</p></div></div>
      <div class="row gap-sm"><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; width: 140px;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">HITL Controls</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #0079C1; margin: 0; font-weight: 600;">Comprehensive</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Interrupt</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Basic</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Basic</p></div></div>
      <div class="row gap-sm"><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; width: 140px;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Local Models</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #0079C1; margin: 0; font-weight: 600;">Ollama Default</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Optional</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Optional</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Optional</p></div></div>
    </div>'''),

    # 48 - Open Source Acknowledgements
    (48, 'content', 'Open Source Acknowledgements', '''    <div class="row gap-sm" style="height: 100%; flex-wrap: wrap; align-content: flex-start;">
      <div style="background: #FFF; padding: 6px; border-radius: 4px; width: 280px; border-left: 3px solid #0079C1;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">LLM & AI</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">LangChain, LlamaIndex, Ollama, OpenAI SDK, Anthropic SDK, Sentence Transformers, ChromaDB, FAISS</p>
      </div>
      <div style="background: #FFF; padding: 6px; border-radius: 4px; width: 280px; border-left: 3px solid #0079C1;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Web Framework</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Flask, SQLAlchemy, Pydantic, Bootstrap 5, Jinja2, Gunicorn</p>
      </div>
      <div style="background: #FFF; padding: 6px; border-radius: 4px; width: 280px; border-left: 3px solid #0079C1;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Infrastructure</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Docker, PostgreSQL, Redis, Kafka, RabbitMQ</p>
      </div>
      <div style="background: #FFF; padding: 6px; border-radius: 4px; width: 280px; border-left: 3px solid #0079C1;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Utilities</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Click, Rich, PyYAML, Requests, aiohttp, NumPy, Pandas, PyPDF</p>
      </div>
    </div>
    <div style="background: #FFF; padding: 8px; border-radius: 4px; margin-top: 6px;">
      <p style="font-size: 8px; color: #5A7A9C; margin: 0; text-align: center;">Thank you to all open source contributors. Abhikarta-LLM incorporates these projects under their respective licenses.</p>
    </div>'''),

    # 49 - Licensing & IP
    (49, 'content', 'Licensing & Intellectual Property', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 10px; border-radius: 4px;">
        <p style="font-size: 11px; color: #ED1C24; margin: 0; font-weight: 600;">Proprietary License</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Abhikarta-LLM is proprietary software. All rights reserved. Unauthorized copying, modification, distribution, or use is strictly prohibited.</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 10px; border-radius: 4px;">
        <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Patent Pending</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">AI Organization Management technology and hierarchical AI governance framework are patent pending innovations.</p>
      </div>
      <div style="background: #FFF; padding: 10px; border-radius: 4px;">
        <p style="font-size: 11px; color: #1A3A5C; margin: 0; font-weight: 600;">Copyright</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Contact: ajsinha@gmail.com</p>
      </div>
    </div>'''),
]

# Thank you slide
thank_you = (50, 'thankyou', None, None)

for item in slides:
    num, stype, title, content = item
    filename = f"slide{num:02d}.html"
    if stype == 'section':
        html = section_slide(num, title, content)
    else:
        html = content_slide(num, title, content)
    with open(filename, 'w') as f:
        f.write(html)

# Write thank you slide
with open('slide50.html', 'w') as f:
    f.write(thank_you_slide(50))

print(f"Created slides 41-50 (Use Cases, Appendix, Thank You)")
