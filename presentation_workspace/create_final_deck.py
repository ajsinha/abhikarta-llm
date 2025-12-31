import os

def title_slide():
    return '''<!DOCTYPE html>
<html>
<head></head>
<body class="col center" style="width: 960px; height: 540px; background: #F4F9FD; padding: 40px; box-sizing: border-box;">
  <h1 style="font-size: 44px; color: #0079C1; margin: 0; font-weight: 700;">Abhikarta-LLM</h1>
  <p style="font-size: 18px; color: #1A3A5C; margin: 10px 0 0 0;">Enterprise AI Orchestration Platform</p>
  <p style="font-size: 13px; color: #5A7A9C; margin: 6px 0 0 0;">Version 1.4.6</p>
  <div class="row gap" style="margin-top: 20px;">
    <div style="background: #E8F4FC; padding: 10px 18px; border-radius: 6px; text-align: center;">
      <p style="font-size: 22px; color: #0079C1; margin: 0; font-weight: 600;">11+</p>
      <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Providers</p>
    </div>
    <div style="background: #E8F4FC; padding: 10px 18px; border-radius: 6px; text-align: center;">
      <p style="font-size: 22px; color: #1A3A5C; margin: 0; font-weight: 600;">100+</p>
      <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Models</p>
    </div>
    <div style="background: #E8F4FC; padding: 10px 18px; border-radius: 6px; text-align: center;">
      <p style="font-size: 22px; color: #ED1C24; margin: 0; font-weight: 600;">$0</p>
      <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Local Models</p>
    </div>
  </div>
  <p style="font-size: 8px; color: #5A7A9C; margin: 30px 0 0 0;">Copyright 2025-2030 Ashutosh Sinha | All Rights Reserved | Patent Pending</p>
</body>
</html>'''

def section_slide(num, title, subtitle):
    return f'''<!DOCTYPE html>
<html>
<head></head>
<body class="col center" style="width: 960px; height: 540px; background: #0079C1; padding: 50px; box-sizing: border-box;">
  <p style="font-size: 13px; color: #FFFFFF; margin: 0; opacity: 0.7;">Section</p>
  <h1 style="font-size: 32px; color: #FFFFFF; margin: 10px 0 0 0; font-weight: 700;">{title}</h1>
  <p style="font-size: 13px; color: #FFFFFF; margin: 8px 0 0 0; opacity: 0.8;">{subtitle}</p>
  <p style="font-size: 8px; color: #FFFFFF; margin: 30px 0 0 0; opacity: 0.6;">Copyright 2025-2030 Ashutosh Sinha | Patent Pending</p>
</body>
</html>'''

def content_slide(num, title, content):
    return f'''<!DOCTYPE html>
<html>
<head></head>
<body class="col" style="width: 960px; height: 540px; background: #F4F9FD; padding: 30px 40px; box-sizing: border-box;">
  <div class="row" style="justify-content: space-between; align-items: center; margin-bottom: 8px;">
    <p style="font-size: 15px; color: #0079C1; margin: 0; font-weight: 600;">{title}</p>
    <p style="font-size: 9px; color: #5A7A9C; margin: 0;">Abhikarta-LLM v1.4.6</p>
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

def thank_you_slide(num):
    return f'''<!DOCTYPE html>
<html>
<head></head>
<body class="col center" style="width: 960px; height: 540px; background: #F4F9FD; padding: 50px; box-sizing: border-box;">
  <h1 style="font-size: 42px; color: #0079C1; margin: 0; font-weight: 700;">Thank You</h1>
  <p style="font-size: 18px; color: #1A3A5C; margin: 12px 0 0 0;">Abhikarta-LLM</p>
  <p style="font-size: 12px; color: #5A7A9C; margin: 6px 0 0 0;">Enterprise AI Orchestration Platform v1.4.6</p>
  <div class="row gap" style="margin-top: 20px;">
    <div style="background: #E8F4FC; padding: 10px 16px; border-radius: 6px; text-align: center;">
      <p style="font-size: 16px; color: #ED1C24; margin: 0; font-weight: 600;">11+ Providers</p>
    </div>
    <div style="background: #E8F4FC; padding: 10px 16px; border-radius: 6px; text-align: center;">
      <p style="font-size: 16px; color: #0079C1; margin: 0; font-weight: 600;">100+ Models</p>
    </div>
  </div>
  <p style="font-size: 8px; color: #5A7A9C; margin: 24px 0 0 0;">Copyright 2025-2030 Ashutosh Sinha | All Rights Reserved | Patent Pending</p>
</body>
</html>'''

# All slides definition
slides = []

# 1 - Title
slides.append((1, 'title', None, None))

# 2 - The AI Revolution
slides.append((2, 'content', 'The AI Revolution in Enterprise', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 10px; border-radius: 6px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">From Traditional AI to Generative AI</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0; line-height: 1.4;">Traditional AI excelled at classification and prediction. Generative AI (GenAI) creates new content - text, code, images, analysis. Large Language Models (LLMs) like GPT-4, Claude, and Llama have transformed what machines can accomplish.</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Enterprise Impact</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">McKinsey estimates GenAI could add $2.6-4.4 trillion annually across industries</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 2px 0 0 0;">82% of organizations are exploring AI agents for automation</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 2px 0 0 0;">Knowledge work productivity gains of 20-40% are achievable</p>
      </div>
      <div style="background: #FFE8E8; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">The Challenge</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">Only 44% have security policies for AI. Most lack governance, oversight, and control.</p>
      </div>
    </div>'''))

# 3 - What is Agentic AI
slides.append((3, 'content', 'What is Agentic AI?', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 10px; border-radius: 6px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Definition</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0; line-height: 1.4;">Agentic AI refers to AI systems that can autonomously plan, reason, use tools, and take actions to accomplish goals. Unlike simple chatbots, agents iterate until objectives are achieved.</p>
      </div>
      <div class="row gap-sm">
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px; flex: 1;">
          <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Chatbot</p>
          <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">Single response to query</p>
          <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">No tool access</p>
          <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">No memory across turns</p>
        </div>
        <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px; flex: 1;">
          <p style="font-size: 9px; color: #ED1C24; margin: 0; font-weight: 600;">AI Agent</p>
          <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">Plans and iterates to goal</p>
          <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Uses tools (DB, API, code)</p>
          <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Maintains context and memory</p>
        </div>
      </div>
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #1A3A5C; margin: 0; font-weight: 600;">Agent Components: LLM + Tools + Memory + Reasoning + Goals</p>
      </div>
    </div>'''))

# 4 - Why Orchestration Matters
slides.append((4, 'content', 'Why AI Orchestration Matters', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">The Need for Orchestration</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0; line-height: 1.4;">Real enterprise tasks require multiple AI agents working together - research teams, approval chains, multi-step workflows. Orchestration coordinates these agents for reliable, governed outcomes.</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Without Orchestration</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">Shadow AI - employees use ChatGPT without oversight</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">No audit trail for compliance or debugging</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Costs spiral without rate limiting or quotas</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">No human oversight on critical decisions</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">With Orchestration</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">Centralized governance and visibility</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Complete audit logging for compliance</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Cost control with usage limits</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Human-in-the-loop at every level</p>
      </div>
    </div>'''))

# 5 - Why Abhikarta
slides.append((5, 'content', 'Why Abhikarta-LLM for Enterprise?', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Purpose-Built for Enterprise AI</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0; line-height: 1.4;">Abhikarta-LLM addresses the governance gap in enterprise AI adoption. While other frameworks focus on capabilities, Abhikarta prioritizes security, oversight, and organizational alignment.</p>
      </div>
      <div class="row gap-sm">
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px; border-radius: 4px; flex: 1;">
          <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Multi-Provider</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">11+ LLM providers</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">No vendor lock-in</p>
        </div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px; border-radius: 4px; flex: 1;">
          <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Visual Design</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">No-code agent builder</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">DAG workflow editor</p>
        </div>
        <div style="background: #FFE8E8; border-left: 3px solid #ED1C24; padding: 6px; border-radius: 4px; flex: 1;">
          <p style="font-size: 9px; color: #ED1C24; margin: 0; font-weight: 600;">AI Organizations</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Patent-pending</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">Hierarchy + HITL</p>
        </div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px; border-radius: 4px; flex: 1;">
          <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Enterprise RBAC</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Model-level perms</p>
          <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">Full audit trails</p>
        </div>
      </div>
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 9px; color: #1A3A5C; margin: 0; font-weight: 600;">Result: Safe, governed AI that aligns with how enterprises actually operate</p>
      </div>
    </div>'''))

# 6 - TOC
slides.append((6, 'content', 'Table of Contents', '''    <div class="row gap" style="height: 100%;">
      <div class="col gap-sm" style="flex: 1;">
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">1. Market Challenges</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">2. Platform Architecture</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">3. Multi-Provider LLM Support</p></div>
        <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">4. Agent Framework</p></div>
        <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">5. Workflow DAG System</p></div>
        <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">6. Agent Swarms</p></div>
      </div>
      <div class="col gap-sm" style="flex: 1;">
        <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">7. AI Organizations (Patent)</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">8. RBAC and Security</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">9. Notifications Integration</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">10. Use Cases with Examples</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">11. Competitive Analysis</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">12. Appendix</p></div>
      </div>
    </div>'''))

# 7 - Market Challenges Section
slides.append((7, 'section', 'Market Challenges', 'Problems solved by Abhikarta-LLM'))

# 8 - Provider Lock-In
slides.append((8, 'content', 'Challenge: Provider Lock-In', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 10px; border-radius: 4px;">
        <p style="font-size: 11px; color: #ED1C24; margin: 0; font-weight: 600;">The Problem</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Organizations commit to single LLM provider (OpenAI, Anthropic, etc.)</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Provider-specific code patterns create high switching costs</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Pricing changes impact budgets with no alternatives</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Service disruptions halt production workloads</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 10px; border-radius: 4px;">
        <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Our Solution</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Unified abstraction layer across 11+ providers</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Same code works with any provider - switch via config</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Automatic failover between providers on errors</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Best-of-breed model selection per use case</p>
      </div>
    </div>'''))

# 9 - Governance Gaps
slides.append((9, 'content', 'Challenge: AI Governance Gaps', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 10px; border-radius: 4px;">
        <p style="font-size: 11px; color: #ED1C24; margin: 0; font-weight: 600;">The Problem</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Shadow AI proliferates - employees use ChatGPT without oversight</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Sensitive data leaked to external AI services</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">No audit trail for AI-generated content</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Regulatory compliance gaps (GDPR, HIPAA, SOX)</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 10px; border-radius: 4px;">
        <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Our Solution</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Centralized platform with RBAC at model level</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Complete audit logging of all LLM interactions</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Rate limiting per user, team, organization</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Local Ollama models for sensitive workloads</p>
      </div>
    </div>'''))

# 10 - Architecture Section
slides.append((10, 'section', 'Platform Architecture', 'System design and components'))

# 11 - Architecture Overview
slides.append((11, 'content', 'Architecture Overview', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 6px 10px; border-radius: 4px; text-align: center;">
        <p style="font-size: 9px; color: #5A7A9C; margin: 0; font-weight: 600;">USER INTERFACES</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 2px 0 0 0;">Web UI (Bootstrap 5) | REST API | Admin Console | CLI</p>
      </div>
      <div style="background: #FFF; border: 2px solid #0079C1; padding: 8px; border-radius: 6px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600; text-align: center;">ABHIKARTA-LLM CORE (Flask + SQLAlchemy)</p>
        <div class="row gap-sm" style="margin-top: 6px;">
          <div style="background: #E8F4FC; padding: 6px; border-radius: 4px; flex: 1; text-align: center;">
            <p style="font-size: 8px; color: #0079C1; margin: 0; font-weight: 600;">Agent Engine</p>
          </div>
          <div style="background: #E8F4FC; padding: 6px; border-radius: 4px; flex: 1; text-align: center;">
            <p style="font-size: 8px; color: #0079C1; margin: 0; font-weight: 600;">Workflow DAG</p>
          </div>
          <div style="background: #FFE8E8; padding: 6px; border-radius: 4px; flex: 1; text-align: center;">
            <p style="font-size: 8px; color: #ED1C24; margin: 0; font-weight: 600;">AI Org Manager</p>
          </div>
          <div style="background: #E8F4FC; padding: 6px; border-radius: 4px; flex: 1; text-align: center;">
            <p style="font-size: 8px; color: #0079C1; margin: 0; font-weight: 600;">Security/RBAC</p>
          </div>
        </div>
      </div>
      <div style="background: #FFF; padding: 6px 10px; border-radius: 4px; text-align: center;">
        <p style="font-size: 9px; color: #ED1C24; margin: 0; font-weight: 600;">LLM PROVIDERS (11+ Unified)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 2px 0 0 0;">Ollama (Default) | OpenAI | Anthropic | Google | Azure | AWS | Groq | Mistral | Cohere | Together | HuggingFace</p>
      </div>
    </div>'''))

# 12 - Core Components
slides.append((12, 'content', 'Core Components', '''    <div class="row gap-sm" style="height: 100%; flex-wrap: wrap; align-content: flex-start;">
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px; width: 420px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Agent Framework</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">Modular agents: Persona + Tools + Memory + Knowledge Base</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">6 reasoning patterns: ReAct, CoT, ToT, Reflexion, Hierarchical, Goal</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">MCP tool integration for external services</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px; width: 420px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Workflow Engine</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">DAG orchestration with topological execution</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">12+ node types including Python code nodes</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Parallel execution with HITL approval gates</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px; width: 420px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">AI Organization Manager (Patent Pending)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">Digital twin of corporate hierarchy</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Task delegation down, response aggregation up</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Human mirrors with configurable autonomy</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px; width: 420px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Security Layer</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">RBAC with role to permission to model mapping</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">API key management with scoped access</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Rate limiting and complete audit trails</p>
      </div>
    </div>'''))

# 13 - Multi-Provider Section
slides.append((13, 'section', 'Multi-Provider LLM Support', 'Unified access to 11+ providers'))

# 14 - Providers
slides.append((14, 'content', 'Supported LLM Providers', '''    <div class="col gap-sm" style="height: 100%;">
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
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">UI Configuration (Admin - Providers)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">Add/edit providers with API keys securely stored in database</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Configure base URLs for self-hosted endpoints (Azure, vLLM)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Set rate limits (RPM/TPM) per provider with test connectivity</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Enable/disable providers and models with one click</p>
      </div>
    </div>'''))

# 15 - Unified API
slides.append((15, 'content', 'Unified API Benefits', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Key API Endpoints</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">POST /api/v1/complete - Unified completion across any provider</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">POST /api/v1/chat - Multi-turn conversations with history</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">POST /api/v1/embed - Generate embeddings for RAG</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">POST /api/v1/agents/id/execute - Run agent with tools</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">POST /api/v1/workflows/id/execute - Run workflow DAG</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Benefits</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">Single API for any provider - switch via provider parameter</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Consistent error handling with automatic retry logic</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Streaming support for all providers</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Standardized usage metrics and cost tracking</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">OpenAPI/Swagger documentation at /api/docs</p>
      </div>
    </div>'''))

# Continue with more slides...
# 16 - Agent Section
slides.append((16, 'section', 'Agent Framework', 'Building intelligent AI agents'))

# 17 - What is Agent
slides.append((17, 'content', 'What is an AI Agent?', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 10px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Definition</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0; line-height: 1.4;">An AI Agent is an autonomous entity combining an LLM with tools, memory, and reasoning patterns to accomplish tasks. Unlike chatbots, agents plan, use tools, iterate until goals are achieved.</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Agent Components</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">Persona: System prompt defining role, expertise, constraints</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">LLM: The language model from any provider</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Tools: Functions the agent can call (DB, API, File, MCP)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Memory: Conversation history, working memory, long-term KB</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Reasoning: Pattern for thinking (ReAct, CoT, ToT, Reflexion)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">HITL: Human checkpoints for oversight</p>
      </div>
    </div>'''))

# 18 - Reasoning Patterns
slides.append((18, 'content', 'Agent Reasoning Patterns', '''    <div class="row gap-sm" style="height: 100%; flex-wrap: wrap; align-content: flex-start;">
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 8px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">ReAct (Reason + Act)</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Think then Act then Observe then Repeat</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">Best for: multi-step tasks with tools</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 8px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Chain-of-Thought (CoT)</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Step-by-step reasoning before answer</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">Best for: math, logic, analysis</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 8px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Tree-of-Thoughts (ToT)</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Explore multiple paths, backtrack</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">Best for: creative, open-ended</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px 8px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #ED1C24; margin: 0; font-weight: 600;">Reflexion</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Self-critique and improve iteratively</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">Best for: quality refinement</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px 8px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #ED1C24; margin: 0; font-weight: 600;">Hierarchical</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Manager delegates to worker agents</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">Best for: complex decomposition</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 8px; border-radius: 4px; width: 280px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Goal-Based</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Define goal, plan, execute, replan</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 1px 0 0 0;">Best for: autonomous objectives</p>
      </div>
    </div>'''))

# 19 - Tool Integration
slides.append((19, 'content', 'Agent Tool Integration', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Built-in Tool Types</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">Database: Query SQLite, PostgreSQL, MySQL</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">API: Call REST/GraphQL with auth headers</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">File: Read/write files, parse PDF, Excel, CSV</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Search: Web search, vector RAG retrieval</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Python: Execute Python in sandbox</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">MCP (Model Context Protocol) Integration</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">Connect external MCP servers as agent tools</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Pre-built: Filesystem, GitHub, Slack, Postgres, Puppeteer</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Auto-discovery of MCP tool schemas</p>
      </div>
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">UI Tool Management (Admin - Tools)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">Browse/enable tools per agent | Configure parameters | Test before save</p>
      </div>
    </div>'''))

# 20 - Agent Creation UI
slides.append((20, 'content', 'Creating Agents via UI', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Visual Agent Designer (Agents - New)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">1. Basic Info: Name, description, category, tags</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">2. Provider/Model: Select from dropdown (Ollama default)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">3. Persona: Rich text editor for system prompt</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">4. Tools: Drag-drop from tool library, configure params</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">5. Knowledge Base: Upload docs for RAG retrieval</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">6. Reasoning: Select pattern (ReAct, CoT, etc.)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">7. HITL: Configure approval checkpoints</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">8. Test: Interactive chat to validate before save</p>
      </div>
    </div>'''))

# 21 - Agent JSON
slides.append((21, 'content', 'Agent Definition: JSON Format', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #1A3A5C; padding: 8px; border-radius: 4px;">
        <p style="font-size: 7px; color: #7FDBFF; margin: 0; font-family: monospace; white-space: pre; line-height: 1.3;">{"name": "Research Assistant",
 "provider": "ollama", "model": "llama3.3:70b",
 "persona": "You are a research assistant...",
 "reasoning_pattern": "react",
 "tools": [
   {"type": "web_search", "config": {"max_results": 5}},
   {"type": "file_read"},
   {"type": "mcp", "server": "github"}
 ],
 "knowledge_base": {"vector_store": "chroma"},
 "hitl": {"approval_required": ["web_search"]},
 "max_iterations": 10, "temperature": 0.7}</p>
      </div>
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Python Usage</p>
        <p style="font-size: 7px; color: #1A3A5C; margin: 3px 0 0 0; font-family: monospace;">from abhikarta import Agent</p>
        <p style="font-size: 7px; color: #1A3A5C; margin: 1px 0 0 0; font-family: monospace;">agent = Agent.from_json("agent.json")</p>
        <p style="font-size: 7px; color: #1A3A5C; margin: 1px 0 0 0; font-family: monospace;">result = agent.run("Analyze Q3 earnings")</p>
      </div>
    </div>'''))

# 22 - Workflow Section
slides.append((22, 'section', 'Workflow DAG System', 'Visual pipeline orchestration'))

# 23 - Workflow Overview
slides.append((23, 'content', 'Workflow DAG Overview', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">What is a Workflow DAG?</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0; line-height: 1.4;">A Directed Acyclic Graph (DAG) represents multi-step AI pipelines where nodes are processing steps and edges define data flow. Workflows enable parallel execution, conditional logic, and human checkpoints.</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Key Capabilities</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">12+ Node Types: LLM, Agent, Tool, Python, Condition, Human...</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Parallel Execution: Nodes without dependencies run concurrently</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Conditional Branching: Route based on output values</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Error Handling: Retry, fallback, or fail-fast per node</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">HITL Nodes: Pause for human approval at any step</p>
      </div>
    </div>'''))

# 24 - Workflow Creation UI
slides.append((24, 'content', 'Creating Workflows via UI', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Visual Workflow Designer (Workflows - New)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">1. Canvas: Drag-drop nodes from palette onto canvas</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">2. Connect: Draw edges between node outputs and inputs</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">3. Configure: Click node to edit parameters in sidebar</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">4. Python Code: Add Python nodes with syntax highlighting</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">5. Variables: Define workflow inputs, pass between nodes</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">6. Validate: Check for cycles, missing connections</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">7. Test Run: Execute with sample inputs before deploy</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Python Integration</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">Inline Python with workflow context | Import existing files | pip install per workflow</p>
      </div>
    </div>'''))

# 25 - Workflow JSON
slides.append((25, 'content', 'Workflow Definition: JSON Format', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #1A3A5C; padding: 8px; border-radius: 4px;">
        <p style="font-size: 6px; color: #7FDBFF; margin: 0; font-family: monospace; white-space: pre; line-height: 1.2;">{"name": "Document Analysis Pipeline",
 "nodes": [
   {"id": "extract", "type": "tool", "tool": "file_read"},
   {"id": "summarize", "type": "llm", "provider": "ollama",
    "prompt": "Summarize: {{extract.output}}"},
   {"id": "approve", "type": "human", "message": "Review summary"},
   {"id": "notify", "type": "tool", "tool": "slack_send"}
 ],
 "edges": [
   {"from": "extract", "to": "summarize"},
   {"from": "summarize", "to": "approve"},
   {"from": "approve", "to": "notify"}
 ]}</p>
      </div>
      <div style="background: #FFF; padding: 6px; border-radius: 4px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Python Usage</p>
        <p style="font-size: 7px; color: #1A3A5C; margin: 2px 0 0 0; font-family: monospace;">result = Workflow.from_json("pipeline.json").run({"file": "report.pdf"})</p>
      </div>
    </div>'''))

# 26 - Swarm Section
slides.append((26, 'section', 'Agent Swarms', 'Dynamic multi-agent coordination'))

# 27 - What is Swarm
slides.append((27, 'content', 'What is an Agent Swarm?', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 10px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Definition</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0; line-height: 1.4;">An Agent Swarm is a collection of autonomous agents that collaborate dynamically. Unlike fixed workflows, swarms use event-driven coordination where agents respond to tasks based on capabilities.</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Key Characteristics</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">Event-Driven: Agents react to events, not predefined sequences</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Self-Organizing: Agents claim tasks based on capabilities</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Scalable: Add/remove agents without restructuring</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Fault Tolerant: Other agents compensate for failures</p>
      </div>
      <div style="background: #FFE8E8; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Messaging: Kafka, RabbitMQ, ActiveMQ, built-in pub/sub</p>
      </div>
    </div>'''))

# 28 - AI Org Section
slides.append((28, 'section', 'AI Organizations', 'Patent-pending hierarchical governance'))

# 29 - What is AI Org
slides.append((29, 'content', 'What is an AI Organization?', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 10px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Definition (Patent Pending)</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0; line-height: 1.4;">An AI Organization is a digital twin of a corporate hierarchy where each position is occupied by an AI agent. Tasks flow down (delegation) and responses flow up (aggregation), mirroring how real organizations work.</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Problems Solved</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">Accountability: Clear ownership for AI decisions</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Delegation: Complex tasks decomposed naturally</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Human Oversight: Every AI has a human mirror</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Compliance: Matches regulatory org structures</p>
      </div>
    </div>'''))

# 30 - AI Org JSON
slides.append((30, 'content', 'AI Organization: JSON Definition', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #1A3A5C; padding: 8px; border-radius: 4px;">
        <p style="font-size: 6px; color: #7FDBFF; margin: 0; font-family: monospace; white-space: pre; line-height: 1.2;">{"name": "Research Division",
 "positions": [
   {"id": "director", "title": "Research Director",
    "agent": "strategic_agent",
    "human_mirror": "john.smith@company.com",
    "autonomy": "supervised"},
   {"id": "lead1", "title": "Team Lead",
    "agent": "ai_specialist",
    "reports_to": "director",
    "autonomy": "semi_autonomous"},
   {"id": "analyst1", "title": "Analyst",
    "agent": "research_agent",
    "reports_to": "lead1"}
 ]}</p>
      </div>
      <div style="background: #FFF; padding: 6px; border-radius: 4px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Benefits: Mirrors real org | Clear accountability | Scalable AI teams | Human oversight built-in</p>
      </div>
    </div>'''))

# 31 - RBAC Section
slides.append((31, 'section', 'RBAC and Security', 'Enterprise-grade access control'))

# 32 - RBAC Details
slides.append((32, 'content', 'Role-Based Access Control', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">RBAC Model</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">Users: Individual accounts with authentication</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Roles: Admin, Developer, Analyst, Viewer (+ custom)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Permissions: Granular actions per resource type</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Model Access: Control which models each role can use</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Usage Limits: RPM/TPM quotas per role</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Security Features</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">API Keys: Scoped keys with expiration</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Audit Logs: Every action recorded with user/timestamp</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Rate Limiting: Prevent abuse and cost overruns</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Data Isolation: Multi-tenant data separation</p>
      </div>
    </div>'''))

# 33 - Notifications
slides.append((33, 'content', 'Notifications Integration', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Supported Channels</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">Slack: Bot integration with interactive buttons</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Microsoft Teams: Webhook and bot support</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Email: SMTP with templates</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Webhooks: POST to any endpoint</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">AI Org Integration</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">Human Mirror Alerts: Notify when AI needs approval</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Escalation: Auto-escalate if no response in timeout</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Interactive Buttons: Approve/Reject from notification</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">Summary Reports: Daily/weekly AI activity digests</p>
      </div>
    </div>'''))

# 34 - Use Cases Section
slides.append((34, 'section', 'Use Cases', 'Real-world applications with examples'))

# Use Case slides 35-39
use_cases = [
    (35, 'Use Case: Customer Service Bot', 'Support Bot', '70% auto-resolution | 24/7 availability | RAG over FAQ | CRM integration | HITL for complaints'),
    (36, 'Use Case: Document Analysis', 'Contract Review', '90% faster review | DAG pipeline | PDF parsing | Human approval gate'),
    (37, 'Use Case: Research and Reports', 'Research Team', 'Hours to minutes | AI Org with swarm | Web+DB search | Director aggregates'),
    (38, 'Use Case: Developer Productivity', 'Code Reviewer', 'Ollama for privacy | GitHub MCP | Auto docs and tests'),
    (39, 'Use Case: Risk and Compliance', 'Compliance Swarm', '24/7 monitoring | Transaction analysis | Pattern detection | Audit ready'),
]

for num, title, name, desc in use_cases:
    slides.append((num, 'content', title, f'''    <div class="row gap-sm" style="height: 100%;">
      <div class="col gap-sm" style="flex: 1;">
        <div style="background: #FFF; padding: 8px; border-radius: 4px;">
          <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Key Benefits</p>
          <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">{desc.replace(" | ", "</p><p style=\"font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;\">")}</p>
        </div>
      </div>
      <div style="flex: 1.2; background: #1A3A5C; padding: 8px; border-radius: 4px;">
        <p style="font-size: 7px; color: #7FDBFF; margin: 0; font-family: monospace; white-space: pre; line-height: 1.2;">{{"name": "{name}",
 "provider": "ollama",
 "tools": ["rag", "api"],
 "hitl": {{"enabled": true}}}}</p>
      </div>
    </div>'''))

# 40 - Competitive Section
slides.append((40, 'section', 'Competitive Analysis', 'Market positioning'))

# 41 - Competitive Comparison
slides.append((41, 'content', 'Competitive Comparison', '''    <div class="col gap-sm" style="height: 100%;">
      <div class="row gap-sm" style="align-items: center;">
        <div style="background: #FFF; padding: 4px 6px; border-radius: 4px; width: 130px;"><p style="font-size: 8px; color: #0079C1; margin: 0; font-weight: 600;">Feature</p></div>
        <div style="background: #ED1C24; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 8px; color: #FFF; margin: 0; font-weight: 600;">Abhikarta</p></div>
        <div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 8px; color: #1A3A5C; margin: 0;">LangChain</p></div>
        <div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 8px; color: #1A3A5C; margin: 0;">AutoGen</p></div>
        <div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 8px; color: #1A3A5C; margin: 0;">CrewAI</p></div>
      </div>
      <div class="row gap-sm"><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; width: 130px;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Multi-Provider</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #0079C1; margin: 0; font-weight: 600;">11+ Native</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Via Plugins</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Limited</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Limited</p></div></div>
      <div class="row gap-sm"><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; width: 130px;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Visual Workflow</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #0079C1; margin: 0; font-weight: 600;">Built-in DAG</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">LangGraph</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #ED1C24; margin: 0;">None</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #ED1C24; margin: 0;">None</p></div></div>
      <div class="row gap-sm"><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; width: 130px;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">AI Org Hierarchy</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #0079C1; margin: 0; font-weight: 600;">Patent Pending</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #ED1C24; margin: 0;">None</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Basic</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Basic</p></div></div>
      <div class="row gap-sm"><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; width: 130px;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Enterprise RBAC</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #0079C1; margin: 0; font-weight: 600;">Full + Model</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #ED1C24; margin: 0;">None</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #ED1C24; margin: 0;">None</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #ED1C24; margin: 0;">None</p></div></div>
      <div class="row gap-sm"><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; width: 130px;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">HITL Controls</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #0079C1; margin: 0; font-weight: 600;">Comprehensive</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Interrupt</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Basic</p></div><div style="background: #FFF; padding: 4px 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 7px; color: #5A7A9C; margin: 0;">Basic</p></div></div>
    </div>'''))

# 42 - Appendix Section
slides.append((42, 'section', 'Appendix', 'Acknowledgements and licensing'))

# 43 - Open Source
slides.append((43, 'content', 'Open Source Acknowledgements', '''    <div class="row gap-sm" style="height: 100%; flex-wrap: wrap; align-content: flex-start;">
      <div style="background: #FFF; padding: 6px; border-radius: 4px; width: 420px; border-left: 3px solid #0079C1;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">LLM and AI</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">LangChain, LlamaIndex, Ollama, OpenAI SDK, Anthropic SDK, Sentence Transformers, ChromaDB, FAISS, Transformers</p>
      </div>
      <div style="background: #FFF; padding: 6px; border-radius: 4px; width: 420px; border-left: 3px solid #0079C1;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Web Framework</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Flask, SQLAlchemy, Pydantic, Bootstrap 5, Jinja2, Gunicorn</p>
      </div>
      <div style="background: #FFF; padding: 6px; border-radius: 4px; width: 420px; border-left: 3px solid #0079C1;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Infrastructure</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Docker, PostgreSQL, Redis, Kafka, RabbitMQ</p>
      </div>
      <div style="background: #FFF; padding: 6px; border-radius: 4px; width: 420px; border-left: 3px solid #0079C1;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Utilities</p>
        <p style="font-size: 7px; color: #5A7A9C; margin: 2px 0 0 0;">Click, Rich, PyYAML, Requests, aiohttp, NumPy, Pandas, PyPDF</p>
      </div>
    </div>'''))

# 44 - Licensing
slides.append((44, 'content', 'Licensing and Intellectual Property', '''    <div class="col gap-sm" style="height: 100%;">
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
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Copyright 2025-2030 Ashutosh Sinha. All Rights Reserved.</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Contact: ajsinha@gmail.com</p>
      </div>
    </div>'''))

# 45 - Thank You
slides.append((45, 'thankyou', None, None))

# Write all slides
for item in slides:
    num = item[0]
    stype = item[1]
    filename = f"slide{num:02d}.html"
    
    if stype == 'title':
        html = title_slide()
    elif stype == 'section':
        html = section_slide(num, item[2], item[3])
    elif stype == 'thankyou':
        html = thank_you_slide(num)
    else:
        html = content_slide(num, item[2], item[3])
    
    with open(filename, 'w') as f:
        f.write(html)

print(f"Created {len(slides)} slides")
