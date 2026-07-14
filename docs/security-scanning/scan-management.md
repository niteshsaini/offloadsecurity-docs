---
title: "Scan Management & Scheduling"
sidebar_label: "Scan Management"
sidebar_position: 6
---

# Scan Management & Scheduling

Once you've run a few scans, you'll want them to keep running on their own and you'll want a tidy place to review everything that has run. This page covers the day-to-day management side of scanning: scheduling scans to run automatically, browsing your scan history, re-running past scans, and controlling how long results are kept.

![Unified Scheduler for scans, assessments, evidence collection, and reports](/img/screenshots/unified-scheduler.png)

:::note[Running pipeline scans]
Triggering scans from a build pipeline (GitHub Actions, Jenkins, and the like) is covered separately on the **CLI & CI/CD** page. This page is about scheduling and managing scans inside the platform.
:::

## What you can do here

- **Schedule recurring scans** so they run on a fixed cadence (for example, every night) without anyone clicking a button.
- **Review scan history** — see what ran, when, whether it succeeded or failed, and what it found.
- **Re-run a past scan** with the same settings, or remove old runs you no longer need.
- **Control result retention** so old scan data is summarized, archived, and eventually cleaned up on a schedule you choose.

---

## Scheduling recurring scans

Recurring and automated scans are managed from the **Unified Scheduler**, found under **Management → Unified Scheduler** in the left navigation. The scheduler isn't just for scans — it also handles scheduled assessments, evidence collection, reports, and reminders — but this page focuses on the **Scans** entity type.

At the top of the page, status cards summarize your schedules at a glance: total schedules, how many are active, how many are paused, how many are expiring soon, available templates, and whether the scheduler itself is running.

### Create a schedule from a template (quickest)

Templates are pre-built schedules for common jobs (such as a recurring cloud or Kubernetes scan), so you don't have to fill in every field.

1. Select **From Template** at the top of the Unified Scheduler.
2. Pick the template that matches the scan you want to automate.
3. If the template needs a target, you'll be asked to provide it — for example, the **cloud account IDs**, **container registry IDs**, or **cluster IDs** to scan. You can find these IDs in the corresponding section of the platform (Cloud Accounts, Container Registries, or Kubernetes).
4. Select **Create Schedule**. The new schedule appears in the list and starts running on its cadence.

### Create a custom schedule

For full control, build a schedule from scratch:

1. Select **Create Schedule**.
2. Enter a **Name** and (optionally) a **Description**, and set **Entity Type** to **Scans**.
3. Choose a **Schedule Type** and its timing:
   - **Cron Schedule** — run at specific times using a cron expression (the default, `0 2 * * *`, runs daily at 2:00 AM).
   - **Interval** — run every N hours.
   - **One-Time** — run once at a specific date and time.
   - **Expiry-Based** — driven by an expiry date rather than a fixed clock.
4. Under **Lifecycle Configuration**, set how long results stay valid (**Validity Period**), and optionally turn on **auto-renewal** with a renewal lead time.
5. Under **Notifications**, choose when to be alerted — on **completion**, on **failure**, and on **expiry warnings**. Notifications can be delivered in-app and, where configured, by email or Slack.
6. Select **Create Schedule**.

:::tip[Time zones and timing]
Schedules use **UTC** by default. When you set a cron expression, double-check it against your team's working hours, and prefer off-peak times (like overnight) so scans don't compete with production traffic.
:::

### Managing existing schedules

Each schedule in the list shows its type, its cadence, the **Next Run** time, any **expiry**, and its current **status** (active, paused, expired, or completed). Use the row actions to:

- **▶ Run Now** — trigger the schedule immediately, without waiting for its next scheduled time.
- **⏸ Pause / ▶ Resume** — temporarily stop a schedule and restart it later.
- **👁 View Details** — open a summary showing the last run, the next run, total/successful/failed run counts, and lifecycle details (validity period, expiry date, auto-renewal, grace period).
- **🗑 Delete** — remove the schedule entirely.

You can filter the list by entity type using the tabs (including a dedicated **Scans** tab), search by name, and filter by status. The **Expiring Soon** tab highlights schedules whose validity is about to lapse so you can renew them in time.

:::note[Permissions]
Creating, editing, pausing, and deleting schedules requires the **Manage Scans** permission. If you only have view access, you'll see the schedules but won't be able to change them. See **[Roles (RBAC)](../getting-started.md)** for what each role can do.
:::

---

## Where scheduled and automated scans appear

A schedule simply runs a scan on your behalf — so once it fires, the resulting scan behaves exactly like one you started manually.

- **Scan history (results):** Completed runs land in your scan results view alongside manual scans, with their findings, severity counts, and downloadable reports.
- **Scheduler execution history:** The Unified Scheduler's **History** tab records every time a schedule ran — when it started, how long it took, whether it **completed**, **failed**, or is still **running**, and a short result summary. Select any row to expand it for the full configuration and result details (for example, how many accounts or clusters were scanned).

Together, these give you two complementary views: the **History** tab tells you whether your automation is firing reliably, and the scan results view shows you what those runs actually found.

---

## Reviewing scan history

Your scan results view organizes runs into three tabs:

- **✅ Completed** — runs that finished successfully, with their findings.
- **🔄 Running** — scans currently in progress. This tab refreshes on its own so you can watch a scan complete.
- **❌ Failed** — runs that were rejected or errored (for example, a target that failed safety validation), surfaced so problems aren't hidden.

Summary cards at the top show **Total Scans**, **Total Findings**, and counts of **Completed** and **Failed** runs. You can also filter the list by **tool type** (such as ZAP, Nmap, or Nuclei) to focus on one kind of scan.

From a completed run you can:

- **Open** it to review the normalized findings.
- **Re-scan** — start a fresh scan that reuses the original run's settings, so you don't have to re-enter the target and options.
- **Download a report** — generate a consolidated security report; you can select multiple completed scans to roll them into a single report.
- **Delete** runs you no longer need.

:::tip[Re-running vs. scheduling]
Use **Re-scan** for a one-off "run that again" check. If you find yourself re-scanning the same target regularly, turn it into a **schedule** instead so it happens automatically.
:::

---

## Result retention

Scan results don't grow forever. The platform applies a **tiered retention policy** that keeps recent results in full detail, summarizes older ones, archives them, and eventually deletes the oldest data — all automatically.

Each retention policy has four stages:

| Stage | What happens | Default |
|---|---|---|
| **Hot** | Results are kept in full detail. | 30 days |
| **Warm** | Older results are summarized to save space (trends are preserved). | after 90 days |
| **Archive** | Results are moved to compressed archive storage. | after 365 days |
| **Delete** | Archived data is permanently removed. | after 730 days |

You can also toggle whether summarization and archival run at all. Separate policies apply to different kinds of scan data (cloud scans, Kubernetes scans, findings, native scans, compliance reports, and scan runs), so you can tune each one to your needs.

The retention cycle **runs automatically on a daily schedule** — summarizing, archiving, and cleaning up data as each stage's threshold is reached. If you ever need to, you can also trigger a retention run on demand.

:::note[Who can change retention]
Adjusting retention policies (or running a retention cycle manually) requires the **Manage Scans** permission. Summaries created during the warm stage are retained for long-term trend reporting, so historical dashboards stay useful even after the full detail is gone.
:::

:::warning[Deletion is permanent]
Once data passes the **Delete** threshold it is removed for good. If you have a compliance requirement to retain scan evidence for a set period, increase the relevant policy's thresholds **before** that data ages out.
:::

---

## Related

- **[Native Security Scans (Web, Network, SSL)](./native-scans.md)** — run web, network, and SSL/TLS scans on demand.
- **[API & Code Security Scanning](./api-code-scanning.md)** — API discovery and source-code analysis.
- **[Container & Registry Security](./container-security.md)** — scan container images across your registries.
- **[Kubernetes Security](./kubernetes-security.md)** — cluster posture and CIS benchmark scanning.
- **[Getting Started](../getting-started.md)** — sign in, tour the dashboard, and learn the Scan → Finding → Risk → Report flow.
