---
title: "DPDP Act (India)"
sidebar_label: "DPDP Act (India)"
sidebar_position: 7
description: "A beta module for India's Digital Personal Data Protection Act 2023 and Rules 2025 plus CERT-In directions: readiness against 22 rule-level controls with the penalty provisions at risk, DPIAs with maker-checker approval, Significant Data Fiduciary classification, vendor (processor) due diligence, breach records with the 72-hour DPB and 6-hour CERT-In clocks, and a sealed, verifiable audit pack."
status: beta
---

# DPDP Act (India)

The Digital Personal Data Protection Act is enforced per **rule**, with penalties up to **₹250 crore** for failing to take reasonable security safeguards. The DPDP module maps the platform's controls onto those rules, runs several of the workflows the Rules require (impact assessments, processor due diligence, breach records) and produces the audit record a Data Protection Board inquiry would ask for.

:::note[Beta: not every obligation has a workflow]
The module is marked beta in the product. It does not include a personal-data inventory, consent and notice management, or a workflow for Data Principal requests (access, correction, erasure, grievances). Those obligations appear only as controls in the catalog: keep their records in your own systems and attach evidence in the [Evidence Hub](./evidence-hub.md). Breach notices and regulator filings are **recorded** here, not sent.
:::

**Where:** left navigation → **DPDP Compliance**.

![DPDP Compliance overview: readiness 18.2% (4 of 22 controls implemented), 9 penalty provisions at risk with the highest ceiling ₹250 Cr, 2 active breaches, 0 overdue reports, 2 in reportability triage, SDF status SDF; controls the platform cannot assess](/img/screenshots/compliance/dpdp-overview.webp)

## Overview

| Tile | Meaning |
| --- | --- |
| **DPDP Readiness** | Share of applicable DPDP controls at *implemented* (19 controls for a regular fiduciary, 22 once you are a Significant Data Fiduciary), and the share of the controls the platform can assess |
| **Penalty Provisions at Risk** | How many penalty provisions of the Act have unmet controls, with the highest ceiling. Ceilings are per provision and **not additive**. |
| **Active Breaches** | Open incidents (not closed or withdrawn) |
| **Overdue Reports** | Incidents past the DPB (72 h) or CERT-In (6 h) deadline |
| **Reportability Triage** | Incidents past their window with the reportability decision still open |
| **SDF Status** | *SDF*, *Non-SDF*, or *Unclassified* until the [SDF questionnaire](#sdf-classification) is completed (scored as non-SDF until then) |

Below the tiles:

- **Controls the platform can't assess**: applicable controls with no scanner or workflow evidence in the platform. They stay *not assessed*, so readiness cannot reach 100% from telemetry alone; keep your own evidence for them.
- **Penalty Provisions with Unmet Controls**: one row per provision (for example Section 8(5) security safeguards, ₹250 Cr; Section 8(6) breach notification, ₹200 Cr; Section 10 SDF obligations, ₹150 Cr; other provisions, ₹50 Cr) with its unmet controls. These are the maximum penalties in the Act's Schedule; the Board decides any actual penalty, and they are not an exposure estimate or legal advice.
- The **priority findings** to fix next, the team's **DPIAs**, **vendor compliance** and the full **control status breakdown**.

## Controls

![DPDP control catalog (22 controls): search, obligation-type and control filters; ID, title, rule, type, penalty (₹ Cr), SDF-only flag and enforcement date for each rule-level control](/img/screenshots/compliance/dpdp-controls.webp)

The 22 DPDP controls are **rule-level requirements** — Rule 6 security safeguards (a)–(g), Rule 7 breach intimation and reporting, Rule 8 retention and erasure, DPO contact and grievance redressal, the Significant Data Fiduciary duties (DPO appointment, independent audits, DPIAs), Data Principal rights (access, correction, grievance) and cross-border transfer — each mapped to the SCF controls that implement it. Status is derived from those SCF controls with a deliberately conservative **worst-link rule**:

- any mapped control *not implemented* → the DPDP control is **not implemented**;
- else any *partial* or *planned* → **partial**;
- else any *not assessed* → **not assessed**;
- all *implemented* → **implemented**; *not applicable* controls are excluded.

Enforcement is not fractional — nine of ten controls in place still means the rule is not met — so the module under-claims rather than surprises you at inquiry. Improve a DPDP control by improving its SCF controls on the [posture page](./compliance-dashboard.md): scans, assessments or a manual override with justification.

## DPIA

![Data Protection Impact Assessments: Fraud scoring on card transactions (Payments API), 12% complete, draft; Customer KYC onboarding (Customer Portal), 100% complete, in review; New DPIA](/img/screenshots/compliance/dpdp-dpia.webp)

A **DPIA** is required for high-risk processing (and for every processing activity of a Significant Data Fiduciary). Each DPIA covers one **processing activity** through eight sections — description, necessity and proportionality, legal basis (consent or Section 7 legitimate use), data flows and storage, risks to Data Principals with inherent severity, mitigations (technical / organisational / procedural), residual risk, and approval with a review cadence. Required questions drive the **completeness** percentage.

**Autofill suggestions** pre-populate questions from what the platform knows (processing locations from cloud regions, processors from vendor assessments, technical mitigations from control status) and are tagged as *auto* until a human confirms them.

Workflow: **draft → in review** (Submit) **→ approved** (with a validity period, 365 days by default) or **rejected** with a reason. The author or submitter of a DPIA cannot approve it. Approvals are recorded with who and when; an expired DPIA shows on the overview.

## SDF classification

![Significant Data Fiduciary classification: current classification Likely SDF (score 11, formula v1.0); auto-fill suggestions from platform data; volume tier, sector and data-category questions](/img/screenshots/compliance/dpdp-sdf.webp)

The Act lets the Government designate **Significant Data Fiduciaries**, who carry extra duties (DPO in India, independent audits, mandatory DPIAs). The thresholds are not yet prescribed, so the module scores the factors the Act names — **volume tier** of Data Principals, **sector** (BFSI, healthcare, telecom, government, edtech, e-commerce, …), sensitive **data categories** (financial, health, biometric, children, government ID, …), **cross-border** processing, **automated decision-making** and **children's data at scale** — into a versioned score:

| Result | Score | Posture |
| --- | --- | --- |
| **Likely SDF** | ≥ 8 | Behave as designated: the three SDF-only controls become applicable and readiness is recalculated |
| **Possible SDF** | 4–7 | Prepare — designation is plausible |
| **Unlikely SDF** | < 4 | Monitor; reassess when processing scales |

Every assessment is kept in the **history** with the formula version, so a later change in thresholds is auditable.

## Vendor assessment

![Vendor assessments (DPDP Section 8 / Rule 6): FaceSure Technologies — conditional pass, CloudMail Relay — passing, both expiring 11/1/2027; Assess Vendor](/img/screenshots/compliance/dpdp-vendors.webp)

A fiduciary remains responsible for its **processors**. The vendor questionnaire has **18 questions** across encryption, access control, logging, backups, incident handling, sub-processors, data location, erasure, audit rights and HR security; answer each **pass / partial / fail / not assessed** with notes.

| Verdict | Rule |
| --- | --- |
| **Not assessed** | Fewer than 10 questions answered |
| **Failing** | Any **critical** question fails (encryption at rest / in transit, and the other critical items), or more than 2 non-critical failures |
| **Conditional pass** | Any non-critical failure, or more than 2 partial answers — remediation expected |
| **Passing** | Every critical question answered *pass*, no failures, at most 2 partials |

Assessments carry a **validity** (365 days by default); the history per vendor shows how a processor has trended. **Vendor failing** feeds the overview and the audit pack.

## Breach management

![Breach Incident Management (Rule 7): two incidents with detection source, detected time, status (detected, declared), DPB 72 h and CERT-In 6 h clocks with reportability state; Report Incident](/img/screenshots/compliance/dpdp-breach.webp)

Two clocks start when something goes wrong, and they start at different moments:

| Regime | Deadline | Clock starts |
| --- | --- | --- |
| **DPDP Rule 7(1)(b)** — report to the Data Protection Board | **72 hours** | When the incident is **declared** a personal-data breach |
| **CERT-In Directions 2022** — report to CERT-In (for the incident categories in Annexure I) | **6 hours** | When the incident is **detected** |
| **DPDP Rule 7(1)(a)** — intimate affected Data Principals | Without delay | On declaration |

The workflow enforces the order the Rules imply:

1. **Report Incident** — detection time, source, evidence references. Status **detected**.
2. **Declare** it a breach with the basis (or **withdraw** a false alarm). Status **declared**; the DPB clock starts.
3. Fill the **assessment**: nature, extent, timing and location; likely consequences; mitigation; data and record categories with counts; cause and remedial steps; responsible officer; affected systems. Then **Assess**: reportable to DPB? to CERT-In (which Annexure I category)? Status **assessed**.
4. **Record DP Notification** (channels used, summary), **Record CERT-In Filing** and **Record DPB Filing**. The module does not send these: you notify and file through the regulator's own channels, then record the filing here. It refuses to record a report until every field the regulation lists (Rule 7(2)(1)–(9) for the Board, Annexure I for CERT-In) is present, and generates the **report text** for you to submit.
5. **Close** with closure notes. Closing is blocked while a required report is unfiled or the CERT-In reportability decision is still open.

Records are protected once filed: a report cannot be re-filed, the Rule 7(2) assessment cannot be edited after the DPB filing (CERT-In-only fields stay editable until the CERT-In filing), reportability cannot be flipped after filing, and an incident cannot be withdrawn once any report or notification has been recorded. The filing actor is the signed-in user.

The **triage** views list incidents whose reportability decision is pending; the **approaching** and **overdue** views watch both clocks, and the breach list shows 72 h and 6 h countdowns. **Auto-detection** is off by default (`DPDP_BREACH_AUTODETECT_ENABLED=false`); when an administrator enables it, critical and high platform alerts that look like data exposure become *candidate* incidents in **detected** status. It never declares, so no legal clock starts without a human, and a false positive is simply withdrawn.

## Audit & export

![Audit & Export: retention policy (730 days, residency india), generate an audit pack for a period with Verify integrity and Download PDF, and the recent DPDP audit events](/img/screenshots/compliance/dpdp-audit.webp)

Every DPDP action (a DPIA approved, a vendor assessed, a breach declared, a report recorded) is written to the **DPDP audit event log**. An **audit pack** is an export, for a period you select, of those events plus the module's state at period end (readiness, SDF classification, DPIA and vendor summaries), persisted in full as an immutable record and downloadable as PDF.

Packs are sealed with an **HMAC-SHA256** under a server-held key, so someone with database access cannot reseal an altered pack. **Verify integrity** recomputes the seal and reports the reason when it fails, distinguishing tampering, a pack from an earlier format (plain SHA-256), and a pack sealed under a different key. The key is `DPDP_AUDIT_SIGNING_KEY`, or one derived from the platform's `SECRET_KEY` when that is unset; rotating it makes older packs report "signed under a different key". A pack whose stored events are incomplete is refused rather than served.

The **retention policy** enforces the Rule 8(3) floor of **365 days** for processing logs (set longer, never shorter) and records data residency.

## Related

- [Compliance Posture](./compliance-dashboard.md) — the SCF controls behind each DPDP rule.
- [India regulatory readiness](../industries/india-regulatory-readiness.md) — DPDP alongside RBI, SEBI CSCRF and CERT-In.
- [Compliance & GRC API](./api.md#dpdp) — readiness, DPIA, SDF, vendor, breach and audit endpoints.
