---
title: "AI Governance"
sidebar_label: "AI Governance"
sidebar_position: 3
---

# AI Governance

AI Governance gives you one place to inventory the AI systems your organization builds or uses, classify them against the **EU AI Act** risk tiers, run structured risk assessments, and keep the controls and evidence that regulators expect. Significant AI risks feed into the same **Risk Register** you use for the rest of your security program, so AI doesn't sit in a silo.

![AI Governance dashboard](/img/screenshots/ai-governance.png)

## What it does

- **AI system registry** — a living catalog of your models and AI systems, each with an owner, use case, data sources, deployment stage, and lifecycle status.
- **EU AI Act risk-tier classification** — answer a few questions about a system and the platform places it in the correct tier (**prohibited**, **high-risk**, **limited-risk**, or **minimal-risk**) and tells you what that means.
- **Guided risk assessments** — a step-by-step wizard for assessing a system against a framework (such as **NIST AI RMF** or the EU AI Act), scoring risk, and attaching evidence.
- **Fundamental Rights Impact Assessment (FRIA)** — for high-risk systems, a structured assessment covering human dignity, privacy and data protection, non-discrimination, and the rights of children.
- **Operational monitoring** — fairness/bias testing, privacy (PII) scanning, data-quality checks, AI incident logging, and human-oversight records.
- **Risk Register integration** — AI systems and their assessments surface alongside your other risks, with treatment and review built in.

Supported regulatory frameworks include the **EU AI Act**, **NIST AI RMF**, US AI regulations, and India's **DPDP Act 2023**.

## How to use it

### 1. Register an AI system

1. Open **AI Governance** from the left navigation (or the AI Governance quick-action card on the Dashboard).
2. Select **Register** (or **Add AI System / Model**) and fill in the details:
   - **Name**, **description**, and **owner** (required).
   - **Type** — for example machine learning or generative AI.
   - **Use case**, **data sources**, **business unit**, and **deployment status** (development, staging, production, and so on).
   - Optional **last assessment** and **next review** dates.
3. Save. The system is added to your registry with a lifecycle stage of *registered* and a compliance status of *pending assessment*.

:::tip[Start with what's in production]
Register customer-facing and decision-making systems first — these are the ones most likely to fall into a higher EU AI Act tier and to need governance controls soonest.
:::

### 2. Classify it under the EU AI Act

Run the EU AI Act classification to find out where a system sits. The platform looks at the **use case**, **sector**, **whether it makes or supports decisions**, and **whether it interacts directly with people**, then assigns one of four tiers:

| Tier | What it means | Enforcement date |
|---|---|---|
| **Prohibited** | Uses banned under the Act (for example social scoring, mass surveillance, subliminal manipulation). | 2 Feb 2025 |
| **High-risk** | Systems in sensitive sectors (critical infrastructure, education, employment, healthcare, law enforcement) or making high-stakes decisions (hiring, loan approval, medical diagnosis). | 2 Aug 2026 |
| **Limited-risk** | Systems that interact with people and require transparency (for example chatbots). | 2 Aug 2025 |
| **Minimal-risk** | Everything else; voluntary best practices apply. | No specific timeline |

For each result you also get the **compliance requirements** for that tier (such as conformity assessment, CE marking, FRIA, quality-management system, and post-market monitoring for high-risk systems), the **immediate next steps**, an **effort and timeline estimate**, and a short **rationale** explaining the classification.

:::note[High-risk systems need a FRIA]
If a system lands in the high-risk tier, complete a **Fundamental Rights Impact Assessment** from the same module. It walks you through human dignity, privacy and data protection, non-discrimination, and the rights of children.
:::

### 3. Run a risk assessment

Use the assessment wizard to produce a documented, scored assessment:

1. **Scope & setup** — choose the assessment type and framework (for example NIST AI RMF) and record the assessor.
2. **Risk categories** — pick the categories that apply (such as transparency or robustness); each comes with guidance on how to assess it and what evidence to collect.
3. **Evidence** — attach supporting documents or link automated test results.
4. **Risk scoring** — for each category, set **likelihood** and **impact** on a 1–5 scale with a rationale. The platform computes an **inherent risk score** (likelihood × impact) and, after you factor in control effectiveness, a **residual risk score**.
5. **Review & submit** — review the results and submit. The assessment generates structured findings and remediation tasks you can track to completion.

Scores roll up into familiar risk levels: **Critical**, **High**, **Medium**, and **Low**.

### 4. Track governance controls and operations

For production systems, use the operational tools to keep evidence current:

- **Fairness / bias testing** — checks such as the 80% (disparate-impact) rule, demographic parity, and equal opportunity across protected groups.
- **Privacy (PII) scanning** — detects personal data (emails, phone numbers, and similar) in datasets.
- **Data-quality checks** — completeness, accuracy, consistency, and uniqueness.
- **AI incident tracking** — log AI-specific issues such as performance degradation, security incidents, or ethical concerns.
- **Human oversight** — record where a human reviewed or overrode an AI recommendation, with the reason, to evidence "human-in-the-loop" controls.

### 5. See AI risk in the Risk Register

You don't manage AI risk separately from everything else. Registered AI systems and their assessments surface as governance items scoped to your active team and, like other findings on the platform, can be promoted into the **Risk Register** for treatment, ownership, and review. This follows the platform's **Scan → Finding → Risk → Report** flow, so an AI risk is tracked, reported on, and closed out the same way a cloud misconfiguration or vulnerability is.

:::tip[Team scoping]
AI systems, assessments, and evidence belong to your **active team**. Switch to the correct team before registering systems or running assessments so the records — and any risks they raise — land in the right place.
:::

## Related

- [AI & Threat Intelligence overview](./index.md)
- [Security Command Center (AI-SOC)](./ai-soc-agents.md)
- [Threat Intelligence & Feeds](./threat-intelligence.md)
