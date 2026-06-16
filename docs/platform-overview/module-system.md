---
title: "Module System & Navigation"
sidebar_position: 4
---

The OffloadSecurity platform utilizes a modular architecture designed for scalability and feature-flagged access control. This system enables the platform to dynamically enable or disable high-level security modules (e.g., Cloud Security, Risk Management, AI Governance) based on user subscriptions and organizational needs. Navigation is orchestrated through a centralized sidebar and a main content router that leverages React lazy loading to optimize performance.

## Modular Feature-Flag System

The platform's capabilities are governed by a modular licensing and permission system. The frontend synchronizes with the backend via the `unifiedApiService.getEnabledModules()` call within the `Sidebar` component.

### Module Authorization and Initialization
- **Module Source of Truth**: The `ALL_PLATFORM_MODULES` constant in the frontend defines the comprehensive list of available modules, including `vulnerability_scanning`, `cloud_security`, `risk_management`, and `ai_security`.
- **Dynamic Filtering**: The list of enabled modules is stored in the `enabledModules` state. If the API call fails, the system defaults to the full list to ensure availability.
- **Module Loading Configuration**: The module loader defines which modules load `immediate` (e.g., `overview`) and which load `lazy` (e.g., `threat-intelligence`, `cloud-security`).

**Data Flow: Module Authorization**
```mermaid
sequenceDiagram
    participant U as "User Browser"
    participant S as "Sidebar"
    participant API as "unifiedApiService"
    participant B as "FastAPI Backend"

    U->>S: "Mount Sidebar"
    S->>API: "getEnabledModules()"
    API->>B: "GET /api/modules/enabled"
    B-->>API: "['cloud_security', 'risk_management', ...]"
    API-->>S: "Module List"
    S->>S: "Filter sectionGroups based on requiredModule"
    S-->>U: "Render permitted Navigation Items"
```

---

## Sidebar & Navigation Structure

The `Sidebar` component defines the primary navigation hierarchy. Sections are organized into logical groups, each potentially requiring specific module permissions.

### Navigation Groups
The platform categorizes security features into functional groups:

| Group ID | Group Name | Key Sections | Required Module |
| :--- | :--- | :--- | :--- |
| `core_security` | CORE SECURITY | Dashboard, AI SOC, Scanning, Code Command Center | `vulnerability_scanning` |
| `cloud_infrastructure` | CLOUD & INFRASTRUCTURE | Cloud Security, Containers, K8s, Asset Inventory | `cloud_security` |
| `compliance_risk` | COMPLIANCE & RISK | Compliance Posture, Risk Management, Assessments | `risk_management` / `compliance_assessments` |
| `threat_intelligence` | THREAT & INTELLIGENCE | Threat Intel, AI Governance, Knowledge Base | `threat_intelligence` |

### Implementation Logic
Each navigation item in the `sectionGroups` array contains a `requiredModule` property. The rendering logic checks whether the `requiredModule` is either `null` or present in the `enabledModules` list.

The `Sidebar` also fetches dashboard statistics (`getDashboardStats`) and AI insights (`getAiInsights`) in parallel during its initialization to populate UI badges.

---

## MainContent Routing & Lazy Loading

The `MainContent` router serves as the dynamic routing hub for the authenticated dashboard. It utilizes React's `lazy` and `Suspense` APIs to implement code-splitting, reducing the initial bundle size by loading security modules only when requested.

### Implementation Details
- **Eager Loading**: Critical components used on initial render or accessed frequently are imported traditionally. These include `NewScan`, `CreateAssessment`, and `CloudSecurityManagement`.
- **Lazy Loading**: Secondary modules are loaded on-demand. For example, `ThreatIntelligence`, `KnowledgeBase`, and `EnhancedRiskManagement` are defined as lazy components.
- **Loading State**: A `LazyFallback` component renders a spinner during chunk retrieval.

**Component Mapping & Entity Space**
```mermaid
graph TD
    subgraph "Navigation Space (Dashboard / Sidebar)"
        N1["activeSection: 'cloud-security'"]
        N2["activeSection: 'scans'"]
        N3["activeSection: 'threat-intel'"]
    end

    subgraph "Routing Space (MainContent)"
        R["renderSection(activeSection)"]
    end

    subgraph "Code Entity Space (Components)"
        C1["CloudSecurityManagement (Eager)"]
        C2["NewScan (Eager)"]
        C3["ThreatIntelligence (Lazy)"]
    end

    N1 --> R
    N2 --> R
    N3 --> R

    R -- "case 'cloud-security'" --> C1
    R -- "case 'scans'" --> C2
    R -- "case 'threat-intel'" --> C3
```

### Module Navigation & State Management
When a user selects a section in the `Sidebar`, the `onSectionChange` callback triggers `handleSectionChange` in `Dashboard`. This updates the URL with the `section` parameter and increments a `sectionResetKey` to force-refresh child components.

Several modules implement internal sub-navigation:
- **CloudSecurityManagement**: Uses `activeCloudTab` to switch between `accounts`, `compliance`, `findings`, and `inventory`.
- **Dashboard**: Synchronizes URL parameters (`section`, `tab`, `action`) with component state to allow deep-linking.

### Authentication & Setup Guarding
Navigation is protected by the `ProtectedRoute` component, which verifies both the `user` session via `AuthContext` and the platform's initialization status via the `/setup/status` endpoint.
