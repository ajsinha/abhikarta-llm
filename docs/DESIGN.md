# Abhikarta-LLM v1.4.8 - Architecture Design Document

## Table of Contents

1. [Overview](#1-overview)
2. [System Architecture](#2-system-architecture)
3. [SDK Architecture (v1.4.8)](#3-sdk-architecture)
4. [Actor System](#4-actor-system)
5. [Notification System (v1.4.0)](#5-notification-system)
6. [Database Design](#6-database-design)
7. [Agent System Design](#7-agent-system-design)
8. [Workflow Engine Design](#8-workflow-engine-design)
9. [LLM Provider Integration](#9-llm-provider-integration)
10. [Human-in-the-Loop System](#10-human-in-the-loop-system)
11. [Tools System Design](#11-tools-system-design)
12. [MCP Plugin Framework](#12-mcp-plugin-framework)
13. [Pre-built Solutions](#13-pre-built-solutions)
14. [Security Architecture](#14-security-architecture)
15. [API Design](#15-api-design)

---

## 1. Overview

### 1.1 Purpose

Abhikarta-LLM is an enterprise-grade platform for building, deploying, and managing AI agents and workflows. It provides:

- Multi-provider LLM abstraction
- Visual agent and workflow designers
- Human-in-the-loop capabilities
- Comprehensive tools system
- Banking industry solutions

### 1.2 Design Principles

- **Modularity**: Components are loosely coupled and independently deployable
- **Extensibility**: Easy to add providers, tools, and integrations
- **Security**: Role-based access with audit trails
- **Scalability**: Supports horizontal scaling
- **Reliability**: Fault tolerance with retry mechanisms

### 1.3 Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Flask + Jinja2 + Bootstrap 5 |
| Backend | Python 3.9+ |
| Database | PostgreSQL / SQLite |
| LLM Integration | LangChain, LangGraph |
| External Tools | MCP (Model Context Protocol) |

---

## 2. System Architecture

### 2.1 Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Web UI    │  │  REST API   │  │  Help Documentation     │  │
│  │  (Flask)    │  │  Endpoints  │  │  (35+ pages)            │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                     APPLICATION LAYER                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │ Agent        │ │ Workflow     │ │ HITL         │             │
│  │ Manager      │ │ Engine       │ │ Manager      │             │
│  └──────────────┘ └──────────────┘ └──────────────┘             │
│  ┌──────────────┐ ┌──────────────┐                              │
│  │ Swarm        │ │ Notification │  (v1.3.0+)                   │
│  │ Orchestrator │ │ Manager      │  (v1.4.0)                    │
│  └──────────────┘ └──────────────┘                              │
├─────────────────────────────────────────────────────────────────┤
│                   ACTOR SYSTEM LAYER (v1.3.0)                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    ActorSystem                             │  │
│  │  ┌─────────┐ ┌─────────────┐ ┌────────────┐ ┌──────────┐  │  │
│  │  │ Actors  │ │ Dispatchers │ │ Supervision│ │ Scheduler│  │  │
│  │  │ Props   │ │ Mailboxes   │ │ Strategies │ │ EventBus │  │  │
│  │  └─────────┘ └─────────────┘ └────────────┘ └──────────┘  │  │
│  │  ┌──────────────────────────────────────────────────────┐ │  │
│  │  │ Patterns: Routers │ CircuitBreaker │ Aggregator      │ │  │
│  │  └──────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                   NOTIFICATION LAYER (v1.4.0)                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  │  │
│  │  │ Slack       │ │ Teams       │ │ Webhook Receiver    │  │  │
│  │  │ Adapter     │ │ Adapter     │ │ (HMAC/JWT/API Key)  │  │  │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘  │  │
│  │  ┌──────────────────────────────────────────────────────┐ │  │
│  │  │ Rate Limiting │ Retry Logic │ Audit Logging          │ │  │
│  │  └──────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                        TOOLS LAYER                               │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌─────────────────┐  │
│  │ BaseTool  │ │ MCPTool   │ │ HTTPTool  │ │ ToolsRegistry   │  │
│  └───────────┘ └───────────┘ └───────────┘ └─────────────────┘  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Tool Framework (10 Types)                        │    │
│  │   Common(28)│Banking(13)│Integration(20)│General(24)    │    │
│  └─────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│                     INTEGRATION LAYER                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │ LangChain    │ │ MCP Clients  │ │ LLM Provider Facade      │ │
│  │ LangGraph    │ │ (HTTP/WS)    │ │ (11 providers)           │ │
│  └──────────────┘ └──────────────┘ └──────────────────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │ Kafka        │ │ RabbitMQ     │ │ Slack/Teams APIs         │ │
│  │ (v1.3.0)     │ │ (v1.3.0)     │ │ (v1.4.0)                 │ │
│  └──────────────┘ └──────────────┘ └──────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                        DATA LAYER                                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  DatabaseFacade │ 10 Delegates │ PostgreSQL/SQLite (27 Tbl)│ │
│  │  Core│Users│LLM│Tools│HITL│Audit│Config│Swarm│Notification │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Diagram

```
                    ┌─────────────────┐
                    │   Web Browser   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Flask App     │
                    │   (Routes)      │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼───────┐
│ Agent Manager │   │Workflow Engine│   │ HITL Manager  │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        └─────────┬─────────┴─────────┬─────────┘
                  │                   │
         ┌────────▼────────┐  ┌──────▼──────┐
         │ ToolsRegistry   │  │ LLM Facade  │
         └────────┬────────┘  └──────┬──────┘
                  │                  │
    ┌─────────────┼─────────────┐   │
    │             │             │   │
┌───▼───┐  ┌─────▼─────┐  ┌────▼───┐
│PreBuilt│  │ MCP Tools │  │ Custom │
│ Tools  │  │           │  │ Tools  │
└────────┘  └───────────┘  └────────┘
```

---

## 3. SDK Architecture (v1.4.8)

### 3.1 Overview

Abhikarta v1.4.8 introduces a modular SDK architecture with three standalone packages:

| Package | Purpose | Server Required |
|---------|---------|-----------------|
| `abhikarta-sdk-client` | Connect to deployed Abhikarta server | Yes |
| `abhikarta-sdk-embedded` | Standalone usage without server | No |
| `abhikarta-web` | Web UI module | N/A (module) |

### 3.2 Project Structure

```
abhikarta-llm/
├── abhikarta-main/               # Core library package
│   ├── src/abhikarta/            # Core library
│   │   ├── agent/                # Agent management
│   │   ├── workflow/             # Workflow engine
│   │   ├── swarm/                # Swarm orchestration
│   │   ├── aiorg/                # AI Organizations
│   │   ├── database/             # Persistence layer
│   │   ├── langchain/            # LangChain integration
│   │   └── tools/                # Tool framework
│   │
│   ├── entity_definitions/       # JSON entity templates
│   │   ├── agents/               # Agent templates
│   │   ├── workflows/            # Workflow templates
│   │   ├── swarms/               # Swarm templates
│   │   ├── aiorg/                # AI Org templates
│   │   └── scripts/              # Script templates
│   │
│   └── examples/                 # Example code
│
├── abhikarta-web/                # Web UI module
│   └── src/abhikarta_web/
│       ├── routes/               # Flask routes
│       ├── templates/            # Jinja2 templates
│       └── static/               # CSS, JS, images
│
├── abhikarta-sdk-client/         # API Client SDK
│   └── src/abhikarta_client/
│       ├── client.py             # Main client
│       ├── agents.py             # Agents API
│       ├── workflows.py          # Workflows API
│       ├── swarms.py             # Swarms API
│       └── organizations.py      # Organizations API
│
├── abhikarta-sdk-embedded/       # Embedded SDK
│   └── src/abhikarta_embedded/
│       ├── core.py               # Main Abhikarta class
│       ├── agents/               # Agent implementations
│       ├── workflows/            # Workflow engine
│       ├── swarms/               # Swarm engine
│       ├── orgs/                 # Organization engine
│       ├── providers/            # LLM providers
│       ├── tools/                # Tool framework
│       └── decorators.py         # @agent, @workflow, @tool
│
└── run_server.py                 # Application entry point
```

### 3.3 SDK Client Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AbhikartaClient                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    HTTP Client                        │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │  │
│  │  │ Agents  │ │Workflows│ │ Swarms  │ │  Orgs   │     │  │
│  │  │ Client  │ │ Client  │ │ Client  │ │ Client  │     │  │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘     │  │
│  │       │           │           │           │          │  │
│  │       └───────────┴─────┬─────┴───────────┘          │  │
│  │                         │                            │  │
│  │              ┌──────────▼──────────┐                │  │
│  │              │   REST API Layer    │                │  │
│  │              └──────────┬──────────┘                │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP/HTTPS
                    ┌──────────▼──────────┐
                    │  Abhikarta Server   │
                    └─────────────────────┘
```

### 3.4 SDK Embedded Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Abhikarta                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                 Core Components                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │  │
│  │  │   Agents    │  │  Workflows  │  │   Swarms    │   │  │
│  │  │  ReAct      │  │  DAGWorkflow│  │ Collaborative│  │  │
│  │  │  Goal       │  │  Nodes      │  │ Sequential  │   │  │
│  │  │  Reflect    │  │  Edges      │  │ Parallel    │   │  │
│  │  │  Hierarchical│ │             │  │             │   │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘   │  │
│  │         │                │                │          │  │
│  │         └────────────────┼────────────────┘          │  │
│  │                          │                           │  │
│  │              ┌───────────▼───────────┐              │  │
│  │              │   Provider Layer      │              │  │
│  │              │  Ollama│OpenAI│Anthropic│             │  │
│  │              └───────────────────────┘              │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 3.5 Decorator Pattern

The SDK Embedded supports Pythonic decorator-based definitions:

```python
from abhikarta_embedded import agent, tool

@tool(description="Search the web")
def web_search(query: str) -> dict:
    return {"results": [...]}

@agent(type="react", model="ollama/llama3.2:3b", tools=[web_search])
class ResearchAgent:
    system_prompt = "You are a research assistant."
```

---

## 4. Actor System

### 5.1 Overview

The Actor System provides a Pekko-inspired framework for highly concurrent, distributed, and fault-tolerant agent execution. It enables running millions of agents and workflows in real-time, message-driven fashion.

**Acknowledgement**: Inspired by Apache Pekko (incubating), the open-source fork of Akka.

### 3.2 Actor System Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                        ActorSystem                                  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Actor Hierarchy                            │  │
│  │         /system                /user                          │  │
│  │            │                      │                           │  │
│  │      ┌─────┴─────┐         ┌──────┴──────┐                   │  │
│  │      │           │         │             │                    │  │
│  │   guardian   scheduler   router     orchestrator              │  │
│  │                          /    \          │                    │  │
│  │                    worker-1  worker-n  agent-pool             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────┐  │
│  │  Dispatchers  │  │   Mailboxes   │  │    Supervision        │  │
│  │  ┌─────────┐  │  │  ┌─────────┐  │  │  ┌─────────────────┐  │  │
│  │  │Default  │  │  │  │Unbounded│  │  │  │OneForOneStrategy│  │  │
│  │  │Pinned   │  │  │  │Bounded  │  │  │  │AllForOneStrategy│  │  │
│  │  │ForkJoin │  │  │  │Priority │  │  │  │BackoffStrategy  │  │  │
│  │  └─────────┘  │  │  └─────────┘  │  │  └─────────────────┘  │  │
│  └───────────────┘  └───────────────┘  └───────────────────────┘  │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                      Patterns                               │    │
│  │   Router │ EventBus │ Aggregator │ CircuitBreaker │ Stash  │    │
│  └────────────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────────┘
```

### 3.3 Core Components

| Component | Description |
|-----------|-------------|
| **Actor** | Lightweight entity processing messages sequentially |
| **ActorRef** | Immutable, location-transparent reference to an actor |
| **ActorSystem** | Container managing actors, dispatchers, lifecycle |
| **Props** | Immutable configuration for actor creation |
| **Mailbox** | Message queue for each actor |
| **Dispatcher** | Thread pool executing actor message processing |
| **Supervision** | Fault-tolerance strategy for child failures |

### 3.4 Message Flow

```
Sender                    Mailbox                    Actor
  │                          │                         │
  │  tell(message)           │                         │
  │────────────────────────▶│                         │
  │                          │  enqueue(envelope)     │
  │                          │────────────────────────▶│
  │                          │                         │ process
  │                          │                         │ message
  │                          │◀────────────────────────│
  │                          │  dequeue next           │
  │◀ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│                         │
  │  reply (optional)        │                         │
```

### 3.5 Dispatcher Types

| Type | Thread Model | Use Case |
|------|--------------|----------|
| **DefaultDispatcher** | Shared thread pool | General-purpose actors |
| **PinnedDispatcher** | One thread per actor | Blocking I/O operations |
| **ForkJoinDispatcher** | Work-stealing pool | CPU-bound computations |
| **CallingThreadDispatcher** | Caller's thread | Testing/debugging |
| **BalancingDispatcher** | Multi-pool balancing | High-throughput systems |

### 3.6 Supervision Strategies

```python
# OneForOne: Only restart failed child
strategy = OneForOneStrategy(
    max_restarts=10,
    within_time=60.0,
    decider=lambda e: Directive.RESTART
)

# AllForOne: Restart all children on any failure
strategy = AllForOneStrategy(
    max_restarts=5,
    decider=lambda e: Directive.RESTART
)

# Exponential Backoff: Delay between restarts
strategy = ExponentialBackoffStrategy(
    min_backoff=0.1,
    max_backoff=30.0,
    max_restarts=10
)
```

### 3.7 Router Patterns

```
                    ┌─────────────┐
                    │   Router    │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
   │ Worker1 │       │ Worker2 │       │ Worker3 │
   └─────────┘       └─────────┘       └─────────┘

Routing Strategies:
- RoundRobin: Sequential distribution
- Random: Random selection
- Broadcast: Send to all
- ConsistentHashing: Hash-based routing
- SmallestMailbox: Route to least busy
```

### 3.8 Actor Example

```python
from abhikarta.actor import Actor, ActorSystem, Props

class AgentActor(Actor):
    def __init__(self, model: str):
        super().__init__()
        self._model = model
        self._tasks_completed = 0
    
    def receive(self, message):
        if isinstance(message, AgentTask):
            result = self._process_task(message)
            self._tasks_completed += 1
            if self.sender:
                self.sender.tell(result)

# Create system with 1000 agents
system = ActorSystem()
agents = [
    system.actor_of(Props(AgentActor, args=("gpt-4",)), f"agent-{i}")
    for i in range(1000)
]
```

### 3.9 Scalability Features

- **Lightweight**: Millions of actors in single process
- **Non-blocking**: Async message passing, no locks
- **Location Transparent**: Same API for local/remote actors
- **Backpressure**: Bounded mailboxes for flow control
- **Fault Isolation**: Actor failures don't crash system

---

## 5. Notification System (v1.4.0)

### 5.1 Overview

The Notification System provides enterprise-grade multi-channel notifications for agents, workflows, and swarms. It supports outgoing notifications (Slack, Teams, Email) and incoming webhooks from external systems.

### 5.2 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   NOTIFICATION SYSTEM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  NotificationManager                      │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │   │
│  │  │ Routing     │ │ Rate        │ │ Retry Logic         │ │   │
│  │  │ Engine      │ │ Limiter     │ │ (Exp. Backoff)      │ │   │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         ▼                    ▼                    ▼             │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐     │
│  │ Slack       │      │ Teams       │      │ Email       │     │
│  │ Adapter     │      │ Adapter     │      │ Adapter     │     │
│  │ ─────────── │      │ ─────────── │      │ ─────────── │     │
│  │ Block Kit   │      │ Adaptive    │      │ SMTP        │     │
│  │ Web API     │      │ Cards       │      │ Templates   │     │
│  └─────────────┘      └─────────────┘      └─────────────┘     │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                   WEBHOOK RECEIVER                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  WebhookReceiver                          │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │   │
│  │  │ Signature   │ │ Replay      │ │ Event               │ │   │
│  │  │ Verification│ │ Protection  │ │ Dispatcher          │ │   │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         ▼                    ▼                    ▼             │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐     │
│  │ Trigger     │      │ Trigger     │      │ Trigger     │     │
│  │ Agent       │      │ Workflow    │      │ Swarm       │     │
│  └─────────────┘      └─────────────┘      └─────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 NotificationManager

Central orchestrator for all notification operations:

```python
class NotificationManager:
    """Routes notifications to appropriate channels with retry and rate limiting."""
    
    def __init__(self, db_facade: DatabaseFacade):
        self.db = db_facade
        self.adapters = {
            ChannelType.SLACK: SlackAdapter(),
            ChannelType.TEAMS: TeamsAdapter(),
            ChannelType.EMAIL: EmailAdapter()
        }
        self.rate_limiters = {}  # Per-channel token bucket
    
    async def send(self, notification: Notification) -> NotificationResult:
        """Send notification with rate limiting and retry."""
        # Check rate limit
        if not self._check_rate_limit(notification.channel_id):
            return NotificationResult(success=False, error="Rate limited")
        
        # Get adapter and send
        adapter = self.adapters[notification.channel_type]
        result = await self._send_with_retry(adapter, notification)
        
        # Log result
        self.db.notifications.log_notification(notification, result)
        return result
    
    async def _send_with_retry(self, adapter, notification, max_retries=3):
        """Exponential backoff retry logic."""
        for attempt in range(max_retries):
            try:
                return await adapter.send(notification)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # 1s, 2s, 4s
```

### 4.4 Slack Adapter

```python
class SlackAdapter:
    """Slack Web API integration with Block Kit support."""
    
    async def send(self, notification: Notification) -> NotificationResult:
        # Build Block Kit message
        blocks = self._build_blocks(notification)
        
        # Send via Web API
        response = await self.client.chat_postMessage(
            channel=notification.channel_address,
            text=notification.title,
            blocks=blocks,
            thread_ts=notification.thread_ts  # Optional thread reply
        )
        
        return NotificationResult(
            success=response["ok"],
            message_id=response.get("ts")
        )
    
    def _build_blocks(self, notification):
        """Build Slack Block Kit blocks from notification."""
        return [
            {"type": "header", "text": {"type": "plain_text", "text": notification.title}},
            {"type": "section", "text": {"type": "mrkdwn", "text": notification.body}},
            {"type": "context", "elements": [
                {"type": "mrkdwn", "text": f"Level: {notification.level.value}"}
            ]}
        ]
```

### 4.5 Webhook Receiver

```python
class WebhookReceiver:
    """Receives and processes external webhooks."""
    
    def __init__(self, db_facade: DatabaseFacade):
        self.db = db_facade
        self.verifiers = {
            AuthMethod.HMAC: HMACVerifier(),
            AuthMethod.JWT: JWTVerifier(),
            AuthMethod.API_KEY: APIKeyVerifier()
        }
    
    async def handle(self, endpoint_path: str, request: Request) -> WebhookResult:
        # Find endpoint
        endpoint = self.db.notifications.get_webhook_endpoint(path=endpoint_path)
        if not endpoint:
            return WebhookResult(success=False, error="Endpoint not found")
        
        # Verify signature
        verifier = self.verifiers[endpoint.auth_method]
        if not await verifier.verify(request, endpoint.secret):
            return WebhookResult(success=False, error="Signature verification failed")
        
        # Check replay protection
        if self._is_replay(request):
            return WebhookResult(success=False, error="Replay detected")
        
        # Log event
        event_id = self.db.notifications.log_webhook_event(endpoint, request)
        
        # Dispatch to target
        await self._dispatch(endpoint, request.json)
        
        return WebhookResult(success=True, event_id=event_id)
    
    async def _dispatch(self, endpoint: WebhookEndpoint, payload: dict):
        """Dispatch webhook to agent, workflow, or swarm."""
        if endpoint.target_type == TargetType.AGENT:
            await self.agent_manager.execute(endpoint.target_id, payload)
        elif endpoint.target_type == TargetType.WORKFLOW:
            await self.workflow_engine.execute(endpoint.target_id, payload)
        elif endpoint.target_type == TargetType.SWARM:
            await self.swarm_orchestrator.trigger(endpoint.target_id, payload)
```

### 4.6 Authentication Methods

| Method | How It Works | Best For |
|--------|--------------|----------|
| **HMAC-SHA256** | Compute hash of payload with shared secret, compare to header | GitHub, Stripe, Slack |
| **JWT** | Verify JWT signature in Authorization header | Enterprise integrations |
| **API Key** | Check X-API-Key header against stored key | Simple integrations |
| **Basic** | Username/password in Authorization header | Legacy systems |

### 4.7 Rate Limiting

Token bucket algorithm prevents overwhelming external services:

```python
class TokenBucketRateLimiter:
    def __init__(self, rate: int, capacity: int):
        self.rate = rate          # Tokens per second
        self.capacity = capacity  # Max bucket size
        self.tokens = capacity
        self.last_update = time.time()
    
    def acquire(self) -> bool:
        """Try to acquire a token. Returns True if allowed."""
        self._refill()
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
    
    def _refill(self):
        """Add tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_update = now
```

### 4.8 Database Tables (5 new)

| Table | Purpose |
|-------|---------|
| `notification_channels` | Channel configurations (Slack, Teams, Email) |
| `notification_logs` | Notification history and delivery status |
| `webhook_endpoints` | Registered webhook paths and auth |
| `webhook_events` | Incoming webhook event log |
| `user_notification_preferences` | Per-user notification settings |

---

## 6. Database Design

### 5.1 Schema Overview (27 Tables)

```
┌─────────────────────────────────────────────────────────────────┐
│                        CORE TABLES                               │
├─────────────────┬───────────────────────────────────────────────┤
│ agents          │ Agent definitions and configurations           │
│ workflows       │ Workflow DAG definitions                       │
│ executions      │ Execution records and status                   │
│ execution_steps │ Individual step results                        │
├─────────────────┴───────────────────────────────────────────────┤
│                        USER TABLES                               │
├─────────────────┬───────────────────────────────────────────────┤
│ users           │ User accounts and profiles                     │
│ api_keys        │ API key management                             │
│ audit_logs      │ Activity audit trail                           │
├─────────────────┴───────────────────────────────────────────────┤
│                         LLM TABLES                               │
├─────────────────┬───────────────────────────────────────────────┤
│ llm_providers   │ LLM provider configurations                    │
│ llm_models      │ Available models per provider                  │
│ llm_model_perms │ Role-based model permissions                   │
│ llm_logs        │ LLM call logging                               │
├─────────────────┴───────────────────────────────────────────────┤
│                        TOOL TABLES                               │
├─────────────────┬───────────────────────────────────────────────┤
│ mcp_servers     │ MCP server configurations                      │
│ mcp_tools       │ Tools discovered from MCP servers              │
│ code_fragments  │ Reusable code snippets                         │
├─────────────────┴───────────────────────────────────────────────┤
│                        HITL TABLES                               │
├─────────────────┬───────────────────────────────────────────────┤
│ hitl_tasks      │ Human-in-the-loop tasks                        │
│ hitl_comments   │ Task comments and discussions                  │
│ hitl_assignments│ Task assignments to users                      │
├─────────────────┴───────────────────────────────────────────────┤
│                       CONFIG TABLES                              │
├─────────────────┬───────────────────────────────────────────────┤
│ settings        │ Application settings                           │
│ templates       │ Agent/workflow templates                       │
└─────────────────┴───────────────────────────────────────────────┘
```

### 5.2 Key Table Schemas

#### agents
```sql
CREATE TABLE agents (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    agent_type VARCHAR(50),        -- react, cot, pae, custom
    model_id VARCHAR(100),
    system_prompt TEXT,
    tools TEXT,                    -- JSON array of tool names
    config TEXT,                   -- JSON configuration
    status VARCHAR(50),
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### workflows
```sql
CREATE TABLE workflows (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    definition TEXT NOT NULL,      -- JSON DAG definition
    status VARCHAR(50),
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### hitl_tasks
```sql
CREATE TABLE hitl_tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(100) UNIQUE NOT NULL,
    execution_id VARCHAR(100),
    task_type VARCHAR(50),
    title VARCHAR(255),
    description TEXT,
    input_data TEXT,               -- JSON
    output_data TEXT,              -- JSON
    status VARCHAR(50),            -- pending, in_progress, completed, rejected
    priority VARCHAR(20),          -- low, medium, high, critical
    assigned_to INTEGER REFERENCES users(id),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

---

## 4. Agent System Design

### 5.1 Agent Types

| Type | Description | Use Case |
|------|-------------|----------|
| **ReAct** | Reasoning + Acting loop | General purpose |
| **Chain-of-Thought** | Step-by-step reasoning | Complex reasoning |
| **Plan-and-Execute** | Plan then execute | Multi-step tasks |
| **Custom** | User-defined | Specialized needs |

### 5.2 Agent Configuration Schema

```json
{
  "agent_id": "unique_identifier",
  "name": "Agent Name",
  "description": "What the agent does",
  "agent_type": "react",
  "model_id": "gpt-4o",
  "system_prompt": "You are a helpful assistant...",
  "tools": ["tool1", "tool2"],
  "temperature": 0.7,
  "max_tokens": 1024,
  "max_iterations": 10,
  "input_schema": {},
  "output_schema": {}
}
```

### 5.3 Visual Agent Designer

The designer supports 14 node types with drag-and-drop functionality:

- **Input/Output**: Start, End
- **Processing**: LLM, Agent, Tool, Code, RAG
- **Control Flow**: Condition, Loop, Passthrough
- **Human**: HITL
- **Data**: Transform, Filter, Aggregate

---

## 5. Workflow Engine Design

### 5.1 DAG Execution Model

```
Workflow Definition (JSON)
         │
         ▼
    ┌────────────┐
    │ DAG Parser │
    └─────┬──────┘
          │
          ▼
    ┌────────────┐
    │  Executor  │──────► Context
    └─────┬──────┘          │
          │                 │
    ┌─────▼─────┐          │
    │ Node Exec │◄─────────┘
    └─────┬─────┘
          │
          ▼
    ┌────────────┐
    │  Results   │
    └────────────┘
```

### 5.2 Node Types

| Node Type | Description | Implementation |
|-----------|-------------|----------------|
| `start` | Entry point | Initializes context |
| `end` | Exit point | Returns final output |
| `llm` | LLM call | Uses LLM facade |
| `agent` | Agent invocation | Calls agent executor |
| `tool` | Tool execution | Uses ToolsRegistry |
| `code` | Python execution | Sandboxed execution |
| `condition` | Branching | Expression evaluation |
| `passthrough` | Data pass | Merges contexts |
| `rag` | RAG query | Vector store lookup |
| `hitl` | Human task | Creates HITL task |

### 5.3 Workflow Definition Format

```json
{
  "workflow_id": "loan_processing",
  "name": "Loan Application Workflow",
  "nodes": [
    {
      "id": "start",
      "type": "start",
      "config": {}
    },
    {
      "id": "credit_check",
      "type": "tool",
      "config": {
        "tool_name": "calculate_credit_score"
      }
    },
    {
      "id": "decision",
      "type": "condition",
      "config": {
        "condition": "credit_score >= 700"
      }
    }
  ],
  "edges": [
    {"from": "start", "to": "credit_check"},
    {"from": "credit_check", "to": "decision"}
  ]
}
```

---

## 6. LLM Provider Integration

### 6.1 Provider Facade

```python
class LLMFacade:
    """Unified interface for all LLM providers."""
    
    def get_completion(self, model_id, messages, **kwargs):
        """Get completion from configured provider."""
        provider = self._get_provider(model_id)
        return provider.complete(messages, **kwargs)
    
    def get_streaming_completion(self, model_id, messages, **kwargs):
        """Get streaming completion."""
        provider = self._get_provider(model_id)
        return provider.stream(messages, **kwargs)
```

### 6.2 Supported Providers

| Provider | Module | Features |
|----------|--------|----------|
| OpenAI | `langchain_openai` | Full support, function calling |
| Anthropic | `langchain_anthropic` | Claude models, tools |
| Google | `langchain_google_genai` | Gemini models |
| Azure OpenAI | `langchain_openai` | Enterprise deployment |
| AWS Bedrock | `langchain_aws` | Multi-model access |
| Mistral | `langchain_mistral` | Open-weight models |
| Groq | `langchain_groq` | Fast inference |
| Together | `langchain_together` | Open source models |
| Cohere | `langchain_cohere` | Command models |
| Hugging Face | `langchain_huggingface` | Inference API |
| Ollama | `langchain_community` | Local deployment |

### 6.3 LangChain Integration

```python
# LLM Factory
from abhikarta.langchain import create_llm, create_agent

llm = create_llm(provider="openai", model="gpt-4o")
agent = create_agent(llm, tools, agent_type="react")

# LangGraph Workflow
from abhikarta.langchain import create_workflow_graph

graph = create_workflow_graph(workflow_definition)
result = graph.invoke(input_data)
```

### 6.4 LLM Adapter (v1.4.0 - NEW)

The LLM Adapter provides an async-first interface for making LLM calls,
designed for use in the swarm and agent modules.

```python
from abhikarta.llm import LLMAdapter, LLMResponse, LLMConfig

# Simple usage
adapter = LLMAdapter(provider='openai', model='gpt-4o')
response = await adapter.generate(
    prompt="Hello, world!",
    system_prompt="You are a helpful assistant."
)
print(response.content)

# With configuration
config = LLMConfig(
    provider='anthropic',
    model='claude-3-5-sonnet-20241022',
    temperature=0.5,
    max_tokens=4000
)
adapter = LLMAdapter(config=config)

# Multi-turn chat
messages = [
    {'role': 'system', 'content': 'You are a helpful assistant.'},
    {'role': 'user', 'content': 'Hello!'},
    {'role': 'assistant', 'content': 'Hi! How can I help?'},
    {'role': 'user', 'content': 'Tell me about swarms.'}
]
response = await adapter.chat(messages)

# Quick one-off call
from abhikarta.llm import generate
response = await generate("Tell me a joke", provider='openai')
```

#### LLM Adapter Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      LLM Adapter                             │
│                                                             │
│   ┌────────────┐    ┌────────────┐    ┌────────────┐      │
│   │ generate() │    │  chat()    │    │ direct_call│      │
│   └─────┬──────┘    └─────┬──────┘    └─────┬──────┘      │
│         │                 │                 │              │
│         └────────┬────────┴────────┬────────┘              │
│                  │                 │                        │
│         ┌────────▼────────┐        │                       │
│         │   LLMFacade     │◄───────┘ (fallback)            │
│         └────────┬────────┘                                │
│                  │                                         │
└──────────────────┼─────────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌────────┐   ┌────────┐   ┌────────┐
│ OpenAI │   │Anthropic│   │ Ollama │  ... (10+ providers)
└────────┘   └────────┘   └────────┘
```

---

### 6.5 Playground Navigation (v1.4.0 - NEW)

The navigation has been streamlined with a unified **Playground** mega-menu combining Agents, Workflows, and Swarms:

```
┌─────────────────────────────────────────────────────────┐
│ Abhikarta-LLM  │ Admin │ Dashboard │ Playground ▼ │ ...│
└─────────────────────────────────────┬───────────────────┘
                                      │
                    ┌─────────────────▼─────────────────┐
                    │     PLAYGROUND MEGA-MENU          │
                    ├───────────────────────────────────┤
                    │ 🤖 AGENTS                         │
                    │   • Browse Agents                 │
                    │   • Visual Designer               │
                    │   • Template Library              │
                    ├───────────────────────────────────┤
                    │ 📊 WORKFLOWS                      │
                    │   • All Workflows                 │
                    │   • Visual Designer               │
                    │   • Template Library              │
                    │   • Upload Workflow               │
                    ├───────────────────────────────────┤
                    │ 🐝 SWARMS (v1.4.0)                │
                    │   • All Swarms                    │
                    │   • Swarm Designer                │
                    └───────────────────────────────────┘
```

### 6.6 Swarm Execution Logging (v1.4.0 - NEW)

Swarm executions are fully logged to the database, similar to agent and workflow executions:

**Database Tables:**
```
swarm_executions
├── execution_id (UUID)
├── swarm_id (FK → swarms)
├── trigger_type (kafka/http/schedule/user_query)
├── trigger_data (JSON)
├── status (pending/running/completed/failed)
├── result (JSON)
├── error (text)
├── user_id (FK → users)
├── duration_ms (integer)
├── created_at, completed_at

swarm_events
├── event_id (UUID)
├── swarm_id, execution_id
├── event_type (task.*/result.*/error.*)
├── source_agent, target_agent
├── payload (JSON)
├── created_at

swarm_decisions
├── decision_id (UUID)
├── swarm_id, execution_id
├── decision_type (delegate/plan/respond)
├── target_agent
├── reasoning (text)
├── created_at
```

**Unified Executions View:**
```
┌─────────────────────────────────────────────────────────┐
│ My Executions                                           │
├─────────────────────────────────────────────────────────┤
│ ┌───────────────────────┐ ┌───────────────────────────┐ │
│ │ Agents & Workflows    │ │ Swarms                    │ │
│ │ [Tab - Active]        │ │ [Tab]                     │ │
│ └───────────────────────┘ └───────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ ID      │ Type   │ Name    │ Status │ Tokens │ Started │
│ abc123  │ Agent  │ Analyst │ ✓ Done │ 1,234  │ 10:30   │
│ def456  │ Wrkflw │ ETL     │ ✗ Fail │   892  │ 10:15   │
└─────────────────────────────────────────────────────────┘
```

**Swarm Execution Detail Page:**
- Status overview with trigger info and timing
- Master Actor decisions timeline with reasoning
- Event log showing inter-agent communication
- Trigger data and result display

---

## 7. Human-in-the-Loop System

### 7.1 HITL Architecture

```
Workflow Execution
        │
        ▼
┌───────────────┐
│  HITL Node    │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Create Task   │
└───────┬───────┘
        │
        ▼
┌───────────────┐         ┌──────────────┐
│ Task Queue    │◄────────│ User Action  │
└───────┬───────┘         └──────────────┘
        │
        ▼
┌───────────────┐
│Resume Workflow│
└───────────────┘
```

### 7.2 Task Lifecycle

```
PENDING ──► IN_PROGRESS ──► COMPLETED
                │                │
                │                ▼
                └──────► REJECTED
```

### 7.3 HITL Manager API

```python
class HITLManager:
    def create_task(self, execution_id, task_type, data) -> str
    def get_pending_tasks(self, user_id=None) -> List[Task]
    def assign_task(self, task_id, user_id) -> bool
    def complete_task(self, task_id, output, user_id) -> bool
    def reject_task(self, task_id, reason, user_id) -> bool
    def add_comment(self, task_id, user_id, comment) -> bool
```

---

## 8. Tools System Design

### 8.1 BaseTool Architecture

```python
class BaseTool(ABC):
    """Abstract base class for all tools."""
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters."""
        pass
    
    @abstractmethod
    def get_schema(self) -> ToolSchema:
        """Return tool schema for LLM function calling."""
        pass
    
    def to_openai_function(self) -> Dict:
        """Convert to OpenAI function format."""
        pass
    
    def to_anthropic_tool(self) -> Dict:
        """Convert to Anthropic tool format."""
        pass
    
    def to_langchain_tool(self) -> LangChainTool:
        """Convert to LangChain tool."""
        pass
```

### 8.2 Tool Implementations

| Tool Type | Description | Use Case |
|-----------|-------------|----------|
| `FunctionTool` | Python function wrapper | Simple tools |
| `MCPTool` | MCP server tool wrapper | External tools |
| `HTTPTool` | REST API caller | API integrations |
| `CodeFragmentTool` | Database code execution | Dynamic tools |
| `LangChainTool` | LangChain integration | LangChain ecosystem |

### 8.3 ToolsRegistry

```python
class ToolsRegistry:
    """Centralized tool registration and discovery."""
    
    def register(self, tool: BaseTool) -> bool
    def get(self, name: str) -> Optional[BaseTool]
    def list_tools(self) -> List[BaseTool]
    def search(self, query: str) -> List[BaseTool]
    def execute(self, name: str, **kwargs) -> ToolResult
    
    # Format conversion
    def to_openai_functions(self) -> List[Dict]
    def to_anthropic_tools(self) -> List[Dict]
    def to_langchain_tools(self) -> List[LangChainTool]
```

### 8.4 Tool Framework (10 Types)

#### Common Tools (28)
- Date/Time: 5 tools
- Math/Calculator: 5 tools
- Text Processing: 5 tools
- Validation: 5 tools
- Format Conversion: 5 tools
- ID Generation: 3 tools

#### Banking Tools (13)
- KYC: 4 tools
- Credit: 2 tools
- Loan: 2 tools
- Transaction: 3 tools
- Compliance: 2 tools

#### Integration Tools (20)
- HTTP/API: 4 tools
- Notifications: 3 tools
- Data Transform: 5 tools
- List/Array: 5 tools
- Workflow: 3 tools

#### General Tools (24) - NEW in v1.4.0
- Web/Search: 4 tools (web_search, web_fetch, intranet_search, news_search)
- Document Handling: 4 tools (read_document, write_document, convert_document, extract_document_metadata)
- File Operations: 4 tools (list_files, copy_file, move_file, delete_file)
- System Utilities: 4 tools (get_system_info, execute_shell_command, get/set_environment_variable)
- Network Tools: 4 tools (check_url_status, ping_host, dns_lookup, parse_url)
- Encoding: 4 tools (url_encode/decode, html_encode/decode)

### 8.5 Tools Management Pages

#### Tools List Page (`/tools`)
- **Centralized View**: Browse all registered tools (pre-built, MCP, code fragments)
- **DataTables Integration**: Pagination, sorting, search
- **Filtering**: By category, source type
- **Quick Actions**: View and Test buttons for each tool
- **MCP Refresh**: Manually trigger MCP server sync

#### Tool Detail Page (`/tools/{name}`)
- **Complete Information**: Name, ID, type, category, status, version
- **Source Details**: Source type, server (for MCP), author, tags
- **Parameters Display**: All parameters with types and descriptions
- **JSON Schema**: Complete schema with copy functionality
- **Navigation**: Links to test page and back to list

#### Tool Test Page (`/tools/{name}/test`)
- **Form-based Input**: Type-specific controls for each parameter
- **Boolean**: Toggle switches
- **Number**: Numeric inputs with step
- **Enum**: Dropdown selects
- **Array/Object**: JSON text areas
- **String**: Text inputs or textareas
- **Raw JSON Mode**: Toggle to enter parameters as JSON
- **Execution Results**: Formatted output with success/error status
- **Request Display**: View the request that was sent

### 8.6 Tools API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tools` | Tools listing page |
| GET | `/tools/{name}` | Tool detail page |
| GET | `/tools/{name}/test` | Tool test page |
| GET | `/api/tools` | List all registered tools (JSON) |
| GET | `/api/tools/{name}` | Get tool details and schema (JSON) |
| POST | `/api/tools/{name}/execute` | Execute tool with parameters |
| POST | `/api/tools/refresh-mcp` | Refresh MCP server tools (admin) |

---

## 9. MCP Plugin Framework

### 9.1 MCPServerManager

```python
class MCPServerManager:
    """Centralized MCP server lifecycle management."""
    
    def add_server(self, config: MCPServerConfig) -> str
    def connect_server(self, server_id: str) -> bool
    def disconnect_server(self, server_id: str) -> bool
    def get_server_tools(self, server_id: str) -> List[MCPTool]
    
    # Health monitoring
    def start_health_monitor(self, interval: int = 30)
    def check_health(self, server_id: str) -> bool
    
    # Database persistence
    def load_from_database(self)
    def save_to_database(self)
```

### 9.2 Transport Types

| Transport | Protocol | Use Case |
|-----------|----------|----------|
| HTTP | REST over HTTP/HTTPS | Standard web services |
| WebSocket | Full-duplex connection | Real-time tools |
| SSE | Server-Sent Events | Streaming responses |
| STDIO | Standard I/O | Local processes |

### 9.3 Tool Registration Flow

```
MCP Server Connect
        │
        ▼
┌──────────────────┐
│ List Tools API   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Create MCPTool   │
│ for each tool    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Register with    │
│ ToolsRegistry    │
└──────────────────┘
```

---

## 10. Pre-built Solutions

### 10.1 Template Libraries

The platform includes comprehensive template libraries for rapid deployment:

| Library | Count | Categories |
|---------|-------|------------|
| **Agent Templates** | 36 | 15 categories (Analytics, Banking, Development, Healthcare, Legal, etc.) |
| **Workflow Templates** | 33 | 11 industries (Finance, Healthcare, HR, Legal, Technology, etc.) |
| **Code Fragment Templates** | 25 | 16 workflows + 9 agents with URI-based code references |

### 10.2 Code Fragment URI Schemes

Templates reference code fragments using standardized URI schemes:

| Scheme | Format | Example | Use Case |
|--------|--------|---------|----------|
| `db://` | `db://code_fragments/<id>` | `db://code_fragments/data_validator` | Database-managed code |
| `s3://` | `s3://<bucket>/<key>` | `s3://ml-models/fraud_detector.py` | Cloud-stored code |
| `file://` | `file:///<path>` | `file:///opt/abhikarta/fragments/custom.py` | Local file system |

### 10.3 Banking Agents (10)

| Agent | Description | Tools Used |
|-------|-------------|------------|
| KYC Verification | Identity/document verification | verify_identity_document, calculate_kyc_risk_score |
| Loan Processor | Loan application evaluation | calculate_loan_eligibility, generate_amortization_schedule |
| Fraud Detection | Transaction fraud analysis | analyze_transaction, detect_transaction_patterns |
| Credit Risk | Credit risk assessment | calculate_credit_score, assess_debt_to_income |
| Customer Service | General customer support | Common tools |
| Account Opening | New account onboarding | verify_identity_document, verify_address |
| Compliance Officer | Regulatory compliance | generate_aml_report, check_sanctions_list |
| Investment Advisor | Investment recommendations | calculate_compound_interest |
| Collections | Debt collection | calculate_loan_emi |
| Document Processor | Document processing | extract_entities, clean_text |

### 10.2 Banking Workflows (7)

| Workflow | Nodes | Features |
|----------|-------|----------|
| Loan Application | 12 | Credit check, DTI, HITL review |
| Customer Onboarding | 15 | KYC, verification, parallel processing |
| Transaction Monitoring | 14 | Real-time fraud, AML reporting |
| Mortgage Application | 13 | Appraisal, underwriting |
| Credit Card Application | 15 | Product selection, fraud screening |
| Wire Transfer | 17 | OFAC, fraud, CTR |
| Dispute Resolution | 13 | Classification, investigation |

---

## 11. Security Architecture

### 11.1 Authentication & Authorization

```
┌─────────────────────────────────────────┐
│           User Request                   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│      Session/API Key Validation         │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│           RBAC Check                     │
│  ┌─────────────────────────────────┐    │
│  │ super_admin > domain_admin >    │    │
│  │ agent_developer > agent_user    │    │
│  └─────────────────────────────────┘    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         Resource Access                  │
└─────────────────────────────────────────┘
```

### 11.2 Role Permissions

| Permission | super_admin | domain_admin | agent_developer | agent_user |
|------------|:-----------:|:------------:|:---------------:|:----------:|
| Manage Users | ✅ | ✅ | ❌ | ❌ |
| Configure LLM | ✅ | ✅ | ❌ | ❌ |
| Create Agents | ✅ | ✅ | ✅ | ❌ |
| Execute Agents | ✅ | ✅ | ✅ | ✅ |
| View Logs | ✅ | ✅ | ✅ | ✅ |
| System Config | ✅ | ❌ | ❌ | ❌ |

### 11.3 Security Features

- **Password Hashing**: bcrypt with salt
- **Session Management**: Secure cookies, timeout
- **API Keys**: Secure generation, rotation support
- **Audit Logging**: All actions logged
- **Input Validation**: SQL injection prevention
- **HTTPS**: TLS encryption support

---

## 12. API Design

### 12.1 REST API Endpoints

#### Agents
```
GET    /api/agents              # List agents
POST   /api/agents              # Create agent
GET    /api/agents/{id}         # Get agent
PUT    /api/agents/{id}         # Update agent
DELETE /api/agents/{id}         # Delete agent
POST   /api/agents/{id}/execute # Execute agent
```

#### Workflows
```
GET    /api/workflows              # List workflows
POST   /api/workflows              # Create workflow
GET    /api/workflows/{id}         # Get workflow
PUT    /api/workflows/{id}         # Update workflow
DELETE /api/workflows/{id}         # Delete workflow
POST   /api/workflows/{id}/execute # Execute workflow
```

#### Executions
```
GET    /api/executions           # List executions
GET    /api/executions/{id}      # Get execution
GET    /api/executions/{id}/logs # Get execution logs
```

#### HITL
```
GET    /api/hitl/tasks           # List tasks
GET    /api/hitl/tasks/{id}      # Get task
POST   /api/hitl/tasks/{id}/complete # Complete task
POST   /api/hitl/tasks/{id}/reject   # Reject task
```

#### Tools
```
GET    /api/tools                # List tools
GET    /api/tools/{name}         # Get tool details
POST   /api/tools/{name}/execute # Execute tool
```

### 12.2 Response Format

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

## 13. Notification System (v1.4.0)

### 13.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        NOTIFICATION MODULE                                   │
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
│  │  ┌─────────────┐  ┌───────┴─────┐  ┌─────────────┐                  │   │
│  │  │   Slack     │  │   Teams     │  │   Email     │                  │   │
│  │  │   Adapter   │  │   Adapter   │  │   Adapter   │                  │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                  │   │
│  └─────────┼────────────────┼────────────────┼──────────────────────────┘   │
│            │                │                │                              │
│            ▼                ▼                ▼                              │
│       ┌─────────┐     ┌─────────┐     ┌─────────┐                          │
│       │ Slack   │     │ Teams   │     │ SMTP    │                          │
│       │ API     │     │ Webhook │     │ Server  │                          │
│       └─────────┘     └─────────┘     └─────────┘                          │
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

### 13.2 Components

#### NotificationManager
Central orchestrator for all notification operations:
- Multi-channel support (Slack, Teams, Email)
- Priority-based routing
- Retry with exponential backoff
- Rate limiting per channel
- Audit logging

#### SlackAdapter
Slack integration using Web API:
- Channel messages (#channel)
- Direct messages (@user)
- Rich formatting (Block Kit)
- Thread replies
- File attachments

#### TeamsAdapter
Microsoft Teams integration using Incoming Webhooks:
- Channel messages
- Adaptive Cards
- MessageCard format
- Action buttons

#### WebhookReceiver
Receives and processes incoming webhooks:
- Endpoint registration
- Signature verification (HMAC, JWT, API key)
- Payload validation
- Event dispatching to agents/workflows/swarms
- Rate limiting and replay protection

### 13.3 Database Tables

```sql
-- Notification Channels Configuration
notification_channels (
    channel_id, channel_type, name, config, is_active, created_by
)

-- Notification Logs
notification_logs (
    notification_id, channel_type, recipient, title, body, level,
    status, source, source_type, correlation_id, sent_at
)

-- Webhook Endpoints
webhook_endpoints (
    endpoint_id, path, name, auth_method, secret_hash,
    target_type, target_id, rate_limit, is_active
)

-- Webhook Events
webhook_events (
    event_id, endpoint_id, event_type, payload, headers,
    source_ip, verified, processed, received_at
)

-- User Notification Preferences
user_notification_preferences (
    user_id, channel_type, channel_address, enabled,
    min_level, quiet_hours_start, quiet_hours_end
)
```

### 13.4 Integration with Agents/Workflows/Swarms

Agents, workflows, and swarms can send notifications:

```python
# From an Agent
await notification_manager.send(
    channels=["slack", "teams"],
    message=NotificationMessage(
        title="Agent Task Complete",
        body="Data analysis finished",
        level=NotificationLevel.SUCCESS,
        source=agent_id,
        source_type="agent"
    )
)

# From a Workflow Node
- node_id: notify_success
  node_type: notification
  config:
    channels: ["slack"]
    level: success
    title: "Workflow Complete"

# From a Swarm Master Actor
await master_actor.notify_stakeholders(event, channels=["slack", "teams"])
```

### 13.5 Webhook Triggers

External systems can trigger agents/workflows/swarms via webhooks:

```python
# Register endpoint
receiver.register_endpoint(
    path="/webhooks/github",
    name="GitHub Webhook",
    auth_method=AuthMethod.HMAC,
    secret="github-secret",
    target_type="swarm",
    target_id="code-review-swarm"
)
```

---

## Appendix A: Module Structure

```
abhikarta/
├── agent/              # Agent management (2 files)
├── config/             # Configuration (1 file)
├── core/               # Core utilities (2 files)
├── database/           # Database layer (5 files)
├── hitl/               # HITL system (1 file)
├── langchain/          # LangChain integration (4 files)
├── llm/                # LLM Adapter (v1.3.0) (2 files)
├── llm_provider/       # LLM facade (1 file)
├── mcp/                # MCP integration (3 files)
├── messaging/          # Message brokers (v1.3.0) (6 files)
├── notification/       # Notification system (v1.4.0) (6 files)
│   ├── __init__.py
│   ├── base.py         # Data models and enums
│   ├── manager.py      # NotificationManager
│   ├── slack_adapter.py
│   ├── teams_adapter.py
│   └── webhook_receiver.py
├── rbac/               # Access control (1 file)
├── swarm/              # Agent Swarms (v1.3.0) (5 files)
├── tools/              # Tools system (8 files)
│   └── prebuilt/       # Pre-built tools (4 files)
├── user_management/    # User management (1 file)
├── utils/              # Utilities (4 files)
├── web/                # Web application (50+ files)
└── workflow/           # Workflow engine (3 files)
```

---

*Version 1.4.0 - Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.*
