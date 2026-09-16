---
title: "Cloud Security API"
sidebar_label: "API"
sidebar_position: 12
description: "Every Cloud Security workflow over REST — connect accounts, start and poll scans, list and triage grouped findings, read compliance scores and coverage, manage remediation tasks, cloud events and SSL domains."
---

# Cloud Security API

Everything on the Cloud Security pages is available over the REST API. This page maps each workflow to its endpoints; the [API Reference](../api-reference/index.md) covers authentication, conventions and full request/response examples, and the live Swagger UI at `https://<your-host>/api/docs` is the exhaustive list.

```bash
export OFFLOAD_HOST="https://your-instance.example.com"
export OFFLOAD_API_KEY="osk_xxxxxxxxxxxxxxxxxxxx"   # Settings → API Keys
```

Send the key as `X-API-Key`. Every call is scoped to the key's team. A few endpoints noted below are **session-only** (they accept a signed-in user's `X-Session-ID` but not an API key).

## Accounts

| Task | Endpoint | Notes |
| --- | --- | --- |
| List connected accounts | `GET /api/cloud-accounts/` | Credentials are never returned. |
| Connect an account | `POST /api/cloud-accounts/` | `provider`, `account_id`, `account_name`, `region`, `credentials{}` — per-provider keys in [Cloud Accounts API](../api-reference/cloud-accounts.md). Validates before saving; returns `scan_run_id` of the first scan. |
| Get / update / remove | `GET` · `PUT` · `DELETE /api/cloud-accounts/{id}` | `PUT` accepts `regions` (the scan scope) among other fields. `DELETE` cascades findings, scores, scan history and schedules. |
| Test connection | `POST /api/cloud-accounts/{id}/revalidate` | Same check as onboarding step 6. |
| Scan one account | `POST /api/cloud-accounts/{id}/scan` | Body `{ "scan_type": "quick" \| "full" \| "comprehensive" }`. Needs **Run Scans**. |
| Bulk actions | `POST /api/cloud-accounts/bulk/revalidate` · `/bulk/scan` · `/bulk/delete` | Body `{ "account_ids": [...] }` (+ `scan_type` for scan). Result lists queued / already running / skipped / failed. |
| GCP organization | `POST /api/gcp/org/readiness` · `POST /api/gcp/org/connections` · `GET /api/gcp/org/connections/{id}/hierarchy` · `POST …/rediscover` | Org/folder onboarding, project discovery, per-project toggle (`PUT …/projects/{project_id}/toggle`). |

```bash
curl -s -X POST "$OFFLOAD_HOST/api/cloud-accounts/$ACCOUNT_ID/scan" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{ "scan_type": "full" }'
```

## Scans

| Task | Endpoint | Notes |
| --- | --- | --- |
| Start a scan | `POST /api/cloud-scans/initiate` | Body `{ "account_id", "provider", "scan_type": "full", "regions": ["us-east-1", …] }` — omit `regions` to use the account's configured scope. **Session-only**; from automation use `POST /api/cloud-accounts/{id}/scan` above. Returns `run_id`, `status`, `sub_jobs_count`, `estimated_completion`. |
| List scans | `GET /api/cloud-scans/?account_id=&provider=&status=&limit=50&skip=0` | Team-scoped history. |
| Poll one scan | `GET /api/cloud-scans/{run_id}/status` | `status` (`queued` → `running` → `completed` / `partial` / `failed` / `cancelled`), `progress.overall`, per-job and per-region status, `summary`. |
| Run summary | `GET /api/cloud-scans/{run_id}/summary` | Totals and severity breakdown. |
| Cancel | `DELETE /api/cloud-scans/{run_id}` | Needs **Manage Scans**. |
| Coverage dashboard | `GET /api/cloud/coverage-summary?scan_stale_days=30` | The Coverage tab's data: scanned / scheduled / not covered, findings by severity, stale accounts. |

```bash
# poll until terminal
curl -s "$OFFLOAD_HOST/api/cloud-scans/$RUN_ID/status" -H "X-API-Key: $OFFLOAD_API_KEY" \
  | jq '{status: .status, overall: .progress.overall, findings: .summary.total_findings}'
```

## Findings

| Task | Endpoint | Notes |
| --- | --- | --- |
| Grouped findings (the Scanning tab) | `GET /api/cspm/findings/grouped` | Filters: `account_id`, `provider`, `category`, `severity`, `status` (default `fail`), `service`, `framework`, `search`, `limit`, `skip`. Returns one group per check with instance counts, regions, accounts and risk score. |
| Raw findings | `GET /api/cspm/findings` | Per-resource rows with the same filters. |
| One finding | `GET /api/cspm/findings/{finding_id}` | Full detail incl. remediation and framework controls. |
| Stats | `GET /api/cspm/findings/stats` · `/category-summary` · `/risk-trend` · `/posture-trend/{account_id}` | Severity counts, per-category posture scores (incl. IAM and network scores), trends. `stats-by-account` and `compliance-scores` are **session-only**. |
| Resolve | `POST /api/cspm/findings/{finding_id}/resolve` | Body `{ "resolution_notes": "…" }`. Needs **Manage Risks**. |
| Suppress / unsuppress | `POST /api/cspm/findings/{finding_id}/suppress` · `/unsuppress` | Body `{ "reason": "…", "duration_days": 30 }` or `{ "suppress_until": "2026-12-31T00:00:00Z" }`; omit both for permanent. |
| Bulk action on a check | `POST /api/cspm/findings/grouped/{check_id}/bulk-action` | Body `{ "action": "resolve_all" \| "suppress_all" \| "create_remediation", "reason": "…" }` — every instance of the check in one call. |
| Create remediation task | `POST /api/cspm/findings/{finding_id}/remediation` | Body `{ "assigned_to", "priority", "due_date", "notes" }`. |
| Export | `GET /api/cspm/findings/export?format=csv` | `format` = `csv` \| `xlsx`. **Session-only**; honours the same filters. |

```bash
# critical, still-failing checks in one account
curl -s "$OFFLOAD_HOST/api/cspm/findings/grouped?account_id=$ACCOUNT_ID&severity=critical&status=fail" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
```

## Remediation tasks

| Task | Endpoint | Notes |
| --- | --- | --- |
| List the queue | `GET /api/cspm/remediation-tasks?status=open&severity=&priority=&search=&limit=20&skip=0` | Non-terminal tasks first; response carries `tasks`, `summary` (count per status) and `total`. |
| Update a task | `PATCH /api/cspm/remediation-tasks/{task_id}` | Any of `status` (`open` · `in_progress` · `done` · `wont_fix` · `cancelled`), `assigned_to`, `priority`, `due_date`, `notes`. |

## Compliance

| Task | Endpoint | Notes |
| --- | --- | --- |
| Per-framework scores | `GET /api/cspm/findings/compliance-scores?account_id=&provider=&framework=&scan_run_id=` | **Session-only.** One row per account × framework from the latest finished scan: `score`, `passed_checks`, `failed_checks`, `total_checks`, `by_severity`. |

## Identity & network analysis

| Task | Endpoint | Notes |
| --- | --- | --- |
| CIEM coverage | `GET /api/ciem/coverage-summary` | The IAM tab's identity coverage & risk. |
| Run IAM analysis | `POST /api/advanced-cspm/identity-analysis` | Body `{ "account_id" }`. Live, read-only; result persisted for the roster and graph. |
| Access review / unused | `POST /api/advanced-cspm/identity-analysis/access-review` · `/cleanup-unused` | `cleanup-unused` is a dry-run listing — nothing is deleted. |
| Network analyses | `POST /api/advanced-cspm/network-analysis/firewall-audit` · `/public-exposure` · `/segmentation` | Body `{ "account_id" }`. |

## Cloud events

| Task | Endpoint | Notes |
| --- | --- | --- |
| Receive events | `POST /api/cloud-events/webhook/aws` · `/gcp` · `/azure` | Target of your EventBridge / Pub/Sub / Event Grid route — see [Real-Time Cloud Events](./cloud-events.md#authenticating-the-webhook). |
| Recent events | `GET /api/cloud-events/recent?limit=50&provider=&severity=` | Enriched events (raw log omitted). |
| Ingestion stats | `GET /api/cloud-events/stats` | Totals and per-provider counts. |

## SSL certificates

| Task | Endpoint | Notes |
| --- | --- | --- |
| Manage domains | `GET` · `POST /api/ssl-monitor/domains` · `PUT` · `DELETE /api/ssl-monitor/domains/{id}` | `POST` body `{ "domain", "port": 443, "alert_threshold_days": 30, "enabled": true, "tags": [] }`; checks immediately. |
| Check now | `POST /api/ssl-monitor/domains/{id}/check` · `POST /api/ssl-monitor/domains/check-all` · `POST /api/ssl-monitor/check` (ad-hoc, unsaved) | |
| Dashboard / expiring | `GET /api/ssl-monitor/dashboard` · `GET /api/ssl-monitor/expiring` · `GET /api/ssl-monitor/domains/{id}/history` | |

## Assets and attack paths

| Task | Endpoint | Notes |
| --- | --- | --- |
| Inventory | `GET /api/unified-cloud-security/assets` · `/assets/summary` · `/assets/by-account` | Filters mirror the Detailed Inventory tab. |
| Refresh discovery | `POST /api/unified-cloud-security/assets/refresh?account_id=` | Background job. |
| Security graph | `POST /api/security-graph/sync` · `GET /api/security-graph/stats` | Build / inspect the graph. |
| Attack paths | `POST /api/attack-paths/analyze` · `GET /api/attack-paths/latest` · `GET /api/attack-paths/blast-radius/{node_id}` · `POST /api/attack-paths/simulate` | Analysis, last result, blast radius, what-if. |

## Permissions

| Action | Platform permission |
| --- | --- |
| Read accounts, scans, findings | **View Cloud Accounts** / **View Scans** |
| Connect, update, remove accounts | **Manage Cloud Accounts** |
| Start or cancel scans | **Run Scans** / **Manage Scans** |
| Resolve, suppress, create tasks | **Manage Risks** |

See [Authentication](../api-reference/authentication.md) for creating keys with the right scopes and [Conventions](../api-reference/conventions.md) for pagination, error shapes and rate limits.
