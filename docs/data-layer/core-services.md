---
title: "Core Service Patterns & Utilities"
sidebar_position: 3
---

This page documents the foundational architectural patterns and shared utility services that power the OffloadSecurity CSPM platform. The system utilizes a centralized dependency injection container, a robust repository pattern for data access, optimized MongoDB aggregation pipelines, and a multi-database management strategy.

## Dependency Injection & Service Management

The platform uses a centralized `ServiceContainer` to manage the lifecycle of business logic services and data repositories. This ensures that dependencies are injected consistently across the application.

### Service Initialization Flow
The `ServiceContainer` initializes in two phases:
1.  **Repository Initialization**: Uses the `repository_factory` to create typed repositories for core entities including Assessments, Scans, Users, Teams, Risks, and Cloud Security `backend/services/dependency_injection.py:47-59`. It includes a fallback mechanism to manual initialization using the base `db` object if the factory fails `backend/services/dependency_injection.py:65-76`.
2.  **Service Initialization**: Constructs high-level business services (e.g., `WebSecurityService`, `ContainerSecurityService`, `CloudSecurityService`, `AIComplianceService`), injecting the core `DatabaseService` and relevant repositories `backend/services/dependency_injection.py:78-140`.

### Service Registration System
The `ServiceContainer` acts as a registry, providing a `get_service` method to retrieve initialized instances by name `backend/services/dependency_injection.py:148-154`. This pattern allows complex services like `ScanOrchestrationService` to depend on multiple other services (Web, Container, Cloud, and Assessment services) while maintaining a clean construction logic `backend/services/dependency_injection.py:132-140`.

**Entity Relationship: DI and Service Graph**
```mermaid
graph TD
    subgraph "Code_Entity_Space: backend/core/"
        SC["ServiceContainer (dependency_injection.py)"]
        RF["repository_factory (repository_factory.py)"]
        DF["database_factory (database_factory.py)"]
    end

    subgraph "Service_Instances: backend/services/"
        AS["AssessmentService"]
        SOS["ScanOrchestrationService"]
        CSS["CloudSecurityService"]
        DBS["DatabaseService"]
    end

    SC -->|Initializes| RF
    RF -->|Uses| DF
    SC -->|Injects Repos Into| AS
    SC -->|Injects DBS Into| CSS
    SC -->|Injects AS & CSS Into| SOS
    DBS -->|Lazy Loads| DB["get_database() (core/database.py)"]
```
Sources: `backend/services/dependency_injection.py:35-140`, `backend/services/database_service.py:12-38`

---

## Data Access & Repository Pattern

The platform abstracts database interactions through a `DatabaseService` and specialized repositories to ensure data integrity and consistent query patterns.

### Database Service Operations
The `DatabaseService` provides a high-level API for MongoDB operations with built-in verification and timestamping:
*   **Document Creation**: The `create_document` method generates UUIDs, adds `created_at`/`updated_at` timestamps, and performs an immediate post-insert verification check to ensure the document was successfully persisted `backend/services/database_service.py:40-83`.
*   **Query Helpers**: Specialized methods exist for finding documents by `user_id` or `team_id`, facilitating multi-tenant data isolation `backend/services/database_service.py:121-182`.
*   **Update Logic**: The `update_document` method supports both plain field updates and MongoDB operators (like `$set` or `$push`), automatically handling the `updated_at` timestamp `backend/services/database_service.py:184-210`.

### Centralized Route Registration
To prevent server startup crashes due to individual module failures, the platform uses a centralized `register_all_routes` function `backend/core/route_registration.py:14-22`. Each router import is wrapped in a try/except block, logging a warning rather than crashing if a specific module is broken `backend/core/route_registration.py:26-37`. This handles everything from core auth `backend/core/route_registration.py:41` to specialized compliance and AI routes `backend/core/route_registration.py:121-128`.

Sources: `backend/services/database_service.py:22-210`, `backend/core/route_registration.py:1-133`

---

## Storage & Evidence Patterns

The platform implements a multi-tier storage strategy for scan results and compliance evidence, prioritizing cloud providers with local fallbacks.

### Object Storage Service
The `ObjectStorageService` provides a unified interface for S3, GCS, Azure, and local filesystem backends `backend/services/object_storage_service.py:5-12`. 
*   **Connectivity Probes**: The platform includes a `test_storage_connectivity` probe that validates credentials and write permissions before configuration is saved to `.env` `backend/tests/unit/test_storage_connectivity_probe.py:1-24`.
*   **Cloud-Primary Logic**: The `ScanResultsStorage` service attempts to write to cloud providers first. If the write fails, it falls back to local disk to prevent data loss `backend/services/scan_results_storage_service.py:57-70`.

### Evidence Masking & Collection
Before cloud API responses are stored as compliance evidence, they must pass through the `EvidenceMaskingService` `backend/services/evidence_masking_service.py:4-6`.
*   **Redaction Rules**: It uses regex patterns to mask AWS Account IDs (last 4 digits only), Access Keys, Emails, and JWT/Bearer tokens `backend/services/evidence_masking_service.py:61-117`.
*   **API Collection**: The `APIEvidenceCollector` maps real cloud API calls (e.g., `get_bucket_encryption`) to SCF controls like `DSP-03` `backend/services/api_evidence_collector.py:36-48`.

**Natural Language to Code Entity Space: Evidence Pipeline**
```mermaid
graph LR
    subgraph "Natural_Language_Space"
        direction TB
        A["'Capture S3 encryption settings'"]
        B["'Hide my AWS Account ID'"]
        C["'Store it in S3 or local disk'"]
    end

    subgraph "Code_Entity_Space"
        direction TB
        A1["APIEvidenceCollector.AWS_EVIDENCE_QUERIES (api_evidence_collector.py)"]
        B1["EvidenceMaskingService.mask_evidence() (evidence_masking_service.py)"]
        C1["ScanResultsStorage.store_scan() (scan_results_storage_service.py)"]
    end

    A -.-> A1
    B -.-> B1
    C -.-> C1
```
Sources: `backend/services/api_evidence_collector.py:36-186`, `backend/services/evidence_masking_service.py:129-156`, `backend/services/scan_results_storage_service.py:141-180`

---

## Caching & Performance

### Redis Cache Service
The `CacheService` provides a primary Redis interface with an in-memory fallback for environments where Redis is unavailable `backend/services/cache_service.py:20-47`.
*   **Decorators**: Developers can use `@cache_result` or `@cache_user_result` to automatically cache function outputs with specific TTLs `backend/services/cache_service.py:150-185`.
*   **Key Generation**: Keys are generated consistently based on function arguments and hashed if they exceed 200 characters `backend/services/cache_service.py:49-66`.

### Platform Setup Wizard
The `PlatformSetupService` manages the first-time configuration of the platform `backend/services/platform_setup_service.py:81-82`.
*   **Secret Generation**: It auto-generates Fernet keys for cloud credentials and hex secrets for JWT signing using `secrets` and `cryptography` libraries `backend/services/platform_setup_service.py:69-79`.
*   **Validation**: It validates MongoDB and Redis connectivity before marking setup as complete `backend/services/platform_setup_service.py:125-146`.
*   **Locking**: Once setup is complete, mutation endpoints are locked via environment variables and database flags `backend/routes/platform_setup_routes.py:84-100`.

Sources: `backend/services/cache_service.py:20-185`, `backend/services/platform_setup_service.py:1-146`, `backend/routes/platform_setup_routes.py:139-191`, `frontend/src/components/SetupWizard.js:112-166`

---