---
title: "Wazuh Integration"
sidebar_label: "Wazuh"
sidebar_position: 5
description: "Connect Wazuh (Manager API + Indexer) to bring agents, alerts and host vulnerability state into the platform — what is synced every 30 minutes, where it lands, and the Endpoint Security dashboard."
---

# Wazuh Integration

Connect your **Wazuh** deployment to bring host-level security telemetry — endpoint detections, SIEM events, vulnerability state, file-integrity monitoring, and compliance checks — into the same unified view as your cloud, application, and container posture. Wazuh data doesn't sit in a separate console; agents, alerts and host CVEs are synced into the platform's own inventory, alert stream and vulnerability views, and the rest is browsed live from an in-platform dashboard.

:::tip[Looking for the full picture?]
This page covers connecting Wazuh as an integration. For the complete capability walkthrough — the in-platform dashboard, MITRE ATT&CK mapping, active response, and how host data feeds Vulnerability Management and Compliance — see the **[Wazuh Integration deep-dive](../on-premises/wazuh-integration.md)**.
:::

## What Wazuh brings in

Once connected, the platform ingests and presents:

| Data type | What you see |
|---|---|
| **Agents** | Endpoint inventory with active / disconnected status and health across the fleet. |
| **Security events & alerts** | Host detections, prioritized and browsable, feeding the platform's centralized Alerts. |
| **Vulnerability state** | Which monitored hosts are affected by which CVEs. |
| **Compliance (SCA)** | Security Configuration Assessment (CIS-style) results per host, browsed in the Endpoint Security dashboard. |
| **File Integrity Monitoring** | Changes to critical files and directories on monitored systems. |
| **MITRE ATT&CK** | Detections mapped to adversary techniques. |

## How the connection works

Wazuh exposes its data through two services, and the platform connects to both:

- **Wazuh Manager API** — agents, Security Configuration Assessment (SCA), File Integrity Monitoring, and manager status.
- **Wazuh Indexer (OpenSearch)** — security alerts/events and vulnerability state.

## Connect Wazuh

**Integrations → Wazuh → Connect.** The wizard asks for:

| Field | Value |
| --- | --- |
| `wazuh_host` · `wazuh_port` | The Manager API host and port (`55000`) |
| `api_username` · `api_password` | A Manager API user — read-only is enough |
| `verify_ssl` · `ca_cert` | Keep verification on and paste your CA certificate for a private PKI; off only for a self-signed lab |
| `indexer_host` · `indexer_port` · `indexer_username` · `indexer_password` *(optional)* | The Indexer (OpenSearch) for alerts and vulnerability state. Leave blank on a single-node deployment — the Manager host on `9200` with the same credentials is assumed |

The connection test authenticates to the Manager **and** checks the Indexer. A Manager-only success with an unreachable Indexer is shown as a **warning you must accept**: agents will sync, alerts and vulnerabilities will stay empty until the Indexer is reachable. Wazuh normally lives on a private network — on an on-premises install set `ALLOW_PRIVATE_SCAN_TARGETS=true` or the private address is refused before any connection is attempted.

## What a sync does

Every 30 minutes (and on **Sync now**) the platform pulls agents from the Manager and alerts, vulnerabilities and active responses from the Indexer, then:

| Wazuh data | Where it lands |
| --- | --- |
| **Agents** | [Asset Inventory](../cloud-security/asset-inventory.md) as endpoints (name, IP, OS, agent status), and the security graph used by [Attack Paths](../cloud-security/attack-paths.md) |
| **Alerts** (rule level ≥ 7) | The unified [Alerts](../vulnerability-risk/alerts.md) stream, de-duplicated per rule and agent, with MITRE ATT&CK technique ids |
| **Vulnerability state** | Vulnerability occurrences per host in [Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx), so a CVE on a server is triaged next to the same CVE in a container image |
| **SCA and FIM** | Browsed live per agent in the Endpoint Security dashboard (below); not copied into compliance evidence automatically |

## The Endpoint Security dashboard

**Where:** **Infra Command Center → Endpoint Security** (the tab appears once Wazuh is connected for the team).

Overview counts, then tabs for **Agents**, **Alerts**, **Vulnerabilities**, **Compliance** (SCA results per agent), **FIM** and **MITRE**. Agents, alerts and vulnerabilities are browsable beyond the sync snapshot — the dashboard queries your Wazuh directly with the stored credentials — and a dataset the Indexer refused is flagged on the page rather than shown empty.

## Related

- **[OpenVAS](./openvas.md)** — network vulnerability scanning of internal and private assets.
- **[Wazuh + OpenVAS together](./wazuh-openvas.md)** — complete internal coverage: endpoint/SIEM plus network vulnerability scanning.
- **[On-Premises deep-dive](../on-premises/wazuh-integration.md)** — full Wazuh capability reference.
