---
title: "Autonomous Compliance"
sidebar_label: "Autonomous Compliance"
sidebar_position: 1
---

# Autonomous Compliance

Autonomous Compliance keeps your framework status up to date automatically. As scans run across your cloud accounts, containers, code, and other targets, the platform maps each finding to the security controls it affects and recalculates your compliance scores — so what you see always reflects your current posture, not a point-in-time audit.

![Compliance posture with framework scores and control status](/img/screenshots/compliance-posture.png)

## What it does

At the center is a single **common controls registry** of 1,451 controls organized into 33 domains, built on the **Secure Controls Framework (SCF)**. Each control is pre-mapped to the requirements it satisfies across frameworks like **SOC 2, ISO 27001, NIST CSF, PCI-DSS**, and more.

Because one control can satisfy requirements in several frameworks at once, a single security check updates every framework it touches — assess once, comply many. That means you don't maintain a separate checklist per framework; you maintain one set of controls, and the platform translates their status into each framework's scoring for you.

The engine continuously:

- **Maps findings to controls.** New scan findings are matched to the specific controls they affect. When there's no exact control match, a finding is associated with the broader domain it belongs to, so nothing goes uncounted.
- **Updates control status.** As issues appear or get remediated, control status moves automatically between implemented, partial, and not implemented.
- **Recalculates framework scores** so dashboards and reports stay current without anyone re-running an assessment.
- **Detects drift** — when posture slips since the last check — and flags it for review.

## How control status works

Every control sits in one of these states:

| Status | Meaning |
|---|---|
| **Implemented** | The control is satisfied — no open findings indicate a gap. |
| **Partial** | The control is partly satisfied — some evidence or coverage exists, but open findings or gaps remain. |
| **Not implemented** | Open findings show the control is not being met. |
| **Not applicable** | The control doesn't apply to your environment, so it's excluded from scoring (it neither helps nor hurts your score). |
| **Not assessed** | The control hasn't been evaluated yet and counts as not yet earned. |

### How status becomes a score

Each framework's score is a weighted percentage of its in-scope controls:

- **Implemented** counts as full credit (100%).
- **Partial** counts as half credit (50%).
- **Not implemented** and **not assessed** count as no credit (0%).
- **Not applicable** controls are removed from the calculation entirely — they don't drag your score down.

So a framework at, say, 82% means its in-scope controls, weighted this way, add up to 82% of the possible total. Closing findings moves controls toward **implemented** and raises the score; new findings do the opposite.

:::tip Reading pass / fail / partial at a glance
- **Pass (implemented)** → nothing to do; keep the supporting evidence current.
- **Partial** → you're close. Look at the findings or missing evidence linked to the control and close the remaining gap to earn full credit.
- **Fail (not implemented)** → start here. These have open findings actively working against your score and are usually the highest-leverage fixes.
:::

## How to use it

1. **Connect your environment and run scans.** Compliance status is driven by findings, so the more you have connected — cloud accounts, containers, code, assessments — the more complete your picture. See **[Connecting Cloud Accounts](../cloud-security/connecting-accounts.md)**.
2. **Open Compliance Posture.** Pick a framework to see its overall score and the breakdown of controls by status.
3. **Drill into a control.** Open any control to see its status, the frameworks it maps to, and the findings or evidence behind that status.
4. **Work the gaps.** Start with **not implemented**, then **partial**. Remediating the underlying findings updates the control automatically on the next sync — you don't re-grade anything by hand.
5. **Refresh when you need the latest.** Status updates on its own as scans complete. If you want to force an immediate recalculation after making changes, trigger a refresh from the compliance view.

### Drift detection

Between scan cycles, the platform watches for posture slipping and surfaces it as drift, including:

- **Control regression** — a control that was implemented has fallen back to a lower status.
- **Expired evidence** — supporting evidence linked to a control has aged past its freshness window (90 days).
- **New findings in a clean domain** — a domain that was fully compliant now has open findings.
- **Threshold crossed** — a framework's score has dropped below the target you set.

Use drift alerts as your early-warning signal: they tell you a previously passing area needs attention before it shows up in an audit.

### Manual overrides

When you have context the scanners can't see — for example, a compensating control or an accepted exception — you can set a control's status manually. A manually set control is **locked** so automated syncs won't change it based on new findings, until you clear the override.

:::note Keep overrides honest
Manual overrides are powerful but bypass the automation. Use them deliberately, attach evidence where you can, and revisit them periodically so your reported posture stays trustworthy.
:::

:::tip Make sure you're in the right team
Compliance status is scoped to your **active team**. Confirm you're in the correct team (top-right account menu) before reviewing scores or setting overrides, so you're acting on the right environment's data.
:::

## Related

- **[Compliance Dashboard & Reporting](./compliance-dashboard.md)** — executive views and exportable reports built on these scores.
- **[Evidence Hub](./evidence-hub.md)** — gather and link the artifacts that back up each control.
- **[Interactive Assessments](./interactive-assessments.md)** — guided questionnaires that also feed control status.
- **[Connecting Cloud Accounts](../cloud-security/connecting-accounts.md)** — connect the sources that drive findings.
