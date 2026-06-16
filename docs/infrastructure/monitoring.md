---
title: "Monitoring & Observability"
sidebar_position: 4
---

The OffloadSecurity CSPM platform utilizes a comprehensive monitoring stack designed for high availability and deep visibility into security scanning operations. The stack follows a "sidecar" pattern where monitoring services (Prometheus, Grafana, Loki, Promtail) run alongside the core application to collect metrics, structured logs, and system health data without impacting scanning performance.

## Monitoring Stack Architecture

The observability architecture is composed of four primary layers: metrics collection, log aggregation, system integrity monitoring, and automated data reconciliation.

### Data Flow & Component Interaction

The diagram below illustrates how system telemetry flows from the FastAPI backend and Celery workers to the centralized Grafana dashboard.

**Title: Observability Data Flow**
```mermaid
graph TD
    subgraph "ApplicationSpace"
        [FastAPI_App] -- "StructuredJSONLogs" --> [Log_Files]
        [FastAPI_App] -- "PrometheusMetrics" --> [Metrics_Endpoint]
        [Celery_Workers] -- "TaskMetrics" --> [Metrics_Endpoint]
        [SystemIntegrityMonitor] -- "Status" --> [Health_Endpoints]
    end

    subgraph "CollectionLayer"
        [Promtail] -- "Scrapes" --> [Log_Files]
        [Prometheus] -- "Scrapes" --> [Metrics_Endpoint]
    end

    subgraph "StorageAndVisualization"
        [Promtail] -- "Push" --> [Loki]
        [Prometheus] -- "Alerting" --> [AlertManager]
        [Loki] -- "Query" --> [Grafana]
        [Prometheus] -- "Query" --> [Grafana]
    end

    [Grafana] -- "Displays" --> ["offload-operations-Dashboard"]
```

## Structured Logging & Credential Scrubbing

The platform implements a `StructuredFormatter` that outputs logs in JSON format for ingestion by Loki.

### Security-First Logging
A critical feature of the logging subsystem is global credential scrubbing. The `_scrub_credentials` function uses broad regex patterns to redact sensitive data from log messages, including:
*   AWS Access Keys (AKIA...)
*   Fernet Tokens
*   Bearer Tokens and GCP Private Keys

The `SecurityLogger` class provides specialized methods for logging authentication attempts, authorization failures, and rate limit violations with standardized metadata.

## Health Routes & Integrity Monitoring

The platform provides a multi-tiered health check system through dedicated health endpoints and the `SystemIntegrityMonitor`.

### System Integrity Monitor
The `SystemIntegrityMonitor` detects when subsystems are running in degraded or fallback modes. This is critical for identifying "silent failures" where the system continues to operate but with reduced efficiency.

| Subsystem | Optimal Mode | Degraded Mode | Impact |
| :--- | :--- | :--- | :--- |
| **Session Storage** | Redis | MongoDB / In-Memory | Slower lookups; session loss on restart |
| **Cache Backend** | Redis | In-Memory | No cross-worker sharing |
| **Security Tools** | Docker Images Present | Missing | Scan failures for specific tools (Trivy, Grype, Syft) |
| **Database** | `CSPMDatabaseManager` | Fallback Client | Potential connection instability |
| **SCF Baseline** | Excel-parsed (1,451) | Hardcoded (~80) | Reduced compliance control coverage |

### Health Endpoints
*   **Readiness Probe**: `/health/ready` verifies critical dependencies like MongoDB and Redis.
*   **Detailed Status**: `/health/status` returns comprehensive component status including security tool availability (Syft, Grype, Trivy) checked via subprocess calls.
*   **Basic Metrics**: `/health/metrics` returns simple application counters like active user sessions.

## Database Index Management

Optimal query performance is maintained via the `IndexManagementService`.

**Title: Code-to-Database Index Mapping**
```mermaid
graph LR
    subgraph "IndexManagementService"
        [IMS_Class] -- "defines" --> [Index_Map]
    end

    subgraph "MongoDB_Collections"
        [Index_Map] -- "idx_dedup_key_unique" --> [cspm_findings_Coll]
        [Index_Map] -- "idx_run_id_unique" --> [scan_runs_Coll]
        [Index_Map] -- "idx_team_id" --> [vulnerability_occurrences_Coll]
    end
```

The system ensures critical indexes exist for high-traffic collections:
*   **CSPM Findings**: Unique index on `dedup_key` prevents race condition duplicates during ingestion.
*   **Vulnerability Occurrences**: Indexed by `team_id`, `status`, and `risk_score` to support the unified vulnerability dashboard.
*   **Cloud Accounts**: Indexed by `user_id` and `provider` for rapid account retrieval.

## Data Consistency & Watchdog

The `DataSyncWatchdogService` acts as a background monitor to ensure data remains consistent across the platform's multi-database architecture.

### Automated Reconciliation Logic
The watchdog dispatches existing sync tasks when it detects state drift:
1.  **Stuck Scan Detection**: Identifies scans in `RUNNING` state longer than `STUCK_SCAN_HOURS` (4 hours).
2.  **Vulnerability Sync**: Checks if findings from CSPM, K8s, and Container modules are propagated to the `vulnerability_occurrences` collection.
3.  **Compliance Freshness**: Triggers a refresh if compliance data is older than `STALE_COMPLIANCE_HOURS` (5 hours).

**Title: Watchdog Entity Mapping**
```mermaid
graph TD
    [DataSyncWatchdogService] -- "inspects" --> ["cspm_cloud_security.findings"]
    [DataSyncWatchdogService] -- "inspects" --> ["cspm_orchestration.scan_runs"]
    [DataSyncWatchdogService] -- "triggers" --> [VulnerabilitySyncService]
    
    [VulnerabilitySyncService] -- "sync_all" --> [vulnerability_occurrences]

    style [DataSyncWatchdogService] stroke-width:2px
    style [VulnerabilitySyncService] stroke-width:2px
```

## Build & Runtime Validation

The build validation script provides a dual-mode health check to ensure the system is correctly configured before and during execution.

1.  **Build-time Checks**: Validates critical Python dependency availability (e.g., `boto3`, `motor`, `fastapi`) and SCF control data integrity.
2.  **Runtime Checks**: Verifies live connectivity to MongoDB, Redis, and Docker engine.

---