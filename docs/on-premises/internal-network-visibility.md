---
title: "Internal Network Visibility"
sidebar_label: "Internal Network Visibility"
sidebar_position: 2
description: "How hosts and endpoints behind the firewall get into the platform — network discovery scans of private ranges run by the on-premises workers, Wazuh agents synced into Asset Inventory and the security graph, and cloud-side private resources — and what each path does and does not give you."
---

# Internal Network Visibility

The platform builds its picture of your internal estate from three sources, none of them magic: **network scans** you point at private ranges, the **Wazuh agents** you have deployed, and the **cloud inventory** for private resources inside your VPCs. Knowing which source feeds which view is what keeps the inventory honest.

## Three ways in

| Source | What it produces | Where it lands | Continuous? |
| --- | --- | --- | --- |
| **Network discovery scan** (nmap, run by the scan worker) against a host, range or CIDR on your LAN | Live hosts, open ports, protocol, state, detected service and version — as findings of a scan | [Scan Results](../security-scanning/scan-results.md) · unified findings; port exposure feeds [Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx) | On the schedule you give it in [Scan Management](../security-scanning/scan-management.md) |
| **Wazuh agents** on servers and workstations | Endpoints with name, IP, OS and agent status; host CVEs; alerts | [Asset Inventory](../cloud-security/asset-inventory.md) (type *endpoint*), the security graph behind [Attack Paths](../cloud-security/attack-paths.md), Vulnerability Management, [Alerts](../vulnerability-risk/alerts.md) | Every 30 minutes |
| **Cloud scans** of your accounts | Private-subnet instances, databases, internal load balancers and the network paths between them | Asset Inventory, identity and network analysis | Per cloud scan schedule |

Private targets are only reachable when the operator has set `ALLOW_PRIVATE_SCAN_TARGETS=true` — see [Deployment & Operations](./deployment.md#the-env-values-that-matter-on-premises). Without it, a `10.x` target is refused with an explicit *SSRF protection* message.

## Running a network discovery scan

**Where:** **Scanning** → new scan → **Network** assessment.

1. Enter the target: a hostname, an IP, or a CIDR your scan worker can reach.
2. Choose a rate-limit profile — *gentle* for production segments, *normal* by default.
3. Schedule it (weekly is typical for a segment; daily for a DMZ) so new hosts and newly opened ports show up as *new* findings rather than a surprise.

Results list every host and port with the service nmap identified; changes between runs are visible in the findings' first-seen / last-seen. Pair a discovery scan with [Private Infrastructure Scanning](./private-infrastructure-scanning.md) of the web and API services it finds.

## What this is not

- There is no passive network sensor or agentless continuous discovery of your LAN. Coverage is exactly the union of the ranges you scan and the hosts that run a Wazuh agent.
- Network findings describe exposure (a port is open, a service is old); they are not authenticated vulnerability assessments of the host. For that, use Wazuh's vulnerability detection (synced in) or [Greenbone / OpenVAS](./openvas-scanning.md) (results stay in Greenbone).

## Related

- [Wazuh Integration](./wazuh-integration.md) — the agent-based half.
- [Asset Inventory](../cloud-security/asset-inventory.md) — where endpoints and cloud assets meet.
- [Scanning](../security-scanning/native-scans.md) — every assessment type, including Network.
