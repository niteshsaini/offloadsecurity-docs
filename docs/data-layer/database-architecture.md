---
title: "Database Architecture"
sidebar_position: 2
---

The OffloadSecurity CSPM platform utilizes a modular multi-database architecture powered by MongoDB. This design ensures data isolation between functional modules (e.g., Cloud Security, Risk Management, Assessments), optimizes query performance through specialized indexing, and provides a scalable foundation for the platform's asynchronous scanning engine.

## Modular Database Strategy

The system distributes data across 14 distinct MongoDB databases. This approach allows for granular backup strategies, independent scaling, and prevents a single large collection from impacting the performance of unrelated services.

### Database Registry
The `DatabaseRegistry` class serves as the single source of truth for database names and purposes across the platform. It maps functional areas to specific database constants and maintains a registry of deprecated databases (e.g., `cspm_platform_core`) to ensure legacy data is correctly mapped to the current `PLATFORM` store.

| Database Name (Default) | Registry Constant | Primary Responsibility |
|:---|:---|:---|
| `cspm_platform` | `PLATFORM` | Core data: users, sessions, audit logs, and global templates. |
| `cspm_cloud_security` | `CLOUD_SECURITY` | Consolidated cloud accounts, Prowler findings, and compliance scores. |
| `cspm_cloud_assets` | `CLOUD_ASSETS` | Asset inventory from Steampipe and discovery history. |
| `cspm_orchestration` | `ORCHESTRATION` | Scan orchestration: `scan_runs`, `scan_jobs`, and `sub_jobs`. |
| `cspm_vulnerabilities` | `VULNERABILITIES` | Unified vulnerability catalog and occurrence lifecycle. |
| `cspm_risk_management` | `RISK_MANAGEMENT` | Risk register, treatment plans, KRIs, and scenarios. |
| `cspm_assessments` | `ASSESSMENTS` | Interactive assessments and completion progress. |
| `cspm_container_registries` | `CONTAINER_REGISTRY` | Registry metadata, repository sync status, and image discovery cache. |
| `cspm_security_scans` | `SECURITY_SCANS` | Native scans: Nuclei, SSL/TLS, ZAP, and Header results. |
| `cspm_threat_intelligence` | `THREAT_INTELLIGENCE` | Indicators (IoC), CISA KEV feeds, and correlations. |
| `cspm_ai_governance` | `AI_GOVERNANCE` | AI model registry, bias tests, and EU AI Act assessments. |
| `cspm_integrations` | `INTEGRATIONS` | Connection status, health monitoring, and wizard sessions. |
| `cspm_knowledge_base` | `KNOWLEDGE_BASE` | Document embeddings and semantic search cache. |
| `cspm_bia` | `BIA` | Business impact analyses and exercises. |

## Connection Management

The platform employs specialized managers to handle different execution contexts, particularly for asynchronous API routes versus long-running background tasks.

### CSPMDatabaseManager
The primary manager for the FastAPI application. It maintains a mapping of module names to `AsyncIOMotorDatabase` instances. It facilitates cross-module data relationships via `create_cross_module_reference`, which stores links in the `core` database (mapping to `cspm_platform`) to maintain referential integrity across logical boundaries.

### CeleryDatabaseManager (Loop-Aware Pattern)
Database singletons bound to the FastAPI event loop fail when accessed within Celery workers, which create/close a new event loop for every task execution.

The system solves this by:
1.  Creating a **fresh** `AsyncIOMotorClient` for task execution if the loop ID has changed.
2.  Using the `get_async_client()` singleton factory to ensure that while the database handle is fresh, the underlying connection pool is reused.
3.  Providing a `run_async` helper in task modules to manage the loop lifecycle.

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

## Optimized Aggregations

To reduce database round trips by 40-60%, the `AggregationService` provides pre-built MongoDB pipelines using `$facet` and `$lookup` stages.

Key pipelines include:
*   **Dashboard Summary**: Uses `$facet` to simultaneously calculate counts by status, retrieve recent scans, and get total counts in one pass.
*   **Scan with Findings**: Performs a `$lookup` join between `scan_runs` and `cspm_findings` (within the orchestration DB context) to return a complete summary with severity counts.

## Index Management and Retention

The platform ensures performance and compliance through specialized indexing and automated data retention tasks.

### Critical Indexes
| Collection | Database | Index Fields | Purpose |
|:---|:---|:---|:---|
| `asset_cache` | `cspm_cloud_assets` | `asset_id` (Unique) | Asset inventory lookup. |
| `registry_images`| `cspm_container_registries`| `(account_id, repository_name, image_digest)` (Unique) | Data integrity for container images. |
| `embedding_cache`| `cspm_knowledge_base`| `content_hash` (Unique) | RAG deduplication. |
| `connection_status`| `cspm_integrations` | `integration_id` (Unique) | Integration health tracking. |

### Data Retention (TTL)
The platform uses MongoDB TTL indexes to auto-purge old scan data, typically set to 180 days by default. Celery tasks like `run_retention_cycle` further manage archival and cleanup of data exceeding retention policies.

## Initialization and Deployment

Database setup is handled idempotently during platform installation and startup:
1.  **System Level**: The installation script installs core packages and configures MongoDB as a system service.
2.  **App Level**: `CSPMDatabaseManager.connect_to_mongo()` is called on startup to initialize database handles and trigger index creation.
3.  **Cross-Module Support**: The `AssessmentIntegrationService` allows for data migration and "wrapping" of legacy module data into unified global assessment structures.