---
title: "Audit Trail & Webhook Events"
sidebar_position: 4
---

This section documents the platform's observability and event-driven architecture. It covers the immutable audit trail for user actions, the platform event bus for internal reactivity, the webhook subsystem for external integrations, and the automation of evidence collection and risk management.

## Platform Audit Trail

The platform implements a unified audit trail via the `AuditTrailMiddleware`. This middleware captures every authenticated API request and persists it to an immutable MongoDB collection named `event_bus_audit_log` `backend/core/event_bus.py:185-186`. This system provides compliance-ready logs that answer who did what, when, and with what outcome `backend/middleware/audit_trail.py:8-13`.

### AuditTrailMiddleware Implementation
The middleware operates as a `BaseHTTPMiddleware` within the FastAPI pipeline `backend/middleware/audit_trail.py:155-156`. It classifies actions, redacts sensitive data, and performs asynchronous background writes to minimize latency.

*   **Action Classification**: Uses the `_classify_action` function to map HTTP methods and path patterns to human-readable strings (e.g., `POST /api/auth/login` becomes `user.login`) `backend/middleware/audit_trail.py:66-116`.
*   **Recursive Body Redaction**: The `_redact_body` function recursively traverses request bodies to scrub fields like `password`, `secret`, `token`, `api_key`, and `mfa_token` `backend/middleware/audit_trail.py:119-144`. This prevents sensitive credentials buried in nested objects (e.g., within configuration payloads) from leaking into the audit store.
*   **Performance**: To prevent blocking the response, the database write is scheduled as an `asyncio.create_task` after the response has been generated `backend/middleware/audit_trail.py:238`.
*   **Exclusion Rules**: Noisy paths (e.g., `/api/health`, `/api/sse/`) and standard `GET` requests (except for reports/exports) are excluded to reduce log volume `backend/middleware/audit_trail.py:40-45`, `backend/middleware/audit_trail.py:182-183`.

**Audit Logging Data Flow**
```mermaid
sequenceDiagram
    participant C as "Client"
    participant M as "AuditTrailMiddleware"
    participant A as "AuthService (auth_system.py)"
    participant R as "Route Handler"
    participant DB as "MongoDB (event_bus_audit_log)"

    C->>M: "HTTP Request (POST /api/risks)"
    M->>A: "get_user_from_session()"
    A-->>M: "User (request.state.user)"
    M->>M: "_classify_action() -> 'risk.post'"
    M->>M: "_redact_body(request_payload)"
    M->>R: "call_next(request)"
    R-->>M: "Response (201 Created)"
    Note over M,DB: "Async background task"
    M->>DB: "insert_one(audit_doc)"
    M-->>C: "HTTP Response"
```
**Sources:** `backend/middleware/audit_trail.py:66-144`, `backend/middleware/audit_trail.py:155-245`, `backend/core/event_bus.py:185-186`

## Platform Event Bus (Internal)

The `EventBus` is the central nervous system for cross-module reactivity, utilizing Redis Pub/Sub for real-time delivery and MongoDB for persistence `backend/core/event_bus.py:4-10`.

### Event Architecture
*   **Event Types**: Canonical constants are defined in `EventTypes`, covering `SCAN_COMPLETED`, `FINDING_CREATED`, `SLA_BREACHED`, and `COMPLIANCE_DRIFT_DETECTED` `backend/core/event_bus.py:64-172`.
*   **Subscribers**: The `event_subscribers.py` module registers handlers that route events to notifications (Email/Slack/Teams), integration tickets (Jira), and real-time SSE streams `backend/core/event_subscribers.py:4-14`.
*   **SSE Real-time Stream**: The `stream_platform_events` route in `sse_routes.py` allows frontend clients to subscribe to specific channels (e.g., `?channels=scan,finding`) for live updates `backend/routes/sse_routes.py:171-184`.

**Sources:** `backend/core/event_bus.py:12-45`, `backend/core/event_subscribers.py:37-140`, `backend/routes/sse_routes.py:76-168`

## Webhook Security & Inbound Ingestion

The platform accepts scan results from external tools via secure webhook endpoints `backend/routes/webhook_routes.py:2-4`.

### Webhook Security Schemes
The `WebhookSecurityService` supports two versions of HMAC authentication to ensure integrity and prevent replay attacks `backend/services/webhook_security_service.py:5-15`:

| Feature | v1 (Legacy) | v2 (Current) |
| :--- | :--- | :--- |
| **Location** | Query Parameters (`sig`, `ts`) | Headers (`X-Webhook-Signature`, `X-Webhook-Timestamp`) |
| **Body Binding** | No (Vulnerable to substitution) | Yes (HMAC includes SHA256 of body) |
| **Replay Protection** | `WebhookReplayCache` (5 min TTL) | `WebhookReplayCache` (5 min TTL) |

*   **v2 Signature Logic**: The signature is computed as `HMAC(secret, "v1:timestamp:scan_id:tool_name:body_hash")` where the body hash is a SHA256 hexdigest of the raw bytes `backend/services/webhook_security_service.py:111-127`.
*   **Replay Protection**: The `WebhookReplayCache` stores `(timestamp, signature)` pairs to prevent the same signature from being used twice within the TTL window `backend/services/webhook_security_service.py:57-98`.
*   **Ingestion**: Validated payloads are passed to the `external_scanner.receive_scan_result` for processing `backend/routes/webhook_routes.py:144`.

**Sources:** `backend/routes/webhook_routes.py:25-112`, `backend/services/webhook_security_service.py:117-186`

## Evidence Automation & Risk Exceptions

The platform automates the GRC lifecycle by wiring evidence collection to platform events and providing formal risk exception workflows.

### Evidence Auto-Trigger Service
The `EvidenceAutoTriggerService` eliminates manual evidence collection by reacting to `EventTypes` `backend/services/evidence_auto_trigger_service.py:4-11`.
*   **Scan Completion**: Triggers `on_scan_completed`, which delegates to specific collectors (CSPM, K8s, Container, etc.) based on the `scan_type` `backend/services/evidence_auto_trigger_service.py:45-91`.
*   **Freshness Monitoring**: A weekly Celery task `check_evidence_freshness` uses `_is_evidence_fresh` to identify expiring evidence and alert users `backend/tasks/sla_enforcement_tasks.py:182-191`, `backend/services/evidence_intelligence_service.py:23-58`.

### Risk Exception & KRI Monitoring
*   **Risk Exceptions**: The `RiskExceptionService` manages the lifecycle of suppressed findings, including creation, admin approval, and expiration tracking `backend/services/risk_exception_service.py:43-114`.
*   **KRI Monitoring**: The `KRIMonitoringService` evaluates Key Risk Indicators (e.g., `critical_vuln_count`, `sla_breach_rate`) against thresholds and emits `RISK_THRESHOLD_BREACHED` events when limits are crossed `backend/services/kri_and_assignment_service.py:81-106`, `backend/services/kri_and_assignment_service.py:155-172`.

**Entity Space Mapping**
```mermaid
graph TD
    subgraph "Core Security (Audit/Webhook)"
        ATM["AuditTrailMiddleware (audit_trail.py)"]
        WSS["WebhookSecurityService (webhook_security_service.py)"]
        WRC["WebhookReplayCache"]
    end

    subgraph "Event-Driven Automation"
        EB["EventBus (event_bus.py)"]
        EATS["EvidenceAutoTriggerService (evidence_auto_trigger_service.py)"]
        KRIS["KRIMonitoringService (kri_and_assignment_service.py)"]
    end

    subgraph "Data Store (MongoDB)"
        EBAL["event_bus_audit_log"]
        KS["kri_snapshots"]
        RES["risk_exceptions"]
    end

    ATM --> EBAL
    EB -- "persists" --> EBAL
    WSS --> WRC
    EATS -- "subscribes" --> EB
    KRIS -- "snapshots" --> KS
    KRIS -- "publishes" --> EB
```

**Sources:** `backend/services/evidence_auto_trigger_service.py:45-130`, `backend/services/kri_and_assignment_service.py:28-78`, `backend/services/risk_exception_service.py:10-64`, `backend/tasks/sla_enforcement_tasks.py:51-112`

---