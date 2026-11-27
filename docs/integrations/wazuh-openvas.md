---
title: "Wazuh + OpenVAS: Complete On-Premises Coverage"
description: "Run Wazuh and OpenVAS together with Offload Security for complete on-premises coverage: endpoint telemetry and network vulnerability scanning, in one set of views."
sidebar_label: "Wazuh + OpenVAS"
sidebar_position: 9
---

# Wazuh + OpenVAS: Complete On-Premises Coverage

Wazuh and OpenVAS answer two different questions about your internal estate. Run them together, connected to Offload Security, and you get both in the same Vulnerability Management views instead of two consoles.

| | **[Wazuh](./wazuh.md)** | **[OpenVAS](./openvas.md)** |
|---|---|---|
| **Answers** | *"What is happening on our hosts?"* | *"What weaknesses exist on our network?"* |
| **Approach** | Agent-based endpoint telemetry & SIEM | Network vulnerability scanning |
| **Surfaces** | Detections, alerts, FIM, SCA compliance, host CVE state, ATT&CK | CVEs, missing patches, exposed services, weak configs |
| **Best for** | Continuous host monitoring & response | Periodic deep vulnerability assessment of internal assets |

## Why they're better together

- **Breadth × depth.** Wazuh gives continuous, agent-level visibility on the hosts you manage; OpenVAS reaches everything on the network — including appliances, OT/IoT, and unmanaged systems where you can't install an agent.
- **Detection × prevention.** Wazuh tells you what's *happening* (events, integrity changes, active response); OpenVAS tells you what's *exposed* before it's exploited.
- **Corroborated vulnerability state.** A host CVE flagged by Wazuh's vulnerability detection and found again by an authenticated OpenVAS scan — both synced into Vulnerability Management — gives you higher-confidence signal on the same host.
- **Both control types covered.** Wazuh SCA failures map to SCF controls as fleet evidence for endpoint-hardening controls, while OpenVAS covers the internal-scanning controls many frameworks require (e.g., PCI-DSS) — together spanning both requirements.

## How they fit together

The two integrations sit at different depths in the platform:

- **Wazuh telemetry streams into the platform** — agents become assets, alerts reach the centralized **[Alerts](../vulnerability-risk/alerts.md)**, and host CVE state becomes vulnerability occurrences in **[Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx)**. SCA and FIM are browsed in the Endpoint Security dashboard.
- **OpenVAS results are synced over GMP** — the latest report of each Greenbone scan task becomes vulnerability occurrences (one per check, host and port) in the same Vulnerability Management views, every 30 minutes and within minutes of a scan finishing. Scans can be started, stopped, created, edited, deleted and scheduled from **Infra Command Center → Network VAPT (OpenVAS)**, as well as in the Greenbone console.
- **Wazuh agents are OpenVAS targets** — each host in Endpoint 360 shows its OpenVAS scan state and can be scanned from there, and the **OpenVAS coverage** tab in Endpoint Security lists which Wazuh hosts have been scanned, not scanned, are in progress or failed. See the [OpenVAS Scanning deep-dive](../on-premises/openvas-scanning.md).

Together they give you continuous host visibility *and* network vulnerability assessment in one place — covering the endpoint-hardening and internal-scanning controls that regulated environments require.

## Get started

1. Connect **[Wazuh](./wazuh.md)** (Manager API + Indexer).
2. Connect **[OpenVAS](./openvas.md)** (GMP on port 9390), then create scans for your internal scope from **Network VAPT (OpenVAS)** or the Greenbone console. Add scan credentials for authenticated scans, which find missing patches on each host (see the [OpenVAS Scanning deep-dive](../on-premises/openvas-scanning.md)).
3. Use the **OpenVAS coverage** tab in Endpoint Security to find Wazuh hosts that have never been scanned.
4. Review host and network findings together in **[Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx)**, and Wazuh alerts in **[Alerts](../vulnerability-risk/alerts.md)**.

For the full architecture of internal coverage, see the **[On-Premises](../on-premises/index.mdx)** section.
