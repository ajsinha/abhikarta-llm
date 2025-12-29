# Notification Module Architecture

## Version 1.4.0 - Enterprise Notification System

### Overview

The Abhikarta-LLM Notification Module provides a unified interface for sending notifications across multiple channels (Slack, Microsoft Teams, Email, SMS) and receiving external events via webhooks. This enables agents, workflows, and swarms to communicate with external systems and stakeholders in real-time.

---

## 1. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ABHIKARTA NOTIFICATION MODULE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    NOTIFICATION MANAGER                              │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │   │
│  │  │   Config    │  │   Queue     │  │   Logger    │                  │   │
│  │  │   Loader    │  │   Manager   │  │   (Audit)   │                  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                  │   │
│  └───────────────────────────┬─────────────────────────────────────────┘   │
│                              │                                              │
│  ┌───────────────────────────┼─────────────────────────────────────────┐   │
│  │                    PROVIDER ADAPTERS                                 │   │
│  │                           │                                          │   │
│  │  ┌─────────────┐  ┌───────┴─────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │   Slack     │  │   Teams     │  │   Email     │  │   SMS       │ │   │
│  │  │   Adapter   │  │   Adapter   │  │   Adapter   │  │   Adapter   │ │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘ │   │
│  │         │                │                │                │         │   │
│  └─────────┼────────────────┼────────────────┼────────────────┼─────────┘   │
│            │                │                │                │             │
│            ▼                ▼                ▼                ▼             │
│       ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐          │
│       │ Slack   │     │ Teams   │     │ SMTP    │     │ Twilio  │          │
│       │ API     │     │ Webhook │     │ Server  │     │ API     │          │
│       └─────────┘     └─────────┘     └─────────┘     └─────────┘          │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                        WEBHOOK RECEIVER                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │   │
│  │  │  Endpoint   │  │  Validator  │  │  Dispatcher │                  │   │
│  │  │  Registry   │  │  & Auth     │  │  (Events)   │                  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Components

### 2.1 NotificationManager

The central orchestrator for all notification operations.

```python
class NotificationManager:
    """
    Central notification manager that routes messages to appropriate channels.
    
    Features:
    - Multi-channel support (Slack, Teams, Email, SMS)
    - Priority-based routing
    - Retry with exponential backoff
    - Rate limiting per channel
    - Audit logging
    """
    
    async def send(
        self,
        channels: List[str],          # ['slack', 'teams', 'email']
        message: NotificationMessage,
        priority: Priority = Priority.NORMAL,
        retry_count: int = 3
    ) -> NotificationResult
    
    async def send_to_user(
        self,
        user_id: str,
        message: NotificationMessage
    ) -> NotificationResult
    
    async def broadcast(
        self,
        channel: str,
        message: NotificationMessage
    ) -> NotificationResult
```

### 2.2 Provider Adapters

Each notification channel has a dedicated adapter implementing a common interface.

```python
class NotificationAdapter(ABC):
    """Base class for all notification adapters."""
    
    @abstractmethod
    async def send(self, message: NotificationMessage) -> bool:
        """Send a notification through this channel."""
        pass
    
    @abstractmethod
    async def validate_config(self) -> bool:
        """Validate the adapter configuration."""
        pass
    
    @abstractmethod
    def get_rate_limit(self) -> RateLimit:
        """Get rate limit for this channel."""
        pass
```

#### 2.2.1 SlackAdapter

```python
class SlackAdapter(NotificationAdapter):
    """
    Slack integration using Web API.
    
    Supports:
    - Channel messages (#channel)
    - Direct messages (@user)
    - Rich formatting (Blocks API)
    - File attachments
    - Interactive messages (buttons, menus)
    - Thread replies
    """
    
    def __init__(self, config: SlackConfig):
        self.bot_token = config.bot_token
        self.app_token = config.app_token  # For Socket Mode
        self.default_channel = config.default_channel
        self.client = WebClient(token=self.bot_token)
```

#### 2.2.2 TeamsAdapter

```python
class TeamsAdapter(NotificationAdapter):
    """
    Microsoft Teams integration using Incoming Webhooks.
    
    Supports:
    - Channel messages
    - Adaptive Cards
    - @mentions
    - Action buttons
    - Connector cards
    """
    
    def __init__(self, config: TeamsConfig):
        self.webhook_url = config.webhook_url
        self.tenant_id = config.tenant_id  # Optional: for Graph API
```

### 2.3 WebhookReceiver

Receives and processes incoming webhooks from external systems.

```python
class WebhookReceiver:
    """
    Receives and validates incoming webhooks.
    
    Features:
    - Endpoint registration
    - Signature verification (HMAC, JWT)
    - Payload validation
    - Event dispatching to agents/swarms
    - Replay protection
    """
    
    def register_endpoint(
        self,
        path: str,
        handler: Callable,
        auth_method: AuthMethod = AuthMethod.HMAC,
        secret: str = None
    ) -> WebhookEndpoint
    
    async def process_webhook(
        self,
        endpoint_id: str,
        request: Request
    ) -> WebhookResponse
```

---

## 3. Data Models

### 3.1 NotificationMessage

```python
@dataclass
class NotificationMessage:
    """Unified notification message format."""
    
    title: str
    body: str
    level: NotificationLevel = NotificationLevel.INFO  # INFO, WARNING, ERROR, SUCCESS
    
    # Optional rich content
    fields: Optional[Dict[str, str]] = None  # Key-value pairs
    actions: Optional[List[Action]] = None    # Buttons/links
    attachments: Optional[List[Attachment]] = None
    
    # Metadata
    source: str = "system"                    # agent_id, workflow_id, swarm_id
    source_type: str = "system"               # agent, workflow, swarm
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None      # For tracking
    
    # Channel-specific overrides
    slack_blocks: Optional[List[Dict]] = None
    teams_card: Optional[Dict] = None
```

### 3.2 NotificationLevel

```python
class NotificationLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
```

### 3.3 WebhookEvent

```python
@dataclass
class WebhookEvent:
    """Represents an incoming webhook event."""
    
    event_id: str
    endpoint_id: str
    event_type: str
    payload: Dict[str, Any]
    headers: Dict[str, str]
    timestamp: datetime
    source_ip: str
    verified: bool
```

---

## 4. Database Schema

### 4.1 Notification Channels Table

```sql
CREATE TABLE notification_channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id TEXT UNIQUE NOT NULL,
    channel_type TEXT NOT NULL,           -- 'slack', 'teams', 'email', 'sms'
    name TEXT NOT NULL,
    config TEXT NOT NULL,                 -- JSON encrypted config
    is_active INTEGER DEFAULT 1,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 Notification Log Table

```sql
CREATE TABLE notification_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notification_id TEXT UNIQUE NOT NULL,
    channel_id TEXT NOT NULL,
    channel_type TEXT NOT NULL,
    recipient TEXT,
    title TEXT,
    body TEXT,
    level TEXT DEFAULT 'info',
    status TEXT DEFAULT 'pending',        -- pending, sent, failed, delivered
    error_message TEXT,
    source TEXT,                          -- agent_id, workflow_id, etc.
    source_type TEXT,                     -- 'agent', 'workflow', 'swarm'
    correlation_id TEXT,
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (channel_id) REFERENCES notification_channels(channel_id)
);
```

### 4.3 Webhook Endpoints Table

```sql
CREATE TABLE webhook_endpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    endpoint_id TEXT UNIQUE NOT NULL,
    path TEXT UNIQUE NOT NULL,            -- '/webhooks/github'
    name TEXT NOT NULL,
    description TEXT,
    auth_method TEXT DEFAULT 'hmac',      -- 'hmac', 'jwt', 'api_key', 'none'
    secret_hash TEXT,                     -- Hashed secret for HMAC
    target_type TEXT,                     -- 'agent', 'workflow', 'swarm'
    target_id TEXT,                       -- ID of agent/workflow/swarm to trigger
    is_active INTEGER DEFAULT 1,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.4 Webhook Events Log

```sql
CREATE TABLE webhook_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT UNIQUE NOT NULL,
    endpoint_id TEXT NOT NULL,
    event_type TEXT,
    payload TEXT,                         -- JSON payload
    headers TEXT,                         -- JSON headers
    source_ip TEXT,
    verified INTEGER DEFAULT 0,
    processed INTEGER DEFAULT 0,
    process_result TEXT,
    error_message TEXT,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    
    FOREIGN KEY (endpoint_id) REFERENCES webhook_endpoints(endpoint_id)
);
```

### 4.5 User Notification Preferences

```sql
CREATE TABLE user_notification_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    channel_type TEXT NOT NULL,           -- 'slack', 'teams', 'email'
    channel_address TEXT,                 -- email, slack user ID, etc.
    enabled INTEGER DEFAULT 1,
    min_level TEXT DEFAULT 'info',        -- Minimum notification level
    quiet_hours_start TEXT,               -- '22:00'
    quiet_hours_end TEXT,                 -- '08:00'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, channel_type)
);
```

---

## 5. Integration Points

### 5.1 Agent Integration

Agents can send notifications through the notification manager:

```python
class AgentNotificationMixin:
    """Mixin to add notification capabilities to agents."""
    
    async def notify(
        self,
        message: str,
        level: NotificationLevel = NotificationLevel.INFO,
        channels: List[str] = None
    ):
        """Send notification from this agent."""
        notification = NotificationMessage(
            title=f"Agent: {self.name}",
            body=message,
            level=level,
            source=self.agent_id,
            source_type="agent"
        )
        await self.notification_manager.send(
            channels=channels or self.default_channels,
            message=notification
        )
```

### 5.2 Workflow Integration

Workflow nodes can include notification steps:

```yaml
# Notification node in workflow DAG
- node_id: notify_success
  node_type: notification
  config:
    channels: ["slack", "teams"]
    level: success
    title: "Workflow Complete"
    body: "Data processing completed successfully"
    fields:
      records_processed: "{{ context.record_count }}"
      duration: "{{ context.duration }}"
```

### 5.3 Swarm Integration

Master Actor can broadcast notifications to external channels:

```python
class MasterActor:
    async def notify_stakeholders(
        self,
        event: SwarmEvent,
        channels: List[str]
    ):
        """Notify external stakeholders about swarm events."""
        message = NotificationMessage(
            title=f"Swarm: {self.swarm.name}",
            body=event.summary,
            level=self._event_to_level(event),
            source=self.swarm.swarm_id,
            source_type="swarm"
        )
        await self.notification_manager.send(channels, message)
```

---

## 6. Configuration

### 6.1 Environment Variables

```bash
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_DEFAULT_CHANNEL=#notifications
SLACK_SIGNING_SECRET=your-signing-secret

# Microsoft Teams Configuration
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...
TEAMS_TENANT_ID=your-tenant-id        # Optional for Graph API

# Email Configuration (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_NAME=Abhikarta Notifications

# SMS Configuration (Twilio)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_FROM_NUMBER=+1234567890

# Webhook Security
WEBHOOK_SECRET_KEY=your-secret-key
WEBHOOK_RATE_LIMIT=100/minute
```

### 6.2 YAML Configuration

```yaml
# config/notifications.yaml
notifications:
  enabled: true
  default_channels:
    - slack
  
  channels:
    slack:
      enabled: true
      bot_token: ${SLACK_BOT_TOKEN}
      default_channel: "#abhikarta-notifications"
      rate_limit: 50/minute
      
    teams:
      enabled: true
      webhook_url: ${TEAMS_WEBHOOK_URL}
      rate_limit: 30/minute
      
    email:
      enabled: true
      smtp_host: ${SMTP_HOST}
      smtp_port: ${SMTP_PORT}
      from_address: notifications@abhikarta.ai
      
  webhooks:
    enabled: true
    base_path: /api/webhooks
    default_auth: hmac
    rate_limit: 100/minute
```

---

## 7. Security Considerations

### 7.1 Credential Management

- All API tokens stored encrypted in database
- Environment variables for sensitive data
- No credentials in logs or error messages
- Rotation support for tokens

### 7.2 Webhook Security

- HMAC signature verification
- Timestamp validation (prevent replay)
- IP allowlisting (optional)
- Rate limiting per endpoint
- Payload size limits

### 7.3 Audit Logging

- All notifications logged with full context
- Webhook events logged for debugging
- PII masking in logs
- Retention policies

---

## 8. API Endpoints

### 8.1 Notification Management

```
POST   /api/notifications/send              - Send notification
GET    /api/notifications/channels          - List configured channels
POST   /api/notifications/channels          - Create channel config
PUT    /api/notifications/channels/{id}     - Update channel config
DELETE /api/notifications/channels/{id}     - Delete channel config
GET    /api/notifications/logs              - Get notification history
POST   /api/notifications/test/{channel}    - Test channel configuration
```

### 8.2 Webhook Management

```
GET    /api/webhooks/endpoints              - List webhook endpoints
POST   /api/webhooks/endpoints              - Create endpoint
PUT    /api/webhooks/endpoints/{id}         - Update endpoint
DELETE /api/webhooks/endpoints/{id}         - Delete endpoint
GET    /api/webhooks/events                 - Get webhook event history
POST   /api/webhooks/{path}                 - Receive webhook (public)
```

---

## 9. Message Formatting

### 9.1 Slack Block Kit

```python
def format_for_slack(message: NotificationMessage) -> List[Dict]:
    """Convert to Slack Block Kit format."""
    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": message.title}
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": message.body}
        }
    ]
    
    if message.fields:
        blocks.append({
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*{k}:* {v}"}
                for k, v in message.fields.items()
            ]
        })
    
    if message.actions:
        blocks.append({
            "type": "actions",
            "elements": [
                {"type": "button", "text": {"type": "plain_text", "text": a.label}, "url": a.url}
                for a in message.actions
            ]
        })
    
    return blocks
```

### 9.2 Teams Adaptive Cards

```python
def format_for_teams(message: NotificationMessage) -> Dict:
    """Convert to Teams Adaptive Card format."""
    card = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": LEVEL_COLORS.get(message.level, "0076D7"),
        "summary": message.title,
        "sections": [{
            "activityTitle": message.title,
            "activitySubtitle": message.source,
            "text": message.body,
            "facts": [
                {"name": k, "value": v}
                for k, v in (message.fields or {}).items()
            ]
        }]
    }
    
    if message.actions:
        card["potentialAction"] = [
            {"@type": "OpenUri", "name": a.label, "targets": [{"os": "default", "uri": a.url}]}
            for a in message.actions
        ]
    
    return card
```

---

## 10. Error Handling & Retry

```python
class NotificationRetryPolicy:
    """Retry policy for failed notifications."""
    
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except RetryableError as e:
                delay = min(
                    self.base_delay * (self.exponential_base ** attempt),
                    self.max_delay
                )
                await asyncio.sleep(delay)
        raise MaxRetriesExceeded()
```

---

## 11. Monitoring & Metrics

### 11.1 Key Metrics

- `notifications_sent_total` - Counter by channel, level, status
- `notification_latency_seconds` - Histogram of send times
- `webhook_events_received_total` - Counter by endpoint, verified
- `webhook_processing_duration_seconds` - Histogram

### 11.2 Health Checks

```python
async def check_channel_health(channel: str) -> HealthStatus:
    """Check if a notification channel is healthy."""
    adapter = get_adapter(channel)
    try:
        await adapter.validate_config()
        return HealthStatus.HEALTHY
    except Exception as e:
        return HealthStatus.UNHEALTHY
```

---

## 12. Usage Examples

### 12.1 Sending Slack Notification

```python
from abhikarta.notification import NotificationManager, NotificationMessage

manager = NotificationManager()

await manager.send(
    channels=["slack"],
    message=NotificationMessage(
        title="Agent Task Complete",
        body="The data analysis agent has finished processing your request.",
        level=NotificationLevel.SUCCESS,
        fields={
            "Records Processed": "1,234",
            "Duration": "2m 34s"
        },
        actions=[
            Action(label="View Results", url="https://abhikarta.ai/results/123")
        ]
    )
)
```

### 12.2 Receiving Webhook

```python
from abhikarta.notification import WebhookReceiver

receiver = WebhookReceiver()

# Register endpoint that triggers a swarm
receiver.register_endpoint(
    path="/webhooks/github",
    handler=trigger_swarm_handler,
    auth_method=AuthMethod.HMAC,
    secret="github-webhook-secret"
)

# Handler function
async def trigger_swarm_handler(event: WebhookEvent):
    if event.payload.get("action") == "opened":
        await swarm_orchestrator.trigger(
            swarm_id="code-review-swarm",
            trigger_data=event.payload
        )
```

---

## 13. Migration Guide

### From v1.3.0 to v1.4.0

1. Run database migrations to add notification tables
2. Configure notification channels in settings
3. Update agent/workflow configs to include notification settings
4. Test webhook endpoints with sample payloads

---

*Document Version: 1.4.0*
*Last Updated: December 2025*
