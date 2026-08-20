---
title: "OpenVAS Vulnerability Scanning"
sidebar_label: "OpenVAS Scanning"
sidebar_position: 4
---

# OpenVAS Vulnerability Scanning

OpenVAS (part of the Greenbone Vulnerability Management stack) is a **supported integration for network vulnerability scanning of internal and private assets.** OpenVAS performs the scanning inside your network — deep, host-level vulnerability detection against servers, network devices, databases, and appliances that a public SaaS scanner can't reach. Offload Security connects to your Greenbone/OpenVAS deployment and verifies connectivity to it, so it fits alongside your cloud posture and application testing as part of one program.

Running OpenVAS inside your environment means the scan happens **where the assets are** — against the systems that live behind your perimeter.

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

## How the integration works

Offload Security connects to your Greenbone/OpenVAS deployment and **verifies connectivity** to it, so OpenVAS becomes part of your overall program rather than a wholly separate tool. You run and review the network scans in OpenVAS/Greenbone, which is where the scan configuration and results live.

:::note[Scope of the integration today]
This integration establishes and validates the connection to your OpenVAS/Greenbone instance. Automated import of OpenVAS scan results into Offload Security's unified [Vulnerability Management](../vulnerability-risk/vulnerability-management.mdx) is **not** part of the integration today — OpenVAS remains the system of record for these scans. Wazuh, by contrast, does stream telemetry into the platform (see [Wazuh Integration](./wazuh-integration.md)).
:::

## Setting it up

1. Deploy OpenVAS/Greenbone inside your network with reachability to the target segments.
2. Connect it to Offload Security, which verifies connectivity to your OpenVAS/Greenbone deployment.
3. Configure and run your network scans from the OpenVAS/Greenbone console against the internal targets (informed by **[Internal Network Visibility](./internal-network-visibility.md)** or specified directly).

:::note[Positioning and credentials]
Scan quality depends on network reachability and, for authenticated scans, valid host credentials. Placement of the scanner relative to your network segments is part of deployment planning handled during onboarding.
:::

## OpenVAS and Wazuh together

OpenVAS and Wazuh are complementary halves of internal coverage:

- **OpenVAS** answers *"what vulnerabilities exist on this host and network?"* — active, scan-based detection.
- **[Wazuh](./wazuh-integration.md)** answers *"what is happening on this host?"* — passive, agent-based monitoring, events, and integrity.

Run both for full internal coverage — OpenVAS for host and network weaknesses, and Wazuh (whose telemetry streams into the platform) for live activity and hardening state.
