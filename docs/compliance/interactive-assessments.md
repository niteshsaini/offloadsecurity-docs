---
title: "Interactive Assessments"
sidebar_label: "Assessments"
sidebar_position: 3
---

# Interactive Assessments

Assessments turn long compliance and security-maturity questionnaires into guided, auto-scored evaluations. You pick a framework, work through its requirements question by question, and let the platform pre-fill answers from your scan data and earlier assessments. As you answer, scores update in real time — so you always know where you stand and what's left to do.

![Running a guided assessment with auto-scoring](/img/screenshots/assessments.png)

## What it does

- **Guided, multi-framework questionnaires.** Run a structured assessment against an industry framework and answer each requirement with a simple Yes / Partially / No / Not Applicable.
- **Auto-fill from your data.** The platform suggests answers based on previous assessments and automated scan findings, with a confidence level so you can review before accepting ("assess once, comply many").
- **Real-time scoring.** Category and overall scores recalculate as you answer, and progress is tracked to completion.
- **Evidence on every answer.** Attach supporting evidence, an explanation, and notes to each requirement so the result is audit-ready.
- **Exportable results.** Produce a PDF report of the completed assessment for auditors and stakeholders.

### Supported frameworks

You can start an assessment for any of these:

| Framework | What it covers |
|---|---|
| **OWASP ASVS 5.0** | Application Security Verification Standard — 345 requirements, with verification levels 1–3. |
| **OWASP SAMM 2.0** | Software Assurance Maturity Model. |
| **NIST SSDF 1.1** | Secure Software Development Framework. |
| **NIST CSF 2.0** | Cybersecurity Framework 2.0. |
| **DevSecOps Maturity** | Unified DevSecOps maturity model with industry benchmarks. |
| **OWASP API Security Top 10** | API security risk assessment. |
| **ISO 27001:2022** | Information Security Management System controls. |
| **SOC 2 Type II** | Trust Services Criteria. |
| **Insider Threat** | Insider Threat Management framework. |
| **Security Operations & Resilience** | SecOps and resilience maturity. |

## How to use it

### 1. Start an assessment

1. Go to **Compliance → Assessments**.
2. Select **Create Assessment** (or the create button) to open the setup wizard.
3. Choose the **framework** you want to assess against.
4. Set any framework-specific options the wizard offers — for example, the **verification level** for OWASP ASVS or the **scope** for SAMM — then confirm.

The platform builds the questionnaire and opens it at **Not Started**. As soon as you answer the first question, it moves to **In Progress**.

### 2. Answer the questions

Work through the requirements, grouped by category. For each one:

1. Read the requirement (use the inline help for a fuller description if you need it).
2. Choose a response:
   - **Yes** — fully implemented (counts as full credit).
   - **Partially** — partially implemented (counts as half credit).
   - **No** — not implemented (no credit).
   - **Not Applicable** — doesn't apply; excluded from the score so it never penalizes you.
3. Optionally add an **explanation** and **notes** to record context.

Your progress bar and scores update with every answer.

### 3. Use auto-fill to save time

Instead of answering everything by hand, let the platform propose answers:

- Trigger **auto-fill** to have the platform suggest responses based on your **previous assessments** and **automated scan findings**.
- Each suggestion comes with a **confidence level** (for example, high or medium) and a short reason, so you can review and accept or adjust it rather than taking it blindly.

:::tip[Assess once, comply many]
Because frameworks share common controls, answering a requirement in one assessment can pre-fill the equivalent requirement elsewhere. The more scans you run and assessments you complete, the more the platform can fill in for you.
:::

### 4. Attach evidence

Strengthen each answer with evidence:

- Add evidence directly to a question to back up your response.
- The platform can also **collect evidence automatically** from your scan results, cloud configuration, and risk data and link it to relevant requirements, so you don't have to gather everything manually.
- Collected evidence is tagged by type (such as a scan result, configuration, or policy) and may carry a quality score to help you judge how strong it is.

### 5. Complete and export

1. When every applicable question is answered, the assessment reaches **Completed** and finalizes its scores. You can also mark it complete from the assessment view.
2. Review the **results** — overall score, category breakdown, and maturity rating.
3. Select **Export PDF** to download a shareable report of the completed assessment.

## Tips & prerequisites

:::note[Permissions]
Creating assessments and submitting answers requires the **assessment management** permission (for example, the **Compliance Officer** or **Admin** role). Read-only roles can view results but not change answers.
:::

:::tip[Run scans first]
Auto-fill and automated evidence are only as good as the data behind them. Connect your cloud accounts and run your scans **before** starting an assessment so there's real data to draw on.
:::

:::warning[Not Applicable vs. No]
Use **Not Applicable** only when a requirement genuinely doesn't apply — it's removed from scoring entirely. Marking something **No** keeps it in the score as a gap, which is what you want for controls you simply haven't implemented yet.
:::

## Related

- [Compliance Posture](./compliance-dashboard.md) — track framework control status across your environment.
- [Evidence Hub & Collection](./evidence-hub.md) — manage and reuse the evidence behind your assessments.
- [Common Controls Registry & Autonomous Compliance](./autonomous-compliance.md) — how shared controls power "assess once, comply many."
