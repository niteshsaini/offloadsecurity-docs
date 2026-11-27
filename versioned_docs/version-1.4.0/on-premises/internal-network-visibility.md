---
title: "Internal Network Visibility"
sidebar_label: "Internal Network Visibility"
sidebar_position: 2
description: "How hosts and endpoints behind the firewall get into the platform — nmap discovery scans of private ranges run by the on-premises workers, Wazuh agents synced into Asset Inventory and the security graph, Greenbone / OpenVAS results, and cloud-side private resources — and what each path does and does not give you."
---

# Internal Network Visibility

The platform builds its picture of your internal estate from four sources, none of them magic: **network scans** you point at private ranges, the **Wazuh agents** you have deployed, the **Greenbone / OpenVAS** scans you run, and the **cloud inventory** for private resources inside your VPCs. Knowing which source feeds which view is what keeps the inventory honest.

## Four ways in

| Source | What it produces | Where it lands | Continuous? |
| --- | --- | --- | --- |
| **Network discovery scan** (nmap, run by the scan worker) against a host, range or CIDR on your LAN | Live hosts, open ports, protocol, state, detected service and version — as findings of a scan | [Scan Results](../security-scanning/scan-results.md) · unified findings; port exposure feeds [Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx) | On the schedule you give it in [Scan Management](../security-scanning/scan-management.md) |
| **Wazuh agents** on servers and workstations | Endpoints with name, IP, OS and agent status, linked to their cloud VM where one matches; host CVEs; alerts and login anomalies | [Asset Inventory](../cloud-security/asset-inventory.md), the security graph behind [Attack Paths](../cloud-security/attack-paths.md), Vulnerability Management, [Alerts](../vulnerability-risk/alerts.md), [Endpoint Security](./endpoint-security.md) | Every 30 minutes |
| **Greenbone / OpenVAS** scan tasks you run in Greenbone | Network vulnerability findings per check, host and port, from the latest report of each task | Vulnerability Management; Endpoint 360 of the matching Wazuh host — see [OpenVAS Scanning](./openvas-scanning.md) | Every 30 minutes (reads what Greenbone has scanned) |
| **Cloud scans** of your accounts | Private-subnet instances, databases, internal load balancers and the network paths between them | Asset Inventory, identity and network analysis | Per cloud scan schedule |

Private scan targets are only reachable when the operator has set `ALLOW_PRIVATE_SCAN_TARGETS=true` — see [Deployment & Operations](./deployment.md#the-env-values-that-matter-on-premises). Without it, a `10.x` target is refused with an explicit *SSRF protection* message. Integrations such as Wazuh and Greenbone may reach private addresses by default (`ALLOW_PRIVATE_INTEGRATION_TARGETS`).

## Running a network discovery scan

**Where:** **Scanning → New scan → Network Discovery (Nmap)**.

1. **Enter the target**: a hostname, an IP, or a CIDR your scan worker can reach. One scan covers at most `SCAN_MAX_NETWORK_HOSTS` addresses (default 4096, a /20); list hosts to leave out under exclusions.
2. **Record the authorization** — who approved testing the target. It is stored with the scan; with `SCAN_REQUIRE_AUTHORIZATION=true` a scan without it is refused.
3. **Choose the nmap configuration:**

   | Configuration | Covers |
   | --- | --- |
   | Ping Sweep | Host discovery only |
   | Port Scan · Service Detection | Top 1000 TCP ports; service and version detection on the second |
   | Full TCP | All 65,535 TCP ports with service detection |
   | UDP | Top 100 UDP ports (needs the Docker scanner engine; refused up front otherwise) |
   | Comprehensive | Services and default scripts; OS detection when nmap runs on the Docker scanner engine (otherwise the run records that OS detection was skipped) |
   | Vulnerability Scan | nmap vuln scripts over the top 1000 TCP ports |

4. **Optionally** tick **Skip host discovery (-Pn)** for hosts that drop ping probes (otherwise they are reported down and not scanned), and pick a **Timing**: *Polite (-T2)* for fragile segments, *Normal (-T3)* or *Aggressive (-T4)*.
5. **Schedule it** (weekly is typical for a segment; daily for a DMZ) so new hosts and newly opened ports show up as *new* findings rather than a surprise.

Results list every host and port with the service nmap identified. Compare a run with the previous run of the same target to see what is new, fixed and unchanged; the options used are recorded with the run and reused by **Rescan**. Pair a discovery scan with [Private Infrastructure Scanning](./private-infrastructure-scanning.md) of the web and API services it finds.

## What this is not

- There is no passive network sensor or agentless continuous discovery of your LAN. Coverage is exactly the union of the ranges you scan (with nmap or Greenbone) and the hosts that run a Wazuh agent.
- nmap findings describe exposure (a port is open, a service is old); they are not authenticated vulnerability assessments of the host. For that, use Wazuh's vulnerability detection or authenticated [Greenbone / OpenVAS](./openvas-scanning.md) scans — both are imported.

## Related

- [Wazuh Integration](./wazuh-integration.md) — the agent-based half.
- [Asset Inventory](../cloud-security/asset-inventory.md) — where endpoints and cloud assets meet.
- [Scanning](../security-scanning/native-scans.md) — every assessment type, including Network.
