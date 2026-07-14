---
title: "Compliance Posture Dashboard"
sidebar_label: "Compliance Posture"
sidebar_position: 2
---

# Compliance Posture Dashboard

The **Compliance Posture** dashboard gives you a single, real-time view of how well your environment meets the frameworks you care about — SOC 2, ISO 27001, NIST CSF, PCI-DSS, CIS, and more. Instead of chasing audit artifacts by hand, it maps your scan findings and assessment answers to a common control library, scores each framework, and flags where your posture has slipped.

![Compliance Posture dashboard showing framework scores and control status](/img/screenshots/compliance-posture.png)

## What it does

Open **Compliance Posture** from the **Compliance & Risk** section of the left navigation. The page is organized into four tabs:

| Tab | What you use it for |
|---|---|
| **Compliance Posture** | The main scoreboard — control totals, per-framework scores, evidence coverage, gap analysis, and control search. |
| **Compliance Engine** | The autonomous engine that maps scan findings to controls and keeps scores current. |
| **Drift Detection** | A timeline of posture regressions and expired evidence, with one-click remediation. |
| **Evidence Hub** | Collect, review, and attach the audit artifacts that back each control. See **[Evidence Hub](./evidence-hub.md)**. |

All data is scoped to your **active team**, so you only ever see the posture for the environment you're working in.

## Reading the scoreboard

The row of tiles at the top of the **Compliance Posture** tab summarizes your overall standing:

- **Total Controls** — the number of unique controls being tracked across your active frameworks.
- **Implemented** — controls confirmed as in place, shown with the percentage of the total. Select this tile to drill into the full list.
- **With Evidence** — controls that have at least one piece of evidence attached. Select to see them.
- **Evidence Items** — the total count of collected evidence artifacts. Select to browse them with their source, linked controls, and frameworks.
- **Dedup Ratio** — how much duplicate effort the platform saved by reusing one piece of evidence across multiple controls and frameworks.
- **Frameworks** — how many frameworks are active out of those available. Select this tile to open the **Framework Activation** panel.

:::tip[Choose the frameworks you report on]
Use the **Framework Activation** panel to turn frameworks on or off. Deactivated frameworks are hidden from the dashboard and scores, but their controls stay in the database — so you can re-enable them later without losing anything. Select **Save Activation** to apply your choices.
:::

## Framework scores

The **Compliance by Framework** panel lists each active framework with a progress bar and a percentage score. Scores are color-coded so you can scan them at a glance:

- **Green** — 70% or higher
- **Amber** — 40–69%
- **Red** — below 40%

The number beside each bar (for example, `42/118`) shows how many controls are covered out of the framework's total. Hover over it for a breakdown of implemented, partial, evidence-only, and not-yet-assessed controls.

### Control status

Each control rolls up into one of these states, which you'll see throughout the dashboard:

| Status | Meaning |
|---|---|
| **Implemented** | The control is satisfied. |
| **Partial** | Partially implemented; some work remains. |
| **Planned** | Acknowledged but not yet in place. |
| **Not Applicable** | Marked out of scope for your environment. |
| **Not Implemented / Not Assessed** | No evidence yet, or known to be missing. |

### Gap analysis

Select any framework bar to open its **Gap Analysis**. This lists the controls that are failing or unaddressed, ranked by a priority weighting (out of 10) so you can tackle the most important gaps first. For each gap you'll see its control ID, name, domain, priority, and current status — plus an **Override** action (see below).

### Searching for controls

Use the **Search Controls** box at the bottom of the tab to find a specific requirement by keyword — for example, `encryption`, `access control`, or `MFA`. Results show each matching control's ID, name, status, and how many frameworks it maps to.

## Attaching and managing evidence

Evidence is what proves a control is genuinely in place. The platform collects most of it for you automatically — cloud configuration scans, vulnerability and container scans, and assessment answers are all mapped to the relevant controls. The **Evidence Sources** and **Evidence per Framework** panels on the right of the dashboard show where your evidence is coming from and how it's distributed.

To collect, upload, or review evidence in detail — including manual uploads and the auditor evidence package — open the **Evidence Hub** tab. See **[Evidence Hub](./evidence-hub.md)** for the full workflow.

### Overriding a control's status

Sometimes a control is satisfied in a way the automated engine can't detect — for example, a compensating control such as a WAF. From **Gap Analysis**, select **Override** on the control to set its status manually:

1. Choose the **New Status** (Implemented, Partially Implemented, Planned, Not Applicable, or Not Implemented).
2. Enter a **Justification** — this field is required.
3. Select **Apply Override**.

:::note[Overrides are tracked]
Every manual override is recorded for audit purposes, and it prevents the autonomous engine from overwriting your decision on the next scan. Always give a clear justification so auditors understand the reasoning.
:::

## Tracking drift

Posture isn't static — a new misconfiguration can break a control that was passing yesterday, or a piece of evidence can age out. The **Drift Detection** tab tracks these changes over time.

- **Control Regression** — a control that was implemented now fails because of a new finding.
- **Evidence Expired** — supporting evidence has passed its validity period and needs refreshing.

Select **Detect Drift** to run a check on demand, or review the history of past drift events. Where a remediation playbook matches a drift type, you can trigger it directly from the event. You can also create **alert policies** to be notified when drift of a chosen type and severity occurs.

:::tip[Keep scores fresh]
The dashboard is populated automatically as scans run and findings are mapped to controls. If a framework shows **No Compliance Data Yet**, run a cloud security scan or complete an assessment checklist, then return here — the engine maps the results to controls for you. Use **Refresh** to pull the latest at any time.
:::

## Related

- **[Compliance & Assessment Overview](./index.md)** — how the whole compliance framework fits together.
- **[Evidence Hub](./evidence-hub.md)** — collect, review, and attach audit evidence.
- **[Interactive Assessments](./interactive-assessments.md)** — guided, auto-scored framework questionnaires.
- **[Autonomous Compliance](./autonomous-compliance.md)** — the engine that maps findings to controls automatically.
- **[Connecting Cloud Accounts](../cloud-security/connecting-accounts.md)** — connect an account so scans can feed your posture.
