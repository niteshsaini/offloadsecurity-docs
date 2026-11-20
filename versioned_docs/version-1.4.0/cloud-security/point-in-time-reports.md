---
title: "Point-in-Time Reports for a Cloud Scan Run"
sidebar_label: "Point-in-Time Reports"
sidebar_position: 3.5
description: "Download a reproducible posture report for one cloud scan run, compare two runs finding by finding, and verify that a report file was issued by the platform."
new_in: 1.4.0
---

# Point-in-Time Reports for a Cloud Scan Run

A posture report for one scan run is rebuilt from that run's **frozen snapshot**, so later scans and triage do not change it. Use it as audit evidence for "the state of this account on this date", compare it with the previous run to see what changed, and verify later that a report file is exactly the one the platform issued.

## Before you begin

- A **Completed** or **Partial** cloud scan run. Failed, running and queued runs have no report or comparison: there is no result to freeze.
- The **View Scans** permission.

## Steps

1. **Find the run.** Open **Cloud Security → Cloud Scans** and find the run under the **Completed** or **Partial** tab. **View** shows its run ID.
2. **Download the report.** Select **PDF**, or **Word** for an editable document. The file is built from that run only.
3. **Compare with the previous run.** Select **Compare** to see what changed since the previous run of the same account.

## What the report contains

When a run completes, the findings it observed are written as a snapshot with a recorded SHA-256. A report for the run reads the snapshot (the hash is checked; a mismatch is refused and stated) instead of live findings. The report's **Scope & Methodology** is built from what actually ran:

| Row | What it states |
| --- | --- |
| **Accounts Assessed** | The accounts the run covered. |
| **Authorization** | Who attested that testing was authorized, when, the reference and environment, whether it was a standing authorization — or that none was recorded or it had expired. See [Scan authorization](./scan-orchestration.md#scan-authorization). |
| **Scan Runs** | Status and start → end time per account, and who launched it. |
| **Regions Tested** / **Region Scope** | The regions that completed, and which scope was used (configured, every enabled region, the fallback list, or the single quick-scan region — with "other regions were NOT tested" where that applies). |
| **Engine** | The Prowler version the run reported, how it was launched, and the image digest. |
| **Scan Identity** | The identity the scan ran as: the STS-verified role ARN on AWS, the service-account email and project on GCP, the client and tenant ID on Azure. No secrets. |
| **Raw Evidence** | The SHA-256 of the raw Prowler output kept per region. |
| **Estate Coverage** | For AWS Organizations and Azure tenants visible to the credential: member accounts or subscriptions that are not onboarded, and onboarded ones not assessed in this report. |
| Coverage gaps | Each region or job not tested or incomplete, regions with check errors, results that could not be saved, and where resolution by absence was withheld. |
| **Scan Delta Basis** | Whether the "changes since last scan" section is exact (from the previous run's snapshot) or approximate. |
| **Display Limits** | Every chart that shows a top-N of a larger set says so. |

Compliance scores in the report count only checks that were assessed: **passed ÷ (passed + failed)**. Checks reported as *manual* are not assessed, and suppressed or accepted findings are counted as exceptions.

:::note[Without a run ID the report is not point-in-time]
Through the API, a posture report requested without `scan_run_id` shows the current state of every finding across all runs. Only a run-scoped request reads a frozen snapshot.
:::

## Reading a comparison

**Compare** lists findings in four groups, each shown in full, page by page:

| Group | Meaning |
| --- | --- |
| **New failing** | Failing in this run, not failing (or absent) in the baseline. |
| **Fixed** | Failing in the baseline, passing or resolved in this run. |
| **Still failing** | Failing in both runs. |
| **Not re-evaluated** | Failing in the baseline and absent from this run — neither fixed nor still failing. |

Above the lists, Compare says when either run was **Partial** or when the two runs covered different regions. The default baseline is the account's previous run that has a snapshot; over the API you can name another one.

## Verify an issued report

Every Cloud Security Posture **PDF** and **HTML** export is fingerprinted when it is issued: the response carries its SHA-256 in the `X-Content-SHA256` header, the issue is recorded (who, when, which run), and an exact copy is kept.

- **Check a file:** compute its SHA-256 and call `GET /api/native-scans/exports/verify?sha256=<digest>`. The answer says whether this platform issued exactly that file to your team.
- **Re-download the original:** `GET /api/export/issued/<sha256>` returns the issued copy byte for byte (team-scoped). A kept copy that no longer matches its digest is refused.

Kept copies follow the deployment's report retention (`REPORT_RETENTION_DAYS`, 180 days in the example configuration). Word (DOCX) exports are not fingerprinted.

## Over the API

| Task | Endpoint |
| --- | --- |
| PDF for one run | `GET /api/export/cloud-posture?scan_run_id=<run ID>` |
| HTML for one run | `GET /api/export/cloud-posture.html?scan_run_id=<run ID>` |
| Word for one run | `GET /api/export/cloud-posture.docx?scan_run_id=<run ID>` |
| Compare two runs | `GET /api/cloud-scans/<run ID>/compare` (optionally `?baseline=<earlier run ID>`) |

## If something goes wrong

- **"No earlier run of this account has a frozen snapshot to compare with."** — This is the account's first run with a snapshot. Compare becomes available after the next scan.
- **"Run … has no frozen snapshot (it predates snapshots, or none was taken)"** — One of the two runs was made before snapshots existed (before release 1.4.0). Compare a newer run.
- **No PDF / Word / Compare buttons** — The run failed, is still running, or is queued.

## Next steps

- [Running Cloud Scans](./scan-orchestration.md) — scan scope, authorization and status.
- [Compliance & Benchmark Checks](./prowler-integration.md) — how scores are computed.
- [Report Catalog](../reports-and-ai/report-catalog.md) — the platform's other reports.
