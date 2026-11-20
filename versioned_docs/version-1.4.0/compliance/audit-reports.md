---
title: "Audit Reports"
sidebar_label: "Audit Reports"
sidebar_position: 6
description: "Generate attestable compliance reports as PDF plus CSV or CSV only: framework scores, control status, findings, drift, remediation and sync history, frozen at issue with a SHA-256 you can verify later, plus the per-framework evidence bundle."
---

# Audit Reports

An auditor's first request is rarely a dashboard; it is "send me the list". Audit Reports turn the compliance engine's state into a formatted, attestable PDF and flat CSV files. The figures are the same ones the posture page shows, computed over your team's active frameworks.

**Where:** left navigation → **Audit Reports**.

![Audit Reports: generate a new report by type (Full Report, Controls Only, Findings Only, Drift History, Remediation Audit) and format (PDF + CSV or CSV only), with 3 reports generated; Network VAPT report downloads and the Evidence Bundle per active framework below](/img/screenshots/compliance/audit-reports.webp)

## Generate a report

1. Under **Generate New Report**, pick a report type (table below).
2. Pick a format:
   - **PDF + CSV**: a formatted PDF with the content hash printed on every page, plus every section as CSV.
   - **CSV only**: every section as CSV, with the same content hash.
3. Click **Generate** (the button names the type and format, for example *Generate Full Report (PDF)*). Generation runs as a background job; the page refreshes every 60 seconds, and the report appears in **Report History** when it is ready.

Generating needs the **Manage Assessments** permission. Requesting the same type and format while one is already running joins the running job instead of starting a second.

## Report types

Every report starts with the **framework scores** section: the per-framework implementation score with every input, so the other figures can be reproduced.

| Report | Sections included |
| --- | --- |
| **Full Report** | framework scores · controls · contradicted attestations · findings · drift · remediation · sync history · unmapped failing checks |
| **Controls Only** | framework scores · controls |
| **Findings Only** | framework scores · findings |
| **Drift History** | framework scores · drift |
| **Remediation Audit** | framework scores · remediation |

## What each section contains

| Section | Columns |
| --- | --- |
| **framework_scores** | Framework, implementation score, assessed, in-scope controls, implemented, partial, evidence-only, planned, not implemented, not assessed, not applicable, implemented with open findings, with current evidence, method version |
| **controls** | SCF ID, domain, control name, active frameworks mapped, implementation status, scored status, open findings, current evidence count, manual override, last auto-update, update reason. One row per control of the active frameworks. |
| **contradictions** | SCF ID, status, attested by, attested at, failing checks, active findings, contradicted since, check IDs. Controls a person marked implemented that active scan failures contradict. |
| **findings** | Check ID, title, severity, status, service, provider, region, resource ID, description. Every cloud posture finding stored for the team, in every status. |
| **drift** | Drift ID, detected at, total drifts, regressions, and a count per [drift type](./drift-detection.md#what-counts-as-drift). One row per detection run. |
| **remediation** | Action ID, playbook, check ID, resource ID, provider, risk level, status, auto-approved, requested by, approved by, created at, executed at. The full [remediation playbook](./autonomous-compliance.md#remediation-playbooks) trail. |
| **compliance_scores** | Sync ID, synced at, decision method, controls and findings counted, controls updated / upgraded / downgraded, controls not assessed for lack of evidence. The [sync history](./autonomous-compliance.md#what-runs-on-its-own). |
| **unmapped_checks** | Check ID, source, reason, active findings. Failing checks that map to no SCF control. |

Sections are not truncated: every row is in the CSV. The PDF prints up to 2,000 rows per section and states where the complete list is; columns not printed in the PDF are named and are in the CSV.

## Frozen reports and verification

A report is frozen when it is issued:

- The report's canonical data file (JSON) is hashed. That SHA-256 is the **content hash**, printed on every PDF page and shown in the history.
- The PDF, each section CSV and the data JSON are kept byte for byte, each with its own SHA-256. Re-downloading serves the issued file, not a regeneration.
- Reports issued before freezing was introduced have no kept files. Their sections are regenerated from current data and labeled as regenerated.

To check a report later, paste a SHA-256 into **Verify a report**:

| You paste | Result |
| --- | --- |
| The SHA-256 of a downloaded file (PDF, CSV or data JSON) | Proves that exact file is unaltered and was issued to your team |
| The content hash from a PDF footer | Identifies which report it is; it does not prove the PDF file itself is unaltered |
| Anything else | Not verified: the file was altered, or did not come from this platform |

:::note
A kept copy can be missing if object storage was unavailable or the file exceeded `AUDIT_REPORT_COPY_MAX_BYTES` (default 1 GiB). The history then marks that file *not kept*; its SHA-256 is still on record. Generate a new report to get the file.
:::

## Evidence bundle

The **Evidence bundle** panel downloads the per-framework [auditor package](./evidence-hub.md#auditor-package) for each active framework: a ZIP organized by control, with evidence in four layers. It is the same export as in the Evidence Hub and is built from current evidence when downloaded.

The page also shows a **Network VAPT report** download (PDF or Word) built from the latest Greenbone OpenVAS and nmap results, for users permitted to export it.

## Retention

Issued report files are kept for **180 days** (`REPORT_RETENTION_DAYS`; `0` keeps them indefinitely). Reports are scoped to your team. The history shows the true number of reports, not only the newest page.

## Which report for which question

| The auditor asks… | Send |
| --- | --- |
| "Show me your control status as of today, and which ones a human set" | **Controls Only**. The *manual override* and *update reason* columns answer the second half. |
| "What open issues do you have in the cloud estate?" | **Findings Only** |
| "Has your posture regressed during the audit period?" | **Drift History** |
| "Who approved automated changes to production?" | **Remediation Audit** |
| "Do any attested controls conflict with your scan results?" | **Full Report**, *contradictions* section |
| "Give me everything" | **Full Report** |

For the artifacts behind each control, use the **Evidence bundle**. For the India DPDP regime, the [DPDP audit pack](./dpdp-privacy.md#audit--export) is a separate, sealed export.

The Compliance Engine page also has an **Engine Exports** tab with quick CSV exports of the same engine data; it links here for formal audit reports.

## Related

- [Compliance Engine](./autonomous-compliance.md): the syncs, drift and remediation actions these reports export.
- [Reports & AI](../reports-and-ai/index.md): executive and scheduled reports across the whole platform.
- [Compliance & GRC API](./api.md#audit-reports): generate, list, download and verify over REST.
