import os

def title_slide():
    return '''<!DOCTYPE html>
<html>
<head></head>
<body class="col center" style="width: 960px; height: 540px; background: #F4F9FD; padding: 40px; box-sizing: border-box;">
  <h1 style="font-size: 44px; color: #0079C1; margin: 0; font-weight: 700;">Abhikarta-LLM</h1>
  <p style="font-size: 18px; color: #1A3A5C; margin: 10px 0 0 0;">Enterprise AI Orchestration Platform</p>
  <p style="font-size: 13px; color: #5A7A9C; margin: 6px 0 0 0;">Version 1.4.7</p>
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

# Define all slides with detailed content
all_slides = []

# 1 - Title
all_slides.append((1, 'title', None, None))

# 2 - TOC
all_slides.append((2, 'content', 'Table of Contents', '''    <div class="row gap" style="height: 100%;">
      <div class="col gap-sm" style="flex: 1;">
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">1. Executive Summary</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">2. Market Challenges</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">3. Platform Architecture</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">4. Multi-Provider LLM Support</p></div>
        <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">5. Agent Framework & Patterns</p></div>
        <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">6. Workflow DAG System</p></div>
      </div>
      <div class="col gap-sm" style="flex: 1;">
        <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">7. Agent Swarms</p></div>
        <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">8. AI Organizations</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">9. RBAC & Security</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">10. Notifications Integration</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">11. Use Cases with Examples</p></div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 6px 10px; border-radius: 4px;"><p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">12. Appendix & Acknowledgements</p></div>
      </div>
    </div>'''))

# 3 - Executive Summary
all_slides.append((3, 'content', 'Executive Summary', '''    <div class="row gap" style="height: 100%;">
      <div class="col gap-sm" style="flex: 1.2;">
        <div style="background: #FFF; padding: 10px; border-radius: 6px;">
          <p style="font-size: 10px; color: #1A3A5C; margin: 0; line-height: 1.4;">Abhikarta-LLM is an enterprise platform for AI agents and workflows with multi-provider LLM support and governance.</p>
        </div>
        <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px;">
          <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Key Capabilities</p>
          <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• 11+ LLM providers with unified API</p>
          <p style="font-size: 8px; color: #5A7A9C; margin: 2px 0 0 0;">• Visual Agent & Workflow designers</p>
          <p style="font-size: 8px; color: #5A7A9C; margin: 2px 0 0 0;">• AI Organizations with HITL controls</p>
          <p style="font-size: 8px; color: #5A7A9C; margin: 2px 0 0 0;">• Enterprise RBAC & audit trails</p>
        </div>
      </div>
      <div class="col gap-sm" style="flex: 0.8;">
        <div style="background: #FFF; padding: 8px; border-radius: 6px; text-align: center;">
          <p style="font-size: 20px; color: #0079C1; margin: 0; font-weight: 700;">11+</p>
          <p style="font-size: 8px; color: #5A7A9C; margin: 2px 0 0 0;">Providers</p>
        </div>
        <div style="background: #FFF; padding: 8px; border-radius: 6px; text-align: center;">
          <p style="font-size: 20px; color: #1A3A5C; margin: 0; font-weight: 700;">100+</p>
          <p style="font-size: 8px; color: #5A7A9C; margin: 2px 0 0 0;">Models</p>
        </div>
        <div style="background: #FFF; padding: 8px; border-radius: 6px; text-align: center;">
          <p style="font-size: 20px; color: #ED1C24; margin: 0; font-weight: 700;">$0</p>
          <p style="font-size: 8px; color: #5A7A9C; margin: 2px 0 0 0;">Local Cost</p>
        </div>
      </div>
    </div>'''))

# 4 - Value Props
all_slides.append((4, 'content', 'Key Value Propositions', '''    <div class="row gap-sm" style="height: 100%; flex-wrap: wrap; align-content: flex-start;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px; border-top: 2px solid #0079C1; width: 280px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Provider Agnostic</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• Switch providers via config, not code</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Unified API across all providers</p>
      </div>
      <div style="background: #FFF; padding: 8px; border-radius: 4px; border-top: 2px solid #0079C1; width: 280px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Cost Optimization</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• Ollama for $0 local inference</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Rate limiting & token quotas</p>
      </div>
      <div style="background: #FFF; padding: 8px; border-radius: 4px; border-top: 2px solid #ED1C24; width: 280px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Data Privacy</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• Local models: data stays on-prem</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Air-gapped deployment option</p>
      </div>
      <div style="background: #FFF; padding: 8px; border-radius: 4px; border-top: 2px solid #0079C1; width: 280px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Visual Orchestration</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• Drag-drop DAG workflow builder</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• No-code agent designer</p>
      </div>
      <div style="background: #FFF; padding: 8px; border-radius: 4px; border-top: 2px solid #ED1C24; width: 280px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Enterprise Governance</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• RBAC with model permissions</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Complete audit trails</p>
      </div>
      <div style="background: #FFF; padding: 8px; border-radius: 4px; border-top: 2px solid #0079C1; width: 280px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Human-in-the-Loop</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• Approval workflows at any step</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Override & escalation controls</p>
      </div>
    </div>'''))

# Market Challenges Section
all_slides.append((5, 'section', 'Market Challenges', 'Problems solved by Abhikarta-LLM'))

# 6 - Provider Lock-In (vertical layout)
all_slides.append((6, 'content', 'Challenge: Provider Lock-In', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 10px; border-radius: 4px;">
        <p style="font-size: 11px; color: #ED1C24; margin: 0; font-weight: 600;">The Problem</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">• Organizations commit to single LLM provider (OpenAI, Anthropic, etc.)</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Provider-specific code patterns create switching costs</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Pricing changes impact budgets with no alternatives</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Service disruptions halt production workloads</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Cannot leverage new models from other providers</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 10px; border-radius: 4px;">
        <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Our Solution</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">• Unified abstraction layer across 11+ providers</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Same code works with any provider - switch via config</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Automatic failover between providers on errors</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Best-of-breed model selection per use case</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Competitive pricing leverage across vendors</p>
      </div>
    </div>'''))

# 7 - AI Governance Gaps
all_slides.append((7, 'content', 'Challenge: AI Governance Gaps', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 10px; border-radius: 4px;">
        <p style="font-size: 11px; color: #ED1C24; margin: 0; font-weight: 600;">The Problem</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">• Shadow AI proliferates - employees use ChatGPT without oversight</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Sensitive data leaked to external AI services</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• No audit trail for AI-generated content</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Regulatory compliance gaps (GDPR, HIPAA, SOX)</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• No visibility into AI usage patterns or costs</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 10px; border-radius: 4px;">
        <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Our Solution</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">• Centralized platform with RBAC at model level</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Complete audit logging of all LLM interactions</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Rate limiting per user, team, organization</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Local Ollama models for sensitive workloads</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Usage analytics dashboard with cost allocation</p>
      </div>
    </div>'''))

# 8 - Complex Orchestration
all_slides.append((8, 'content', 'Challenge: Complex Orchestration', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 10px; border-radius: 4px;">
        <p style="font-size: 11px; color: #ED1C24; margin: 0; font-weight: 600;">The Problem</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">• Multi-step AI pipelines require significant engineering</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Error handling across chained LLM calls is complex</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Parallel execution optimization requires expertise</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Debugging failed workflows is time-consuming</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Business users cannot build AI workflows</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 10px; border-radius: 4px;">
        <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Our Solution</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">• Visual DAG workflow designer - drag-and-drop</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• 12+ node types: LLM, Agent, Tool, Condition, Human...</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Automatic parallel execution with dependency management</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Built-in retry logic and error handling</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">• Step-by-step execution viewer with logs</p>
      </div>
    </div>'''))

# Write first 8 slides
for item in all_slides:
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

print(f"Created {len(all_slides)} slides (batch 1)")
