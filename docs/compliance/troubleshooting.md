---
title: "Compliance Troubleshooting & FAQ"
sidebar_label: "Troubleshooting & FAQ"
sidebar_position: 10
description: "Fix the common compliance problems — scores that look too low or never move, assessments that do not change posture, an override that keeps getting overwritten, no drift, empty evidence, missing DPDP controls, breach reports that will not file — and answers to frequent questions."
---

# Compliance Troubleshooting & FAQ

## Posture and scores

**Every framework is at 5–15% although we have connected accounts and scans.**
That is the honest starting point. Scans only ever touch the controls a scanner can observe (roughly encryption, access, logging, network, vulnerability management); the denominator is *every* in-scope control, and *not assessed* counts as zero. The score moves when you (a) complete an [assessment](./interactive-assessments.md) — one ISO 27001 assessment typically lifts ISO 27001/27002 by 60–70 points and SOC 2, NIST CSF and PCI by 20–40 because of the SCF cross-mappings — and (b) [override](./compliance-dashboard.md#manual-overrides) the governance, HR and continuity controls no scanner can see.

**A framework shows "Not Assessed" instead of a percentage.**
No control in that framework has any status other than *not assessed*. Run a sync (Compliance Engine → **Run Now**), complete an assessment for it, or set an override.

**The score did not change after new scans.**
Findings reach controls on the 4-hourly refresh; **Run Now** does it immediately. If it still does not move, the scan probably did not complete cleanly — a scan with tool failures never promotes a control (by design), and a paused cloud account is skipped. Check the scan's status in its module.

**Total Controls says 1,003 but the catalog has 1,534.**
Total Controls counts controls referenced by your *active* frameworks. Activate more frameworks from the Frameworks tile to widen the scope (and lower the percentages, since more controls become in-scope).

**Two teams see different scores for the same framework.**
Correct: control state, evidence, overrides, thresholds and assessments are all per team. The catalog is shared; nothing else is.

## Assessments

**I completed an assessment and posture did not move.**
Check three things. (1) It must be **completed**, not just 100% answered — completion is what maps answers to controls. (2) The framework must be **active** for the mapping's effect to show in scores (an ISO 27001 assessment maps to ISO 27001 and ISO 27002 controls). (3) Locked controls keep their overridden status — the assessment attaches evidence but cannot change them. A **Run Now** on the engine tab re-maps every completed assessment.

**Auto-Fill suggests "No" for things we do.**
Suggestions come from SCF control state and cloud-scan pass rates, not from your documents. Answer the question yourself (the platform-derived answer is a hint), attach the evidence in the *evidence* field, and — if the underlying control really is in place — override that control so the next assessment sees it.

**Auto-Fill / Auto-Suggest is greyed out or says no mapping.**
The header's *SCF coverage* shows how many questions have a mapped control. Frameworks with maturity-style questions (SAMM, DevSecOps) map little; ISO 27001, SOC 2 and NIST CSF map well.

**I cannot find the assessment I started yesterday.**
**View All Assessments** on the hub opens Assessment History, filterable by status and framework; **View Details** reopens it. (The *Assessment Center* is a different list — the enhanced, expiring assessments — and will not show framework questionnaires.)

**The score dropped when I pressed Complete.**
It should not: N/A answers count for progress but never for the score, at completion as well as during. If you see this on an older release, upgrade; the answers themselves are intact and completing again recomputes the score.

## Overrides and the engine

**My override was overwritten.**
It cannot be — the sync never changes a locked control's status. What can happen: someone **unlocked** it on Compliance Engine → Manual Overrides (the audit log at `GET /api/common-controls/audit-log/{scf_id}` shows who), or you changed the status through the plain status endpoint rather than the override, which does not lock. Set it again through **Override** with a justification.

**Manual Overrides tab says "No Active Overrides" but the posture shows locked controls.**
Fixed in the current release — the status payload now lists the team's locked controls. Until you upgrade, the posture page's gap analysis and the audit log are the authoritative view.

**Threshold breach for a framework we do not report against.**
Thresholds apply to every *active* framework at the default 70%. Either deactivate the framework or set its threshold to what you actually accept.

**Run Now returns a job id and nothing visible happens.**
Sync is a background job (`GET /api/jobs/{job_id}`); on a large tenant it runs for a minute or two and the overview refreshes on its own. Only one sync runs per team at a time — a second click while one is running is ignored.

## Drift

**Run Drift Detection always says 0 drifts, even after a control regressed today.**
Regression detection compares the **two most recent daily snapshots** (taken at 00:05 UTC), so a change made today shows up tomorrow. A brand-new team needs two days of snapshots before any regression can appear. Threshold crossings and expired evidence are evaluated against the current state and do show immediately.

**Snapshots are missing / drift never shows anything, for weeks.**
Check the Celery beat is running the `compliance-daily-snapshot` task (00:05 UTC) and that `team_control_state_snapshots` is being written. Earlier releases could fail the snapshot on an index-name conflict at startup; the current release tolerates it.

**Alert policy fires but nothing arrives.**
The policy chooses drifts; delivery uses the channels configured under [Notifications](../integrations/notifications.md). Confirm the channel is enabled and its test passes, and that the drift's severity meets the policy's threshold (default *high*; expired evidence is *medium*).

## Evidence

**Coverage is 45% but scans run every day.**
Scan evidence only lands on the controls the scanners map to. **Collect All Evidence** (walks every module) and **Collect API Evidence** (raw cloud API captures) widen it; the remainder — policies, minutes, training records — needs a manual upload or a knowledge-base document mapped to controls.

**The auditor package is empty for a framework.**
The framework has no controls with linked evidence, or the framework key is wrong — use the SCF keys (`iso_27001`, `soc2`, `pci_dss_4`, `nist_csf_2`, `cis_v8`, `hipaa`, `gdpr`, …) as shown in `GET /api/common-controls/frameworks`.

**Manual evidence disappeared from a control.**
It passed its `valid_until` date. Expired evidence stops supporting controls (it is still in the store); renew it from **Renewals** or upload the current version.

## DPDP

**Readiness counts 22 controls for us but 19 for another team.**
The other team is not classified as a Significant Data Fiduciary; the three SDF-only controls (DPO appointment, independent audits, DPIAs) apply once the SDF classification returns *Likely SDF*.

**A DPDP control stays "not implemented" although most of its SCF controls are green.**
The worst-link rule: one *not implemented* SCF control makes the rule not met. Open the control to see its mapped SCF controls and fix the red one — or, if it genuinely does not apply, mark that SCF control *not applicable* with a justification.

**The DPB / CERT-In report will not file.**
The completeness check lists the missing fields (`GET /api/dpdp/breach/{incident_id}/dpb-completeness` or `…/cert-in-completeness`). The Board report needs Rule 7(2)(1)–(9): nature, extent, timing and location; likely consequences; mitigation; data categories and Data Principal count; record categories and count; containment; cause and remedial steps; Data Principal notification; responsible officer. CERT-In needs the incident category, affected systems, impact, mitigation and a responsible contact.

**I cannot close a breach.**
Every required report (DPB and, if CERT-In-reportable, CERT-In) must be filed first. If the incident was a false alarm, **withdraw** it instead.

**The DPIA tab shows an error page.**
An earlier release crashed the tab when a DPIA existed (`completeness_percentage` serialisation). Upgrade; no data is lost.

## Frequently asked questions

**Which frameworks are covered, and how current is the SCF?**
All 27 frameworks on the [Supported Frameworks](./supported-frameworks.md) page, mapped through SCF release 2026.2. `POST /api/common-controls/import-scf` refreshes the catalog when a new release ships.

**Can an auditor get read-only access?**
Yes — an **Auditor** or **Viewer** team role can read posture, evidence and reports without changing anything; see [Roles, Teams & API Keys](../authentication/rbac-team-management.md).

**Does the platform change my cloud environment?**
Only through the [remediation playbooks](./autonomous-compliance.md#remediation-playbooks), only after approval, and only when `REMEDIATION_LIVE_EXECUTE=true` — otherwise every action is a logged dry run.

**How far back can I prove my posture?**
Daily snapshots are kept under the snapshot retention policy; audit reports for 180 days; the DPDP audit event log for at least 365 days (the Rule 8(3) floor, configurable upward).

**Is there an ISO 27001 Statement of Applicability?**
`GET /api/common-controls/soa/iso_27001` returns requirement → controls → status; the Controls CSV in [Audit Reports](./audit-reports.md) is the flat version.

## Still stuck?

The platform-wide [Troubleshooting](../troubleshooting.md) page covers login, workers and deployment. When contacting support include the framework key, the SCF ID of the control in question and the sync id from `GET /api/compliance-engine/sync-history`.
