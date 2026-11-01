---
title: "Threat Intelligence"
sidebar_label: "Threat Intelligence"
sidebar_position: 1
description: "Eight built-in feeds normalised into indicators and matched against your findings and assets automatically, a threat-intelligence lens over your open CVEs (CISA KEV, EPSS, exploitation, actors, IOC matches), a MITRE ATT&CK matrix built from your Wazuh and alert telemetry, threat landscape reports, STIX 2.1 / CSV import and export, and indicator aging."
---

# Threat Intelligence

A vulnerability that is being exploited this week is not the same as one that merely has a CVSS score. Threat Intelligence keeps a current picture of what attackers are actually using — known-exploited CVEs, live C2 servers, phishing and malware URLs, botnet infrastructure — and connects it to your findings and assets, so exploitability, not just severity, decides what your team fixes first.

**Where:** left navigation → *Threat & Intelligence* → **Threat Intelligence**. Tabs: **Dashboard**, **IOC Analysis**, **Threat Feeds**, **Vuln Prioritization**, **MITRE ATT&CK**, **Reports**, **Import/Export**.

![Threat Intelligence Center dashboard: active threats, new in 24 h, high-confidence IOCs, active feeds; severity and IOC-type distribution; feed status](/img/screenshots/ai-threat-intelligence/ti-dashboard.webp)

## Dashboard

Headline counts — **active threats**, **new in the last 24 hours**, **high-confidence IOCs**, **active feeds** — then the severity mix, the indicator-type mix, a status card per enabled feed, emerging threats of the last 48 hours, 7-day trends and recent alerts. *Active* means not expired or archived (see [Import / export and indicator aging](#import--export-and-indicator-aging)), so the dashboard reflects current intelligence rather than everything ever fetched. A chip in the page header summarises feed health.

## Threat feeds

Eight feeds are built in. Keyless feeds are switched on for every team; feeds that need a key stay off until you add one. Only these feeds are available — you cannot add your own feed URL; load your own indicators with **+ Create IOC** or Import/Export instead.

| Feed | What it contributes | Key |
| --- | --- | --- |
| **CISA Known Exploited Vulnerabilities** | CVEs confirmed exploited in the wild | — |
| **Abuse.ch URLhaus** | Malware distribution URLs | required |
| **AlienVault OTX Community** | Community pulses: IPs, domains, hashes with context | required |
| **Feodo Tracker** (abuse.ch) | Botnet C2 servers (Emotet, Dridex, QakBot…) | optional |
| **SSL Blacklist (SSLBL)** (abuse.ch) | Certificates and IPs used by malware C2 | optional |
| **Blocklist.de** | IPs reported for attacks on SSH, mail, web | — |
| **Spamhaus DROP** | Hijacked / criminal netblocks (CIDR) | — |
| **OpenPhish** | Phishing URLs | — |

**PhishTank** has been retired by its provider. Installations that had it keep its card, marked **Retired** with the switch locked off; use OpenPhish for phishing URLs.

![Threat Feed Management: CISA KEV, Abuse.ch URLhaus, AlienVault OTX, Feodo Tracker cards with enable switch, last fetch, indicator count, Process Feed Now, Add API Key](/img/screenshots/ai-threat-intelligence/ti-feeds.webp)

Enabled feeds are checked every **15 minutes**, and each feed is fetched when its own refresh interval has passed — **24 hours** by default for the built-in feeds (adjustable per feed over the API). **Process Feed Now** fetches one immediately. Feeds that need no key are downloaded **once for the whole platform** per refresh and shared; each team still gets its own copy of the indicators, so aging, false-positive marks and team views stay separate. Keyed feeds are fetched per team with that team's key.

Each card shows the last fetch result (and the error when it failed), the indicator count and, where the source needs one, **Add API Key** (tested with *Test Connection*, stored encrypted, per team). Failures are classified — authentication, rate-limited, quota, timeout, unreachable, parse error, discontinued — so the card says what to fix; transient classes are retried automatically. The header chip reads the last 24 hours of fetches: *Feeds healthy* (no failures), *Feeds degraded* (fewer than 1 in 5 failed), *Feeds failing*, *No fetches in 24h*. Disable a feed and its indicators stop refreshing; they age out on their normal schedule.

:::note[KEV and EPSS on your findings do not depend on the feed]
The CISA KEV catalogue and EPSS scores used by [Triage](../vulnerability-risk/vulnerability-management/triage.md) and Vuln Prioritization are refreshed daily for the whole platform, whether or not a team enables the CISA KEV feed. Enabling the feed also adds the KEV CVEs to your team's indicators.
:::

## Automatic correlation onto findings

Since 1.4.0, intelligence reaches your findings without anyone pressing a button. Every 30 minutes, and right after a feed brings in new indicators, the platform:

- marks open findings whose CVE is in **CISA KEV**, has an **EPSS** score, or is tagged as exploited by one of your team's indicators;
- matches active **IP, domain and URL** indicators exactly against the public IPs, host names and URLs on your open findings and the assets they sit on.

The result is stored on the finding (KEV flag, EPSS, exploit available, threat activity, IOC matches) and the finding is re-scored at once, so a match moves it up the [Triage](../vulnerability-risk/vulnerability-management/triage.md) queue. An IOC match is its own scoring signal; it does not by itself force a finding to P1. Private IP addresses and shared cloud host names (such as `amazonaws.com`) never match, and indicators or correlations you mark as **false positive** are never matched again. Runs are incremental — only new findings and those affected by changed intelligence are re-read; the daily KEV/EPSS refresh triggers a full pass.

## IOC analysis

![Threat Indicators: search, severity / type / confidence filters, IOC Correlation Analysis box, indicator table with value, type, severity, confidence, source and Correlate action](/img/screenshots/ai-threat-intelligence/ti-indicators.webp)

Every indicator from every feed in one table: value, type, severity, confidence (0–100), source feed. Search by value or description; filter by severity, type, confidence, or **status** (active or false positive — false-positive marks can be listed and cleared here). **+ Create IOC** adds your own indicator (type — IP, domain, URL, file hash, email, certificate, registry key, user agent, cryptocurrency address, YARA rule — value, severity, confidence, description) — from an incident, a partner, or a red-team exercise — and it is treated like any feed indicator from then on.

**Correlate** (on a row, or any value typed into *IOC Correlation Analysis*) searches one value by hand across your assets, cloud findings, vulnerability occurrences, scan targets and cloud accounts. Matching is exact on whole tokens (`1.2.3.4` does not match `11.2.3.45`). The result names where it searched; a **Partial result** note lists stores that could not be searched or returned more than 200 matches, so "no matches" next to that note is not proof of absence. A match is the strongest signal you have of active compromise and deserves an incident, not a ticket.

## Vulnerability prioritisation

**Vuln Prioritization** is a threat-intelligence lens over your **open CVEs** from Vulnerability Management. It fills itself — there is nothing to paste — and lists each open CVE with the signals the platform holds for it, next to its VM priority and open-finding count:

| Signal | Shown as |
| --- | --- |
| Listed in **CISA KEV** | *CISA KEV* chip (date added and CISA's due date on hover) |
| Tagged exploited by a team indicator | *Exploited (feed)* |
| Linked threat actors or campaigns | *Actor:* / *Campaign:* chips |
| Matched indicators | IOC chip, with the feeds |
| **EPSS** probability and percentile | EPSS column; *not cached* means unknown, not zero |

Filter by **Any TI signal**, **CISA KEV**, **Known exploited**, **Actor / campaign**, **IOC match** or **EPSS known**; tiles count open CVEs, CVEs with a signal, CVEs in KEV and actor-linked CVEs. **Open in VM** jumps to those findings in the Triage queue. There is no separate threat score: the order follows the signals, and the priority that decides the work is VM's own. On first open the page says it is computing; counts are unknown, not zero, until it finishes.

**Check specific CVEs** looks up the same signals for CVEs you paste (for example, ones in an advisory), and says whether each is open in your environment. Only findings identified by a CVE carry these signals; misconfigurations and most code findings have none.

The older score-based endpoint (`POST /api/threat-intelligence/vulnerabilities/prioritize`: base 50, +25 for KEV, +5 per related indicator up to +15, +5 per actor and per campaign up to +10 each, +10 for a critical indicator; needs **Manage Threat Intelligence**) remains available over the API; the UI no longer uses it.

## MITRE ATT&CK

![MITRE ATT&CK Coverage: techniques observed, indicators mapped, actors mapped; kill-chain phase coverage; technique heatmap](/img/screenshots/ai-threat-intelligence/ti-mitre.webp)

Since 1.4.0 the matrix is built from **your own telemetry** as well as intelligence: Wazuh alerts carry their rule's ATT&CK technique into the platform, and every alert producer that tags techniques contributes, alongside the Wazuh indexer's own aggregate and the techniques on your indicators and threat actors. Sub-techniques roll up to their parent.

- **Tiles** — techniques observed, techniques **seen in telemetry**, alerts with ATT&CK ids, indicators mapped, threat actors mapped.
- **Telemetry window** — last 24 hours, 7, 30 (default) or 90 days, or all time.
- **Sources** — which sources are connected, contributing, or never synced.
- **Technique heatmap** and **kill-chain phase** view (Reconnaissance → Impact). Each cell shows a count per source, with units, rather than one summed number (the sources overlap). Techniques seen in telemetry are marked *seen*.
- **Drill-down** — click a technique for the alerts mapped to it in the window, with links to the ATT&CK page and **Open in Wazuh**.

It is a map of *observed activity and intelligence*, not of your defensive coverage: an empty phase means nothing you hold maps there, not that you are protected.

## Reports

**Threat Landscape Reporting** generates a report for a period (last 7, 30 or 90 days) in a chosen format (**Executive Summary**, **Technical Analysis**, **Comprehensive Report**) from the team's indicators: threats analysed, new threats discovered, active actors and campaigns, top techniques, and recommendations. Reports are kept in **Report History** and retrievable over the API.

![Threat Landscape Reporting: report period and format, Generate Report, report history](/img/screenshots/ai-threat-intelligence/ti-reporting.webp)

## Import / export and indicator aging

![Bulk Import/Export & IOC Lifecycle: import CSV/JSON/STIX, export STIX 2.1 filtered by type; confidence decay, aging configuration, expiration policy](/img/screenshots/ai-threat-intelligence/ti-import-export.webp)

- **Bulk import** — paste CSV, JSON or STIX 2.1 (there is no file upload); indicators are validated, duplicates are skipped, and imports default to TLP:AMBER and confidence 50.
- **Bulk export** — STIX 2.1 (or CSV / JSON), optionally filtered by indicator type, for sharing with a partner or loading into a SIEM; expired indicators are left out.
- **Archiving** — a daily clean-up archives indicators not seen for **90 days**, including ones you created or imported. Archived indicators stop matching.
- **Indicator aging** *(when configured for the team under IOC Lifecycle Management)* — confidence **decays** by a set percentage per day (0.5 % by default, floor 10 %) and indicators **expire** after a time-to-live (90 days by default, configurable per type). Aging is applied daily and can be applied on demand. This is why the dashboard's *active threats* is not a monotonically growing number.

## Threat actors, campaigns, hunting queries and alert rules

The data model also holds **threat actors** (with TLP classification and ATT&CK techniques), **campaigns** attributed to them, saved **hunting queries** and **alert rules** that raise an alert when a matching indicator arrives. They are managed over the API today (`/api/enhanced-threat-intelligence/…`, see [API](./api.md#threat-intelligence)); the tabs are not shown in the UI. Actors and campaigns you record appear as signals in Vuln Prioritization and on the ATT&CK matrix.

## Related

- [Triage](../vulnerability-risk/vulnerability-management/triage.md) — where KEV, EPSS and IOC matches change the order of work.
- [Security Command Center](./ai-soc-agents.md) — the triage agent's KEV-driven *Critical* verdicts and threat hunts.
- [Wazuh Integration](../on-premises/wazuh-integration.md) — the alerts that feed the ATT&CK matrix.
- [Asset Inventory](../cloud-security/asset-inventory.md) — what indicators are correlated against.
