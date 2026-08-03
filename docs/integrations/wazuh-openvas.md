---
title: "Wazuh + OpenVAS: Complete On-Premises Coverage"
sidebar_label: "Wazuh + OpenVAS"
sidebar_position: 5
---

# Wazuh + OpenVAS: Complete On-Premises Coverage

Wazuh and OpenVAS answer two different questions about your internal estate. Run them together, connected to Offload Security, and you get both — correlated in one place instead of two consoles.

| | **[Wazuh](./wazuh.md)** | **[OpenVAS](./openvas.md)** |
|---|---|---|
| **Answers** | *"What is happening on our hosts?"* | *"What weaknesses exist on our network?"* |
| **Approach** | Agent-based endpoint telemetry & SIEM | Network vulnerability scanning |
| **Surfaces** | Detections, alerts, FIM, SCA compliance, host CVE state, ATT&CK | CVEs, missing patches, exposed services, weak configs |
| **Best for** | Continuous host monitoring & response | Periodic deep vulnerability assessment of internal assets |

## Why they're better together

- **Breadth × depth.** Wazuh gives continuous, agent-level visibility on the hosts you manage; OpenVAS reaches everything on the network — including appliances, OT/IoT, and unmanaged systems where you can't install an agent.
- **Detection × prevention.** Wazuh tells you what's *happening* (events, integrity changes, active response); OpenVAS tells you what's *exposed* before it's exploited.
- **Corroborated vulnerability state.** A host CVE flagged by Wazuh's vulnerability detection and confirmed by an authenticated OpenVAS scan is a stronger, deduplicated signal — not two separate tickets.
- **One evidence trail.** SCA/FIM from Wazuh and internal scan results from OpenVAS both become audit evidence in the same platform, covering endpoint-hardening *and* internal-scanning controls (e.g., PCI-DSS).

## How it comes together in the platform

Both integrations normalize into the **same unified data layer**:

- Findings from both flow into **[Vulnerability Management](../vulnerability-risk/vulnerability-management.mdx)**, deduplicated against each other and against native scans.
- Wazuh detections feed the centralized **[Alerts](./notifications.md)**; OpenVAS findings are risk-mapped alongside them.
- Compliance evidence from both is collected once and reused across frameworks.

The result is a single, governed view of your on-premises risk — real-time host activity and deep network vulnerability state in the same posture, not adjacent to it.

## Get started

1. Connect **[Wazuh](./wazuh.md)** (Manager API + Indexer).
2. Connect **[OpenVAS](./openvas.md)** and define your internal scan scope.
3. Review the combined picture in **[Vulnerability Management](../vulnerability-risk/vulnerability-management.mdx)** and **[Alerts](./notifications.md)**.

For the full architecture of internal coverage, see the **[On-Premises](../on-premises/index.mdx)** section.
