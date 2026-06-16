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
        [SystemIntegrityMonitor] -- "Status" --> [Health_Routes]
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
Sources: ``backend/services/system_integrity_monitor.py:1-24``, ``backend/routes/health_routes.py:17-19``, ``backend/core/structured_logging.py:54-115``

## Structured Logging & Credential Scrubbing

The platform implements a `StructuredFormatter` ``backend/core/structured_logging.py:54-55`` that outputs logs in JSON format for ingestion by Loki. 

### Security-First Logging
A critical feature of the logging subsystem is global credential scrubbing ``backend/core/structured_logging.py:21-25``. The `_scrub_credentials` function ``backend/core/structured_logging.py:40-44`` uses broad regex patterns to redact sensitive data from log messages, including:
*   AWS Access Keys (AKIA...) ``backend/core/structured_logging.py:28-28``
*   Fernet Tokens ``backend/core/structured_logging.py:31-32``
*   Bearer Tokens and GCP Private Keys ``backend/core/structured_logging.py:34-36``

The `SecurityLogger` class ``backend/core/structured_logging.py:118-121`` provides specialized methods for logging authentication attempts, authorization failures, and rate limit violations with standardized metadata ``backend/core/structured_logging.py:124-182``.

Sources: ``backend/core/structured_logging.py:1-115``, ``backend/core/structured_logging.py:118-200``

## Health Routes & Integrity Monitoring

The platform provides a multi-tiered health check system through `health_routes.py` and the `SystemIntegrityMonitor`.

### System Integrity Monitor
The `SystemIntegrityMonitor` class ``backend/services/system_integrity_monitor.py:68-76`` detects when subsystems are running in degraded or fallback modes. This is critical for identifying "silent failures" where the system continues to operate but with reduced efficiency.

| Subsystem | Optimal Mode | Degraded Mode | Impact |
| :--- | :--- | :--- | :--- |
| **Session Storage** | Redis | MongoDB / In-Memory | Slower lookups; session loss on restart ``backend/services/system_integrity_monitor.py:142-173`` |
| **Cache Backend** | Redis | In-Memory | No cross-worker sharing ``backend/services/system_integrity_monitor.py:180-189`` |
| **Security Tools** | Docker Images Present | Missing | Scan failures for specific tools (Trivy, Grype, Syft) ``backend/services/system_integrity_monitor.py:96-96`` |
| **Database** | `CSPMDatabaseManager` | Fallback Client | Potential connection instability ``backend/services/system_integrity_monitor.py:93-93`` |
| **SCF Baseline** | Excel-parsed (1,451) | Hardcoded (~80) | Reduced compliance control coverage ``backend/services/system_integrity_monitor.py:13-13`` |

### Health Endpoints
*   **Readiness Probe**: `/health/ready` verifies critical dependencies like MongoDB and Redis ``backend/routes/health_routes.py:129-154``.
*   **Detailed Status**: `/health/status` returns comprehensive component status including security tool availability (Syft, Grype, Trivy) checked via subprocess calls ``backend/routes/health_routes.py:164-189``.
*   **Basic Metrics**: `/health/metrics` returns simple application counters like active user sessions ``backend/routes/health_routes.py:199-212``.

Sources: ``backend/services/system_integrity_monitor.py:1-132``, ``backend/routes/health_routes.py:1-198``

## Database Index Management

Optimal query performance is maintained via the `IndexManagementService` ``backend/services/index_management_service.py:20-25`` and `database_indexes.py` ``backend/services/database_indexes.py:1-4``.

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

    [IMS_Class] --> `backend/services/index_management_service.py:20-25`
    [cspm_findings_Coll] --> `backend/services/database_indexes.py:101-106`
    [scan_runs_Coll] --> `backend/services/database_indexes.py:160-164`
```

The system ensures critical indexes exist for high-traffic collections:
*   **CSPM Findings**: Unique index on `dedup_key` prevents race condition duplicates during ingestion ``backend/services/database_indexes.py:101-107``.
*   **Vulnerability Occurrences**: Indexed by `team_id`, `status`, and `risk_score` to support the unified vulnerability dashboard ``backend/services/index_management_service.py:94-99``.
*   **Cloud Accounts**: Indexed by `user_id` and `provider` for rapid account retrieval ``backend/services/index_management_service.py:43-49``.

Sources: ``backend/services/index_management_service.py:20-107``, ``backend/services/database_indexes.py:1-170``

## Data Consistency & Watchdog

The `DataSyncWatchdogService` ``backend/services/data_sync_watchdog_service.py:34-38`` acts as a background monitor to ensure data remains consistent across the platform's multi-database architecture.

### Automated Reconciliation Logic
The watchdog dispatches existing sync tasks when it detects state drift:
1.  **Stuck Scan Detection**: Identifies scans in `RUNNING` state longer than `STUCK_SCAN_HOURS` (4 hours) ``backend/services/data_sync_watchdog_service.py:41-41``.
2.  **Vulnerability Sync**: Checks if findings from CSPM, K8s, and Container modules are propagated to the `vulnerability_occurrences` collection ``backend/services/vulnerability_sync_service.py:76-152``.
3.  **Compliance Freshness**: Triggers a refresh if compliance data is older than `STALE_COMPLIANCE_HOURS` (5 hours) ``backend/services/data_sync_watchdog_service.py:42-42``.

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
Sources: ``backend/services/data_sync_watchdog_service.py:1-172``, ``backend/services/vulnerability_sync_service.py:31-75``

## Build & Runtime Validation

The `validate_build.py` script provides a dual-mode health check to ensure the system is correctly configured before and during execution ``backend/scripts/validate_build.py:1-16``.

1.  **Build-time Checks**: Validates critical Python dependency availability (e.g., `boto3`, `motor`, `fastapi`) ``backend/scripts/validate_build.py:61-101`` and SCF control data integrity ``backend/scripts/validate_build.py:30-47``.
2.  **Runtime Checks**: Verifies live connectivity to MongoDB ``backend/scripts/validate_build.py:154-166``, Redis ``backend/scripts/validate_build.py:169-177``, and Docker engine ``backend/scripts/validate_build.py:194-204``.

Sources: ``backend/scripts/validate_build.py:1-204``

---