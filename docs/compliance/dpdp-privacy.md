---
title: "DPDP Act (India) Privacy"
sidebar_label: "DPDP Act (India)"
sidebar_position: 5
---

# DPDP Act (India) Privacy

The DPDP module operationalizes India's **Digital Personal Data Protection Act, 2023** for your organization: a readiness assessment against the Act's obligations, **Data Protection Impact Assessments (DPIAs)**, **Significant Data Fiduciary (SDF)** obligation tracking, **vendor / data-processor due diligence**, and a full **breach-incident workflow** with the notification deadlines the Act and CERT-In expect — all backed by a tamper-evident audit trail you can export as an audit pack.

![DPDP Compliance module with DPIA, SDF, vendor assessment, and breach management tabs](/img/screenshots/dpdp-compliance.png)

## What it does

- **DPDP readiness assessment** — a control-by-control view of where you stand against the Act, with a readiness score and a ranked list of the top findings to fix first.
- **DPIA lifecycle** — create DPIAs from a built-in template, answer with **AI auto-fill suggestions** drawn from your existing evidence, then route through **submit → approve / reject** so every high-risk processing activity has a documented, signed-off assessment.
- **SDF obligations** — assess whether you qualify as a Significant Data Fiduciary and track the additional obligations (such as appointing a Data Protection Officer and periodic DPIAs) if you do. Assessment history is kept, so you can show how your status evolved.
- **Vendor / data-processor due diligence** — structured questionnaires per vendor, with history per vendor and a **failing-vendors** view so procurement and privacy teams see at a glance which processors need attention.
- **Breach incident workflow** — record an incident, run a structured assessment, and manage the two notification tracks Indian organizations face: the **Data Protection Board (DPB)** and **CERT-In**. The module generates draft report text for both, checks each report for completeness, and tracks **notify-data-principals**, **report-to-DPB**, and **report-to-CERT-In** as explicit steps through to closure (or withdrawal for false alarms).
- **Deadline watchdog** — overdue and approaching-deadline views for both DPB and CERT-In timelines, so a breach never silently misses its reporting window. CERT-In's 6-hour expectation is exactly the kind of clock this exists for.
- **Audit trail & audit packs** — every DPDP action is logged; you can assemble events into a verifiable **audit pack**, export it as PDF, and configure how long audit records are retained.
- **Privacy dashboard** — readiness, open DPIAs, vendor status, and breach posture on one screen.

:::note[Scope of the module]
The module covers readiness, DPIA, SDF, vendor due diligence, breach management, and audit evidence. Consent management and data-principal request handling (access / correction / erasure) are on the product roadmap and not part of the module today.
:::

## How to use it

### 1. Establish your baseline

Open **DPDP** and review the **readiness assessment**. The score is computed from the framework's controls; the **top findings** list tells you which gaps matter most. Treat this as the running scorecard for your DPDP program.

### 2. Determine SDF status

Run the **SDF assessment** from its template. If you qualify as a Significant Data Fiduciary, the module tracks the additional obligations that follow. Re-assess when your processing volumes or data categories change — history is preserved.

### 3. Run DPIAs for high-risk processing

1. Create a DPIA from the template.
2. Answer the questionnaire — use **auto-fill suggestions** to pre-populate answers from evidence the platform already holds, then review and correct them.
3. **Submit** for review; an approver **approves or rejects** with comments.

:::tip[Auto-fill is a draft, not an answer]
Suggestions come from your existing platform evidence and prior assessments. Always review them — the reviewer sign-off is the point of the DPIA.
:::

### 4. Assess your vendors

Send each data processor through the **vendor due-diligence** questionnaire. Check the **failing vendors** view periodically and before renewals.

### 5. Practice the breach workflow before you need it

Create a test incident and walk it through: assessment → CERT-In reportability check → draft DPB and CERT-In report text → completeness checks → close. Confirm the **overdue / approaching-deadline** views behave as expected. When a real incident happens, the workflow — not memory — carries the deadlines.

### 6. Keep the audit trail export-ready

Use **audit packs** to bundle DPDP activity into a verifiable, PDF-exportable package for auditors or the Board, and set the **retention period** for audit events to match your policy.

## Related

- [Compliance & GRC overview](./index.md)
- [Supported frameworks](./supported-frameworks.md)
- [Evidence Hub](./evidence-hub.md)
- [India regulatory readiness](../industries/india-regulatory-readiness.md)
