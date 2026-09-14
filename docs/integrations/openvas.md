---
title: "OpenVAS Integration"
sidebar_label: "OpenVAS"
sidebar_position: 7
description: "Connect a Greenbone / OpenVAS instance so the platform verifies and monitors the connection — and be clear that scan results stay in Greenbone; they are not imported today."
---

# OpenVAS Integration

Connect **OpenVAS** (part of the Greenbone Vulnerability Management stack) to scan the internal and private assets a public SaaS scanner can't reach — internal servers, network appliances, databases, and segmented environments. OpenVAS performs the scanning inside your network, so it runs **where the assets are** and sensitive scan data stays inside your boundary; Offload Security connects to your Greenbone/OpenVAS deployment and verifies connectivity to it.

:::tip[Looking for the full picture?]
This page covers connecting OpenVAS as an integration. For scan strategy — authenticated vs. unauthenticated scanning, scheduling, and internal-network coverage — see the **[OpenVAS Scanning deep-dive](../on-premises/openvas-scanning.md)**.
:::

## What it scans

- **Internal hosts and servers** — Linux and Windows systems on the corporate network.
- **Network infrastructure** — routers, switches, firewalls, and appliances with a management interface.
- **Databases and internal services** — the backend systems behind your applications.
- **Private / segmented environments** — assets intentionally unreachable from the internet.

## What it detects

OpenVAS draws on a large, continuously updated feed of network vulnerability tests to find:

- **Known vulnerabilities (CVEs)** on internal hosts and services.
- **Missing patches and outdated software** across the internal estate.
- **Insecure configurations and exposed services** detectable over the network.
- **Weak or default credentials** where checks apply.

Scans can be **unauthenticated** (an outside-in view of what's exposed) or **authenticated** (credentialed scans that inspect installed software and patch levels for far deeper accuracy).

## Connect OpenVAS

**Integrations → Greenbone OpenVAS → Connect.** The wizard asks for:

| Field | Value |
| --- | --- |
| `gmp_host` · `gmp_port` | The host and **web (Greenbone Security Assistant) port** of your Greenbone instance — `9392` by default. The field is named for GMP, but the platform signs in to GSA's web API, not the raw GMP socket on 9390 |
| `username` · `password` | A Greenbone user |
| `verify_ssl` · `ca_cert` *(optional)* | TLS verification and a private CA certificate |

The connection test signs in to the Greenbone web API (and reads its version) before anything is saved; the health check repeats it on the cadence you choose. Targets, scan configurations and schedules are defined in the Greenbone console — the platform does not push them.

## Scope of the integration

:::note[Connectivity integration]
This integration establishes and validates the connection to your OpenVAS/Greenbone instance so it fits into your overall program. **Automated import of OpenVAS scan results into the platform's unified [Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx) is not part of the integration today** — OpenVAS remains the system of record for these scans, and it's where the scan configuration and results live. (Wazuh, by contrast, does stream telemetry into the platform — see **[Wazuh](./wazuh.md)**.)
:::

## Related

- **[Wazuh](./wazuh.md)** — endpoint security and SIEM-style monitoring for on-premises hosts.
- **[Wazuh + OpenVAS together](./wazuh-openvas.md)** — pair endpoint/SIEM visibility with network vulnerability scanning for complete internal coverage.
- **[On-Premises deep-dive](../on-premises/openvas-scanning.md)** — full OpenVAS scanning reference.
