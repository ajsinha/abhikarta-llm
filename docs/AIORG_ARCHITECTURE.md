# AI Org - Architecture Document

**Module:** AI Org (Artificial Intelligence Organization)  
**Version:** 1.4.5  
**Date:** December 2025  
**Author:** Abhikarta Team  
**Status:** Draft

---

## 1. Overview

### 1.1 System Context

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SYSTEM CONTEXT                                     │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌──────────────────┐
                    │   External       │
                    │   Systems        │
                    │ (Webhooks, APIs) │
                    └────────┬─────────┘
                             │
                             ▼
┌──────────────┐    ┌───────────────────┐    ┌──────────────┐
│   Human      │    │                   │    │   LLM        │
│   Users      │◄──►│   ABHIKARTA       │◄──►│   Providers  │
│ (Browsers)   │    │   AI ORG          │    │ (OpenAI,     │
└──────────────┘    │                   │    │  Anthropic)  │
                    └─────────┬─────────┘    └──────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
       ┌──────────┐    ┌──────────┐    ┌──────────┐
       │  Email   │    │  MS      │    │  Slack   │
       │  Server  │    │  Teams   │    │          │
       └──────────┘    └──────────┘    └──────────┘
```

### 1.2 Architectural Goals

1. **Scalability**: Support thousands of concurrent org charts
2. **Resilience**: Handle node failures without losing tasks
3. **Real-time**: Sub-second event propagation
4. **Auditability**: Complete traceability of all actions
5. **Extensibility**: Easy to add new node types, channels

### 1.3 Key Architectural Decisions

| Decision | Rationale |
|----------|-----------|
| Actor-based nodes | Natural mapping to org hierarchy, isolation, concurrency |
| Event-driven communication | Loose coupling, async processing, scalability |
| Database-first persistence | Durability, recovery, audit trail |
| WebSocket for real-time | Efficient bi-directional updates |
| Plugin architecture for notifications | Support multiple channels easily |

---

## 2. High-Level Architecture

### 2.1 Layered Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION LAYER                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Web UI     │  │  REST API   │  │  WebSocket  │  │  Webhook    │        │
│  │  (Jinja2)   │  │  (Flask)    │  │  Server     │  │  Receiver   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          APPLICATION LAYER                                   │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        AI ORG SERVICES                                 │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │ OrgManager  │  │ TaskEngine  │  │ HITLManager │  │ OrgNotifier │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                       CORE SERVICES                                    │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │ AgentMgr    │  │ LLM Facade  │  │ Event Bus   │  │ ActorSystem │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          INFRASTRUCTURE LAYER                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Database   │  │  Message    │  │  Cache      │  │  External   │        │
│  │  Facade     │  │  Queue      │  │  (Optional) │  │  Services   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                          │
│  │  SQLite     │  │  PostgreSQL │  │  File       │                          │
│  │             │  │             │  │  Storage    │                          │
│  └─────────────┘  └─────────────┘  └─────────────┘                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AI ORG COMPONENT DIAGRAM                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              aiorg Package                                   │
│                                                                              │
│  ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐  │
│  │    models.py     │      │   org_manager.py │      │  task_engine.py  │  │
│  │                  │      │                  │      │                  │  │
│  │  - AIOrg         │◄────►│  - OrgManager    │◄────►│  - TaskEngine    │  │
│  │  - AINode        │      │  - OrgLoader     │      │  - TaskProcessor │  │
│  │  - AITask        │      │  - OrgExporter   │      │  - Delegator     │  │
│  │  - AIResponse    │      │                  │      │  - Aggregator    │  │
│  │  - AIHITLAction  │      └────────┬─────────┘      └────────┬─────────┘  │
│  └────────┬─────────┘               │                         │            │
│           │                         │                         │            │
│           │              ┌──────────▼─────────────────────────▼─────────┐  │
│           │              │                                               │  │
│           │              │              node_actor.py                    │  │
│           │              │                                               │  │
│           │              │  - AINodeActor                                │  │
│           │              │    - receive_task()                           │  │
│           │              │    - delegate_to_subordinates()               │  │
│           │              │    - receive_subordinate_response()           │  │
│           │              │    - aggregate_and_report()                   │  │
│           │              │                                               │  │
│           │              └───────────────────────────────────────────────┘  │
│           │                                                                  │
│           │              ┌──────────────────┐      ┌──────────────────┐    │
│           │              │  hitl_manager.py │      │   notifier.py    │    │
│           │              │                  │      │                  │    │
│           └─────────────►│  - HITLManager   │      │  - OrgNotifier   │    │
│                          │  - ReviewQueue   │◄────►│  - EmailChannel  │    │
│                          │  - ActionLogger  │      │  - TeamsChannel  │    │
│                          │                  │      │  - SlackChannel  │    │
│                          └──────────────────┘      └──────────────────┘    │
│                                                                              │
│  ┌──────────────────┐      ┌──────────────────┐                            │
│  │    db_ops.py     │      │    events.py     │                            │
│  │                  │      │                  │                            │
│  │  - AIORGDBOps    │      │  - AIorgEvents   │                            │
│  │  - save_org()    │      │  - TASK_CREATED  │                            │
│  │  - save_node()   │      │  - TASK_DELEGATED│                            │
│  │  - save_task()   │      │  - RESPONSE_RECV │                            │
│  │  - query_*()     │      │  - HITL_REQUIRED │                            │
│  └──────────────────┘      └──────────────────┘                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

External Dependencies:
  ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
  │  abhikarta.actor │      │ abhikarta.agent  │      │abhikarta.messaging│
  │                  │      │                  │      │                  │
  │  - ActorSystem   │      │  - AgentManager  │      │  - NotificationMgr│
  │  - BaseActor     │      │  - AgentRunner   │      │  - EmailSender   │
  │  - EventBus      │      │                  │      │  - TeamsSender   │
  └──────────────────┘      └──────────────────┘      └──────────────────┘
```

---

## 3. Detailed Component Architecture

### 3.1 Org Manager Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OrgManager Internal Structure                        │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────────────────┐
                    │          OrgManager              │
                    │                                  │
                    │  active_orgs: Dict[str, AIOrg]   │
                    │  node_actors: Dict[str, Actor]   │
                    │                                  │
                    └─────────────┬────────────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
          ▼                       ▼                       ▼
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│   OrgLifecycle   │   │   NodeRegistry   │   │  OrgSerializer   │
│                  │   │                  │   │                  │
│ - create()       │   │ - register()     │   │ - to_json()      │
│ - activate()     │   │ - unregister()   │   │ - from_json()    │
│ - pause()        │   │ - get_actor()    │   │ - validate()     │
│ - archive()      │   │ - list_nodes()   │   │                  │
└──────────────────┘   └──────────────────┘   └──────────────────┘

Activation Flow:
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  1. Load org from DB                                                        │
│                │                                                             │
│                ▼                                                             │
│  2. Validate structure (DAG check, root exists, etc.)                       │
│                │                                                             │
│                ▼                                                             │
│  3. Create AINodeActor for each node                                        │
│                │                                                             │
│                ▼                                                             │
│  4. Subscribe actors to event bus channels                                  │
│                │                                                             │
│                ▼                                                             │
│  5. Set org status to 'active'                                              │
│                │                                                             │
│                ▼                                                             │
│  6. Publish ORG_ACTIVATED event                                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Task Engine Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TaskEngine Internal Structure                         │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────────────────┐
                    │          TaskEngine              │
                    │                                  │
                    │  llm_facade: LLMFacade          │
                    │  event_bus: EventBus            │
                    │  org_manager: OrgManager        │
                    │                                  │
                    └─────────────┬────────────────────┘
                                  │
       ┌──────────────────────────┼──────────────────────────┐
       │                          │                          │
       ▼                          ▼                          ▼
┌────────────────┐      ┌────────────────┐      ┌────────────────┐
│ TaskProcessor  │      │   Delegator    │      │   Aggregator   │
│                │      │                │      │                │
│ - analyze()    │      │ - plan()       │      │ - collect()    │
│ - decide()     │      │ - assign()     │      │ - synthesize() │
│ - execute()    │      │ - distribute() │      │ - summarize()  │
└────────────────┘      └────────────────┘      └────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            PROMPT TEMPLATES                                  │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ TASK_ANALYSIS_PROMPT:                                                  │ │
│  │ You are {role_name} in an organization. You have received a task:      │ │
│  │ Title: {task_title}                                                    │ │
│  │ Description: {task_description}                                        │ │
│  │                                                                        │ │
│  │ Your subordinates are: {subordinate_list}                              │ │
│  │                                                                        │ │
│  │ Analyze this task and decide:                                          │ │
│  │ 1. Can you complete this yourself? (leaf nodes always yes)             │ │
│  │ 2. If not, how should it be decomposed for your subordinates?          │ │
│  │                                                                        │ │
│  │ Response format: {response_schema}                                     │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ AGGREGATION_PROMPT:                                                    │ │
│  │ You are {role_name}. You delegated subtasks to your team.              │ │
│  │ They have all responded. Here are their findings:                      │ │
│  │                                                                        │ │
│  │ {subordinate_responses}                                                │ │
│  │                                                                        │ │
│  │ Your task is to synthesize these into a coherent summary that:         │ │
│  │ - Extracts key findings from each subordinate                          │ │
│  │ - Identifies any conflicts or gaps                                     │ │
│  │ - Provides actionable conclusions                                      │ │
│  │ - Prepares this for your supervisor                                    │ │
│  │                                                                        │ │
│  │ Response format: {response_schema}                                     │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Node Actor State Machine

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AINodeActor State Machine                               │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────┐
                              │  IDLE   │
                              └────┬────┘
                                   │
                        receive_task()
                                   │
                                   ▼
                         ┌─────────────────┐
                         │   ANALYZING     │
                         │                 │
                         │ AI decides:     │
                         │ delegate or     │
                         │ complete self   │
                         └────────┬────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 │                                 │
         can_complete_self              needs_delegation
                 │                                 │
                 ▼                                 ▼
        ┌───────────────┐               ┌───────────────┐
        │   EXECUTING   │               │  DELEGATING   │
        │               │               │               │
        │ Process task  │               │ Create        │
        │ using AI      │               │ subtasks      │
        └───────┬───────┘               └───────┬───────┘
                │                               │
                │                               ▼
                │                      ┌───────────────┐
                │                      │   WAITING     │
                │                      │               │
                │                      │ Wait for all  │
                │                      │ subordinate   │
                │                      │ responses     │
                │                      └───────┬───────┘
                │                               │
                │                   all_responses_received
                │                               │
                │                               ▼
                │                      ┌───────────────┐
                │                      │  AGGREGATING  │
                │                      │               │
                │                      │ Synthesize    │
                │                      │ responses     │
                │                      └───────┬───────┘
                │                               │
                └───────────────┬───────────────┘
                                │
                    hitl_required?
                                │
              ┌─────────────────┴─────────────────┐
              │                                   │
            yes                                  no
              │                                   │
              ▼                                   │
     ┌────────────────┐                          │
     │ HITL_PENDING   │                          │
     │                │                          │
     │ Wait for human │                          │
     │ review         │                          │
     └───────┬────────┘                          │
             │                                   │
    approved/overridden                          │
             │                                   │
             └───────────────┬───────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  COMPLETING    │
                    │                │
                    │ Save response  │
                    │ Notify parent  │
                    │ Send notifs    │
                    └───────┬────────┘
                            │
                            ▼
                      ┌───────────┐
                      │   IDLE    │
                      └───────────┘
```

---

## 4. Data Flow Architecture

### 4.1 Task Submission Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Task Submission Sequence                              │
└─────────────────────────────────────────────────────────────────────────────┘

User        Web UI       API          TaskEngine    RootActor     EventBus
 │            │           │               │            │             │
 │──Submit───►│           │               │            │             │
 │ Task Form  │           │               │            │             │
 │            │──POST────►│               │            │             │
 │            │ /tasks    │               │            │             │
 │            │           │──submit_task─►│            │             │
 │            │           │               │            │             │
 │            │           │               │──create───►│             │
 │            │           │               │   task     │             │
 │            │           │               │            │             │
 │            │           │               │──dispatch─►│             │
 │            │           │               │   to actor │             │
 │            │           │               │            │──publish───►│
 │            │           │               │            │ TASK_CREATED │
 │            │           │               │            │             │
 │            │           │◄──task_id─────│            │             │
 │            │◄──202─────│               │            │             │
 │◄─Redirect──│ Accepted  │               │            │             │
 │ to monitor │           │               │            │             │
 │            │           │               │            │             │
```

### 4.2 Delegation and Aggregation Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Delegation & Aggregation Sequence                         │
└─────────────────────────────────────────────────────────────────────────────┘

CEO_Actor     TaskEngine     PM_Actor_1    PM_Actor_2    EventBus
    │             │              │              │            │
    │──process───►│              │              │            │
    │   task      │              │              │            │
    │             │──LLM call───►│              │            │
    │             │              │              │            │
    │◄─delegation─│              │              │            │
    │   plan      │              │              │            │
    │             │              │              │            │
    │──delegate──►│              │              │            │
    │             │──create      │              │            │
    │             │ subtasks     │              │            │
    │             │──dispatch───►│              │            │
    │             │   task 1     │              │            │
    │             │──────────────│──dispatch───►│            │
    │             │              │   task 2     │            │
    │             │              │              │──publish──►│
    │             │              │              │ DELEGATED  │
    │             │              │              │            │
    │  [WAITING]  │              │              │            │
    │             │              │              │            │
    │             │  [PM_Actor_1 processes...]  │            │
    │             │              │              │            │
    │             │◄─response────│              │            │
    │◄─response───│              │              │            │
    │  received   │              │              │            │
    │             │              │              │            │
    │             │  [PM_Actor_2 processes...]  │            │
    │             │              │              │            │
    │             │◄─────────────│──response────│            │
    │◄─response───│              │              │            │
    │  received   │              │              │            │
    │             │              │              │            │
    │──ALL       ─│              │              │            │
    │ RECEIVED   │              │              │            │
    │             │              │              │            │
    │──aggregate─►│              │              │            │
    │             │──LLM call───►│              │            │
    │             │  summarize   │              │            │
    │◄─summary────│              │              │            │
    │             │              │              │            │
    │──complete───│              │              │──publish──►│
    │   report    │              │              │ COMPLETED  │
    │             │              │              │            │
```

### 4.3 HITL Intervention Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HITL Intervention Sequence                           │
└─────────────────────────────────────────────────────────────────────────────┘

NodeActor    HITLManager   Database    Notifier    Human      WebSocket
    │            │            │           │          │            │
    │──queue────►│            │           │          │            │
    │ for review │            │           │          │            │
    │            │──save─────►│           │          │            │
    │            │            │           │          │            │
    │            │──notify───►│──────────►│          │            │
    │            │            │  (email)  │          │            │
    │            │            │           │          │            │
    │            │────────────│───────────│─────────►│            │
    │            │            │           │ realtime │ (push)     │
    │            │            │           │  update  │            │
    │            │            │           │          │            │
    │  [PAUSED]  │            │           │          │            │
    │            │            │           │          │            │
    │            │            │           │          │──view─────►│
    │            │            │           │          │            │
    │            │◄───────────│───────────│──────────│─override──│
    │            │            │           │          │            │
    │            │──log      ►│           │          │            │
    │            │  action    │           │          │            │
    │            │            │           │          │            │
    │◄─continue──│            │           │          │            │
    │ with new   │            │           │          │            │
    │ content    │            │           │          │            │
    │            │            │           │          │            │
    │  [RESUME]  │            │           │          │            │
    │            │            │           │          │            │
```

---

## 5. Integration Architecture

### 5.1 Integration with Existing Abhikarta Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Integration with Abhikarta Core                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────┐     ┌────────────────────────────┐
│        AI ORG              │     │      ACTOR SYSTEM          │
│                            │     │                            │
│  AINodeActor extends       │────►│  BaseActor                 │
│                            │     │  - receive()               │
│  Uses ActorSystem for      │◄────│  - send()                  │
│  actor lifecycle           │     │  - schedule()              │
│                            │     │                            │
└────────────────────────────┘     └────────────────────────────┘
            │                                   │
            │                                   │
            ▼                                   ▼
┌────────────────────────────┐     ┌────────────────────────────┐
│        EVENT BUS           │     │       LLM FACADE           │
│                            │     │                            │
│  AI ORG publishes/         │     │  Task analysis uses        │
│  subscribes to events      │     │  LLM for decisions         │
│                            │     │                            │
│  Channel: aiorg:{org_id}   │     │  Prompts defined in        │
│                            │     │  ai_org_prompts.py         │
└────────────────────────────┘     └────────────────────────────┘
            │                                   │
            │                                   │
            ▼                                   ▼
┌────────────────────────────┐     ┌────────────────────────────┐
│      AGENT MANAGER         │     │    NOTIFICATION MGR        │
│                            │     │                            │
│  Nodes can reference       │     │  AI ORG uses existing      │
│  existing agents for       │     │  notification channels     │
│  their AI capabilities     │     │  for alerts                │
│                            │     │                            │
└────────────────────────────┘     └────────────────────────────┘
            │
            │
            ▼
┌────────────────────────────┐
│       DATABASE FACADE      │
│                            │
│  AI ORG uses delegate      │
│  pattern for persistence   │
│                            │
│  AIORGDBOps implements     │
│  AI ORG specific queries   │
│                            │
└────────────────────────────┘
```

### 5.2 External Integration Points

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      External Integration Points                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           INBOUND                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. Task Submission API                                                      │
│     POST /api/aiorg/{org_id}/tasks                                          │
│     - External systems can submit tasks                                      │
│     - Webhook signature verification                                         │
│                                                                              │
│  2. Webhook Receiver                                                         │
│     POST /webhooks/aiorg/{org_id}                                           │
│     - Receive events from external systems                                   │
│     - Transform to internal task format                                      │
│                                                                              │
│  3. HITL API                                                                 │
│     POST /api/aiorg/hitl/{item_id}/action                                   │
│     - External HITL interfaces can interact                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           OUTBOUND                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. Email (SMTP / SendGrid)                                                 │
│     - Task completion notifications                                          │
│     - Final reports                                                          │
│     - HITL alerts                                                            │
│                                                                              │
│  2. Microsoft Teams                                                          │
│     - Webhook notifications                                                  │
│     - Adaptive cards with actions                                            │
│                                                                              │
│  3. Slack                                                                    │
│     - Webhook notifications                                                  │
│     - Interactive messages                                                   │
│                                                                              │
│  4. Custom Webhooks                                                          │
│     - POST to configured URLs                                                │
│     - Task completion, status changes                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Deployment Architecture

### 6.1 Single Instance Deployment

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Single Instance Deployment                               │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────────┐
                    │         Docker Container            │
                    │                                     │
                    │  ┌─────────────────────────────┐   │
                    │  │    Abhikarta Server         │   │
                    │  │                             │   │
                    │  │  - Flask App                │   │
                    │  │  - AI Org Module            │   │
                    │  │  - Actor System             │   │
                    │  │  - Event Bus (in-memory)    │   │
                    │  │  - WebSocket Server         │   │
                    │  │                             │   │
                    │  └─────────────────────────────┘   │
                    │              │                      │
                    │              ▼                      │
                    │  ┌─────────────────────────────┐   │
                    │  │    SQLite Database          │   │
                    │  │    (or external Postgres)   │   │
                    │  └─────────────────────────────┘   │
                    │                                     │
                    └─────────────────────────────────────┘
```

### 6.2 Scalable Deployment (Future)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Scalable Deployment (Future)                             │
└─────────────────────────────────────────────────────────────────────────────┘

              ┌─────────────────────────────────────────────┐
              │              Load Balancer                  │
              └─────────────────────┬───────────────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           │                        │                        │
           ▼                        ▼                        ▼
    ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
    │  Web Server  │        │  Web Server  │        │  Web Server  │
    │    (API)     │        │    (API)     │        │    (API)     │
    └──────┬───────┘        └──────┬───────┘        └──────┬───────┘
           │                       │                        │
           └───────────────────────┼────────────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │      Message Queue       │
                    │   (Redis / RabbitMQ)     │
                    └──────────────┬───────────┘
                                   │
           ┌───────────────────────┼───────────────────────┐
           │                       │                       │
           ▼                       ▼                       ▼
    ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
    │   Worker     │       │   Worker     │       │   Worker     │
    │ (AI Org      │       │ (AI Org      │       │ (AI Org      │
    │  Actors)     │       │  Actors)     │       │  Actors)     │
    └──────┬───────┘       └──────┬───────┘       └──────┬───────┘
           │                      │                       │
           └──────────────────────┼───────────────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │      PostgreSQL          │
                    │      (Primary)           │
                    └──────────────────────────┘
```

---

## 7. Security Architecture

### 7.1 Security Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Security Architecture                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: Authentication                                                     │
│  - Session-based authentication (existing)                                   │
│  - API key authentication for external calls                                 │
│  - HITL requires user authentication                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 2: Authorization                                                      │
│  - Role-based access (Admin, Manager, User)                                 │
│  - Org-level access control                                                  │
│  - HITL restricted to node's human mirror or admin                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 3: Data Protection                                                    │
│  - Encryption at rest (database encryption)                                  │
│  - Encryption in transit (HTTPS/TLS)                                         │
│  - PII minimization in logs                                                  │
│  - Sensitive field masking                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 4: Audit & Compliance                                                 │
│  - Immutable audit log                                                       │
│  - All HITL actions logged                                                   │
│  - Task history preserved                                                    │
│  - Configurable log retention                                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Performance Considerations

### 8.1 Performance Targets

| Metric | Target | Rationale |
|--------|--------|-----------|
| Org load time | < 2 sec | User experience |
| Task delegation | < 500ms | Real-time feel |
| Event propagation | < 100ms | Coordination |
| LLM response | < 30 sec | Model dependent |
| Database query | < 100ms | Scalability |

### 8.2 Optimization Strategies

1. **Connection Pooling**: Database and LLM connections
2. **Event Batching**: Batch similar events
3. **Caching**: Org structure, agent configs
4. **Async Processing**: All LLM calls async
5. **Pagination**: Large result sets

---

## 9. Monitoring and Observability

### 9.1 Key Metrics

- **Org Metrics**: Active orgs, nodes per org, tasks per hour
- **Task Metrics**: Completion time, delegation depth, failure rate
- **HITL Metrics**: Queue length, response time, override rate
- **System Metrics**: CPU, memory, DB connections, LLM latency

### 9.2 Logging Strategy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Logging Strategy                                    │
└─────────────────────────────────────────────────────────────────────────────┘

Level: INFO
- Org lifecycle events (create, activate, pause)
- Task state transitions
- HITL actions

Level: DEBUG
- Event bus messages
- Actor state changes
- LLM request/response summaries

Level: ERROR
- Task failures
- LLM errors
- Integration failures

Level: AUDIT (custom)
- HITL interventions
- Data modifications
- Access events
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2025-12-30 | Abhikarta Team | Initial draft |

