---
title: "Compliance Engine"
sidebar_label: "Compliance Engine"
sidebar_position: 2
description: "The part that keeps posture current without anyone clicking: 4-hourly evidence-based sync of findings into controls, thresholds and breaches, score trends and a timeline that explains each move, locked controls, evidence expiry, control testing, exceptions and remediation playbooks with a previewed run."
---

# Compliance Engine

The **Compliance Engine** tab is the operations view behind the posture: when the last sync ran and what it changed, which frameworks are below their threshold, how scores have trended and why, which controls are locked by a human, and what the engine is allowed to fix on its own.

**Where:** left navigation → **Compliance Posture** → *Compliance Engine* tab.

![Autonomous Compliance Engine overview: 1,003 controls, 10 frameworks, total syncs, 10 active breaches; sync status, evidence collection and active breaches panels; score changes since last check and recent sync operations](/img/screenshots/compliance/compliance-engine.webp)

The tiles across the top are **Total Controls**, **Frameworks**, **Engine Evidence Items** (a count of items the engine collected, not of controls with evidence), **Total Syncs** and **Active Breaches**. The sub-tabs are *Overview*, *Compliance Trends*, *Breaches*, *Timeline*, *Manual Overrides*, *Evidence Expiry*, *Control Testing*, *Exceptions*, *Engine Exports*, *Remediation* and *Thresholds*.

## What runs on its own

| Job | Cadence | What it does |
| --- | --- | --- |
| **Compliance refresh** | Every **4 hours**, after scans, and on demand | Maps the team's active cloud, Kubernetes and container scan failures to SCF controls by check ID and decides status from evidence; recalculates framework scores; checks thresholds; runs drift detection |
| **Daily snapshot** | 00:05 UTC | Freezes every control's status for the day: the record that answers "what was your posture on 14 March?" |
| **Exception expiry** | Every 12 hours | Expires approved exceptions past their `expires_at` |
| **Compliance → risk sweep** | Hourly | A control that has been *not implemented* or *partial* for more than 24 hours is minted as a system risk in the [Risk Register](../vulnerability-risk/risk-management/risk-register.md) (one per control, deduplicated) |

**Run Now** on this tab triggers the refresh immediately (needs **Manage Assessments**); **Sync** on the API does the same. Syncs are recorded in the **sync history** (controls updated, upgraded, downgraded, frameworks checked), tagged with what started them: *scheduled*, *event* (a scan) or *manual*.

:::note[Two rules the engine never breaks]
1. **A person's status wins.** The engine never changes a status a person set (an override, a status set over the API, an approved exception). New evidence is still linked; if active scan failures contradict a person's *implemented*, the control is flagged as contradicted for review instead of being downgraded.
2. **A failed or empty scan never improves a score.** Status follows evidence: a clean result counts only when the scanner genuinely ran, and a scan with tool failures, or a paused account, leaves status as it was.

See [How control status is decided](./control-status.md) for the full rules.
:::

## Thresholds and breaches

![Compliance Thresholds: current default threshold 70%, set a per-framework or global threshold, custom framework thresholds list](/img/screenshots/compliance/compliance-engine-thresholds.webp)

A **threshold** is the implementation score a framework must hold. The default is **70%** for every active framework; set a stricter one per framework (ISO 27001 at 90 before the certification audit, PCI DSS at 85). The framework list on the *Thresholds* tab is built from your team's active frameworks. Setting thresholds requires the **admin** role.

After every refresh the engine compares each active framework's implementation score (the same score as the Posture page) with its threshold and records a **breach** when it is below, with the gap in points and the **minimum number of controls** that would have to become implemented to close it. If no combination of in-scope controls can reach the threshold, the breach says so.

![Framework Threshold Breaches: soc2, cis_v8, iso_27002, nist_800_53_r5, nist_csf_2 … each with current score, threshold and gap](/img/screenshots/compliance/compliance-engine-breaches.webp)

Breaches surface on the overview (*Active Breaches*), on the *Breaches* sub-tab, as a **Threshold Crossed** drift, and through [alert policies](./drift-detection.md#alert-policies).

## Trends and timeline

![Compliance Score Trends: score per framework over time with a time-range selector](/img/screenshots/compliance/compliance-engine-trends.webp)

**Compliance Trends** plots each framework's implementation score across threshold checks (7 days, 30 days, 90 days or all). **Timeline** lists every check with per-framework score, delta and direction, and explains each move since the previous check by cause: status upgrades, status downgrades, evidence gained, evidence expired, newly assessed, or added to scope (a framework was activated). Sync rows show their trigger and per-cause counts, and the timeline notes any period with no scheduled sync for more than two cadences.

When the scoring method changes between releases, the timeline marks the change point: checks scored with the previous method are labeled and not compared with current ones.

![Compliance Check History timeline entries with framework scores and deltas](/img/screenshots/compliance/compliance-engine-timeline.webp)

## Manual overrides

![Manual Control Overrides: lock a control by SCF ID with a reason; active overrides list with reason, locked time and an Unlock action](/img/screenshots/compliance/compliance-engine-overrides.webp)

This sub-tab lists every control the team has locked, whether from the [posture gap analysis](./compliance-dashboard.md#manual-overrides) or from the **Override a Control** form here, with the reason and when it was locked. **Unlock** removes the lock. Locking and unlocking require the **admin** role and are written to the compliance audit log.

## Evidence expiry

The *Evidence Expiry* sub-tab has two panels:

- **Evidence Expiring Soon**: evidence whose validity ends within the window you choose, with the true total.
- **Proactive Expiry Alerts**: alerts the scheduler raised for evidence expiring within 7, 14 or 30 days. Filter by open or acknowledged, and **acknowledge** an alert once handled.

Expired evidence stops supporting its controls and shows up as an *Evidence Expired* drift. See [Evidence Hub → Freshness](./evidence-hub.md#freshness).

## Remediation playbooks

![Remediation Playbooks (20): Block S3 Public Access, Enable S3 Default Encryption, Remove Open Security Group Ingress, Enable CloudTrail Logging, Disable RDS Public Accessibility, Enable EBS Default Encryption, Strengthen IAM Password Policy, Enable GuardDuty, Restrict GCP Firewall Rules, Restrict Azure NSG Rules …](/img/screenshots/compliance/compliance-engine-remediation.webp)

Twenty cloud-native fixes for the misconfigurations that most often drag a framework down: public S3, unencrypted storage, open security groups, missing CloudTrail or GuardDuty, public RDS, IMDSv1, unused access keys, and their GCP and Azure equivalents. Each playbook carries a **risk level** and **rollback parameters**.

- **Process Active Findings** first runs a dry run and asks you to confirm: "N findings → M new actions (K already pending)". Confirming creates the **remediation actions**. A finding never gets a second open action for the same playbook, so clicking again does not create duplicates.
- Actions from **low-risk playbooks** (10 of the 20) are auto-approved; the rest wait for **Approve** / **Deny**. The person who created an action cannot approve it.
- **Execute** runs the fix; **Rollback** reverts it using the stored parameters. Every step is recorded and exported in the [remediation audit report](./audit-reports.md).

Processing findings and approving, denying, executing or rolling back actions require the **Execute Remediations** permission.

:::warning[Dry run by default]
Execution is a **dry run** unless the platform is started with `REMEDIATION_LIVE_EXECUTE=true`. In dry-run mode actions are planned, approved and logged but no cloud API call is made. Run one full cycle that way and read the audit trail before switching it on.
:::

## Control testing

Auditors distinguish *automated monitoring* from *formal control tests*: a documented test of design or of operating effectiveness, on a cadence, with a recorded result. The *Control Testing* sub-tab keeps that record:

- **Control Test Schedules**: one per control, with the test type (*Design*, *Operating effectiveness* or *Design + operating*), frequency in days and owner (a written procedure can be added over the API). **Seed quarterly schedules** creates a 90-day schedule for every in-scope control; add or edit one with the form, or delete it. *Overdue only* filters the list, and the header counts overdue tests by urgency.
- **Record result** on a schedule: `pass` · `fail` · `exception` · `not_tested`, with notes. Recording a result sets the next due date. Over the API a result can also carry linked evidence, exceptions noted and the management response.
- **Recent Test Results**: the 50 most recent tests.

The [Control test cadence](./compliance-dashboard.md#control-test-cadence) panel on the Posture tab summarizes what is overdue, due in 7 days or never tested.

## Exceptions

When a control cannot be met (a legacy system, a vendor constraint, a cost decision), file an **exception** rather than leaving a red control unexplained. The *Exceptions* sub-tab shows a summary (total, pending, approved, expiring within 14 days), a status filter, and a request form with the SCF control ID, justification, risk impact and expiry date. The API accepts the full record:

| Field | Purpose |
| --- | --- |
| **justification** and **risk_impact** (low · medium · high · critical) | Why, and what it exposes |
| **compensating_controls** | What reduces the risk meanwhile |
| **remediation_plan** and **remediation_target_date** | How and when it will be closed |
| **expires_at** | Exceptions are time-boxed; expired ones are flagged every 12 hours |

An exception moves through **pending_approval → approved / denied**, then **remediated** (**Mark remediated**) or **expired**. The requester cannot approve their own exception. Approving an exception locks the control with a manual override. Requesting and deciding exceptions require **Manage Assessments**.

## Engine Exports

The **Engine Exports** sub-tab produces quick CSV exports of the engine's controls, findings, drift history and remediation status. For formal, attestable reports use the [Audit Reports](./audit-reports.md) module, which this tab links to.

## Related

- [Compliance Posture](./compliance-dashboard.md): the scores this engine maintains.
- [How control status is decided](./control-status.md): evidence rules, person statements and contradictions.
- [Drift Detection](./drift-detection.md): regressions, expired evidence and threshold crossings.
- [Compliance & GRC API](./api.md#compliance-engine): sync, thresholds, overrides, testing, exceptions and remediation over REST.
