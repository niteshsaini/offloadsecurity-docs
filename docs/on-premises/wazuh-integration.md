---
title: "Wazuh Integration"
sidebar_label: "Wazuh Integration"
sidebar_position: 3
---

# Wazuh Integration

Wazuh is the platform's engine for **endpoint security and SIEM-style monitoring** across your on-premises and private estate. By deploying lightweight Wazuh agents on your servers, workstations, and internal hosts — and connecting Offload Security to your Wazuh deployment — you bring host-level security telemetry into the same unified dashboard as your cloud, application, and vulnerability posture.

This is what turns Offload Security from a scanning platform into a complete view of your internal environment: not just *"what weaknesses exist"* but *"what is happening on our hosts right now."*

## What Wazuh brings into the platform

Once connected, Offload Security ingests and presents Wazuh data in a **customized in-platform dashboard**, so your team doesn't need to live in a separate SIEM console. The integration surfaces:

| Data type | What you see |
|---|---|
| **Agents** | Your fleet of Wazuh agents — endpoint inventory, active/disconnected status, and health across the environment. |
| **Security events & alerts** | The security events Wazuh generates from host logs and detections, prioritized and browsable, with the ability to drill into detail. |
| **Vulnerability information** | Wazuh's vulnerability-detection state for monitored hosts — which endpoints are affected by which CVEs. |
| **Compliance & configuration** | Security Configuration Assessment (SCA) results — CIS-style benchmark and policy checks per host — for compliance evidence. |
| **File Integrity Monitoring (FIM)** | Changes to critical files and directories on monitored systems, a core control for many frameworks. |
| **MITRE ATT&CK mapping** | Detections mapped to ATT&CK techniques, so activity is framed in terms of adversary behavior. |
| **Active response** | Visibility into Wazuh's automated response actions on the endpoint. |

## The customized dashboard

Rather than forcing analysts to context-switch into Wazuh, Offload Security renders Wazuh data inside the platform:

- **Agent and event summaries at a glance** — counts and status for agents, alerts, vulnerabilities, and compliance checks, so posture is visible without a query.
- **Per-dataset visibility with honest status.** Each data section reports whether it was fetched successfully, is empty, or hit an error — so a connectivity or permission problem is *shown*, never silently hidden.
- **Deep links to Wazuh.** Where you need the full native view, the platform links straight through to your Wazuh dashboard ("Open in Wazuh") for the underlying detail.

## SIEM-style monitoring, unified

Wazuh data doesn't just sit in its own tab — it's **correlated with the rest of your posture:**

- **Into Alerts.** Wazuh security events feed the platform's centralized **[Alerts](../integrations/notifications.md)**, so host-level detections are triaged alongside cloud, application, and compliance alerts in one place — deduplicated, not multiplied.
- **Into Vulnerability Management.** Host vulnerability state contributes to the unified **[Vulnerability Management](../vulnerability-risk/vulnerability-management.md)** view of your estate.
- **Into Compliance & Evidence.** SCA and FIM results become **[compliance evidence](../compliance/evidence-hub.md)** — proof that endpoint hardening and integrity controls are in place and monitored.

This is the SIEM value proposition without the SIEM silo: real-time host visibility that is part of your posture, not adjacent to it.

## How the integration works

Wazuh exposes its data through two services, and the platform connects to both:

- **The Wazuh Manager API** — for agents, Security Configuration Assessment (SCA), File Integrity Monitoring, and manager status.
- **The Wazuh Indexer (OpenSearch)** — for security alerts/events and vulnerability state.

:::note Configure both endpoints
The Indexer typically runs on its own host and has **separate credentials** from the Manager API. Provide both when configuring the integration so alerts, events, and vulnerability data come through — not just the agent list. The platform's connection test probes the Indexer and tells you if it's unreachable, rather than masking a partial connection.
:::

## Setting it up

1. Deploy Wazuh (Manager + Indexer) and install agents on the hosts you want to monitor — inside your network, where your assets are.
2. In Offload Security, add the **Wazuh** integration and provide the Manager API and Indexer connection details and credentials.
3. Run a sync. The dashboard populates with agents, events, alerts, vulnerabilities, SCA, and FIM — and any dataset that couldn't be fetched is flagged with the reason.

For the integrations model in general, see **[Integrations](../integrations/index.md)** and **[Third-Party Integrations](../integrations/third-party.md)**.

## Why it matters

- **The internal blind spot, closed.** Endpoints and internal servers are where a lot of real attack activity lands. Wazuh gives you eyes there, in the same platform as everything else.
- **Compliance evidence from the endpoint.** SCA and FIM produce exactly the hardening and integrity evidence auditors ask for — captured continuously.
- **One triage queue.** Host detections join cloud and app alerts in one correlated stream, cutting alert fatigue instead of adding to it.
- **Data stays in your boundary.** Wazuh runs on your infrastructure; for regulated organizations, that keeps sensitive endpoint telemetry on-prem while still feeding a unified view.

## Related

- **[OpenVAS Scanning](./openvas-scanning.md)** — network vulnerability scanning to pair with Wazuh's endpoint view.
- **[Centralized Ingestion](./centralized-ingestion.md)** — how Wazuh, OpenVAS, cloud, and app data become one picture.
