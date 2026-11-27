---
title: "OpenVAS Vulnerability Scanning"
sidebar_label: "OpenVAS Scanning"
sidebar_position: 5
description: "Connect Greenbone / OpenVAS over GMP, start, stop, create, edit, delete and schedule OpenVAS scans from the platform, run authenticated (credentialed) scans with a login result per host, scan endpoints from Endpoint 360 and track OpenVAS coverage, and import the results into Vulnerability Management, correlated with Wazuh and rolled into a network VAPT report."
---

# OpenVAS Vulnerability Scanning

Greenbone / OpenVAS answers a question the platform's own scanners do not: *which patches are missing on this internal host*, from the network, with credentials where you give them. The platform connects to Greenbone over **GMP** (the Greenbone Management Protocol). From 1.4.0 it imports Greenbone's results; from 1.4.1 it can also run OpenVAS scans in your Greenbone: start and stop tasks, create new ones, log in to hosts with stored scan credentials, edit, delete and schedule the tasks it created, and scan Wazuh endpoints one at a time or in bulk.

The scans still run on your Greenbone scanner, not on the platform host. In the 1.4.1 pre-releases, scan launch, task controls and credentialed scans have been tested against a simulated Greenbone; validation against a live `gvmd` is still pending (see the [1.4.1-beta.8 release notes](../release-notes/v1-4-1-beta-8.md)).

## What the integration does

| | |
| --- | --- |
| Connect to your Greenbone instance over GMP (TLS, port 9390) and verify an authenticated read | **Yes** |
| Import the **latest report of each scan task** as vulnerability findings — one per check (NVT), host and port | **Yes**, on connect, every 30 minutes, on **Sync now**, and within minutes of a scan finishing |
| Resolve findings a clean rescan no longer reports; reopen them if they return | **Yes** |
| Start and stop any Greenbone task the account can see; create a new scan for hosts, IP addresses and CIDR ranges | **Yes** (1.4.1) — see [Run scans from the platform](#run-scans-from-the-platform) |
| Log in to hosts with SSH, SMB, SNMP or ESXi credentials and report each host's login result | **Yes** (1.4.1) — see [Authenticated scans](#authenticated-credentialed-scans) |
| Edit, delete and schedule tasks created from the platform | **Yes** (1.4.1). Tasks created in Greenbone itself can only be started and stopped from the platform |
| Scan a Wazuh endpoint from its Endpoint 360, and show which endpoints OpenVAS has covered | **Yes** (1.4.1) — see [Scan endpoints](#scan-endpoints-endpoint-360-and-openvas-coverage) |
| Match each finding to the Wazuh agent on the same host and check Wazuh's package inventory for the same CVEs | **Yes** — evidence only, see [below](#host-side-correlation-with-wazuh) |
| Build a network VAPT report (PDF or Word) from Greenbone and nmap results | **Yes** |
| Create scan configurations or port lists | **No** — those stay in Greenbone; the platform offers the ones Greenbone has |

Findings land in [Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx) as network findings, with their own OpenVAS source tab, next to host CVEs from Wazuh and image CVEs from container scans, and on each matching host's [Endpoint 360](./endpoint-security.md#endpoint-360).

## Connect

**Integrations → Greenbone OpenVAS → Connect.**

| Field | Value |
| --- | --- |
| **Username** · **Password** | A Greenbone user that can read your tasks and reports. To run scans from the platform it must be able to create and start tasks: Greenbone's **User** role can, **Observer** cannot |
| **Gmp Host** · **Gmp Port** | The Greenbone host and the **GMP** port — `9390` by default. Not the 9392 web interface, which has no GMP |
| **Verify SSL** · **Ca Cert** | Keep verification on and paste the server's certificate (Greenbone's is usually self-signed); turn it off only in a lab |

The test signs in over GMP and reads with that session; a wrong password, the web UI port or an untrusted certificate each gets its own message. Integrations may reach private addresses by default (`ALLOW_PRIVATE_INTEGRATION_TARGETS`, default true); loopback and metadata addresses are always refused.

## Run scans from the platform

**Infra Command Center → Network VAPT (OpenVAS)** lists the scan tasks the Greenbone account can see, live from Greenbone, with status and progress. It refreshes while a task is queued or running.

### Before you begin

- The Greenbone integration is connected for the active team, with a Greenbone **User**-role account.
- **Run scans** permission to start, stop and create scans. Roles without it see the tasks and their states, but no scan buttons.
- **Manage scans** permission to edit, delete or schedule a task, and to run a credentialed scan.
- **Manage integrations** permission to import a finished scan's results at once from the page. Without it, results arrive with the next automatic check, within minutes.

### Start, stop and create

- **Scan now** starts a task; **Stop** asks Greenbone to stop a running one.
- **New scan** creates a target and a task in Greenbone, named `offload-<name>`, for the targets you enter (one host name, IP address or CIDR range per line), with the scan config, port list and scanner you pick from Greenbone's own lists. You can add excluded hosts.
- **Start the scan now** is ticked by default. Untick it to only create the task (**Create task**); start it later with **Scan now**, or schedule it.
- Starting a scan asks for the same authorization attestation as other network scans. Whether the attestation is required depends on `SCAN_REQUIRE_AUTHORIZATION`; without it, scans are recorded as "authorization not recorded".

### Edit, delete and schedule

These actions appear only on tasks created from the platform (marked **Created from Offload**) and need **Manage scans**:

| Action | What it does |
| --- | --- |
| **Edit** | Change the name, comment, scan config, scanner, hosts, excluded hosts, port list and credentials of a task that is not running. Saving does not start a scan. A change of hosts, port list or credentials gives the task a new Greenbone target, because Greenbone does not change a target in use; the old target moves to Greenbone's trashcan when the platform created it and nothing else uses it. Endpoint 360 host tasks (`offload-host-…`) and authenticated-scan tasks (`offload-auth …`) are not edited here |
| **Delete** | Moves a task that is not running, and its target, to Greenbone's trashcan, where it can be restored. Findings already imported stay open and are marked as removed from the source after the next sync. Schedules that start the task fail until it is restored |
| **Schedule…** | Creates a recurring `openvas` schedule (daily, weekly on Monday or monthly on the 1st, at an hour in UTC). Its runs, history and failures are in the [Scheduler](../security-scanning/scan-management.md) like any other scheduled scan; you can also pick the **OpenVAS (Greenbone)** type there. Each run re-checks the task's target hosts against the target rules |

The same task actions are available through the API: `PATCH`, `DELETE`, `POST …/start` and `POST …/stop` on `/api/integrations/greenbone-openvas/tasks/{id}`, and `POST /api/integrations/greenbone-openvas/scans` to create one.

### Target rules

- **Loopback and cloud-metadata addresses are always refused**, as are IPv4 addresses embedded in IPv6.
- **Private (RFC 1918) ranges are allowed by default**, because the scan runs on the Greenbone scanner, not on the platform host. Set `OPENVAS_ALLOW_PRIVATE_TARGETS=false` in `.env` to refuse them.
- **Scan now** applies the same rules to a task's existing targets.

:::note[Known issue: host names that resolve to a metadata address]
With private targets allowed (the default), a target given as a **host name** that resolves to a cloud-metadata address is not refused, because only Greenbone resolves the name. Targets given as IP addresses are checked. A fix is planned as a follow-up; until then, review host-name targets before you start a scan.
:::

## Authenticated (credentialed) scans

An unauthenticated scan sees what is exposed on the network. An authenticated scan logs in to each host and runs local security checks, which is how OpenVAS finds missing patches.

### Scan credentials

Scan credentials belong to the team and are managed in the **Scan credentials** panel of the scan form (see below) or through `/api/native-scans/network-credentials`.

| Type | Fields |
| --- | --- |
| **SSH (Linux / Unix)** | Username, password or private key (with optional passphrase), SSH port |
| **SMB (Windows)** | Username, password, optional domain |
| **SNMP (network devices)** | v2c community string, or v3 user with auth algorithm (MD5 / SHA1) and password, and optional privacy algorithm (AES / DES) and password |
| **ESXi (VMware hosts)** | Username, password |

- **Secrets are write-only.** They are encrypted with the platform key `CLOUD_ENCRYPTION_KEY`, never shown again and never logged. To rotate, enter a new secret and **Save / rotate**; a blank secret keeps the stored one. Without `CLOUD_ENCRYPTION_KEY` in `.env`, saving a credential is refused (HTTP 503) and nothing is stored; the installer generates the key. See [Encryption keys](./deployment.md#encryption-keys).
- **They are copied to Greenbone** as `offload: …` credentials before a scan uses them.
- **Deleting a credential** wipes the stored secret at once, then overwrites and deletes the Greenbone copy and reports what happened there. If a target created in Greenbone itself still uses the copy, the platform can't delete it; the credential shows a pending cleanup, which a team administrator can dismiss with a note after cleaning it up in GSA.
- Creating, rotating and deleting credentials needs **Manage scans**.

### Run an authenticated scan

1. **Scanning → New scan**, scan type **Network Vulnerability Scan (OpenVAS, authenticated)**. The form shows which Greenbone server will run it.
2. Enter up to 64 targets, separated by commas or new lines (IP address, host name or CIDR range).
3. In **Scan credentials**, choose the credentials to use, or add one. With none chosen, the scan is unauthenticated.
4. Complete the authorization attestation (required when `SCAN_REQUIRE_AUTHORIZATION=true`) and start the scan. Choosing credentials needs **Manage scans**; without it you can run the scan unauthenticated.

### Results per host

The scan result has a **Host authentication** panel with counts and a filterable list of hosts:

| Result | Meaning |
| --- | --- |
| **Authenticated** | The login worked; local and remote checks ran |
| **Login failed** | Credentials were tried and refused; remote checks only |
| **Login not confirmed** | Greenbone did not confirm the login; treated as not assessed locally |
| **Unauthenticated** | No credentials for this host; remote checks only |

A host whose login failed or was not confirmed is shown as **Not assessed locally**, never as clean. **A failed login does not close findings**: its earlier local-check findings stay open. Package CVEs from local checks show the installed and the fixed package version.

**Edit & re-run this scan setup** opens the scan form with the same targets, credentials and scan settings, so you can change them and run it again. Replacing a setup retires its Greenbone task, so it needs **Manage scans**.

## Scan endpoints: Endpoint 360 and OpenVAS coverage

With Wazuh connected as well, you can scan endpoints directly.

- **Endpoint 360 → Network VAPT findings on this host → Trigger Network VAPT scan** scans that host. Each host gets its own reusable Greenbone task (`offload-host-…`). The panel shows the scan state, last scan time and whether the results have been imported, and reloads the findings once they are.
- **Endpoint Security → OpenVAS coverage** lists every Wazuh endpoint with an IP address as **Scanned**, **Not scanned**, **Scan in progress** or **Failed**, based on the Greenbone tasks whose targets cover it, with a coverage percentage. Scan one host, the hosts you select, or up to 100 not-scanned hosts at a time; each gets its own Greenbone task.

"Scanned" means a completed Greenbone scan covered the host's IP address or name. Greenbone does not report hosts that were down, so it does not prove the host answered.

## How results are imported

- **When.** On connect, every 30 minutes, on **Sync now**, and within minutes of a scan finishing: the platform checks Greenbone for finished, not yet imported scans every `OPENVAS_COMPLETION_CHECK_MINUTES` minutes (default 5; `0` turns the check off).
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

**Audit Reports → Network VAPT report → VAPT report (PDF)** or **VAPT report (Word)** builds a report from the latest Greenbone OpenVAS and nmap results when you download it: scope and methodology (tools, versions, and whether each host was scanned authenticated), an executive summary, risk-rated findings with affected hosts, evidence, remediation and retest status, and annexes for host inventory, open ports and Wazuh host-side correlation. For authentication, OpenVAS scans started from the platform record each host's login result; hosts of tasks run only in Greenbone read *not recorded*; nmap hosts read *Unauthenticated*. The correlation annex is included only for users who may view integrations. See [Audit Reports](../compliance/audit-reports.md).

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

- **Authenticated scans.** Store SSH / SMB credentials for the hosts and run [authenticated scans](#authenticated-credentialed-scans); unauthenticated scans see exposure, authenticated scans see missing patches. Check the **Host authentication** panel: a host with *Login failed* was not assessed locally.
- **Scope by the platform's discovery.** Use the ranges and hosts a [network discovery scan](./internal-network-visibility.md) found as OpenVAS targets, so both tools cover the same estate. **OpenVAS coverage** shows which Wazuh endpoints have not been scanned yet.
- **Agents where you can, OpenVAS everywhere.** An agent-less appliance, printer, OT controller or forgotten VM is exactly what OpenVAS reaches and Wazuh cannot; where both see a host, the correlation tells you whether they agree.

## OpenVAS and Wazuh together

| | Wazuh | OpenVAS |
| --- | --- | --- |
| Answers | What is happening on the hosts I manage | What is exposed and unpatched on everything on the network |
| Needs | An agent per host | Network reach (and credentials for depth) |
| Into the platform | Agents, alerts, host CVEs, login anomalies, SCA failures | Latest report per task as network findings, correlated with Wazuh agents; scans started from the platform record each host's login result |

## Related

- [OpenVAS](../integrations/openvas.md) — the Integrations-section page.
- [Wazuh Integration](./wazuh-integration.md) · [Wazuh + OpenVAS](../integrations/wazuh-openvas.md).
- [Internal Network Visibility](./internal-network-visibility.md) — the platform's own network discovery.
- [Scan Management](../security-scanning/scan-management.md) — the Scheduler, where recurring OpenVAS scans run.
