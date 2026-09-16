---
title: "Reports & AI API"
sidebar_label: "API"
sidebar_position: 5
description: "Executive dashboard, scheduled reports, consolidated and branded report generation, and the AI endpoints — chat, quick insights, scan analysis, explain / fix / summarise — plus LLM provider configuration and the permissions behind each."
---

# Reports & AI API

Everything in this section is available over the REST API. [API Reference](../api-reference/index.md) covers authentication and conventions; Swagger at `https://<your-host>/api/docs` is exhaustive.

```bash
export OFFLOAD_HOST="https://your-instance.example.com"
export OFFLOAD_API_KEY="osk_xxxxxxxxxxxxxxxxxxxx"
```

Send the key as `X-API-Key`; calls are scoped to the key's team.

## Executive dashboard

| Task | Endpoint | Notes |
| --- | --- | --- |
| Overview | `GET /api/executive-dashboard/overview` | Maturity, per-framework status, priority gaps, certification readiness, strengths, 90-day trend, recommendations — the same scorer as Compliance Posture. |
| Metrics | `GET /api/executive-dashboard/compliance-metrics?period_days=90` (≤ 365) · `GET /api/executive-dashboard/board-metrics` | |
| Generate | `POST /api/executive-dashboard/gap-analysis` · `POST /api/executive-dashboard/remediation-roadmap` · `POST /api/executive-dashboard/executive-report?report_type=summary\|detailed\|board` | **View Dashboard**. |
| PDF | `GET /api/executive-dashboard/export-pdf?report_type=summary\|board\|gap-analysis` | Branded Compliance Posture Report (PDF stream). |
| Work the gaps | `PUT /api/executive-dashboard/gaps/{gap_id}/assign?owner=` · `PUT …/gaps/{gap_id}/status?status=` · `PUT …/roadmap/{milestone_id}/progress?progress=` | `gap_id` is the SCF ID. |

## Scheduled reports

| Task | Endpoint | Notes |
| --- | --- | --- |
| Create | `POST /api/executive-dashboard/schedule-report?report_type=summary\|board\|gap-analysis&frequency=daily\|weekly\|monthly\|quarterly&recipients=a@x,b@y` | First run at 09:00 UTC one interval out. |
| List / delete | `GET /api/executive-dashboard/scheduled-reports` · `DELETE …/scheduled-reports/{schedule_id}` | Rows carry `last_run`, `last_status`, `run_count`, `next_run`, `last_delivery`. |
| Runs | `GET …/scheduled-reports/{schedule_id}/history` · `GET …/scheduled-reports/{schedule_id}/latest` | `latest` streams the most recent PDF. |

## Consolidated and per-module reports

| Task | Endpoint | Notes |
| --- | --- | --- |
| Consolidated scan report | `POST /api/reports/consolidated` `{scan_ids[], report_format: html\|pdf\|docx, report_title?, project_name?, include_screenshots (default true), max_screenshots ≤ 30}` · `POST /api/reports/target` `{target, report_format, …}` | Returns a job id; poll `GET /api/jobs/{job_id}`, then `GET /api/reports/{job_id}/download`. |
| Report history | `GET /api/reports/history` | Generated reports for the team (180-day retention). |
| Per-scan report | `GET /api/native-scans/results/{scan_id}/download?format=html\|pdf\|docx` · `GET /api/app-scan/{app_scan_id}/report?format=html\|pdf` | |
| Code / SBOM | `GET /api/code/reports/{scan_id}/export?format=pdf` · `GET /api/code/sbom/{scan_id}/download` · `…/export?format=csv\|csv-vulns\|json` | |
| Container / Kubernetes | `GET /api/container/scans/{scan_id}/export?format=json\|csv\|cyclonedx` · `POST /api/container-security/compliance-report` · `POST /api/k8s/compliance/report` | |
| Cloud findings | `GET /api/cspm/findings/export?format=csv\|xlsx` | Session-authenticated only. |
| Risk | `GET /api/risk-management/reports/export?format=json\|csv` · `…/reports/executive-summary` · `…/reports/executive-pdf-data` | |
| Compliance | `POST /api/compliance-engine/reports/generate` → `GET …/reports/{report_id}/download/{section}` · `GET /api/evidence-completion/auditor-package/{framework}` · `GET /api/common-controls/soa/{framework}` · `GET /api/assessments/{assessment_id}/export-pdf` · `GET /api/dpdp/audit/pack/{pack_id}/pdf` | See [Compliance & GRC API](../compliance/api.md). |

## Branded report family

| Route | Formats |
| --- | --- |
| `GET /api/export/executive-dashboard` · `GET /api/export/compliance-posture` · `GET /api/export/ai-decisions` · `GET /api/export/scan-results?scan_type=all\|…` | PDF |
| `GET /api/export/cloud-posture` · `web-app` · `network` · `app-sec` · `consolidated-exec` — each also as `.html` and `.docx` | PDF · HTML · DOCX |

## AI

| Task | Endpoint | Notes |
| --- | --- | --- |
| Assistant | `POST /api/ai/chat/message` `{message, conversation_id?, context?}` · `GET /api/ai/chat/conversations` · `GET` · `DELETE …/conversations/{conversation_id}` · `POST /api/ai/chat/suggestions` `{context?}` · `GET /api/ai/chat/status` | Message and provider name come back with `cached: true` when served from platform knowledge. |
| Quick insight | `POST /api/ai/chat/quick-insight` `{insight_type: vulnerability\|scan\|compliance\|risk, data}` | Two or three sentences for a card. |
| Explain / fix / summarise | `POST /api/ai/explain-vulnerability` · `POST /api/ai/suggest-fix` · `POST /api/ai/summarize-scan` · `POST /api/ai/prioritize-findings` · `GET /api/ai/status` · `GET /api/ai/models` | **Manage Integrations**. |
| Scan analysis | `POST /api/ai/analysis/analyze` · `…/compare` · `…/executive-report` · `…/predict-risk` · `…/quick-insights` · `GET /api/ai/analysis/status` | **Manage Scans**. |
| Risk AI | `POST /api/risk-management/ai/{suggest \| treatment-plan \| compliance-gaps \| recommend-kris \| scenarios}` | See [Vulnerabilities & Risk API](../vulnerability-risk/api.md#risks). |
| Triage explain | `POST /api/triage/finding/{fingerprint}/explain` | See [Vulnerabilities & Risk API](../vulnerability-risk/api.md#triage). |
| Knowledge base | `GET /api/knowledge-base/…` — documents, search, questionnaire | See [Knowledge Base](../ai-threat-intelligence/knowledge-base.md). |

## LLM providers

| Task | Endpoint | Notes |
| --- | --- | --- |
| List | `GET /api/llm/providers` | Per provider: `configured`, masked key, models, default and fast model, `active_provider`. |
| Configure | `POST /api/llm/providers/{anthropic\|openai\|google}/configure` `{api_key, model?}` | Key encrypted at rest, team-scoped; first configured becomes active. **Manage Integrations**. |
| Test / activate / remove | `POST …/providers/{provider_id}/test` · `POST …/providers/{provider_id}/activate` · `DELETE …/providers/{provider_id}` | |

## Permissions

| Action | Permission |
| --- | --- |
| Read executive overview, metrics, PDF, scheduled reports, report history | any authenticated team member |
| Generate gap analysis / roadmap / executive reports, assign gaps, update roadmap progress, create or delete schedules | **View Dashboard** (`view_dashboard`) |
| Consolidated scan reports and per-module exports | the module's view permission (e.g. **View Scans**) |
| Assistant messages, explain / suggest fix / summarise / prioritise, LLM provider configuration | **Manage Integrations** (`manage_integrations`) |
| AI scan analysis | **Manage Scans** (`manage_scans`) |

See [Authentication](../api-reference/authentication.md) for key scopes and [Conventions](../api-reference/conventions.md) for pagination, error shapes and rate limits.
