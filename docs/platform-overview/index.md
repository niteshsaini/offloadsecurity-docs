---
title: "Platform Overview"
sidebar_position: 1
---

The **OffloadSecurity CSPM** (Cloud Security Posture Management) platform is an enterprise-grade security orchestration and compliance suite. It provides a unified interface for multi-cloud security, vulnerability management, interactive assessments, and AI-driven security operations.

The platform is designed to ingest data from diverse security tools (Prowler, ZAP, Trivy, Nmap, etc.), normalize findings into a canonical format, and map them to the **Secure Controls Framework (SCF)** for automated compliance tracking.

## Core Capabilities

The platform operates across several high-level security domains:

*   **Multi-Cloud Posture Management:** Automated scanning and account management for AWS, GCP, and Azure using a factory pattern.
*   **Vulnerability & Infrastructure Scanning:** Orchestrated execution of native tools like ZAP (Web), Nmap (Network), and Trivy (Containers/K8s) verified on startup.
*   **Governance, Risk, and Compliance (GRC):** Interactive assessments (OWASP ASVS 5.0, NIST CSF), Business Impact Analysis (BIA), and an automated Risk Register.
*   **Autonomous Compliance:** A continuous monitoring engine that auto-updates SCF control status based on scan findings and keyword correlation.
*   **AI Security Operations:** A multi-agent SOC framework (AI-SOC) and AI-assisted threat intelligence for automated triage and remediation.

## Technology Stack

The platform follows a modern architecture optimized for security tool orchestration:

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | React 18 (SPA) | Modular UI with extensive code-splitting via `lazy()` and `Suspense`. |
| **Backend** | FastAPI (Python 3.12) | High-performance asynchronous API layer with Pydantic validation. |
| **Primary Database** | MongoDB 7.0 | Multi-database architecture (14+ DBs) for data isolation via `CSPMDatabaseManager`. |
| **Task Queue** | Redis + Celery | Asynchronous scan execution and scheduled maintenance tasks. |
| **Authentication** | JWT + RBAC | Secure session management with role-based access control and MFA support. |

### System Data Flow & Code Entities
The following diagram illustrates how frontend navigation triggers backend logic and interacts with the modular database layer.

**Diagram: Request Orchestration Flow**
```mermaid
graph TD
    subgraph "Frontend_React_Space"
        [Sidebar] -- "onSectionChange" --> [MainContent]
        [MainContent] -- "lazy()" --> [CloudSecurityManagement]
        [CloudSecurityManagement] -- "unifiedApiService" --> [FastAPI_Router]
    end

    subgraph "Backend_Logic_Space"
        [FastAPI_Router] -- "Depends(require_auth)" --> [auth_standard]
        [auth_standard] -- "cloud_security_factory" --> [CloudAccountService]
        [CloudAccountService] -- "CSPMDatabaseManager" --> [Database_Interface]
    end

    subgraph "Data_Space"
        [Database_Interface] --> [MongoDB_cloud_security]
        [Database_Interface] --> [MongoDB_platform]
    end
```

## Major Subsystems

### 1. Architecture & Technology Stack
The platform utilizes a monolithic FastAPI backend that communicates with a multi-tenant MongoDB cluster using optimized connection pooling. It features a modular service layer where components like `AssessmentFactory` handle specialized domain logic.
*   For details, see **Architecture & Technology Stack**.

### 2. Getting Started & Setup
Initial deployment is handled via Docker Compose. The platform includes a dedicated `SetupWizard` for first-run bootstrap and a `PlatformSetupLauncher` for reconfiguration of MongoDB, Redis, and encryption keys.
*   For details, see **Getting Started & Setup**.

### 3. Module System & Navigation
The UI is built on a modular system where features can be toggled via `ModuleManagementDashboard`. Navigation is centralized in the `Sidebar`, which dynamically renders sections based on `ALL_PLATFORM_MODULES`. The `MainContent` component acts as the primary router for these modules.
*   For details, see **Module System & Navigation**.

**Diagram: Code Entity Mapping (Navigation to Service)**
```mermaid
graph LR
    subgraph "Natural_Language_UI"
        [NAV_Sidebar_Assessments]
    end

    subgraph "Code_Entity_Space"
        [COMP_MainContent_InteractiveAssessments]
        [ROUTE_common_control_routes]
        [SVC_autonomous_compliance_engine]
        [DB_CSPMDatabaseManager_get_core_db]
    end

    [NAV_Sidebar_Assessments] --> [COMP_MainContent_InteractiveAssessments]
    [COMP_MainContent_InteractiveAssessments] --> [ROUTE_common_control_routes]
    [ROUTE_common_control_routes] --> [SVC_autonomous_compliance_engine]
    [SVC_autonomous_compliance_engine] --> [DB_CSPMDatabaseManager_get_core_db]
```

## Related Sections
*   **Architecture & Technology Stack**
*   **Getting Started & Setup**
*   **Module System & Navigation**

---