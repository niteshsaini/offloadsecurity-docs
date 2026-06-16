---
title: "Data Layer & Core Services"
sidebar_position: 1
---

The Data Layer and Core Services form the backbone of the OffloadSecurity CSPM platform. This layer is responsible for multi-database management, persistent storage of scan results, and providing shared infrastructure services—including dependency injection, standardized response handling, and the repository pattern—that are used across all security modules.

## Database Architecture

The platform utilizes a **multi-database MongoDB architecture** to ensure data isolation, scalability, and modularity. Instead of a single monolithic database, the system partitions data into 14+ distinct databases based on functional domains (e.g., `cspm_cloud_security`, `cspm_risk_management`, `cspm_assessments`).

The `CSPMDatabaseManager` class in `backend/core/database.py:10-127` serves as the central orchestrator. It utilizes a singleton client factory via `get_async_client` `backend/core/database.py:21-23` to manage connections using the `motor` async driver. For standardizing these names, the `DatabaseRegistry` `backend/core/database_registry.py:20-213` acts as the single source of truth for database constants and purpose mapping.

### Database Distribution
| Database Alias | Registry Constant | Purpose |
|:---|:---|:---|
| `core` | `PLATFORM` | Platform settings, users, sessions, and audit logs `backend/core/database_registry.py:39-49`. |
| `cloud_security` | `CLOUD_SECURITY` | Cloud accounts (consolidated), Prowler findings, and scores `backend/core/database_registry.py:52-59`. |
| `native_scans` | `SECURITY_SCANS` | Persistent storage for Nuclei, SSL, and Header scans `backend/core/database_registry.py:135-139`. |
| `orchestration` | `ORCHESTRATION` | Scan runs, jobs, and sub-job lifecycle state `backend/core/database_registry.py:70-76`. |
| `vulnerabilities` | `VULNERABILITIES` | Vulnerability occurrences (UVM), catalog, and SLA policies `backend/core/database_registry.py:79-86`. |
| `ai_governance` | `AI_GOVERNANCE` | AI models, risk assessments, and EU AI Act compliance data `backend/core/database_registry.py:157-164`. |

For details on collection schemas, cross-module references, and index management, see **Database Architecture**.

**Sources:** `backend/core/database.py:39-51`, `backend/core/database_registry.py:20-164`, `backend/core/database_factory.py:84-112`

## Core Service Infrastructure

Shared services provide standardized functionality to API routes and background workers, ensuring that operations like dependency injection and reporting are performed consistently.

### Dependency Injection & Service Container
The platform uses a `ServiceContainer` to manage the lifecycle of services and repositories. It initializes repositories using a `RepositoryFactory` and then injects these into business logic services. This pattern is extended to specialized services like the `CentralAccountService` `backend/services/central_account_service.py:69-73` which acts as the single source of truth for cloud account management.

### Standardized API Responses
The `ResponseService` provides a unified way to return `success_response` or `error_response`. This is heavily utilized across the platform's modular routers to ensure consistent JSON structures for the frontend.

### Cross-Module Data Access & Aggregation
While data is isolated into multiple databases, the platform supports cross-module logic through services like `AggregationService` `backend/services/aggregation_service.py:22-31`. This service uses MongoDB `$facet` and `$lookup` pipelines to reduce database round trips by 40-60% `backend/services/aggregation_service.py:8-12`. For example, `get_dashboard_summary` replaces up to 10 separate queries with a single aggregation `backend/services/aggregation_service.py:47-59`.

Specialized integration services like `AssessmentIntegrationService` `backend/services/assessment_integration_service.py:16-26` and `EvidenceIntegrationService` `backend/services/evidence_integration_service.py:14-25` bridge different modules by collecting data from multiple databases to satisfy compliance and risk assessment requirements.

For details on the repository pattern, caching with Redis, and credential encryption, see **Core Service Patterns & Utilities**.

**Sources:** `backend/services/aggregation_service.py:22-120`, `backend/services/assessment_integration_service.py:16-26`, `backend/services/evidence_integration_service.py:14-25`, `backend/services/central_account_service.py:69-180`

## System Integration Diagram

This diagram illustrates how the `DatabaseFactory` and `CSPMDatabaseManager` bridge the logical security modules to specific code entities and storage.

```mermaid
graph TD
    subgraph "Service Layer"
        SVC_ACC["CentralAccountService"]
        SVC_AGG["AggregationService"]
        SVC_EV["EvidenceIntegrationService"]
        SVC_ASS["GlobalAssessmentService"]
    end

    subgraph "Data Access Core"
        DF["DatabaseFactory"]
        DBM["CSPMDatabaseManager"]
        REG["DatabaseRegistry"]
    end

    subgraph "MongoDB Persistence"
        DB_PLAT[("PLATFORM: cspm_platform")]
        DB_CLOUD[("CLOUD_SECURITY: cspm_cloud_security")]
        DB_ORCH[("ORCHESTRATION: cspm_orchestration")]
        DB_ASS[("ASSESSMENTS: cspm_assessments")]
    end

    SVC_ACC -->|get_cloud_security_db| DBM
    SVC_AGG -->|self.db| DB_ORCH
    SVC_EV -->|get_database| DBM
    SVC_ASS -->|get_database| DBM

    DF -->|get_database| DBM
    DBM -.->|Constants| REG
    
    DBM --> DB_PLAT
    DBM --> DB_CLOUD
    DBM --> DB_ORCH
    DBM --> DB_ASS
```
**Sources:** `backend/core/database.py:67-127`, `backend/core/database_registry.py:39-164`, `backend/core/database_factory.py:60-80`, `backend/services/central_account_service.py:16-35`, `backend/services/global_assessment_service.py:23-26`

## Request & Data Flow

The following diagram traces a request through the backend core services to the multi-database storage, specifically showing how dependencies are resolved for the Global Assessment module.

```mermaid
sequenceDiagram
    participant FE as Frontend (React)
    participant RT as FastAPI Router
    participant SVC as GlobalAssessmentService
    participant DBM as CSPMDatabaseManager
    participant EV_SVC as EvidenceIntegrationService

    FE->>RT: POST /assessments/create
    RT->>SVC: create_assessment(data, team_id)
    SVC->>DBM: get_database()
    DBM-->>SVC: AsyncIOMotorDatabase (cspm_platform)
    SVC->>SVC: _calculate_assessment_dates()
    SVC->>EV_SVC: collect_comprehensive_evidence(assessment_id, team_id)
    EV_SVC->>DBM: get_cloud_security_db()
    DBM-->>EV_SVC: AsyncIOMotorDatabase (cspm_cloud_security)
    EV_SVC-->>SVC: Evidence results
    SVC-->>RT: GlobalAssessment object
    RT-->>FE: JSON {success: true, data: {...}}
```
**Sources:** `backend/services/global_assessment_service.py:23-80`, `backend/services/evidence_integration_service.py:27-82`, `backend/core/database.py:67-71`

## Data Integrity & Architecture Contracts

The platform enforces strict architectural contracts to ensure stability and deployment consistency:
*   **Collection Consolidation**: The platform enforces a contract where no production code may query the legacy `cloud_accounts` collection; all cloud account data must reside in `enhanced_cloud_accounts` `backend/tests/architecture/test_cloud_accounts_collection_consolidated_contract.py:83-91`.
*   **Database Single Source of Truth**: All database names and purpose mappings must be derived from `DatabaseRegistry` to avoid connection proliferation `backend/core/database_registry.py:20-32`.
*   **Cross-DB Aggregation Restrictions**: The `AggregationService` is prohibited from using `$lookup` for cross-database joins (e.g., joining orchestration and cloud security data in a single pipeline), as MongoDB `$lookup` is single-DB only `backend/services/aggregation_service.py:138-142`. Metadata resolution for such cases must be performed via explicit cross-DB queries `backend/tests/architecture/test_cloud_accounts_collection_consolidated_contract.py:94-115`.
*   **Migration Idempotency**: Maintenance scripts, such as `kb_reembed_documents.py`, must be idempotent, checking fields like `embedding_model_used` before performing expensive operations `backend/scripts/kb_reembed_documents.py:17-25`.

**Sources:** `backend/core/database_registry.py:20-164`, `backend/tests/architecture/test_cloud_accounts_collection_consolidated_contract.py:1-115`, `backend/services/aggregation_service.py:138-142`, `backend/scripts/kb_reembed_documents.py:17-25`

---