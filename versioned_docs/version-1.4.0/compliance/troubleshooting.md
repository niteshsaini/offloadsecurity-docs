---
title: "Compliance Troubleshooting & FAQ"
sidebar_label: "Troubleshooting & FAQ"
sidebar_position: 10
description: "Fix the common compliance problems: scores that look too low or never move, assessments that do not change posture, a status automation will not change, drift and alert questions, evidence that earns no credit, audit report verification, DPDP readiness and breach filings, and answers to frequent questions."
---

# Compliance Troubleshooting & FAQ

## Posture and scores

**Every framework is at 5–15% although we have connected accounts and scans.**
That is the honest starting point. Scans only ever touch the controls a scanner can observe (roughly encryption, access, logging, network, vulnerability management); the denominator is *every* in-scope control, and *not assessed* counts as zero. The score moves when you (a) complete an [assessment](./interactive-assessments.md) — one ISO 27001 assessment typically lifts ISO 27001/27002 by 60–70 points and SOC 2, NIST CSF and PCI by 20–40 because of the SCF cross-mappings — and (b) [override](./compliance-dashboard.md#manual-overrides) the governance, HR and continuity controls no scanner can see.

**A framework shows "Not Assessed" instead of a percentage.**
No control in that framework has any status other than *not assessed*. Run a sync (Compliance Engine → **Run Now**), complete an assessment for it, or set an override.

**The score did not change after new scans.**
Findings reach controls on the 4-hourly refresh and after scans; **Run Now** does it immediately. If it still does not move: the scan may not have completed cleanly (a scan with tool failures never promotes a control, and a paused cloud account is skipped); the failing checks may have only derived mappings, which record gaps but never earn credit; or the control's status was set by a person, which automation never changes. Open the control in the Evidence Hub and read **Why this status** ([How status is decided](./control-status.md)).

**Total Controls says 1,003 but the catalog has 1,534.**
Total Controls counts controls referenced by your *active* frameworks. Activate more frameworks from the Frameworks tile to widen the scope (and lower the percentages, since more controls become in-scope).

**Two teams see different scores for the same framework.**
Correct: control state, evidence, overrides, thresholds, assessments and the active framework set are all per team. The catalog is shared; nothing else is.

## Assessments

**I completed an assessment and posture did not move.**
Check three things. (1) It must be **completed**, not just answered; completion is what maps answers to controls, and it needs at least 80% of questions answered. (2) The framework must be **active** for the mapping's effect to show in scores (an ISO 27001 assessment maps to ISO 27001 and ISO 27002 controls). (3) Controls whose status a person set, including overrides, keep that status; the assessment attaches evidence but cannot change them. A **Run Now** on the engine tab re-maps every completed assessment.

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
Automation never changes a status a person set. What can happen: another person changed or **unlocked** it on Compliance Engine → Manual Overrides, or a person changed the status through the status endpoint. The audit log at `GET /api/common-controls/audit-log/{scf_id}` shows who. Set it again through **Override** with a justification.

**A control is marked "contradicted".**
A person set it to *implemented* and mapped scan checks are failing now. The status is left as the person set it. Review the failing checks in **Why this status**: fix the resources, or change the status yourself if the attestation no longer holds. The flag clears when the failures resolve.

**A control went back to "not assessed" on its own.**
Its *implemented* status rested on evidence that is no longer current (expired, superseded or rejected), or the failures behind an engine downgrade resolved without current evidence to restore it. Add or renew the evidence, or set the status with a justification.

**Manual Overrides tab says "No Active Overrides" but the posture shows locked controls.**
Fixed in the current release — the status payload now lists the team's locked controls. Until you upgrade, the posture page's gap analysis and the audit log are the authoritative view.

**Threshold breach for a framework we do not report against.**
Thresholds apply to every *active* framework at the default 70%. Ask a platform administrator to deactivate the framework for your team, or set its threshold to what you actually accept (needs the **admin** role).

**Run Now returns a job id and nothing visible happens.**
Sync is a background job (`GET /api/jobs/{job_id}`); on a large tenant it runs for a minute or two and the overview refreshes on its own. Only one sync runs per team at a time — a second click while one is running is ignored.

## Drift

**Run Drift Detection says 0 drifts, but a control regressed today.**
Each change is reported once. If the 4-hourly refresh or a post-scan run already reported it, a manual run finds nothing new; look under **Drift History**. A control's first evaluation is its baseline, not drift. Finding-count regressions are the exception that still compares the last two daily snapshots (00:05 UTC), so they appear the day after.

**Drift never shows anything, for weeks.**
Drift is read from the compliance audit log of status changes. Check that compliance refreshes are running (the Compliance Engine *Total Syncs* tile and timeline) and that the Celery beat is running. Earlier releases could fail the daily snapshot on an index-name conflict at startup; the current release tolerates it.

**Alert policy fires but nothing arrives.**
The policy chooses drifts; delivery uses the channels configured under [Notifications](../integrations/notifications.md). Confirm the channel is enabled and its test passes, and that the drift's severity meets the policy's minimum (expired evidence is *medium*). Drift notifications go to email, Slack and in-app only: a policy with only **Teams** selected notifies in-app, and *Info (all)* behaves as *High+*.

## Evidence

**Coverage is 45% but scans run every day.**
Scan evidence only lands on the controls the scanners map to. **Collect All Evidence** (walks every module) and **Collect API Evidence** (raw cloud API captures) widen it; the remainder — policies, minutes, training records — needs a manual upload or a knowledge-base document mapped to controls.

**The auditor package is empty for a framework.**
The framework has no controls with linked evidence, or the framework key is wrong — use the SCF keys (`iso_27001`, `soc2`, `pci_dss_4`, `nist_csf_2`, `cis_v8`, `hipaa`, `gdpr`, …) as shown in `GET /api/common-controls/frameworks`.

**Evidence is linked to a control but the status or score does not change.**
The item earns no credit. The Evidence Hub labels the reason: a failing check (a gap), a pass through a derived mapping (Wazuh, Kubernetes and unreviewed Prowler mappings never earn credit), not yet approved in the review queue, superseded, or expired. See [Evidence Hub → What earns credit](./evidence-hub.md#what-earns-credit).

**API evidence shows nothing for a GCP or Azure account.**
The tab lists any provider without API evidence and why. A resource type with no resources is *not evaluated*; permission denied or a disabled API is a collection error. Grant the read-only permissions for the account and collect again.

**Manual evidence disappeared from a control.**
It passed its `valid_until` date. Expired evidence stops supporting controls (it is still in the store); renew it from **Renewals** or upload the current version.

## Audit reports

**Verify says a PDF is "identified" rather than verified.**
You pasted the content hash from the PDF footer. It identifies which report the PDF belongs to but does not prove the PDF file is unaltered. Paste the SHA-256 of the downloaded file itself to prove that.

**A report file shows "not kept" or returns 410.**
Object storage was unavailable when it was issued, or the file was larger than `AUDIT_REPORT_COPY_MAX_BYTES`. Its SHA-256 is still on record; generate a new report to get the file.

**A report from before 1.4.0 says "regenerated".**
Reports issued before freezing kept no copies. Their sections are rebuilt from current data and labeled so; they are not the issued figures.

## DPDP

**Readiness counts 22 controls for us but 19 for another team.**
The other team is not classified as a Significant Data Fiduciary; the three SDF-only controls (DPO appointment, independent audits, DPIAs) apply once the SDF classification returns *Likely SDF*.

**A DPDP control stays "not implemented" although most of its SCF controls are green.**
The worst-link rule: one *not implemented* SCF control makes the rule not met. Open the control to see its mapped SCF controls and fix the red one — or, if it genuinely does not apply, mark that SCF control *not applicable* with a justification.

**The DPB / CERT-In report will not file.**
The completeness check lists the missing fields (`GET /api/dpdp/breach/{incident_id}/dpb-completeness` or `…/cert-in-completeness`). The Board report needs Rule 7(2)(1)–(9): nature, extent, timing and location; likely consequences; mitigation; data categories and Data Principal count; record categories and count; containment; cause and remedial steps; Data Principal notification; responsible officer. CERT-In needs the incident category, affected systems, impact, mitigation and a responsible contact.

**I cannot close a breach.**
Every required report (DPB and, if CERT-In-reportable, CERT-In) must be recorded first, and the CERT-In reportability decision must be made. If the incident was a false alarm, **withdraw** it instead; withdrawal is refused once any report or notification has been recorded.

**Readiness cannot reach 100%.**
Some applicable controls have no scanner or workflow evidence in the platform and stay *not assessed*. The overview lists them under *Controls the platform can't assess*; keep your own evidence for them.

**An audit pack fails verification with "signed under a different key".**
The pack was sealed under an earlier `DPDP_AUDIT_SIGNING_KEY` (or `SECRET_KEY`, when no signing key is set). It does not indicate tampering; verify with the key that was in use when the pack was generated.

**The DPIA tab shows an error page.**
An earlier release crashed the tab when a DPIA existed (`completeness_percentage` serialisation). Upgrade; no data is lost.

## Frequently asked questions

**Which frameworks are covered, and how current is the SCF?**
All 27 frameworks on the [Supported Frameworks](./supported-frameworks.md) page, mapped through SCF release 2026.2. RBI directions are not a selectable framework. `POST /api/common-controls/import-scf` refreshes the catalog when a new release ships.

**Can an auditor get read-only access?**
Yes — an **Auditor** or **Viewer** team role can read posture, evidence and reports without changing anything; see [Roles, Teams & API Keys](../authentication/rbac-team-management.md).

**Does the platform change my cloud environment?**
Only through the [remediation playbooks](./autonomous-compliance.md#remediation-playbooks), only after approval, and only when `REMEDIATION_LIVE_EXECUTE=true` — otherwise every action is a logged dry run.

**How far back can I prove my posture?**
The compliance audit log of every status change and drift reports are kept for 5 years; daily snapshots for 90 days, weekly for a year, monthly indefinitely; issued audit report files for 180 days (`REPORT_RETENTION_DAYS`); the DPDP audit event log for at least 365 days (the Rule 8(3) floor, configurable upward). See [Retention](./index.md#retention).

**Is there an ISO 27001 Statement of Applicability?**
Yes, for every framework: select the framework on Compliance Posture to see its Statement of Applicability (ISO 27001 clauses 4–10 and Annex A), edit justifications and **Download SoA (XLSX)**. Over the API: `GET /api/common-controls/soa/iso_27001?format=xlsx`.

## Still stuck?

The platform-wide [Troubleshooting](../troubleshooting.md) page covers login, workers and deployment. When contacting support include the framework key, the SCF ID of the control in question and the sync id from `GET /api/compliance-engine/sync-history`.
