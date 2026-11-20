---
title: "Compliance Posture"
sidebar_label: "Compliance Posture"
sidebar_position: 1
description: "The live compliance picture: implementation score per active framework, gap analysis down to the control, a Statement of Applicability per framework, manual overrides with justification, framework activation, control test cadence, cloud-check coverage, evidence sources and SCF control search."
---

# Compliance Posture

The **Compliance Posture** tab is the page you open when someone asks "where are we on SOC 2?". It shows every active framework's score, lets you drill from a framework to the exact controls holding it back, and lets you fix the picture where automation cannot see — with a justification that is kept for the auditor.

**Where:** left navigation → **Compliance Posture** → *Compliance Posture* tab.

![Compliance Posture: tiles for total controls (1,046 across 11 active frameworks), implemented, with evidence, evidence items, average controls per item and frameworks (11/27, custom selection); control test cadence; implementation score by framework; evidence sources and evidence per framework](/img/screenshots/compliance/compliance-posture.webp)

## The tiles

| Tile | Meaning | Click |
| --- | --- | --- |
| **Total Controls** | Distinct SCF controls mapped to at least one active framework; a control shared by two frameworks counts once (1,003 of the 1,534-control catalog with the default 10 frameworks) | Drill-down list |
| **Implemented** | Controls at *implemented* and their share of the total. The subtitle also counts implemented controls with open findings, which the score treats as partial. | Drill-down list of implemented controls |
| **With Evidence** | Controls with at least one **current** evidence item (the same count as the Evidence Hub) | Drill-down list |
| **Evidence Items** | Current evidence items (not expired, archived or revoked) linked to a control of the active frameworks | Drill-down list of the items counted |
| **Avg Controls / Item** | Links from current evidence items to active-framework controls ÷ current evidence items with at least one such link: how many controls one artifact supports on average | — |
| **Frameworks** | Platform administrators see active / available (e.g. 10/27) and whether the team uses the *Default set* or a *Custom selection*; other users see the active count | Opens the framework activation panel |

## Compliance by framework

One bar per active framework with its **implementation score** and the inputs it was computed from (for example "33 implemented · 89 partial · 12 evidence-only of 371"). The score is the weighted formula in the [overview](./index.md#how-a-framework-score-is-calculated): implemented 1.0, partial 0.5, evidence-only 0.25, over every in-scope control; an implemented control with open findings counts as partial. A framework with no assessed controls and no evidence-only credit reads *Not Assessed* instead of 0%. Hover the help icon for the definition.

![Implementation score by framework (ISO 27001 94%, ISO 27002 94%, HIPAA 61%, NIST CSF 59%, SOC 2 52%, PCI DSS 51%, ISO 42001 48%) with implemented, partial and evidence-only counts; evidence sources, evidence per framework and SCF domains panels](/img/screenshots/compliance/compliance-posture-frameworks.webp)

**Click a framework** to open its **gap analysis**.

## Gap analysis

![Gap Analysis for PCI DSS 4.0.1: 366 controls, 189 gaps, implementation score 50.8%; search, domain and status filters; one row per control with SCF ID, control name, domain, priority, status and an Override action; page 1 of 10](/img/screenshots/compliance/compliance-gap-analysis.webp)

Every **gap**: an in-scope control (not marked not applicable) that is not implemented with current evidence. That is a control that is not implemented, partial, implemented with open findings, or implemented without current evidence. The header shows the total, the gap count and the implementation score. Each row shows:

- **SCF ID** and **control name**, its **domain** (Asset Management, Continuous Monitoring, Cryptographic Protections, …),
- **Priority** — the SCF weighting (1–10) of the control; sort by it to work on what moves the score most,
- **Status**,
- search by control name or SCF ID, filters by domain and status, 20 / 50 / 100 per page.

The **Override** action on each row opens the manual override dialog.

## Manual overrides

![Manual Override dialog for CFG-02 Secure Baseline Configurations (current: partial): new status Implemented and a required justification, with Apply Override](/img/screenshots/compliance/compliance-override.webp)

Scans can prove that a bucket is encrypted; they cannot prove that the board approved the security policy. For controls satisfied by a document, a committee or a process, set the status yourself:

1. Choose the **new status**: Implemented, Partially Implemented, Planned, Not Applicable or Not Implemented.
2. Write the **justification** (required) — where the evidence lives, who approved it, when it is reviewed.
3. **Apply Override.**

An overridden control is **locked**: the 4-hourly sync, assessment mapping, scan correlation and evidence collectors still attach evidence to it but never change its status. If active scan failures contradict an *implemented* override, the control is flagged as contradicted for review (see [How control status is decided](./control-status.md)). The override, the justification and who set it are written to the compliance audit log, and the control appears under Compliance Engine → [Manual Overrides](./autonomous-compliance.md#manual-overrides), where it can be unlocked. Overrides require the **admin** role.

:::tip[Override the whole story, not one row]
Setting *GOV-01 Information security programme* to implemented is not a shortcut to a green ISO 27001 — but the handful of governance, HR and business-continuity controls that no scanner can observe typically account for 10–15 points of a framework score. Do them once, with justifications an auditor can follow, and keep the rest automated.
:::

## Framework activation

![Framework activation panel: 11 of 27 frameworks active, a toggle per framework with its control count, Activate All / Deactivate All, who last changed the set, and Save Activation](/img/screenshots/compliance/compliance-frameworks-panel.webp)

The **Frameworks** tile opens the activation panel. Active frameworks determine what is counted everywhere: tiles, scores, thresholds, evidence per framework, audit reports and the executive dashboard. Activation is **per team**. A team that has not saved its own selection uses the default set of ten (ISO 27001, ISO 27002, SOC 2, PCI DSS 4.0.1, NIST CSF 2.0, NIST 800-53 r5, CIS v8.1, HIPAA, GDPR, OWASP Top 10); activate others from the [27-framework catalog](./supported-frameworks.md) as you need them.

Changing activation requires a **platform administrator**. Only frameworks in the catalog can be activated. Every change is written to the audit log, and the panel shows who last changed the framework set and when.

## Control test cadence

Formal control testing (*test of design*, *test of operating effectiveness* or both) on a schedule, separate from automated scans. The panel shows **scheduled tests**, **overdue**, **due in 7 days** and **never tested**, with the overdue list; it stays quiet until the team has schedules. Create schedules and record results on Compliance Engine → *Control Testing*. See [Control testing](./autonomous-compliance.md#control-testing).

## Statement of Applicability

Selecting a framework also opens its **Statement of Applicability**: one row per requirement of the standard (for ISO 27001, clauses 4–10 and the 93 Annex A controls), rolled up from the mapped SCF controls. Each row shows whether the requirement applies, its status, the controls and evidence behind it, and a justification. Summary tiles count requirements, applicable, not applicable, with evidence, and not-applicable rows without a justification.

Users with **Manage Assessments** can edit a requirement's justification; everything else is derived from the control registry. **Download SoA (XLSX)** exports the auditor-facing spreadsheet.

## What cloud checks can and can't evidence

This panel shows, per cloud provider, how many Prowler checks have a **reviewed mapping** to SCF controls (a pass can mark a control implemented), a **derived** mapping (gaps only: a fail records a gap, a pass earns no credit), or none, with the reason each unmapped check is unmapped. See [How control status is decided](./control-status.md#reviewed-and-derived-mappings).

## Evidence sources, evidence per framework, SCF domains

- **Evidence Sources**: where the evidence store's items came from, for example Prowler (cloud), container and Kubernetes scans, cloud API captures, Wazuh, manual uploads, assessment answers and policy acknowledgements.
- **Evidence per Framework**: distinct current evidence items linked to each active framework's controls; inactive frameworks are collapsed.
- **SCF domains (34)**: the catalog's domains; the [Evidence Hub](./evidence-hub.md) breaks coverage down by these.
- **Search controls**: text search across the SCF catalog (control name, SCF ID, description), filterable by framework and domain; each result shows its status for your team and the frameworks it maps to.

## Related

- [Compliance Engine](./autonomous-compliance.md) — sync, thresholds, breaches, overrides list, control testing, exceptions.
- [How control status is decided](./control-status.md) — why a control has its status.
- [Drift Detection](./drift-detection.md) — what regressed since yesterday's snapshot.
- [Compliance & GRC API](./api.md#controls-and-posture) — posture, gap analysis and overrides over REST.
