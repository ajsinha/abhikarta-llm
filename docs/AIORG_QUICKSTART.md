# AI Org Quickstart Guide

**Version:** 1.4.6  
**Last Updated:** December 2025

---

## Introduction

AI Org (AI Organizations) is a revolutionary feature that lets you create **AI-powered digital twins of organizational structures**. Each position in your org chart becomes an AI agent that can receive tasks, delegate to subordinates, and aggregate results—just like a real organization.

### Key Concepts

| Concept | Description |
|---------|-------------|
| **AI Org** | An AI-powered organizational hierarchy |
| **Node** | A position/role in the org (e.g., CEO, PM, Analyst) |
| **Human Mirror** | The human employee represented by a node |
| **HITL** | Human-in-the-Loop - allows human intervention |
| **Task** | Work item that flows through the organization |
| **Delegation** | Assigning subtasks to subordinates |
| **Aggregation** | Synthesizing responses from subordinates |

---

## Quick Start Example: Project Analysis Team

This example creates an AI org that analyzes project proposals.

### Step 1: Create the Organization

1. Navigate to **Playground → AI Organizations → All AI Orgs**
2. Click **Create AI Org**
3. Fill in:
   - **Name:** "Project Analysis Team"
   - **Description:** "Analyzes project proposals and provides feasibility assessments"
   - **CEO Role Name:** "Chief Analysis Officer"
   - **CEO Email:** your-email@company.com

4. Click **Create Organization**

### Step 2: Design the Org Structure

You'll be taken to the Visual Designer. Create this hierarchy:

```
                    Chief Analysis Officer (CEO)
                              │
           ┌──────────────────┼──────────────────┐
           │                  │                  │
    Technical PM         Business PM          Finance Lead
           │                  │                  │
     ┌─────┴─────┐      ┌─────┴─────┐           │
     │           │      │           │           │
Tech Analyst  Dev Lead  Market      Business    Financial
                       Analyst     Analyst     Analyst
```

**To add nodes:**
1. Click **Add Node**
2. Select the parent node
3. Enter role name and type
4. Configure human mirror email
5. Enable HITL if needed

### Step 3: Configure Nodes

For each node, configure:

**Role Details:**
- Role Name: e.g., "Technical PM"
- Role Type: Manager (for PMs), Analyst (for leaf nodes)
- Description: What this role does

**Human Mirror:**
- Name: Real person's name
- Email: Their email for notifications
- Teams/Slack ID: For instant messaging

**HITL Settings:**
- Enable HITL: ✓ (for critical roles)
- Approval Required: ✓ (to review before sending)
- Timeout: 24 hours

### Step 4: Activate the Organization

1. Click **Save Changes** in the designer
2. Go to org detail page
3. Click **Activate**

### Step 5: Submit Your First Task

1. Click **Submit Task**
2. Fill in:

```
Title: Analyze Mobile Banking App Proposal

Description:
Please analyze the attached project proposal for a new mobile banking application.

Focus areas:
1. Technical Feasibility - Architecture, scalability, security
2. Market Analysis - Competitive landscape, target users, market size
3. Financial Viability - Cost estimates, ROI projections, resource requirements

Please provide a comprehensive assessment with recommendations.

Priority: High
```

3. Click **Submit Task**

### Step 6: Watch the Organization Work

**What happens automatically:**

1. **CEO Receives Task** → Analyzes and creates delegation plan
2. **CEO Delegates** → Creates subtasks for Technical PM, Business PM, Finance Lead
3. **PMs Delegate** → Create subtasks for their analysts
4. **Analysts Work** → Each analyst researches their assigned area
5. **Analysts Report** → Send findings to their PM
6. **PMs Aggregate** → Synthesize analyst findings, send to CEO
7. **CEO Aggregates** → Creates final consolidated report
8. **Notification Sent** → Final report emailed to CEO's human mirror

**Monitor Progress:**
- Go to **Monitor** page to see real-time activity
- Check **Tasks** page to see all tasks and their status
- Check **HITL Dashboard** if you're a human mirror

### Step 7: Review HITL Requests (if enabled)

If HITL is enabled:

1. You'll receive email/Teams notification
2. Go to **HITL Dashboard**
3. Review the AI's proposed response
4. Choose:
   - **Approve** - Accept AI's response
   - **Override** - Provide your own response
   - **Reject** - Request re-analysis

---

## Real-World Use Cases

### 1. Research Organization

**Structure:**
```
Chief Research Officer
├── Research Lead (Healthcare)
│   ├── Data Analyst 1
│   └── Data Analyst 2
├── Research Lead (Technology)
│   ├── Data Analyst 3
│   └── Data Analyst 4
└── Research Lead (Finance)
    ├── Data Analyst 5
    └── Data Analyst 6
```

**Use Case:** Market research, competitive analysis, due diligence

### 2. Compliance Review Team

**Structure:**
```
Chief Compliance Officer
├── Regulatory Auditor
│   ├── Policy Analyst 1
│   └── Policy Analyst 2
├── Risk Auditor
│   └── Risk Analyst
└── Documentation Auditor
    └── Documentation Analyst
```

**Use Case:** Regulatory compliance reviews, policy gap analysis

### 3. Software Development Planning

**Structure:**
```
VP of Engineering
├── Technical Architect
│   ├── Backend Specialist
│   └── Frontend Specialist
├── QA Lead
│   └── QA Analyst
└── DevOps Lead
    └── Infrastructure Analyst
```

**Use Case:** Technical feasibility, architecture planning, sprint planning

---

## JSON Import/Export

### Export

1. Go to org detail page
2. Click **Export JSON**
3. Save the file

### Import

1. Go to AI Orgs list
2. Click **Import JSON**
3. Upload your file

### Sample JSON Structure

```json
{
  "org": {
    "name": "Project Analysis Team",
    "description": "Analyzes project proposals"
  },
  "nodes": [
    {
      "node_id": "ceo-001",
      "role_name": "Chief Analysis Officer",
      "role_type": "executive",
      "parent_node_id": null,
      "human_name": "John Smith",
      "human_email": "john@company.com",
      "hitl_enabled": true,
      "notification_channels": ["email", "teams"],
      "position_x": 400,
      "position_y": 50
    },
    {
      "node_id": "pm-tech-001",
      "role_name": "Technical PM",
      "role_type": "manager",
      "parent_node_id": "ceo-001",
      "human_name": "Alice Johnson",
      "human_email": "alice@company.com",
      "hitl_enabled": false,
      "position_x": 200,
      "position_y": 170
    }
  ],
  "version": "1.4.6"
}
```

---

## API Integration

### Submit Task via API

```bash
curl -X POST "http://localhost:5000/api/aiorg/{org_id}/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Analyze Q4 Performance",
    "description": "Provide comprehensive analysis...",
    "priority": "high",
    "input_data": {
      "quarter": "Q4",
      "year": 2025,
      "focus_areas": ["revenue", "costs", "growth"]
    }
  }'
```

### Submit via Webhook

Configure a webhook to trigger tasks:

1. Go to **Admin → Webhooks**
2. Create webhook with target: `/api/aiorg/{org_id}/tasks`
3. External systems can now trigger org tasks

---

## Best Practices

### Design Tips

1. **Keep it Simple** - Start with 3-5 nodes, expand as needed
2. **Clear Roles** - Each node should have a distinct purpose
3. **Appropriate Depth** - 2-4 levels is usually optimal
4. **Balance Width** - Don't overload any single manager

### HITL Guidelines

1. **Enable for Executives** - Critical decisions need human review
2. **Configure Timeouts** - 24 hours is usually appropriate
3. **Set Auto-Proceed** - Decide if tasks should continue on timeout
4. **Review Patterns** - If AI is consistently wrong, adjust prompts

### Notification Setup

1. **Configure Channels** - Email + Teams/Slack for redundancy
2. **Set Triggers** - Task completion, HITL required, errors
3. **Test First** - Verify notifications work before going live

---

## Troubleshooting

### Task Stuck in "Delegated" State

- Check if all subordinates have responded
- Check for HITL items pending review
- Review Monitor page for errors

### HITL Not Receiving Notifications

- Verify human mirror email is correct
- Check notification channels are configured
- Confirm SMTP/Teams/Slack integration is working

### AI Responses Not Matching Expectations

- Review node descriptions for clarity
- Adjust agent prompts if configured
- Enable HITL to guide AI learning

---

## What's Next?

- **Templates** - Pre-built org structures (Coming Soon)
- **Analytics** - Performance metrics and insights
- **Integration** - Direct JIRA/Confluence integration
- **Training** - Fine-tune AI per role

---

*For more information, see the [Help Documentation](/help) or contact support.*
