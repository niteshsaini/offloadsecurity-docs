---
title: "Endpoint Security: Working Wazuh Data"
sidebar_label: "Endpoint Security"
sidebar_position: 4.1
new_in: 1.4.0
description: "Work Wazuh endpoint data inside the platform — open any host's Endpoint 360, fix the riskiest vulnerabilities and package upgrades first, triage grouped alerts with tickets and SLAs, review login anomalies, cut file-integrity noise, see ATT&CK techniques, and check the Wazuh server's own health."
---

# Endpoint Security: Working Wazuh Data

Once [Wazuh is connected](./wazuh-integration.md), **Infra Command Center → Endpoint Security** is where endpoint triage happens. This page covers the working views; fleet hygiene and cloud linking are on [Agent Health & Cloud Links](./wazuh-agent-fleet.md).

Reading these views needs the **View Integrations** permission. State changes need the permission named in each section.

## Endpoint 360

One page per Wazuh agent with everything the platform knows about that host.

**Open it** in any of these ways:

- Type at least 2 characters of an agent name, IP address or agent id in **Find an endpoint** at the top of Endpoint Security, then pick the agent (arrow keys and Enter work). The search also matches OS text such as `ubuntu`. Up to 8 matches are listed, exact matches first; if more match, the list says how many.
- Click an agent name, or **Open 360** beside it, in Agents, Agent health, Coverage, Alerts, Vulnerabilities and other tabs.
- From [Asset Inventory](../cloud-security/asset-inventory.md), click the agent id on a cloud VM that has a linked agent.

**Share it** with **Copy link** in the Endpoint 360 header: the link opens this host's Endpoint 360 directly for anyone with access to the same team.

| Part | Shows |
| --- | --- |
| Tiles | Open vulnerabilities, known-exploited (KEV), P1 / P2, critical and past-SLA findings for this host. Findings under an approved risk exception are excluded and counted |
| Identity · Cloud VM link | Agent details; the linked cloud VM (account, region, CSPM findings, exposure as scored), candidates, link history, and controls to confirm, change or mark "not a cloud VM" |
| Fix first on this host | The package upgrades that resolve this host's vulnerabilities |
| Vulnerabilities | Host CVEs |
| Network VAPT findings on this host | Greenbone OpenVAS findings matched to this host, with the host-side verdict — see [OpenVAS Scanning](./openvas-scanning.md#host-side-correlation-with-wazuh) |
| Alert groups · Recent alerts | Grouped alerts with triage state; the latest individual alerts |
| MITRE ATT&CK (30 days) | Techniques seen on this host |
| Failed configuration checks | SCA failures, with the SCF controls each one affects |
| File integrity · Logins | Grouped file changes for this host; its login activity and anomalies |

Each panel says whether it is live from Wazuh or stored from the last sync, and how old it is. If Wazuh is unreachable the panel shows the error with **Retry**, never an empty table.

## Fix first

**Endpoint Security → Fix first** answers "what do I patch first?" from the same triage engine as every other finding.

- **By vulnerability** ranks open endpoint vulnerabilities by triage priority (P1–P4), with filters for severity and KEV. Tiles show open vulnerabilities, KEV, P1 / P2 and past SLA.
- **By upgrade** ranks package upgrades per distribution release by what they resolve: "Upgrading `<package>` from `<current>` to `<recommended>` resolves N vulnerabilities (x Critical, y High …)". Click a row to open the **Upgrade Impact** drawer: the CVEs, the affected hosts (each opens its Endpoint 360), the upgrade command for that distribution's package manager, and what stays unresolved.

Wazuh does not report fixed versions. The platform looks them up from the distributions' security advisories via OSV.dev and matches them to each host's OS release:

| Coverage | Detail |
| --- | --- |
| Supported | Ubuntu, Debian, Alpine, Rocky Linux, AlmaLinux, Red Hat Enterprise Linux, SUSE Linux Enterprise / openSUSE Leap |
| Not included | Windows and macOS hosts; other Linux distributions are listed as "unsupported OS" with a count |
| "Fix data pending" | The lookup has not run yet for this host or package, the OS release is not yet known, or the host changed since the last lookup |
| "No advisory matched" | The advisory names a different package (for example the source package); it does not mean there is no fix |
| "No fix known" | The advisory lists the CVE for this release without a fixed version yet |

If OSV.dev cannot be reached, the page says so and uses the last cached advisories; nothing is marked "no fix" because of it.

:::note[The platform does not patch hosts]
Fix first tells you which upgrade to apply and shows the command. Applying it — on the host, through your own patch tooling — is your step; kernel updates take effect after a reboot. Check that the recommended version has reached your package mirror first.
:::

## Alert triage

**Endpoint Security → Alerts → Grouped (triage)** groups alerts of level 7 and above by **rule and agent** over a window you choose (last hour to last 30 days). Counts come from Indexer aggregations, not a sample.

| Action | What it does |
| --- | --- |
| **Acknowledge** | Marks the group seen (needs the acknowledge-alerts permission) |
| **Assign…** | Gives the group an owner |
| **Suppress…** | Hides the group until an end date (at most 365 days), with a required reason and an optional count threshold |
| **Resolve** · **Reopen** | Closes or reopens the group |
| **Create ticket** | One Jira ticket per selected group, up to 25 at a time (Jira must be connected); the ticket's status is tracked back |

State is stored per group, so it survives re-syncs. A suppressed group returns as *new* when the suppression ends or its threshold is exceeded; a resolved group that fires again reopens and restarts its SLA clock. Groups at **level 12 and above** get acknowledge and resolve deadlines from your team's [SLA policies](../vulnerability-risk/sla-management.md). Bulk actions take at most 100 groups and report what was skipped and why. Changes other than acknowledge need the manage-alerts permission.

**Raw alerts** lists individual alerts (level 7 and above by default; change the level filter for more). It pages only as deep as the Indexer allows, and links to older alerts in Wazuh.

Wazuh alerts also flow into the platform-wide [Alerts](../vulnerability-risk/alerts.md) stream, de-duplicated per rule and agent.

## Logins

**Endpoint Security → Logins** baselines sign-ins (SSH, PAM, sudo, su, Windows logon) and flags anomalies from the last 24 hours. The baseline shows "learning (N of 14 days)" until 14 days of history exist; history-based anomalies wait for it.

| Anomaly | Meaning |
| --- | --- |
| Automated account | An account signing in with a machine-like pattern (successful logins only) |
| New account on host · New source IP | Not seen in the baseline |
| Rate spike | Far more logins than the baseline |
| Brute force on account · Brute force from source IP · Password spray | Failed-login attacks; one item per attack |

**Platform alerts.** Each anomaly is tracked as an **episode** (first and last seen, current and highest severity, open or closed). An episode at or above the team's threshold — **high** by default, set per team with *Login Alert Min Severity* on the Wazuh integration or platform-wide with `WAZUH_LOGIN_ALERT_MIN_SEVERITY` — raises **one** alert in [Alerts](../vulnerability-risk/alerts.md), routed and notified like any other. It is raised again only if the episode reopens, its severity rises, or new failures arrive after an acknowledgement. An episode closes after several consecutive complete syncs see the subject clean, and its alert is resolved by the system.

**Acknowledge** a brute force or spray you dealt with, saying what was done; it also acknowledges the linked platform alerts. An acknowledgement covers only failures seen so far, lasts 24 hours unless you set a date, and at most 7 days.

**Allowlist** an expected account (a deploy bot, a backup job): the account, optionally one agent and one source IP, a reason and an optional end date (at most 365 days). Allowlisted accounts are still counted, just not flagged. Brute force and password spray can **never** be allowlisted, and privileged accounts (root, Administrator) only for one host **and** one source IP. Changes need the manage-alerts permission.

## File integrity

**Endpoint Security → File Integrity → Grouped by path pattern** turns the raw change feed into groups with true counts. Paths are normalized (numbers, hashes, dates, UUIDs and per-user home directories become `*`; rotated logs, caches and temp files collapse into one pattern), and **sensitive** locations are flagged with the reason: system binaries, SSH keys, accounts and sudoers, cron / systemd / scheduled tasks, web roots, Windows Run and Services keys. Filter by sensitivity to see only those.

- **Allowlist** hides expected churn behind a disclosed count. Each entry needs a reason and may have an end date (at most 365 days); it needs the manage-alerts permission and is audited. A pattern that would cover sensitive paths asks for explicit confirmation, and a sensitive group is never hidden.
- **Raw (sync sample)** shows the individual events captured by the last sync, sampled from a subset of agents.

## MITRE ATT&CK

**Endpoint Security → MITRE ATT&CK** shows the techniques and tactics in your Wazuh alerts; Endpoint 360 shows the last 30 days for one host. The **MITRE ATT&CK** matrix in [Threat Intelligence](../ai-threat-intelligence/threat-intelligence.md) combines Wazuh and other alert telemetry with threat indicators and actors, with per-source counts, a time window, sub-techniques rolled up to their parent, and a drill-down to the alerts with **Open in Wazuh** links.

## Health and noise advisor

**Endpoint Security → Health** reads the Wazuh server's own state, read-only, with a short cache (2 minutes; noise 5 minutes):

- **Server health** — indexer cluster status, heap and swap, load per core, disk watermarks, shards per node and unassigned replicas, alert volume per day, index retention, and manager daemons and dropped events. Each finding is in plain English with the threshold it crossed.
- **Noise advisor** — the rules that generate most alerts over up to 7 days, with their share of the total and their top agents, accounts and source IPs, plus a suggested `local_rules.xml` snippet to review. Authentication, sudo, PAM and logon rules are never silenced fleet-wide: the advice is to identify the account first, and any snippet is scoped to one non-privileged account or source IP.

A check the Indexer user is not permitted to run shows **No permission** (with the permission it needs), never "healthy". Snippets are copy-only: **the platform does not change Wazuh**.

Use Health first when syncs time out or panels show "not read — the sync ran out of time": an overloaded indexer is the usual cause.

## Related

- [Wazuh Integration](./wazuh-integration.md) — what syncs and what stays in Wazuh.
- [Agent Health & Cloud Links](./wazuh-agent-fleet.md) — fleet hygiene, stale agents, VM links.
- [OpenVAS Scanning](./openvas-scanning.md) — network VAPT findings and their host-side verdict.
- [Vulnerability Management triage](../vulnerability-risk/vulnerability-management/triage.md) — the priority Fix first ranks by.
