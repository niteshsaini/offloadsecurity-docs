---
title: "Wazuh Integration"
sidebar_label: "Wazuh Integration"
sidebar_position: 4
description: "Wazuh is how endpoints and servers report into the platform — agents become assets (correlated with their cloud VM), rule-level ≥ 7 alerts join the unified Alerts stream, host CVEs become vulnerability occurrences, and SCA, FIM and ATT&CK are browsed live in the Endpoint Security dashboard. What syncs, how often, and what stays in Wazuh."
---

# Wazuh Integration

Wazuh gives you agents on the machines a scanner cannot log into — servers, workstations, on-premises hosts — and a SIEM's worth of detections, configuration checks and file-integrity events about them. Connecting it to Offload Security does two things: the parts that belong next to your other findings are **synced in** (agents, alerts, host CVEs), and the rest is **browsed live** from an in-platform dashboard so nobody has to keep a second console open.

**Where:** connect under **Integrations → Wazuh**; browse under **Infra Command Center → Endpoint Security** (the tab appears once Wazuh is connected for the team).

## What syncs, and where it lands

Every 30 minutes (and on **Sync now**) the platform reads the Wazuh **Manager API** and the **Indexer** (OpenSearch):

| Wazuh data | Becomes | Notes |
| --- | --- | --- |
| **Agents** | Assets in [Asset Inventory](../cloud-security/asset-inventory.md) — name, IP, OS, agent status — and nodes in the security graph behind [Attack Paths](../cloud-security/attack-paths.md) | An agent on a cloud VM is **correlated with that VM** (by hostname, then IP) so it appears as the EC2 instance / Compute Engine instance / Azure VM the cloud scanner already knows, not as a second "endpoint" |
| **Alerts** with rule level **≥ 7** | Entries in the unified [Alerts](../vulnerability-risk/alerts.md) stream, source *integration*, de-duplicated per rule and agent with an occurrence count | Severity from the rule level: 7–11 medium · 12–14 high · ≥ 15 critical; MITRE technique ids carried through |
| **Vulnerability state** (per agent, package, CVE) | Vulnerability occurrences in [Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx), de-duplicated per (agent, package, CVE) | The same CVE on a container image and on a host is triaged side by side |
| **Active responses** | Snapshot for the dashboard | |

Sync needs the **Indexer**: a Manager-only connection syncs agents and nothing else, and the wizard says so as a warning you must accept.

## The Endpoint Security dashboard

Overview counts (agents, alerts, vulnerabilities, last sync), then:

| Tab | Content | Source |
| --- | --- | --- |
| **Agents** | The fleet: name, IP, OS, version, status (active / disconnected / never connected), last keep-alive; browsable beyond the snapshot | Manager, live |
| **Alerts** | Detections with rule, level, agent, ATT&CK technique; browsable | Indexer, live |
| **Vulnerabilities** | Host CVEs by agent and package with severity | Indexer, live |
| **Compliance** | Security Configuration Assessment (CIS-style) results per agent — policy, pass / fail counts, failed checks | Manager, live per agent |
| **File Integrity** | FIM events per agent — path, change type, time | Manager, live per agent |
| **MITRE ATT&CK** | Techniques and tactics seen in the alerts | Indexer |

A dataset the Indexer refused (wrong credentials, index missing) is flagged on the page rather than shown as empty.

**Not copied into the platform:** SCA and FIM results are browsed, not imported as compliance evidence or findings; alerts below rule level 7 are not synced; Wazuh's own dashboards, rules and agent management remain in Wazuh.

## Connect Wazuh

**Integrations → Wazuh → Connect** — fields, the Manager + Indexer test and the private-address rule are on [Wazuh](../integrations/wazuh.md) in the Integrations section. In short: `wazuh_host` / `wazuh_port` (55000) and a read-only API user; Indexer host, port (9200) and credentials for split deployments; `verify_ssl` with your CA certificate; and, because a Wazuh Manager is almost always on a private address, `ALLOW_PRIVATE_SCAN_TARGETS=true` on the platform host.

## Why it matters on-premises

- **The host layer, joined up.** A public S3 bucket, a vulnerable container image and a server with a KEV-listed package look like three tools' problems; here they are three findings on one queue, with the server's exposure known because its VM is the same asset the cloud scan saw.
- **Detections next to posture.** A Wazuh alert about a brute-force on an internal host lands in the same alert stream — with the same Slack routing and SLA rules — as a critical cloud finding.
- **Evidence you already generate.** Agent coverage, SCA pass rates and FIM activity are the operational evidence behind endpoint-hardening controls; the dashboard is where an auditor can be shown them.

## Related

- [Wazuh](../integrations/wazuh.md) — connection fields and troubleshooting.
- [OpenVAS Scanning](./openvas-scanning.md) — the network-scanning counterpart.
- [Alerts](../vulnerability-risk/alerts.md) · [Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx) — where synced data is worked.
