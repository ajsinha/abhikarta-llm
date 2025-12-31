import os

# Professional template with BMO blue top/bottom bars and light blue content
def create_slide(slide_num, title, content_html):
    return f'''<!DOCTYPE html>
<html>
<head><link rel="stylesheet" href="professional-theme.css"></head>
<body class="col" style="width: 960px; height: 540px; background: #F4F9FD;">
  <div style="background: #0079C1; padding: 12px 40px; display: flex; justify-content: space-between; align-items: center;">
    <p style="font-size: 18px; color: #FFFFFF; margin: 0; font-weight: 600;">{title}</p>
    <p style="font-size: 11px; color: #FFFFFF; margin: 0;">Abhikarta-LLM v1.4.6</p>
  </div>
  
  <div class="fill-height" style="background: #F4F9FD; padding: 16px 40px;">
{content_html}
  </div>
  
  <div style="background: #0079C1; padding: 8px 40px; display: flex; justify-content: space-between; align-items: center;">
    <p style="font-size: 9px; color: #FFFFFF; margin: 0;">Copyright © 2025-2030 Ashutosh Sinha | Patent Pending</p>
    <p style="font-size: 9px; color: #FFFFFF; margin: 0;">{slide_num}</p>
  </div>
</body>
</html>'''

# Define all slides
slides = []

# Slide 3: Executive Summary
slides.append((3, "Executive Summary", '''
    <div style="display: flex; gap: 20px; height: 100%;">
      <div style="flex: 1.2; display: flex; flex-direction: column; gap: 12px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px;">
          <p style="font-size: 14px; color: #1A3A5C; margin: 0; line-height: 1.5;">Abhikarta-LLM is a comprehensive enterprise platform for building, deploying, and managing AI agents and workflows with multi-provider LLM support, visual designers, and industry-specific solutions.</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-left: 4px solid #0079C1;">
          <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">Vision</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 6px 0 0 0;">Democratize enterprise AI by providing a unified platform that abstracts LLM complexity while maintaining enterprise-grade security and governance.</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-left: 4px solid #ED1C24;">
          <p style="font-size: 12px; color: #ED1C24; margin: 0; font-weight: 600;">Mission</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 6px 0 0 0;">Enable organizations to leverage AI capabilities without vendor lock-in, with full control over costs, data privacy, and compliance requirements.</p>
        </div>
      </div>
      <div style="flex: 0.8; display: flex; flex-direction: column; gap: 10px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; text-align: center;">
          <p style="font-size: 28px; color: #0079C1; margin: 0; font-weight: 700;">11+</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 4px 0 0 0;">LLM Providers</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; text-align: center;">
          <p style="font-size: 28px; color: #1A3A5C; margin: 0; font-weight: 700;">100+</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 4px 0 0 0;">Models Available</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; text-align: center;">
          <p style="font-size: 28px; color: #ED1C24; margin: 0; font-weight: 700;">$0</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 4px 0 0 0;">Local Model Cost</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; text-align: center;">
          <p style="font-size: 28px; color: #0079C1; margin: 0; font-weight: 700;">100%</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 4px 0 0 0;">Data Privacy</p>
        </div>
      </div>
    </div>'''))

# Slide 4: Key Value Propositions
slides.append((4, "Key Value Propositions", '''
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; height: 100%;">
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-top: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Provider Agnostic</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Switch between OpenAI, Anthropic, Google, Azure, AWS, and local models without code changes. Avoid vendor lock-in.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-top: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Cost Optimization</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Use free local models for development, cloud for production. Rate limiting and quotas prevent cost overruns.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-top: 4px solid #ED1C24;">
        <p style="font-size: 14px; color: #ED1C24; margin: 0; font-weight: 600;">Data Privacy</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Run sensitive workloads on local Ollama models. Data never leaves your infrastructure.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-top: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Visual Orchestration</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Design complex AI pipelines visually with DAG workflows. No coding required for business users.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-top: 4px solid #ED1C24;">
        <p style="font-size: 14px; color: #ED1C24; margin: 0; font-weight: 600;">Enterprise Governance</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">RBAC, audit trails, compliance controls. Meet regulatory requirements for AI deployment.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-top: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Human-in-the-Loop</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Human oversight for critical decisions. Approve, reject, or modify AI outputs before execution.</p>
      </div>
    </div>'''))

# Slide 5: Market Challenges - Section Divider
slides.append((5, "Market Challenges", '''
    <div class="col center" style="height: 100%;">
      <p style="font-size: 36px; color: #0079C1; margin: 0; font-weight: 700;">Section 2</p>
      <p style="font-size: 20px; color: #1A3A5C; margin: 16px 0 0 0;">Market Challenges & Problems Solved</p>
      <p style="font-size: 13px; color: #5A7A9C; margin: 12px 0 0 0;">Understanding the enterprise AI landscape</p>
    </div>'''))

# Slide 6: Challenge - Provider Lock-In
slides.append((6, "Challenge: Provider Lock-In", '''
    <div style="display: flex; gap: 20px; height: 100%;">
      <div style="flex: 1; display: flex; flex-direction: column; gap: 12px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #ED1C24;">
          <p style="font-size: 13px; color: #ED1C24; margin: 0; font-weight: 600;">The Problem</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.5;">Organizations building on a single LLM provider face significant risks: pricing changes, service disruptions, capability gaps, and inability to leverage new models from competitors.</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Impact</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 6px 0 0 0;">High switching costs, competitive disadvantage, limited negotiating power</p>
        </div>
      </div>
      <div style="flex: 1; display: flex; flex-direction: column; gap: 12px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #0079C1;">
          <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Our Solution</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.5;">Unified abstraction layer across 11+ providers. Same code, different models. Switch providers with configuration change.</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Benefits</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 6px 0 0 0;">Negotiate better rates, access best-in-class models, eliminate migration costs</p>
        </div>
      </div>
    </div>'''))

# Slide 7: Challenge - Governance Gaps
slides.append((7, "Challenge: AI Governance Gaps", '''
    <div style="display: flex; gap: 20px; height: 100%;">
      <div style="flex: 1; display: flex; flex-direction: column; gap: 12px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #ED1C24;">
          <p style="font-size: 13px; color: #ED1C24; margin: 0; font-weight: 600;">The Problem</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.5;">Shadow AI proliferates across organizations. Teams use ChatGPT, Claude, and other tools without IT oversight, creating compliance, security, and data leakage risks.</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Impact</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 6px 0 0 0;">Regulatory violations, data breaches, uncontrolled costs, inconsistent outputs</p>
        </div>
      </div>
      <div style="flex: 1; display: flex; flex-direction: column; gap: 12px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #0079C1;">
          <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Our Solution</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.5;">Centralized AI platform with RBAC, audit logging, rate limiting, and usage tracking. All AI interactions go through governed channels.</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Benefits</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 6px 0 0 0;">Complete visibility, compliance-ready, cost control, consistent quality</p>
        </div>
      </div>
    </div>'''))

# Slide 8: Challenge - Complex Orchestration
slides.append((8, "Challenge: Complex Orchestration", '''
    <div style="display: flex; gap: 20px; height: 100%;">
      <div style="flex: 1; display: flex; flex-direction: column; gap: 12px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #ED1C24;">
          <p style="font-size: 13px; color: #ED1C24; margin: 0; font-weight: 600;">The Problem</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.5;">Building multi-step AI pipelines requires significant engineering effort. Handling parallel execution, error recovery, and state management is complex and error-prone.</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Impact</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 6px 0 0 0;">Long development cycles, brittle systems, difficult debugging</p>
        </div>
      </div>
      <div style="flex: 1; display: flex; flex-direction: column; gap: 12px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #0079C1;">
          <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Our Solution</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.5;">Visual DAG workflow designer. Drag-and-drop interface for creating AI pipelines. Built-in parallel execution, error handling, and retry logic.</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Benefits</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 6px 0 0 0;">Rapid development, visual debugging, business user empowerment</p>
        </div>
      </div>
    </div>'''))

# Slide 9: Challenge - Cost Management
slides.append((9, "Challenge: AI Cost Management", '''
    <div style="display: flex; gap: 20px; height: 100%;">
      <div style="flex: 1; display: flex; flex-direction: column; gap: 12px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #ED1C24;">
          <p style="font-size: 13px; color: #ED1C24; margin: 0; font-weight: 600;">The Problem</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.5;">LLM API costs can spiral quickly at scale. Without controls, a single runaway process or popular feature can generate unexpected bills in the thousands of dollars.</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Impact</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 6px 0 0 0;">Budget overruns, project cancellations, limited AI adoption</p>
        </div>
      </div>
      <div style="flex: 1; display: flex; flex-direction: column; gap: 12px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #0079C1;">
          <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Our Solution</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.5;">Rate limiting per user/team/org. Token quotas. Local model support via Ollama at $0 cost. Usage analytics and alerts.</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Benefits</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 6px 0 0 0;">Predictable costs, development at $0, scale with confidence</p>
        </div>
      </div>
    </div>'''))

# Slide 10: Platform Architecture - Section Divider
slides.append((10, "Platform Architecture", '''
    <div class="col center" style="height: 100%;">
      <p style="font-size: 36px; color: #0079C1; margin: 0; font-weight: 700;">Section 3</p>
      <p style="font-size: 20px; color: #1A3A5C; margin: 16px 0 0 0;">Platform Architecture</p>
      <p style="font-size: 13px; color: #5A7A9C; margin: 12px 0 0 0;">System design, components, and integration patterns</p>
    </div>'''))

# Slide 11: Architecture Overview
slides.append((11, "Architecture Overview", '''
    <div style="display: flex; flex-direction: column; gap: 10px; height: 100%;">
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 6px; padding: 8px; text-align: center;">
        <p style="font-size: 11px; color: #5A7A9C; margin: 0;">USER INTERFACES: Web UI | REST API | Admin Console | CLI</p>
      </div>
      <p style="font-size: 14px; color: #0079C1; margin: 0; text-align: center;">▼</p>
      <div style="background: #FFFFFF; border: 2px solid #0079C1; border-radius: 8px; padding: 12px;">
        <p style="font-size: 12px; color: #0079C1; margin: 0 0 8px 0; font-weight: 600; text-align: center;">ABHIKARTA-LLM CORE ENGINE</p>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px;">
          <div style="background: #F4F9FD; padding: 8px; border-radius: 6px; text-align: center;">
            <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Agent Framework</p>
            <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Persona, Tools, Memory</p>
          </div>
          <div style="background: #F4F9FD; padding: 8px; border-radius: 6px; text-align: center;">
            <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Workflow Engine</p>
            <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">DAG Orchestration</p>
          </div>
          <div style="background: #F4F9FD; padding: 8px; border-radius: 6px; text-align: center;">
            <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">AI Org Manager</p>
            <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Hierarchy & HITL</p>
          </div>
          <div style="background: #F4F9FD; padding: 8px; border-radius: 6px; text-align: center;">
            <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Security Layer</p>
            <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">RBAC, Audit, Keys</p>
          </div>
        </div>
      </div>
      <p style="font-size: 14px; color: #0079C1; margin: 0; text-align: center;">▼</p>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 6px; padding: 8px; text-align: center;">
        <p style="font-size: 11px; color: #5A7A9C; margin: 0;">LLM PROVIDERS: Ollama | OpenAI | Anthropic | Google | Azure | AWS Bedrock | Groq | Mistral</p>
      </div>
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 6px; padding: 8px; text-align: center;">
          <p style="font-size: 10px; color: #1A3A5C; margin: 0;">SQLite / PostgreSQL</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 6px; padding: 8px; text-align: center;">
          <p style="font-size: 10px; color: #1A3A5C; margin: 0;">Vector Store (RAG)</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 6px; padding: 8px; text-align: center;">
          <p style="font-size: 10px; color: #1A3A5C; margin: 0;">File Storage</p>
        </div>
      </div>
    </div>'''))

# Slide 12: Core Components
slides.append((12, "Core Components", '''
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; height: 100%;">
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-left: 4px solid #0079C1;">
        <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Agent Framework</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Modular AI agents with personas, tools, memory, and knowledge bases. Support for ReAct, Chain-of-Thought, and Tree-of-Thoughts reasoning patterns.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-left: 4px solid #0079C1;">
        <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Workflow Engine</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">DAG-based orchestration with parallel execution, conditional branching, error handling, and full execution traceability.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-left: 4px solid #ED1C24;">
        <p style="font-size: 13px; color: #ED1C24; margin: 0; font-weight: 600;">AI Organization Manager</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Patent-pending hierarchical AI governance. Create AI org charts with delegation, aggregation, and human-in-the-loop controls.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-left: 4px solid #0079C1;">
        <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Security Layer</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Role-based access control, API key management, rate limiting, audit logging, and compliance controls.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-left: 4px solid #0079C1;">
        <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Provider Abstraction</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Unified interface for 11+ LLM providers. Consistent API regardless of underlying model or provider.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-left: 4px solid #0079C1;">
        <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Knowledge Management</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">RAG pipeline with vector stores, document ingestion, chunking strategies, and semantic search.</p>
      </div>
    </div>'''))

# Continue with more slides...
for num, title, content in slides:
    filename = f"slide{num:02d}.html"
    with open(filename, 'w') as f:
        f.write(create_slide(num, title, content))
    print(f"Created {filename}")

print("Initial slides created")
