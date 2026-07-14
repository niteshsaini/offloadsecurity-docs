---
title: "OpenVAS Vulnerability Scanning"
sidebar_label: "OpenVAS Scanning"
sidebar_position: 4
---

# OpenVAS Vulnerability Scanning

OpenVAS (part of the Greenbone Vulnerability Management stack) is the platform's engine for **network vulnerability scanning of internal and private assets.** It complements cloud posture assessment and application testing with deep, host-level vulnerability detection against the systems that live inside your network — servers, network devices, databases, and appliances that a public SaaS scanner can't reach.

Running OpenVAS inside your environment means the scan happens **where the assets are**, and the results flow straight into Offload Security's unified **[Vulnerability Management](../vulnerability-risk/vulnerability-management.md)**.

## What it scans

- **Internal hosts and servers** — Linux and Windows systems on the corporate network.
- **Network infrastructure** — routers, switches, firewalls, and other appliances with a management interface.
- **Databases and internal services** — the backend systems behind your applications.
- **Private and segmented environments** — assets in networks that are intentionally unreachable from the internet.

## What it detects

OpenVAS draws on a large, continuously updated feed of network vulnerability tests to identify:

- **Known vulnerabilities (CVEs)** on internal hosts and services.
- **Missing patches and outdated software** across the internal estate.
- **Insecure configurations and exposed services** detectable over the network.
- **Weak or default credentials and services** where checks apply.

Scans can be **unauthenticated** (an outside-in view of what's exposed on the network) or **authenticated** (credentialed scans that inspect installed software and patch levels for far deeper accuracy). Authenticated scanning of internal hosts is typically where OpenVAS delivers the most value.

## Why it matters for internal and private environments

- **Reaches what cloud tools can't.** Internal servers, OT/IoT, and appliances are a major part of enterprise risk and are invisible to external scanners.
- **Depth on the host.** Network vulnerability scanning finds missing patches and vulnerable services that a configuration-only assessment won't surface.
- **Data residency.** Because the scanner runs on your infrastructure, scan data about sensitive internal systems stays inside your boundary — important for banking, healthcare, and other regulated sectors.
- **Regulatory expectation.** Regular internal vulnerability scanning is an explicit control in many frameworks (for example, PCI-DSS internal scanning requirements). OpenVAS provides the capability and the evidence.

## How results flow into the platform

OpenVAS findings are normalized into the same finding schema as every other source, so an internal-host CVE behaves exactly like a cloud or application finding:

- **Triaged in one queue** — deduplicated and risk-scored in **[Vulnerability Management](../vulnerability-risk/vulnerability-management.md)**.
- **Tracked to SLA** and promoted into the **[Risk Register](../vulnerability-risk/risk-register.md)** with a treatment plan.
- **Counted toward compliance** and captured as **[audit evidence](../compliance/evidence-hub.md)**.
- **Correlated with the asset** in the shared **[Asset Inventory](../cloud-security/asset-inventory.md)**, and with endpoint activity from **[Wazuh](./wazuh-integration.md)** on the same host.

## Setting it up

1. Deploy OpenVAS/Greenbone inside your network with reachability to the target segments.
2. Connect it to Offload Security and define the internal targets to scan (drawn from **[Internal Network Visibility](./internal-network-visibility.md)** or specified directly).
3. Schedule scans; results appear in Vulnerability Management alongside your cloud, application, and container findings.

:::note[Positioning and credentials]
Scan quality depends on network reachability and, for authenticated scans, valid host credentials. Placement of the scanner relative to your network segments is part of deployment planning handled during onboarding.
:::

## OpenVAS and Wazuh together

OpenVAS and Wazuh are complementary halves of internal coverage:

- **OpenVAS** answers *"what vulnerabilities exist on this host and network?"* — active, scan-based detection.
- **[Wazuh](./wazuh-integration.md)** answers *"what is happening on this host?"* — passive, agent-based monitoring, events, and integrity.

Run both, and an internal server has both its weaknesses (OpenVAS) and its live activity and hardening state (Wazuh) represented in one correlated view.
