---
title: "Drift Detection"
sidebar_label: "Drift Detection"
sidebar_position: 3
description: "Catch a control that regressed, lost its evaluation or was marked not applicable while failing, an attestation that scans contradict, evidence that expired or a framework that fell below its threshold, each reported once with the findings behind it, and route it to email, Slack or in-app notifications."
---

# Drift Detection

A compliance score is a number; drift is the *change* in it, and change is what auditors and you care about between two dates. Drift detection names every control, framework and evidence item that moved, with what caused it, and reports each change exactly once.

**Where:** left navigation → **Compliance Posture** → *Drift Detection* tab.

![Compliance Drift Detection: 2 total drifts, 2 regressions; latest drift details listing IAC-06 (implemented → partial) and CRY-05 (implemented → not_implemented) as control regressions with Fix this actions](/img/screenshots/compliance/compliance-drift.webp)

## What counts as drift

Each control status maps to one of four states: pass, fail, not evaluated, or not applicable. Drift is a move between those states, or one of the framework- and evidence-level events below.

| Type | Detected when | Severity |
| --- | --- | --- |
| **Control Regression** | Pass → fail, or a failing control moved further down (partial → not implemented) | high |
| **Control Recovered** | Fail → pass | low |
| **No Longer Evaluated** | Pass or fail → not evaluated (the evidence or assessment behind it was lost) | high if it was passing, otherwise medium |
| **Re-evaluated** | Not evaluated → pass or fail, for a control that was evaluated before. A control's first evaluation is its baseline, not drift. | high if it is now failing, otherwise low |
| **Failing Control Marked N/A** | A failing control was taken out of scope | high |
| **Control contradicted** / **contradiction cleared** | Active mapped scan failures contradict a status a person set to implemented, and later stop doing so (see [How status is decided](./control-status.md)) | high / low |
| **New Finding in Clean Domain** | An SCF domain whose controls were all implemented or not applicable has a regression | high |
| **Finding-count regression** | Open findings behind a control rose while its status stayed the same (compared between the last two daily snapshots) | high if up by 5 or more, otherwise medium |
| **Evidence Expired** | Evidence linked to a control passed its validity date | medium |
| **Threshold Crossed** | A framework fell below its [threshold](./autonomous-compliance.md#thresholds-and-breaches) | critical |
| **Resolved** | A breached framework is back at or above its threshold | low |

Each control drift names the control (SCF ID, name, domain), the previous and current status, and what moved it: for an engine downgrade, the active findings that caused it (a sample plus the true total); for a recovery, the findings it resolved; for a person's change, who made it and why.

A framework that has not been assessed never crosses a threshold, and nothing is reported as crossing between two checks scored by different scoring methods.

## How changes are found

Every change to a control's status is written to the compliance audit log as it happens. Drift detection reads those recorded transitions, so a change made today is reported on the next detection run, not the next day.

- Detection runs with every 4-hourly compliance refresh, after scans, and when you click **Run Drift Detection**.
- Each change is reported once, no matter how many runs see it. The summary tiles (**Total Drifts**, **Regressions**, **Evidence Expired**, **New in Clean**, **Threshold Crossed**) count the drifts new in the latest run.
- The first run for a team back-fills up to 90 days of history. Back-filled drifts are shown and flagged, but not alerted.
- **Drift History** keeps every detection run with its counts by type.

Daily posture snapshots (00:05 UTC) are still taken. They feed finding-count regressions and answer point-in-time questions such as "what was your posture on 14 March?".

Each drift is also mirrored to the unified Alerts board. A control has one row per state: a recovery resolves it, and a later regression reopens the same row.

## Fix this

A regression whose control maps to one of the [remediation playbooks](./autonomous-compliance.md#remediation-playbooks) shows **Fix this**: it creates a remediation action for the matching playbook. Approval and dry-run rules apply as on the engine tab.

## Alert policies

![Alert Policies: create policy with name, drift types, severity threshold, frameworks and notification channels](/img/screenshots/compliance/compliance-drift-policies.webp)

An **alert policy** decides which drifts become notifications:

| Field | Meaning |
| --- | --- |
| **Drift Types to Monitor** | Any of the control, evidence and threshold types above; empty = all. A policy that monitors *Control Regression* also matches *No Longer Evaluated*, *Failing Control Marked N/A* and a re-evaluation into fail. |
| **Minimum Severity** | Lowest drift severity that notifies: *Medium+* (the form's default), *High+* or *Critical only* |
| **Notification Channels** | Email and Slack, using the integrations configured under [Notifications](../integrations/notifications.md); in-app notifications are always on |

Choose at least one of Email or Slack; with neither selected the policy notifies in-app only. Policies apply to all of the team's active frameworks; there is no per-framework filter. Recipients are the policy's escalation recipients (set over the API), or every team member when none are set. With no policy configured, a default applies: severity *high* and above, by email, Slack and in-app.

Policies are evaluated after every detection run. Each notification lists up to 10 matching drifts; the full list is on the tab.

:::note
The policy form also offers a **Teams** channel and an *Info (all)* severity. In 1.4.0 drift notifications are delivered by email, Slack and in-app only, so selecting Teams has no effect, and *Info (all)* is evaluated as *High+*. Use *Medium+* to be notified of the most drifts.
:::

## Related

- [Compliance Engine](./autonomous-compliance.md): the refresh that triggers detection, thresholds and playbooks.
- [Evidence Hub → Freshness](./evidence-hub.md#freshness): see expiring evidence before it becomes drift.
- [Compliance & GRC API](./api.md#compliance-engine): `detect-drift`, `drift-history`, `alert-policies`.
