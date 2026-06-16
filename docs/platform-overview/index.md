---
title: "Platform Overview"
sidebar_position: 1
---

The **OffloadSecurity CSPM** (Cloud Security Posture Management) platform is an enterprise-grade security orchestration and compliance suite. It provides a unified interface for multi-cloud security, vulnerability management, interactive assessments, and AI-driven security operations.

The platform is designed to ingest data from diverse security tools (Prowler, ZAP, Trivy, Nmap, etc.), normalize findings into a canonical format, and map them to the **Secure Controls Framework (SCF)** for automated compliance tracking `backend/services/autonomous_compliance_engine.py:142-168`.

## Core Capabilities

The platform operates across several high-level security domains:

*   **Multi-Cloud Posture Management:** Automated scanning and account management for AWS, GCP, and Azure using a factory pattern `backend/server.py:20`, `frontend/src/components/cloud/CloudSecurityManagement.js:4-12`.
*   **Vulnerability & Infrastructure Scanning:** Orchestrated execution of native tools like ZAP (Web), Nmap (Network), and Trivy (Containers/K8s) verified on startup `backend/server.py:105-112`.
*   **Governance, Risk, and Compliance (GRC):** Interactive assessments (OWASP ASVS 5.0, NIST CSF), Business Impact Analysis (BIA), and an automated Risk Register `frontend/src/components/MainContent.js:45-49`.
*   **Autonomous Compliance:** A continuous monitoring engine that auto-updates SCF control status based on scan findings and keyword correlation `backend/services/autonomous_compliance_engine.py:5-11`.
*   **AI Security Operations:** A multi-agent SOC framework (AI-SOC) and AI-assisted threat intelligence for automated triage and remediation `backend/server.py:86`, `frontend/src/components/Sidebar.js:86-91`.

## Technology Stack

The platform follows a modern architecture optimized for security tool orchestration:

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | React 18 (SPA) | Modular UI with extensive code-splitting via `lazy()` and `Suspense` `frontend/src/App.js:15-30`. |
| **Backend** | FastAPI (Python 3.12) | High-performance asynchronous API layer with Pydantic validation `backend/server.py:89-94`. |
| **Primary Database** | MongoDB 7.0 | Multi-database architecture (14+ DBs) for data isolation via `CSPMDatabaseManager` `backend/server.py:53-65`. |
| **Task Queue** | Redis + Celery | Asynchronous scan execution and scheduled maintenance tasks `backend/server.py:78`. |
| **Authentication** | JWT + RBAC | Secure session management with role-based access control and MFA support `backend/server.py:75-81`, `frontend/src/components/MainContent.js:74`. |

### System Data Flow & Code Entities
The following diagram illustrates how frontend navigation triggers backend logic and interacts with the modular database layer.

**Diagram: Request Orchestration Flow**
```mermaid
graph TD
    subgraph "Frontend_React_Space"
        [Sidebar.js] -- "onSectionChange" --> [MainContent.js]
        [MainContent.js] -- "lazy()" --> [CloudSecurityManagement.js]
        [CloudSecurityManagement.js] -- "unifiedApiService.js" --> [FastAPI_Router]
    end

    subgraph "Backend_Logic_Space"
        [FastAPI_Router] -- "Depends(require_auth)" --> [auth_standard.py]
        [auth_standard.py] -- "cloud_security_factory" --> [CloudAccountService]
        [CloudAccountService] -- "CSPMDatabaseManager" --> [Database_Interface]
    end

    subgraph "Data_Space"
        [Database_Interface] --> [MongoDB_cloud_security]
        [Database_Interface] --> [MongoDB_platform]
    end
```
**Sources:** `frontend/src/components/Sidebar.js:37-42`, `frontend/src/components/MainContent.js:1-15`, `backend/server.py:20`, `backend/server.py:36`, `backend/server.py:53-65`, `backend/server.py:81`.

## Major Subsystems

### 1. Architecture & Technology Stack
The platform utilizes a monolithic FastAPI backend that communicates with a multi-tenant MongoDB cluster using optimized connection pooling `backend/server.py:53-65`. It features a modular service layer where components like `AssessmentFactory` handle specialized domain logic `backend/server.py:27-29`.
*   For details, see **Architecture & Technology Stack**.

### 2. Getting Started & Setup
Initial deployment is handled via Docker Compose. The platform includes a dedicated `SetupWizard.js` for first-run bootstrap and a `PlatformSetupLauncher` for reconfiguration of MongoDB, Redis, and encryption keys `frontend/src/components/MainContent.js:78-105`, `frontend/src/App.js:110`.
*   For details, see **Getting Started & Setup**.

### 3. Module System & Navigation
The UI is built on a modular system where features can be toggled via `ModuleManagementDashboard` `frontend/src/components/MainContent.js:30`. Navigation is centralized in `Sidebar.js`, which dynamically renders sections based on `ALL_PLATFORM_MODULES` `frontend/src/components/Sidebar.js:6-22`. The `MainContent.js` component acts as the primary router for these modules `frontend/src/components/MainContent.js:132-143`.
*   For details, see **Module System & Navigation**.

**Diagram: Code Entity Mapping (Navigation to Service)**
```mermaid
graph LR
    subgraph "Natural_Language_UI"
        [NAV_Sidebar_Assessments]
    end

    subgraph "Code_Entity_Space"
        [COMP_MainContent.js_InteractiveAssessments]
        [ROUTE_common_control_routes.py]
        [SVC_autonomous_compliance_engine.py]
        [DB_CSPMDatabaseManager_get_core_db]
    end

    [NAV_Sidebar_Assessments] --> [COMP_MainContent.js_InteractiveAssessments]
    [COMP_MainContent.js_InteractiveAssessments] --> [ROUTE_common_control_routes.py]
    [ROUTE_common_control_routes.py] --> [SVC_autonomous_compliance_engine.py]
    [SVC_autonomous_compliance_engine.py] --> [DB_CSPMDatabaseManager_get_core_db]
```
**Sources:** `frontend/src/components/Sidebar.js:199-204`, `frontend/src/components/MainContent.js:23`, `backend/routes/common_control_routes.py:25`, `backend/services/autonomous_compliance_engine.py:36`.

## Related Sections
*   **Architecture & Technology Stack**
*   **Getting Started & Setup**
*   **Module System & Navigation**

---