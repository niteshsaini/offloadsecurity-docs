---
title: "Greenbone OpenVAS Integration"
sidebar_label: "OpenVAS"
sidebar_position: 8
description: "Connect a Greenbone / OpenVAS instance over GMP so the latest results of each scan task are synced into Vulnerability Management every 30 minutes — fields, the connection test, what is synced and how findings are resolved."
---

# Greenbone OpenVAS Integration

Connect **Greenbone OpenVAS** (the Greenbone Community Edition / GVM stack) and the platform reads your network scan results over **GMP**, the Greenbone Management Protocol. The latest report of each scan task becomes vulnerability occurrences in [Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx), next to cloud, container, code and Wazuh findings. Scanning itself still runs in Greenbone, inside your network: targets, scan configurations and schedules are defined in the Greenbone console, and the platform does not push them.

:::note[Looking for the full picture?]
This page covers connecting OpenVAS as an integration. For running the bundled Greenbone stack, scan strategy, authenticated scanning and internal-network coverage, see the **[OpenVAS Scanning deep-dive](../on-premises/openvas-scanning.md)**.
:::

## Before you begin

- **Manage Integrations** permission in Offload Security.
- A Greenbone user (the platform reads tasks and reports; it does not create them).
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

## What a sync does

Every 30 minutes (and on **Sync now**), the platform reads the **latest report of each scan task**, using Greenbone's default result filter (overrides applied, quality of detection at least 70%, high / medium / low results — log-level results are skipped). Then:

| Greenbone data | Where it lands |
| --- | --- |
| Each result | One vulnerability occurrence per **check (NVT), host and port**, with severity from Greenbone, CVEs from the NVT references, the solution as the recommendation, and the task and host recorded |
| Consolidation | Occurrences of an NVT that maps to exactly one CVE consolidate on that CVE; others on the NVT itself (many checks are misconfigurations with no CVE) |

Because only the latest report of each task is read, a re-scan **replaces** that task's results rather than adding to them.

### How findings are resolved

- A finding missing from a task's latest report is resolved — but **only after a complete read**. If a read was capped or failed, the dataset is marked *partial* and nothing is resolved on its basis.
- A task deleted in Greenbone closes its findings as *task removed*, not as fixed.
- A finding the sync resolved and that appears again is reopened.
- Analyst decisions (false positive, accepted risk, a manual resolve) are never overridden by a sync.

Up to **10,000 results** are read per sync. A larger total is reported as a *partial* dataset on the card rather than cut silently.

## Check that it worked

The card shows *Connected & healthy*, the last sync time and the counts ingested. Findings appear in Vulnerability Management with the source **greenbone-openvas**.

## If something goes wrong

- **Connection refused / timeout on 9390** — gvmd's GMP is not exposed over TLS on that host and port, or a firewall blocks it. The web UI port (9392) will not work.
- **"Server URL is not allowed … (SSRF protection)"** — loopback is always refused; use the host's real address. On a deployment that set `ALLOW_PRIVATE_INTEGRATION_TARGETS=false`, only the bundled stack's `OPENVAS_BIND` address is accepted as a private target.
- **Authentication failed** — check the Greenbone user and password; on the bundled stack, the values in `.env`.

See [Troubleshooting & FAQ](./troubleshooting.md) and the [On-Premises troubleshooting](../on-premises/troubleshooting.md) page.

## Related

- **[Wazuh](./wazuh.md)** — endpoint security and SIEM-style monitoring for on-premises hosts.
- **[Wazuh + OpenVAS together](./wazuh-openvas.md)** — endpoint telemetry plus network vulnerability scanning.
- **[On-Premises deep-dive](../on-premises/openvas-scanning.md)** — full OpenVAS scanning reference.
