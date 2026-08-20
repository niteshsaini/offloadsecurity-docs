---
title: "OpenVAS Integration"
sidebar_label: "OpenVAS"
sidebar_position: 4
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

1. Deploy or identify your OpenVAS / Greenbone instance inside the network where your assets live.
2. In the platform, open **Integrations** and choose **Add Integration → OpenVAS**.
3. Enter your OpenVAS endpoint and credentials, and define the target scope (hosts / ranges) to scan.
4. **Test the connection**, then **Save**. Credentials are stored **encrypted at rest** and isolated to your **active team**.
5. Run and review your network scans from the OpenVAS / Greenbone console.

## Scope of the integration

:::note[Connectivity integration]
This integration establishes and validates the connection to your OpenVAS/Greenbone instance so it fits into your overall program. **Automated import of OpenVAS scan results into the platform's unified [Vulnerability Management](../vulnerability-risk/vulnerability-management.mdx) is not part of the integration today** — OpenVAS remains the system of record for these scans, and it's where the scan configuration and results live. (Wazuh, by contrast, does stream telemetry into the platform — see **[Wazuh](./wazuh.md)**.)
:::

## Related

- **[Wazuh](./wazuh.md)** — endpoint security and SIEM-style monitoring for on-premises hosts.
- **[Wazuh + OpenVAS together](./wazuh-openvas.md)** — pair endpoint/SIEM visibility with network vulnerability scanning for complete internal coverage.
- **[On-Premises deep-dive](../on-premises/openvas-scanning.md)** — full OpenVAS scanning reference.
