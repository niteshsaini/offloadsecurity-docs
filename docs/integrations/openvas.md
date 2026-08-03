---
title: "OpenVAS Integration"
sidebar_label: "OpenVAS"
sidebar_position: 4
---

# OpenVAS Integration

Connect **OpenVAS** (part of the Greenbone Vulnerability Management stack) to scan the internal and private assets a public SaaS scanner can't reach — internal servers, network appliances, databases, and segmented environments. Because the scan runs **where the assets are**, results flow straight into the platform's unified **[Vulnerability Management](../vulnerability-risk/vulnerability-management.mdx)** and sensitive scan data stays inside your boundary.

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
5. Run or schedule scans; findings are normalized into the platform's finding schema.

## Where the data goes

OpenVAS findings are normalized into the **same finding schema** as every other source, so an internal-host CVE behaves exactly like a cloud or application finding — deduplicated, severity-ranked, risk-mapped, and available as compliance evidence (for example, PCI-DSS internal scanning requirements).

## Related

- **[Wazuh](./wazuh.md)** — endpoint security and SIEM-style monitoring for on-premises hosts.
- **[Wazuh + OpenVAS together](./wazuh-openvas.md)** — pair endpoint/SIEM visibility with network vulnerability scanning for complete internal coverage.
- **[On-Premises deep-dive](../on-premises/openvas-scanning.md)** — full OpenVAS scanning reference.
