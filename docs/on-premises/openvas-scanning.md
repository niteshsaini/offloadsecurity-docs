---
title: "OpenVAS Vulnerability Scanning"
sidebar_label: "OpenVAS Scanning"
sidebar_position: 5
description: "Greenbone / OpenVAS is the authenticated network vulnerability scanner for the internal estate. The platform connects to your instance and keeps the connection healthy; scans, targets and results stay in Greenbone today — this page is honest about that split and about how to run the two together."
---

# OpenVAS Vulnerability Scanning

Greenbone / OpenVAS answers a question the platform's own scanners do not: *which patches are missing on this internal host*, from the inside, with credentials. It belongs in an on-premises programme. What the platform does with it today is narrower than a full import, and it is worth being precise.

## What the integration does today

| | Status |
| --- | --- |
| Connect to your Greenbone instance (web API sign-in, version read) and re-check it on the health schedule | **Yes** |
| Show the connection on the Integrations hub with *Connected & healthy* / the error | **Yes** |
| Define targets, scan configurations or schedules from the platform | No — done in the Greenbone console |
| Import OpenVAS results as findings or occurrences | **No** — results stay in Greenbone; the catalog badge says *connection test only* |
| Correlate OpenVAS CVEs with Wazuh host CVEs | Not automatically; both name the host, so the comparison is a manual one today |

Treat the connection as the wiring for the future import and as the inventory record that you *have* an internal scanner — not as a data source yet. For host-level CVEs that do land in [Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx), use [Wazuh's vulnerability detection](./wazuh-integration.md).

## Connect

**Integrations → Greenbone OpenVAS → Connect.**

| Field | Value |
| --- | --- |
| `gmp_host` · `gmp_port` | Host and **web (Greenbone Security Assistant) port** — `9392` by default. Despite the name, the platform signs in to the GSA web API, not the raw GMP socket on 9390 |
| `username` · `password` | A Greenbone user; read access is enough |
| `verify_ssl` · `ca_cert` | Keep verification on and paste your CA certificate for Greenbone's usual self-signed or private-CA certificate; off only for a lab |

The instance is on your LAN, so `ALLOW_PRIVATE_SCAN_TARGETS=true` must be set on the platform host or the address is refused before any connection is attempted. Full wizard behaviour: [Connecting Tools](../integrations/connecting-tools.md).

## Running OpenVAS well beside the platform

- **Authenticated scans.** Give Greenbone SSH / SMB credentials for the hosts; unauthenticated scans see exposure, authenticated scans see missing patches. Wazuh already tells you the exposed package versions; OpenVAS confirms them and finds what an agentless host has.
- **Scope by the platform's discovery.** Use the ranges and hosts a [network discovery scan](./internal-network-visibility.md) found as the Greenbone target list, so both tools cover the same estate.
- **Bring the numbers in as evidence.** Until results import, export Greenbone's report PDF and attach it to the relevant controls in the [Evidence Hub](../compliance/evidence-hub.md) (internal vulnerability scanning is an explicit requirement in PCI DSS and most frameworks); the connection record plus the report is what an auditor asks for.

## OpenVAS and Wazuh together

| | Wazuh | OpenVAS |
| --- | --- | --- |
| Answers | What is happening on the hosts I manage | What is exposed and unpatched on everything on the network |
| Needs | An agent per host | Network reach (and credentials for depth) |
| Into the platform today | Agents, alerts, host CVEs synced; SCA / FIM browsed | Connection only |

An agent-less appliance, printer, OT controller or forgotten VM is exactly what OpenVAS reaches and Wazuh cannot — which is why both belong in the estate even while only one flows into the platform.

## Related

- [OpenVAS](../integrations/openvas.md) — the Integrations-section page with troubleshooting.
- [Wazuh Integration](./wazuh-integration.md) · [Wazuh + OpenVAS](../integrations/wazuh-openvas.md).
- [Internal Network Visibility](./internal-network-visibility.md) — the platform's own network discovery.
