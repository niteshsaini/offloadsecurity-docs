---
title: "Greenbone OpenVAS Integration"
sidebar_label: "OpenVAS"
sidebar_position: 8
description: "Connect a Greenbone / OpenVAS instance over GMP, start, stop, create, edit, delete and schedule its scan tasks from the platform, and sync the latest results of each task into Vulnerability Management — fields, permissions, scan control and how findings are resolved."
---

# Greenbone OpenVAS Integration

Connect **Greenbone OpenVAS** (the Greenbone Community Edition / GVM stack) and the platform reads your network scan results over **GMP**, the Greenbone Management Protocol. The latest report of each scan task becomes vulnerability occurrences in [Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx), next to cloud, container, code and Wazuh findings. The platform can also **run** scans: start and stop Greenbone tasks, create new ones for hosts, IP addresses and CIDR ranges, and edit, delete and schedule the tasks it created. The scanning itself always runs on the Greenbone scanner inside your network.

:::note[Looking for the full picture?]
This page covers connecting OpenVAS and controlling its scans. For running the bundled Greenbone stack, credentialed (authenticated) scans, Endpoint 360 host scans, OpenVAS coverage and internal-network strategy, see the **[OpenVAS Scanning deep-dive](../on-premises/openvas-scanning.md)**.
:::

## Before you begin

- **Manage Integrations** permission in Offload Security.
- A Greenbone user. To only import results, any user that can read tasks and reports is enough. To start, create, edit or delete scans from the platform, the user must be allowed to create and start tasks in Greenbone (for example the **User** role; an **Observer** cannot).
- **GMP reachable over TLS** from the platform server, on port **9390** by default. This is gvmd's management protocol — not the Greenbone Security Assistant web UI on 9392, which has no GMP. Greenbone's official compose exposes gvmd only on a Unix socket; the bundled `docker-compose.openvas.yml` adds a TLS bridge on 9390 for this purpose.
- On the bundled stack, `OPENVAS_ADMIN_USER` / `OPENVAS_ADMIN_PASSWORD` in `.env` are the credentials to use (`docker-setup.sh` writes them), and the ports bind to `OPENVAS_BIND` (the Docker bridge, `172.17.0.1` by default).

## Connect OpenVAS

**Integrations → Greenbone OpenVAS → Connect.** The wizard asks for:

| Field | Value |
| --- | --- |
| `gmp_host` | The host running gvmd's GMP endpoint (a pasted URL is reduced to its host name) |
| `gmp_port` | `9390` by default — GMP over TLS |
| `username` · `password` | A Greenbone user |
| `verify_ssl` · `ca_cert` *(optional)* | TLS verification and a private CA certificate |

The connection test opens a GMP session, **authenticates and makes an authenticated read** before anything is saved; a wrong password is rejected there. The health check repeats it on the cadence you choose.

## Run scans from the platform

New in 1.4.1. **Infra Command Center → Network VAPT (OpenVAS)** (the tab appears once the integration is connected) lists the scan tasks the Greenbone account can see, with live status and progress, the target, the scan config and the last completed scan. The list refreshes while a task is queued or running.

| Action | What it does | Permission |
| --- | --- | --- |
| **Scan now** · **Stop** | Start or stop any task the account can see, including tasks created in the Greenbone console. Starting checks the task's targets against the same target rules as a new scan | **Run Scans** |
| **New scan** | Creates a target and task in Greenbone (named `offload-…`) for the hosts, IP addresses and CIDR ranges you enter, with a scan config (*Full and fast* preselected), port list and scanner. Untick **Start the scan now** to create the task without scanning; start it later with **Scan now** | **Run Scans** |
| **Edit** | Change the name, note, scan config, scanner, targets, excluded hosts, port list and attached scan credentials of a task created from Offload. Refused while the task is queued or running. Nothing is scanned until you start it | **Manage Scans** |
| **Schedule…** | A recurring run of the task (daily, weekly on Monday or monthly on the 1st, at an hour in UTC) through the [Scheduler](../security-scanning/scan-management.md#scheduling-recurring-scans) as scan type `openvas`. Each run re-checks the target hosts | **Manage Scans** |
| **Delete** | Moves a task created from Offload, and its target when nothing else uses it, to Greenbone's trashcan, where it can be restored. Refused while the task is running: stop it first. Imported findings are kept | **Manage Scans** |

Tasks created in the Greenbone console can only be started and stopped from here. Per-host tasks (`offload-host-…`, created by Endpoint 360 host scans) can be deleted but not edited. Tasks that belong to a credentialed network scan setup are changed through that scan setup instead (**Edit & re-run**); see the [OpenVAS Scanning deep-dive](../on-premises/openvas-scanning.md).

Who started a scan, when, and the engagement reference are written into the Greenbone task's comment. When the deployment sets `SCAN_REQUIRE_AUTHORIZATION=true` (off by default), starting a scan asks for the same authorization attestation as the other network scans.

**Target rules.** Private (RFC 1918) targets are allowed by default, because the scan runs on the Greenbone scanner, not on the platform host; set `OPENVAS_ALLOW_PRIVATE_TARGETS=false` to refuse them. Loopback, cloud-metadata and IPv4-mapped IPv6 addresses are always refused.

:::note[Host names are resolved by Greenbone]
A target given as a host name is resolved only by Greenbone. With private targets allowed, a host name that resolves to a cloud metadata address is not blocked by the platform. Enter IP addresses or CIDR ranges where this matters.
:::

**When results arrive.** Results come in through the integration sync. A scan that finishes while the Network VAPT page is open is imported straight away (this needs **Manage Integrations**; without it the page says when the results will arrive). In the background, the platform checks every `OPENVAS_COMPLETION_CHECK_MINUTES` minutes (default 5; `0` turns the check off) for finished scans that are not yet imported and syncs when it finds one. The 30-minute sync covers everything else.

## What a sync does

Every 30 minutes (and on **Sync now**), the platform reads the **latest report of each scan task**, using Greenbone's default result filter (overrides applied, quality of detection at least 70%, high / medium / low results — log-level results are skipped). Then:

| Greenbone data | Where it lands |
| --- | --- |
| Each result | One vulnerability occurrence per **check (NVT), host and port**, with severity from Greenbone, CVEs from the NVT references, the solution as the recommendation, and the task and host recorded |
| Consolidation | Occurrences of an NVT that maps to exactly one CVE consolidate on that CVE; others on the NVT itself (many checks are misconfigurations with no CVE) |

Because only the latest report of each task is read, a re-scan **replaces** that task's results rather than adding to them.

### How findings are resolved

- A finding missing from a task's latest report is resolved — but **only after a complete read**. If a read was capped or failed, the dataset is marked *partial* and nothing is resolved on its basis.
- Deleting a task is never treated as a fix. Open findings of a task Greenbone no longer has **stay open**, marked as *source removed, not re-verified*; a later complete scan of that host by any task resolves them, and seeing them again clears the marker.
- Only hosts that a report actually scanned can have findings resolved; a host that was down proves nothing.
- **Credentialed scans:** when a host's login failed or was never confirmed, its local-check findings (installed packages, registry) are held open, not resolved. Local-check findings are resolved only on a host where an SSH, SMB or ESXi login succeeded.
- UDP findings are resolved only by a task whose port list includes UDP ports.
- A finding the sync resolved and that appears again is reopened.
- Analyst decisions (false positive, accepted risk, a manual resolve) are never overridden by a sync.

Up to **10,000 results** are read per sync. A larger total is reported as a *partial* dataset on the card rather than cut silently.

## Check that it worked

The card shows *Connected & healthy*, the last sync time and the counts ingested. Infra Command Center → **Network VAPT (OpenVAS)** lists the account's tasks. Findings appear in Vulnerability Management with the source **greenbone-openvas**, under their own OpenVAS source filter and badge.

## If something goes wrong

- **Connection refused / timeout on 9390** — gvmd's GMP is not exposed over TLS on that host and port, or a firewall blocks it. The web UI port (9392) will not work.
- **"Server URL is not allowed … (SSRF protection)"** — loopback is always refused; use the host's real address. On a deployment that set `ALLOW_PRIVATE_INTEGRATION_TARGETS=false`, only the bundled stack's `OPENVAS_BIND` address is accepted as a private target.
- **Authentication failed** — check the Greenbone user and password; on the bundled stack, the values in `.env`.
- **Scan now or New scan fails with a permission error from Greenbone** — the Greenbone account cannot create or start tasks (an Observer account). Give it a role that can, such as **User**.
- **Edit, Delete or Schedule… is missing** — your Offload role lacks **Manage Scans**, or the task was not created from Offload. Edit and Delete are also unavailable while the task is queued or running.

See [Troubleshooting & FAQ](./troubleshooting.md) and the [On-Premises troubleshooting](../on-premises/troubleshooting.md) page.

## Related

- **[Wazuh](./wazuh.md)** — endpoint security and SIEM-style monitoring for on-premises hosts.
- **[Wazuh + OpenVAS together](./wazuh-openvas.md)** — endpoint telemetry plus network vulnerability scanning.
- **[On-Premises deep-dive](../on-premises/openvas-scanning.md)** — full OpenVAS scanning reference.
