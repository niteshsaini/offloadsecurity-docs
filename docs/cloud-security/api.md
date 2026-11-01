---
title: "Cloud Security API"
sidebar_label: "API"
sidebar_position: 12
description: "Every Cloud Security workflow over REST — connect accounts, start and poll scans, point-in-time reports and run comparison, grouped findings, custom policies, compliance scores, identity and network analysis, cloud events and SSL domains."
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
| Get / update / remove | `GET` · `PUT` · `DELETE /api/cloud-accounts/{id}` | `PUT` accepts `regions` (the scan scope) and `credentials` (rotation — tested with the account's own sign-in method; the result is in `credential_test`). `DELETE` cascades findings, scores, scan history and schedules; the deletion is recorded. |
| Test connection | `POST /api/cloud-accounts/{id}/revalidate` | Same check as onboarding step 6. |
| Scan one account | `POST /api/cloud-accounts/{id}/scan` | Body `{ "scan_type": "quick" \| "full" \| "comprehensive" }`. Needs **Run Scans** and **Manage Cloud Accounts**. Works with an API key. |
| Bulk actions | `POST /api/cloud-accounts/bulk/revalidate` · `/bulk/scan` · `/bulk/delete` | Body `{ "account_ids": [...] }` (at most 100; + `scan_type` for scan). Bulk scans are staggered. Result lists queued / already running / skipped / failed. |
| GCP organization | `POST /api/gcp/org/readiness` · `POST /api/gcp/org/connections` · `GET /api/gcp/org/connections/{id}/hierarchy` · `POST …/rediscover` | Org/folder onboarding, project discovery, per-project toggle (`PUT …/projects/{project_id}/toggle`). There is no organization onboarding API for AWS or Azure. |

```bash
curl -s -X POST "$OFFLOAD_HOST/api/cloud-accounts/$ACCOUNT_ID/scan" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{ "scan_type": "full" }'
```

## Scans

| Task | Endpoint | Notes |
| --- | --- | --- |
| Start a scan | `POST /api/cloud-scans/initiate` | Body `{ "account_id", "provider", "scan_type": "full" \| "incremental", "regions": ["us-east-1", …], "engagement": { "attested": true, "reference", "environment", "valid_until" } }` — omit `regions` to use the account's configured scope (AWS with none configured: every enabled region). `engagement` records the [scan authorization](./scan-orchestration.md#scan-authorization); with `SCAN_REQUIRE_AUTHORIZATION` on, a scan without a current one is refused with `400`. **Session-only** (needs **Create Cloud Scans**); from automation use `POST /api/cloud-accounts/{id}/scan` above. Returns `run_id`, `status`, `sub_jobs_count`, `estimated_completion`. |
| List scans | `GET /api/cloud-scans/?account_id=&provider=&status=&limit=50&skip=0` | Team-scoped history. |
| Poll one scan | `GET /api/cloud-scans/{run_id}/status` | `status` (`queued` → `running` → `completed` / `partial` / `failed` / `cancelled`), `progress.overall`, per-job and per-region status, `summary`. |
| Run summary | `GET /api/cloud-scans/{run_id}/summary` | Totals and severity breakdown. |
| Compare two runs | `GET /api/cloud-scans/{run_id}/compare?baseline=` | New failing / fixed / still failing / not re-evaluated, from the runs' frozen snapshots. Default baseline: the account's previous run with a snapshot. |
| Cancel | `DELETE /api/cloud-scans/{run_id}` | Needs **Manage Scans**. |
| Coverage dashboard | `GET /api/cloud/coverage-summary?scan_stale_days=30` | The Coverage tab's data: scanned / scheduled / not covered, findings by severity, stale accounts. |

```bash
# poll until terminal
curl -s "$OFFLOAD_HOST/api/cloud-scans/$RUN_ID/status" -H "X-API-Key: $OFFLOAD_API_KEY" \
  | jq '{status: .status, overall: .progress.overall, findings: .summary.total_findings}'
```

## Point-in-time reports

| Task | Endpoint | Notes |
| --- | --- | --- |
| Posture report for one run | `GET /api/export/cloud-posture?scan_run_id=` · `/export/cloud-posture.html?scan_run_id=` · `/export/cloud-posture.docx?scan_run_id=` | Built from the run's frozen snapshot. Without `scan_run_id`: the current state of all findings, not a point in time. PDF and HTML responses carry `X-Content-SHA256`. |
| Re-download an issued report | `GET /api/export/issued/{sha256}` | The exact issued PDF/HTML copy, team-scoped. |
| Verify a report file | `GET /api/native-scans/exports/verify?sha256=` | `verified: true` when this platform issued exactly that file to your team. |

See [Point-in-Time Reports](./point-in-time-reports.md).

## Findings

| Task | Endpoint | Notes |
| --- | --- | --- |
| Grouped findings (the Findings tab) | `GET /api/cspm/findings/grouped` | Filters: `account_id`, `provider`, `category`, `severity`, `status` (default `fail`), `service`, `framework`, `search`, `limit`, `skip`. Returns one group per check with instance counts, regions, accounts and risk score. |
| Raw findings | `GET /api/cspm/findings` | Per-resource rows with the same filters. |
| One finding | `GET /api/cspm/findings/{finding_id}` | Full detail incl. remediation and framework controls. |
| Stats | `GET /api/cspm/findings/stats` · `/category-summary` · `/risk-trend` · `/posture-trend/{account_id}` | Severity counts, per-category posture scores (incl. IAM and network scores), trends. `stats-by-account` and `compliance-scores` are **session-only**. |
| Resolve | `POST /api/cspm/findings/{finding_id}/resolve` | Body `{ "resolution_notes": "…" }`. Needs **Manage Risks**. |
| Suppress / unsuppress | `POST /api/cspm/findings/{finding_id}/suppress` · `/unsuppress` | Body `{ "reason": "…", "duration_days": 30 }` or `{ "suppress_until": "2026-12-31T00:00:00Z" }`; omit both for permanent. |
| Bulk action on a check | `POST /api/cspm/findings/grouped/{check_id}/bulk-action` | Body `{ "action": "resolve_all" \| "suppress_all" \| "create_remediation", "reason": "…" }` — every instance of the check in one call. |
| Create remediation task | `POST /api/cspm/findings/{finding_id}/remediation` | Body `{ "assigned_to", "priority", "due_date", "notes" }`. |
| Export | `GET /api/cspm/findings/export?format=csv` | `format` = `csv` \| `xlsx`. **Session-only**; honors the same filters, including `framework`. Includes custom-policy findings; at most 50,000 rows, with the cap disclosed in the file. |

```bash
# critical, still-failing checks in one account
curl -s "$OFFLOAD_HOST/api/cspm/findings/grouped?account_id=$ACCOUNT_ID&severity=critical&status=fail" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
```

## Custom policies

| Task | Endpoint | Notes |
| --- | --- | --- |
| List | `GET /api/cspm/policies/custom` | The team's policies with per-account evaluation results. Needs **View Scans**. |
| Create / update | `POST /api/cspm/policies/custom` · `PUT /api/cspm/policies/custom/{id}` | `name`, `severity`, `provider`, `service`, `resource_type`, `description`, `remediation`, `compliance_frameworks`, `enabled`, `condition`. A condition outside the supported language is rejected with `400`. Evaluation starts as a background job. Needs **Manage Scans**. |
| Delete | `DELETE /api/cspm/policies/custom/{id}` | Retires the policy's open findings. API only — the UI offers disable. Needs **Manage Scans**. |

See [Custom Cloud Policies](./custom-policies.md) for the condition language.

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
| Identity analysis attempts and evaluation coverage | `GET /api/advanced-cspm/identity-analysis/coverage` | Per account: last attempt (completed / partial / failed), result age, and AWS evaluation coverage (SCPs, boundaries, resource policies, principals analysed). |
| Run IAM analysis | `POST /api/advanced-cspm/identity-analysis` | Body `{ "account_id" }`. Starts a deduplicated background job; read-only; the result is persisted for the roster and graph. |
| Reachability refresh status | `GET /api/advanced-cspm/network-analysis/coverage` | Per account: when internet reachability was last refreshed and how the last attempt ended. |
| Access review / unused | `POST /api/advanced-cspm/identity-analysis/access-review` · `/cleanup-unused` | `cleanup-unused` is a dry-run listing — nothing is deleted. |
| Network analyses | `POST /api/advanced-cspm/network-analysis/firewall-audit` · `/public-exposure` · `/segmentation` | Body `{ "account_id" }`. |

## Cloud events

| Task | Endpoint | Notes |
| --- | --- | --- |
| Receive events | `POST /api/cloud-events/webhook/{aws\|gcp\|azure}/{team_token}`, or `…/webhook/{provider}` with the `x-offload-webhook-token` header | Target of your EventBridge / Pub/Sub / Event Grid route — see [Real-Time Cloud Events](./cloud-events.md#authenticating-the-webhook). |
| Team webhook token | `GET` · `POST` · `DELETE /api/cloud-events/webhook-token` | Status (hint only) · create or rotate (the token is returned once) · revoke. `POST` / `DELETE` need **Manage Cloud Accounts**. |
| Setup guide | `GET /api/cloud-events/setup-guide` | Per-provider URLs and steps for your instance. |
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
| Inventory | `GET /api/unified-cloud-security/assets` · `/assets/summary` · `/assets/by-account` | Filters mirror the Detailed Inventory tab, plus `encryption_state=encrypted\|not_encrypted\|not_assessed` and `status=deleted`. |
| Export inventory | `GET /api/unified-cloud-security/assets/export` | Streamed CSV of every matching asset. |
| Refresh discovery | `POST /api/unified-cloud-security/assets/refresh?account_id=` | Background job. |
| Security graph | `POST /api/security-graph/sync` · `GET /api/security-graph/stats` | Build / inspect the graph. |
| Graph explorer | `GET /api/security-graph/graph?node_type=&provider=&account_id=&public_only=&with_findings=&search=&limit=1000` | Filtered nodes and edges with per-node finding roll-ups, true totals and a `truncated` flag when `limit` cuts the set (max 5,000). |
| Attack paths | `POST /api/attack-paths/analyze` · `GET /api/attack-paths/latest` · `GET /api/attack-paths/blast-radius/{node_id}` · `POST /api/attack-paths/simulate` | Analysis (background job, needs **Manage Risks**), last result, blast radius (team-checked: a node outside your team returns `404`), what-if. |

## Permissions

| Action | Platform permission |
| --- | --- |
| Read accounts, scans, findings | **View Cloud Accounts** / **View Scans** |
| Connect, update, remove accounts | **Manage Cloud Accounts** |
| Start or cancel scans | **Create Cloud Scans** / **Run Scans** / **Manage Scans** |
| Manage custom policies | **Manage Scans** |
| Resolve, suppress, create tasks | **Manage Risks** |

See [Authentication](../api-reference/authentication.md) for creating keys with the right scopes and [Conventions](../api-reference/conventions.md) for pagination, error shapes and rate limits.
