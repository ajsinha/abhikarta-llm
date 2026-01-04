import os

def create_slide(slide_num, title, content_html):
    return f'''<!DOCTYPE html>
<html>
<head><link rel="stylesheet" href="professional-theme.css"></head>
<body class="col" style="width: 960px; height: 540px; background: #F4F9FD;">
  <div style="background: #0079C1; padding: 12px 40px; display: flex; justify-content: space-between; align-items: center;">
    <p style="font-size: 18px; color: #FFFFFF; margin: 0; font-weight: 600;">{title}</p>
    <p style="font-size: 11px; color: #FFFFFF; margin: 0;">Abhikarta-LLM v1.4.7</p>
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

slides = []

# Slide 36: Developer Productivity Use Case
slides.append((36, "Use Case: Developer Productivity", '''
    <div style="display: flex; gap: 20px; height: 100%;">
      <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-left: 4px solid #0079C1;">
          <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Challenge</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Code review bottlenecks, documentation debt, onboarding new developers, technical debt accumulation.</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-left: 4px solid #ED1C24;">
          <p style="font-size: 13px; color: #ED1C24; margin: 0; font-weight: 600;">Solution</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">AI coding assistants for review, doc generation, test creation. Local models for code privacy. Technical Q&A agents.</p>
        </div>
      </div>
      <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Key Features Used</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">CodeLlama via Ollama, RAG for codebase, Agent tools for git/IDE</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Results</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">Faster reviews, better docs, improved code quality, faster onboarding</p>
        </div>
      </div>
    </div>'''))

# Slide 37: Technology Stack - Section Divider
slides.append((37, "Technology Stack", '''
    <div class="col center" style="height: 100%;">
      <p style="font-size: 36px; color: #0079C1; margin: 0; font-weight: 700;">Section 10</p>
      <p style="font-size: 20px; color: #1A3A5C; margin: 16px 0 0 0;">Technology Stack</p>
      <p style="font-size: 13px; color: #5A7A9C; margin: 12px 0 0 0;">Modern, scalable, enterprise-ready architecture</p>
    </div>'''))

# Slide 38: Technology Stack Overview
slides.append((38, "Technology Stack Overview", '''
    <div style="display: flex; gap: 16px; height: 100%;">
      <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #ED1C24;">
          <p style="font-size: 12px; color: #ED1C24; margin: 0; font-weight: 600;">BACKEND</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">Python 3.11+ | Flask | SQLAlchemy | Pydantic</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
          <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">FRONTEND</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">Bootstrap 5 | Jinja2 | JavaScript | REST API</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
          <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">DATABASE</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">SQLite (dev) | PostgreSQL (prod) | Vector Store</p>
        </div>
      </div>
      <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
          <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">LLM INTEGRATION</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">LangChain | LlamaIndex | OpenAI SDK | Anthropic SDK</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #ED1C24;">
          <p style="font-size: 12px; color: #ED1C24; margin: 0; font-weight: 600;">DEPLOYMENT</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">Docker | Kubernetes | Gunicorn | Nginx</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
          <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">OBSERVABILITY</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">Structured Logging | Metrics | Audit Trails</p>
        </div>
      </div>
    </div>'''))

# Slide 39: Deployment Options
slides.append((39, "Deployment Options", '''
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; height: 100%;">
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-top: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Local Development</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">SQLite database, Flask dev server. pip install and go. Perfect for exploration and development.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-top: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Docker Compose</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Containerized with PostgreSQL. Single command deployment. Ideal for small teams and pilots.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-top: 4px solid #ED1C24;">
        <p style="font-size: 14px; color: #ED1C24; margin: 0; font-weight: 600;">Kubernetes</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Helm charts for production scale. Horizontal scaling, high availability, enterprise SLAs.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-top: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Air-Gapped</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Fully offline with Ollama. No external connectivity required. Maximum security.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-top: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Cloud Hosted</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">AWS, Azure, GCP deployment. Managed services integration. Scalable infrastructure.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-top: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Hybrid</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Local models for sensitive data, cloud for scale. Best of both worlds.</p>
      </div>
    </div>'''))

# Slide 40: Getting Started
slides.append((40, "Getting Started", '''
    <div style="display: flex; flex-direction: column; gap: 12px; height: 100%;">
      <div style="display: flex; gap: 12px;">
        <div style="flex: 1; background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px;">
          <p style="font-size: 13px; color: #ED1C24; margin: 0; font-weight: 600;">Step 1: Install</p>
          <div style="background: #F4F9FD; padding: 8px; border-radius: 4px; margin-top: 8px;">
            <p style="font-size: 10px; color: #1A3A5C; margin: 0; font-family: monospace;">pip install abhikarta-llm</p>
          </div>
        </div>
        <div style="flex: 1; background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px;">
          <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Step 2: Configure</p>
          <div style="background: #F4F9FD; padding: 8px; border-radius: 4px; margin-top: 8px;">
            <p style="font-size: 10px; color: #1A3A5C; margin: 0; font-family: monospace;">abhikarta init</p>
          </div>
        </div>
        <div style="flex: 1; background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px;">
          <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Step 3: Run</p>
          <div style="background: #F4F9FD; padding: 8px; border-radius: 4px; margin-top: 8px;">
            <p style="font-size: 10px; color: #1A3A5C; margin: 0; font-family: monospace;">abhikarta web start</p>
          </div>
        </div>
      </div>
      <div style="background: #FFFFFF; border: 2px solid #0079C1; border-radius: 8px; padding: 14px;">
        <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Quick Start with Ollama (Free, Local, Private)</p>
        <div style="display: flex; gap: 10px; margin-top: 10px;">
          <div style="flex: 1; background: #F4F9FD; padding: 8px; border-radius: 4px;">
            <p style="font-size: 9px; color: #5A7A9C; margin: 0;">1. Install Ollama</p>
            <p style="font-size: 9px; color: #1A3A5C; margin: 4px 0 0 0; font-family: monospace;">curl -fsSL ollama.com/install.sh | sh</p>
          </div>
          <div style="flex: 1; background: #F4F9FD; padding: 8px; border-radius: 4px;">
            <p style="font-size: 9px; color: #5A7A9C; margin: 0;">2. Pull a model</p>
            <p style="font-size: 9px; color: #1A3A5C; margin: 4px 0 0 0; font-family: monospace;">ollama pull llama3.3</p>
          </div>
          <div style="flex: 1; background: #F4F9FD; padding: 8px; border-radius: 4px;">
            <p style="font-size: 9px; color: #5A7A9C; margin: 0;">3. Start using</p>
            <p style="font-size: 9px; color: #1A3A5C; margin: 4px 0 0 0;">Ollama is the default!</p>
          </div>
        </div>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px;">
        <p style="font-size: 11px; color: #5A7A9C; margin: 0;">Documentation includes quick start guides, API reference, tutorials, and example projects. Access at localhost:5000/docs after installation.</p>
      </div>
    </div>'''))

# Slide 41: Roadmap
slides.append((41, "Product Roadmap", '''
    <div style="display: flex; gap: 14px; height: 100%;">
      <div style="flex: 1; background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-top: 4px solid #0079C1;">
        <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Q1 2025</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Enhanced Workflow Designer, Agent Swarm Orchestration, Visual Analytics Dashboard</p>
      </div>
      <div style="flex: 1; background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-top: 4px solid #0079C1;">
        <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Q2 2025</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Multi-Tenant SaaS, Advanced RAG Strategies, Model Fine-Tuning Integration</p>
      </div>
      <div style="flex: 1; background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-top: 4px solid #ED1C24;">
        <p style="font-size: 13px; color: #ED1C24; margin: 0; font-weight: 600;">Q3 2025</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Industry Vertical Solutions, Enterprise SSO, Advanced HITL Workflows</p>
      </div>
      <div style="flex: 1; background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-top: 4px solid #0079C1;">
        <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Q4 2025</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Marketplace for Agents & Workflows, Advanced Observability, Global Expansion</p>
      </div>
    </div>'''))

# Slide 42: Competitive Analysis - Section Divider
slides.append((42, "Competitive Analysis", '''
    <div class="col center" style="height: 100%;">
      <p style="font-size: 36px; color: #0079C1; margin: 0; font-weight: 700;">Appendix A</p>
      <p style="font-size: 20px; color: #1A3A5C; margin: 16px 0 0 0;">Competitive Analysis</p>
      <p style="font-size: 13px; color: #5A7A9C; margin: 12px 0 0 0;">Market positioning and differentiation</p>
    </div>'''))

# Slide 43: Competitive Comparison Table
slides.append((43, "Competitive Comparison", '''
    <div style="display: flex; flex-direction: column; gap: 8px; height: 100%;">
      <div style="display: grid; grid-template-columns: 1.8fr 1fr 1fr 1fr 1fr; gap: 4px; font-size: 9px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 6px; border-radius: 4px;">
          <p style="color: #0079C1; margin: 0; font-weight: 600;">Feature</p>
        </div>
        <div style="background: #ED1C24; padding: 6px; border-radius: 4px; text-align: center;">
          <p style="color: #FFFFFF; margin: 0; font-weight: 600;">Abhikarta</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 6px; border-radius: 4px; text-align: center;">
          <p style="color: #1A3A5C; margin: 0;">LangChain</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 6px; border-radius: 4px; text-align: center;">
          <p style="color: #1A3A5C; margin: 0;">AutoGen</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 6px; border-radius: 4px; text-align: center;">
          <p style="color: #1A3A5C; margin: 0;">CrewAI</p>
        </div>
      </div>
      <div style="display: grid; grid-template-columns: 1.8fr 1fr 1fr 1fr 1fr; gap: 4px; font-size: 8px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px;"><p style="color: #5A7A9C; margin: 0;">Multi-Provider Support</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #0079C1; margin: 0;">11+ Native</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #5A7A9C; margin: 0;">Via Integrations</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #5A7A9C; margin: 0;">Limited</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #5A7A9C; margin: 0;">Limited</p></div>
        
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px;"><p style="color: #5A7A9C; margin: 0;">Visual Workflow Designer</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #0079C1; margin: 0;">Built-in DAG</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #5A7A9C; margin: 0;">LangGraph</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #5A7A9C; margin: 0;">Code Only</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #5A7A9C; margin: 0;">Code Only</p></div>
        
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px;"><p style="color: #5A7A9C; margin: 0;">AI Organization Hierarchy</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #0079C1; margin: 0;">Full Support</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #ED1C24; margin: 0;">None</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #5A7A9C; margin: 0;">Basic</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #5A7A9C; margin: 0;">Basic</p></div>
        
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px;"><p style="color: #5A7A9C; margin: 0;">Human-in-the-Loop</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #0079C1; margin: 0;">Native HITL</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #5A7A9C; margin: 0;">Manual</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #5A7A9C; margin: 0;">Basic</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #ED1C24; margin: 0;">None</p></div>
        
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px;"><p style="color: #5A7A9C; margin: 0;">Enterprise RBAC</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #0079C1; margin: 0;">Full RBAC</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #ED1C24; margin: 0;">None</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #ED1C24; margin: 0;">None</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #ED1C24; margin: 0;">None</p></div>
        
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px;"><p style="color: #5A7A9C; margin: 0;">Local Model Default</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #0079C1; margin: 0;">Ollama Default</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #5A7A9C; margin: 0;">Via Config</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #5A7A9C; margin: 0;">Via Config</p></div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 5px; border-radius: 3px; text-align: center;"><p style="color: #5A7A9C; margin: 0;">Via Config</p></div>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 6px; padding: 10px; margin-top: auto;">
        <p style="font-size: 9px; color: #5A7A9C; margin: 0; line-height: 1.3;">Key Differentiator: Abhikarta-LLM uniquely combines multi-provider abstraction, visual workflows, AI organizations, HITL controls, and enterprise security in a single integrated platform.</p>
      </div>
    </div>'''))

# Slide 44: Acknowledgements - Section Divider
slides.append((44, "Acknowledgements", '''
    <div class="col center" style="height: 100%;">
      <p style="font-size: 36px; color: #0079C1; margin: 0; font-weight: 700;">Appendix B</p>
      <p style="font-size: 20px; color: #1A3A5C; margin: 16px 0 0 0;">Open Source Acknowledgements</p>
      <p style="font-size: 13px; color: #5A7A9C; margin: 12px 0 0 0;">Standing on the shoulders of giants</p>
    </div>'''))

# Slide 45: Open Source Acknowledgements Part 1
slides.append((45, "Open Source: LLM & AI Frameworks", '''
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; height: 100%;">
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">LangChain</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">MIT License</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">LLM application framework</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">LlamaIndex</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">MIT License</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Data framework for LLMs</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #ED1C24;">
        <p style="font-size: 12px; color: #ED1C24; margin: 0; font-weight: 600;">Ollama</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">MIT License</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Local LLM runtime</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">OpenAI SDK</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">MIT License</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">OpenAI API client</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">Anthropic SDK</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">MIT License</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Anthropic API client</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">Sentence Transformers</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">Apache 2.0</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Text embeddings</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">ChromaDB</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">Apache 2.0</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Vector database</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">FAISS</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">MIT License</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Vector similarity search</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">Transformers</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">Apache 2.0</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">HuggingFace ML library</p>
      </div>
    </div>'''))

# Slide 46: Open Source Acknowledgements Part 2
slides.append((46, "Open Source: Web & Infrastructure", '''
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; height: 100%;">
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">Flask</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">BSD License</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Web framework</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">SQLAlchemy</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">MIT License</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">ORM and database toolkit</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">Pydantic</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">MIT License</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Data validation</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">Bootstrap</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">MIT License</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Frontend framework</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">Jinja2</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">BSD License</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Template engine</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">Gunicorn</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">MIT License</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">WSGI HTTP Server</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">Docker</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">Apache 2.0</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Container platform</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">PostgreSQL</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">PostgreSQL License</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Database</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">Redis</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">BSD License</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Caching & queues</p>
      </div>
    </div>'''))

# Slide 47: Thank You
slides.append((47, "Thank You", '''
    <div class="col center" style="height: 100%;">
      <p style="font-size: 48px; color: #0079C1; margin: 0; font-weight: 700;">Thank You</p>
      <p style="font-size: 22px; color: #1A3A5C; margin: 16px 0 0 0;">Abhikarta-LLM</p>
      <p style="font-size: 14px; color: #5A7A9C; margin: 8px 0 0 0;">Enterprise AI Orchestration Platform</p>
      
      <div style="display: flex; gap: 20px; margin-top: 28px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 12px 20px; border-radius: 8px; text-align: center;">
          <p style="font-size: 18px; color: #ED1C24; margin: 0; font-weight: 600;">11+ Providers</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 12px 20px; border-radius: 8px; text-align: center;">
          <p style="font-size: 18px; color: #0079C1; margin: 0; font-weight: 600;">100+ Models</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 12px 20px; border-radius: 8px; text-align: center;">
          <p style="font-size: 18px; color: #1A3A5C; margin: 0; font-weight: 600;">v1.4.7</p>
        </div>
      </div>
      
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 12px 28px; border-radius: 8px; margin-top: 24px;">
        <p style="font-size: 13px; color: #1A3A5C; margin: 0;">Questions? Contact the Development Team</p>
      </div>
    </div>'''))

for num, title, content in slides:
    filename = f"slide{num:02d}.html"
    with open(filename, 'w') as f:
        f.write(create_slide(num, title, content))
    print(f"Created {filename}")

print("Part 4 slides created")
