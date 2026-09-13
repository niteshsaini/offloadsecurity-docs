---
title: "DPDP Act (India)"
sidebar_label: "DPDP Act (India)"
sidebar_position: 7
description: "A dedicated module for India's Digital Personal Data Protection Act 2023 and Rules 2025 plus CERT-In directions — readiness against 22 rule-level controls with penalty exposure, DPIAs with approval, Significant Data Fiduciary classification, vendor (processor) due diligence, breach management with the 72-hour DPB and 6-hour CERT-In clocks, and a hash-verified audit pack."
---

# DPDP Act (India)

The Digital Personal Data Protection Act is enforced per **rule**, with penalties up to **₹250 crore** per breach of the security-safeguards rule. The DPDP module maps the platform's controls onto those rules, runs the privacy workflows the Rules require (impact assessments, processor due diligence, breach reporting) and produces the audit record a Data Protection Board inquiry would ask for.

**Where:** left navigation → **DPDP Compliance**.

![DPDP Compliance overview: readiness 36.4% (8 of 22 controls implemented), penalty exposure ₹650 Cr, 2 active breaches, SDF status Likely SDF; priority findings; DPIAs; vendor compliance; control status breakdown](/img/screenshots/compliance/dpdp-overview.webp)

## Overview

| Tile | Meaning |
| --- | --- |
| **DPDP readiness** | Share of applicable DPDP controls at *implemented* (19 controls for a regular fiduciary, 22 once you are a Significant Data Fiduciary) |
| **Penalty exposure** | The statutory penalty ceilings (₹250 Cr security safeguards, ₹200 Cr breach notification, ₹50 Cr other) attached to rules whose controls are **not implemented** |
| **Active breaches** | Open incidents, with the count overdue for the Data Protection Board (DPB) and CERT-In |
| **SDF status** | Result of the latest [SDF classification](#sdf-classification) |

Below the tiles: the **priority findings** to fix next (by penalty), the team's **DPIAs**, **vendor compliance** and the full **control status breakdown**.

## Controls

![DPDP controls: rule, type, penalty, SCF mapping and status for each of the 22 rule-level controls](/img/screenshots/compliance/dpdp-controls.webp)

The 22 DPDP controls are **rule-level requirements** — Rule 6 security safeguards (a)–(g), Rule 7 breach intimation and reporting, Rule 8 retention and erasure, DPO contact and grievance redressal, the Significant Data Fiduciary duties (DPO appointment, independent audits, DPIAs), Data Principal rights (access, correction, grievance) and cross-border transfer — each mapped to the SCF controls that implement it. Status is derived from those SCF controls with a deliberately conservative **worst-link rule**:

- any mapped control *not implemented* → the DPDP control is **not implemented**;
- else any *partial* or *planned* → **partial**;
- else any *not assessed* → **not assessed**;
- all *implemented* → **implemented**; *not applicable* controls are excluded.

Enforcement is not fractional — nine of ten controls in place still means the rule is not met — so the module under-claims rather than surprises you at inquiry. Improve a DPDP control by improving its SCF controls on the [posture page](./compliance-dashboard.md): scans, assessments or a manual override with justification.

## DPIA

![Data Protection Impact Assessments: list with completeness and status (draft, in_review); New DPIA](/img/screenshots/compliance/dpdp-dpia.webp)

A **DPIA** is required for high-risk processing (and for every processing activity of a Significant Data Fiduciary). Each DPIA covers one **processing activity** through eight sections — description, necessity and proportionality, legal basis (consent or Section 7 legitimate use), data flows and storage, risks to Data Principals with inherent severity, mitigations (technical / organisational / procedural), residual risk, and approval with a review cadence. Required questions drive the **completeness** percentage.

**Autofill suggestions** pre-populate questions from what the platform knows (processing locations from cloud regions, processors from vendor assessments, technical mitigations from control status) and are tagged as *auto* until a human confirms them.

Workflow: **draft → in review** (Submit) **→ approved** (with a validity period, 365 days by default) or **rejected** with a reason. Approvals are recorded with who and when; an expired DPIA shows on the overview.

## SDF classification

![Significant Data Fiduciary classification: current classification Likely SDF; volume tier, sector, data categories, cross-border, automated decision-making, children's data](/img/screenshots/compliance/dpdp-sdf.webp)

The Act lets the Government designate **Significant Data Fiduciaries**, who carry extra duties (DPO in India, independent audits, mandatory DPIAs). The thresholds are not yet prescribed, so the module scores the factors the Act names — **volume tier** of Data Principals, **sector** (BFSI, healthcare, telecom, government, edtech, e-commerce, …), sensitive **data categories** (financial, health, biometric, children, government ID, …), **cross-border** processing, **automated decision-making** and **children's data at scale** — into a versioned score:

| Result | Score | Posture |
| --- | --- | --- |
| **Likely SDF** | ≥ 8 | Behave as designated: the three SDF-only controls become applicable and readiness is recalculated |
| **Possible SDF** | 4–7 | Prepare — designation is plausible |
| **Unlikely SDF** | < 4 | Monitor; reassess when processing scales |

Every assessment is kept in the **history** with the formula version, so a later change in thresholds is auditable.

## Vendor assessment

![Vendor assessments (DPDP Section 8 / Rule 6): FaceSure Technologies — conditional pass, expires 2027; Assess Vendor](/img/screenshots/compliance/dpdp-vendors.webp)

A fiduciary remains responsible for its **processors**. The vendor questionnaire has **18 questions** across encryption, access control, logging, backups, incident handling, sub-processors, data location, erasure, audit rights and HR security; answer each **pass / partial / fail / not assessed** with notes.

| Verdict | Rule |
| --- | --- |
| **Not assessed** | Fewer than 10 questions answered |
| **Failing** | Any **critical** question fails (encryption at rest / in transit, and the other critical items), or more than 2 non-critical failures |
| **Conditional pass** | Any non-critical failure, or more than 2 partial answers — remediation expected |
| **Passing** | Every critical question answered *pass*, no failures, at most 2 partials |

Assessments carry a **validity** (365 days by default); the history per vendor shows how a processor has trended. **Vendor failing** feeds the overview and the audit pack.

## Breach management

![Breach Incident Management (Rule 7): incident list with status, CERT-In and DPB report state, detected time and affected Data Principals; Report Incident](/img/screenshots/compliance/dpdp-breach.webp)

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
4. **Notify Data Principals** (channels used, summary), **file the CERT-In report** and **file the DPB report** — the module refuses to record a report until every field the regulation lists (Rule 7(2)(1)–(9) for the Board, Annexure I for CERT-In) is present, and generates the **report text** for you.
5. **Close** with closure notes. Closing is blocked while a required report is unfiled.

The **triage** views list incidents whose reportability decision is pending; the **approaching** and **overdue** views watch both clocks. **Auto-detection** (off by default; an administrator opts in per environment) turns critical/high platform alerts that look like data exposure into *candidate* incidents in **detected** status — it never declares, so no legal clock starts without a human — and a false positive is simply withdrawn.

## Audit & export

![Audit & Export: retention policy, generate audit pack, recent audit events](/img/screenshots/compliance/dpdp-audit.webp)

Every DPDP action — a DPIA approved, a vendor assessed, a breach declared, a report filed — is written to the **DPDP audit event log**. An **audit pack** is a date-ranged export of those events plus the module's state at period end (readiness, SDF classification, DPIA and vendor summaries), persisted in full as an immutable record and sealed with a **SHA-256 pack hash**; **Verify** recomputes the hash so a regulator can confirm nothing changed. The **retention policy** enforces the Rule 8(3) floor of **365 days** for processing logs (set longer, never shorter) and records data residency.

## Related

- [Compliance Posture](./compliance-dashboard.md) — the SCF controls behind each DPDP rule.
- [India regulatory readiness](../industries/india-regulatory-readiness.md) — DPDP alongside RBI, SEBI CSCRF and CERT-In.
- [Compliance & GRC API](./api.md#dpdp) — readiness, DPIA, SDF, vendor, breach and audit endpoints.
