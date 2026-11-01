---
title: "Scan Results"
sidebar_label: "Scan Results"
sidebar_position: 3
description: "Browse targeted runs as a target tree, open a run's findings and evidence, compare it with the previous run of the same target, export HTML/PDF/Word reports, re-scan, and merge runs into a consolidated report."
---

# Scan Results

Every targeted run started from **Scanning** — and every such scan sent in from CI, the API or a schedule — lands on the **Targeted runs** tab. App Scan assessments have their own tab, **Assessments**, and the tool runs an App Scan launches are shown inside the assessment instead of being listed here a second time ([Run an App Scan](./app-scan.md#check-that-it-worked)).

**Where:** left navigation → **Scanning** → **Targeted runs**.

![Scan Results hub with 36 scans and 981 findings, Completed / Running / Failed tabs, tool-type filter, and rows for ZAP, Nmap and testssl with View / HTML / PDF actions](/img/screenshots/security-scanning/scans-results.webp)

## The list

- **Tiles** — total scans, total findings, completed and failed counts (App Scan tool runs are not counted here).
- **Tabs** — **Completed** (includes partial runs), **Running** (refreshes itself every few seconds) and **Failed**, so a scan that errored or was refused is visible instead of silently missing.
- **Tool Type** filter — ZAP, Nmap, testssl, Nuclei, API security, security headers, API discovery, API deep scan, domain recon and others.
- **Grouped** (default) or **All runs** view.

### Grouped: the target tree

**Grouped** shows history as **target → scan type → runs**, newest first, instead of one row per run. Each group states its **true** run count even when it shows fewer runs (up to 50 runs per group are listed). The summary line gives the number of targets and scans; when you have more than 300 targets, the tree shows the 300 most recently scanned and says so. Search filters whole targets by name. Select runs in the tree (one, or a whole group) to build a consolidated report.

### All runs: the flat table

**All runs** is the right view for finding a scan ID or sorting across every target. Columns: tool, target, type, **triggered by** (manual UI, or the API key / CI pipeline that started it), findings, status and date; search by target or scan ID and filter by scan type. Row actions: **View**, **HTML**, **PDF**, **DOCX**, **Rescan** and **Delete**.

Cloud posture scans are listed on their own tab in [Cloud Security](../cloud-security/scan-orchestration.md#scan-history); they are excluded here to keep this list about application and host testing.

## The run detail

Select a run to open it: target, scan type, status and finding count at the top, then:

- **What ran** — tool, engine and pinned version, Nuclei templates release, profile, UTC start and end, anything that was not done (for example OS detection), and links to the tool's kept **raw output** with its SHA-256 ([Engagement & Evidence](./scan-evidence.md)).
- **Compared with the previous run** — see below.
- **Findings** — each with severity, what was observed, the recommended fix and the tool's own proof: CVE and CVSS, confidence, where it matched, extracted values, ZAP instances (method, URL, parameter, evidence), references and, where the tool gives one, the **reproducing request**. Network scans show host, port, protocol, state and service; API scans group findings by OWASP API Top 10 category; reconnaissance scans show DNS records, email-security results and exposed services.
- A **Degraded coverage** badge when a fallback engine ran (for example ZAP's built-in HTTP checks instead of ZAP).

From the detail view you can:

| Action | What you get |
| --- | --- |
| **HTML Report** / **PDF Report** / **DOCX Report** | A formatted report of this run — executive summary, findings by severity, coverage and completeness, remediation. Each download is fingerprinted and kept ([details](./scan-evidence.md#fingerprinted-frozen-exports)). |
| **With Screenshots** | The web-scan report including captured evidence screenshots. |
| **AI Summary** | A plain-language recap of what the scan found and what to do first. |
| **Rescan** | Re-runs the same tool against the same target with the same profile, options, exclusions and attestation — the fastest way to verify a fix. Refused once the authorized window has ended. |
| **Delete** | Removes the run from the lists; it is kept as a tombstone for `SCAN_TOMBSTONE_DAYS` (default 30) before it is purged. |

Report buttons appear for completed and partial runs.

## Compare a run with the previous run

For a completed or partial run, the detail shows **Compared with the previous run**: the latest earlier completed or partial run of the **same tool on the same target**. Findings are matched on rule, location (URL, or host:port/protocol) and parameter, and split into:

| Group | Meaning |
| --- | --- |
| **New** | In this run, not in the previous one |
| **Fixed** | In the previous run, not in this one |
| **Not seen (run incomplete)** | In the previous run, not reported by this **partial** run — possibly not tested, so never counted as fixed |
| **Severity changed** | In both, with a different severity |
| **Unchanged** | In both |

Select a group to list its findings. Caveats are shown when the previous run was partial (a "new" finding may simply not have been tested then) or used a different profile or scan type. To compare with a specific earlier run, use `GET /api/native-scans/results/{scan_id}/compare?baseline=<scan_id>`.

## Consolidated reports

Select several completed runs — for example the ZAP, Nuclei, testssl.sh and Nmap scans of one application — and choose **Consolidated Report** (or **Generate Report (n)**). Give it a title, pick HTML, PDF or Word, optionally capture **Evidence Screenshots**, and the platform merges them into a single report with one severity roll-up and one remediation list. Large reports are generated in the background and downloaded when ready; the generated file's SHA-256 is stored so it can be [verified later](./scan-evidence.md#fingerprinted-frozen-exports).

## Where results go next

- **Vulnerability Management** — when a run completes (or completes partially), its findings are synced to Vulnerability Management for that target right away; the periodic sweep remains as a fallback. A clean completed run retires that tool's earlier findings on the target ([Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx)).
- **Risk Register** — promote a significant finding into a managed risk ([Risk Register](../vulnerability-risk/risk-management/index.md)).
- **Compliance** — web and API findings map to OWASP categories and NIST SSDF for the compliance and executive reports ([Reports & AI](../reports-and-ai/index.md)).

## Related

- [Running Web, API & Host Scans](./native-scans.md) — starting scans, profiles, authentication.
- [Engagement & Evidence](./scan-evidence.md) — authorization, provenance, raw output, export fingerprints.
- [Scan Management & Scheduling](./scan-management.md) — recurring scans and retention.
- [Scanning API](./api.md#web-api--host-scans) — list, poll, compare, download and re-scan over REST.
