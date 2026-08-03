---
title: "Wazuh Integration"
sidebar_label: "Wazuh"
sidebar_position: 3
---

# Wazuh Integration

Connect your **Wazuh** deployment to bring host-level security telemetry — endpoint detections, SIEM events, vulnerability state, file-integrity monitoring, and compliance checks — into the same unified view as your cloud, application, and container posture. Wazuh data doesn't sit in a separate console; it's rendered inside Offload Security and correlated with the rest of your findings.

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
| **Compliance (SCA)** | Security Configuration Assessment (CIS-style) results per host, as compliance evidence. |
| **File Integrity Monitoring** | Changes to critical files and directories on monitored systems. |
| **MITRE ATT&CK** | Detections mapped to adversary techniques. |

## How the connection works

Wazuh exposes its data through two services, and the platform connects to both:

- **Wazuh Manager API** — agents, Security Configuration Assessment (SCA), File Integrity Monitoring, and manager status.
- **Wazuh Indexer (OpenSearch)** — security alerts/events and vulnerability state.

## Connect Wazuh

1. In the platform, open **Integrations** and choose **Add Integration → Wazuh**.
2. Enter your **Wazuh Manager API** URL and credentials, and your **Wazuh Indexer (OpenSearch)** endpoint and credentials.
3. **Test the connection.** The platform makes a live call to both services and reports success, an empty result, or a specific error — a connectivity or permission problem is shown, never hidden.
4. **Save.** Credentials are stored **encrypted at rest** and isolated to your **active team**. Wazuh data begins flowing into the dashboard and into unified Alerts and Vulnerability Management.

## Where the data goes

- **Alerts** — host detections are triaged alongside cloud, application, and compliance alerts, deduplicated rather than multiplied. See **[Notifications & Alerts](./notifications.md)**.
- **Vulnerability Management** — host vulnerability state joins the unified **[Vulnerability Management](../vulnerability-risk/vulnerability-management.mdx)** view.
- **Compliance & Evidence** — SCA and FIM results become audit evidence.

## Related

- **[OpenVAS](./openvas.md)** — network vulnerability scanning of internal and private assets.
- **[Wazuh + OpenVAS together](./wazuh-openvas.md)** — complete internal coverage: endpoint/SIEM plus network vulnerability scanning.
- **[On-Premises deep-dive](../on-premises/wazuh-integration.md)** — full Wazuh capability reference.
