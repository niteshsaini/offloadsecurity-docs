---
title: "AI & Threat Intelligence API"
sidebar_label: "API"
sidebar_position: 7
description: "Threat feeds, indicators, correlation, prioritisation, heatmap and reports; the Security Command Center agents, worklist, incidents, FP/TP assessment and Auto-Fix Engine; AI governance registry and ISO 42001 exports; discovery, AIBOM and prompt tests; the Knowledge Base, questionnaire fill and review queue — with the permission each needs."
---

# AI & Threat Intelligence API

Everything in this section is available over the REST API. [API Reference](../api-reference/index.md) covers authentication and conventions; Swagger at `https://<your-host>/api/docs` is exhaustive.

```bash
export OFFLOAD_HOST="https://your-instance.example.com"
export OFFLOAD_API_KEY="osk_xxxxxxxxxxxxxxxxxxxx"
```

Send the key as `X-API-Key`; calls are scoped to the key's team.

## Threat Intelligence

| Task | Endpoint | Notes |
| --- | --- | --- |
| Dashboard · indicators | `GET /api/threat-intelligence/dashboard` · `GET /api/threat-intelligence/indicators?ioc_type=&severity=&confidence=&search=&limit=` · `POST /api/threat-intelligence/search` | Read: any member |
| Add an indicator | `POST /api/threat-intelligence/indicators` `{ioc_type, value, severity, description, …}` | **Manage Threat Intelligence** |
| Correlate | `POST /api/threat-intelligence/correlate` `{indicator}` | Assets, related indicators, actors, campaigns |
| Prioritise CVEs | `POST /api/threat-intelligence/vulnerabilities/prioritize` `{cve_ids[]}` · `POST /api/enhanced-threat-intelligence/vulnerabilities/prioritize-real` | Score 50 + KEV 25 + indicators ≤ 15 + actors ≤ 10 + campaigns ≤ 10 + critical 10 |
| Feeds | `GET /api/threat-intelligence/feeds` · `GET …/feeds/{feed_id}/details` · `POST …/feeds/process/{feed_id}` · `POST …/feeds/{feed_id}/refresh` · `PUT …/feeds/{feed_id}` `{api_key, …}` · `PUT …/feeds/{feed_id}/enable` · `…/disable` · `POST …/feeds/test-connection` | Configuration needs **Manage Threat Intelligence** |
| MITRE heatmap · alerts | `GET /api/threat-intelligence/mitre-heatmap` · `GET /api/threat-intelligence/alerts` | |
| Landscape reports | `POST /api/threat-intelligence/landscape-report` `{report_period_days: 7\|30\|90, report_format: executive\|technical\|comprehensive}` · `GET …/landscape-reports` · `GET …/landscape-reports/{report_id}` | |
| Actors · campaigns | `POST` · `GET /api/enhanced-threat-intelligence/actors` · `GET` · `PUT` · `DELETE …/actors/{actor_id}` · same under `…/campaigns` | TLP classification, ATT&CK techniques; API-only today |
| Alert rules · hunting | `GET` · `POST …/alert-rules` · `POST …/alert-rules/{rule_id}/toggle` · `GET` · `POST …/hunting-queries` · `POST …/hunting-queries/{query_id}/execute` | |
| Alerts workflow | `POST` · `GET …/alerts` · `GET …/alerts/{alert_id}` · `PUT …/alerts/{alert_id}/status` · `…/assign` · `POST …/alerts/{alert_id}/comments` · `GET …/ioc-sightings` | |
| Import · export | `POST …/bulk-import` `{format: csv\|json\|stix, data}` · `POST …/bulk-export` `{format: stix\|csv\|json, ioc_type?}` | |
| Aging | `GET` · `PUT …/ioc-aging-config` `{default_ttl_days, ttl_by_ioc_type, decay_rate_per_day, minimum_confidence}` · `POST …/ioc-aging/apply-decay` | Defaults 90 days · 0.5 %/day · floor 10 |
| Vocabularies | `GET …/tlp-classifications` · `GET …/kill-chain-phases` | |

## Security Command Center

| Task | Endpoint | Notes |
| --- | --- | --- |
| Dashboard · status · triggers · log | `GET /api/ai-agents/dashboard` · `GET /api/ai-agents/status` · `GET /api/ai-agents/triggers` · `GET /api/ai-agents/audit-log?limit=` | **Run AI Agent** |
| Triage | `POST /api/ai-agents/triage/findings` `{scan_id: "<run id>" \| "latest"}` or `{findings: [...]}` · `POST /api/ai-agents/triage/worklist/run` `{scan_id?, limit?}` · `GET /api/ai-agents/triage/worklist?action=&limit=` · `POST …/triage/worklist/{finding_id}/decision` `{action: fix\|defer\|dedup\|suppress, decision?}` | **Run AI Agent** |
| Incidents · FP/TP | `POST …/triage/incidents/run` · `GET …/triage/incidents` · `POST …/triage/fp-assess/run` · `POST …/triage/fp-assess/code` · `GET …/triage/fp-assessments` · `GET …/triage/fp-accuracy` | Advisory; never suppresses |
| Auto-fix hand-off | `GET …/triage/auto-fix-queue` · `POST …/triage/auto-fix/process` · `POST …/triage/worklist/{finding_id}/auto-fix` · `GET` · `POST …/triage/auto-fix/settings` `{enabled}` | Settings need **Manage Team** |
| Remediation · compliance agents | `POST /api/ai-agents/remediation/generate` `{finding}` · `POST /api/ai-agents/compliance/assess` · `…/compliance/evidence` · `…/compliance/gap-analysis` · `GET …/compliance/evidence-templates` | |
| Threat hunt · advisor | `POST /api/ai-agents/threat-hunt/execute` `{action: hunt\|correlate\|generate_hypothesis}` · `POST /api/ai-agents/posture/ask` `{question}` · `POST …/posture/briefing` `{period?}` · `GET …/posture/benchmark` · `GET …/posture/priorities` | |
| Auto-Fix Engine | `POST /api/compliance-engine/remediation/process-findings` `{all_active?}` · `GET …/remediation/actions?status=pending\|approved\|executed\|denied\|rolled_back&limit=` · `GET …/remediation/stats` · `POST …/remediation/actions/{action_id}/approve` · `…/deny` `{reason}` · `…/execute` · `…/rollback` | **Execute Remediations**; `status=pending` covers both awaiting-approval spellings |

## AI Governance

| Task | Endpoint | Notes |
| --- | --- | --- |
| Dashboard · posture | `GET /api/ai-governance/dashboard` · `GET …/compliance-score` · `GET …/gap-analysis` · `GET …/certification-readiness` · `GET …/compliance-dashboard` · `GET …/coverage-summary` | |
| Registry | `GET` · `POST /api/ai-governance/models` `{name, description, owner, type, risk_level, use_case, data_sources[], deployment_status, business_unit, last_assessment_date?, next_review_date?}` · `GET` · `PUT` · `DELETE …/models/{model_id}` | **Manage Assessments** throughout |
| Assessments · tests | `GET` · `POST …/risk-assessments` · `GET` · `POST …/bias-tests` · `POST …/models/{model_id}/run-bias-tests` · `GET …/models/{model_id}/bias-test-results` · `GET` · `POST …/impact-analysis` · `POST …/automated-tests/{fairness\|privacy\|data-quality\|comprehensive}` | |
| Structured assessments | `POST …/assessments/draft` · `GET …/assessments/{assessment_id}/draft` · `POST …/assessments/{assessment_id}/submit` · `…/evidence` · `…/remediation-tasks` · `GET …/assessments/{assessment_id}/executive-summary` · `…/compliance-mapping` · `…/detailed-report` · `GET …/risk-categories` · `…/assessment-frameworks` | |
| Operations | `GET` · `POST …/incidents` · `GET` · `POST …/human-oversight` · `GET` · `POST …/training-records` · `GET …/audit-trail` | |
| Monitoring | `POST …/models/{model_id}/health-score` · `…/drift-detection` · `…/performance-trend` · `…/monitoring-alert` · `GET …/models/{model_id}/monitoring-summary` | |
| Helpers · reports | `POST …/assessment-helper/{suggest-scores\|suggest-mitigations\|validate-completeness\|generate-summary}` · `POST …/generate-report` `{report_type, format}` | Helpers use the configured LLM |
| ISO 42001 exports | `GET /api/common-controls/soa/iso_42001?format=xlsx` · `GET /api/evidence-completion/auditor-package/iso_42001` | Statement of Applicability · auditor ZIP |

## Discovery, AIBOM and testing

| Task | Endpoint | Notes |
| --- | --- | --- |
| Discovery | `POST /api/ai-spm/discover` → job; `GET /api/jobs/{job_id}` · `GET /api/ai-spm/dashboard` | Cloud asset inventory + LLM configuration |
| Classify | `POST /api/ai-spm/classify/{model_id}` `{use_case?, sector?, data_types?, decision_impact?}` · `GET /api/ai-spm/risk-tiers` · `GET /api/ai-spm/compliance` | EU AI Act tier + NIST AI RMF |
| Prompt tests | `POST /api/ai-spm/prompt-test/{model_id}` `{api_endpoint?, api_key?, custom_payloads?}` · `GET …/prompt-test/results/{test_id}` · `GET /api/ai-spm/supply-chain/{model_id}` | Key is used for the run only |
| AIBOM | `GET /api/v1/aibom/summary` · `GET /api/v1/aibom/components?component_type=&provider=&owner=&environment=&state=active\|stale\|all&needs_confirmation=&page=` · `GET …/components/{component_id}` · `PATCH …/components/{component_id}/governance` (owner, environment, confirm / dismiss) · `GET …/relationships/{component_id}` · `GET …/scans` · `POST …/scans/sbom` (reconcile now) | |

## Knowledge Base

| Task | Endpoint | Notes |
| --- | --- | --- |
| Sections · documents | `GET` · `POST /api/knowledge-base/sections` · `POST /api/knowledge-base/upload` (multipart: `file`, `title`, `section_id`, `document_type`, `sensitivity_level`, `description`, `tags`) · `GET …/documents` · `DELETE …/documents/{document_id}` · `POST …/documents/reprocess` · `…/reprocess-extraction` | Uploads need **Manage Assessments** |
| Ask · search | `POST /api/knowledge-base/ask` `{question, section_id?, document_id?}` · `POST …/search` `{query, section_id?}` · `GET …/questions` · `POST …/questions/{question_id}/feedback` `{helpful}` · `GET …/templates` | Answers carry `sources[]`, `confidence_score`, `confidence_level` |
| Questionnaire | `POST /api/knowledge-base/questionnaire/detect-columns` (multipart) · `POST …/questionnaire/fill` (multipart: `file`, `detail_level: short\|standard\|detailed`) → `GET …/questionnaire/fill/{fill_id}/download` · `GET` · `PUT …/questionnaire/settings` `{refinement_enabled, default_detail_level, max_words}` · `POST …/questionnaire/refine` | |
| Review queue · bank | `GET /api/review/queue?priority=&status=` · `GET /api/review/summary` · `GET /api/review/items/{item_id}` · `POST …/items/{item_id}/approve` · `…/edit` `{answer}` · `…/reject` · `GET` · `POST /api/question-bank/entries` · `POST /api/question-bank/import` | Approved answers write back to the bank |
| Analytics · config | `GET /api/knowledge-base/analytics` · `GET` · `PUT …/config` · `GET …/ai-providers` · LLM providers: see [Reports & AI API](../reports-and-ai/api.md#llm-providers) | |

## Permissions

| Action | Permission |
| --- | --- |
| Read the threat dashboard, indicators, feeds, heatmap, reports, alerts | any authenticated team member |
| Configure feeds, add indicators, correlate, prioritise, generate reports, actors / campaigns / rules / hunting, aging, import / export | **Manage Threat Intelligence** (`manage_threat_intelligence`) — Security Manager |
| Run agents: triage, worklist decisions, incidents, FP/TP, hand-offs, remediation drafting, threat hunt, advisor | **Run AI Agent** (`run_ai_agent`) |
| Team auto-fix opt-in | **Manage Team** |
| Approve / deny / execute / roll back Auto-Fix actions, process findings | **Execute Remediations** (`execute_remediations`) |
| AI governance registry, assessments, tests, incidents, oversight, training, reports; discovery, classification, prompt tests, AIBOM; Knowledge Base uploads, questions, questionnaire fill, review queue | **Manage Assessments** (`manage_assessments`) |
| Knowledge Base library, analytics, templates | any authenticated team member |

See [Authentication](../api-reference/authentication.md) for key scopes and [Conventions](../api-reference/conventions.md) for pagination, error shapes and rate limits.
