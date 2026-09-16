---
title: "Findings & Reports"
sidebar_label: "Findings & Reports"
sidebar_position: 3
description: "Triage SAST, dependency, secret and IaC findings across repositories with a time-bound, evidence-backed lifecycle; get AI analysis and fix suggestions; open fix pull requests; export scan reports."
---

# Findings & Reports

## Findings

**Where:** Code Command Center → **Findings**.

![Findings tab for payments-api.zip: 134 open findings (2 critical, 15 high, 103 medium, 14 low), grouped by source with dependency CVEs (GHSA IDs, package versions) and Triage buttons](/img/screenshots/security-scanning/code-findings.webp)

The Findings tab is the cross-repository triage list. Pick a **repository** (or all), and the tiles show open findings by severity. Findings are **grouped by source** — **Dependencies (SCA)**, **Secrets**, **SAST**, **Dockerfile / IaC**, **Outdated packages** — with a per-group severity breakdown, and can be searched by title, file, CVE or package. **AI Analysis** summarises the current view: what is exploitable, what is noise, where to start.

Each row shows severity, source, the identifier (rule, CVE/GHSA, detector or Checkov check), the location (file and line, or package and version) and, for dependencies, the **fixed version** plus **KEV** (actively exploited) and **EPSS** badges. Open a row for the code context or advisory text, the remediation, the **activity** history and comments.

### Lifecycle

Every finding starts **open**. **Triage** records a decision that survives re-scans:

| Decision | Requires | Effect |
| --- | --- | --- |
| **Resolved** | — | Closed; re-detected on a later scan → **reopened** automatically. |
| **Accept risk (time-bound)** | **Owner**, **justification**, **expiry** | Hidden from open counts until the expiry, then returns for review. Under the *Production* policy pack acceptances also need an **approver** and are capped at 30 days (90 under *Baseline*). |
| **False positive** | **Justification** | Excluded from counts, scores and reports; kept on the finding. |
| **Reopen** | — | Returns an accepted or resolved finding to open. |

Attach **evidence** (a link or note) to any decision; it appears in the activity log and in exports, which is what an auditor asks for when they see an accepted critical. Decisions can be applied in bulk to a selection.

### Fixing

- **AI Fix Suggestion** drafts the code change for a SAST finding or the upgrade for a dependency, with an explanation.
- **Fix PR** pushes a branch with the change and opens a pull request on the connected provider (GitHub, GitLab or Bitbucket). This is the only code-scanning action that writes to your repository; it needs the **Execute Remediations** permission and a token with pull-request write access. The PR body links back to the finding.
- **Copy PR body** and **Copy upgrade commands** are available when you would rather open the change yourself.

:::tip[SCA first, then SAST]
Dependency findings usually outnumber everything else and are the cheapest to fix — a version bump. Filter to KEV-flagged and fixable high/critical dependencies, ship those, then work SAST criticals with the code context in front of you.
:::

## Scan reports

**Where:** Code Command Center → **Reports**.

![Reports tab: scan reports list with payments-api.zip (upload, completed) and Refresh / page-size controls](/img/screenshots/security-scanning/code-reports.webp)

One report per scan: source (repository and branch, or upload), type, status (**completed**, **completed with errors** when a tool failed, **failed**) and date. Filter with **Show: application / owner** once repositories are mapped ([Repository ownership](./connecting-repositories.md#repository-ownership)). Select several and **Delete** to prune.

Open a report for the detail view:

![Report detail: Security Findings (98) grouped by tool — Dependencies (SCA), Secrets, SAST — with severity, package/file, and per-finding AI Fix and Triage actions](/img/screenshots/security-scanning/code-report-detail.webp)

- **Security findings** for that scan, grouped by tool, with the same triage and AI actions as the Findings tab.
- **Artifact / image scan results** when the scan was of a build artifact or compiled image.
- **SonarQube report** when SonarQube is configured — the platform stores the report artifact and links it.
- **AI Analysis** of the whole scan and **Export Report (PDF)** for a release record or an auditor.

## Where code findings go next

- **Vulnerability Management** — SCA and image CVEs appear in the unified view with SLAs and ownership ([Vulnerability Management](../../vulnerability-risk/vulnerability-management.mdx)).
- **Risk Register** — promote an accepted critical into a tracked risk ([Risk Register](../../vulnerability-risk/risk-register.md)).
- **Release gates** — the same findings drive the pass/fail decision in CI ([CI/CD & Automation](./ci-cd-and-automation.md)).

## Related

- [Running Code Scans](./running-code-scans.md) — producing the findings.
- [SBOM & Licences](./sbom-and-licenses.md) — the inventory and licence side of the same scans.
- [Scanning API](../api.md#code) — findings lifecycle, reports and exports over REST.
