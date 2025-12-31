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
    # 29 - Swarms Section
    (29, 'section', 'Agent Swarms', 'Dynamic multi-agent coordination'),

    # 30 - What is a Swarm
    (30, 'content', 'What is an Agent Swarm?', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 10px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Definition</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0; line-height: 1.4;">An Agent Swarm is a collection of autonomous agents that collaborate dynamically on tasks. Unlike fixed workflows, swarms use event-driven coordination where agents discover and respond to tasks based on capabilities.</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Key Characteristics</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• <b>Event-Driven</b>: Agents react to events, not predefined sequences</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Self-Organizing</b>: Agents claim tasks based on capabilities</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Emergent Behavior</b>: Complex outcomes from simple rules</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Scalable</b>: Add/remove agents without restructuring</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Fault Tolerant</b>: Other agents compensate for failures</p>
      </div>
      <div style="background: #FFE8E8; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Use Cases</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">Research teams • Customer service pools • Data processing clusters • Competitive analysis</p>
      </div>
    </div>'''),

    # 31 - Swarm UI and Messaging
    (31, 'content', 'Swarm Creation & Messaging', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Creating Swarms via UI (Swarms → New)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">1. <b>Define Swarm</b>: Name, description, coordination strategy</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">2. <b>Add Agents</b>: Select agents to include in swarm pool</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">3. <b>Configure Routing</b>: Capability matching, priority rules</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">4. <b>Set Coordination</b>: Choreography (LLM) or Orchestration (rules)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">5. <b>Monitor</b>: Real-time dashboard of agent activity</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Messaging Integration</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• <b>Kafka</b>: High-throughput event streaming</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>RabbitMQ</b>: Message queuing with routing</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>ActiveMQ</b>: Enterprise messaging</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Built-in pub/sub</b>: In-memory for development</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Backpressure</b>: Automatic load balancing</p>
      </div>
    </div>'''),

    # 32 - AI Org Section
    (32, 'section', 'AI Organizations', 'Patent-pending hierarchical governance'),

    # 33 - What is AI Org
    (33, 'content', 'What is an AI Organization?', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 10px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Definition (Patent Pending)</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0; line-height: 1.4;">An AI Organization is a digital twin of a corporate hierarchy where each position is occupied by an AI agent. Tasks flow down the org chart (delegation) and responses flow up (aggregation), mirroring how real organizations work.</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Problems Solved</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• <b>Accountability</b>: Clear ownership for AI decisions</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Delegation</b>: Complex tasks decomposed naturally</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Human Oversight</b>: Every AI has a human mirror</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Compliance</b>: Matches regulatory org structures</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Scalability</b>: Grow AI teams like human teams</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #0079C1; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Key Features</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• Task delegation down • Response aggregation up • Human mirrors • Configurable autonomy • HITL at any level</p>
      </div>
    </div>'''),

    # 34 - AI Org UI Creation
    (34, 'content', 'Creating AI Organizations via UI', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Organization Designer (AI Orgs → New)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">1. <b>Create Org</b>: Name, description, industry template</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">2. <b>Add Positions</b>: Define roles (CEO, VP, Manager, Analyst...)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">3. <b>Build Hierarchy</b>: Drag to set reporting relationships</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">4. <b>Assign Agents</b>: Map agents to each position</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">5. <b>Set Human Mirrors</b>: Assign human overseers</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">6. <b>Configure Autonomy</b>: Per-position autonomy levels</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">7. <b>Define Workflows</b>: Attach workflows to positions</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">UI Management Features</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• Visual org chart with drag-drop editing</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Real-time task flow visualization</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Pending approvals dashboard</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• Position performance metrics</p>
      </div>
    </div>'''),

    # 35 - AI Org JSON
    (35, 'content', 'AI Organization: JSON Definition', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #1A3A5C; padding: 8px; border-radius: 4px;">
        <p style="font-size: 6px; color: #7FDBFF; margin: 0; font-family: monospace; white-space: pre; line-height: 1.2;">{
  "name": "Research Division",
  "positions": [
    {"id": "director", "title": "Research Director", "agent": "strategic_agent",
     "human_mirror": "john.smith@company.com", "autonomy": "supervised"},
    {"id": "lead1", "title": "Team Lead - AI", "agent": "ai_specialist",
     "reports_to": "director", "autonomy": "semi_autonomous"},
    {"id": "analyst1", "title": "Research Analyst", "agent": "research_agent",
     "reports_to": "lead1", "autonomy": "autonomous"}
  ],
  "delegation_rules": {
    "strategy_tasks": ["director"],
    "analysis_tasks": ["analyst1", "analyst2"]
  },
  "hitl": {"require_approval": ["budget_decisions", "external_comms"]}
}</p>
      </div>
      <div style="background: #FFF; padding: 6px; border-radius: 4px;">
        <p style="font-size: 9px; color: #0079C1; margin: 0; font-weight: 600;">Benefits</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 2px 0 0 0;">• Mirrors real org structure • Clear accountability • Scalable AI teams • Regulatory compliant • Human oversight built-in</p>
      </div>
    </div>'''),

    # 36 - RBAC Section
    (36, 'section', 'RBAC & Security', 'Enterprise-grade access control'),

    # 37 - RBAC Details
    (37, 'content', 'Role-Based Access Control', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">RBAC Model</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• <b>Users</b>: Individual accounts with authentication</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Roles</b>: Admin, Developer, Analyst, Viewer (+ custom)</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Permissions</b>: Granular actions per resource type</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Model Access</b>: Control which models each role can use</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Usage Limits</b>: RPM/TPM quotas per role</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">Security Features</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• <b>API Keys</b>: Scoped keys with expiration</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Audit Logs</b>: Every action recorded with user/timestamp</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Rate Limiting</b>: Prevent abuse and cost overruns</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Data Isolation</b>: Multi-tenant data separation</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>SSO</b>: SAML/OIDC integration ready</p>
      </div>
    </div>'''),

    # 38 - Notifications Section
    (38, 'section', 'Notifications Integration', 'Multi-channel enterprise alerts'),

    # 39 - Notifications Details
    (39, 'content', 'Notifications System', '''    <div class="col gap-sm" style="height: 100%;">
      <div style="background: #FFF; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #0079C1; margin: 0; font-weight: 600;">Supported Channels</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• <b>Slack</b>: Bot integration with interactive buttons</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Microsoft Teams</b>: Webhook and bot support</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Email</b>: SMTP with templates</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Webhooks</b>: POST to any endpoint</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>SMS</b>: Twilio integration (optional)</p>
      </div>
      <div style="background: #FFF; border-left: 3px solid #ED1C24; padding: 8px; border-radius: 4px;">
        <p style="font-size: 10px; color: #ED1C24; margin: 0; font-weight: 600;">AI Org Integration</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 3px 0 0 0;">• <b>Human Mirror Alerts</b>: Notify when AI needs approval</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Escalation</b>: Auto-escalate if no response in timeout</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Summary Reports</b>: Daily/weekly AI activity digests</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Interactive Buttons</b>: Approve/Reject from notification</p>
        <p style="font-size: 8px; color: #5A7A9C; margin: 1px 0 0 0;">• <b>Audit Trail</b>: Link to detailed execution logs</p>
      </div>
    </div>'''),

    # 40 - Use Cases Section
    (40, 'section', 'Use Cases', 'Real-world applications with examples'),
]

for num, stype, title, content in slides:
    filename = f"slide{num:02d}.html"
    if stype == 'section':
        html = section_slide(num, title, content)
    else:
        html = content_slide(num, title, content)
    with open(filename, 'w') as f:
        f.write(html)

print(f"Created slides 29-40")
