---
title: "Compliance & GRC"
sidebar_label: "Overview"
sidebar_position: 0
---

# Compliance & GRC

Offload Security turns your live security findings into **audit-ready compliance posture**. Instead of chasing evidence at audit time, you get a continuously updated view of where you stand against the frameworks you care about — with every control backed by the scans, assessments, and documents that prove it.

![Compliance posture across frameworks with control status and scores](/img/screenshots/compliance-posture.png)

## What it does

Compliance & GRC continuously maps your technical findings to a common set of controls, scores your posture per framework, and flags when something slips.

- **Tracks the frameworks you report against.** Out of the box the platform maps your posture to:
  - **SOC 2** (AICPA Trust Services Criteria)
  - **ISO 27001:2022**
  - **NIST CSF 2.0**
  - **PCI DSS 4.0.1**
  - **CIS Controls v8.1**
  - **HIPAA**
  - **EU GDPR**
- **One control, many frameworks.** Controls are built on the **Secure Controls Framework (SCF)**, so a single check — for example, "data at rest is encrypted" — can satisfy the matching requirement in SOC 2, ISO 27001, NIST CSF, and more at the same time. You evaluate a control once and see credit everywhere it applies.
- **Scores your posture automatically.** Each control rolls up into a framework score from 0–100% so you can see readiness at a glance and track it over time.
- **Detects drift.** When a previously satisfied control regresses — because a new scan finding appeared or supporting evidence expired — the platform flags it so you can act before your next audit, not during it.
- **Collects evidence as you go.** Findings, assessment answers, and uploaded documents are linked to the controls they support, building your evidence trail continuously.

## How control status works

Every control carries a status, and that status drives your framework score:

| Status | Meaning | Counts toward score as |
|---|---|---|
| **Implemented** | The control is fully in place and evidenced. | 100% |
| **Partial** | Partially implemented or only partly evidenced. | 50% |
| **Not Implemented** | Required but not yet in place. | 0% |
| **Not Applicable** | Out of scope for your environment. | Excluded from the score |
| **Not Assessed** | Not yet evaluated. | Excluded from the score |

:::note How the score is calculated
A framework score reflects only the controls that are **in scope** — controls marked *Not Applicable* or *Not Assessed* are left out of the math, so your percentage reflects real, evaluated coverage rather than being diluted by items that don't apply to you.
:::

## How findings map to controls

The platform keeps your posture current by connecting day-to-day security activity to the right controls:

1. **A scan or check runs** — for example, a cloud posture scan reports that a database isn't encrypted.
2. **The finding is matched to the controls it affects**, using the SCF mappings and the subject of the finding (such as encryption, access management, or logging).
3. **Control status updates automatically.** A passing result moves the control toward *Implemented*; a failing result can move it to *Partial* or *Not Implemented*.
4. **Scores and evidence refresh** so your framework readiness — and the evidence behind each control — always reflects your current environment.

## How to use it

1. Open **Compliance** from the left navigation to land on your compliance posture.
2. **Pick a framework** to see its overall score and the status of each control within it.
3. **Drill into a control** to review its current status, the frameworks it maps to, and the linked evidence (findings, assessment answers, or documents).
4. **Work the gaps.** Sort or filter to controls that are *Not Implemented* or *Partial*, and use the linked findings to drive remediation.
5. **Override where automation can't see the full picture.** For controls satisfied by a process or document rather than a scan, set the status manually. A manual status is **locked** so the automated sync won't overwrite it.
6. **Re-check after changes.** As scans re-run and you add evidence, statuses and scores update on their own — and any regression is surfaced as drift.

:::tip Lock controls you've judged manually
Use a manual override for controls that depend on policy or human review. The platform respects your decision and won't auto-change a locked control, while still tracking everything else automatically.
:::

:::warning Watch for drift
A control can fall out of compliance without anyone touching it — a new misconfiguration appears, or a piece of evidence ages out. Review drift alerts regularly so your reported posture stays accurate between audits.
:::

## Prerequisites

- **Connect your environment first.** The more you scan — cloud accounts, containers, Kubernetes, code, and web apps — the more controls update automatically from real findings. See **[Connecting Cloud Accounts](../cloud-security/connecting-accounts.md)**.
- **Compliance roles.** Driving assessments and evidence is typically done by a **Compliance Officer**, while **Auditors** and **Viewers** have read-only access. See your team's roles in **[Getting Started](../getting-started.md)**.

## Related

- **[Interactive Assessments](./interactive-assessments.md)** — guided questionnaires that feed control status and evidence.
- **[Evidence Hub & Collection](./evidence-hub.md)** — where automated and uploaded evidence is gathered and linked to controls.
- **[Autonomous Compliance Engine](./autonomous-compliance.md)** — how findings are continuously synced to controls.
- **[Executive Compliance Dashboard & Reporting](./compliance-dashboard.md)** — leadership-level scores, trends, and audit reports.
- **[Getting Started](../getting-started.md)** — sign in, teams, roles, and the Scan → Finding → Risk → Report flow.
