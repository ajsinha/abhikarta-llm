# Notification Module - Quick Start Guide

## Overview

The Abhikarta-LLM Notification Module (v1.4.0) provides enterprise-grade notification capabilities for agents, workflows, and swarms. Send notifications to Slack, Microsoft Teams, and receive external webhooks.

---

## 1. Quick Start

### 1.1 Send a Slack Notification

```python
from abhikarta.notification import (
    NotificationManager,
    NotificationMessage,
    NotificationLevel,
    SlackConfig
)

# Configure Slack
manager = NotificationManager()
manager.configure_slack(SlackConfig(
    bot_token="xoxb-your-bot-token",
    default_channel="#notifications"
))

# Send notification
import asyncio

async def send_alert():
    result = await manager.send_to_slack(
        NotificationMessage(
            title="Agent Task Complete",
            body="Data analysis finished successfully!",
            level=NotificationLevel.SUCCESS,
            fields={
                "Records": "1,234",
                "Duration": "2m 15s"
            }
        )
    )
    print(f"Sent: {result.success}")

asyncio.run(send_alert())
```

### 1.2 Send a Teams Notification

```python
from abhikarta.notification import TeamsConfig

# Configure Teams
manager.configure_teams(TeamsConfig(
    webhook_url="https://outlook.office.com/webhook/your-webhook-url"
))

# Send notification
async def send_teams_alert():
    result = await manager.send_to_teams(
        NotificationMessage(
            title="Workflow Failed",
            body="The ETL workflow encountered an error",
            level=NotificationLevel.ERROR,
            source="workflow-123",
            source_type="workflow"
        )
    )
    print(f"Sent: {result.success}")

asyncio.run(send_teams_alert())
```

### 1.3 Broadcast to All Channels

```python
async def broadcast_alert():
    results = await manager.broadcast(
        NotificationMessage(
            title="System Maintenance",
            body="Scheduled maintenance in 30 minutes",
            level=NotificationLevel.WARNING
        )
    )
    for result in results:
        print(f"{result.channel.value}: {result.success}")

asyncio.run(broadcast_alert())
```

---

## 2. Webhook Receiver

### 2.1 Register a Webhook Endpoint

```python
from abhikarta.notification import WebhookReceiver, AuthMethod

receiver = WebhookReceiver()

# Register endpoint for GitHub webhooks
endpoint = receiver.register_endpoint(
    path="/webhooks/github",
    name="GitHub Webhook",
    auth_method=AuthMethod.HMAC,
    secret="your-github-webhook-secret",
    target_type="swarm",
    target_id="code-review-swarm"
)

print(f"Registered: {endpoint.path}")
```

### 2.2 Process Incoming Webhook (Flask Example)

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhooks/<path:webhook_path>', methods=['POST'])
async def handle_webhook(webhook_path):
    result = await receiver.process_webhook(
        path=f"/webhooks/{webhook_path}",
        method=request.method,
        headers=dict(request.headers),
        body=request.data,
        query_params=dict(request.args),
        source_ip=request.remote_addr
    )
    
    return {
        "success": result.success,
        "event_id": result.event_id,
        "message": result.message
    }, result.status_code
```

### 2.3 Custom Event Handler

```python
from abhikarta.notification import WebhookEvent

async def handle_github_event(event: WebhookEvent):
    """Custom handler for GitHub webhook events."""
    if event.event_type == "push":
        print(f"Push to {event.payload.get('ref')}")
        # Trigger CI/CD workflow
        return {"action": "triggered_ci"}
    
    elif event.event_type == "pull_request":
        action = event.payload.get("action")
        if action == "opened":
            # Trigger code review swarm
            return {"action": "triggered_review"}
    
    return {"action": "ignored"}

# Register handler
receiver.set_handler("/webhooks/github", handle_github_event)
```

---

## 3. Configuration

### 3.1 Environment Variables

```bash
# Slack
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
export SLACK_APP_TOKEN="xapp-your-app-token"
export SLACK_DEFAULT_CHANNEL="#notifications"

# Microsoft Teams
export TEAMS_WEBHOOK_URL="https://outlook.office.com/webhook/..."

# Webhook Security
export WEBHOOK_SECRET_KEY="your-secret-key"
```

### 3.2 JSON Configuration

```json
{
  "notifications": {
    "enabled": true,
    "default_channels": ["slack"],
    
    "channels": {
      "slack": {
        "enabled": true,
        "bot_token": "${SLACK_BOT_TOKEN}",
        "default_channel": "#abhikarta-alerts",
        "rate_limit": 50
      },
      "teams": {
        "enabled": true,
        "webhook_url": "${TEAMS_WEBHOOK_URL}",
        "rate_limit": 30
      }
    },
    
    "webhooks": {
      "enabled": true,
      "default_auth": "hmac",
      "rate_limit": 100
    }
  }
}
```

### 3.3 Load from Configuration

```python
import json

with open('config/notifications.json') as f:
    config = json.load(f)

manager.configure_from_dict(config['notifications']['channels'])
```

---

## 4. Agent/Workflow Integration

### 4.1 Send from Agent

```python
from abhikarta.notification import NotificationMessage, NotificationLevel

class MyAgent:
    def __init__(self, notification_manager):
        self.nm = notification_manager
    
    async def on_task_complete(self, result):
        await self.nm.send(
            channels=["slack", "teams"],
            message=NotificationMessage(
                title=f"Agent: {self.name}",
                body=f"Task completed: {result.summary}",
                level=NotificationLevel.SUCCESS,
                source=self.agent_id,
                source_type="agent",
                fields={"Output": result.output[:100]}
            )
        )
```

### 4.2 Workflow Notification Node

```json
{
  "nodes": [
    {
      "node_id": "notify_on_complete",
      "node_type": "notification",
      "config": {
        "channels": ["slack"],
        "level": "success",
        "title": "ETL Complete",
        "body": "Processed {{ context.record_count }} records",
        "fields": {
          "duration": "{{ context.duration }}",
          "status": "{{ context.status }}"
        }
      }
    }
  ]
}
```

### 4.3 Swarm Broadcast

```python
class SwarmMasterActor:
    async def notify_stakeholders(self, event):
        await self.notification_manager.send(
            channels=["slack", "teams"],
            message=NotificationMessage(
                title=f"Swarm: {self.swarm.name}",
                body=f"Decision made: {event.decision}",
                level=NotificationLevel.INFO,
                source=self.swarm.swarm_id,
                source_type="swarm",
                fields={
                    "Target Agent": event.target_agent,
                    "Reasoning": event.reasoning[:200]
                }
            )
        )
```

---

## 5. Testing

### 5.1 Test Channel Configuration

```python
async def test_channels():
    results = await manager.test_all_channels()
    for channel, result in results.items():
        status = "✓" if result["success"] else "✗"
        print(f"{status} {channel}: {result.get('error', 'OK')}")

asyncio.run(test_channels())
```

### 5.2 View Notification History

```python
# Get recent notifications
history = manager.get_notification_history(
    limit=50,
    channel="slack",
    status="sent"
)

for notif in history:
    print(f"{notif['created_at']}: {notif['title']} - {notif['status']}")
```

### 5.3 View Webhook Events

```python
# Get webhook event history
events = receiver.get_event_history(
    endpoint_path="/webhooks/github",
    limit=100,
    verified_only=True
)

for event in events:
    print(f"{event['received_at']}: {event['event_type']} - {'✓' if event['verified'] else '✗'}")
```

---

## 6. Slack Setup Guide

### Step 1: Create Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Enter app name: "Abhikarta Notifications"
4. Select your workspace

### Step 2: Configure OAuth Scopes

Go to "OAuth & Permissions" and add these Bot Token Scopes:
- `chat:write` - Send messages
- `chat:write.public` - Send to public channels
- `users:read` - For DM support (optional)

### Step 3: Install to Workspace

1. Click "Install to Workspace"
2. Authorize the app
3. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

### Step 4: Invite Bot to Channel

In Slack:
1. Go to your target channel
2. Type `/invite @Abhikarta Notifications`

---

## 7. Teams Setup Guide

### Step 1: Create Incoming Webhook

1. In Teams, go to the target channel
2. Click "..." → "Connectors"
3. Find "Incoming Webhook" → "Configure"
4. Name it: "Abhikarta Notifications"
5. Optionally upload an icon
6. Click "Create"
7. Copy the webhook URL

### Step 2: Configure in Abhikarta

```python
manager.configure_teams(TeamsConfig(
    webhook_url="https://outlook.office.com/webhook/your-copied-url"
))
```

---

## 8. Troubleshooting

### Slack: "channel_not_found"
- Ensure the bot is invited to the channel
- Use channel ID instead of name if private

### Slack: "invalid_auth"
- Verify bot token starts with `xoxb-`
- Check token hasn't been revoked

### Teams: "HTTP 400"
- Verify webhook URL is complete and correct
- Check card format matches schema

### Webhook: "401 Unauthorized"
- Verify HMAC secret matches sender's secret
- Check signature header name

### Rate Limiting
- Reduce rate_limit in config
- Implement queuing for high-volume scenarios

---

## 9. Best Practices

1. **Use Appropriate Levels**: Match notification level to urgency
2. **Include Context**: Add relevant fields for debugging
3. **Rate Limit**: Don't spam channels with notifications
4. **Quiet Hours**: Respect user notification preferences
5. **Error Handling**: Always check result.success
6. **Audit Trail**: Use correlation_id for tracking
7. **Test First**: Use test_channel() before production
8. **Secure Webhooks**: Always use HMAC or stronger auth

---

*Version 1.4.0 - Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.*
