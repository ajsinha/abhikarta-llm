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

# Slide 13: Multi-Provider Support - Section Divider
slides.append((13, "Multi-Provider LLM Support", '''
    <div class="col center" style="height: 100%;">
      <p style="font-size: 36px; color: #0079C1; margin: 0; font-weight: 700;">Section 4</p>
      <p style="font-size: 20px; color: #1A3A5C; margin: 16px 0 0 0;">Multi-Provider LLM Support</p>
      <p style="font-size: 13px; color: #5A7A9C; margin: 12px 0 0 0;">Unified access to 11+ LLM providers and 100+ models</p>
    </div>'''))

# Slide 14: Supported Providers Overview
slides.append((14, "Supported LLM Providers", '''
    <div style="display: flex; flex-direction: column; gap: 12px; height: 100%;">
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px;">
        <p style="font-size: 11px; color: #5A7A9C; margin: 0; line-height: 1.4;">Abhikarta-LLM provides a unified abstraction layer across all major LLM providers. Switch between providers without code changes. Optimize for cost, speed, capability, or compliance requirements.</p>
      </div>
      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; flex: 1;">
        <div style="background: linear-gradient(135deg, #ED1C24, #B81419); border-radius: 8px; padding: 12px; text-align: center;">
          <p style="font-size: 13px; color: #FFFFFF; margin: 0; font-weight: 600;">Ollama</p>
          <p style="font-size: 9px; color: #FFD0D0; margin: 4px 0 0 0;">DEFAULT - Free, Local</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; text-align: center;">
          <p style="font-size: 13px; color: #1A3A5C; margin: 0; font-weight: 600;">OpenAI</p>
          <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">GPT-4o, o1, o3</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; text-align: center;">
          <p style="font-size: 13px; color: #1A3A5C; margin: 0; font-weight: 600;">Anthropic</p>
          <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Claude 4.5 Series</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; text-align: center;">
          <p style="font-size: 13px; color: #1A3A5C; margin: 0; font-weight: 600;">Google</p>
          <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Gemini 2.0, 1.5</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; text-align: center;">
          <p style="font-size: 13px; color: #1A3A5C; margin: 0; font-weight: 600;">Azure OpenAI</p>
          <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Enterprise Compliant</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; text-align: center;">
          <p style="font-size: 13px; color: #1A3A5C; margin: 0; font-weight: 600;">AWS Bedrock</p>
          <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Multi-Model Access</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; text-align: center;">
          <p style="font-size: 13px; color: #1A3A5C; margin: 0; font-weight: 600;">Groq</p>
          <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Ultra-Fast Inference</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; text-align: center;">
          <p style="font-size: 13px; color: #1A3A5C; margin: 0; font-weight: 600;">Mistral AI</p>
          <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">EU Data Residency</p>
        </div>
      </div>
      <p style="font-size: 10px; color: #5A7A9C; margin: 0; text-align: center;">+ Cohere | Together AI | HuggingFace | Custom Endpoints</p>
    </div>'''))

# Slide 15: Ollama - Default Provider
slides.append((15, "Ollama: Default Provider", '''
    <div style="display: flex; gap: 20px; height: 100%;">
      <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-left: 4px solid #ED1C24;">
          <p style="font-size: 13px; color: #ED1C24; margin: 0; font-weight: 600;">Why Ollama is Default</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Free, runs locally, data never leaves your infrastructure. Perfect for development, testing, and sensitive workloads.</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">40+ Models Supported</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">Llama 3.3, Qwen 2.5, DeepSeek, Mistral, Phi-4, Gemma 2, CodeLlama, and more</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Key Benefits</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">Zero API costs, complete privacy, offline capable, fast local inference</p>
        </div>
      </div>
      <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-left: 4px solid #0079C1;">
          <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">Quick Start</p>
          <div style="background: #F4F9FD; padding: 8px; border-radius: 4px; margin-top: 8px;">
            <p style="font-size: 10px; color: #1A3A5C; margin: 0; font-family: monospace;">curl -fsSL ollama.com/install.sh | sh</p>
          </div>
          <div style="background: #F4F9FD; padding: 8px; border-radius: 4px; margin-top: 6px;">
            <p style="font-size: 10px; color: #1A3A5C; margin: 0; font-family: monospace;">ollama pull llama3.3</p>
          </div>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Use Cases</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">Development, testing, air-gapped environments, cost-sensitive workloads, GDPR compliance</p>
        </div>
      </div>
    </div>'''))

# Slide 16: Provider Selection Strategy
slides.append((16, "Provider Selection Strategy", '''
    <div style="display: flex; flex-direction: column; gap: 12px; height: 100%;">
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px;">
        <p style="font-size: 11px; color: #5A7A9C; margin: 0;">Choose the right provider based on your specific requirements. Abhikarta makes switching seamless.</p>
      </div>
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; flex: 1;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-top: 3px solid #0079C1;">
          <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">Cost Optimization</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0;">Use Ollama for dev/test, Groq for fast inference, cloud for production scale</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-top: 3px solid #ED1C24;">
          <p style="font-size: 12px; color: #ED1C24; margin: 0; font-weight: 600;">Data Privacy</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0;">Ollama for sensitive data, Azure/Bedrock for enterprise compliance</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-top: 3px solid #0079C1;">
          <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">Performance</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0;">Groq for ultra-fast, OpenAI/Anthropic for reasoning, Gemini for multimodal</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-top: 3px solid #0079C1;">
          <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">EU Compliance</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0;">Mistral AI for EU data residency, Azure Europe regions</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-top: 3px solid #0079C1;">
          <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">Enterprise Scale</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0;">Azure OpenAI, AWS Bedrock for SLAs and enterprise support</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-top: 3px solid #0079C1;">
          <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">Specialized Tasks</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0;">CodeLlama for code, Claude for analysis, Gemini for vision</p>
        </div>
      </div>
    </div>'''))

# Slide 17: Unified API Benefits
slides.append((17, "Unified API Benefits", '''
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; height: 100%;">
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">No Code Changes Required</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Same agent definition works with any provider. Change model via configuration, not code refactoring.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Consistent Error Handling</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Unified error types and retry logic across all providers. Provider-specific quirks handled internally.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #ED1C24;">
        <p style="font-size: 14px; color: #ED1C24; margin: 0; font-weight: 600;">Automatic Failover</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Configure backup providers. If primary fails, automatically route to secondary without user disruption.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Standardized Metrics</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Compare token usage, latency, and costs across providers using consistent metrics.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Future-Proof</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">New providers added without application changes. Stay current with latest models automatically.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Vendor Negotiation Power</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Credible ability to switch gives leverage in pricing negotiations with LLM providers.</p>
      </div>
    </div>'''))

# Slide 18: Agent Framework - Section Divider
slides.append((18, "Agent Framework", '''
    <div class="col center" style="height: 100%;">
      <p style="font-size: 36px; color: #0079C1; margin: 0; font-weight: 700;">Section 5</p>
      <p style="font-size: 20px; color: #1A3A5C; margin: 16px 0 0 0;">Agent Framework</p>
      <p style="font-size: 13px; color: #5A7A9C; margin: 12px 0 0 0;">Building intelligent, reusable AI agents</p>
    </div>'''))

# Slide 19: Agent Architecture
slides.append((19, "Agent Architecture", '''
    <div style="display: flex; gap: 20px; height: 100%;">
      <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
        <div style="background: #FFFFFF; border: 2px solid #0079C1; border-radius: 8px; padding: 14px;">
          <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600; text-align: center;">AI AGENT COMPONENTS</p>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px;">
            <div style="background: #F4F9FD; padding: 10px; border-radius: 6px; text-align: center;">
              <p style="font-size: 11px; color: #ED1C24; margin: 0; font-weight: 600;">Persona</p>
              <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">System prompts</p>
            </div>
            <div style="background: #F4F9FD; padding: 10px; border-radius: 6px; text-align: center;">
              <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Tools</p>
              <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">APIs, functions</p>
            </div>
            <div style="background: #F4F9FD; padding: 10px; border-radius: 6px; text-align: center;">
              <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Memory</p>
              <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Context, history</p>
            </div>
            <div style="background: #F4F9FD; padding: 10px; border-radius: 6px; text-align: center;">
              <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Knowledge</p>
              <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">RAG, documents</p>
            </div>
          </div>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px;">
          <p style="font-size: 11px; color: #5A7A9C; margin: 0; line-height: 1.4;">Agents are reusable AI entities that combine LLM capabilities with specialized tools and knowledge to accomplish specific tasks.</p>
        </div>
      </div>
      <div style="flex: 1; display: flex; flex-direction: column; gap: 8px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 3px solid #0079C1;">
          <p style="font-size: 11px; color: #1A3A5C; margin: 0; font-weight: 600;">Multi-Provider Support</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 4px 0 0 0;">Same agent works with any LLM provider</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 3px solid #0079C1;">
          <p style="font-size: 11px; color: #1A3A5C; margin: 0; font-weight: 600;">Tool Integration</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 4px 0 0 0;">Connect to databases, APIs, file systems</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 3px solid #0079C1;">
          <p style="font-size: 11px; color: #1A3A5C; margin: 0; font-weight: 600;">RAG Pipeline</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 4px 0 0 0;">Ground responses in your documents</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 3px solid #ED1C24;">
          <p style="font-size: 11px; color: #1A3A5C; margin: 0; font-weight: 600;">Governance Controls</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 4px 0 0 0;">Rate limits, model restrictions, audit logs</p>
        </div>
      </div>
    </div>'''))

# Slide 20: Reasoning Patterns
slides.append((20, "Agent Reasoning Patterns", '''
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; height: 100%;">
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-top: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">ReAct Pattern</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Reasoning + Acting. Agent thinks through problem, takes action, observes result, and iterates until task complete.</p>
        <p style="font-size: 10px; color: #1A3A5C; margin: 10px 0 0 0; font-weight: 600;">Best for: Tool use, multi-step tasks</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-top: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Chain-of-Thought</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Step-by-step reasoning. Agent breaks complex problems into smaller steps and solves sequentially.</p>
        <p style="font-size: 10px; color: #1A3A5C; margin: 10px 0 0 0; font-weight: 600;">Best for: Analysis, math, logic</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-top: 4px solid #ED1C24;">
        <p style="font-size: 14px; color: #ED1C24; margin: 0; font-weight: 600;">Tree-of-Thoughts</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Explore multiple reasoning paths. Evaluate branches and select best approach. Enables backtracking.</p>
        <p style="font-size: 10px; color: #1A3A5C; margin: 10px 0 0 0; font-weight: 600;">Best for: Creative, strategic decisions</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-top: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Reflexion</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Self-reflection on outputs. Agent critiques own response and improves iteratively.</p>
        <p style="font-size: 10px; color: #1A3A5C; margin: 10px 0 0 0; font-weight: 600;">Best for: Quality improvement</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-top: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Hierarchical Agents</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Manager agents delegate to specialist agents. Aggregates results from subordinates.</p>
        <p style="font-size: 10px; color: #1A3A5C; margin: 10px 0 0 0; font-weight: 600;">Best for: Complex workflows</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-top: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Goal-Based Agents</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Define objectives, agent plans and executes autonomously to achieve goals.</p>
        <p style="font-size: 10px; color: #1A3A5C; margin: 10px 0 0 0; font-weight: 600;">Best for: Autonomous tasks</p>
      </div>
    </div>'''))

for num, title, content in slides:
    filename = f"slide{num:02d}.html"
    with open(filename, 'w') as f:
        f.write(create_slide(num, title, content))
    print(f"Created {filename}")

print("Part 2 slides created")
