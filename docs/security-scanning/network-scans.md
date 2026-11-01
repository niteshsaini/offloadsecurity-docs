---
title: "Network Scans & VAPT Report"
sidebar_label: "Network Scans & VAPT"
sidebar_position: 2.2
description: "Port-scan hosts and ranges with Nmap — all TCP ports, UDP, -Pn, timing and OS detection — then download the network / infrastructure VAPT report and see which findings the host's Wazuh agent confirms."
new_in: 1.4.0
---

# Network Scans & VAPT Report

Network testing has three parts in 1.4.0: **Nmap** targeted runs for ports, services and OS, the **Network VAPT report** that combines Nmap with Greenbone OpenVAS results into one auditor-ready deliverable, and a **host-side verdict** from the Wazuh agent on the same machine. This page covers all three.

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

**Rescan** repeats the run with the same profile, `-Pn`, timing and exclusions.

### What the result tells you honestly

- **OS detection** needs raw sockets. The Docker scanner engine has them; a run on an unprivileged local engine records **Not done: OS detection skipped** in the run detail instead of implying it ran.
- **UDP** on an unprivileged engine is refused before it starts, with a message, rather than failing inside Nmap.
- If **no host answered discovery**, the run is **partial** ("nothing was port-scanned"), not "0 open ports", and the reason suggests re-running with `-Pn`.
- If Nmap **times out**, the hosts it finished are kept and the run is **partial**. The run records hosts up, down and total.
- The run detail shows the Nmap version and options that ran and links to the kept raw output (XML and normal output).

## Network VAPT report

**Where:** left navigation → **Audit Reports** → **Network VAPT report** → **VAPT report (PDF)** or **VAPT report (Word)**.

The report is built when you download it, from the **latest Greenbone OpenVAS report of each task** and the **latest Nmap scan of each target**. It contains:

| Section | Content |
| --- | --- |
| 1. Scope and methodology | Targets, test windows, tools and versions (Nmap from the run's provenance; the OpenVAS version is shown as not recorded), the Greenbone result filter, per-host authenticated coverage where recorded |
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
- More in [Scanning Troubleshooting](./troubleshooting.md#web-api--host-scans).

## Next steps

- [Scan Results](./scan-results.md) — compare a run with the previous run of the same target.
- [Engagement & Evidence](./scan-evidence.md) — authorization, provenance and export fingerprints.
