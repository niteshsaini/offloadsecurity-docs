---
title: "Background Tasks & Scheduler"
sidebar_position: 3
---

The OffloadSecurity CSPM platform utilizes a distributed task queue system based on **Celery** and **Redis**, complemented by a **Unified Lifecycle Scheduler** built on **APScheduler**. This architecture ensures that long-running security scans, compliance audits, and system maintenance tasks do not block the main application thread while providing robust persistence and retry logic.

## Celery Application Configuration

The Celery application is the primary engine for asynchronous execution. It is configured to use **Redis** as the message broker and **MongoDB** as the result backend, specifically targeting the `cspm_orchestration` database `backend/celery_app.py:14-23`.

### Task Queues & Routing
To prevent resource contention between lightweight maintenance and heavy scanning tasks, the platform implements strict queue isolation `backend/celery_app.py:75-206`:

| Queue | Purpose | Key Tasks |
| :--- | :--- | :--- |
| `scans` | Primary orchestration | `execute_cloud_scan`, `run_scheduled_scans` |
| `discovery` | Resource inventory | `execute_steampipe_discovery`, `execute_hybrid_asset_discovery`, `execute_kubernetes_cluster_discovery` |
| `compliance` | Posture assessment | `execute_prowler_scan`, `run_compliance_refresh`, `snapshot_all_teams` |
| `threat_feeds` | Intelligence updates | `fetch_all_enabled_feeds`, `cleanup_old_indicators` |
| `sync` | Data consistency | `sync_all_teams_vulnerabilities`, `sync_vulnerabilities_for_team` |
| `maintenance` | System hygiene | `run_retention_cycle`, `check_sla_breaches_all_teams`, `run_data_sync_watchdog` |

### Celery Database Management
A critical architectural pattern in the platform is the use of `CeleryDatabaseManager`. Standard database singletons (like `CSPMDatabaseManager`) are bound to the FastAPI main process event loop. Because Celery workers create and close a new event loop for every task, using singletons leads to `RuntimeError: Event loop is closed` `backend/core/celery_database.py:5-13`.

The `CeleryDatabaseManager` creates a **fresh** `AsyncIOMotorClient` for every task, ensuring the connection is bound to the current worker loop `backend/core/celery_database.py:62-74`.

**Sources**: `backend/celery_app.py:14-206`, `backend/core/celery_database.py:1-135`

---

## Unified Lifecycle Scheduler

The `UnifiedLifecycleSchedulerService` manages the temporal aspects of security entities, consolidating scans, assessments, evidence collection, and reports `backend/services/unified_lifecycle_scheduler_service.py:1-12`. It uses **APScheduler** with a `MongoDBJobStore` to ensure that schedules persist across service restarts `backend/services/unified_lifecycle_scheduler_service.py:10-33`.

### Schedule Types & Statuses
The scheduler supports four distinct triggers `backend/services/unified_lifecycle_scheduler_service.py:54-60`:
1.  **CRON**: Complex calendar-based schedules (e.g., "0 2 * * *") `backend/services/unified_lifecycle_scheduler_service.py:56`.
2.  **INTERVAL**: Simple recurring timers (e.g., every 24 hours) `backend/services/unified_lifecycle_scheduler_service.py:57`.
3.  **EXPIRY_BASED**: Triggers based on entity age, such as a risk assessment expiring `backend/services/unified_lifecycle_scheduler_service.py:58, 110-123`.
4.  **ONE_TIME**: Specific future timestamps `backend/services/unified_lifecycle_scheduler_service.py:59`.

### Zombie Schedule Prevention & Overlap Policies
To prevent system exhaustion and "stampede" conditions where multiple instances of the same long-running scan overlap, the scheduler implements an `OverlapPolicy` `backend/services/unified_lifecycle_scheduler_service.py:85-90`:
- **SKIP**: If a previous run is still active, the new trigger is ignored `backend/services/unified_lifecycle_scheduler_service.py:87`.
- **QUEUE**: Queues the new run to start after the current one finishes `backend/services/unified_lifecycle_scheduler_service.py:88`.
- **CANCEL_PREVIOUS**: Terminates the running job and starts a fresh one `backend/services/unified_lifecycle_scheduler_service.py:89`.

### Implementation Diagram: Scheduler to Code Entities
This diagram illustrates how the `UnifiedLifecycleSchedulerService` interacts with the Celery task infrastructure and the database layer.

Title: "Scheduler and Task Execution Mapping"
```mermaid
graph TD
    subgraph "Frontend_Space"
        ULS_UI["UnifiedLifecycleScheduler_UI"]
    end

    subgraph "Backend_Service_Space"
        ULS_SVC["UnifiedLifecycleSchedulerService"]
        APS["AsyncIOScheduler"]
        MJS["MongoDBJobStore"]
    end

    subgraph "Worker_Space"
        CAPP["celery_app"]
        NST["tasks.native_scan_tasks"]
        SLA["tasks.sla_enforcement_tasks"]
        CDM["CeleryDatabaseManager"]
        CTASKS["tasks.cloud_scan_tasks"]
    end

    ULS_UI -->|POST_api_unified_scheduler_schedules| ULS_SVC
    ULS_SVC -->|".add_job()"| APS
    APS -->|Persists| MJS
    APS -->|".send_task()"| CAPP
    
    CAPP -->|"dispatch"| NST
    CAPP -->|"dispatch"| SLA
    CAPP -->|"dispatch"| CTASKS
    
    NST -->|Uses| CDM
    SLA -->|Uses| CDM
    CTASKS -->|Uses| CDM
```
**Sources**: `backend/services/unified_lifecycle_scheduler_service.py:1-114`, `backend/tasks/cloud_scan_tasks.py:52-60`, `backend/core/celery_database.py:38-45`

---

## Cloud Scan Orchestration Tasks

### Execution Flow
The `execute_cloud_scan` task is the primary entry point for cloud security assessments. It manages the lifecycle of a `ScanRun` `backend/tasks/cloud_scan_tasks.py:60-72`.

1.  **Initialization**: Reuses a single event loop per `ForkPoolWorker` process but creates a fresh `AsyncIOMotorClient` to avoid loop conflicts `backend/tasks/cloud_scan_tasks.py:40-50, 81-88`.
2.  **Status Mirroring**: Updates the unified Scan Results store via `mirror_to_unified_scan_results` so the scan appears in the "running" tab of the UI `backend/tasks/cloud_scan_tasks.py:114-117`.
3.  **Sub-Job Dispatch**: Dispatches lightweight discovery jobs (Steampipe) and heavy compliance jobs (Prowler) `backend/tasks/cloud_scan_tasks.py:132-170`.
4.  **Batching & Staggering**: Compliance jobs are staggered using a `countdown` based on `REGION_BATCH_SIZE` to prevent API rate limiting `backend/tasks/cloud_scan_tasks.py:125-130, 184-188`.

### Native Security Scans
The platform executes "native" scans (Web/ZAP, Network/Nmap, SSL/testssl) through dedicated Celery tasks in `tasks.native_scan_tasks` `backend/celery_app.py:203-206`. These tasks use a fresh database client via `CeleryDatabaseManager` to ensure the Motor client is always bound to the correct event loop `backend/core/celery_database.py:12-13`.

**Sources**: `backend/tasks/cloud_scan_tasks.py:40-190`, `backend/services/cloud_scan_orchestration_service.py:24-40`, `backend/celery_app.py:203-206`

---

## Maintenance & Watchdog Tasks

### Data Sync Watchdog
The `DataSyncWatchdogService` periodically monitors data consistency across platform modules `backend/services/data_sync_watchdog_service.py:4-12`.
- **Stuck Scan Detection**: Identifies scans running longer than `STUCK_SCAN_HOURS` (4 hours) `backend/services/data_sync_watchdog_service.py:41, 157`.
- **Reconciliation**: When a mismatch is detected, it dispatches the appropriate existing sync task (e.g., `compliance_refresh`, `vulnerability_sync`) `backend/services/data_sync_watchdog_service.py:14-16`.

### Vulnerability Sync
The `VulnerabilitySyncService` synchronizes findings from CSPM, Kubernetes, and Container modules into the unified Vulnerability Management system `backend/services/vulnerability_sync_service.py:4-11`.
- **Source Aggregation**: Pulls from `cspm_findings`, `k8s_findings`, and `container_scans` `backend/services/vulnerability_sync_service.py:55-66`.
- **Deduplication**: Uses a stable `dedup_key` to prevent duplicate occurrences during sync `backend/services/vulnerability_sync_service.py:180-185`.

### Data Flow Diagram: Ingestion and Sync
Title: "Finding Ingestion and Sync Flow"
```mermaid
graph LR
    subgraph "Scan_Execution"
        Prowler["tasks.cloud_scan_tasks.execute_prowler_scan"]
        Trivy["EnhancedContainerSecurityService"]
    end

    subgraph "Unified_Storage"
        VOC["vulnerability_occurrences"]
        CDBM["CeleryDatabaseManager"]
    end

    subgraph "Maintenance_Layer"
        DSW["DataSyncWatchdogService"]
        VSS["VulnerabilitySyncService"]
    end

    Prowler -->|Findings| VSS
    Trivy -->|Scan_Results| VSS
    
    VSS -->|Sync| VOC
    DSW -->|Trigger_Sync| VSS
    
    Prowler -.->|Uses| CDBM
    VSS -.->|Uses| CDBM
```
**Sources**: `backend/services/data_sync_watchdog_service.py:133-172`, `backend/services/vulnerability_sync_service.py:31-152`, `backend/core/celery_database.py:38-50`, `backend/services/enhanced_container_security_service.py:50-109`

---