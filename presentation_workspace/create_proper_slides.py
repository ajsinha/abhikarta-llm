import os

def title_slide():
    return '''<!DOCTYPE html>
<html>
<head></head>
<body class="col center" style="width: 960px; height: 540px; background: #F4F9FD; padding: 50px; box-sizing: border-box;">
  <h1 style="font-size: 42px; color: #0079C1; margin: 0; font-weight: 700;">Abhikarta-LLM</h1>
  <p style="font-size: 16px; color: #1A3A5C; margin: 8px 0 0 0;">Enterprise AI Orchestration Platform v1.4.7</p>
  <div class="row gap" style="margin-top: 24px;">
    <div style="background: #E8F4FC; padding: 12px 20px; border-radius: 6px; text-align: center;">
      <p style="font-size: 20px; color: #0079C1; margin: 0; font-weight: 600;">11+</p>
      <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Providers</p>
    </div>
    <div style="background: #E8F4FC; padding: 12px 20px; border-radius: 6px; text-align: center;">
      <p style="font-size: 20px; color: #1A3A5C; margin: 0; font-weight: 600;">100+</p>
      <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Models</p>
    </div>
    <div style="background: #E8F4FC; padding: 12px 20px; border-radius: 6px; text-align: center;">
      <p style="font-size: 20px; color: #ED1C24; margin: 0; font-weight: 600;">$0</p>
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
  <p style="font-size: 12px; color: #FFFFFF; margin: 0; opacity: 0.7;">Section</p>
  <h1 style="font-size: 30px; color: #FFFFFF; margin: 10px 0 0 0; font-weight: 700;">{title}</h1>
  <p style="font-size: 12px; color: #FFFFFF; margin: 8px 0 0 0; opacity: 0.8;">{subtitle}</p>
  <p style="font-size: 8px; color: #FFFFFF; margin: 30px 0 0 0; opacity: 0.6;">Copyright 2025-2030 Ashutosh Sinha | Patent Pending | Slide {num}</p>
</body>
</html>'''

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

def thank_you_slide(num):
    return f'''<!DOCTYPE html>
<html>
<head></head>
<body class="col center" style="width: 960px; height: 540px; background: #F4F9FD; padding: 50px; box-sizing: border-box;">
  <h1 style="font-size: 40px; color: #0079C1; margin: 0; font-weight: 700;">Thank You</h1>
  <p style="font-size: 16px; color: #1A3A5C; margin: 10px 0 0 0;">Abhikarta-LLM v1.4.7</p>
  <p style="font-size: 11px; color: #5A7A9C; margin: 6px 0 0 0;">Enterprise AI Orchestration Platform</p>
  <p style="font-size: 8px; color: #5A7A9C; margin: 24px 0 0 0;">Copyright 2025-2030 Ashutosh Sinha | All Rights Reserved | Patent Pending | Slide {num}</p>
</body>
</html>'''

slides = []

# 1 - Title
slides.append((1, 'title', None, None))

# 2 - TOC
slides.append((2, 'content', 'Table of Contents', '''    <div class="row gap" style="height: 100%;">
      <div class="col gap-sm" style="flex: 1;">
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">1. Executive Summary</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">2. Market Challenges</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">3. Platform Architecture</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">4. Multi-Provider Support</p></div>
        <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">5. Agent Framework</p></div>
        <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">6. Workflow DAG System</p></div>
      </div>
      <div class="col gap-sm" style="flex: 1;">
        <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">7. Agent Swarms</p></div>
        <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">8. AI Organizations</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">9. RBAC and Security</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">10. Notifications</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">11. Use Cases</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">12. Appendix</p></div>
      </div>
    </div>'''))

# 3 - Executive Summary
slides.append((3, 'content', 'Executive Summary', '''    <div class="row gap" style="height: 100%;">
      <div class="col gap-sm" style="flex: 1.2;">
        <div style="background: #FFF; padding: 10px; border-radius: 6px;">
          <p style="font-size: 10px; color: #1A3A5C; margin: 0; line-height: 1.4;">Abhikarta-LLM is an enterprise platform for AI agent design and orchestration with multi-provider LLM support, visual workflow builders, and comprehensive governance.</p>
        </div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px;">
          <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Key Capabilities</p>
          <ul style="font-size: 8px; color: #5A7A9C; margin: 4px 0 0 0; padding-left: 16px; line-height: 1.4;">
            <li>11+ LLM providers with unified API abstraction</li>
            <li>Visual Agent and Workflow designers</li>
            <li>AI Organizations with human-in-the-loop controls</li>
            <li>Enterprise RBAC with model-level permissions</li>
          </ul>
        </div>
      </div>
      <div class="col gap-sm" style="flex: 0.8;">
        <div style="background: #FFF; padding: 10px; border-radius: 6px; text-align: center;">
          <p style="font-size: 22px; color: #0079C1; margin: 0; font-weight: 700;">11+</p>
          <p style="font-size: 8px; color: #5A7A9C; margin: 2px 0 0 0;">Providers</p>
        </div>
        <div style="background: #FFF; padding: 10px; border-radius: 6px; text-align: center;">
          <p style="font-size: 22px; color: #1A3A5C; margin: 0; font-weight: 700;">100+</p>
          <p style="font-size: 8px; color: #5A7A9C; margin: 2px 0 0 0;">Models</p>
        </div>
        <div style="background: #FFF; padding: 10px; border-radius: 6px; text-align: center;">
          <p style="font-size: 22px; color: #ED1C24; margin: 0; font-weight: 700;">$0</p>
          <p style="font-size: 8px; color: #5A7A9C; margin: 2px 0 0 0;">Local Cost</p>
        </div>
      </div>
    </div>'''))

# 4 - Market Challenges Section
slides.append((4, 'section', 'Market Challenges', 'Problems solved by Abhikarta-LLM'))

# 5 - Provider Lock-In (vertical Problem/Solution)
slides.append((5, 'content', 'Challenge: Provider Lock-In', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 10px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">The Problem</p>
        <ul style="font-size: 8px; color: #5A7A9C; margin: 4px 0 0 0; padding-left: 16px; line-height: 1.4;">
          <li>Organizations commit to single LLM provider with provider-specific code</li>
          <li>High switching costs when better alternatives emerge</li>
          <li>Pricing changes impact budgets with no alternatives</li>
          <li>Service disruptions halt production workloads</li>
          <li>Cannot leverage new models from competing providers</li>
        </ul>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 10px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Our Solution</p>
        <ul style="font-size: 8px; color: #5A7A9C; margin: 4px 0 0 0; padding-left: 16px; line-height: 1.4;">
          <li>Unified abstraction layer across 11+ providers (Ollama, OpenAI, Anthropic, Google...)</li>
          <li>Same code works with any provider - switch via configuration</li>
          <li>Automatic failover between providers on errors</li>
          <li>Best-of-breed model selection per use case</li>
          <li>Negotiate better rates with competitive leverage</li>
        </ul>
      </div>
    </div>'''))

# 6 - AI Governance Gaps
slides.append((6, 'content', 'Challenge: AI Governance Gaps', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 10px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">The Problem</p>
        <ul style="font-size: 8px; color: #5A7A9C; margin: 4px 0 0 0; padding-left: 16px; line-height: 1.4;">
          <li>Shadow AI proliferates - employees use ChatGPT without IT oversight</li>
          <li>Sensitive corporate data leaked to external AI services</li>
          <li>No audit trail for AI-generated content or decisions</li>
          <li>Regulatory compliance gaps (GDPR, HIPAA, SOX, EU AI Act)</li>
          <li>No visibility into AI usage patterns, costs, or risks</li>
        </ul>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 10px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Our Solution</p>
        <ul style="font-size: 8px; color: #5A7A9C; margin: 4px 0 0 0; padding-left: 16px; line-height: 1.4;">
          <li>Centralized platform with RBAC at model and feature level</li>
          <li>Complete audit logging of all LLM interactions</li>
          <li>Rate limiting per user, team, and organization unit</li>
          <li>Local Ollama models for sensitive workloads - data never leaves</li>
          <li>Usage analytics dashboard with cost allocation</li>
        </ul>
      </div>
    </div>'''))

# 7 - Complex Orchestration
slides.append((7, 'content', 'Challenge: Complex Orchestration', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 10px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">The Problem</p>
        <ul style="font-size: 8px; color: #5A7A9C; margin: 4px 0 0 0; padding-left: 16px; line-height: 1.4;">
          <li>Multi-step AI pipelines require significant engineering effort</li>
          <li>Error handling across chained LLM calls is complex</li>
          <li>Parallel execution optimization requires deep expertise</li>
          <li>Debugging failed multi-agent workflows is time-consuming</li>
          <li>Business users cannot build or modify AI workflows</li>
        </ul>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 10px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Our Solution</p>
        <ul style="font-size: 8px; color: #5A7A9C; margin: 4px 0 0 0; padding-left: 16px; line-height: 1.4;">
          <li>Visual DAG workflow designer with drag-and-drop interface</li>
          <li>12+ node types: LLM, Agent, Tool, Python, Condition, Human...</li>
          <li>Automatic parallel execution with dependency management</li>
          <li>Built-in retry logic, error handling, and fallback paths</li>
          <li>Step-by-step execution viewer with detailed logs</li>
        </ul>
      </div>
    </div>'''))

# Write slides 1-7
for item in slides:
    num = item[0]
    stype = item[1]
    filename = f"slide{num:02d}.html"
    
    if stype == 'title':
        html = title_slide()
    elif stype == 'section':
        html = section_slide(num, item[2], item[3])
    else:
        html = content_slide(num, item[2], item[3])
    
    with open(filename, 'w') as f:
        f.write(html)

print("Created slides 1-7")
