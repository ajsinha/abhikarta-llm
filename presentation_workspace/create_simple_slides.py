import os

# Simple slide templates that keep everything within body boundaries
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
  <p style="font-size: 8px; color: #5A7A9C; margin: 30px 0 0 0;">Copyright © 2025-2030 Ashutosh Sinha | All Rights Reserved | Patent Pending</p>
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

def content_slide(num, title, content):
    return f'''<!DOCTYPE html>
<html>
<head></head>
<body class="col" style="width: 960px; height: 540px; background: #F4F9FD; padding: 20px 30px; box-sizing: border-box;">
  <div class="row" style="justify-content: space-between; align-items: center; margin-bottom: 12px;">
    <p style="font-size: 16px; color: #0079C1; margin: 0; font-weight: 600;">{title}</p>
    <p style="font-size: 9px; color: #5A7A9C; margin: 0;">Abhikarta-LLM v1.4.6</p>
  </div>
  <div style="background: #0079C1; height: 3px; margin-bottom: 12px; border-radius: 2px;"></div>
  <div class="fill-height" style="overflow: hidden;">
{content}
  </div>
  <div class="row" style="justify-content: space-between; align-items: center; margin-top: 10px;">
    <p style="font-size: 8px; color: #5A7A9C; margin: 0;">Copyright © 2025-2030 Ashutosh Sinha | Patent Pending</p>
    <p style="font-size: 8px; color: #5A7A9C; margin: 0;">{num}</p>
  </div>
</body>
</html>'''

def thank_you_slide(num):
    return f'''<!DOCTYPE html>
<html>
<head></head>
<body class="col center" style="width: 960px; height: 540px; background: #F4F9FD; padding: 40px; box-sizing: border-box;">
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
  <p style="font-size: 8px; color: #5A7A9C; margin: 24px 0 0 0;">Copyright © 2025-2030 Ashutosh Sinha | All Rights Reserved | Patent Pending | Slide {num}</p>
</body>
</html>'''

# Define all slides
all_slides = []

# 1 - Title
all_slides.append((1, 'title', None, None))

# 2 - TOC
all_slides.append((2, 'content', 'Table of Contents', '''    <div class="row gap" style="height: 100%;">
      <div class="col gap-sm" style="flex: 1;">
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px 12px; border-radius: 4px;"><p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">1. Executive Summary</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px 12px; border-radius: 4px;"><p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">2. Market Challenges</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px 12px; border-radius: 4px;"><p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">3. Platform Architecture</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px 12px; border-radius: 4px;"><p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">4. Multi-Provider Support</p></div>
        <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px 12px; border-radius: 4px;"><p style="font-size: 11px; color: #ED1C24; margin: 0; font-weight: 600;">5. Agent Framework</p></div>
      </div>
      <div class="col gap-sm" style="flex: 1;">
        <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px 12px; border-radius: 4px;"><p style="font-size: 11px; color: #ED1C24; margin: 0; font-weight: 600;">6. Workflow DAG System</p></div>
        <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px 12px; border-radius: 4px;"><p style="font-size: 11px; color: #ED1C24; margin: 0; font-weight: 600;">7. AI Organizations</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px 12px; border-radius: 4px;"><p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">8. Security & Governance</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px 12px; border-radius: 4px;"><p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">9. Use Cases</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px 12px; border-radius: 4px;"><p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">10. Appendix</p></div>
      </div>
    </div>'''))

# 3 - Executive Summary
all_slides.append((3, 'content', 'Executive Summary', '''    <div class="row gap" style="height: 100%;">
      <div class="col gap-sm" style="flex: 1.2;">
        <div style="background: #FFF; padding: 12px; border-radius: 6px;">
          <p style="font-size: 11px; color: #1A3A5C; margin: 0; line-height: 1.5;">Abhikarta-LLM is an enterprise platform for AI agents and workflows with multi-provider LLM support and governance.</p>
        </div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 10px; border-radius: 4px;">
          <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Vision</p>
          <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Democratize enterprise AI with security.</p>
        </div>
        <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 10px; border-radius: 4px;">
          <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Mission</p>
          <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Enable AI without vendor lock-in.</p>
        </div>
      </div>
      <div class="col gap-sm" style="flex: 0.8;">
        <div style="background: #FFF; padding: 10px; border-radius: 6px; text-align: center;">
          <p style="font-size: 24px; color: #0079C1; margin: 0; font-weight: 700;">11+</p>
          <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Providers</p>
        </div>
        <div style="background: #FFF; padding: 10px; border-radius: 6px; text-align: center;">
          <p style="font-size: 24px; color: #1A3A5C; margin: 0; font-weight: 700;">100+</p>
          <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Models</p>
        </div>
        <div style="background: #FFF; padding: 10px; border-radius: 6px; text-align: center;">
          <p style="font-size: 24px; color: #ED1C24; margin: 0; font-weight: 700;">$0</p>
          <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Local Cost</p>
        </div>
      </div>
    </div>'''))

# 4 - Value Props
all_slides.append((4, 'content', 'Key Value Propositions', '''    <div class="row gap" style="height: 100%; flex-wrap: wrap; align-content: flex-start;">
      <div style="background: #FFF; padding: 12px; border-radius: 6px; border-top: 3px solid #0079C1; width: 270px;">
        <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Provider Agnostic</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Switch providers without code changes.</p>
      </div>
      <div style="background: #FFF; padding: 12px; border-radius: 6px; border-top: 3px solid #0079C1; width: 270px;">
        <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Cost Optimization</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Free local models for development.</p>
      </div>
      <div style="background: #FFF; padding: 12px; border-radius: 6px; border-top: 3px solid #ED1C24; width: 270px;">
        <p style="font-size: 11px; color: #ED1C24; margin: 0; font-weight: 600;">Data Privacy</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Local models keep data secure.</p>
      </div>
      <div style="background: #FFF; padding: 12px; border-radius: 6px; border-top: 3px solid #0079C1; width: 270px;">
        <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Visual Orchestration</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">DAG workflows for AI pipelines.</p>
      </div>
      <div style="background: #FFF; padding: 12px; border-radius: 6px; border-top: 3px solid #ED1C24; width: 270px;">
        <p style="font-size: 11px; color: #ED1C24; margin: 0; font-weight: 600;">Enterprise Governance</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">RBAC, audit trails, compliance.</p>
      </div>
      <div style="background: #FFF; padding: 12px; border-radius: 6px; border-top: 3px solid #0079C1; width: 270px;">
        <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Human-in-the-Loop</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Human oversight for AI decisions.</p>
      </div>
    </div>'''))

# Sections
sections = [
    (5, 'Market Challenges', 'Problems solved by Abhikarta-LLM'),
    (10, 'Platform Architecture', 'System design and components'),
    (13, 'Multi-Provider LLM Support', 'Unified access to 11+ providers'),
    (18, 'Agent Framework', 'Building intelligent AI agents'),
    (23, 'Workflow DAG System', 'Visual pipeline orchestration'),
    (26, 'AI Organizations', 'Patent-pending hierarchical governance'),
    (29, 'Security & Governance', 'Enterprise-grade controls'),
    (31, 'Use Cases', 'Real-world applications'),
    (37, 'Technology Stack', 'Modern enterprise architecture'),
    (42, 'Competitive Analysis', 'Market positioning'),
    (44, 'Open Source Acknowledgements', 'Standing on giants'),
]

for num, title, sub in sections:
    all_slides.append((num, 'section', title, sub))

# Content slides
content_slides_data = [
    (6, 'Challenge: Provider Lock-In', '''    <div class="row gap" style="height: 100%;">
      <div class="col gap-sm" style="flex: 1;">
        <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 12px; border-radius: 4px;">
          <p style="font-size: 11px; color: #ED1C24; margin: 0; font-weight: 600;">The Problem</p>
          <p style="font-size: 9px; color: #5A7A9C; margin: 6px 0 0 0;">Organizations face pricing changes, service disruptions, inability to use competitors.</p>
        </div>
      </div>
      <div class="col gap-sm" style="flex: 1;">
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 12px; border-radius: 4px;">
          <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Our Solution</p>
          <p style="font-size: 9px; color: #5A7A9C; margin: 6px 0 0 0;">Unified abstraction across 11+ providers. Same code, different models.</p>
        </div>
      </div>
    </div>'''),
    (7, 'Challenge: AI Governance Gaps', '''    <div class="row gap" style="height: 100%;">
      <div class="col gap-sm" style="flex: 1;">
        <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 12px; border-radius: 4px;">
          <p style="font-size: 11px; color: #ED1C24; margin: 0; font-weight: 600;">The Problem</p>
          <p style="font-size: 9px; color: #5A7A9C; margin: 6px 0 0 0;">Shadow AI creates compliance and data leakage risks.</p>
        </div>
      </div>
      <div class="col gap-sm" style="flex: 1;">
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 12px; border-radius: 4px;">
          <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Our Solution</p>
          <p style="font-size: 9px; color: #5A7A9C; margin: 6px 0 0 0;">Centralized platform with RBAC, audit logging, rate limiting.</p>
        </div>
      </div>
    </div>'''),
    (8, 'Challenge: Complex Orchestration', '''    <div class="row gap" style="height: 100%;">
      <div class="col gap-sm" style="flex: 1;">
        <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 12px; border-radius: 4px;">
          <p style="font-size: 11px; color: #ED1C24; margin: 0; font-weight: 600;">The Problem</p>
          <p style="font-size: 9px; color: #5A7A9C; margin: 6px 0 0 0;">Multi-step AI pipelines require significant engineering effort.</p>
        </div>
      </div>
      <div class="col gap-sm" style="flex: 1;">
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 12px; border-radius: 4px;">
          <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Our Solution</p>
          <p style="font-size: 9px; color: #5A7A9C; margin: 6px 0 0 0;">Visual DAG workflow designer with built-in error handling.</p>
        </div>
      </div>
    </div>'''),
    (9, 'Challenge: AI Cost Management', '''    <div class="row gap" style="height: 100%;">
      <div class="col gap-sm" style="flex: 1;">
        <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 12px; border-radius: 4px;">
          <p style="font-size: 11px; color: #ED1C24; margin: 0; font-weight: 600;">The Problem</p>
          <p style="font-size: 9px; color: #5A7A9C; margin: 6px 0 0 0;">LLM costs spiral at scale without controls.</p>
        </div>
      </div>
      <div class="col gap-sm" style="flex: 1;">
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 12px; border-radius: 4px;">
          <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Our Solution</p>
          <p style="font-size: 9px; color: #5A7A9C; margin: 6px 0 0 0;">Rate limiting, token quotas. Local Ollama at $0 cost.</p>
        </div>
      </div>
    </div>'''),
    (11, 'Architecture Overview', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px; text-align: center;">
        <p style="font-size: 10px; color: #5A7A9C; margin: 0;">USER INTERFACES: Web UI | REST API | Admin Console | CLI</p>
      </div>
      <div style="background: #FFF; border: 2px solid #0079C1; padding: 10px; border-radius: 6px;">
        <p style="font-size: 11px; color: #0079C1; margin: 0 0 6px 0; font-weight: 600; text-align: center;">ABHIKARTA-LLM CORE</p>
        <div class="row gap-sm">
          <div style="background: #E8F4FC; padding: 8px; border-radius: 4px; flex: 1; text-align: center;">
            <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Agent Framework</p>
          </div>
          <div style="background: #E8F4FC; padding: 8px; border-radius: 4px; flex: 1; text-align: center;">
            <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Workflow Engine</p>
          </div>
          <div style="background: #E8F4FC; padding: 8px; border-radius: 4px; flex: 1; text-align: center;">
            <p style="font-size: 9px; color: #ED1C24; margin: 0; font-weight: 600;">AI Org Manager</p>
          </div>
          <div style="background: #E8F4FC; padding: 8px; border-radius: 4px; flex: 1; text-align: center;">
            <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Security Layer</p>
          </div>
        </div>
      </div>
      <div style="background: #FFF; padding: 8px; border-radius: 4px; text-align: center;">
        <p style="font-size: 10px; color: #5A7A9C; margin: 0;">PROVIDERS: Ollama | OpenAI | Anthropic | Google | Azure | AWS | Groq | Mistral</p>
      </div>
    </div>'''),
    (12, 'Core Components', '''    <div class="row gap" style="height: 100%; flex-wrap: wrap; align-content: flex-start;">
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 10px; border-radius: 4px; width: 400px;">
        <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Agent Framework</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Modular AI agents with personas, tools, memory.</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 10px; border-radius: 4px; width: 400px;">
        <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Workflow Engine</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">DAG orchestration with parallel execution.</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 10px; border-radius: 4px; width: 400px;">
        <p style="font-size: 11px; color: #ED1C24; margin: 0; font-weight: 600;">AI Organization Manager</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Patent-pending hierarchical governance.</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 10px; border-radius: 4px; width: 400px;">
        <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Security Layer</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">RBAC, API keys, rate limiting, audit logs.</p>
      </div>
    </div>'''),
    (14, 'Supported LLM Providers', '''    <div class="col gap-sm" style="height: 100%;">
      <div class="row gap-sm">
        <div style="background: #ED1C24; padding: 10px; border-radius: 6px; flex: 1; text-align: center;">
          <p style="font-size: 12px; color: #FFF; margin: 0; font-weight: 600;">Ollama (Default)</p>
        </div>
        <div style="background: #FFF; padding: 10px; border-radius: 6px; flex: 1; text-align: center;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">OpenAI</p>
        </div>
        <div style="background: #FFF; padding: 10px; border-radius: 6px; flex: 1; text-align: center;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Anthropic</p>
        </div>
        <div style="background: #FFF; padding: 10px; border-radius: 6px; flex: 1; text-align: center;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Google</p>
        </div>
      </div>
      <div class="row gap-sm">
        <div style="background: #FFF; padding: 10px; border-radius: 6px; flex: 1; text-align: center;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Azure OpenAI</p>
        </div>
        <div style="background: #FFF; padding: 10px; border-radius: 6px; flex: 1; text-align: center;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">AWS Bedrock</p>
        </div>
        <div style="background: #FFF; padding: 10px; border-radius: 6px; flex: 1; text-align: center;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Groq</p>
        </div>
        <div style="background: #FFF; padding: 10px; border-radius: 6px; flex: 1; text-align: center;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Mistral AI</p>
        </div>
      </div>
    </div>'''),
    (43, 'Competitive Comparison', '''    <div class="col gap-sm" style="height: 100%;">
      <div class="row gap-sm">
        <div style="background: #FFF; padding: 6px; border-radius: 4px; width: 180px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Feature</p></div>
        <div style="background: #ED1C24; padding: 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 10px; color: #FFF; margin: 0; font-weight: 600;">Abhikarta</p></div>
        <div style="background: #FFF; padding: 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 10px; color: #1A3A5C; margin: 0;">LangChain</p></div>
        <div style="background: #FFF; padding: 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 10px; color: #1A3A5C; margin: 0;">AutoGen</p></div>
        <div style="background: #FFF; padding: 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 10px; color: #1A3A5C; margin: 0;">CrewAI</p></div>
      </div>
      <div class="row gap-sm">
        <div style="background: #FFF; padding: 6px; border-radius: 4px; width: 180px;"><p style="font-size: 9px; color: #5A7A9C; margin: 0;">Multi-Provider</p></div>
        <div style="background: #FFF; padding: 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 9px; color: #0079C1; margin: 0;">11+ Native</p></div>
        <div style="background: #FFF; padding: 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 9px; color: #5A7A9C; margin: 0;">Via Plugins</p></div>
        <div style="background: #FFF; padding: 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 9px; color: #5A7A9C; margin: 0;">Limited</p></div>
        <div style="background: #FFF; padding: 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 9px; color: #5A7A9C; margin: 0;">Limited</p></div>
      </div>
      <div class="row gap-sm">
        <div style="background: #FFF; padding: 6px; border-radius: 4px; width: 180px;"><p style="font-size: 9px; color: #5A7A9C; margin: 0;">Visual Workflow</p></div>
        <div style="background: #FFF; padding: 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 9px; color: #0079C1; margin: 0;">Built-in DAG</p></div>
        <div style="background: #FFF; padding: 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 9px; color: #5A7A9C; margin: 0;">LangGraph</p></div>
        <div style="background: #FFF; padding: 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 9px; color: #ED1C24; margin: 0;">Code Only</p></div>
        <div style="background: #FFF; padding: 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 9px; color: #ED1C24; margin: 0;">Code Only</p></div>
      </div>
      <div class="row gap-sm">
        <div style="background: #FFF; padding: 6px; border-radius: 4px; width: 180px;"><p style="font-size: 9px; color: #5A7A9C; margin: 0;">AI Org Hierarchy</p></div>
        <div style="background: #FFF; padding: 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 9px; color: #0079C1; margin: 0;">Full Support</p></div>
        <div style="background: #FFF; padding: 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 9px; color: #ED1C24; margin: 0;">None</p></div>
        <div style="background: #FFF; padding: 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 9px; color: #5A7A9C; margin: 0;">Basic</p></div>
        <div style="background: #FFF; padding: 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 9px; color: #5A7A9C; margin: 0;">Basic</p></div>
      </div>
      <div class="row gap-sm">
        <div style="background: #FFF; padding: 6px; border-radius: 4px; width: 180px;"><p style="font-size: 9px; color: #5A7A9C; margin: 0;">Enterprise RBAC</p></div>
        <div style="background: #FFF; padding: 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 9px; color: #0079C1; margin: 0;">Full RBAC</p></div>
        <div style="background: #FFF; padding: 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 9px; color: #ED1C24; margin: 0;">None</p></div>
        <div style="background: #FFF; padding: 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 9px; color: #ED1C24; margin: 0;">None</p></div>
        <div style="background: #FFF; padding: 6px; border-radius: 4px; flex: 1; text-align: center;"><p style="font-size: 9px; color: #ED1C24; margin: 0;">None</p></div>
      </div>
    </div>'''),
]

for num, title, content in content_slides_data:
    all_slides.append((num, 'content', title, content))

# Simple content slides
simple_slides = [
    (15, 'Ollama: Default Provider', 'Why Ollama is default: Free, local, private. 40+ models including Llama 3.3, Qwen 2.5, DeepSeek.'),
    (16, 'Provider Selection Strategy', 'Choose providers based on: Cost, Privacy, Performance, Compliance, or Specialized capabilities.'),
    (17, 'Unified API Benefits', 'No code changes to switch. Consistent error handling. Automatic failover. Standardized metrics.'),
    (19, 'Agent Architecture', 'Agents combine: Persona, Tools, Memory, Knowledge. Support all providers uniformly.'),
    (20, 'Agent Reasoning Patterns', 'ReAct, Chain-of-Thought, Tree-of-Thoughts, Reflexion, Hierarchical, Goal-Based patterns.'),
    (21, 'Agent Tool Integration', 'Database, API, File, Search, Custom tools. Human-in-loop for approvals.'),
    (22, 'Knowledge & RAG Pipeline', 'Ingest → Chunk → Embed → Retrieve. Supports Chroma, Pinecone, FAISS vector stores.'),
    (24, 'DAG Workflow Overview', 'Directed Acyclic Graph for complex pipelines. Parallel execution, conditional branching, error handling.'),
    (25, 'Workflow Node Types', 'LLM, Agent, Tool, Transform, Human, Condition nodes. Build any workflow visually.'),
    (27, 'AI Organization Overview', 'Digital twins of org structure. Tasks delegate down, responses aggregate up. Human mirrors.'),
    (28, 'Human-in-the-Loop Controls', 'Human mirrors, approval workflows, override capability, notifications via Slack/Email/Teams.'),
    (30, 'Security Framework', 'RBAC, audit logging, API key management, rate limiting, data isolation, compliance ready.'),
    (32, 'Use Case: Customer Service', 'AI chatbot with RAG. 70% auto-resolution, 24/7 availability, consistent quality.'),
    (33, 'Use Case: Document Analysis', 'DAG workflow for contracts/reports. 90% faster review, improved accuracy.'),
    (34, 'Use Case: Risk & Compliance', 'AI transaction monitoring, communication analysis. Comprehensive coverage, audit-ready.'),
    (35, 'Use Case: Research & Reports', 'Multi-step synthesis workflow. Hours to minutes, comprehensive coverage.'),
    (36, 'Use Case: Developer Productivity', 'AI code review, doc generation, test creation. Local models for code privacy.'),
    (38, 'Technology Stack Overview', 'Python 3.11+, Flask, SQLAlchemy, Bootstrap 5, SQLite/PostgreSQL, Docker, Kubernetes.'),
    (39, 'Deployment Options', 'Local dev, Docker Compose, Kubernetes, Air-gapped, Cloud (AWS/Azure/GCP), Hybrid.'),
    (40, 'Getting Started', 'pip install abhikarta-llm → abhikarta init → abhikarta web start. That simple.'),
    (41, 'Product Roadmap', 'Q1: Enhanced Workflow Designer. Q2: Multi-Tenant SaaS. Q3: Industry Verticals. Q4: Marketplace.'),
    (45, 'Open Source: LLM Frameworks', 'LangChain, LlamaIndex, Ollama, OpenAI SDK, Anthropic SDK, ChromaDB, FAISS, Transformers.'),
    (46, 'Open Source: Web & Infrastructure', 'Flask, SQLAlchemy, Pydantic, Bootstrap, Jinja2, Gunicorn, Docker, PostgreSQL, Redis.'),
    (48, 'Open Source: Utilities', 'Click, Rich, PyYAML, Requests, aiohttp, NumPy, Pandas, PyPDF, python-docx.'),
    (49, 'Licensing & Intellectual Property', 'Proprietary license. Copyright © 2025-2030 Ashutosh Sinha. Patent pending for AI Org technology.'),
    (50, 'Contact & Resources', 'Docs at /docs. Research paper in docs/research/. Enterprise support available.'),
    (51, 'Copyright Notice', 'Abhikarta-LLM v1.4.6. Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved. PATENT PENDING.'),
]

for num, title, desc in simple_slides:
    content = f'''    <div class="col center" style="height: 100%;">
      <div style="background: #FFF; padding: 16px 24px; border-radius: 6px; max-width: 680px; text-align: center;">
        <p style="font-size: 12px; color: #1A3A5C; margin: 0; line-height: 1.6;">{desc}</p>
      </div>
    </div>'''
    all_slides.append((num, 'content', title, content))

# Thank you slide
all_slides.append((47, 'thankyou', None, None))

# Write all slides
for item in all_slides:
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

print(f"Created {len(all_slides)} slides")
