---
title: "Wazuh Integration"
sidebar_label: "Wazuh Integration"
sidebar_position: 4
description: "Wazuh is how endpoints and servers report into the platform — agents become assets linked to their cloud VM, alerts and login anomalies join the unified Alerts stream, host CVEs become vulnerability occurrences, SCA failures become control evidence, and the Endpoint Security dashboard covers the rest. What syncs, how often, what is stored and what stays in Wazuh."
---

# Wazuh Integration

Wazuh gives you agents on the machines a scanner cannot log into — servers, workstations, on-premises hosts — and a SIEM's worth of detections, configuration checks and file-integrity events about them. Connecting it to Offload Security does two things: the parts that belong next to your other findings are **synced in** (agents, alerts, host CVEs, configuration failures, login anomalies), and the rest is **read live** from the in-platform **Endpoint Security** dashboard, so day-to-day endpoint triage does not need the Wazuh dashboard.

**Where:** connect under **Integrations → Wazuh**; work under **Infra Command Center → Endpoint Security** (the tab appears once Wazuh is connected for the active team).

The platform is **read-only towards Wazuh**: it never enrolls, upgrades or deletes agents, changes rules or installs patches. Where it suggests a change in Wazuh (a rule snippet, an agent cleanup script), you review and run it yourself.

## What syncs, and where it lands

Every 30 minutes (`INTEGRATION_SYNC_INTERVAL_MINUTES`), on connect and on **Sync now**, the platform reads the Wazuh **Manager API** and the **Indexer** (OpenSearch):

| Wazuh data | Becomes | Notes |
| --- | --- | --- |
| **Agents** | Assets in [Asset Inventory](../cloud-security/asset-inventory.md) and hosts in the security graph behind [Attack Paths](../cloud-security/attack-paths.md) | An agent on a cloud VM is **linked to that VM** (see [Agent ↔ cloud VM link](#agent--cloud-vm-link)) so it appears as one host, not a second "endpoint" |
| **Alerts** with rule level **≥ 7** | Entries in the unified [Alerts](../vulnerability-risk/alerts.md) stream, de-duplicated per rule and agent with an occurrence count; and grouped alerts with their own triage state in Endpoint Security | Severity from the rule level: 7–11 medium · 12–14 high · 15 critical; MITRE technique ids carried through |
| **Vulnerability state** (per agent, package, CVE) | Vulnerability occurrences in [Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx) and the unified findings behind [Triage](../vulnerability-risk/vulnerability-management/triage.md) | Scored with the linked VM's real exposure when a link exists |
| **Login events** (SSH, PAM, sudo, su, Windows logon) | A 14-day login baseline and anomalies; anomalies at or above the team's threshold (high by default) raise **one platform alert per episode** | See [Endpoint Security](./endpoint-security.md#logins) |
| **SCA results** (Security Configuration Assessment) | Fleet results by check; **failures** become evidence against [SCF](../compliance/supported-frameworks.md) controls in the [Evidence Hub](../compliance/evidence-hub.md) | Fail-only — see [SCA results as control evidence](#sca-results-as-control-evidence) |
| **File-integrity events** | Changes grouped by path pattern, with sensitive paths flagged and an allowlist for expected churn | See [Endpoint Security](./endpoint-security.md#file-integrity) |
| **Daily fleet figures** | 30-day trends on the Endpoint Security Overview (alerts by level, vulnerabilities opened and closed, open KEV, SCA fail rate) | Days without data show as —, never 0 |

Sync needs the **Indexer**: a Manager-only connection syncs agents and little else, and the connection test says so as a warning you must accept.

## The Endpoint Security dashboard

| Tab | Content | Source |
| --- | --- | --- |
| **Overview** | Agent counts, 30-day trends, agent health tiles | Last sync |
| **Agents** | The fleet: name, IP, OS, version, status (active / disconnected / pending / never connected), last keep-alive | Manager, live |
| **Alerts** | **Grouped (triage)** — one row per rule and agent, with state, tickets and SLA; **Raw alerts** — individual alerts, level 7 and above by default | Stored groups · Indexer, live |
| **Vulnerabilities** | Host CVEs by agent and package with severity | Indexer, live |
| **Fix first** | Endpoint vulnerabilities ranked by triage priority (**By vulnerability**) and package upgrades ranked by what they resolve (**By upgrade**) | Findings lake · OSV advisories |
| **Compliance** | SCA **Fleet by check** (every agent) and a **Per-agent sample** | Stored · Manager |
| **File Integrity** | **Grouped by path pattern**, **Allowlist**, **Raw (sync sample)** | Stored · last sync |
| **MITRE ATT&CK** | Techniques and tactics seen in the alerts | Indexer |
| **Coverage** | Cloud VMs with no Wazuh agent; agents that match no cloud VM; bulk cloud-link tools | Asset inventory + links |
| **Logins** | Logins, accounts and anomalies over the last 24 hours; baseline state | Stored aggregations |
| **Health** | The Wazuh server's own health and a noise advisor | Wazuh, live (read-only) |

Every host also has an **Endpoint 360** page. How to work these tabs — Endpoint 360, Fix first, alert triage, logins, file integrity, Health — is on [Endpoint Security](./endpoint-security.md). Agent health, stale-agent cleanup and cloud linking are on [Agent Health & Cloud Links](./wazuh-agent-fleet.md).

Every panel says whether its data is live or from the last sync, and a dataset Wazuh refused or timed out on is named on the page rather than shown as empty. Unknown counts show as —, never 0.

## Agent ↔ cloud VM link

During each sync the platform matches agents to the compute instances your cloud scans discovered, strongest evidence first: the cloud instance id (from agent labels or hostname), then IP plus account or VPC, then IP plus region or hostname, then hostname. The method and confidence are recorded. Several candidate VMs **never** link automatically, and an IP address alone is never treated as identity.

A link is used everywhere it matters: the agent's vulnerabilities and alert signals attach to the VM's node in the security graph, endpoint findings are scored with the VM's real exposure in triage, Asset Inventory shows the agent on the VM's row, and Endpoint 360 shows the VM. Confirm, change or remove a link per agent in Endpoint 360, or in bulk under **Coverage** — see [Agent Health & Cloud Links](./wazuh-agent-fleet.md#link-agents-to-cloud-vms).

## SCA results as control evidence

Wazuh tags SCA checks with framework requirements. The platform maps those tags to SCF controls with the same consensus method it uses for Prowler, and records results as fleet evidence:

- A **failed** check adds a gap to the mapped controls; the Evidence Hub shows the Wazuh fleet evidence and the failing agents.
- A **passing** check is shown but **never** raises a control's status or score — the mapping is derived, so it is not credited.
- Results from agents that stopped reporting are *not evaluated*; silence is never a pass.
- Frameworks the SCF catalog does not carry (for example PCI DSS 3.2.1, CIS benchmark ids, ISO 27001:2013) are reported as unmapped, not guessed.

**Endpoint Security → Compliance → Fleet by check** lists checks worst-first with the controls they affect; Endpoint 360 lists a host's failed checks with their controls.

## Connect Wazuh

**Integrations → Wazuh → Connect** — fields and the Manager + Indexer test are on [Wazuh](../integrations/wazuh.md) in the Integrations section. In short: `wazuh_host` / `wazuh_port` (55000) and an API user; Indexer host, port (9200) and credentials for split deployments (blank = the Manager host on 9200); `verify_ssl` with your CA certificate in `ca_cert`; and optionally **Login Alert Min Severity** for the team (blank = `WAZUH_LOGIN_ALERT_MIN_SEVERITY`, default high).

A Wazuh Manager is almost always on a private address. Integrations may reach private addresses by default (`ALLOW_PRIVATE_INTEGRATION_TARGETS`, default true); loopback and link-local / metadata addresses are always refused.

## The bundled Wazuh stack

If you do not already run Wazuh, `docker-compose.integrations.yml` contains a single-node Wazuh 4.14.6 (manager, indexer, dashboard). The file is an integration test environment that also defines Jenkins, SonarQube and ZAP, so start only the Wazuh services:

```bash
docker compose -f docker-compose.integrations.yml up -d wazuh-manager wazuh-indexer wazuh-dashboard
```

It is intended for evaluation and small estates:

| `.env` variable | Purpose |
| --- | --- |
| `WAZUH_API_USERNAME` (default `wazuh-wui`) · `WAZUH_API_PASSWORD` | The API user the manager creates on every start. The password is **required** (8–64 characters with upper, lower, digit and symbol); use the same pair in the platform's Wazuh integration |
| `WAZUH_BIND` (default `172.17.0.1`) | The address the API (55000), indexer (9200) and dashboard (5601) bind to — the Docker bridge, so the platform's containers reach them and other hosts do not. Use `https://<WAZUH_BIND>:55000` as the integration's host |

`scripts/setup/docker-setup.sh` generates a per-server `WAZUH_API_PASSWORD` and reads the docker0 address for `WAZUH_BIND`; otherwise set them yourself. Agent enrollment ports 1514 / 1515 stay open on all interfaces so remote agents can connect.

:::warning[Demo indexer credentials]
The bundled indexer runs Wazuh's demo security configuration (`admin` / `admin`). That is why it binds only to `WAZUH_BIND` — never publish port 9200 more widely. For production, run Wazuh with its own hardened configuration and connect it as an external instance.
:::

## What stays in Wazuh

- Agent enrollment, upgrades and removal; rules, decoders and active-response configuration.
- Alerts below rule level 7 (browsable under **Raw alerts → All levels**, not synced or grouped).
- Raw FIM and SCA history beyond what the sync stores; Wazuh's own dashboards.
- Patching: the platform shows which package upgrades fix what and the command to run, but it **does not install patches** or change hosts.

## Why it matters on-premises

- **The host layer, joined up.** A public S3 bucket, a vulnerable container image and a server with a KEV-listed package are three findings on one queue, with the server's exposure known because its VM is the same asset the cloud scan saw.
- **Detections next to posture.** A brute force on an internal host lands in the same alert stream — with the same notification routing and SLA rules — as a critical cloud finding.
- **Evidence you already generate.** Agent coverage, SCA failures and FIM activity are the operational evidence behind endpoint-hardening controls, and they reach the Evidence Hub without an export.

## Related

- [Endpoint Security](./endpoint-security.md) — Endpoint 360, Fix first, alert triage, logins, file integrity, Health.
- [Agent Health & Cloud Links](./wazuh-agent-fleet.md) — fleet hygiene, stale-agent cleanup, linking agents to VMs.
- [Wazuh](../integrations/wazuh.md) — connection fields and troubleshooting.
- [OpenVAS Scanning](./openvas-scanning.md) — the network-scanning counterpart; its findings correlate with Wazuh agents.
- [Alerts](../vulnerability-risk/alerts.md) · [Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx) — where synced data is worked.
