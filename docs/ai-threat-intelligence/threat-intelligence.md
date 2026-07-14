---
title: "Threat Intelligence"
sidebar_label: "Threat Intelligence"
sidebar_position: 1
---

# Threat Intelligence

Threat Intelligence brings external, real-world threat data into Offload Security and connects it to what you actually run. The platform pulls indicators of compromise (IOCs) from industry feeds, keeps them current, and correlates them against your assets and vulnerabilities — so you can see which of your exposures are tied to *active* exploitation, not just theoretical risk.

![Threat Intelligence dashboard](/img/screenshots/threat-intelligence.png)

## What it does

- **Ingests multiple threat feeds.** Out of the box the platform pulls from industry sources including **CISA KEV** (Known Exploited Vulnerabilities), **AlienVault OTX** (community pulses), **Abuse.ch URLhaus** (malicious URLs), and **Emerging Threats** (compromised-IP and blocklist data). Feeds refresh automatically on a schedule, and you can trigger a manual re-sync for any single feed at any time.
- **Normalizes everything into IOCs.** Indicators from every feed are standardized into a common format — IPs, domains, URLs, and file hashes — each with a severity and confidence rating, so you can search and filter across all sources at once.
- **Correlates IOCs against your environment.** Indicators are matched against your discovered assets, and against real-time cloud activity (AWS CloudTrail, GCP Audit Logs, Azure Activity Log), to surface potential active compromise.
- **Prioritizes vulnerabilities by threat data.** Findings tied to known-exploited vulnerabilities (via CISA KEV) and to trending, high-confidence indicators are pushed up your remediation queue, so you fix what attackers are actually using first.
- **Keeps the picture fresh.** Indicators age out automatically once they expire, so stale data doesn't inflate your risk scores.

## How to use it

### 1. Open Threat Intelligence
From the left navigation, under **Threat & Intelligence**, select **Threat Intelligence**. The module opens on the **Dashboard** tab.

The screen is organized into tabs:

| Tab | What you do here |
|---|---|
| **Dashboard** | See headline metrics — active threats, high-confidence IOCs, feed health — and a live feed of recent indicators. |
| **Indicators** | Search and filter every IOC by type (IP, domain, URL, hash), severity, and confidence. |
| **Feeds** | Configure your intelligence sources and monitor each feed's health. |
| **Actors & Campaigns** | Track known threat groups and the active campaigns attributed to them. |
| **Hunting & Rules** | Run IOC search queries and set up automated alert rules. |

### 2. Turn on and check your feeds
1. Go to the **Feeds** tab.
2. Enable the sources you want (CISA KEV, OTX, URLhaus, Emerging Threats). Enabled feeds fetch automatically on a schedule.
3. Watch each feed's **health status** — **healthy**, **degraded**, or **critical** — which reflects how many of its recent fetches succeeded. If a feed shows degraded or critical, trigger a manual re-sync from the same tab.

### 3. Explore indicators
On the **Indicators** tab, filter by type, severity, or confidence to find what matters. Use this to investigate a suspicious IP or hash you've seen elsewhere, or to review the newest high-confidence indicators.

### 4. Correlate against your assets
The platform automatically checks incoming indicators against your asset inventory and cloud activity. When an IOC matches something in your environment — or lines up with a high-impact cloud event such as an IAM policy change or firewall-rule modification — it's flagged so you can investigate a possible active compromise.

### 5. Let threat data drive prioritization
You don't need to act on the threat feed in isolation. Threat context flows into **[Vulnerability Management](../vulnerability-risk/vulnerability-management.md)**: vulnerabilities that appear in the CISA KEV catalog or relate to trending indicators are scored higher and rise to the top of your remediation work.

## Advanced capabilities

- **STIX/TAXII import & export.** Bring in your own or a partner's intelligence — and share yours — using the industry-standard STIX/TAXII format. This is how you add **custom** indicators beyond the built-in feeds.
- **MITRE ATT&CK heatmap.** Visualize which attacker techniques your threat coverage maps to, so you can spot gaps.
- **Threat actors & campaigns.** Group related indicators under known actors and the campaigns they run, with Traffic Light Protocol (TLP) handling so intelligence is shared at the right sensitivity.
- **Hunting & alert rules.** Save IOC queries and turn them into rules that raise alerts automatically when new matching indicators arrive.

:::tip[Start with CISA KEV]
If you only enable one feed, make it **CISA KEV**. It directly powers vulnerability prioritization by flagging the CVEs that are confirmed to be exploited in the wild.
:::

:::note[Indicators expire on purpose]
Indicators have an expiration so old intelligence is retired automatically. An IOC that no longer appears in this module has aged out — that's expected behavior, not a gap.
:::

:::note[Why CVE context matters]
Threat Intelligence is most powerful when paired with vulnerability data. The more of your environment you've connected and scanned, the more matches the platform can make between live threats and your actual exposure.
:::

## Related

- **[Vulnerability Management](../vulnerability-risk/vulnerability-management.md)** — where threat-prioritized findings are triaged and tracked.
- **[Asset Inventory](../cloud-security/asset-inventory.md)** — the catalog of resources IOCs are correlated against.
- **[Security Command Center (AI-SOC)](./ai-soc-agents.md)** — AI-assisted incident correlation and prioritization.
