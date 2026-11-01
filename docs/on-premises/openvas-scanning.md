---
title: "OpenVAS Vulnerability Scanning"
sidebar_label: "OpenVAS Scanning"
sidebar_position: 5
description: "Connect Greenbone / OpenVAS over GMP so the latest report of every scan task lands in Vulnerability Management as network findings, correlated with the Wazuh agent on the same host and rolled into a downloadable network VAPT report — and run the bundled Greenbone stack if you do not have one."
---

# OpenVAS Vulnerability Scanning

Greenbone / OpenVAS answers a question the platform's own scanners do not: *which patches are missing on this internal host*, from the network, with credentials where you give them. From 1.4.0 the platform connects to Greenbone over **GMP** (the Greenbone Management Protocol) and imports its results.

## What the integration does

| | |
| --- | --- |
| Connect to your Greenbone instance over GMP (TLS, port 9390) and verify an authenticated read | **Yes** |
| Import the **latest report of each scan task** as vulnerability findings — one per check (NVT), host and port | **Yes**, on connect, every 30 minutes and on **Sync now** |
| Resolve findings a clean rescan no longer reports; reopen them if they return | **Yes** |
| Match each finding to the Wazuh agent on the same host and check Wazuh's package inventory for the same CVEs | **Yes** — evidence only, see [below](#host-side-correlation-with-wazuh) |
| Build a network VAPT report (PDF or Word) from Greenbone and nmap results | **Yes** |
| Define targets, scan configurations or schedules, or start scans | **No** — done in Greenbone. The platform reads results; it does not start OpenVAS scans |

Findings land in [Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx) as network findings, next to host CVEs from Wazuh and image CVEs from container scans, and on each matching host's [Endpoint 360](./endpoint-security.md#endpoint-360).

## Connect

**Integrations → Greenbone OpenVAS → Connect.**

| Field | Value |
| --- | --- |
| **Username** · **Password** | A Greenbone user that can read your tasks and reports |
| **Gmp Host** · **Gmp Port** | The Greenbone host and the **GMP** port — `9390` by default. Not the 9392 web interface, which has no GMP |
| **Verify SSL** · **Ca Cert** | Keep verification on and paste the server's certificate (Greenbone's is usually self-signed); turn it off only in a lab |

The test signs in over GMP and reads with that session; a wrong password, the web UI port or an untrusted certificate each gets its own message. Integrations may reach private addresses by default (`ALLOW_PRIVATE_INTEGRATION_TARGETS`, default true); loopback and metadata addresses are always refused.

## How results are imported

- **Latest report per task.** A re-scan replaces that task's results rather than adding to them.
- **Greenbone's default filter applies**: log-level results and results below 70% quality of detection are not imported; overrides you set in Greenbone are applied.
- **Severity** comes from Greenbone's severity; **CVEs** from the NVT references. Many checks are configuration findings with no CVE.
- **A clean rescan resolves** what it no longer reports, within the same Greenbone server and the tasks read in full. A finding the sync closed reopens when Greenbone reports it again.
- **A task deleted in Greenbone** closes its findings as *removed*, never as fixed.
- **Your triage stands**: false positive, accepted risk and manual resolution are never changed by a sync.
- **Bounded reads.** At most 10,000 results are imported per sync, read a page at a time. A larger total is marked *partial*, and a partial read never resolves anything.

:::tip[Restart gvmd after the first feed load]
On a fresh Greenbone install, `gvmd` caches CVE references at startup, before the feed is imported. Until it is restarted once after the first feed load, results arrive without CVEs — and Wazuh correlation has nothing to compare.
:::

## Host-side correlation with Wazuh

Each OpenVAS finding is matched to a Wazuh agent by agent IP, the IP of a linked cloud VM, or agent name, and Wazuh's package inventory on that agent is checked for the same CVEs. The verdict shows in Vulnerability Management (**Host-side (Wazuh)**) and in Endpoint 360 (**Network VAPT findings on this host**):

| Verdict | Meaning |
| --- | --- |
| Confirmed on host | Wazuh's inventory on that agent reports the CVE(s) |
| Not present per agent inventory | Wazuh reported the CVE(s) earlier and a later complete read no longer does. A *Conflict* note means the scanner still saw it afterwards — verify |
| Agent present — not reported by Wazuh | Inconclusive: the check may test a service Wazuh's package inventory does not cover |
| Agent present — no CVE to compare | A configuration or service check with no CVE |
| Several agents match this host | Not resolved automatically — fix the duplicate enrollment or link the agent to its VM |
| No agent | No host-side evidence either way |
| Not evaluated | The agent data is stale, the agent was removed, or the agent index could not be read completely |

The verdict is **evidence only**: it never closes or changes the finding. A network finding closes only when the network scanner stops detecting it. Seeing the Wazuh data needs the View Integrations permission.

## Network VAPT report

**Audit Reports → Network VAPT report → VAPT report (PDF)** or **VAPT report (Word)** builds a report from the latest Greenbone OpenVAS and nmap results when you download it: scope and methodology (tools, versions, and whether each host was scanned authenticated — OpenVAS hosts currently read *not recorded*, nmap hosts *Unauthenticated*), an executive summary, risk-rated findings with affected hosts, evidence, remediation and retest status, and annexes for host inventory, open ports and Wazuh host-side correlation. The correlation annex is included only for users who may view integrations. See [Audit Reports](../compliance/audit-reports.md).

## The bundled Greenbone stack

If you do not run Greenbone yet, `docker-compose.openvas.yml` is Greenbone's Community Edition compose, adapted to run beside the platform as its own project (`offload-openvas`):

| `.env` variable | Purpose |
| --- | --- |
| `OPENVAS_ADMIN_USER` (default `admin`) · `OPENVAS_ADMIN_PASSWORD` | The admin user `gvmd` creates on **first** start; the password is required. Use the same pair in the integration. Changing it later in `.env` does not change it in Greenbone |
| `OPENVAS_BIND` | The address the GMP (9390) and web UI (9392) ports bind to. Set it to the Docker bridge address (`.env.example` uses `172.17.0.1`) so the platform's containers reach it and other hosts do not. The platform always accepts this one host for the integration |

`scripts/setup/docker-setup.sh` writes the admin credentials and reads the docker0 address for `OPENVAS_BIND`; otherwise set them yourself. Then:

```bash
docker compose -f docker-compose.openvas.yml up -d
# print the self-signed GMP certificate to paste into the integration's Ca Cert field:
docker compose -f docker-compose.openvas.yml exec gmp-tls sed -n '/BEGIN CERT/,/END CERT/p' /certs/gmp.pem
# after the FIRST feed load finishes (about 2 hours; gvmd logs "Data objects feed sync finished"):
docker compose -f docker-compose.openvas.yml restart gvmd
```

Connect with **Gmp Host** = the `OPENVAS_BIND` address and port 9390. The first start downloads several gigabytes of feed data and needs outbound access to Greenbone's community registry; scans find nothing until the feed has loaded. The feed images are deliberately not pinned so coverage stays current; the engine images are.

## Running OpenVAS well beside the platform

- **Authenticated scans.** Give Greenbone SSH / SMB credentials for the hosts; unauthenticated scans see exposure, authenticated scans see missing patches.
- **Scope by the platform's discovery.** Use the ranges and hosts a [network discovery scan](./internal-network-visibility.md) found as the Greenbone target list, so both tools cover the same estate.
- **Agents where you can, OpenVAS everywhere.** An agent-less appliance, printer, OT controller or forgotten VM is exactly what OpenVAS reaches and Wazuh cannot; where both see a host, the correlation tells you whether they agree.

## OpenVAS and Wazuh together

| | Wazuh | OpenVAS |
| --- | --- | --- |
| Answers | What is happening on the hosts I manage | What is exposed and unpatched on everything on the network |
| Needs | An agent per host | Network reach (and credentials for depth) |
| Into the platform | Agents, alerts, host CVEs, login anomalies, SCA failures | Latest report per task as network findings, correlated with Wazuh agents |

## Related

- [OpenVAS](../integrations/openvas.md) — the Integrations-section page.
- [Wazuh Integration](./wazuh-integration.md) · [Wazuh + OpenVAS](../integrations/wazuh-openvas.md).
- [Internal Network Visibility](./internal-network-visibility.md) — the platform's own network discovery.
