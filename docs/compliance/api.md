---
title: "Compliance & GRC API"
sidebar_label: "API"
sidebar_position: 9
description: "Every compliance workflow over REST — SCF controls and posture, gap analysis and overrides, the compliance engine (sync, thresholds, drift, alert policies, control testing, exceptions, remediation), evidence, assessments, audit reports and the full DPDP surface."
---

# Compliance & GRC API

Everything in this section is available over the REST API. [API Reference](../api-reference/index.md) covers authentication and conventions; Swagger at `https://<your-host>/api/docs` is exhaustive.

```bash
export OFFLOAD_HOST="https://your-instance.example.com"
export OFFLOAD_API_KEY="osk_xxxxxxxxxxxxxxxxxxxx"
```

Send the key as `X-API-Key`; calls are scoped to the key's team.

## Controls and posture

| Task | Endpoint | Notes |
| --- | --- | --- |
| Frameworks | `GET /api/common-controls/frameworks` · `POST /api/common-controls/frameworks/activate` | Catalog of 27 with active flags; activation is platform-admin. |
| Posture | `GET /api/common-controls/posture` · `GET /api/common-controls/posture/active` · `GET /api/common-controls/stats` · `GET /api/common-controls/map/stats` | Per-framework score, counts, assessed flag (`/active` = active frameworks only). |
| Controls | `GET /api/common-controls/controls?limit=&skip=` · `GET /api/common-controls/search?q=&framework=&domain=` · `GET /api/common-controls/control/{scf_id}` · `GET /api/common-controls/framework/{framework}` | Catalog plus the caller's team state per control. |
| Gap analysis | `GET /api/common-controls/gap-analysis/{framework}` | Non-implemented controls with priority (SCF weighting), status and evidence. |
| Statement of Applicability | `GET /api/common-controls/soa/{framework}` · `GET …/soa/{framework}/requirements/{requirement}` | Requirement → controls → status, ready for an ISO SoA. |
| Override | `PUT /api/common-controls/controls/{scf_id}/override` `{implementation_status, justification, override_type}` | Locks the control. **admin** role. |
| Status / evidence link | `POST /api/common-controls/control/{scf_id}/status` · `POST /api/common-controls/control/{scf_id}/evidence` | Set status without a lock; link an evidence item. |
| Sync | `POST /api/common-controls/map/sync-all` · `POST /api/common-controls/map/assessment` · `POST /api/common-controls/map/scan-findings` · `POST /api/common-controls/correlate-all` | Replay assessments and scan findings into controls; `correlate-all` is admin-only. |
| Auto-fill | `POST /api/common-controls/auto-fill` `{framework, questions[]}` · `GET …/auto-fill/readiness/{framework}` · `POST …/auto-fill/build-mapping` · `GET …/auto-fill/mapping/{framework}` | Suggested answers with confidence from SCF state; pre-computed question→control map. |
| Audit log | `GET /api/common-controls/audit-log` · `GET …/audit-log/{scf_id}` | Every status change, override and evidence link, with actor. |
| SCF import | `POST /api/common-controls/import-scf` | Refresh the catalog from the SCF release (admin). |

## Compliance engine

| Task | Endpoint | Notes |
| --- | --- | --- |
| Status | `GET /api/compliance-engine/status` | Last sync and result, thresholds check, active breaches, `overridden_controls`. |
| Run | `POST /api/compliance-engine/sync` · `POST /api/compliance-engine/refresh` | Sync returns a job id (`GET /api/jobs/{job_id}`); refresh = sync + thresholds + scores. |
| History | `GET /api/compliance-engine/sync-history` · `GET /api/compliance-engine/timeline?limit=` | |
| Thresholds | `GET` · `POST /api/compliance-engine/thresholds` `{framework?, threshold}` · `GET /api/compliance-engine/check-thresholds` | Omit `framework` to set the default (70). |
| Drift | `POST /api/compliance-engine/detect-drift` · `GET /api/compliance-engine/drift-history?limit=` | Diff of the two most recent daily snapshots. |
| Alert policies | `GET` · `POST /api/compliance-engine/alert-policies` · `PUT` · `DELETE …/alert-policies/{policy_id}` | `{policy_name, drift_types[], severity_threshold, frameworks[], channels[], enabled}`. |
| Overrides | `POST /api/compliance-engine/controls/{scf_id}/override` `{override: true/false, reason}` | Lock / unlock; **admin**. Same store as the posture override. |
| Evidence expiry | `GET /api/compliance-engine/evidence-expiring-soon` · `GET …/evidence-expiry-alerts` · `POST …/evidence-expiry-alerts/{alert_id}/acknowledge` | |
| Reseed | `POST /api/compliance-engine/reseed-controls` | Add newly shipped baseline controls (admin). |

### Control testing

| Task | Endpoint |
| --- | --- |
| Schedules | `GET /api/compliance-engine/test-schedules` · `GET …/test-schedules/overdue-summary` · `GET` · `PUT` · `DELETE …/test-schedules/{scf_id}` `{test_type: design\|operating_effectiveness\|both, frequency_days, procedure, owner, enabled}` · `POST …/test-schedules/seed` |
| Results | `POST /api/compliance-engine/test-results/{scf_id}` `{result: pass\|fail\|exception\|not_tested, test_type, notes, evidence_ids[], exceptions_noted, management_response}` · `GET …/test-results/{scf_id}` · `GET …/test-results` |

### Exceptions

| Task | Endpoint |
| --- | --- |
| Create / list | `POST /api/compliance-engine/exceptions` `{scf_id, framework, justification, risk_impact, compensating_controls, remediation_plan, remediation_target_date, expires_at}` · `GET …/exceptions` · `GET …/exceptions/summary` · `GET …/exceptions/{exception_id}` |
| Decide | `POST …/exceptions/{exception_id}/approve` · `…/deny` · `…/remediate` — the requester cannot approve their own |

### Remediation

| Task | Endpoint |
| --- | --- |
| Playbooks and actions | `GET /api/compliance-engine/remediation/playbooks` · `GET …/remediation/actions` · `GET …/remediation/stats` · `POST …/remediation/process-findings` |
| Act | `POST …/remediation/actions/{action_id}/approve` · `…/deny` · `…/execute` · `…/rollback` — **Execute Remediations** permission; execution is a dry run unless `REMEDIATION_LIVE_EXECUTE=true` |

## Evidence

| Task | Endpoint | Notes |
| --- | --- | --- |
| Evidence store | `GET` · `POST /api/common-controls/evidence` `{title, evidence_type, source, scf_control_ids[], metadata}` · `GET …/evidence/{evidence_id}` · `POST …/evidence/{evidence_id}/link-controls` · `GET …/evidence/framework/{framework}` · `GET …/evidence/dedup-stats` · `GET …/evidence-reuse` · `POST …/evidence/auto-from-scan` | Deduplicated by content hash. |
| Collection | `POST /api/evidence-collection/collect-all` · `GET …/collection-history` · `GET …/coverage` · `GET …/framework-controls/{framework_key}` · `GET …/control/{scf_id}` · `POST …/manual-upload` · `POST …/manual-upload-file` (multipart) · `GET …/evidence/{id}` · `GET …/evidence/{id}/download` · `DELETE …/evidence/{id}` · `POST …/evidence/{id}/comment` | `collect-all` returns a job id. |
| API captures | `POST /api/evidence-capture/collect-all` · `POST …/collect/{account_id}` · `GET …/status` | Read-only cloud API evidence per connected account. |
| Review, quality, renewals | `POST /api/evidence-completion/review/submit/{evidence_id}` · `POST …/review/action/{evidence_id}` `{action: approve\|reject}` · `POST …/review/bulk-approve` · `GET …/review/pending` · `POST …/quality/score-all` · `GET …/quality/{evidence_id}` · `GET …/renewals?days_since=365` · `POST …/renewals/{evidence_id}` | |
| AI document mapping | `POST /api/evidence-completion/ai-map/{document_id}` · `POST …/ai-map/{document_id}/confirm` | Needs an LLM provider. |
| Auditor package | `GET /api/evidence-completion/auditor-package/{framework}` | ZIP, organised by control in four layers. |
| Intelligence | `GET /api/evidence-intelligence/freshness` · `GET …/smart-coverage` · `GET …/control-bundle/{scf_id}` | |

## Assessments

| Task | Endpoint | Notes |
| --- | --- | --- |
| Create | `POST /api/assessments/create` `{framework_type, organization, assessor_name, assessor_designation, product_name, attendees, asvs_level?}` — or the per-framework routes `POST /api/assessments/{iso-27001 \| soc2 \| asvs-5-0 \| nist-csf-2-0 \| nist-ssdf \| samm \| owasp-api-security-top10 \| enhanced-devsecops}/create` | Types: `iso-27001`, `soc2`, `asvs-5-0`, `nist-csf-2-0`, `nist-ssdf`, `samm`, `owasp-api-security-top10`, `enhanced-devsecops`, `insider-threat`, `security-operations-resilience`. |
| Work | `GET /api/assessments` · `GET /api/assessments/{assessment_id}` · `GET …/{assessment_id}/questions` · `POST …/{assessment_id}/answer` `{question_id, response: yes\|partially\|no\|not_applicable, evidence, explanation, notes}` · `POST …/{assessment_id}/complete` · `GET …/{assessment_id}/results` · `DELETE /api/assessments/{assessment_id}` | Completing maps answers to SCF controls. |
| Framework toggle | `GET` · `PUT /api/assessments/framework-toggle` | Which frameworks the hub offers. |
| Enhanced assessments | `POST /api/global-assessments/create` · `GET …/list` · `GET …/{assessment_id}` · `POST …/evidence/upload` · `GET …/evidence/{assessment_id}` · `POST …/collect-evidence` · `GET …/expiring` · `POST …/renew/{assessment_id}` · `GET` · `POST …/evidence-rules` · `GET …/expiry-rules` · `GET …/dashboard` · `GET …/analytics` · `POST …/bulk-operations` · `GET …/notifications` | The Assessment Center store. |

## Audit reports

| Task | Endpoint |
| --- | --- |
| Generate / list / download | `POST /api/compliance-engine/reports/generate` `{report_type: full\|controls\|findings\|drift\|remediation}` · `GET /api/compliance-engine/reports` · `GET …/reports/{report_id}/download/{section}` (`controls` · `findings` · `drift` · `remediation` · `compliance_scores`) |

## DPDP

| Task | Endpoint |
| --- | --- |
| Readiness | `GET /api/dpdp/readiness` · `GET /api/dpdp/readiness/top-findings` · `GET /api/dpdp/framework/controls` · `GET /api/dpdp/dashboard` |
| DPIA | `GET /api/dpdp/dpia/template` · `GET` · `POST /api/dpdp/dpia` `{processing_activity, initial_answers?}` · `GET …/dpia/{dpia_id}` · `PUT …/dpia/{dpia_id}/answers` `{answers, risk_assessments?, answer_sources?}` · `GET …/dpia/{dpia_id}/autofill-suggestions` · `POST …/dpia/{dpia_id}/submit` · `…/approve` `{validity_days}` · `…/reject` `{reason}` |
| SDF | `GET /api/dpdp/sdf/template` · `POST /api/dpdp/sdf/assess` `{volume_tier, data_categories[], sector, processes_cross_border, uses_automated_decision_making, processes_children_at_scale, additional_context}` · `GET …/sdf/current` · `GET …/sdf/history` · `GET …/sdf/autofill-suggestions` |
| Vendors | `GET /api/dpdp/vendor/template` · `POST /api/dpdp/vendor/assess` `{vendor_name, vendor_processing_description, answers, notes?, validity_days}` · `GET /api/dpdp/vendor` · `GET …/vendor/{vendor_name}` · `GET …/vendor/{vendor_name}/history` · `GET /api/dpdp/vendor-failing` |
| Breaches | `POST /api/dpdp/breach` `{detected_at, detection_source, detection_evidence_refs[], initial_notes}` · `GET /api/dpdp/breach` · `GET …/breach/{incident_id}` · `POST …/declare` `{declaration_basis}` · `PUT …/assessment` `{fields}` · `POST …/assess` `{is_reportable, reportability_basis, is_cert_in_reportable, cert_in_reportability_basis, cert_in_incident_category}` · `GET …/cert-in-reportability` · `POST …/notify-dp` `{channels_used[], notification_summary}` · `POST …/report-dpb` · `POST …/report-cert-in` `{filed_by, filed_at, report_reference}` · `GET …/dpb-report-text` · `GET …/dpb-completeness` · `GET …/cert-in-report-text` · `GET …/cert-in-completeness` · `POST …/close` `{closure_notes}` · `POST …/withdraw` |
| Breach queues | `GET /api/dpdp/breach/overdue/dpb` · `…/overdue/cert-in` · `…/approaching/dpb` · `…/approaching/cert-in` · `…/triage/dpb` · `…/triage/cert-in` |
| Audit & export | `GET /api/dpdp/audit/events?event_type=&limit=` · `POST /api/dpdp/audit/pack` `{period_start, period_end, pack_label}` · `GET …/audit/packs` · `GET …/audit/pack/{pack_id}` · `GET …/audit/pack/{pack_id}/pdf` · `POST …/audit/pack/{pack_id}/verify` · `GET` · `PUT /api/dpdp/audit/retention` `{retention_days ≥ 365, data_residency}` |

## Permissions

| Action | Permission |
| --- | --- |
| Read posture, controls, evidence, assessments, DPDP | any authenticated team member (`view_assessments` for DPDP and assessment lists) |
| Sync, auto-fill, evidence upload / review, assessments, DPIA / SDF / vendor / breach writes, thresholds, drift, alert policies, test schedules, exceptions, reports | **Manage Assessments** (`manage_assessments`) |
| Manual overrides (lock / unlock), `correlate-all`, reseed controls, SCF import | **admin** role (or admin-scoped API key) |
| Framework activation | platform administrator |
| Approve / deny / execute / roll back remediation actions | **Execute Remediations** (`execute_remediations`) |

See [Authentication](../api-reference/authentication.md) for key scopes and [Conventions](../api-reference/conventions.md) for pagination, error shapes and rate limits.
