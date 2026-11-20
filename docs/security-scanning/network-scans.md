---
title: "Network Scans & VAPT Report"
sidebar_label: "Network Scans & VAPT"
sidebar_position: 2.2
description: "Port-scan hosts and ranges with Nmap, run Greenbone OpenVAS vulnerability scans (with or without host credentials) from the platform, download the network / infrastructure VAPT report and see which findings the host's Wazuh agent confirms."
new_in: 1.4.0
---

# Network Scans & VAPT Report

Network testing has four parts: **Nmap** targeted runs for ports, services and OS, **Greenbone OpenVAS** vulnerability scans that you start from the platform (optionally logging in to each host), the **Network VAPT report** that combines Nmap with OpenVAS results into one auditor-ready deliverable, and a **host-side verdict** from the Wazuh agent on the same machine. This page covers all four.

## Before you begin

- The **Run Scans** permission to start Nmap runs.
- Authorization to test the hosts. The launcher records your attestation, the environment and any excluded hosts ([Engagement & Evidence](./scan-evidence.md)).
- Private (RFC 1918) addresses are refused unless the deployment sets `ALLOW_PRIVATE_SCAN_TARGETS=true`; loopback, link-local and cloud-metadata addresses are always refused. One run may cover at most `SCAN_MAX_NETWORK_HOSTS` addresses (default 4,096, a /20).
- For vulnerability findings in the VAPT report: a Greenbone OpenVAS connection ([OpenVAS scanning](../on-premises/openvas-scanning.md)). For host-side verdicts: a Wazuh connection ([Wazuh](../integrations/wazuh.md)).

## Run an Nmap scan

1. **Scanning** → **New scan** → **Network Discovery (Nmap)**.
2. Enter a hostname, an IP address or a CIDR range (`192.168.1.0/24`).
3. Choose the profile:

   | Profile | What Nmap does |
   | --- | --- |
   | **Ping Sweep** | Host discovery only |
   | **Port Scan** | Top 1,000 TCP ports |
   | **Service Detection** | Top 1,000 TCP ports with service and version detection |
   | **Full TCP** | All 65,535 TCP ports with service detection |
   | **UDP** | Top 100 UDP ports (Docker scanner engine only) |
   | **Comprehensive** | Services and default scripts; OS detection with the Docker scanner engine |
   | **Vulnerability Scan** | `vuln` scripts against the top 1,000 TCP ports |

4. Optionally tick **Skip host discovery (-Pn)** for hosts that drop ping probes, and choose a **Timing**: nmap default, **Polite (-T2)** for fragile targets, **Normal (-T3)**, or **Aggressive (-T4)** for fast networks.
5. Under **Authorization & scope**, attest, set the environment, and list **excluded hosts or CIDRs**, one per line. They are passed to Nmap as `--exclude`.
6. **Launch.** The run opens under **Targeted runs**.

**Rescan** repeats the run with the same profile, `-Pn`, timing and exclusions. To repeat it on a timetable, create a **Network** schedule in the Unified Scheduler, or use the **Weekly Network Scan** template ([Scan Management](./scan-management.md#scheduled-network-container-registry-and-openvas-scans)).

### What the result tells you honestly

- **OS detection** needs raw sockets. The Docker scanner engine has them; a run on an unprivileged local engine records **Not done: OS detection skipped** in the run detail instead of implying it ran.
- **UDP** on an unprivileged engine is refused before it starts, with a message, rather than failing inside Nmap.
- If **no host answered discovery**, the run is **partial** ("nothing was port-scanned"), not "0 open ports", and the reason suggests re-running with `-Pn`.
- If Nmap **times out**, the hosts it finished are kept and the run is **partial**. The run records hosts up, down and total.
- The run detail shows the Nmap version and options that ran and links to the kept raw output (XML and normal output).

## OpenVAS scans from the platform

With a Greenbone OpenVAS connection ([OpenVAS scanning](../on-premises/openvas-scanning.md)), you can start OpenVAS scans without opening Greenbone. There are four ways in:

| Where | What it does |
| --- | --- |
| **Scanning** → **New scan** → **Network Vulnerability Scan (OpenVAS, authenticated)** | A scan of up to 64 hosts, IP addresses or CIDR ranges, with excluded hosts and, optionally, scan credentials. The run appears under **Targeted runs**. |
| **Infra Command Center** → **Network VAPT (OpenVAS)** | The team's Greenbone tasks: **Scan now** or **Stop** each one, create a new scan, and edit, delete or schedule tasks created from Offload. |
| **Endpoint 360** → **Network VAPT findings** → **Trigger Network VAPT scan** | A scan of one Wazuh-monitored host. |
| **Endpoint Security** → **OpenVAS coverage** | Which endpoints are scanned, not scanned, in progress or failed; scan one host, a selection, or up to 100 unscanned hosts at a time. |

Every start asks you to confirm that you are authorized to test the targets and records it, as for Nmap. Loopback, cloud-metadata and IPv4-in-IPv6 addresses are always refused. Private address ranges are allowed by default for OpenVAS (`OPENVAS_ALLOW_PRIVATE_TARGETS=true`); an administrator can turn that off. Results of a finished scan are imported within minutes (every `OPENVAS_COMPLETION_CHECK_MINUTES`, default 5) and appear in Vulnerability Management under the OpenVAS source and on each matching host's Endpoint 360.

### Authenticated (credentialed) scans

Scan credentials let OpenVAS log in to each host and run local security checks, which find missing patches an outside scan cannot see.

- **Credential types:** SSH (password or key), SMB, SNMP v2c / v3 and ESXi. Add them from the **Scan credentials** panel of the launcher. Secrets are encrypted with the platform encryption key, are never shown again and are never written to logs.
- **Login result per host:** each host is reported as **authenticated**, **login failed**, **not confirmed** or **unauthenticated**. The VAPT report's scope section prints it per host.
- **A failed login does not close findings.** When a host's login fails, its earlier local-check findings stay open instead of being marked fixed.
- **Package findings** from a local check show the installed and the fixed package version.
- **Edit & re-run** on a finished OpenVAS run opens the launcher with its setup. The previous setup's Greenbone task is retired after the new run completes; findings on hosts you removed stay open, marked *Source removed — not re-verified*, until a scan checks those hosts again.

### Permissions

| Action | Permission |
| --- | --- |
| Start or stop a scan without credentials | **Run Scans** |
| Add, change or delete scan credentials; start a credentialed scan; edit & re-run a setup; edit, delete or schedule a task | **Manage Scans** |
| Import a finished scan's results at once from the page | **Manage Integrations** (otherwise the periodic check imports them) |

The Greenbone account Offload uses needs Greenbone's **User** role; an **Observer** account cannot create or start tasks. Credential storage, the Greenbone side and the operator settings are covered in [OpenVAS scanning](../on-premises/openvas-scanning.md).

:::note[Tested against simulated Greenbone]
In 1.4.1 pre-releases, starting OpenVAS scans, task controls and credentialed scans have been tested against a simulated Greenbone server only. Check them against your own Greenbone before relying on them.
:::

## Network VAPT report

**Where:** left navigation → **Audit Reports** → **Network VAPT report** → **VAPT report (PDF)** or **VAPT report (Word)**.

The report is built when you download it, from the **latest Greenbone OpenVAS report of each task** and the **latest Nmap scan of each target**. It contains:

| Section | Content |
| --- | --- |
| 1. Scope and methodology | Targets, test windows, tools and versions (Nmap from the run's provenance; the OpenVAS version is shown as not recorded), the Greenbone result filter, and per host whether the scan was authenticated (recorded for OpenVAS scans started from the platform; *not recorded* for tasks run only in Greenbone) |
| 2. Summary of the assessment | Executive summary, severity distribution, KEV / EPSS view, top findings |
| 3. Risk-rated findings | One entry per check (Greenbone NVT or Nmap script) with every affected host, CVSS, evidence, remediation, retest status and the Wazuh verdict |
| 4. Retest status | Findings closed on retest, findings whose scan task was removed (reported as not retested, never as fixed), and analyst decisions from the last 90 days |
| Annexures | Host inventory, open ports and services, host-side (Wazuh) correlation |
| Integrity | Whether every source could be read; a source that could not be read marks the report degraded, never "Complete" |

Who can download it: anyone with **View Vulnerabilities**, **View Scans** or **View Assessments** — including auditor and compliance roles. The Wazuh correlation columns and annexure are included only for users who can view integrations. The HTML version is available over the API (`GET /api/export/network-vapt.html`).

:::note[Point in time]
The report reflects the latest result per OpenVAS task and per Nmap target at the moment you download it. Targets whose latest Nmap run failed are disclosed, and overlapping observations of the same port are folded and counted.
:::

## Host-side correlation with Wazuh

A network scanner sees a vulnerable service from outside; it cannot tell whether the package is actually installed. When the same host runs a Wazuh agent, each OpenVAS or Nmap finding gets a **host-side verdict**, computed when you read it:

| Verdict | Meaning |
| --- | --- |
| **Confirmed on host** | Wazuh reports the same CVE on the matched agent |
| **Not present per agent inventory** | Wazuh reported it and a later complete read resolved it (a conflict is noted if the network scanner saw it again afterwards) |
| **Agent present — not reported by Wazuh** | Inconclusive |
| **Agent present — no CVE to compare** | The finding has no CVE |
| **Several agents match this host** | Ambiguous; the platform does not guess |
| **No agent** | No Wazuh agent matches the host |
| **Not evaluated** | No host on the finding, a failed read, or an agent fleet larger than one read covers |

Agents are matched by IP first (agent IP, then the IP of a linked cloud VM), then by name. The verdict is **evidence only**: it never closes, reopens or changes a finding.

**Where you see it:**

- **Vulnerability Management** → the finding's occurrence detail → **Host-side correlation (Wazuh)**.
- **Endpoint 360** for an agent → **Network VAPT findings on this host** ([Wazuh](../integrations/wazuh.md)).
- The VAPT report's findings and annexure.

Reading these needs the permission to view integrations.

## If something goes wrong

- **"Target refused" for an internal address** — set `ALLOW_PRIVATE_SCAN_TARGETS=true` on the deployment, or the range exceeds `SCAN_MAX_NETWORK_HOSTS`.
- **Partial: no host responded** — the hosts drop ping probes; tick **Skip host discovery (-Pn)** and rescan.
- **The VAPT report has no OpenVAS findings** — no Greenbone report has been ingested for the team; check the OpenVAS connection.
- **An OpenVAS host shows *login failed*** — the scan credential was rejected by that host. Its earlier local-check findings stay open; fix the credential and use **Edit & re-run**.
- **An OpenVAS start is refused with 403** — credentialed scans and edits need **Manage Scans**; run it without credentials or ask a scan manager.
- More in [Scanning Troubleshooting](./troubleshooting.md#web-api--host-scans).

## Next steps

- [Scan Results](./scan-results.md) — compare a run with the previous run of the same target.
- [Engagement & Evidence](./scan-evidence.md) — authorization, provenance and export fingerprints.
