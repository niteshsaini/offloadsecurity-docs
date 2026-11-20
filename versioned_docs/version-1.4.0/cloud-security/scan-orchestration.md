---
title: "Running Cloud Scans"
sidebar_label: "Running Cloud Scans"
sidebar_position: 3
description: "Start quick or full posture scans, record the scan authorization, understand how work is split per region and provider, read progress and status, and keep accounts scanned on a schedule."
---

# Running Cloud Scans

A cloud scan inventories the resources in one account and evaluates its configuration against the platform's check set. Scans run in the background as many parallel jobs, results stream in as each job finishes, and every repeat scan is compared to the last one so findings open and close automatically. Each run records what it scanned, how, and as which identity, and freezes its findings so its report can be reproduced later.

## Start a scan

| From | How |
| --- | --- |
| **Cloud Security → Accounts** | **Quick scan** or **Full scan** on an account card. |
| **Cloud Security → Coverage** | **Scan now** starts a full scan of every account that is not covered yet. |
| **Cloud Accounts → Manage Accounts** | **Quick Scan** / **Full Scan** per row, or select several rows and **Start Scan** in bulk. |
| **Automatically** | A first scan runs when an account is connected; a **daily incremental** and **weekly full** scan are scheduled for every account (see [Scheduled scans](#scheduled-scans)). |
| **API / CI** | `POST /api/cloud-accounts/{id}/scan` with an API key, or `POST /api/cloud-scans/initiate` from a signed-in session — see the [Cloud Security API](./api.md#scans). |

Only one scan can run per account at a time. Starting another while one is in progress returns the running scan instead of queuing a duplicate. Starting scans from the UI needs the **Create Cloud Scans** permission.

:::note[Read-only, always]
Scans only ever **read** your environment with the credentials you provided at onboarding. Nothing is created, changed or deleted in your cloud. On AWS, each scan assumes the account's role (or uses its access keys) and verifies with `sts:GetCallerIdentity` that it reached the account you entered; a mismatch refuses the scan.
:::

## Scan authorization

A scan run can carry an **authorization attestation**: who authorized testing the account, an optional reference (for example a change or engagement ticket), the environment and an optional end date. The attestation is recorded on the run, kept on the account as its **standing authorization**, and covers the account's scheduled scans until the end date. Every run's report prints the authorization it ran under — or says that none was recorded.

Whether an attestation is **required** is a deployment setting, `SCAN_REQUIRE_AUTHORIZATION` (off by default). With it on:

1. The first scan you start on an account opens **Authorization required**.
2. Tick **I am authorized to test this target**, optionally add a reference and an end date, and select **Record and start scan**.
3. Scheduled scans then run under that standing authorization. Once it ends, scans of the account are refused until someone records a new one.

With it off, scans run as before and are recorded as *authorization not recorded* — never as authorized. Bulk **Start Scan** and Coverage **Scan now** do not prompt for an attestation; with the setting on, an account without a current one is counted as failed there.

## Scan types and regions

All scan types run the **complete check set**. The type controls the region footprint the platform picks when you have not configured regions, and how the run is labeled in history and schedules.

| Type | Region footprint on AWS when no regions are configured | Typical use |
| --- | --- | --- |
| **Full** | Every region **enabled** on the account | The weekly baseline and the run to do before an audit. |
| **Incremental** | Every region enabled on the account | The daily scheduled run, and the **Quick scan** button on Cloud Security → Accounts. |
| **Quick** (Manage Accounts only) | `us-east-1` only — the button then reads **Quick scan (us-east-1)** | A fast smoke test of one region. |

Region precedence is always: **regions you pass explicitly → the account's configured regions (wizard or *Regions* editor) → the default for the scan type**. The enabled-region list is read from the account (`ec2:DescribeRegions`) and cached for a day; if that lookup fails, the scan falls back to a fixed list of 13 common commercial regions. The run records which scope it used — configured, every enabled region, the fallback list or the single quick-scan region — and the run's report prints it, naming any regions that were **not** tested.

On **GCP and Azure** a scan always covers the whole project or subscription, regardless of type.

### How scans partition work by provider

| Provider | Boundary | Parallelism | Why |
| --- | --- | --- | --- |
| **AWS** | Account | One discovery job **and** one compliance job **per selected region**, run concurrently | AWS resources and checks are genuinely region-scoped; splitting by region parallelizes a large account. |
| **GCP** | Project | One discovery + one compliance job (`global`) | Cloud Asset Inventory and the checks read the whole project; per-region fan-out would repeat identical work. |
| **Azure** | Subscription | One discovery + one compliance job (`global`) | Resource Graph / ARM enumerate the whole subscription at once. |

Every scan additionally runs two account-wide jobs once: **Kubernetes cluster discovery** (EKS / GKE / AKS) and **container registry discovery** (ECR / Artifact Registry / ACR). Discovered clusters and registries appear in [Kubernetes Security](../security-scanning/kubernetes/index.md) and [Container Security](../security-scanning/containers/index.md).

For GCP and Azure, breadth comes from onboarding **more projects or subscriptions** — each scans in parallel with the others. GCP organization onboarding does that for you ([Connecting Cloud Accounts](./connecting-accounts.md#onboarding-a-gcp-organization)); AWS accounts and Azure subscriptions are added one by one.

## What happens during a scan

1. **Queued.** The platform checks that no other scan is running for the account, resolves the authorization and region scope, records the run and creates its jobs.
2. **Discovery** jobs enumerate resources per region (or per project/subscription) through the provider's native APIs and write them to [Asset Inventory](./asset-inventory.md). On AWS, untagged EC2 instances, security groups, volumes, VPCs, RDS instances and Lambda functions are listed too, and encryption-at-rest status is collected for encryptable resources.
3. **Compliance** jobs evaluate configuration with the check engine (Prowler 5.44.0) for the same scope. They are lightly staggered so the run stays under your cloud provider's API rate limits. The raw Prowler output of each region is kept with its SHA-256.
4. **Results stream in** per job. Findings appear on the **Findings** tab and assets in the inventory before the whole run has finished.
5. **Delta ingestion.** Every repeat scan is compared against the previous state for the same scope: new failures open as findings, and failures that are no longer reported are **auto-resolved** — but only for checks this run actually evaluated (pass or fail). Checks that errored, were denied access or returned *manual* leave existing findings open. Findings you resolved or suppressed keep their status. A region that unexpectedly reports **zero** results is treated as unverified and resolves nothing — a broken credential can never make an account look clean.
6. **Completion.** Once every job has finished, the run gets its final status (below), its findings are frozen into a snapshot for [point-in-time reports](./point-in-time-reports.md), and your [custom policies](./custom-policies.md) are evaluated against the refreshed inventory.

## Scan history

**Cloud Security → Cloud Scans** lists every run for the team, grouped under status tabs — **Completed**, **Partial**, **Running**, **Failed**, and **Queued** / **Cancelled** when there are any — with provider, account, type, findings count and date. Filter by provider, account or type.

![Cloud Scans tab: 28 runs with provider, account, type, findings, status and date columns, plus completed / running / failed tiles](/img/screenshots/cloud-security/cloud-scans-list.webp)

Select **View** on a row for the run's summary — account, type, status, finding count, and metadata such as run ID, total assets, completed and failed sub-jobs, and the queued / running / completed timestamps. The detail window lists the run's first 50 findings; use the Findings tab or an export for all of them. **AI Summary** produces a plain-language recap of the run.

Completed and Partial runs also offer **PDF**, **Word** and **Compare** — see [Point-in-Time Reports](./point-in-time-reports.md).

![Scan detail dialog for an AWS full scan: 41 findings, 46 assets, 8 completed sub-jobs and the run timeline](/img/screenshots/cloud-security/cloud-scan-detail.webp)

## Reading status and progress

| Status | Meaning |
| --- | --- |
| **Queued** | Accepted and waiting for a worker. |
| **Running** | Jobs are discovering assets and running checks. The account card shows the overall percentage; Cloud Scans shows progress per region. |
| **Completed** | Every job finished and every region returned verified results. |
| **Partial** | The run finished but is incomplete: a job failed or was cancelled, Prowler reported check errors in a region (for example access denied), or a region returned no results it could verify. You have usable results but incomplete coverage, so it is deliberately not shown as a clean run, and nothing is marked fixed for the parts that failed. |
| **Failed** | No usable result — almost always a credentials or permissions problem. Previous findings stay as they were. |
| **Cancelled** | Stopped before finishing (via the API `DELETE /api/cloud-scans/{run_id}`). |

While a run is in progress you see an **overall percentage** plus separate discovery and compliance progress, and an **estimated completion** that scales with the number of regions. The confirmation message's time estimates are rough; large accounts take longer. A finished run reports **total assets**, **total findings** and the **breakdown by severity**.

:::warning[Partial usually means permissions or limits]
Missing read permission for a service or region, or API throttling in your account, are the usual causes. The run's report lists each region and job that was not tested or was incomplete; fix the role or service account described in [Required Permissions](./permissions.md), then re-scan.
:::

## Scheduled scans

Every account gets two schedules the moment it connects:

| Schedule | Cadence | Purpose |
| --- | --- | --- |
| **Daily Cloud Incremental Scan** | Every day 02:00 UTC | Keeps findings and inventory current. |
| **Weekly Cloud Full Scan** | Sunday 03:00 UTC | The baseline that catches drift and deletions. |

Manage them in **Unified Scheduler** — retime, pause or resume per account. Scheduled runs honor the one-scan-per-account rule and skip an account that was scanned very recently (within 22 hours for incremental, 6 days for full), so overlapping triggers never pile up. Large fleets are dispatched with a staggered start rather than all at once. When `SCAN_REQUIRE_AUTHORIZATION` is on, scheduled scans run only while the account has a current standing authorization.

If an account fails **three times in a row**, further scheduled runs are paused for that account until a scan succeeds or its credentials are replaced — see [Managing Connected Accounts](./account-management.md#account-status-and-health).

## Related

- [Reviewing & Triaging Findings](./findings.md) — what to do with the results.
- [Point-in-Time Reports](./point-in-time-reports.md) — a reproducible report per run, and run comparison.
- [Compliance & Benchmark Checks](./prowler-integration.md) — the checks behind the findings.
- [Cloud Security API](./api.md#scans) — start, poll and cancel scans programmatically.
- [Troubleshooting](./troubleshooting.md#scans) — scans that will not start, stay queued, or come back partial.
