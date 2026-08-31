---
title: "Compliance Officer Journey"
sidebar_label: "Compliance Officer"
sidebar_position: 3
description: "The path for the person who owns frameworks, assessments, evidence, and audits — from framework activation to an exportable audit package."
---

# Compliance Officer journey

You own frameworks, assessments, evidence, and audit readiness. This path assumes the security team has already connected accounts and run scans (Days 1–2 of the [First 7 Days](./first-7-days.md)) — compliance scores are computed from that scan data, so coverage comes first.

Typical role: **Compliance Officer**, with **Auditor** accounts for external reviewers (see [Roles, Teams & API Keys](../authentication/rbac-team-management.md)).

## Stage 1 — Choose your frameworks

1. [Supported Frameworks](../compliance/supported-frameworks.md) — the full catalog (ISO 27001:2022, SOC 2, PCI DSS 4.0.1, NIST CSF 2.0, GDPR, DPDP Act, SEBI CSCRF, and more), all mapped through the SCF common-control library.
2. [Compliance & GRC overview](../compliance/index.md) — how one control maps to many frameworks, and how statuses become scores.
3. Activate the one or two frameworks you actually answer to. Every additional framework is mostly free later — the common-control model means evidence and control status carry across.

**You can now:** explain to an auditor which framework versions you track and where the control library comes from.

## Stage 2 — Read your posture

1. [Compliance Posture Dashboard](../compliance/compliance-dashboard.md) — scores, gap analysis, and drift detection.
2. [Autonomous Compliance](../compliance/autonomous-compliance.md) — how control statuses are derived automatically from scan findings, what the score weightings are, and when manual overrides are appropriate.

**You can now:** name your top gaps per framework and distinguish "failing" from "not assessed."

## Stage 3 — Assess what scans can't see

1. [Interactive Assessments](../compliance/interactive-assessments.md) — questionnaire-based assessments (ISO 27001, SOC 2 Type II, NIST CSF, OWASP ASVS/SAMM, and more) with Yes/Partially/No scoring and PDF export.
2. Use auto-fill to draft answers from platform data, then review each one — auto-filled answers carry confidence levels and are yours to confirm or correct.

**You can now:** produce a scored self-assessment for your primary framework.

## Stage 4 — Build the evidence trail

1. [Evidence Hub](../compliance/evidence-hub.md) — auto-collected evidence with quality scores and validity windows (cloud and scan evidence stays valid 90 days; assessment answers and policy documents, 365), plus manual upload for policies and screenshots.
2. Run **Collect All**, then work the review queue: approve what's right, reject what isn't, replace what's expired.
3. Turn material gaps into governed risks in the [Risk Register](../vulnerability-risk/risk-register.md) so they get owners, treatment plans, and SLAs instead of living in a spreadsheet.

**You can now:** show, for any control, *why* it has its status — with dated evidence behind it.

## Stage 5 — India-specific obligations

*Skip this stage if you have no Indian regulatory exposure.*

1. [DPDP Act (India) Privacy](../compliance/dpdp-privacy.md) — readiness assessment, DPIA lifecycle, vendor due diligence, and the breach workflow with dual DPB and CERT-In reporting tracks and deadline watchdog. (Consent management and data-principal request handling are on the roadmap, not in the module today.)
2. [India Regulatory Readiness](../industries/india-regulatory-readiness.md) — how RBI expectations, SEBI CSCRF, and CERT-In directions map to platform capabilities, and the recommended deployment shape for regulated entities. Note: CSCRF audits and VAPT remain with CERT-In-empanelled firms — the platform maintains your evidence and posture between audits; it doesn't replace the auditor.

**You can now:** run a DPDP readiness check and show CSCRF-relevant evidence continuity between audit cycles.

## Stage 6 — Face the audit

1. Export the audit package for your framework from the [Evidence Hub](../compliance/evidence-hub.md) — four layers per control: policy, procedure, technical proof, attestation.
2. Generate executive and audit reports in PDF/HTML — [Reports & AI Assistance](../reports-and-ai.md).
3. Give your external auditor an **Auditor** account: read-only access to evidence and reports, with export rights — [Roles, Teams & API Keys](../authentication/rbac-team-management.md).

**You can now:** hand an auditor a package and an account instead of a shared drive of screenshots.

## Ongoing rhythm

- **Weekly:** check the Compliance Dashboard for drift and newly failing controls.
- **Monthly:** review the Evidence Hub for expiring evidence (cloud/scan evidence ages out at 90 days by design — fresh scans refresh it automatically).
- **Quarterly:** re-run interactive assessments and update the Risk Register treatment plans.
- **Continuously:** let [scheduled scans](../security-scanning/scan-management.md) keep the technical evidence current — that's what makes this posture *continuous* rather than an annual scramble.
