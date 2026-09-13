---
title: "Scheduled Reports"
sidebar_label: "Scheduled Reports"
sidebar_position: 2
description: "Send the compliance summary, board report or gap analysis on a cadence — weekly, monthly or quarterly at 09:00 UTC — rendered to PDF, emailed to the recipients, kept in history with honest run status."
---

# Scheduled Reports

The report nobody has to remember to generate is the one that actually reaches the board. A scheduled report renders the chosen executive report to PDF on its cadence, emails it, and keeps every run so the copy the CFO received in March is still downloadable in September.

**Where:** Dashboard → *Executive Dashboard* → **Executive Reports** → *Scheduled reports*.

![Scheduled reports: report type, frequency and recipients form; table of schedules with last run, delivery and next run](/img/screenshots/reports-and-ai/exec-reports-scheduled.webp)

## Create a schedule

| Field | Options |
| --- | --- |
| **Report** | Compliance summary · Board report · Gap analysis |
| **Frequency** | Weekly · Monthly · Quarterly (daily is available over the API) |
| **Recipients** | Comma-separated email addresses |

**Schedule** creates it; the first run is one interval out, at **09:00 UTC**. Schedules are per team; anyone on the team can see them.

## What a run does

Every 30 minutes the platform looks for schedules whose `next_run` has passed and, for each:

1. Builds the report from the live executive overview (the same scorer as the dashboard).
2. Renders it to **PDF** (falls back to a labelled text report if the PDF renderer is unavailable — never a silent empty file).
3. Stores the artefact in report history (team-stamped, kept **180 days**).
4. **Emails** it to the recipients as an attachment, subject `[OffloadSecurity] Scheduled <report> compliance report — <maturity>`; if no email channel is configured the run is recorded as *not delivered* rather than pretending.
5. Writes `last_run`, `last_status` (`generated`, or `error:<category>`), `run_count` and the next `next_run` back onto the schedule.

The **history** endpoint lists every run; **latest** downloads the most recent PDF.

## Delivery prerequisites

Email needs the platform's SMTP settings (`SMTP_HOST`/`SMTP_SERVER` and credentials) — see [Notifications](../integrations/notifications.md). Without them reports are still generated and downloadable; only the send is skipped, and the schedule row says so.

:::tip[One schedule per audience]
*Board report — monthly* to the executive list; *Compliance summary — weekly* to security leads; *Gap analysis — quarterly* to the control owners. Recipients who get the wrong depth stop reading.
:::

## Related

- [Executive Dashboard](./executive-dashboard.md) — the reports being scheduled.
- [Reports & AI API](./api.md#scheduled-reports) — create, list, history, latest, delete.
