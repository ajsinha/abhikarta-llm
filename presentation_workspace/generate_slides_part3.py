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

# Slide 21: Agent Tools
slides.append((21, "Agent Tool Integration", '''
    <div style="display: flex; gap: 20px; height: 100%;">
      <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">What Are Agent Tools?</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Tools are functions that agents can call to interact with external systems, retrieve data, or perform actions beyond text generation.</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 3px solid #0079C1;">
          <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Database Tools</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 4px 0 0 0;">Query SQL/NoSQL, retrieve records, update data</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 3px solid #0079C1;">
          <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">API Tools</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 4px 0 0 0;">REST calls, webhooks, external service integration</p>
        </div>
      </div>
      <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 3px solid #0079C1;">
          <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">File Tools</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 4px 0 0 0;">Read/write files, parse documents, generate reports</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 3px solid #0079C1;">
          <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Search Tools</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 4px 0 0 0;">Web search, vector search, knowledge base queries</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 3px solid #ED1C24;">
          <p style="font-size: 11px; color: #ED1C24; margin: 0; font-weight: 600;">Custom Tools</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 4px 0 0 0;">Python functions, shell commands, domain-specific</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 3px solid #0079C1;">
          <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">Human-in-Loop</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 4px 0 0 0;">Request human approval, input, or review</p>
        </div>
      </div>
    </div>'''))

# Slide 22: RAG Pipeline
slides.append((22, "Knowledge & RAG Pipeline", '''
    <div style="display: flex; flex-direction: column; gap: 12px; height: 100%;">
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px;">
        <p style="font-size: 11px; color: #5A7A9C; margin: 0;">Retrieval Augmented Generation (RAG) grounds AI responses in your organization's documents, ensuring accuracy and relevance.</p>
      </div>
      <div style="display: flex; gap: 12px; flex: 1;">
        <div style="flex: 1; background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; text-align: center; border-top: 4px solid #0079C1;">
          <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">1. INGEST</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0;">Upload documents: PDF, Word, HTML, Markdown, CSV</p>
        </div>
        <div style="flex: 1; background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; text-align: center; border-top: 4px solid #0079C1;">
          <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">2. CHUNK</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0;">Split into semantic chunks with overlap for context</p>
        </div>
        <div style="flex: 1; background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; text-align: center; border-top: 4px solid #0079C1;">
          <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">3. EMBED</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0;">Generate vector embeddings using selected model</p>
        </div>
        <div style="flex: 1; background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; text-align: center; border-top: 4px solid #ED1C24;">
          <p style="font-size: 12px; color: #ED1C24; margin: 0; font-weight: 600;">4. RETRIEVE</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0;">Semantic search to find relevant context</p>
        </div>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px;">
        <p style="font-size: 11px; color: #1A3A5C; margin: 0; font-weight: 600;">Supported Vector Stores: Chroma, Pinecone, Weaviate, Qdrant, FAISS</p>
      </div>
    </div>'''))

# Slide 23: Workflow DAG - Section Divider
slides.append((23, "Workflow DAG System", '''
    <div class="col center" style="height: 100%;">
      <p style="font-size: 36px; color: #0079C1; margin: 0; font-weight: 700;">Section 6</p>
      <p style="font-size: 20px; color: #1A3A5C; margin: 16px 0 0 0;">Workflow DAG System</p>
      <p style="font-size: 13px; color: #5A7A9C; margin: 12px 0 0 0;">Visual orchestration of complex AI pipelines</p>
    </div>'''))

# Slide 24: DAG Overview
slides.append((24, "DAG Workflow Overview", '''
    <div style="display: flex; gap: 20px; height: 100%;">
      <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">What is a DAG Workflow?</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Directed Acyclic Graph workflows allow you to compose complex AI pipelines from simple building blocks. Nodes execute in dependency order with automatic parallel execution.</p>
        </div>
        <div style="background: #FFFFFF; border: 2px solid #0079C1; border-radius: 8px; padding: 12px;">
          <div style="background: #F4F9FD; padding: 6px; border-radius: 4px; text-align: center;">
            <p style="font-size: 10px; color: #ED1C24; margin: 0;">START: Input</p>
          </div>
          <p style="font-size: 12px; color: #0079C1; margin: 4px 0; text-align: center;">▼</p>
          <div style="display: flex; gap: 6px;">
            <div style="flex: 1; background: #E8F4FC; padding: 5px; border-radius: 4px; text-align: center;">
              <p style="font-size: 9px; color: #0079C1; margin: 0;">Extract</p>
            </div>
            <div style="flex: 1; background: #E8F4FC; padding: 5px; border-radius: 4px; text-align: center;">
              <p style="font-size: 9px; color: #0079C1; margin: 0;">Summarize</p>
            </div>
            <div style="flex: 1; background: #E8F4FC; padding: 5px; border-radius: 4px; text-align: center;">
              <p style="font-size: 9px; color: #0079C1; margin: 0;">Analyze</p>
            </div>
          </div>
          <p style="font-size: 12px; color: #0079C1; margin: 4px 0; text-align: center;">▼</p>
          <div style="background: #F4F9FD; padding: 6px; border-radius: 4px; text-align: center;">
            <p style="font-size: 10px; color: #0079C1; margin: 0;">OUTPUT: Report</p>
          </div>
        </div>
      </div>
      <div style="flex: 1; display: flex; flex-direction: column; gap: 8px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 10px; border-left: 3px solid #0079C1;">
          <p style="font-size: 11px; color: #1A3A5C; margin: 0;">Parallel Execution</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 10px; border-left: 3px solid #0079C1;">
          <p style="font-size: 11px; color: #1A3A5C; margin: 0;">Conditional Branching</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 10px; border-left: 3px solid #0079C1;">
          <p style="font-size: 11px; color: #1A3A5C; margin: 0;">Error Handling & Retry</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 10px; border-left: 3px solid #0079C1;">
          <p style="font-size: 11px; color: #1A3A5C; margin: 0;">Full Audit Trail</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 10px; border-left: 3px solid #ED1C24;">
          <p style="font-size: 11px; color: #1A3A5C; margin: 0;">Human-in-the-Loop Nodes</p>
        </div>
      </div>
    </div>'''))

# Slide 25: Node Types
slides.append((25, "Workflow Node Types", '''
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; height: 100%;">
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-top: 4px solid #0079C1;">
        <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">LLM Node</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Execute prompts against any configured LLM. Supports all providers and models.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-top: 4px solid #0079C1;">
        <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Agent Node</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Invoke a full agent with tools, memory, and knowledge within workflow.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-top: 4px solid #0079C1;">
        <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Tool Node</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Call external APIs, databases, or functions without LLM involvement.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-top: 4px solid #0079C1;">
        <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Transform Node</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Data manipulation: parse JSON, filter, map, aggregate, format outputs.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-top: 4px solid #ED1C24;">
        <p style="font-size: 13px; color: #ED1C24; margin: 0; font-weight: 600;">Human Node</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Pause for human review, approval, or input before continuing.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-top: 4px solid #0079C1;">
        <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Condition Node</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Branch workflow based on conditions, outputs, or rules.</p>
      </div>
    </div>'''))

# Slide 26: AI Organizations - Section Divider
slides.append((26, "AI Organizations", '''
    <div class="col center" style="height: 100%;">
      <p style="font-size: 36px; color: #ED1C24; margin: 0; font-weight: 700;">Section 7</p>
      <p style="font-size: 20px; color: #1A3A5C; margin: 16px 0 0 0;">AI Organizations</p>
      <p style="font-size: 13px; color: #5A7A9C; margin: 12px 0 0 0;">Patent-pending hierarchical AI governance framework</p>
    </div>'''))

# Slide 27: AI Org Overview
slides.append((27, "AI Organization Overview", '''
    <div style="display: flex; gap: 20px; height: 100%;">
      <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-left: 4px solid #ED1C24;">
          <p style="font-size: 13px; color: #ED1C24; margin: 0; font-weight: 600;">What is AI Organization?</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Create AI-powered digital twins of organizational structures. Tasks flow down through delegation, responses aggregate up through hierarchy.</p>
        </div>
        <div style="background: #FFFFFF; border: 2px solid #ED1C24; border-radius: 8px; padding: 12px;">
          <div style="background: linear-gradient(90deg, #ED1C24, #B81419); padding: 8px; border-radius: 4px; text-align: center;">
            <p style="font-size: 10px; color: #FFFFFF; margin: 0;">Enterprise CEO</p>
          </div>
          <div style="display: flex; gap: 6px; margin: 8px 0 0 12px;">
            <div style="flex: 1; background: #E8F4FC; padding: 6px; border-radius: 4px; text-align: center;">
              <p style="font-size: 9px; color: #0079C1; margin: 0;">Division VP</p>
            </div>
            <div style="flex: 1; background: #E8F4FC; padding: 6px; border-radius: 4px; text-align: center;">
              <p style="font-size: 9px; color: #0079C1; margin: 0;">Division VP</p>
            </div>
          </div>
          <div style="display: flex; gap: 4px; margin: 6px 0 0 24px;">
            <div style="flex: 1; background: #F4F9FD; padding: 4px; border-radius: 3px; text-align: center;">
              <p style="font-size: 8px; color: #5A7A9C; margin: 0;">Team</p>
            </div>
            <div style="flex: 1; background: #F4F9FD; padding: 4px; border-radius: 3px; text-align: center;">
              <p style="font-size: 8px; color: #5A7A9C; margin: 0;">Team</p>
            </div>
            <div style="flex: 1; background: #F4F9FD; padding: 4px; border-radius: 3px; text-align: center;">
              <p style="font-size: 8px; color: #5A7A9C; margin: 0;">Team</p>
            </div>
          </div>
        </div>
      </div>
      <div style="flex: 1; display: flex; flex-direction: column; gap: 8px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 10px; border-left: 3px solid #ED1C24;">
          <p style="font-size: 11px; color: #1A3A5C; margin: 0;">Hierarchical Task Delegation</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 10px; border-left: 3px solid #0079C1;">
          <p style="font-size: 11px; color: #1A3A5C; margin: 0;">Response Aggregation</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 10px; border-left: 3px solid #ED1C24;">
          <p style="font-size: 11px; color: #1A3A5C; margin: 0;">Human-in-the-Loop Controls</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 10px; border-left: 3px solid #0079C1;">
          <p style="font-size: 11px; color: #1A3A5C; margin: 0;">Inherited Permissions</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 10px; border-left: 3px solid #0079C1;">
          <p style="font-size: 11px; color: #1A3A5C; margin: 0;">Cost Allocation by Org Unit</p>
        </div>
      </div>
    </div>'''))

# Slide 28: Human-in-the-Loop
slides.append((28, "Human-in-the-Loop Controls", '''
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; height: 100%;">
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #ED1C24;">
        <p style="font-size: 14px; color: #ED1C24; margin: 0; font-weight: 600;">Human Mirrors</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Each AI node can have a human mirror who receives notifications and can review, approve, modify, or reject AI decisions.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Approval Workflows</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Configure which decisions require human approval. Set thresholds based on risk, value, or complexity.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Override Capability</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Humans can override AI decisions at any level. Changes propagate through the hierarchy appropriately.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Notification Channels</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Email, Slack, Microsoft Teams integration. Humans notified when their attention is needed.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">HITL Dashboard</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Central view for humans to manage all their AI mirror responsibilities in one place.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #ED1C24;">
        <p style="font-size: 14px; color: #ED1C24; margin: 0; font-weight: 600;">Audit Trail</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.4;">Complete record of AI decisions and human interventions for compliance and analysis.</p>
      </div>
    </div>'''))

# Slide 29: Security - Section Divider
slides.append((29, "Security & Governance", '''
    <div class="col center" style="height: 100%;">
      <p style="font-size: 36px; color: #0079C1; margin: 0; font-weight: 700;">Section 8</p>
      <p style="font-size: 20px; color: #1A3A5C; margin: 16px 0 0 0;">Security & Governance</p>
      <p style="font-size: 13px; color: #5A7A9C; margin: 12px 0 0 0;">Enterprise-grade controls for AI deployment</p>
    </div>'''))

# Slide 30: Security Overview
slides.append((30, "Security Framework", '''
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; height: 100%;">
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-top: 4px solid #ED1C24;">
        <p style="font-size: 13px; color: #ED1C24; margin: 0; font-weight: 600;">Role-Based Access</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Admin, Operator, Developer, Viewer roles. Customizable permissions per resource type.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-top: 4px solid #0079C1;">
        <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Audit Logging</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Every API call, agent execution, config change logged with user context and timestamps.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-top: 4px solid #0079C1;">
        <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">API Key Management</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Encrypted storage, environment injection, rotation support for provider credentials.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-top: 4px solid #0079C1;">
        <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Rate Limiting</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">RPM/TPM limits per provider, model, user, org unit. Prevent runaway costs.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-top: 4px solid #ED1C24;">
        <p style="font-size: 13px; color: #ED1C24; margin: 0; font-weight: 600;">Data Isolation</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Tenant isolation, local model support ensures data never leaves your infrastructure.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-top: 4px solid #0079C1;">
        <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Compliance Ready</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Built for SOC 2, HIPAA, GDPR via Azure/Bedrock provider options.</p>
      </div>
    </div>'''))

# Slide 31: Use Cases - Section Divider
slides.append((31, "Use Cases", '''
    <div class="col center" style="height: 100%;">
      <p style="font-size: 36px; color: #0079C1; margin: 0; font-weight: 700;">Section 9</p>
      <p style="font-size: 20px; color: #1A3A5C; margin: 16px 0 0 0;">Use Cases & Applications</p>
      <p style="font-size: 13px; color: #5A7A9C; margin: 12px 0 0 0;">Real-world applications across industries</p>
    </div>'''))

# Slide 32: Customer Service Use Case
slides.append((32, "Use Case: Customer Service", '''
    <div style="display: flex; gap: 20px; height: 100%;">
      <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-left: 4px solid #0079C1;">
          <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Challenge</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">High volume of customer inquiries, long wait times, inconsistent responses, expensive human agents.</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-left: 4px solid #ED1C24;">
          <p style="font-size: 13px; color: #ED1C24; margin: 0; font-weight: 600;">Solution</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">AI chatbot with RAG for policy lookup. Handles FAQs, account inquiries. Escalates complex issues to humans.</p>
        </div>
      </div>
      <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Key Features Used</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">RAG for knowledge, Agent tools, HITL escalation, Multi-channel deployment</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Results</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">70% query resolution, 24/7 availability, consistent quality, cost reduction</p>
        </div>
      </div>
    </div>'''))

# Slide 33: Document Analysis Use Case
slides.append((33, "Use Case: Document Analysis", '''
    <div style="display: flex; gap: 20px; height: 100%;">
      <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-left: 4px solid #0079C1;">
          <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Challenge</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Large volumes of contracts, reports, regulatory filings. Manual review is slow, expensive, error-prone.</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-left: 4px solid #ED1C24;">
          <p style="font-size: 13px; color: #ED1C24; margin: 0; font-weight: 600;">Solution</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">DAG workflow for document processing. Extract entities, summarize, classify, flag key clauses. Human review for exceptions.</p>
        </div>
      </div>
      <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Key Features Used</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">Workflow DAG, Agent tools for extraction, RAG for context, Transform nodes</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Results</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">90% faster review, improved accuracy, consistent classification, reduced costs</p>
        </div>
      </div>
    </div>'''))

# Slide 34: Risk & Compliance Use Case
slides.append((34, "Use Case: Risk & Compliance", '''
    <div style="display: flex; gap: 20px; height: 100%;">
      <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-left: 4px solid #0079C1;">
          <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Challenge</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">AML/KYC requirements, communication surveillance, regulatory reporting. Scale makes manual review impossible.</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-left: 4px solid #ED1C24;">
          <p style="font-size: 13px; color: #ED1C24; margin: 0; font-weight: 600;">Solution</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">AI-powered transaction monitoring, communication analysis. Automated flagging with human review for high-risk items.</p>
        </div>
      </div>
      <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Key Features Used</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">AI Org hierarchy, HITL controls, Audit trails, Local models for privacy</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Results</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">Comprehensive coverage, reduced false positives, regulatory compliance, audit-ready</p>
        </div>
      </div>
    </div>'''))

# Slide 35: Research & Reports Use Case
slides.append((35, "Use Case: Research & Reports", '''
    <div style="display: flex; gap: 20px; height: 100%;">
      <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-left: 4px solid #0079C1;">
          <p style="font-size: 13px; color: #0079C1; margin: 0; font-weight: 600;">Challenge</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Market research, competitor analysis, internal reports require gathering data from multiple sources and synthesizing insights.</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px; border-left: 4px solid #ED1C24;">
          <p style="font-size: 13px; color: #ED1C24; margin: 0; font-weight: 600;">Solution</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 8px 0 0 0; line-height: 1.4;">Multi-step DAG workflow with parallel data gathering, AI synthesis, and automated report generation.</p>
        </div>
      </div>
      <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Key Features Used</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">Workflow DAG, Parallel execution, Search tools, Agent synthesis</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 14px;">
          <p style="font-size: 12px; color: #1A3A5C; margin: 0; font-weight: 600;">Results</p>
          <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">Hours to minutes, comprehensive coverage, consistent format, scalable</p>
        </div>
      </div>
    </div>'''))

for num, title, content in slides:
    filename = f"slide{num:02d}.html"
    with open(filename, 'w') as f:
        f.write(create_slide(num, title, content))
    print(f"Created {filename}")

print("Part 3 slides created")
