---
title: "Database Architecture"
sidebar_position: 2
---

The OffloadSecurity CSPM platform utilizes a modular multi-database architecture powered by MongoDB. This design ensures data isolation between functional modules (e.g., Cloud Security, Risk Management, Assessments), optimizes query performance through specialized indexing, and provides a scalable foundation for the platform's asynchronous scanning engine `backend/core/database.py:10-51`.

## Modular Database Strategy

The system distributes data across 14 distinct MongoDB databases. This approach allows for granular backup strategies, independent scaling, and prevents a single large collection from impacting the performance of unrelated services `backend/core/database.py:28-51`.

### Database Registry
The `DatabaseRegistry` class serves as the single source of truth for database names and purposes across the platform `backend/core/database_registry.py:2-11`. It maps functional areas to specific database constants and maintains a registry of deprecated databases (e.g., `cspm_platform_core`) to ensure legacy data is correctly mapped to the current `PLATFORM` store `backend/core/database_registry.py:38-230`.

| Database Name (Default) | Registry Constant | Primary Responsibility |
|:---|:---|:---|
| `cspm_platform` | `PLATFORM` | Core data: users, sessions, audit logs, and global templates `backend/core/database_registry.py:39-49`. |
| `cspm_cloud_security` | `CLOUD_SECURITY` | Consolidated cloud accounts, Prowler findings, and compliance scores `backend/core/database_registry.py:52-59`. |
| `cspm_cloud_assets` | `CLOUD_ASSETS` | Asset inventory from Steampipe and discovery history `backend/core/database_registry.py:61-67`. |
| `cspm_orchestration` | `ORCHESTRATION` | Scan orchestration: `scan_runs`, `scan_jobs`, and `sub_jobs` `backend/core/database_registry.py:69-76`. |
| `cspm_vulnerabilities` | `VULNERABILITIES` | Unified vulnerability catalog and occurrence lifecycle `backend/core/database_registry.py:78-86`. |
| `cspm_risk_management` | `RISK_MANAGEMENT` | Risk register, treatment plans, KRIs, and scenarios `backend/core/database_registry.py:99-108`. |
| `cspm_assessments` | `ASSESSMENTS` | Interactive assessments and completion progress `backend/core/database_registry.py:111-116`. |
| `cspm_container_registries` | `CONTAINER_REGISTRY` | Registry metadata, repository sync status, and image discovery cache `backend/core/container_registry_database.py:28-31`. |
| `cspm_security_scans` | `SECURITY_SCANS` | Native scans: Nuclei, SSL/TLS, ZAP, and Header results `backend/core/database_registry.py:135-139`. |
| `cspm_threat_intelligence` | `THREAT_INTELLIGENCE` | Indicators (IoC), CISA KEV feeds, and correlations `backend/core/database_registry.py:141-154`. |
| `cspm_ai_governance` | `AI_GOVERNANCE` | AI model registry, bias tests, and EU AI Act assessments `backend/core/database_registry.py:157-164`. |
| `cspm_integrations` | `INTEGRATIONS` | Connection status, health monitoring, and wizard sessions `backend/core/integration_monitoring_database.py:25-26`. |
| `cspm_knowledge_base` | `KNOWLEDGE_BASE` | Document embeddings and semantic search cache `backend/core/knowledge_base_database.py:25`. |
| `cspm_bia` | `BIA` | Business impact analyses and exercises `backend/core/database_registry.py:119-124`. |

**Sources:** `backend/core/database_registry.py:38-214`, `backend/core/database.py:28-51`, `backend/core/container_registry_database.py:28-31`, `backend/core/integration_monitoring_database.py:25-26`, `backend/core/knowledge_base_database.py:25`

## Connection Management

The platform employs specialized managers to handle different execution contexts, particularly for asynchronous API routes versus long-running background tasks.

### CSPMDatabaseManager
The primary manager for the FastAPI application. It maintains a mapping of module names to `AsyncIOMotorDatabase` instances `backend/core/database.py:10-14`. It facilitates cross-module data relationships via `create_cross_module_reference`, which stores links in the `core` database (mapping to `cspm_platform`) to maintain referential integrity across logical boundaries `backend/core/database.py:129-163`.

### CeleryDatabaseManager (Loop-Aware Pattern)
Database singletons bound to the FastAPI event loop fail when accessed within Celery workers, which create/close a new event loop for every task execution `backend/core/container_registry_database.py:36-39`.

The system solves this by:
1.  Creating a **fresh** `AsyncIOMotorClient` for task execution if the loop ID has changed `backend/core/container_registry_database.py:42-47`.
2.  Using the `get_async_client()` singleton factory to ensure that while the database handle is fresh, the underlying connection pool is reused `backend/core/container_registry_database.py:45`.
3.  Providing a `run_async` helper in task modules to manage the loop lifecycle `backend/tasks/scan_retention_tasks.py:18-28`.

**Sources:** `backend/core/database.py:10-14`, `backend/core/container_registry_database.py:33-56`, `backend/tasks/scan_retention_tasks.py:18-28`

## Data Flow and Code Entity Mapping

### Asynchronous Task Database Access
The following diagram illustrates how Celery tasks obtain isolated database connections to avoid "Event loop is closed" errors.

Title: Celery Task Database Connection Flow
```mermaid
graph TD
    subgraph "Celery_Worker_Process"
        "CeleryTask[purge_soft_deleted_registries]" -- "calls" --> "CDatabase[ContainerRegistryDatabase.get_database]"
    end

    subgraph "Code_Entity_Space"
        "CDatabase[ContainerRegistryDatabase.get_database]" -- "checks" --> "LoopCheck{id(asyncio.get_event_loop)}"
        "LoopCheck{id(asyncio.get_event_loop)}" -- "if_new" --> "Factory[get_async_client]"
    end

    subgraph "MongoDB_Connection"
        "Factory[get_async_client]" -- "returns" --> "Client[AsyncIOMotorClient]"
        "Client[AsyncIOMotorClient]" -- "targets" --> "RegistryDB[(cspm_container_registries)]"
    end
```
**Sources:** `backend/core/container_registry_database.py:33-56`, `backend/core/container_registry_database.py:74-79`, `backend/tasks/scan_retention_tasks.py:191-214`

### Unified Scan Results Ingestion
The `ScanResultsDatabase` acts as a centralized repository for persistent results from various scanning modules, ensuring consistent indexing for the UI.

Title: Scan Results Ingestion Mapping
```mermaid
graph LR
    subgraph "Code_Entity_Space"
        "SRD[ScanResultsDatabase.store_security_scan]"
        "CSRD[ScanResultsDatabase.store_container_scan]"
        "IAS[AssessmentIntegrationService._create_global_wrapper]"
    end

    subgraph "Storage_Contract"
        "SRD[ScanResultsDatabase.store_security_scan]" -- "writes_to" --> "N_DB[(cspm_security_scans)]"
        "CSRD[ScanResultsDatabase.store_container_scan]" -- "writes_to" --> "C_DB[(cspm_container_security)]"
        "IAS[AssessmentIntegrationService._create_global_wrapper]" -- "writes_to" --> "A_DB[(cspm_assessments)]"
    end
```
**Sources:** `backend/core/scan_results_database.py:135-155`, `backend/core/scan_results_database.py:25-31`, `backend/services/assessment_integration_service.py:84-147`

## Optimized Aggregations

To reduce database round trips by 40-60%, the `AggregationService` provides pre-built MongoDB pipelines using `$facet` and `$lookup` stages `backend/services/aggregation_service.py:5-12`.

Key pipelines include:
*   **Dashboard Summary**: Uses `$facet` to simultaneously calculate counts by status, retrieve recent scans, and get total counts in one pass `backend/services/aggregation_service.py:63-98`.
*   **Scan with Findings**: Performs a `$lookup` join between `scan_runs` and `cspm_findings` (within the orchestration DB context) to return a complete summary with severity counts `backend/services/aggregation_service.py:143-199`.

**Sources:** `backend/services/aggregation_service.py:22-200`

## Index Management and Retention

The platform ensures performance and compliance through specialized indexing and automated data retention tasks.

### Critical Indexes
| Collection | Database | Index Fields | Purpose |
|:---|:---|:---|:---|
| `asset_cache` | `cspm_cloud_assets` | `asset_id` (Unique) | Asset inventory lookup `backend/core/cloud_asset_discovery_database.py:59`. |
| `registry_images`| `cspm_container_registries`| `(account_id, repository_name, image_digest)` (Unique) | Data integrity for container images `backend/core/container_registry_database.py:99`. |
| `embedding_cache`| `cspm_knowledge_base`| `content_hash` (Unique) | RAG deduplication `backend/core/knowledge_base_database.py:65`. |
| `connection_status`| `cspm_integrations` | `integration_id` (Unique) | Integration health tracking `backend/core/integration_monitoring_database.py:59`. |

### Data Retention (TTL)
The platform uses MongoDB TTL indexes to auto-purge old scan data, typically set to 180 days by default `backend/core/scan_results_database.py:99-122`. Celery tasks like `run_retention_cycle` further manage archival and cleanup of data exceeding retention policies `backend/tasks/scan_retention_tasks.py:31-50`.

**Sources:** `backend/core/cloud_asset_discovery_database.py:53-92`, `backend/core/container_registry_database.py:81-141`, `backend/core/knowledge_base_database.py:59-80`, `backend/core/scan_results_database.py:75-134`, `backend/tasks/scan_retention_tasks.py:31-50`

## Initialization and Deployment

Database setup is handled idempotently during platform installation and startup:
1.  **System Level**: The `install.sh` script installs core packages and configures MongoDB as a system service `deployment/install.sh:91-103`.
2.  **App Level**: `CSPMDatabaseManager.connect_to_mongo()` is called on startup to initialize database handles and trigger index creation `backend/core/database.py:18-64`.
3.  **Cross-Module Support**: The `AssessmentIntegrationService` allows for data migration and "wrapping" of legacy module data into unified global assessment structures `backend/services/assessment_integration_service.py:16-147`.

**Sources:** `backend/core/database.py:18-64`, `deployment/install.sh:91-103`, `backend/services/assessment_integration_service.py:16-147`

---