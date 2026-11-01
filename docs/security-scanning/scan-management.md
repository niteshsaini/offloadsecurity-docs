---
title: "Scan Management & Scheduling"
sidebar_label: "Scan Management"
sidebar_position: 7
description: "Schedule recurring scans from templates or custom cron, keep their authorization current, manage and pause schedules, review scan history, and understand how long results are kept."
---

# Scan Management & Scheduling

Once you've run a few scans, you'll want them to keep running on their own and you'll want a tidy place to review everything that has run. This page covers the day-to-day management side of scanning: scheduling scans to run automatically, keeping their authorization current, browsing your scan history, re-running past scans, and how long results are kept.

:::note[Running pipeline scans]
Triggering scans from a build pipeline (GitHub Actions, Jenkins, and the like) is covered separately on the [CLI & CI/CD](../cli-and-cicd.md) page. This page is about scheduling and managing scans inside the platform.
:::

## What you can do here

- **Schedule recurring scans** so they run on a fixed cadence (for example, every night) without anyone clicking a button.
- **Keep scheduled scans authorized** — record who authorized testing the targets, and re-attest when the authorization expires.
- **Review scan history** — see what ran, when, whether it succeeded or failed, and what it found.
- **Re-run a past scan** with the same settings, or remove old runs you no longer need.
- **Know the retention windows** for each kind of scan data.

---

## Scheduling recurring scans

Recurring and automated scans are managed from the **Unified Scheduler**, found under **Management → Unified Scheduler** in the left navigation. The scheduler isn't just for scans — it also handles assessments, evidence collection, reports, and reminders — but this page focuses on the **Scans** entity type.

At the top of the page, status cards summarize your schedules at a glance: total schedules, how many are active, how many are paused, how many are expiring soon, available templates, and whether the scheduler itself is running.

### Which scan types can be scheduled

| Scan type | On a schedule in 1.4.0 |
| --- | --- |
| Cloud Security, Kubernetes | Dispatched to the onboarded accounts or clusters you pick |
| Application Scan (App Scan) | Dispatched with the same options as a manual App Scan, including OAuth2 authentication |
| Web Application | Dispatched as a Nuclei URL scan per target URL |
| Other scan types in the list (API Security, API Discovery, Domain Recon, Lightweight Scan, SSL/TLS Monitor, code and IaC types) | Dispatched to the targets you enter |
| **Network** and **Container Registry** | Offered, but every run fails with "not yet implemented" |

:::warning[Network and Container Registry schedules do not run]
In 1.4.0 the **Network** and **Container Registry** scan types — and the **Weekly Network Scan** and **Weekly Container Audit** templates — are listed but cannot run on a schedule: each run fails as not yet implemented. Run Nmap scans from **Scanning** ([Network Scans](./network-scans.md)), schedule an **App Scan** with the Nmap tool for recurring port coverage of an application, and use registry polling for images ([Container Security](./containers/index.md)).
:::

### Create a schedule from a template (quickest)

Templates are pre-built schedules for common jobs (such as a daily cloud scan or a daily App Scan), so you don't have to fill in every field.

1. Open the **Templates** tab, or select **From Template**.
2. Pick the template that matches the scan you want to automate.
3. Provide its targets: pick the onboarded **cloud accounts**, **Kubernetes clusters** or **registries** from the list, or enter **URLs / hosts / domains** one per line.
4. For web, API, network and domain scan types, fill in **Authorization & scope** (see below).
5. Select **Create Schedule**. The new schedule appears in the list and starts running on its cadence.

### Create a custom schedule

For full control, build a schedule from scratch:

1. Select **Create Schedule**.
2. Enter a **Name** and (optionally) a **Description**, set **Entity Type** to **Scans**, and pick the scan type.
3. Provide the targets the scan type requires (picker or one-per-line box).
4. Choose a **Schedule Type** and its timing:
   - **Cron Schedule** — run at specific times using a cron expression (the default, `0 2 * * *`, runs daily at 2:00 AM).
   - **Interval** — run at a fixed interval.
   - **One-Time** — run once at a specific date and time.
   - **Expiry-Based** — driven by an expiry date rather than a fixed clock.
5. Under **Lifecycle Configuration**, set how long results stay valid (**Validity Period**), and optionally turn on **auto-renewal** with a renewal lead time.
6. Under **Notifications**, choose when to be alerted — on **completion**, on **failure**, and on **expiry warnings**. Notifications can be delivered in-app and, where configured, by email or Slack.
7. For web, API, network and domain scan types, fill in **Authorization & scope**.
8. Select **Create Schedule**.

A target the platform would refuse for a manual scan — loopback, a cloud-metadata address, or a private address while `ALLOW_PRIVATE_SCAN_TARGETS` is off — is refused when you save the schedule (HTTP 400, naming the target and the reason), and checked again at every run.

:::tip[Time zones and timing]
Schedules use **UTC** by default. When you set a cron expression, double-check it against your team's working hours, and prefer off-peak times (like overnight) so scans don't compete with production traffic.
:::

### Authorization on scheduled scans

Scheduled web, App Scan, API, SSL, domain, network and code scans carry the same **engagement record** as a manual launch: an attestation that you are authorized to test the targets, recorded with your name and the time, an optional reference, the environment, and an optional **authorized until** date ([Engagement & Evidence](./scan-evidence.md)).

- When the deployment sets `SCAN_REQUIRE_AUTHORIZATION=true`, **Create Schedule** stays disabled until you attest.
- At every run the platform checks the stored authorization again. If it is missing (when required) or past its end date, the run **fails, scanning nothing**, with the reason. If only some targets are refused, the others run and the refused ones are reported as failed targets.
- The schedule list marks affected schedules **Authorization expired** or **No authorization recorded** (the latter only where authorization is required). Use the **Re-attest** action on the row to record a fresh authorization.
- Each scan a schedule starts is saved with the schedule's engagement record.

### Managing existing schedules

Each schedule in the list shows its type, its cadence, the **Next Run** time, any **expiry**, and its current **status** (active, paused, expired, or completed). Use the row actions to:

- **Run Now** — trigger the schedule immediately, without waiting for its next scheduled time.
- **Pause / Resume** — temporarily stop a schedule and restart it later.
- **View Details** — a summary showing the last run, the next run, total / successful / failed run counts, and lifecycle details (validity period, expiry date, auto-renewal, grace period).
- **Re-attest** — shown when the schedule's authorization needs renewing.
- **Delete** — remove the schedule entirely.

Filter the list with the tabs (**All Schedules**, **Scans**, **Assessments**, **Evidence**, **Reports**, **System Jobs**), search by name, and filter by status. The **Expiring Soon** tab highlights schedules whose validity is about to lapse so you can renew them in time.

:::note[Permissions]
Creating, editing, pausing, and deleting schedules requires the **Manage Scans** permission. If you only have view access, you'll see the schedules but won't be able to change them. See **[Roles (RBAC)](../authentication/rbac-team-management.md)** for what each role can do.
:::

---

## Where scheduled and automated scans appear

A schedule simply runs a scan on your behalf — so once it fires, the resulting scan behaves exactly like one you started manually.

- **Scan history (results):** Scheduled App Scans appear on **Scanning → Assessments**, marked **scheduled**; scheduled single-tool web scans appear on **Scanning → Targeted runs** alongside manual scans; cloud, Kubernetes and code scans appear in their own modules.
- **Scheduler execution history:** The Unified Scheduler's **History** tab records every time a schedule ran — when it started, how long it took, whether it **completed**, **failed**, or is still **running**, and a short result summary. Select any row to expand it for the full configuration and result details (for example, how many accounts or clusters were scanned, and which targets were refused).

Together, these give you two complementary views: the **History** tab tells you whether your automation is firing reliably, and the scan results view shows you what those runs actually found.

---

## Reviewing scan history

**Scanning → Targeted runs** shows every single-tool run as a **target tree** (target → scan type → runs) by default, with an **All runs** table one click away. Three tabs separate **Completed** (including partial runs), **Running** (refreshes on its own) and **Failed** runs (for example a target refused by the safety checks), so problems aren't hidden. Summary cards show **Total Scans**, **Total Findings**, and counts of **Completed** and **Failed** runs, and you can filter by **Tool Type** (such as ZAP, Nmap, or Nuclei). App Scan assessments are listed separately under **Scanning → Assessments**.

From a completed run you can:

- **Open** it to review the findings, what ran and its raw output.
- **Compare** it with the previous run of the same tool on the same target (new, fixed, unchanged).
- **Re-scan** — start a fresh scan that reuses the original run's settings, exclusions and authorization, so you don't have to re-enter them.
- **Download a report**, or select several runs and roll them into a **consolidated report**.
- **Delete** runs you no longer need (they are kept as tombstones for 30 days by default before being purged).

Details in [Scan Results](./scan-results.md).

:::note[Re-running vs. scheduling]
Use **Re-scan** for a one-off "run that again" check. If you find yourself re-scanning the same target regularly, turn it into a **schedule** instead so it happens automatically.
:::

---

## Result retention

Scan data is not kept forever. Each kind of data has a retention window, enforced by database expiry and by a **retention cycle that runs automatically every day**. The shipped defaults in 1.4.0:

| Data | Default retention | Set with |
| --- | --- | --- |
| Targeted-run records (Scanning → Targeted runs) | 365 days (12 months) | `NATIVE_SCAN_RETENTION_DAYS` |
| Cloud, Kubernetes, container, code SBOM and WAF scan results; scan runs | 730 days (24 months) | `SCAN_RETENTION_DAYS`, `SCAN_RUN_RETENTION_DAYS`, `CONTAINER_SCAN_RETENTION_DAYS`, and related variables |
| Findings (CSPM, Kubernetes, code; resolved unified findings) | 730 days (24 months) | `FINDING_RETENTION_DAYS`, `CODE_SCANS_RETENTION_DAYS`, `UNIFIED_FINDINGS_RETENTION_DAYS` |
| Compliance records | 1,825 days (5 years) | `COMPLIANCE_RETENTION_DAYS` and related variables |
| Deleted targeted runs (tombstones) | 30 days | `SCAN_TOMBSTONE_DAYS` |
| Raw tool output and issued report copies | Deleted with their run | — |

The windows are deployment settings: an operator changes them in the environment and restarts the platform. Before deletion, the retention cycle also **summarizes** older data (so trend reporting keeps working after the full detail is gone) and can **archive** it.

Over the API, `GET /api/scan-retention/status` and `GET /api/scan-retention/policies` show the active windows, and `POST /api/scan-retention/run-cycle` runs a retention cycle on demand (requires **Manage Scans**).

:::warning[Deletion is permanent]
Once data passes its retention window it is removed for good. If you have a compliance requirement to retain scan evidence for a set period, have your operator raise the relevant variable **before** that data ages out, and keep downloaded reports with their SHA-256 digests ([Engagement & Evidence](./scan-evidence.md#fingerprinted-frozen-exports)).
:::

---

## Related

- **[Running Web, API & Host Scans](./native-scans.md)** — run App Scans and targeted scans on demand.
- **[Code Command Center](./code/index.md)** — source-code analysis.
- **[Container Security](./containers/index.md)** — scan container images across your registries.
- **[Kubernetes Security](./kubernetes/index.md)** — cluster posture scanning.
- **[Quickstart](../getting-started.md)** — sign in, tour the dashboard, and learn the Scan → Finding → Risk → Report flow.
