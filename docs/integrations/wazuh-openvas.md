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
- **Corroborated vulnerability state.** A host CVE flagged by Wazuh's vulnerability detection (which streams into the platform) and confirmed by an authenticated OpenVAS scan gives you higher-confidence signal on the same host.
- **Both control types covered.** Wazuh's SCA/FIM telemetry becomes audit evidence in the platform for endpoint-hardening controls, while OpenVAS covers the internal-scanning controls many frameworks require (e.g., PCI-DSS) — together spanning both requirements.

## How they fit together

The two integrations sit at different depths in the platform:

- **Wazuh telemetry streams into the platform** — detections, alerts, FIM, SCA compliance, and host CVE state flow into **[Vulnerability Management](../vulnerability-risk/vulnerability-management.mdx)** and the centralized **[Alerts](./notifications.md)**, deduplicated against native scans.
- **OpenVAS is a connectivity integration** — Offload connects to and verifies your Greenbone/OpenVAS deployment; you run and review the network scans there. Its results are not imported into the platform today, so OpenVAS remains the system of record for internal scan findings.

Together they give you continuous host visibility in-platform *and* deep network vulnerability assessment on your own infrastructure — covering the endpoint-hardening and internal-scanning controls that regulated environments require.

## Get started

1. Connect **[Wazuh](./wazuh.md)** (Manager API + Indexer).
2. Connect **[OpenVAS](./openvas.md)** and define your internal scan scope.
3. Review Wazuh's host activity in **[Vulnerability Management](../vulnerability-risk/vulnerability-management.mdx)** and **[Alerts](./notifications.md)**, and run your network scans in the OpenVAS / Greenbone console.

For the full architecture of internal coverage, see the **[On-Premises](../on-premises/index.mdx)** section.
